// Enrich flights.json with PRECOMPUTED demo data so the demo renders instantly:
//   - each flight gets its baked `color`
//   - top-level `capture` = { areaM2, feature } (the captured-territory MultiPolygon)
// Uploads still compute capture live in the browser; only the demo is baked.
//
// Usage: node bake_demo.mjs            (writes back to ../static/flights/flights.json)
//        node bake_demo.mjs --dry      (report sizes, don't write)
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dry = process.argv.includes('--dry');

global.d3 = { contours: require('d3-contour').contours };
const CT = require(path.join(__dirname, '..', 'static', 'flights', 'pipeline.js'));

const jsonPath = path.join(__dirname, '..', 'static', 'flights', 'flights.json');
const data = JSON.parse(fs.readFileSync(jsonPath));
const flights = data.flights.map((f, i) => ({ ...f, id: i }));

// 1) bake colours (deterministic; fast)
CT.assignColors(flights);
flights.forEach((f, i) => { data.flights[i].color = f.color; });

// 2) compute captured territory
const t0 = Date.now();
const cap = await CT.computeCapture(flights);
console.log(`computed capture in ${Date.now() - t0} ms — ${cap.areaM2.toFixed(0)} m²`);

// 3) shrink polygons: round coords to 5 dp (~1 m) and RDP-simplify rings just under
//    the grid resolution so the staircase smooths without losing tiny thermal discs.
const epsArg = process.argv.find(a => a.startsWith('--eps='));
const EPS = epsArg ? +epsArg.slice(6) : 1.5e-5; // ~1.6 m; grid cells ~12 m, shape preserved
let ptsBefore = 0, ptsAfter = 0;
const polys = cap.feature.geometry.coordinates.map(poly =>
  poly.map(ring => {
    ptsBefore += ring.length;
    let r = ring;
    if (ring.length > 6) r = CT.rdp(ring, EPS);
    if (r.length < 4) r = ring;                       // keep degenerate-safe rings whole
    ptsAfter += r.length;
    return r.map(([x, y]) => [+x.toFixed(5), +y.toFixed(5)]);
  })
).filter(poly => poly[0] && poly[0].length >= 4);

data.capture = {
  areaM2: Math.round(cap.areaM2),
  feature: { type: 'Feature', geometry: { type: 'MultiPolygon', coordinates: polys } }
};

const out = JSON.stringify(data);
console.log(`polygons: ${polys.length} | ring points ${ptsBefore} -> ${ptsAfter} (${(100 * ptsAfter / ptsBefore).toFixed(0)}%)`);
console.log(`flights.json size: ${(out.length / 1024 / 1024).toFixed(2)} MB`);
if (dry) { console.log('(dry run — not written)'); }
else { fs.writeFileSync(jsonPath, out); console.log('wrote', jsonPath); }
