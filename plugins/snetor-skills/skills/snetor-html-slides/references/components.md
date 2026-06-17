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

> ⚠️ **Layout pitfall**: placing `loss-item` elements inside a nested `display:grid` that is itself a flex or grid item can cause text to wrap word-by-word in some browsers (the inner `1fr` column collapses to 0px). Avoid nesting `loss-item` inside a second-level `display:grid` column. Use the `market-facts` pattern below instead when you have exactly 4 problems — it is bulletproof.

Use this pattern only when you have fewer than 4 items and the `loss-hero` drama panel is essential:

```html
<div style="display:flex; gap:22px; align-items:stretch; width:100%;">
  <article class="loss-hero animate d1" style="flex:0 0 42%;">
    <div>
      <span class="label">Cost / Risk</span>
      <strong>Bold problem headline</strong>
      <p>Explanation of why this is a problem.</p>
    </div>
    <div class="mini-note">Important nuance or caveat to keep honest.</div>
  </article>
  <div class="animate d2" style="flex:1; display:flex; flex-direction:column; gap:12px; min-width:0;">
    <div class="loss-item">
      <div></div>
      <div><strong>Problem name</strong><p style="margin:4px 0 0; font-size:16px; color:var(--muted);">Short explanation in a block-level p, not a span.</p></div>
    </div>
    <div class="loss-item">
      <div></div>
      <div><strong>Problem name</strong><p style="margin:4px 0 0; font-size:16px; color:var(--muted);">Short explanation.</p></div>
    </div>
    <div class="loss-item">
      <div></div>
      <div><strong>Problem name</strong><p style="margin:4px 0 0; font-size:16px; color:var(--muted);">Short explanation.</p></div>
    </div>
  </div>
</div>
```

**Rules for safe `loss-item` use:**
- Always use `<p>` (block element), never `<span>`, for the description text inside `.loss-item`
- The parent container must use `display:flex` (not `display:grid`) to avoid the `1fr` collapse bug
- Add `min-width:0` to the flex child that wraps the loss-items

## 4-Layer Problem / Debt Map (preferred alternative to loss-hero + loss-list)

When you have exactly 4 problems / debt layers / steps, prefer `market-facts` — it avoids all nested-grid layout bugs and renders correctly in all browsers:

```html
<div class="market-facts animate d2">
  <article class="fact-card">
    <i class="ph ph-broom ph-icon navy"></i>
    <h3>1 · Layer name</h3>
    <p>Short description. Keep under 25 words.</p>
  </article>
  <article class="fact-card">
    <i class="ph ph-link ph-icon teal"></i>
    <h3>2 · Layer name</h3>
    <p>Short description.</p>
  </article>
  <article class="fact-card">
    <i class="ph ph-robot ph-icon"></i>
    <h3>3 · Layer name</h3>
    <p>Short description.</p>
  </article>
  <article class="fact-card">
    <i class="ph ph-shield-check ph-icon navy"></i>
    <h3>4 · Layer name</h3>
    <p>Short description.</p>
  </article>
</div>
<div class="big-message animate d4">Key decision or call to action for the audience.</div>
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

## Tabs (interactive — alternative to splitting into 3 slides)

```html
<div class="tab-slide">
  <div class="tabs" role="tablist">
    <button class="tab active" data-tab="opt1" role="tab">Option A</button>
    <button class="tab" data-tab="opt2" role="tab">Option B</button>
    <button class="tab" data-tab="opt3" role="tab">Option C</button>
  </div>
  <div class="tab-panels">
    <div class="panel active" id="opt1" role="tabpanel">
      <!-- content for option A -->
    </div>
    <div class="panel" id="opt2" role="tabpanel">
      <!-- content for option B -->
    </div>
    <div class="panel" id="opt3" role="tabpanel">
      <!-- content for option C -->
    </div>
  </div>
