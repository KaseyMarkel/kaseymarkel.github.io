"""
Create Figure 1: Model Architecture Diagram
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

# Set style
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def create_architecture_diagram(output_path="figures/fig1_architecture.pdf"):
    """Create model architecture diagram."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Colors
    input_color = '#E8F4F8'
    conv_color = '#B3D9E6'
    fc_color = '#FFE6CC'
    output_color = '#FFCC99'
    
    # Input
    input_box = FancyBboxPatch((0.5, 2.5), 1.2, 1, 
                               boxstyle="round,pad=0.1", 
                               facecolor=input_color, 
                               edgecolor='black', linewidth=2)
    ax.add_patch(input_box)
    ax.text(1.1, 3, 'Input Image\n224×224×3', 
           ha='center', va='center', fontweight='bold', fontsize=11)
    
    # Arrow 1
    arrow1 = FancyArrowPatch((1.7, 3), (2.3, 3), 
                            arrowstyle='->', lw=2.5, color='black')
    ax.add_patch(arrow1)
    
    # ResNet Backbone
    resnet_box = FancyBboxPatch((2.5, 1.5), 2.5, 2, 
                               boxstyle="round,pad=0.15", 
                               facecolor=conv_color, 
                               edgecolor='black', linewidth=2)
    ax.add_patch(resnet_box)
    
    # ResNet layers
    ax.text(3.75, 3.2, 'ResNet-18 Backbone', 
           ha='center', va='center', fontweight='bold', fontsize=12)
    
    # Show some layers
    layer_y = 2.8
    layers = ['Conv1', 'Layer1', 'Layer2', 'Layer3', 'Layer4']
    for i, layer in enumerate(layers):
        ax.text(3.75, layer_y - i*0.25, f'  {layer}', 
               ha='center', va='center', fontsize=9, 
               family='monospace')
    
    # Arrow 2
    arrow2 = FancyArrowPatch((5, 3), (5.6, 3), 
                            arrowstyle='->', lw=2.5, color='black')
    ax.add_patch(arrow2)
    
    # Feature extraction
    feat_box = FancyBboxPatch((5.8, 2.5), 1.2, 1, 
                             boxstyle="round,pad=0.1", 
                             facecolor=conv_color, 
                             edgecolor='black', linewidth=2)
    ax.add_patch(feat_box)
    ax.text(6.4, 3, 'Feature\nExtraction\n512-dim', 
           ha='center', va='center', fontweight='bold', fontsize=10)
    
    # Arrow 3
    arrow3 = FancyArrowPatch((7, 3), (7.4, 3), 
                            arrowstyle='->', lw=2.5, color='black')
    ax.add_patch(arrow3)
    
    # Regression Head
    reg_head = FancyBboxPatch((7.6, 1), 1.8, 4, 
                             boxstyle="round,pad=0.15", 
                             facecolor=fc_color, 
                             edgecolor='black', linewidth=2)
    ax.add_patch(reg_head)
    ax.text(8.5, 4.5, 'Regression Head', 
           ha='center', va='center', fontweight='bold', fontsize=12)
    
    # FC layers
    fc_layers = [
        ('FC: 512→256', 3.8),
        ('ReLU + Dropout', 3.5),
        ('FC: 256→128', 3.2),
        ('ReLU + Dropout', 2.9),
        ('FC: 128→1', 2.6)
    ]
    
    for text, y_pos in fc_layers:
        ax.text(8.5, y_pos, text, ha='center', va='center', 
               fontsize=9, family='monospace')
    
    # Arrow 4
    arrow4 = FancyArrowPatch((9.4, 3), (9.7, 3), 
                            arrowstyle='->', lw=2.5, color='black')
    ax.add_patch(arrow4)
    
    # Output
    output_box = FancyBboxPatch((9.8, 2.8), 0.4, 0.4, 
                               boxstyle="round,pad=0.05", 
                               facecolor=output_color, 
                               edgecolor='black', linewidth=2)
    ax.add_patch(output_box)
    ax.text(10, 3, 'Hours\nUntil\nSunset', 
           ha='center', va='center', fontweight='bold', fontsize=9)
    
    # Title
    ax.text(5, 5.5, 'Sunset Prediction Model Architecture', 
           ha='center', va='center', fontweight='bold', fontsize=16)
    
    # Add annotations
    ax.text(3.75, 0.8, 'ImageNet\nPretrained', 
           ha='center', va='center', fontsize=9, 
           style='italic', color='gray')
    
    ax.text(8.5, 0.5, 'Trainable', 
           ha='center', va='center', fontsize=9, 
           style='italic', color='gray')
    
    plt.tight_layout()
    from pathlib import Path
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    print(f"✓ Saved: {output_path}")
    plt.close()


if __name__ == "__main__":
    create_architecture_diagram()

