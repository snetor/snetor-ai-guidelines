# External Libraries & Modern Components

CDN-hosted libraries and code-copied components for v1.2 features. All Snetor-branded.

---

## Index

1. [21st.dev components — Snetor-branded](#21stdev-components)
   - Marquee
   - Bento grid
   - Animated shiny text
   - Spotlight card
2. [Lottie icons](#lottie-icons)
3. [tsParticles cover](#tsparticles-cover)

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

### Animated shiny text

For h1 cover headline and 1 big-message punchline per deck. Animate a shimmer that sweeps across text.

```html
<h1 class="shiny-text">Snetor AI Strategy 2026.</h1>
```

Pure CSS via `background-clip: text` + animated gradient. Works on both light and dark backgrounds (default = light text on dark; add `.shiny-text.dark-bg` for navy text on light).

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

## Lottie icons

For animated icons on `.fact-card` (replacing static emoji or no-icon). Use sparingly — meant to draw attention to the metric, not decorate every slide.

### CDN

```html
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie_light.min.js"></script>
```

Add only if the deck uses Lottie icons. Light build is ~62 KB gzipped.

### Component

```html
<article class="fact-card">
  <div class="lottie-icon" data-src="https://lottie.host/EXAMPLE_HASH/icon.json" data-loop="true"></div>
  <span class="metric counter" data-target="42" data-suffix="%">0%</span>
  <h3>Croissance</h3>
  <p>Sur les 12 derniers mois.</p>
</article>
```

Attributes:
- `data-src` (required) — URL to a Lottie JSON file. Can be a remote URL (LottieFiles, lottie.host) or a relative path to a local copy in `assets/DECK/lottie/`.
- `data-loop` — `"true"` (default) or `"false"`
- `data-autoplay` — `"true"` (default) or `"false"`

### Bootstrap script

```javascript
document.querySelectorAll('.lottie-icon').forEach((el) => {
  if (!window.lottie) return;
  lottie.loadAnimation({
    container: el,
    renderer: 'svg',
    loop: el.dataset.loop !== 'false',
    autoplay: el.dataset.autoplay !== 'false',
    path: el.dataset.src,
  });
});
```

### Sourcing icons

Recommended sources (in order of preference):

1. **lottie.host** (LottieFiles CDN) — copy any community icon URL ending in `.json`
2. **assets/DECK/lottie/** — for guaranteed offline access, download a JSON and reference it by relative path
3. **Custom** — design via LottieFiles editor or After Effects + bodymovin plugin

When adding a Lottie icon to a deck, prefer to download the JSON to `assets/DECK/lottie/` so the deck remains stable if the source URL changes.

---

## tsParticles cover

Subtle particle effect on the cover slide. Activated by adding `.particles` to the cover slide class.

### CDN

```html
<script src="https://cdn.jsdelivr.net/npm/@tsparticles/slim@3.5.0/tsparticles.slim.bundle.min.js"></script>
```

Add only if the deck has a particles cover.

### Activation

```html
<section class="slide cover active particles">
  <!-- normal cover content -->
</section>
```

The bootstrap script auto-injects a `<div id="tsparticles">` inside any `.slide.particles` and starts the engine when that slide becomes active.

### Bootstrap script

```javascript
function initParticles() {
  if (!window.tsParticles) return;
  document.querySelectorAll('.slide.particles').forEach((slide) => {
    if (slide.querySelector('#tsparticles')) return;
    const host = document.createElement('div');
    host.id = 'tsparticles';
    slide.insertBefore(host, slide.firstChild);
  });

  tsParticles.load({
    id: 'tsparticles',
    options: {
      fullScreen: { enable: false },
      background: { color: 'transparent' },
      fpsLimit: 60,
      particles: {
        color: { value: '#8CCAAE' },
        links: { enable: true, color: '#8CCAAE', distance: 130, opacity: 0.25, width: 1 },
        move: { enable: true, direction: 'top', speed: 0.6, outModes: { default: 'out' } },
        number: { value: 40, density: { enable: true, area: 900 } },
        opacity: { value: 0.55 },
        shape: { type: 'circle' },
        size: { value: { min: 1, max: 3 } },
      },
      detectRetina: true,
    },
  });
}

// Call this AFTER the first show(0) so the cover is in DOM
initParticles();
```

The particles are visible only on slides with `.particles`. They render behind text content (z-index 0) and above the gradient background (z-index -1 via CSS).

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

<!-- 3. Lottie (if icons used) -->
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie_light.min.js"></script>

<!-- 4. tsParticles (if particles used) -->
<script src="https://cdn.jsdelivr.net/npm/@tsparticles/slim@3.5.0/tsparticles.slim.bundle.min.js"></script>
```

Bootstrap scripts at the end of `<body>` in this order:

1. Navigation JS
2. Interactivity (tabs, accordion, tooltips)
3. Presenter mode (F/O/?/N/T)
4. Charts + counters + world map (only if used)
5. Spotlight (only if used)
6. Lottie (only if used)
7. tsParticles (only if used)
