"""
Download 300 timelapse videos from LHS and extract sunset frames.
"""

import requests
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import json
import time

LHS_BASE = "https://www.ocf.berkeley.edu/~thelawrence/timelapse/"


def download_lhs_video(date, output_dir="data/lhs_timelapses"):
    """
    Try to download LHS timelapse for a specific date.
    Tries multiple URL patterns.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    date_str = date.strftime("%Y%m%d")
    
    # Try different URL patterns
    url_patterns = [
        f"{LHS_BASE}{date_str}view.1080p.mp4",
        f"{LHS_BASE}view{date_str}.1080p.mp4",
        f"{LHS_BASE}{date_str}.1080p.mp4",
        f"{LHS_BASE}{date_str}view.mp4",
    ]
    
    for url in url_patterns:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                # Download it
                print(f"  Downloading: {date_str}")
                video_response = requests.get(url, timeout=60, stream=True)
                video_response.raise_for_status()
                
                filename = f"lhs_{date_str}.mp4"
                filepath = output_path / filename
                
                with open(filepath, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                if filepath.exists() and filepath.stat().st_size > 1000:
                    print(f"    ✓ Saved: {filename}")
                    return filepath
        except:
            continue
    
    return None


def extract_sunset_frame(video_path, date, output_dir="data/sunset_images_for_grading"):
    """Extract sunset frame from video using ffmpeg."""
    from data_collector import get_sunset_time
    from pytz import timezone
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get sunset time
    sunset_time = get_sunset_time(datetime.combine(date, datetime.min.time()))
    
    # Calculate frame number (LHS: 1440 frames, 1 per minute, starts 00:01)
    pacific = timezone('US/Pacific')
    start_time = pacific.localize(datetime.combine(date, datetime.min.time().replace(hour=0, minute=1)))
    minutes_from_start = (sunset_time - start_time).total_seconds() / 60
    frame_number = int(minutes_from_start)
    
    # Extract frame
    output_file = output_path / f"sunset_{date.strftime('%Y%m%d')}.jpg"
    
    try:
        subprocess.run([
            'ffmpeg', '-i', str(video_path),
            '-vf', f'select=eq(n\\,{frame_number})',
            '-vframes', '1',
            '-q:v', '2',
            '-y',  # Overwrite
            str(output_file)
        ], check=True, capture_output=True)
        
        if output_file.exists():
            return output_file
    except Exception as e:
        print(f"    ✗ Extraction failed: {e}")
    
    return None


def download_and_extract_300_sunsets(num_sunsets=300, start_date=None):
    """Download 300 timelapse videos and extract sunset frames."""
    if start_date is None:
        start_date = datetime.now().date() - timedelta(days=1)
    
    print("=" * 70)
    print("DOWNLOADING 300 SUNSET IMAGES FROM LHS TIMELAPSES")
    print("=" * 70)
    print(f"\nStarting from: {start_date}")
    print(f"Target: {num_sunsets} sunset images")
    print(f"\nNote: This will attempt to download videos from LHS archive.")
    print("Not all dates may have videos available.\n")
    
    videos_dir = Path("data/lhs_timelapses")
    videos_dir.mkdir(parents=True, exist_ok=True)
    
    sunsets_dir = Path("data/sunset_images_for_grading")
    sunsets_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded = 0
    extracted = 0
    current_date = start_date
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        ffmpeg_available = True
    except:
        ffmpeg_available = False
        print("⚠ ffmpeg not found - will download videos but can't extract frames")
        print("  Install: brew install ffmpeg\n")
    
    metadata = []
    
    for i in range(num_sunsets):
        print(f"\n[{i+1}/{num_sunsets}] Date: {current_date}")
        
        # Check if we already have this sunset
        sunset_file = sunsets_dir / f"sunset_{current_date.strftime('%Y%m%d')}.jpg"
        if sunset_file.exists():
            print("  ✓ Already have sunset image")
            extracted += 1
            current_date -= timedelta(days=1)
            continue
        
        # Try to download video
        video_path = download_lhs_video(current_date)
        
        if video_path:
            downloaded += 1
            
            # Extract sunset frame
            if ffmpeg_available:
                sunset_img = extract_sunset_frame(video_path, current_date)
                if sunset_img:
                    extracted += 1
                    print(f"    ✓ Extracted sunset frame")
                    
                    # Add to metadata
                    sunset_time = get_sunset_time(datetime.combine(current_date, datetime.min.time()))
                    metadata.append({
                        "date": current_date.isoformat(),
                        "sunset_time": sunset_time.isoformat(),
                        "image_path": str(sunset_img),
                        "quality_score": None,
                        "graded": False,
                        "source": "LHS_timelapse"
                    })
        else:
            print(f"  ✗ No video found for {current_date}")
        
        current_date -= timedelta(days=1)
        
        # Rate limiting
        time.sleep(0.5)
        
        # Progress update every 10
        if (i + 1) % 10 == 0:
            print(f"\n  Progress: {downloaded} videos downloaded, {extracted} sunsets extracted")
    
    # Save metadata
    metadata_file = sunsets_dir / "sunset_metadata.json"
    if metadata:
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"\n✓ Saved metadata: {metadata_file}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Videos downloaded: {downloaded}")
    print(f"Sunset images extracted: {extracted}")
    print(f"\nNext steps:")
    if extracted > 0:
        print(f"  1. Review images in: {sunsets_dir}")
        print(f"  2. Run: python3 setup_grading.py")
        print(f"  3. Grade sunsets: python3 grade_sunsets.py")
    else:
        print(f"  Need ffmpeg to extract frames: brew install ffmpeg")
        print(f"  Then run this script again")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download 300 sunsets from LHS")
    parser.add_argument("--num-sunsets", type=int, default=300,
                       help="Number of sunsets to collect")
    parser.add_argument("--start-date", type=str, default=None,
                       help="Start date (YYYY-MM-DD), default: yesterday")
    
    args = parser.parse_args()
    
    start_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    
    download_and_extract_300_sunsets(args.num_sunsets, start_date)

