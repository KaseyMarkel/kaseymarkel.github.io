---
title: "The Basketball Cube"
socialShare: true
---

{{< rawhtml >}}
<style>
/* Hide entire header section and add top spacing */
.intro-header {
  display: none !important;
}
.header-section.has-img {
  display: none !important;
}

/* Add top padding to main content to account for navigation bar */
div[role="main"].container {
  padding-top: 100px !important;
  margin-top: 0 !important;
}

/* Override the default column width for wider layout */
div[role="main"].container .col-lg-8 {
  width: 100% !important;
  margin-left: 0 !important;
}
div[role="main"].container .col-lg-offset-2 {
  margin-left: 0 !important;
}
div[role="main"].container .col-md-10 {
  width: 100% !important;
}
div[role="main"].container .col-md-offset-1 {
  margin-left: 0 !important;
}

/* Essay layout */
.essay-page {
  max-width: 680px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Essay header */
.essay-page-header {
  text-align: center;
  margin-bottom: 50px;
  padding-bottom: 40px;
  border-bottom: 1px solid #e0e0e0;
}

.essay-page-label {
  font-family: 'Open Sans', sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: #aaa;
  margin-bottom: 20px;
}

.essay-page-label a {
  color: #aaa;
  text-decoration: none;
  transition: color 0.2s ease;
}

.essay-page-label a:hover {
  color: #0085a1;
}

.essay-page-title {
  font-family: 'Lora', Georgia, serif;
  font-size: 40px;
  font-weight: 700;
  line-height: 1.2;
  color: #222;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
}

.essay-page-meta {
  font-family: 'Open Sans', sans-serif;
  font-size: 13px;
  color: #999;
  letter-spacing: 0.3px;
}

/* Essay body */
.essay-body {
  font-family: 'Lora', Georgia, serif;
  font-size: 19px;
  line-height: 1.8;
  color: #333;
}

.essay-body p {
  margin-bottom: 1.6em;
}

.essay-body a {
  color: #008AFF;
  text-decoration: underline;
  text-decoration-color: rgba(0, 138, 255, 0.3);
  text-underline-offset: 2px;
  transition: text-decoration-color 0.2s ease;
}

.essay-body a:hover {
  text-decoration-color: #008AFF;
}

.essay-body em {
  font-style: italic;
}

.essay-body strong {
  font-weight: 700;
}

/* Drop cap */
.essay-body .essay-first-paragraph::first-letter {
  float: left;
  font-family: 'Lora', Georgia, serif;
  font-size: 68px;
  line-height: 0.85;
  font-weight: 700;
  padding-right: 8px;
  padding-top: 4px;
  color: #222;
}

/* Chart container */
.essay-chart-container {
  margin: 2.5em -40px;
  padding: 0;
  position: relative;
}

.essay-chart-container .chart-caption {
  font-family: 'Open Sans', sans-serif;
  font-size: 12px;
  color: #999;
  text-align: center;
  margin-top: 8px;
  letter-spacing: 0.3px;
}

/* Data table styling */
.essay-data-table-wrapper {
  margin: 2em 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.essay-data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Open Sans', sans-serif;
  font-size: 13px;
}

.essay-data-table thead th {
  font-weight: 700;
  font-size: 11px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #999;
  padding: 10px 12px;
  border-bottom: 2px solid #e0e0e0;
  text-align: left;
  white-space: nowrap;
}

.essay-data-table tbody td {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  color: #444;
  white-space: nowrap;
}

.essay-data-table tbody tr:hover td {
  background: #f8f8f8;
}

.essay-data-table .cat-youth { color: #2563eb; }
.essay-data-table .cat-hs { color: #16a34a; }
.essay-data-table .cat-college { color: #7c3aed; }
.essay-data-table .cat-pro { color: #ea580c; }
.essay-data-table .cat-3x3 { color: #ca8a04; }
.essay-data-table .cat-adaptive { color: #db2777; }

/* Footnotes */
.essay-footnotes {
  margin-top: 50px;
  padding-top: 30px;
  border-top: 1px solid #e0e0e0;
}

.essay-footnotes h3 {
  font-family: 'Open Sans', sans-serif;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #aaa;
  margin-bottom: 20px;
}

.essay-footnote {
  font-family: 'Lora', Georgia, serif;
  font-size: 15px;
  line-height: 1.7;
  color: #666;
  margin-bottom: 16px;
  padding-left: 28px;
  position: relative;
}

.essay-footnote-num {
  position: absolute;
  left: 0;
  font-family: 'Open Sans', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: #999;
  top: 2px;
}

/* Superscript footnote refs */
.essay-body .fn-ref {
  font-family: 'Open Sans', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: #008AFF;
  text-decoration: none;
  vertical-align: super;
  line-height: 0;
  margin-left: 1px;
}

.essay-body .fn-ref:hover {
  color: #0085a1;
}

/* Back link */
.essay-back {
  margin-top: 60px;
  padding-top: 30px;
  border-top: 1px solid #e0e0e0;
  text-align: center;
}

.essay-back a {
  font-family: 'Open Sans', sans-serif;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #aaa;
  text-decoration: none;
  transition: color 0.2s ease;
}

.essay-back a:hover {
  color: #0085a1;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  .essay-page-header {
    border-bottom-color: #333;
  }
  .essay-page-label, .essay-page-label a {
    color: #666;
  }
  .essay-page-label a:hover {
    color: #50afff;
  }
  .essay-page-title {
    color: #e8e8e8;
  }
  .essay-page-meta {
    color: #666;
  }
  .essay-body {
    color: #ccc;
  }
  .essay-body .essay-first-paragraph::first-letter {
    color: #e8e8e8;
  }
  .essay-body a {
    color: #50afff;
    text-decoration-color: rgba(80, 175, 255, 0.3);
  }
  .essay-body a:hover {
    text-decoration-color: #50afff;
  }
  .essay-body .fn-ref {
    color: #50afff;
  }
  .essay-body .fn-ref:hover {
    color: #b0e0ff;
  }
  .essay-chart-container .chart-caption {
    color: #666;
  }
  .essay-data-table thead th {
    color: #666;
    border-bottom-color: #333;
  }
  .essay-data-table tbody td {
    color: #bbb;
    border-bottom-color: #222;
  }
  .essay-data-table tbody tr:hover td {
    background: #1a1a1a;
  }
  .essay-footnotes {
    border-top-color: #333;
  }
  .essay-footnotes h3 {
    color: #555;
  }
  .essay-footnote {
    color: #888;
  }
  .essay-footnote-num {
    color: #666;
  }
  .essay-back {
    border-top-color: #333;
  }
  .essay-back a {
    color: #666;
  }
  .essay-back a:hover {
    color: #50afff;
  }
}

@media (max-width: 768px) {
  .essay-page-title {
    font-size: 30px;
  }
  .essay-body {
    font-size: 17px;
  }
  .essay-body .essay-first-paragraph::first-letter {
    font-size: 56px;
  }
  .essay-footnote {
    font-size: 14px;
  }
  .essay-chart-container {
    margin-left: 0;
    margin-right: 0;
  }
  .essay-data-table {
    font-size: 12px;
  }
}
/* Vibe Card image */
.essay-vibe-card-img {
  display: block;
  max-width: 480px;
  width: 100%;
  margin: 0 auto 40px;
  border-radius: 12px;
}
</style>

<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

<div class="essay-page">
  <div class="essay-page-header">
    <div class="essay-page-label"><a href="/page/essays/">Essays</a> &middot; 02</div>
    <h1 class="essay-page-title">The Basketball Cube</h1>
    <div class="essay-page-meta">Sports &middot; Equipment Standards &middot; Data Visualization</div>
  </div>

  <img class="essay-vibe-card-img" src="/img/vibe_card_basketball_cube.png" alt="Vibe Card for this essay" />

  <div class="essay-body">
    <p class="essay-first-paragraph">At a friend's 27th birthday party&thinsp;&mdash;&thinsp;cube-themed, naturally&thinsp;&mdash;&thinsp;the conversation turned to a MrBeast video in which competitors ranging from age 1 to 100 faced off in athletic challenges<a href="#fn1" class="fn-ref">1</a>. In the final round, a 28-year-old played basketball free throws against a 7-year-old. The child couldn't physically heave the ball high enough to reach the hoop. It was, everyone agreed, spectacularly unfair. I pointed out that organized basketball already solves this problem: different levels of play use different hoop heights, ball sizes, and ball weights. Youth leagues don't ask 6-year-olds to shoot a full-size ball at a 10-foot rim any more than little league asks 8-year-olds to hit off a major league mound.</p>

    <p>But I realized I wasn't totally sure about the details. Do women's professional leagues actually use a different ball than men's? Does the hoop height ever change, or just the ball? What about wheelchair basketball, deaf basketball, Special Olympics? The cube-themed party had planted the image in my head: three parameters, three axes, a cube of basketball configurations floating in space. So I asked Claude to look it all up.</p>

   

    <div class="essay-chart-container">
      <div class="chart-caption" style="margin-bottom:8px; margin-top:0;"><strong>Cube 1: Ball and hoop</strong></div>
      <div id="basketball-cube" style="width:100%; height:560px;"></div>
      <div class="chart-caption">Drag to rotate. Hover for details. Each point is one category of organized basketball.</div>
    </div>

    <div class="essay-data-table-wrapper">
    <table class="essay-data-table">
      <thead>
        <tr>
          <th>Category</th>
          <th>Ball Size</th>
          <th>Diameter</th>
          <th>Weight</th>
          <th>Hoop</th>
        </tr>
      </thead>
      <tbody>
        <tr><td class="cat-youth">Mini (Ages &le;4)</td><td>3</td><td>7.0&Prime;</td><td>10 oz</td><td>5.5 ft</td></tr>
        <tr><td class="cat-youth">Youth (Ages 5&ndash;6)</td><td>4</td><td>8.1&Prime;</td><td>14 oz</td><td>6.5 ft</td></tr>
        <tr><td class="cat-youth">Youth (Ages 7&ndash;8)</td><td>5</td><td>8.75&Prime;</td><td>17 oz</td><td>8.0 ft</td></tr>
        <tr><td class="cat-youth">Youth (Ages 9&ndash;11)</td><td>6</td><td>9.1&Prime;</td><td>20 oz</td><td>9.0 ft</td></tr>
        <tr><td class="cat-hs">Boys&rsquo; High School</td><td>7</td><td>9.4&Prime;</td><td>22 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-hs">Girls&rsquo; High School</td><td>6</td><td>9.1&Prime;</td><td>20 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-college">NCAA Men&rsquo;s</td><td>7</td><td>9.47&Prime;</td><td>22 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-college">NCAA Women&rsquo;s</td><td>6</td><td>9.15&Prime;</td><td>20 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-pro">NBA</td><td>7</td><td>9.47&Prime;</td><td>22 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-pro">WNBA</td><td>6</td><td>9.15&Prime;</td><td>20 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-3x3">FIBA 3&times;3</td><td>6*</td><td>9.15&Prime;</td><td>21 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-adaptive">Wheelchair (M)</td><td>7</td><td>9.47&Prime;</td><td>22 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-adaptive">Wheelchair (W)</td><td>6</td><td>9.15&Prime;</td><td>20 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-adaptive">Deaf (M)</td><td>7</td><td>9.47&Prime;</td><td>22 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-adaptive">Deaf (W)</td><td>6</td><td>9.15&Prime;</td><td>20 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-adaptive">Spec. Olympics (M)</td><td>7</td><td>9.47&Prime;</td><td>22 oz</td><td>10 ft</td></tr>
        <tr><td class="cat-adaptive">Spec. Olympics (Jr.)</td><td>6</td><td>9.15&Prime;</td><td>20 oz</td><td>8.0 ft</td></tr>
      </tbody>
    </table>
    </div>

    <p style="font-size:14px; color:#999; margin-top:-0.5em;">*FIBA 3&times;3 uses a Size 6 circumference with Size 7 weight&thinsp;&mdash;&thinsp;the only hybrid ball in organized basketball<a href="#fn2" class="fn-ref">2</a>.</p>

    <p>The ball is only part of the story. Three court parameters also vary across levels: court length, three-point line distance, and key (paint) width. Unlike the ball cube, these parameters don't collapse into two clusters&thinsp;&mdash;&thinsp;the NBA's court is longer than a high school's, its three-point line is four feet deeper, and its key is a third wider than what college players use. The WNBA sits between them: NBA-sized court and key, but FIBA's shorter three-point arc. Youth leagues below age 12 don't use a three-point line at all.</p>

    <div class="essay-chart-container">
      <div class="chart-caption" style="margin-bottom:8px; margin-top:0;"><strong>Cube 2: Court dimensions</strong></div>
      <div id="court-cube" style="width:100%; height:560px;"></div>
      <div class="chart-caption">Drag to rotate. Hover for details. Each point is one level of organized basketball.</div>
    </div>

    <div class="essay-data-table-wrapper">
    <table class="essay-data-table">
      <thead>
        <tr>
          <th>Category</th>
          <th>Court Length</th>
          <th>3-Point Line</th>
          <th>Key Width</th>
        </tr>
      </thead>
      <tbody>
        <tr><td class="cat-youth">Junior High</td><td>74 ft</td><td>19&prime; 9&Prime;</td><td>12 ft</td></tr>
        <tr><td class="cat-hs">High School</td><td>84 ft</td><td>19&prime; 9&Prime;</td><td>12 ft</td></tr>
        <tr><td class="cat-college">NCAA (M &amp; W)</td><td>94 ft</td><td>20&prime; 9&Prime;</td><td>12 ft</td></tr>
        <tr><td class="cat-pro">WNBA</td><td>94 ft</td><td>22&prime; 2&Prime;</td><td>16 ft</td></tr>
        <tr><td class="cat-pro">NBA</td><td>94 ft</td><td>23&prime; 9&Prime;</td><td>16 ft</td></tr>
        <tr><td class="cat-adaptive">FIBA / WC / Deaf / SO</td><td>92 ft</td><td>22&prime; 2&Prime;</td><td>16 ft</td></tr>
      </tbody>
    </table>
    </div>

    <p>So back to the MrBeast video. That 7-year-old appears to be playing with a regulation NBA ball on a 10-foot hoop, and that's not what any basketball organization on earth would give a 7-year-old. USA Basketball guidelines call for a Size 5 ball (27.5-inch circumference, about 17 ounces) and an 8-foot hoop for that age. The challenge wasn't just unfair because of the age gap&thinsp;&mdash;&thinsp;it was unfair because the equipment was wrong. The 7-year-old was handed a ball 30% heavier than an age-appropriate ball and asked to throw it two feet higher than an age-appropriate regulation hoop<a href="#fn3" class="fn-ref">3</a>.</p>

    <p>At the party I asked "where on the spectrum of basketball size between an 8 year old and adult men does every other demographic fit?", but I was simplifying too much - the better question was "what is the shape of the basketball parameter cube?"</p>
  </div>

  <div class="essay-footnotes">
    <h3>Notes</h3>

    <div class="essay-footnote" id="fn1">
      <span class="essay-footnote-num">1.</span>
      <a href="https://www.youtube.com/watch?v=9WEQts7b8Pw">Ages 1&ndash;100 Compete for $250,000</a>, MrBeast, YouTube.
    </div>

    <div class="essay-footnote" id="fn2">
      <span class="essay-footnote-num">2.</span>
      The reasoning behind the 3&times;3 hybrid ball is that the smaller circumference suits one-handed ball handling on the half-court, while the extra weight gives it a truer arc on longer shots. Whether this is real biomechanics or marketing, I leave to the reader.
    </div>

    <div class="essay-footnote" id="fn3">
      <span class="essay-footnote-num">3.</span>
      The sole exception: Special Olympics Junior Division allows an 8-foot rim, but this is a youth accommodation, not a disability-specific adaptation. Every other adaptive league&thinsp;&mdash;&thinsp;wheelchair, deaf, Special Olympics adult&thinsp;&mdash;&thinsp;uses the full 10-foot hoop. The International Wheelchair Basketball Federation explicitly maintains standard court dimensions to emphasize that wheelchair basketball <em>is</em> basketball.
    </div>
  </div>

  <div class="essay-back">
    <a href="/page/essays/">&larr; Back to Essays</a>
  </div>
</div>

<script>
(function() {
  var isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  var bgColor = isDark ? '#1a1a1a' : '#fff';
  var gridColor = isDark ? '#333' : '#e0e0e0';
  var fontColor = isDark ? '#ccc' : '#444';
  var axisLabelColor = isDark ? '#999' : '#666';
  var planeBg = isDark ? '#111' : '#f8f8f8';

  // Each entry = one unique point in the cube. Overlapping categories are merged.
  var points = [
    { legend: "Mini (Ages \u22644)",
      hoopHt: 5.5, diameter: 7.00, weight: 10,
      color: isDark ? "#93c5fd" : "#2563eb",
      cats: ["Mini (Ages \u22644)"] },
    { legend: "Youth (5\u20136)",
      hoopHt: 6.5, diameter: 8.12, weight: 14,
      color: isDark ? "#60a5fa" : "#3b82f6",
      cats: ["Youth (Ages 5\u20136)"] },
    { legend: "Youth (7\u20138)",
      hoopHt: 8.0, diameter: 8.75, weight: 17,
      color: isDark ? "#3b82f6" : "#1d4ed8",
      cats: ["Youth (Ages 7\u20138)"] },
    { legend: "Youth (9\u201311)",
      hoopHt: 9.0, diameter: 9.10, weight: 20,
      color: isDark ? "#2563eb" : "#1e40af",
      cats: ["Youth (Ages 9\u201311)"] },
    { legend: "Boys\u2019 HS",
      hoopHt: 10.0, diameter: 9.40, weight: 22,
      color: isDark ? "#4ade80" : "#16a34a",
      cats: ["Boys\u2019 High School"] },
    { legend: "Girls\u2019 HS",
      hoopHt: 10.0, diameter: 9.10, weight: 20,
      color: isDark ? "#86efac" : "#22c55e",
      cats: ["Girls\u2019 High School"] },
    { legend: "NBA, NCAA (M), WC (M), Deaf (M), SO (M)",
      hoopHt: 10.0, diameter: 9.47, weight: 22,
      color: isDark ? "#fb923c" : "#ea580c",
      cats: ["NBA", "NCAA Men\u2019s", "Wheelchair (M)", "Deaf (M)", "Spec. Olympics (M)"] },
    { legend: "WNBA, NCAA (W), WC (W), Deaf (W)",
      hoopHt: 10.0, diameter: 9.15, weight: 20,
      color: isDark ? "#c084fc" : "#7c3aed",
      cats: ["WNBA", "NCAA Women\u2019s", "Wheelchair (W)", "Deaf (W)"] },
    { legend: "FIBA 3\u00d73",
      hoopHt: 10.0, diameter: 9.15, weight: 21,
      color: isDark ? "#facc15" : "#ca8a04",
      cats: ["FIBA 3\u00d73 (hybrid ball)"] },
    { legend: "Spec. Olympics (Jr.)",
      hoopHt: 8.0, diameter: 9.15, weight: 20,
      color: isDark ? "#f472b6" : "#db2777",
      cats: ["Special Olympics Junior Division"] }
  ];

  var traces = points.map(function(p) {
    var hover = '<b>' + p.cats.join(', ') + '</b><br>' +
      'Ball Diameter: ' + p.diameter + '"<br>' +
      'Ball Weight: ' + p.weight + ' oz<br>' +
      'Hoop Height: ' + p.hoopHt + ' ft';
    return {
      x: [p.diameter], y: [p.weight], z: [p.hoopHt],
      text: [hover],
      hoverinfo: 'text',
      mode: 'markers',
      type: 'scatter3d',
      name: p.legend,
      marker: {
        size: 7,
        color: p.color,
        opacity: 0.92,
        line: { color: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.15)', width: 1 }
      }
    };
  });

  var layout = {
    showlegend: false,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: fontColor, family: "'Open Sans', system-ui, sans-serif", size: 12 },
    scene: {
      xaxis: {
        title: { text: 'Ball Diameter (in)', font: { size: 12, color: axisLabelColor } },
        range: [6.5, 10],
        gridcolor: gridColor,
        zerolinecolor: gridColor,
        backgroundcolor: planeBg
      },
      yaxis: {
        title: { text: 'Ball Weight (oz)', font: { size: 12, color: axisLabelColor } },
        range: [8, 24],
        gridcolor: gridColor,
        zerolinecolor: gridColor,
        backgroundcolor: planeBg
      },
      zaxis: {
        title: { text: 'Hoop Height (ft)', font: { size: 12, color: axisLabelColor } },
        range: [5, 11],
        gridcolor: gridColor,
        zerolinecolor: gridColor,
        backgroundcolor: planeBg
      },
      camera: { eye: { x: 1.9, y: 1.3, z: 0.8 } },
      aspectmode: 'cube'
    },
    legend: {
      x: 0.01, y: 0.99,
      bgcolor: 'rgba(0,0,0,0)',
      font: { size: 11 }
    },
    margin: { l: 0, r: 0, t: 10, b: 0 }
  };

  Plotly.newPlot('basketball-cube', traces, layout, {
    responsive: true,
    displayModeBar: false
  });

  // === Court Parameter Cube ===
  var courtPoints = [
    { legend: "Junior High",
      courtLen: 74, threePt: 19.75, keyW: 12,
      color: isDark ? "#93c5fd" : "#2563eb",
      cats: ["Junior High / Middle School"] },
    { legend: "High School",
      courtLen: 84, threePt: 19.75, keyW: 12,
      color: isDark ? "#4ade80" : "#16a34a",
      cats: ["High School (Boys & Girls)"] },
    { legend: "NCAA (M & W)",
      courtLen: 94, threePt: 20.75, keyW: 12,
      color: isDark ? "#c084fc" : "#7c3aed",
      cats: ["NCAA Men\u2019s", "NCAA Women\u2019s"] },
    { legend: "WNBA",
      courtLen: 94, threePt: 22.15, keyW: 16,
      color: isDark ? "#fb923c" : "#ea580c",
      cats: ["WNBA"] },
    { legend: "NBA",
      courtLen: 94, threePt: 23.75, keyW: 16,
      color: isDark ? "#f87171" : "#dc2626",
      cats: ["NBA"] },
    { legend: "FIBA, WC, Deaf, SO",
      courtLen: 92, threePt: 22.15, keyW: 16,
      color: isDark ? "#f472b6" : "#db2777",
      cats: ["FIBA 5v5", "Wheelchair", "Deaf", "Spec. Olympics"] }
  ];

  var courtTraces = courtPoints.map(function(p) {
    var hover = '<b>' + p.cats.join(', ') + '</b><br>' +
      'Court Length: ' + p.courtLen + ' ft<br>' +
      '3-Point Line: ' + p.threePt + ' ft<br>' +
      'Key Width: ' + p.keyW + ' ft';
    return {
      x: [p.courtLen], y: [p.threePt], z: [p.keyW],
      text: [hover],
      hoverinfo: 'text',
      mode: 'markers',
      type: 'scatter3d',
      name: p.legend,
      marker: {
        size: 7,
        color: p.color,
        opacity: 0.92,
        line: { color: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.15)', width: 1 }
      }
    };
  });

  var courtLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: fontColor, family: "'Open Sans', system-ui, sans-serif", size: 12 },
    scene: {
      xaxis: {
        title: { text: 'Court Length (ft)', font: { size: 12, color: axisLabelColor } },
        range: [70, 96],
        gridcolor: gridColor,
        zerolinecolor: gridColor,
        backgroundcolor: planeBg
      },
      yaxis: {
        title: { text: '3-Point Line (ft)', font: { size: 12, color: axisLabelColor } },
        range: [18, 25],
        gridcolor: gridColor,
        zerolinecolor: gridColor,
        backgroundcolor: planeBg
      },
      zaxis: {
        title: { text: 'Key Width (ft)', font: { size: 12, color: axisLabelColor } },
        range: [10, 18],
        gridcolor: gridColor,
        zerolinecolor: gridColor,
        backgroundcolor: planeBg
      },
      camera: { eye: { x: 1.9, y: 1.3, z: 0.8 } },
      aspectmode: 'cube'
    },
    legend: {
      x: 0.01, y: 0.99,
      bgcolor: 'rgba(0,0,0,0)',
      font: { size: 11 }
    },
    margin: { l: 0, r: 0, t: 10, b: 0 }
  };

  Plotly.newPlot('court-cube', courtTraces, courtLayout, {
    responsive: true,
    displayModeBar: false
  });
})();
</script>
{{< /rawhtml >}}
