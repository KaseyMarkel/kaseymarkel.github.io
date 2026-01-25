"""
Process YouTube timelapse videos to extract frames at sunset times.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import sys
from data_collector import get_sunset_time


def check_dependencies():
    """Check if required tools are installed."""
    tools = {
        'yt-dlp': ['yt-dlp', '--version'],
        'ffmpeg': ['ffmpeg', '-version']
    }
    
    missing = []
    for tool, cmd in tools.items():
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"✓ {tool} installed")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"✗ {tool} not found")
            missing.append(tool)
    
    if missing:
        print(f"\nPlease install: {', '.join(missing)}")
        print("  yt-dlp: pip install yt-dlp")
        print("  ffmpeg: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
        return False
    return True


def download_video(url, output_dir="data/youtube_videos"):
    """Download YouTube video."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading: {url}")
    try:
        # Get video info first
        info_cmd = [
            'yt-dlp', '--dump-json', '--no-download', url
        ]
        info_result = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
        video_info = json.loads(info_result.stdout)
        
        title = video_info.get('title', 'video')
        duration = video_info.get('duration', 0)
        upload_date = video_info.get('upload_date', '')
        
        print(f"  Title: {title}")
        print(f"  Duration: {duration}s ({duration/3600:.1f} hours)")
        if upload_date:
            upload_dt = datetime.strptime(upload_date, '%Y%m%d')
            print(f"  Upload date: {upload_dt.strftime('%Y-%m-%d')}")
        
        # Download video
        output_template = str(output_path / f"{title.replace('/', '_')}.%(ext)s")
        subprocess.run([
            'yt-dlp',
            '-f', 'best[height<=720]',  # Reasonable quality
            '-o', output_template,
            url
        ], check=True)
        
        # Find downloaded file
        video_file = output_path / f"{title.replace('/', '_')}.mp4"
        if not video_file.exists():
            # Try other extensions
            for ext in ['webm', 'mkv', 'mp4']:
                video_file = output_path / f"{title.replace('/', '_')}.{ext}"
                if video_file.exists():
                    break
        
        return video_file, video_info
        
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def extract_frames_at_times(video_path, target_times, timelapse_start, 
                           timelapse_speed_seconds_per_frame, output_dir):
    """
    Extract frames from timelapse video at specific real-world times.
    
    Args:
        video_path: Path to video file
        target_times: List of datetime objects (real-world times)
        timelapse_start: datetime when timelapse started
        timelapse_speed_seconds_per_frame: Real seconds per video frame
        output_dir: Directory to save frames
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    metadata = []
    
    for target_time in target_times:
        # Calculate time difference from start
        time_diff = (target_time - timelapse_start).total_seconds()
        
        # Calculate which frame this corresponds to
        frame_number = int(time_diff / timelapse_speed_seconds_per_frame)
        
        # Extract frame using ffmpeg
        frame_filename = f"frame_{target_time.strftime('%Y%m%d_%H%M%S')}.jpg"
        frame_path = output_path / frame_filename
        
        try:
            subprocess.run([
                'ffmpeg', '-i', str(video_path),
                '-vf', f'select=eq(n\\,{frame_number})',
                '-vframes', '1',
                '-q:v', '2',
                str(frame_path)
            ], check=True, capture_output=True)
            
            if frame_path.exists():
                metadata.append({
                    "image_path": str(frame_path),
                    "capture_time": target_time.isoformat(),
                    "frame_number": frame_number
                })
                print(f"  Extracted: {frame_filename} (frame {frame_number})")
        except Exception as e:
            print(f"  Error extracting frame {frame_number}: {e}")
    
    return metadata


def process_timelapse_for_sunset(video_url, timelapse_start_date, 
                                timelapse_speed_hours_per_frame=1,
                                days_to_process=365):
    """
    Process a timelapse video to extract frames ~3 hours before sunset.
    
    Args:
        video_url: YouTube URL
        timelapse_start_date: Date when timelapse started (YYYY-MM-DD)
        timelapse_speed_hours_per_frame: Hours of real time per video frame
        days_to_process: Number of days to process
    """
    print("=" * 70)
    print("LBNL Timelapse Sunset Frame Extractor")
    print("=" * 70)
    
    if not check_dependencies():
        return
    
    # Download video
    video_path, video_info = download_video(video_url)
    if video_path is None:
        return
    
    print(f"\n✓ Video downloaded: {video_path.name}")
    
    # Parse timelapse start
    timelapse_start = datetime.strptime(timelapse_start_date, '%Y-%m-%d')
    
    # Calculate target times (3 hours before sunset for each day)
    target_times = []
    current_date = timelapse_start
    
    for day in range(days_to_process):
        sunset_time = get_sunset_time(current_date)
        target_time = sunset_time - timedelta(hours=3)
        
        # Only include if target time is after timelapse start
        if target_time >= timelapse_start:
            target_times.append(target_time)
        
        current_date += timedelta(days=1)
    
    print(f"\nFound {len(target_times)} target times (~3 hours before sunset)")
    
    # Convert speed to seconds per frame
    timelapse_speed_seconds_per_frame = timelapse_speed_hours_per_frame * 3600
    
    # Extract frames
    output_dir = Path("data/lbnl_frames")
    print(f"\nExtracting frames to {output_dir}...")
    
    metadata = extract_frames_at_times(
        video_path, target_times, timelapse_start,
        timelapse_speed_seconds_per_frame, output_dir
    )
    
    # Save metadata
    metadata_file = output_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Extracted {len(metadata)} frames")
    print(f"✓ Metadata saved to {metadata_file}")
    
    return metadata


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download and process LBNL YouTube timelapse videos"
    )
    parser.add_argument("--url", type=str, required=True,
                       help="YouTube video URL")
    parser.add_argument("--start-date", type=str, required=True,
                       help="Timelapse start date (YYYY-MM-DD)")
    parser.add_argument("--speed", type=float, default=1.0,
                       help="Hours of real time per video frame (default: 1.0)")
    parser.add_argument("--days", type=int, default=365,
                       help="Number of days to process (default: 365)")
    
    args = parser.parse_args()
    
    process_timelapse_for_sunset(
        args.url,
        args.start_date,
        args.speed,
        args.days
    )

