// Evo Tree Viewer — 3D phylogeny rendered as an oak.
// The scene is (re)built from a "model": either the full tree, or the tree pruned to a species list.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { layoutTree, mulberry32 } from './layout.js';
import { parseList, resolveEntries, encodeList, decodeList } from './lists.js';

const params = new URLSearchParams(location.search);
const DATA_URL = params.get('data') || 'data/land-plants.json';
const IS_TOUCH = matchMedia('(pointer: coarse)').matches;
const IS_SMALL = Math.min(innerWidth, innerHeight) < 720;
const $ = (id) => document.getElementById(id);
const fmt = (x) => x.toLocaleString('en-US');
const esc = (s) => String(s).replace(/[&<>"]/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } },
};

// ================================================================ base data
const D = await (await fetch(DATA_URL)).json();
const BN = D.parent.length;
const bName = (i) => D.labels[D.label[i]] || '';
const bFam = (i) => D.labels[D.family[i]] || '';
const friendly = (nm) => D.friendly[nm] || '';
const KINGDOM = (D.gbif && D.gbif.kingdom) || 'Plantae';
$('nsp').textContent = fmt(D.total);
$('dsName').textContent = D.title || 'Tree';

// name indexes over the base tree (for list matching)
const genusIndex = new Map(), cladeIndex = new Map();
for (let i = 0; i < BN; i++) {
  const nm = bName(i); if (!nm) continue;
  const k = nm.toLowerCase();
  if (D.genus[i]) { if (!genusIndex.has(k)) genusIndex.set(k, i); }
  else if (!cladeIndex.has(k)) cladeIndex.set(k, i);
  const fr = friendly(nm); if (fr && !D.genus[i] && !cladeIndex.has(fr.toLowerCase())) cladeIndex.set(fr.toLowerCase(), i);
}

// ================================================================ models
// A model: parent[], n[] (wires = species, or list members when pruned), and per-node name/family/kind/base.
// kind: 0 clade, 1 genus, 2 list species (pruned tips)
function fullModel() {
  return {
    pruned: false, N: BN, parent: D.parent, n: D.n, total: D.total,
    name: bName, fam: bFam, kind: (i) => (D.genus[i] ? 1 : 0), base: (i) => i, item: () => null,
  };
}
function prunedModel(items) {
  const keep = new Uint8Array(BN);
  for (const it of items) { let u = it.at; while (u >= 0 && !keep[u]) { keep[u] = 1; u = D.parent[u]; } }
  const kidsB = new Map();
  for (let i = 1; i < BN; i++) if (keep[i]) { const p = D.parent[i]; (kidsB.get(p) || kidsB.set(p, []).get(p)).push(i); }
  const tipsAt = new Map();
  items.forEach((it, k) => (tipsAt.get(it.at) || tipsAt.set(it.at, []).get(it.at)).push(k));
  const parent = [], n = [], name = [], fam = [], kind = [], base = [], item = [];
  const push = (p, nm, f, kd, b, itk) => { parent.push(p); n.push(0); name.push(nm); fam.push(f); kind.push(kd); base.push(b); item.push(itk); return parent.length - 1; };
  const childrenOf = (u) => [...(kidsB.get(u) || []).map((c) => ({ c })), ...(tipsAt.get(u) || []).map((k) => ({ k }))];
  const bestName = (chain) => {   // deepest named node of a collapsed chain, friendly names preferred
    let best = '';
    for (const u of chain) { const nm = bName(u); if (nm) best = nm; }
    return best;
  };
  const emit = (u, p, isRoot) => {
    // collapse single-child chains of clades (keeps the tree to its real branch points)
    const chain = [u]; let ch = childrenOf(u);
    while (!isRoot && ch.length === 1 && ch[0].c !== undefined && !D.genus[u]) { u = ch[0].c; chain.push(u); ch = childrenOf(u); }
    const me = push(p, isRoot ? bName(u) : bestName(chain), D.genus[u] ? bFam(u) : '', D.genus[u] ? 1 : 0, u, null);
    for (const x of ch) {
      if (x.k !== undefined) { const it = items[x.k]; push(me, it.label, it.family || bFam(it.at), 2, it.at, x.k); }
      else emit(x.c, me, false);
    }
    return me;
  };
  emit(0, -1, true);
  const N = parent.length;
  for (let i = N - 1; i >= 0; i--) { if (kind[i] === 2) n[i] = 1; if (i > 0) n[parent[i]] += n[i]; }
  // children must be in descending-n order for the layout; layoutTree sorts its own kid lists, preorder is preserved
  return {
    pruned: true, N, parent, n, total: n[0],
    name: (i) => name[i], fam: (i) => fam[i], kind: (i) => kind[i], base: (i) => base[i], item: (i) => (item[i] === null ? null : items[item[i]]),
  };
}

// ================================================================ three setup (once)
const canvas = $('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: !IS_SMALL, powerPreference: 'high-performance' });
const DPR = Math.min(devicePixelRatio || 1, IS_SMALL ? 1.75 : 2);
renderer.setPixelRatio(DPR);
renderer.setSize(innerWidth, innerHeight, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.05, 6000);
const v3 = new THREE.Vector3();
{
  const c = document.createElement('canvas'); c.width = 4; c.height = 512;
  const g = c.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, 512);
  gr.addColorStop(0, '#0b1420'); gr.addColorStop(0.45, '#19324a'); gr.addColorStop(0.72, '#3d5568');
  gr.addColorStop(0.86, '#8a7a6a'); gr.addColorStop(1, '#2a2620');
  g.fillStyle = gr; g.fillRect(0, 0, 4, 512);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  scene.background = t;
}
const FOG = new THREE.Color('#2b3c4a');
scene.fog = new THREE.Fog(FOG, 100, 500);
scene.add(new THREE.HemisphereLight(0xbcd3e6, 0x3a2e22, 1.35));
const sun = new THREE.DirectionalLight(0xffe2b8, 2.4);
sun.position.set(-0.6, 1, 0.45).multiplyScalar(100);
scene.add(sun);
const SUN_DIR = sun.position.clone().normalize();
// the ground under the tree: patchy grass over bare soil, worn to dirt around the trunk, soft edge into the dusk
const groundTex = (() => {
  const S = 1024, h = S / 2, c = document.createElement('canvas'); c.width = c.height = S;
  const g = c.getContext('2d'), rnd = mulberry32(7);
  // smooth value noise (two octaves) → where grass grows
  const G = 12, grid = Array.from({ length: (G + 1) * (G + 1) }, rnd), G2 = 29, grid2 = Array.from({ length: (G2 + 1) * (G2 + 1) }, rnd);
  const vn = (gr, n, x, y) => {
    const fx = x * n, fy = y * n, ix = Math.min(n - 1, fx | 0), iy = Math.min(n - 1, fy | 0), tx = fx - ix, ty = fy - iy;
    const sx = tx * tx * (3 - 2 * tx), sy = ty * ty * (3 - 2 * ty), at = (i, j) => gr[j * (n + 1) + i];
    return (at(ix, iy) * (1 - sx) + at(ix + 1, iy) * sx) * (1 - sy) + (at(ix, iy + 1) * (1 - sx) + at(ix + 1, iy + 1) * sx) * sy;
  };
  const grass = (x, y) => {   // 0 = bare soil … 1 = full grass
    const d = Math.hypot(x - h, y - h) / h;
    const n = 0.65 * vn(grid, G, x / S, y / S) + 0.35 * vn(grid2, G2, x / S, y / S);
    const worn = Math.min(1, Math.max(0, (d - 0.12) / 0.3));   // trampled/shaded soil near the trunk
    return Math.min(1, Math.max(0, (n - 0.3) * 2.8)) * worn;
  };
  // soil
  g.fillStyle = '#5c4430'; g.beginPath(); g.arc(h, h, h, 0, Math.PI * 2); g.fill();
  for (let k = 0; k < 9000; k++) {   // crumbs, pebbles, leaf litter
    const a = rnd() * Math.PI * 2, d = Math.sqrt(rnd()) * h, x = h + Math.cos(a) * d, y = h + Math.sin(a) * d;
    const l = 14 + rnd() * 22, r = 0.8 + rnd() * (rnd() < 0.05 ? 4 : 1.8);
    g.fillStyle = rnd() < 0.12 ? `hsla(${30 + rnd() * 20},${20 + rnd() * 25}%,${l + 10}%,0.7)` : `hsla(${22 + rnd() * 14},${25 + rnd() * 20}%,${l}%,0.6)`;
    g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
  }
  // grass: a green wash where it grows, then blades whose density follows the same field
  const img = g.getImageData(0, 0, S, S), px = img.data;
  for (let y = 0; y < S; y += 1) for (let x = 0; x < S; x += 1) {
    const w = grass(x, y) * 0.85; if (w <= 0) continue;
    const o = (y * S + x) * 4;
    px[o] = px[o] * (1 - w) + 58 * w; px[o + 1] = px[o + 1] * (1 - w) + 88 * w; px[o + 2] = px[o + 2] * (1 - w) + 38 * w;
  }
  g.putImageData(img, 0, 0);
  g.lineCap = 'round';
  for (let k = 0; k < 42000; k++) {
    const a = rnd() * Math.PI * 2, d = Math.sqrt(rnd()) * h * 0.98, x = h + Math.cos(a) * d, y = h + Math.sin(a) * d;
    if (rnd() > grass(x, y) * 1.1 + 0.03) continue;
    const L = 3 + rnd() * 6, ang = rnd() * Math.PI * 2, l = 22 + rnd() * 26;
    g.strokeStyle = `hsla(${84 + rnd() * 26},${38 + rnd() * 25}%,${l}%,${0.5 + rnd() * 0.4})`;
    g.lineWidth = 0.8 + rnd() * 0.9;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(ang) * L, y + Math.sin(ang) * L); g.stroke();
  }
  let gr = g.createRadialGradient(h, h, h * 0.05, h, h, h * 0.8);   // crown shadow
  gr.addColorStop(0, 'rgba(0,0,0,0.3)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(0, 0, S, S);
  g.globalCompositeOperation = 'destination-in';   // soft, slightly ragged rim
  gr = g.createRadialGradient(h, h, h * 0.72, h, h, h);
  gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(0.6, 'rgba(0,0,0,0.7)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(0, 0, S, S);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
})();
const beadTex = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,230,160,0.9)'); gr.addColorStop(1, 'rgba(255,180,60,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
})();
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth / 2, innerHeight / 2), 0.7, 0.45, 0.95);
composer.addPass(bloom);
composer.addPass(new OutputPass());

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.08;
controls.zoomToCursor = true;            // zoom toward the pointer, so you can travel anywhere in the crown
controls.minDistance = 0.15;
controls.maxPolarAngle = Math.PI * 0.53;
controls.zoomSpeed = 2.6; controls.rotateSpeed = IS_TOUCH ? 0.7 : 0.9;
controls.autoRotateSpeed = 0.35;
controls.screenSpacePanning = true;

