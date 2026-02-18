#!/usr/bin/env python3
"""
Part 3: Comparison of Enrique's Per-Accession Purity Verdicts with
Our Automated Per-Sample Analysis (ZMS25508 B04)
=================================================================

Enrique's spreadsheet provides one summary verdict per GID/accession (37 entries),
while our automated analysis provides per-sample calls (538 samples across the
same 37 accessions). This script aggregates our sample-level results to the
accession level and compares them with Enrique's manual verdicts.

Usage:
    python3 enrique_comparison.py <enrique_csv> [purity_summary.csv]
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
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.dpi": 150,
})


# ── Data Loading & Parsing ─────────────────────────────────────────────────────
def parse_enrique_verdict(verdict_str):
    """Parse Enrique's free-text verdict into structured fields."""
    if pd.isna(verdict_str):
        return {"enr_status": "Unknown", "enr_impurity_pct": np.nan, "enr_notes": ""}

    v = str(verdict_str).strip()

    # Check for explicit rejection
    if "No aceptable" in v or "No es el genotipo" in v:
        # Try to extract percentage
        pct_match = re.search(r'(\d+)\s*%', v)
        pct = float(pct_match.group(1)) if pct_match else np.nan
        return {"enr_status": "Not acceptable", "enr_impurity_pct": pct, "enr_notes": v}

    # "Aceptable" with qualifications
    if "Aceptable" in v or "aceptable" in v:
        pct_match = re.search(r'(\d+)\s*%', v)
        pct = float(pct_match.group(1)) if pct_match else 0.0

        if pct > 0:
            return {"enr_status": "Acceptable with notes", "enr_impurity_pct": pct, "enr_notes": v}
        else:
            return {"enr_status": "Acceptable", "enr_impurity_pct": 0.0, "enr_notes": v}

    # Percentage-based verdicts (F5 hybrid lots)
    pct_match = re.search(r'(\d+)\s*%', v)
    if pct_match:
        pct = float(pct_match.group(1))
        return {"enr_status": "Impure (hybrid lot)", "enr_impurity_pct": pct, "enr_notes": v}

    return {"enr_status": "Unknown", "enr_impurity_pct": np.nan, "enr_notes": v}


def load_data(enrique_csv, our_csv):
    enr = pd.read_csv(enrique_csv)
    ours = pd.read_csv(our_csv)

    # Parse Enrique's verdicts
    parsed = enr["Purity summary (% de Outcross/self o residual heterozygosity)"].apply(parse_enrique_verdict)
    enr = pd.concat([enr, pd.DataFrame(parsed.tolist())], axis=1)

    # Aggregate our per-sample results to per-GID
    agg = ours.groupby("GID").agg(
        n_samples=("sample", "count"),
        n_pass=("purity_status", lambda x: (x == "PASS").sum()),
        n_warn=("purity_status", lambda x: (x == "WARNING").sum()),
        n_fail=("purity_status", lambda x: (x == "FAIL").sum()),
        med_het=("het_rate", "median"),
        mean_het=("het_rate", "mean"),
        std_het=("het_rate", "std"),
        med_concordance=("concordance", "median"),
        mean_concordance=("concordance", "mean"),
        min_concordance=("concordance", "min"),
        mean_fail_rate=("fail_rate", "mean"),
        group=("group", "first"),
        is_hybrid=("is_hybrid", "first"),
    ).reset_index()

    agg["our_pass_rate"] = agg["n_pass"] / agg["n_samples"]
    agg["our_fail_rate_samples"] = agg["n_fail"] / agg["n_samples"]
    agg["our_impurity_pct"] = (1 - agg["our_pass_rate"]) * 100

    # Merge
    merged = enr.merge(agg, on="GID", how="left")

    return enr, ours, agg, merged


