"""
Prepare training data from graded timepoints.
Loads scores from -10, 0, +10 timepoints and creates train/test splits.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import pandas as pd
import re

def load_graded_scores(timepoints=[-10, -5, 0, 5, 10, 15, 20, 25], grading_dir="data/grading_by_timepoint"):
    """Load all graded scores from specified timepoints."""
    grading_path = Path(grading_dir)
    
    # Collect scores by date
    scores_by_date = {}
    
    for offset in timepoints:
        offset_str = f"{offset:+d}" if offset >= 0 else f"{offset}"
        scores_file = grading_path / f"timepoint_{offset_str}min" / "scores.json"
        
        if scores_file.exists():
            with open(scores_file, "r") as f:
                timepoint_scores = json.load(f)
            
            # Extract date and score from each image
            for img_path, score_data in timepoint_scores.items():
                if score_data.get("graded"):
                    date = score_data.get("date")
                    # Extract date from image path if not in score_data
                    if not date or date == "Unknown":
                        # Try YYYY-MM-DD format first
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(img_path))
                        if date_match:
                            date = date_match.group(1)
                        else:
                            # Try YYYYMMDD format
                            date_match = re.search(r'(\d{8})', str(img_path))
                            if date_match:
                                date_str = date_match.group(1)
                                date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    
                    if date and date != "Unknown":
                        if date not in scores_by_date:
                            scores_by_date[date] = {}
                        scores_by_date[date][offset] = score_data["quality_score"]
    
    print(f"Loaded scores for {len(scores_by_date)} dates")
    print(f"Timepoints: {timepoints}")
    
    return scores_by_date

def calculate_peak_times(scores_by_date):
    """Calculate peak times from scores across timepoints."""
    from calculate_peak_time import calculate_peak_time
    
    peak_times = {}
    
    for date, timepoint_scores in scores_by_date.items():
        if len(timepoint_scores) >= 2:  # Need at least 2 points
            peak_time, peak_score = calculate_peak_time(timepoint_scores)
            peak_times[date] = {
                "peak_time_minutes": peak_time,
                "peak_score": float(peak_score) if peak_score else None,
                "timepoint_scores": timepoint_scores
            }
        else:
            peak_times[date] = {
                "peak_time_minutes": None,
                "peak_score": None,
                "timepoint_scores": timepoint_scores
            }
    
    return peak_times

def calculate_duration_above_5(scores_by_date):
    """Calculate duration (in minutes) that sunset quality is above 5."""
    durations = {}
    
    for date, timepoint_scores in scores_by_date.items():
        # We have scores at -10, 0, +10 minutes
        # Need to estimate when quality crosses 5 threshold
        sorted_tps = sorted(timepoint_scores.keys())
        
        if len(sorted_tps) < 2:
            durations[date] = None
            continue
        
        # Interpolate to find when quality crosses 5
        times = sorted_tps
        scores = [timepoint_scores[tp] for tp in times]
        
        # Find intervals where quality > 5
        duration = 0.0
        
        # Check each interval
        for i in range(len(times) - 1):
            t1, t2 = times[i], times[i+1]
            s1, s2 = scores[i], scores[i+1]
            
            # If both above 5, add full interval
            if s1 > 5 and s2 > 5:
                duration += (t2 - t1)
            # If crosses threshold, find intersection
            elif (s1 <= 5 and s2 > 5) or (s1 > 5 and s2 <= 5):
                # Linear interpolation to find crossing point
                if s2 != s1:
                    t_cross = t1 + (5 - s1) * (t2 - t1) / (s2 - s1)
                    if s1 > 5:
                        duration += (t_cross - t1)
                    else:
                        duration += (t2 - t_cross)
        
        # If we have all 8 timepoints, we don't need extrapolation
        # Just use the actual data we have
        durations[date] = max(0, duration)  # Ensure non-negative
    
    return durations

def create_training_dataset(scores_by_date, peak_times, durations_above_5, midday_dir="data/extracted_frames/midday"):
    """Create training dataset with midday images, quality scores, peak times, and duration above 5."""
    midday_path = Path(midday_dir)
    
    dataset = []
    
    for date, timepoint_scores in scores_by_date.items():
        # Midday images use YYYYMMDD format
        date_compact = date.replace("-", "")
        midday_img = midday_path / f"midday_{date_compact}.jpg"
        
        if not midday_img.exists():
            continue
        
        # Calculate average quality (or use peak score)
        quality_scores = [s for s in timepoint_scores.values()]
        avg_quality = np.mean(quality_scores)
        max_quality = np.max(quality_scores)
        
        # Get peak time
        peak_data = peak_times.get(date, {})
        peak_time = peak_data.get("peak_time_minutes")
        
        if peak_time is None:
            # Estimate from max score timepoint
            max_score_timepoint = max(timepoint_scores.items(), key=lambda x: x[1])[0]
            peak_time = float(max_score_timepoint)
        
        # Get duration above quality 5
        duration = durations_above_5.get(date)
        if duration is None:
            # Estimate: if max quality > 5, assume some duration
            if max_quality > 5:
                duration = 10.0  # Rough estimate
            else:
                duration = 0.0
        
        dataset.append({
            "date": date,
            "midday_image": str(midday_img),
            "quality_score": float(avg_quality),  # Average across timepoints
            "max_quality": float(max_quality),
            "peak_time_minutes": float(peak_time),
            "duration_above_5_minutes": float(duration),
            "timepoint_scores": timepoint_scores
        })
    
    print(f"\nCreated dataset with {len(dataset)} samples")
    if len(dataset) > 0:
        print(f"  Quality range: {min(d['quality_score'] for d in dataset):.1f} - {max(d['quality_score'] for d in dataset):.1f}")
        print(f"  Peak time range: {min(d['peak_time_minutes'] for d in dataset):.1f} - {max(d['peak_time_minutes'] for d in dataset):.1f} minutes")
        durations = [d['duration_above_5_minutes'] for d in dataset if d.get('duration_above_5_minutes') is not None]
        if durations:
            print(f"  Duration above 5: {min(durations):.1f} - {max(durations):.1f} minutes")
    else:
        print("  ⚠ No samples created - check that midday images exist for graded dates")
    
    return dataset

def split_train_test(dataset, test_size=0.2, random_state=42):
    """Split dataset into train and test sets."""
    np.random.seed(random_state)
    indices = np.random.permutation(len(dataset))
    
    split_idx = int(len(dataset) * (1 - test_size))
    train_indices = indices[:split_idx]
    test_indices = indices[split_idx:]
    
    train_set = [dataset[i] for i in train_indices]
    test_set = [dataset[i] for i in test_indices]
    
    print(f"\nTrain/Test Split:")
    print(f"  Train: {len(train_set)} samples")
    print(f"  Test: {len(test_set)} samples")
    
    return train_set, test_set

def save_datasets(train_set, test_set, output_dir="data/training"):
    """Save train and test datasets."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save as JSON
    train_file = output_path / "train_dataset.json"
    test_file = output_path / "test_dataset.json"
    
    with open(train_file, "w") as f:
        json.dump(train_set, f, indent=2)
    
    with open(test_file, "w") as f:
        json.dump(test_set, f, indent=2)
    
    print(f"\n✓ Saved datasets:")
    print(f"  Train: {train_file}")
    print(f"  Test: {test_file}")
    
    # Also create CSV for easy viewing
    train_df = pd.DataFrame([
        {
            "date": d["date"],
            "quality_score": d["quality_score"],
            "peak_time_minutes": d["peak_time_minutes"],
            "duration_above_5_minutes": d.get("duration_above_5_minutes", 0),
            "max_quality": d["max_quality"]
        }
        for d in train_set
    ])
    
    test_df = pd.DataFrame([
        {
            "date": d["date"],
            "quality_score": d["quality_score"],
            "peak_time_minutes": d["peak_time_minutes"],
            "duration_above_5_minutes": d.get("duration_above_5_minutes", 0),
            "max_quality": d["max_quality"]
        }
        for d in test_set
    ])
    
    train_df.to_csv(output_path / "train_dataset.csv", index=False)
    test_df.to_csv(output_path / "test_dataset.csv", index=False)
    
    print(f"  CSV files also created")
    
    return train_file, test_file

if __name__ == "__main__":
    print("=" * 70)
    print("PREPARING TRAINING DATA")
    print("=" * 70)
    
    # Load graded scores
    print("\n[1/4] Loading graded scores...")
    scores_by_date = load_graded_scores(timepoints=[-10, -5, 0, 5, 10, 15, 20, 25])
    
    # Calculate peak times
    print("\n[2/5] Calculating peak times...")
    peak_times = calculate_peak_times(scores_by_date)
    
    # Calculate duration above quality 5
    print("\n[3/5] Calculating duration above quality 5...")
    durations_above_5 = calculate_duration_above_5(scores_by_date)
    
    # Create dataset
    print("\n[4/5] Creating training dataset...")
    dataset = create_training_dataset(scores_by_date, peak_times, durations_above_5)
    
    # Split train/test
    print("\n[5/5] Splitting into train/test sets...")
    train_set, test_set = split_train_test(dataset)
    
    # Save datasets
    print("\n[6/6] Saving datasets...")
    save_datasets(train_set, test_set)
    
    print("\n" + "=" * 70)
    print("✓ DATA PREPARATION COMPLETE")
    print("=" * 70)
    print("\nNext: Train model with:")
    print("  python3 train_dual_predictor.py")

