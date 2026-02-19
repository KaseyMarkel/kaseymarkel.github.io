---
title: "The Vibe Card"
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
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.essay-page-subtitle {
  font-family: 'Lora', Georgia, serif;
  font-size: 18px;
  font-style: italic;
  color: #888;
  margin-bottom: 16px;
}

.essay-page-meta {
  font-family: 'Open Sans', sans-serif;
  font-size: 13px;
  color: #999;
  letter-spacing: 0.3px;
}

/* Vibe Card image */
.essay-vibe-card-img {
  display: block;
  max-width: 480px;
  width: 100%;
  margin: 0 auto 40px;
  border-radius: 12px;
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

/* Section headings */
.essay-body h2 {
  font-family: 'Lora', Georgia, serif;
  font-size: 28px;
  font-weight: 700;
  color: #222;
  margin-top: 2.2em;
  margin-bottom: 0.8em;
  letter-spacing: -0.3px;
}

/* Lists */
.essay-body ul {
  margin-bottom: 1.6em;
  padding-left: 1.5em;
}

.essay-body ul li {
  margin-bottom: 0.5em;
}

/* Ordered lists */
.essay-body ol {
  margin-bottom: 1.6em;
  padding-left: 1.5em;
}

.essay-body ol li {
  margin-bottom: 0.5em;
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
  .essay-page-subtitle {
    color: #777;
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
  .essay-body h2 {
    color: #e8e8e8;
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
  .essay-body h2 {
    font-size: 24px;
  }
}
</style>

<div class="essay-page">
  <div class="essay-page-header">
    <div class="essay-page-label"><a href="/page/essays/">Essays</a> &middot; 03</div>
    <h1 class="essay-page-title">The Vibe Card</h1>
    <div class="essay-page-subtitle">A Transparency Standard for the AI Era</div>
    <div class="essay-page-meta">AI &middot; Transparency &middot; Standards &middot; February 2026</div>
  </div>

  <img class="essay-vibe-card-img" src="/img/vibe_card_the_vibe_card.png" alt="Vibe Card for this essay" />

  <div class="essay-body">
    <p class="essay-first-paragraph">It's very useful to know which mind is responsible for the content of an essay, a report, a codebase, or any intellectual work product. This is why we have authorship in the first place. It's why the scientific community developed the <a href="https://credit.niso.org/">CRediT (Contributor Roles Taxonomy)</a> system&thinsp;&mdash;&thinsp;so that when someone finds fraud in the data analysis of a multi-author paper, you can look at who was actually responsible for the data analysis, rather than blaming the person who only designed the experiments.</p>

    <p>For the first time in history, there's a new category of mind available. It's being used, to one degree or another, in a substantial minority of intellectual output&thinsp;&mdash;&thinsp;and almost certainly, in the near future, the majority. Now is the time to be developing standards, because there are genuinely new things happening that our existing attribution systems weren't designed for.</p>

    <p>I'm proposing a simple one. I'm calling it the Vibe Card.</p>

    <h2>What It Is</h2>

    <p>The Vibe Card is a small visual element that sits at the top of an essay, report, or work product&thinsp;&mdash;&thinsp;right under the title, like the epistemic status remarks that rationalist bloggers often include. It contains a set of sliders, each representing a different dimension of contribution, ranging from "Fully Human" on the left to "Fully AI" on the right.</p>

    <p>The dimensions are inspired by the <a href="https://credit.niso.org/">CRediT taxonomy</a> used for scientific authorship, adapted for the kinds of intellectual work people actually produce with LLMs:</p>

    <ul>
      <li><strong>Ideation</strong>&thinsp;&mdash;&thinsp;Who came up with the core ideas and questions?</li>
      <li><strong>Research &amp; Analysis</strong>&thinsp;&mdash;&thinsp;Who gathered data, ran analyses, found sources?</li>
      <li><strong>Drafting</strong>&thinsp;&mdash;&thinsp;Who wrote the text?</li>
      <li><strong>Code</strong>&thinsp;&mdash;&thinsp;Who wrote any code involved in the project? (Include only if applicable.)</li>
      <li><strong>Editing &amp; Refinement</strong>&thinsp;&mdash;&thinsp;Who reviewed and improved the work?</li>
      <li><strong>Final Review</strong>&thinsp;&mdash;&thinsp;How thoroughly did a human review the final product?</li>
    </ul>

    <p>At the bottom of the card, you note the specific AI model and version used&thinsp;&mdash;&thinsp;not just "Claude" but "Claude Opus 4.6" or "GPT-4o" or whatever was actually in the loop. Model capabilities vary enormously, and a Vibe Card from 2024 using GPT-3.5 means something very different from one using a 2026 frontier model.</p>

    <p>A quick cautionary note on this: AI models are bad at self-identification. The model that built this very essay (Claude Opus 4.6) initially labeled itself as Opus 4.5 when generating the Vibe Card component. If you're asking an AI to help generate your Vibe Card, you should explicitly prompt it to state its exact model name and version, then verify it yourself. The interactive tool includes a prompt template for this&thinsp;&mdash;&thinsp;because if the whole point of the standard is transparency, getting the model name wrong kind of defeats the purpose.</p>

    <h2>Why It Matters</h2>

    <p>The first reason is simple honesty. If a colleague sends you a report, it's useful to know whether they spent forty hours writing it or whether they spent twenty minutes talking into their phone on a walk and had Claude build a first draft. The information content is different. The appropriate level of trust is different. The kind of feedback that's useful is different.</p>

    <p>The second is accountability. The <a href="https://credit.niso.org/">CRediT taxonomy</a> became valuable in science partly because it clarifies responsibility. If fraud is discovered, you can trace it to the people who actually handled that part of the work. AI can't take responsibility&thinsp;&mdash;&thinsp;not yet, at any rate. But a Vibe Card that shows "Analysis: 90% AI" tells you that if there are errors in the analysis, a human didn't carefully check every step. That's important information.</p>

    <p>Related: consider the "Final Review" slider. If someone sends you an essay where Drafting is 90% AI and Final Review is also way over on the AI side, that's telling you something important&thinsp;&mdash;&thinsp;probably that the human barely read their own work product before shipping it. That's useful context for deciding how much weight to give it.</p>

    <p>The third is just that it's the right thing to do for the intellectual community. We're in a transition period where norms around AI use are still forming. Being transparent about it&thinsp;&mdash;&thinsp;ahead of any requirement to be&thinsp;&mdash;&thinsp;builds trust and sets a good precedent.</p>

    <p>And the fourth, honestly, is that it's kind of fun. There's something satisfying about being explicit about your process.</p>

    <h2>How It Works in Practice</h2>

    <p>The Vibe Card is interactive. The workflow goes like this:</p>

    <ol>
      <li>You ask your AI to propose initial slider values for each dimension, based on the work it actually did.</li>
      <li>The AI generates a card with its proposed values.</li>
      <li>You drag the sliders to where you think they should actually be.</li>
      <li>You hit "Save as PNG" and get a transparent-background image to embed at the top of your essay or report.</li>
    </ol>

    <p>An optional feature: the card can display both the AI's proposed values and the human's final values as two separate dots on each slider&thinsp;&mdash;&thinsp;the AI's proposal as a faded amber dot, the human's final call as a solid green one. The gap between them is itself interesting data. It tells you something about how the human and AI perceive their relative contributions, and whether the human thought the AI was overclaiming or underclaiming its role.</p>

    <p>For this essay, for example, Claude proposed that Drafting was about 80% AI. Looking at it, I'd say that's roughly right&thinsp;&mdash;&thinsp;the ideas and structure came from me talking on a walk, but the actual prose is mostly Claude's. I might nudge the "Editing" slider a bit, but the overall picture is honest. The final card is mine to approve.</p>

    <h2>The Code</h2>

    <p>The Vibe Card is designed to be a reusable, open standard. The code for generating these cards&thinsp;&mdash;&thinsp;including the interactive slider component, the dual-dot AI/human comparison, and the PNG export&thinsp;&mdash;&thinsp;is <a href="https://github.com/KaseyMarkel/vibe-card">publicly available on my GitHub</a>. Anyone who wants to adopt the standard can grab the code, drop it into their own site, and generate Vibe Cards for their own work. The whole process takes about thirty seconds.</p>

    <h2>Adopt It</h2>

    <p>You don't have to use my exact categories. You don't have to use my exact visual design. But I'd encourage anyone publishing intellectual work that involves AI to put <em>something</em> at the top that says how much of this was you and how much was the machine. The norms we set now will matter as AI contribution becomes the default rather than the exception.</p>

    <p>Ultimately, any human who signs their name at the top of a work product is taking responsibility for everything in it. That hasn't changed. But a Vibe Card helps your readers&thinsp;&mdash;&thinsp;and your future self&thinsp;&mdash;&thinsp;understand how that responsibility was distributed in practice.</p>
  </div>

  <div class="essay-back">
    <a href="/page/essays/">&larr; Back to Essays</a>
  </div>
</div>
{{< /rawhtml >}}
