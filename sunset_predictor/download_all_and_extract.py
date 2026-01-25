"""
Download all videos from playlist and extract sunset frames (10 min after sunset).
"""

import subprocess
from pathlib import Path
import time

def download_all_videos():
    """Download remaining videos from playlist."""
    print("=" * 70)
    print("DOWNLOADING ALL VIDEOS FROM PLAYLIST")
    print("=" * 70)
    print("\nThis will download ~93 remaining videos.")
    print("Estimated time: 2-3 hours (depends on connection speed)\n")
    
    # Run download script
    result = subprocess.run([
        'python3', 'download_playlist.py'
    ], cwd=Path(__file__).parent)
    
    return result.returncode == 0

def extract_all_sunsets():
    """Extract sunset frames from all videos (10 min after sunset)."""
    print("\n" + "=" * 70)
    print("EXTRACTING SUNSET FRAMES (10 MIN AFTER SUNSET)")
    print("=" * 70)
    print("\nProcessing all videos...")
    print("Target: Frame 10 minutes after sunset\n")
    
    result = subprocess.run([
        'python3', 'extract_lhs_sunsets.py', '--process-all'
    ], cwd=Path(__file__).parent)
    
    return result.returncode == 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download and extract all sunsets")
    parser.add_argument("--download-only", action="store_true",
                       help="Only download videos, don't extract")
    parser.add_argument("--extract-only", action="store_true",
                       help="Only extract, don't download")
    
    args = parser.parse_args()
    
    if not args.extract_only:
        print("Step 1: Downloading videos...")
        download_all_videos()
    
    if not args.download_only:
        print("\nStep 2: Extracting sunset frames...")
        extract_all_sunsets()
        
        print("\n" + "=" * 70)
        print("COMPLETE!")
        print("=" * 70)
        print("\nNext: Run python3 setup_grading.py to organize for grading")


