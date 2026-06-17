# Charts — Dynamic Visualizations

Chart.js + jsvectormap + native counters. Use these instead of hand-coded SVG / static CSS bars whenever the data is non-trivial (multi-series, donut, line trend, radar, area, world map).

---

## CDN libraries

Add to `<head>` only when the deck includes charts or maps:

```html
<!-- Chart.js (always include if any chart-card is used) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js"></script>

<!-- jsvectormap (only if .world-map is used) -->
<script src="https://cdn.jsdelivr.net/npm/jsvectormap@1.5.4/dist/jsvectormap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jsvectormap@1.5.4/dist/maps/world.js"></script>
<link href="https://cdn.jsdelivr.net/npm/jsvectormap@1.5.4/dist/jsvectormap.min.css" rel="stylesheet">
```

Pin versions exactly as above to avoid breakage.

---

## Snetor theme for Chart.js

Place once at the very start of the chart bootstrap script (after Chart.js loaded, before any chart instantiation):

```javascript
const SNETOR_PALETTE = ['#007D36', '#152B47', '#168C74', '#8CCAAE', '#293F52', '#CCE0CD'];
Chart.defaults.font.family = 'Raleway, system-ui, sans-serif';
Chart.defaults.font.weight = '600';
Chart.defaults.color = '#4A5A6E';
Chart.defaults.animation = { duration: 900, easing: 'easeOutCubic' };
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 14;
```

---

## chart-card component

```html
<article class="chart-card animate d1">
  <div class="eyebrow">Chart label</div>
  <h3>Chart headline</h3>
  <div class="chart-wrap">
    <canvas
      data-chart="bar"
      data-labels='["Azure","AWS","GCP","Other"]'
      data-values='[24,31,11,34]'
      data-suffix="%"
    ></canvas>
  </div>
  <p class="source-note">Source: <a href="URL">label</a></p>
</article>
```

Supported `data-chart` types: `bar`, `line`, `donut`, `radar`, `area`.

Optional attributes:
- `data-suffix="%"` — appended to tick and tooltip values
- `data-label="Label"` — series legend label

---

## Bootstrap script (chart-card)

Append to the end of `<body>` after navigation JS:

```javascript
function snetorChartConfig(canvas) {
  const type = canvas.dataset.chart;
  const labels = JSON.parse(canvas.dataset.labels || '[]');
  const values = JSON.parse(canvas.dataset.values || '[]');
  const suffix = canvas.dataset.suffix || '';

  const dataset = {
    label: canvas.dataset.label || '',
    data: values,
    backgroundColor: type === 'donut' ? SNETOR_PALETTE
      : type === 'area' ? 'rgba(0,125,54,.18)'
      : type === 'radar' ? 'rgba(0,125,54,.22)'
      : '#007D36',
    borderColor: '#007D36',
    borderWidth: ['line', 'area', 'radar'].includes(type) ? 3 : 0,
    fill: type === 'area' || type === 'radar',
    tension: 0.3,
    pointRadius: ['line', 'area', 'radar'].includes(type) ? 4 : 0,
    pointBackgroundColor: '#007D36',
  };

  const chartType = type === 'area' ? 'line' : type === 'donut' ? 'doughnut' : type;
  return {
    type: chartType,
    data: { labels, datasets: [dataset] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: type === 'donut' || type === 'radar' },
        tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.parsed.y ?? ctx.parsed.r ?? ctx.parsed}${suffix}` } }
      },
      scales: ['bar', 'line', 'area'].includes(type) ? {
        y: { beginAtZero: true, grid: { color: '#E0E5DF' }, ticks: { callback: (v) => v + suffix } },
        x: { grid: { display: false } }
      } : type === 'radar' ? {
        r: { beginAtZero: true, grid: { color: '#E0E5DF' }, angleLines: { color: '#E0E5DF' }, pointLabels: { color: '#152B47', font: { weight: '700' } } }
      } : undefined
    }
  };
}

document.querySelectorAll('canvas[data-chart]').forEach((canvas) => {
  new Chart(canvas, snetorChartConfig(canvas));
});
```

---

## Counter animation (.metric.counter)

For hero metrics that should count up from 0 when the slide becomes active:

```html
<span class="metric counter" data-target="88" data-suffix="%" data-duration="1200">0%</span>
```

Attributes:
- `data-target` (required) — final value (number)
- `data-suffix` — string appended (e.g. `%`, `M€`, `+`)
- `data-duration` — milliseconds, default 1000

Bootstrap script:

```javascript
function animateCounter(el) {
  if (el.dataset.animated === '1') return;
  el.dataset.animated = '1';
  const target = parseFloat(el.dataset.target);
  const duration = parseInt(el.dataset.duration || '1000', 10);
  const suffix = el.dataset.suffix || '';
  const start = performance.now();
  function step(now) {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = Math.round(target * eased) + suffix;
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function runCountersOnActive() {
  document.querySelectorAll('.slide.active .counter').forEach(animateCounter);
}
```

**Hook into `show()` from navigation JS** by adding `runCountersOnActive();` right before the `document.title = ...` line.

When re-entering a slide, counters with `data-animated="1"` are skipped (no flicker). To allow re-animation on re-entry, remove the `if (el.dataset.animated === '1') return;` guard.

---

## World map (jsvectormap)

For implantations / coverage / geographical reach slides:

```html
<div class="world-map" data-points='[
  {"name":"HQ Lyon","coords":[45.74,4.84]},
  {"name":"Madrid","coords":[40.42,-3.70]},
  {"name":"São Paulo","coords":[-23.55,-46.63]},
  {"name":"Singapore","coords":[1.35,103.82]}
]'></div>
```

Bootstrap script:

```javascript
document.querySelectorAll('.world-map').forEach((el) => {
  const markers = JSON.parse(el.dataset.points || '[]');
  new jsVectorMap({
    selector: el,
    map: 'world',
    backgroundColor: 'transparent',
    regionStyle: {
      initial: { fill: '#E5EFE5', stroke: '#CCE0CD', strokeWidth: 0.5 },
      hover: { fill: '#CCE0CD', cursor: 'default' }
    },
    markers,
    markerStyle: {
      initial: { fill: '#007D36', stroke: '#FFFFFF', strokeWidth: 2, r: 6 },
      hover: { fill: '#168C74', stroke: '#FFFFFF', strokeWidth: 3, r: 8 }
    },
    markersSelectable: false,
    zoomOnScroll: false,
    zoomButtons: false,
  });
});
```

Markers expect `coords: [latitude, longitude]`. Pass an empty array if you only want regions without points.

---

## When to use each chart type

| Type | When |
|---|---|
| `bar` | Comparing 3-8 discrete categories |
| `donut` | Market share / distribution (max 6 slices) |
| `line` | Trend over time (5+ points) |
| `area` | Cumulative trend or single-series emphasis |
| `radar` | Capability / readiness comparison (4-8 axes) |
| static `.stacked` (CSS) | Single horizontal stacked bar with 3-4 segments — keep using when no labels needed beyond %s |
| static `.impact-bars` (CSS) | 2-3 horizontal progress bars with manual percentages |

If the data is a single percentage or a static demonstration, the existing CSS components (`.stacked`, `.impact-bars`) remain preferable — lighter and no JS.
