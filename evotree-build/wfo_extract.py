"""Stream WFO classification.csv -> accepted species counts per family & genus, plus majorGroup."""
import csv, sys, json, collections
csv.field_size_limit(10**8)
fam = collections.Counter(); gen = collections.Counter(); famgroup = {}; genfam = {}
status = collections.Counter(); groups = collections.Counter()
with open('cache/classification.csv', newline='', encoding='utf-8', errors='replace') as f:
    r = csv.DictReader(f, delimiter='\t')
    for row in r:
        if row['taxonRank'] != 'species': continue
        status[row['taxonomicStatus']] += 1
        if row['taxonomicStatus'] != 'Accepted': continue
        fa, ge = row['family'], row['genus']
        fam[fa] += 1; gen[(fa, ge)] += 1; famgroup[fa] = row['majorGroup']; groups[row['majorGroup']] += 1
print(status, groups, 'species', sum(fam.values()), 'families', len(fam), 'genera', len(gen), file=sys.stderr)
json.dump({'families': {k: {'n': v, 'group': famgroup[k]} for k, v in fam.items()},
           'genera': [[fa, ge, n] for (fa, ge), n in gen.items()]}, open('cache/wfo_counts.json', 'w'))
for k, v in fam.most_common(8): print(k, v, file=sys.stderr)
