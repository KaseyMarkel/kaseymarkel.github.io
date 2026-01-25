"""
Analyze high-level cloud sweet spot hypothesis.
Uses cloud_cover as proxy for high-level clouds (cirrus/mackerel sky).
Sweet spot: 5-80% cloud cover predicts better sunsets.
"""

import pandas as pd
import json
import numpy as np
from scipy.stats import pearsonr
from pathlib import Path

def analyze_sweet_spot():
    """Analyze the sweet spot hypothesis."""
    print("=" * 70)
    print("HIGH-LEVEL CLOUD SWEET SPOT ANALYSIS")
    print("=" * 70)
    
    # Load actual high-level cloud data (prefer this over total cloud cover)
    high_cloud_file = Path("data/weather/high_level_cloud_data.csv")
    if high_cloud_file.exists():
        weather_df = pd.read_csv(high_cloud_file)
        cloud_col = 'cloud_cover_high'
        print("Using actual high-level cloud data")
    else:
        # Fallback to total cloud cover
        weather_df = pd.read_csv("data/weather/weather_data.csv")
        cloud_col = 'cloud_cover'
        print("Using total cloud cover as proxy")
    
    weather_df['date'] = weather_df['date'].astype(str)
    
    # Load all quality scores (train + test)
    with open("data/training/train_dataset.json", "r") as f:
        train_data = json.load(f)
    with open("data/training/test_dataset.json", "r") as f:
        test_data = json.load(f)
    
    all_data = train_data + test_data
    date_to_quality = {d['date']: d['quality_score'] for d in all_data}
    date_to_peak = {d['date']: d['peak_time_minutes'] for d in all_data}
    date_to_duration = {d['date']: d.get('duration_above_5_minutes', 0) for d in all_data}
    
    weather_df['quality'] = weather_df['date'].map(date_to_quality)
    weather_df['peak_time'] = weather_df['date'].map(date_to_peak)
    weather_df['duration'] = weather_df['date'].map(date_to_duration)
    
    # Filter to dates with quality scores
    df = weather_df.dropna(subset=['quality'])
    
    print(f"\nTotal dates with cloud and quality data: {len(df)}")
    print()
    
    # Sweet spot analysis: 5-80% high-level cloud cover
    cloud_cover = df[cloud_col].values
    quality = df['quality'].values
    peak_time = df['peak_time'].values
    duration = df['duration'].values
    
    sweet_spot_mask = (cloud_cover >= 5) & (cloud_cover <= 80)
    
    print("Sweet Spot Analysis (5-80% cloud cover):")
    print(f"  Days in sweet spot: {sweet_spot_mask.sum()} ({100*sweet_spot_mask.sum()/len(df):.1f}%)")
    print(f"  Days outside: {(~sweet_spot_mask).sum()} ({100*(~sweet_spot_mask).sum()/len(df):.1f}%)")
    print()
    
    # Quality comparison
    in_sweet_q = quality[sweet_spot_mask]
    out_sweet_q = quality[~sweet_spot_mask]
    
    print("Quality Score:")
    print(f"  In sweet spot: {in_sweet_q.mean():.2f} ± {in_sweet_q.std():.2f} (range: {in_sweet_q.min():.1f}-{in_sweet_q.max():.1f})")
    print(f"  Outside: {out_sweet_q.mean():.2f} ± {out_sweet_q.std():.2f} (range: {out_sweet_q.min():.1f}-{out_sweet_q.max():.1f})")
    
    # Statistical test
    from scipy.stats import ttest_ind
    t_stat, p_val_q = ttest_ind(in_sweet_q, out_sweet_q)
    print(f"  t-test: t={t_stat:.3f}, p={p_val_q:.3f}")
    print()
    
    # Peak time comparison
    in_sweet_p = peak_time[sweet_spot_mask]
    out_sweet_p = peak_time[~sweet_spot_mask]
    
    print("Peak Time (minutes):")
    print(f"  In sweet spot: {in_sweet_p.mean():.2f} ± {in_sweet_p.std():.2f}")
    print(f"  Outside: {out_sweet_p.mean():.2f} ± {out_sweet_p.std():.2f}")
    print()
    
    # Duration comparison
    in_sweet_d = duration[sweet_spot_mask]
    out_sweet_d = duration[~sweet_spot_mask]
    
    print("Duration Above Quality 5 (minutes):")
    print(f"  In sweet spot: {in_sweet_d.mean():.2f} ± {in_sweet_d.std():.2f}")
    print(f"  Outside: {out_sweet_d.mean():.2f} ± {out_sweet_d.std():.2f}")
    print()
    
    # Correlation analysis
    corr_q, p_corr_q = pearsonr(cloud_cover, quality)
    corr_p, p_corr_p = pearsonr(cloud_cover, peak_time)
    corr_d, p_corr_d = pearsonr(cloud_cover, duration)
    
    print("Correlations (cloud cover vs targets):")
    print(f"  Quality: r={corr_q:.3f}, p={p_corr_q:.3f}")
    print(f"  Peak Time: r={corr_p:.3f}, p={p_corr_p:.3f}")
    print(f"  Duration: r={corr_d:.3f}, p={p_corr_d:.3f}")
    print()
    
    # Save results
    results = {
        "sweet_spot_range": [5, 80],
        "total_dates": int(len(df)),
        "dates_in_sweet_spot": int(sweet_spot_mask.sum()),
        "dates_outside": int((~sweet_spot_mask).sum()),
        "quality": {
            "in_sweet_spot": {
                "mean": float(in_sweet_q.mean()),
                "std": float(in_sweet_q.std()),
                "min": float(in_sweet_q.min()),
                "max": float(in_sweet_q.max())
            },
            "outside": {
                "mean": float(out_sweet_q.mean()),
                "std": float(out_sweet_q.std()),
                "min": float(out_sweet_q.min()),
                "max": float(out_sweet_q.max())
            },
            "t_test": {
                "t_statistic": float(t_stat),
                "p_value": float(p_val_q)
            },
            "correlation": {
                "r": float(corr_q),
                "p_value": float(p_corr_q)
            }
        },
        "peak_time": {
            "in_sweet_spot": {
                "mean": float(in_sweet_p.mean()),
                "std": float(in_sweet_p.std())
            },
            "outside": {
                "mean": float(out_sweet_p.mean()),
                "std": float(out_sweet_p.std())
            },
            "correlation": {
                "r": float(corr_p),
                "p_value": float(p_corr_p)
            }
        },
        "duration": {
            "in_sweet_spot": {
                "mean": float(in_sweet_d.mean()),
                "std": float(in_sweet_d.std())
            },
            "outside": {
                "mean": float(out_sweet_d.mean()),
                "std": float(out_sweet_d.std())
            },
            "correlation": {
                "r": float(corr_d),
                "p_value": float(p_corr_d)
            }
        },
        "data": [
            {
                "date": str(row['date']),
                "cloud_cover": float(row[cloud_col]),
                "quality": float(row['quality']),
                "peak_time": float(row['peak_time']),
                "duration": float(row['duration']),
                "in_sweet_spot": bool((row[cloud_col] >= 5) & (row[cloud_col] <= 80))
            }
            for _, row in df.iterrows()
        ]
    }
    
    output_file = Path("data/training/high_cloud_sweet_spot_analysis.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Analysis saved: {output_file}")
    
    return results

if __name__ == "__main__":
    analyze_sweet_spot()

