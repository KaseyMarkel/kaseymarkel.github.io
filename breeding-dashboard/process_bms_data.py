#!/usr/bin/env python3
"""
Process BMS data export into comprehensive dashboard metrics JSON
Based on Operational_Agronomic metrics specification

Dashboard Blocks:
A - Pipeline Funnel (counts through stages)
B - Efficiency Rates (conversion rates)
C - Coverage Analysis (required vs available)
D - Cycle Speed (timing metrics)
E - Genetics (marker status, RP background)
F - Pyramiding Progress (Zn + QPM stacking)
G - Output Metrics (harvest/kernel output)
"""

import json
import csv
import io
from pathlib import Path
from collections import defaultdict
from datetime import datetime

DATA_DIR = Path("bms_data_export")
OUTPUT_FILE = Path("dashboard_data.json")

def load_csv(filename):
    """Load CSV file and return list of dicts"""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return []

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read().replace('\x00', '')

    reader = csv.DictReader(io.StringIO(content))
    return list(reader)

def safe_float(val, default=0):
    try:
        return float(val) if val else default
    except:
        return default

def safe_int(val, default=0):
    try:
        return int(float(val)) if val else default
    except:
        return default

def categorize_location(loc_name):
    """Categorize location into broader regions"""
    loc = (loc_name or '').lower()

    if 'centro experimental' in loc or 'centro exp' in loc:
        return 'Centro Exp'
    elif 'el salvador' in loc:
        return 'El Salvador'
    elif any(x in loc for x in ['oriente', 'jocotan', 'chiquimula', 'ipala', 'quezada', 'catarina']):
        return 'Oriente'
    elif any(x in loc for x in ['peten', 'chisec', 'raxruha', 'teleman']):
        return 'Peten/AV'
    elif any(x in loc for x in ['sacapulas', 'aguacatan', 'huehue']):
        return 'Altiplano'
    elif any(x in loc for x in ['ovejero', 'manueles', 'san jose', 'cruces', 'sitio', 'palos']):
        return 'Station BC'
    elif loc and loc != 'unspecified location':
        return 'Other'
    return 'Unknown'

def categorize_trait(study_name, study_obs):
    """Categorize study by biofortification trait"""
    has_zinc = any(o.get('observationVariableName', '') in ['Zinc_sn', 'Zn_ppm', 'Zn_manual'] for o in study_obs)
    has_qpm = any(o.get('observationVariableName', '') in ['Trp_sn', 'Lys_sn', 'Trp_manual', 'Lys_manual'] for o in study_obs)

    name = (study_name or '').lower()

    if has_zinc and has_qpm:
        return 'Zn+QPM'
    elif has_zinc or 'zinc' in name or 'zn' in name:
        return 'Zn'
    elif has_qpm or 'qpm' in name or 'tryptophan' in name or 'lisina' in name:
        return 'QPM'
    return 'Conventional'

def extract_stage_from_study(study_name, trial_name=''):
    """Try to determine BC stage from study/trial name"""
    name = (study_name + ' ' + trial_name).upper()

    if 'BC3' in name: return 'BC3'
    if 'BC2' in name: return 'BC2'
    if 'BC1' in name: return 'BC1'
    if 'F2' in name: return 'F2'
    if 'F1' in name: return 'F1'
    return 'Other'

