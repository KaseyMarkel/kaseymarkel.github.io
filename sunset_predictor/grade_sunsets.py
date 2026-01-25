"""
Interactive grading interface for sunset quality.
Shows images one by one for scoring.
"""

import json
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from pathlib import Path
from PIL import Image
import numpy as np

class SunsetGrader:
    def __init__(self, images_dir, metadata_file):
        self.images_dir = Path(images_dir)
        self.metadata_file = Path(metadata_file)
        
        # Load metadata
        with open(metadata_file, "r") as f:
            self.metadata = json.load(f)
        
        # Filter to images that actually exist and have image_path
        self.ungraded_indices = []
        for i, item in enumerate(self.metadata):
            # Check if image exists
            image_path = item.get("image_path")
            if image_path:
                img_path = Path(image_path)
                # Also check numbered file in grading folder
                if not img_path.exists():
                    # Try numbered file
                    numbered_file = self.images_dir / f"{i+1:04d}_sunset.jpg"
                    if numbered_file.exists():
                        item["image_path"] = str(numbered_file)
                        img_path = numbered_file
                
                if img_path.exists() and not item.get("graded", False):
                    self.ungraded_indices.append(i)
        
        self.current_idx = 0
        self.current_score = 5  # Default score
        
        print(f"Loaded {len(self.ungraded_indices)} images to grade")
        print(f"Total images in metadata: {len(self.metadata)}")
        print(f"Images with actual files: {len(self.ungraded_indices)}")
    
    def load_image(self, index):
        """Load image for given metadata index."""
        item = self.metadata[index]
        image_path = item.get("image_path")
        
        if not image_path:
            # Try numbered file
            img_path = self.images_dir / f"{index+1:04d}_sunset.jpg"
        else:
            img_path = Path(image_path)
        
        if img_path.exists():
            return Image.open(img_path)
        
        # Try numbered file as fallback
        numbered_file = self.images_dir / f"{index+1:04d}_sunset.jpg"
        if numbered_file.exists():
            return Image.open(numbered_file)
        
        return None
    
    def show_image(self, index):
        """Display image with grading interface."""
        item = self.metadata[index]
        img = self.load_image(index)
        
        if img is None:
            print(f"Image not found for index {index}")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(img)
        ax.axis('off')
        
        # Title with info
        title = f"Sunset #{index+1} of {len(self.metadata)}\n"
        title += f"Date: {item['date']} | Sunset: {item['sunset_time'][:10]}"
        if item.get("quality_score"):
            title += f" | Current Score: {item['quality_score']}"
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Instructions
        fig.text(0.5, 0.02, 
                "Rate this sunset's aesthetic quality (1-10 scale)\n"
                "Press number keys 1-10 to score, or use slider",
                ha='center', fontsize=11, style='italic')
        
        # Score display
        score_text = fig.text(0.5, 0.08, f"Score: {self.current_score}", 
                             ha='center', fontsize=16, fontweight='bold',
                             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # Slider for score
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
            self.metadata[index]["quality_score"] = self.current_score
            self.metadata[index]["graded"] = True
            
            # Save immediately
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
            
            print(f"✓ Saved score {self.current_score} for image {index+1}")
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
        plt.show()
    
    def next_image(self):
        """Move to next ungraded image."""
        if self.current_idx < len(self.ungraded_indices) - 1:
            self.current_idx += 1
            idx = self.ungraded_indices[self.current_idx]
            self.current_score = self.metadata[idx].get("quality_score", 5) or 5
            self.show_image(idx)
        else:
            print("\n✓ All images graded!")
            self.show_summary()
    
    def prev_image(self):
        """Move to previous image."""
        if self.current_idx > 0:
            self.current_idx -= 1
            idx = self.ungraded_indices[self.current_idx]
            self.current_score = self.metadata[idx].get("quality_score", 5) or 5
            self.show_image(idx)
    
    def show_summary(self):
        """Show grading summary."""
        graded = [item for item in self.metadata if item.get("graded", False)]
        scores = [item["quality_score"] for item in graded if item.get("quality_score")]
        
        if scores:
            print(f"\nGrading Summary:")
            print(f"  Total graded: {len(graded)}")
            print(f"  Average score: {np.mean(scores):.2f}")
            print(f"  Score range: {min(scores)} - {max(scores)}")
            print(f"  Std dev: {np.std(scores):.2f}")
    
    def start_grading(self):
        """Start the grading session."""
        if not self.ungraded_indices:
            print("All images already graded!")
            return
        
        idx = self.ungraded_indices[self.current_idx]
        self.current_score = self.metadata[idx].get("quality_score", 5) or 5
        self.show_image(idx)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive sunset grading")
    parser.add_argument("--images-dir", type=str, 
                       default="data/grading/images_to_grade",
                       help="Directory with images")
    parser.add_argument("--metadata", type=str,
                       default="data/sunset_images_for_grading/sunset_metadata.json",
                       help="Metadata file")
    
    args = parser.parse_args()
    
    grader = SunsetGrader(args.images_dir, args.metadata)
    grader.start_grading()

