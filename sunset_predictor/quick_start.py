"""
Quick start script to generate synthetic data and train a model.
Useful for testing the pipeline when historical data is unavailable.
"""

import subprocess
import sys
from pathlib import Path


def main():
    print("Sunset Predictor - Quick Start")
    print("=" * 50)
    print("\nThis script will:")
    print("1. Generate synthetic training data")
    print("2. Build train/test datasets")
    print("3. Train a model")
    print("4. Evaluate the model")
    print("\nNote: This uses synthetic data. For best results,")
    print("use real LBNL webcam images when available.\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    
    # Step 1: Generate synthetic data
    print("\n[1/4] Generating synthetic data...")
    subprocess.run([
        sys.executable, str(base_dir / "generate_synthetic_data.py"),
        "--num-samples", "200",
        "--output-dir", str(data_dir / "synthetic_images")
    ], check=True)
    
    # Step 2: Build dataset
    print("\n[2/4] Building train/test datasets...")
    subprocess.run([
        sys.executable, str(base_dir / "dataset_builder.py"),
        "--metadata", str(data_dir / "synthetic_images" / "metadata.json"),
        "--image-dir", str(data_dir / "synthetic_images"),
        "--output-dir", str(data_dir / "processed"),
        "--test-size", "0.2"
    ], check=True)
    
    # Step 3: Train model
    print("\n[3/4] Training model...")
    print("(This may take a while...)")
    subprocess.run([
        sys.executable, str(base_dir / "train.py"),
        "--train-metadata", str(data_dir / "processed" / "train_metadata.json"),
        "--test-metadata", str(data_dir / "processed" / "test_metadata.json"),
        "--image-dir", str(data_dir / "synthetic_images"),
        "--model-type", "resnet18",
        "--batch-size", "16",  # Smaller batch for synthetic data
        "--num-epochs", "20",  # Fewer epochs for quick start
        "--learning-rate", "1e-4",
        "--save-dir", str(base_dir / "checkpoints"),
        "--log-dir", str(base_dir / "logs"),
        "--device", "cuda" if sys.platform != "darwin" else "cpu"
    ], check=True)
    
    # Step 4: Evaluate
    print("\n[4/4] Evaluating model...")
    subprocess.run([
        sys.executable, str(base_dir / "evaluate.py"),
        "--test-metadata", str(data_dir / "processed" / "test_metadata.json"),
        "--image-dir", str(data_dir / "synthetic_images"),
        "--checkpoint", str(base_dir / "checkpoints" / "best.pth"),
        "--model-type", "resnet18",
        "--output-dir", str(base_dir / "evaluation")
    ], check=True)
    
    print("\n" + "=" * 50)
    print("Quick start complete!")
    print("\nResults:")
    print(f"- Checkpoints: {base_dir / 'checkpoints'}")
    print(f"- Logs: {base_dir / 'logs'}")
    print(f"- Evaluation: {base_dir / 'evaluation'}")
    print("\nView training progress:")
    print(f"  tensorboard --logdir {base_dir / 'logs'}")


if __name__ == "__main__":
    main()

