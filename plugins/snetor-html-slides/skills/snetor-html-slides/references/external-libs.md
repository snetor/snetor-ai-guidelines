# External Libraries & Modern Components

CDN-hosted libraries and code-copied components. All Snetor-branded.

---

## Index

1. [21st.dev components — Snetor-branded](#21stdev-components)
   - Marquee
   - Bento grid
   - Spotlight card
2. [Phosphor Icons — fact-card iconography](#phosphor-icons)

---

## 21st.dev components

Inspired by [21st.dev](https://21st.dev). Code is copied & adapted to Snetor branding (no npm dependency, no CDN).

### Marquee — infinite logo scroll

For "ecosystem" / "clients" / "partners" slides with **6 or more** logos. For ≤5, use a static row instead.

```html
<div class="marquee animate d1">
  <div class="marquee-track">
    <!-- duplicate the inner logos twice for seamless loop -->
    <div class="marquee-logo" style="background-image:url('../assets/DECK/azure.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/aws.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/gcp.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/sap.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/anthropic.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/openai.png');"></div>
    <!-- duplicates -->
    <div class="marquee-logo" style="background-image:url('../assets/DECK/azure.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/aws.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/gcp.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/sap.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/anthropic.png');"></div>
    <div class="marquee-logo" style="background-image:url('../assets/DECK/openai.png');"></div>
  </div>
</div>
```

CSS handles infinite scroll. Pause on hover. **Always duplicate the logo set twice** in the markup so the loop is seamless.

---

### Bento grid — asymmetric value prop

For "what we do" / "value proposition synthesis" slides. **Max 1 per deck.**

5 cells with varied spans:

```html
<div class="bento animate d1">
  <article class="bento-cell big">
    <div class="eyebrow">Mission</div>
    <h3>Accélérer l'IA dans la chaîne de valeur Snetor</h3>
    <p>Un texte de synthèse plus long ici, occupant la plus grande cellule.</p>
  </article>
  <article class="bento-cell">
    <span class="metric">12</span>
    <p>Projets pilotes 2026</p>
  </article>
  <article class="bento-cell green">
    <h3>Sécurité by design</h3>
    <p>Données EU only.</p>
  </article>
  <article class="bento-cell tall">
    <h3>Roadmap</h3>
    <p>POC → Pilote → Run → Scale</p>
  </article>
  <article class="bento-cell dark">
    <span class="metric pastel">42%</span>
    <p>Gain de productivité moyen.</p>
  </article>
</div>
```

Cell modifiers: `.big` (col-span 2), `.tall` (row-span 2), `.green` (green tint), `.dark` (navy gradient with pastel metric).

---

### Spotlight card — follows mouse

For dark slides only, max 1 row of these per deck. The card has a radial gradient that follows the cursor.

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

**Bootstrap script** (append after presenter-mode JS):

```javascript
document.querySelectorAll('.spotlight-card').forEach((card) => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    card.style.setProperty('--mx', `${e.clientX - rect.left}px`);
    card.style.setProperty('--my', `${e.clientY - rect.top}px`);
  });
});
```

CSS uses `--mx` / `--my` to position a radial gradient mask.

---

## Phosphor Icons

Lightweight icon library for fact-cards and inline iconography. Web-font, ~3000 icons, six weights (thin / light / regular / bold / fill / duotone). Works under `file://` (no XHR), no CORS, no JSON loading.

### CDN

Add to `<head>` once if the deck uses any `<i class="ph ...">` icon:

```html
<script src="https://unpkg.com/@phosphor-icons/web"></script>
```

The script auto-loads all six weight stylesheets. Single line, no bootstrap needed.

### Component on fact-card

```html
<article class="fact-card animate d1">
  <i class="ph ph-trophy ph-icon"></i>
  <span class="metric counter" data-target="42" data-suffix="%">0%</span>
  <h3>Croissance</h3>
  <p>Sur 12 mois.</p>
</article>
```

Class breakdown:
- `ph` — base class (required, regular weight by default)
- `ph-<name>` — icon name (e.g. `ph-trophy`, `ph-shield-check`)
- `ph-icon` — Snetor sizing/color override (defined in `css-system.md`)

**Tone variants** (mix across a deck for visual rhythm):
- default (green) — growth, KPIs, finance
- `.ph-icon.navy` — security, risk, governance
- `.ph-icon.teal` — tech, AI, data
- `.ph-icon.large` — for cover or hero positioning (56×56)

### Weight variants

Replace `ph` with one of:
- `ph-thin` (1px stroke)
- `ph-light` (1.5px)
- `ph` (2px, default)
- `ph-bold` (2.5px)
- `ph-fill` (solid fill)
- `ph-duotone` (two-tone)

For Snetor decks, prefer **`ph` (regular)** or **`ph-fill`** for KPI cards (more visual weight).

### Recommended icons by topic

| Topic | Icon |
|---|---|
| Growth / KPI | `ph-trend-up`, `ph-trophy`, `ph-rocket-launch` |
| Quality / Validation | `ph-check-circle`, `ph-star`, `ph-medal` |
| Speed | `ph-lightning`, `ph-rocket`, `ph-clock-counter-clockwise` |
| Security | `ph-shield-check`, `ph-lock`, `ph-fingerprint` |
| Cloud / IT | `ph-cloud`, `ph-cloud-check`, `ph-database` |
| Logistics | `ph-truck`, `ph-package`, `ph-globe-hemisphere-east` |
| AI / Data | `ph-brain`, `ph-cpu`, `ph-graph` |
| People | `ph-users-three`, `ph-user-circle`, `ph-handshake` |
| Money | `ph-currency-eur`, `ph-coins`, `ph-chart-line-up` |

Browse the full catalog at [phosphoricons.com](https://phosphoricons.com).

---

## Loading order

When a deck uses several of these libraries, the `<head>` script tags must be in this order:

```html
<!-- in <head> -->
<!-- 1. Chart.js (if charts used) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js"></script>

<!-- 2. jsvectormap (if world map used) -->
<script src="https://cdn.jsdelivr.net/npm/jsvectormap@1.5.4/dist/jsvectormap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jsvectormap@1.5.4/dist/maps/world.js"></script>
<link href="https://cdn.jsdelivr.net/npm/jsvectormap@1.5.4/dist/jsvectormap.min.css" rel="stylesheet">

<!-- 3. Phosphor Icons (if icons used) -->
<script src="https://unpkg.com/@phosphor-icons/web"></script>
```

Bootstrap scripts at the end of `<body>` in this order:

1. Navigation JS
2. Interactivity (tabs, accordion, tooltips)
3. Presenter mode (F/O/?/N/T)
4. Charts + counters + world map (only if used)
5. Spotlight (only if used)

(Phosphor needs no bootstrap script — it's pure font-icon rendering.)
