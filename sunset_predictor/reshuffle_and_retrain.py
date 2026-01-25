"""
Complete re-shuffle and re-train pipeline.
Creates new train/test splits and retrains all models from scratch.
Also checks for potential signal loss issues.
"""

import json
import numpy as np
import random
from pathlib import Path
import subprocess
import sys

def set_random_seeds(seed=12345):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except:
        pass

def check_data_quality():
    """Check for potential data quality issues."""
    print("=" * 70)
    print("CHECKING DATA QUALITY")
    print("=" * 70)
    
    # Load datasets
    train_file = Path("data/training/train_dataset.json")
    test_file = Path("data/training/test_dataset.json")
    
    if not train_file.exists() or not test_file.exists():
        print("⚠ Training datasets not found. Run prepare_training_data.py first.")
        return False
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    all_data = train_data + test_data
    
    # Check quality score distribution
    qualities = [d['quality_score'] for d in all_data]
    peak_times = [d['peak_time_minutes'] for d in all_data]
    durations = [d.get('duration_above_5_minutes', 0) for d in all_data]
    
    print(f"\nDataset statistics:")
    print(f"  Total samples: {len(all_data)}")
    print(f"  Quality: mean={np.mean(qualities):.2f}, std={np.std(qualities):.2f}, range=[{np.min(qualities):.1f}, {np.max(qualities):.1f}]")
    print(f"  Peak time: mean={np.mean(peak_times):.2f}, std={np.std(peak_times):.2f}, range=[{np.min(peak_times):.1f}, {np.max(peak_times):.1f}]")
    print(f"  Duration: mean={np.mean(durations):.2f}, std={np.std(durations):.2f}, range=[{np.min(durations):.1f}, {np.max(durations):.1f}]")
    
    # Check for variance
    if np.std(qualities) < 0.5:
        print("  ⚠ WARNING: Very low variance in quality scores!")
    if np.std(peak_times) < 1.0:
        print("  ⚠ WARNING: Very low variance in peak times!")
    
    # Check for correlations between features
    print(f"\nChecking correlations:")
    corr_q_pt = np.corrcoef(qualities, peak_times)[0, 1]
    corr_q_d = np.corrcoef(qualities, durations)[0, 1]
    corr_pt_d = np.corrcoef(peak_times, durations)[0, 1]
    print(f"  Quality vs Peak Time: r={corr_q_pt:.3f}")
    print(f"  Quality vs Duration: r={corr_q_d:.3f}")
    print(f"  Peak Time vs Duration: r={corr_pt_d:.3f}")
    
    # Check image paths
    missing_images = []
    for d in all_data:
        img_path = Path(d['midday_image'])
        if not img_path.exists():
            missing_images.append(d['date'])
    
    if missing_images:
        print(f"\n⚠ WARNING: {len(missing_images)} missing midday images!")
        print(f"  Examples: {missing_images[:5]}")
    else:
        print(f"\n✓ All {len(all_data)} midday images found")
    
    return True

