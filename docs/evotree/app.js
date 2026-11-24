// Evo Tree Viewer — 3D phylogeny rendered as an oak.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { layoutTree, mulberry32 } from './layout.js';

const params = new URLSearchParams(location.search);
const DATA_URL = params.get('data') || 'data/land-plants.json';
const IS_TOUCH = matchMedia('(pointer: coarse)').matches;
const IS_SMALL = Math.min(innerWidth, innerHeight) < 720;
const $ = (id) => document.getElementById(id);
const fmt = (x) => x.toLocaleString('en-US');

// ---------------------------------------------------------------- data
const D = await (await fetch(DATA_URL)).json();
const N = D.parent.length;
const NAME = (i) => D.labels[D.label[i]] || '';
const FAM = (i) => D.labels[D.family[i]] || '';
const isGenus = (i) => D.genus[i] === 1;
const friendly = (nm) => D.friendly[nm] || '';
const display = (i) => {
  const nm = NAME(i);
  if (!nm) return 'Unnamed clade';
  return friendly(nm) || nm;
};
const L = layoutTree(D.parent, D.n);
const { start, end, dir, radius, size, kids } = L;
$('nsp').textContent = fmt(D.total);
$('subtitle').firstChild.textContent = (D.title || 'Tree') + ' · ';

// living-wall path
const wallItems = (D.highlight && D.highlight.items) || [];
const onPath = new Uint8Array(N);
for (const h of wallItems) { let u = h.at; while (u >= 0 && !onPath[u]) { onPath[u] = 1; u = D.parent[u]; } }
const wallCount = new Int32Array(N);   // # wall species in subtree
for (const h of wallItems) { let u = h.at; while (u >= 0) { wallCount[u]++; u = D.parent[u]; } }

// ---------------------------------------------------------------- three setup
const canvas = $('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: !IS_SMALL, powerPreference: 'high-performance' });
const DPR = Math.min(devicePixelRatio || 1, IS_SMALL ? 1.75 : 2);
renderer.setPixelRatio(DPR);
renderer.setSize(innerWidth, innerHeight, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.05, 4000);

// bounding box of the crown
const bb = new THREE.Box3();
const v3 = new THREE.Vector3();
for (let i = 0; i < N; i++) bb.expandByPoint(v3.fromArray(end, i * 3));
bb.expandByPoint(new THREE.Vector3(0, 0, 0));
const crownCenter = bb.getCenter(new THREE.Vector3());
const crownSize = bb.getSize(new THREE.Vector3());
const treeR = crownSize.length() / 2;

// sky gradient
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
scene.fog = new THREE.Fog(FOG, treeR * 1.6, treeR * 5.5);

scene.add(new THREE.HemisphereLight(0xbcd3e6, 0x3a2e22, 1.35));
const sun = new THREE.DirectionalLight(0xffe2b8, 2.4);
sun.position.set(-0.6, 1, 0.45).multiplyScalar(100);
scene.add(sun);
const SUN_DIR = sun.position.clone().normalize();

// ground: soft mossy disc
{
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const g = c.getContext('2d'), gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  gr.addColorStop(0, 'rgba(20,28,18,1)'); gr.addColorStop(0.35, 'rgba(32,44,28,0.9)');
  gr.addColorStop(0.75, 'rgba(36,46,38,0.35)'); gr.addColorStop(1, 'rgba(40,50,50,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.CircleGeometry(treeR * 1.5, 64), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, fog: false }));
  m.rotation.x = -Math.PI / 2; m.position.set(crownCenter.x, -0.01, crownCenter.z); scene.add(m);
}

// ---------------------------------------------------------------- bark geometry
const BARK_DARK = new THREE.Color('#3b3028'), BARK_TWIG = new THREE.Color('#5b4a3a');
const BARK_SEL = new THREE.Color('#c9b48a'), BARK_PATH = new THREE.Color('#c08a3a');
const vStart = new Int32Array(N + 1);
const rnd = mulberry32(11);

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
  const p = D.parent[i];
  const pd = v3.fromArray(dir, p * 3);
  S.fromArray(start, i * 3).addScaledVector(pd, -Math.min(radius[p] * 0.8, L.len[p] * 0.3));
  C.copy(S).addScaledVector(pd, L.len[i] * 0.35).lerp(E, 0.25);
}
function bez(S, C, E, t, P, T) {
  const mt = 1 - t;
  P.set(mt * mt * S.x + 2 * mt * t * C.x + t * t * E.x, mt * mt * S.y + 2 * mt * t * C.y + t * t * E.y, mt * mt * S.z + 2 * mt * t * C.z + t * t * E.z);
  if (T) T.set(2 * mt * (C.x - S.x) + 2 * t * (E.x - C.x), 2 * mt * (C.y - S.y) + 2 * t * (E.y - C.y), 2 * mt * (C.z - S.z) + 2 * t * (E.z - C.z)).normalize();
}
let nVert = 0, nIdx = 0;
for (let i = 0; i < N; i++) { const [a, s] = tubeSpec(i); vStart[i] = nVert; nVert += a * (s + 1); nIdx += a * s * 6; }
vStart[N] = nVert;
const bPos = new Float32Array(nVert * 3), bNor = new Float32Array(nVert * 3), bCol = new Float32Array(nVert * 3);
const bIdx = new Uint32Array(nIdx);
const baseCol = new Float32Array(N * 3);
{
  let vi = 0, ii = 0;
  const S = new THREE.Vector3(), E = new THREE.Vector3(), C = new THREE.Vector3(), P = new THREE.Vector3(), T = new THREE.Vector3();
  const U = new THREE.Vector3(), V = new THREE.Vector3(), ref = new THREE.Vector3(), prevU = new THREE.Vector3();
  for (let i = 0; i < N; i++) {
    const [radial, segs] = tubeSpec(i);
    const p = D.parent[i];
    branchCurve(i, S, C, E);
    const r1 = radius[i];
    const r0 = i === 0 ? r1 * 1.55 : Math.min(radius[p], r1 * 1.12);
    // per-branch colour: thick = dark bark, thin = warmer twig
    const tw = Math.min(1, Math.max(0, (0.12 - r1) / 0.12));
    const col = BARK_DARK.clone().lerp(BARK_TWIG, tw);
    col.offsetHSL(0, 0, (rnd() - 0.5) * 0.04);
    if (onPath[i]) col.lerp(BARK_PATH, 0.4);
    baseCol[i * 3] = col.r; baseCol[i * 3 + 1] = col.g; baseCol[i * 3 + 2] = col.b;
    const base = vi;
    for (let s = 0; s <= segs; s++) {
      const t = s / segs;
      bez(S, C, E, t, P, T);
      if (s === 0) {
        ref.set(0, 1, 0); if (Math.abs(T.y) > 0.9) ref.set(1, 0, 0);
        U.crossVectors(T, ref).normalize();
      } else { U.copy(prevU).addScaledVector(T, -prevU.dot(T)).normalize(); }   // parallel transport
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
    for (let s = 0; s < segs; s++) for (let a = 0; a < radial; a++) {
      const a1 = (a + 1) % radial;
      const i0 = base + s * radial + a, i1 = base + s * radial + a1, i2 = base + (s + 1) * radial + a, i3 = base + (s + 1) * radial + a1;
      bIdx[ii++] = i0; bIdx[ii++] = i2; bIdx[ii++] = i1; bIdx[ii++] = i1; bIdx[ii++] = i2; bIdx[ii++] = i3;
    }
  }
}
const barkGeo = new THREE.BufferGeometry();
barkGeo.setAttribute('position', new THREE.BufferAttribute(bPos, 3));
barkGeo.setAttribute('normal', new THREE.BufferAttribute(bNor, 3));
const bColAttr = new THREE.BufferAttribute(bCol, 3); bColAttr.setUsage(THREE.DynamicDrawUsage);
barkGeo.setAttribute('color', bColAttr);
barkGeo.setIndex(new THREE.BufferAttribute(bIdx, 1));
const bark = new THREE.Mesh(barkGeo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.92, metalness: 0 }));
scene.add(bark);

