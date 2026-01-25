"""
Process new LHS timelapse videos as they become available.
Run this daily or whenever you download new videos.
"""

from pathlib import Path
from datetime import datetime, timedelta
import json
import subprocess

def process_new_videos(video_dir="data/lhs_timelapses", 
                      output_dir="data/sunset_images_for_grading"):
    """Process any new videos in the directory."""
    video_path = Path(video_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load existing metadata
    metadata_file = output_path / "sunset_metadata.json"
    existing_dates = set()
    
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        existing_dates = {item["date"] for item in metadata if item.get("image_path")}
    else:
        metadata = []
    
    print(f"Found {len(existing_dates)} existing sunset images")
    
    # Find video files
    video_files = sorted(video_path.glob("*.mp4")) + sorted(video_path.glob("*.webm"))
    
    print(f"Found {len(video_files)} video file(s) to process\n")
    
    # Process each video
    from extract_lhs_sunsets import extract_sunset_from_lhs_video
    
    processed = 0
    for video_file in video_files:
        # Try to determine date from filename
        filename = video_file.stem.lower()
        
        if "yesterday" in filename:
            video_date = datetime.now().date() - timedelta(days=1)
        elif "today" in filename:
            video_date = datetime.now().date()
        else:
            # Try to extract date
            import re
            date_match = re.search(r'(\d{8})', filename)
            if date_match:
                video_date = datetime.strptime(date_match.group(1), "%Y%m%d").date()
            else:
                # Use modification date
                mtime = datetime.fromtimestamp(video_file.stat().st_mtime)
                video_date = mtime.date()
        
        date_str = video_date.isoformat()
        
        # Skip if already processed
        if date_str in existing_dates:
            print(f"⏭️  Skipping {video_file.name} (already have sunset for {date_str})")
            continue
        
        print(f"Processing {video_file.name} (date: {date_str})...")
        result = extract_sunset_from_lhs_video(video_file, video_date, output_dir)
        
        if result:
            processed += 1
            existing_dates.add(date_str)
            print(f"  ✓ Extracted sunset\n")
    
    # Reload metadata to get updated count
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        actual_images = [item for item in metadata if item.get("image_path") and Path(item["image_path"]).exists()]
        print(f"✓ Processed {processed} new video(s)")
        print(f"✓ Total sunset images: {len(actual_images)}")
        print(f"\nNext: Run python3 setup_grading.py to update grading folder")
    else:
        print(f"✓ Processed {processed} video(s)")


if __name__ == "__main__":
    process_new_videos()

