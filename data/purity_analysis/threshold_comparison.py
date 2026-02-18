#!/usr/bin/env python3
"""
Part 4: Threshold Sensitivity Analysis — Reconciling Our Automated
Analysis with Enrique's Manual Classification
==================================================================

The key disagreements between our Part 1 automated analysis and Enrique's
verdicts stem from three methodological differences:

1. CONCORDANCE BASELINE: We compute concordance against a pooled group
   consensus (all CLWQHZN47 lots together), but some lots are genuinely
   different sub-lines (e.g., F6695 has ~0.3% het = very pure, but 78%
   concordance because it's a different sub-line). Enrique evaluates each
   lot's internal uniformity, not cross-lot concordance.

2. INBRED HET THRESHOLD: We fail inbreds above 10% het. Enrique accepts
   Hembra F7 (~14% het) as expected residual heterozygosity for this
   partially-fixed line. He only flags the 1/10 outcross sample (32% het).

3. HYBRID CLASSIFICATION: For hybrid samples, Enrique uses IBS genetic
   distance (dist_prom_F5, dist_prom_hembra) rather than heterozygosity
   rate. Selfed seeds are detected by proximity to the female parent.

This script re-runs the classification with Enrique-aligned thresholds
and identifies which disagreements are threshold-driven (reconcilable)
vs. fundamental (suggesting a potential error in one analysis).

Usage:
    python3 threshold_comparison.py
"""

import sys
import os
import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.dpi": 150,
})

OUTDIR = os.path.dirname(os.path.abspath(__file__))


# ── Data Loading ──────────────────────────────────────────────────────────────
def load_all_data():
    """Load all data sources needed for the comparison."""
    # Our per-sample results
    our_csv = os.path.join(OUTDIR, "purity_summary.csv")
    ours = pd.read_csv(our_csv)

    # Enrique's accession-level verdicts
    enr_candidates = [
        os.path.expanduser("~/Downloads/Genotype and seed sources - commercial hybrid seed and parent seed - 18-02-2025.xlsx - Genotype and seed sources.csv"),
    ]
    enr_path = next((c for c in enr_candidates if os.path.exists(c)), None)
    if enr_path is None:
        print("ERROR: Cannot find Enrique's CSV. Provide path as argument.")
        sys.exit(1)
    enr = pd.read_csv(enr_path)

    # EK's per-sample hybrid data (with distance metrics)
    ek_candidates = [
        os.path.expanduser("~/Downloads/260128_ZMS25508_B04_GT_EK_F5 purity_12_02_2026.xlsx"),
    ]
    ek_path = next((c for c in ek_candidates if os.path.exists(c)), None)
    ek = None
    if ek_path:
        ek = pd.read_excel(ek_path, sheet_name="Pureza de F5")

    return ours, enr, ek


def parse_enrique_verdict(verdict_str):
    """Parse Enrique's free-text verdict."""
    if pd.isna(verdict_str):
        return {"enr_status": "Unknown", "enr_impurity_pct": np.nan}
    v = str(verdict_str).strip()
    if "No aceptable" in v or "No es el genotipo" in v:
        pct_match = re.search(r'(\d+)\s*%', v)
        return {"enr_status": "Not acceptable", "enr_impurity_pct": float(pct_match.group(1)) if pct_match else np.nan}
    if "Aceptable" in v or "aceptable" in v:
        pct_match = re.search(r'(\d+)\s*%', v)
        pct = float(pct_match.group(1)) if pct_match else 0.0
        if pct > 0:
            return {"enr_status": "Acceptable with notes", "enr_impurity_pct": pct}
        return {"enr_status": "Acceptable", "enr_impurity_pct": 0.0}
    pct_match = re.search(r'(\d+)\s*%', v)
    if pct_match:
        return {"enr_status": "Impure (hybrid lot)", "enr_impurity_pct": float(pct_match.group(1))}
    return {"enr_status": "Unknown", "enr_impurity_pct": np.nan}


# ── Reclassification with Enrique-Aligned Thresholds ─────────────────────────

# Original thresholds (from Part 1)
ORIG = {
    "inbred_het_fail": 0.10,
    "inbred_het_warn": 0.05,
    "hybrid_het_min_warn": 0.15,
    "hybrid_het_min_fail": 0.20,
    "concordance_fail": 0.80,
    "concordance_warn": 0.90,
}