// ================================================================ world (rebuilt per model)
const BARK_DARK = new THREE.Color('#3b3028'), BARK_TWIG = new THREE.Color('#5b4a3a');
const BARK_SEL = new THREE.Color('#c9b48a'), BARK_PATH = new THREE.Color('#c08a3a');
const GLOW = new THREE.Color(3.2, 2.1, 0.75);
const GROUP_HSL = {
  A: [0.27, 0.42, 0.33], Polypodiophyta: [0.40, 0.38, 0.33], Bryophyta: [0.21, 0.55, 0.38],
  Marchantiophyta: [0.18, 0.42, 0.32], Anthocerotophyta: [0.15, 0.45, 0.36], Lycopodiophyta: [0.36, 0.42, 0.28],
  Pinophyta: [0.44, 0.32, 0.24], Cycadophyta: [0.32, 0.38, 0.27], Ginkgophyta: [0.13, 0.85, 0.52],
};

let M, N, L, start, end, dir, radius, size, kids;
let items = [], listTitle = '', listSource = 'default';
let hlNode = [];                 // per list item: node index in the current model
let onPath, listCount;
let world = null;                // { group, bark, leaves, glow, beads, ... }
let crownCenter = new THREE.Vector3(), treeR = 50;
let clusterR, clusterC;
let selected = -1;
let leafMat;
let labelsOn = true, glowOn = true, leavesOn = true, focusOn = false;
let candidates = [], index = [];
const NAME = (i) => M.name(i);
const FAM = (i) => M.fam(i);
const KIND = (i) => M.kind(i);
const display = (i) => { const nm = NAME(i); if (!nm) return 'Unnamed clade'; return KIND(i) === 2 ? nm : friendly(nm) || nm; };

function disposeWorld() {
  if (!world) return;
  scene.remove(world.group);
  world.group.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) [].concat(o.material).forEach((m) => m.dispose()); });
  for (const el of labelPool.values()) el.remove();
  labelPool.clear(); shown = new Set();
}

function buildWorld() {
  disposeWorld();
  N = M.N;
  L = layoutTree(M.parent, M.n, M.pruned ? { lenBase: 15, minRadius: 0.02 } : {});
  ({ start, end, dir, radius, size, kids } = L);
  // list → node in this model
  if (M.pruned) { hlNode = []; for (let i = 0; i < N; i++) { const it = M.item(i); if (it) hlNode[items.indexOf(it)] = i; } }
  else hlNode = items.map((it) => it.at);
  onPath = new Uint8Array(N); listCount = new Int32Array(N);
  for (const h of hlNode) { if (h === undefined) continue; let u = h; while (u >= 0) { onPath[u] = 1; listCount[u]++; u = M.parent[u]; } }

  const group = new THREE.Group(); scene.add(group);
  world = { group };
  const bb = new THREE.Box3();
  for (let i = 0; i < N; i++) bb.expandByPoint(v3.fromArray(end, i * 3));
  bb.expandByPoint(new THREE.Vector3(0, 0, 0));
  bb.getCenter(crownCenter);
  treeR = Math.max(5, bb.getSize(new THREE.Vector3()).length() / 2);
  scene.fog.near = treeR * 1.6; scene.fog.far = treeR * 5.5;
  controls.maxDistance = treeR * 6;
  {
    const m = new THREE.Mesh(new THREE.CircleGeometry(treeR * 0.575, 96), new THREE.MeshLambertMaterial({ map: groundTex, color: 0xc4c4c4, transparent: true, depthWrite: false, fog: false }));
    m.rotation.x = -Math.PI / 2; m.position.set(crownCenter.x, -0.01, crownCenter.z); group.add(m); world.ground = m;
  }
  buildBark(group);
  buildLeaves(group);
  buildGlow(group);
  buildCandidates();
  buildSearchIndex();
  world.glow.visible = glowOn; world.leaves.visible = leavesOn;
  applyFocus();
}
// "Your species only": everything off your lineages fades to 10% and loses its labels
function applyFocus() {
  const on = focusOn && items.length > 0;
  const gm = world.barkGhost;
  gm.transparent = on; gm.opacity = on ? 0.1 : 1; gm.depthWrite = !on; gm.needsUpdate = true;
  leafMat.uniforms.uFocus.value = on ? 1 : 0;
  leafMat.transparent = on; leafMat.depthWrite = !on; leafMat.needsUpdate = true;
  world.ground.material.opacity = on ? 0.5 : 1;
  $('bFocus').classList.toggle('on', focusOn);
}

