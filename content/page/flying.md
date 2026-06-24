---
title: "Captured Territory"
socialShare: false
---

{{< rawhtml >}}
<style>
.intro-header { display: none !important; }
.header-section.has-img { display: none !important; }

div[role="main"].container {
  padding-top: 90px !important;
  margin-top: 0 !important;
  max-width: 100% !important;
}

.ct-intro { max-width: 820px; margin: 0 auto 16px; padding: 0 20px; }
.ct-intro p { font-size: 0.98rem; line-height: 1.55; }

.ct-actions {
  max-width: 820px; margin: 0 auto 14px; padding: 0 20px;
  display: flex; gap: 14px; flex-wrap: wrap; align-items: center;
}
.ct-play {
  display: inline-block; padding: 10px 20px; background-color: #0085a1;
  color: #fff; border-radius: 8px; text-decoration: none; font-weight: 600;
}
.ct-play:hover { background-color: #006d85; color: #fff; text-decoration: none; }

.ct-frame-wrap { max-width: 1200px; margin: 0 auto; padding: 0 20px 40px; }
.ct-frame-wrap iframe {
  width: 100%; height: calc(100vh - 210px); min-height: 560px;
  border: 1px solid #ddd; border-radius: 10px; background: #eef1f3;
}

@media (max-width: 768px) {
  .ct-frame-wrap { padding: 0 12px 30px; }
  .ct-frame-wrap iframe { height: calc(100vh - 170px); min-height: 460px; }
}
</style>

<div class="ct-intro">
  <p><strong>Captured Territory</strong> maps every paragliding flight I&rsquo;ve logged and
  asks a playful question: how much of the planet have I drawn a closed loop around? Like
  capturing ground in a strategy game, every thermal I circle fences off a little disc, and
  whenever separate cross&#8209;country flights cross to enclose a triangle or polygon, that
  land counts too. Each flight is drawn in its own colour, chosen so neighbouring flights
  stay distinct &mdash; so you can see when it took <em>several</em> flights, together, to
  surround a patch of ground. Hover a track for its stats; drop in your own
  <code>.igc</code> files to add them to the map.</p>
</div>

<div class="ct-actions">
  <a class="ct-play" href="/flights/" target="_blank" rel="noopener">⛰ Open fullscreen</a>
</div>

<div class="ct-frame-wrap">
  <iframe src="/flights/" title="Captured Territory — flight map" loading="lazy"></iframe>
</div>
{{< /rawhtml >}}
