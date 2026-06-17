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
    el.textContent = Math.round(target * eased).toLocaleString('fr-FR') + suffix;
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
| `bubble` | Prioritization matrix — value × complexity × size (see below) |
| static `.stacked` (CSS) | Single horizontal stacked bar with 3-4 segments — keep using when no labels needed beyond %s |
| static `.impact-bars` (CSS) | 2-3 horizontal progress bars with manual percentages |

If the data is a single percentage or a static demonstration, the existing CSS components (`.stacked`, `.impact-bars`) remain preferable — lighter and no JS.

---

## ⚠️ Lazy-init: build charts when their slide becomes active

**Charts created while their slide is `display:none` size to 0px, so hover/tooltip hit-testing is misaligned (tooltips appear not to work).** Build each chart the first time its slide is shown — not eagerly at load.

```javascript
const chartBuilders = {
  matrixMain: () => buildMatrix('matrixMain', RAW.filter(d => d.key)),
  matrixFull: () => buildMatrix('matrixFull', RAW),
  chargeBars: () => buildCharges('chargeBars')
};
const builtCharts = {};
function initChartsOnActive() {
  if (!window.Chart) return;
  slides[current].querySelectorAll('canvas[id]').forEach((c) => {
    if (!builtCharts[c.id] && chartBuilders[c.id]) { builtCharts[c.id] = true; chartBuilders[c.id](); }
  });
}
```

Hook `initChartsOnActive();` into `show()` right before the `document.title = ...` line (next to `runCountersOnActive();`). Set `Chart.defaults` once at load, but defer the `new Chart(...)` calls to `initChartsOnActive`.

---

## Bubble matrix — value × complexity prioritization

For a prioritization output (use cases, initiatives, risks) on a 2-axis grid colored by category. Pair with the `.cat-legend` component (see `components.md`). Markup is a single `<canvas id="...">` inside a `chart-card`; build it via `buildMatrix` under lazy-init.

```javascript
const CAT = {
  qw:  {label:"Quick win",          bg:'rgba(0,125,54,.72)',  border:'#007D36'},
  ps:  {label:"Projet structurant", bg:'rgba(21,43,71,.78)',  border:'#152B47'},
  exp: {label:"Expérimentation",    bg:'rgba(42,84,88,.80)',  border:'#2A5458'},
  ac:  {label:"À challenger",       bg:'rgba(180,50,50,.78)', border:'#b43232'}
};
const VL  = ['','Incertaine','Moyenne','Moy.→haute','Haute','Très haute'];   // y, 1..5
const CXL = ['','Faible','Faible→moy.','Moy.→haute','Haute','Très haute'];   // x, 1..5
// Deterministic jitter so points sharing the same (val,cplx) cell don't overlap
function jit(i, salt){ const v = Math.sin((i+1)*(salt===0?12.9898:78.233))*43758.5453; return ((v - Math.floor(v)) - 0.5) * 0.42; }

// RAW = array of { name, dept, val:1-5, cplx:1-5, cat:'qw|ps|exp|ac', ex:'concrete example', key:1? }
function buildMatrix(canvasId, rows) {
  if (!window.Chart) return;
  const datasets = Object.keys(CAT).map((c) => ({
    label: CAT[c].label,
    backgroundColor: CAT[c].bg,
    borderColor: CAT[c].border,
    borderWidth: 1.5,
    data: rows.filter(d => d.cat === c).map((d) => {
      const gi = RAW.indexOf(d);
      return { x: d.cplx + jit(gi,0), y: d.val + jit(gi,1), r: 7 + d.val*2.2, name: d.name, dept: d.dept, ex: d.ex || '' };
    })
  }));
  new Chart(document.getElementById(canvasId), {
    type: 'bubble',
    data: { datasets },
    options: {
      responsive: true, maintainAspectRatio: false, layout: { padding: 6 },
      plugins: {
        legend: { position: 'bottom', labels: { usePointStyle: true, padding: 14, font:{family:'Raleway',weight:'600'} } },
        tooltip: { padding:12, titleFont:{size:14,weight:'700'}, bodyFont:{size:12}, boxPadding:4, callbacks: {
          title: (items) => items[0].raw.name,
          label: (ctx) => ctx.raw.ex,
          afterLabel: (ctx) => `${ctx.raw.dept} · valeur ${VL[Math.round(ctx.raw.y)]||''} · complexité ${CXL[Math.round(ctx.raw.x)]||''}`
        } }
      },
      scales: {
        x: { min:0.4, max:5.6, title:{display:true,text:'Complexité de mise en œuvre →',color:'#7E8A9A',font:{weight:'700'}},
             grid:{color:'#E0E5DF'}, ticks:{stepSize:1, color:'#4A5A6E', callback:(v)=>CXL[v]||''} },
        y: { min:0.4, max:5.6, title:{display:true,text:'↑ Valeur métier',color:'#7E8A9A',font:{weight:'700'}},
             grid:{color:'#E0E5DF'}, ticks:{stepSize:1, color:'#4A5A6E', callback:(v)=>VL[v]||''} }
      }
    }
  });
}
```

Give every data point an `ex` (concrete one-liner) — the tooltip surfaces **name + example + axes**, far more useful than coordinates. Show a pruned `key` subset on the main slide and the full set on an annex slide (same function, different `rows`).

### Horizontal charge bar (companion annex)

For the quantified detail (e.g. effort j-h/mois) behind the matrix — keep it in annex when the numbers are sensitive.

```javascript
function buildCharges(canvasId) {
  if (!window.Chart) return;
  const rows = RAW.filter(d => d.jh != null).sort((a,b) => b.jh - a.jh);
  new Chart(document.getElementById(canvasId), {
    type: 'bar',
    data: { labels: rows.map(d => d.name), datasets: [{
      label: 'j-h / mois', data: rows.map(d => d.jh),
      backgroundColor: rows.map(d => CAT[d.cat].bg), borderColor: rows.map(d => CAT[d.cat].border),
      borderWidth: 1, borderRadius: 4 }] },
    options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display:false } },
      scales: { x: { beginAtZero:true, grid:{color:'#E0E5DF'} }, y: { grid:{display:false}, ticks:{color:'#152B47', font:{size:11, weight:'600'}} } } }
  });
}
```
