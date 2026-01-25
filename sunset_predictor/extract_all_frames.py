"""
Extract multiple frames per video:
1. Midday frame (3 hours before sunset) - for prediction input
2. 8 sunset frames: -10, -5, 0, +5, +10, +15, +20, +25 minutes relative to sun-under-horizon
"""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import json
import re
import csv

from astral import LocationInfo
from astral.sun import sun

BERKELEY_LAT = 37.8715
BERKELEY_LON = -122.2730

def get_sunset_time(date):
    """Get sunset time for a given date in Berkeley."""
    location = LocationInfo("Berkeley", "California", "US/Pacific", BERKELEY_LAT, BERKELEY_LON)
    s = sun(location.observer, date=date.date() if isinstance(date, datetime) else date, tzinfo=location.timezone)
    return s["sunset"]

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

def extract_frame_at_time(video_path, video_date, target_time, output_file):
    """
    Extract frame at specific time from video.
    Videos are ~120 seconds compressed from 24 hours.
    1 second of video = 12 minutes of real time.
    """
    # Calculate minutes from start (00:01) to target time
    from pytz import timezone
    pacific = timezone('US/Pacific')
    start_time = pacific.localize(datetime.combine(video_date, datetime.min.time().replace(hour=0, minute=1)))
    
    if target_time.tzinfo is None:
        target_time = pacific.localize(target_time)
    
    minutes_from_start = (target_time - start_time).total_seconds() / 60
    
    # Convert to video timestamp (minutes / 12 = seconds in video)
    video_timestamp_seconds = minutes_from_start / 12.0
    
    # Format as HH:MM:SS for ffmpeg
    hours = int(video_timestamp_seconds // 3600)
    minutes = int((video_timestamp_seconds % 3600) // 60)
    seconds = int(video_timestamp_seconds % 60)
    timestamp_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Extract frame
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        subprocess.run([
            'ffmpeg', '-ss', timestamp_str,
            '-i', str(video_path),
            '-frames:v', '1',
            '-q:v', '2',
            '-y',
            str(output_path)
        ], check=True, capture_output=True)
        
        return output_path.exists()
    except:
        return False

def extract_all_frames_for_video(video_path, video_date, base_output_dir="data/extracted_frames"):
    """
    Extract all frames for a video:
    - 1 midday frame (3h before sunset)
    - 8 sunset frames at specified times
    """
    video_path = Path(video_path)
    video_date = datetime.strptime(video_date, "%Y-%m-%d").date() if isinstance(video_date, str) else video_date
    
    # Get sunset time
    sunset_time = get_sunset_time(datetime.combine(video_date, datetime.min.time()))
    
    # Sunset frame offsets (minutes relative to sun-under-horizon)
    sunset_offsets = [-10, -5, 0, 5, 10, 15, 20, 25]
    
    extracted = {
        "midday": None,
        "sunset_frames": {}
    }
    
    date_str = video_date.strftime("%Y%m%d")
    
    # Extract midday frame (3 hours before sunset)
    midday_time = sunset_time - timedelta(hours=3)
    midday_file = Path(base_output_dir) / "midday" / f"midday_{date_str}.jpg"
    if extract_frame_at_time(video_path, video_date, midday_time, midday_file):
        extracted["midday"] = str(midday_file)
        print(f"  ✓ Midday frame: {midday_file.name}")
    
    # Extract sunset frames
    for offset in sunset_offsets:
        target_time = sunset_time + timedelta(minutes=offset)
        offset_str = f"{offset:+d}min"
        sunset_file = Path(base_output_dir) / "sunset" / offset_str / f"sunset_{date_str}_{offset_str}.jpg"
        
        if extract_frame_at_time(video_path, video_date, target_time, sunset_file):
            extracted["sunset_frames"][offset] = str(sunset_file)
            print(f"  ✓ Sunset {offset_str}: {sunset_file.name}")
    
    return extracted

def process_all_videos():
    """Process all videos in the directory."""
    videos_dir = Path("data/lhs_timelapses")
    video_files = sorted(videos_dir.glob("lhs_*.mp4"))
    
    print(f"Processing {len(video_files)} videos...")
    print("Extracting:")
    print("  - 1 midday frame per video (3h before sunset)")
    print("  - 8 sunset frames per video (-10 to +25 min)")
    print()
    
    all_extracted = {}
    
    for i, video_file in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] {video_file.name}")
        
        # Extract index number
        match = re.search(r'lhs_(\d+)', video_file.stem)
        if not match:
            print(f"  ✗ Could not parse index from filename")
            continue
        
        index_num = int(match.group(1))
        date_str = get_date_from_index(index_num)
        
        if not date_str:
            print(f"  ✗ Could not find date for index {index_num}")
            continue
        
        video_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Extract all frames
        extracted = extract_all_frames_for_video(video_file, video_date)
        all_extracted[date_str] = {
            "date": date_str,
            "video_file": str(video_file),
            "index": index_num,
            **extracted
        }
    
    # Save metadata
    metadata_file = Path("data/extracted_frames/metadata.json")
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_file, "w") as f:
        json.dump(all_extracted, f, indent=2)
    
    print(f"\n✓ Extraction complete!")
    print(f"✓ Metadata saved: {metadata_file}")
    print(f"\nSummary:")
    print(f"  Videos processed: {len(all_extracted)}")
    print(f"  Midday frames: {sum(1 for v in all_extracted.values() if v.get('midday'))}")
    print(f"  Sunset frames: {sum(len(v.get('sunset_frames', {})) for v in all_extracted.values())}")
    
    return all_extracted

if __name__ == "__main__":
    process_all_videos()


