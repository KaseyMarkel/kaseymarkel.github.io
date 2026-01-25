#!/bin/bash
# Script to download and process LBNL YouTube timelapse

set -e

echo "LBNL YouTube Timelapse Processor"
echo "================================"
echo ""

# Check dependencies
echo "Checking dependencies..."

if ! command -v yt-dlp &> /dev/null; then
    echo "Installing yt-dlp..."
    python3 -m pip install yt-dlp --quiet
fi

if ! command -v ffmpeg &> /dev/null; then
    echo "⚠ ffmpeg not found. Please install it first:"
    echo "   brew install ffmpeg"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✓ All dependencies installed"
echo ""

# Get YouTube URL from user
if [ -z "$1" ]; then
    echo "Usage: ./run_youtube_download.sh <YOUTUBE_URL> [START_DATE] [SPEED]"
    echo ""
    echo "Example:"
    echo "  ./run_youtube_download.sh https://www.youtube.com/watch?v=abc123 2024-01-01 1.0"
    echo ""
    echo "Parameters:"
    echo "  YOUTUBE_URL: Full YouTube video URL"
    echo "  START_DATE: When timelapse started (YYYY-MM-DD), default: 2024-01-01"
    echo "  SPEED: Hours per frame, default: 1.0"
    echo ""
    exit 1
fi

YOUTUBE_URL=$1
START_DATE=${2:-"2024-01-01"}
SPEED=${3:-"1.0"}

echo "Processing video: $YOUTUBE_URL"
echo "Start date: $START_DATE"
echo "Speed: $SPEED hours per frame"
echo ""

# Run the processor
python3 process_timelapse.py \
    --url "$YOUTUBE_URL" \
    --start-date "$START_DATE" \
    --speed "$SPEED" \
    --days 365

echo ""
echo "Done! Check data/lbnl_frames/ for extracted frames."

