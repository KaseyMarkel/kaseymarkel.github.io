"""
Generate comparison figures for weather-based prediction vs image-only.
Creates Figures 12-17 (equivalent to Figures 1-6 but for weather approach).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

def create_figure_12_weather_architecture():
    """Figure 12: Weather-only model architecture."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    boxes = [
        ("Weather Features\n(9 features)", 0.1, 0.5, 0.15, 0.2),
        ("Feature\nEncoder", 0.3, 0.5, 0.15, 0.2),
        ("Shared\nFeatures", 0.5, 0.5, 0.15, 0.2),
        ("Quality Head\n(1-10 scale)", 0.7, 0.25, 0.15, 0.2),
        ("Peak Time Head\n(minutes)", 0.7, 0.5, 0.15, 0.2),
        ("Duration Head\n(minutes above 5)", 0.7, 0.75, 0.15, 0.2),
    ]
    
    for label, x, y, w, h in boxes:
        rect = plt.Rectangle((x, y-h/2), w, h, 
                           facecolor='lightgreen', edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x+w/2, y, label, ha='center', va='center', fontsize=10, fontweight='bold')
    
    arrows = [
        (0.25, 0.5, 0.05, 0),
        (0.45, 0.5, 0.05, 0),
        (0.65, 0.5, 0.05, -0.25),
        (0.65, 0.5, 0.05, 0),
        (0.65, 0.5, 0.05, 0.25),
    ]
    
    for x, y, dx, dy in arrows:
        ax.arrow(x, y, dx, dy, head_width=0.02, head_length=0.02, 
                fc='black', ec='black', linewidth=2)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Weather-Only Predictor Architecture", fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig("figures/fig12_weather_architecture.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 12: Weather architecture")

