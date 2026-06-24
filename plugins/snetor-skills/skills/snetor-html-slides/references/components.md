# Snetor HTML Slides — Component Catalog

HTML patterns for every reusable component. Copy and adapt to content.
All examples assume `class="slide active"` context.

---

## Slide Shell (always the same)

```html
<section class="slide [cover|dark|light|section-divider|quote|agenda|big-number|closing|]">
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
- `light` — light accent slide inside a `theme-dark` deck (symmetric of `dark`)
- archetype classes (`section-divider`, `quote`, `agenda`, `big-number`, `closing`) — see "Slide Archetypes"

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

## Method Flow (icon nodes on a connected line)

Richer alternative to the 4-step `.path` for a "how it works / our method" slide. Big circular Phosphor icons over an animated connector — more elaborate than plain stacked cards.

```html
<div class="flow">
  <div class="flow-node">
    <i class="ph ph-microphone-stage ph-icon teal"></i>
    <h3>1 · Capter</h3>
    <p>Short description of step one.</p>
  </div>
  <div class="flow-node">
    <i class="ph ph-tree-structure ph-icon"></i>
    <h3>2 · Structurer</h3>
    <p>Short description.</p>
  </div>
  <div class="flow-node">
    <i class="ph ph-robot ph-icon navy"></i>
    <h3>3 · Augmenter</h3>
    <p>Short description.</p>
  </div>
  <div class="flow-node">
    <i class="ph ph-package ph-icon"></i>
    <h3>4 · Livrer</h3>
    <p>Short description.</p>
  </div>
</div>
```

Pair with a `big-message` band underneath for the "so what / takeaway".

---

## Value × Complexity Bubble Matrix (Chart.js)

Prioritization output (use cases, initiatives, risks) plotted on a value × complexity grid, colored by category. See `references/charts.md` for the `buildMatrix()` script, category colors, axis labels and the lazy-init pattern (charts MUST be built when their slide becomes active — otherwise tooltips mis-align).

```html
<div class="two-col left-wide">
  <article class="chart-card animate d2">
    <div class="eyebrow" style="margin-bottom:0;">Valeur métier × complexité</div>
    <div class="chart-wrap" style="height:330px;">
      <canvas id="matrixMain"></canvas>
    </div>
    <p class="source-note">Survolez une bulle pour le détail · taille = valeur · Source : ...</p>
  </article>
  <div class="animate d3" style="display:flex; flex-direction:column; gap:18px; justify-content:center;">
    <div class="cat-legend">
      <div class="cat-row"><span class="cat-dot qw"></span><div><span class="n">20</span> <span class="l">Quick wins — valeur haute, faible complexité</span></div></div>
      <div class="cat-row"><span class="cat-dot ps"></span><div><span class="n">16</span> <span class="l">Projets structurants — fort impact</span></div></div>
      <div class="cat-row"><span class="cat-dot exp"></span><div><span class="n">4</span> <span class="l">Expérimentations</span></div></div>
      <div class="cat-row"><span class="cat-dot ac"></span><div><span class="n">1</span> <span class="l">À challenger</span></div></div>
    </div>
  </div>
</div>
```

Each data point should carry a short `ex` (concrete example) field so the tooltip can show name + example + axes — much more useful than coordinates alone.

---

## Product Preview Cards (clickable, with screenshot)

For an app / product portfolio slide. Each card shows a screenshot that zooms on hover, a tag, title, one-liner and a status/CTA. Wrap in `<a>` for live products. Use 3 cards by default, or 4 with an inline `grid-template-columns:repeat(4,minmax(0,1fr))`.

```html
<div class="product-grid">
  <a class="product-card" href="https://app.example.com" target="_blank" rel="noreferrer">
    <div class="shot-wrap"><img class="shot" src="../assets/DECK_NAME/preview-app.png" alt="App"></div>
    <div class="pbody">
      <span class="ptag"><i class="ph-fill ph-compass"></i>Catégorie</span>
      <strong>Nom du produit</strong>
      <p>Une phrase de description.</p>
      <span class="open">Découvrir <i class="ph-bold ph-arrow-up-right"></i></span>
    </div>
  </a>
  <div class="product-card">
    <div class="shot-wrap"><img class="shot" src="../assets/DECK_NAME/preview-b.png" alt="B"></div>
    <div class="pbody">
      <span class="ptag"><i class="ph-fill ph-flask"></i>MVP</span>
      <strong>Produit en test</strong>
      <p>Description.</p>
      <span class="open">MVP en cours <i class="ph-bold ph-flask"></i></span>
    </div>
  </div>