// ---------------------------------------------------------------- bark
let vStart, bCol, bNor, bColAttr, baseCol;
function tubeSpec(i) {
  const r = radius[i];
  const radial = r > 0.25 ? 14 : r > 0.06 ? 9 : r > 0.015 ? 6 : 4;
  const segs = r > 0.06 ? 6 : r > 0.015 ? 3 : 1;
  return [radial, segs];
}
// each branch is a quadratic Bézier that leaves its parent along the parent's direction;
// the start is pushed back into the parent so joints are buried, not gaping
function branchCurve(i, S, C, E) {
  E.fromArray(end, i * 3);
  if (i === 0) { S.set(0, 0, 0); C.set(0, E.y * 0.5, 0); return; }
  const p = M.parent[i];
  const pd = v3.fromArray(dir, p * 3);
  S.fromArray(start, i * 3).addScaledVector(pd, -Math.min(radius[p] * 0.8, L.len[p] * 0.3));
  C.copy(S).addScaledVector(pd, L.len[i] * 0.35).lerp(E, 0.25);
}
function bez(S, C, E, t, P, T) {
  const mt = 1 - t;
  P.set(mt * mt * S.x + 2 * mt * t * C.x + t * t * E.x, mt * mt * S.y + 2 * mt * t * C.y + t * t * E.y, mt * mt * S.z + 2 * mt * t * C.z + t * t * E.z);
  if (T) T.set(2 * mt * (C.x - S.x) + 2 * t * (E.x - C.x), 2 * mt * (C.y - S.y) + 2 * t * (E.y - C.y), 2 * mt * (C.z - S.z) + 2 * t * (E.z - C.z)).normalize();
}
function buildBark(group) {
  const rnd = mulberry32(11);
  vStart = new Int32Array(N + 1);
  let nVert = 0, nIdx = 0;
  for (let i = 0; i < N; i++) { const [a, s] = tubeSpec(i); vStart[i] = nVert; nVert += a * (s + 1); nIdx += a * s * 6; }
  vStart[N] = nVert;
  const bPos = new Float32Array(nVert * 3); bNor = new Float32Array(nVert * 3); bCol = new Float32Array(nVert * 3);
  const bIdx = new Uint32Array(nIdx);
  let nOn = 0; for (let i = 0; i < N; i++) if (onPath[i]) { const [a, sg] = tubeSpec(i); nOn += a * sg * 6; }
  let iOn = 0, iOff = nOn;
  baseCol = new Float32Array(N * 3);
  let vi = 0;
  const S = new THREE.Vector3(), E = new THREE.Vector3(), C = new THREE.Vector3(), P = new THREE.Vector3(), T = new THREE.Vector3();
  const U = new THREE.Vector3(), V = new THREE.Vector3(), ref = new THREE.Vector3(), prevU = new THREE.Vector3();
  for (let i = 0; i < N; i++) {
    const [radial, segs] = tubeSpec(i);
    const p = M.parent[i];
    branchCurve(i, S, C, E);
    const r1 = radius[i];
    const r0 = i === 0 ? r1 * 1.55 : Math.min(radius[p], r1 * 1.12);
    const tw = Math.min(1, Math.max(0, (0.12 - r1) / 0.12));
    const col = BARK_DARK.clone().lerp(BARK_TWIG, tw);
    col.offsetHSL(0, 0, (rnd() - 0.5) * 0.04);
    if (onPath[i] && !M.pruned) col.lerp(BARK_PATH, 0.4);
    baseCol[i * 3] = col.r; baseCol[i * 3 + 1] = col.g; baseCol[i * 3 + 2] = col.b;
    const base = vi;
    for (let s = 0; s <= segs; s++) {
      const t = s / segs;
      bez(S, C, E, t, P, T);
      if (s === 0) { ref.set(0, 1, 0); if (Math.abs(T.y) > 0.9) ref.set(1, 0, 0); U.crossVectors(T, ref).normalize(); }
      else U.copy(prevU).addScaledVector(T, -prevU.dot(T)).normalize();   // parallel transport
      prevU.copy(U); V.crossVectors(T, U);
      let r = r0 + (r1 - r0) * t;
      if (i === 0) r = r1 * (1 + 0.55 * Math.pow(1 - t, 3));   // root flare
      const gnarl = r1 > 0.06 ? 1 + 0.06 * Math.sin(t * 9 + i) : 1;
      for (let a = 0; a < radial; a++) {
        const ang = (a / radial) * Math.PI * 2;
        const ca = Math.cos(ang), sa = Math.sin(ang);
        const nx = U.x * ca + V.x * sa, ny = U.y * ca + V.y * sa, nz = U.z * ca + V.z * sa;
        const rr = r * gnarl * (1 + (r1 > 0.2 ? 0.05 * Math.sin(ang * 5 + t * 3) : 0));
        bPos[vi * 3] = P.x + nx * rr; bPos[vi * 3 + 1] = P.y + ny * rr; bPos[vi * 3 + 2] = P.z + nz * rr;
        bNor[vi * 3] = nx; bNor[vi * 3 + 1] = ny; bNor[vi * 3 + 2] = nz;
        const shade = 0.88 + 0.12 * ny;
        bCol[vi * 3] = col.r * shade; bCol[vi * 3 + 1] = col.g * shade; bCol[vi * 3 + 2] = col.b * shade;
        vi++;
      }
    }
    let ii = onPath[i] ? iOn : iOff;
    for (let s = 0; s < segs; s++) for (let a = 0; a < radial; a++) {
      const a1 = (a + 1) % radial;
      const i0 = base + s * radial + a, i1 = base + s * radial + a1, i2 = base + (s + 1) * radial + a, i3 = base + (s + 1) * radial + a1;
      bIdx[ii++] = i0; bIdx[ii++] = i2; bIdx[ii++] = i1; bIdx[ii++] = i1; bIdx[ii++] = i2; bIdx[ii++] = i3;
    }
    if (onPath[i]) iOn = ii; else iOff = ii;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(bPos, 3));
  g.setAttribute('normal', new THREE.BufferAttribute(bNor, 3));
  bColAttr = new THREE.BufferAttribute(bCol, 3); bColAttr.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute('color', bColAttr);
  g.setIndex(new THREE.BufferAttribute(bIdx, 1));
  g.addGroup(0, nOn, 0); g.addGroup(nOn, nIdx - nOn, 1);
  const barkMat = () => new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.92, metalness: 0 });
  world.barkGhost = barkMat();
  world.bark = new THREE.Mesh(g, [barkMat(), world.barkGhost]);
  group.add(world.bark);
}
function paintBark(i0, i1, mode) {
  for (let i = i0; i < i1; i++) {
    let r = baseCol[i * 3], g = baseCol[i * 3 + 1], b = baseCol[i * 3 + 2];
    if (mode === 1) { r = r * 0.35 + BARK_SEL.r * 0.65; g = g * 0.35 + BARK_SEL.g * 0.65; b = b * 0.35 + BARK_SEL.b * 0.65; }
    for (let v = vStart[i]; v < vStart[i + 1]; v++) {
      const shade = 0.88 + 0.12 * bNor[v * 3 + 1];
      bCol[v * 3] = r * shade; bCol[v * 3 + 1] = g * shade; bCol[v * 3 + 2] = b * shade;
    }
  }
  bColAttr.needsUpdate = true;
}

// ---------------------------------------------------------------- leaves (one per species; decorative tufts on pruned tips)
function buildLeaves(group) {
  clusterR = new Float32Array(N); clusterC = new Float32Array(N * 3);
  const tips = [];
  const leafN = (i) => (M.pruned ? 36 : M.n[i]);
  for (let i = 0; i < N; i++) if ((M.pruned ? KIND(i) === 2 : KIND(i) === 1 && M.n[i] > 0)) tips.push(i);
  const total = tips.reduce((a, i) => a + leafN(i), 0);
  const lPos = new Float32Array(total * 3), lCol = new Float32Array(total * 3), lSize = new Float32Array(total), lAng = new Float32Array(total), lNode = new Float32Array(total), lOn = new Float32Array(total);
  const r = mulberry32(3); const col = new THREE.Color(); let k = 0;
  for (const i of tips) {
    const n = leafN(i);
    const grp = D.groups[FAM(i)] || 'A';
    const [h, s, l] = GROUP_HSL[grp] || GROUP_HSL.A;
    const hj = (r() - 0.5) * 0.05, sj = (r() - 0.5) * 0.12;
    const rho = M.pruned ? Math.max(0.35, radius[i] * 3.2) : 0.09 + 0.1 * Math.cbrt(n);
    const leafSz = M.pruned ? Math.max(0.11, rho * 0.32) : 0.11;
    const dx = dir[i * 3], dy = dir[i * 3 + 1], dz = dir[i * 3 + 2];
    const cx = end[i * 3] + dx * rho * 0.7, cy = end[i * 3 + 1] + dy * rho * 0.7 + rho * 0.15, cz = end[i * 3 + 2] + dz * rho * 0.7;
    clusterR[i] = rho; clusterC[i * 3] = cx; clusterC[i * 3 + 1] = cy; clusterC[i * 3 + 2] = cz;
    for (let j = 0; j < n; j++, k++) {
      let x, y, z, q; do { x = r() * 2 - 1; y = r() * 2 - 1; z = r() * 2 - 1; q = x * x + y * y + z * z; } while (q > 1 || q < 0.04);
      const sh = Math.pow(q, 0.15);
      lPos[k * 3] = cx + x * rho * sh; lPos[k * 3 + 1] = cy + y * rho * sh * 0.75; lPos[k * 3 + 2] = cz + z * rho * sh;
      col.setHSL(h + hj + (r() - 0.5) * 0.02, Math.min(1, s + sj), l * (0.8 + r() * 0.45));
      lCol[k * 3] = col.r; lCol[k * 3 + 1] = col.g; lCol[k * 3 + 2] = col.b;
      lSize[k] = leafSz * (0.7 + r() * 0.6); lAng[k] = r() * Math.PI * 2; lNode[k] = i; lOn[k] = onPath[i];
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(lPos, 3));
  g.setAttribute('color', new THREE.BufferAttribute(lCol, 3));
  g.setAttribute('size', new THREE.BufferAttribute(lSize, 1));
  g.setAttribute('ang', new THREE.BufferAttribute(lAng, 1));
  g.setAttribute('node', new THREE.BufferAttribute(lNode, 1));
  g.setAttribute('onp', new THREE.BufferAttribute(lOn, 1));
  leafMat = new THREE.ShaderMaterial({
    uniforms: {
      uScale: { value: leafScale() }, uFocus: { value: 0 }, uTime: { value: 0 }, uSel: { value: new THREE.Vector2(-1, -1) },
      uSun: { value: SUN_DIR }, uCenter: { value: crownCenter.clone() }, uR: { value: treeR },
      uFog: { value: FOG }, uFogNear: { value: scene.fog.near }, uFogFar: { value: scene.fog.far },
    },
    vertexShader: /* glsl */`
      attribute float size; attribute float ang; attribute float node; attribute float onp; attribute vec3 color;
      uniform float uScale, uTime, uR, uFocus; uniform vec2 uSel; uniform vec3 uSun, uCenter;
      varying vec3 vCol; varying float vAng, vDim, vFogD, vAlpha;
      void main() {
        vec3 p = position;
        float w = sin(uTime * 1.3 + p.x * 0.7 + p.z * 0.5) * 0.012 + sin(uTime * 2.1 + p.y * 1.3) * 0.006;
        p.x += w; p.z += w * 0.6;
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * mv;
        gl_PointSize = clamp(size * uScale / -mv.z, 1.6, 90.0);
        vec3 rel = normalize(p - uCenter);
        float lit = 0.62 + 0.5 * max(dot(rel, uSun), 0.0) + 0.18 * clamp((p.y - uCenter.y) / uR, -1.0, 1.0);
        vCol = color * lit;
        vAng = ang;
        vDim = (uSel.y > 0.0 && (node < uSel.x || node >= uSel.y)) ? 1.0 : 0.0;
        vFogD = -mv.z;
        vAlpha = mix(1.0, 0.1, uFocus * (1.0 - onp));
      }`,
    fragmentShader: /* glsl */`
      uniform vec3 uFog; uniform float uFogNear, uFogFar;
      varying vec3 vCol; varying float vAng, vDim, vFogD, vAlpha;
      void main() {
        vec2 q = gl_PointCoord * 2.0 - 1.0;
        float c = cos(vAng), s = sin(vAng);
        q = vec2(c * q.x - s * q.y, s * q.x + c * q.y);
        float halfW = 0.5 * pow(max(1.0 - q.y * q.y, 0.0), 0.85);
        if (abs(q.x) > halfW || abs(q.y) > 0.98) discard;
        float rib = smoothstep(0.0, 0.07, abs(q.x));
        vec3 col = vCol * (0.78 + 0.22 * rib) * (0.92 + 0.12 * q.y);
        col = mix(col, col * 0.28 + vec3(0.02, 0.03, 0.04), vDim);
        float f = smoothstep(uFogNear, uFogFar, vFogD);
        gl_FragColor = vec4(mix(col, uFog, f), vAlpha);
        #include <colorspace_fragment>
      }`,
  });
  world.leaves = new THREE.Points(g, leafMat);
  world.leaves.frustumCulled = false;
  group.add(world.leaves);
}
const pxPerUnit = () => (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))) / innerHeight;
const leafScale = () => (innerHeight * DPR) / 2 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));

