#!/bin/bash
# Setup script for downloading YouTube timelapses

echo "Setting up dependencies for YouTube timelapse processing..."
echo ""

# Check Python
python3 --version || { echo "Error: Python 3 not found"; exit 1; }

# Install yt-dlp
echo "Installing yt-dlp..."
python3 -m pip install yt-dlp --quiet

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "⚠ ffmpeg not found. Please install it:"
    echo "  macOS: brew install ffmpeg"
    echo "  Linux: sudo apt-get install ffmpeg"
    echo ""
    echo "After installing, run this script again or proceed manually."
else
    echo "✓ ffmpeg found"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To download a timelapse video:"
echo "  python3 process_timelapse.py --url <YOUTUBE_URL> --start-date <YYYY-MM-DD>"

