/* Captured Territory — UI + map rendering. Data logic lives in pipeline.js (CT). */
'use strict';

/* ===================================================================== MAP */
const map = L.map('map', { preferCanvas: true, zoomControl: true, worldCopyJump: true })
  .setView([37.5, -121.9], 9);

L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
  subdomains: 'abc', maxZoom: 19, maxNativeZoom: 17,  // overzoom past native res for thermal detail
  attribution: 'map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://viewfinderpanoramas.org">SRTM</a> &middot; style &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)'
}).addTo(map);

L.control.scale({ imperial: true, metric: true, position: 'bottomleft' }).addTo(map);

map.createPane('terr');  map.getPane('terr').style.zIndex = 350;
map.createPane('halo');  map.getPane('halo').style.zIndex = 360;
map.createPane('track'); map.getPane('track').style.zIndex = 370;
const rTrack = L.canvas({ pane: 'track', tolerance: 5 });
const rHalo  = L.canvas({ pane: 'halo' });
const rTerr  = L.canvas({ pane: 'terr' });  // canvas handles the ~10k capture polygons smoothly

let flights = [];
let trackLayers = [];
let terrLayer = null;
let siteBounds = [];      // L.latLngBounds per cluster, sorted by flight count desc
let curSite = 0;
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* ============================================================ SITE NAV */
function buildSiteBounds() {
  const sites = CT.unionFindSites(flights);
  siteBounds = sites
    .map(members => {
      const b = L.latLngBounds([]);
      for (const m of members) for (const p of flights[m].pts) b.extend(p);
      return { bounds: b, n: members.length };
    })
    .filter(s => s.bounds.isValid())
    .sort((a, b) => b.n - a.n);
  curSite = 0;
  updateNavLabel();
}
function gotoSite(i) {
  if (!siteBounds.length) return;
  curSite = (i + siteBounds.length) % siteBounds.length;
  map.fitBounds(siteBounds[curSite].bounds.pad(0.12));
  updateNavLabel();
}
function updateNavLabel() {
  const el = document.getElementById('nav-label');
  if (!siteBounds.length) { el.textContent = ''; return; }
  el.textContent = `site ${curSite + 1} / ${siteBounds.length} · ${siteBounds[curSite].n} flt`;
}
function fitWorld() {
  const grp = L.featureGroup(trackLayers.map(t => t.line));
  try { map.fitBounds(grp.getBounds().pad(0.05)); } catch (e) {}
  document.getElementById('nav-label').textContent = 'all flights';
}
document.getElementById('nav-home').addEventListener('click', () => gotoSite(0));
document.getElementById('nav-prev').addEventListener('click', () => gotoSite(curSite - 1));
document.getElementById('nav-next').addEventListener('click', () => gotoSite(curSite + 1));
document.getElementById('nav-world').addEventListener('click', fitWorld);

/* ============================================================ RENDER */
function renderTracks() {
  trackLayers.forEach(t => { map.removeLayer(t.halo); map.removeLayer(t.line); });
  trackLayers = [];
  for (const f of flights) {
    const halo = L.polyline(f.pts, { renderer: rHalo, pane: 'halo', color: '#ffffff',
      weight: 4, opacity: 0.55, lineJoin: 'round', lineCap: 'round', interactive: false }).addTo(map);
    const line = L.polyline(f.pts, { renderer: rTrack, pane: 'track', color: f.color,
      weight: 2.1, opacity: 0.9, lineJoin: 'round', lineCap: 'round' }).addTo(map);
    line.on('mouseover', () => { line.setStyle({ weight: 4.5, opacity: 1 }); showReadout(f); });
    line.on('mousemove', e => moveReadout(e));
    line.on('mouseout', () => { line.setStyle({ weight: 2.1, opacity: 0.9 }); hideReadout(); });
    trackLayers.push({ flight: f, halo, line });
  }
}
function setTerritory(feature) {
  if (terrLayer) { map.removeLayer(terrLayer); terrLayer = null; }
  if (!feature || !feature.geometry.coordinates.length) return;
  terrLayer = L.geoJSON(feature, {
    renderer: rTerr, pane: 'terr', interactive: false,
    style: { color: '#c85a25', weight: 1, opacity: 0.5, fillColor: '#e8842f', fillOpacity: 0.2, fillRule: 'evenodd' }
  }).addTo(map);
  if (!document.getElementById('t-terr').checked) map.removeLayer(terrLayer);
}

