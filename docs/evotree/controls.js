// "Drone" camera controls for the Evo Tree viewer.
// - wheel / pinch: fly toward (or away from) whatever is under the pointer, a fixed fraction of the way per notch,
//   so you can travel from the whole tree down to a single twig at a steady pace
// - drag: turn the world around a pivot chosen at the start of each drag (getPivot): the selected branch if there
//   is one, the tree itself when you're outside it, otherwise yourself (look around like a hovering drone)
// - right-drag / shift-drag / two-finger drag: slide sideways
// The camera always looks at `target` (kept in front of it), so fly-to animations just move position + target.
import * as THREE from 'three';

const UP = new THREE.Vector3(0, 1, 0);

export class DroneControls extends THREE.EventDispatcher {
  constructor(camera, el, { getPivot, getDepth, getBounds }) {
    super();
    this.camera = camera; this.el = el;
    this.getPivot = getPivot; this.getDepth = getDepth; this.getBounds = getBounds;
    this.target = new THREE.Vector3();
    this.rotateSpeed = 1; this.zoomSpeed = 1; this.damping = 0.12;
    this.autoRotate = false; this.autoRotateSpeed = 0.35; this.autoPivot = new THREE.Vector3();
    this.minY = 0.03; this.maxDistance = 1e4;
    this.pivot = new THREE.Vector3();
    this.vYaw = 0; this.vPitch = 0;          // pending rotation (radians), drained with damping
    this.vMove = new THREE.Vector3();        // pending translation
    this.ptrs = new Map(); this.mode = null;
    const on = (t, f, o) => el.addEventListener(t, f, o);
    on('pointerdown', (e) => this._down(e));
    on('pointermove', (e) => this._move(e));
    on('pointerup', (e) => this._up(e)); on('pointercancel', (e) => this._up(e));
    on('wheel', (e) => this._wheel(e), { passive: false });
    on('contextmenu', (e) => e.preventDefault());
    el.style.touchAction = 'none';
  }

  // ---- input
  _down(e) {
    this.el.setPointerCapture?.(e.pointerId);
    this.ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    this.dispatchEvent({ type: 'start' });
    if (this.ptrs.size === 1) {
      this.mode = e.button === 2 || e.shiftKey || e.ctrlKey || e.metaKey ? 'pan' : 'rotate';
      if (this.mode === 'rotate') this._setPivot(this.getPivot(e.clientX, e.clientY));
      else this.panDepth = this._depthAt(e.clientX, e.clientY);
    } else if (this.ptrs.size === 2) {
      this.mode = 'pinch';
      const [a, b] = [...this.ptrs.values()];
      this.pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
      this.panDepth = this._depthAt(this.pinch.x, this.pinch.y);
    }
  }
  _move(e) {
    const p = this.ptrs.get(e.pointerId); if (!p) return;
    const dx = e.clientX - p.x, dy = e.clientY - p.y;
    p.x = e.clientX; p.y = e.clientY;
    if (this.mode === 'rotate' && this.ptrs.size === 1) {
      if (this.self) {   // the scene sticks to the pointer, like dragging a panorama
        const k = THREE.MathUtils.degToRad(this.camera.fov) / this.el.clientHeight;
        this.vYaw += dx * k; this.vPitch += dy * k;
      } else {           // grab the pivot and turn it
        const k = (2 * Math.PI / this.el.clientHeight) * this.rotateSpeed;
        this.vYaw -= dx * k; this.vPitch -= dy * k;
      }
    } else if (this.mode === 'pan' && this.ptrs.size === 1) {
      this._pan(dx, dy, this.panDepth);
    } else if (this.mode === 'pinch' && this.ptrs.size === 2) {
      const [a, b] = [...this.ptrs.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y), x = (a.x + b.x) / 2, y = (a.y + b.y) / 2;
      this._pan(x - this.pinch.x, y - this.pinch.y, this.panDepth);
      if (this.pinch.d > 10 && d > 10) this._zoomAt(x, y, Math.log(this.pinch.d / d) * 3.2);
      this.pinch = { d, x, y };
    }
  }
  _up(e) {
    this.ptrs.delete(e.pointerId);
    if (this.ptrs.size === 1) {   // pinch → one finger: carry on rotating around a fresh pivot
      const [p] = [...this.ptrs.values()];
      this.mode = 'rotate'; this._setPivot(this.getPivot(p.x, p.y));
    } else if (!this.ptrs.size) this.mode = null;
  }
  _wheel(e) {
    e.preventDefault();
    this.dispatchEvent({ type: 'start' });
    let d = e.deltaY * (e.deltaMode === 1 ? 33 : e.deltaMode === 2 ? 400 : 1);
    if (e.ctrlKey) d *= 4;            // trackpad pinch arrives as ctrl+wheel with small deltas
    d = Math.max(-300, Math.min(300, d));
    this._zoomAt(e.clientX, e.clientY, (d / 100) * this.zoomSpeed);
  }