# Enrique-aligned thresholds (reverse-engineered from his data)
ENRIQUE = {
    # Hembra F7 at ~14% het is "Acceptable" → raise inbred het threshold
    # Selfed hybrid at 26.5% het is flagged → the hybrid lower bound is similar
    "inbred_het_fail": 0.20,      # was 0.10; Enrique accepts 14-17% for partially-fixed lines
    "inbred_het_warn": 0.15,      # was 0.05; Enrique notes residual het up to ~17% as OK
    # Hybrid thresholds stay similar — Enrique's selfed samples top out at 26.5% het
    "hybrid_het_min_warn": 0.15,  # same
    "hybrid_het_min_fail": 0.20,  # same
    # Concordance: Enrique evaluates within-lot, not cross-lot.
    # F6695 at 78% concordance is "Acceptable" because it's internally uniform.
    # We use within-lot concordance instead of pooled group concordance.
    "concordance_fail": 0.80,     # same numeric value, but computed differently
    "concordance_warn": 0.90,     # same
    "use_lot_concordance": True,  # KEY CHANGE: evaluate within production lot
}


def compute_within_lot_uniformity(ours):
    """
    For each sample, compute how uniform its lot is.

    The key insight: CLWQHZN47 F6695 has low GROUP concordance (78%) because it's
    a different sub-line, but it's internally uniform (all 5 samples are nearly
    identical). Enrique evaluates within-lot uniformity, not cross-lot concordance.

    We approximate this by checking:
    1. het_std within the lot (lower = more uniform)
    2. Whether the lot's samples are tightly clustered
    3. If a lot is uniform with low het, it's "pure but different" — not impure

    Returns the dataframe with lot_uniform (bool) and lot_het_std columns.
    """
    df = ours.copy()
    df["lot"] = df["sample"].str.extract(r'^(F\d+)')

    # Compute within-lot statistics
    lot_stats = df.groupby("lot").agg(
        lot_het_std=("het_rate", "std"),
        lot_het_median=("het_rate", "median"),
        lot_het_range=("het_rate", lambda x: x.max() - x.min()),
        lot_n=("sample", "count"),
    )

    df = df.merge(lot_stats, on="lot", how="left")

    # A lot is "internally uniform" if het_std < 0.03 and het_range < 0.10
    # (all samples look alike, even if they differ from the group consensus)
    df["lot_uniform"] = (df["lot_het_std"] < 0.03) & (df["lot_het_range"] < 0.10)

    return df


def classify_sample_enrique_aligned(row, thresholds):
    """Classify a single sample using Enrique-aligned thresholds.

    Key differences from original:
    1. Higher inbred het thresholds (accepts partially-fixed lines)
    2. Lot-uniform override: if a lot is internally uniform with low het,
       low GROUP concordance is OK (it's a different sub-line, not impure)
    3. NaN het/concordance (genotyping failure) still counts as FAIL
    """
    het = row["het_rate"]
    conc = row["concordance"]
    is_hybrid = row["is_hybrid"]
    fail_rate = row.get("fail_rate", 0)
    lot_uniform = row.get("lot_uniform", False)
    lot_het_median = row.get("lot_het_median", np.nan)

    # If het is NaN, the sample failed genotyping entirely
    if pd.isna(het):
        return "FAIL", "genotyping failure (no het data)"

    reasons = []

    if is_hybrid:
        if het < thresholds["hybrid_het_min_fail"]:
            reasons.append(f"selfed: het={het:.1%}")
        elif het < thresholds["hybrid_het_min_warn"]:
            reasons.append(f"low het for hybrid: {het:.1%}")
    else:
        if het > thresholds["inbred_het_fail"]:
            reasons.append(f"high het for inbred: {het:.1%}")
        elif het > thresholds["inbred_het_warn"]:
            reasons.append(f"elevated het for inbred: {het:.1%}")

    # Concordance check with lot-uniformity override
    if pd.notna(conc):
        if conc < thresholds["concordance_fail"]:
            if lot_uniform and pd.notna(lot_het_median) and lot_het_median < 0.05:
                # Lot is internally uniform with low het — different sub-line, not impure
                pass  # Override: don't flag concordance
            else:
                reasons.append(f"low concordance: {conc:.1%}")
        elif conc < thresholds["concordance_warn"]:
            if not (lot_uniform and pd.notna(lot_het_median) and lot_het_median < 0.05):
                reasons.append(f"reduced concordance: {conc:.1%}")

    if fail_rate > 0.20:
        reasons.append(f"high fail rate: {fail_rate:.1%}")

    if not reasons:
        return "PASS", "OK"

    # Determine severity
    has_fail = any("low concordance" in r or "selfed" in r or
                   ("high het" in r and "inbred" in r) or "high fail" in r or
                   "genotyping" in r
                   for r in reasons)
    status = "FAIL" if has_fail else "WARNING"
    return status, "; ".join(reasons)


# ── Figures ───────────────────────────────────────────────────────────────────

