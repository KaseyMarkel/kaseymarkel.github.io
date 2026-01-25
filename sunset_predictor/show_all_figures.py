"""
Display all figures in a grid for review.
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
import subprocess
import sys

def show_figures_summary():
    """Show summary of all figures."""
    figures_dir = Path("figures")
    pdf_files = sorted(figures_dir.glob("*.pdf"))
    
    print("=" * 70)
    print("GENERATED FIGURES SUMMARY")
    print("=" * 70)
    print(f"\nFound {len(pdf_files)} PDF figures:\n")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        size_kb = pdf_file.stat().st_size / 1024
        print(f"{i}. {pdf_file.name:30} ({size_kb:.1f} KB)")
    
    print("\n" + "=" * 70)
    print("FIGURE DESCRIPTIONS:")
    print("=" * 70)
    
    descriptions = {
        "fig1_architecture.pdf": "Model Architecture Diagram - ResNet-18 backbone + regression head",
        "fig2_scatter.pdf": "Prediction vs Ground Truth - Scatter plot with error coloring",
        "fig3_residuals.pdf": "Residual Analysis - Error distribution across prediction range",
        "fig4_histogram.pdf": "Error Distribution - Histogram with normal distribution overlay",
        "fig5_examples.pdf": "Example Predictions - 5 sample images with predictions",
        "fig7_temporal.pdf": "Temporal Performance - MAE over time (full year)",
        "fig8_comparison.pdf": "Model Comparison - Bar chart comparing different models",
        "fig9_gradcam.pdf": "Grad-CAM Visualizations - Model attention heatmaps"
    }
    
    for pdf_file in pdf_files:
        desc = descriptions.get(pdf_file.name, "Figure")
        print(f"\n{pdf_file.name}:")
        print(f"  {desc}")
    
    print("\n" + "=" * 70)
    print("To view figures:")
    print("  open figures/*.pdf")
    print("  or use Preview app on macOS")
    print("=" * 70)
    
    # Try to open all figures
    print("\nAttempting to open figures in Preview...")
    for pdf_file in pdf_files:
        try:
            subprocess.run(['open', str(pdf_file)], check=False)
        except:
            pass

if __name__ == "__main__":
    show_figures_summary()

