# Figure Creation Checklist for NeurIPS Paper

## Required Figures

### Figure 1: Model Architecture
**Type:** Diagram  
**Tool:** Draw.io, TikZ, or similar  
**Content:**
- Input image (224×224×3)
- ResNet-18 backbone (show key layers)
- Feature extraction (512-dim)
- Regression head (FC layers)
- Output (hours until sunset)
- Arrows showing data flow

**Status:** [ ] To create

---

### Figure 2: Prediction vs. Ground Truth Scatter Plot
**Type:** Scatter plot  
**Tool:** Matplotlib/Seaborn  
**Script:** `create_figure2_scatter.py`
```python
# X: true hours until sunset
# Y: predicted hours until sunset
# Diagonal line: perfect prediction
# Color: by season or error magnitude
```

**Status:** [ ] To create

---

### Figure 3: Residual Plot
**Type:** Scatter plot  
**Tool:** Matplotlib  
**Script:** `create_figure3_residuals.py`
```python
# X: true hours until sunset
# Y: prediction error (predicted - true)
# Horizontal line at y=0
# Show systematic bias if any
```

**Status:** [ ] To create

---

### Figure 4: Error Distribution Histogram
**Type:** Histogram  
**Tool:** Matplotlib  
**Script:** `create_figure4_histogram.py`
```python
# Distribution of prediction errors
# Overlay normal distribution
# Annotate mean, std dev
# Show percentiles
```

**Status:** [ ] To create

---

### Figure 5: Example Predictions
**Type:** Image grid (5 panels)  
**Tool:** Matplotlib  
**Script:** `create_figure5_examples.py`
**Content per panel:**
- Original sky image
- Text overlay:
  - Capture time
  - True hours until sunset
  - Predicted hours until sunset
  - Error (minutes)
- Include both good and moderate predictions

**Status:** [ ] To create

---

### Figure 6: Failure Cases
**Type:** Image grid (3-5 panels)  
**Tool:** Matplotlib  
**Script:** `create_figure6_failures.py`
**Content:**
- Examples with largest errors
- Analysis text explaining failures
- Common failure patterns

**Status:** [ ] To create

---

### Figure 7: Temporal Performance
**Type:** Line plot  
**Tool:** Matplotlib  
**Script:** `create_figure7_temporal.py`
```python
# X: Date (full year)
# Y: MAE (hours)
# Show seasonal trends
# Annotate weather events
# Smoothing curve overlay
```

**Status:** [ ] To create

---

### Figure 8: Model Comparison
**Type:** Bar chart  
**Tool:** Matplotlib/Seaborn  
**Script:** `create_figure8_comparison.py`
```python
# Models on X-axis
# MAE, RMSE, R² as grouped bars
# Error bars showing std dev
# Color coding
```

**Status:** [ ] To create

---

### Figure 9: Activation Maps (Grad-CAM)
**Type:** Heatmap overlays  
**Tool:** PyTorch Grad-CAM library  
**Script:** `create_figure9_activations.py`
**Content:**
- Original images
- Grad-CAM heatmaps showing important regions
- Multiple examples at different times before sunset
- Interpretation text

**Status:** [ ] To create

---

## Figure Creation Scripts

Create these Python scripts to generate figures:

1. `create_figure2_scatter.py` - Scatter plot
2. `create_figure3_residuals.py` - Residual plot  
3. `create_figure4_histogram.py` - Error histogram
4. `create_figure5_examples.py` - Example predictions
5. `create_figure6_failures.py` - Failure cases
6. `create_figure7_temporal.py` - Temporal analysis
7. `create_figure8_comparison.py` - Model comparison
8. `create_figure9_activations.py` - Grad-CAM visualizations

## Table Creation

Tables can be created from evaluation results:

1. **Table 1:** Dataset statistics (from metadata)
2. **Table 2:** Ablation study (from training logs)
3. **Table 3:** Model comparison (from evaluation)
4. **Table 4:** Seasonal performance (from evaluation by date)

Use pandas to create tables, export to LaTeX format for paper.

