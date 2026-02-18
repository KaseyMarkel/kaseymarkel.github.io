README — Part 3: Enrique's Accession-Level Verdicts vs. Automated Analysis
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
  Acceptable:           29 of 37 accessions (78%)
  Not acceptable:       2 of 37 (5%)
  Impure (hybrid lot):  6 of 37 (16%)

PER-ACCESSION COMPARISON (sorted by our automated impurity rate):
  CLWQHZN47             F6695  Enrique=   0%  Auto= 100%  n= 10  Verdict: Acceptable
  Hembra F7             F6681  Enrique=  10%  Auto= 100%  n= 10  Verdict: Acceptable with notes
  CLWQHZN46             F6701  Enrique=  N/A  Auto=  80%  n=  5  Verdict: Not acceptable
  CLWQHZN47             F6717  Enrique=  50%  Auto=  60%  n= 10  Verdict: Not acceptable
  CLWQHZN86             F6672  Enrique=  20%  Auto=  60%  n=  5  Verdict: Acceptable with notes
  CLWQHZN47             F6706  Enrique=   0%  Auto=  40%  n=  5  Verdict: Acceptable
  SNLWZ240088           F6711  Enrique=   4%  Auto=  20%  n=  5  Verdict: Acceptable with notes
  CLWQHZN46             F6702  Enrique=  20%  Auto=  20%  n=  5  Verdict: Acceptable with notes
  CLWQHZN86             F6676  Enrique=  20%  Auto=  20%  n=  5  Verdict: Acceptable with notes
  F5                    F6601  Enrique=  24%  Auto=  20%  n=100  Verdict: Impure (hybrid lot)
  CLWQHZN86             F6668  Enrique=  20%  Auto=  20%  n=  5  Verdict: Acceptable with notes
  F5                    F6625  Enrique=  30%  Auto=  13%  n= 30  Verdict: Impure (hybrid lot)
  SNMLWZ200296-C        F6715  Enrique=   4%  Auto=  10%  n= 10  Verdict: Acceptable with notes
  CLWQHZN12             F6697  Enrique=  10%  Auto=  10%  n= 10  Verdict: Acceptable with notes
  F5                    F6613  Enrique=  16%  Auto=   9%  n= 43  Verdict: Impure (hybrid lot)
  F5                    F6629  Enrique=  13%  Auto=   7%  n= 30  Verdict: Impure (hybrid lot)
  Hembra F5             F6664  Enrique=   3%  Auto=   7%  n= 30  Verdict: Acceptable with notes
  F5                    F6633  Enrique=  10%  Auto=   0%  n= 30  Verdict: Impure (hybrid lot)
  SNLWZ240001           F6714  Enrique=   0%  Auto=   0%  n=  8  Verdict: Acceptable
  CLWQHZN47-5-1-1-B     F6712  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  CLWQHZN46-6-1-1-B     F6709  Enrique=   0%  Auto=   0%  n=  7  Verdict: Acceptable
  CLWQHZN47             F6708  Enrique=   0%  Auto=   0%  n=  5  Verdict: Acceptable
  CLWQHZN47             F6705  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  CLWQHZN46             F6704  Enrique=   0%  Auto=   0%  n=  5  Verdict: Acceptable
  CLWQHZN46             F6703  Enrique=   0%  Auto=   0%  n=  5  Verdict: Acceptable
  CLWQHZN46             F6699  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  F5-DOBLE              F6647  Enrique=   5%  Auto=   0%  n= 40  Verdict: Impure (hybrid lot)
  Hembra F5             F6656  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  SNCLWQZ1714-13        F6693  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  CLWQZ19020            F6691  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  SNHWZ230164           F6687  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  SNHWZ241205           F6685  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  Hembra F5B            F6683  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  Hembra F5             F6658  Enrique=   0%  Auto=   0%  n= 10  Verdict: Acceptable
  CLWQHZN86             F6680  Enrique=   0%  Auto=   0%  n=  5  Verdict: Acceptable
  CLWQHZN86             F6678  Enrique=   0%  Auto=   0%  n=  5  Verdict: Acceptable
  SNMLWZ211776          F6689  Enrique=   4%  Auto=   0%  n= 10  Verdict: Acceptable with notes

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