function paintBark(i0, i1, mode) {   // mode: 0 base, 1 selected
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

// ---------------------------------------------------------------- glow (living-wall lineages)
const glowGroup = new THREE.Group(); scene.add(glowGroup);
const GLOW = new THREE.Color(3.2, 2.1, 0.75);
{
  const segs = [];
  for (let i = 0; i < N; i++) if (onPath[i]) segs.push(i);
  const pos = [], idx = [], col = [], lp = [];
  const S = new THREE.Vector3(), C = new THREE.Vector3(), E = new THREE.Vector3(), P = new THREE.Vector3(), T = new THREE.Vector3();
  const U = new THREE.Vector3(), V = new THREE.Vector3(), ref = new THREE.Vector3(), prev = new THREE.Vector3();
  for (const i of segs) {
    branchCurve(i, S, C, E);
    const p = D.parent[i];
    const r1 = radius[i], r0 = i === 0 ? r1 : Math.min(radius[p], r1 * 1.12);
    const segsN = Math.max(2, tubeSpec(i)[1]), radial = 8, base = pos.length / 3;
    // thin twigs glow brightly; thick limbs only get a warm sheen so the trunk doesn't blow out
    const k = 0.05 + 0.95 * Math.pow(Math.max(0, 1 - r1 / 0.15), 1.5);
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
      if (s > 0 && r1 < 0.15) lp.push(prev.x, prev.y, prev.z, P.x, P.y, P.z);
      prev.copy(P);
    }
    for (let s = 0; s < segsN; s++) for (let a = 0; a < radial; a++) {
      const a1 = (a + 1) % radial, o = base + s * radial;
      idx.push(o + a, o + radial + a, o + a1, o + a1, o + radial + a, o + radial + a1);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.setIndex(idx);
  const m = new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, opacity: 1, depthWrite: false, blending: THREE.AdditiveBlending, fog: false });
  glowGroup.add(new THREE.Mesh(g, m));
  // hairline that stays visible at any zoom (blooms into a glowing thread)
  const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(lp, 3));
  glowGroup.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: new THREE.Color(2.2, 1.5, 0.55), transparent: true, opacity: 0.9, depthWrite: false, blending: THREE.AdditiveBlending, fog: false })));
}

