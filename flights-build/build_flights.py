#!/usr/bin/env python3
"""
Parse a directory of IGC flight logs into a compact flights.json for the
"Captured Territory" web app.

Per flight we compute, at full track resolution:
  - track length (sum of haversine distances between fixes), metres
  - total height climbed (sum of positive, lightly-smoothed altitude deltas), metres
  - duration, max altitude, takeoff point, date

The track geometry itself is downsampled with Ramer-Douglas-Peucker so the
bundle stays small while preserving the shape of thermals (tight 360s) well
enough for the browser-side flood-fill to detect captured areas.

Usage:
  python3 build_flights.py <igc_dir> <out_json>
"""

import sys, os, glob, json, math

EARTH_R = 6371000.0  # mean Earth radius, metres


# ---------------------------------------------------------------- IGC parsing
def parse_igc(path):
    """Return (date_iso, fixes) where fixes = [(lat, lon, baro_m, gps_m), ...]."""
    date_iso = None
    fixes = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("HFDTE"):
                # HFDTEDATE:DDMMYY,nn   or   HFDTEDDMMYY
                digits = "".join(ch for ch in line if ch.isdigit())
                # take the first 6 digits after the prefix as DDMMYY
                tail = line.split(":")[-1] if ":" in line else line[5:]
                d6 = "".join(ch for ch in tail if ch.isdigit())[:6]
                if len(d6) == 6:
                    dd, mm, yy = d6[0:2], d6[2:4], d6[4:6]
                    year = 2000 + int(yy)
                    date_iso = f"{year:04d}-{mm}-{dd}"
            elif line.startswith("B") and len(line) >= 35:
                try:
                    lat_deg = int(line[7:9])
                    lat_min = int(line[9:11]) + int(line[11:14]) / 1000.0
                    lat = lat_deg + lat_min / 60.0
                    if line[14] in ("S", "s"):
                        lat = -lat
                    lon_deg = int(line[15:18])
                    lon_min = int(line[18:20]) + int(line[20:23]) / 1000.0
                    lon = lon_deg + lon_min / 60.0
                    if line[23] in ("W", "w"):
                        lon = -lon
                    baro = int(line[25:30])
                    gps = int(line[30:35])
                except ValueError:
                    continue
                if lat == 0 and lon == 0:
                    continue
                fixes.append((lat, lon, baro, gps))
    return date_iso, fixes


# ---------------------------------------------------------------- geometry
def haversine(a_lat, a_lon, b_lat, b_lon):
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dlmb = math.radians(b_lon - a_lon)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_R * math.asin(min(1.0, math.sqrt(h)))


def track_length(fixes):
    total = 0.0
    for i in range(1, len(fixes)):
        total += haversine(fixes[i - 1][0], fixes[i - 1][1], fixes[i][0], fixes[i][1])
    return total


def smooth(vals, win=5):
    if len(vals) < win:
        return vals[:]
    half = win // 2
    out = []
    for i in range(len(vals)):
        lo, hi = max(0, i - half), min(len(vals), i + half + 1)
        out.append(sum(vals[lo:hi]) / (hi - lo))
    return out


def total_climb(fixes):
    """Sum of positive, smoothed altitude gains. Prefer baro; fall back to GPS."""
    if len(fixes) < 2:
        return 0.0
    baro = [f[2] for f in fixes]
    gps = [f[3] for f in fixes]
    # baro of ~0 throughout means no pressure sensor -> use GPS
    use = baro if (sorted(baro)[len(baro) // 2] > 30) else gps
    use = smooth(use, 5)
    gain = 0.0
    deadband = 0.4  # metres; ignore sub-noise wiggle
    for i in range(1, len(use)):
        d = use[i] - use[i - 1]
        if d > deadband:
            gain += d
    return gain


def rdp(points, eps):
    """Iterative Ramer-Douglas-Peucker on (lat, lon). eps in degrees."""
    if len(points) < 3:
        return points[:]
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        lo, hi = stack.pop()
        if hi <= lo + 1:
            continue
        ax, ay = points[lo]
        bx, by = points[hi]
        dx, dy = bx - ax, by - ay
        denom = math.hypot(dx, dy)
        dmax, idx = -1.0, -1
        for i in range(lo + 1, hi):
            px, py = points[i]
            if denom == 0:
                dist = math.hypot(px - ax, py - ay)
            else:
                dist = abs(dy * (px - ax) - dx * (py - ay)) / denom
            if dist > dmax:
                dmax, idx = dist, i
        if dmax > eps and idx != -1:
            keep[idx] = True
            stack.append((lo, idx))
            stack.append((idx, hi))
    return [points[i] for i in range(len(points)) if keep[i]]


# ---------------------------------------------------------------- main
def main():
    igc_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        "~/Downloads/KM_2026_flights")
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(__file__), "..", "static", "flights", "flights.json")

    paths = sorted(
        glob.glob(os.path.join(igc_dir, "*.IGC"))
        + glob.glob(os.path.join(igc_dir, "*.igc"))
    )
    flights = []
    tot_climb = tot_len = tot_air = 0.0
    eps = 3.0 / 111320.0  # ~3 m tolerance, in degrees

    for p in paths:
        date_iso, fixes = parse_igc(p)
        if len(fixes) < 10:
            continue
        length = track_length(fixes)
        climb = total_climb(fixes)
        alts = [f[2] if f[2] > 30 else f[3] for f in fixes]
        max_alt = max(alts) if alts else 0
        # duration: B-records are ~1/sec; estimate from fix count is unreliable,
        # so we approximate airtime as (n_fixes) seconds only if cadence ~1Hz.
        # We instead leave duration unknown-ish; the page shows count + length.
        latlon = [(f[0], f[1]) for f in fixes]
        simplified = rdp(latlon, eps)
        # round to 5 dp (~1.1 m) to shrink JSON
        pts = [[round(la, 5), round(lo, 5)] for la, lo in simplified]
        name = os.path.splitext(os.path.basename(p))[0]
        flights.append({
            "id": len(flights),
            "date": date_iso or "",
            "name": name,
            "lengthM": round(length, 1),
            "climbM": round(climb, 1),
            "maxAltM": round(max_alt, 1),
            "nFix": len(fixes),
            "takeoff": [round(latlon[0][0], 5), round(latlon[0][1], 5)],
            "pts": pts,
        })
        tot_climb += climb
        tot_len += length

    flights.sort(key=lambda f: f["date"])
    for i, f in enumerate(flights):
        f["id"] = i

    out = {
        "earthAreaKm2": 510072000.0,
        "totals": {
            "flights": len(flights),
            "climbM": round(tot_climb, 1),
            "lengthM": round(tot_len, 1),
        },
        "flights": flights,
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(out, fh, separators=(",", ":"))
    size = os.path.getsize(out_path)
    print(f"Wrote {len(flights)} flights -> {out_path} ({size/1024/1024:.2f} MB)")
    print(f"  total climb: {tot_climb/1000:.1f} km   total track: {tot_len/1000:.1f} km")


if __name__ == "__main__":
    main()
