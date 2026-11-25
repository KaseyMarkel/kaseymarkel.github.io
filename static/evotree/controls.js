// Turntable camera for the Evo Tree viewer, after the Vehicle Assembly Building in Kerbal Space Program:
// the tree stands on a turntable and you grab it.
// - drag (one finger / left mouse): spin the tree around a vertical axis through the focus, and tilt it toward you
// - scroll / pinch: zoom toward the focus (keep zooming in and you push the focus forward, flying into the crown)
// - right-drag / shift-drag / two-finger drag / shift+scroll: elevator: move the focus up/down and sideways
// - keys: ←/→ (A/D) spin · ↑/↓ elevator · W/S or +/− zoom
// The focus is the tree's centre until the app moves it (double-click a branch to put it on the turntable).
// Everything eases toward goal values, so motion is smooth and input never fights the animation.
import * as THREE from 'three';

const UP = new THREE.Vector3(0, 1, 0);
const PHI_MIN = -0.2, PHI_MAX = 1.45;   // elevation of the camera above the focus (radians)

export class TurntableControls extends THREE.EventDispatcher {
  constructor(camera, el, { getBounds }) {
    super();
    this.camera = camera; this.el = el; this.getBounds = getBounds;
    this.target = new THREE.Vector3();     // focus (current)
    this.goal = new THREE.Vector3();       // focus (goal)
    this.theta = 0; this.phi = 0.2; this.r = 10;
    this.gTheta = 0; this.gPhi = 0.2; this.gR = 10;
    this.minR = 0.12; this.maxDistance = 1e4; this.minY = 0.04;
    this.rotateSpeed = 1; this.autoRotate = false; this.autoRotateSpeed = 0.35;
    this.ptrs = new Map(); this.mode = null; this.keys = new Set();
    this.last = performance.now();
    const on = (t, f, o) => el.addEventListener(t, f, o);
    on('pointerdown', (e) => this._down(e));
    on('pointermove', (e) => this._move(e));
    on('pointerup', (e) => this._up(e)); on('pointercancel', (e) => this._up(e));
    on('wheel', (e) => this.wheel(e), { passive: false });
    on('contextmenu', (e) => e.preventDefault());
    addEventListener('keydown', (e) => this._key(e, true));
    addEventListener('keyup', (e) => this._key(e, false));
    addEventListener('blur', () => this.keys.clear());
    el.style.touchAction = 'none';
  }

  // adopt whatever camera.position / target the app set (fly-to animations, home view, deep links)
  setFromCamera() {
    const off = this.camera.position.clone().sub(this.target);
    this.r = this.gR = Math.max(this.minR, off.length());
    this.theta = this.gTheta = Math.atan2(off.x, off.z);
    this.phi = this.gPhi = Math.asin(THREE.MathUtils.clamp(off.y / this.r, -1, 1));
    this.goal.copy(this.target);
    this._apply();
  }

