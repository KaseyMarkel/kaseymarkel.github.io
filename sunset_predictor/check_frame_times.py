"""
Check if extracted frames are actually the right time apart.
Diagnostic script to verify frame extraction timing.
"""

import subprocess
from pathlib import Path
from datetime import datetime
import json
from PIL import Image
from PIL.ExifTags import TAGS

def get_video_duration(video_path):
    """Get video duration in seconds."""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ], capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip())
    except:
        return None

def get_frame_timestamp_from_video(video_path, timestamp_str):
    """Get the actual timestamp of a frame extracted at a given video time."""
    # Extract frame and check its metadata
    temp_file = Path("/tmp/test_frame.jpg")
    try:
        subprocess.run([
            'ffmpeg', '-ss', timestamp_str, '-i', str(video_path),
            '-frames:v', '1', '-y', str(temp_file)
        ], capture_output=True, timeout=10)
        
        if temp_file.exists():
            # Try to get creation time from file metadata
            stat = temp_file.stat()
            return stat.st_mtime
    except:
        pass
    finally:
        if temp_file.exists():
            temp_file.unlink()
    return None

def check_extracted_frames_for_date(date_str):
    """Check if frames for a date are actually different times."""
    base_dir = Path("data/extracted_frames/sunset")
    timepoints = [-10, -5, 0, 5, 10, 15, 20, 25]
    
    frames = {}
    for tp in timepoints:
        tp_str = f"{tp:+d}min"
        frame_path = base_dir / tp_str / f"sunset_{date_str.replace('-', '')}_{tp_str}.jpg"
        if frame_path.exists():
            # Get file modification time and size
            stat = frame_path.stat()
            img = Image.open(frame_path)
            frames[tp] = {
                "path": frame_path,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "dimensions": img.size
            }
    
    # Check if frames are identical (same file size suggests same content)
    print(f"\nDate: {date_str}")
    print(f"{'Timepoint':<12} {'File Size':<12} {'Dimensions':<15} {'Same as prev?'}")
    print("-" * 60)
    
    prev_size = None
    prev_dims = None
    
    for tp in sorted(frames.keys()):
        info = frames[tp]
        same = ""
        if prev_size is not None:
            if info["size"] == prev_size and info["dimensions"] == prev_dims:
                same = "⚠ SAME!"
            else:
                same = "✓ Different"
        
        print(f"{tp:+3d} min     {info['size']:<12} {str(info['dimensions']):<15} {same}")
        prev_size = info["size"]
        prev_dims = info["dimensions"]
    
    # Check a sample video to see actual compression ratio
    video_dir = Path("data/lhs_timelapses")
    video_files = list(video_dir.glob("lhs_*.mp4"))
    if video_files:
        sample_video = video_files[0]
        duration = get_video_duration(sample_video)
        if duration:
            print(f"\nSample video: {sample_video.name}")
            print(f"  Duration: {duration:.1f} seconds")
            print(f"  Assumed compression: 24 hours = 120 seconds (12:1 ratio)")
            print(f"  Actual compression: 24 hours = {duration:.1f} seconds ({24*60*60/duration:.1f}:1 ratio)")
            if abs(duration - 120) > 10:
                print(f"  ⚠ WARNING: Compression ratio doesn't match assumption!")

def check_all_dates():
    """Check frames for all dates."""
    base_dir = Path("data/extracted_frames/sunset")
    dates_checked = set()
    
    for tp_dir in base_dir.glob("*min"):
        for frame_file in tp_dir.glob("sunset_*.jpg"):
            # Extract date from filename
            date_match = frame_file.stem.split("_")
            if len(date_match) >= 2:
                date_str = date_match[1]  # YYYYMMDD format
                # Convert to YYYY-MM-DD
                if len(date_str) == 8:
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    dates_checked.add(formatted_date)
    
    print(f"Found {len(dates_checked)} dates with extracted frames")
    print("=" * 70)
    
    # Check first 5 dates
    for date_str in sorted(list(dates_checked))[:5]:
        check_extracted_frames_for_date(date_str)

if __name__ == "__main__":
    check_all_dates()