// ---------------------------------------------------------------- leaves: one point per species
const GROUP_HSL = {
  A: [0.27, 0.42, 0.33], Polypodiophyta: [0.40, 0.38, 0.33], Bryophyta: [0.21, 0.55, 0.38],
  Marchantiophyta: [0.18, 0.42, 0.32], Anthocerotophyta: [0.15, 0.45, 0.36], Lycopodiophyta: [0.36, 0.42, 0.28],
  Pinophyta: [0.44, 0.32, 0.24], Cycadophyta: [0.32, 0.38, 0.27], Ginkgophyta: [0.13, 0.85, 0.52],
};
const tips = [];
for (let i = 0; i < N; i++) if (isGenus(i) && D.n[i] > 0) tips.push(i);
const nLeaves = tips.reduce((a, i) => a + D.n[i], 0);
const lPos = new Float32Array(nLeaves * 3), lCol = new Float32Array(nLeaves * 3), lSize = new Float32Array(nLeaves), lAng = new Float32Array(nLeaves), lNode = new Float32Array(nLeaves);
const clusterR = new Float32Array(N), clusterC = new Float32Array(N * 3);
{
  const r = mulberry32(3); const col = new THREE.Color(); let k = 0;
  for (const i of tips) {
    const n = D.n[i];
    const grp = D.groups[FAM(i)] || 'A';
    const [h, s, l] = GROUP_HSL[grp] || GROUP_HSL.A;
    const hj = (r() - 0.5) * 0.05, sj = (r() - 0.5) * 0.12;
    const rho = 0.09 + 0.1 * Math.cbrt(n);
    const dx = dir[i * 3], dy = dir[i * 3 + 1], dz = dir[i * 3 + 2];
    const cx = end[i * 3] + dx * rho * 0.7, cy = end[i * 3 + 1] + dy * rho * 0.7 + rho * 0.15, cz = end[i * 3 + 2] + dz * rho * 0.7;
    clusterR[i] = rho; clusterC[i * 3] = cx; clusterC[i * 3 + 1] = cy; clusterC[i * 3 + 2] = cz;
    for (let j = 0; j < n; j++, k++) {
      // point in a slightly flattened ball, denser toward the shell
      let x, y, z, q; do { x = r() * 2 - 1; y = r() * 2 - 1; z = r() * 2 - 1; q = x * x + y * y + z * z; } while (q > 1 || q < 0.04);
      const sh = Math.pow(q, 0.15);
      lPos[k * 3] = cx + x * rho * sh; lPos[k * 3 + 1] = cy + y * rho * sh * 0.75; lPos[k * 3 + 2] = cz + z * rho * sh;
      col.setHSL(h + hj + (r() - 0.5) * 0.02, Math.min(1, s + sj), l * (0.8 + r() * 0.45));
      lCol[k * 3] = col.r; lCol[k * 3 + 1] = col.g; lCol[k * 3 + 2] = col.b;
      lSize[k] = 0.11 * (0.7 + r() * 0.6); lAng[k] = r() * Math.PI * 2; lNode[k] = i;
    }
  }
}
const leafGeo = new THREE.BufferGeometry();
leafGeo.setAttribute('position', new THREE.BufferAttribute(lPos, 3));
leafGeo.setAttribute('color', new THREE.BufferAttribute(lCol, 3));
leafGeo.setAttribute('size', new THREE.BufferAttribute(lSize, 1));
leafGeo.setAttribute('ang', new THREE.BufferAttribute(lAng, 1));
leafGeo.setAttribute('node', new THREE.BufferAttribute(lNode, 1));
const leafMat = new THREE.ShaderMaterial({
  uniforms: {
    uScale: { value: 1 }, uTime: { value: 0 }, uSel: { value: new THREE.Vector2(-1, -1) },
    uSun: { value: SUN_DIR }, uCenter: { value: crownCenter }, uR: { value: treeR },
    uFog: { value: FOG }, uFogNear: { value: scene.fog.near }, uFogFar: { value: scene.fog.far },
  },
  vertexShader: /* glsl */`
    attribute float size; attribute float ang; attribute float node; attribute vec3 color;
    uniform float uScale, uTime, uR; uniform vec2 uSel; uniform vec3 uSun, uCenter;
    varying vec3 vCol; varying float vAng, vDim, vFogD;
    void main() {
      vec3 p = position;
      float w = sin(uTime * 1.3 + p.x * 0.7 + p.z * 0.5) * 0.012 + sin(uTime * 2.1 + p.y * 1.3) * 0.006;
      p.x += w; p.z += w * 0.6;
      vec4 mv = modelViewMatrix * vec4(p, 1.0);
      gl_Position = projectionMatrix * mv;
      float px = size * uScale / -mv.z;
      gl_PointSize = clamp(px, 1.6, 90.0);
      vec3 rel = normalize(p - uCenter);
      float lit = 0.62 + 0.5 * max(dot(rel, uSun), 0.0) + 0.18 * clamp((p.y - uCenter.y) / uR, -1.0, 1.0);
      vCol = color * lit;
      vAng = ang;
      vDim = (uSel.y > 0.0 && (node < uSel.x || node >= uSel.y)) ? 1.0 : 0.0;
      vFogD = -mv.z;
    }`,
  fragmentShader: /* glsl */`
    uniform vec3 uFog; uniform float uFogNear, uFogFar;
    varying vec3 vCol; varying float vAng, vDim, vFogD;
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
      gl_FragColor = vec4(mix(col, uFog, f), 1.0);
      #include <colorspace_fragment>
    }`,
});
const leaves = new THREE.Points(leafGeo, leafMat);
leaves.frustumCulled = false;
scene.add(leaves);

