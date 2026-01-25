"""
Fix frame extraction to ensure frames are actually different times.
Use frame-based extraction instead of timestamp-based for better precision.
"""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import json
import re
import csv

from astral import LocationInfo
from astral.sun import sun
from pytz import timezone

BERKELEY_LAT = 37.8715
BERKELEY_LON = -122.2730

def get_video_info(video_path):
    """Get video frame rate and duration."""
    try:
        # Get frame rate
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ], capture_output=True, text=True, timeout=10)
        
        frame_rate_str = result.stdout.strip()
        if '/' in frame_rate_str:
            num, den = map(int, frame_rate_str.split('/'))
            fps = num / den
        else:
            fps = float(frame_rate_str)
        
        # Get duration
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ], capture_output=True, text=True, timeout=10)
        
        duration = float(result.stdout.strip())
        
        return fps, duration
    except Exception as e:
        print(f"  Error getting video info: {e}")
        return None, None

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
                    from parse_video_dates import parse_date_from_title
                    date = parse_date_from_title(row['Title'])
                    if date:
                        return date.isoformat()
    except:
        pass
    return None

def extract_frame_at_time_precise(video_path, video_date, target_time, output_file, fps):
    """
    Extract frame at specific time using frame number for precision.
    Videos are ~120 seconds compressed from 24 hours.
    1 second of video = 12 minutes of real time = 720 seconds.
    So: frame_number = (minutes_from_start * 60) / (12 * 60) * fps
        = minutes_from_start * fps / 12
    """
    pacific = timezone('US/Pacific')
    start_time = pacific.localize(datetime.combine(video_date, datetime.min.time().replace(hour=0, minute=1)))
    
    if target_time.tzinfo is None:
        target_time = pacific.localize(target_time)
    
    minutes_from_start = (target_time - start_time).total_seconds() / 60
    
    # Calculate frame number: minutes_from_start * fps / 12
    # (12 minutes per second of video)
    frame_number = int(minutes_from_start * fps / 12.0)
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Extract using frame number for precision
        subprocess.run([
            'ffmpeg', '-i', str(video_path),
            '-vf', f'select=eq(n\\,{frame_number})',
            '-frames:v', '1',
            '-q:v', '2',
            '-y',
            str(output_path)
        ], check=True, capture_output=True, timeout=30)
        
        return output_path.exists()
    except Exception as e:
        print(f"    Error extracting frame {frame_number}: {e}")
        return False

def re_extract_frames_for_video(video_path, video_date, base_output_dir="data/extracted_frames"):
    """Re-extract frames using precise frame-based method."""
    video_path = Path(video_path)
    video_date = datetime.strptime(video_date, "%Y-%m-%d").date() if isinstance(video_date, str) else video_date
    
    # Get video info
    fps, duration = get_video_info(video_path)
    if fps is None:
        print(f"  ✗ Could not get video info")
        return None
    
    print(f"  Video: {fps:.2f} fps, {duration:.1f}s duration")
    
    # Get sunset time
    sunset_time = get_sunset_time(datetime.combine(video_date, datetime.min.time()))
    
    # Sunset frame offsets
    sunset_offsets = [-10, -5, 0, 5, 10, 15, 20, 25]
    
    extracted = {
        "midday": None,
        "sunset_frames": {}
    }
    
    date_str = video_date.strftime("%Y%m%d")
    
    # Extract midday frame
    midday_time = sunset_time - timedelta(hours=3)
    midday_file = Path(base_output_dir) / "midday" / f"midday_{date_str}.jpg"
    if extract_frame_at_time_precise(video_path, video_date, midday_time, midday_file, fps):
        extracted["midday"] = str(midday_file)
        print(f"  ✓ Midday frame")
    
    # Extract sunset frames
    for offset in sunset_offsets:
        target_time = sunset_time + timedelta(minutes=offset)
        offset_str = f"{offset:+d}min"
        sunset_file = Path(base_output_dir) / "sunset" / offset_str / f"sunset_{date_str}_{offset_str}.jpg"
        
        if extract_frame_at_time_precise(video_path, video_date, target_time, sunset_file, fps):
            extracted["sunset_frames"][offset] = str(sunset_file)
            print(f"  ✓ Sunset {offset_str}")
    
    return extracted

def fix_all_extractions():
    """Re-extract all frames with precise method."""
    videos_dir = Path("data/lhs_timelapses")
    video_files = sorted(videos_dir.glob("lhs_*.mp4"))
    
    print(f"Re-extracting frames for {len(video_files)} videos...")
    print("Using frame-based extraction for precision")
    print()
    
    fixed_count = 0
    
    for i, video_file in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] {video_file.name}")
        
        # Extract index number
        match = re.search(r'lhs_(\d+)', video_file.stem)
        if not match:
            print(f"  ✗ Could not parse index")
            continue
        
        index_num = int(match.group(1))
        date_str = get_date_from_index(index_num)
        
        if not date_str:
            print(f"  ✗ Could not find date")
            continue
        
        video_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Re-extract frames
        extracted = re_extract_frames_for_video(video_file, video_date)
        if extracted:
            fixed_count += 1
    
    print(f"\n✓ Re-extraction complete!")
    print(f"  Fixed: {fixed_count} videos")

if __name__ == "__main__":
    fix_all_extractions()