# ── Figures ────────────────────────────────────────────────────────────────────
def fig_cmp1_verdict_comparison(merged, outdir):
    """Bar chart comparing Enrique's impurity % vs our automated impurity %."""
    fig, ax = plt.subplots(figsize=(18, 7))

    # Sort by Enrique's impurity rate
    df = merged.dropna(subset=["enr_impurity_pct"]).sort_values("enr_impurity_pct", ascending=False)
    # Add entries with 0% impurity
    df_zero = merged[merged["enr_impurity_pct"] == 0].sort_values("our_impurity_pct", ascending=False)
    df = pd.concat([df[df["enr_impurity_pct"] > 0], df_zero])

    labels = [f"{row['Genotype']}\n(GID {int(row['GID'])})" for _, row in df.iterrows()]
    x = np.arange(len(df))
    w = 0.35

    bars1 = ax.bar(x - w/2, df["enr_impurity_pct"], w, color="#E57373", alpha=0.8,
                    label="Enrique's impurity %", edgecolor="white")
    bars2 = ax.bar(x + w/2, df["our_impurity_pct"], w, color="#64B5F6", alpha=0.8,
                    label="Our automated impurity %", edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=7)
    ax.set_ylabel("Impurity Rate (%)")
    ax.set_title("Enrique's Manual Verdict vs. Our Automated Purity Analysis\n(per-accession impurity rate)")
    ax.legend(fontsize=10)

    # Add sample count annotations
    for i, (_, row) in enumerate(df.iterrows()):
        n = row.get("n_samples", 0)
        if pd.notna(n):
            ax.annotate(f"n={int(n)}", (i, max(row["enr_impurity_pct"], row["our_impurity_pct"]) + 1),
                        ha="center", fontsize=6, alpha=0.7)

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_cmp1_verdict_comparison.png"), bbox_inches="tight")
    plt.close()


