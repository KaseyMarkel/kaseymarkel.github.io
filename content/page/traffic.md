---
title: "Site Traffic"
socialShare: false
---

{{< rawhtml >}}
<style>
.intro-header { display: none !important; }
.header-section.has-img { display: none !important; }
div[role="main"].container {
  padding-top: 90px !important; margin-top: 0 !important; max-width: 100% !important;
}
footer { display: none !important; }

/* ---- password gate ---- */
.tg-gate {
  min-height: 78vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #0085a1 0%, #023e52 100%);
}
.tg-box {
  background: rgba(255,255,255,0.96); border-radius: 16px; padding: 40px;
  box-shadow: 0 8px 32px rgba(2,62,82,0.25); text-align: center; max-width: 400px; width: 90%;
}
.tg-box h2 { color: #233; margin-bottom: 8px; font-size: 1.5rem; }
.tg-box p { color: #667; margin-bottom: 22px; font-size: 0.95rem; }
.tg-box input[type=password] {
  width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 8px;
  font-size: 1rem; margin-bottom: 14px; box-sizing: border-box;
}
.tg-box input:focus { outline: none; border-color: #0085a1; }
.tg-box button {
  width: 100%; padding: 12px; background: #0085a1; color: #fff; border: none;
  border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background .15s;
}
.tg-box button:hover { background: #006d85; }
.tg-err { color: #ef4444; font-size: 0.9rem; margin-top: 10px; display: none; }
.tg-err.show { display: block; }

/* ---- dashboard ---- */
#tg-app { display: none; }
#tg-app.show { display: block; }
.tg-wrap { max-width: 1040px; margin: 0 auto; padding: 0 22px 70px; }
.tg-top { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 4px; }
.tg-top h1 { font-size: 2rem; letter-spacing: -0.02em; margin: 0; }
.tg-back { font-size: 0.9rem; color: #0085a1; text-decoration: none; }
.tg-back:hover { text-decoration: underline; }
.tg-sub { color: #777; font-size: 0.95rem; margin: 6px 0 26px; }

.tg-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 18px; margin-bottom: 34px; }
.tg-card {
  background: #fff; border: 1px solid #ececec; border-radius: 16px; padding: 22px 24px;
  box-shadow: 0 2px 14px rgba(0,0,0,0.05);
}
.tg-card .lbl { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; color: #889; margin: 0 0 8px; }
.tg-card .val { font-size: 2.1rem; font-weight: 700; color: #023e52; line-height: 1; letter-spacing: -0.02em; }
.tg-card .val small { font-size: 0.85rem; font-weight: 500; color: #99a; }

.tg-panel {
  background: #fff; border: 1px solid #ececec; border-radius: 16px; padding: 24px 26px;
  box-shadow: 0 2px 14px rgba(0,0,0,0.05); margin-bottom: 24px;
}
.tg-panel h3 { font-size: 1.1rem; margin: 0 0 18px; color: #2a2f35; letter-spacing: -0.01em; }
.tg-grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 760px) { .tg-grid2 { grid-template-columns: 1fr; } }

.tg-bar-row { display: flex; align-items: center; gap: 12px; margin: 9px 0; font-size: 0.9rem; }
.tg-bar-label { flex: 0 0 42%; color: #455; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tg-bar-track { flex: 1; background: #eef3f4; border-radius: 6px; height: 16px; overflow: hidden; }
.tg-bar-fill { height: 100%; background: linear-gradient(90deg, #0085a1, #00aecb); border-radius: 6px; }
.tg-bar-val { flex: 0 0 auto; color: #678; font-variant-numeric: tabular-nums; min-width: 44px; text-align: right; }

.tg-empty { color: #99a; font-size: 0.92rem; line-height: 1.5; background: #fafbfc; border: 1px dashed #dde; border-radius: 10px; padding: 18px 20px; }
.tg-svg { width: 100%; height: auto; display: block; }
.tg-foot { font-size: 0.82rem; color: #99a; margin-top: 4px; }
.tg-foot a { color: #0085a1; }
.tg-link-btn {
  display: inline-block; margin-top: 6px; padding: 10px 18px; background: #0085a1; color: #fff;
  border-radius: 9px; font-weight: 600; font-size: 0.9rem; text-decoration: none;
}
.tg-link-btn:hover { background: #006d85; color: #fff; text-decoration: none; }
</style>

<!-- ============ PASSWORD GATE ============ -->
<div id="tg-gate" class="tg-gate">
  <div class="tg-box">
    <h2>📈 Site Traffic</h2>
    <p>Enter the password to view visitor analytics.</p>
    <input type="password" id="tg-pw" placeholder="Password"
           onkeypress="if(event.key==='Enter') tgCheck()">
    <button onclick="tgCheck()">Unlock</button>
    <p id="tg-pw-err" class="tg-err">Incorrect password.</p>
  </div>
</div>

<!-- ============ DASHBOARD ============ -->
<div id="tg-app">
  <div class="tg-wrap">
    <div class="tg-top">
      <h1>Site Traffic</h1>
      <a class="tg-back" href="/page/projects/">&larr; Back to Projects</a>
    </div>
    <p class="tg-sub">Privacy-friendly analytics for kaseymarkel.com, via GoatCounter.</p>

    <div class="tg-cards">
      <div class="tg-card"><p class="lbl">Total page views</p><div class="val" id="tg-views">&hellip;</div></div>
      <div class="tg-card"><p class="lbl">Unique visitors</p><div class="val" id="tg-uniq">&hellip;</div></div>
      <div class="tg-card"><p class="lbl">Views, last 30 days</p><div class="val" id="tg-30d">&hellip;</div></div>
    </div>

    <div class="tg-panel">
      <h3>Visits over time <span style="font-weight:400;color:#99a;font-size:0.85rem;">(last 30 days)</span></h3>
      <div id="tg-timeseries">
        <div class="tg-empty">Daily history starts building once the snapshot has run on two separate days &mdash; the first delta needs a day-over-day comparison.</div>
      </div>
    </div>

    <div class="tg-panel">
      <h3>Top pages <span style="font-weight:400;color:#99a;font-size:0.85rem;">(all-time)</span></h3>
      <div id="tg-pages"><div class="tg-empty">Populates after the first daily snapshot runs.</div></div>
    </div>

    <p class="tg-foot" id="tg-updated"></p>
    <a class="tg-link-btn" href="https://kaseymarkel.goatcounter.com" target="_blank" rel="noopener">Open full GoatCounter dashboard &rarr;</a>
  </div>
</div>

<script>
(function () {
  var GC = "kaseymarkel"; // GoatCounter site code -> https://<GC>.goatcounter.com
  var BASE = "https://" + GC + ".goatcounter.com";

  window.tgCheck = function () {
    var input = document.getElementById('tg-pw');
    if (input.value === 'traffic') {
      sessionStorage.setItem('traffic-auth', 'true');
      tgReveal();
    } else {
      document.getElementById('tg-pw-err').classList.add('show');
      input.value = ''; input.focus();
    }
  };

  function tgReveal() {
    document.getElementById('tg-gate').style.display = 'none';
    document.getElementById('tg-app').classList.add('show');
    tgLoad();
  }

  function fmt(n) { return (n == null ? '0' : String(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function num(s) { return parseInt(String(s == null ? '0' : s).replace(/[^0-9]/g, ''), 10) || 0; }

  function tgLoad() {
    // ---- Live headline numbers from the public (tokenless) counter endpoint ----
    fetch(BASE + "/counter/TOTAL.json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d) return;
        document.getElementById('tg-views').textContent = fmt(d.count);
        document.getElementById('tg-uniq').textContent = fmt(d.count_unique);
      })
      .catch(function () {});

    // ---- Time series + top pages from the daily snapshot (tokenless GitHub Action) ----
    fetch("/traffic-data.json", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (d) { renderRich(d); }
        else { document.getElementById('tg-30d').textContent = '—'; }
      })
      .catch(function () { document.getElementById('tg-30d').textContent = '—'; });
  }

  function renderRich(d) {
    if (d.updated) document.getElementById('tg-updated').innerHTML =
      'Snapshot updated ' + d.updated + ' &middot; built from GoatCounter’s public counter by a daily GitHub Action (no cookies, no API token).';

    if (d.daily && d.daily.length) {
      renderLine(d.daily);
      var sum = d.daily.reduce(function (a, p) { return a + num(p.count); }, 0);
      document.getElementById('tg-30d').textContent = fmt(sum);
    } else {
      document.getElementById('tg-30d').textContent = '—';
    }
    if (d.top_pages && d.top_pages.length) renderBars('tg-pages', d.top_pages.map(function (p) {
      return { label: p.path, value: p.count };
    }));
  }

  function renderBars(id, rows) {
    rows = rows.filter(function (r) { return r.value > 0; }).slice(0, 8);
    if (!rows.length) return;
    var max = rows.reduce(function (m, r) { return Math.max(m, r.value); }, 0) || 1;
    var html = rows.map(function (r) {
      var pct = Math.max(2, Math.round(r.value / max * 100));
      return '<div class="tg-bar-row">' +
        '<span class="tg-bar-label" title="' + esc(r.label) + '">' + esc(r.label) + '</span>' +
        '<span class="tg-bar-track"><span class="tg-bar-fill" style="width:' + pct + '%"></span></span>' +
        '<span class="tg-bar-val">' + fmt(r.value) + '</span></div>';
    }).join('');
    document.getElementById(id).innerHTML = html;
  }

  function renderLine(daily) {
    var W = 920, H = 220, pad = 34;
    var vals = daily.map(function (p) { return num(p.count); });
    var max = Math.max.apply(null, vals.concat([1]));
    var n = daily.length;
    var x = function (i) { return pad + (n <= 1 ? 0 : i * (W - 2 * pad) / (n - 1)); };
    var y = function (v) { return H - pad - (v / max) * (H - 2 * pad); };
    var pts = daily.map(function (p, i) { return x(i) + ',' + y(num(p.count)); }).join(' ');
    var area = 'M' + x(0) + ',' + (H - pad) + ' L' + pts.replace(/ /g, ' L') + ' L' + x(n - 1) + ',' + (H - pad) + ' Z';
    var first = daily[0].date, last = daily[n - 1].date;
    var svg = '<svg class="tg-svg" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" role="img">' +
      '<defs><linearGradient id="tgFill" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0%" stop-color="#0085a1" stop-opacity="0.22"/>' +
      '<stop offset="100%" stop-color="#0085a1" stop-opacity="0"/></linearGradient></defs>' +
      '<line x1="' + pad + '" y1="' + (H - pad) + '" x2="' + (W - pad) + '" y2="' + (H - pad) + '" stroke="#e6ebec" stroke-width="1"/>' +
      '<path d="' + area + '" fill="url(#tgFill)"/>' +
      '<polyline points="' + pts + '" fill="none" stroke="#0085a1" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>' +
      '<text x="' + pad + '" y="16" font-size="12" fill="#99a">' + fmt(max) + ' / day peak</text>' +
      '<text x="' + pad + '" y="' + (H - 8) + '" font-size="12" fill="#99a">' + esc(first) + '</text>' +
      '<text x="' + (W - pad) + '" y="' + (H - 8) + '" font-size="12" fill="#99a" text-anchor="end">' + esc(last) + '</text>' +
      '</svg>';
    document.getElementById('tg-timeseries').innerHTML = svg;
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (sessionStorage.getItem('traffic-auth') === 'true') tgReveal();
  });
})();
</script>
{{< /rawhtml >}}