  // ---- input
  _start() { this.dispatchEvent({ type: 'start' }); }
  _down(e) {
    this.el.setPointerCapture?.(e.pointerId);
    this.ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    this._start();
    if (this.ptrs.size === 1) this.mode = e.button === 2 || e.shiftKey || e.ctrlKey || e.metaKey ? 'pan' : 'rotate';
    else if (this.ptrs.size === 2) { this.mode = 'pinch'; this.pinch = this._pinchState(); }
  }
  _pinchState() {
    const [a, b] = [...this.ptrs.values()];
    return { d: Math.hypot(a.x - b.x, a.y - b.y), x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  }
  _move(e) {
    const p = this.ptrs.get(e.pointerId); if (!p) return;
    const dx = e.clientX - p.x, dy = e.clientY - p.y;
    p.x = e.clientX; p.y = e.clientY;
    if (this.ptrs.size === 1 && this.mode === 'rotate') this._rotate(dx, dy);
    else if (this.ptrs.size === 1 && this.mode === 'pan') this._pan(dx, dy);
    else if (this.ptrs.size === 2 && this.mode === 'pinch') {
      const s = this._pinchState();
      this._pan(s.x - this.pinch.x, s.y - this.pinch.y);
      if (this.pinch.d > 10 && s.d > 10) this._zoom(this.pinch.d / s.d);
      this.pinch = s;
    }
  }
  _up(e) {
    this.ptrs.delete(e.pointerId);
    if (this.ptrs.size === 1) this.mode = 'rotate';
    else if (!this.ptrs.size) this.mode = null;
  }
  wheel(e) {
    e.preventDefault(); this._start();
    let d = e.deltaY * (e.deltaMode === 1 ? 33 : e.deltaMode === 2 ? 400 : 1);
    if (e.ctrlKey) d *= 3;               // trackpad pinch arrives as ctrl+wheel with small deltas
    d = THREE.MathUtils.clamp(d, -250, 250);
    if (e.shiftKey) this._pan(0, -d * 0.5);   // shift+scroll: elevator, like the VAB
    else this._zoom(Math.pow(1.2, d / 100));
  }
  _key(e, down) {
    if (e.target && /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
    const k = e.key.toLowerCase();
    if (!['arrowleft', 'arrowright', 'arrowup', 'arrowdown', 'a', 'd', 'w', 's', '+', '=', '-', '_'].includes(k)) return;
    if (down) { this.keys.add(k); this._start(); } else this.keys.delete(k);
    e.preventDefault();
  }

  // ---- motions (all act on goals)
  _rotate(dx, dy) {
    const k = (Math.PI / Math.min(this.el.clientWidth, this.el.clientHeight)) * this.rotateSpeed;
    this.gTheta -= dx * k;               // drag right → the tree turns right
    this.gPhi = THREE.MathUtils.clamp(this.gPhi + dy * k, PHI_MIN, PHI_MAX);
  }
  _pan(dx, dy) {   // screen-space drag → focus moves sideways (horizontal) and up/down (world vertical)
    const s = (2 * Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2)) * this.gR) / this.el.clientHeight;
    const right = new THREE.Vector3(Math.cos(this.gTheta), 0, -Math.sin(this.gTheta));
    this.goal.addScaledVector(right, -dx * s).addScaledVector(UP, dy * s);
    const { center, radius } = this.getBounds();
    this.goal.y = THREE.MathUtils.clamp(this.goal.y, 0, center.y + radius * 1.2);
  }
  _zoom(f) {
    let r = this.gR * f;
    if (r < this.minR) {   // already at the focus: keep going by pushing the focus forward into the tree
      const fwd = this.goal.clone().sub(this._camFor(this.gTheta, this.gPhi, this.gR, this.goal)).normalize();
      this.goal.addScaledVector(fwd, (this.minR - r) * 2.5);
      r = this.minR;
    }
    this.gR = Math.min(r, this.maxDistance);
  }
  _camFor(theta, phi, r, focus) {
    return new THREE.Vector3(Math.cos(phi) * Math.sin(theta), Math.sin(phi), Math.cos(phi) * Math.cos(theta)).multiplyScalar(r).add(focus);
  }
  _apply() {
    const c = this._camFor(this.theta, this.phi, this.r, this.target);
    if (c.y < this.minY) c.y = this.minY;
    this.camera.position.copy(c);
    this.camera.up.copy(UP);
    this.camera.lookAt(this.target);
    this.camera.updateMatrixWorld();
  }

  update() {
    const now = performance.now(), dt = Math.min(0.1, (now - this.last) / 1000); this.last = now;
    if (this.keys.size) {
      const K = this.keys, has = (...ks) => ks.some((k) => K.has(k));
      const step = dt * 60;
      if (has('arrowleft', 'a')) this._rotate(-3.5 * step, 0);
      if (has('arrowright', 'd')) this._rotate(3.5 * step, 0);
      if (has('arrowup')) this._pan(0, 6 * step);
      if (has('arrowdown')) this._pan(0, -6 * step);
      if (has('w', '+', '=')) this._zoom(Math.pow(0.985, step));
      if (has('s', '-', '_')) this._zoom(Math.pow(1 / 0.985, step));
    }
    if (this.autoRotate && !this.ptrs.size) this.gTheta -= this.autoRotateSpeed * 0.2 * dt;
    const a = 1 - Math.exp(-dt * 14);    // easing toward the goals (frame-rate independent)
    this.theta += (this.gTheta - this.theta) * a;
    this.phi += (this.gPhi - this.phi) * a;
    this.r *= Math.pow(this.gR / this.r, a);   // ease zoom in log space
    this.target.lerp(this.goal, a);
    this._apply();
  }
}
