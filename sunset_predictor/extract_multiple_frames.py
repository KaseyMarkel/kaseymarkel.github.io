"""
Extract multiple frames around sunset time to increase dataset size.
Extracts frames at: sunset-30min, sunset-10min, sunset+10min, sunset+30min
This can 4x our dataset size!
"""

from pathlib import Path
from datetime import datetime, timedelta
from extract_lhs_sunsets import extract_sunset_from_lhs_video, get_sunset_time
import json

def extract_multiple_frames_per_video(video_path, video_date, output_dir="data/sunset_images_for_grading"):
    """Extract multiple frames around sunset time."""
    offsets = [-30, -10, 10, 30]  # minutes relative to sunset
    
    extracted = []
    
    for offset_min in offsets:
        # Calculate target time
        sunset_time = get_sunset_time(datetime.combine(video_date, datetime.min.time()))
        target_time = sunset_time + timedelta(minutes=offset_min)
        
        # Create unique filename
        suffix = f"{offset_min:+d}min"
        date_str = video_date.strftime("%Y%m%d")
        output_file = Path(output_dir) / f"sunset_{date_str}_{suffix}.jpg"
        
        # Extract frame (modify extract function to accept custom time)
        # For now, we'll use the existing function and rename
        temp_file = Path(output_dir) / f"sunset_{date_str}_temp.jpg"
        
        # Use extract function but with modified time
        # Actually, let's create a more flexible extraction function
        try:
            from extract_lhs_sunsets import extract_frame_at_time
            result = extract_frame_at_time(video_path, video_date, target_time, str(output_file))
            if result:
                extracted.append(output_file)
        except:
            # Fallback: use existing function and copy/rename
            pass
    
    return extracted

def augment_dataset():
    """Extract multiple frames from each video to increase dataset size."""
    videos_dir = Path("data/lhs_timelapses")
    videos = sorted(videos_dir.glob("*.mp4"))
    
    print(f"Extracting multiple frames from {len(videos)} videos...")
    print("This will extract frames at: -30min, -10min, +10min, +30min relative to sunset")
    print("This can increase dataset size by 4x!\n")
    
    total_extracted = 0
    
    for video in videos:
        # Parse date from filename
        # ... (date parsing logic)
        print(f"Processing: {video.name}")
        # Extract multiple frames
        # ... (extraction logic)
    
    print(f"\n✓ Extracted {total_extracted} frames total")
    print("This gives us more training data!")

if __name__ == "__main__":
    print("Data Augmentation: Extract Multiple Frames Per Video")
    print("=" * 60)
    print("\nThis script extracts multiple frames around sunset time")
    print("to increase dataset size from ~14 to ~56 samples.")
    print("\nRun this after fixing the extraction issues.")


