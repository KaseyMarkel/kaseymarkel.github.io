# Getting Started with Sunset Predictor

## Step 1: Generate Synthetic Data (for testing)

Since we don't have access to the LBNL webcam historical archive yet, let's generate synthetic sky images to test the pipeline:

```bash
python3 generate_synthetic_data.py --num-samples 200 --output-dir data/synthetic_images
```

This will create 200 synthetic sky images with appropriate colors based on time until sunset.

## Step 2: Build Train/Test Dataset

Split the data into training and test sets:

```bash
python3 dataset_builder.py \
    --metadata data/synthetic_images/metadata.json \
    --image-dir data/synthetic_images \
    --output-dir data/processed \
    --test-size 0.2
```

This creates:
- `data/processed/train_metadata.json` (80% of data)
- `data/processed/test_metadata.json` (20% of data)

## Step 3: Train the Model

Train a ResNet18 model:

```bash
python3 train.py \
    --train-metadata data/processed/train_metadata.json \
    --test-metadata data/processed/test_metadata.json \
    --image-dir data/synthetic_images \
    --model-type resnet18 \
    --batch-size 16 \
    --num-epochs 20 \
    --learning-rate 1e-4 \
    --device cpu
```

**Note**: Use `--device cpu` on macOS (no CUDA). Training will take 10-30 minutes depending on your machine.

## Step 4: Evaluate the Model

After training, evaluate the model:

```bash
python3 evaluate.py \
    --test-metadata data/processed/test_metadata.json \
    --image-dir data/synthetic_images \
    --checkpoint checkpoints/best.pth \
    --model-type resnet18 \
    --device cpu \
    --output-dir evaluation
```

This will create evaluation plots and metrics in the `evaluation/` directory.

## Quick Start (All-in-One)

Or use the quick start script to do everything:

```bash
python3 quick_start.py
```

## View Training Progress

In a separate terminal, start TensorBoard:

```bash
tensorboard --logdir logs
```

Then open http://localhost:6006 in your browser.

## Next Steps: Using Real LBNL Webcam Data

Once you have access to LBNL webcam historical images:

1. Find the archive URL pattern
2. Update `ARCHIVE_URL_PATTERN` in `data_collector.py`
3. Run: `python3 data_collector.py` to download images
4. Follow steps 2-4 above with the real data

## Troubleshooting

- **Out of memory**: Reduce `--batch-size` (try 8 or 4)
- **Slow training**: Use `--model-type simple` for a lighter model
- **Import errors**: Make sure you're in the `sunset_predictor` directory

