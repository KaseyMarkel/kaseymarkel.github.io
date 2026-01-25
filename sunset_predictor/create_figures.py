"""
Generate publication-quality figures for NeurIPS paper.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from datetime import datetime
import seaborn as sns
from PIL import Image
import torch
from collections import defaultdict

# Set style for publication-quality figures
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'font.serif': ['Times', 'Palatino', 'New Century Schoolbook', 'Bookman', 'Computer Modern Roman'],
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 16,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'axes.linewidth': 1.2,
    'grid.alpha': 0.3
})


def load_predictions(metadata_file, checkpoint_path, model_type="resnet18", device="cpu"):
    """Load model and generate predictions."""
    from model import create_model
    from dataset_builder import SunsetDataset
    from torch.utils.data import DataLoader
    from torchvision import transforms
    
    # Load metadata
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    
    # Create model
    model = create_model(model_type, pretrained=False)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    model.eval()
    
    # Create dataset
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    dataset = SunsetDataset(metadata, "data/synthetic_images", transform=transform)
    loader = DataLoader(dataset, batch_size=32, shuffle=False)
    
    predictions = []
    targets = []
    image_paths = []
    
    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(loader):
            images = images.to(device)
            outputs = model(images)
            predictions.extend(outputs.cpu().numpy())
            targets.extend(labels.cpu().numpy())
            image_paths.extend([metadata[batch_idx * 32 + i]["image_path"] 
                               for i in range(len(outputs))])
    
    return np.array(predictions), np.array(targets), image_paths, metadata


def figure2_scatter_plot(predictions, targets, output_path="figures/fig2_scatter.pdf"):
    """Figure 2: Prediction vs Ground Truth Scatter Plot"""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Calculate errors for coloring
    errors = np.abs(predictions - targets)
    
    # Create scatter plot with color by error
    scatter = ax.scatter(targets, predictions, c=errors, cmap='RdYlGn_r', 
                        alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
    
    # Perfect prediction line
    min_val = min(targets.min(), predictions.min())
    max_val = max(targets.max(), predictions.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', 
           linewidth=2, label='Perfect Prediction', alpha=0.8)
    
    # Labels and title
    ax.set_xlabel('True Hours Until Sunset', fontweight='bold')
    ax.set_ylabel('Predicted Hours Until Sunset', fontweight='bold')
    ax.set_title('Prediction Accuracy', fontweight='bold', pad=15)
    
    # Calculate and display metrics
    mae = np.mean(np.abs(predictions - targets))
    rmse = np.sqrt(np.mean((predictions - targets)**2))
    r2 = 1 - np.sum((targets - predictions)**2) / np.sum((targets - targets.mean())**2)
    
    # Add text box with metrics
    textstr = f'MAE: {mae:.2f} hours\nRMSE: {rmse:.2f} hours\nR²: {r2:.2f}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', bbox=props)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Absolute Error (hours)', rotation=270, labelpad=20)
    
    ax.legend(loc='lower right', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    print(f"✓ Saved: {output_path}")
    plt.close()


def figure3_residual_plot(predictions, targets, output_path="figures/fig3_residuals.pdf"):
    """Figure 3: Residual Plot"""
    fig, ax = plt.subplots(figsize=(7, 5))
    
    residuals = predictions - targets
    
    # Scatter plot
    ax.scatter(targets, residuals, alpha=0.6, s=50, c='steelblue', 
              edgecolors='black', linewidth=0.5)
    
    # Zero line
    ax.axhline(y=0, color='r', linestyle='--', linewidth=2, label='Zero Error')
    
    # Mean residual line
    mean_residual = residuals.mean()
    ax.axhline(y=mean_residual, color='orange', linestyle='--', 
              linewidth=1.5, label=f'Mean: {mean_residual:.3f}')
    
    # ±1 std dev bands
    std_residual = residuals.std()
    ax.axhspan(-std_residual, std_residual, alpha=0.2, color='gray', 
              label=f'±1σ: {std_residual:.2f}')
    
    ax.set_xlabel('True Hours Until Sunset', fontweight='bold')
    ax.set_ylabel('Residual (Predicted - True)', fontweight='bold')
    ax.set_title('Residual Analysis', fontweight='bold', pad=15)
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    print(f"✓ Saved: {output_path}")
    plt.close()


def figure4_error_histogram(predictions, targets, output_path="figures/fig4_histogram.pdf"):
    """Figure 4: Error Distribution Histogram"""
    fig, ax = plt.subplots(figsize=(7, 5))
    
    errors = predictions - targets
    
    # Histogram
    n, bins, patches = ax.hist(errors, bins=30, edgecolor='black', 
                              linewidth=1.2, alpha=0.7, color='steelblue')
    
    # Overlay normal distribution
    mu, sigma = errors.mean(), errors.std()
    x = np.linspace(errors.min(), errors.max(), 100)
    normal = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma)**2)
    normal = normal * len(errors) * (bins[1] - bins[0])  # Scale to match histogram
    ax.plot(x, normal, 'r-', linewidth=2.5, label=f'Normal(μ={mu:.3f}, σ={sigma:.3f})')
    
    # Vertical lines for mean and percentiles
    ax.axvline(mu, color='red', linestyle='--', linewidth=2, label=f'Mean: {mu:.3f}')
    ax.axvline(np.percentile(errors, 25), color='orange', linestyle=':', 
              linewidth=1.5, label=f'Q1: {np.percentile(errors, 25):.3f}')
    ax.axvline(np.percentile(errors, 75), color='orange', linestyle=':', 
              linewidth=1.5, label=f'Q3: {np.percentile(errors, 75):.3f}')
    
    ax.set_xlabel('Prediction Error (hours)', fontweight='bold')
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.set_title('Error Distribution', fontweight='bold', pad=15)
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    print(f"✓ Saved: {output_path}")
    plt.close()


def figure5_example_predictions(metadata, predictions, targets, image_dir, 
                               output_path="figures/fig5_examples.pdf"):
    """Figure 5: Example Predictions"""
    # Select diverse examples
    errors = np.abs(predictions - targets)
    
    # Get examples: best, median, worst, and two random
    best_idx = np.argmin(errors)
    worst_idx = np.argmax(errors)
    median_idx = np.argsort(errors)[len(errors)//2]
    random_indices = np.random.choice(len(errors), 2, replace=False)
    
    indices = [best_idx, median_idx, worst_idx] + list(random_indices)
    
    fig, axes = plt.subplots(1, 5, figsize=(16, 3.5))
    
    for idx, ax in zip(indices, axes):
        # Load image
        img_path = Path(metadata[idx]["image_path"])
        if not img_path.is_absolute():
            img_path = Path(image_dir) / img_path
        
        try:
            img = Image.open(img_path).convert("RGB")
            ax.imshow(img)
        except:
            ax.text(0.5, 0.5, "Image not found", ha='center', va='center')
        
        # Add text overlay
        true_val = targets[idx]
        pred_val = predictions[idx]
        error = errors[idx]
        
        capture_time = datetime.fromisoformat(metadata[idx]["capture_time"])
        
        textstr = (
            f"Time: {capture_time.strftime('%m/%d %H:%M')}\n"
            f"True: {true_val:.2f} hrs\n"
            f"Pred: {pred_val:.2f} hrs\n"
            f"Error: {error*60:.1f} min"
        )
        
        # Color code by error
        if error < 0.2:
            bgcolor = 'lightgreen'
        elif error < 0.4:
            bgcolor = 'lightyellow'
        else:
            bgcolor = 'lightcoral'
        
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor=bgcolor, alpha=0.9, edgecolor='black', linewidth=1))
        
        ax.axis('off')
        ax.set_title(f"Example {list(indices).index(idx)+1}", 
                    fontweight='bold', pad=5)
    
    plt.suptitle('Example Predictions', fontweight='bold', fontsize=14, y=1.02)
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    print(f"✓ Saved: {output_path}")
    plt.close()


def figure7_temporal_performance(metadata, predictions, targets, 
                               output_path="figures/fig7_temporal.pdf"):
    """Figure 7: Temporal Performance Over Time"""
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Group by date and calculate MAE
    date_mae = defaultdict(list)
    dates = []
    
    for i, item in enumerate(metadata):
        date = datetime.fromisoformat(item["capture_time"]).date()
        error = abs(predictions[i] - targets[i])
        date_mae[date].append(error)
        dates.append(date)
    
    # Calculate daily MAE
    unique_dates = sorted(set(dates))
    daily_mae = [np.mean(date_mae[date]) for date in unique_dates]
    
    # Plot
    ax.plot(unique_dates, daily_mae, 'o-', markersize=4, linewidth=1.5, 
           color='steelblue', alpha=0.7, label='Daily MAE')
    
    # Rolling average
    window = 7  # 7-day rolling average
    if len(daily_mae) >= window:
        rolling_mae = np.convolve(daily_mae, np.ones(window)/window, mode='valid')
        rolling_dates = unique_dates[window-1:]
        ax.plot(rolling_dates, rolling_mae, '-', linewidth=2.5, 
               color='darkred', label=f'{window}-day rolling average')
    
    # Overall mean
    overall_mae = np.mean(daily_mae)
    ax.axhline(y=overall_mae, color='gray', linestyle='--', 
              linewidth=2, label=f'Overall MAE: {overall_mae:.3f}')
    
    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Mean Absolute Error (hours)', fontweight='bold')
    ax.set_title('Prediction Accuracy Over Time', fontweight='bold', pad=15)
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Format x-axis dates
    fig.autofmt_xdate()
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    print(f"✓ Saved: {output_path}")
    plt.close()


def figure8_model_comparison(output_path="figures/fig8_comparison.pdf"):
    """Figure 8: Model Comparison Bar Chart"""
    # Example data - replace with actual results
    models = ['Simple\nCNN', 'ResNet-18', 'ResNet-34', 'ResNet-50']
    mae_values = [0.42, 0.27, 0.26, 0.25]
    rmse_values = [0.51, 0.34, 0.33, 0.32]
    r2_values = [0.45, 0.78, 0.79, 0.80]
    
    x = np.arange(len(models))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars1 = ax.bar(x - width, mae_values, width, label='MAE', 
                   color='steelblue', edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x, rmse_values, width, label='RMSE', 
                   color='coral', edgecolor='black', linewidth=1.2)
    bars3 = ax.bar(x + width, r2_values, width, label='R²', 
                   color='lightgreen', edgecolor='black', linewidth=1.2)
    
    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_ylabel('Metric Value', fontweight='bold')
    ax.set_title('Model Comparison', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.set_ylim([0, max(max(mae_values), max(rmse_values), max(r2_values)) * 1.15])
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    print(f"✓ Saved: {output_path}")
    plt.close()


def main():
    """Generate all figures."""
    print("Generating publication-quality figures...")
    print("=" * 60)
    
    # Load predictions if checkpoint exists
    checkpoint_path = Path("checkpoints/best.pth")
    metadata_file = "data/processed/test_metadata.json"
    image_dir = "data/synthetic_images"
    
    if checkpoint_path.exists() and Path(metadata_file).exists():
        print("Loading model predictions...")
        predictions, targets, image_paths, metadata = load_predictions(
            metadata_file, checkpoint_path
        )
        
        print(f"Loaded {len(predictions)} predictions")
        print("\nGenerating figures...")
        
        # Generate figures
        figure2_scatter_plot(predictions, targets)
        figure3_residual_plot(predictions, targets)
        figure4_error_histogram(predictions, targets)
        figure5_example_predictions(metadata, predictions, targets, image_dir)
        figure7_temporal_performance(metadata, predictions, targets)
        
    else:
        print("⚠ Checkpoint or metadata not found. Generating example figures...")
        # Generate example figures with dummy data
        np.random.seed(42)
        targets = np.random.uniform(2.5, 3.5, 100)
        predictions = targets + np.random.normal(0, 0.3, 100)
        
        figure2_scatter_plot(predictions, targets)
        figure3_residual_plot(predictions, targets)
        figure4_error_histogram(predictions, targets)
    
    # Model comparison (uses example data)
    figure8_model_comparison()
    
    print("\n" + "=" * 60)
    print("✓ All figures generated!")
    print("Check the 'figures/' directory for PDF files.")


if __name__ == "__main__":
    main()