// ---------------------------------------------------------------- glow: highlighted lineages, tip to root
function buildGlow(group) {
  const glow = new THREE.Group(); group.add(glow); world.glow = glow;
  const segs = [];
  for (let i = 0; i < N; i++) if (onPath[i]) segs.push(i);
  const S = new THREE.Vector3(), C = new THREE.Vector3(), E = new THREE.Vector3(), P = new THREE.Vector3(), T = new THREE.Vector3();
  const U = new THREE.Vector3(), V = new THREE.Vector3(), ref = new THREE.Vector3();
  // (a) a warm sheen over every lineage branch, brightest on thin twigs
  const pos = [], idx = [], col = [];
  // (b) a glowing vine along every lineage branch, tip to root
  const vpos = [], vidx = [], vtan = [], vang = [], vext = [];
  for (const i of segs) {
    branchCurve(i, S, C, E);
    const p = M.parent[i];
    const r1 = radius[i], r0 = i === 0 ? r1 : Math.min(radius[p], r1 * 1.12);
    const segsN = Math.max(2, tubeSpec(i)[1]), radial = 8, base = pos.length / 3;
    const k = (M.pruned ? 0.03 : 0.05) + 0.95 * Math.pow(Math.max(0, 1 - r1 / 0.15), 1.5);
    for (let s = 0; s <= segsN; s++) {
      const t = s / segsN; bez(S, C, E, t, P, T);
      if (s === 0) { ref.set(0, 1, 0); if (Math.abs(T.y) > 0.9) ref.set(1, 0, 0); U.crossVectors(T, ref).normalize(); }
      else U.addScaledVector(T, -U.dot(T)).normalize();
      V.crossVectors(T, U);
      const r = (r0 + (r1 - r0) * t) * 1.14 + 0.012;
      for (let a = 0; a < radial; a++) {
        const ang = a / radial * Math.PI * 2, c = Math.cos(ang), sn = Math.sin(ang);
        pos.push(P.x + (U.x * c + V.x * sn) * r, P.y + (U.y * c + V.y * sn) * r, P.z + (U.z * c + V.z * sn) * r);
        col.push(GLOW.r * k, GLOW.g * k, GLOW.b * k);
      }
    }
    for (let s = 0; s < segsN; s++) for (let a = 0; a < radial; a++) {
      const a1 = (a + 1) % radial, o = base + s * radial;
      idx.push(o + a, o + radial + a, o + a1, o + a1, o + radial + a, o + radial + a1);
    }
    {
      // a vine painted on the camera-facing side of every lineage branch (oriented in the vertex shader, so it
      // never wraps out of sight). Continuous by construction: the side-to-side wander is zero at both ends of
      // each branch, the start of a branch (buried inside its parent's bark) is depth-lifted toward the camera
      // so it draws over the joint, and the shader keeps it at least ~1px wide at any zoom.
      const len = Math.max(1e-3, S.distanceTo(E));
      const amp = r1 >= 0.05 ? 0.42 : 0;
      const turns = amp ? Math.max(0.6, len / (r1 * 7)) : 0;
      const steps = Math.min(60, Math.max(4, Math.ceil(turns * 10)));
      const hw = Math.min(Math.max(r1 * 0.3, 0.006), 0.026 + 0.024 * Math.sqrt(listCount[i]));   // half-width
      const phase = (i * 2.399) % (Math.PI * 2);
      const rp = i === 0 ? 0 : radius[p];
      const tj = i === 0 ? 0 : Math.min(1, (Math.min(rp * 0.8, L.len[p] * 0.3) + rp * 1.2) / len);
      const vb = vpos.length / 3;
      for (let s = 0; s <= steps; s++) {
        const t = s / steps; bez(S, C, E, t, P, T);
        const r = (r0 + (r1 - r0) * t) * (r1 > 0.06 ? 1 + 0.06 * Math.sin(t * 9 + i) : 1);
        const wave = amp * Math.sin(Math.PI * t) * Math.sin(phase + t * turns * Math.PI * 2);
        const lift = tj > 0 ? rp * 1.3 * Math.max(0, 1 - t / tj) : 0;
        for (let a = -1; a <= 1; a++) { vpos.push(P.x, P.y, P.z); vtan.push(T.x, T.y, T.z); vang.push(wave, r, a); vext.push(hw, lift); }
      }
      for (let s = 0; s < steps; s++) for (let a = 0; a < 2; a++) {
        const o = vb + s * 3 + a;
        vidx.push(o, o + 3, o + 1, o + 1, o + 3, o + 4);
      }
    }
  }
  const add = (G, M) => { const m = new THREE.Mesh(G, M); glow.add(m); return m; };
  {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.setIndex(idx);
    world.sheen = add(g, new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, opacity: 1, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
  }
  {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(vpos, 3)); g.setIndex(vidx);
    g.setAttribute('tang', new THREE.Float32BufferAttribute(vtan, 3)); g.setAttribute('arc', new THREE.Float32BufferAttribute(vang, 3));
    g.setAttribute('ext', new THREE.Float32BufferAttribute(vext, 2));
    world.vine = add(g, new THREE.ShaderMaterial({
      uniforms: { uCol: { value: new THREE.Color(2.6, 1.75, 0.6) }, uPx: { value: pxPerUnit() } },
      side: THREE.DoubleSide,
      vertexShader: /* glsl */`
        attribute vec3 tang; attribute vec3 arc;   // arc = (angle from the camera-facing line, bark radius, -1..1 across)
        attribute vec2 ext;                        // ext = (half-width, depth lift toward the camera)
        uniform float uPx;                         // world units per pixel at distance 1
        varying float vAcross;
        void main() {
          vec3 c = (modelMatrix * vec4(position, 1.0)).xyz;
          vec3 t = normalize(mat3(modelMatrix) * tang);
          vec3 v = cameraPosition - c;
          vec3 n = v - t * dot(v, t);
          if (dot(n, n) < 1e-8) n = cross(t, abs(t.y) < 0.9 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0));
          n = normalize(n);
          vec3 b = normalize(cross(t, n));
          float d = length(v), px = uPx * d;
          float hw = max(ext.x, px * 0.9);
          vec3 p = c + n * (arc.y * 1.1 * cos(arc.x) + 0.002) + b * (arc.y * sin(arc.x) + arc.z * hw)
                 + (v / d) * (ext.y + px * 2.0);
          vAcross = arc.z;
          gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0);
        }`,
      fragmentShader: /* glsl */`
        uniform vec3 uCol; varying float vAcross;
        void main() {
          gl_FragColor = vec4(uCol * (1.0 - 0.45 * vAcross * vAcross), 1.0);
          #include <colorspace_fragment>
        }`,
    }));
    world.vine.frustumCulled = false;
  }
  // beads at each listed species
  const beadPos = [];
  const byNode = new Map();
  hlNode.forEach((h, k) => { if (h !== undefined) (byNode.get(h) || byNode.set(h, []).get(h)).push(k); });
  for (const [i, ks] of byNode) {
    const rho = clusterR[i] || radius[i] * 3 + 0.3;
    const c = clusterR[i] ? new THREE.Vector3().fromArray(clusterC, i * 3) : new THREE.Vector3().fromArray(end, i * 3);
    const d = new THREE.Vector3().fromArray(dir, i * 3);
    ks.forEach((k, j) => {
      const a = j * 2.4, off = new THREE.Vector3(Math.cos(a), 0.4, Math.sin(a)).multiplyScalar(rho * 0.55);
      const p = c.clone().addScaledVector(d, M.pruned ? rho * 0.2 : rho * 0.85).add(ks.length > 1 ? off : new THREE.Vector3());
      beadPos.push(p); items[k].pos = p;
    });
  }
  world.beadSize = M.pruned ? Math.max(1.2, treeR * 0.02) : 1.4;
  world.beadMat = new THREE.PointsMaterial({ map: beadTex, color: GLOW, size: world.beadSize, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, sizeAttenuation: true });
  glow.add(new THREE.Points(new THREE.BufferGeometry().setFromPoints(beadPos.length ? beadPos : [new THREE.Vector3(0, -999, 0)]), world.beadMat));
}

