"""
Setup grading interface for sunset quality scores.
Creates organized folder structure and grading interface.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def setup_grading_folders(metadata_file="data/sunset_images_for_grading/sunset_metadata.json",
                         output_base="data/grading"):
    """
    Organize images into folders for easy grading.
    Creates numbered folders with images ready for review.
    """
    output_path = Path(output_base)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load metadata
    metadata_path = Path(metadata_file)
    if not metadata_path.exists():
        print(f"Metadata file not found: {metadata_file}")
        print("Run collect_sunset_images.py first or provide existing images.")
        return
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    print(f"Setting up grading for {len(metadata)} sunset images...")
    
    # Create grading structure
    images_dir = output_path / "images_to_grade"
    images_dir.mkdir(exist_ok=True)
    
    # Copy images to numbered files for easy grading
    graded_count = 0
    ungraded_count = 0
    
    for i, item in enumerate(metadata):
        source_path_str = item.get("image_path")
        if not source_path_str:
            print(f"Warning: No image path for item {i+1}")
            continue
        
        source_path = Path(source_path_str)
        
        if not source_path.exists():
            print(f"Warning: Image not found: {source_path}")
            continue
        
        # Create numbered filename
        target_filename = f"{i+1:04d}_sunset.jpg"
        target_path = images_dir / target_filename
        
        # Copy image
        try:
            shutil.copy2(source_path, target_path)
            
            # Create info file
            info_file = images_dir / f"{i+1:04d}_info.txt"
            with open(info_file, "w") as f:
                f.write(f"Image #{i+1}\n")
                f.write(f"Date: {item['date']}\n")
                f.write(f"Sunset Time: {item['sunset_time']}\n")
                f.write(f"Original: {source_path.name}\n")
                f.write(f"\nGrade this sunset on a scale (e.g., 1-10):\n")
                f.write(f"Quality Score: ___\n")
            
            if item.get("graded", False):
                graded_count += 1
            else:
                ungraded_count += 1
                
        except Exception as e:
            print(f"Error copying {source_path}: {e}")
    
    print(f"\n✓ Setup complete!")
    print(f"  Images ready for grading: {ungraded_count}")
    print(f"  Already graded: {graded_count}")
    print(f"\nImages organized in: {images_dir}")
    print(f"\nTo grade:")
    print(f"  1. Open images in: {images_dir}")
    print(f"  2. Review each sunset image")
    print(f"  3. Record scores in: {images_dir}/*_info.txt")
    print(f"  4. Or use: python3 grade_sunsets.py (interactive grading)")
    
    # Create grading template CSV
    csv_file = output_path / "grading_sheet.csv"
    with open(csv_file, "w") as f:
        f.write("Image_Number,Date,Sunset_Time,Quality_Score,Notes\n")
        for i, item in enumerate(metadata):
            f.write(f"{i+1},{item['date']},{item['sunset_time']},,\n")
    
    print(f"\n✓ Created grading sheet: {csv_file}")
    print(f"  Fill in Quality_Score column (e.g., 1-10 scale)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup sunset grading interface")
    parser.add_argument("--metadata", type=str, 
                       default="data/sunset_images_for_grading/sunset_metadata.json",
                       help="Metadata file")
    parser.add_argument("--output", type=str, default="data/grading",
                       help="Output directory")
    
    args = parser.parse_args()
    
    setup_grading_folders(args.metadata, args.output)

