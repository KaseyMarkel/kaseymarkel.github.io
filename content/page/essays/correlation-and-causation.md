---
title: "Correlation Does in Fact Imply Causation"
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

<div class="essay-page">
  <div class="essay-page-header">
    <div class="essay-page-label"><a href="/page/essays/">Essays</a> &middot; 01</div>
    <h1 class="essay-page-title">Correlation Does in Fact Imply Causation</h1>
    <div class="essay-page-meta">Statistics &middot; Scientific Reasoning</div>
  </div>

  <img class="essay-vibe-card-img" src="/img/vibe_card_correlation_causation.png" alt="Vibe Card for this essay" />

  <div class="essay-body">
    <p class="essay-first-paragraph">Perhaps the <a href="https://en.wikipedia.org/wiki/Correlation_does_not_imply_causation">single</a> <a href="https://towardsdatascience.com/4-reasons-why-correlation-does-not-imply-causation-f202f69fe979/">most</a>-<a href="https://www.statology.org/correlation-does-not-imply-causation-examples/">quoted</a> <a href="https://www.mathtutordvd.com/public/Why-Correlation-does-not-Imply-Causation-in-Statistics.cfm">phrase</a> <a href="https://www.geeksforgeeks.org/machine-learning/reasons-why-correlation-does-not-imply-causation/">about</a> <a href="https://xkcd.com/552/">statistics</a><a href="#fn1" class="fn-ref">1</a> is that 'correlation does not imply causation.' It's a phrase I've spoken hundreds of times, even after the ideas that resulted in this essay were broadly developed. It's often a useful educational tool for beginner-level students, and it's convenient as a shorthand description of a failure of scientific reasoning that's disturbingly common: just because A correlates with B, it doesn't mean that A causes B. The classic example is that ice cream sales correlate with violent crime rates, but that doesn't mean ice cream fuels crime&thinsp;&mdash;&thinsp;and of course this is true, and anyone still making base-level errors is well-served by that catchphrase 'correlation does not imply causation'.</p>

    <p>The thing is, our catchphrase is wrong&thinsp;&mdash;&thinsp;correlation does in fact imply<a href="#fn2" class="fn-ref">2</a> causation. More precisely, if things are correlated, there exists a relatively short causal chain linking those things, with confidence one minus the p-value of the correlation. Far too many smart people think the catchphrase is literally true, and end up dismissing correlation as uninteresting. It's of course <em>possible</em> for things to be correlated by chance, in the same way that it's <em>possible</em> to flip a coin and get 10 heads in a row<a href="#fn3" class="fn-ref">3</a>, but as sample size increases this becomes less and less likely, that's the whole point of calculating the p-value when testing for correlation. In other words, there are only two explanations for a correlation: coincidence or causation.</p>

    <p>Let's return to the ice cream example. It doesn't take long to guess what's really going on here: warm weather causes both the increased occupancy of public space and irritability that leads to spikes in violent crime and to a craving for a cold treat. So no, ice cream does not cause violent crime. But they are causally linked, through a quite short causal pathway. There are three possible architectures for the pathway: A causes B, B causes A, and C causes both, either directly or indirectly<a href="#fn4" class="fn-ref">4</a>.</p>

    <p>I would hate to push anyone back to the truly naive position that A correlating with B means A causes B, but let's not say false things: correlation does in fact imply causation<a href="#fn5" class="fn-ref">5</a>, just doesn't show you which direction that causation flows.</p>

    <p>Why do I care about correcting this phrase? Two reasons&thinsp;&mdash;&thinsp;it is bad as a community to have catchphrases that are factually false, and "correlation does not imply causation" can and has been used for dark arts before. Rather famously, Ronald Fisher spent decades arguing that there was insufficient evidence to conclude that smoking causes lung cancer - because correlation does not imply causation. The tobacco industry was grateful. Meanwhile, the correlation was telling us exactly what we should have been doing: not dismissing it, but designing experiments to determine which of the three causal architectures explained it. The answer, of course, was the obvious one. Correlation was trying to tell us something, and we spent decades pretending it wasn't allowed to.</p>
  </div>

  <div class="essay-footnotes">
    <h3>Notes</h3>

    <div class="essay-footnote" id="fn1">
      <span class="essay-footnote-num">1.</span>
      This one strikes closest to my heart as a longtime XKCD fan. Randall is almost gesturing at the point I make in this essay, but not quite. At the risk of thinking too hard about a joke (surely not a sin for this particular comic), the key flaw here is the tiny sample size&thinsp;&mdash;&thinsp;this isn't even correlation, the p-value is 0.5. If 1,000 people take a statistics class and we survey them before and after, then we could get a meaningful, statistically-robust correlation here&thinsp;&mdash;&thinsp;and unfortunately it would probably be the case that taking the class makes people more likely to believe this phrase.
    </div>

    <div class="essay-footnote" id="fn2">
      <span class="essay-footnote-num">2.</span>
      I'm using 'imply' in an empirical rather than logical sense&thinsp;&mdash;&thinsp;it's not that correlation <em>proves</em> causation the way a mathematical proof does, but that it provides evidence for causation, with strength proportional to sample size.
    </div>

    <div class="essay-footnote" id="fn3">
      <span class="essay-footnote-num">3.</span>
      p=0.00195, being generous and taking the two-tailed value.
    </div>

    <div class="essay-footnote" id="fn4">
      <span class="essay-footnote-num">4.</span>
      That "indirectly" is pointing at a fourth option, actually an infinite set of options: C causes A and D which causes B, C causes A and E which causes D which causes B, etc. I'm not including these because it's natural to consider those as variants on C causes both. As an analogy: if one pushes over the first domino, did that cause the last domino to fall? A pedant might argue the actual cause of the last domino falling was the penultimate domino falling on it, and in some cases that precision can be useful, but most of the time it's natural to just say the person who pushed the first domino caused the last one to fall over. In practice the causal chain is probably pretty short, because interesting correlations tend to be well below one, and after a few intermediates the correlation strength drops below the noise threshold of detection.
    </div>

    <div class="essay-footnote" id="fn5">
      <span class="essay-footnote-num">5.</span>
      With the evidentiary strength you would expect based on the p-value of the correlation. Coincidence is always a possibility, but becomes pretty unlikely for correlations with a large sample size.
    </div>
  </div>

  <div class="essay-back">
    <a href="/page/essays/">&larr; Back to Essays</a>
  </div>
</div>
{{< /rawhtml >}}
