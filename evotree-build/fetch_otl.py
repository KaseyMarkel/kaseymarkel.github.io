"""Map WFO genera + families to OTT ids (TNRS, land-plant context) and fetch the induced synthetic subtree."""
import json, urllib.request, urllib.error, time, os, sys
API = 'https://api.opentreeoflife.org/v3/'
def post(ep, body):
    for a in range(5):
        try:
            req = urllib.request.Request(API+ep, json.dumps(body).encode(), {'content-type':'application/json'})
            return json.load(urllib.request.urlopen(req, timeout=300))
        except Exception as e:
            print('retry', ep, e, file=sys.stderr); time.sleep(3)
    raise SystemExit('failed '+ep)
W = json.load(open('cache/wfo_counts.json'))
names = sorted({g for _, g, _ in W['genera'] if g} | set(W['families']))
cache = 'cache/tnrs.json'
M = json.load(open(cache)) if os.path.exists(cache) else {}
todo = [n for n in names if n not in M]
for i in range(0, len(todo), 250):
    chunk = todo[i:i+250]
    r = post('tnrs/match_names', {'names': chunk, 'context_name': 'Land plants', 'do_approximate_matching': False})
    for res in r['results']:
        ms = [m for m in res['matches'] if not m['is_synonym']] or res['matches']
        if ms: M[res['name']] = [ms[0]['taxon']['ott_id'], ms[0]['taxon']['rank'], ms[0]['is_synonym']]
    for n in chunk: M.setdefault(n, None)
    print(i, len(todo), file=sys.stderr)
    json.dump(M, open(cache, 'w'))
ids = sorted({v[0] for k, v in M.items() if v and k in {g for _, g, _ in W['genera']}})
print('genus ott ids', len(ids), 'unmatched', sum(1 for v in M.values() if not v), file=sys.stderr)
for attempt in range(5):   # drop ids pruned from synthesis, then retry
    req = urllib.request.Request(API + 'tree_of_life/induced_subtree', json.dumps({'ott_ids': ids, 'label_format': 'name_and_id'}).encode(), {'content-type': 'application/json'})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=600)); break
    except urllib.error.HTTPError as e:
        bad = {int(k[3:]) for k in json.loads(e.read()).get('unknown', {})}
        print('dropping', len(bad), 'pruned ids', file=sys.stderr); ids = [i for i in ids if i not in bad]
json.dump(r, open('cache/induced_genera.json', 'w'))
print({k: (v if not isinstance(v, (list, dict, str)) or len(str(v)) < 300 else len(v)) for k, v in r.items()}, file=sys.stderr)
