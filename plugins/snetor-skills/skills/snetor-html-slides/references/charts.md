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

> **⚠️ Tooltip gotcha (REQUIRED for any chart with hover tooltips).** The global
> `Chart.defaults.animation` override above freezes the tooltip's opacity animation: on hover
> the tooltip becomes *active* (`getActiveElements().length === 1`, correct title) but its
> `opacity` stays stuck at ~0.02 — **active but invisible, so tooltips look broken**. Setting
> `plugins.tooltip.animation` does NOT fix it; you must override the chart's own animation.
> The reliable fix is **`animation: false` in the chart's `options`** (see `buildMatrix` /
> `buildCharges` below) — entrance flair is already provided by the slide's CSS `animate`
> classes, so disabling Chart.js's internal animation costs nothing visually. Symptom is
> invisible only at runtime: verify with a trusted CDP hover and read back `chart.tooltip.opacity`
> (expect `1`), not a static screenshot.

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

  // Theme-aware text/grid colors: charts on a dark slide (.dark/.cover accent
  // or any slide of a theme-dark deck that is not a .light accent) need light
  // legend/axis text — Chart.defaults.color (#4A5A6E) is unreadable on dark.
  const slide = canvas.closest('.slide');
  const onDark = !!slide && (slide.classList.contains('dark') || slide.classList.contains('cover')
    || (!!document.querySelector('.deck.theme-dark') && !slide.classList.contains('light')));
  const ink = onDark ? 'rgba(255,255,255,.82)' : '#4A5A6E';
  const gridc = onDark ? 'rgba(255,255,255,.16)' : '#E0E5DF';
  const ptLabel = onDark ? '#FFFFFF' : '#152B47';

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
        legend: { display: type === 'donut' || type === 'radar', labels: { color: ink } },
        tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.parsed.y ?? ctx.parsed.r ?? ctx.parsed}${suffix}` } }
      },
      scales: ['bar', 'line', 'area'].includes(type) ? {
        y: { beginAtZero: true, grid: { color: gridc }, ticks: { color: ink, callback: (v) => v + suffix } },
        x: { grid: { display: false }, ticks: { color: ink } }
      } : type === 'radar' ? {
        r: { beginAtZero: true, grid: { color: gridc }, angleLines: { color: gridc }, pointLabels: { color: ptLabel, font: { weight: '700' } } }
      } : undefined
    }
  };
}

// LEGACY eager bootstrap — superseded by the lazy-init pattern (SKILL rule 22).
// Building a chart while its slide is display:none renders to a 0px canvas (blank
// + dead tooltips). Use initChartsOnActive() below instead; keep this only for a
// single-chart prototype without slide navigation.
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

## ⚠️ Lazy-init: build charts on slide activation, after layout (CRITICAL)

This is the single most error-prone part of a chart deck. Get all three details right:

1. **Never build eagerly at load.** A chart created while its slide is `display:none` sizes its canvas to 0px. Result: the chart renders blank (you "have to reload to see it"), and its hover/tooltip hit model stays calibrated on the 0px size, so **tooltips never trigger even though the chart later paints**.
2. **Build inside `requestAnimationFrame`,** not synchronously in `show()`. When `show()` flips the `.active` class the slide is still being laid out (and a CSS enter-animation may be running); a synchronous `new Chart()` reads a not-yet-settled size. One `rAF` lets layout settle first.
3. **Keep the instance and `resize()` on every (re)activation.** Revisiting a slide, or a viewport change, needs an explicit `chart.resize()` to re-sync the canvas and the hit model.

Builders must **`return` the `Chart` instance** (see `buildMatrix` / `buildCharges` below — note the `return new Chart(...)`).

```javascript
const chartBuilders = {
  matrixMain: () => buildMatrix('matrixMain', RAW.filter(d => d.key)),
  matrixFull: () => buildMatrix('matrixFull', RAW),
  chargeBars: () => buildCharges('chargeBars')
};
const chartInstances = {};
function initChartsOnActive() {
  if (!window.Chart) return;
  slides[current].querySelectorAll('canvas[id]').forEach((c) => {
    const id = c.id;
    if (chartInstances[id]) { requestAnimationFrame(() => chartInstances[id].resize()); return; }
    if (!chartBuilders[id]) return;
    requestAnimationFrame(() => {
      if (chartInstances[id]) return;
      chartInstances[id] = chartBuilders[id]();
      requestAnimationFrame(() => { if (chartInstances[id]) chartInstances[id].resize(); });
    });
  });
}
```

Hook `initChartsOnActive();` into `show()` right before the `document.title = ...` line (next to `runCountersOnActive();`). Set `Chart.defaults` once at load, but defer the `new Chart(...)` calls to `initChartsOnActive`.

> **Verifying it really works** (you can't see hover in a static screenshot): drive headless Edge/Chrome over the DevTools Protocol — `Page.navigate`, send `ArrowRight` `Input.dispatchKeyEvent`s to reach the slide, then a trusted `Input.dispatchMouseEvent {type:'mouseMoved'}` on a bubble, and read back `Chart.getChart(canvasEl).getActiveElements().length` / `.tooltip.title`. Probe with the **canvas element** (`Chart.getChart(document.getElementById(id))`) — `Chart.getChart('id')` by string returns `undefined` and gives false negatives. Note: a synthetic `new MouseEvent('mousemove')` is unreliable (no `offsetX/Y`); use trusted CDP events.

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
  return new Chart(document.getElementById(canvasId), {
    type: 'bubble',
    data: { datasets },
    options: {
      animation: false, // REQUIRED: see tooltip gotcha above — keeps hover tooltips visible
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
  return new Chart(document.getElementById(canvasId), {
    type: 'bar',
    data: { labels: rows.map(d => d.name), datasets: [{
      label: 'j-h / mois', data: rows.map(d => d.jh),
      backgroundColor: rows.map(d => CAT[d.cat].bg), borderColor: rows.map(d => CAT[d.cat].border),
      borderWidth: 1, borderRadius: 4 }] },
    options: { animation: false, /* see tooltip gotcha above */ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display:false } },
      scales: { x: { beginAtZero:true, grid:{color:'#E0E5DF'} }, y: { grid:{display:false}, ticks:{color:'#152B47', font:{size:11, weight:'600'}} } } }
  });
}
```

