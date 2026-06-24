// Node harness to validate the capture pipeline against the real flights.json.
// d3-contour is resolved by pipeline.js via require(); expose it on global.
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// emulate the browser global `d3` (CDN) so the contour path is exercised
global.d3 = { contours: require('d3-contour').contours };
const CT = require(path.join(__dirname, '..', 'static', 'flights', 'pipeline.js'));
const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'static', 'flights', 'flights.json')));
const flights = data.flights.map((f, i) => ({ ...f, id: i }));

console.log('flights:', flights.length);
CT.assignColors(flights);
const colors = new Set(flights.map(f => f.color));
console.log('distinct colours used:', colors.size, '/', flights.length);

const sites = CT.unionFindSites(flights);
console.log('sites (clusters):', sites.length, '| sizes:', sites.map(s => s.length).sort((a,b)=>b-a).slice(0,12).join(','));

const t0 = Date.now();
const cap = await CT.computeCapture(flights);
const ms = Date.now() - t0;
const km2 = cap.areaM2 / 1e6;
console.log('capture compute time:', ms, 'ms');
console.log('captured area:', cap.areaM2.toFixed(0), 'm²  =', km2.toFixed(4), 'km²');
console.log('% of Earth surface:', (km2 / CT.EARTH_AREA_KM2 * 100).toExponential(2), '%');
console.log('landmark:', CT.landmarkCompare(km2));
console.log('multipolygon parts:', cap.feature.geometry.coordinates.length);

// sanity: totals
const climb = flights.reduce((s,f)=>s+f.climbM,0), dist = flights.reduce((s,f)=>s+f.lengthM,0);
console.log('total climb:', (climb/1000).toFixed(1), 'km  | Everests:', (climb/CT.EVEREST_M).toFixed(1));
console.log('total track:', (dist/1000).toFixed(1), 'km  | around Earth:', (dist/CT.EARTH_CIRC_M*100).toFixed(1), '%');

// adjacency check: do any spatially-overlapping flights share an identical colour?
const boxes = flights.map(f => CT.bbox(f.pts));
const pad = 1500/111000;
let clash = 0;
for (let i=0;i<flights.length;i++) for (let j=i+1;j<flights.length;j++){
  const a=boxes[i], b=boxes[j];
  const near = !(a.minLat-pad>b.maxLat||a.maxLat+pad<b.minLat||a.minLon-pad>b.maxLon||a.maxLon+pad<b.minLon);
  if (near && flights[i].color===flights[j].color) clash++;
}
console.log('adjacent same-colour clashes:', clash);