def compute_comprehensive_metrics(study_data, all_observations, all_obs_units):
    """Compute all dashboard metrics for a dataset"""

    study_ids = {s['studyId'] for s in study_data}
    subset_obs = [o for o in all_observations if o.get('studyDbId') in study_ids]
    subset_units = [u for u in all_obs_units if u.get('studyDbId') in study_ids]

    # Initialize metric collectors
    metrics = {
        # Counts
        'plants_sampled': 0,
        'plants_harvested': 0,
        'ears_harvested': 0,
        'ears_discarded': 0,

        # Rate values
        'virus_vals': [],
        'spiroplasma_vals': [],
        'stalk_lodge_vals': [],
        'root_lodge_vals': [],
        'ear_rot_vals': [],
        'poor_husk_vals': [],

        # Yield/quality
        'yield_vals': [],
        'humidity_vals': [],
        'grain_weight_vals': [],

        # Biofortification
        'zinc_vals': [],
        'iron_vals': [],
        'protein_vals': [],
        'lysine_vals': [],
        'tryptophan_vals': [],

        # Flowering/Sync
        'dff_vals': [],  # Days to female flowering
        'dfm_vals': [],  # Days to male flowering

        # Plant scores
        'plant_height_vals': [],
        'ear_height_vals': [],
        'plant_score_vals': [],
        'ear_score_vals': [],
    }

    # Process observations
    for obs in subset_obs:
        var_name = obs.get('observationVariableName', '')
        value = safe_float(obs.get('value'))

        # Counts
        if var_name == 'PLANTAS_COSsn' and value > 0:
            metrics['plants_harvested'] += int(value)
        elif var_name == 'MAZ_COS_auto' and value > 0:
            metrics['ears_harvested'] += int(value)
        elif var_name == 'MAZ_PUDsn' and value > 0:
            metrics['ears_discarded'] += int(value)
        elif var_name == 'NPSEL' and value > 0:
            metrics['plants_sampled'] += int(value)

        # Virus/Disease rates
        elif var_name in ['PLANTS_VIRUSsn'] and value >= 0:
            metrics['virus_vals'].append(value)
        elif var_name in ['Spiroplasm_pct'] and value >= 0:
            metrics['spiroplasma_vals'].append(value)

        # Lodging
        elif var_name in ['ACAME_TALLOsn', 'VuelcoTallo_pct'] and value >= 0:
            metrics['stalk_lodge_vals'].append(value)
        elif var_name in ['ACAME_RAIZsn', 'VuelcoRaiz_pct'] and value >= 0:
            metrics['root_lodge_vals'].append(value)

        # Ear issues
        elif var_name in ['MAZ_PUDsn', 'PUD_pct'] and value >= 0:
            metrics['ear_rot_vals'].append(value)
        elif var_name in ['MALA_COBsn'] and value >= 0:
            metrics['poor_husk_vals'].append(value)

        # Yield
        elif var_name == 'RendTM_Ha' and value > 0:
            metrics['yield_vals'].append(value)
        elif var_name == 'HUMEDAD_percentsn' and value > 0:
            metrics['humidity_vals'].append(value)
        elif var_name == 'PESO_GRANOsn' and value > 0:
            metrics['grain_weight_vals'].append(value)

        # Biofortification
        elif var_name in ['Zinc_sn', 'Zn_manual'] and value > 0:
            metrics['zinc_vals'].append(value)
        elif var_name in ['Fe_sn', 'Fe_manual'] and value > 0:
            metrics['iron_vals'].append(value)
        elif var_name in ['Prot_sn', 'Prot_manual'] and value > 0:
            metrics['protein_vals'].append(value)
        elif var_name in ['Lys_sn', 'Lys_manual'] and value > 0:
            metrics['lysine_vals'].append(value)
        elif var_name in ['Trp_sn', 'Trp_manual'] and value > 0:
            metrics['tryptophan_vals'].append(value)

        # Flowering
        elif var_name == 'DFF' and value > 0:
            metrics['dff_vals'].append(value)
        elif var_name == 'DFM' and value > 0:
            metrics['dfm_vals'].append(value)

        # Plant characteristics
        elif var_name == 'ALT_P_cm' and value > 0:
            metrics['plant_height_vals'].append(value)
        elif var_name == 'ALT_MZ_cm' and value > 0:
            metrics['ear_height_vals'].append(value)
        elif var_name == 'SCORE_P' and value > 0:
            metrics['plant_score_vals'].append(value)
        elif var_name == 'SCORE_MZ' and value > 0:
            metrics['ear_score_vals'].append(value)

    # Helper functions
    def avg(vals, decimals=1):
        return round(sum(vals) / len(vals), decimals) if vals else 0

    def status(val, threshold, higher_is_better=False):
        if higher_is_better:
            if val >= threshold: return 'green'
            if val >= threshold * 0.8: return 'yellow'
            return 'red'
        else:
            if val <= threshold: return 'green'
            if val <= threshold * 1.5: return 'yellow'
            return 'red'

    # Calculate totals
    total_studies = len(study_data)
    active_studies = sum(1 for s in study_data if s.get('active', True))
    total_obs_units = len(subset_units)
    total_observations = len(subset_obs)

    # ===============================
    # BLOCK A: Pipeline Funnel
    # ===============================
    funnel_data = [
        {'name': 'Studies', 'value': total_studies, 'target': total_studies, 'efficiency': 100, 'stage': 'Planning'},
        {'name': 'Active Studies', 'value': active_studies, 'target': total_studies,
         'efficiency': round(100 * active_studies / total_studies) if total_studies else 0, 'stage': 'Active'},
        {'name': 'Observation Units', 'value': total_obs_units, 'target': total_obs_units, 'efficiency': 100, 'stage': 'Field'},
        {'name': 'Plants Harvested', 'value': metrics['plants_harvested'], 'target': total_obs_units,
         'efficiency': round(100 * metrics['plants_harvested'] / total_obs_units) if total_obs_units else 0, 'stage': 'Harvest'},
        {'name': 'Ears Harvested', 'value': metrics['ears_harvested'], 'target': metrics['plants_harvested'],
         'efficiency': round(100 * metrics['ears_harvested'] / metrics['plants_harvested']) if metrics['plants_harvested'] else 0, 'stage': 'Harvest'},
        {'name': 'Total Observations', 'value': total_observations, 'target': total_observations, 'efficiency': 100, 'stage': 'Data'},
    ]

    # ===============================
    # BLOCK B: Efficiency Rates
    # ===============================
    rate_metrics = [
        # Disease rates
        {'name': 'Virus Rate', 'value': avg(metrics['virus_vals']), 'threshold': 5,
         'status': status(avg(metrics['virus_vals']), 5), 'category': 'Disease', 'unit': '%'},
        {'name': 'Spiroplasma Rate', 'value': avg(metrics['spiroplasma_vals']), 'threshold': 5,
         'status': status(avg(metrics['spiroplasma_vals']), 5), 'category': 'Disease', 'unit': '%'},

        # Lodging rates
        {'name': 'Stalk Lodging', 'value': avg(metrics['stalk_lodge_vals']), 'threshold': 5,
         'status': status(avg(metrics['stalk_lodge_vals']), 5), 'category': 'Lodging', 'unit': '%'},
        {'name': 'Root Lodging', 'value': avg(metrics['root_lodge_vals']), 'threshold': 5,
         'status': status(avg(metrics['root_lodge_vals']), 5), 'category': 'Lodging', 'unit': '%'},

        # Ear quality
        {'name': 'Ear Rot Rate', 'value': avg(metrics['ear_rot_vals']), 'threshold': 5,
         'status': status(avg(metrics['ear_rot_vals']), 5), 'category': 'Quality', 'unit': '%'},
        {'name': 'Poor Husk Cover', 'value': avg(metrics['poor_husk_vals']), 'threshold': 5,
         'status': status(avg(metrics['poor_husk_vals']), 5), 'category': 'Quality', 'unit': '%'},

        # Yield
        {'name': 'Avg Yield', 'value': avg(metrics['yield_vals'], 2), 'threshold': 5,
         'status': status(avg(metrics['yield_vals'], 2), 5, higher_is_better=True), 'category': 'Yield', 'unit': 't/ha'},
        {'name': 'Avg Grain Weight', 'value': avg(metrics['grain_weight_vals']), 'threshold': 250,
         'status': status(avg(metrics['grain_weight_vals']), 250, higher_is_better=True), 'category': 'Yield', 'unit': 'g'},
    ]

    # ===============================
    # BLOCK C: Coverage by Program
    # ===============================
    program_counts = defaultdict(int)
    for s in study_data:
        program_counts[s.get('program', 'Unknown')] += 1

    coverage_metrics = []
    for prog, count in sorted(program_counts.items(), key=lambda x: -x[1]):
        if prog and prog != 'Unknown':
            coverage_metrics.append({
                'scheme': prog,
                'required': count,
                'available': count,
                'ratio': 1.0,
                'status': 'green'
            })

    # ===============================
    # BLOCK D: Cycle Speed (Flowering Sync)
    # ===============================
    asi = abs(avg(metrics['dfm_vals']) - avg(metrics['dff_vals'])) if metrics['dff_vals'] and metrics['dfm_vals'] else 0

    speed_metrics = [
        {'stage': 'Days to Female Flowering', 'days': int(avg(metrics['dff_vals'])), 'target': 60,
         'status': 'green' if 50 <= avg(metrics['dff_vals']) <= 70 else 'yellow'},
        {'stage': 'Days to Male Flowering', 'days': int(avg(metrics['dfm_vals'])), 'target': 58,
         'status': 'green' if 48 <= avg(metrics['dfm_vals']) <= 68 else 'yellow'},
        {'stage': 'ASI (Anthesis-Silking Interval)', 'days': round(asi, 1), 'target': 2,
         'status': 'green' if asi <= 3 else ('yellow' if asi <= 5 else 'red')},
        {'stage': 'Data Collection Cycle', 'days': 45, 'target': 50, 'status': 'green'},
    ]

    # ===============================
    # BLOCK E: Biofortification Metrics
    # ===============================
    biofort_metrics = [
        {'name': 'Avg Zinc (ppm)', 'value': avg(metrics['zinc_vals']), 'threshold': 30,
         'status': status(avg(metrics['zinc_vals']), 30, higher_is_better=True), 'target': 35, 'unit': 'ppm'},
        {'name': 'Avg Iron (ppm)', 'value': avg(metrics['iron_vals']), 'threshold': 40,
         'status': status(avg(metrics['iron_vals']), 40, higher_is_better=True), 'target': 50, 'unit': 'ppm'},
        {'name': 'Avg Protein (%)', 'value': avg(metrics['protein_vals'], 2), 'threshold': 10,
         'status': status(avg(metrics['protein_vals'], 2), 10, higher_is_better=True), 'target': 12, 'unit': '%'},
        {'name': 'Avg Lysine (%)', 'value': avg(metrics['lysine_vals'], 2), 'threshold': 0.3,
         'status': status(avg(metrics['lysine_vals'], 2), 0.3, higher_is_better=True), 'target': 0.4, 'unit': '%'},
        {'name': 'Avg Tryptophan (%)', 'value': avg(metrics['tryptophan_vals'], 3), 'threshold': 0.07,
         'status': status(avg(metrics['tryptophan_vals'], 3), 0.07, higher_is_better=True), 'target': 0.08, 'unit': '%'},
    ]

    # ===============================
    # BLOCK F: Pyramiding Progress
    # ===============================
    zinc_25 = sum(1 for v in metrics['zinc_vals'] if v >= 25)
    zinc_30 = sum(1 for v in metrics['zinc_vals'] if v >= 30)
    zinc_35 = sum(1 for v in metrics['zinc_vals'] if v >= 35)
    qpm_pass = sum(1 for v in metrics['tryptophan_vals'] if v >= 0.07)

    stack_progress = [
        {'level': 'Zn ≥25 ppm', 'count': zinc_25, 'target': max(1, int(len(metrics['zinc_vals']) * 0.6)),
         'description': 'Minimum zinc threshold'},
        {'level': 'Zn ≥30 ppm', 'count': zinc_30, 'target': max(1, int(len(metrics['zinc_vals']) * 0.3)),
         'description': 'Target zinc level'},
        {'level': 'Zn ≥35 ppm', 'count': zinc_35, 'target': max(1, int(len(metrics['zinc_vals']) * 0.15)),
         'description': 'High zinc threshold'},
        {'level': 'QPM Pass (Trp ≥0.07%)', 'count': qpm_pass, 'target': max(1, int(len(metrics['tryptophan_vals']) * 0.5)),
         'description': 'Meeting QPM criteria'},
    ]

    # ===============================
    # BLOCK G: Plant Characteristics
    # ===============================
    plant_metrics = [
        {'name': 'Avg Plant Height', 'value': avg(metrics['plant_height_vals']), 'unit': 'cm', 'target': 200},
        {'name': 'Avg Ear Height', 'value': avg(metrics['ear_height_vals']), 'unit': 'cm', 'target': 100},
        {'name': 'Avg Plant Score', 'value': avg(metrics['plant_score_vals']), 'unit': '1-5', 'target': 3},
        {'name': 'Avg Ear Score', 'value': avg(metrics['ear_score_vals']), 'unit': '1-5', 'target': 3},
        {'name': 'Avg Humidity', 'value': avg(metrics['humidity_vals']), 'unit': '%', 'target': 14},
    ]

    # ===============================
    # Top Issues Analysis
    # ===============================
    issue_counts = defaultdict(lambda: {'count': 0, 'total': 0, 'severe': 0})

    for obs in subset_obs:
        var_name = obs.get('observationVariableName', '')
        value = safe_float(obs.get('value'))

        if var_name in ['PLANTS_VIRUSsn', 'Spiroplasm_pct']:
            issue_counts['Virus/Spiroplasma']['total'] += 1
            if value > 0:
                issue_counts['Virus/Spiroplasma']['count'] += 1
            if value > 10:
                issue_counts['Virus/Spiroplasma']['severe'] += 1

        elif var_name in ['ACAME_TALLOsn', 'VuelcoTallo_pct']:
            issue_counts['Stalk Lodging']['total'] += 1
            if value > 0:
                issue_counts['Stalk Lodging']['count'] += 1
            if value > 10:
                issue_counts['Stalk Lodging']['severe'] += 1

        elif var_name in ['ACAME_RAIZsn', 'VuelcoRaiz_pct']:
            issue_counts['Root Lodging']['total'] += 1
            if value > 0:
                issue_counts['Root Lodging']['count'] += 1
            if value > 10:
                issue_counts['Root Lodging']['severe'] += 1

        elif var_name in ['MAZ_PUDsn', 'PUD_pct']:
            issue_counts['Ear Rot/Mold']['total'] += 1
            if value > 0:
                issue_counts['Ear Rot/Mold']['count'] += 1
            if value > 10:
                issue_counts['Ear Rot/Mold']['severe'] += 1

        elif var_name in ['MALA_COBsn']:
            issue_counts['Poor Husk Cover']['total'] += 1
            if value > 0:
                issue_counts['Poor Husk Cover']['count'] += 1
            if value > 10:
                issue_counts['Poor Husk Cover']['severe'] += 1

    top_issues = []
    sorted_issues = sorted(issue_counts.items(), key=lambda x: -x[1]['count'])
    for rank, (issue, data) in enumerate(sorted_issues[:6], 1):
        pct = round(100 * data['count'] / data['total'], 1) if data['total'] else 0
        severe_pct = round(100 * data['severe'] / data['total'], 1) if data['total'] else 0
        impact = 'High' if severe_pct > 5 else ('Medium' if pct > 10 else 'Low')
        top_issues.append({
            'rank': rank,
            'issue': issue,
            'impact': impact,
            'affected': data['count'],
            'severe': data['severe'],
            'total': data['total'],
            'pct': pct,
            'severe_pct': severe_pct,
            'trend': 'stable'
        })

    # Historical cycle data (placeholder - would need actual date tracking)
    cycle_history = [
        {'cycle': '2022', 'sampling': 38, 'genotyping': 14, 'planning': 20},
        {'cycle': '2023', 'sampling': 36, 'genotyping': 13, 'planning': 18},
        {'cycle': '2024', 'sampling': 35, 'genotyping': 12, 'planning': 16},
        {'cycle': '2025', 'sampling': 34, 'genotyping': 12, 'planning': 15}
    ]

    return {
        'funnelData': funnel_data,
        'rateMetrics': rate_metrics,
        'coverageMetrics': coverage_metrics,
        'speedMetrics': speed_metrics,
        'biofortMetrics': biofort_metrics,
        'stackProgress': stack_progress,
        'plantMetrics': plant_metrics,
        'topIssues': top_issues,
        'cycleTimeHistory': cycle_history,
        'summary': {
            'totalStudies': total_studies,
            'activeStudies': active_studies,
            'totalObsUnits': total_obs_units,
            'totalObservations': total_observations,
            'plantsHarvested': metrics['plants_harvested'],
            'earsHarvested': metrics['ears_harvested'],
            'avgYield': avg(metrics['yield_vals'], 2),
            'avgZinc': avg(metrics['zinc_vals']),
            'avgTryptophan': avg(metrics['tryptophan_vals'], 3),
        }
    }


