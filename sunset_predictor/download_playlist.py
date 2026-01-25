"""
Download all videos from LHS YouTube timelapse playlist.
"""

import subprocess
import json
import csv
from pathlib import Path
from datetime import datetime

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PL7C4BF8E749192ADB"

def get_playlist_info():
    """Get all videos from the playlist."""
    print("Fetching playlist information...")
    
    try:
        # Get playlist info as JSON (try different yt-dlp locations)
        yt_dlp_cmd = None
        for path in ['yt-dlp', '/Users/kasey/Library/Python/3.9/bin/yt-dlp', 
                     'python3', '-m', 'yt_dlp']:
            try:
                if path == 'python3':
                    result = subprocess.run([
                        'python3', '-m', 'yt_dlp', '--flat-playlist', '--dump-json',
                        PLAYLIST_URL
                    ], capture_output=True, text=True, check=True)
                    break
                else:
                    result = subprocess.run([
                        path, '--flat-playlist', '--dump-json',
                        PLAYLIST_URL
                    ], capture_output=True, text=True, check=True)
                    break
            except:
                continue
        else:
            raise FileNotFoundError("yt-dlp not found")
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    video_info = json.loads(line)
                    videos.append({
                        'title': video_info.get('title', 'Unknown'),
                        'id': video_info.get('id', ''),
                        'url': video_info.get('url', ''),
                        'duration': video_info.get('duration', 0),
                        'upload_date': video_info.get('upload_date', '')
                    })
                except:
                    continue
        
        return videos
        
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        return []

def create_video_table(videos, output_file="lhs_playlist_videos.csv"):
    """Create CSV table of all videos."""
    output_path = Path(output_file)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'Title', 'Video ID', 'URL', 'Duration (sec)', 'Upload Date'])
        
        for i, video in enumerate(videos, 1):
            writer.writerow([
                i,
                video['title'],
                video['id'],
                video['url'],
                video['duration'],
                video['upload_date']
            ])
    
    print(f"✓ Created video table: {output_path}")
    return output_path

def download_all_videos(videos, output_dir="data/lhs_timelapses"):
    """Download all videos from the playlist."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\nDownloading {len(videos)} videos...")
    print("This may take a while...\n")
    
    downloaded = []
    failed = []
    
    for i, video in enumerate(videos, 1):
        url = video['url']
        title = video['title'].replace('/', '_').replace('\\', '_')
        
        print(f"[{i}/{len(videos)}] {title[:60]}...")
        
        # Create safe filename
        filename = f"lhs_{i:03d}_{video['id']}.mp4"
        filepath = output_path / filename
        
        # Skip if already downloaded
        if filepath.exists():
            size_mb = filepath.stat().st_size / 1024 / 1024
            print(f"  ⏭️  Already exists ({size_mb:.1f} MB)")
            downloaded.append((video, filepath))
            continue
        
        try:
            # Download video (try different yt-dlp locations)
            downloaded_success = False
            last_error = None
            for cmd_base in [['python3', '-m', 'yt_dlp'], ['yt-dlp'], 
                           ['/Users/kasey/Library/Python/3.9/bin/yt-dlp']]:
                try:
                    result = subprocess.run(
                        cmd_base + [
                            '-f', 'best[height<=720]',
                            '-o', str(filepath),
                            '--no-warnings',
                            url
                        ], check=True, capture_output=True, text=True, timeout=300
                    )
                    downloaded_success = True
                    break
                except subprocess.TimeoutExpired:
                    last_error = "Timeout"
                    continue
                except subprocess.CalledProcessError as e:
                    last_error = f"Exit code {e.returncode}: {e.stderr[:100]}"
                    continue
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if not downloaded_success:
                print(f"  ✗ Error: {last_error}")
                failed.append(video)
                continue
            
            if filepath.exists():
                size_mb = filepath.stat().st_size / 1024 / 1024
                print(f"  ✓ Downloaded ({size_mb:.1f} MB)")
                downloaded.append((video, filepath))
            else:
                print(f"  ✗ Download failed")
                failed.append(video)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed.append(video)
    
    print(f"\n" + "=" * 70)
    print(f"Download Summary:")
    print(f"  Successfully downloaded: {len(downloaded)}")
    print(f"  Failed: {len(failed)}")
    print(f"  Saved to: {output_path}")
    
    if failed:
        print(f"\nFailed videos:")
        for video in failed:
            print(f"  - {video['title']}: {video['url']}")
    
    return downloaded, failed

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download LHS YouTube playlist")
    parser.add_argument("--list-only", action="store_true",
                       help="Only create table, don't download")
    parser.add_argument("--output-dir", type=str, default="data/lhs_timelapses",
                       help="Output directory")
    
    args = parser.parse_args()
    
    # Get playlist info
    videos = get_playlist_info()
    
    if not videos:
        print("No videos found in playlist")
        exit(1)
    
    print(f"\nFound {len(videos)} videos in playlist")
    
    # Create table
    table_file = create_video_table(videos)
    print(f"\nVideo list saved to: {table_file}")
    
    if not args.list_only:
        # Download all videos
        downloaded, failed = download_all_videos(videos, args.output_dir)
        
        print(f"\n✓ Download complete!")
        print(f"\nNext steps:")
        print(f"  1. Extract sunsets: python3 process_new_videos.py")
        print(f"  2. Setup grading: python3 setup_grading.py")
        print(f"  3. Grade sunsets: python3 grade_sunsets.py")