def fig_th1_threshold_impact(ours_orig, ours_enrique, merged, outdir):
    """
    Side-by-side comparison: how do results change with Enrique-aligned thresholds?
    """
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    # Panel 1: Per-accession impurity rate comparison (3 bars)
    ax = axes[0]

    # Aggregate both analyses to per-GID
    agg_orig = ours_orig.groupby("GID").agg(
        n=("sample", "count"),
        orig_fail=("purity_status", lambda x: (x != "PASS").sum()),
    ).reset_index()
    agg_orig["orig_impurity"] = agg_orig["orig_fail"] / agg_orig["n"] * 100

    agg_enr = ours_enrique.groupby("GID").agg(
        enr_aligned_fail=("new_status", lambda x: (x != "PASS").sum()),
    ).reset_index()
    agg_enr["enr_aligned_impurity"] = agg_enr["enr_aligned_fail"] / agg_orig.set_index("GID").loc[agg_enr["GID"], "n"].values * 100

    combined = merged.merge(agg_orig[["GID", "orig_impurity"]], on="GID", how="left")
    combined = combined.merge(agg_enr[["GID", "enr_aligned_impurity"]], on="GID", how="left")

    # Sort by magnitude of disagreement
    combined["orig_diff"] = abs(combined["orig_impurity"] - combined["enr_impurity_pct"])
    combined["new_diff"] = abs(combined["enr_aligned_impurity"] - combined["enr_impurity_pct"])
    combined = combined.sort_values("orig_diff", ascending=False)

    # Top 15 most disagreed accessions
    top = combined.head(15)
    labels = [f"{row['Genotype']}\n({row['PLOT_CODE']})" for _, row in top.iterrows()]
    x = np.arange(len(top))
    w = 0.25

    ax.bar(x - w, top["enr_impurity_pct"], w, color="#E57373", alpha=0.8, label="Enrique's %")
    ax.bar(x, top["orig_impurity"], w, color="#64B5F6", alpha=0.8, label="Our original %")
    ax.bar(x + w, top["enr_aligned_impurity"], w, color="#81C784", alpha=0.8, label="Enrique-aligned %")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=55, ha="right", fontsize=7)
    ax.set_ylabel("Impurity Rate (%)")
    ax.set_title("Top 15 Disagreements:\nThree Classification Methods")
    ax.legend(fontsize=8)

    # Panel 2: Overall status distribution shift
    ax = axes[1]
    orig_counts = ours_orig["purity_status"].value_counts()
    new_counts = ours_enrique["new_status"].value_counts()

    categories = ["PASS", "WARNING", "FAIL"]
    orig_vals = [orig_counts.get(c, 0) for c in categories]
    new_vals = [new_counts.get(c, 0) for c in categories]

    x = np.arange(len(categories))
    w = 0.35
    colors_orig = ["#81C784", "#FFB74D", "#E57373"]
    colors_new = ["#4CAF50", "#FF9800", "#F44336"]

    bars1 = ax.bar(x - w/2, orig_vals, w, color=colors_orig, alpha=0.7, edgecolor="white")
    bars2 = ax.bar(x + w/2, new_vals, w, color=colors_new, alpha=0.9, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("Number of Samples")
    ax.set_title("Status Distribution Shift\n(Original → Enrique-Aligned)")

    # Add count labels
    for bar_set in [bars1, bars2]:
        for bar in bar_set:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h + 2, str(int(h)),
                        ha="center", fontsize=9)

    ax.legend([bars1[0], bars2[0]], ["Original thresholds", "Enrique-aligned"],
              fontsize=9, loc="upper right")

    # Panel 3: Transition matrix — how many samples changed status?
    ax = axes[2]
    transitions = pd.crosstab(
        ours_enrique["purity_status"].map(lambda x: f"Orig: {x}"),
        ours_enrique["new_status"].map(lambda x: f"New: {x}"),
    )
    # Ensure all categories exist
    for prefix in ["Orig: ", "New: "]:
        for cat in categories:
            col = f"{prefix}{cat}"
            if prefix == "Orig: " and col not in transitions.index:
                transitions.loc[col] = 0
            if prefix == "New: " and col not in transitions.columns:
                transitions[col] = 0

    ordered_rows = [f"Orig: {c}" for c in categories]
    ordered_cols = [f"New: {c}" for c in categories]
    transitions = transitions.reindex(index=ordered_rows, columns=ordered_cols, fill_value=0)

    im = ax.imshow(transitions.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(ordered_cols)))
    ax.set_xticklabels([c.replace("New: ", "") for c in ordered_cols])
    ax.set_yticks(range(len(ordered_rows)))
    ax.set_yticklabels([c.replace("Orig: ", "") for c in ordered_rows])
    ax.set_xlabel("Enrique-Aligned Status")
    ax.set_ylabel("Original Status")
    ax.set_title("Status Transition Matrix\n(how many samples changed?)")

    for i in range(len(ordered_rows)):
        for j in range(len(ordered_cols)):
            val = transitions.values[i, j]
            if val > 0:
                color = "white" if val > transitions.values.max() * 0.5 else "black"
                ax.text(j, i, str(val), ha="center", va="center",
                        fontsize=14, fontweight="bold", color=color)

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_th1_threshold_impact.png"), bbox_inches="tight")
    plt.close()
    return combined


