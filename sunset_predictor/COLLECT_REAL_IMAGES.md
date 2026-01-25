# Collecting Real LBNL Webcam Images

## Current Status

The current dataset uses **synthetic images** (colored gradients with cloud shapes), not real sky photos. We need real LBNL webcam images to train a proper model.

## Option 1: Find LBNL Webcam URL

1. **Search for LBNL webcam:**
   - Visit https://www.lbl.gov/ and look for webcam links
   - Check if there's a public webcam feed
   - Look for archive/historical data access

2. **Once you have the URL**, update `data_collector.py`:
   ```python
   ARCHIVE_URL_PATTERN = "http://your-found-url/archive/{date}/{time}.jpg"
   ```

3. **Or download current images:**
   ```bash
   python3 download_lbnl_images.py --webcam-url <YOUR_URL> --current
   ```

## Option 2: Manual Image Collection

1. **Download images manually** from LBNL webcam at times ~3 hours before sunset
2. **Save them** with timestamp format: `img_YYYYMMDD_HHMMSS.jpg`
3. **Place them** in a directory (e.g., `data/lbnl_images/`)
4. **Create metadata** using:
   ```python
   from data_collector import load_existing_images
   metadata = load_existing_images("data/lbnl_images")
   ```

## Option 3: Use Existing Sky Image Dataset

If LBNL webcam isn't available, consider:
- Other Berkeley-area webcams
- Public sky image datasets
- Your own photos of Berkeley sky

## Verify Before Training

Always verify images are real before training:

```bash
python3 verify_images.py --metadata data/processed/train_metadata.json --image-dir data/lbnl_images
```

This will show sample images so you can confirm they're actual sky photos.

## Next Steps

1. **Find/collect real images** (one of the options above)
2. **Verify images** are real sky photos
3. **Rebuild dataset** with real images:
   ```bash
   python3 dataset_builder.py --metadata data/lbnl_images/metadata.json --image-dir data/lbnl_images --output-dir data/processed_real
   ```
4. **Train model** on real data:
   ```bash
   python3 train.py --train-metadata data/processed_real/train_metadata.json --test-metadata data/processed_real/test_metadata.json --image-dir data/lbnl_images
   ```

## Quick Test

To test if you have a working webcam URL:

```bash
python3 download_lbnl_images.py --current
```

This will try common URLs and download a test image if successful.

