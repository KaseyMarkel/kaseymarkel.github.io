---
title: "Paraglide Go"
socialShare: false
---

{{< rawhtml >}}
<style>
.intro-header { display: none !important; }
.header-section.has-img { display: none !important; }
footer { display: none !important; }

div[role="main"].container {
  padding: 64px 0 0 0 !important;   /* clear the fixed nav; map fills the rest */
  margin: 0 !important;
  max-width: 100% !important;
}
div[role="main"].container .row { margin: 0 !important; }
div[role="main"].container .row > div[class*="col-"] {
  width: 100% !important; max-width: 100% !important; flex: 0 0 100% !important;
  margin: 0 !important; padding: 0 !important;   /* kill Bootstrap col width + offset */
}
div[role="main"].container .blog-post { width: 100% !important; }

.ct-frame-wrap { position: relative; margin: 0; padding: 0; line-height: 0; }
.ct-frame-wrap iframe {
  display: block; width: 100%; height: calc(100vh - 64px); min-height: 460px;
  border: 0; background: #eef1f3;
}
.ct-open {
  position: absolute; top: 12px; right: 16px; z-index: 5;
  font-size: 0.8rem; font-weight: 600; text-decoration: none;
  background: rgba(255,255,255,0.92); color: #0085a1;
  padding: 7px 13px; border-radius: 8px; box-shadow: 0 1px 8px rgba(0,0,0,0.15);
}
.ct-open:hover { background: #0085a1; color: #fff; text-decoration: none; }
</style>

<div class="ct-frame-wrap">
  <a class="ct-open" href="/flights/" target="_blank" rel="noopener">Open in full window ↗</a>
  <iframe src="/flights/" title="Paraglide Go — flight map" loading="lazy"></iframe>
</div>
{{< /rawhtml >}}
