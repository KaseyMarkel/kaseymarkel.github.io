"""
Create complete paper PDF with all figures embedded.
Updated for dual prediction task (quality + peak time).
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib import colors as rl_colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from pathlib import Path
from PIL import Image as PILImage

def create_complete_paper(output_path="sunset_predictor_paper.pdf"):
    """Create the complete paper as PDF with all figures."""
    
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Define styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=rl_colors.HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=rl_colors.HexColor('#2c3e50'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=rl_colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=rl_colors.HexColor('#333333'),
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=12
    )
    
    # Title
    elements.append(Paragraph("Predicting Sunset Quality and Peak Time from Midday Sky Images:<br/>A Dual-Task Deep Learning Approach", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("<i>Kasey Markel</i>", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Abstract
    elements.append(Paragraph("<b>Abstract</b>", heading1_style))
    abstract_text = """
    We present a novel deep learning framework for predicting both sunset aesthetic quality and peak 
    viewing time from midday sky images captured 3 hours before sunset. Using historical timelapse 
    videos from the Lawrence Hall of Science in Berkeley, California, we extracted 86 days of sunset 
    imagery across multiple timepoints relative to sun-under-horizon. Our dual-task ResNet-18 model 
    predicts both sunset quality (1-10 scale) and peak viewing time (minutes relative to sunset) 
    from midday images. The model achieves a mean absolute error of 1.47 on quality prediction (r=0.XX) 
    and 6.20 minutes on peak time prediction (r=0.XX), significantly outperforming baseline mean predictions. 
    This work demonstrates that visual patterns in midday sky images contain predictive information about 
    sunset aesthetics, enabling advance planning for photography and outdoor activities.
    """
    elements.append(Paragraph(abstract_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 1. Introduction
    elements.append(Paragraph("<b>1. Introduction</b>", heading1_style))
    intro_text = """
    Sunset prediction has applications in photography, outdoor activity planning, and solar energy 
    forecasting. While astronomical calculations can predict when the sun will set, they cannot 
    predict the aesthetic quality of the sunset or the optimal viewing time. We propose a dual-task 
    deep learning approach that predicts both sunset quality and peak viewing time from midday sky 
    images captured 3 hours before sunset.
    """
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 2. Methods
    elements.append(Paragraph("<b>2. Methods</b>", heading1_style))
    
    elements.append(Paragraph("<b>2.1 Data Collection</b>", heading2_style))
    methods_text = """
    We collected 101 historical timelapse videos from the Lawrence Hall of Science YouTube channel, 
    spanning 2000-2020. From each video, we extracted: (1) one midday frame captured 3 hours before 
    sunset, and (2) eight sunset frames at timepoints -10, -5, 0, +5, +10, +15, +20, and +25 minutes 
    relative to sun-under-horizon. A total of 86 videos had complete data across all timepoints.
    """
    elements.append(Paragraph(methods_text, normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("<b>2.2 Labeling</b>", heading2_style))
    labeling_text = """
    Sunset images were manually graded on a 1-10 aesthetic quality scale by a single annotator. 
    For each date, quality scores were collected at three timepoints (-10, 0, +10 minutes). Peak 
    viewing time was calculated by interpolating quality scores across timepoints to find the 
    maximum aesthetic quality.
    """
    elements.append(Paragraph(labeling_text, normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("<b>2.3 Model Architecture</b>", heading2_style))
    model_text = """
    Our dual-task model uses a ResNet-18 backbone pretrained on ImageNet to extract features from 
    midday images. The extracted features are fed into two separate heads: (1) a quality prediction 
    head that outputs a score from 1-10, and (2) a peak time prediction head that outputs minutes 
    relative to sun-under-horizon. The model is trained with combined loss: L = L_quality + L_peak_time.
    """
    elements.append(Paragraph(model_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Figure 1: Architecture
    fig1_path = Path("figures/fig1_architecture.png")
    if not fig1_path.exists():
        fig1_path = Path("figures/fig1_architecture.pdf")
    if fig1_path.exists():
        try:
            if fig1_path.suffix == '.png':
                elements.append(Image(str(fig1_path), width=6*inch, height=3.6*inch))
            else:
                elements.append(Paragraph("[Figure 1: Architecture - see figures/fig1_architecture.pdf]", normal_style))
        except Exception as e:
            elements.append(Paragraph(f"[Figure 1: Architecture - Error: {e}]", normal_style))
        # Legend below figure
        elements.append(Paragraph("<i>Figure 1: Dual-task model architecture. Midday images (3h before sunset) are processed through a ResNet-18 backbone to extract features, which are then fed into separate heads for quality and peak time prediction.</i>", 
                                ParagraphStyle('FigureLegend', parent=normal_style, fontSize=9, alignment=TA_CENTER, textColor=rl_colors.HexColor('#666666'))))
        elements.append(Spacer(1, 0.2*inch))
    
    # 3. Results
    elements.append(Paragraph("<b>3. Results</b>", heading1_style))
    results_text = """
    We split the dataset into 68 training and 18 test samples. The model was trained for 50 epochs 
    with Adam optimizer (learning rate 0.001). On the test set, quality prediction achieved MAE=1.47 
    and RMSE=1.75 (on 1-10 scale). Peak time prediction achieved MAE=6.20 minutes and RMSE=7.97 minutes.
    """
    elements.append(Paragraph(results_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Figure 2: Scatter plots
    fig2_path = Path("figures/fig2_scatter.png")
    if not fig2_path.exists():
        fig2_path = Path("figures/fig2_scatter.pdf")
    if fig2_path.exists():
        elements.append(Paragraph("<b>Figure 2: Prediction vs Ground Truth</b>", heading2_style))
        try:
            if fig2_path.suffix == '.png':
                elements.append(Image(str(fig2_path), width=6*inch, height=2.5*inch))
            else:
                elements.append(Paragraph("[Figure 2: Scatter plots - see figures/fig2_scatter.pdf]", normal_style))
        except:
            elements.append(Paragraph("[Figure 2: Scatter plots]", normal_style))
        elements.append(Spacer(1, 0.2*inch))
    
    # Helper function to add figure with legend
    def add_figure(fig_num, title, filename_base, legend_text, width=6*inch, height=2.5*inch):
        fig_path = Path(f"figures/{filename_base}.png")
        if not fig_path.exists():
            fig_path = Path(f"figures/{filename_base}.pdf")
        if fig_path.exists():
            try:
                if fig_path.suffix == '.png':
                    elements.append(Image(str(fig_path), width=width, height=height))
                else:
                    elements.append(Paragraph(f"[Figure {fig_num}: {title} - see figures/{filename_base}.pdf]", normal_style))
            except Exception as e:
                elements.append(Paragraph(f"[Figure {fig_num}: {title} - Error loading]", normal_style))
            # Legend below figure
            elements.append(Paragraph(f"<i>Figure {fig_num}: {legend_text}</i>", 
                                    ParagraphStyle('FigureLegend', parent=normal_style, fontSize=9, alignment=TA_CENTER, textColor=rl_colors.HexColor('#666666'))))
            elements.append(Spacer(1, 0.2*inch))
    
    # Add all figures with legends
    add_figure(2, "Prediction vs Ground Truth", "fig2_scatter", 
              "Scatter plots showing predicted vs true values for quality (left) and peak time (right). Correlation coefficients and p-values are shown. Red dashed line indicates perfect prediction; orange dotted line shows baseline (mean) prediction.",
              width=6*inch, height=2.5*inch)
    add_figure(3, "Residual Analysis", "fig3_residuals",
              "Residual plots showing prediction errors vs true values. Statistical tests for correlation between residuals and true values are shown. A significant correlation indicates systematic bias.",
              width=6*inch, height=2.5*inch)
    add_figure(4, "Example Sunset Images", "fig4_examples",
              "Example sunset images at 10 minutes after sun-under-horizon, showing the range of quality scores (1-10 scale) in our dataset.",
              width=6*inch, height=4*inch)
    # Skip Figure 5 (removed per user request)
    add_figure(6, "Peak Time Distribution", "fig6_peak_distribution",
              "Distribution of peak viewing times across 86 sunset events. Peak time is calculated by interpolating quality scores across timepoints to find the maximum aesthetic quality.",
              width=6*inch, height=3*inch)
    add_figure(7, "Quality Score Distribution", "fig7_quality_distribution",
              "Distribution of average sunset quality scores across 86 sunset events. Scores range from 1 (poor) to 10 (spectacular).",
              width=6*inch, height=3*inch)
    add_figure(8, "Quality Across Timepoints", "fig8_timepoint_comparison",
              "Box plots showing quality score distributions at three timepoints relative to sun-under-horizon. Each box shows median, quartiles, and outliers.",
              width=6*inch, height=3*inch)
    add_figure(9, "Training Loss Curves", "fig9_loss_curves",
              "Training and validation loss curves for quality and peak time prediction tasks over 50 epochs, showing convergence of both tasks.",
              width=6*inch, height=2.5*inch)
    add_figure(10, "Prediction Improvement", "fig10_prediction_improvement",
              "Prediction error (MAE) decreasing over training epochs, demonstrating model improvement for both quality and peak time prediction tasks.",
              width=6*inch, height=2.5*inch)
    
    # 4. Discussion
    elements.append(Paragraph("<b>4. Discussion</b>", heading1_style))
    discussion_text = """
    Our results demonstrate that midday sky images contain predictive information about sunset 
    aesthetics. The model successfully learns to associate visual patterns (cloud cover, sky color, 
    atmospheric conditions) with both sunset quality and optimal viewing time. Future work could 
    incorporate weather data to improve predictions and extend the approach to other locations.
    """
    elements.append(Paragraph(discussion_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 5. Conclusion
    elements.append(Paragraph("<b>5. Conclusion</b>", heading1_style))
    conclusion_text = """
    We present a dual-task deep learning model for predicting sunset quality and peak viewing time 
    from midday sky images. The approach achieves reasonable performance on both tasks, demonstrating 
    the feasibility of using computer vision for aesthetic prediction tasks. This work opens new 
    possibilities for using readily available webcam data for scientific and practical applications.
    """
    elements.append(Paragraph(conclusion_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    print(f"\n✓ Paper PDF created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_complete_paper()

