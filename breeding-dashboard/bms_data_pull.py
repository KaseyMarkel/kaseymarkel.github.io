#!/usr/bin/env python3
"""
BMS Full Data Export Script for Semilla Nueva
Pulls all data from BMS via BrAPI and saves to CSV/JSON files
"""

import requests
import json
import csv
import os
from datetime import datetime
from pathlib import Path

# Configuration
BMS_BASE_URL = "https://semillanueva.bmspro.io/bmsapi"
CROP = "maize"  # Crop name required in API path
OUTPUT_DIR = Path("bms_data_export")

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

def get_token(username, password):
    """Authenticate and get access token"""
    response = requests.post(
        f"{BMS_BASE_URL}/brapi/v2/token",
        headers={"Content-Type": "application/json"},
        json={
            "username": username,
            "password": password,
            "grant_type": "password"
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]

def api_get(endpoint, token, params=None):
    """Make authenticated GET request to BrAPI endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BMS_BASE_URL}/{CROP}{endpoint}",
        headers=headers,
        params=params or {}
    )
    response.raise_for_status()
    return response.json()

def paginate_all(endpoint, token, page_size=1000):
    """Fetch all pages of a paginated endpoint"""
    all_data = []
    page = 0

    while True:
        print(f"  Fetching page {page}...")
        result = api_get(endpoint, token, {"page": page, "pageSize": page_size})

        data = result.get("result", {}).get("data", [])
        if not data:
            break

        all_data.extend(data)

        # Check if there are more pages
        total_pages = result.get("metadata", {}).get("pagination", {}).get("totalPages", 1)
        page += 1
        if page >= total_pages:
            break

    return all_data

def save_json(data, filename):
    """Save data to JSON file"""
    filepath = OUTPUT_DIR / f"{filename}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  Saved {len(data)} records to {filepath}")

def save_csv(data, filename):
    """Save data to CSV file"""
    if not data:
        print(f"  No data to save for {filename}")
        return

    filepath = OUTPUT_DIR / f"{filename}.csv"

    # Flatten nested dicts for CSV
    flattened = []
    for item in data:
        flat_item = {}
        for key, value in item.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    flat_item[f"{key}_{k}"] = v
            elif isinstance(value, list):
                flat_item[key] = json.dumps(value)
            else:
                flat_item[key] = value
        flattened.append(flat_item)

    # Get all unique keys
    all_keys = set()
    for item in flattened:
        all_keys.update(item.keys())

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(flattened)

    print(f"  Saved {len(data)} records to {filepath}")

def get_programs(token):
    """Get all breeding programs"""
    print("\n📋 Fetching programs...")
    try:
        data = paginate_all("/brapi/v2/programs", token)
        save_json(data, "programs")
        save_csv(data, "programs")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_trials(token):
    """Get all trials/studies"""
    print("\n🧪 Fetching trials...")
    try:
        data = paginate_all("/brapi/v2/trials", token)
        save_json(data, "trials")
        save_csv(data, "trials")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_studies(token):
    """Get all studies"""
    print("\n📊 Fetching studies...")
    try:
        data = paginate_all("/brapi/v2/studies", token)
        save_json(data, "studies")
        save_csv(data, "studies")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_germplasm(token):
    """Get all germplasm entries"""
    print("\n🌱 Fetching germplasm...")
    try:
        data = paginate_all("/brapi/v2/germplasm", token)
        save_json(data, "germplasm")
        save_csv(data, "germplasm")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_observations(token):
    """Get all observations (phenotypic data)"""
    print("\n📈 Fetching observations...")
    try:
        data = paginate_all("/brapi/v2/observations", token)
        save_json(data, "observations")
        save_csv(data, "observations")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_observation_units(token):
    """Get all observation units (plots/plants)"""
    print("\n🌿 Fetching observation units...")
    try:
        data = paginate_all("/brapi/v2/observationunits", token)
        save_json(data, "observation_units")
        save_csv(data, "observation_units")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_variables(token):
    """Get all observation variables/traits"""
    print("\n📏 Fetching variables/traits...")
    try:
        data = paginate_all("/brapi/v2/variables", token)
        save_json(data, "variables")
        save_csv(data, "variables")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_locations(token):
    """Get all locations"""
    print("\n📍 Fetching locations...")
    try:
        data = paginate_all("/brapi/v2/locations", token)
        save_json(data, "locations")
        save_csv(data, "locations")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_seasons(token):
    """Get all seasons"""
    print("\n📅 Fetching seasons...")
    try:
        data = paginate_all("/brapi/v2/seasons", token)
        save_json(data, "seasons")
        save_csv(data, "seasons")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_pedigree(token, germplasm_list):
    """Get pedigree data for all germplasm"""
    print("\n🌳 Fetching pedigree data...")
    pedigree_data = []

    for i, germ in enumerate(germplasm_list):
        germ_id = germ.get("germplasmDbId")
        if germ_id:
            try:
                result = api_get(f"/brapi/v2/germplasm/{germ_id}/pedigree", token)
                pedigree_data.append(result.get("result", {}))
            except:
                pass

        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(germplasm_list)} germplasm entries...")

    save_json(pedigree_data, "pedigree")
    save_csv(pedigree_data, "pedigree")
    return pedigree_data

def get_crosses(token):
    """Get all crosses"""
    print("\n🔀 Fetching crosses...")
    try:
        data = paginate_all("/brapi/v2/crosses", token)
        save_json(data, "crosses")
        save_csv(data, "crosses")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def get_samples(token):
    """Get all samples"""
    print("\n🧬 Fetching samples...")
    try:
        data = paginate_all("/brapi/v2/samples", token)
        save_json(data, "samples")
        save_csv(data, "samples")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return []

def main():
    print("=" * 60)
    print("BMS Full Data Export - Semilla Nueva")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")

    # Get credentials
    username = input("Enter BMS username: ").strip()
    password = input("Enter BMS password: ").strip()

    print("\n🔐 Authenticating...")
    try:
        token = get_token(username, password)
        print("  ✓ Authentication successful!")
    except Exception as e:
        print(f"  ✗ Authentication failed: {e}")
        return

    # Pull all data
    programs = get_programs(token)
    trials = get_trials(token)
    studies = get_studies(token)
    germplasm = get_germplasm(token)
    observations = get_observations(token)
    observation_units = get_observation_units(token)
    variables = get_variables(token)
    locations = get_locations(token)
    seasons = get_seasons(token)
    crosses = get_crosses(token)
    samples = get_samples(token)

    # Pedigree takes longer - optional
    pull_pedigree = input("\nPull pedigree data? This may take a while (y/n): ").strip().lower()
    if pull_pedigree == 'y' and germplasm:
        get_pedigree(token, germplasm)

    # Summary
    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)
    print(f"Finished at: {datetime.now().isoformat()}")
    print(f"Data saved to: {OUTPUT_DIR.absolute()}")
    print("\nRecord counts:")
    print(f"  Programs:          {len(programs)}")
    print(f"  Trials:            {len(trials)}")
    print(f"  Studies:           {len(studies)}")
    print(f"  Germplasm:         {len(germplasm)}")
    print(f"  Observations:      {len(observations)}")
    print(f"  Observation Units: {len(observation_units)}")
    print(f"  Variables:         {len(variables)}")
    print(f"  Locations:         {len(locations)}")
    print(f"  Seasons:           {len(seasons)}")
    print(f"  Crosses:           {len(crosses)}")
    print(f"  Samples:           {len(samples)}")

if __name__ == "__main__":
    main()
