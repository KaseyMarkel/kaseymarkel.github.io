"""
Generate all figures for the paper.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path
from PIL import Image
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

def create_figure_1_architecture():
    """Figure 1: Model architecture diagram."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Draw architecture
    boxes = [
        ("Midday Image\n(3h before sunset)", 0.1, 0.5, 0.15, 0.2),
        ("ResNet-18\nBackbone", 0.3, 0.5, 0.15, 0.2),
        ("Feature\nExtraction", 0.5, 0.5, 0.15, 0.2),
        ("Quality Head\n(1-10 scale)", 0.7, 0.3, 0.15, 0.2),
        ("Peak Time Head\n(minutes)", 0.7, 0.7, 0.15, 0.2),
    ]
    
    for label, x, y, w, h in boxes:
        rect = plt.Rectangle((x, y-h/2), w, h, 
                           facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x+w/2, y, label, ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Arrows
    arrows = [
        (0.25, 0.5, 0.05, 0),
        (0.45, 0.5, 0.05, 0),
        (0.65, 0.5, 0.05, -0.2),
        (0.65, 0.5, 0.05, 0.2),
    ]
    
    for x, y, dx, dy in arrows:
        ax.arrow(x, y, dx, dy, head_width=0.02, head_length=0.02, 
                fc='black', ec='black', linewidth=2)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Dual Predictor Architecture", fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig("figures/fig1_architecture.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 1: Architecture")

def create_figure_2_scatter():
    """Figure 2: Prediction vs Ground Truth scatter plots."""
    # Load evaluation results
    results_file = Path("data/training/evaluation_results.json")
    if not results_file.exists():
        print("⚠ No evaluation results - creating placeholder")
        return
    
    with open(results_file, "r") as f:
        results = json.load(f)
    
    true_quality = [r["true_quality"] for r in results]
    pred_quality = [r["pred_quality"] for r in results]
    true_peak = [r["true_peak_time"] for r in results]
    pred_peak = [r["pred_peak_time"] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Quality scatter
    ax1.scatter(true_quality, pred_quality, alpha=0.6, s=50, c='steelblue', edgecolors='black', linewidth=0.5)
    ax1.plot([0, 10], [0, 10], 'r--', linewidth=2, label='Perfect prediction')
    ax1.set_xlabel('True Quality Score', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Predicted Quality Score', fontsize=12, fontweight='bold')
    ax1.set_title('Quality Prediction', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    
    # Peak time scatter
    ax2.scatter(true_peak, pred_peak, alpha=0.6, s=50, c='coral', edgecolors='black', linewidth=0.5)
    ax2.plot([-15, 15], [-15, 15], 'r--', linewidth=2, label='Perfect prediction')
    ax2.set_xlabel('True Peak Time (minutes)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Predicted Peak Time (minutes)', fontsize=12, fontweight='bold')
    ax2.set_title('Peak Time Prediction', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xlim(-15, 15)
    ax2.set_ylim(-15, 15)
    
    plt.tight_layout()
    plt.savefig("figures/fig2_scatter.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 2: Scatter plots")

def create_figure_3_residuals():
    """Figure 3: Residual plots."""
    results_file = Path("data/training/evaluation_results.json")
    if not results_file.exists():
        return
    
    with open(results_file, "r") as f:
        results = json.load(f)
    
    quality_errors = [r["quality_error"] for r in results]
    peak_errors = [r["peak_error"] for r in results]
    true_quality = [r["true_quality"] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Quality residuals
    residuals_q = [pred - true for pred, true in 
                   zip([r["pred_quality"] for r in results], 
                       [r["true_quality"] for r in results])]
    ax1.scatter(true_quality, residuals_q, alpha=0.6, s=50, c='steelblue', edgecolors='black', linewidth=0.5)
    ax1.axhline(y=0, color='r', linestyle='--', linewidth=2)
    ax1.set_xlabel('True Quality Score', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Residual (Predicted - True)', fontsize=12, fontweight='bold')
    ax1.set_title('Quality Residuals', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Peak time residuals
    residuals_p = [pred - true for pred, true in 
                   zip([r["pred_peak_time"] for r in results], 
                       [r["true_peak_time"] for r in results])]
    true_peak = [r["true_peak_time"] for r in results]
    ax2.scatter(true_peak, residuals_p, alpha=0.6, s=50, c='coral', edgecolors='black', linewidth=0.5)
    ax2.axhline(y=0, color='r', linestyle='--', linewidth=2)
    ax2.set_xlabel('True Peak Time (minutes)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Residual (Predicted - True)', fontsize=12, fontweight='bold')
    ax2.set_title('Peak Time Residuals', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("figures/fig3_residuals.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 3: Residual plots")

def create_figure_4_examples():
    """Figure 4: Example predictions with images."""
    # Load paper examples
    examples_dir = Path("data/paper_examples")
    if not examples_dir.exists():
        print("⚠ No paper examples found")
        return
    
    example_files = sorted(examples_dir.glob("example_*_score.jpg"))
    
    if len(example_files) == 0:
        print("⚠ No example images found")
        return
    
    # Take up to 6 examples
    examples = example_files[:6]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, img_path in enumerate(examples):
        # Extract score from filename
        score_match = re.search(r'example_(\d+)_score', str(img_path))
        score = score_match.group(1) if score_match else "?"
        
        img = Image.open(img_path)
        axes[i].imshow(img)
        axes[i].axis('off')
        axes[i].set_title(f'Score: {score}/10', fontsize=12, fontweight='bold', pad=10)
    
    # Hide unused subplots
    for i in range(len(examples), len(axes)):
        axes[i].axis('off')
    
    plt.suptitle('Example Sunset Images (10 min after sunset)', 
                fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig("figures/fig4_examples.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 4: Example images")

def create_figure_5_temporal():
    """Figure 5: Temporal analysis - quality over time."""
    # Load training data
    train_file = Path("data/training/train_dataset.json")
    if not train_file.exists():
        return
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    
    # Parse dates and sort
    dates = []
    qualities = []
    for d in train_data:
        try:
            date = datetime.strptime(d["date"], "%Y-%m-%d")
            dates.append(date)
            qualities.append(d["quality_score"])
        except:
            continue
    
    if len(dates) == 0:
        return
    
    # Sort by date
    sorted_data = sorted(zip(dates, qualities))
    dates_sorted, qualities_sorted = zip(*sorted_data)
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates_sorted, qualities_sorted, 'o-', markersize=4, linewidth=1.5, 
           color='steelblue', alpha=0.7)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Sunset Quality Score', fontsize=12, fontweight='bold')
    ax.set_title('Sunset Quality Over Time', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("figures/fig5_temporal.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 5: Temporal analysis")

def create_figure_6_peak_distribution():
    """Figure 6: Distribution of peak times."""
    train_file = Path("data/training/train_dataset.json")
    if not train_file.exists():
        return
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    
    peak_times = [d["peak_time_minutes"] for d in train_data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(peak_times, bins=20, color='coral', edgecolor='black', alpha=0.7)
    ax.axvline(x=np.mean(peak_times), color='red', linestyle='--', linewidth=2, 
              label=f'Mean: {np.mean(peak_times):.1f} min')
    ax.set_xlabel('Peak Time (minutes relative to sun-under-horizon)', 
                 fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Distribution of Peak Sunset Times', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig("figures/fig6_peak_distribution.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 6: Peak time distribution")

def create_figure_7_quality_distribution():
    """Figure 7: Distribution of quality scores."""
    train_file = Path("data/training/train_dataset.json")
    if not train_file.exists():
        return
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    
    qualities = [d["quality_score"] for d in train_data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(qualities, bins=15, color='steelblue', edgecolor='black', alpha=0.7)
    ax.axvline(x=np.mean(qualities), color='red', linestyle='--', linewidth=2,
              label=f'Mean: {np.mean(qualities):.2f}')
    ax.set_xlabel('Quality Score (1-10 scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Distribution of Sunset Quality Scores', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig("figures/fig7_quality_distribution.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 7: Quality distribution")

def create_figure_8_timepoint_comparison():
    """Figure 8: Quality scores across timepoints."""
    # Load scores from all timepoints
    timepoints = [-10, 0, 10]
    tp_scores = {}
    
    for tp in timepoints:
        tp_str = f"{tp:+d}"
        scores_file = Path(f"data/grading_by_timepoint/timepoint_{tp_str}min/scores.json")
        if scores_file.exists():
            with open(scores_file, "r") as f:
                data = json.load(f)
            scores = [s["quality_score"] for s in data.values() if s.get("graded")]
            if scores:
                tp_scores[tp] = scores
    
    if len(tp_scores) == 0:
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    positions = list(tp_scores.keys())
    data_to_plot = [tp_scores[tp] for tp in positions]
    labels = [f"{tp:+d} min" for tp in positions]
    
    bp = ax.boxplot(data_to_plot, positions=positions, labels=labels, 
                    patch_artist=True, widths=3)
    
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)
    
    ax.set_xlabel('Timepoint (minutes relative to sun-under-horizon)', 
                 fontsize=12, fontweight='bold')
    ax.set_ylabel('Quality Score', fontsize=12, fontweight='bold')
    ax.set_title('Quality Scores Across Timepoints', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig("figures/fig8_timepoint_comparison.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 8: Timepoint comparison")

if __name__ == "__main__":
    import re
    from datetime import datetime
    
    print("=" * 70)
    print("GENERATING ALL PAPER FIGURES")
    print("=" * 70)
    print()
    
    # Create figures directory
    Path("figures").mkdir(exist_ok=True)
    
    # Generate all figures
    create_figure_1_architecture()
    create_figure_2_scatter()
    create_figure_3_residuals()
    create_figure_4_examples()
    create_figure_5_temporal()
    create_figure_6_peak_distribution()
    create_figure_7_quality_distribution()
    create_figure_8_timepoint_comparison()
    
    print()
    print("=" * 70)
    print("✓ ALL FIGURES GENERATED")
    print("=" * 70)
    print(f"\nFigures saved to: figures/")
    print(f"Total: {len(list(Path('figures').glob('*.pdf')))} PDF figures")


