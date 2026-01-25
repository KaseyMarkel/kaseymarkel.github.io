"""
Setup grading interface for multiple timepoints.
Organizes images by timepoint so you can grade each set separately.
"""

import json
from pathlib import Path
import shutil

def setup_timepoint_grading(metadata_file="data/extracted_frames/metadata.json",
                           output_base="data/grading_by_timepoint"):
    """Organize images by timepoint for grading."""
    output_path = Path(output_base)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load metadata
    metadata_path = Path(metadata_file)
    if not metadata_path.exists():
        print(f"Metadata file not found: {metadata_file}")
        print("Run extract_all_frames.py first!")
        return
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    # Sunset timepoints
    timepoints = [-10, -5, 0, 5, 10, 15, 20, 25]
    
    print("=" * 70)
    print("SETTING UP TIMEPOINT GRADING")
    print("=" * 70)
    print(f"\nOrganizing {len(metadata)} videos by timepoint...")
    print(f"Timepoints: {timepoints} minutes relative to sun-under-horizon\n")
    
    # Create folders for each timepoint
    for offset in timepoints:
        offset_str = f"{offset:+d}" if offset >= 0 else f"{offset}"
        timepoint_dir = output_path / f"timepoint_{offset_str}min"
        timepoint_dir.mkdir(exist_ok=True)
        
        images_dir = timepoint_dir / "images_to_grade"
        images_dir.mkdir(exist_ok=True)
    
    # Also create midday folder
    midday_dir = output_path / "midday"
    midday_dir.mkdir(exist_ok=True)
    midday_images_dir = midday_dir / "images_to_grade"
    midday_images_dir.mkdir(exist_ok=True)
    
    # Organize images
    counts = {}
    
    for date_str, video_data in metadata.items():
        # Copy midday frame
        midday_path = video_data.get("midday")
        if midday_path and Path(midday_path).exists():
            target = midday_images_dir / f"midday_{date_str}.jpg"
            shutil.copy2(midday_path, target)
            counts.setdefault("midday", 0)
            counts["midday"] += 1
        
        # Copy sunset frames
        sunset_frames = video_data.get("sunset_frames", {})
        for offset, frame_path in sunset_frames.items():
            if Path(frame_path).exists():
                offset_int = int(offset) if isinstance(offset, str) else offset
                offset_str = f"{offset_int:+d}" if offset_int >= 0 else f"{offset_int}"
                timepoint_dir = output_path / f"timepoint_{offset_str}min" / "images_to_grade"
                target = timepoint_dir / f"sunset_{date_str}_{offset_str}min.jpg"
                shutil.copy2(frame_path, target)
                counts.setdefault(offset_int, 0)
                counts[offset_int] += 1
    
    # Create grading sheets
    print("\nCreating grading sheets...")
    for offset in timepoints:
        offset_str = f"{offset:+d}" if offset >= 0 else f"{offset}"
        timepoint_dir = output_path / f"timepoint_{offset_str}min"
        csv_file = timepoint_dir / "grading_sheet.csv"
        
        images = sorted((timepoint_dir / "images_to_grade").glob("*.jpg"))
        
        with open(csv_file, "w") as f:
            f.write("Image_Number,Date,Timepoint_Min,Quality_Score,Notes\n")
            for i, img in enumerate(images, 1):
                date_match = re.search(r'(\d{8})', img.stem)
                date = date_match.group(1) if date_match else ""
                f.write(f"{i},{date},{offset},,\n")
        
        print(f"  ✓ {offset:+d}min: {len(images)} images")
    
    # Midday grading sheet
    midday_csv = midday_dir / "grading_sheet.csv"
    midday_images = sorted(midday_images_dir.glob("*.jpg"))
    with open(midday_csv, "w") as f:
        f.write("Image_Number,Date,Quality_Score,Notes\n")
        for i, img in enumerate(midday_images, 1):
            date_match = re.search(r'(\d{8})', img.stem)
            date = date_match.group(1) if date_match else ""
            f.write(f"{i},{date},,\n")
    
    print(f"  ✓ Midday: {len(midday_images)} images")
    
    print(f"\n✓ Setup complete!")
    print(f"\nGrading folders:")
    print(f"  {output_path}/")
    print(f"\nTo grade each timepoint:")
    print(f"  1. Open folder: timepoint_Xmin/images_to_grade/")
    print(f"  2. Review images")
    print(f"  3. Record scores in: timepoint_Xmin/grading_sheet.csv")
    print(f"  4. Or use: python3 grade_timepoint.py --timepoint X")
    
    return output_path

if __name__ == "__main__":
    import re
    setup_timepoint_grading()

