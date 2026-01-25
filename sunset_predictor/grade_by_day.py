"""
Grade sunsets day by day - shows all 8 timepoints for each day.
Easier and faster than grading timepoint by timepoint.
"""

import json
import subprocess
from pathlib import Path
import re
from collections import defaultdict
import time

class DayByDayGrader:
    def __init__(self, grading_dir="data/grading_by_timepoint"):
        self.grading_dir = Path(grading_dir)
        self.timepoints = [-10, -5, 0, 5, 10, 15, 20, 25]
        
        # Organize images by date
        self.images_by_date = defaultdict(dict)
        
        for tp in self.timepoints:
            tp_str = f"{tp:+d}"
            scores_file = self.grading_dir / f"timepoint_{tp_str}min" / "scores.json"
            images_dir = self.grading_dir / f"timepoint_{tp_str}min" / "images_to_grade"
            
            if images_dir.exists():
                for img_path in sorted(images_dir.glob("*.jpg")):
                    # Extract date
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(img_path))
                    if date_match:
                        date_str = date_match.group(1)
                        self.images_by_date[date_str][tp] = img_path
        
        # Get dates that need grading (have at least some images)
        self.dates = sorted(self.images_by_date.keys())
        
        print(f"\n{'='*70}")
        print(f"DAY-BY-DAY GRADING SYSTEM")
        print(f"{'='*70}")
        print(f"\nFound {len(self.dates)} days with sunset images")
        print(f"Each day has up to 8 timepoints: {self.timepoints}")
        print(f"\nYou'll grade all timepoints for one day at a time.")
        print(f"Images will open in Preview, then you'll score them in sequence.")
        print(f"Each image closes automatically after you grade it.")
        print(f"{'='*70}\n")
    
    def close_preview_window(self, img_path):
        """Close the Preview window for a specific image file."""
        try:
            filename = Path(img_path).name
            
            # Use the method that works: close by window name containing filename
            # This matches what we tested successfully
            script = f'''
            tell application "Preview"
                repeat with win in windows
                    try
                        set winName to name of win
                        if winName contains "{filename}" then
                            close win
                            return "closed"
                        end if
                    end try
                end repeat
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, timeout=3, 
                                  text=True, stderr=subprocess.DEVNULL)
            
            # If that didn't work, try closing by document path
            if result.returncode != 0 or "closed" not in result.stdout:
                script2 = f'''
                tell application "Preview"
                    repeat with doc in documents
                        try
                            set docPath to path of doc
                            if docPath ends with "{filename}" then
                                close doc
                            end if
                        end try
                    end repeat
                end tell
                '''
                subprocess.run(['osascript', '-e', script2], 
                             capture_output=True, timeout=3,
                             text=True, stderr=subprocess.DEVNULL)
                
        except Exception:
            # Silently fail - window might already be closed
            pass
    
    def grade_day(self, date_str):
        """Grade all timepoints for a single day."""
        print(f"\n{'='*70}")
        print(f"GRADING DAY: {date_str}")
        print(f"{'='*70}")
        
        day_images = self.images_by_date[date_str]
        
        if len(day_images) == 0:
            print(f"No images found for {date_str}")
            return False
        
        # Open all images for this day in Preview (non-blocking)
        # Sort by timepoint in ascending order (earliest first)
        print(f"\nOpening {len(day_images)} images in Preview...")
        sorted_items = sorted(day_images.items(), key=lambda x: x[0])  # Sort by timepoint
        for tp, img_path in sorted_items:
            subprocess.Popen(['open', str(img_path)])
            time.sleep(0.2)  # Slightly longer delay to ensure proper ordering
        
        # Wait a moment for Preview to open, then try to refocus Terminal
        time.sleep(1.5)
        
        # Try to bring Terminal back to front (macOS)
        try:
            subprocess.run(['osascript', '-e', 
                          'tell application "Terminal" to activate'], 
                         capture_output=True, timeout=1)
            time.sleep(0.3)  # Give it time to switch
        except:
            pass
        
        print(f"\n{'='*70}")
        print(f"Images are open in Preview.")
        print(f"Terminal should be focused - just type numbers and press Enter!")
        print(f"Each image will close automatically after you grade it.")
        print(f"Grading order: Latest to earliest (top image first)")
        print(f"Score each timepoint (1-10), or 's' to skip, 'q' to quit this day")
        print(f"{'='*70}\n")
        
        scores = {}
        
        # Grade in reverse chronological order (latest timepoint first)
        # This way the top image (latest) gets graded first, matching the window stack
        for tp in sorted(day_images.keys(), reverse=True):
            img_path = day_images[tp]
            tp_str = f"{tp:+d}"
            
            # Check if already graded
            scores_file = self.grading_dir / f"timepoint_{tp_str}min" / "scores.json"
            existing_score = None
            if scores_file.exists():
                with open(scores_file, "r") as f:
                    existing_data = json.load(f)
                    if str(img_path) in existing_data and existing_data[str(img_path)].get("graded"):
                        existing_score = existing_data[str(img_path)]["quality_score"]
            
            # Prompt for score - make it very clear and visible
            if existing_score:
                prompt_text = f"{tp:+3d} min (current: {existing_score}): "
            else:
                prompt_text = f"{tp:+3d} min: "
            
            # Make prompt very visible
            print(f"\n>>> {prompt_text}", end='', flush=True)
            
            try:
                score_input = input().strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nGrading interrupted.")
                return False
            
            # If empty, might mean user didn't see prompt - try once more
            if not score_input:
                print("  (No input - try again)")
                print(f">>> {prompt_text}", end='', flush=True)
                try:
                    score_input = input().strip()
                except:
                    score_input = 's'  # Skip if still no input
            
            if score_input.lower() == 'q':
                print("Quitting this day...")
                return False
            elif score_input.lower() == 's':
                print("  Skipped")
                # Close this Preview window even if skipped
                self.close_preview_window(img_path)
                continue
            elif score_input.lower() == 'b':
                # Go back one timepoint
                print("  Going back...")
                # This is tricky - we'd need to track state
                continue
            else:
                try:
                    score = int(score_input)
                    if 1 <= score <= 10:
                        scores[tp] = {
                            "score": score,
                            "image_path": str(img_path),
                            "date": date_str
                        }
                        print(f"  ✓ Scored: {score}", end='', flush=True)
                        
                        # Close this Preview window
                        self.close_preview_window(img_path)
                        print()  # New line after closing
                        
                    else:
                        print(f"  ⚠ Invalid score. Please enter 1-10.")
                        # Retry this timepoint
                        continue
                except ValueError:
                    print(f"  ⚠ Invalid input. Please enter 1-10, 's' to skip, or 'q' to quit.")
                    continue
        
        # Save all scores for this day
        if scores:
            self.save_scores(scores)
            print(f"\n✓ Saved {len(scores)} scores for {date_str}")
        
        return True
    
    def save_scores(self, scores_dict):
        """Save scores to their respective timepoint files."""
        for tp, score_data in scores_dict.items():
            tp_str = f"{tp:+d}"
            scores_file = self.grading_dir / f"timepoint_{tp_str}min" / "scores.json"
            
            # Load existing scores
            existing_scores = {}
            if scores_file.exists():
                with open(scores_file, "r") as f:
                    existing_scores = json.load(f)
            
            # Update with new score
            img_path = score_data["image_path"]
            existing_scores[str(img_path)] = {
                "quality_score": score_data["score"],
                "graded": True,
                "timepoint": tp,
                "date": score_data["date"]
            }
            
            # Save
            scores_file.parent.mkdir(parents=True, exist_ok=True)
            with open(scores_file, "w") as f:
                json.dump(existing_scores, f, indent=2)
    
    def start_grading(self):
        """Start the day-by-day grading session."""
        if not self.dates:
            print("No dates found to grade!")
            return
        
        print(f"\nStarting grading session...")
        print(f"You'll grade {len(self.dates)} days, one at a time.\n")
        
        graded_count = 0
        
        for i, date_str in enumerate(self.dates, 1):
            print(f"\n[{i}/{len(self.dates)}] Day: {date_str}")
            
            # Check how many already graded
            already_graded = 0
            for tp in self.timepoints:
                tp_str = f"{tp:+d}"
                scores_file = self.grading_dir / f"timepoint_{tp_str}min" / "scores.json"
                if scores_file.exists():
                    with open(scores_file, "r") as f:
                        data = json.load(f)
                        for img_path, score_data in data.items():
                            if date_str in str(img_path) and score_data.get("graded"):
                                already_graded += 1
                                break
            
            if already_graded == len(self.timepoints):
                print(f"  Already fully graded ({already_graded}/{len(self.timepoints)} timepoints)")
                continue
            
            print(f"  {already_graded}/{len(self.timepoints)} timepoints already graded")
            
            # Grade this day
            result = self.grade_day(date_str)
            
            if result:
                graded_count += 1
            else:
                print("\nGrading stopped by user.")
                break
        
        print(f"\n{'='*70}")
        print(f"GRADING SESSION COMPLETE")
        print(f"{'='*70}")
        print(f"Graded: {graded_count} days")
        print(f"Remaining: {len(self.dates) - graded_count} days")
        print(f"\nTo continue grading, run: python3 grade_by_day.py")

if __name__ == "__main__":
    import sys
    
    # Try to ensure terminal has focus (macOS)
    # This might help but isn't guaranteed
    try:
        subprocess.run(['osascript', '-e', 'tell application "Terminal" to activate'], 
                      capture_output=True)
    except:
        pass
    
    grader = DayByDayGrader()
    grader.start_grading()

