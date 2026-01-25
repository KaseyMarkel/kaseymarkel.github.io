---
title: "Gallery"
socialShare: false
---

{{< rawhtml >}}
<style>
  .intro-header { display: none !important; }
  div[role="main"].container {
    padding: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
  }
  .blog-post { padding: 0 !important; margin: 0 !important; }
  footer, .footer { display: none !important; }

  #gallery-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 999;
    background: #1a1a1a;
  }

  #gallery-canvas {
    width: 100%;
    height: 100%;
    display: block;
  }

  #instructions {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: #fff;
    font-family: 'Open Sans', sans-serif;
    background: rgba(0,0,0,0.88);
    padding: 45px 60px;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 12px 40px rgba(0,0,0,0.5);
    max-width: 440px;
  }

  #instructions:hover {
    background: rgba(0,0,0,0.95);
    transform: translate(-50%, -50%) scale(1.02);
  }

  #instructions h2 {
    margin: 0 0 18px 0;
    font-size: 26px;
    font-weight: 300;
    letter-spacing: 4px;
    text-transform: uppercase;
  }

  #instructions .description {
    margin: 0 0 22px 0;
    font-size: 13px;
    line-height: 1.7;
    opacity: 0.7;
    font-style: italic;
  }

  #instructions p {
    margin: 6px 0;
    font-size: 13px;
    opacity: 0.8;
    letter-spacing: 1px;
  }

  #instructions .click-hint {
    margin-top: 28px;
    font-size: 11px;
    opacity: 0.5;
    text-transform: uppercase;
    letter-spacing: 3px;
  }

  #loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #aaa;
    font-family: 'Open Sans', sans-serif;
    font-size: 14px;
    letter-spacing: 3px;
  }

  #loading-bar {
    width: 200px;
    height: 2px;
    background: rgba(255,255,255,0.15);
    margin-top: 20px;
    border-radius: 1px;
    overflow: hidden;
  }

  #loading-progress {
    width: 0%;
    height: 100%;
    background: #fff;
    transition: width 0.3s ease;
  }

  #crosshair {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 24px;
    height: 24px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
  }

  #crosshair::before,
  #crosshair::after {
    content: '';
    position: absolute;
    background: rgba(255,255,255,0.4);
    border-radius: 1px;
  }

  #crosshair::before {
    width: 2px;
    height: 24px;
    left: 11px;
    top: 0;
  }

  #crosshair::after {
    width: 24px;
    height: 2px;
    left: 0;
    top: 11px;
  }

  #exit-hint {
    position: absolute;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    color: rgba(255,255,255,0.5);
    font-family: 'Open Sans', sans-serif;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    opacity: 0;
    transition: opacity 0.5s;
    pointer-events: none;
  }

  @media (max-width: 768px) {
    #instructions {
      padding: 30px 35px;
      max-width: 320px;
    }
    #instructions h2 {
      font-size: 20px;
    }
  }
</style>

