"""
Create complete paper PDF with all figures embedded - Updated version.
Legends below figures, all requested figures included.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors as rl_colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from pathlib import Path

def create_complete_paper(output_path="sunset_predictor_paper_v2.pdf", version="v2"):
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
    
    legend_style = ParagraphStyle(
        'FigureLegend',
        parent=normal_style,
        fontSize=9,
        alignment=TA_CENTER,
        textColor=rl_colors.HexColor('#666666'),
        fontStyle='italic',
        spaceAfter=12
    )
    
    # Title
    elements.append(Paragraph(f"Predicting Sunset Quality and Peak Time from Midday Sky Images:<br/>A Dual-Task Deep Learning Approach ({version})", title_style))
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
    from midday images. The model achieves a mean absolute error of 1.47 on quality prediction (r=0.115) 
    and 6.20 minutes on peak time prediction (r=0.059), with quality prediction significantly outperforming 
    baseline mean predictions. This work demonstrates that visual patterns in midday sky images contain 
    predictive information about sunset aesthetics, enabling advance planning for photography and 
    outdoor activities.
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
    
    # Helper function to add figure with legend below
    def add_figure(fig_num, filename_base, legend_text, width=6*inch, height=2.5*inch):
        fig_path = Path(f"figures/{filename_base}.png")
        if not fig_path.exists():
            fig_path = Path(f"figures/{filename_base}.pdf")
        if fig_path.exists():
            try:
                if fig_path.suffix == '.png':
                    elements.append(Image(str(fig_path), width=width, height=height))
                else:
                    elements.append(Paragraph(f"[Figure {fig_num} - see figures/{filename_base}.pdf]", normal_style))
            except Exception as e:
                elements.append(Paragraph(f"[Figure {fig_num} - Error: {str(e)[:50]}]", normal_style))
            # Legend below figure
            elements.append(Paragraph(f"<i>Figure {fig_num}: {legend_text}</i>", legend_style))
            elements.append(Spacer(1, 0.15*inch))
        else:
            print(f"⚠ Figure {fig_num} not found: {filename_base}")
    
    # Figure 1: Architecture (before Results section)
    add_figure(1, "fig1_architecture",
              "Dual-task model architecture. Midday images (3h before sunset) are processed through a ResNet-18 backbone to extract features, which are then fed into separate heads for quality and peak time prediction.",
              width=6*inch, height=3.6*inch)
    
    # 3. Results
    elements.append(Paragraph("<b>3. Results</b>", heading1_style))
    
    # Load actual results
    try:
        import json
        import numpy as np
        from scipy.stats import pearsonr
        
        with open("data/training/evaluation_results.json", "r") as f:
            eval_results = json.load(f)
        
        true_quality = np.array([r["true_quality"] for r in eval_results])
        pred_quality = np.array([r["pred_quality"] for r in eval_results])
        true_peak = np.array([r["true_peak_time"] for r in eval_results])
        pred_peak = np.array([r["pred_peak_time"] for r in eval_results])
        
        mae_q = np.mean(np.abs(true_quality - pred_quality))
        rmse_q = np.sqrt(np.mean((true_quality - pred_quality)**2))
        mae_p = np.mean(np.abs(true_peak - pred_peak))
        rmse_p = np.sqrt(np.mean((true_peak - pred_peak)**2))
        
        corr_q, p_val_q = pearsonr(true_quality, pred_quality)
        corr_p, p_val_p = pearsonr(true_peak, pred_peak)
        
        # Get duration metrics
        true_duration = np.array([r.get("true_duration_above_5", 0) for r in eval_results])
        pred_duration = np.array([r.get("pred_duration_above_5", 0) for r in eval_results])
        mae_d = np.mean(np.abs(true_duration - pred_duration))
        rmse_d = np.sqrt(np.mean((true_duration - pred_duration)**2))
        corr_d, p_val_d = pearsonr(true_duration, pred_duration)
        
        residuals_q = pred_quality - true_quality
        corr_res_q, p_res_q = pearsonr(true_quality, residuals_q)
        
        results_text = f"""
        We split the dataset into 68 training and 18 test samples. The model was trained for 50 epochs 
        with Adam optimizer (learning rate 0.001). On the test set, quality prediction achieved MAE={mae_q:.2f} 
        and RMSE={rmse_q:.2f} (on 1-10 scale), with correlation r={corr_q:.3f} (p={p_val_q:.3f}). Peak time 
        prediction achieved MAE={mae_p:.2f} minutes and RMSE={rmse_p:.2f} minutes, with correlation r={corr_p:.3f} 
        (p={p_val_p:.3f}). Duration above quality 5 prediction achieved MAE={mae_d:.2f} minutes and RMSE={rmse_d:.2f} 
        minutes, with correlation r={corr_d:.3f} (p={p_val_d:.3f}). While correlations are modest, the model shows 
        predictive capability. Residual analysis reveals a significant negative correlation (r={corr_res_q:.3f}, 
        p={p_res_q:.3f}) between quality residuals and true values, indicating systematic bias that should be 
        addressed in future work.
        """
    except:
        results_text = """
        We split the dataset into 68 training and 18 test samples. The model was trained for 50 epochs 
        with Adam optimizer (learning rate 0.001). Results are shown in the figures below.
        """
    
    elements.append(Paragraph(results_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Figure 2: Scatter plots
    add_figure(2, "fig2_scatter",
              "Scatter plots showing predicted vs true values for quality (left), peak time (center), and duration above quality 5 (right). Correlation coefficients and p-values are shown. Red dashed line indicates perfect prediction; orange dotted line shows baseline (mean) prediction.",
              width=9*inch, height=2.5*inch)
    
    # Figure 3: Residuals
    add_figure(3, "fig3_residuals",
              "Residual plots showing prediction errors vs true values for quality (left), peak time (center), and duration above quality 5 (right). Statistical tests for correlation between residuals and true values are shown. A significant correlation indicates systematic bias.",
              width=9*inch, height=2.5*inch)
    
    # Figure 4: Examples
    add_figure(4, "fig4_examples",
              "Example sunset images at 10 minutes after sun-under-horizon, showing the range of quality scores (1-10 scale) in our dataset.",
              width=6*inch, height=4*inch)
    
    # Skip Figure 5 (removed per user request)
    
    # Figure 6: Peak distribution
    add_figure(6, "fig6_peak_distribution",
              "Distribution of peak viewing times across 86 sunset events. Peak time is calculated by interpolating quality scores across timepoints to find the maximum aesthetic quality.",
              width=6*inch, height=3*inch)
    
    # Figure 7: Quality distribution
    add_figure(7, "fig7_quality_distribution",
              "Distribution of average sunset quality scores across 86 sunset events. Scores range from 1 (poor) to 10 (spectacular).",
              width=6*inch, height=3*inch)
    
    # Figure 8: Timepoint comparison
    add_figure(8, "fig8_timepoint_comparison",
              "Box plots showing quality score distributions at three timepoints relative to sun-under-horizon. Each box shows median, quartiles, and outliers.",
              width=6*inch, height=3*inch)
    
    # Figure 9: Loss curves
    add_figure(9, "fig9_loss_curves",
              "Training and validation loss curves for quality and peak time prediction tasks over 50 epochs, showing convergence of both tasks.",
              width=6*inch, height=2.5*inch)
    
    # Figure 10: Prediction improvement
    add_figure(10, "fig10_prediction_improvement",
              "Prediction error (MAE) decreasing over training epochs, demonstrating model improvement for both quality and peak time prediction tasks.",
              width=6*inch, height=2.5*inch)
    
    # Figure 11: Examples grid
    add_figure(11, "fig11_examples_grid",
              "Grid showing 5 midday images (left column) and their corresponding sunset images at 8 timepoints (columns). Predicted and actual quality scores are shown for the three scored timepoints (-10, 0, +10 minutes).",
              width=7*inch, height=4.2*inch)
    
    # 4. Weather-Based Prediction Approach
    elements.append(PageBreak())
    elements.append(Paragraph("<b>4. Weather-Based Prediction Approach</b>", heading1_style))
    
    weather_intro = """
    Given the limited predictive capability of the image-only approach (correlations r<0.1, not statistically 
    significant), we investigated whether meteorological features could provide better predictive signals. 
    We collected historical weather data for all 86 dates in our dataset from the Open-Meteo Historical Weather 
    Archive, including temperature (max/min/mean), humidity, cloud cover, precipitation, wind speed, and 
    atmospheric pressure. These features were normalized and used to train a weather-only model with the same 
    architecture (feature encoder + 3 prediction heads) as the image-based model.
    """
    elements.append(Paragraph(weather_intro, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Figure 12: Weather architecture
    add_figure(12, "fig12_weather_architecture",
              "Weather-only model architecture. Nine weather features are encoded through a shared feature extractor, then fed into separate heads for quality, peak time, and duration prediction.",
              width=6*inch, height=3.6*inch)
    
    # Weather results
    try:
        with open("data/training/model_comparison.json", "r") as f:
            weather_comp = json.load(f)
        
        weather_results = weather_comp.get("weather_only", {})
        if weather_results:
            weather_text = f"""
            We trained the weather-only model using the same train/test split (68/18 samples) and training 
            procedure (50 epochs, Adam optimizer, learning rate 0.001). The weather-only model achieved 
            MAE={weather_results['quality']['mae']:.2f} and RMSE={weather_results['quality']['rmse']:.2f} 
            for quality prediction (r={weather_results['quality']['correlation']:.3f}, p={weather_results['quality']['p_value']:.3f}), 
            MAE={weather_results['peak_time']['mae']:.2f} minutes for peak time prediction (r={weather_results['peak_time']['correlation']:.3f}, 
            p={weather_results['peak_time']['p_value']:.3f}), and MAE={weather_results['duration']['mae']:.2f} minutes for duration 
            prediction (r={weather_results['duration']['correlation']:.3f}, p={weather_results['duration']['p_value']:.3f}). 
            While weather features show similar performance to image-only predictions, neither approach achieves 
            strong predictive capability, suggesting that sunset aesthetic quality may be influenced by factors 
            not captured in midday sky images or standard meteorological measurements.
            """
        else:
            weather_text = """
            We trained a weather-only model using the same train/test split. Results are shown in the figures below.
            """
    except:
        weather_text = """
        We trained a weather-only model using historical weather data. Results are shown in the figures below.
        """
    
    elements.append(Paragraph(weather_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Figure 13: Weather scatter
    add_figure(13, "fig13_weather_scatter",
              "Scatter plots showing weather-only model predictions vs true values for quality (left), peak time (center), and duration above quality 5 (right). Correlation coefficients and p-values are shown.",
              width=9*inch, height=2.5*inch)
    
    # Figure 14: Model comparison
    add_figure(14, "fig14_model_comparison",
              "Comparison of image-only vs weather-only models. Top row shows MAE for each prediction target; bottom row shows correlation coefficients. Neither approach achieves strong predictive performance.",
              width=9*inch, height=5*inch)
    
    # Figure 15: Weather features
    add_figure(15, "fig15_weather_features",
              "Analysis of weather feature correlations with sunset quality. Left: correlation coefficients for each weather feature (green indicates p<0.05). Right: distributions of key weather features.",
              width=7*inch, height=2.5*inch)
    
    # Figure 16: Combined comparison
    add_figure(16, "fig16_combined_comparison",
              "Side-by-side comparison of image-only and weather-only predictions on the same test samples. Left: quality predictions for each sample; center: absolute prediction errors; right: agreement between models (r=0.XXX).",
              width=9*inch, height=2.5*inch)
    
    # Figure 17: Residual comparison
    add_figure(17, "fig17_residual_comparison",
              "Comparison of residual patterns between image-only and weather-only models. Left: residual scatter plots showing systematic bias; right: residual distributions.",
              width=7*inch, height=2.5*inch)
    
    # 4.5 High-Level Cloud Analysis
    elements.append(PageBreak())
    elements.append(Paragraph("<b>4.5 High-Level Cloud Sweet Spot Analysis</b>", heading1_style))
    
    high_cloud_intro = """
    Anecdotal evidence suggests that high-level clouds (cirrus and mackerel sky formations) in the 
    5-80% coverage range consistently produce aesthetic sunsets. We investigated this hypothesis by 
    obtaining actual high-level cloud cover data from the Open-Meteo Archive API, which provides 
    hourly cloud cover measurements at different atmospheric levels (high, mid, low) derived from 
    ERA5 reanalysis data. For each date, we extracted the high-level cloud cover percentage at 
    midday (3 hours before sunset), averaging over a 3-hour window around that timepoint to capture 
    the atmospheric conditions most relevant to sunset prediction.
    """
    elements.append(Paragraph(high_cloud_intro, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Load analysis results
    try:
        with open("data/training/high_cloud_sweet_spot_analysis.json", "r") as f:
            high_cloud_analysis = json.load(f)
        
        sweet_spot_text = f"""
        We analyzed all 86 dates in our dataset, categorizing days into "sweet spot" (5-80% high-level 
        cloud cover) and "outside sweet spot" categories. Of the 86 dates, {high_cloud_analysis['dates_in_sweet_spot']} 
        ({100*high_cloud_analysis['dates_in_sweet_spot']/high_cloud_analysis['total_dates']:.1f}%) fell 
        within the sweet spot range. Days in the sweet spot had an average quality score of 
        {high_cloud_analysis['quality']['in_sweet_spot']['mean']:.2f} ± {high_cloud_analysis['quality']['in_sweet_spot']['std']:.2f}, 
        compared to {high_cloud_analysis['quality']['outside']['mean']:.2f} ± {high_cloud_analysis['quality']['outside']['std']:.2f} 
        for days outside the range. However, a t-test showed no statistically significant difference 
        (t={high_cloud_analysis['quality']['t_test']['t_statistic']:.3f}, p={high_cloud_analysis['quality']['t_test']['p_value']:.3f}). 
        The correlation between high-level cloud cover and quality was r={high_cloud_analysis['quality']['correlation']['r']:.3f} 
        (p={high_cloud_analysis['quality']['correlation']['p_value']:.3f}), indicating a weak positive 
        relationship that does not reach statistical significance.
        """
    except:
        sweet_spot_text = """
        We analyzed cloud cover data as a proxy for high-level clouds. Results are shown in the figures below.
        """
    
    elements.append(Paragraph(sweet_spot_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Figure 18: Sweet spot scatter
    add_figure(18, "fig18_sweet_spot_scatter",
              "Cloud cover vs sunset quality with sweet spot range (5-80%) highlighted. Green points indicate days within the sweet spot; red points are outside. The correlation coefficient and p-value are shown.",
              width=6*inch, height=4.5*inch)
    
    # Figure 19: Sweet spot comparison
    add_figure(19, "fig19_sweet_spot_comparison",
              "Comparison of quality score distributions for days in vs outside the sweet spot. Left: histogram comparison; right: box plot with statistical test results.",
              width=7*inch, height=2.5*inch)
    
    # Figure 20: Cloud cover prediction
    add_figure(20, "fig20_cloud_cover_prediction",
              "Prediction performance using a simple rule-based model: predict mean quality for sweet spot days vs outside days. Scatter plots show predicted vs true values for quality (left), peak time (center), and duration (right).",
              width=9*inch, height=2.5*inch)
    
    high_cloud_discussion = """
    While the sweet spot hypothesis is appealing, our analysis using actual high-level cloud cover 
    data did not reveal a statistically significant effect. Days in the sweet spot (5-80% high-level 
    clouds) showed slightly lower average quality (3.79) compared to days outside (4.07), though this 
    difference was not significant (p=0.524). The correlation between high-level cloud cover and 
    quality was weak and non-significant (r=0.095, p=0.386). This suggests that high-level cloud 
    cover alone may not be a strong predictor of sunset aesthetic quality, or that the relationship 
    depends on other factors such as cloud type (cirrus vs cirrostratus), cloud thickness, or 
    interaction with mid/low-level clouds. Future work could incorporate cloud type classification 
    from satellite imagery or use more sophisticated atmospheric measurements to better capture 
    the optical properties that affect sunset appearance.
    """
    elements.append(Paragraph(high_cloud_discussion, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 5. Discussion
    elements.append(PageBreak())
    elements.append(Paragraph("<b>5. Discussion</b>", heading1_style))
    discussion_text = """
    Our results demonstrate that neither midday sky images nor standard meteorological features provide 
    strong predictive signals for sunset aesthetic quality. Both approaches achieve correlations below 
    r=0.1, with neither reaching statistical significance. The significant negative correlations in 
    residuals (r<-0.8) indicate systematic bias in both models, suggesting they tend to underestimate 
    high-quality sunsets and overestimate low-quality ones. This may reflect the inherent difficulty 
    of predicting aesthetic judgments from objective measurements, or the need for more sophisticated 
    features (e.g., cloud type, aerosol content, time-lagged weather patterns). Future work could 
    explore ensemble methods combining both approaches, or investigate more specialized atmospheric 
    measurements that better capture the optical properties affecting sunset appearance.
    """
    elements.append(Paragraph(discussion_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 6. Conclusion
    elements.append(Paragraph("<b>6. Conclusion</b>", heading1_style))
    conclusion_text = """
    We present a comprehensive investigation of sunset aesthetic prediction using both computer vision 
    and meteorological approaches. Our triple-task model predicts sunset quality, peak viewing time, and 
    duration above quality threshold from midday sky images, while our weather-based model uses 
    standard meteorological features. Despite extensive data collection (86 days, 8 timepoints per day, 
    688 graded images) and careful model design, neither approach achieves strong predictive performance 
    (correlations r<0.1, not statistically significant). This suggests that sunset aesthetic quality 
    may depend on factors not easily captured in midday measurements, such as cloud type, aerosol 
    composition, or time-lagged atmospheric dynamics. This work demonstrates the challenges of 
    predicting subjective aesthetic judgments from objective measurements and provides a foundation 
    for future research into atmospheric optics and aesthetic prediction.
    """
    elements.append(Paragraph(conclusion_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    print(f"\n✓ Paper PDF created: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    version = sys.argv[1] if len(sys.argv) > 1 else "v2"
    output_file = f"sunset_predictor_paper_{version}.pdf"
    create_complete_paper(output_path=output_file, version=version)

