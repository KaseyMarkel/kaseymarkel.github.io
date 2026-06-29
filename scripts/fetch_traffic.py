#!/usr/bin/env python3
"""Build traffic-data.json for the Site Traffic dashboard -- TOKENLESS.

Uses only GoatCounter's PUBLIC counter endpoints (no API token, no secret):
  https://<code>.goatcounter.com/counter/TOTAL.json   -> all-time totals
  https://<code>.goatcounter.com/counter/<path>.json  -> per-page totals

Visits-over-time is derived by keeping a small running history of the all-time
total (data/traffic-history.json) and diffing day over day. The first chart point
therefore appears on the second day the Action runs.

Outputs traffic-data.json to static/ (durable across Hugo rebuilds) and docs/
(the path the live site actually serves). No geography -- that needs the authed API.

Env (optional):
  GOATCOUNTER_CODE   Site code, e.g. "kaseymarkel" (default below).
"""
import json
import os
import glob
import datetime
import urllib.request
import urllib.error

CODE = os.environ.get("GOATCOUNTER_CODE", "kaseymarkel")
HOST = "https://%s.goatcounter.com" % CODE
PERIOD_DAYS = 30
HISTORY_FILE = "data/traffic-history.json"

today = datetime.date.today().isoformat()


def fetch_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def num(s):
    return int(str(s if s is not None else "0").replace(",", "").strip() or 0)


def counter(path):
    """path is a recorded page path with leading slash, e.g. '/page/flying/'."""
    return fetch_json("%s/counter/%s.json" % (HOST, path))  # '/counter//page/...'


# ---- All-time totals (the one call that always works) ----
total, unique = 0, 0
try:
    d = fetch_json("%s/counter/TOTAL.json" % HOST)
    total, unique = num(d.get("count")), num(d.get("count_unique"))
    print("TOTAL: %d views / %d unique" % (total, unique))
except Exception as e:  # noqa: BLE001
    print("WARN TOTAL: %s" % e)

# ---- Running history -> daily series ----
history = []
if os.path.exists(HISTORY_FILE):
    try:
        history = json.load(open(HISTORY_FILE)).get("snapshots", [])
    except Exception as e:  # noqa: BLE001
        print("WARN reading history: %s" % e)

# upsert today's snapshot (replace if the Action already ran today)
history = [h for h in history if h.get("date") != today]
history.append({"date": today, "total": total, "unique": unique})
history.sort(key=lambda h: h["date"])
history = history[-120:]  # keep ~4 months

# daily delta series: count[i] = total[i] - total[i-1]
daily_map = {}
for i in range(1, len(history)):
    prev, cur = history[i - 1], history[i]
    daily_map[cur["date"]] = max(0, cur["total"] - prev["total"])

daily = []
base = datetime.date.fromisoformat(today)
for i in range(PERIOD_DAYS):
    d = (base - datetime.timedelta(days=PERIOD_DAYS - 1 - i)).isoformat()
    daily.append({"date": d, "count": daily_map.get(d, 0)})

# ---- Top pages (best-effort) from public per-path counters ----
# Derive the path list from the built site so it stays in sync automatically.
paths = set()
for f in glob.glob("docs/**/index.html", recursive=True):
    rel = os.path.relpath(os.path.dirname(f), "docs")
    paths.add("/" if rel == "." else "/" + rel.replace(os.sep, "/") + "/")

top_pages = []
for p in sorted(paths):
    try:
        c = num(counter(p).get("count"))
        if c > 0:
            top_pages.append({"path": p, "count": c})
    except urllib.error.HTTPError:
        pass  # path never visited, or public counter disabled -> skip
    except Exception as e:  # noqa: BLE001
        print("WARN counter %s: %s" % (p, e))
top_pages.sort(key=lambda x: x["count"], reverse=True)
top_pages = top_pages[:10]

out = {
    "updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "period_days": PERIOD_DAYS,
    "total": total,
    "unique": unique,
    "daily": daily,
    "top_pages": top_pages,
}

# persist history
os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
with open(HISTORY_FILE, "w") as f:
    f.write(json.dumps({"snapshots": history}, indent=2))

payload = json.dumps(out, indent=2)
for dest in ("static/traffic-data.json", "docs/traffic-data.json"):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        f.write(payload)
    print("wrote %s" % dest)

print("history_points=%d top_pages=%d days_with_data=%d" % (
    len(history), len(top_pages), sum(1 for x in daily if x["count"])))
