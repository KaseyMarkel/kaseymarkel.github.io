#!/bin/bash
# Setup script for Sunset Predictor
# This installs all required dependencies

echo "Sunset Predictor - Setup Script"
echo "================================"
echo ""

# Check Python version
python3 --version || { echo "Error: Python 3 not found"; exit 1; }

# Upgrade pip first
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install PyTorch (CPU version for macOS)
echo ""
echo "Installing PyTorch (CPU version for macOS)..."
python3 -m pip install torch torchvision

# Install other dependencies
echo ""
echo "Installing other dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo "================================"
echo "Setup complete!"
echo ""
echo "To verify installation, run:"
echo "  python3 -c 'import torch; print(f\"PyTorch {torch.__version__}\")'"
echo "  python3 -c 'import astral; print(\"Astral library OK\")'"

