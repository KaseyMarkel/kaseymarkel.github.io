"""
Generate figures for high-level cloud sweet spot analysis.
Creates Figures 18-20.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr, ttest_ind
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

def create_figure_18_sweet_spot_scatter():
    """Figure 18: Cloud cover vs quality with sweet spot highlighted."""
    # Load analysis results
    analysis_file = Path("data/training/high_cloud_sweet_spot_analysis.json")
    if not analysis_file.exists():
        print("⚠ No sweet spot analysis found")
        return
    
    with open(analysis_file, "r") as f:
        analysis = json.load(f)
    
    data = analysis["data"]
    cloud_cover = np.array([d["cloud_cover"] for d in data])
    quality = np.array([d["quality"] for d in data])
    in_sweet_spot = np.array([d["in_sweet_spot"] for d in data])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot points
    ax.scatter(cloud_cover[in_sweet_spot], quality[in_sweet_spot], 
              alpha=0.7, s=80, c='green', edgecolors='black', linewidth=0.5,
              label='Sweet spot (5-80%)')
    ax.scatter(cloud_cover[~in_sweet_spot], quality[~in_sweet_spot],
              alpha=0.7, s=80, c='red', edgecolors='black', linewidth=0.5,
              label='Outside sweet spot')
    
    # Highlight sweet spot region
    ax.axvspan(5, 80, alpha=0.2, color='green', label='Sweet spot range')
    
    # Add correlation
    corr, p_val = pearsonr(cloud_cover, quality)
    ax.text(0.05, 0.95, f'r = {corr:.3f}\np = {p_val:.3f}',
            transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Add statistics
    sweet_mean = analysis["quality"]["in_sweet_spot"]["mean"]
    outside_mean = analysis["quality"]["outside"]["mean"]
    ax.text(0.05, 0.15, f'In sweet spot: {sweet_mean:.2f} ± {analysis["quality"]["in_sweet_spot"]["std"]:.2f}\n'
                        f'Outside: {outside_mean:.2f} ± {analysis["quality"]["outside"]["std"]:.2f}',
            transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    ax.set_xlabel('Cloud Cover (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Sunset Quality Score', fontsize=12, fontweight='bold')
    ax.set_title('High-Level Cloud Sweet Spot Analysis\n(Cirrus/Mackerel Sky: 5-80% Cloud Cover)', 
                fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 10)
    
    plt.tight_layout()
    plt.savefig("figures/fig18_sweet_spot_scatter.pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ Figure 18: Sweet spot scatter (r={corr:.3f}, p={p_val:.3f})")

def create_figure_19_sweet_spot_comparison():
    """Figure 19: Comparison of quality distributions in vs out of sweet spot."""
    analysis_file = Path("data/training/high_cloud_sweet_spot_analysis.json")
    if not analysis_file.exists():
        return
    
    with open(analysis_file, "r") as f:
        analysis = json.load(f)
    
    data = analysis["data"]
    quality = np.array([d["quality"] for d in data])
    in_sweet_spot = np.array([d["in_sweet_spot"] for d in data])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram comparison
    ax1.hist(quality[in_sweet_spot], bins=15, alpha=0.6, label='In sweet spot', 
            color='green', edgecolor='black', density=True)
    ax1.hist(quality[~in_sweet_spot], bins=15, alpha=0.6, label='Outside sweet spot',
            color='red', edgecolor='black', density=True)
    ax1.set_xlabel('Sunset Quality Score', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Density', fontsize=12, fontweight='bold')
    ax1.set_title('Quality Distribution Comparison', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Box plot comparison
    box_data = [quality[in_sweet_spot], quality[~in_sweet_spot]]
    bp = ax2.boxplot(box_data, labels=['In sweet spot\n(5-80%)', 'Outside\nsweet spot'],
                    patch_artist=True, widths=0.6)
    bp['boxes'][0].set_facecolor('lightgreen')
    bp['boxes'][1].set_facecolor('lightcoral')
    
    # Add mean markers
    ax2.scatter([1, 2], [analysis["quality"]["in_sweet_spot"]["mean"],
                         analysis["quality"]["outside"]["mean"]],
               s=100, marker='D', color='black', zorder=10, label='Mean')
    
    # Add statistics
    t_stat = analysis["quality"]["t_test"]["t_statistic"]
    p_val = analysis["quality"]["t_test"]["p_value"]
    ax2.text(0.5, 0.95, f't-test: t={t_stat:.3f}, p={p_val:.3f}',
            transform=ax2.transAxes, fontsize=10,
            verticalalignment='top', ha='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax2.set_ylabel('Sunset Quality Score', fontsize=12, fontweight='bold')
    ax2.set_title('Quality Score Comparison', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig("figures/fig19_sweet_spot_comparison.pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ Figure 19: Sweet spot comparison (p={p_val:.3f})")

def create_figure_20_cloud_cover_prediction():
    """Figure 20: Using cloud cover as predictor."""
    analysis_file = Path("data/training/high_cloud_sweet_spot_analysis.json")
    if not analysis_file.exists():
        return
    
    with open(analysis_file, "r") as f:
        analysis = json.load(f)
    
    data = analysis["data"]
    cloud_cover = np.array([d["cloud_cover"] for d in data])
    quality = np.array([d["quality"] for d in data])
    peak_time = np.array([d["peak_time"] for d in data])
    duration = np.array([d["duration"] for d in data])
    
    # Simple prediction: if in sweet spot, predict higher quality
    # Use a simple linear model based on sweet spot
    sweet_spot_mask = (cloud_cover >= 5) & (cloud_cover <= 80)
    
    # Predictions: simple rule-based
    pred_quality = np.where(sweet_spot_mask, 
                           analysis["quality"]["in_sweet_spot"]["mean"],
                           analysis["quality"]["outside"]["mean"])
    
    # For peak time and duration, use mean of sweet spot vs outside
    pred_peak = np.where(sweet_spot_mask,
                        analysis["peak_time"]["in_sweet_spot"]["mean"],
                        analysis["peak_time"]["outside"]["mean"])
    
    pred_duration = np.where(sweet_spot_mask,
                            analysis["duration"]["in_sweet_spot"]["mean"],
                            analysis["duration"]["outside"]["mean"])
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
    
    # Quality scatter
    ax1.scatter(quality, pred_quality, alpha=0.6, s=60, c='steelblue', 
               edgecolors='black', linewidth=0.5)
    ax1.plot([0, 10], [0, 10], 'r--', linewidth=2, label='Perfect prediction')
    corr_q, p_val_q = pearsonr(quality, pred_quality)
    mae_q = np.mean(np.abs(quality - pred_quality))
    ax1.text(0.05, 0.95, f'MAE = {mae_q:.2f}\nr = {corr_q:.3f}\np = {p_val_q:.3f}',
            transform=ax1.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    ax1.set_xlabel('True Quality Score', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Predicted Quality Score', fontsize=11, fontweight='bold')
    ax1.set_title('Quality Prediction\n(Sweet Spot Rule)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    
    # Peak time scatter
    peak_range = max(abs(min(peak_time)), abs(max(peak_time)), 
                    abs(min(pred_peak)), abs(max(pred_peak))) + 5
    ax2.scatter(peak_time, pred_peak, alpha=0.6, s=60, c='coral',
               edgecolors='black', linewidth=0.5)
    ax2.plot([-peak_range, peak_range], [-peak_range, peak_range], 'r--', linewidth=2)
    corr_p, p_val_p = pearsonr(peak_time, pred_peak)
    mae_p = np.mean(np.abs(peak_time - pred_peak))
    ax2.text(0.05, 0.95, f'MAE = {mae_p:.2f} min\nr = {corr_p:.3f}\np = {p_val_p:.3f}',
            transform=ax2.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    ax2.set_xlabel('True Peak Time (minutes)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Predicted Peak Time (minutes)', fontsize=11, fontweight='bold')
    ax2.set_title('Peak Time Prediction\n(Sweet Spot Rule)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(-peak_range, peak_range)
    ax2.set_ylim(-peak_range, peak_range)
    
    # Duration scatter
    max_duration = max(max(duration), max(pred_duration)) + 5
    ax3.scatter(duration, pred_duration, alpha=0.6, s=60, c='mediumseagreen',
               edgecolors='black', linewidth=0.5)
    ax3.plot([0, max_duration], [0, max_duration], 'r--', linewidth=2)
    corr_d, p_val_d = pearsonr(duration, pred_duration)
    mae_d = np.mean(np.abs(duration - pred_duration))
    ax3.text(0.05, 0.95, f'MAE = {mae_d:.2f} min\nr = {corr_d:.3f}\np = {p_val_d:.3f}',
            transform=ax3.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    ax3.set_xlabel('True Duration Above 5 (minutes)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Predicted Duration Above 5 (minutes)', fontsize=11, fontweight='bold')
    ax3.set_title('Duration Prediction\n(Sweet Spot Rule)', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, max_duration)
    ax3.set_ylim(0, max_duration)
    
    plt.tight_layout()
    plt.savefig("figures/fig20_cloud_cover_prediction.pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ Figure 20: Cloud cover prediction (Quality r={corr_q:.3f}, Peak r={corr_p:.3f}, Duration r={corr_d:.3f})")

if __name__ == "__main__":
    print("=" * 70)
    print("GENERATING HIGH-LEVEL CLOUD FIGURES")
    print("=" * 70)
    
    create_figure_18_sweet_spot_scatter()
    create_figure_19_sweet_spot_comparison()
    create_figure_20_cloud_cover_prediction()
    
    print("\n" + "=" * 70)
    print("✓ ALL HIGH-LEVEL CLOUD FIGURES GENERATED")
    print("=" * 70)

