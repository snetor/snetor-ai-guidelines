# Snetor HTML Slides — Component Catalog

HTML patterns for every reusable component. Copy and adapt to content.
All examples assume `class="slide active"` context.

---

## Slide Shell (always the same)

```html
<section class="slide [cover|dark|]">
  <header class="brand animate">
    <div class="logo" aria-label="Snetor"></div>
    <div class="eyebrow">Section label</div>
  </header>

  <div class="body">
    <!-- CONTENT HERE -->
  </div>

  <footer class="footer">
    <div class="sources src">Sources: ...</div>
    <div class="progress" aria-hidden="true"></div>
  </footer>
</section>
```

Slide classes:
- *(none)* — white background with subtle left green gradient
- `cover` — dark hero background (use for slide 1 only)
- `dark` — dark navy→teal→green gradient (for emphasis slides)

---

## Cover Slide (slide 1)

```html
<section class="slide cover active">
  <header class="brand animate">
    <div class="logo" aria-label="Snetor"></div>
    <div>COMEX Snetor — 6 mai 2026</div>
  </header>
  <div class="body">
    <div class="animate d1">
      <div class="eyebrow">Section / Topic</div>
      <h1>Main headline of the presentation in 10 words max.</h1>
      <p class="lead">One or two sentences of context for the audience. Who needs to know what, and why now.</p>
      <div class="hero-line"></div>
    </div>
  </div>
  <div class="globe" aria-hidden="true"></div>
  <footer class="footer">
    <div>Version — deck HTML animé.</div>
    <div class="progress" aria-hidden="true"></div>
  </footer>
</section>
```

---

## Standard Slide with Heading + Statement

```html
<section class="slide">
  <header class="brand animate">
    <div class="logo" aria-label="Snetor"></div>
    <div class="eyebrow">Topic label</div>
  </header>
  <div class="body">
    <h2 class="animate d1">Slide headline — the one thing the audience must remember.</h2>
    <p class="animate d2 statement">Supporting assertion. <strong>Key phrase highlighted.</strong></p>
    <!-- main content below -->
  </div>
  <footer class="footer">
    <div class="sources">Sources: ...</div>
    <div class="progress" aria-hidden="true"></div>
  </footer>
</section>
```

---

## Stat / Metric Cards (2, 3, or 4 columns)

```html
<div class="grid cols-4">
  <article class="card animate d1">
    <span class="metric">88%</span>
    <h3>Short label</h3>
    <p>One sentence of context.</p>
  </article>
  <article class="card animate d2">
    <a class="metric" href="https://source.url" target="_blank" rel="noreferrer">~1/3</a>
    <h3>Label with source link</h3>
    <p>Context sentence.</p>
  </article>
  <!-- repeat for d3, d4 -->
</div>
```

Use `a.metric` when the stat comes from a citable external source. Link to the source.

---

## Fact Cards Row (4-col, market data style)

```html
<div class="market-facts">
  <article class="fact-card animate d1">
    <a class="metric" href="URL" target="_blank" rel="noreferrer">95%</a>
    <h3>Short finding</h3>
    <p>Short explanation.</p>
  </article>
  <!-- d2, d3, d4 -->
</div>
```

---

## 2-Column Layout (left text + right visual)

```html
<div style="display:grid; grid-template-columns:1.1fr .9fr; gap:24px; align-items:stretch;">
  <div class="animate d1">
    <!-- text content, cards, lists -->
  </div>
  <div class="animate d2">
    <!-- chart, visual panel, check grid -->
  </div>
</div>
```

---

## Loss / Problem Hero (left big panel + right problem list)

