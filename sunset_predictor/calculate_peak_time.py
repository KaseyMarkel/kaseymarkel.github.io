"""
Calculate peak sunset time from quality scores across timepoints.
Uses interpolation to find the timepoint with maximum quality.
"""

import json
import numpy as np
from pathlib import Path
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar

def calculate_peak_time(scores_by_timepoint):
    """
    Calculate peak time from quality scores.
    
    Args:
        scores_by_timepoint: dict mapping timepoint (minutes) to quality score
    
    Returns:
        peak_time: minutes relative to sun-under-horizon (interpolated)
        peak_score: quality score at peak
    """
    timepoints = sorted(scores_by_timepoint.keys())
    scores = [scores_by_timepoint[tp] for tp in timepoints]
    
    if len(timepoints) < 2:
        # Not enough data
        return None, None
    
    # Choose interpolation method based on number of points
    if len(timepoints) >= 4:
        # Use cubic interpolation for 4+ points
        kind = 'cubic'
    elif len(timepoints) == 3:
        # Use quadratic for 3 points
        kind = 'quadratic'
    else:
        # Linear for 2 points
        kind = 'linear'
    
    # Interpolate
    f = interp1d(timepoints, scores, kind=kind, bounds_error=False, fill_value='extrapolate')
    
    # Find maximum in range
    result = minimize_scalar(lambda x: -f(x), bounds=(min(timepoints), max(timepoints)), method='bounded')
    
    if result.success:
        peak_time = result.x
        peak_score = f(peak_time)
        return peak_time, peak_score
    
    # Fallback: find max from data points
    max_idx = np.argmax(scores)
    return timepoints[max_idx], scores[max_idx]

def process_all_peak_times(grading_dir="data/grading_by_timepoint"):
    """Calculate peak times for all videos."""
    grading_path = Path(grading_dir)
    
    # Load scores for each timepoint
    timepoints = [-10, -5, 0, 5, 10, 15, 20, 25]
    
    # Collect scores by date
    scores_by_date = {}
    
    for offset in timepoints:
        scores_file = grading_path / f"timepoint_{offset:+d}min" / "scores.json"
        if scores_file.exists():
            with open(scores_file, "r") as f:
                timepoint_scores = json.load(f)
            
            # Extract date from image path and group by date
            for img_path, score_data in timepoint_scores.items():
                if score_data.get("graded"):
                    date = score_data.get("date")
                    if date:
                        if date not in scores_by_date:
                            scores_by_date[date] = {}
                        scores_by_date[date][offset] = score_data["quality_score"]
    
    # Calculate peak times
    peak_times = {}
    
    for date, timepoint_scores in scores_by_date.items():
        if len(timepoint_scores) >= 3:  # Need at least 3 points for interpolation
            peak_time, peak_score = calculate_peak_time(timepoint_scores)
            peak_times[date] = {
                "peak_time_minutes": peak_time,
                "peak_score": float(peak_score),
                "timepoint_scores": timepoint_scores
            }
        else:
            # Not enough data
            peak_times[date] = {
                "peak_time_minutes": None,
                "peak_score": None,
                "timepoint_scores": timepoint_scores,
                "note": "Insufficient data points"
            }
    
    # Save results
    output_file = grading_path / "peak_times.json"
    with open(output_file, "w") as f:
        json.dump(peak_times, f, indent=2)
    
    print(f"✓ Calculated peak times for {len(peak_times)} videos")
    print(f"✓ Saved to: {output_file}")
    
    # Summary
    valid_peaks = [pt for pt in peak_times.values() if pt.get("peak_time_minutes") is not None]
    if valid_peaks:
        peak_times_list = [pt["peak_time_minutes"] for pt in valid_peaks]
        print(f"\nPeak time statistics:")
        print(f"  Average peak time: {np.mean(peak_times_list):.1f} minutes")
        print(f"  Peak time range: {np.min(peak_times_list):.1f} to {np.max(peak_times_list):.1f} minutes")
        print(f"  Std dev: {np.std(peak_times_list):.1f} minutes")
    
    return peak_times

if __name__ == "__main__":
    process_all_peak_times()

