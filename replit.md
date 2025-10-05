# Image & Data Analysis - College Group Project

## Overview
Python-based image analysis component for a college group project. This script processes profile images, computes perceptual hashes using the imagehash library, and sends results to a backend API endpoint with concurrent processing support.

## Purpose
Part of a larger group project - handles the "Image & Data Analysis" component:
1. Downloads profile images from URLs provided in JSON format
2. Computes perceptual hash (pHash) for each image
3. Sends results to backend API with optional authentication
4. Saves results locally for logging and verification

## Recent Changes
- **October 5, 2025**: Initial project setup
  - Created main image analyzer script with concurrent processing
  - Added sample profiles.json with example data
  - Configured environment variables via .env
  - Set up Python dependencies (imagehash, Pillow, requests, python-dotenv)
  - Implemented ThreadPoolExecutor for parallel image processing

## Project Architecture

### Core Files
- `image_analyzer.py` - Main script with image processing logic
- `profiles.json` - Sample input file with profile data (id, profile_image_url)
- `.env` - Configuration file (API endpoint, worker secret, file paths)
- `.env.example` - Template for environment variables
- `results.json` - Output file with computed hashes and API responses

### Key Features
- Concurrent image processing using ThreadPoolExecutor
- Perceptual hash (pHash) computation using imagehash library
- REST API integration with optional X-WORKER-SECRET header
- Comprehensive error handling and logging
- Beginner-friendly code with extensive comments

### Dependencies
- **imagehash** - Perceptual hashing library
- **Pillow** - Image processing
- **requests** - HTTP requests for image download and API calls
- **python-dotenv** - Environment variable management

## How to Run

### Setup
1. Copy `.env.example` to `.env` and configure:
   - Set your backend API endpoint URL
   - Add worker secret if required
   - Adjust concurrent workers if needed

2. Prepare your profiles.json with actual data:
   ```json
   [
     {
       "id": "your-uuid-here",
       "profile_image_url": "https://example.com/image.jpg"
     }
   ]
   ```

3. Run the script:
   ```bash
   python image_analyzer.py
   ```

### Expected Output
- Console progress showing download, hash computation, and API submission
- `results.json` file with all results and timestamps
- Summary statistics showing success/failure counts

## Configuration Options
- `API_ENDPOINT` - Backend API URL for POST requests
- `WORKER_SECRET` - Optional authentication header value
- `INPUT_FILE` - Input JSON file path (default: profiles.json)
- `OUTPUT_FILE` - Output JSON file path (default: results.json)
- `MAX_WORKERS` - Number of concurrent threads (default: 5)
