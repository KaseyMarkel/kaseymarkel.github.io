---
title: "How dense is San Francisco, really?"
socialShare: false
---

{{< rawhtml >}}
<style>
.intro-header { display: none !important; }
.header-section.has-img { display: none !important; }
div[role="main"].container { padding-top: 100px !important; margin-top: 0 !important; max-width: 100% !important; }
div[role="main"].container .row { margin: 0 !important; }
div[role="main"].container .row > div[class*="col-"] {
  width: 100% !important; max-width: 100% !important; flex: 0 0 100% !important; margin: 0 !important; padding: 0 !important;
}

.sfd { max-width: 1180px; margin: 0 auto; padding: 0 18px 60px; }
.sfd-text { max-width: 760px; }
.sfd h1 { font-size: 34px; line-height: 1.15; letter-spacing: -0.02em; margin: 0 0 14px; }
.sfd h2 { font-size: 24px; letter-spacing: -0.01em; margin: 44px 0 6px; }
.sfd p { font-size: 18px; line-height: 1.6; }
.sfd .lede { font-size: 19px; }
.sfd .muted { color: #667; font-size: 15px; line-height: 1.5; }
.sfd-back { font-size: 15px; color: #0085a1; }

.sfd-map { width: 100%; border: 0; display: block; height: 760px; margin: 10px 0 4px; }
.sfd-open { font-size: 15px; }

.sfd-controls { display: flex; flex-wrap: wrap; gap: 14px 22px; align-items: center; margin: 14px 0 12px; }
.sfd-group { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.sfd-group > span { font-size: 12px; text-transform: uppercase; letter-spacing: .06em; color: #778; font-weight: 700; font-family: "Open Sans", sans-serif; }
.sfd-seg { display: inline-flex; border: 1px solid #d5dde0; border-radius: 9px; overflow: hidden; }
.sfd-seg button { font: 600 14px "Open Sans", sans-serif; border: 0; border-right: 1px solid #d5dde0; background: #fff; color: #234; padding: 7px 13px; cursor: pointer; }
.sfd-seg button:last-child { border-right: 0; }
.sfd-seg button[aria-pressed="true"] { background: #0085a1; color: #fff; }
.sfd-seg button:focus-visible { outline: 2px solid #0085a1; outline-offset: 2px; }

.sfd-tablewrap { overflow-x: auto; border: 1px solid #e6eaec; border-radius: 12px; }
.sfd table { width: 100%; border-collapse: collapse; font: 14.5px/1.35 "Open Sans", sans-serif; font-variant-numeric: tabular-nums; }
.sfd th, .sfd td { padding: 7px 10px; border-bottom: 1px solid #eef1f2; text-align: left; white-space: nowrap; }
.sfd th { background: #f6f8f9; font-weight: 700; color: #345; position: sticky; top: 0; }
.sfd th.sortable { cursor: pointer; user-select: none; }
.sfd th.sortable:hover { color: #0085a1; }
.sfd th .arr { color: #0085a1; font-size: 11px; }
.sfd td.num, .sfd th.num { text-align: right; }
.sfd td.where { white-space: normal; min-width: 180px; }
.sfd td .nb { color: #8a5a00; font-size: 12.5px; }
.sfd tr.sf td { background: #fff4d1; }
.sfd tr.sf td:first-child { box-shadow: inset 4px 0 0 #e0a400; }
.sfd .flag { display: inline-block; min-width: 54px; font-size: 12px; font-weight: 700; color: #456; }
.sfd .lowland { color: #b4572b; font-weight: 700; }
.sfd td a.m { color: #0085a1; text-decoration: none; font-size: 13px; }
.sfd .blank { color: #bbb; }
.sfd .best { font-weight: 700; }
.sfd-legend { font-size: 13.5px; color: #667; margin: 8px 2px 0; font-family: "Open Sans", sans-serif; }
.sfd-legend i { display: inline-block; width: 12px; height: 12px; background: #fff4d1; border-left: 4px solid #e0a400; vertical-align: -1px; margin-right: 4px; }
@media (prefers-color-scheme: dark) {
  .sfd .muted, .sfd-legend { color: #a3aab2; }
  .sfd-group > span { color: #a3aab2; }
  .sfd-seg { border-color: #3a4248; }
  .sfd-seg button { background: #15191c; color: #e6e9eb; border-right-color: #3a4248; }
  .sfd-seg button[aria-pressed="true"] { background: #0085a1; color: #fff; }
  .sfd-tablewrap { border-color: #2b3236; }
  .sfd th { background: #1b2023; color: #cfd6da; }
  .sfd th, .sfd td { border-bottom-color: #24292c; }
  .sfd .flag { color: #b9c3c8; }
  .sfd tr.sf td { background: #3d3212; }
  .sfd td .nb { color: #f0c060; }
  .sfd td a.m, .sfd th.sortable:hover, .sfd th .arr { color: #50afff; }
  .sfd .blank { color: #555; }
  .sfd-legend i { background: #3d3212; }
}
@media (max-width: 600px) { .sfd h1 { font-size: 27px; } .sfd p { font-size: 17px; } .sfd th, .sfd td { padding: 6px 7px; } }
</style>

<div class="sfd">
  <p><a class="sfd-back" href="/page/projects/">&larr; Projects</a></p>
  <div class="sfd-text">
    <h1>How dense is San Francisco, really?</h1>
    <div class="sfd-lede">
      <p class="lede">San Francisco feels packed, and there&rsquo;s a claim going around that part of it is among the densest places in America. It holds up. I counted all 8.2 million 2020 Census blocks and slid squares of 1, 2, 3, 5 and 10&nbsp;km across the whole country. By homes, the area around the Tenderloin and Nob Hill is the densest in the US outside New York City at every size from 1 to 5&nbsp;km (at 10&nbsp;km, Chicago edges ahead). Its densest square kilometre holds about 25,800 homes. Only ten squares in the US have more, all of them in Manhattan.</p>
      <p>But it&rsquo;s dense in homes more than in people, and the density doesn&rsquo;t spread far. Those homes are small: about 1.5 residents each, against about 2 in Barcelona&rsquo;s densest square. SF&rsquo;s densest square kilometre has about 39,700 residents. In the four countries I checked, 78 squares beat it: 27 in New York, 44 in Barcelona, its neighbouring towns, Madrid and Valencia, and 7 in Paris. Zoom out to a 10&nbsp;km square, about the size of the city, and SF&rsquo;s best holds about 8,200 residents per km² (it&rsquo;s 98% land, so water isn&rsquo;t the excuse). London&rsquo;s best holds 12,300, Madrid&rsquo;s and Barcelona&rsquo;s about 18,900, New York&rsquo;s 19,300 and Paris&rsquo;s 21,700. Cities built out with mid-rise apartments fit two to three times as many people on the same ground.</p>
      <p class="muted">The map below shows SF block by block. Switch between homes and people, and step the resolution out from single census blocks to ZIP codes. Hover or tap for numbers.</p>
    </div>
  </div>

  <iframe class="sfd-map" id="sfd-map" src="/sf-density/map.html?embed=1" title="San Francisco density map" loading="lazy"></iframe>
  <p class="sfd-open"><a href="/sf-density/map.html" target="_blank" rel="noopener">Open the map in its own window ↗</a></p>

  <h2>The densest squares in the US, England &amp; Wales, Spain and France</h2>
  <p class="muted">The 50 densest squares of each size, all four countries in one ranking. Squares don&rsquo;t overlap: once a square is listed, everything overlapping it is skipped. Click a column to sort. San Francisco rows are highlighted.</p>
  <div class="sfd-controls">
    <div class="sfd-group"><span>Rank by</span>
      <div class="sfd-seg" id="sfd-metric"><button data-v="people" aria-pressed="true">People</button><button data-v="homes" aria-pressed="false">Homes</button></div>
    </div>
    <div class="sfd-group"><span>Square</span>
      <div class="sfd-seg" id="sfd-size"><button data-v="1" aria-pressed="true">1 km</button><button data-v="2" aria-pressed="false">2 km</button><button data-v="3" aria-pressed="false">3 km</button><button data-v="5" aria-pressed="false">5 km</button><button data-v="10" aria-pressed="false">10 km</button></div>
    </div>
  </div>
  <div class="sfd-tablewrap"><table id="sfd-top"></table></div>
  <p class="sfd-legend"><i></i>San Francisco &nbsp;·&nbsp; <span class="lowland">Land %</span> under 85% means part of the square is water, which pulls its density down.</p>

  <h2>Summary by city</h2>
  <p class="muted">Each city&rsquo;s densest square of each size, per km² (squares whose centre is in the city). Blank means none of that city&rsquo;s squares made its country&rsquo;s top 60.</p>
  <div class="sfd-controls">
    <div class="sfd-group"><span>Show</span>
      <div class="sfd-seg" id="sfd-smetric"><button data-v="people" aria-pressed="true">People/km²</button><button data-v="homes" aria-pressed="false">Homes/km²</button></div>
    </div>
  </div>
  <div class="sfd-tablewrap"><table id="sfd-summary"></table></div>

  <div class="sfd-text">
    <h2>How it was made</h2>
    <p>For each country I took the finest official counts available. For the US, all 2020 Census blocks. For England and Wales, 2021 Census output areas. For Spain, 2021 Census sections. For France, INSEE&rsquo;s 2021 Filosofi 200&nbsp;m grid. I placed each small area at one point and slid squares across the map in 100&nbsp;m steps on an equal-area projection. The ranking keeps the densest square, drops everything overlapping it, and repeats, so the top 50 aren&rsquo;t 50 copies of one Manhattan block.</p>
    <p>A few things aren&rsquo;t like-for-like. &ldquo;Homes&rdquo; means every housing unit in the US and every dwelling in Spain, vacant ones included, but only occupied homes in England, Wales and France. So people per km² is the fairer comparison across countries. The French grid leaves out people living in institutions and student halls (it covers 94% of Paris&rsquo;s census population), so Paris is slightly undercounted. Densities are per km² of the whole square, water included. The Land % column shows how much of each square is land; it&rsquo;s approximate, because each area&rsquo;s land counts at its centre point. Scotland and Northern Ireland aren&rsquo;t included.</p>
    <p>Code and data to reproduce everything, including a spreadsheet of all the tables: <a href="https://github.com/KaseyMarkel/sf-density">github.com/KaseyMarkel/sf-density</a>.</p>
    <p class="muted">Made by Kasey Markel and Claude Opus 5.5.</p>
  </div>
</div>

<script>
(function(){
  var frame = document.getElementById('sfd-map');
  window.addEventListener('message', function(e){
    if (e.source === frame.contentWindow && e.data && e.data.sfDensityHeight) frame.style.height = (e.data.sfDensityHeight + 4) + 'px';
  });

  var D, S = {metric: 'people', size: 1, sortKey: null, sortDir: -1, smetric: 'people'};
  var fmt = function(n){ return Math.round(n).toLocaleString('en-US'); };
  var esc = function(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); };
  var FLAG = {US: 'US', UK: 'UK', Spain: 'Spain', France: 'France'};

  function rows(){
    var s = S.size, list = D.tables[S.metric + '_' + s + 'km'].map(function(r, i){
      return {rank: i + 1, country: r.country, where: r.where, nb: r.nb, sf: r.city === 'San Francisco',
        homes: r.homes / s / s, people: r.people / s / s, land: r.land_km2 == null ? null : r.land_km2 / s / s, lat: r.lat, lon: r.lon};
    });
    if (S.sortKey) {
      var k = S.sortKey, d = S.sortDir;
      list.sort(function(a, b){
        var x = a[k], y = b[k];
        if (x == null) return 1; if (y == null) return -1;
        return (typeof x === 'string' ? x.localeCompare(y) : x - y) * d;
      });
    }
    return list;
  }
  var COLS = [
    ['rank', 'Rank', 'num'], ['country', 'Country', ''], ['where', 'Where (square centre)', ''],
    ['homes', 'Homes/km²', 'num'], ['people', 'People/km²', 'num'], ['land', 'Land %', 'num'], [null, 'Map', '']
  ];
  function renderTop(){
    var t = document.getElementById('sfd-top'), z = {1: 15, 2: 14, 3: 14, 5: 13, 10: 12}[S.size];
    var h = '<thead><tr>' + COLS.map(function(c){
      var arr = c[0] && S.sortKey === c[0] ? ' <span class="arr">' + (S.sortDir < 0 ? '▼' : '▲') + '</span>' : '';
      var isRank = c[0] === 'rank' && !S.sortKey;
      return '<th class="' + c[2] + (c[0] ? ' sortable' : '') + '"' + (c[0] ? ' data-k="' + c[0] + '"' : '') + '>' + c[1] + arr + (isRank ? '' : '') + '</th>';
    }).join('') + '</tr></thead><tbody>';
    h += rows().map(function(r){
      var land = r.land == null ? '<span class="blank">n/a</span>' : '<span class="' + (r.land < 0.85 ? 'lowland' : '') + '">' + Math.min(100, Math.round(r.land * 100)) + '%</span>';
      return '<tr class="' + (r.sf ? 'sf' : '') + '"><td class="num">' + r.rank + '</td><td><span class="flag">' + FLAG[r.country] + '</span></td>' +
        '<td class="where">' + esc(r.where) + (r.nb ? ' <span class="nb">· near ' + esc(r.nb) + '</span>' : '') + '</td>' +
        '<td class="num' + (S.metric === 'homes' ? ' best' : '') + '">' + fmt(r.homes) + '</td><td class="num' + (S.metric === 'people' ? ' best' : '') + '">' + fmt(r.people) + '</td>' +
        '<td class="num">' + land + '</td><td><a class="m" target="_blank" rel="noopener" href="https://www.openstreetmap.org/?mlat=' + r.lat + '&mlon=' + r.lon + '#map=' + z + '/' + r.lat + '/' + r.lon + '">map ↗</a></td></tr>';
    }).join('') + '</tbody>';
    t.innerHTML = h;
  }
  function renderSummary(){
    var t = document.getElementById('sfd-summary'), m = S.smetric, sizes = D.meta.sizes;
    var best = {}; sizes.forEach(function(s){ best[s] = Math.max.apply(null, D.summary.map(function(r){ return r[m + '_' + s + 'km'] || 0; })); });
    var h = '<thead><tr><th>City</th><th>Country</th>' + sizes.map(function(s){ return '<th class="num">' + s + '×' + s + ' km</th>'; }).join('') + '</tr></thead><tbody>';
    h += D.summary.map(function(r){
      return '<tr class="' + (r.city === 'San Francisco' ? 'sf' : '') + '"><td>' + esc(r.city) + '</td><td><span class="flag">' + FLAG[r.country] + '</span></td>' +
        sizes.map(function(s){ var v = r[m + '_' + s + 'km'];
          return '<td class="num' + (v === best[s] ? ' best' : '') + '">' + (v == null ? '<span class="blank">–</span>' : fmt(v)) + '</td>'; }).join('') + '</tr>';
    }).join('') + '</tbody>';
    t.innerHTML = h;
  }
  function seg(id, fn){
    var el = document.getElementById(id);
    el.addEventListener('click', function(e){
      var b = e.target.closest('button'); if (!b) return;
      el.querySelectorAll('button').forEach(function(x){ x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      fn(b.dataset.v);
    });
  }
  seg('sfd-metric', function(v){ S.metric = v; S.sortKey = null; renderTop(); });
  seg('sfd-size', function(v){ S.size = +v; renderTop(); });
  seg('sfd-smetric', function(v){ S.smetric = v; renderSummary(); });
  document.getElementById('sfd-top').addEventListener('click', function(e){
    var th = e.target.closest('th[data-k]'); if (!th) return;
    var k = th.dataset.k;
    if (k === 'rank') { S.sortKey = null; S.sortDir = -1; }
    else if (S.sortKey === k) S.sortDir = -S.sortDir;
    else { S.sortKey = k; S.sortDir = (k === 'country' || k === 'where') ? 1 : -1; }
    renderTop();
  });

  fetch('/sf-density/tables.json').then(function(r){ return r.json(); }).then(function(d){
    D = d; renderTop(); renderSummary();
  });
})();
</script>
{{< /rawhtml >}}