<div id="gallery-container">
  <div id="loading">
    LOADING GALLERY
    <div id="loading-bar">
      <div id="loading-progress"></div>
    </div>
  </div>
  <div id="instructions" style="display: none;">
    <h2>Pour Paintings</h2>
    <p class="description">These are real pour paintings I've made, hosted in a virtual gallery Claude made. In reality, most of these paintings hang in my garage.</p>
    <p>Use mouse to look around</p>
    <p>WASD or Arrow keys to move</p>
    <div class="click-hint">Click to enter</div>
  </div>
  <div id="crosshair"></div>
  <div id="exit-hint">Press ESC to exit</div>
  <canvas id="gallery-canvas"></canvas>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function() {
  'use strict';

  const canvas = document.getElementById('gallery-canvas');
  const instructions = document.getElementById('instructions');
  const loading = document.getElementById('loading');
  const loadingProgress = document.getElementById('loading-progress');
  const crosshair = document.getElementById('crosshair');
  const exitHint = document.getElementById('exit-hint');

  let camera, scene, renderer;
  let isLocked = false;
  let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
  const velocity = new THREE.Vector3();
  const direction = new THREE.Vector3();
  const euler = new THREE.Euler(0, 0, 0, 'YXZ');

  const roomWidth = 24;
  const roomDepth = 16;
  const roomHeight = 5;

  const paintings = [
    { file: '/img/paint1.jpg', x: -roomWidth/2 + 0.05, z: -5, rotY: Math.PI/2 },
    { file: '/img/paint2.jpg', x: -roomWidth/2 + 0.05, z: 0, rotY: Math.PI/2 },
    { file: '/img/paint3.jpg', x: -roomWidth/2 + 0.05, z: 5, rotY: Math.PI/2 },
    { file: '/img/paint4.jpg', x: roomWidth/2 - 0.05, z: -5, rotY: -Math.PI/2 },
    { file: '/img/paint5.jpg', x: roomWidth/2 - 0.05, z: 0, rotY: -Math.PI/2 },
    { file: '/img/paint6.jpg', x: roomWidth/2 - 0.05, z: 5, rotY: -Math.PI/2 },
    { file: '/img/paint7.jpg', x: 0, z: -roomDepth/2 + 0.05, rotY: 0 },
    { file: '/img/paint8.jpg', x: 0, z: roomDepth/2 - 0.05, rotY: Math.PI }
  ];

  let loadedCount = 0;

  function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);

    camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 1.6, 0);
    euler.y = Math.PI / 2;
    camera.quaternion.setFromEuler(euler);

    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.physicallyCorrectLights = true;

    createRoom();
    loadPaintings();

    window.addEventListener('resize', onWindowResize);
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('keyup', onKeyUp);
    document.addEventListener('mousemove', onMouseMove);

    instructions.addEventListener('click', () => canvas.requestPointerLock());

    document.addEventListener('pointerlockchange', () => {
      isLocked = document.pointerLockElement === canvas;
      instructions.style.display = isLocked ? 'none' : 'block';
      crosshair.style.opacity = isLocked ? '1' : '0';
      if (isLocked) {
        exitHint.style.opacity = '1';
        setTimeout(() => exitHint.style.opacity = '0', 3000);
      }
    });

    animate();
  }

  // Create oak hardwood floor texture
  function createHardwoodTexture() {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');

    const plankHeight = 64;
    const planksPerRow = 8;

    for (let row = 0; row < planksPerRow; row++) {
      const y = row * plankHeight;

      // Stagger planks
      const offset = (row % 2) * 128;

      for (let plank = -1; plank < 5; plank++) {
        const x = plank * 128 + offset;
        const plankWidth = 120 + Math.random() * 16;

        // Base plank color with variation
        const baseHue = 25 + Math.random() * 10;
        const baseSat = 35 + Math.random() * 15;
        const baseLit = 35 + Math.random() * 15;
        ctx.fillStyle = `hsl(${baseHue}, ${baseSat}%, ${baseLit}%)`;
        ctx.fillRect(x, y, plankWidth, plankHeight - 1);

        // Wood grain lines
        ctx.strokeStyle = `hsla(${baseHue - 5}, ${baseSat + 10}%, ${baseLit - 8}%, 0.4)`;
        ctx.lineWidth = 0.5;
        for (let g = 0; g < 12; g++) {
          const gy = y + 3 + g * 5 + Math.random() * 2;
          ctx.beginPath();
          ctx.moveTo(x, gy);
          // Wavy grain
          for (let gx = x; gx < x + plankWidth; gx += 10) {
            ctx.lineTo(gx, gy + (Math.random() - 0.5) * 2);
          }
          ctx.stroke();
        }

        // Darker grain details
        ctx.strokeStyle = `hsla(${baseHue}, ${baseSat}%, ${baseLit - 12}%, 0.3)`;
        ctx.lineWidth = 1;
        for (let g = 0; g < 4; g++) {
          const gy = y + 8 + g * 15 + Math.random() * 5;
          ctx.beginPath();
          ctx.moveTo(x, gy);
          for (let gx = x; gx < x + plankWidth; gx += 8) {
            ctx.lineTo(gx, gy + (Math.random() - 0.5) * 1.5);
          }
          ctx.stroke();
        }

        // Knots (occasional)
        if (Math.random() > 0.85) {
          const kx = x + 20 + Math.random() * (plankWidth - 40);
          const ky = y + 15 + Math.random() * (plankHeight - 30);
          const kr = 3 + Math.random() * 5;
          ctx.fillStyle = `hsla(${baseHue}, ${baseSat + 5}%, ${baseLit - 15}%, 0.6)`;
          ctx.beginPath();
          ctx.ellipse(kx, ky, kr, kr * 0.7, Math.random() * Math.PI, 0, Math.PI * 2);
          ctx.fill();
        }

        // Gap between planks
        ctx.fillStyle = '#1a1512';
        ctx.fillRect(x + plankWidth, y, 2, plankHeight);
      }

      // Horizontal gap between rows
      ctx.fillStyle = '#1a1512';
      ctx.fillRect(0, y + plankHeight - 1, 512, 1);
    }

    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    return tex;
  }

  // Create textured wall (orange peel / knockdown texture)
  function createWallTexture() {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext('2d');

    // Base color - warm white
    ctx.fillStyle = '#f8f6f2';
    ctx.fillRect(0, 0, 256, 256);

    // Orange peel texture bumps
    for (let i = 0; i < 800; i++) {
      const x = Math.random() * 256;
      const y = Math.random() * 256;
      const r = 1 + Math.random() * 3;
      const brightness = 245 + Math.random() * 10;
      ctx.fillStyle = `rgb(${brightness}, ${brightness - 2}, ${brightness - 5})`;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }

    // Subtle shadow spots for depth
    for (let i = 0; i < 200; i++) {
      const x = Math.random() * 256;
      const y = Math.random() * 256;
      const r = 0.5 + Math.random() * 1.5;
      ctx.fillStyle = `rgba(200, 195, 188, ${0.1 + Math.random() * 0.15})`;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }

    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    return tex;
  }

  // Create ceiling texture (acoustic tile / textured drywall)
  function createCeilingTexture() {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext('2d');

    // Base color - slightly warm white
    ctx.fillStyle = '#f5f3ef';
    ctx.fillRect(0, 0, 256, 256);

    // Fine stipple texture
    for (let i = 0; i < 3000; i++) {
      const x = Math.random() * 256;
      const y = Math.random() * 256;
      const brightness = 230 + Math.random() * 25;
      ctx.fillStyle = `rgb(${brightness}, ${brightness}, ${brightness - 3})`;
      ctx.fillRect(x, y, 1, 1);
    }

    // Larger texture spots
    for (let i = 0; i < 150; i++) {
      const x = Math.random() * 256;
      const y = Math.random() * 256;
      const r = 1 + Math.random() * 2;
      const brightness = 235 + Math.random() * 15;
      ctx.fillStyle = `rgb(${brightness}, ${brightness}, ${brightness})`;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }

    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    return tex;
  }

  function createRoom() {
    // Hardwood floor
    const floorTex = createHardwoodTexture();
    floorTex.repeat.set(4, 3);
    const floor = new THREE.Mesh(
      new THREE.PlaneGeometry(roomWidth, roomDepth),
      new THREE.MeshStandardMaterial({
        map: floorTex,
        roughness: 0.4,
        metalness: 0.05
      })
    );
    floor.rotation.x = -Math.PI / 2;
    scene.add(floor);

    // Textured ceiling
    const ceilingTex = createCeilingTexture();
    ceilingTex.repeat.set(6, 4);
    const ceiling = new THREE.Mesh(
      new THREE.PlaneGeometry(roomWidth, roomDepth),
      new THREE.MeshStandardMaterial({
        map: ceilingTex,
        roughness: 0.9,
        metalness: 0
      })
    );
    ceiling.rotation.x = Math.PI / 2;
    ceiling.position.y = roomHeight;
    scene.add(ceiling);

    // Textured walls
    const wallTexLeft = createWallTexture();
    wallTexLeft.repeat.set(4, 2);
    const leftWall = new THREE.Mesh(
      new THREE.PlaneGeometry(roomDepth, roomHeight),
      new THREE.MeshStandardMaterial({ map: wallTexLeft, roughness: 0.85, metalness: 0 })
    );
    leftWall.rotation.y = Math.PI / 2;
    leftWall.position.set(-roomWidth/2, roomHeight/2, 0);
    scene.add(leftWall);

    const wallTexRight = createWallTexture();
    wallTexRight.repeat.set(4, 2);
    const rightWall = new THREE.Mesh(
      new THREE.PlaneGeometry(roomDepth, roomHeight),
      new THREE.MeshStandardMaterial({ map: wallTexRight, roughness: 0.85, metalness: 0 })
    );
    rightWall.rotation.y = -Math.PI / 2;
    rightWall.position.set(roomWidth/2, roomHeight/2, 0);
    scene.add(rightWall);

    const wallTexBack = createWallTexture();
    wallTexBack.repeat.set(6, 2);
    const backWall = new THREE.Mesh(
      new THREE.PlaneGeometry(roomWidth, roomHeight),
      new THREE.MeshStandardMaterial({ map: wallTexBack, roughness: 0.85, metalness: 0 })
    );
    backWall.position.set(0, roomHeight/2, -roomDepth/2);
    scene.add(backWall);

    const wallTexFront = createWallTexture();
    wallTexFront.repeat.set(6, 2);
    const frontWall = new THREE.Mesh(
      new THREE.PlaneGeometry(roomWidth, roomHeight),
      new THREE.MeshStandardMaterial({ map: wallTexFront, roughness: 0.85, metalness: 0 })
    );
    frontWall.rotation.y = Math.PI;
    frontWall.position.set(0, roomHeight/2, roomDepth/2);
    scene.add(frontWall);

    // Ambient light
    const ambient = new THREE.AmbientLight(0xfff8f0, 0.15);
    scene.add(ambient);

    // Light fixtures and spotlights
    const fixtureMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.3, metalness: 0.8 });

    paintings.forEach(p => {
      let fx = p.x, fz = p.z;
      const offset = 0.8;
      if (p.rotY === Math.PI/2) fx += offset;
      else if (p.rotY === -Math.PI/2) fx -= offset;
      else if (p.rotY === 0) fz += offset;
      else fz -= offset;

      // Track light fixture
      const fixture = new THREE.Mesh(
        new THREE.CylinderGeometry(0.06, 0.08, 0.12, 8),
        fixtureMat
      );
      fixture.position.set(fx, roomHeight - 0.06, fz);
      scene.add(fixture);

      const arm = new THREE.Mesh(
        new THREE.CylinderGeometry(0.02, 0.02, 0.15, 6),
        fixtureMat
      );
      arm.position.set(fx, roomHeight - 0.18, fz);
      scene.add(arm);

      const head = new THREE.Mesh(
        new THREE.CylinderGeometry(0.04, 0.07, 0.1, 8),
        fixtureMat
      );
      head.position.set(fx, roomHeight - 0.28, fz);
      if (p.rotY === Math.PI/2) head.rotation.z = -0.4;
      else if (p.rotY === -Math.PI/2) head.rotation.z = 0.4;
      else if (p.rotY === 0) head.rotation.x = 0.4;
      else head.rotation.x = -0.4;
      scene.add(head);

      // Spotlight
      const spot = new THREE.SpotLight(0xfff6e6, 2.5);
      spot.position.set(fx, roomHeight - 0.3, fz);
      spot.angle = Math.PI / 6;
      spot.penumbra = 0.5;
      spot.decay = 1.5;
      spot.distance = 8;

      const target = new THREE.Object3D();
      target.position.set(p.x, 2, p.z);
      scene.add(target);
      spot.target = target;
      scene.add(spot);
    });
  }

  function loadPaintings() {
    const loader = new THREE.TextureLoader();

    paintings.forEach(p => {
      loader.load(p.file, tex => {
        tex.encoding = THREE.sRGBEncoding;

        const aspect = tex.image.width / tex.image.height;
        const h = 2;
        const w = h * aspect;

        const painting = new THREE.Mesh(
          new THREE.PlaneGeometry(w, h),
          new THREE.MeshBasicMaterial({ map: tex })
        );
        painting.position.set(p.x, 2.1, p.z);
        painting.rotation.y = p.rotY;
        scene.add(painting);

        loadedCount++;
        loadingProgress.style.width = (loadedCount / paintings.length * 100) + '%';

        if (loadedCount === paintings.length) {
          setTimeout(() => {
            loading.style.display = 'none';
            instructions.style.display = 'block';
          }, 100);
        }
      });
    });
  }

  function onMouseMove(e) {
    if (!isLocked) return;
    euler.setFromQuaternion(camera.quaternion);
    euler.y -= e.movementX * 0.002;
    euler.x -= e.movementY * 0.002;
    euler.x = Math.max(-Math.PI/2, Math.min(Math.PI/2, euler.x));
    camera.quaternion.setFromEuler(euler);
  }

  function onKeyDown(e) {
    if (e.code === 'KeyW' || e.code === 'ArrowUp') moveForward = true;
    if (e.code === 'KeyS' || e.code === 'ArrowDown') moveBackward = true;
    if (e.code === 'KeyA' || e.code === 'ArrowLeft') moveLeft = true;
    if (e.code === 'KeyD' || e.code === 'ArrowRight') moveRight = true;
  }

  function onKeyUp(e) {
    if (e.code === 'KeyW' || e.code === 'ArrowUp') moveForward = false;
    if (e.code === 'KeyS' || e.code === 'ArrowDown') moveBackward = false;
    if (e.code === 'KeyA' || e.code === 'ArrowLeft') moveLeft = false;
    if (e.code === 'KeyD' || e.code === 'ArrowRight') moveRight = false;
  }

  function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  let prevTime = performance.now();

  function animate() {
    requestAnimationFrame(animate);

    const delta = (performance.now() - prevTime) / 1000;
    prevTime = performance.now();

    if (isLocked) {
      velocity.x -= velocity.x * 12 * delta;
      velocity.z -= velocity.z * 12 * delta;

      direction.z = Number(moveForward) - Number(moveBackward);
      direction.x = Number(moveRight) - Number(moveLeft);
      direction.normalize();

      const speed = 35;
      if (moveForward || moveBackward) velocity.z -= direction.z * speed * delta;
      if (moveLeft || moveRight) velocity.x -= direction.x * speed * delta;

      const fwd = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
      fwd.y = 0;
      fwd.normalize();
      const right = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
      right.y = 0;
      right.normalize();

      const mx = right.x * -velocity.x + fwd.x * -velocity.z;
      const mz = right.z * -velocity.x + fwd.z * -velocity.z;

      const nx = camera.position.x + mx * delta;
      const nz = camera.position.z + mz * delta;

      if (nx > -roomWidth/2 + 0.5 && nx < roomWidth/2 - 0.5) camera.position.x = nx;
      if (nz > -roomDepth/2 + 0.5 && nz < roomDepth/2 - 0.5) camera.position.z = nz;
    }

    renderer.render(scene, camera);
  }

  init();
})();
</script>
{{< /rawhtml >}}