// ================================================================ camera
let flyAnim = null;
function fly(pos, target, ms = 1100) { flyAnim = { p0: camera.position.clone(), t0: controls.target.clone(), p1: pos, t1: target, start: performance.now(), ms }; }
function fitDist(r, k) {
  const vf = THREE.MathUtils.degToRad(camera.fov / 2), hf = Math.atan(Math.tan(vf) * camera.aspect);
  return (r / Math.sin(Math.min(vf, hf))) * k;
}
function homeView(animate) {
  const target = crownCenter.clone(); target.y *= 0.92;
  const pos = target.clone().add(new THREE.Vector3(0.55, 0.18, 1).normalize().multiplyScalar(fitDist(treeR, camera.aspect < 0.8 ? 0.85 : 0.82)));
  if (animate) fly(pos, target); else { flyAnim = null; camera.position.copy(pos); controls.target.copy(target); controls.update(); }
}
function subtreeSphere(i) {
  const b = new THREE.Box3();
  const step = Math.max(1, Math.floor(size[i] / 4000));
  for (let k = i; k < i + size[i]; k += step) {
    b.expandByPoint(v3.fromArray(end, k * 3));
    if (clusterR[k]) b.expandByPoint(v3.fromArray(clusterC, k * 3).addScalar(clusterR[k])).expandByPoint(v3.fromArray(clusterC, k * 3).addScalar(-clusterR[k]));
  }
  b.expandByPoint(v3.fromArray(start, i * 3));
  const s = new THREE.Sphere(); b.getBoundingSphere(s); return s;
}
function flyToNode(i) {
  const s = subtreeSphere(i);
  const viewDir = camera.position.clone().sub(controls.target).normalize();
  if (viewDir.y < 0.05) { viewDir.y = 0.15; viewDir.normalize(); }
  fly(s.center.clone().addScaledVector(viewDir, fitDist(Math.max(s.radius, 0.6), 0.95)), s.center.clone());
}

// ================================================================ labels
const labelsEl = $('labels');
const labelPool = new Map();
let shown = new Set();
const itemSub = (it) => (it.sci && it.sci !== it.label ? it.sci : (it.family || ''));
function buildCandidates() {
  candidates = [];
  for (let i = 0; i < N; i++) {
    const nm = NAME(i); if (!nm) continue;
    const kd = KIND(i);
    if (kd === 2) continue;                       // pruned tips are labelled through their list item
    if (kd === 1) { candidates.push({ i, kind: 'genus', pri: M.pruned ? 1 : 0.35 }); continue; }
    if (!M.pruned && M.n[i] < 15) continue;
    const fr = friendly(nm);
    candidates.push({ i, kind: nm.endsWith('aceae') ? 'fam' : 'clade', pri: fr ? 2.2 : nm.endsWith('aceae') ? 1.15 : nm.endsWith('ales') ? 1.1 : 0.9 });
  }
  hlNode.forEach((h, k) => { if (h !== undefined) candidates.push({ i: h, kind: 'item', pri: 50, it: items[k] }); });
}
function labelEl(c) {
  const key = c.kind === 'item' ? 'w' + items.indexOf(c.it) : c.i;
  let el = labelPool.get(key);
  if (!el) {
    el = document.createElement('div');
    const nm = NAME(c.i);
    const count = M.pruned ? `${fmt(M.n[c.i])} of yours` : `${fmt(M.n[c.i])} spp.`;
    let w;
    if (c.kind === 'item') {
      el.className = 'lab wall';
      el._wc = c.it.label.length * 6.4 + 18;
      el.innerHTML = `${esc(c.it.label)}<small>${esc(itemSub(c.it))}</small>`;
      w = Math.max(c.it.label.length * 7.5, itemSub(c.it).length * 6.2);
    } else {
      const fr = friendly(nm);
      el.className = 'lab ' + (c.kind === 'fam' ? 'fam' : '') + ((M.pruned ? M.n[c.i] >= M.total * 0.5 && M.total > 4 : M.n[c.i] > 20000) ? ' big' : '');
      el.innerHTML = fr ? `${esc(fr)}<small>${esc(nm)} · ${count}</small>` : `${esc(nm)}<small>${count}</small>`;
      w = Math.max((fr || nm).length * 8.5, ((fr ? nm + ' · ' : '') + count).length * 6.2);
    }
    el.addEventListener('click', (e) => { e.stopPropagation(); select(c.i, true, c.it); });
    el.addEventListener('dblclick', (e) => e.preventDefault());
    labelsEl.appendChild(el); labelPool.set(key, el);
    el._w = w + 18;
  }
  return el;
}
const P = new THREE.Vector3(), Q = new THREE.Vector3();
function updateLabels() {
  const W = innerWidth, H = innerHeight;
  const focal = H / 2 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const camPos = camera.position;
  const maxLabels = (IS_SMALL ? 16 : 34) + (M.pruned || focusOn ? 14 : 0);
  const cands = [];
  for (const c of candidates) {
    if (c.kind === 'item' ? !glowOn && !focusOn : !labelsOn || (focusOn && c.i !== selected)) continue;
    const i = c.i;
    if (c.kind === 'item') { if (!c.it.pos) continue; P.copy(c.it.pos); }
    else if (c.kind === 'genus' && clusterR[i]) P.fromArray(clusterC, i * 3);
    else { P.fromArray(start, i * 3).lerp(Q.fromArray(end, i * 3), 0.55); if (i === 0) P.set(0, end[1] * 0.5, 0); }
    const dist = P.distanceTo(camPos);
    Q.copy(P).project(camera);
    if (Q.z > 1 || Q.x < -1.05 || Q.x > 1.05 || Q.y < -1.05 || Q.y > 1.05) continue;
    const r = c.kind === 'genus' ? (clusterR[i] || radius[i]) * 0.6 : radius[i];
    const sr = (r * focal) / dist;
    let score;
    let compact = false;
    if (c.kind === 'item') {
      compact = !M.pruned && dist > treeR * 0.55 && i !== selected;
      score = compact && !focusOn ? 5 + 100 / dist : 1e6 / dist;   // far away: big clade names still win the space
    }
    else {
      const need = c.kind === 'genus' ? (M.pruned ? 6 : 14) : M.pruned ? 0.8 : 1.6;
      if (sr < need && i !== selected) continue;
      score = sr * c.pri + (i === selected ? 1e9 : 0);
    }
    cands.push({ c, x: (Q.x + 1) / 2 * W, y: (1 - Q.y) / 2 * H, score, compact });
  }
  cands.sort((a, b) => b.score - a.score);
  const placed = [], now = new Set();
  for (const k of cands) {
    if (placed.length >= maxLabels) break;
    const el = labelEl(k.c);
    el.classList.toggle('compact', k.compact);
    const w = k.compact ? el._wc : el._w, h = k.compact ? 20 : 38;
    const x0 = k.x - w / 2, y0 = k.y - h / 2;
    if (x0 < 4 || x0 + w > W - 4 || y0 < 60 || y0 + h > H - 8) continue;
    let ok = true;
    for (const p of placed) if (x0 < p[2] && x0 + w > p[0] && y0 < p[3] && y0 + h > p[1]) { ok = false; break; }
    if (!ok) continue;
    placed.push([x0, y0, x0 + w, y0 + h]);
    el.style.transform = `translate(${x0 | 0}px, ${y0 | 0}px)`;
    el.style.width = w + 'px'; el.style.textAlign = 'center';
    el.classList.toggle('sel', k.c.i === selected && k.c.kind !== 'item');
    el.classList.add('show'); now.add(el);
  }
  for (const el of shown) if (!now.has(el)) el.classList.remove('show');
  shown = now;
}