</div>
```

Copy the screenshots into `03-Outputs/assets/<deck-slug>/` like any other asset. Crop is handled by `object-fit:cover; object-position:top`.

---

## Foundation Strip (full-width gradient base band)

For a "the common platform / foundation everything sits on" band — typically placed **below** a product grid to read as the base layer. Holds an icon, a text block and 1-3 white logo chips.

```html
<div class="foundation animate d4">
  <i class="ph-fill ph-stack ph-icon large"></i>
  <div class="f-txt">
    <div class="eyebrow">La fondation</div>
    <strong>Landing Zone Azure — le socle commun</strong>
    <p>Une phrase sur ce que le socle apporte et ce qui s'y déploie.</p>
  </div>
  <div class="f-logos">
    <div class="chip" style="background-image:url('../assets/DECK_NAME/azure.png');"></div>
    <div class="chip" style="background-image:url('../assets/DECK_NAME/microsoft_fabric.png');"></div>
  </div>
</div>
```

---

## Gantt Roadmap (timeline)

Preferred for a roadmap slide when phases overlap across time — richer than the 4-step `.path`. Column 1 = labels, columns 2..N = time buckets. Place each label and bar with explicit `grid-row`; span time with `grid-column:start/end`. Bar status: `.done` (green), `.prog` (navy), `.plan` (hatched). Add `.g-today` for a dashed "now" line. A chantier can have several segments on the same row (e.g. MVP → Scale → Prod).

```html
<div class="gantt animate d2">
  <div class="g-corner"></div>
  <div class="g-head" style="grid-column:2;">Avr</div>
  <div class="g-head" style="grid-column:3;">Mai</div>
  <div class="g-head" style="grid-column:4;">Juin</div>
  <div class="g-head" style="grid-column:5;">Juil</div>
  <div class="g-head" style="grid-column:6;">Août</div>
  <div class="g-head" style="grid-column:7;">Sept</div>
  <div class="g-head" style="grid-column:8;">Q4</div>
  <div class="g-today" style="grid-column:5;"></div>

  <div class="g-label" style="grid-row:2;"><i class="ph-fill ph-magnifying-glass"></i>Audit</div>
  <div class="g-bar done" style="grid-row:2; grid-column:2 / 5;">Réalisé</div>

  <div class="g-label" style="grid-row:3;"><i class="ph-fill ph-address-book"></i>Produit (MVP→prod)</div>
  <div class="g-bar prog" style="grid-row:3; grid-column:3 / 6;">MVP</div>
  <div class="g-bar plan" style="grid-row:3; grid-column:6 / 7;">Scale</div>
  <div class="g-bar plan" style="grid-row:3; grid-column:7 / 9;">Prod groupe</div>
</div>
```

`grid-template-columns` is `190px repeat(7, 1fr)` by default — adjust the repeat count to match your number of time buckets, and place `.g-today` at the column that starts "now".

---

## Journey Stepper (premium closing milestone bar)

For a closing / status slide — a polished alternative to `readiness-rail`. 5 nodes on a connector: `.done` filled green, `.current` pulsing ring ("we are here"), plain = future.

```html
<div class="journey animate d3">
  <div class="j-step done"><div class="j-ic"><i class="ph-fill ph-magnifying-glass"></i></div><strong>Audit</strong><span>Fait</span></div>
  <div class="j-step done"><div class="j-ic"><i class="ph-fill ph-compass"></i></div><strong>Vision</strong><span>Fait</span></div>
  <div class="j-step done"><div class="j-ic"><i class="ph-fill ph-stack"></i></div><strong>Socle</strong><span>Fait</span></div>
  <div class="j-step current"><div class="j-ic"><i class="ph-fill ph-rocket-launch"></i></div><strong>Projets</strong><span>Nous sommes ici</span></div>
  <div class="j-step"><div class="j-ic"><i class="ph-fill ph-trend-up"></i></div><strong>Échelle</strong><span>À venir</span></div>
