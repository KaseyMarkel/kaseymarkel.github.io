# Sunset Predictor for Berkeley

A machine learning project to predict sunset times in Berkeley, California using historical webcam images from Lawrence Berkeley National Laboratory (LBNL). The model predicts the time until sunset from images captured 3 hours before the actual sunset.

## Overview

This project uses convolutional neural networks (CNNs) to analyze sky images and predict how many hours remain until sunset. The model is trained on images captured approximately 3 hours before sunset, learning visual patterns in the sky that correlate with the approaching sunset.

## Project Structure

```
sunset_predictor/
├── data_collector.py      # Script to download/load webcam images
├── dataset_builder.py      # Creates train/test splits and data loaders
├── model.py                # CNN model architectures
├── train.py                # Training script
├── evaluate.py             # Evaluation and visualization script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have PyTorch installed (with CUDA support if available):
```bash
# For CPU only
pip install torch torchvision

# For CUDA (check your CUDA version)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## Data Collection

### Option 1: Using Historical Archive (if available)

If you have access to LBNL webcam historical archive:

1. Find the archive URL pattern (e.g., `http://www.lbl.gov/webcam/archive/{date}/{time}.jpg`)
2. Update `ARCHIVE_URL_PATTERN` in `data_collector.py`
3. Run the collector:

```python
from data_collector import collect_historical_data
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=30)  # Last 30 days

metadata = collect_historical_data(start_date, end_date, 
                                   output_dir="data/raw_images")
```

### Option 2: Using Existing Images

If you already have a directory of webcam images:

```python
from data_collector import load_existing_images

metadata = load_existing_images("path/to/images", metadata_file=None)
```

The script will attempt to infer timestamps from filenames (patterns like `img_YYYYMMDD_HHMMSS.jpg`).

### Option 3: Manual Collection

1. Download images from the LBNL webcam at times approximately 3 hours before sunset
2. Name them with timestamps: `img_YYYYMMDD_HHMMSS.jpg`
3. Use `load_existing_images()` to create metadata

## Building the Dataset

Once you have images and metadata, create train/test splits:

```bash
python dataset_builder.py \
    --metadata data/raw_images/metadata.json \
    --image-dir data/raw_images \
    --output-dir data/processed \
    --test-size 0.2
```

This will create:
- `data/processed/train_metadata.json`
- `data/processed/test_metadata.json`

## Training

Train the model:

```bash
python train.py \
    --train-metadata data/processed/train_metadata.json \
    --test-metadata data/processed/test_metadata.json \
    --image-dir data/raw_images \
    --model-type resnet18 \
    --batch-size 32 \
    --num-epochs 50 \
    --learning-rate 1e-4 \
    --save-dir checkpoints \
    --log-dir logs \
    --device cuda
```

### Model Options

- `resnet18`: Lightweight ResNet-18 (recommended for starting)
- `resnet34`: Medium ResNet-34
- `resnet50`: Larger ResNet-50 (better accuracy, slower)
- `simple`: Custom lightweight CNN

### Monitoring Training

View training progress with TensorBoard:

```bash
tensorboard --logdir logs
```

## Evaluation

Evaluate a trained model:

```bash
python evaluate.py \
    --test-metadata data/processed/test_metadata.json \
    --image-dir data/raw_images \
    --checkpoint checkpoints/best.pth \
    --model-type resnet18 \
    --output-dir evaluation
```

This generates:
- `evaluation/metrics.json`: Quantitative metrics (MAE, RMSE, R², etc.)
- `evaluation/evaluation_plots.png`: Visualization plots

## Model Architecture

The model uses a pre-trained ResNet backbone (ImageNet weights) with a custom regression head:

1. **Backbone**: ResNet feature extractor (frozen or fine-tuned)
2. **Regressor**: Fully connected layers predicting hours until sunset
   - Input: 512/2048 features (depending on ResNet variant)
   - Output: Single value (hours until sunset)

## Expected Performance

With sufficient training data (100+ images across different seasons/weather):

- **MAE**: 0.3-0.5 hours (18-30 minutes)
- **RMSE**: 0.4-0.7 hours
- **R²**: 0.7-0.9

Performance depends on:
- Dataset size and diversity
- Weather conditions in training data
- Seasonal variation coverage

## Data Requirements

For good model performance, aim for:

- **Minimum**: 50-100 images
- **Recommended**: 200+ images
- **Ideal**: 500+ images across multiple seasons

Images should cover:
- Different times of year (seasonal variation)
- Various weather conditions (clear, cloudy, foggy)
- Different times of day (around 3 hours before sunset)

## Limitations

1. **Historical Data Access**: LBNL webcam historical archive may not be publicly available
2. **Weather Dependency**: Model accuracy may vary with weather conditions not seen in training
3. **Geographic Specificity**: Model trained on Berkeley may not generalize to other locations
4. **Time Window**: Model predicts from images 3 hours before sunset; accuracy may decrease for longer/shorter windows

## Future Improvements

- [ ] Add weather data as additional features
- [ ] Multi-task learning (predict both sunset time and quality)
- [ ] Temporal models (LSTM/Transformer) for video sequences
- [ ] Transfer learning from other sky image datasets
- [ ] Real-time prediction pipeline

## References

- LBNL Webcam: http://www.lbl.gov/webcam/
- Astral library for sunset calculations: https://github.com/sffjunkie/astral
- Berkeley coordinates: 37.8715° N, 122.2730° W

## License

This project is for educational/research purposes. Please respect LBNL's terms of service when accessing webcam data.

## Contact

For questions or issues, please open an issue or contact the repository maintainer.

