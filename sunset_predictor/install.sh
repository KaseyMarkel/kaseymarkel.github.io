#!/bin/bash
# Simple installation script for Sunset Predictor

set -e  # Exit on error

echo "Installing Sunset Predictor dependencies..."
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# Install PyTorch
echo "Installing PyTorch (this may take a few minutes)..."
python3 -m pip install torch torchvision

# Install other dependencies
echo "Installing other dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo "✓ Installation complete!"
echo ""
echo "To verify, run: python3 -c 'import torch; print(\"PyTorch\", torch.__version__)'"

