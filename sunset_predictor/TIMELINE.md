# Timeline: Getting 300 Sunset Images

## Current Status

- **Videos downloaded:** 8 out of 101
- **Sunset images extracted:** 7 (with correct dates + 10 min after sunset)
- **Remaining videos:** ~93

## Time Estimates

### To Get All 300 Sunsets:

**Option 1: Use YouTube Playlist (101 videos)**
- **Download remaining ~93 videos:** 2-3 hours
  - Each video ~50-100 MB
  - Depends on connection speed
- **Extract sunset frames:** ~10-15 minutes
  - Processing ~100 videos at ~10 seconds each
- **Total:** ~2.5-3.5 hours

**Option 2: Daily Collection**
- Download "yesterday" video daily for 300 days
- **Total:** 300 days (but automated)

## What We've Fixed

✅ **Sunset timing:** Now extracts frames **10 minutes AFTER sunset** (not at sunset)
✅ **Date parsing:** Extracts dates from video titles (2000-2020)
✅ **Frame calculation:** Correctly calculates frame number for target time

## Next Steps

### To Get All 300:

1. **Download remaining videos:**
   ```bash
   python3 download_playlist.py
   ```
   This will skip already downloaded videos and get the rest.

2. **Parse dates from titles:**
   ```bash
   python3 parse_video_dates.py
   ```
   Updates filenames with correct dates.

3. **Extract all sunsets:**
   ```bash
   python3 extract_lhs_sunsets.py --process-all
   ```
   Extracts frames 10 minutes after sunset for each video.

4. **Setup grading:**
   ```bash
   python3 setup_grading.py
   ```

5. **Grade sunsets:**
   ```bash
   python3 grade_sunsets.py
   ```

## Current Extraction Method

- **Target:** Frame 10 minutes after sunset
- **Calculation:** 
  - Get sunset time for video date
  - Add 10 minutes
  - Calculate frame number (LHS: 1 frame per minute, starts 00:01)
- **Result:** Consistent sunset images showing sky ~10 min after sun goes below horizon

## Notes

- YouTube playlist has 101 videos spanning 2000-2020
- Each video is a full day timelapse (1440 frames = 24 hours)
- We extract 1 frame per video (10 min after sunset)
- To get 300 sunsets, we'd need ~300 videos (or use videos multiple times if needed)