  _setPivot(v) {
    this.pivot.copy(v);
    this.self = v.distanceTo(this.camera.position) < 1e-4;   // turning around yourself: look around
  }

  // ---- motions
  _ray(x, y) {
    const r = this.el.getBoundingClientRect();
    const v = new THREE.Vector3(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1, 0.5).unproject(this.camera);
    return v.sub(this.camera.position).normalize();
  }
  _depthAt(x, y) {
    const d = this.getDepth(x, y);
    return d && isFinite(d) ? d : this.camera.position.distanceTo(this.getBounds().center) * 0.6;
  }
  // notches > 0 = away; each notch covers ~28% of the distance to what's under the pointer (symmetric in/out)
  _zoomAt(x, y, notches) {
    if (!notches) return;
    const { center, radius } = this.getBounds();
    const ray = this._ray(x, y);
    // measure from where the camera is already heading, so quick scrolls don't overshoot
    let D = this._depthAt(x, y) - this.vMove.dot(ray);
    D = Math.max(D, 0.02);
    if (notches > 0) D = Math.max(D, this.camera.position.clone().add(this.vMove).distanceTo(center) * 0.08);
    const f = Math.pow(0.72, -notches);           // <1 when moving in
    const step = D * (1 - f);                      // positive = toward
    this.vMove.addScaledVector(ray, step);
  }
  _pan(dx, dy, depth) {
    const k = (2 * Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2)) * depth) / this.el.clientHeight;
    const right = new THREE.Vector3().setFromMatrixColumn(this.camera.matrix, 0);
    const up = new THREE.Vector3().setFromMatrixColumn(this.camera.matrix, 1);
    const m = right.multiplyScalar(-dx * k).addScaledVector(up, dy * k);
    this.camera.position.add(m); this.target.add(m);
  }
  _turn(yaw, pitch, pivot) {
    const cam = this.camera.position, tgt = this.target;
    if (yaw) {
      const q = new THREE.Quaternion().setFromAxisAngle(UP, yaw);
      cam.sub(pivot).applyQuaternion(q).add(pivot); tgt.sub(pivot).applyQuaternion(q).add(pivot);
    }
    if (pitch) {
      const dir = tgt.clone().sub(cam).normalize();
      const right = new THREE.Vector3().crossVectors(dir, UP).normalize();
      const q = new THREE.Quaternion().setFromAxisAngle(right, pitch);
      const nd = dir.clone().applyQuaternion(q);
      if (Math.abs(nd.y) < 0.97) {                // don't flip over the top
        const c2 = cam.clone().sub(pivot).applyQuaternion(q).add(pivot);
        if (c2.y >= this.minY || c2.y >= cam.y) { // don't sink under the ground
          const t2 = tgt.clone().sub(pivot).applyQuaternion(q).add(pivot);
          cam.copy(c2); tgt.copy(t2);
        }
      }
    }
  }

  update() {
    const a = this.damping;
    if (Math.abs(this.vYaw) > 1e-6 || Math.abs(this.vPitch) > 1e-6) {
      const y = this.vYaw * a * 2.2, p = this.vPitch * a * 2.2;
      this._turn(y, p, this.pivot); this.vYaw -= y; this.vPitch -= p;
    }
    if (this.vMove.lengthSq() > 1e-12) {
      const m = this.vMove.clone().multiplyScalar(a * 1.6);
      this.camera.position.add(m); this.target.add(m); this.vMove.sub(m);
    }
    if (this.autoRotate && !this.ptrs.size) this._turn(-this.autoRotateSpeed * 0.0035, 0, this.autoPivot);
    // stay above ground and within range of the tree
    const { center } = this.getBounds();
    const cam = this.camera.position;
    if (cam.y < this.minY) { const d = this.minY - cam.y; cam.y += d; this.target.y += d; }
    const off = cam.clone().sub(center), L = off.length();
    if (L > this.maxDistance) { const d = off.multiplyScalar(this.maxDistance / L - 1); cam.add(d); this.target.add(d); }
    if (this.target.distanceToSquared(cam) < 1e-8) this.target.add(new THREE.Vector3(0, 0, -0.01));
    this.camera.up.copy(UP);
    this.camera.lookAt(this.target);
    this.camera.updateMatrixWorld();
  }
}