// ================================================================ picking
function pick(cx, cy, tol) {
  const W = innerWidth, H = innerHeight;
  const focal = H / 2 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const m = new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  const e = m.elements;
  const proj = (x, y, z, out) => {
    const w = e[3] * x + e[7] * y + e[11] * z + e[15];
    if (w <= 0.01) return false;
    out[0] = ((e[0] * x + e[4] * y + e[8] * z + e[12]) / w + 1) / 2 * W;
    out[1] = (1 - (e[1] * x + e[5] * y + e[9] * z + e[13]) / w) / 2 * H;
    out[2] = w; return true;
  };
  const a = [0, 0, 0], b = [0, 0, 0];
  // listed species beads first
  if (glowOn || focusOn) for (let k = 0; k < items.length; k++) {
    const it = items[k]; if (!it.pos || hlNode[k] === undefined || !proj(it.pos.x, it.pos.y, it.pos.z, a)) continue;
    if (Math.hypot(a[0] - cx, a[1] - cy) < tol + 8) return { i: hlNode[k], it };
  }
  let best = -1, bestD = Infinity;
  for (let i = 0; i < N; i++) {
    if (focusOn && items.length && !onPath[i]) continue;
    if (leavesOn && clusterR[i] && proj(clusterC[i * 3], clusterC[i * 3 + 1], clusterC[i * 3 + 2], a)) {
      const sr = clusterR[i] * focal / a[2];
      if (Math.hypot(a[0] - cx, a[1] - cy) < sr + tol && a[2] < bestD) { best = i; bestD = a[2]; }
    }
    const sx = i ? start[i * 3] : 0, sy = i ? start[i * 3 + 1] : 0, sz = i ? start[i * 3 + 2] : 0;
    if (!proj(sx, sy, sz, a) || !proj(end[i * 3], end[i * 3 + 1], end[i * 3 + 2], b)) continue;
    const dx = b[0] - a[0], dy = b[1] - a[1], l2 = dx * dx + dy * dy || 1;
    let t = ((cx - a[0]) * dx + (cy - a[1]) * dy) / l2; t = Math.max(0, Math.min(1, t));
    const depth = a[2] + (b[2] - a[2]) * t;
    const sr = radius[i] * focal / depth;
    if (Math.hypot(a[0] + dx * t - cx, a[1] + dy * t - cy) < sr + tol && depth < bestD) { best = i; bestD = depth; }
  }
  if (best < 0) return null;
  const it = M.item(best);
  return { i: best, it: it || undefined };
}
function namedAncestor(i) { let u = i; while (u > 0 && !NAME(u)) u = M.parent[u]; return u; }

// ================================================================ selection & panel
function select(i, flyIt, it) {
  if (selected >= 0 && selected < N) paintBark(selected, selected + size[selected], 0);
  selected = i;
  if (i < 0) { $('panel').classList.add('hidden'); if (leafMat) leafMat.uniforms.uSel.value.set(-1, -1); return; }
  paintBark(i, i + size[i], 1);
  leafMat.uniforms.uSel.value.set(i, i === 0 ? -1 : i + size[i]);
  renderPanel(i, it || M.item(i));
  if (IS_SMALL || !$('panel').classList.contains('hidden')) $('wall').classList.add('collapsed');
  if (flyIt) flyToNode(i);
}
function lineage(i) { const out = []; let u = M.parent[i]; while (u >= 0) { if (NAME(u)) out.push(u); u = M.parent[u]; } return out.reverse(); }
function namedDescendants(i, max) {
  const out = []; let frontier = [...kids[i]];
  while (frontier.length && out.length < 40) {
    const next = [];
    for (const k of frontier) { if (NAME(k) || KIND(k)) out.push(k); else next.push(...kids[k]); }
    frontier = next;
  }
  return out.sort((a, b) => M.n[b] - M.n[a]).slice(0, max);
}
function renderPanel(i, it) {
  const nm = NAME(i), fr = friendly(nm), bi = M.base(i), kd = KIND(i);
  const allSp = D.n[bi];
  const pct = (100 * allSp) / D.total;
  let html = '';
  if (it) {
    html += `<h2 class="wallhit">${esc(it.label)}</h2><div class="sci">${it.sci && it.sci !== it.label ? '<i>' + esc(it.sci) + '</i>' : ''}${it.family ? (it.sci && it.sci !== it.label ? ' · ' : '') + esc(it.family) : ''}</div>`;
    if (it.entries && it.entries.length > 1) html += `<h4>In this list</h4><ul class="kids">${it.entries.map((p) => `<li>${esc(p)}</li>`).join('')}</ul>`;
    if (it.note) html += `<div class="sci" style="margin-top:6px">${esc(it.note)}</div>`;
    html += `<h4>Placed on the tree at</h4>`;
  }
  const genusLike = kd === 1 || (kd === 2 && D.genus[bi]);
  const title = kd === 2 ? bName(bi) || 'clade' : genusLike ? nm : fr || nm || 'Unnamed clade';
  const titleHtml = genusLike ? `<i>${esc(title)}</i>` : esc(kd === 2 && friendly(title) ? friendly(title) : title);
  html += it ? `<div style="font-size:18px;font-family:var(--serif)">${titleHtml}</div>` : `<h2>${titleHtml}</h2>`;
  const sub = genusLike ? `Genus · ${esc(bFam(bi))}` : fr ? esc(nm) : nm ? '' : `within ${esc(display(namedAncestor(M.parent[i])))}`;
  if (sub) html += `<div class="sci">${sub}</div>`;
  html += `<div class="stat"><div><b>${fmt(allSp)}</b>species</div><div><b>${pct < 0.1 ? pct.toFixed(3) : pct.toFixed(1)}%</b>of ${esc((D.title || '').toLowerCase())}</div>${listCount[i] && !it ? `<div class="wallhit"><b>${listCount[i]}</b>in list</div>` : ''}</div>`;
  html += `<div class="bar"><i style="width:${Math.max(0.6, Math.sqrt(pct / 100) * 100)}%"></i></div>`;
  const lin = lineage(i);
  if (lin.length) html += `<h4>Lineage</h4><div class="crumbs">${lin.map((u) => `<a data-n="${u}">${esc(display(u))}</a>`).join(' › ')}</div>`;
  if (kd === 0) {
    const ds = namedDescendants(i, 8);
    if (ds.length) html += `<h4>${M.pruned ? 'Branches' : 'Biggest branches'}</h4><ul class="kids">${ds.map((u) => `<li><a data-n="${u}">${KIND(u) === 1 ? '<i>' + esc(NAME(u)) + '</i>' : esc(display(u))}</a>${listCount[u] && !M.pruned ? ' <b class="wallhit">✦</b>' : ''}<span>${fmt(M.n[u])}${M.pruned ? ' yours' : ''}</span></li>`).join('')}</ul>`;
  }
  if (listCount[i] && !it) {
    const ws = items.map((w, k) => ({ w, h: hlNode[k] })).filter((x) => x.h !== undefined && x.h >= i && x.h < i + size[i]);
    html += `<h4 class="wallhit">From ${esc(listTitle)}</h4><ul class="kids">${ws.slice(0, 60).map(({ w }) => `<li><a data-w="${items.indexOf(w)}">${esc(w.label)}</a><span><i>${esc(w.sci && w.sci !== w.label ? w.sci : '')}</i></span></li>`).join('')}${ws.length > 60 ? `<li><span>…and ${ws.length - 60} more</span></li>` : ''}</ul>`;
  }
  html += `<div class="acts"><button data-act="fly">Fly here</button>${i > 0 ? '<button data-act="up">Up a level</button>' : ''}</div>`;
  $('pBody').innerHTML = html;
  $('panel').classList.remove('hidden');
}
$('pBody').addEventListener('click', (e) => {
  const a = e.target.closest('[data-n],[data-w],[data-act]'); if (!a) return;
  if (a.dataset.n) select(+a.dataset.n, true);
  else if (a.dataset.w) { const k = +a.dataset.w; if (hlNode[k] !== undefined) select(hlNode[k], true, items[k]); }
  else if (a.dataset.act === 'fly') flyToNode(selected);
  else if (a.dataset.act === 'up') select(namedAncestor(M.parent[selected]), true);
});
$('pClose').onclick = () => select(-1);

