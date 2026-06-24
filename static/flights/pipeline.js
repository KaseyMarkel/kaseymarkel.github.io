/* Captured Territory — pure data pipeline (no DOM, no Leaflet).
 * Shared by the browser app (window.CT) and the Node test harness
 * (module.exports). Contour extraction uses d3-contour, resolved from the
 * global `d3` in the browser or `require('d3-contour')` in Node. */
(function (root, factory) {
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.CT = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const EARTH_AREA_KM2 = 510072000;
  const EARTH_CIRC_M = 40075017;
  const EVEREST_M = 8849;

  const TARGET_CELL_M = 12;   // desired grid cell size
  const MAX_DIM = 2200;       // cap grid dimension per site (perf)
  const SITE_PAD_M = 160;     // pad site bbox so border cells are truly "outside"
  const CLUSTER_PAD_M = 1500; // flights within this of each other share a site

  function getContours() {
    if (typeof d3 !== 'undefined' && d3.contours) return d3.contours;
    if (typeof require !== 'undefined') { try { return require('d3-contour').contours; } catch (e) {} }
    return null;
  }
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  /* ----------------------------------------------------------- geometry */
  function haversine(aLat, aLon, bLat, bLon) {
    const R = 6371000, r = Math.PI / 180;
    const p1 = aLat * r, p2 = bLat * r;
    const dp = (bLat - aLat) * r, dl = (bLon - aLon) * r;
    const h = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
    return 2 * R * Math.asin(Math.min(1, Math.sqrt(h)));
  }
  function rdp(points, eps) {
    if (points.length < 3) return points.slice();
    const keep = new Uint8Array(points.length); keep[0] = keep[points.length - 1] = 1;
    const stack = [[0, points.length - 1]];
    while (stack.length) {
      const [lo, hi] = stack.pop();
      if (hi <= lo + 1) continue;
      const [ax, ay] = points[lo], [bx, by] = points[hi];
      const dx = bx - ax, dy = by - ay, den = Math.hypot(dx, dy);
      let dmax = -1, idx = -1;
      for (let i = lo + 1; i < hi; i++) {
        const [px, py] = points[i];
        const dist = den === 0 ? Math.hypot(px - ax, py - ay)
          : Math.abs(dy * (px - ax) - dx * (py - ay)) / den;
        if (dist > dmax) { dmax = dist; idx = i; }
      }
      if (dmax > eps && idx !== -1) { keep[idx] = 1; stack.push([lo, idx], [idx, hi]); }
    }
    const out = [];
    for (let i = 0; i < points.length; i++) if (keep[i]) out.push(points[i]);
    return out;
  }
  function bbox(pts) {
    let a = 90, b = -90, c = 180, d = -180;
    for (const [la, lo] of pts) { if (la < a) a = la; if (la > b) b = la; if (lo < c) c = lo; if (lo > d) d = lo; }
    return { minLat: a, maxLat: b, minLon: c, maxLon: d };
  }
  function boxesNear(x, y, padDeg) {
    return !(x.minLat - padDeg > y.maxLat || x.maxLat + padDeg < y.minLat ||
             x.minLon - padDeg > y.maxLon || x.maxLon + padDeg < y.minLon);
  }

  /* ----------------------------------------------------------- IGC parse */
  function parseIGC(text, fallbackName) {
    let date = '';
    const fixes = [];
    const lines = text.split(/\r?\n/);
    for (const line of lines) {
      if (line.startsWith('HFDTE')) {
        const tail = line.includes(':') ? line.split(':').pop() : line.slice(5);
        const d6 = (tail.match(/\d/g) || []).join('').slice(0, 6);
        if (d6.length === 6) date = `20${d6.slice(4, 6)}-${d6.slice(2, 4)}-${d6.slice(0, 2)}`;
      } else if (line[0] === 'B' && line.length >= 35) {
        const latD = +line.slice(7, 9), latM = +line.slice(9, 11) + +line.slice(11, 14) / 1000;
        let lat = latD + latM / 60; if (line[14] === 'S' || line[14] === 's') lat = -lat;
        const lonD = +line.slice(15, 18), lonM = +line.slice(18, 20) + +line.slice(20, 23) / 1000;
        let lon = lonD + lonM / 60; if (line[23] === 'W' || line[23] === 'w') lon = -lon;
        const baro = +line.slice(25, 30), gps = +line.slice(30, 35);
        if (!isFinite(lat) || !isFinite(lon) || (lat === 0 && lon === 0)) continue;
        fixes.push([lat, lon, baro, gps]);
      }
    }
    if (fixes.length < 10) return null;
    return statsFromFixes(fixes, date, fallbackName);
  }
  function statsFromFixes(fixes, date, name) {
    let length = 0;
    for (let i = 1; i < fixes.length; i++)
      length += haversine(fixes[i - 1][0], fixes[i - 1][1], fixes[i][0], fixes[i][1]);
    const baros = fixes.map(f => f[2]).sort((a, b) => a - b);
    const useBaro = baros[baros.length >> 1] > 30;
    const alt = fixes.map(f => useBaro ? f[2] : f[3]);
    const sm = alt.map((_, i) => {
      const lo = Math.max(0, i - 2), hi = Math.min(alt.length, i + 3); let s = 0;
      for (let k = lo; k < hi; k++) s += alt[k];
      return s / (hi - lo);
    });
    let climb = 0;
    for (let i = 1; i < sm.length; i++) { const d = sm[i] - sm[i - 1]; if (d > 0.4) climb += d; }
    const maxAlt = Math.max.apply(null, alt);
    const latlon = fixes.map(f => [f[0], f[1]]);
    const pts = rdp(latlon, 3 / 111320).map(p => [+p[0].toFixed(5), +p[1].toFixed(5)]);
    return {
      date, name, lengthM: +length.toFixed(1), climbM: +climb.toFixed(1),
      maxAltM: +maxAlt.toFixed(1), takeoff: [+latlon[0][0].toFixed(5), +latlon[0][1].toFixed(5)], pts
    };
  }

  /* ----------------------------------------------------------- colour */
  function hsl(h, s, l) {
    s /= 100; l /= 100;
    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
    const to = x => Math.round(255 * x).toString(16).padStart(2, '0');
    return '#' + to(f(0)) + to(f(8)) + to(f(4));
  }
  function buildPalette(n) {
    const bands = [[68, 50], [60, 40], [74, 60], [55, 46]];
    const P = [], count = Math.max(96, n + 12);
    for (let i = 0; i < count; i++) {
      const h = (i * 137.508) % 360, [s, l] = bands[i % bands.length];
      P.push({ hex: hsl(h, s, l), h, l });
    }
    return P;
  }
  function assignColors(fl) {
    const pal = buildPalette(fl.length);
    const boxes = fl.map(f => bbox(f.pts));
    const padDeg = CLUSTER_PAD_M / 111000;
    const adj = fl.map(() => []);
    for (let i = 0; i < fl.length; i++)
      for (let j = i + 1; j < fl.length; j++)
        if (boxesNear(boxes[i], boxes[j], padDeg)) { adj[i].push(j); adj[j].push(i); }
    const order = [...fl.keys()].sort((a, b) => adj[b].length - adj[a].length);
    const chosen = new Array(fl.length).fill(-1);
    const usage = new Array(pal.length).fill(0);
    const hueDist = (p, q) => { const d = Math.abs(p.h - q.h) % 360; return Math.min(d, 360 - d); };
    for (const i of order) {
      const nb = adj[i].map(j => chosen[j]).filter(c => c >= 0).map(c => pal[c]);
      let best = -1, bestScore = -Infinity;
      for (let p = 0; p < pal.length; p++) {
        let minD = 180;
        for (const c of nb) minD = Math.min(minD, hueDist(pal[p], c) + Math.abs(pal[p].l - c.l) * 60);
        const score = minD - usage[p] * 25;
        if (score > bestScore) { bestScore = score; best = p; }
      }
      chosen[i] = best; usage[best]++;
    }
    fl.forEach((f, i) => f.color = pal[chosen[i]].hex);
  }

  /* ----------------------------------------------------------- capture */
  function unionFindSites(fl) {
    const boxes = fl.map(f => bbox(f.pts));
    const parent = [...fl.keys()];
    const find = x => { while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; };
    const padDeg = CLUSTER_PAD_M / 111000;
    for (let i = 0; i < fl.length; i++)
      for (let j = i + 1; j < fl.length; j++)
        if (boxesNear(boxes[i], boxes[j], padDeg)) parent[find(i)] = find(j);
    const groups = new Map();
    for (let i = 0; i < fl.length; i++) {
      const r = find(i);
      if (!groups.has(r)) groups.set(r, []);
      groups.get(r).push(i);
    }
    return [...groups.values()];
  }

  function captureSite(members, fl) {
    let minLat = 90, maxLat = -90, minLon = 180, maxLon = -180;
    for (const m of members) for (const [la, lo] of fl[m].pts) {
      if (la < minLat) minLat = la; if (la > maxLat) maxLat = la;
      if (lo < minLon) minLon = lo; if (lo > maxLon) maxLon = lo;
    }
    const centerLat = (minLat + maxLat) / 2;
    const mPerLat = 110540, mPerLon = 111320 * Math.cos(centerLat * Math.PI / 180);
    minLat -= SITE_PAD_M / mPerLat; maxLat += SITE_PAD_M / mPerLat;
    minLon -= SITE_PAD_M / mPerLon; maxLon += SITE_PAD_M / mPerLon;

    const widthM = (maxLon - minLon) * mPerLon, heightM = (maxLat - minLat) * mPerLat;
    if (widthM < 30 || heightM < 30) return null;
    const Nx = Math.min(MAX_DIM, Math.max(3, Math.round(widthM / TARGET_CELL_M)));
    const Ny = Math.min(MAX_DIM, Math.max(3, Math.round(heightM / TARGET_CELL_M)));
    const cellW = widthM / Nx, cellH = heightM / Ny;

    const mask = new Uint8Array(Nx * Ny);
    const col = lon => Math.max(0, Math.min(Nx - 1, Math.floor((lon - minLon) / (maxLon - minLon) * Nx)));
    const row = lat => Math.max(0, Math.min(Ny - 1, Math.floor((lat - minLat) / (maxLat - minLat) * Ny)));

    const plot = (x0, y0, x1, y1) => {
      let dx = Math.abs(x1 - x0), dy = Math.abs(y1 - y0), x = x0, y = y0, n = 1 + dx + dy;
      const xi = x1 > x0 ? 1 : -1, yi = y1 > y0 ? 1 : -1;
      let err = dx - dy; dx *= 2; dy *= 2;
      for (; n > 0; n--) { mask[y * Nx + x] = 1; if (err > 0) { x += xi; err -= dy; } else { y += yi; err += dx; } }
    };
    for (const m of members) {
      const p = fl[m].pts;
      for (let i = 1; i < p.length; i++)
        plot(col(p[i - 1][1]), row(p[i - 1][0]), col(p[i][1]), row(p[i][0]));
    }

    const stack = new Int32Array(Nx * Ny); let sp = 0;
    const push = idx => { if (mask[idx] === 0) { mask[idx] = 2; stack[sp++] = idx; } };
    for (let x = 0; x < Nx; x++) { push(x); push((Ny - 1) * Nx + x); }
    for (let y = 0; y < Ny; y++) { push(y * Nx); push(y * Nx + Nx - 1); }
    while (sp > 0) {
      const idx = stack[--sp], x = idx % Nx, y = (idx - x) / Nx;
      if (x > 0) push(idx - 1);
      if (x < Nx - 1) push(idx + 1);
      if (y > 0) push(idx - Nx);
      if (y < Ny - 1) push(idx + Nx);
    }

    const vals = new Float64Array(Nx * Ny); let captured = 0;
    for (let i = 0; i < mask.length; i++) if (mask[i] === 0) { vals[i] = 1; captured++; }
    const areaM2 = captured * cellW * cellH;
    if (captured === 0) return { areaM2: 0, polys: [], Nx, Ny };

    const polys = [];
    const contours = getContours();
    if (contours) {
      const geo = contours().size([Nx, Ny]).thresholds([0.5])(vals)[0];
      const toLL = ([x, y]) => [minLon + (x / Nx) * (maxLon - minLon), minLat + (y / Ny) * (maxLat - minLat)];
      for (const poly of geo.coordinates) polys.push(poly.map(ring => ring.map(toLL)));
    }
    return { areaM2, polys, Nx, Ny };
  }

  async function computeCapture(fl, onProgress) {
    const sites = unionFindSites(fl);
    let totalArea = 0; const allPolys = [];
    for (let s = 0; s < sites.length; s++) {
      const res = captureSite(sites[s], fl);
      if (res) { totalArea += res.areaM2; for (const p of res.polys) allPolys.push(p); }
      if (onProgress) onProgress(s + 1, sites.length);
      await sleep(0);
    }
    return {
      areaM2: totalArea, nSites: sites.length,
      feature: { type: 'Feature', geometry: { type: 'MultiPolygon', coordinates: allPolys } }
    };
  }

  /* ----------------------------------------------------------- format */
  function fmtKm(m) {
    const km = m / 1000;
    if (km >= 100) return Math.round(km).toLocaleString() + ' km';
    if (km >= 10) return km.toFixed(1) + ' km';
    return km.toFixed(2) + ' km';
  }
  function fmtArea(m2) {
    const km2 = m2 / 1e6;
    if (km2 >= 1) return km2.toFixed(km2 >= 10 ? 0 : 2) + ' km²';
    return Math.round(m2).toLocaleString() + ' m²';
  }
  function prettyDate(iso) {
    if (!iso) return '';
    const [y, m, d] = iso.split('-').map(Number);
    const mo = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m - 1] || '';
    return `${mo} ${d}, ${y}`;
  }
  function landmarkCompare(km2) {
    const L = [
      ['football pitches', 0.00714], ['Central Parks', 3.41], ['Monacos', 2.02],
      ['Manhattans', 59.1], ['San Franciscos', 121], ['Singapores', 728.6]
    ];
    let best = L[0];
    for (const c of L) if (km2 / c[1] >= 0.8) best = c;
    const n = km2 / best[1];
    return `≈ ${n >= 10 ? Math.round(n).toLocaleString() : n.toFixed(1)} ${best[0]}`;
  }

  return {
    EARTH_AREA_KM2, EARTH_CIRC_M, EVEREST_M,
    haversine, rdp, bbox, parseIGC, statsFromFixes,
    buildPalette, assignColors, unionFindSites, captureSite, computeCapture,
    fmtKm, fmtArea, prettyDate, landmarkCompare
  };
});
