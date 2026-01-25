"""
Create Figure: 5 midday photos with all 8 sunset timepoints.
Shows predicted vs actual scores for the 3 scored timepoints.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import numpy as np
import json
import torch
from pathlib import Path
from PIL import Image
from torchvision import transforms
from train_dual_predictor import DualPredictor

def load_model_and_predict(midday_image_path):
    """Load model and predict quality/peak time for a midday image."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DualPredictor(num_weather_features=0)
    
    model_path = Path("models/dual_predictor.pth")
    if not model_path.exists():
        return None, None
    
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=False))
    model.to(device)
    model.eval()
    
    # Transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Load and predict
    img = Image.open(midday_image_path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        pred_quality, pred_peak, pred_duration = model(img_tensor)
    
    return pred_quality.item(), pred_peak.item(), pred_duration.item()

def get_sunset_images_for_date(date_str, timepoints=[-10, -5, 0, 5, 10, 15, 20, 25]):
    """Get sunset images for all timepoints for a given date - USE ONLY NEW EXTRACTED FRAMES."""
    sunset_images = {}
    
    for tp in timepoints:
        tp_str = f"{tp:+d}"
        # ONLY use newly extracted frames (the fixed ones)
        img_path = Path(f"data/extracted_frames/sunset/{tp_str}min/sunset_{date_str.replace('-', '')}_{tp_str}min.jpg")
        
        if img_path.exists():
            sunset_images[tp] = img_path
    
    return sunset_images

def get_actual_scores(date_str, timepoints=[-10, 0, 10]):
    """Get actual scores for scored timepoints."""
    scores = {}
    
    for tp in timepoints:
        tp_str = f"{tp:+d}"
        scores_file = Path(f"data/grading_by_timepoint/timepoint_{tp_str}min/scores.json")
        if scores_file.exists():
            with open(scores_file, "r") as f:
                data = json.load(f)
            
            # Find score for this date
            for img_path, score_data in data.items():
                if date_str in str(img_path) and score_data.get("graded"):
                    scores[tp] = score_data["quality_score"]
                    break
    
    return scores

def create_figure_examples_grid():
    """Create 5x8 grid showing midday photos and all sunset timepoints."""
    # Load test data
    test_file = Path("data/training/test_dataset.json")
    if not test_file.exists():
        print("⚠ No test dataset found")
        return
    
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    # Select 5 examples (prefer ones with good predictions)
    selected = test_data[:5]  # Take first 5
    
    # Timepoints to show
    all_timepoints = [-10, -5, 0, 5, 10, 15, 20, 25]
    scored_timepoints = [-10, 0, 10]
    
    # Create figure with grid
    fig = plt.figure(figsize=(20, 12))
    gs = GridSpec(5, 9, figure=fig, width_ratios=[1.2] + [1]*8, hspace=0.3, wspace=0.1)
    
    for row, example in enumerate(selected):
        date_str = example["date"]
        midday_path = Path(example["midday_image"])
        
        # Get predictions
        pred_quality, pred_peak, pred_duration = load_model_and_predict(midday_path)
        
        # Get actual scores
        actual_scores = get_actual_scores(date_str, scored_timepoints)
        
        # Column 0: Midday image
        ax_midday = fig.add_subplot(gs[row, 0])
        if midday_path.exists():
            img = Image.open(midday_path)
            ax_midday.imshow(img)
            ax_midday.axis('off')
            # Add prediction annotation
            if pred_quality is not None:
                ax_midday.set_title(f'Midday\nPred Q: {pred_quality:.1f}\nPred Peak: {pred_peak:.1f} min', 
                                   fontsize=9, fontweight='bold', pad=5)
            else:
                ax_midday.set_title('Midday', fontsize=9, fontweight='bold')
        else:
            ax_midday.text(0.5, 0.5, 'Image\nnot found', ha='center', va='center', fontsize=8)
            ax_midday.axis('off')
        
        # Columns 1-8: Sunset images at each timepoint
        for col, tp in enumerate(all_timepoints, 1):
            ax = fig.add_subplot(gs[row, col])
            
            # Get sunset image
            sunset_images = get_sunset_images_for_date(date_str, [tp])
            sunset_path = sunset_images.get(tp)
            
            if sunset_path and sunset_path.exists():
                img = Image.open(sunset_path)
                ax.imshow(img)
                ax.axis('off')
                
                # Add annotation if this is a scored timepoint
                if tp in scored_timepoints:
                    actual = actual_scores.get(tp, "?")
                    # Use predicted quality as approximation for this timepoint
                    # (model predicts average quality, so use that)
                    pred_text = f"Pred: {pred_quality:.1f}" if pred_quality is not None else "Pred: ?"
                    ax.set_title(f'{tp:+d} min\nActual: {actual}\n{pred_text}', 
                               fontsize=8, fontweight='bold', 
                               color='red' if tp in scored_timepoints else 'black',
                               pad=3)
                else:
                    ax.set_title(f'{tp:+d} min', fontsize=8, pad=3)
            else:
                ax.text(0.5, 0.5, f'{tp:+d}\nmin\n(no image)', 
                       ha='center', va='center', fontsize=7)
                ax.axis('off')
    
    # Add column headers
    fig.text(0.05, 0.98, 'Midday\n(3h before)', ha='center', va='top', fontsize=10, fontweight='bold')
    for col, tp in enumerate(all_timepoints, 1):
        x_pos = 0.1 + (col - 0.5) * 0.9 / 8
        fig.text(x_pos, 0.98, f'{tp:+d} min', ha='center', va='top', fontsize=9, fontweight='bold')
    
    # Add overall title
    fig.suptitle('Midday Images and Corresponding Sunset Timepoints\n(Predicted vs Actual Scores for -10, 0, +10 min)', 
                fontsize=14, fontweight='bold', y=0.995)
    
    plt.savefig("figures/fig11_examples_grid.pdf", bbox_inches='tight', dpi=300)
    plt.close()
    print("✓ Figure 11: Examples grid (5x8)")

if __name__ == "__main__":
    create_figure_examples_grid()

