"""
Download timelapse videos/images from Lawrence Hall of Science webcam.
https://lawrencehallofscience.org/play/view/
"""

import requests
from pathlib import Path
from datetime import datetime, timedelta
from data_collector import get_sunset_time
import json
import re
from bs4 import BeautifulSoup

LHS_BASE_URL = "https://lawrencehallofscience.org/play/view/"


def find_timelapse_urls():
    """Find timelapse video URLs from the LHS webcam page."""
    print("Accessing Lawrence Hall of Science webcam page...")
    
    try:
        response = requests.get(LHS_BASE_URL, timeout=10)
        response.raise_for_status()
        
        # Parse HTML to find timelapse video URLs
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for video tags
        videos = soup.find_all('video')
        video_urls = []
        
        for video in videos:
            source = video.find('source')
            if source and source.get('src'):
                url = source.get('src')
                if not url.startswith('http'):
                    url = LHS_BASE_URL.rstrip('/') + '/' + url.lstrip('/')
                video_urls.append(url)
        
        # Also look for links to timelapse archive
        archive_links = soup.find_all('a', href=re.compile(r'timelapse|archive', re.I))
        
        print(f"Found {len(video_urls)} video(s) and {len(archive_links)} archive link(s)")
        
        return video_urls, archive_links
        
    except Exception as e:
        print(f"Error accessing page: {e}")
        return [], []


def download_timelapse_video(video_url, output_dir="data/lhs_timelapses"):
    """Download a timelapse video."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading: {video_url}")
    
    try:
        response = requests.get(video_url, timeout=30, stream=True)
        response.raise_for_status()
        
        # Determine filename
        filename = video_url.split('/')[-1]
        if not filename.endswith(('.mp4', '.webm', '.mov')):
            filename = f"timelapse_{datetime.now().strftime('%Y%m%d')}.mp4"
        
        filepath = output_path / filename
        
        # Download
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Saved: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"✗ Error downloading: {e}")
        return None


def extract_sunsets_from_lhs_timelapse(video_path, num_sunsets=300, 
                                      output_dir="data/sunset_images_for_grading"):
    """
    Extract sunset frames from LHS timelapse video.
    LHS timelapses are 1440 frames (1 per minute, 24 hours).
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not Path(video_path).exists():
        print(f"Video not found: {video_path}")
        return
    
    print(f"Extracting sunset frames from: {Path(video_path).name}")
    print("LHS timelapses: 1440 frames = 24 hours (1 frame per minute)")
    
    # Get video info
    try:
        import subprocess
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ], capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        fps = 1440 / duration  # 1440 frames total
        print(f"Video duration: {duration:.1f} seconds")
        print(f"Effective FPS: {fps:.3f}")
    except:
        fps = 1.0  # Assume 1 frame per minute
        print("Using default: 1 frame per minute")
    
    # Calculate sunset times and frame numbers
    # Start from 300 days ago
    start_date = datetime.now() - timedelta(days=num_sunsets)
    sunset_times = []
    
    current_date = start_date
    for _ in range(num_sunsets):
        sunset = get_sunset_time(current_date)
        sunset_times.append({
            "date": current_date.date(),
            "sunset_time": sunset
        })
        current_date += timedelta(days=1)
    
    # For LHS timelapse, we need to know:
    # 1. What date does the video start?
    # 2. Each frame = 1 minute of real time
    
    print(f"\nFound {len(sunset_times)} sunset times")
    print("\nNote: To extract frames, we need to know:")
    print("  1. What date does this timelapse video cover?")
    print("  2. Which frame corresponds to midnight of that date?")
    print("\nFor now, extracting all frames. You can manually identify sunset frames.")
    
    # Extract all frames (user can identify which are sunsets)
    frames_dir = output_path / "all_frames"
    frames_dir.mkdir(exist_ok=True)
    
    try:
        subprocess.run([
            'ffmpeg', '-i', str(video_path),
            '-vf', 'fps=1/60',  # Extract 1 frame per minute
            '-q:v', '2',
            str(frames_dir / 'frame_%06d.jpg')
        ], check=True, capture_output=True)
        
        frames = sorted(frames_dir.glob("frame_*.jpg"))
        print(f"\n✓ Extracted {len(frames)} frames to {frames_dir}")
        print(f"\nNext steps:")
        print(f"  1. Identify which frames are sunsets")
        print(f"  2. Copy sunset frames to {output_path}")
        print(f"  3. Name them: sunset_YYYYMMDD.jpg")
        print(f"  4. Run: python3 setup_grading.py")
        
    except Exception as e:
        print(f"Error extracting frames: {e}")
        print("Make sure ffmpeg is installed: brew install ffmpeg")


def download_yesterday_timelapse(output_dir="data/lhs_timelapses"):
    """Download yesterday's timelapse from LHS."""
    print("Attempting to download yesterday's timelapse from LHS...")
    
    # Try to find the video URL
    video_urls, archive_links = find_timelapse_urls()
    
    if video_urls:
        print(f"Found {len(video_urls)} video URL(s)")
        for url in video_urls:
            video_path = download_timelapse_video(url, output_dir)
            if video_path:
                return video_path
    else:
        print("Could not find video URLs automatically.")
        print("\nManual steps:")
        print("1. Visit: https://lawrencehallofscience.org/play/view/")
        print("2. Right-click on 'Yesterday' video")
        print("3. Save video as...")
        print("4. Place in data/lhs_timelapses/")
        print("5. Run: python3 extract_sunsets_from_lhs_timelapse.py")
    
    return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download LHS timelapse videos")
    parser.add_argument("--download-yesterday", action="store_true",
                       help="Download yesterday's timelapse")
    parser.add_argument("--video-file", type=str, default=None,
                       help="Path to existing timelapse video file")
    parser.add_argument("--extract-sunsets", action="store_true",
                       help="Extract sunset frames from video")
    parser.add_argument("--num-sunsets", type=int, default=300,
                       help="Number of sunsets to extract")
    
    args = parser.parse_args()
    
    if args.download_yesterday:
        video_path = download_yesterday_timelapse()
        if video_path and args.extract_sunsets:
            extract_sunsets_from_lhs_timelapse(video_path, args.num_sunsets)
    elif args.video_file and args.extract_sunsets:
        extract_sunsets_from_lhs_timelapse(args.video_file, args.num_sunsets)
    else:
        print("LHS Timelapse Downloader")
        print("=" * 60)
        print("\nUsage:")
        print("  # Download yesterday's timelapse:")
        print("  python3 download_lhs_timelapse.py --download-yesterday")
        print("\n  # Extract sunsets from existing video:")
        print("  python3 download_lhs_timelapse.py --video-file <VIDEO> --extract-sunsets")
        print("\n  # Or manually:")
        print("  1. Visit https://lawrencehallofscience.org/play/view/")
        print("  2. Download timelapse video(s)")
        print("  3. Run extraction script")