/* ---- hover readout ---- */
const readout = document.getElementById('readout');
function showReadout(f) {
  readout.innerHTML =
    `<div><span class="swatch" style="background:${f.color}"></span><b>${CT.prettyDate(f.date) || f.name}</b></div>` +
    `<div class="r-row">${CT.fmtKm(f.lengthM)} flown &middot; ${Math.round(f.climbM).toLocaleString()} m climbed</div>` +
    `<div class="r-row">peak ${Math.round(f.maxAltM).toLocaleString()} m</div>`;
  readout.classList.remove('hidden');
}
function moveReadout(e) {
  const pt = e.containerPoint || map.latLngToContainerPoint(e.latlng);
  readout.style.left = pt.x + 'px'; readout.style.top = pt.y + 'px';
}
function hideReadout() { readout.classList.add('hidden'); }

/* ============================================================ STATS */
function updateStats(areaM2) {
  const climbM = flights.reduce((s, f) => s + f.climbM, 0);
  const distM = flights.reduce((s, f) => s + f.lengthM, 0);
  const dates = flights.map(f => f.date).filter(Boolean).sort();

  document.getElementById('s-climb').textContent = CT.fmtKm(climbM);
  document.getElementById('s-climb-note').innerHTML =
    `&approx; ${(climbM / CT.EVEREST_M).toFixed(1)}&times; Everest, sea&#8209;to&#8209;summit`;

  document.getElementById('s-dist').textContent = CT.fmtKm(distM);
  document.getElementById('s-dist-note').innerHTML =
    `${(distM / CT.EARTH_CIRC_M * 100).toFixed(1)}% of the way around the Earth`;

  const km2 = areaM2 / 1e6, pct = km2 / CT.EARTH_AREA_KM2 * 100;
  document.getElementById('s-area').textContent = CT.fmtArea(areaM2);
  const pctStr = pct >= 0.001 ? pct.toFixed(4) + '%'
    : (pct === 0 ? '0%' : pct.toExponential(1).replace(/e(-?\d+)/, '×10<sup>$1</sup>') + '%');
  document.getElementById('s-area-note').innerHTML =
    `${Math.round(areaM2).toLocaleString()} m² &middot; ${pctStr} of the globe<br>${CT.landmarkCompare(km2)}`;

  document.getElementById('s-flights').textContent = flights.length.toLocaleString();
  if (dates.length)
    document.getElementById('s-flights-note').textContent =
      `${CT.prettyDate(dates[0])} – ${CT.prettyDate(dates[dates.length - 1])}`;
}

/* ============================================================ PIPELINE
 * `precomputed` ({areaM2, feature}) is supplied for the baked demo so it
 * renders instantly; uploads pass nothing and the capture is computed live. */
async function rebuild(fitView, precomputed) {
  veil(true, 'Drawing flight tracks…');
  if (!precomputed) CT.assignColors(flights);   // demo colours are baked into flights.json
  renderTracks();
  buildSiteBounds();
  if (fitView) gotoSite(0);   // open on the busiest site; "World" button fits everything
  await sleep(30);
  if (precomputed) {
    setTerritory(precomputed.feature);
    updateStats(precomputed.areaM2);
    veil(false);
  } else {
    veil(true, 'Computing captured territory…');
    const cap = await CT.computeCapture(flights, (i, n) =>
      veilMsg(`Computing captured territory… site ${i}/${n}`));
    setTerritory(cap.feature);
    updateStats(cap.areaM2);
    veil(false);
  }
}

/* ============================================================ VEIL */
const veilEl = document.getElementById('veil'), veilMsgEl = document.getElementById('veil-msg');
function veil(on, msg) { if (msg) veilMsgEl.textContent = msg; veilEl.classList.toggle('gone', !on); }
function veilMsg(m) { veilMsgEl.textContent = m; }

