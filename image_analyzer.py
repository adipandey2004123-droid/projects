#!/usr/bin/env python3
"""
Image & Data Analysis Script
College Group Project Component

This script processes profile images from a JSON file:
1. Downloads each profile image from URL
2. Computes perceptual hash (pHash) using imagehash library
3. Sends results to backend API endpoint
4. Saves results locally for logging

Author: [Your Name]
Date: October 2025
"""

import os
import json
import requests
import imagehash
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from datetime import datetime
import sys

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
API_ENDPOINT = os.getenv('API_ENDPOINT', 'https://your-backend-api.com/api/checkImage')
WORKER_SECRET = os.getenv('WORKER_SECRET', '')  # Optional authentication header
INPUT_FILE = os.getenv('INPUT_FILE', 'profiles.json')
OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'results.json')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '5'))  # Number of concurrent threads

def load_profiles(file_path):
    """
    Load profile data from JSON file.

    Args:
        file_path (str): Path to the JSON file containing profiles

    Returns:
        list: List of profile dictionaries with 'id' and 'profile_image_url'
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            print(f"✓ Loaded {len(data)} profiles from {file_path}")
            return data
    except FileNotFoundError:
        print(f"✗ Error: File '{file_path}' not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in '{file_path}': {e}")
        sys.exit(1)

def download_image(url):
    """
    Download an image from a URL.

    Args:
        url (str): The URL of the image to download

    Returns:
        PIL.Image: The downloaded image object

    Raises:
        Exception: If download fails or image cannot be opened
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raise error for bad status codes
    image = Image.open(BytesIO(response.content))
    return image

def compute_phash(image):
    """
    Compute perceptual hash (pHash) for an image.

    Args:
        image (PIL.Image): The image object to hash

    Returns:
        str: Hexadecimal string representation of the perceptual hash
    """
    # Compute pHash using imagehash library
    phash = imagehash.phash(image)
    return str(phash)

def send_to_api(profile_id, phash):
    """
    Send the computed hash to the backend API.

    Args:
        profile_id (str): The profile UUID
        phash (str): The perceptual hash as hex string

    Returns:
        dict: API response data or error information
    """
    payload = {
        "id": profile_id,
        "p_hash": phash,
        "matches": []  # Adding matches field as an empty list
    }

    headers = {'Content-Type': 'application/json'}

    # Add optional worker secret header if provided
    if WORKER_SECRET:
        headers['X-WORKER-SECRET'] = WORKER_SECRET

    try:
        response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.json() if response.text else {}
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def process_profile(profile):
    """
    Process a single profile: download image, compute hash, send to API.

    Args:
        profile (dict): Profile dictionary with 'id' and 'profile_image_url'

    Returns:
        dict: Result dictionary with profile_id, phash, and status
    """
    profile_id = profile.get('id')
    image_url = profile.get('profile_image_url')

    result = {
        "id": profile_id,
        "p_hash": None,
        "status": "failed",
        "error": None,
        "api_response": None,
        "timestamp": datetime.now().isoformat()
    }

    try:
        # Step 1: Download the image
        print(f"  → Downloading image for profile {profile_id}...")
        image = download_image(image_url)

        # Step 2: Compute perceptual hash
        print(f"  → Computing pHash for profile {profile_id}...")
        phash = compute_phash(image)
        result["p_hash"] = phash

        # Step 3: Send to API
        print(f"  → Sending pHash to API for profile {profile_id}...")
        api_result = send_to_api(profile_id, phash)
        result["api_response"] = api_result

        if api_result.get("success"):
            result["status"] = "success"
            print(f"  ✓ Successfully processed profile {profile_id} (pHash: {phash})")
        else:
            result["status"] = "api_failed"
            result["error"] = api_result.get("error")
            print(f"  ✗ API failed for profile {profile_id}: {api_result.get('error')}")

    except Exception as e:
        result["error"] = str(e)
        print(f"  ✗ Failed to process profile {profile_id}: {e}")

    return result

def save_results(results, output_file):
    """
    Save processing results to a JSON file.

    Args:
        results (list): List of result dictionaries
        output_file (str): Path to the output JSON file
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {output_file}")
    except Exception as e:
        print(f"\n✗ Error saving results: {e}")

def main():
    """
    Main function to orchestrate the image analysis workflow.
    """
    print("=" * 60)
    print("IMAGE & DATA ANALYSIS - Perceptual Hash Processor")
    print("=" * 60)
    print()

    # Display configuration
    print("Configuration:")
    print(f"  Input File: {INPUT_FILE}")
    print(f"  Output File: {OUTPUT_FILE}")
    print(f"  API Endpoint: {API_ENDPOINT}")
    print(f"  Max Workers: {MAX_WORKERS}")
    print(f"  Worker Secret: {'[SET]' if WORKER_SECRET else '[NOT SET]'}")
    print()

    # Load profiles from JSON
    profiles = load_profiles(INPUT_FILE)

    if not profiles:
        print("✗ No profiles to process!")
        return

    print(f"\nProcessing {len(profiles)} profiles with {MAX_WORKERS} concurrent workers...")
    print("-" * 60)

    # Process profiles concurrently using ThreadPoolExecutor
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_profile = {
            executor.submit(process_profile, profile): profile 
            for profile in profiles
        }

        # Collect results as they complete
        for future in as_completed(future_to_profile):
            result = future.result()
            results.append(result)

    print("-" * 60)

    # Summary statistics
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful

    print(f"\nProcessing Complete!")
    print(f"  ✓ Successful: {successful}/{len(results)}")
    print(f"  ✗ Failed: {failed}/{len(results)}")

    # Save results to file
    save_results(results, OUTPUT_FILE)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()
