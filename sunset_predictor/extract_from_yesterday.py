"""
Extract sunset frame from yesterday's LHS timelapse video.
This works with the video we already downloaded.
"""

from pathlib import Path
from datetime import datetime, timedelta
from data_collector import get_sunset_time
import subprocess
import json

def extract_yesterday_sunset():
    """Extract sunset from yesterday's video."""
    video_file = Path("data/lhs_timelapses/yesterdayview.1080p.mp4")
    
    if not video_file.exists():
        print("Video not found. Download it first:")
        print("  python3 download_lhs_timelapse.py --download-yesterday")
        return
    
    # Yesterday's date
    yesterday = datetime.now().date() - timedelta(days=1)
    
    print(f"Extracting sunset for: {yesterday}")
    print(f"Video: {video_file.name}")
    
    # Get sunset time
    sunset_time = get_sunset_time(datetime.combine(yesterday, datetime.min.time()))
    print(f"Sunset time: {sunset_time.strftime('%H:%M:%S %Z')}")
    
    # LHS timelapse: 1440 frames, 1 per minute, starts at 00:01
    # Calculate frame number
    from pytz import timezone
    pacific = timezone('US/Pacific')
    start_time = pacific.localize(datetime.combine(yesterday, datetime.min.time().replace(hour=0, minute=1)))
    
    minutes_from_start = (sunset_time - start_time).total_seconds() / 60
    frame_number = int(minutes_from_start)
    
    print(f"Frame number: {frame_number} (minute {minutes_from_start:.1f} from start)")
    
    # Check ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except:
        print("\n⚠ ffmpeg not installed!")
        print("Install: brew install ffmpeg")
        print("\nOnce installed, run this script again.")
        return
    
    # Extract frame
    output_dir = Path("data/sunset_images_for_grading")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"sunset_{yesterday.strftime('%Y%m%d')}.jpg"
    
    print(f"\nExtracting frame...")
    try:
        subprocess.run([
            'ffmpeg', '-i', str(video_file),
            '-vf', f'select=eq(n\\,{frame_number})',
            '-vframes', '1',
            '-q:v', '2',
            '-y',
            str(output_file)
        ], check=True, capture_output=True)
        
        if output_file.exists():
            print(f"✓ Extracted: {output_file.name}")
            
            # Create/update metadata
            metadata_file = output_dir / "sunset_metadata.json"
            metadata = []
            
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
            
            # Add entry
            entry = {
                "date": yesterday.isoformat(),
                "sunset_time": sunset_time.isoformat(),
                "image_path": str(output_file),
                "quality_score": None,
                "graded": False,
                "source": "LHS_yesterday",
                "frame_number": frame_number
            }
            
            # Check if exists
            existing = False
            for i, item in enumerate(metadata):
                if item.get("date") == entry["date"]:
                    metadata[i] = entry
                    existing = True
                    break
            
            if not existing:
                metadata.append(entry)
            
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✓ Updated metadata: {metadata_file}")
            print(f"\nYou now have {len(metadata)} sunset image(s) ready for grading!")
            print(f"\nTo grade:")
            print(f"  python3 setup_grading.py")
            print(f"  python3 grade_sunsets.py")
            
        else:
            print("✗ Frame extraction failed")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print("Make sure ffmpeg is installed: brew install ffmpeg")

if __name__ == "__main__":
    extract_yesterday_sunset()