def reshuffle_and_prepare():
    """Create new train/test split with different random seed."""
    print("\n" + "=" * 70)
    print("RE-SHUFFLING TRAIN/TEST SPLIT")
    print("=" * 70)
    
    # Load current dataset
    train_file = Path("data/training/train_dataset.json")
    test_file = Path("data/training/test_dataset.json")
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    # Combine and re-shuffle
    all_data = train_data + test_data
    print(f"Combined dataset: {len(all_data)} samples")
    
    # New random split (different seed)
    set_random_seeds(seed=99999)  # Different from original 42
    indices = np.random.permutation(len(all_data))
    split_idx = int(len(all_data) * 0.8)  # 80/20 split
    
    new_train = [all_data[i] for i in indices[:split_idx]]
    new_test = [all_data[i] for i in indices[split_idx:]]
    
    print(f"New split:")
    print(f"  Train: {len(new_train)} samples")
    print(f"  Test: {len(new_test)} samples")
    
    # Save new datasets
    output_dir = Path("data/training")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "train_dataset.json", "w") as f:
        json.dump(new_train, f, indent=2)
    with open(output_dir / "test_dataset.json", "w") as f:
        json.dump(new_test, f, indent=2)
    
    print(f"\n✓ Saved new train/test splits")
    
    # Also update weather datasets
    print("\nUpdating weather datasets...")
    try:
        result = subprocess.run([sys.executable, "prepare_weather_features.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Weather features updated")
        else:
            print(f"⚠ Weather features update had issues: {result.stderr[:200]}")
    except Exception as e:
        print(f"⚠ Could not update weather features: {e}")

def retrain_all_models():
    """Retrain all models from scratch."""
    print("\n" + "=" * 70)
    print("RETRAINING ALL MODELS")
    print("=" * 70)
    
    models_to_train = [
        ("train_dual_predictor.py", "Image-only model"),
        ("train_weather_predictor.py", "Weather-only model"),
    ]
    
    for script, name in models_to_train:
        print(f"\nTraining {name}...")
        try:
            result = subprocess.run([sys.executable, script], 
                                  capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"✓ {name} trained successfully")
                # Show last few lines of output
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:
                    if line.strip():
                        print(f"  {line}")
            else:
                print(f"✗ {name} training failed:")
                print(f"  {result.stderr[:500]}")
        except subprocess.TimeoutExpired:
            print(f"✗ {name} training timed out")
        except Exception as e:
            print(f"✗ {name} training error: {e}")

def reevaluate_all():
    """Re-evaluate all models."""
    print("\n" + "=" * 70)
    print("RE-EVALUATING ALL MODELS")
    print("=" * 70)
    
    scripts_to_run = [
        ("evaluate_dual_predictor.py", "Image-only evaluation"),
        ("evaluate_weather_models.py", "Weather model comparison"),
    ]
    
    for script, name in scripts_to_run:
        print(f"\nRunning {name}...")
        try:
            result = subprocess.run([sys.executable, script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {name} completed")
                # Show summary
                lines = result.stdout.strip().split('\n')
                for line in lines[-10:]:
                    if line.strip() and ('MAE' in line or 'Correlation' in line or 'RMSE' in line):
                        print(f"  {line}")
            else:
                print(f"✗ {name} failed: {result.stderr[:300]}")
        except Exception as e:
            print(f"✗ {name} error: {e}")

def regenerate_figures():
    """Regenerate all figures."""
    print("\n" + "=" * 70)
    print("REGENERATING ALL FIGURES")
    print("=" * 70)
    
    scripts_to_run = [
        ("create_all_paper_figures_v2.py", "Main figures"),
        ("create_weather_figures.py", "Weather figures"),
        ("create_high_cloud_figures.py", "High-cloud figures"),
    ]
    
    for script, name in scripts_to_run:
        print(f"\nGenerating {name}...")
        try:
            result = subprocess.run([sys.executable, script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {name} generated")
            else:
                print(f"✗ {name} failed: {result.stderr[:300]}")
        except Exception as e:
            print(f"✗ {name} error: {e}")

def check_for_issues():
    """Check for common issues that could cause signal loss."""
    print("\n" + "=" * 70)
    print("CHECKING FOR SIGNAL LOSS ISSUES")
    print("=" * 70)
    
    issues_found = []
    
    # Check if targets are being normalized incorrectly
    train_file = Path("data/training/train_dataset.json")
    with open(train_file, "r") as f:
        train_data = json.load(f)
    
    qualities = [d['quality_score'] for d in train_data]
    
    # Check if quality is in reasonable range
    if max(qualities) > 10 or min(qualities) < 0:
        issues_found.append("Quality scores outside 0-10 range")
    
    # Check for data leakage
    print("\nChecking for data leakage...")
    # This would require checking model code
    
    # Check model architecture
    print("\nChecking model architecture...")
    try:
        from train_dual_predictor import DualPredictor
        model = DualPredictor()
        print(f"  Model: {type(model).__name__}")
        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"  Total parameters: {total_params:,}")
        print(f"  Trainable parameters: {trainable_params:,}")
        
        if trainable_params < 1000:
            issues_found.append("Model may be too small")
        if trainable_params > 50_000_000:
            issues_found.append("Model may be too large (overfitting risk)")
    except Exception as e:
        print(f"  Could not check model: {e}")
    
    if issues_found:
        print("\n⚠ Issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
    else:
        print("\n✓ No obvious issues detected")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    print("=" * 70)
    print("COMPLETE RE-SHUFFLE AND RE-TRAIN PIPELINE")
    print("=" * 70)
    
    # Step 1: Check data quality
    if not check_data_quality():
        print("\n✗ Data quality check failed. Aborting.")
        sys.exit(1)
    
    # Step 2: Re-shuffle train/test split
    reshuffle_and_prepare()
    
    # Step 3: Check for issues
    check_for_issues()
    
    # Step 4: Retrain all models
    retrain_all_models()
    
    # Step 5: Re-evaluate
    reevaluate_all()
    
    # Step 6: Regenerate figures
    regenerate_figures()
    
    print("\n" + "=" * 70)
    print("✓ COMPLETE RE-SHUFFLE AND RE-TRAIN FINISHED")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Review evaluation results")
    print("  2. Check if performance improved")
    print("  3. Regenerate paper: python3 create_complete_paper_v2.py v8")