// ---------------------------------------------------------------- wall beads (highlighted species tips)
const beadPos = [], beadOf = [];
{
  const byNode = {};
  for (const h of wallItems) (byNode[h.at] = byNode[h.at] || []).push(h);
  for (const at in byNode) {
    const i = +at, hs = byNode[at];
    const rho = clusterR[i] || radius[i] * 3 + 0.3;
    const c = clusterR[i] ? new THREE.Vector3().fromArray(clusterC, i * 3) : new THREE.Vector3().fromArray(end, i * 3);
    const d = new THREE.Vector3().fromArray(dir, i * 3);
    hs.forEach((h, j) => {
      const a = j * 2.4, off = new THREE.Vector3(Math.cos(a), 0.4, Math.sin(a)).multiplyScalar(rho * 0.55);
      const p = c.clone().addScaledVector(d, rho * 0.85).add(hs.length > 1 ? off : new THREE.Vector3());
      beadPos.push(p); beadOf.push(h); h.pos = p;
    });
  }
}
const beadTex = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,230,160,0.9)'); gr.addColorStop(1, 'rgba(255,180,60,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
})();
const beadGeo = new THREE.BufferGeometry().setFromPoints(beadPos);
const beadMat = new THREE.PointsMaterial({ map: beadTex, color: GLOW, size: 1.4, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, sizeAttenuation: true });
const beads = new THREE.Points(beadGeo, beadMat);
glowGroup.add(beads);

// ---------------------------------------------------------------- post-processing
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth / 2, innerHeight / 2), 0.7, 0.45, 0.95);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// ---------------------------------------------------------------- controls & camera
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.08;
controls.minDistance = 0.4; controls.maxDistance = treeR * 6;
controls.maxPolarAngle = Math.PI * 0.53;
controls.zoomSpeed = 1.1; controls.rotateSpeed = IS_TOUCH ? 0.7 : 0.9;
controls.autoRotateSpeed = 0.35;
function homeView(animate) {
  const target = crownCenter.clone(); target.y *= 0.92;
  const vf = THREE.MathUtils.degToRad(camera.fov / 2), hf = Math.atan(Math.tan(vf) * camera.aspect);
  const dist = (treeR / Math.sin(Math.min(vf, hf))) * (camera.aspect < 0.8 ? 0.85 : 0.82);
  const pos = target.clone().add(new THREE.Vector3(0.55, 0.18, 1).normalize().multiplyScalar(dist));
  if (animate) fly(pos, target); else { camera.position.copy(pos); controls.target.copy(target); controls.update(); }
}
homeView(false);
controls.autoRotate = !params.has('still');
if (params.has('az')) {   // debug/deep-link: ?az=deg&el=deg&zoom=f
  const off = camera.position.clone().sub(controls.target);
  const sph = new THREE.Spherical().setFromVector3(off);
  sph.theta = THREE.MathUtils.degToRad(+params.get('az'));
  if (params.has('el')) sph.phi = THREE.MathUtils.degToRad(90 - +params.get('el'));
  sph.radius *= +(params.get('zoom') || 1);
  camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(sph)); controls.update();
}
let userTouched = false;
controls.addEventListener('start', () => { if (!userTouched) { userTouched = true; controls.autoRotate = $('bSpin').classList.contains('on'); } cancelFly(); });

let flyAnim = null;
function fly(pos, target, ms = 1100) {
  flyAnim = { p0: camera.position.clone(), t0: controls.target.clone(), p1: pos, t1: target, start: performance.now(), ms };
}
function cancelFly() { flyAnim = null; }
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
  const r = Math.max(s.radius, 0.6);
  const vf = THREE.MathUtils.degToRad(camera.fov / 2), hf = Math.atan(Math.tan(vf) * camera.aspect);
  const dist = r / Math.sin(Math.min(vf, hf)) * 0.95;
  const viewDir = camera.position.clone().sub(controls.target).normalize();
  // keep current heading but avoid looking from below
  if (viewDir.y < 0.05) { viewDir.y = 0.15; viewDir.normalize(); }
  fly(s.center.clone().addScaledVector(viewDir, dist), s.center.clone());
}

