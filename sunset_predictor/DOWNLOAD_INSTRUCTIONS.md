# Download Instructions - Simplified Naming

## Filepath for Downloaded Videos

**Full path:**
```
/Users/kasey/personal_website/sunset_predictor/data/lhs_timelapses
```

## Naming Convention (Simplified!)

Just use:
```
lhs_XXX.mp4
```

Where `XXX` is the **Index number** from the CSV file. Leading zeros are optional but recommended for sorting.

**Examples:**
- Video #2: `lhs_002.mp4` or `lhs_2.mp4` (both work!)
- Video #8: `lhs_008.mp4` or `lhs_8.mp4`
- Video #42: `lhs_042.mp4` or `lhs_42.mp4`
- Video #100: `lhs_100.mp4`

**Pattern:** `lhs_` followed by the Index number, then `.mp4`

## How to Download

1. Open `video_download_status.csv` in Excel/Numbers/Google Sheets
2. Filter to show only videos with "✗ Needs Download"
3. For each video:
   - Click the YouTube URL
   - Download the video (use any YouTube downloader)
   - Rename it to `lhs_XXX.mp4` (where XXX is the Index number)
   - Place it in: `/Users/kasey/personal_website/sunset_predictor/data/lhs_timelapses/`

## After Downloading

Once you've placed videos in the folder, run:

```bash
cd /Users/kasey/personal_website/sunset_predictor
python3 extract_lhs_sunsets.py --process-all
```

The script will:
- Find all videos (including your new `lhs_XXX.mp4` files)
- Look up dates from the playlist CSV
- Extract sunset frames automatically

## Quick Reference

- **CSV file:** `video_download_status.csv` (shows all videos with links)
- **Download folder:** `/Users/kasey/personal_website/sunset_predictor/data/lhs_timelapses/`
- **Naming:** `lhs_XXX.mp4` (XXX = Index number from CSV)

That's it! Much simpler. 🎉