</div>
```

Add `<div class="deco-shapes" aria-hidden="true"></div>` on the slide for a subtle branded backdrop.

---

## Annex Tag

Marks appendix slides kept after the main deck (full data, detailed charts) — surfaced only if the audience digs deeper.

```html
<span class="annex-tag animate d1"><i class="ph-fill ph-paperclip"></i>Annexe A</span>
```

---

## Slide Archetypes (aerated, low-density)

Use these for rhythm and to keep slides light. They adapt to the deck theme
automatically (text follows the slide color). `section-divider`, `quote` and
`big-number` shine as **accent** slides (`dark` in a light deck, `light` in a
dark deck).

### Section Divider (chapter break)

```html
<section class="slide section-divider dark">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Partie 2</div></header>
  <div class="body">
    <div class="sd-index animate d1">02</div>
    <h2 class="sd-title animate d2">Le titre du chapitre, court et net.</h2>
    <p class="sd-sub animate d3">Une ligne de contexte optionnelle.</p>
  </div>
  <footer class="footer"><div class="sources"></div><div class="progress" aria-hidden="true"></div></footer>
</section>
```

### Quote (full-bleed citation)

```html
<section class="slide quote">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Verbatim</div></header>
  <div class="body">
    <blockquote class="animate d1">Une citation marquante, en une à deux phrases maximum.</blockquote>
    <div class="q-author animate d2"><div><span class="q-name">Prénom Nom</span> · <span class="q-role">Rôle, Direction</span></div></div>
  </div>
  <footer class="footer"><div class="sources">Source : entretien interne.</div><div class="progress" aria-hidden="true"></div></footer>
</section>
```

### Agenda (numbered outline, optionally clickable)

Wrap items in `<a class="agenda-item" href="?slide=N">` to jump to a slide; use `<div class="agenda-item">` for a static outline.

```html
<section class="slide agenda">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Sommaire</div></header>
  <div class="body">
    <h2 class="animate d1">Au programme</h2>
    <div class="agenda-list animate d2">
      <a class="agenda-item" href="?slide=3"><span class="ai-num">1</span><span><span class="ai-title">Contexte</span><span class="ai-sub">Où en est-on aujourd'hui.</span></span></a>
      <a class="agenda-item" href="?slide=5"><span class="ai-num">2</span><span><span class="ai-title">Enjeux</span><span class="ai-sub">Ce qui est en jeu.</span></span></a>
      <a class="agenda-item" href="?slide=7"><span class="ai-num">3</span><span><span class="ai-title">Décision</span><span class="ai-sub">Ce qu'on demande.</span></span></a>
    </div>
  </div>
  <footer class="footer"><div class="sources"></div><div class="progress" aria-hidden="true"></div></footer>
</section>
```

### Big Number (single hero KPI)

```html
<section class="slide big-number dark">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Le chiffre</div></header>
  <div class="body">
    <span class="bn-metric counter animate d1" data-target="68" data-suffix="%">0%</span>
    <p class="bn-label animate d2">La phrase qui donne le sens du chiffre.</p>
    <p class="bn-sub animate d3">Précision / périmètre / source.</p>
  </div>
  <footer class="footer"><div class="sources">Source : ...</div><div class="progress" aria-hidden="true"></div></footer>
</section>
```

### Closing (final message + next steps + contact)

```html
<section class="slide closing dark">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Prochaines étapes</div></header>
  <div class="body">
    <h2 class="closing-title animate d1">Ce qu'on retient, et la suite.</h2>
    <div class="closing-steps pill-row animate d2"><span class="pill">Valider le périmètre</span><span class="pill">Lancer le pilote</span><span class="pill">Point à J+30</span></div>
    <div class="closing-contact animate d3"><i class="ph ph-envelope-simple"></i> c.peponnet@snetor.com</div>
  </div>
  <div class="deco-shapes" aria-hidden="true"></div>
  <footer class="footer"><div class="sources"></div><div class="progress" aria-hidden="true"></div></footer>
</section>
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
