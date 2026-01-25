"""
Extract sunset frames from YouTube timelapse video.
Extracts frames at actual sunset times for aesthetic grading.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from data_collector import get_sunset_time
import subprocess
import sys

def extract_sunsets_from_timelapse(video_url, timelapse_start_date, 
                                  timelapse_speed_hours_per_frame=1,
                                  num_sunsets=300, output_dir="data/sunset_images_for_grading"):
    """
    Extract frames from timelapse at actual sunset times.
    
    Args:
        video_url: YouTube URL
        timelapse_start_date: When timelapse started (YYYY-MM-DD)
        timelapse_speed_hours_per_frame: Real hours per video frame
        num_sunsets: Number of sunsets to extract
        output_dir: Where to save sunset images
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("SUNSET FRAME EXTRACTOR")
    print("=" * 70)
    print(f"\nExtracting {num_sunsets} sunset images from timelapse...")
    print(f"Video: {video_url}")
    print(f"Start date: {timelapse_start_date}")
    print(f"Speed: {timelapse_speed_hours_per_frame} hours per frame")
    
    # Check dependencies
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
    except:
        print("\n⚠ yt-dlp not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp', '--quiet'])
    
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except:
        print("\n⚠ ffmpeg not found. Please install:")
        print("  brew install ffmpeg")
        return
    
    # Download video if needed
    video_dir = Path("data/youtube_videos")
    video_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n[1/3] Downloading video...")
    try:
        result = subprocess.run([
            'yt-dlp', '--dump-json', '--no-download', video_url
        ], capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)
        title = video_info.get('title', 'video').replace('/', '_')
        
        video_file = video_dir / f"{title}.mp4"
        if not video_file.exists():
            for ext in ['webm', 'mkv', 'mp4']:
                test_file = video_dir / f"{title}.{ext}"
                if test_file.exists():
                    video_file = test_file
                    break
            
            if not video_file.exists():
                print("Downloading video (this may take a while)...")
                subprocess.run([
                    'yt-dlp', '-f', 'best[height<=720]',
                    '-o', str(video_dir / f"{title}.%(ext)s"),
                    video_url
                ], check=True)
                
                # Find downloaded file
                for ext in ['mp4', 'webm', 'mkv']:
                    test_file = video_dir / f"{title}.{ext}"
                    if test_file.exists():
                        video_file = test_file
                        break
        
        print(f"✓ Video: {video_file.name}")
    except Exception as e:
        print(f"✗ Error downloading video: {e}")
        return
    
    # Calculate sunset times
    print("\n[2/3] Calculating sunset times...")
    timelapse_start = datetime.strptime(timelapse_start_date, '%Y-%m-%d')
    sunset_times = []
    
    current_date = timelapse_start
    for _ in range(num_sunsets):
        sunset = get_sunset_time(current_date)
        if sunset >= timelapse_start:
            sunset_times.append({
                "date": current_date.date(),
                "sunset_time": sunset,
                "frame_number": None  # Will calculate
            })
        current_date += timedelta(days=1)
    
    print(f"✓ Found {len(sunset_times)} sunset times")
    
    # Calculate frame numbers
    speed_seconds = timelapse_speed_hours_per_frame * 3600
    for item in sunset_times:
        time_diff = (item["sunset_time"] - timelapse_start).total_seconds()
        item["frame_number"] = int(time_diff / speed_seconds)
    
    # Extract frames
    print("\n[3/3] Extracting sunset frames...")
    metadata = []
    
    for i, item in enumerate(sunset_times):
        frame_num = item["frame_number"]
        date_str = item["date"].strftime("%Y%m%d")
        output_file = output_path / f"sunset_{date_str}.jpg"
        
        try:
            # Extract frame using ffmpeg
            subprocess.run([
                'ffmpeg', '-i', str(video_file),
                '-vf', f'select=eq(n\\,{frame_num})',
                '-vframes', '1',
                '-q:v', '2',  # High quality
                str(output_file)
            ], capture_output=True, check=True)
            
            if output_file.exists():
                metadata.append({
                    "date": item["date"].isoformat(),
                    "sunset_time": item["sunset_time"].isoformat(),
                    "image_path": str(output_file),
                    "quality_score": None,
                    "graded": False,
                    "frame_number": frame_num
                })
                print(f"  [{i+1}/{len(sunset_times)}] Extracted: {output_file.name}")
            else:
                print(f"  [{i+1}/{len(sunset_times)}] Failed: {date_str}")
                
        except Exception as e:
            print(f"  [{i+1}/{len(sunset_times)}] Error: {date_str} - {e}")
    
    # Save metadata
    metadata_file = output_path / "sunset_metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Extracted {len(metadata)} sunset images")
    print(f"✓ Saved to: {output_path}")
    print(f"✓ Metadata: {metadata_file}")
    print(f"\nNext: Run python3 setup_grading.py to organize for grading")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract sunset frames from YouTube timelapse")
    parser.add_argument("--url", type=str, required=True,
                       help="YouTube video URL")
    parser.add_argument("--start-date", type=str, required=True,
                       help="Timelapse start date (YYYY-MM-DD)")
    parser.add_argument("--speed", type=float, default=1.0,
                       help="Hours per frame (default: 1.0)")
    parser.add_argument("--num-sunsets", type=int, default=300,
                       help="Number of sunsets to extract")
    parser.add_argument("--output-dir", type=str, 
                       default="data/sunset_images_for_grading",
                       help="Output directory")
    
    args = parser.parse_args()
    
    extract_sunsets_from_timelapse(
        args.url, args.start_date, args.speed, 
        args.num_sunsets, args.output_dir
    )

