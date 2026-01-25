"""
Create a combined overview of all figures.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path

def create_figure_overview():
    """Create an overview page showing all figures."""
    fig, ax = plt.subplots(figsize=(12, 16))
    ax.axis('off')
    
    figures_dir = Path("figures")
    pdf_files = sorted(figures_dir.glob("*.pdf"))
    
    # Title
    ax.text(0.5, 0.98, "Sunset Predictor - All Figures", 
           ha='center', va='top', fontsize=20, fontweight='bold',
           transform=ax.transAxes)
    
    # List all figures
    y_start = 0.92
    y_spacing = 0.11
    
    descriptions = {
        "fig1_architecture.pdf": "Figure 1: Model Architecture Diagram",
        "fig2_scatter.pdf": "Figure 2: Prediction vs Ground Truth Scatter Plot",
        "fig3_residuals.pdf": "Figure 3: Residual Analysis",
        "fig4_histogram.pdf": "Figure 4: Error Distribution Histogram",
        "fig5_examples.pdf": "Figure 5: Example Predictions (5 samples)",
        "fig7_temporal.pdf": "Figure 6: Temporal Performance Over Time",
        "fig8_comparison.pdf": "Figure 7: Model Comparison",
        "fig9_gradcam.pdf": "Figure 8: Grad-CAM Attention Visualizations"
    }
    
    for i, pdf_file in enumerate(pdf_files):
        y_pos = y_start - i * y_spacing
        
        # File info box
        size_kb = pdf_file.stat().st_size / 1024
        info_text = f"{descriptions.get(pdf_file.name, pdf_file.name)}\nFile: {pdf_file.name} ({size_kb:.1f} KB)"
        
        # Draw box
        rect = Rectangle((0.05, y_pos - 0.05), 0.9, 0.08, 
                        linewidth=2, edgecolor='black', 
                        facecolor='lightblue', alpha=0.3)
        ax.add_patch(rect)
        
        ax.text(0.1, y_pos, info_text, 
               ha='left', va='top', fontsize=11, fontweight='bold',
               transform=ax.transAxes, family='monospace')
    
    # Footer
    ax.text(0.5, 0.02, 
           "All figures are PDFs in the 'figures/' directory.\n"
           "Open with: open figures/*.pdf",
           ha='center', va='bottom', fontsize=10, style='italic',
           transform=ax.transAxes)
    
    plt.tight_layout()
    output_path = Path("figures_overview.pdf")
    plt.savefig(output_path, format='pdf', bbox_inches='tight', dpi=300)
    print(f"✓ Created overview: {output_path}")
    
    # Also create as PNG for easier viewing
    output_path_png = Path("figures_overview.png")
    plt.savefig(output_path_png, format='png', bbox_inches='tight', dpi=150)
    print(f"✓ Created overview image: {output_path_png}")
    
    plt.close()
    
    # Try to open
    import subprocess
    try:
        subprocess.run(['open', str(output_path_png)], check=False)
    except:
        pass

if __name__ == "__main__":
    create_figure_overview()

