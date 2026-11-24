# Evo Tree Viewer: data build

Builds `static/evotree/data/land-plants.json` (the viewer itself is `static/evotree/`, served at `/evotree/`,
wrapped by `content/page/evo-tree.md`). Nothing here is published; `cache/` is gitignored (~1.3 GB).

## Rebuild after editing the living wall
Only the last step is needed. Highlights come from `data/living_wall.yaml` (the `latin:` field):
```
python3 evotree-build/build_tree.py && hugo --minify
```
"Genus sp." glows at the genus; "Unidentified fern" glows at the fern node (`PLACE_AT`); extra wall
organisms not in the catalog (currently Sphagnum) are in `EXTRA` in build_tree.py.

## Full rebuild from sources (regenerates cache/)
```
# 1. WFO Plant List (accepted species per family/genus): June 2026 DwC backbone from Zenodo
curl -L https://zenodo.org/api/records/20782718/files/_DwC_backbone_R.zip/content -o cache/wfo.zip
unzip cache/wfo.zip -d cache && python3 wfo_extract.py          # -> cache/wfo_counts.json
# 2. OTT taxonomy (higher-taxon names for clade labels)
curl https://files.opentreeoflife.org/ott/ott3.7.2/ott3.7.2.tgz | tar xz -C cache ott3.7.2/taxonomy.tsv
python3 ott_extract.py cache/ott3.7.2/taxonomy.tsv cache/emb_ott.json
# 3. Open Tree TNRS + synthetic tree induced on all genera
python3 fetch_otl.py      # -> cache/tnrs.json, cache/induced_genera.json
python3 build_tree.py
```
Note: fetch_otl.py drops genera pruned from synthesis (337 last run) and retries.
Those genera, and ones TNRS couldn't match, hang from their family's node.

## Method notes
- Topology = Open Tree synthetic tree (genus level). Species within a genus are unresolved; they're drawn as a leaf cluster.
- Counts = WFO accepted species (382,376). Bryophyte/fern counts are WFO's too.
- Clade labels: a taxon labels the deepest node holding ≥97% of its species if ≥85% of that node's species belong to it
  (tolerates a few misplaced genera in the synthetic tree).
- Layout (static/evotree/layout.js): radius ∝ √species (wire-tree / Leonardo's rule); lengths, angles and
  tropisms are artistic. Tunables are in `DEFAULTS`.
