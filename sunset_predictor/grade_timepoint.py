"""
Interactive grading for a specific timepoint.
Shows images one by one for scoring.
"""

import json
import matplotlib
# Try different backends for macOS
try:
    matplotlib.use('TkAgg')
except:
    try:
        matplotlib.use('Qt5Agg')
    except:
        matplotlib.use('macosx')  # Fallback to macOS native
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from pathlib import Path
from PIL import Image
import numpy as np
import re
import sys

class TimepointGrader:
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
        self.current_score = 5
        
        print(f"Timepoint: {timepoint:+d} minutes")
        print(f"Total images: {len(self.image_files)}")
        print(f"To grade: {len(self.ungraded)}")
        print(f"Already graded: {len(self.image_files) - len(self.ungraded)}")
    
    def show_image(self, img_path):
        """Display image with grading interface."""
        img = Image.open(img_path)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(img)
        ax.axis('off')
        
        # Extract date from filename
        date_match = re.search(r'(\d{8})', img_path.stem)
        date_str = date_match.group(1) if date_match else "Unknown"
        
        title = f"Timepoint: {self.timepoint:+d} min | Image {self.current_idx+1}/{len(self.ungraded)}\n"
        title += f"Date: {date_str}"
        if self.scores.get(str(img_path), {}).get("quality_score"):
            title += f" | Current: {self.scores[str(img_path)]['quality_score']}"
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Instructions
        fig.text(0.5, 0.02, 
                f"Rate aesthetic quality (1-10 scale) for {self.timepoint:+d} min timepoint\n"
                "Press number keys 1-10 to score, or use slider",
                ha='center', fontsize=11, style='italic')
        
        # Score display
        score_text = fig.text(0.5, 0.08, f"Score: {self.current_score}", 
                             ha='center', fontsize=16, fontweight='bold',
                             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # Slider
        ax_slider = plt.axes([0.2, 0.15, 0.6, 0.03])
        slider = Slider(ax_slider, 'Score', 1, 10, valinit=self.current_score, 
                       valstep=1, valfmt='%d')
        
        def update_score(val):
            self.current_score = int(val)
            score_text.set_text(f"Score: {self.current_score}")
            fig.canvas.draw()
        
        slider.on_changed(update_score)
        
        # Buttons
        ax_save = plt.axes([0.3, 0.05, 0.15, 0.04])
        ax_next = plt.axes([0.5, 0.05, 0.15, 0.04])
        ax_prev = plt.axes([0.1, 0.05, 0.15, 0.04])
        
        btn_save = Button(ax_save, 'Save Score')
        btn_next = Button(ax_next, 'Next')
        btn_prev = Button(ax_prev, 'Previous')
        
        def save_score(event):
            self.scores[str(img_path)] = {
                "quality_score": self.current_score,
                "graded": True,
                "timepoint": self.timepoint,
                "date": date_str
            }
            
            with open(self.metadata_file, "w") as f:
                json.dump(self.scores, f, indent=2)
            
            print(f"✓ Saved score {self.current_score} for {img_path.name}")
            plt.close()
            self.next_image()
        
        def next_img(event):
            plt.close()
            self.next_image()
        
        def prev_img(event):
            plt.close()
            self.prev_image()
        
        btn_save.on_clicked(save_score)
        btn_next.on_clicked(next_img)
        btn_prev.on_clicked(prev_img)
        
        # Keyboard shortcuts
        def on_key(event):
            if event.key in [str(i) for i in range(1, 10)]:
                self.current_score = int(event.key)
                slider.set_val(self.current_score)
            elif event.key == '0':
                self.current_score = 10
                slider.set_val(10)
            elif event.key == 'enter':
                save_score(None)
            elif event.key == 'right':
                next_img(None)
            elif event.key == 'left':
                prev_img(None)
        
        fig.canvas.mpl_connect('key_press_event', on_key)
        
        plt.tight_layout()
        try:
            plt.show(block=True)
        except Exception as e:
            print(f"Error displaying window: {e}")
            print("Trying alternative display method...")
            plt.show()
            input("Press Enter after viewing image...")
    
    def next_image(self):
        if self.current_idx < len(self.ungraded) - 1:
            self.current_idx += 1
            img_path = self.ungraded[self.current_idx]
            self.current_score = self.scores.get(str(img_path), {}).get("quality_score", 5) or 5
            self.show_image(img_path)
        else:
            print("\n✓ All images graded for this timepoint!")
            self.show_summary()
    
    def prev_image(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            img_path = self.ungraded[self.current_idx]
            self.current_score = self.scores.get(str(img_path), {}).get("quality_score", 5) or 5
            self.show_image(img_path)
    
    def show_summary(self):
        scores_list = [s["quality_score"] for s in self.scores.values() if s.get("graded")]
        if scores_list:
            print(f"\nGrading Summary for {self.timepoint:+d}min:")
            print(f"  Total graded: {len(scores_list)}")
            print(f"  Average score: {np.mean(scores_list):.2f}")
            print(f"  Score range: {min(scores_list)} - {max(scores_list)}")
    
    def start_grading(self):
        if not self.ungraded:
            print("All images already graded!")
            return
        
        img_path = self.ungraded[self.current_idx]
        self.current_score = self.scores.get(str(img_path), {}).get("quality_score", 5) or 5
        self.show_image(img_path)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Grade images for a specific timepoint")
    parser.add_argument("--timepoint", type=int, required=True,
                       help="Timepoint offset in minutes (e.g., -10, 0, 10)")
    parser.add_argument("--grading-dir", type=str, default="data/grading_by_timepoint",
                       help="Grading directory")
    
    args = parser.parse_args()
    
    grader = TimepointGrader(args.timepoint, args.grading_dir)
    grader.start_grading()

