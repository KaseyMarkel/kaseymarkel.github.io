# Installation Guide

## Quick Install

You have two options:

### Option 1: Use the setup script (Recommended)
```bash
cd sunset_predictor
./setup.sh
```

### Option 2: Manual installation

1. **Install PyTorch first** (it's a large package):
   ```bash
   # For macOS (CPU version)
   pip3 install torch torchvision
   
   # If you have CUDA GPU (Linux/Windows):
   # Visit https://pytorch.org/get-started/locally/ for the correct command
   ```

2. **Install other dependencies**:
   ```bash
   cd sunset_predictor
   pip3 install -r requirements.txt
   ```

## Verify Installation

Test that everything is installed correctly:

```bash
python3 -c "import torch; print(f'PyTorch {torch.__version__}')"
python3 -c "import torchvision; print(f'Torchvision {torchvision.__version__}')"
python3 -c "import astral; print('Astral library OK')"
python3 -c "import numpy, pandas, sklearn, PIL, requests, tqdm, tensorboard; print('All dependencies OK')"
```

## Troubleshooting

### If pip3 is not found:
- On macOS: `python3 -m pip install ...` instead of `pip3 install ...`
- Make sure Python 3 is installed: `python3 --version`

### If PyTorch installation fails:
- Try installing without version constraints: `pip3 install torch torchvision --no-cache-dir`
- For macOS with Apple Silicon (M1/M2), you may need: `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu`

### If you get permission errors:
- Use `--user` flag: `pip3 install --user -r requirements.txt`
- Or use a virtual environment (recommended):
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On macOS/Linux
  pip install -r requirements.txt
  ```

## Using a Virtual Environment (Recommended)

To keep dependencies isolated:

```bash
cd sunset_predictor
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate

pip install --upgrade pip
pip install torch torchvision
pip install -r requirements.txt
```

To deactivate later: `deactivate`

