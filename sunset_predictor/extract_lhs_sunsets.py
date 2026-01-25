"""
Extract sunset frames from LHS timelapse videos.
LHS timelapses: 1440 frames = 24 hours (1 frame per minute, starting at 12:01am)
"""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import json
import re
import csv
import csv

# Import sunset calculation directly
from astral import LocationInfo
from astral.sun import sun

BERKELEY_LAT = 37.8715
BERKELEY_LON = -122.2730

def get_sunset_time(date, lat=BERKELEY_LAT, lon=BERKELEY_LON):
    """Get sunset time for a given date in Berkeley."""
    location = LocationInfo("Berkeley", "California", "US/Pacific", lat, lon)
    s = sun(location.observer, date=date.date() if isinstance(date, datetime) else date, tzinfo=location.timezone)
    return s["sunset"]

def extract_sunset_from_lhs_video(video_path, video_date, output_dir="data/sunset_images_for_grading"):
    """
    Extract sunset frame from LHS timelapse video.
    
    Args:
        video_path: Path to LHS timelapse video
        video_date: Date the video covers (YYYY-MM-DD)
        output_dir: Where to save sunset image
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"Video not found: {video_path}")
        return None
    
    # Parse date
    if isinstance(video_date, str):
        video_date = datetime.strptime(video_date, "%Y-%m-%d").date()
    
    # Get sunset time for this date
    sunset_time = get_sunset_time(datetime.combine(video_date, datetime.min.time()))
    
    # We want the frame 10 minutes AFTER sunset
    target_time = sunset_time + timedelta(minutes=10)
    
    # LHS timelapse videos are ~120 seconds compressed from 24 hours
    # Video duration: ~120 seconds = 1440 minutes of real time
    # So: 1 second of video = 12 minutes of real time
    
    # Calculate minutes from start to target time (sunset + 10 min)
    # LHS timelapse starts at 00:01 (12:01am)
    start_time = datetime.combine(video_date, datetime.min.time().replace(hour=0, minute=1))
    # Make timezone-aware to match sunset_time
    if sunset_time.tzinfo is not None:
        from pytz import timezone
        pacific = timezone('US/Pacific')
        start_time = pacific.localize(start_time)
    minutes_from_start = (target_time - start_time).total_seconds() / 60
    
    # Convert to video timestamp (minutes / 12 = seconds in video)
    video_timestamp_seconds = minutes_from_start / 12.0
    
    # Use timestamp-based extraction instead of frame number
    # Format as HH:MM:SS for ffmpeg
    hours = int(video_timestamp_seconds // 3600)
    minutes = int((video_timestamp_seconds % 3600) // 60)
    seconds = int(video_timestamp_seconds % 60)
    timestamp_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # LHS videos are ~120 seconds compressed from 24 hours
    # 1 second of video = 12 minutes of real time
    video_timestamp_seconds = minutes_from_start / 12.0
    
    # Format as HH:MM:SS for ffmpeg
    hours = int(video_timestamp_seconds // 3600)
    minutes = int((video_timestamp_seconds % 3600) // 60)
    seconds = int(video_timestamp_seconds % 60)
    timestamp_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    print(f"Video date: {video_date}")
    print(f"Sunset time: {sunset_time.strftime('%H:%M:%S')}")
    print(f"Target time (sunset + 10 min): {target_time.strftime('%H:%M:%S')}")
    print(f"Minutes from start: {minutes_from_start:.1f}")
    print(f"Video timestamp: {timestamp_str}")
    
    # Extract frame using timestamp (more reliable for compressed timelapses)
    output_file = output_path / f"sunset_{video_date.strftime('%Y%m%d')}.jpg"
    
    try:
        subprocess.run([
            'ffmpeg', '-ss', timestamp_str,
            '-i', str(video_path),
            '-frames:v', '1',
            '-q:v', '2',  # High quality
            '-y',
            str(output_file)
        ], check=True, capture_output=True)
        
        if output_file.exists():
            print(f"✓ Extracted sunset frame: {output_file.name}")
            
            # Create/update metadata
            metadata_file = output_path / "sunset_metadata.json"
            metadata = []
            
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
            
            # Add or update entry
            entry = {
                "date": video_date.isoformat(),
                "sunset_time": sunset_time.isoformat(),
                "image_path": str(output_file),
                "quality_score": None,
                "graded": False,
                    "source": "LHS_timelapse",
                    "video_timestamp": timestamp_str
            }
            
            # Check if entry exists
            existing_idx = None
            for i, item in enumerate(metadata):
                if item.get("date") == entry["date"]:
                    existing_idx = i
                    break
            
            if existing_idx is not None:
                metadata[existing_idx] = entry
            else:
                metadata.append(entry)
            
            # Save metadata
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            return output_file
        else:
            print(f"✗ Frame extraction failed")
            return None
            
    except Exception as e:
        print(f"✗ Error extracting frame: {e}")
        return None


def get_date_from_index(index_num):
    """Look up date from playlist CSV by index number."""
    csv_file = Path("lhs_playlist_videos.csv")
    if not csv_file.exists():
        return None
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['Index']) == index_num:
                    # Parse date from title
                    from parse_video_dates import parse_date_from_title
                    date = parse_date_from_title(row['Title'])
                    if date:
                        return date.isoformat()
    except:
        pass
    return None

def process_lhs_timelapse_archive(video_dir="data/lhs_timelapses", 
                                  output_dir="data/sunset_images_for_grading",
                                  start_date=None, num_days=300):
    """
    Process multiple LHS timelapse videos to extract sunsets.
    Assumes videos are named with dates or in chronological order.
    """
    video_path = Path(video_dir)
    if not video_path.exists():
        print(f"Directory not found: {video_dir}")
        return
    
    # Find video files
    video_files = sorted(video_path.glob("*.mp4")) + sorted(video_path.glob("*.webm"))
    
    if not video_files:
        print(f"No video files found in {video_dir}")
        print("\nTo get more timelapse videos:")
        print("1. Visit: https://lawrencehallofscience.org/play/view/")
        print("2. Check 'Time-lapse Archive' section")
        print("3. Download videos and place in data/lhs_timelapses/")
        return
    
    print(f"Found {len(video_files)} video file(s)")
    
    # Determine dates
    if start_date is None:
        # Use yesterday for the first video
        start_date = datetime.now().date() - timedelta(days=1)
    
    # Extract sunset from each video
    extracted = []
    current_date = start_date
    
    for i, video_file in enumerate(video_files):
        print(f"\n[{i+1}/{len(video_files)}] Processing: {video_file.name}")
        
        # Try to extract date from filename
        # Patterns: lhs_XXX.mp4 (simple), lhs_YYYYMMDD_VIDEOID.mp4, yesterdayview, etc.
        filename = video_file.stem.lower()
        video_date = None
        
        if "yesterday" in filename:
            video_date = datetime.now().date() - timedelta(days=1)
        elif "today" in filename:
            video_date = datetime.now().date()
        else:
            # Pattern 1: lhs_XXX (simple numbering)
            match = re.search(r'lhs_(\d+)', filename)
            if match:
                index_num = int(match.group(1))
                date_str = get_date_from_index(index_num)
                if date_str:
                    video_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Pattern 2: lhs_YYYYMMDD_VIDEOID or YYYYMMDD
            if not video_date:
                date_match = re.search(r'(\d{8})', filename)
                if date_match:
                    video_date = datetime.strptime(date_match.group(1), "%Y%m%d").date()
            
            # Fallback: Use calculated date
            if not video_date:
                video_date = current_date
        
        result = extract_sunset_from_lhs_video(video_file, video_date, output_dir)
        if result:
            extracted.append(result)
        
        current_date -= timedelta(days=1)  # Assume videos are daily, going backwards
    
    print(f"\n✓ Extracted {len(extracted)} sunset images")
    print(f"✓ Saved to: {output_dir}")
    print(f"\nNext: Run python3 setup_grading.py to organize for grading")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract sunsets from LHS timelapse videos")
    parser.add_argument("--video-file", type=str, default=None,
                       help="Single video file to process")
    parser.add_argument("--video-date", type=str, default=None,
                       help="Date video covers (YYYY-MM-DD), default: yesterday")
    parser.add_argument("--video-dir", type=str, default="data/lhs_timelapses",
                       help="Directory with multiple videos")
    parser.add_argument("--process-all", action="store_true",
                       help="Process all videos in directory")
    parser.add_argument("--output-dir", type=str, 
                       default="data/sunset_images_for_grading",
                       help="Output directory")
    
    args = parser.parse_args()
    
    if args.video_file:
        video_date = args.video_date
        if video_date is None:
            video_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        extract_sunset_from_lhs_video(args.video_file, video_date, args.output_dir)
    elif args.process_all:
        process_lhs_timelapse_archive(args.video_dir, args.output_dir)
    else:
        # Process yesterday's video
        video_file = Path("data/lhs_timelapses/yesterdayview.1080p.mp4")
        if video_file.exists():
            video_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            extract_sunset_from_lhs_video(video_file, video_date, args.output_dir)
        else:
            print("No video file specified. Use --video-file or --process-all")