// ================================================================ pointer
let down = null, lastTap = 0;
canvas.addEventListener('pointerdown', (e) => { down = { x: e.clientX, y: e.clientY, t: performance.now() }; });
canvas.addEventListener('pointerup', (e) => {
  if (!down) return;
  const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y);
  const dt = performance.now() - down.t; down = null;
  if (moved > 7 || dt > 600) return;
  const hit = pick(e.clientX, e.clientY, IS_TOUCH || e.pointerType === 'touch' ? 14 : 5);
  const now = performance.now();
  if (hit) select(hit.i, now - lastTap < 350 && hit.i === selected, hit.it);
  else if (now - lastTap > 350) select(-1);
  lastTap = now;
});
canvas.addEventListener('dblclick', (e) => e.preventDefault());
const tipEl = $('tip');
let hoverQueued = null;
canvas.addEventListener('pointermove', (e) => {
  if (e.pointerType !== 'mouse' || e.buttons) { tipEl.classList.add('hidden'); return; }
  hoverQueued = [e.clientX, e.clientY];
});
canvas.addEventListener('pointerleave', () => { hoverQueued = null; tipEl.classList.add('hidden'); });
function doHover() {
  if (!hoverQueued) return;
  const [x, y] = hoverQueued; hoverQueued = null;
  const hit = pick(x, y, 4);
  if (!hit) { tipEl.classList.add('hidden'); canvas.style.cursor = ''; return; }
  const i = hit.i;
  tipEl.innerHTML = hit.it ? `<b class="wallhit">${esc(hit.it.label)}</b><br><i>${esc(itemSub(hit.it))}</i>`
    : KIND(i) === 1 ? `<b><i>${esc(NAME(i))}</i></b> <i>· ${esc(FAM(i))}</i><br>${fmt(D.n[M.base(i)])} species`
      : `<b>${esc(display(i))}</b>${NAME(i) ? '' : ` <i>in ${esc(display(namedAncestor(i)))}</i>`}<br>${M.pruned ? `${fmt(M.n[i])} of your species · ` : ''}${fmt(D.n[M.base(i)])} species`;
  tipEl.style.left = Math.min(x + 14, innerWidth - 290) + 'px'; tipEl.style.top = y + 14 + 'px';
  tipEl.classList.remove('hidden'); canvas.style.cursor = 'pointer';
}

// ================================================================ search
function buildSearchIndex() {
  index = [];
  for (let i = 0; i < N; i++) {
    const nm = NAME(i); if (!nm || KIND(i) === 2) continue;
    index.push({ key: nm.toLowerCase(), label: nm, i, n: M.n[i], kind: KIND(i) === 1 ? 'genus' : 'clade' });
    const fr = friendly(nm); if (fr) index.push({ key: fr.toLowerCase(), label: fr, alt: nm, i, n: M.n[i], kind: 'clade' });
  }
  items.forEach((it, k) => { if (hlNode[k] !== undefined) index.push({ key: (it.label + ' ' + (it.sci || '')).toLowerCase(), label: it.label, alt: it.sci !== it.label ? it.sci : '', i: hlNode[k], n: 1e9, kind: 'item', it }); });
}
const qEl = $('q'), qRes = $('qres');
let qSel = 0, qItems = [];
qEl.addEventListener('input', () => {
  const q = qEl.value.trim().toLowerCase();
  if (q.length < 2) { qRes.classList.add('hidden'); return; }
  const pre = [], sub = [];
  for (const it of index) { const k = it.key.indexOf(q); if (k === 0) pre.push(it); else if (k > 0) sub.push(it); }
  qItems = [...pre.sort((a, b) => b.n - a.n), ...sub.sort((a, b) => b.n - a.n)].slice(0, 12);
  qSel = 0;
  qRes.innerHTML = qItems.map((it, k) => `<li data-k="${k}" class="${k === 0 ? 'act' : ''}"><span class="${it.kind === 'item' ? 'g' : ''}">${it.kind === 'genus' ? '<i>' + esc(it.label) + '</i>' : esc(it.label)}${it.alt ? ` <small>${esc(it.alt)}</small>` : ''}</span><small>${it.kind === 'item' ? '✦ list' : it.kind === 'genus' ? esc(FAM(it.i)) : fmt(it.n) + (M.pruned ? ' yours' : ' spp.')}</small></li>`).join('') || '<li><small>No match</small></li>';
  qRes.classList.remove('hidden');
});
function choose(it) { if (!it) return; qRes.classList.add('hidden'); qEl.value = ''; qEl.blur(); select(it.i, true, it.it); }
qRes.addEventListener('click', (e) => { const li = e.target.closest('li[data-k]'); if (li) choose(qItems[+li.dataset.k]); });
qEl.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    qSel = (qSel + (e.key === 'ArrowDown' ? 1 : -1) + qItems.length) % Math.max(1, qItems.length);
    [...qRes.children].forEach((li, k) => li.classList.toggle('act', k === qSel)); e.preventDefault();
  } else if (e.key === 'Enter') choose(qItems[qSel]);
  else if (e.key === 'Escape') { qRes.classList.add('hidden'); qEl.blur(); }
});
document.addEventListener('pointerdown', (e) => { if (!e.target.closest('.search')) qRes.classList.add('hidden'); });

// ================================================================ the species list
const PRESETS = D.presets || (D.highlight ? [{ id: 'wall', short: 'Highlighted', ...D.highlight }] : []);
function defaultList(id) {
  const p = PRESETS.find((x) => x.id === id) || PRESETS[0];
  if (!p) return { title: 'Highlighted', source: 'default', items: [] };
  return {
    title: p.title, source: 'preset', preset: p.id,
    items: p.items.map((h) => ({ label: h.plants[0].replace(/\s*\(.*?\)\s*/g, ' ').replace(/\s+/g, ' ').trim(), sci: h.name, family: h.family, at: h.at, entries: h.plants })),
  };
}
let presetId = '';
function usePreset(id) {
  pruneMode = false;
  const q = new URLSearchParams(location.search); q.delete('prune');
  if (id === PRESETS[0].id) q.delete('preset'); else q.set('preset', id);
  history.replaceState(null, '', location.pathname + (q.toString() ? '?' + q : ''));   // also drops any #list=
  setList(defaultList(id));
}
function renderPresets() {
  // top row: one chip per group (living wall, food plants…); second row: that group's sub-lists (fruit, berries…)
  const groups = [];
  for (const p of PRESETS) { const g = p.group || p.id; if (!groups.some((x) => x.g === g)) groups.push({ g, p }); }
  const cur = PRESETS.find((p) => p.id === presetId);
  const curG = cur ? cur.group || cur.id : '';
  let html = groups.map(({ g, p }) => `<button data-p="${esc(p.id)}" class="${g === curG ? 'on' : ''}">${esc(p.short || p.title)}</button>`).join('');
  const subs = PRESETS.filter((p) => curG && (p.group || p.id) === curG);
  if (subs.length > 1) html += `<div class="sub">${subs.map((p) => `<button data-p="${esc(p.id)}" class="${p.id === presetId ? 'on' : ''}">${esc(p.sub || p.short || p.title)}</button>`).join('')}</div>`;
  $('presets').innerHTML = PRESETS.length > 1 || listSource === 'user' ? `<span>Lists</span>${html}` : '';
  $('lPresets').innerHTML = groups.map(({ p }) => `<button class="ghost" data-p="${esc(p.id)}">Load ${esc(p.short || p.title).toLowerCase()}</button>`).join('');
}
$('presets').addEventListener('click', (e) => { const b = e.target.closest('[data-p]'); if (b) usePreset(b.dataset.p); });
$('lPresets').addEventListener('click', (e) => {
  const b = e.target.closest('[data-p]'); if (!b) return;
  const d = defaultList(b.dataset.p);
  lTitle.value = d.title;
  lText.value = d.items.map((it) => `${it.label} (${it.sci})`).join('\n');
});
let pruneMode = false;
function setList(list, { keepView } = {}) {
  items = list.items.filter((it) => it.at !== undefined && it.at !== null);
  listTitle = list.title || 'Your list'; listSource = list.source || 'user';
  presetId = list.source === 'preset' ? list.preset : '';
  if (!items.length) pruneMode = false;
  rebuild(keepView);
  renderListPanel();
}
function rebuild(keepView) {
  select(-1);
  M = pruneMode && items.length ? prunedModel(items) : fullModel();
  buildWorld();
  if (!keepView) homeView(false);
  $('bPrune').classList.toggle('on', pruneMode);
  $('nsp').textContent = fmt(M.pruned ? M.total : D.total);
  $('subtitle').lastChild.textContent = M.pruned ? ` of your species` : ' species';
}
function renderListPanel() {
  $('wallTitle').textContent = listTitle;
  $('wallN').textContent = `${items.length} taxa`;
  $('wallList').innerHTML = items.map((w, k) => `<li data-k="${k}">${esc(w.entries && w.entries.length > 1 ? w.entries.join(', ') : w.label)}<em>${esc([w.sci !== w.label ? w.sci : '', w.family].filter(Boolean).join(' · '))}</em></li>`).join('');
  $('wall').classList.toggle('hidden', !items.length && !PRESETS.length);
  renderPresets();
}
$('wallList').addEventListener('click', (e) => {
  const li = e.target.closest('li'); if (!li) return;
  const k = +li.dataset.k;
  [...$('wallList').children].forEach((x) => x.classList.toggle('act', x === li));
  if (hlNode[k] !== undefined) select(hlNode[k], true, items[k]);
});
$('wallHead').onclick = () => $('wall').classList.toggle('collapsed');
$('bPrune').onclick = () => { pruneMode = !pruneMode; rebuild(false); };
$('bEdit').onclick = () => openListModal();

