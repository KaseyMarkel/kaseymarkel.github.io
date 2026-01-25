"""
Download and process LBNL webcam YouTube timelapse videos.
Extract frames at times ~3 hours before sunset.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import sys
from data_collector import get_sunset_time, BERKELEY_LAT, BERKELEY_LON


def check_yt_dlp():
    """Check if yt-dlp is installed."""
    try:
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False


def install_yt_dlp():
    """Install yt-dlp if not available."""
    print("yt-dlp not found. Installing...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp', '--quiet'])
        print("✓ yt-dlp installed")
        return True
    except Exception as e:
        print(f"✗ Failed to install yt-dlp: {e}")
        print("\nPlease install manually:")
        print("  pip install yt-dlp")
        return False


def download_video(url, output_dir="data/youtube_videos"):
    """Download YouTube video using yt-dlp."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not check_yt_dlp():
        if not install_yt_dlp():
            return None
    
    # Download video
    output_template = str(output_path / "%(title)s.%(ext)s")
    
    print(f"Downloading video from: {url}")
    try:
        subprocess.run([
            'yt-dlp',
            '-f', 'best[height<=720]',  # Get reasonable quality
            '-o', output_template,
            url
        ], check=True)
        
        # Get the actual filename
        result = subprocess.run([
            'yt-dlp',
            '--get-filename',
            '-o', output_template,
            url
        ], capture_output=True, text=True)
        
        filename = result.stdout.strip()
        return Path(filename) if filename else None
        
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e}")
        return None


def extract_frames_from_video(video_path, output_dir, target_times, fps=1):
    """
    Extract frames from video at specific times.
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save frames
        target_times: List of datetime objects for times to extract
        fps: Frames per second to extract (for timelapse, might be 1 frame per hour/day)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not video_path.exists():
        print(f"Video not found: {video_path}")
        return []
    
    # Use ffmpeg to extract frames
    # For timelapse videos, we need to map video time to real time
    # This is tricky - we'll need to know the timelapse speed
    
    print(f"Extracting frames from {video_path.name}...")
    print("Note: For timelapse videos, we need to know the time mapping.")
    print("This script will extract frames, but you may need to manually")
    print("identify which frames correspond to which real-world times.")
    
    # Extract frames at regular intervals first
    metadata = []
    
    # Try to get video duration
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ], capture_output=True, text=True)
        duration = float(result.stdout.strip())
        print(f"Video duration: {duration:.1f} seconds")
    except:
        duration = None
    
    # Extract frames
    frame_pattern = str(output_path / "frame_%06d.jpg")
    
    try:
        subprocess.run([
            'ffmpeg', '-i', str(video_path),
            '-vf', f'fps={fps}',
            '-q:v', '2',  # High quality
            frame_pattern
        ], check=True, capture_output=True)
        
        # List extracted frames
        frames = sorted(output_path.glob("frame_*.jpg"))
        print(f"Extracted {len(frames)} frames")
        
        return frames
        
    except subprocess.CalledProcessError as e:
        print(f"Error extracting frames: {e}")
        print("Make sure ffmpeg is installed:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt-get install ffmpeg")
        return []


def find_lbnl_youtube_channels():
    """Search for LBNL YouTube channels/videos."""
    print("Searching for LBNL webcam YouTube videos...")
    print("\nCommon search terms:")
    print("  - 'LBNL webcam timelapse'")
    print("  - 'Berkeley Lab webcam'")
    print("  - 'LBNL Berkeley timelapse'")
    print("\nPlease search YouTube and provide the video URL(s).")
    print("\nExample URLs:")
    print("  https://www.youtube.com/watch?v=VIDEO_ID")
    print("  https://youtu.be/VIDEO_ID")


def process_timelapse_video(video_url, output_dir="data/lbnl_frames"):
    """
    Download and process a timelapse video.
    Extract frames that correspond to times ~3 hours before sunset.
    """
    print("=" * 60)
    print("LBNL Webcam Timelapse Processor")
    print("=" * 60)
    
    # Download video
    video_path = download_video(video_url)
    if video_path is None:
        return []
    
    print(f"\n✓ Video downloaded: {video_path}")
    
    # For timelapse videos, we need to:
    # 1. Know the start date/time of the timelapse
    # 2. Know the speed (e.g., 1 frame = 1 hour, or 1 frame = 1 day)
    # 3. Map video frames to real-world times
    
    print("\n" + "=" * 60)
    print("IMPORTANT: Timelapse Processing")
    print("=" * 60)
    print("\nTo extract frames at the right times, we need:")
    print("  1. Start date/time of the timelapse")
    print("  2. Timelapse speed (e.g., 1 frame per hour/day)")
    print("  3. Which frames correspond to ~3 hours before sunset")
    print("\nFor now, extracting all frames. You'll need to:")
    print("  1. Identify the start time of the timelapse")
    print("  2. Calculate which frames are ~3 hours before sunset")
    print("  3. Use those frames for training")
    
    # Extract all frames
    frames = extract_frames_from_video(video_path, output_dir, [])
    
    return frames


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download LBNL YouTube timelapse videos")
    parser.add_argument("--url", type=str, help="YouTube video URL")
    parser.add_argument("--search", action="store_true", 
                       help="Show search instructions")
    parser.add_argument("--output-dir", type=str, default="data/lbnl_frames",
                       help="Output directory for frames")
    
    args = parser.parse_args()
    
    if args.search:
        find_lbnl_youtube_channels()
    elif args.url:
        process_timelapse_video(args.url, args.output_dir)
    else:
        print("LBNL YouTube Timelapse Downloader")
        print("=" * 60)
        print("\nUsage:")
        print("  python3 download_youtube_timelapse.py --url <YOUTUBE_URL>")
        print("  python3 download_youtube_timelapse.py --search")
        print("\nExample:")
        print("  python3 download_youtube_timelapse.py --url https://www.youtube.com/watch?v=...")
        print("\nTo find videos, search YouTube for:")
        print("  'LBNL webcam timelapse'")
        print("  'Berkeley Lab webcam'")

