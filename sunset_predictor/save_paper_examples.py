"""
Save example images for the paper.
User provided examples: scores 9, 8, 7, 5, 1, 3, 4 (all at +10 min timepoint)
"""

from pathlib import Path
import shutil
import json

def save_paper_examples():
    """Save example images with their scores for the paper."""
    # Create paper examples directory
    paper_dir = Path("data/paper_examples")
    paper_dir.mkdir(parents=True, exist_ok=True)
    
    # The user provided images in order: 9, 8, 7, 5, 1, 3, 4
    # These are all at +10 min timepoint
    # We need to find images from the +10min timepoint that match these scores
    
    # Load scores for +10min timepoint
    scores_file = Path("data/grading_by_timepoint/timepoint_+10min/scores.json")
    if not scores_file.exists():
        print("Scores file not found. Grade the +10min timepoint first.")
        return
    
    with open(scores_file, "r") as f:
        scores = json.load(f)
    
    # Find images with matching scores
    target_scores = [9, 8, 7, 5, 1, 3, 4]
    examples = []
    
    for img_path, score_data in scores.items():
        if score_data.get("graded") and score_data.get("quality_score") in target_scores:
            score = score_data["quality_score"]
            if score not in [e["score"] for e in examples]:  # One example per score
                examples.append({
                    "score": score,
                    "image_path": img_path,
                    "date": score_data.get("date", "Unknown")
                })
    
    # Sort by score (descending)
    examples.sort(key=lambda x: x["score"], reverse=True)
    
    # Copy images to paper examples directory
    print("Saving paper examples...")
    for i, example in enumerate(examples, 1):
        src_path = Path(example["image_path"])
        if src_path.exists():
            # Name: example_9_score.jpg, example_8_score.jpg, etc.
            dst_path = paper_dir / f"example_{example['score']}_score.jpg"
            shutil.copy2(src_path, dst_path)
            print(f"  {i}. Score {example['score']}: {dst_path.name} (Date: {example['date']})")
        else:
            print(f"  ⚠ Image not found: {src_path}")
    
    # Create metadata
    metadata = {
        "timepoint": "+10 minutes",
        "examples": examples,
        "note": "Example sunset images for paper, showing range of quality scores"
    }
    
    metadata_file = paper_dir / "examples_metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Saved {len(examples)} example images")
    print(f"✓ Metadata: {metadata_file}")
    print(f"\nNote: You provided 7 images (scores: 9,8,7,5,1,3,4)")
    print("If these don't match your graded images, manually copy them to:")
    print(f"  {paper_dir}/")

if __name__ == "__main__":
    save_paper_examples()