// ---- list modal
const lText = $('lText'), lTitle = $('lTitle'), lStatus = $('lStatus'), lResult = $('lResult');
function openListModal() {
  $('listModal').classList.remove('hidden');
  if (listSource === 'user' && !lText.value) { lText.value = items.map((it) => it.raw || (it.label !== it.sci ? `${it.label} (${it.sci})` : it.sci)).join('\n'); lTitle.value = listTitle; }
  lResult.classList.add('hidden'); lStatus.textContent = '';
  setTimeout(() => lText.focus(), 50);
}
$('bList').onclick = openListModal;
$('lClose').onclick = () => $('listModal').classList.add('hidden');
$('listModal').addEventListener('click', (e) => { if (e.target.id === 'listModal') $('listModal').classList.add('hidden'); });
$('lFile').onchange = async (e) => {
  const f = e.target.files[0]; if (!f) return;
  lText.value = await f.text();
  if (!lTitle.value) lTitle.value = f.name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ');
  e.target.value = '';
};
$('lGo').onclick = async () => {
  const entries = parseList(lText.value);
  if (!entries.length) { lStatus.textContent = 'Paste at least one name.'; return; }
  $('lGo').disabled = true;
  lResult.classList.add('hidden');
  const res = await resolveEntries(entries, {
    genusIndex, cladeIndex, kingdom: KINGDOM, bFam,
    onProgress: (k, n) => { lStatus.textContent = `Looking up names… ${k} / ${n}`; },
  });
  $('lGo').disabled = false;
  const title = lTitle.value.trim() || 'My species';
  const matched = res.filter((r) => r.at !== undefined);
  const missed = res.filter((r) => r.at === undefined);
  lStatus.textContent = '';
  lResult.innerHTML = `<b>${matched.length}</b> of ${res.length} names placed on the tree.` +
    (missed.length ? `<div class="miss"><b>Not found:</b> ${missed.map((m) => esc(m.raw)).join(' · ')}</div>` : '') +
    (res.some((r) => r.note) ? `<div class="miss">${res.filter((r) => r.note).slice(0, 30).map((r) => `${esc(r.raw)} → ${esc(r.note)}`).join('<br>')}</div>` : '') +
    `<div class="acts"><button class="primary" id="lShow">Show on tree</button><button id="lShare">Copy share link</button></div>`;
  lResult.classList.remove('hidden');
  const list = { title, source: 'user', items: mergeDupes(matched) };
  $('lShow').onclick = () => { $('listModal').classList.add('hidden'); applyUserList(list); };
  $('lShare').onclick = async () => { await saveToHash(list); try { await navigator.clipboard.writeText(location.href); $('lShare').textContent = 'Copied ✓'; } catch { $('lShare').textContent = 'Link is in the address bar'; } };
  if (!missed.length) { $('listModal').classList.add('hidden'); applyUserList(list); }
};
function mergeDupes(rs) {
  const by = new Map();
  for (const r of rs) {
    const key = (r.sci || r.label).toLowerCase();
    if (by.has(key)) by.get(key).entries.push(r.label);
    else by.set(key, { label: r.label, sci: r.sci, family: r.family, at: r.at, place: r.place, note: r.note, raw: r.raw, entries: [r.label] });
  }
  return [...by.values()];
}
async function saveToHash(list) {
  const enc = await encodeList(list);
  history.replaceState(null, '', '#list=' + enc);
}
async function applyUserList(list) {
  pruneMode = false;
  setList(list);
  await saveToHash(list);
  $('wall').classList.remove('collapsed');
}
function placeAt(place) { if (!place) return undefined; const k = place.toLowerCase(); return genusIndex.has(k) ? genusIndex.get(k) : cladeIndex.get(k); }
async function listFromHash() {
  const m = location.hash.match(/list=([^&]+)/);
  if (!m) return null;
  const dec = await decodeList(m[1]);
  if (!dec) return null;
  return { title: dec.title, source: 'user', items: dec.items.map((x) => { const at = placeAt(x.place); return { ...x, at, family: at !== undefined ? (D.genus[at] ? bFam(at) : '') : '', entries: [x.label] }; }) };
}

// ================================================================ toolbar
const toggle = (id, fn) => { const b = $(id); b.onclick = () => { b.classList.toggle('on'); fn(b.classList.contains('on')); }; };
toggle('bWall', (on) => { glowOn = on; world.glow.visible = on; });
toggle('bLabels', (on) => { labelsOn = on; });
toggle('bLeaves', (on) => { leavesOn = on; world.leaves.visible = on; });
toggle('bSpin', (on) => { controls.autoRotate = on; });
toggle('bFocus', (on) => { focusOn = on; applyFocus(); });
$('bHome').onclick = () => { select(-1); homeView(true); };
if (window.self !== window.top) $('bFull').classList.remove('hidden');
$('bFull').onclick = (e) => { e.currentTarget.href = './' + location.hash; };
$('bAbout').onclick = () => $('about').classList.remove('hidden');
$('aClose').onclick = () => $('about').classList.add('hidden');
$('about').addEventListener('click', (e) => { if (e.target.id === 'about') $('about').classList.add('hidden'); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { $('about').classList.add('hidden'); $('listModal').classList.add('hidden'); } });

// ================================================================ resize & loop
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false); composer.setSize(w, h);
  bloom.resolution.set(w / 2, h / 2);
  camera.aspect = w / h; camera.updateProjectionMatrix();
  if (leafMat) leafMat.uniforms.uScale.value = leafScale();
  if (world && world.vine) world.vine.material.uniforms.uPx.value = pxPerUnit();
}
addEventListener('resize', resize);

// ---- boot
const fromHash = await listFromHash();
if (params.get('prune') !== null) pruneMode = true;
if (params.has('only')) focusOn = true;   // ?only → start in "your species only"
setList(fromHash && fromHash.items.some((x) => x.at !== undefined) ? fromHash : defaultList(params.get('preset')));
resize();
controls.autoRotate = !params.has('still');
let userTouched = false;
controls.addEventListener('start', () => { if (!userTouched) { userTouched = true; controls.autoRotate = $('bSpin').classList.contains('on'); } flyAnim = null; });
if (params.has('az')) {   // debug/deep-link: ?az=deg&el=deg&zoom=f
  const sph = new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
  sph.theta = THREE.MathUtils.degToRad(+params.get('az'));
  if (params.has('el')) sph.phi = THREE.MathUtils.degToRad(90 - +params.get('el'));
  sph.radius *= +(params.get('zoom') || 1);
  camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(sph)); controls.update();
}
if (!IS_SMALL) $('wall').classList.remove('collapsed');
addEventListener('hashchange', async () => { const l = await listFromHash(); if (l) setList(l); });

const clock = new THREE.Clock();
let frame = 0;
function loop() {
  const t = clock.getElapsedTime();
  if (flyAnim) {
    const k = Math.min(1, (performance.now() - flyAnim.start) / flyAnim.ms);
    const e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    camera.position.lerpVectors(flyAnim.p0, flyAnim.p1, e);
    controls.target.lerpVectors(flyAnim.t0, flyAnim.t1, e);
    if (k >= 1) flyAnim = null;
  }
  controls.update();
  leafMat.uniforms.uTime.value = t;
  const pulse = 0.82 + 0.18 * Math.sin(t * 2.2);
  world.sheen.material.opacity = pulse;
  world.beadMat.size = world.beadSize * (0.9 + 0.2 * Math.sin(t * 3.1));
  composer.render();
  if (frame++ % 2 === 0) updateLabels();
  doHover();
  requestAnimationFrame(loop);
}
loop();
$('loading').style.opacity = 0;
setTimeout(() => $('loading').remove(), 700);
if (params.get('focus')) {
  const q = params.get('focus').toLowerCase();
  const it = index.find((x) => x.key === q) || index.find((x) => x.key.startsWith(q)) || index.find((x) => x.key.includes(q));
  if (it) setTimeout(() => select(it.i, true, it.it), 300);
}
if (params.has('add')) openListModal();   // ?add → open the list box (handy share link: "make your own")
window.__evo = { D, get M() { return M; }, camera, controls, select, flyToNode, homeView, setList };
