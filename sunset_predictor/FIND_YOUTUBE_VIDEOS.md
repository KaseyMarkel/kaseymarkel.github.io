# Finding LBNL YouTube Timelapse Videos

## Search Strategy

1. **Search YouTube directly:**
   - Go to YouTube.com
   - Search for: "LBNL webcam timelapse"
   - Search for: "Berkeley Lab webcam"
   - Search for: "Lawrence Berkeley National Laboratory timelapse"

2. **Check LBNL's YouTube channel:**
   - Look for official LBNL/Berkeley Lab channel
   - Check for playlists with webcam/timelapse content

3. **Look for specific patterns:**
   - Videos titled "LBNL Webcam [Year]"
   - Monthly timelapse compilations
   - Annual timelapse videos

## Once You Find a Video

You'll need:
1. **YouTube URL** (e.g., `https://www.youtube.com/watch?v=VIDEO_ID`)
2. **Start date** of the timelapse (when it began)
3. **Timelapse speed** (e.g., 1 frame = 1 hour, or 1 frame = 1 day)

## Usage

```bash
# Install dependencies first
./setup_timelapse.sh

# Process a timelapse video
python3 process_timelapse.py \
    --url https://www.youtube.com/watch?v=VIDEO_ID \
    --start-date 2024-01-01 \
    --speed 1.0 \
    --days 365
```

**Parameters:**
- `--url`: YouTube video URL
- `--start-date`: When the timelapse started (YYYY-MM-DD)
- `--speed`: Hours of real time per video frame (default: 1.0)
- `--days`: Number of days to process (default: 365)

## Example

If you find a timelapse that started Jan 1, 2024, and each frame represents 1 hour:

```bash
python3 process_timelapse.py \
    --url https://www.youtube.com/watch?v=abc123 \
    --start-date 2024-01-01 \
    --speed 1.0
```

This will:
1. Download the video
2. Extract frames at times ~3 hours before sunset for each day
3. Save frames to `data/lbnl_frames/`
4. Create metadata with timestamps

## After Extraction

Once frames are extracted:

1. **Verify frames:**
   ```bash
   python3 verify_images.py --metadata data/lbnl_frames/metadata.json --image-dir data/lbnl_frames
   ```

2. **Build dataset:**
   ```bash
   python3 dataset_builder.py \
       --metadata data/lbnl_frames/metadata.json \
       --image-dir data/lbnl_frames \
       --output-dir data/processed_real
   ```

3. **Train model:**
   ```bash
   python3 train.py \
       --train-metadata data/processed_real/train_metadata.json \
       --test-metadata data/processed_real/test_metadata.json \
       --image-dir data/lbnl_frames
   ```