/* ============================================================ CONTROLS */
document.getElementById('t-terr').addEventListener('change', e => {
  if (!terrLayer) return;
  if (e.target.checked) terrLayer.addTo(map); else map.removeLayer(terrLayer);
});
document.getElementById('t-track').addEventListener('change', e => {
  trackLayers.forEach(t => {
    if (e.target.checked) { t.halo.addTo(map); t.line.addTo(map); }
    else { map.removeLayer(t.halo); map.removeLayer(t.line); }
  });
});

/* ============================================================ DATASET STATE */
let isDemo = false;
const welcomeEl = document.getElementById('welcome');
const HASH_RE = /@(-?[\d.]+),(-?[\d.]+),(\d+(?:\.\d+)?)/;
function showWelcome() { welcomeEl.classList.remove('gone'); }
function hideWelcome() { welcomeEl.classList.add('gone'); }
function freshMode() { return flights.length === 0 || isDemo; }  // replace demo/empty, else append
function updateBadge() {
  const b = document.getElementById('dataset');
  if (isDemo) { b.textContent = `Demo · ${flights.length} flights by Kasey Markel`; b.className = 'badge demo'; }
  else { b.textContent = `Your flights · ${flights.length.toLocaleString()}`; b.className = 'badge'; }
}

async function loadDemo(applyHash) {
  hideWelcome();
  veil(true, 'Loading demo…');
  let data;
  try {
    data = await (await fetch('flights.json')).json();
    flights = data.flights.map((f, i) => ({ ...f, id: i }));  // includes baked .color
    isDemo = true;
  } catch (e) {
    veil(true, 'Could not load the demo — try uploading your own IGC files.'); return;
  }
  const m = applyHash && location.hash.match(HASH_RE);
  await rebuild(!m, data.capture || null);   // baked capture -> instant
  if (m) map.setView([+m[1], +m[2]], +m[3]);
  updateBadge();
}

/* ---- uploads ---- */
async function ingestFiles(fileList, fresh) {
  const files = [...fileList].filter(f => /\.igc$/i.test(f.name));
  if (!files.length) return;
  hideWelcome();
  if (fresh) { flights = []; isDemo = false; }
  veil(true, `Reading ${files.length} file${files.length > 1 ? 's' : ''}…`);
  for (const file of files) {
    try {
      const parsed = CT.parseIGC(await file.text(), file.name.replace(/\.igc$/i, ''));
      if (parsed) { parsed.id = flights.length; flights.push(parsed); }
    } catch (e) {}
  }
  if (flights.length) { isDemo = false; await rebuild(false); fitWorld(); updateBadge(); }
  else { veil(false); showWelcome(); }
}

document.getElementById('w-demo').addEventListener('click', () => loadDemo(false));
document.getElementById('w-upload').addEventListener('click', () => document.getElementById('upload').click());
document.getElementById('restart').addEventListener('click', e => { e.preventDefault(); showWelcome(); });
document.getElementById('upload').addEventListener('change', e => {
  ingestFiles(e.target.files, freshMode());
  e.target.value = '';  // let the same file be re-selected later
});

const dropEl = document.getElementById('drop');
let dragDepth = 0;
window.addEventListener('dragenter', e => { e.preventDefault(); if (dragDepth++ === 0) dropEl.classList.remove('hidden'); });
window.addEventListener('dragover', e => e.preventDefault());
window.addEventListener('dragleave', e => { e.preventDefault(); if (--dragDepth <= 0) { dragDepth = 0; dropEl.classList.add('hidden'); } });
window.addEventListener('drop', e => {
  e.preventDefault(); dragDepth = 0; dropEl.classList.add('hidden');
  if (e.dataTransfer && e.dataTransfer.files.length) ingestFiles(e.dataTransfer.files, freshMode());
});

/* persist the current view in the URL while exploring the demo (shareable links) */
map.on('moveend', () => {
  if (!isDemo) return;
  const c = map.getCenter();
  history.replaceState(null, '', `#@${c.lat.toFixed(5)},${c.lng.toFixed(5)},${map.getZoom()}`);
});

/* ============================================================ BOOT */
// A shared deep-link (#@lat,lng,zoom) jumps straight into the demo at that view;
// otherwise greet the user with the upload-first welcome screen.
if (HASH_RE.test(location.hash)) loadDemo(true);
else showWelcome();
