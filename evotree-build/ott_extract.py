"""Extract the Embryophyta subtree from OTT taxonomy.tsv -> compact JSON cache.
Keeps: families, genera (with extant species counts), and species names (for lookup)."""
import sys, json, collections
src = sys.argv[1]; out = sys.argv[2]
ROOT = 56610
rows = {}
children = collections.defaultdict(list)
with open(src) as f:
    next(f)
    for line in f:
        p = line.rstrip('\n').split('\t|\t')
        uid = int(p[0]); par = int(p[1]) if p[1] else 0
        rows[uid] = (par, p[2], p[3], p[6].rstrip('\t|'))
        children[par].append(uid)
print('rows', len(rows), file=sys.stderr)
# BFS subtree
sub = []
stack = [ROOT]
while stack:
    u = stack.pop(); sub.append(u); stack.extend(children.get(u, []))
flagc = collections.Counter(); rankc = collections.Counter()
for u in sub:
    for fl in rows[u][3].split(','):
        if fl: flagc[fl] += 1
    rankc[rows[u][2]] += 1
print(flagc.most_common(), file=sys.stderr); print(rankc.most_common(15), file=sys.stderr)
json.dump({str(u): [rows[u][0], rows[u][1], rows[u][2], rows[u][3]] for u in sub}, open(out, 'w'))