// ---------------------------------------------------------------- labels
const labelsEl = $('labels');
const candidates = [];
for (let i = 0; i < N; i++) {
  const nm = NAME(i);
  if (!nm) continue;
  if (isGenus(i)) { candidates.push({ i, kind: 'genus', pri: 0.35 }); continue; }
  if (D.n[i] < 15) continue;
  const fr = friendly(nm);
  candidates.push({ i, kind: nm.endsWith('aceae') ? 'fam' : 'clade', pri: fr ? 2.2 : nm.endsWith('aceae') ? 1.15 : nm.endsWith('ales') ? 1.1 : 0.9 });
}
for (const h of wallItems) candidates.push({ i: h.at, kind: 'wall', pri: 50, h });
const labelPool = new Map();
let labelsOn = true, wallOn = true, selected = -1;
function labelEl(c) {
  const key = c.kind === 'wall' ? 'w' + c.h.name : c.i;
  let el = labelPool.get(key);
  if (!el) {
    el = document.createElement('div');
    const nm = NAME(c.i);
    if (c.kind === 'wall') {
      el.className = 'lab wall';
      el.innerHTML = `${esc(c.h.plants[0].replace(/\s*\(.*?\)\s*/g, ' ').trim())}<small>${esc(c.h.name)}</small>`;
    } else {
      const fr = friendly(nm);
      el.className = 'lab ' + (c.kind === 'fam' ? 'fam' : '') + (D.n[c.i] > 20000 ? ' big' : '');
      el.innerHTML = fr ? `${esc(fr)}<small>${esc(nm)} · ${fmt(D.n[c.i])} spp.</small>` : `${esc(nm)}<small>${fmt(D.n[c.i])} spp.</small>`;
    }
    el.addEventListener('click', (e) => { e.stopPropagation(); select(c.i, true); });
    labelsEl.appendChild(el); labelPool.set(key, el);
    el._w = Math.max(nm.length, (friendly(nm) || '').length, c.kind === 'wall' ? c.h.plants[0].length * 0.85 : 0) * 8 + 16;
  }
  return el;
}
const esc = (s) => String(s).replace(/[&<>"]/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const P = new THREE.Vector3(), Q = new THREE.Vector3();
let shown = new Set();
function updateLabels() {
  const W = innerWidth, H = innerHeight;
  const focal = H / 2 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const camPos = camera.position;
  const maxLabels = IS_SMALL ? 16 : 34;
  const cands = [];
  for (const c of candidates) {
    if (!labelsOn && c.kind !== 'wall') continue;
    if (c.kind === 'wall' && !wallOn) continue;
    const i = c.i;
    if (c.kind === 'wall') P.copy(c.h.pos);
    else if (c.kind === 'genus' && clusterR[i]) P.fromArray(clusterC, i * 3);
    else { P.fromArray(start, i * 3).lerp(Q.fromArray(end, i * 3), 0.55); if (i === 0) P.set(0, end[1] * 0.5, 0); }
    const dist = P.distanceTo(camPos);
    Q.copy(P).project(camera);
    if (Q.z > 1 || Q.x < -1.05 || Q.x > 1.05 || Q.y < -1.05 || Q.y > 1.05) continue;
    const r = c.kind === 'genus' ? (clusterR[i] || radius[i]) * 0.6 : radius[i];
    const sr = (r * focal) / dist;
    let score;
    if (c.kind === 'wall') { if (dist > treeR * 1.2 && i !== selected) continue; score = 1e6 / dist; }
    else {
      const need = c.kind === 'genus' ? 14 : 1.6;
      if (sr < need && i !== selected) continue;
      score = sr * c.pri + (i === selected ? 1e9 : 0);
    }
    cands.push({ c, x: (Q.x + 1) / 2 * W, y: (1 - Q.y) / 2 * H, score, dist });
  }
  cands.sort((a, b) => b.score - a.score);
  const placed = [], now = new Set();
  for (const k of cands) {
    if (placed.length >= maxLabels) break;
    const el = labelEl(k.c);
    const w = el._w, h = 38;
    const x0 = k.x - w / 2, y0 = k.y - h / 2;
    if (x0 < 4 || x0 + w > W - 4 || y0 < 60 || y0 + h > H - 8) continue;
    let ok = true;
    for (const p of placed) if (x0 < p[2] && x0 + w > p[0] && y0 < p[3] && y0 + h > p[1]) { ok = false; break; }
    if (!ok) continue;
    placed.push([x0, y0, x0 + w, y0 + h]);
    el.style.transform = `translate(${(k.x - w / 2) | 0}px, ${(k.y - h / 2) | 0}px)`;
    el.style.width = w + 'px'; el.style.textAlign = 'center';
    el.classList.toggle('sel', k.c.i === selected && k.c.kind !== 'wall');
    el.classList.add('show'); now.add(el);
  }
  for (const el of shown) if (!now.has(el)) el.classList.remove('show');
  shown = now;
}

// ---------------------------------------------------------------- picking
function pick(cx, cy, tol) {
  const W = innerWidth, H = innerHeight;
  const focal = H / 2 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const m = new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  const e = m.elements, cp = camera.position;
  const proj = (x, y, z, out) => {
    const w = e[3] * x + e[7] * y + e[11] * z + e[15];
    if (w <= 0.01) return false;
    out[0] = ((e[0] * x + e[4] * y + e[8] * z + e[12]) / w + 1) / 2 * W;
    out[1] = (1 - (e[1] * x + e[5] * y + e[9] * z + e[13]) / w) / 2 * H;
    out[2] = w; return true;
  };
  const a = [0, 0, 0], b = [0, 0, 0];
  let best = -1, bestD = Infinity;
  for (let i = 0; i < N; i++) {
    // leaf clusters
    if (leaves.visible && clusterR[i]) {
      if (proj(clusterC[i * 3], clusterC[i * 3 + 1], clusterC[i * 3 + 2], a)) {
        const sr = clusterR[i] * focal / a[2];
        const d = Math.hypot(a[0] - cx, a[1] - cy);
        if (d < sr + tol && a[2] < bestD) { best = i; bestD = a[2]; }
      }
    }
    const sx = i ? start[i * 3] : 0, sy = i ? start[i * 3 + 1] : 0, sz = i ? start[i * 3 + 2] : 0;
    if (!proj(sx, sy, sz, a) || !proj(end[i * 3], end[i * 3 + 1], end[i * 3 + 2], b)) continue;
    const dx = b[0] - a[0], dy = b[1] - a[1], l2 = dx * dx + dy * dy || 1;
    let t = ((cx - a[0]) * dx + (cy - a[1]) * dy) / l2; t = Math.max(0, Math.min(1, t));
    const px = a[0] + dx * t, py = a[1] + dy * t, depth = a[2] + (b[2] - a[2]) * t;
    const sr = radius[i] * focal / depth;
    const d = Math.hypot(px - cx, py - cy);
    if (d < sr + tol && depth < bestD) { best = i; bestD = depth; }
  }
  // wall beads take precedence
  for (const h of wallItems) {
    if (!wallOn || !h.pos || !proj(h.pos.x, h.pos.y, h.pos.z, a)) continue;
    if (Math.hypot(a[0] - cx, a[1] - cy) < tol + 6 && a[2] < bestD + 2) return { i: h.at, h };
  }
  return best >= 0 ? { i: best } : null;
}
function namedAncestor(i) { let u = i; while (u > 0 && !NAME(u)) u = D.parent[u]; return u; }

// ---------------------------------------------------------------- selection & panel
function select(i, flyIt, h) {
  if (selected >= 0) paintBark(selected, selected + size[selected], 0);
  selected = i;
  if (i < 0) { $('panel').classList.add('hidden'); leafMat.uniforms.uSel.value.set(-1, -1); return; }
  paintBark(i, i + size[i], 1);
  leafMat.uniforms.uSel.value.set(i, i === 0 ? -1 : i + size[i]);
  renderPanel(i, h);
  $('wall').classList.add('collapsed');
  if (flyIt) flyToNode(i);
}
function lineage(i) { const out = []; let u = D.parent[i]; while (u >= 0) { if (NAME(u)) out.push(u); u = D.parent[u]; } return out.reverse(); }
function namedDescendants(i, max) {
  const out = []; let frontier = [...kids[i]];
  while (frontier.length && out.length < 40) {
    const next = [];
    for (const k of frontier) { if (NAME(k) || isGenus(k)) out.push(k); else next.push(...kids[k]); }
    frontier = next;
  }
  return out.sort((a, b) => D.n[b] - D.n[a]).slice(0, max);
}
function renderPanel(i, h) {
  const nm = NAME(i), fr = friendly(nm);
  const pct = (100 * D.n[i]) / D.total;
  let html = '';
  if (h) {
    html += `<h2 class="wallhit">${esc(h.plants[0])}</h2><div class="sci">${esc(h.name)}${h.family ? ' · ' + esc(h.family) : ''}</div>`;
    if (h.plants.length > 1) html += `<h4>In the wall</h4><ul class="kids">${h.plants.map((p) => `<li>${esc(p)}</li>`).join('')}</ul>`;
    html += `<h4>Its ${isGenus(i) ? 'genus' : 'clade'}</h4>`;
  }
  const title = isGenus(i) ? nm : (fr || nm || 'Unnamed clade');
  html += h ? `<div style="font-size:18px;font-family:var(--serif)">${esc(title)}</div>` : `<h2>${isGenus(i) ? '<i>' + esc(nm) + '</i>' : esc(title)}</h2>`;
  const sub = isGenus(i) ? `Genus · ${esc(FAM(i))}` : fr ? esc(nm) : nm ? '' : `within ${esc(display(namedAncestor(D.parent[i])))}`;
  if (sub) html += `<div class="sci">${sub}</div>`;
  html += `<div class="stat"><div><b>${fmt(D.n[i])}</b>species</div><div><b>${pct < 0.1 ? pct.toFixed(3) : pct.toFixed(1)}%</b>of ${esc((D.title || '').toLowerCase())}</div>${wallCount[i] ? `<div class="wallhit"><b>${wallCount[i]}</b>in my wall</div>` : ''}</div>`;
  html += `<div class="bar"><i style="width:${Math.max(0.6, Math.sqrt(pct / 100) * 100)}%"></i></div>`;
  const lin = lineage(i);
  if (lin.length) html += `<h4>Lineage</h4><div class="crumbs">${lin.map((u) => `<a data-n="${u}">${esc(display(u))}</a>`).join(' › ')}</div>`;
  if (!isGenus(i)) {
    const ds = namedDescendants(i, 8);
    if (ds.length) html += `<h4>Biggest branches</h4><ul class="kids">${ds.map((u) => `<li><a data-n="${u}">${isGenus(u) ? '<i>' + esc(NAME(u)) + '</i>' : esc(display(u))}</a>${wallCount[u] ? ' <b class="wallhit">✦</b>' : ''}<span>${fmt(D.n[u])}</span></li>`).join('')}</ul>`;
  }
  if (wallCount[i] && !h) {
    const ws = wallItems.filter((w) => w.at >= i && w.at < i + size[i]);
    html += `<h4 class="wallhit">From my living wall</h4><ul class="kids">${ws.map((w) => `<li><a data-w="${esc(w.name)}">${esc(w.plants[0])}</a><span><i>${esc(w.name)}</i></span></li>`).join('')}</ul>`;
  }
  html += `<div class="acts"><button data-act="fly">Fly here</button>${i > 0 ? '<button data-act="up">Up a level</button>' : ''}</div>`;
  $('pBody').innerHTML = html;
  $('panel').classList.remove('hidden');
}
$('pBody').addEventListener('click', (e) => {
  const a = e.target.closest('[data-n],[data-w],[data-act]'); if (!a) return;
  if (a.dataset.n) select(+a.dataset.n, true);
  else if (a.dataset.w) { const w = wallItems.find((x) => x.name === a.dataset.w); if (w) select(w.at, true, w); }
  else if (a.dataset.act === 'fly') flyToNode(selected);
  else if (a.dataset.act === 'up') select(namedAncestor(D.parent[selected]), true);
});
$('pClose').onclick = () => select(-1);

// ---------------------------------------------------------------- pointer handling
let down = null, lastTap = 0;
canvas.addEventListener('pointerdown', (e) => { down = { x: e.clientX, y: e.clientY, t: performance.now() }; });
canvas.addEventListener('pointerup', (e) => {
  if (!down) return;
  const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y);
  const dt = performance.now() - down.t; down = null;
  if (moved > 7 || dt > 600) return;
  const hit = pick(e.clientX, e.clientY, IS_TOUCH || e.pointerType === 'touch' ? 14 : 5);
  const now = performance.now();
  if (hit) {
    const dbl = now - lastTap < 350 && hit.i === selected;
    select(hit.i, dbl, hit.h);
  } else if (now - lastTap > 350) select(-1);
  lastTap = now;
});
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
  tipEl.innerHTML = hit.h ? `<b class="wallhit">${esc(hit.h.plants[0])}</b><br><i>${esc(hit.h.name)}</i>`
    : isGenus(i) ? `<b><i>${esc(NAME(i))}</i></b> <i>· ${esc(FAM(i))}</i><br>${fmt(D.n[i])} species`
      : `<b>${esc(display(i))}</b>${NAME(i) ? '' : ` <i>in ${esc(display(namedAncestor(i)))}</i>`}<br>${fmt(D.n[i])} species`;
  tipEl.style.left = Math.min(x + 14, innerWidth - 290) + 'px'; tipEl.style.top = y + 14 + 'px';
  tipEl.classList.remove('hidden'); canvas.style.cursor = 'pointer';
}