def create_figure_13_weather_scatter():
    """Figure 13: Weather-only prediction scatter plots."""
    comparison_file = Path("data/training/model_comparison.json")
    if not comparison_file.exists():
        print("⚠ No model comparison found")
        return
    
    with open(comparison_file, "r") as f:
        comparison = json.load(f)
    
    weather_results = comparison.get("weather_only")
    if not weather_results or not weather_results.get("predictions"):
        print("⚠ Weather-only results not found")
        return
    
    predictions = weather_results["predictions"]
    
    true_quality = np.array([p["true_quality"] for p in predictions])
    pred_quality = np.array([p["pred_quality"] for p in predictions])
    true_peak = np.array([p["true_peak_time"] for p in predictions])
    pred_peak = np.array([p["pred_peak_time"] for p in predictions])
    true_duration = np.array([p["true_duration_above_5"] for p in predictions])
    pred_duration = np.array([p["pred_duration_above_5"] for p in predictions])
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
    
    # Quality scatter
    ax1.scatter(true_quality, pred_quality, alpha=0.6, s=50, c='steelblue', edgecolors='black', linewidth=0.5)
    ax1.plot([0, 10], [0, 10], 'r--', linewidth=2, label='Perfect prediction')
    corr_q, p_val_q = pearsonr(true_quality, pred_quality)
    mean_pred = np.mean(pred_quality)
    ax1.axhline(y=mean_pred, color='orange', linestyle=':', linewidth=2, 
               label=f'Baseline (mean={mean_pred:.2f})')
    ax1.text(0.05, 0.95, f'r = {corr_q:.3f}\np = {p_val_q:.3f}', 
            transform=ax1.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    ax1.set_xlabel('True Quality Score', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Predicted Quality Score', fontsize=11, fontweight='bold')
    ax1.set_title('Quality Prediction (Weather)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower right', fontsize=8)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    
    # Peak time scatter
    peak_range = max(abs(min(true_peak)), abs(max(true_peak)), abs(min(pred_peak)), abs(max(pred_peak))) + 5
    ax2.scatter(true_peak, pred_peak, alpha=0.6, s=50, c='coral', edgecolors='black', linewidth=0.5)
    ax2.plot([-peak_range, peak_range], [-peak_range, peak_range], 'r--', linewidth=2, label='Perfect prediction')
    corr_p, p_val_p = pearsonr(true_peak, pred_peak)
    mean_pred_p = np.mean(pred_peak)
    ax2.axhline(y=mean_pred_p, color='orange', linestyle=':', linewidth=2,
               label=f'Baseline (mean={mean_pred_p:.2f})')
    ax2.text(0.05, 0.95, f'r = {corr_p:.3f}\np = {p_val_p:.3f}',
            transform=ax2.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    ax2.set_xlabel('True Peak Time (minutes)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Predicted Peak Time (minutes)', fontsize=11, fontweight='bold')
    ax2.set_title('Peak Time Prediction (Weather)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower right', fontsize=8)
    ax2.set_xlim(-peak_range, peak_range)
    ax2.set_ylim(-peak_range, peak_range)
    
    # Duration scatter
    max_duration = max(max(true_duration), max(pred_duration)) + 5
    ax3.scatter(true_duration, pred_duration, alpha=0.6, s=50, c='mediumseagreen', edgecolors='black', linewidth=0.5)
    ax3.plot([0, max_duration], [0, max_duration], 'r--', linewidth=2, label='Perfect prediction')
    corr_d, p_val_d = pearsonr(true_duration, pred_duration)
    mean_pred_d = np.mean(pred_duration)
    ax3.axhline(y=mean_pred_d, color='orange', linestyle=':', linewidth=2,
               label=f'Baseline (mean={mean_pred_d:.2f})')
    ax3.text(0.05, 0.95, f'r = {corr_d:.3f}\np = {p_val_d:.3f}',
            transform=ax3.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    ax3.set_xlabel('True Duration Above 5 (minutes)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Predicted Duration Above 5 (minutes)', fontsize=11, fontweight='bold')
    ax3.set_title('Duration Above Quality 5 Prediction (Weather)', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='lower right', fontsize=8)
    ax3.set_xlim(0, max_duration)
    ax3.set_ylim(0, max_duration)
    
    plt.tight_layout()
    plt.savefig("figures/fig13_weather_scatter.pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ Figure 13: Weather scatter plots (Quality r={corr_q:.3f}, Peak r={corr_p:.3f}, Duration r={corr_d:.3f})")

def create_figure_14_model_comparison():
    """Figure 14: Compare image-only vs weather-only performance."""
    comparison_file = Path("data/training/model_comparison.json")
    if not comparison_file.exists():
        print("⚠ No model comparison found")
        return
    
    with open(comparison_file, "r") as f:
        comparison = json.load(f)
    
    img_results = comparison.get("image_only")
    weather_results = comparison.get("weather_only")
    
    if not img_results or not weather_results:
        print("⚠ Missing model results")
        return
    
    # Extract metrics
    models = ['Image-Only', 'Weather-Only']
    quality_mae = [
        np.mean([abs(p["pred_quality"] - p["true_quality"]) for p in img_results]),
        weather_results["quality"]["mae"]
    ]
    quality_corr = [
        pearsonr([p["true_quality"] for p in img_results], 
                 [p["pred_quality"] for p in img_results])[0],
        weather_results["quality"]["correlation"]
    ]
    
    peak_mae = [
        np.mean([abs(p["pred_peak_time"] - p["true_peak_time"]) for p in img_results]),
        weather_results["peak_time"]["mae"]
    ]
    peak_corr = [
        pearsonr([p["true_peak_time"] for p in img_results],
                 [p["pred_peak_time"] for p in img_results])[0],
        weather_results["peak_time"]["correlation"]
    ]
    
    duration_mae = [
        np.mean([abs(p.get("pred_duration_above_5", 0) - p.get("true_duration_above_5", 0)) 
                for p in img_results]),
        weather_results["duration"]["mae"]
    ]
    duration_corr = [
        pearsonr([p.get("true_duration_above_5", 0) for p in img_results],
                 [p.get("pred_duration_above_5", 0) for p in img_results])[0],
        weather_results["duration"]["correlation"]
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    x = np.arange(len(models))
    width = 0.35
    
    # MAE comparison
    axes[0, 0].bar(x - width/2, quality_mae, width, label='Image-Only', color='steelblue', alpha=0.7)
    axes[0, 0].bar(x + width/2, [weather_results["quality"]["mae"], 0], width, label='Weather-Only', color='lightgreen', alpha=0.7)
    axes[0, 0].set_ylabel('MAE', fontsize=12, fontweight='bold')
    axes[0, 0].set_title('Quality Prediction MAE', fontsize=12, fontweight='bold')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(models)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    axes[0, 1].bar(x - width/2, peak_mae, width, label='Image-Only', color='coral', alpha=0.7)
    axes[0, 1].bar(x + width/2, [weather_results["peak_time"]["mae"], 0], width, label='Weather-Only', color='lightgreen', alpha=0.7)
    axes[0, 1].set_ylabel('MAE (minutes)', fontsize=12, fontweight='bold')
    axes[0, 1].set_title('Peak Time Prediction MAE', fontsize=12, fontweight='bold')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(models)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    axes[0, 2].bar(x - width/2, duration_mae, width, label='Image-Only', color='mediumseagreen', alpha=0.7)
    axes[0, 2].bar(x + width/2, [weather_results["duration"]["mae"], 0], width, label='Weather-Only', color='lightgreen', alpha=0.7)
    axes[0, 2].set_ylabel('MAE (minutes)', fontsize=12, fontweight='bold')
    axes[0, 2].set_title('Duration Above 5 Prediction MAE', fontsize=12, fontweight='bold')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(models)
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3, axis='y')
    
    # Correlation comparison
    axes[1, 0].bar(x - width/2, quality_corr, width, label='Image-Only', color='steelblue', alpha=0.7)
    axes[1, 0].bar(x + width/2, [weather_results["quality"]["correlation"], 0], width, label='Weather-Only', color='lightgreen', alpha=0.7)
    axes[1, 0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[1, 0].set_ylabel('Correlation (r)', fontsize=12, fontweight='bold')
    axes[1, 0].set_title('Quality Prediction Correlation', fontsize=12, fontweight='bold')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(models)
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    axes[1, 1].bar(x - width/2, peak_corr, width, label='Image-Only', color='coral', alpha=0.7)
    axes[1, 1].bar(x + width/2, [weather_results["peak_time"]["correlation"], 0], width, label='Weather-Only', color='lightgreen', alpha=0.7)
    axes[1, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[1, 1].set_ylabel('Correlation (r)', fontsize=12, fontweight='bold')
    axes[1, 1].set_title('Peak Time Prediction Correlation', fontsize=12, fontweight='bold')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(models)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    axes[1, 2].bar(x - width/2, duration_corr, width, label='Image-Only', color='mediumseagreen', alpha=0.7)
    axes[1, 2].bar(x + width/2, [weather_results["duration"]["correlation"], 0], width, label='Weather-Only', color='lightgreen', alpha=0.7)
    axes[1, 2].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[1, 2].set_ylabel('Correlation (r)', fontsize=12, fontweight='bold')
    axes[1, 2].set_title('Duration Above 5 Prediction Correlation', fontsize=12, fontweight='bold')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(models)
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig("figures/fig14_model_comparison.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 14: Model comparison (Image vs Weather)")

def create_figure_15_weather_features():
    """Figure 15: Weather feature importance/analysis."""
    # Load weather data
    weather_df = pd.read_csv("data/weather/weather_data.csv")
    
    # Load predictions to see which features correlate with quality
    comparison_file = Path("data/training/model_comparison.json")
    with open(comparison_file, "r") as f:
        comparison = json.load(f)
    
    weather_results = comparison.get("weather_only", {}).get("predictions", [])
    
    if not weather_results:
        print("⚠ No weather predictions found")
        return
    
    # Match dates and calculate correlations (only for dates with predictions)
    date_to_quality = {p["date"]: p["true_quality"] for p in weather_results}
    weather_df['quality'] = weather_df['date'].map(date_to_quality)
    
    # Filter to only dates with quality scores
    weather_with_quality = weather_df.dropna(subset=['quality'])
    
    feature_cols = ['temperature_mean', 'humidity', 'cloud_cover', 'precipitation', 
                    'wind_speed', 'pressure']
    correlations = {}
    
    for col in feature_cols:
        if col in weather_with_quality.columns:
            feature_vals = weather_with_quality[col].dropna()
            quality_vals = weather_with_quality.loc[feature_vals.index, 'quality']
            if len(feature_vals) > 2:
                corr, p_val = pearsonr(feature_vals, quality_vals)
                correlations[col] = {'r': corr, 'p': p_val}
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Correlation bar plot
    features = list(correlations.keys())
    corr_values = [correlations[f]['r'] for f in features]
    p_values = [correlations[f]['p'] for f in features]
    
    colors = ['green' if p < 0.05 else 'gray' for p in p_values]
    ax1.barh(features, corr_values, color=colors, alpha=0.7)
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax1.set_xlabel('Correlation with Sunset Quality', fontsize=12, fontweight='bold')
    ax1.set_title('Weather Feature Correlations', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Add p-value annotations
    for i, (feat, corr, p) in enumerate(zip(features, corr_values, p_values)):
        ax1.text(corr + 0.02 if corr >= 0 else corr - 0.02, i, 
                f'r={corr:.3f}, p={p:.3f}', 
                va='center', ha='left' if corr >= 0 else 'right', fontsize=9)
    
    # Feature distributions (use all weather data, not just test set)
    available_cols = [col for col in feature_cols[:3] if col in weather_df.columns]
    if available_cols:
        weather_df[available_cols].boxplot(ax=ax2)
    ax2.set_ylabel('Normalized Values', fontsize=12, fontweight='bold')
    ax2.set_title('Weather Feature Distributions', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig("figures/fig15_weather_features.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 15: Weather feature analysis")

def create_figure_16_combined_comparison():
    """Figure 16: Side-by-side comparison of all predictions."""
    # This will show image-only vs weather-only predictions for same samples
    comparison_file = Path("data/training/model_comparison.json")
    with open(comparison_file, "r") as f:
        comparison = json.load(f)
    
    img_results = comparison.get("image_only", [])
    weather_results = comparison.get("weather_only", {}).get("predictions", [])
    
    if not img_results or not weather_results:
        print("⚠ Missing results for comparison")
        return
    
    # Match by date
    img_dict = {r["date"]: r for r in img_results}
    weather_dict = {r["date"]: r for r in weather_results}
    
    common_dates = sorted(set(img_dict.keys()) & set(weather_dict.keys()))
    
    if len(common_dates) == 0:
        print("⚠ No common dates between models")
        return
    
    # Extract data
    true_quality = [img_dict[d]["true_quality"] for d in common_dates]
    img_pred_q = [img_dict[d]["pred_quality"] for d in common_dates]
    weather_pred_q = [weather_dict[d]["pred_quality"] for d in common_dates]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Quality comparison
    x = np.arange(len(common_dates))
    width = 0.35
    
    axes[0].bar(x - width/2, true_quality, width, label='True', color='black', alpha=0.5)
    axes[0].bar(x, img_pred_q, width, label='Image-Only', color='steelblue', alpha=0.7)
    axes[0].bar(x + width/2, weather_pred_q, width, label='Weather-Only', color='lightgreen', alpha=0.7)
    axes[0].set_ylabel('Quality Score', fontsize=12, fontweight='bold')
    axes[0].set_title('Quality Predictions Comparison', fontsize=12, fontweight='bold')
    axes[0].set_xticks(x[::5])
    axes[0].set_xticklabels([common_dates[i] for i in range(0, len(common_dates), 5)], rotation=45)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Error comparison
    img_errors = [abs(img_pred_q[i] - true_quality[i]) for i in range(len(true_quality))]
    weather_errors = [abs(weather_pred_q[i] - true_quality[i]) for i in range(len(true_quality))]
    
    axes[1].bar(x - width/2, img_errors, width, label='Image-Only', color='steelblue', alpha=0.7)
    axes[1].bar(x + width/2, weather_errors, width, label='Weather-Only', color='lightgreen', alpha=0.7)
    axes[1].set_ylabel('Absolute Error', fontsize=12, fontweight='bold')
    axes[1].set_title('Prediction Errors', fontsize=12, fontweight='bold')
    axes[1].set_xticks(x[::5])
    axes[1].set_xticklabels([common_dates[i] for i in range(0, len(common_dates), 5)], rotation=45)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Scatter: Image vs Weather predictions
    axes[2].scatter(img_pred_q, weather_pred_q, alpha=0.6, s=50, c='purple', edgecolors='black', linewidth=0.5)
    max_val = max(max(img_pred_q), max(weather_pred_q)) + 1
    axes[2].plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Agreement')
    corr, p_val = pearsonr(img_pred_q, weather_pred_q)
    axes[2].text(0.05, 0.95, f'r = {corr:.3f}\np = {p_val:.3f}',
                transform=axes[2].transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    axes[2].set_xlabel('Image-Only Prediction', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Weather-Only Prediction', fontsize=12, fontweight='bold')
    axes[2].set_title('Model Agreement', fontsize=12, fontweight='bold')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlim(0, max_val)
    axes[2].set_ylim(0, max_val)
    
    plt.tight_layout()
    plt.savefig("figures/fig16_combined_comparison.pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ Figure 16: Combined comparison ({len(common_dates)} samples)")

def create_figure_17_residual_comparison():
    """Figure 17: Residual comparison between models."""
    comparison_file = Path("data/training/model_comparison.json")
    with open(comparison_file, "r") as f:
        comparison = json.load(f)
    
    img_results = comparison.get("image_only", [])
    weather_results = comparison.get("weather_only", {}).get("predictions", [])
    
    if not img_results or not weather_results:
        return
    
    # Match by date
    img_dict = {r["date"]: r for r in img_results}
    weather_dict = {r["date"]: r for r in weather_results}
    common_dates = sorted(set(img_dict.keys()) & set(weather_dict.keys()))
    
    true_quality = np.array([img_dict[d]["true_quality"] for d in common_dates])
    img_residuals = np.array([img_dict[d]["pred_quality"] - img_dict[d]["true_quality"] for d in common_dates])
    weather_residuals = np.array([weather_dict[d]["pred_quality"] - weather_dict[d]["true_quality"] for d in common_dates])
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Residual scatter comparison
    axes[0].scatter(true_quality, img_residuals, alpha=0.6, s=50, c='steelblue', 
                   edgecolors='black', linewidth=0.5, label='Image-Only')
    axes[0].scatter(true_quality, weather_residuals, alpha=0.6, s=50, c='lightgreen',
                   edgecolors='black', linewidth=0.5, label='Weather-Only', marker='s')
    axes[0].axhline(y=0, color='r', linestyle='--', linewidth=2)
    axes[0].set_xlabel('True Quality Score', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Residual (Predicted - True)', fontsize=12, fontweight='bold')
    axes[0].set_title('Residual Comparison', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Residual distribution
    axes[1].hist(img_residuals, bins=15, alpha=0.6, label='Image-Only', color='steelblue', edgecolor='black')
    axes[1].hist(weather_residuals, bins=15, alpha=0.6, label='Weather-Only', color='lightgreen', edgecolor='black')
    axes[1].axvline(x=0, color='r', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Residual (Predicted - True)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Frequency', fontsize=12, fontweight='bold')
    axes[1].set_title('Residual Distribution', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig("figures/fig17_residual_comparison.pdf", bbox_inches='tight')
    plt.close()
    print("✓ Figure 17: Residual comparison")

if __name__ == "__main__":
    print("=" * 70)
    print("GENERATING WEATHER FIGURES")
    print("=" * 70)
    
    create_figure_12_weather_architecture()
    create_figure_13_weather_scatter()
    create_figure_14_model_comparison()
    create_figure_15_weather_features()
    create_figure_16_combined_comparison()
    create_figure_17_residual_comparison()
    
    print("\n" + "=" * 70)
    print("✓ ALL WEATHER FIGURES GENERATED")
    print("=" * 70)

