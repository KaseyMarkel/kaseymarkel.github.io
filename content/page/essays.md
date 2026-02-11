---
title: "Essays"
socialShare: false
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
  padding-top: 120px !important;
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

.essays-container {
  max-width: 760px;
  margin: 0 auto;
  padding: 0 20px;
}

.essays-header {
  text-align: center;
  margin-bottom: 60px;
}

.essays-header h1 {
  font-family: 'Lora', Georgia, serif;
  font-weight: 700;
  font-size: 42px;
  letter-spacing: -0.5px;
  color: #222;
  margin-bottom: 12px;
}

.essays-header .essays-subtitle {
  font-family: 'Lora', Georgia, serif;
  font-size: 18px;
  color: #888;
  font-style: italic;
  margin: 0;
}

.essays-divider {
  width: 60px;
  height: 2px;
  background: #ccc;
  margin: 30px auto 0;
}

/* Essay card */
.essay-card {
  display: block;
  text-decoration: none !important;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  padding: 36px 40px;
  margin-bottom: 28px;
  transition: all 0.25s ease;
  background: #fff;
  position: relative;
}

.essay-card:hover {
  border-color: #ccc;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
  text-decoration: none !important;
}

.essay-card:focus {
  text-decoration: none !important;
  outline: 2px solid #008AFF;
  outline-offset: 2px;
}

.essay-card-number {
  font-family: 'Open Sans', sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #bbb;
  margin-bottom: 12px;
}

.essay-card-title {
  font-family: 'Lora', Georgia, serif;
  font-size: 24px;
  font-weight: 700;
  color: #222;
  margin-bottom: 10px;
  line-height: 1.35;
}

.essay-card:hover .essay-card-title {
  color: #0085a1;
}

.essay-card-excerpt {
  font-family: 'Lora', Georgia, serif;
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.essay-card-meta {
  font-family: 'Open Sans', sans-serif;
  font-size: 12px;
  color: #aaa;
  letter-spacing: 0.5px;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  .essays-header h1 {
    color: #e8e8e8;
  }
  .essays-header .essays-subtitle {
    color: #777;
  }
  .essays-divider {
    background: #444;
  }
  .essay-card {
    background: #1a1a1a;
    border-color: #333;
  }
  .essay-card:hover {
    border-color: #555;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }
  .essay-card-number {
    color: #555;
  }
  .essay-card-title {
    color: #e0e0e0;
  }
  .essay-card:hover .essay-card-title {
    color: #50afff;
  }
  .essay-card-excerpt {
    color: #999;
  }
  .essay-card-meta {
    color: #666;
  }
}

@media (max-width: 768px) {
  .essays-header h1 {
    font-size: 32px;
  }
  .essay-card {
    padding: 24px 24px;
  }
  .essay-card-title {
    font-size: 20px;
  }
}
</style>

<div class="essays-container">
  <div class="essays-header">
    <h1>Essays</h1>
    <p class="essays-subtitle">Occasional writing on science, statistics, and thinking clearly</p>
    <div class="essays-divider"></div>
  </div>

  <a href="/page/essays/correlation-and-causation/" class="essay-card">
    <div class="essay-card-number">Essay 01</div>
    <div class="essay-card-title">Correlation Does in Fact Imply Causation</div>
    <div class="essay-card-excerpt">Perhaps the single most-quoted phrase about statistics is that 'correlation does not imply causation.' It's a phrase I've spoken hundreds of times. The thing is, our catchphrase is wrong.</div>
    <div class="essay-card-meta">Statistics &middot; Scientific Reasoning</div>
  </a>
</div>
{{< /rawhtml >}}