// ---------------------------------------------------------------- search
const index = [];
for (let i = 0; i < N; i++) {
  const nm = NAME(i); if (!nm) continue;
  index.push({ key: nm.toLowerCase(), label: nm, i, n: D.n[i], kind: isGenus(i) ? 'genus' : 'clade' });
  const fr = friendly(nm); if (fr) index.push({ key: fr.toLowerCase(), label: fr, alt: nm, i, n: D.n[i], kind: 'clade' });
}
for (const h of wallItems) for (const p of h.plants) index.push({ key: (p + ' ' + h.name).toLowerCase(), label: p, alt: h.name, i: h.at, n: 1e9, kind: 'wall', h });
const qEl = $('q'), qRes = $('qres');
let qSel = 0, qItems = [];
qEl.addEventListener('input', () => {
  const q = qEl.value.trim().toLowerCase();
  if (q.length < 2) { qRes.classList.add('hidden'); return; }
  const pre = [], sub = [];
  for (const it of index) { const k = it.key.indexOf(q); if (k === 0) pre.push(it); else if (k > 0) sub.push(it); }
  qItems = [...pre.sort((a, b) => b.n - a.n), ...sub.sort((a, b) => b.n - a.n)].slice(0, 12);
  qSel = 0;
  qRes.innerHTML = qItems.map((it, k) => `<li data-k="${k}" class="${k === 0 ? 'act' : ''}"><span class="${it.kind === 'wall' ? 'g' : ''}">${it.kind === 'genus' ? '<i>' + esc(it.label) + '</i>' : esc(it.label)}${it.alt ? ` <small>${esc(it.alt)}</small>` : ''}</span><small>${it.kind === 'wall' ? '✦ wall' : it.kind === 'genus' ? esc(FAM(it.i)) : fmt(it.n) + ' spp.'}</small></li>`).join('') || '<li><small>No match</small></li>';
  qRes.classList.remove('hidden');
});
function choose(it) { if (!it) return; qRes.classList.add('hidden'); qEl.value = ''; qEl.blur(); select(it.i, true, it.h); }
qRes.addEventListener('click', (e) => { const li = e.target.closest('li[data-k]'); if (li) choose(qItems[+li.dataset.k]); });
qEl.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    qSel = (qSel + (e.key === 'ArrowDown' ? 1 : -1) + qItems.length) % Math.max(1, qItems.length);
    [...qRes.children].forEach((li, k) => li.classList.toggle('act', k === qSel)); e.preventDefault();
  } else if (e.key === 'Enter') choose(qItems[qSel]);
  else if (e.key === 'Escape') { qRes.classList.add('hidden'); qEl.blur(); }
});
document.addEventListener('pointerdown', (e) => { if (!e.target.closest('.search')) qRes.classList.add('hidden'); });