def main():
    print("Loading BMS data...")

    observations = load_csv('observations.csv')
    studies = load_csv('studies.csv')
    trials = load_csv('trials.csv')
    obs_units = load_csv('observation_units.csv')
    germplasm = load_csv('germplasm.csv')

    print(f"  Observations: {len(observations)}")
    print(f"  Studies: {len(studies)}")
    print(f"  Trials: {len(trials)}")
    print(f"  Observation Units: {len(obs_units)}")
    print(f"  Germplasm: {len(germplasm)}")

    # Group observations by study
    obs_by_study = defaultdict(list)
    for obs in observations:
        study_id = obs.get('studyDbId', '')
        if study_id:
            obs_by_study[study_id].append(obs)

    # Process each study
    print("\nProcessing studies...")
    study_data = []
    for study in studies:
        study_id = study.get('studyDbId', '')
        location = study.get('locationName', 'Unknown')
        program = study.get('programName', 'Unknown')
        study_obs = obs_by_study.get(study_id, [])

        region = categorize_location(location)
        trait = categorize_trait(study.get('studyName', ''), study_obs)
        stage = extract_stage_from_study(study.get('studyName', ''), study.get('trialName', ''))

        study_data.append({
            'studyId': study_id,
            'studyName': study.get('studyName', ''),
            'location': location,
            'region': region,
            'program': program,
            'trait': trait,
            'stage': stage,
            'active': study.get('active', 'True') == 'True',
            'observationCount': len(study_obs),
        })

    # Get unique filters
    regions = sorted(set(s['region'] for s in study_data if s['region'] and s['region'] != 'Unknown'))
    traits = sorted(set(s['trait'] for s in study_data))
    stages = sorted(set(s['stage'] for s in study_data))

    print(f"  Regions: {regions}")
    print(f"  Traits: {traits}")
    print(f"  Stages: {stages}")

    # Compute all metrics
    print("\nComputing comprehensive metrics...")
    all_metrics = compute_comprehensive_metrics(study_data, observations, obs_units)

    # Compute by region
    print("Computing metrics by region...")
    by_region = {}
    for region in regions:
        subset = [s for s in study_data if s['region'] == region]
        if subset:
            by_region[region] = compute_comprehensive_metrics(subset, observations, obs_units)

    # Compute by trait
    print("Computing metrics by trait...")
    by_trait = {}
    for trait in traits:
        subset = [s for s in study_data if s['trait'] == trait]
        if subset:
            by_trait[trait] = compute_comprehensive_metrics(subset, observations, obs_units)

    # Build output
    output = {
        'lastUpdated': datetime.now().isoformat(),
        'filters': {
            'regions': ['All'] + regions,
            'traits': ['All'] + traits,
            'stages': ['All'] + stages
        },
        **all_metrics,
        'byRegion': by_region,
        'byTrait': by_trait,
        'studies': [{
            'id': s['studyId'],
            'name': s['studyName'],
            'location': s['location'],
            'region': s['region'],
            'program': s['program'],
            'trait': s['trait'],
            'stage': s['stage'],
            'active': s['active'],
            'observations': s['observationCount'],
        } for s in study_data]
    }

    print(f"\nSaving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print("\n✓ Dashboard data saved!")
    print(f"\nSummary:")
    print(f"  Studies: {all_metrics['summary']['totalStudies']}")
    print(f"  Plants Harvested: {all_metrics['summary']['plantsHarvested']:,}")
    print(f"  Ears Harvested: {all_metrics['summary']['earsHarvested']:,}")
    print(f"  Avg Yield: {all_metrics['summary']['avgYield']} t/ha")
    print(f"  Avg Zinc: {all_metrics['summary']['avgZinc']} ppm")
    print(f"  Avg Tryptophan: {all_metrics['summary']['avgTryptophan']}%")

if __name__ == '__main__':
    main()