def fig_th2_disagreement_anatomy(ours, merged, outdir):
    """
    For each disagreement, show exactly WHY the methods disagree and whether
    the disagreement is threshold-driven or fundamental.
    """
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    # Top-left: CLWQHZN47 F6695/F6696 — the sub-line problem
    ax = axes[0, 0]
    clwq47 = ours[ours["group"] == "CLWQHZN47"].copy()
    clwq47["lot"] = clwq47["sample"].str.extract(r'^(F\d+)')

    lots_sorted = clwq47.groupby("lot")["concordance"].median().sort_values()
    lot_colors = {}
    cmap = plt.cm.Set2
    for i, lot in enumerate(lots_sorted.index):
        lot_colors[lot] = cmap(i / max(len(lots_sorted) - 1, 1))

    for lot in lots_sorted.index:
        subset = clwq47[clwq47["lot"] == lot]
        ax.scatter(subset["concordance"], subset["het_rate"],
                   c=[lot_colors[lot]], s=60, alpha=0.8, edgecolors="white",
                   label=f"{lot} (n={len(subset)})")

    ax.axvline(0.80, color="red", linestyle="--", alpha=0.5, label="Concordance FAIL (0.80)")
    ax.axhline(0.10, color="orange", linestyle="--", alpha=0.5, label="Inbred het FAIL (0.10)")
    ax.set_xlabel("Group-Wide Concordance")
    ax.set_ylabel("Heterozygosity Rate")
    ax.set_title("CLWQHZN47: Sub-Line Problem\n(F6695/F6696 are pure but different sub-lines)")
    ax.legend(fontsize=7, loc="upper left")
    ax.set_xlim(0.6, 1.02)

    # Top-right: Hembra F7 — residual heterozygosity
    ax = axes[0, 1]
    hemf7 = ours[ours["group"] == "Hembra F7"].copy()
    hemf7["lot"] = hemf7["sample"].str.extract(r'^(F\d+)')

    colors = ["#4CAF50" if h < 0.20 else "#F44336" for h in hemf7["het_rate"]]
    ax.scatter(hemf7["concordance"], hemf7["het_rate"], c=colors, s=80,
               edgecolors="white", alpha=0.8, zorder=3)

    for _, row in hemf7.iterrows():
        ax.annotate(row["sample"].split(" - ")[1], (row["concordance"], row["het_rate"]),
                    fontsize=6, alpha=0.7, ha="center", va="bottom")

    ax.axhline(0.10, color="red", linestyle="--", alpha=0.5, label="Original FAIL (10%)")
    ax.axhline(0.20, color="green", linestyle="--", alpha=0.5, label="Enrique-aligned FAIL (20%)")
    ax.axhspan(0.10, 0.20, color="yellow", alpha=0.1, label="Reconciliation zone")

    ax.set_xlabel("Concordance with Group Consensus")
    ax.set_ylabel("Heterozygosity Rate")
    ax.set_title("Hembra F7: Residual Heterozygosity\n(9/10 samples are uniform at ~14% het — not fully fixed)")
    ax.legend(fontsize=8)

    # Bottom-left: Hybrid lots — selfed seed detection comparison
    ax = axes[1, 0]

    # Get all hybrid samples with our and EK classification
    hyb = ours[ours["is_hybrid"] == True].copy()
    hyb["lot"] = hyb["sample"].str.extract(r'^(F\d+)')

    # Color by our original status
    status_colors = {"PASS": "#4CAF50", "WARNING": "#FFC107", "FAIL": "#F44336"}
    colors = [status_colors.get(s, "#9E9E9E") for s in hyb["purity_status"]]

    ax.scatter(hyb["concordance"], hyb["het_rate"], c=colors, s=30, alpha=0.5,
               edgecolors="none")

    ax.axhline(0.20, color="red", linestyle="--", alpha=0.5, label="Hybrid min het FAIL (0.20)")
    ax.axhline(0.15, color="orange", linestyle="--", alpha=0.5, label="Hybrid min het WARN (0.15)")

    legend_elements = [
        Patch(facecolor="#4CAF50", label="PASS"),
        Patch(facecolor="#FFC107", label="WARNING"),
        Patch(facecolor="#F44336", label="FAIL"),
        Line2D([0], [0], color="red", linestyle="--", label="Het FAIL (0.20)"),
        Line2D([0], [0], color="orange", linestyle="--", label="Het WARN (0.15)"),
    ]
    ax.legend(handles=legend_elements, fontsize=8, loc="lower left")
    ax.set_xlabel("Concordance with Group Consensus")
    ax.set_ylabel("Heterozygosity Rate")
    ax.set_title("Hybrid Samples: Het Rate vs Concordance\n(selfed seeds cluster at low het)")

    # Bottom-right: Fundamental disagreements that thresholds can't fix
    ax = axes[1, 1]

    # These are cases where Enrique and our analysis fundamentally disagree:
    # 1. CLWQHZN47 F6695 — we need lot-level concordance, not just threshold change
    # 2. CLWQHZN46 F6701 — "No es el genotipo esperado" — wrong genotype entirely

    categories = [
        "Threshold-driven\n(reconcilable)",
        "Methodology-driven\n(need lot-concordance)",
        "Fundamental\n(potential error)",
    ]

    # Classify each accession's disagreement
    threshold_driven = 0
    methodology_driven = 0
    fundamental = 0
    agreed = 0

    for _, row in merged.iterrows():
        enr_accept = row["enr_status"] in ["Acceptable", "Acceptable with notes"]
        our_accept = row.get("our_pass_rate", 1) > 0.5

        if enr_accept == our_accept:
            agreed += 1
            continue

        plot = row["PLOT_CODE"]
        genotype = row["Genotype"]

        # Check if this is the sub-line concordance problem
        plot_samples = ours[ours["sample"].str.startswith(plot)]
        if len(plot_samples) > 0:
            med_het = plot_samples["het_rate"].median()
            med_conc = plot_samples["concordance"].median()

            if med_het < 0.05 and med_conc < 0.85:
                # Low het but low concordance = different sub-line
                methodology_driven += 1
            elif med_het > 0.10 and med_het < 0.20:
                # In the "reconciliation zone" between our threshold and Enrique's
                threshold_driven += 1
            elif genotype == "CLWQHZN46" and "No es el genotipo" in str(row.get("enr_notes", "")):
                fundamental += 1
            else:
                # Other disagreements
                if row.get("enr_impurity_pct", 0) == 0 and row.get("our_impurity_pct", 0) > 50:
                    methodology_driven += 1
                else:
                    threshold_driven += 1

    vals = [threshold_driven, methodology_driven, fundamental]
    total_disagree = sum(vals)

    bars = ax.bar(range(3), vals, color=["#FFC107", "#FF9800", "#F44336"], alpha=0.8,
                  edgecolor="white", width=0.6)
    ax.set_xticks(range(3))
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylabel("Number of Accessions")
    ax.set_title(f"Disagreement Classification\n({agreed} agree, {total_disagree} disagree)")

    for bar, val in zip(bars, vals):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    str(val), ha="center", fontsize=12, fontweight="bold")

    # Add annotation box
    ax.text(0.98, 0.95,
            "Threshold-driven: Different het cutoffs\n"
            "Methodology-driven: Need lot-level concordance\n"
            "Fundamental: Wrong genotype or data error",
            transform=ax.transAxes, fontsize=8, va="top", ha="right",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_th2_disagreement_anatomy.png"), bbox_inches="tight")
    plt.close()


def fig_th3_lot_concordance(ours, outdir):
    """
    Show within-lot concordance vs group-wide concordance for problem accessions.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    df = ours.copy()
    df["lot"] = df["sample"].str.extract(r'^(F\d+)')

    # Panel 1: Within-lot vs group-wide concordance scatter
    ax = axes[0]

    # Compute within-lot concordance (approximation: how similar are samples in the same lot?)
    lot_stats = []
    for (group, lot), subset in df.groupby(["group", "lot"]):
        if len(subset) < 2:
            continue
        group_conc = subset["concordance"].median()
        # Within-lot uniformity: std of het_rate (lower = more uniform)
        het_std = subset["het_rate"].std()
        het_range = subset["het_rate"].max() - subset["het_rate"].min()
        lot_stats.append({
            "group": group, "lot": lot, "n": len(subset),
            "group_concordance": group_conc,
            "het_std": het_std, "het_range": het_range,
            "med_het": subset["het_rate"].median(),
            "is_hybrid": subset["is_hybrid"].iloc[0],
        })

    lot_df = pd.DataFrame(lot_stats)
    inbred_lots = lot_df[~lot_df["is_hybrid"]]

    colors = []
    for _, row in inbred_lots.iterrows():
        if row["group_concordance"] < 0.80:
            colors.append("#F44336")  # Sub-line problem
        elif row["het_std"] > 0.05:
            colors.append("#FF9800")  # Mixed lot
        else:
            colors.append("#4CAF50")  # Clean

    sc = ax.scatter(inbred_lots["group_concordance"], inbred_lots["het_std"],
                    c=colors, s=inbred_lots["n"] * 15, alpha=0.7, edgecolors="white")

    for _, row in inbred_lots.iterrows():
        if row["group_concordance"] < 0.85 or row["het_std"] > 0.03:
            ax.annotate(f"{row['group']}\n{row['lot']}", (row["group_concordance"], row["het_std"]),
                        fontsize=7, alpha=0.8, ha="center")

    ax.axvline(0.80, color="red", linestyle="--", alpha=0.3, label="Concordance FAIL")
    ax.axvline(0.90, color="orange", linestyle="--", alpha=0.3, label="Concordance WARN")

    legend_elements = [
        Patch(facecolor="#F44336", label="Different sub-line (low conc, low het_std)"),
        Patch(facecolor="#FF9800", label="Mixed lot (high het variation)"),
        Patch(facecolor="#4CAF50", label="Clean lot"),
    ]
    ax.legend(handles=legend_elements, fontsize=8, loc="upper left")
    ax.set_xlabel("Group-Wide Concordance (median)")
    ax.set_ylabel("Within-Lot Het StdDev (uniformity)")
    ax.set_title("Inbred Lots: Group Concordance vs Internal Uniformity\n(size = sample count)")

    # Panel 2: The sub-line illustration for CLWQHZN47
    ax = axes[1]

    clwq47 = df[df["group"] == "CLWQHZN47"].copy()

    lots = sorted(clwq47["lot"].unique())
    lot_medians = clwq47.groupby("lot")[["het_rate", "concordance"]].median()
    lots_by_conc = lot_medians.sort_values("concordance").index.tolist()

    y_positions = {}
    for i, lot in enumerate(lots_by_conc):
        y_positions[lot] = i

    for lot in lots_by_conc:
        subset = clwq47[clwq47["lot"] == lot]
        y = [y_positions[lot]] * len(subset)
        med_conc = lot_medians.loc[lot, "concordance"]

        color = "#F44336" if med_conc < 0.80 else "#FFC107" if med_conc < 0.90 else "#4CAF50"
        ax.scatter(subset["concordance"], y, c=color, s=50, alpha=0.7, edgecolors="white")
        ax.annotate(f"{lot} (n={len(subset)}, med conc={med_conc:.2f})",
                    (0.58, y_positions[lot]), fontsize=8, va="center")

    ax.axvline(0.80, color="red", linestyle="--", alpha=0.5, label="FAIL threshold")
    ax.axvline(0.90, color="orange", linestyle="--", alpha=0.5, label="WARN threshold")
    ax.set_yticks(range(len(lots_by_conc)))
    ax.set_yticklabels([""] * len(lots_by_conc))
    ax.set_xlabel("Group-Wide Concordance")
    ax.set_title("CLWQHZN47 Lots: The Sub-Line Problem\n(F6695/F6696 are pure but genetically distinct)")
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(0.55, 1.05)

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_th3_lot_concordance.png"), bbox_inches="tight")
    plt.close()


def fig_th4_reconciliation_summary(combined, outdir):
    """
    Final reconciliation: what's the agreement after Enrique-aligned thresholds?
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Panel 1: Agreement improvement
    ax = axes[0]

    df = combined.copy()

    # FAIL-based agreement: WARNING is treated as acceptable
    df["enr_accept"] = df["enr_status"].isin(["Acceptable", "Acceptable with notes"])
    df["orig_accept"] = df.get("orig_fail_count", df["orig_impurity"] / 100 * df["n_samples"]) < (df["n_samples"] * 0.5)
    df["new_accept"] = df.get("new_fail_count", df["enr_aligned_impurity"] / 100 * df["n_samples"]) < (df["n_samples"] * 0.5)

    orig_agree = (df["orig_accept"] == df["enr_accept"]).sum()
    new_agree = (df["new_accept"] == df["enr_accept"]).sum()
    total = len(df)

    bars = ax.bar([0, 1], [orig_agree, new_agree], color=["#64B5F6", "#81C784"],
                  alpha=0.8, edgecolor="white", width=0.5)
    ax.axhline(total, color="gray", linestyle=":", alpha=0.5, label=f"Total accessions ({total})")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Original\nThresholds", "Enrique-Aligned\nThresholds"])
    ax.set_ylabel("Accessions in Agreement with Enrique")
    ax.set_title("Agreement with Enrique's Verdicts")
    ax.set_ylim(0, total + 3)

    for bar, val in zip(bars, [orig_agree, new_agree]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{val}/{total} ({val/total:.0%})", ha="center", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)

    # Panel 2: Remaining disagreements after reconciliation
    ax = axes[1]

    still_disagree = df[df["new_accept"] != df["enr_accept"]]

    if len(still_disagree) > 0:
        labels = [f"{row['Genotype']}\n({row['PLOT_CODE']})" for _, row in still_disagree.iterrows()]
        x = np.arange(len(still_disagree))
        w = 0.3

        ax.bar(x - w/2, still_disagree["enr_impurity_pct"], w, color="#E57373",
               alpha=0.8, label="Enrique's %")
        ax.bar(x + w/2, still_disagree["enr_aligned_impurity"], w, color="#81C784",
               alpha=0.8, label="Enrique-aligned auto %")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.set_ylabel("Impurity Rate (%)")
        ax.set_title(f"Remaining Disagreements ({len(still_disagree)} accessions)\n(these may indicate errors or methodology gaps)")
        ax.legend(fontsize=9)

        # Annotate with likely cause
        for i, (_, row) in enumerate(still_disagree.iterrows()):
            cause = "?"
            if row.get("orig_impurity", 0) > 80 and row["enr_impurity_pct"] < 20:
                cause = "sub-line?"
            elif abs(row["enr_impurity_pct"] - row["enr_aligned_impurity"]) < 15:
                cause = "close"
            ax.annotate(cause, (i, max(row["enr_impurity_pct"], row["enr_aligned_impurity"]) + 2),
                        ha="center", fontsize=7, style="italic", alpha=0.7)
    else:
        ax.text(0.5, 0.5, "Perfect agreement!\nAll accessions reconciled.",
                transform=ax.transAxes, fontsize=16, ha="center", va="center",
                bbox=dict(boxstyle="round", facecolor="#81C784", alpha=0.3))
        ax.set_title("Remaining Disagreements")

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_th4_reconciliation_summary.png"), bbox_inches="tight")
    plt.close()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("Part 4: Threshold Sensitivity — Reconciling with Enrique's Methodology")
    print("=" * 70)
    print()

    print("Loading data...")
    ours, enr, ek = load_all_data()
    print(f"  {len(ours)} samples from our analysis")
    print(f"  {len(enr)} accessions from Enrique")
    if ek is not None:
        print(f"  {len(ek)} hybrid samples from EK (with distance metrics)")
    print()

    # Parse Enrique's verdicts
    parsed = enr["Purity summary (% de Outcross/self o residual heterozygosity)"].apply(parse_enrique_verdict)
    enr = pd.concat([enr, pd.DataFrame(parsed.tolist())], axis=1)

    # Aggregate original results to per-GID
    agg = ours.groupby("GID").agg(
        n_samples=("sample", "count"),
        n_pass=("purity_status", lambda x: (x == "PASS").sum()),
        our_pass_rate=("purity_status", lambda x: (x == "PASS").mean()),
        group=("group", "first"),
        is_hybrid=("is_hybrid", "first"),
    ).reset_index()
    agg["our_impurity_pct"] = (1 - agg["our_pass_rate"]) * 100
    merged = enr.merge(agg, on="GID", how="left")

    # ── Reclassify with Enrique-aligned thresholds ──
    print("THRESHOLD COMPARISON:")
    print(f"{'Metric':<30s} {'Original':>12s} {'Enrique-aligned':>16s}")
    print("-" * 60)
    for key in ["inbred_het_fail", "inbred_het_warn", "hybrid_het_min_warn",
                "hybrid_het_min_fail", "concordance_fail", "concordance_warn"]:
        print(f"  {key:<28s} {ORIG[key]:>10.0%} {ENRIQUE[key]:>14.0%}")
    print(f"  {'lot-level concordance':<28s} {'No':>10s} {'Yes':>14s}")
    print()

    # Compute within-lot uniformity (for concordance override)
    ours_with_lots = compute_within_lot_uniformity(ours)

    # Apply Enrique-aligned thresholds
    ours_reclass = ours_with_lots.copy()
    new_statuses = []
    new_reasons = []
    for _, row in ours_reclass.iterrows():
        status, reason = classify_sample_enrique_aligned(row, ENRIQUE)
        new_statuses.append(status)
        new_reasons.append(reason)
    ours_reclass["new_status"] = new_statuses
    ours_reclass["new_reason"] = new_reasons

    # Summary
    print("ORIGINAL STATUS DISTRIBUTION:")
    for status in ["PASS", "WARNING", "FAIL"]:
        n = (ours["purity_status"] == status).sum()
        print(f"  {status}: {n} ({n/len(ours):.0%})")
    print()

    print("ENRIQUE-ALIGNED STATUS DISTRIBUTION:")
    for status in ["PASS", "WARNING", "FAIL"]:
        n = (ours_reclass["new_status"] == status).sum()
        print(f"  {status}: {n} ({n/len(ours_reclass):.0%})")
    print()

    # Transitions
    print("STATUS TRANSITIONS (Original → Enrique-aligned):")
    transitions = pd.crosstab(ours_reclass["purity_status"], ours_reclass["new_status"],
                              margins=True)
    print(transitions.to_string())
    print()

    # Per-accession comparison
    agg_new = ours_reclass.groupby("GID").agg(
        new_pass=("new_status", lambda x: (x == "PASS").sum()),
    ).reset_index()
    agg_new["new_pass_rate"] = agg_new["new_pass"] / agg.set_index("GID").loc[agg_new["GID"], "n_samples"].values
    agg_new["new_impurity_pct"] = (1 - agg_new["new_pass_rate"]) * 100

    merged2 = merged.merge(agg_new[["GID", "new_impurity_pct"]], on="GID", how="left")

    print("PER-ACCESSION COMPARISON (sorted by disagreement):")
    print(f"{'Genotype':<20s} {'Plot':<7s} {'Enrique':>8s} {'Original':>10s} {'Aligned':>10s}  {'Verdict':<25s} Reconciled?")
    print("-" * 100)

    merged2["orig_diff"] = abs(merged2["our_impurity_pct"] - merged2["enr_impurity_pct"])
    merged2["new_diff"] = abs(merged2["new_impurity_pct"] - merged2["enr_impurity_pct"])

    for _, row in merged2.sort_values("orig_diff", ascending=False).iterrows():
        enr_pct = f"{row['enr_impurity_pct']:.0f}%" if pd.notna(row["enr_impurity_pct"]) else "N/A"
        orig_pct = f"{row['our_impurity_pct']:.0f}%" if pd.notna(row["our_impurity_pct"]) else "N/A"
        new_pct = f"{row['new_impurity_pct']:.0f}%" if pd.notna(row["new_impurity_pct"]) else "N/A"
        reconciled = "✓" if row["new_diff"] < 15 else "✗"
        if row["new_diff"] < row["orig_diff"]:
            reconciled += " (improved)"
        print(f"  {row['Genotype']:<20s} {row['PLOT_CODE']:<7s} {enr_pct:>6s} {orig_pct:>8s} {new_pct:>8s}  {row['enr_status']:<25s} {reconciled}")
    print()

    # Count agreements
    # Enrique "accept" = Acceptable or Acceptable with notes
    # Enrique "reject" = Not acceptable, Impure (hybrid lot)
    # Our "accept" = majority of samples not FAIL (PASS + WARNING count as OK)
    agg_new_detail = ours_reclass.groupby("GID").agg(
        new_fail_count=("new_status", lambda x: (x == "FAIL").sum()),
    ).reset_index()
    merged2 = merged2.merge(agg_new_detail[["GID", "new_fail_count"]], on="GID", how="left")

    orig_fail_count = ours.groupby("GID").agg(
        orig_fail_count=("purity_status", lambda x: (x == "FAIL").sum()),
    ).reset_index()
    merged2 = merged2.merge(orig_fail_count, on="GID", how="left")

    enr_accept = merged2["enr_status"].isin(["Acceptable", "Acceptable with notes"])
    # "Accept" = less than half of samples are FAIL (WARNING is tolerable)
    orig_accept = merged2["orig_fail_count"] < (merged2["n_samples"] * 0.5)
    new_accept = merged2["new_fail_count"] < (merged2["n_samples"] * 0.5)

    orig_agree = (enr_accept == orig_accept).sum()
    new_agree = (enr_accept == new_accept).sum()
    print(f"AGREEMENT SUMMARY (FAIL-based, WARNING treated as acceptable):")
    print(f"  Original thresholds:       {orig_agree}/{len(merged2)} ({orig_agree/len(merged2):.0%}) agree with Enrique")
    print(f"  Enrique-aligned thresholds: {new_agree}/{len(merged2)} ({new_agree/len(merged2):.0%}) agree with Enrique")
    print()

    # Identify remaining disagreements
    still_disagree = merged2[(enr_accept != new_accept)]
    if len(still_disagree) > 0:
        print(f"REMAINING DISAGREEMENTS ({len(still_disagree)}):")
        for _, row in still_disagree.iterrows():
            print(f"  {row['Genotype']} ({row['PLOT_CODE']}): Enrique={row['enr_status']}, "
                  f"auto={row['new_impurity_pct']:.0f}% impure")
            # Diagnose
            plot_samples = ours_reclass[ours_reclass["sample"].str.startswith(row["PLOT_CODE"])]
            if len(plot_samples) > 0:
                med_conc = plot_samples["concordance"].median()
                med_het = plot_samples["het_rate"].median()
                fail_reasons = plot_samples[plot_samples["new_status"] == "FAIL"]["new_reason"].value_counts()
                if not fail_reasons.empty:
                    print(f"    → med_conc={med_conc:.3f}, med_het={med_het:.4f}")
                    print(f"    → fail reasons: {fail_reasons.to_dict()}")
        print()

    # Generate figures
    print("Generating figures...")
    combined = fig_th1_threshold_impact(ours, ours_reclass, merged2, OUTDIR)
    print("  fig_th1_threshold_impact.png")

    fig_th2_disagreement_anatomy(ours, merged2, OUTDIR)
    print("  fig_th2_disagreement_anatomy.png")

    fig_th3_lot_concordance(ours, OUTDIR)
    print("  fig_th3_lot_concordance.png")

    fig_th4_reconciliation_summary(combined, OUTDIR)
    print("  fig_th4_reconciliation_summary.png")

    # Save summary
    csv_path = os.path.join(OUTDIR, "threshold_comparison_summary.csv")
    merged2.to_csv(csv_path, index=False)
    print(f"\nSaved: {csv_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