</div>
```

Bootstrap script in `references/interactivity.md`.

---

## Accordion (details on demand)

```html
<div class="accordion">
  <div>
    <button class="acc-trigger" aria-expanded="false">Risk #1 — Vendor lock-in</button>
    <div class="acc-panel" hidden>Details about the risk and mitigations.</div>
  </div>
  <div>
    <button class="acc-trigger" aria-expanded="false">Risk #2 — Data residency</button>
    <div class="acc-panel" hidden>Details.</div>
  </div>
</div>
```

---

## Hover-reveal Card (punchline + reveal)

```html
<article class="card reveal animate d1">
  <span class="metric counter" data-target="88" data-suffix="%">0%</span>
  <h3>Visible label</h3>
  <p>Short visible context.</p>
  <div class="reveal-back">
    <h3>Detail on hover</h3>
    <p>Extended explanation visible only when hovered.</p>
  </div>
</article>
```

---

## Tooltips (technical terms / acronyms)

```html
<p>We use <span data-tooltip="Retrieval-Augmented Generation: combine a search index with an LLM to ground answers in your data.">RAG</span> for the knowledge base.</p>
```

Use sparingly — max 2-3 tooltips per slide. Bootstrap auto-adds `tabindex="0"` for keyboard accessibility.

---

## Marquee — infinite logo scroll (21st.dev)

For "ecosystem / partners / clients" slides with **6+ logos**. Pause on hover. Always duplicate the logo set twice in the markup.

See `references/external-libs.md` for the full pattern.

```html
<div class="marquee animate d1">
  <div class="marquee-track">
    <div class="marquee-logo" style="background-image:url('../assets/DECK/azure.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/aws.png');"></div>
    <!-- ... rest of logos ... then DUPLICATE ALL OF THEM AGAIN ... -->
  </div>
</div>
```

---

## Bento Grid — asymmetric value prop (21st.dev)

For "what we do / value proposition synthesis" slides. **Max 1 per deck.**

```html
<div class="bento animate d1">
  <article class="bento-cell big">
    <div class="eyebrow">Mission</div>
    <h3>Headline</h3>
    <p>Synthesis paragraph.</p>
  </article>
  <article class="bento-cell"><span class="metric">12</span><p>Label</p></article>
  <article class="bento-cell green"><h3>Title</h3><p>Note.</p></article>
  <article class="bento-cell tall"><h3>Title</h3><p>Note.</p></article>
  <article class="bento-cell dark"><span class="metric pastel">42%</span><p>Label.</p></article>
</div>
```

Cell modifiers: `.big` (col×2 row×2), `.tall` (row×2), `.wide` (col×2), `.green`, `.dark`.

---

## Spotlight Cards — mouse-following radial (21st.dev)

`.dark` slides only, max 1 row per deck.

```html
<div class="grid cols-3">
  <article class="spotlight-card animate d1">
    <h3>Pillar 1</h3>
    <p>Description.</p>
  </article>
  <article class="spotlight-card animate d2">
    <h3>Pillar 2</h3>
    <p>Description.</p>
  </article>
  <article class="spotlight-card animate d3">
    <h3>Pillar 3</h3>
    <p>Description.</p>
  </article>
</div>
```

Bootstrap script in `references/external-libs.md`.

---

## Phosphor Icon on Fact-card

```html
<article class="fact-card animate d1">
  <i class="ph ph-trophy ph-icon"></i>
  <span class="metric counter" data-target="42" data-suffix="%">0%</span>
  <h3>Croissance</h3>
  <p>Sur 12 mois.</p>
</article>
```

Add `<script src="https://unpkg.com/@phosphor-icons/web"></script>` to `<head>`. See `references/external-libs.md` for icon recommendations and weight variants.

---

## Speaker Notes (presenter mode)

Every slide may include a speaker notes aside, hidden by default and revealed via the `N` key in presenter mode:

```html
<section class="slide">
  <header class="brand"><!-- ... --></header>
  <div class="body"><!-- ... --></div>
  <aside class="notes">
    What the presenter should say here. Backstory, numbers, anecdote.
    Not visible to the audience unless they press N.
  </aside>
  <footer class="footer"><!-- ... --></footer>
</section>
```

Required for any slide whose body text exceeds 30 words.

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
