// Evo Tree Viewer — pure layout (no three.js). Works in browser and Node.
// Turns a preorder tree (parent[], n[]) into an oak-like 3D skeleton.
// "Wire tree" rule: every species is one wire, so a branch's cross-sectional
// area ∝ species count → radius ∝ √n (this is also Leonardo da Vinci's rule for real trees).

export function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const DEFAULTS = {
  seed: 7,
  trunkRadius: 1.5,
  trunkHeight: 8,
  lenBase: 15,
  lenExp: 0.36,        // segment length ∝ n^lenExp
  thetaMin: 18,        // degrees: branch angle for a dominant child
  thetaMax: 70,        // degrees: branch angle for a tiny side child
  thetaGamma: 0.75,
  upPull: 0.11,        // tropism toward +y
  outPull: 0.34,       // tropism away from trunk axis (crown spread)
  twigUp: 0.42,        // extra up-pull for thin twigs
  minRadius: 0.0035,
  spreadXZ: 1.35,      // final crown reshaping toward an oak silhouette (wider than tall)
  squashY: 0.8,
};

export function layoutTree(parent, n, opts = {}) {
  const o = { ...DEFAULTS, ...opts };
  const N = parent.length;
  const rnd = mulberry32(o.seed);
  const kids = Array.from({ length: N }, () => []);
  for (let i = 1; i < N; i++) kids[parent[i]].push(i);
  for (const k of kids) k.sort((a, b) => n[b] - n[a]);

  const size = new Int32Array(N);          // subtree node count (preorder → contiguous)
  for (let i = N - 1; i >= 0; i--) { size[i] += 1; if (i > 0) size[parent[i]] += size[i]; }
  const depth = new Int32Array(N);
  for (let i = 1; i < N; i++) depth[i] = depth[parent[i]] + 1;

  const start = new Float32Array(N * 3), end = new Float32Array(N * 3), dir = new Float32Array(N * 3);
  const radius = new Float32Array(N), len = new Float32Array(N);
  const n0 = n[0];
  for (let i = 0; i < N; i++) radius[i] = Math.max(o.minRadius, o.trunkRadius * Math.sqrt(n[i] / n0));

  // root = trunk
  dir[1] = 1; len[0] = o.trunkHeight; end[1] = o.trunkHeight;

  const G = Math.PI * (3 - Math.sqrt(5));
  const D2R = Math.PI / 180;
  const tmp = [0, 0, 0];
  for (let p = 0; p < N; p++) {
    const ks = kids[p];
    if (!ks.length) continue;
    const px = dir[p * 3], py = dir[p * 3 + 1], pz = dir[p * 3 + 2];
    // basis perpendicular to parent direction; reference = world up unless parallel
    let rx = 0, ry = 1, rz = 0;
    if (Math.abs(py) > 0.95) { rx = 1; ry = 0; rz = 0; }
    let ux = py * rz - pz * ry, uy = pz * rx - px * rz, uz = px * ry - py * rx;
    let ul = Math.hypot(ux, uy, uz); ux /= ul; uy /= ul; uz /= ul;
    const vx = py * uz - pz * uy, vy = pz * ux - px * uz, vz = px * uy - py * ux;
    const phi0 = rnd() * Math.PI * 2;
    const ex = end[p * 3], ey = end[p * 3 + 1], ez = end[p * 3 + 2];
    const many = ks.length > 3;
    for (let j = 0; j < ks.length; j++) {
      const k = ks[j];
      const s = n[k] / Math.max(1, n[p]);
      let theta = (o.thetaMin + (o.thetaMax - o.thetaMin) * Math.pow(1 - Math.min(s, 1), o.thetaGamma)) * D2R;
      let phi;
      if (j === 0 && s >= 0.5) { phi = phi0 + Math.PI; }        // dominant child leans away from the rest
      else { phi = phi0 + Math.max(0, j - 1) * G; }
      if (many && j > 0) theta *= 0.75 + 0.6 * rnd();
      theta += (rnd() - 0.5) * 8 * D2R;
      const c = Math.cos(theta), sn = Math.sin(theta), cp = Math.cos(phi), sp = Math.sin(phi);
      let dx = px * c + (ux * cp + vx * sp) * sn;
      let dy = py * c + (uy * cp + vy * sp) * sn;
      let dz = pz * c + (uz * cp + vz * sp) * sn;
      // tropisms
      // tropisms by girth: thick limbs hold up, mid limbs spread out, twigs turn to the light
      const r = radius[k];
      const thick = Math.min(1, Math.max(0, (r - 0.12) / 0.35));
      const thin = 1 - Math.min(1, r / 0.06);
      let ox = ex, oz = ez; const ol = Math.hypot(ox, oz);
      if (ol > 1e-4) { ox /= ol; oz /= ol; } else { ox = cp; oz = sp; }
      const up = o.upPull * (1 + 1.2 * thick) + o.twigUp * thin;
      const out = o.outPull * (1 - thick) * (1 - 0.6 * thin);
      dx += ox * out; dz += oz * out; dy += up;
      if (ey + dy * 3 < 0.5) dy += 0.5;                          // keep off the ground
      const dl = Math.hypot(dx, dy, dz); dx /= dl; dy /= dl; dz /= dl;
      const L = o.lenBase * Math.pow(n[k] / n0, o.lenExp) * (0.18 + 0.82 * Math.pow(1 - Math.min(s, 0.999), 0.55)) + 0.04;
      len[k] = L;
      dir[k * 3] = dx; dir[k * 3 + 1] = dy; dir[k * 3 + 2] = dz;
      start[k * 3] = ex; start[k * 3 + 1] = ey; start[k * 3 + 2] = ez;
      end[k * 3] = ex + dx * L; end[k * 3 + 1] = ey + dy * L; end[k * 3 + 2] = ez + dz * L;
    }
  }
  // reshape the crown about the top of the trunk: broader, lower — an oak rather than a poplar
  const H = o.trunkHeight;
  const warp = (arr, i) => {
    const y = arr[i * 3 + 1];
    if (y <= H) return;
    const f = Math.min(1, (y - H) / (H * 0.8));        // blend in above the first fork
    const sx = 1 + (o.spreadXZ - 1) * f;
    arr[i * 3] *= sx; arr[i * 3 + 2] *= sx; arr[i * 3 + 1] = H + (y - H) * o.squashY;
  };
  for (let i = 0; i < N; i++) { warp(start, i); warp(end, i); }
  for (let i = 1; i < N; i++) {
    const dx = end[i * 3] - start[i * 3], dy = end[i * 3 + 1] - start[i * 3 + 1], dz = end[i * 3 + 2] - start[i * 3 + 2];
    const l = Math.hypot(dx, dy, dz) || 1e-6;
    len[i] = l; dir[i * 3] = dx / l; dir[i * 3 + 1] = dy / l; dir[i * 3 + 2] = dz / l;
  }
  return { N, kids, size, depth, start, end, dir, radius, len };
}
