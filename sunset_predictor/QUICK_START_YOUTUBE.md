# Quick Start: Download LBNL YouTube Timelapses

## Step 1: Install Dependencies

```bash
cd sunset_predictor

# Install yt-dlp (for YouTube downloads)
python3 -m pip install yt-dlp

# Install ffmpeg (for video processing)
# macOS:
brew install ffmpeg

# Linux:
sudo apt-get install ffmpeg
```

## Step 2: Find YouTube Video

1. Go to YouTube.com
2. Search for: **"LBNL webcam timelapse"** or **"Berkeley Lab timelapse"**
3. Find the video with the last year of footage
4. Copy the YouTube URL

## Step 3: Download and Process

You'll need to know:
- **Start date** of the timelapse (when it began)
- **Speed** (how much real time per frame - usually 1 hour per frame for daily timelapses)

```bash
python3 process_timelapse.py \
    --url https://www.youtube.com/watch?v=YOUR_VIDEO_ID \
    --start-date 2024-01-01 \
    --speed 1.0 \
    --days 365
```

**Example:**
If the timelapse started January 1, 2024, and each frame = 1 hour:

```bash
python3 process_timelapse.py \
    --url https://www.youtube.com/watch?v=abc123xyz \
    --start-date 2024-01-01 \
    --speed 1.0
```

## Step 4: Verify Images

Check that frames were extracted correctly:

```bash
python3 verify_images.py \
    --metadata data/lbnl_frames/metadata.json \
    --image-dir data/lbnl_frames \
    --num-samples 10
```

## Step 5: Build Train/Test Sets

```bash
python3 dataset_builder.py \
    --metadata data/lbnl_frames/metadata.json \
    --image-dir data/lbnl_frames \
    --output-dir data/processed_real \
    --test-size 0.2
```

## Step 6: Train Model

```bash
python3 train.py \
    --train-metadata data/processed_real/train_metadata.json \
    --test-metadata data/processed_real/test_metadata.json \
    --image-dir data/lbnl_frames \
    --model-type resnet18 \
    --batch-size 16 \
    --num-epochs 50 \
    --device cpu
```

## Troubleshooting

**Can't find the video?**
- Try different search terms
- Check LBNL's official YouTube channel
- Look for playlists

**Don't know the start date?**
- Check video description
- Look at video upload date
- Check comments for timelapse info

**Don't know the speed?**
- Check video description
- Calculate: video_duration / real_time_span = speed
- Example: 365 day timelapse in 1 hour video = ~365 hours per frame

