"""
Create a table of all videos with download status.
Shows which videos were successfully downloaded and which need manual download.
"""

import csv
from pathlib import Path
import json

def create_download_status_table():
    """Create table showing download status for all videos."""
    # Load playlist CSV
    csv_file = Path("lhs_playlist_videos.csv")
    if not csv_file.exists():
        print("Playlist CSV not found. Run download_playlist.py first.")
        return
    
    # Check which videos exist
    videos_dir = Path("data/lhs_timelapses")
    videos_dir.mkdir(parents=True, exist_ok=True)
    
    existing_videos = set()
    for video_file in videos_dir.glob("*.mp4"):
        # Extract video ID from filename
        video_id = video_file.stem.split("_")[-1]
        existing_videos.add(video_id)
    
    # Read playlist CSV
    videos = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            video_id = row['Video ID']
            videos.append({
                'index': row['Index'],
                'title': row['Title'],
                'video_id': video_id,
                'url': row['URL'],
                'downloaded': video_id in existing_videos
            })
    
    # Create status table
    output_file = Path("video_download_status.csv")
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'Title', 'Video ID', 'URL', 'Status', 'Downloaded'])
        
        for video in videos:
            status = "✓ Downloaded" if video['downloaded'] else "✗ Needs Download"
            writer.writerow([
                video['index'],
                video['title'],
                video['video_id'],
                video['url'],
                status,
                "Yes" if video['downloaded'] else "No"
            ])
    
    # Print summary
    downloaded_count = sum(1 for v in videos if v['downloaded'])
    needed_count = len(videos) - downloaded_count
    
    print("=" * 80)
    print("VIDEO DOWNLOAD STATUS TABLE")
    print("=" * 80)
    print(f"\nTotal videos: {len(videos)}")
    print(f"Downloaded: {downloaded_count}")
    print(f"Need download: {needed_count}")
    print(f"\n✓ Table saved to: {output_file}")
    
    # Show full path
    full_path = videos_dir.resolve()
    print(f"\n📁 Place downloaded videos here:")
    print(f"   {full_path}")
    print(f"\n   Or relative path:")
    print(f"   data/lhs_timelapses/")
    
    # Show first few entries
    print(f"\n📋 First 10 videos:")
    print("-" * 80)
    print(f"{'Index':<6} {'Status':<15} {'Title':<50}")
    print("-" * 80)
    for video in videos[:10]:
        status = "✓" if video['downloaded'] else "✗"
        title = video['title'][:47] + "..." if len(video['title']) > 50 else video['title']
        print(f"{video['index']:<6} {status:<15} {title}")
    
    if len(videos) > 10:
        print(f"... and {len(videos) - 10} more (see CSV file)")
    
    # List videos that need download
    print(f"\n📥 Videos that need manual download ({needed_count}):")
    print("-" * 80)
    needed_videos = [v for v in videos if not v['downloaded']]
    for video in needed_videos[:20]:  # Show first 20
        print(f"{video['index']}. {video['title'][:60]}")
        print(f"   {video['url']}")
    
    if len(needed_videos) > 20:
        print(f"... and {len(needed_videos) - 20} more (see CSV file)")
    
    print(f"\n💡 Tip: Download videos and save them as:")
    print(f"   lhs_XXX_{video_id}.mp4")
    print(f"   (where XXX is the index number)")
    
    return output_file

if __name__ == "__main__":
    create_download_status_table()