def fig_cmp2_status_heatmap(merged, outdir):
    """Heatmap of Enrique's verdict vs our pass/warn/fail counts."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Prepare data: one row per accession, columns = our pass/warn/fail rates
    df = merged[["Genotype", "GID", "PLOT_CODE", "enr_status", "enr_impurity_pct",
                  "n_samples", "n_pass", "n_warn", "n_fail",
                  "our_pass_rate", "med_het", "med_concordance"]].copy()
    df = df.sort_values(["enr_status", "enr_impurity_pct"], ascending=[True, False])

    labels = [f"{row['Genotype']} ({row['PLOT_CODE']})" for _, row in df.iterrows()]
    data = df[["our_pass_rate", "med_het", "med_concordance"]].values

    im = ax.imshow(data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["Pass Rate", "Median Het", "Median Concordance"])

    # Add text annotations
    for i in range(len(df)):
        for j in range(3):
            val = data[i, j]
            color = "white" if val < 0.4 or val > 0.8 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7, color=color)

    # Add Enrique's status as colored sidebar
    status_colors = {
        "Acceptable": "#4CAF50",
        "Acceptable with notes": "#FFC107",
        "Impure (hybrid lot)": "#FF9800",
        "Not acceptable": "#F44336",
        "Unknown": "#9E9E9E",
    }
    for i, (_, row) in enumerate(df.iterrows()):
        color = status_colors.get(row["enr_status"], "#9E9E9E")
        ax.add_patch(plt.Rectangle((-0.6, i - 0.5), 0.15, 1, color=color, clip_on=False))

    # Legend for sidebar
    legend_elements = [Patch(facecolor=c, label=s) for s, c in status_colors.items()
                       if s in df["enr_status"].values]
    ax.legend(handles=legend_elements, title="Enrique's Verdict", loc="upper left",
              bbox_to_anchor=(1.02, 1), fontsize=8)

    ax.set_title("Per-Accession Metrics vs. Enrique's Verdict\n(colored sidebar = Enrique's classification)")
    fig.colorbar(im, ax=ax, label="Rate (0-1)", shrink=0.5)
    plt.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_cmp2_status_heatmap.png"), bbox_inches="tight")
    plt.close()


def fig_cmp3_agreement_summary(merged, outdir):
    """Summary chart: how often do Enrique and our analysis agree?"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Classify agreement
    # Enrique: "Acceptable" (with or without notes) vs "Not acceptable" / "Impure"
    # Ours: majority PASS vs majority FAIL
    df = merged.copy()
    df["enr_accept"] = df["enr_status"].isin(["Acceptable", "Acceptable with notes"])
    df["our_accept"] = df["our_pass_rate"] > 0.5

    # Agreement matrix
    agree = pd.crosstab(
        df["enr_accept"].map({True: "Enrique: Accept", False: "Enrique: Reject/Impure"}),
        df["our_accept"].map({True: "Auto: Majority PASS", False: "Auto: Majority FAIL"})
    )

    # Ensure both columns exist
    for col in ["Auto: Majority PASS", "Auto: Majority FAIL"]:
        if col not in agree.columns:
            agree[col] = 0
    agree = agree[["Auto: Majority PASS", "Auto: Majority FAIL"]]

    im = ax1.imshow(agree.values, cmap="YlOrRd", aspect="auto")
    ax1.set_xticks(range(len(agree.columns)))
    ax1.set_xticklabels(agree.columns, fontsize=9)
    ax1.set_yticks(range(len(agree.index)))
    ax1.set_yticklabels(agree.index, fontsize=9)
    ax1.set_title("Agreement Matrix\n(Enrique accept/reject vs. automated majority)")

    for i in range(len(agree.index)):
        for j in range(len(agree.columns)):
            val = agree.values[i, j]
            ax1.text(j, i, str(val), ha="center", va="center",
                     fontsize=16, fontweight="bold",
                     color="white" if val > agree.values.max() * 0.5 else "black")

    # Scatter: Enrique impurity % vs our impurity %
    has_both = df.dropna(subset=["enr_impurity_pct", "our_impurity_pct"])
    colors = ["#4CAF50" if row["enr_accept"] else "#F44336" for _, row in has_both.iterrows()]
    ax2.scatter(has_both["enr_impurity_pct"], has_both["our_impurity_pct"],
                c=colors, s=60, alpha=0.7, edgecolors="white", linewidth=0.5)

    # Add labels
    for _, row in has_both.iterrows():
        ax2.annotate(f"{row['Genotype']}\n{row['PLOT_CODE']}",
                     (row["enr_impurity_pct"], row["our_impurity_pct"]),
                     fontsize=5.5, alpha=0.8, ha="center", va="bottom")

    # Diagonal
    lim = max(ax2.get_xlim()[1], ax2.get_ylim()[1])
    ax2.plot([0, lim], [0, lim], "k--", alpha=0.3, linewidth=0.8)
    ax2.set_xlabel("Enrique's Impurity Rate (%)")
    ax2.set_ylabel("Our Automated Impurity Rate (%)")
    ax2.set_title("Impurity Rate Correlation\n(green=Enrique accepts, red=Enrique rejects)")

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_cmp3_agreement_summary.png"), bbox_inches="tight")
    plt.close()


