"""
Gallery-style day-by-day grading - shows one image at a time, auto-advances.
Opens images one at a time in Preview, closes before showing next.
Just look, type score, press enter, next image appears.
"""

import json
import subprocess
import time
from pathlib import Path
import re
from collections import defaultdict

class GalleryGrader:
    def __init__(self, grading_dir="data/grading_by_timepoint"):
        self.grading_dir = Path(grading_dir)
        self.timepoints = [-10, -5, 0, 5, 10, 15, 20, 25]
        
        # Organize images by date
        self.images_by_date = defaultdict(dict)
        
        for tp in self.timepoints:
            tp_str = f"{tp:+d}"
            scores_file = self.grading_dir / f"timepoint_{tp_str}min" / "scores.json"
            
            # Try newly extracted frames first (these are the fixed ones!)
            extracted_dir = Path("data/extracted_frames/sunset") / f"{tp_str}min"
            images_dir = self.grading_dir / f"timepoint_{tp_str}min" / "images_to_grade"
            
            # Prefer newly extracted frames (format: sunset_YYYYMMDD_+25min.jpg)
            if extracted_dir.exists():
                for img_path in sorted(extracted_dir.glob("*.jpg")):
                    # Extract date from filename (format: sunset_YYYYMMDD_+25min.jpg)
                    date_match = re.search(r'sunset_(\d{4})(\d{2})(\d{2})', str(img_path))
                    if date_match:
                        date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                        self.images_by_date[date_str][tp] = img_path
            
            # Also check old grading directory (for backwards compatibility)
            if images_dir.exists():
                for img_path in sorted(images_dir.glob("*.jpg")):
                    # Extract date (format: sunset_YYYY-MM-DD_+25min.jpg or sunset_YYYYMMDD_+25min.jpg)
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(img_path))
                    if not date_match:
                        # Try YYYYMMDD format
                        date_match = re.search(r'sunset_(\d{4})(\d{2})(\d{2})', str(img_path))
                        if date_match:
                            date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                        else:
                            continue
                    else:
                        date_str = date_match.group(1)
                    
                    # Only add if not already found in extracted_frames
                    if date_str not in self.images_by_date or tp not in self.images_by_date[date_str]:
                        self.images_by_date[date_str][tp] = img_path
        
        # Get dates that need grading
        self.dates = sorted(self.images_by_date.keys())
        
        print(f"\n{'='*70}")
        print(f"GALLERY-STYLE DAY-BY-DAY GRADING")
        print(f"{'='*70}")
        print(f"\nFound {len(self.dates)} days with sunset images")
        print(f"Each day has up to 8 timepoints: {self.timepoints}")
        print(f"\nGallery mode: One image at a time, auto-advances after you score.")
        print(f"Just type the score (1-10) and press Enter!")
        print(f"{'='*70}\n")
    
    def is_already_graded_or_skipped(self, date_str, tp, img_path):
        """Check if this timepoint is already graded or skipped."""
        tp_str = f"{tp:+d}"
        scores_file = self.grading_dir / f"timepoint_{tp_str}min" / "scores.json"
        
        if scores_file.exists():
            with open(scores_file, "r") as f:
                data = json.load(f)
                
                # Try exact path match first
                img_path_str = str(img_path)
                if img_path_str in data:
                    score_data = data[img_path_str]
                    if score_data.get("graded") or score_data.get("quality_score") is not None:
                        return True, score_data.get("quality_score")
                    if score_data.get("skipped") or score_data.get("quality_score") is None:
                        return True, None
                
                # Try matching by date (in case path format differs)
                date_str_no_dash = date_str.replace('-', '')
                for stored_path, score_data in data.items():
                    # Check if date matches in the path
                    if date_str in stored_path or date_str_no_dash in stored_path:
                        # Also check timepoint matches
                        if f"{tp:+d}" in stored_path or f"{tp}" in stored_path:
                            if score_data.get("graded") or score_data.get("quality_score") is not None:
                                return True, score_data.get("quality_score")
                            if score_data.get("skipped") or score_data.get("quality_score") is None:
                                return True, None
        return False, None
    
    def close_all_preview_windows(self):
        """Close ALL Preview windows to prevent accumulation."""
        try:
            script = '''
            tell application "Preview"
                close every window
            end tell
            '''
            subprocess.run(['osascript', '-e', script], 
                         capture_output=True, timeout=2, 
                         stderr=subprocess.DEVNULL)
            time.sleep(0.2)  # Give it time to close
        except:
            pass
    
    def show_image_and_get_score(self, img_path, timepoint, existing_score, date_str):
        """Show image in Preview and get score from user."""
        # ALWAYS close all windows first to prevent accumulation
        self.close_all_preview_windows()
        
        # Small delay to ensure windows are closed
        time.sleep(0.3)
        
        # Open this image
        subprocess.Popen(['open', str(img_path)])
        time.sleep(0.5)  # Give Preview time to open
        
        # Try to bring Terminal back to front
        try:
            subprocess.run(['osascript', '-e', 
                          'tell application "Terminal" to activate'], 
                         capture_output=True, timeout=1)
            time.sleep(0.2)
        except:
            pass
        
        # Get input
        while True:
            try:
                prompt = f"{timepoint:+3d} min: "
                if existing_score:
                    prompt = f"{timepoint:+3d} min (current: {existing_score}): "
                
                print(f"\n>>> {prompt}", end='', flush=True)
                score_input = input().strip()
                
                if score_input.lower() == 'q':
                    self.close_all_preview_windows()
                    return None
                elif score_input.lower() == 's':
                    self.close_all_preview_windows()
                    return 'skip'
                elif score_input == '':
                    print("  (No input - try again)")
                    continue
                else:
                    try:
                        score = int(score_input)
                        if 1 <= score <= 10:
                            # Close Preview window before returning
                            self.close_all_preview_windows()
                            return score
                        else:
                            print(f"  ⚠ Invalid score. Please enter 1-10.")
                            continue
                    except ValueError:
                        print(f"  ⚠ Invalid input. Please enter 1-10, 's' to skip, or 'q' to quit.")
                        continue
            except (EOFError, KeyboardInterrupt):
                self.close_all_preview_windows()
                print("\n\nGrading interrupted.")
                return None
    
    def grade_day(self, date_str):
        """Grade all timepoints for a single day using gallery view."""
        print(f"\n{'='*70}")
        print(f"GRADING DAY: {date_str}")
        print(f"{'='*70}\n")
        
        day_images = self.images_by_date[date_str]
        
        if len(day_images) == 0:
            print(f"No images found for {date_str}")
            return False
        
        # Sort by timepoint in reverse (latest first, to match window stack)
        sorted_timepoints = sorted(day_images.keys(), reverse=True)
        
        scores = {}
        skipped_count = 0
        
        for tp in sorted_timepoints:
            img_path = day_images[tp]
            tp_str = f"{tp:+d}"
            
            # Check if already graded or skipped (for reference, but we'll re-grade all)
            already_done, existing_score = self.is_already_graded_or_skipped(date_str, tp, img_path)
            
            # Show ALL images and prompt for ALL of them (previous grades were on old images)
            # Only skip if user explicitly skips
            score = self.show_image_and_get_score(img_path, tp, existing_score, date_str)
            
            if score is None:
                print("Quitting this day...")
                return False
            elif score == 'skip':
                # Mark as skipped
                scores[tp] = {
                    "score": None,
                    "skipped": True,
                    "image_path": str(img_path),
                    "date": date_str
                }
                skipped_count += 1
                print("  Skipped")
            else:
                scores[tp] = {
                    "score": score,
                    "skipped": False,
                    "image_path": str(img_path),
                    "date": date_str
                }
                print(f"  ✓ Scored: {score}")
        
        # Save all scores for this day
        if scores:
            self.save_scores(scores)
            print(f"\n✓ Saved {len(scores)} scores for {date_str}")
            if skipped_count > 0:
                print(f"  ({skipped_count} timepoints were already skipped)")
        
        # Always close all windows at end of day
        self.close_all_preview_windows()
        
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
                "quality_score": score_data.get("score"),
                "graded": score_data.get("score") is not None and not score_data.get("skipped", False),
                "skipped": score_data.get("skipped", False),
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
        
        # Close all Preview windows at start
        self.close_all_preview_windows()
        
        print(f"\nStarting grading session...")
        print(f"You'll grade {len(self.dates)} days, one at a time.")
        print(f"Already graded/skipped timepoints will be automatically skipped.\n")
        
        graded_count = 0
        
        for i, date_str in enumerate(self.dates, 1):
            print(f"\n[{i}/{len(self.dates)}] Day: {date_str}")
            
            # Check how many already graded/skipped
            already_graded = 0
            already_skipped = 0
            for tp in self.timepoints:
                if tp in self.images_by_date[date_str]:
                    img_path = self.images_by_date[date_str][tp]
                    done, score = self.is_already_graded_or_skipped(date_str, tp, img_path)
                    if done:
                        if score is None:
                            already_skipped += 1
                        elif score is not None:
                            already_graded += 1
            
            total_timepoints = len(self.images_by_date[date_str])
            remaining = total_timepoints - already_graded - already_skipped
            
            if remaining == 0:
                print(f"  Already complete ({already_graded} graded, {already_skipped} skipped)")
                continue
            
            print(f"  {already_graded} graded, {already_skipped} skipped, {remaining} remaining")
            
            # Grade this day
            result = self.grade_day(date_str)
            
            if result:
                graded_count += 1
            else:
                print("\nGrading stopped by user.")
                print(f"Progress saved. Resume by running: python3 grade_by_day_gallery.py")
                break
        
        # Final cleanup - close all windows
        self.close_all_preview_windows()
        
        print(f"\n{'='*70}")
        print(f"GRADING SESSION COMPLETE")
        print(f"{'='*70}")
        print(f"Graded: {graded_count} days")
        print(f"Remaining: {len(self.dates) - graded_count} days")
        print(f"\nTo continue grading, run: python3 grade_by_day_gallery.py")

if __name__ == "__main__":
    grader = GalleryGrader()
    grader.start_grading()