```html
<div style="display:grid; grid-template-columns:.9fr 1.1fr; gap:22px; align-items:stretch;">
  <article class="loss-hero animate d1">
    <div>
      <span class="label">Cost / Risk</span>
      <strong>Bold problem headline</strong>
      <p>Explanation of why this is a problem.</p>
    </div>
    <div class="mini-note">Important nuance or caveat to keep honest.</div>
  </article>
  <div class="animate d2" style="display:grid; gap:12px;">
    <div class="loss-item"><div><strong>Problem name</strong><span>Short explanation.</span></div></div>
    <div class="loss-item"><div><strong>Problem name</strong><span>Short explanation.</span></div></div>
    <div class="loss-item"><div><strong>Problem name</strong><span>Short explanation.</span></div></div>
    <div class="loss-item"><div><strong>Problem name</strong><span>Short explanation.</span></div></div>
    <div class="big-message animate d4">Key decision or call to action for the audience.</div>
  </div>
</div>
```

---

## Check Card Grid (interactive validation slide)

```html
<div class="check-grid">
  <button type="button" class="check-card checked" aria-pressed="true">
    <span class="box"></span>
    <span>
      <span class="suggestion">Déjà fait</span>
      <strong>Item label</strong>
      <span>Short description of what this covers.</span>
    </span>
  </button>
  <button type="button" class="check-card" aria-pressed="false">
    <span class="box"></span>
    <span>
      <span class="suggestion">À valider</span>
      <strong>Item label</strong>
      <span>Short description.</span>
    </span>
  </button>
</div>
```

Pre-checked items get `class="check-card checked"` and `aria-pressed="true"`. Use `suggestion` spans with labels like "Déjà fait", "À valider", "À borner", "Suggestion".

---

## Timeline (4 phases)

```html
<div class="timeline">
  <div class="phase"><strong>S1</strong><span>Week 1 focus</span></div>
  <div class="phase"><strong>S2</strong><span>Week 2 focus</span></div>
  <div class="phase"><strong>S3</strong><span>Week 3 focus</span></div>
  <div class="phase"><strong>S4</strong><span>Week 4 focus</span></div>
</div>
```

---

## Roadmap Path (4-step with animated connector)

```html
<div class="path">
  <article class="step animate d1">
    <div class="dot"></div>
    <h3>Step 1</h3>
    <p>What happens here.</p>
  </article>
  <article class="step animate d2">
    <div class="dot"></div>
    <h3>Step 2</h3>
    <p>What happens here.</p>
  </article>
  <article class="step animate d3">
    <div class="dot"></div>
    <h3>Step 3</h3>
    <p>What happens here.</p>
  </article>
  <article class="step animate d4">
    <div class="dot"></div>
    <h3>Step 4</h3>
    <p>What happens here.</p>
  </article>
</div>
```

---

## Provider / Technology Comparison Cards

```html
<div class="provider-grid">
  <article class="provider-card featured">
    <div>
      <!-- Logo approach 1: inline CSS background -->
      <div class="asset-logo" style="background-image:url('../assets/DECK/azure.png'); width:92px; height:48px;"></div>
    </div>
    <div class="provider-tag">Recommandé</div>
    <p>Why this provider fits the context.</p>
    <ul>
      <li>Key advantage</li>
      <li>Key advantage</li>
    </ul>
  </article>
  <article class="provider-card">
    <!-- other provider -->
  </article>
</div>
```

---

## Brick Wall (3-col feature list, alternating navy/green)

```html
<div class="brick-wall">
  <div class="brick animate d1"><strong>Feature A</strong><span>Short description.</span></div>
  <div class="brick animate d2"><strong>Feature B</strong><span>Short description.</span></div>
  <div class="brick animate d3"><strong>Feature C</strong><span>Short description.</span></div>
  <div class="brick animate d4"><strong>Feature D</strong><span>Short description.</span></div>
  <div class="brick animate d1"><strong>Feature E</strong><span>Short description.</span></div>
  <div class="brick animate d2"><strong>Feature F</strong><span>Short description.</span></div>
</div>
```

---

## Readiness Rail (horizontal progress bar with stages)

```html
<div class="readiness-rail">
  <span>POC</span>
  <span>Données</span>
  <span class="on">Landing zone</span>
  <span>Run</span>
  <span>Scale</span>
</div>
```

Active step gets `class="on"`.

---

## Dynamic Chart Card (Chart.js)

For any non-trivial chart (multi-series bar, donut, line trend, radar, area), use the `chart-card` component documented in `references/charts.md`.

