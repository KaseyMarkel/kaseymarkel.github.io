---
title: "Anchor Builder"
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

.ab-intro {
  max-width: 820px;
  margin: 0 auto 18px;
  padding: 0 20px;
}
.ab-intro p { font-size: 0.98rem; line-height: 1.55; }

.ab-actions {
  max-width: 820px;
  margin: 0 auto 14px;
  padding: 0 20px;
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  align-items: center;
}
.ab-play {
  display: inline-block;
  padding: 10px 20px;
  background-color: #0085a1;
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
}
.ab-play:hover { background-color: #006d85; color: #fff; text-decoration: none; }
.ab-repo { color: #0085a1; text-decoration: none; font-size: 0.92rem; }

.ab-frame-wrap {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px 40px;
}
.ab-frame-wrap iframe {
  width: 100%;
  height: calc(100vh - 230px);
  min-height: 520px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #0e1320;
}

.ab-mobile-note { display: none; }

/* On phones the inline frame is a little cramped, so we suggest fullscreen — but
   the game still plays right here inline (rotate to landscape). */
@media (max-width: 768px) {
  .ab-actions { flex-direction: column; align-items: stretch; }
  .ab-play { text-align: center; font-size: 1.05rem; padding: 14px 20px; }
  .ab-frame-wrap { padding: 0 12px 30px; }
  .ab-frame-wrap iframe { height: calc(100vh - 200px); min-height: 420px; }
  .ab-mobile-note {
    display: block;
    max-width: 820px;
    margin: 2px auto 16px;
    padding: 0 20px;
    color: #777;
    font-size: 0.9rem;
  }
}
</style>

<div class="ab-intro">
  <p><strong>Anchor Builder</strong> is a trad climbing anchor-building simulator I built as a training tool. Procedurally generated crack systems run down a granite face; against a draining pump clock you pick gear off a real Black Diamond rack, position it over the crack, and place three pieces. To seat a cam you retract its lobes to fit — on desktop hold <strong>SPACE</strong>, on a phone rest your <strong>thumb</strong> below the cam and pull <strong>two fingers</strong> down toward it — just like pulling the trigger on the real thing. A fall test then decides whether your anchor holds. It plays best fullscreen (on a phone, in landscape), but you can play it right here too.</p>
</div>

<div class="ab-actions">
  <a class="ab-play" href="/anchor-builder/" target="_blank" rel="noopener">▶ Play fullscreen</a>
  <a class="ab-repo" href="https://github.com/KaseyMarkel/Anchor-builder" target="_blank" rel="noopener">Source on GitHub ↗</a>
</div>
<p class="ab-mobile-note">Or just play below — rotate your phone to landscape. Fullscreen is roomier, but optional.</p>

<div class="ab-frame-wrap">
  <iframe src="/anchor-builder/" title="Anchor Builder game" loading="lazy"></iframe>
</div>
{{< /rawhtml >}}
