---
title: "Projects"
socialShare: false
aliases:
  - /page/private-projects/
---

{{< rawhtml >}}
<style>
.intro-header { display: none !important; }
.header-section.has-img { display: none !important; }
div[role="main"].container {
  padding-top: 100px !important;
  margin-top: 0 !important;
  max-width: 100% !important;
}

.proj-wrap { max-width: 1040px; margin: 0 auto; padding: 0 22px 60px; }
.proj-lead { margin: 0 0 6px; }
.proj-lead h1 { font-size: 2rem; letter-spacing: -0.02em; margin: 0; }
.proj-lead p { color: #666; font-size: 1.02rem; margin: 8px 0 0; max-width: 720px; }

.proj-section-label {
  font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.1em;
  color: #9aa7ae; font-weight: 700; margin: 42px 0 16px;
  border-bottom: 1px solid #eee; padding-bottom: 8px;
}

.proj-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.proj-card {
  background: #fff; border: 1px solid #ececec; border-radius: 16px;
  padding: 24px 24px 22px; text-decoration: none; color: inherit; display: block;
  box-shadow: 0 2px 14px rgba(0,0,0,0.05);
  transition: transform .18s, box-shadow .18s, border-color .18s;
}
.proj-card:hover {
  transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  text-decoration: none; color: inherit; border-color: #d7e7eb;
}
.proj-card.feature {
  grid-column: span 1;
  background: linear-gradient(180deg, #f7fbfc 0%, #ffffff 60%);
  border-color: #d7e7eb;
}
.proj-icon { font-size: 2.1rem; line-height: 1; margin-bottom: 14px; }
.proj-card h3 { font-size: 1.22rem; margin: 0 0 8px; color: #2a2f35; letter-spacing: -0.01em; }
.proj-card p { font-size: 0.92rem; line-height: 1.5; color: #667; margin: 0; }
.proj-tags { margin-top: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.proj-tag {
  font-size: 0.72rem; font-weight: 700; padding: 3px 10px; border-radius: 20px;
  letter-spacing: 0.02em;
}
.t-play { background: #e0f3f7; color: #0d6c82; }
.t-new  { background: #fef3c7; color: #92400e; }
.t-build{ background: #e9ecef; color: #495057; }
.t-craft{ background: #fde2e2; color: #9b2c2c; }
.t-art  { background: #ede7f6; color: #5e35b1; }
.t-code { background: #e3f0e5; color: #2f6f3e; }

/* private subsection */
.pp-box {
  background: #f7f8fa; border: 1px solid #ececec; border-radius: 16px;
  padding: 26px; margin-top: 4px;
}
.pp-locked { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.pp-locked .pp-text { flex: 1; min-width: 240px; }
.pp-locked h3 { margin: 0 0 4px; font-size: 1.12rem; color: #2a2f35; }
.pp-locked p { margin: 0; color: #777; font-size: 0.9rem; }
.pp-form { display: flex; gap: 10px; }
.pp-form input {
  padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 9px; font-size: 0.95rem;
  width: 180px;
}
.pp-form input:focus { outline: none; border-color: #0085a1; }
.pp-form button {
  padding: 10px 18px; background: #0085a1; color: #fff; border: none; border-radius: 9px;
  font-weight: 600; cursor: pointer; transition: background .15s;
}
.pp-form button:hover { background: #006d85; }
.pp-error { color: #ef4444; font-size: 0.85rem; margin-top: 10px; display: none; }
.pp-error.show { display: block; }
#pp-unlocked { display: none; margin-top: 20px; }
#pp-unlocked.show { display: block; }

@media (max-width: 600px) {
  .pp-form { width: 100%; }
  .pp-form input { flex: 1; width: auto; }
}
</style>

<div class="proj-wrap">
  <div class="proj-lead">
    <h1>Projects</h1>
    <p>Things I&rsquo;ve made &mdash; interactive toys and software, and objects built out of wood, glass, concrete, and plants. A couple are playable right in the browser.</p>
  </div>

  <div class="proj-section-label">Interactive</div>
  <div class="proj-grid">
    <a class="proj-card feature" href="/page/flying/">
      <div class="proj-icon">🪂</div>
      <h3>Paraglide&nbsp;Go</h3>
      <p>Upload your paragliding flights and see how much of the planet you&rsquo;ve &ldquo;captured&rdquo; &mdash; every thermal you circle and every triangle your cross&#8209;country flights enclose becomes territory. Bring your own IGC files, or explore the demo.</p>
      <div class="proj-tags"><span class="proj-tag t-play">Interactive</span><span class="proj-tag t-new">New</span></div>
    </a>
    <a class="proj-card feature" href="/page/anchor-builder/">
      <div class="proj-icon">⚓</div>
      <h3>Anchor Builder</h3>
      <p>A trad-climbing anchor-building simulator and training game. Read the rock, pick gear off a real rack, and place a three-piece anchor against a draining pump clock &mdash; then fall-test it.</p>
      <div class="proj-tags"><span class="proj-tag t-play">Game</span></div>
    </a>
  </div>

  <div class="proj-section-label">Making &amp; tinkering</div>
  <div class="proj-grid">
    <a class="proj-card" href="/page/glass/">
      <div class="proj-icon">🔥</div>
      <h3>Glass</h3>
      <p>Furnace glassblowing and torchwork &mdash; including fuming silver vapour onto hot glass to grow colour, a trick that still feels like alchemy.</p>
      <div class="proj-tags"><span class="proj-tag t-craft">Craft</span></div>
    </a>
    <a class="proj-card" href="/page/living-wall/">
      <div class="proj-icon">🌿</div>
      <h3>Living Wall</h3>
      <p>A one-square-metre mixed-media living wall I designed and built: a waterproof wooden frame with a self-watering bucket system feeding dozens of plants.</p>
      <div class="proj-tags"><span class="proj-tag t-build">Build</span></div>
    </a>
    <a class="proj-card" href="/page/wing-watchers-perch/">
      <div class="proj-icon">🪑</div>
      <h3>Wing Watcher&rsquo;s Perch</h3>
      <p>A public bench on the shore of the bay, cast from salvaged concrete, rebar, and ~350 lbs of cement into one solid piece.</p>
      <div class="proj-tags"><span class="proj-tag t-build">Build</span></div>
    </a>
    <a class="proj-card" href="/page/gallery/">
      <div class="proj-icon">🎨</div>
      <h3>Pour Paintings</h3>
      <p>Real acrylic pour paintings I&rsquo;ve made &mdash; most hang in my garage, but here they live in a virtual gallery.</p>
      <div class="proj-tags"><span class="proj-tag t-art">Art</span></div>
    </a>
    <a class="proj-card" href="/page/mandarin/">
      <div class="proj-icon">🀄</div>
      <h3>Zhōngpath</h3>
      <p>Learn Mandarin characters through spaced repetition &mdash; five new characters a day, one story at a time.</p>
      <div class="proj-tags"><span class="proj-tag t-code">Software</span></div>
    </a>
    <a class="proj-card" href="/page/origin/">
      <div class="proj-icon">✨</div>
      <h3>Origin</h3>
      <p>A project made of bits rather than atoms &mdash; something I wouldn&rsquo;t have had the time to build by hand, made possible by modern AI.</p>
      <div class="proj-tags"><span class="proj-tag t-code">Bits</span></div>
    </a>
  </div>

  <div class="proj-section-label">Private projects</div>
  <div class="pp-box">
    <div id="pp-gate" class="pp-locked">
      <div class="pp-text">
        <h3>🔒 Password-protected</h3>
        <p>A few work-related dashboards live behind a password. Enter it to view them.</p>
      </div>
      <div>
        <div class="pp-form">
          <input type="password" id="pp-password" placeholder="Password"
                 onkeypress="if(event.key==='Enter') checkPP()">
          <button onclick="checkPP()">Unlock</button>
        </div>
        <p id="pp-error" class="pp-error">Incorrect password.</p>
      </div>
    </div>

    <div id="pp-unlocked">
      <div class="proj-grid">
        <a class="proj-card" href="/page/dashboard/">
          <div class="proj-icon">🌱</div>
          <h3>Breeding Dashboard</h3>
          <p>Real-time breeding-program metrics &mdash; pipeline funnel, trait pyramiding, cycle speed, and operational issues.</p>
          <div class="proj-tags"><span class="proj-tag t-play">Live</span></div>
        </a>
        <a class="proj-card" href="/page/cea-dashboard/">
          <div class="proj-icon">📊</div>
          <h3>Biofortified Maize CEA</h3>
          <p>Interactive cost-effectiveness analysis for Semilla Nueva&rsquo;s biofortified maize program &mdash; DALYs, WELLBYs, and benefit-cost modeling.</p>
          <div class="proj-tags"><span class="proj-tag t-new">New</span></div>
        </a>
      </div>
    </div>
  </div>
</div>

<script>
function revealPP() {
  document.getElementById('pp-gate').style.display = 'none';
  document.getElementById('pp-unlocked').classList.add('show');
}
function checkPP() {
  var input = document.getElementById('pp-password');
  if (input.value === 'Semilla') {
    sessionStorage.setItem('private-projects-auth', 'true');
    revealPP();
  } else {
    document.getElementById('pp-error').classList.add('show');
    input.value = ''; input.focus();
  }
}
document.addEventListener('DOMContentLoaded', function() {
  if (sessionStorage.getItem('private-projects-auth') === 'true') revealPP();
});
</script>
{{< /rawhtml >}}