// ---------------------------------------------------------------- wall list & toolbar
$('wallN').textContent = `${wallItems.length} taxa`;
$('wallList').innerHTML = wallItems.map((w, k) => `<li data-k="${k}">${esc(w.plants.join(', '))}<em>${esc(w.name)}${w.family ? ' · ' + esc(w.family) : ''}</em></li>`).join('');
$('wallList').addEventListener('click', (e) => {
  const li = e.target.closest('li'); if (!li) return;
  const w = wallItems[+li.dataset.k];
  [...$('wallList').children].forEach((x) => x.classList.toggle('act', x === li));
  select(w.at, true, w);
});
$('wallHead').onclick = () => $('wall').classList.toggle('collapsed');
if (!IS_SMALL) $('wall').classList.remove('collapsed');
const toggle = (id, fn) => { const b = $(id); b.onclick = () => { b.classList.toggle('on'); fn(b.classList.contains('on')); }; };
toggle('bWall', (on) => { wallOn = on; glowGroup.visible = on; $('wall').classList.toggle('hidden', !on); });
toggle('bLabels', (on) => { labelsOn = on; });
toggle('bLeaves', (on) => { leaves.visible = on; });
toggle('bSpin', (on) => { controls.autoRotate = on; });
$('bHome').onclick = () => { select(-1); homeView(true); };
if (window.self !== window.top) $('bFull').classList.remove('hidden');
$('bAbout').onclick = () => $('about').classList.remove('hidden');
$('aClose').onclick = () => $('about').classList.add('hidden');
$('about').addEventListener('click', (e) => { if (e.target.id === 'about') $('about').classList.add('hidden'); });

