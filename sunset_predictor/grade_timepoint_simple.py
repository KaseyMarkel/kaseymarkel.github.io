"""
Simpler grading interface that opens images in Preview (macOS).
Alternative if matplotlib GUI doesn't work.
"""

import json
import subprocess
from pathlib import Path
import re

class SimpleTimepointGrader:
    def __init__(self, timepoint, grading_dir="data/grading_by_timepoint"):
        self.timepoint = timepoint
        self.grading_dir = Path(grading_dir)
        self.images_dir = self.grading_dir / f"timepoint_{timepoint:+d}min" / "images_to_grade"
        self.metadata_file = self.grading_dir / f"timepoint_{timepoint:+d}min" / "scores.json"
        
        # Load existing scores
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                self.scores = json.load(f)
        else:
            self.scores = {}
        
        # Get all images
        self.image_files = sorted(self.images_dir.glob("*.jpg"))
        self.ungraded = [img for img in self.image_files 
                        if str(img) not in self.scores or not self.scores[str(img)].get("graded", False)]
        
        self.current_idx = 0
        
        print(f"\nTimepoint: {timepoint:+d} minutes")
        print(f"Total images: {len(self.image_files)}")
        print(f"To grade: {len(self.ungraded)}")
        print(f"Already graded: {len(self.image_files) - len(self.ungraded)}")
    
    def grade_image(self, img_path):
        """Open image and get score."""
        # Open image in Preview (non-blocking)
        subprocess.Popen(['open', str(img_path)])
        
        # Wait a moment for Preview to open
        import time
        time.sleep(0.5)
        
        # Get score
        print(f"\n{'='*60}")
        print(f"Image {self.current_idx + 1}/{len(self.ungraded)}: {img_path.name}")
        
        # Extract date
        date_match = re.search(r'(\d{8})', img_path.stem)
        date_str = date_match.group(1) if date_match else "Unknown"
        print(f"Date: {date_str}")
        print(f"Timepoint: {self.timepoint:+d} minutes")
        print(f"{'='*60}")
        
        while True:
            try:
                score_input = input("\nScore (1-10, 's' to skip, 'q' to quit, 'b' to go back): ").strip()
                
                if score_input.lower() == 'q':
                    return False
                elif score_input.lower() == 's':
                    print("Skipped")
                    return True
                elif score_input.lower() == 'b':
                    # Go back one image
                    if self.current_idx > 0:
                        self.current_idx -= 2  # Will be incremented back to previous
                        return True
                    else:
                        print("Already at first image")
                        continue
                else:
                    score = int(score_input)
                    if 1 <= score <= 10:
                        # Save score
                        self.scores[str(img_path)] = {
                            "quality_score": score,
                            "graded": True,
                            "timepoint": self.timepoint,
                            "date": date_str
                        }
                        
                        with open(self.metadata_file, "w") as f:
                            json.dump(self.scores, f, indent=2)
                        
                        print(f"✓ Saved score: {score}")
                        return True
                    else:
                        print("Please enter a number between 1 and 10")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nQuitting...")
                print(f"Progress saved. {len([s for s in self.scores.values() if s.get('graded')])} images graded so far.")
                return False
    
    def start_grading(self):
        """Start grading session."""
        if not self.ungraded:
            print("All images already graded!")
            return
        
        print(f"\n{'='*60}")
        print(f"STARTING GRADING SESSION")
        print(f"{'='*60}")
        print(f"Timepoint: {self.timepoint:+d} minutes")
        print(f"Images to grade: {len(self.ungraded)}")
        print(f"\nImages will open in Preview (macOS default viewer)")
        print(f"Score each image 1-10")
        print(f"Commands:")
        print(f"  - Enter 1-10: Score the image")
        print(f"  - 's': Skip this image")
        print(f"  - 'b': Go back to previous image")
        print(f"  - 'q': Quit and save progress")
        print(f"  - Ctrl+C: Quit and save progress")
        print(f"{'='*60}\n")
        
        i = 0
        while i < len(self.ungraded):
            self.current_idx = i
            img_path = self.ungraded[i]
            
            result = self.grade_image(img_path)
            
            if result is False:  # Quit
                break
            elif result == "back":  # Go back
                if i > 0:
                    i -= 1
                continue
            
            i += 1
        
        graded_count = len([s for s in self.scores.values() if s.get('graded')])
        print(f"\n{'='*60}")
        print(f"GRADING SESSION COMPLETE")
        print(f"{'='*60}")
        print(f"Graded: {graded_count} images")
        print(f"Remaining: {len(self.ungraded) - graded_count} images")
        print(f"Scores saved to: {self.metadata_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Grade images for a specific timepoint (simple version)")
    parser.add_argument("--timepoint", type=int, required=True,
                       help="Timepoint offset in minutes (e.g., -10, 0, 10)")
    parser.add_argument("--grading-dir", type=str, default="data/grading_by_timepoint",
                       help="Grading directory")
    
    args = parser.parse_args()
    
    grader = SimpleTimepointGrader(args.timepoint, args.grading_dir)
    grader.start_grading()