```html
<article class="chart-card animate d1">
  <div class="eyebrow">Cloud Market 2025</div>
  <h3>Part de marché</h3>
  <div class="chart-wrap">
    <canvas
      data-chart="donut"
      data-labels='["Azure","AWS","GCP","Other"]'
      data-values='[24,31,11,34]'
      data-suffix="%"
    ></canvas>
  </div>
  <p class="source-note">Source: <a href="URL">Gartner 2025</a></p>
</article>
```

Static one-row CSS charts (`.stacked`, `.impact-bars`) remain available for simple cases. See `references/charts.md` for the full bootstrap script and chart type guide.

---

## World Map (jsvectormap)

For implantations / coverage slides:

```html
<div class="world-map" data-points='[
  {"name":"HQ Lyon","coords":[45.74,4.84]},
  {"name":"Madrid","coords":[40.42,-3.70]}
]'></div>
```

See `references/charts.md` for the bootstrap script and styling.

---

## Animated Counter Metric

```html
<span class="metric counter" data-target="88" data-suffix="%" data-duration="1200">0%</span>
```

Counts up from 0 to `data-target` when the slide becomes active. See `references/charts.md` for the bootstrap and the hook into `show()`.

---

## Stacked Bar Chart (cloud market share style)

```html
<div class="stacked">
  <div class="segment aws">Azure 45%</div>
  <div class="segment ms">SAP 22%</div>
  <div class="segment google">Google 15%</div>
  <div class="segment other">Autres 18%</div>
</div>
<div class="legend" style="margin-top:16px;">
  <div class="legend-item"><span class="swatch aws"></span>Label for first segment</div>
  <div class="legend-item"><span class="swatch other"></span>Label for last segment</div>
</div>
```

Adjust segment widths with inline `style="width:X%"` if the percentages differ from the CSS defaults.

---

## Mini Table (2-col key-value)

```html
<div class="mini-table">
  <div>Label</div><div>Value or description</div>
  <div>Label</div><div>Value or description</div>
  <div>Label</div><div>Value or description</div>
  <div>Label</div><div>Value or description</div>
</div>
```

Odd children (1st, 3rd...) get the navy/green-05 style automatically.

---

## Big Message Band

```html
<div class="big-message animate d4">
  The single most important thing the audience should remember from this slide.
</div>
```

---

## Pills Row

```html
<div class="pill-row">
  <span class="pill">Tag A</span>
  <span class="pill">Tag B</span>
  <span class="pill">Tag C</span>
</div>
```

---

## Logo Usage in Slides

Assets bundled with the skill live in `skills/snetor-html-slides/assets/`.
When generating a deck, copy needed assets into `03-Outputs/assets/<deck-name>/` relative to the vault.

**Available logos** (in `assets/logos/`):
`azure.png`, `microsoft.png`, `microsoft_fabric.png`, `gcp.png`, `google.png`, `aws.png`, `amazon.png`,
`anthropic.png`, `claude.png`, `openai.png`, `powerbi.png`, `sharepoint.png`, `copilot.png`,
`copilot-studio.png`, `copilot-cowork.png`, `power-automate.png`, `vertex-ai.png`,
`azure-ai-foundry.png`, `amazon-bedrock.png`, `sap.png`, `sap-b1.png`, `sap-concur.png`,
`s4-hana.png`, `opentext.png`, `kantox.png`, `xeneta.png`, `buyco.png`, `datasur.png`, `alpega-tms.png`

**Branding assets** (in `assets/branding/`):
`snetor_full_logo.png`, `snetor_full_logo_reversed.png`, `snetor_globe.png`, `snetor_colors.png`, `snetor_shapes.png`, `Hero-banner-abstrait.jpg`

Reference logos inline:
```html
<div class="asset-logo" style="background-image:url('../assets/DECK_NAME/azure.png');"></div>
```

Or as CSS variable if used on many slides:
```css
--azure-logo: url("../assets/DECK_NAME/azure.png");
```
```html
<div class="asset-logo azure"></div>  <!-- requires .asset-logo.azure { background-image: var(--azure-logo); } -->
```