// ---------------------------------------------------------------- resize & loop
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false); composer.setSize(w, h);
  bloom.resolution.set(w / 2, h / 2);
  camera.aspect = w / h; camera.updateProjectionMatrix();
  leafMat.uniforms.uScale.value = (h * DPR) / 2 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
}
addEventListener('resize', resize); resize();

const clock = new THREE.Clock();
let frame = 0;
function loop() {
  const t = clock.getElapsedTime();
  if (flyAnim) {
    let k = Math.min(1, (performance.now() - flyAnim.start) / flyAnim.ms);
    const e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    camera.position.lerpVectors(flyAnim.p0, flyAnim.p1, e);
    controls.target.lerpVectors(flyAnim.t0, flyAnim.t1, e);
    if (k >= 1) flyAnim = null;
  }
  controls.update();
  leafMat.uniforms.uTime.value = t;
  // gentle firefly pulse on the wall lineages
  const pulse = 0.82 + 0.18 * Math.sin(t * 2.2);
  glowGroup.children[0].material.opacity = pulse;
  beadMat.size = 1.4 * (0.9 + 0.2 * Math.sin(t * 3.1));
  composer.render();
  if (frame++ % 2 === 0) updateLabels();
  doHover();
  requestAnimationFrame(loop);
}
loop();
$('loading').style.opacity = 0;
setTimeout(() => $('loading').remove(), 700);
// deep link: ?focus=Araceae (clade, family, genus, or living-wall species)
if (params.get('focus')) {
  const q = params.get('focus').toLowerCase();
  const it = index.find((x) => x.key === q) || index.find((x) => x.key.startsWith(q)) || index.find((x) => x.key.includes(q));
  if (it) setTimeout(() => select(it.i, true, it.h), 300);
}
window.__evo = { D, L, camera, controls, select, flyToNode, homeView };
