// Evo Tree Viewer — species-list parsing, name resolution, share-link encoding.
// Pure functions (fetch is the only side effect), so they work for any dataset.

const BINOMIAL = /\b([A-Z][a-zë-]{2,})(?:\s+(?:×|x)\s*)?(?:\s+([a-z][a-z-]{2,}|sp\.?|spp\.?))?\b/;
const NOT_GENUS = new Set(['The', 'This', 'And', 'For', 'With', 'Common', 'Scientific', 'Name', 'Species', 'Family', 'Unknown', 'New']);

function splitCSVLine(line, sep) {
  const out = []; let cur = '', q = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (q) { if (ch === '"') { if (line[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += ch; }
    else if (ch === '"') q = true;
    else if (ch === sep) { out.push(cur); cur = ''; }
    else cur += ch;
  }
  out.push(cur); return out.map((s) => s.trim());
}

/** Text → [{raw, sci?, common?}]. Handles plain lists, "Common (Genus species)", and CSV/TSV with a scientific-name column. */
export function parseList(text) {
  const lines = text.replace(/\r/g, '').split('\n').map((l) => l.trim()).filter(Boolean);
  if (!lines.length) return [];
  // table with a header?
  const sep = lines[0].includes('\t') ? '\t' : lines[0].includes(',') ? ',' : null;
  if (sep && lines.length > 1) {
    const head = splitCSVLine(lines[0], sep).map((h) => h.toLowerCase());
    const find = (re) => head.findIndex((h) => re.test(h));
    let sciCol = find(/scientific/);
    if (sciCol < 0) sciCol = find(/latin|binomial/);
    if (sciCol < 0) sciCol = find(/^(taxon|species|taxon name|species name|name)$/);
    const comCol = head.findIndex((h) => /common|english|vernacular/.test(h));
    if (sciCol >= 0 || comCol >= 0) {
      const out = [];
      for (const l of lines.slice(1)) {
        const c = splitCSVLine(l, sep);
        const sci = sciCol >= 0 ? c[sciCol] : '';
        const common = comCol >= 0 ? c[comCol] : '';
        if (!sci && !common) continue;
        out.push({ raw: common && sci ? `${common} (${sci})` : sci || common, sci: cleanSci(sci), common });
      }
      return dedupe(out);
    }
  }
  const out = [];
  for (let l of lines) {
    l = l.replace(/^\s*(?:[-*•·]|\d+[.)])\s*/, '').trim();
    if (!l || l.startsWith('#')) continue;
    // prefer a real binomial (Genus epithet) anywhere in the line; else a lone capitalised word ("Begonia", "Orchidaceae")
    const all = [...l.matchAll(new RegExp(BINOMIAL.source, 'g'))].filter((x) => !NOT_GENUS.has(x[1]));
    const m = all.find((x) => x[2] && !/^(sp|spp)\.?$/.test(x[2]) && x[2] !== x[2].toUpperCase()) || all.find((x) => x[2]) ||
      (/^[A-Z][a-zë-]+\.?$/.test(l) ? all[0] : null) || all.find((x) => new RegExp('\\(' + x[1] + '\\)').test(l));
    let sci = '', common = '';
    if (m) {
      sci = cleanSci(m[0]);
      common = l.replace(m[0], '').replace(/[()[\]{}"']/g, ' ').replace(/[,;:–—-]\s*$/, '').replace(/\s+/g, ' ').trim();
      if (common && /^[A-Z]?[a-z]*\.?$/.test(common) && common.length < 4) common = '';   // leftover "L." etc.
    } else common = l;
    out.push({ raw: l, sci, common });
  }
  return dedupe(out);
}
function cleanSci(s) {
  if (!s) return '';
  s = s.replace(/\s+(?:×|x)\s+/, ' ').replace(/['"‘’].*$/, '').replace(/\s+(var|subsp|ssp|f)\..*$/, '').trim();
  const p = s.split(/\s+/);
  if (p.length >= 2 && /^(sp|spp)\.?$/.test(p[1])) return p[0];
  return p.slice(0, 2).join(' ');
}
function dedupe(arr) { const seen = new Set(); return arr.filter((e) => { const k = (e.sci || e.common).toLowerCase(); if (seen.has(k)) return false; seen.add(k); return true; }); }

/** Place each entry on the tree: local genus/clade match first, then GBIF (synonyms, misspellings, common names). */
export async function resolveEntries(entries, { genusIndex, cladeIndex, kingdom, bFam, onProgress }) {
  const out = entries.map((e) => ({ raw: e.raw, label: e.common || e.raw, sci: e.sci, entry: e }));
  const local = (r, name) => {
    if (!name) return false;
    const k = name.toLowerCase();
    const g = k.split(' ')[0];
    if (genusIndex.has(g)) { r.at = genusIndex.get(g); r.place = name.split(' ')[0]; r.family = bFam(r.at); return true; }
    if (cladeIndex.has(k)) { r.at = cladeIndex.get(k); r.place = name; return true; }
    return false;
  };
  const todo = [];
  for (const r of out) {
    if (local(r, r.sci)) continue;
    const w = (r.raw.match(/^[A-Z][a-zë-]+/) || [])[0];       // "Petunia 'Firefly'", "Begonia maculata 'Wightii'"
    if (w && genusIndex.has(w.toLowerCase()) && local(r, w)) { if (!r.sci) r.sci = w; continue; }
    todo.push(r);
  }
  let done = 0;
  const gbif = async (r) => {
    try {
      let hit = null, viaCommon = false;
      if (r.sci) {
        const u = `https://api.gbif.org/v1/species/match?name=${encodeURIComponent(r.sci)}&kingdom=${kingdom}&strict=false`;
        const j = await (await fetch(u)).json();
        const first = r.sci.split(' ')[0].toLowerCase();
        const okType = j && (j.matchType === 'EXACT' || (j.matchType === 'FUZZY' && j.confidence >= 85) ||
          (j.matchType === 'HIGHERRANK' && j.genus && j.genus.toLowerCase() === first));
        if (okType && (!j.kingdom || j.kingdom === kingdom)) hit = j;
      }
      if (!hit) {
        const q = r.entry.common || r.raw;
        const u = `https://api.gbif.org/v1/species/search?q=${encodeURIComponent(q)}&qField=VERNACULAR&datasetKey=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c&status=ACCEPTED&limit=20`;
        const j = await (await fetch(u)).json();
        const rs = (j.results || []).filter((x) => x.kingdom === kingdom && x.genus);
        const ql = q.toLowerCase();
        hit = rs.find((x) => (x.vernacularNames || []).some((v) => v.vernacularName && v.vernacularName.toLowerCase() === ql)) || rs.find((x) => x.rank === 'SPECIES') || rs[0] || null;
        if (hit) { hit.canonicalName = hit.canonicalName || hit.scientificName; viaCommon = true; }
      }
      if (hit) {
        const sci = hit.species || hit.canonicalName || '';
        const tryNames = [sci, hit.genus, hit.family, hit.order, hit.class].filter(Boolean);
        for (const nm of tryNames) {
          if (local(r, nm)) {
            if (!r.sci || r.sci.toLowerCase() !== sci.toLowerCase()) {
              r.note = r.sci && !viaCommon ? `matched as ${sci || nm}` : `= ${sci || nm}`;
              r.sci = sci || nm;
            }
            if (nm !== sci && nm !== hit.genus) r.note = `${r.note ? r.note + '; ' : ''}placed at ${nm}`;
            if (!r.label) r.label = r.sci;
            break;
          }
        }
      }
    } catch { /* offline / blocked: leave unmatched */ }
    done++; onProgress && onProgress(done, todo.length);
  };
  // small worker pool to be polite to GBIF
  const queue = [...todo];
  await Promise.all(Array.from({ length: Math.min(6, queue.length) }, async () => { while (queue.length) await gbif(queue.shift()); }));
  for (const r of out) if (!r.label) r.label = r.sci || r.raw;
  return out;
}

// ---- share links: deflate-raw + base64url, plain base64url as fallback
const b64u = (bytes) => { let b = ''; for (let i = 0; i < bytes.length; i++) b += String.fromCharCode(bytes[i]); return btoa(b); };
const b64url = (bytes) => b64u(bytes).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64u = (s) => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), (c) => c.charCodeAt(0));
async function pipe(bytes, stream) { return new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(stream)).arrayBuffer()); }
export async function encodeList(list) {
  const text = [list.title || ''].concat(list.items.map((it) => [it.label, it.sci || '', it.place || ''].join('\t'))).join('\n');
  const raw = new TextEncoder().encode(text);
  if (typeof CompressionStream !== 'undefined') { try { return 'z' + b64url(await pipe(raw, new CompressionStream('deflate-raw'))); } catch { /* fall through */ } }
  return 'p' + b64url(raw);
}
export async function decodeList(s) {
  try {
    let bytes = unb64u(s.slice(1));
    if (s[0] === 'z') bytes = await pipe(bytes, new DecompressionStream('deflate-raw'));
    const lines = new TextDecoder().decode(bytes).split('\n');
    return { title: lines[0], items: lines.slice(1).filter(Boolean).map((l) => { const [label, sci, place] = l.split('\t'); return { label, sci, place }; }) };
  } catch { return null; }
}