def fig_cmp4_actions_dashboard(merged, outdir):
    """Dashboard showing Enrique's recommended actions overlaid with our metrics."""
    fig, ax = plt.subplots(figsize=(16, 9))

    df = merged.sort_values("our_impurity_pct", ascending=False).head(20)

    labels = [f"{row['Genotype']} ({row['PLOT_CODE']})" for _, row in df.iterrows()]
    y = range(len(df))

    # Horizontal bar of our impurity rate
    colors = []
    for _, row in df.iterrows():
        if row["enr_status"] == "Not acceptable":
            colors.append("#F44336")
        elif row["enr_status"] == "Impure (hybrid lot)":
            colors.append("#FF9800")
        elif row["enr_status"] == "Acceptable with notes":
            colors.append("#FFC107")
        else:
            colors.append("#4CAF50")

    bars = ax.barh(y, df["our_impurity_pct"], color=colors, alpha=0.8, edgecolor="white")

    # Add Enrique's impurity % as markers
    for i, (_, row) in enumerate(df.iterrows()):
        if pd.notna(row["enr_impurity_pct"]) and row["enr_impurity_pct"] > 0:
            ax.plot(row["enr_impurity_pct"], i, "kD", markersize=8, alpha=0.7)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Impurity Rate (%)")
    ax.invert_yaxis()

    # Add recommended actions as text
    for i, (_, row) in enumerate(df.iterrows()):
        action_ops = row.get("Recommended action Ops", "")
        action_seed = row.get("Recommended action Parent seed", "")
        actions = []
        if pd.notna(action_ops) and action_ops:
            actions.append(str(action_ops))
        if pd.notna(action_seed) and action_seed:
            actions.append(str(action_seed))
        if actions:
            action_text = "; ".join(actions)
            if len(action_text) > 60:
                action_text = action_text[:57] + "..."
            ax.annotate(action_text, (df["our_impurity_pct"].iloc[i] + 1, i),
                        fontsize=6, va="center", alpha=0.8, style="italic")

    ax.set_title("Top 20 Accessions by Impurity Rate\n(bars = automated, diamonds = Enrique's %, color = Enrique's verdict)")

    legend_elements = [
        Patch(facecolor="#F44336", label="Not acceptable"),
        Patch(facecolor="#FF9800", label="Impure (hybrid lot)"),
        Patch(facecolor="#FFC107", label="Acceptable with notes"),
        Patch(facecolor="#4CAF50", label="Acceptable"),
        plt.Line2D([0], [0], marker="D", color="k", linestyle="None", markersize=8, label="Enrique's impurity %"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8)

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_cmp4_actions_dashboard.png"), bbox_inches="tight")
    plt.close()


# ── README ─────────────────────────────────────────────────────────────────────
def build_readme(merged):
    n_total = len(merged)
    n_accept = merged["enr_status"].isin(["Acceptable", "Acceptable with notes"]).sum()
    n_reject = (merged["enr_status"] == "Not acceptable").sum()
    n_impure = (merged["enr_status"] == "Impure (hybrid lot)").sum()

    lines = []
    for _, row in merged.sort_values("our_impurity_pct", ascending=False).iterrows():
        enr_pct = f"{row['enr_impurity_pct']:.0f}%" if pd.notna(row["enr_impurity_pct"]) else "N/A"
        our_pct = f"{row['our_impurity_pct']:.0f}%" if pd.notna(row["our_impurity_pct"]) else "N/A"
        lines.append(
            f"  {row['Genotype']:20s}  {row['PLOT_CODE']}  "
            f"Enrique={enr_pct:>5s}  Auto={our_pct:>5s}  "
            f"n={int(row['n_samples']) if pd.notna(row.get('n_samples')) else '?':>3}  "
            f"Verdict: {row['enr_status']}"
        )

    readme = f"""README — Part 3: Enrique's Accession-Level Verdicts vs. Automated Analysis
==========================================================================

RELATIONSHIP TO OTHER DATA
This CSV ("Genotype and seed sources") is from the SAME sequencing run (ZMS25508 B04).
It contains Enrique's per-accession purity verdicts for all 37 GIDs in the experiment.
Where our automated analysis produces per-sample calls (538 samples), Enrique provides
one summary verdict per accession with recommended actions for operations and parent seed.

DATA STRUCTURE
37 rows, one per GID/accession. Key columns:
  - GID / Genotype / PLOT_CODE: accession identifiers (match original genotyping data)
  - Purity summary: free-text verdict with impurity percentages and types
  - Recommended action Ops: actions for field operations (detasseling, roguing)
  - Recommended action Parent seed: actions for seed stock management
  - Uso en Produccion: current production use status
  - Referencia: role (commercial hybrid, commercial parent, pre-commercial parent, etc.)
  - Parental / Parental Lider: parental identity and leadership status

ENRIQUE'S VERDICTS
  Acceptable:           {n_accept} of {n_total} accessions ({n_accept/n_total:.0%})
  Not acceptable:       {n_reject} of {n_total} ({n_reject/n_total:.0%})
  Impure (hybrid lot):  {n_impure} of {n_total} ({n_impure/n_total:.0%})

PER-ACCESSION COMPARISON (sorted by our automated impurity rate):
{chr(10).join(lines)}

KEY DISAGREEMENTS
Enrique operates at the accession level and uses domain knowledge (production context,
historical performance) that our automated analysis doesn't have. Our analysis flags
individual samples while Enrique accepts whole accessions with notes like "20% out" as
"Acceptable" because the impurity type (outcross in an inbred) may be tolerable in context.

FIGURES:
  fig_cmp1: Side-by-side bar chart of impurity rates
  fig_cmp2: Per-accession metrics heatmap with Enrique's verdict sidebar
  fig_cmp3: Agreement matrix and impurity rate correlation scatter
  fig_cmp4: Top accessions by impurity with recommended actions

HOW TO REPRODUCE:
  python3 enrique_comparison.py <enrique_csv> [purity_summary.csv]
  Requires: pandas, numpy, matplotlib
"""
    return readme


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        candidates = [
            os.path.expanduser("~/Downloads/Genotype and seed sources - commercial hybrid seed and parent seed - 18-02-2025.xlsx - Genotype and seed sources.csv"),
        ]
        enr_path = None
        for c in candidates:
            if os.path.exists(c):
                enr_path = c
                break
        if enr_path is None:
            print("Usage: python3 enrique_comparison.py <enrique_csv> [purity_summary.csv]")
            sys.exit(1)
    else:
        enr_path = sys.argv[1]

    our_csv = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "purity_summary.csv"
    )

    outdir = os.path.dirname(os.path.abspath(__file__))
    print(f"Enrique's data: {enr_path}")
    print(f"Our analysis:   {our_csv}")
    print(f"Output:         {outdir}")
    print()

    print("Loading and merging data...")
    enr, ours, agg, merged = load_data(enr_path, our_csv)
    print(f"  {len(enr)} accessions from Enrique")
    print(f"  {len(ours)} samples from our analysis")
    print(f"  {len(merged)} merged rows")
    print()

    # Print comparison
    print("COMPARISON:")
    print(f"{'Genotype':<20s} {'PLOT':<7s} {'Enrique':>10s} {'Ours':>10s} {'n':>4s}  Verdict")
    print("-" * 75)
    for _, row in merged.sort_values("our_impurity_pct", ascending=False).iterrows():
        enr_pct = f"{row['enr_impurity_pct']:.0f}%" if pd.notna(row["enr_impurity_pct"]) else "N/A"
        our_pct = f"{row['our_impurity_pct']:.0f}%" if pd.notna(row["our_impurity_pct"]) else "N/A"
        n = int(row["n_samples"]) if pd.notna(row.get("n_samples")) else "?"
        print(f"  {row['Genotype']:<20s} {row['PLOT_CODE']:<7s} {enr_pct:>8s} {our_pct:>8s} {n:>4}  {row['enr_status']}")
    print()

    # Figures
    print("Generating figures...")
    fig_cmp1_verdict_comparison(merged, outdir)
    print("  fig_cmp1_verdict_comparison.png")
    fig_cmp2_status_heatmap(merged, outdir)
    print("  fig_cmp2_status_heatmap.png")
    fig_cmp3_agreement_summary(merged, outdir)
    print("  fig_cmp3_agreement_summary.png")
    fig_cmp4_actions_dashboard(merged, outdir)
    print("  fig_cmp4_actions_dashboard.png")

    # CSV
    csv_path = os.path.join(outdir, "enrique_comparison_summary.csv")
    merged.to_csv(csv_path, index=False)
    print(f"\nSaved: {csv_path}")

    # README
    readme = build_readme(merged)
    readme_path = os.path.join(outdir, "enrique_comparison_readme.txt")
    with open(readme_path, "w") as f:
        f.write(readme)
    print(f"Saved: {readme_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