---

## Deep-dive patterns (opt-in — audience technique / annexe)

> These are for the **rich / deep-dive** density only. For an executive / COMEX slide, prefer the CSS **macro cost-code** bars (`references/components.md`) — bigger, legible from far, no legend with 7 entries. Use the patterns below when the audience actually wants the ventilation.

### Multi-series stacked bar (TCO ventilé par poste)

Several cost lines stacked per candidate, with a **footer showing the total**. All datasets share `stack:'t'`; build via lazy-init like any chart. Keep to ≤ 4-5 segments or it becomes unreadable.

```javascript
const TCO = { // k€, per candidate
  'Akeneo':    { build: 62, lic: 68,  staff: 75.75, infra: 32 },
  'Home-made': { build: 20, lic: 0,   staff: 124.5, infra: 44 }
};
const order = ['Home-made','Akeneo'];
const total = (c) => { const t = TCO[c]; return t.build + (t.lic + t.staff + t.infra) * 3; };
function buildStackedTco(canvasId) {
  if (!window.Chart) return;
  return new Chart(document.getElementById(canvasId), {
    type: 'bar',
    data: { labels: order, datasets: [
      { label: 'Build + contingence',   data: order.map(c => TCO[c].build),   backgroundColor: '#8CCAAE', stack: 't', borderRadius: 3 },
      { label: 'Licence / TMA (3 ans)', data: order.map(c => TCO[c].lic * 3),  backgroundColor: '#293F52', stack: 't', borderRadius: 3 },
      { label: 'Staffing recruté (3 ans)', data: order.map(c => TCO[c].staff * 3), backgroundColor: '#168C74', stack: 't', borderRadius: 3 },
      { label: 'Infra, IA & contingence (3 ans)', data: order.map(c => TCO[c].infra * 3), backgroundColor: '#B6C2C9', stack: 't', borderRadius: 3 }
    ] },
    options: { animation: false, /* see tooltip gotcha */ responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position:'bottom', labels:{ usePointStyle:true, padding:10, boxWidth:10, font:{family:'Raleway',weight:'600',size:10} } },
        tooltip: { callbacks: {
          label: (ctx) => `${ctx.dataset.label} : ${ctx.parsed.y.toLocaleString('fr-FR')} k€`,
          footer: (items) => 'TCO : ' + total(items[0].label).toLocaleString('fr-FR') + ' k€' } } },
      scales: { x: { stacked:true, grid:{display:false}, ticks:{color:'#152B47',font:{weight:'700'}} },
                y: { stacked:true, beginAtZero:true, grid:{color:'#E0E5DF'}, ticks:{color:'#4A5A6E', callback:(v)=>v+'k'} } } }
  });
}
```

### Superposed radar (2 profils comparés)

Two datasets on one radar to compare two finalists axis-by-axis (mirror profiles → close scores). Green (`#007D36`) vs navy (`#152B47`).

```javascript
const DIMS = ['Couverture','UX / adoption','Time-to-value','TCO / run','Pérennisation','Fondation data'];
const NOTES = { 'Full custom':[5,5,3.75,4,3,4.5], 'Akeneo':[4.9,4,4.5,3.75,5,4] };
function buildRadarFinalists(canvasId) {
  if (!window.Chart) return;
  return new Chart(document.getElementById(canvasId), {
    type: 'radar',
    data: { labels: DIMS, datasets: [
      { label:'Full custom', data: NOTES['Full custom'], borderColor:'#007D36', backgroundColor:'rgba(0,125,54,.14)', borderWidth:2.5, pointRadius:2.5, pointBackgroundColor:'#007D36' },
      { label:'Akeneo',      data: NOTES['Akeneo'],      borderColor:'#152B47', backgroundColor:'rgba(21,43,71,.12)', borderWidth:2.5, pointRadius:2.5, pointBackgroundColor:'#152B47' }
    ] },
    options: { animation: false, /* see tooltip gotcha */ responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position:'bottom', labels:{ usePointStyle:true, padding:14, font:{family:'Raleway',weight:'600'} } },
        tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label} : ${ctx.parsed.r}/5` } } },
      scales: { r: { min:0, max:5, grid:{color:'#E0E5DF'}, angleLines:{color:'#E0E5DF'}, pointLabels:{color:'#152B47',font:{weight:'700',size:12}}, ticks:{display:false, stepSize:1, backdropColor:'transparent'} } } }
  });
}
```

Both builders `return` the Chart and hook into the same `initChartsOnActive()` lazy-init + `animation:false` tooltip rules as every other chart.
