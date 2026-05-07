# Snetor HTML Slides — CSS Design System

This file contains the full CSS and design tokens for Snetor-branded HTML presentations.
Always include this CSS verbatim in generated slides (inside a `<style>` tag in `<head>`).
Adapt only the `--logo`, `--logo-reversed`, `--globe`, `--hero` and provider logo paths
to match the actual relative path from the output file to the assets folder.

---

## Color Tokens

```
--green: #007D36         primary brand green
--green-dark: #006028    darker green for hover/depth
--green-20: #CCE0CD      green 20% tint (borders, accents)
--green-10: #E5EFE5      green 10% tint (card backgrounds)
--green-05: #F2F7F2      green 5% tint (subtle fills)
--navy: #152B47          primary dark (headlines, dark slides)
--blue-gray: #293F52     mid dark
--blue-green: #2A5458    teal dark (gradients)
--emerald: #168C74       teal accent
--pastel: #8CCAAE        light green (dark-slide accents)
--midnight: #1E1B2F      deep dark (rarely used)
--white: #FFFFFF
--muted: #4A5A6E         body text on light
--subtle: #7E8A9A        captions, small labels
--border: #E0E5DF        card borders
```

---

## Full CSS Block

```css
:root {
  --green: #007D36;
  --green-dark: #006028;
  --green-20: #CCE0CD;
  --green-10: #E5EFE5;
  --green-05: #F2F7F2;
  --navy: #152B47;
  --blue-gray: #293F52;
  --blue-green: #2A5458;
  --emerald: #168C74;
  --pastel: #8CCAAE;
  --midnight: #1E1B2F;
  --white: #FFFFFF;
  --muted: #4A5A6E;
  --subtle: #7E8A9A;
  --border: #E0E5DF;
  --shadow: 0 18px 40px rgba(21, 43, 71, .14);
  --ease: cubic-bezier(.22, .61, .36, 1);
  /* PATHS: adjust relative to the output HTML file location */
  --logo: url("../assets/DECK_NAME/snetor_full_logo.png");
  --logo-reversed: url("../assets/DECK_NAME/snetor_full_logo_reversed.png");
  --globe: url("../assets/DECK_NAME/snetor_globe.png");
  --hero: url("../assets/DECK_NAME/Hero-banner-abstrait.jpg");
}

* { box-sizing: border-box; }

html, body {
  margin: 0; height: 100%; overflow: hidden;
  background: var(--navy);
  color: var(--navy);
  font-family: "Raleway", system-ui, -apple-system, "Segoe UI", sans-serif;
  letter-spacing: 0;
}

.deck { width: 100vw; height: 100vh; position: relative; background: var(--white); }

.slide {
  position: absolute; inset: 0; display: none;
  grid-template-rows: auto 1fr auto;
  gap: 28px; padding: 44px 64px 34px;
  background: linear-gradient(90deg, rgba(0,125,54,.055), transparent 42%), var(--white);
  overflow: hidden;
}

.slide.active { display: grid; animation: slideIn 520ms var(--ease) both; }
.slide.active .animate { animation: rise 620ms var(--ease) both; }
.slide.active .d1 { animation-delay: 90ms; }
.slide.active .d2 { animation-delay: 170ms; }
.slide.active .d3 { animation-delay: 250ms; }
.slide.active .d4 { animation-delay: 330ms; }

@keyframes slideIn { from { opacity:0; transform:translateX(22px); } to { opacity:1; transform:translateX(0); } }
@keyframes rise { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
@keyframes growLine { from { transform:scaleX(0); } to { transform:scaleX(1); } }
@keyframes growPath { from { transform:translateY(-50%) scaleX(0); } to { transform:translateY(-50%) scaleX(1); } }
@keyframes pulseDot { 0% { box-shadow:0 0 0 0 rgba(0,125,54,.24); } 100% { box-shadow:0 0 0 14px rgba(0,125,54,0); } }
@keyframes fadeScale { from { opacity:0; transform:scale(.96); } to { opacity:1; transform:scale(1); } }
@keyframes growBar { from { transform:scaleX(0); } to { transform:scaleX(1); } }
@keyframes checkPop { 0%{transform:scale(.8);opacity:.3;} 70%{transform:scale(1.08);opacity:1;} 100%{transform:scale(1);opacity:1;} }

@media (prefers-reduced-motion: reduce) {
  .slide.active, .slide.active .animate { animation: none; }
}

/* BRAND HEADER */
.brand { display:flex; align-items:center; justify-content:space-between; gap:24px; min-height:42px; position:relative; z-index:2; }
.logo { width:148px; height:42px; background: var(--logo) left center / contain no-repeat; }
.dark .logo, .cover .logo { background-image: var(--logo-reversed); }
.eyebrow { display:flex; align-items:center; gap:10px; color:var(--green); font-size:12px; font-weight:700; letter-spacing:.18em; text-transform:uppercase; margin-bottom:16px; }
.eyebrow::before { content:""; width:3px; height:18px; background:var(--green); display:inline-block; }
.dark .eyebrow, .cover .eyebrow { color:rgba(255,255,255,.82); }
.dark .eyebrow::before, .cover .eyebrow::before { background:var(--pastel); }

/* TYPOGRAPHY */
h1, h2, h3, p { margin: 0; }
h1 { max-width:980px; font-size:60px; line-height:1.06; font-weight:600; color:var(--white); }
h2 { max-width:1040px; font-size:44px; line-height:1.14; font-weight:600; color:var(--navy); }
h3 { font-size:20px; line-height:1.25; font-weight:700; color:var(--navy); margin-bottom:10px; }
p, li { font-size:18px; line-height:1.48; color:var(--muted); }
ul { margin:0; padding-left:18px; }
li { margin:7px 0; }

/* BODY */
.body { display:flex; flex-direction:column; justify-content:center; gap:26px; position:relative; z-index:2; min-height:0; }

/* SLIDE BACKGROUNDS */
.cover {
  color: white;
  background: linear-gradient(90deg, rgba(21,43,71,.94), rgba(0,125,54,.78)), var(--hero) center / cover no-repeat;
}
.cover::after, .dark::after {
  content:""; position:absolute; right:-120px; top:-120px; width:520px; height:520px;
  border:1px solid rgba(255,255,255,.18); background:rgba(255,255,255,.035); transform:rotate(8deg);
}
.dark {
  background: linear-gradient(135deg, var(--navy), var(--blue-green) 72%, var(--green));
  color: white;
}
.dark h2, .dark h3, .dark p, .dark li { color: white; }

/* LEAD TEXT */
.lead { max-width:850px; font-size:22px; line-height:1.45; color:rgba(255,255,255,.84); margin-top:20px; }
.hero-line { width:172px; height:4px; background:linear-gradient(90deg, var(--pastel), var(--white)); margin-top:34px; transform-origin:left center; }
.slide.active .hero-line { animation: growLine 720ms var(--ease) 360ms both; }

/* GLOBE DECORATION */
.globe { position:absolute; right:72px; bottom:80px; width:210px; height:210px; background:var(--globe) center / contain no-repeat; opacity:.9; z-index:1; }
.slide.active .globe { animation: fadeScale 760ms var(--ease) 220ms both; }

/* STATEMENT */
.statement { max-width:1040px; padding-left:24px; border-left:4px solid var(--green); font-size:28px; line-height:1.34; color:var(--navy); font-weight:600; }
.statement strong { color:var(--green); font-weight:700; }

/* GRIDS */
.grid { display:grid; gap:18px; }
.cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }

/* CARDS */
.card { position:relative; min-height:152px; padding:22px; border:1px solid var(--border); border-radius:6px; background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); overflow:hidden; }
.card::before { content:""; position:absolute; inset:0 0 auto 0; height:4px; background:var(--green); transform-origin:left center; }
.slide.active .card::before { animation: growLine 640ms var(--ease) 260ms both; }
.card.tight { min-height:124px; }
.card.dark-card { background:rgba(255,255,255,.08); border-color:rgba(255,255,255,.24); box-shadow:none; }
.card.dark-card::before { background:var(--pastel); }
.card.dark-card h3, .card.dark-card p { color:var(--white); }

/* METRICS */
.metric { display:block; margin-bottom:12px; color:var(--green); font-size:44px; line-height:1; font-weight:700; }
.metric small { font-size:18px; font-weight:600; color:var(--subtle); }
.dark .metric { color:var(--pastel); }
a.metric, a.share, a.figure-link { color:inherit; text-decoration:none; }
a.metric:hover, a.share:hover, a.figure-link:hover { text-decoration:underline; text-underline-offset:4px; }

/* SOURCE NOTE */
.source-note { display:inline-block; margin-top:10px; color:var(--subtle); font-size:12px; font-weight:600; line-height:1.3; }
.source-note a { color:var(--green); text-decoration:underline; text-underline-offset:3px; }

/* PILLS */
.pill-row { display:flex; flex-wrap:wrap; gap:10px; }
.pill { padding:9px 14px; border-radius:999px; color:var(--green); background:var(--green-10); border:1px solid var(--green-20); font-size:13px; font-weight:700; }
.slide.active .pill { animation: fadeScale 480ms var(--ease) both; }
.slide.active .pill:nth-child(1) { animation-delay:80ms; }
.slide.active .pill:nth-child(2) { animation-delay:140ms; }
.slide.active .pill:nth-child(3) { animation-delay:200ms; }
.slide.active .pill:nth-child(4) { animation-delay:260ms; }
.slide.active .pill:nth-child(5) { animation-delay:320ms; }
.slide.active .pill:nth-child(6) { animation-delay:380ms; }

/* MARKET STRIP (3-col stat bar) */
.market-strip { display:grid; grid-template-columns:1fr 1fr 1fr; gap:1px; background:var(--border); border:1px solid var(--border); border-radius:6px; overflow:hidden; }
.market-cell { padding:18px 20px; background:var(--green-05); }
.slide.active .market-cell { animation: fadeScale 520ms var(--ease) both; }
.slide.active .market-cell:nth-child(1) { animation-delay:120ms; }
.slide.active .market-cell:nth-child(2) { animation-delay:220ms; }
.slide.active .market-cell:nth-child(3) { animation-delay:320ms; }
.market-cell .name { display:block; margin-bottom:8px; color:var(--muted); font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
.market-cell .share { color:var(--navy); font-size:30px; font-weight:700; }

/* STACKED BAR CHART */
.stacked { height:68px; display:flex; overflow:hidden; border:1px solid var(--border); border-radius:6px; background:var(--green-05); box-shadow:0 2px 6px rgba(21,43,71,.08); }
.segment { display:grid; place-items:center; transform-origin:left center; color:white; font-size:15px; font-weight:700; }
.slide.active .segment { animation: growBar 820ms var(--ease) both; }
.segment.aws { width:28%; background:var(--navy); }
.segment.ms  { width:21%; background:var(--green); }
.segment.google { width:15%; background:var(--emerald); }
.segment.other { width:36%; background:var(--green-20); color:var(--navy); }

/* LEGEND */
.legend { display:grid; gap:9px; }
.legend-item { display:flex; align-items:center; gap:10px; color:var(--muted); font-size:14px; font-weight:600; }
.swatch { width:18px; height:10px; border-radius:2px; background:var(--green); flex:0 0 auto; }
.swatch.aws { background:var(--navy); }
.swatch.ms  { background:var(--green); }
.swatch.google { background:var(--emerald); }
.swatch.other { background:var(--green-20); border:1px solid var(--border); }

/* IMPACT BARS (horizontal progress) */
.impact-bars { display:grid; gap:14px; }
.impact-bar { display:grid; grid-template-columns:82px 1fr; gap:14px; align-items:center; }
.impact-bar strong { color:var(--navy); font-size:30px; line-height:1; }
.bar-track { height:30px; overflow:hidden; border-radius:999px; background:var(--green-10); border:1px solid var(--green-20); }
.bar-fill { width:var(--w); height:100%; border-radius:inherit; background:linear-gradient(90deg, var(--green), var(--emerald)); transform-origin:left center; }
.bar-fill.ebit { background:linear-gradient(90deg, var(--navy), var(--blue-green)); }
.slide.active .bar-fill { animation: growBar 820ms var(--ease) 160ms both; }

/* LOGOS / WORDMARKS */
.asset-logo { display:block; width:92px; height:48px; background-position:left center; background-size:contain; background-repeat:no-repeat; flex:0 0 auto; }
.wordmark { min-height:64px; display:flex; align-items:center; gap:12px; color:var(--navy); font-size:19px; font-weight:800; }

/* PROVIDER CARDS */
.provider-grid { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:14px; }
.provider-card { min-height:240px; padding:20px; border:1px solid var(--border); border-radius:6px; background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); display:flex; flex-direction:column; justify-content:space-between; gap:18px; }
.provider-card.featured { border-color:rgba(0,125,54,.42); background:linear-gradient(180deg, rgba(242,247,242,.95), white); box-shadow:var(--shadow); }
.provider-tag { display:inline-flex; width:fit-content; padding:7px 10px; border-radius:999px; color:var(--green); background:var(--green-10); border:1px solid var(--green-20); font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:.06em; }

/* BIG MESSAGE BAND */
.big-message { padding:18px 22px; border-radius:6px; color:white; background:linear-gradient(135deg, var(--navy), var(--green)); font-size:22px; line-height:1.28; font-weight:700; box-shadow:var(--shadow); }

/* LOSS / PROBLEM HERO PANEL */
.loss-hero { min-height:420px; padding:30px; border-radius:6px; color:white; background: linear-gradient(135deg, rgba(21,43,71,.98), rgba(176,48,31,.84)), radial-gradient(circle at 86% 18%, rgba(255,255,255,.18), transparent 35%); box-shadow:var(--shadow); display:flex; flex-direction:column; justify-content:space-between; overflow:hidden; }
.loss-hero .label { color:rgba(255,255,255,.72); font-size:13px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }
.loss-hero strong { display:block; max-width:520px; margin:14px 0 18px; color:white; font-size:56px; line-height:1; }
.loss-hero p { color:rgba(255,255,255,.86); font-size:21px; line-height:1.34; }
.loss-hero .mini-note { margin-top:20px; padding:14px 16px; border-left:4px solid var(--pastel); color:rgba(255,255,255,.86); background:rgba(255,255,255,.08); font-size:15px; line-height:1.38; font-weight:600; }

/* LOSS ITEMS (problem list) */
.loss-list { display:grid; gap:12px; }
.loss-item { display:grid; grid-template-columns:8px 1fr; gap:14px; align-items:stretch; padding:16px 18px; background:var(--white); border:1px solid var(--border); border-radius:6px; box-shadow:0 2px 6px rgba(21,43,71,.08); }
.loss-item::before { content:""; display:block; background:#B0301F; border-radius:2px; }
.loss-item strong { display:block; margin-bottom:5px; color:var(--navy); font-size:18px; }
.loss-item span { color:var(--muted); font-size:16px; line-height:1.42; }
.slide.active .loss-item { animation: rise 480ms var(--ease) both; }
.slide.active .loss-item:nth-child(1) { animation-delay:90ms; }
.slide.active .loss-item:nth-child(2) { animation-delay:170ms; }
.slide.active .loss-item:nth-child(3) { animation-delay:250ms; }
.slide.active .loss-item:nth-child(4) { animation-delay:330ms; }

/* CHECK CARDS (interactive validation) */
.check-grid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:10px; }
.check-card { min-height:106px; display:grid; grid-template-columns:32px 1fr; gap:12px; align-items:start; padding:15px; border:1px solid var(--border); border-radius:6px; background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); cursor:pointer; text-align:left; font:inherit; }
.check-card:hover { border-color:rgba(0,125,54,.42); background:var(--green-05); }
.box { width:28px; height:28px; display:grid; place-items:center; border:2px solid var(--green-20); border-radius:6px; background:white; color:white; font-size:20px; font-weight:800; line-height:1; }
.check-card.checked .box { border-color:var(--green); background:var(--green); animation: checkPop 220ms var(--ease) both; }
.check-card.checked .box::before { content:""; width:8px; height:14px; border-right:3px solid white; border-bottom:3px solid white; transform:rotate(42deg) translateY(-1px); }
.check-card strong { display:block; margin-bottom:5px; color:var(--navy); font-size:16px; line-height:1.2; }
.check-card span { color:var(--muted); font-size:13px; line-height:1.28; font-weight:600; }
.check-card .suggestion { display:inline-flex; width:fit-content; margin-bottom:7px; padding:4px 8px; border-radius:999px; color:var(--green); background:var(--green-10); border:1px solid var(--green-20); font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.04em; }

/* TIMELINE */
.timeline { margin-top:16px; display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:1px; border:1px solid var(--border); border-radius:6px; overflow:hidden; background:var(--border); }
.phase { min-height:100px; padding:16px; background:var(--green-05); }
.phase strong { display:block; color:var(--green); font-size:22px; margin-bottom:6px; }
.phase span { color:var(--muted); font-size:14px; line-height:1.32; font-weight:600; }

/* ROADMAP PATH */
.path { display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:16px; position:relative; }
.path::before { content:""; position:absolute; left:9%; right:9%; top:50%; height:2px; background:var(--green-20); transform:translateY(-50%); transform-origin:left center; z-index:0; }
.slide.active .path::before { animation: growPath 900ms var(--ease) 210ms both; }
.step { position:relative; z-index:1; min-height:170px; padding:20px; border:1px solid var(--border); background:var(--white); border-radius:6px; box-shadow:0 2px 6px rgba(21,43,71,.08); }
.step .dot { width:18px; height:18px; border-radius:50%; border:3px solid var(--green); background:var(--white); margin-bottom:18px; }
.slide.active .step .dot { animation: pulseDot 1100ms var(--ease) 680ms 2; }

/* TRADEOFF / COMPARE CARDS */
.tradeoff-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.tradeoff-card { min-height:156px; padding:20px; border-radius:6px; border:1px solid var(--border); background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); }
.tradeoff-card.good { background:linear-gradient(180deg, var(--green-05), white); }
.tradeoff-card.watch { border-color:rgba(176,48,31,.28); background:linear-gradient(180deg, rgba(176,48,31,.06), white); }
.tradeoff-card.wide { grid-column:1 / -1; min-height:124px; }

/* FACT CARDS */
.market-facts { display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:14px; }
.fact-card { min-height:168px; padding:20px; border:1px solid var(--border); border-radius:6px; background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); }
.fact-card .metric { font-size:40px; margin-bottom:14px; }
.fact-card p { font-size:15px; line-height:1.36; }
.slide.active .fact-card { animation: fadeScale 520ms var(--ease) both; }

/* CHART CARDS (Chart.js wrapper) */
.chart-card { padding:22px; border:1px solid var(--border); border-radius:6px; background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); display:flex; flex-direction:column; gap:14px; }
.chart-card h3 { margin:0; }
.chart-wrap { position:relative; height:240px; }
.chart-wrap canvas { max-height:100%; }
.dark .chart-card { background:rgba(255,255,255,.08); border-color:rgba(255,255,255,.24); box-shadow:none; }
.dark .chart-card h3 { color:white; }
.dark .chart-card .source-note { color:rgba(255,255,255,.7); }
.dark .chart-card .source-note a { color:var(--pastel); }

/* WORLD MAP (jsvectormap wrapper) */
.world-map { width:100%; height:340px; }
.jvm-tooltip { background:var(--navy) !important; color:white !important; padding:8px 12px !important; border-radius:6px !important; font:600 13px Raleway, sans-serif !important; box-shadow:var(--shadow) !important; }

/* SERVICE CHIPS */
.service-cloud { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:12px; }
.service-chip { min-height:84px; padding:14px 16px; border-radius:6px; border:1px solid var(--border); background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); }
.service-chip strong { display:block; color:var(--navy); font-size:18px; margin-bottom:6px; }
.service-chip.primary { color:white; background:linear-gradient(135deg, var(--navy), var(--green)); border-color:transparent; box-shadow:var(--shadow); }
.service-chip.primary strong, .service-chip.primary span { color:white; }

/* BRICK WALL (3-col feature grid) */
.brick-wall { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:12px; }
.brick { min-height:92px; padding:16px; border-radius:6px; color:white; background:linear-gradient(135deg, var(--navy), var(--blue-green)); box-shadow:0 2px 6px rgba(21,43,71,.12); }
.brick:nth-child(2n) { background:linear-gradient(135deg, var(--green), var(--emerald)); }
.brick strong { display:block; margin-bottom:7px; font-size:17px; }
.brick span { color:rgba(255,255,255,.82); font-size:13px; line-height:1.28; font-weight:600; }
.slide.active .brick { animation: fadeScale 520ms var(--ease) both; }

/* READINESS RAIL */
.readiness-rail { display:grid; grid-template-columns:repeat(5, minmax(0, 1fr)); gap:8px; margin-top:18px; }
.readiness-rail span { min-height:54px; display:grid; place-items:center; padding:10px; border-radius:6px; color:var(--navy); background:var(--green-10); border:1px solid var(--green-20); font-size:13px; line-height:1.18; font-weight:800; text-align:center; }
.readiness-rail span.on { color:white; background:linear-gradient(135deg, var(--navy), var(--green)); border-color:transparent; }
.slide.active .readiness-rail span { animation: fadeScale 520ms var(--ease) both; }

/* MINI TABLE */
.mini-table { display:grid; grid-template-columns:.85fr 1.15fr; border:1px solid var(--border); border-radius:6px; overflow:hidden; background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); }
.mini-table > div { padding:15px 18px; border-bottom:1px solid var(--border); font-size:17px; line-height:1.36; }
.mini-table > div:nth-child(odd) { font-weight:700; color:var(--navy); background:var(--green-05); }
.mini-table > div:nth-last-child(-n+2) { border-bottom:0; }
.slide.active .mini-table > div { animation: rise 480ms var(--ease) both; }

/* COST BAND (dark 3-col) */
.cost-band { display:grid; grid-template-columns:repeat(3, 1fr); gap:18px; }
.cost { padding:24px; border:1px solid rgba(255,255,255,.28); border-radius:6px; background:rgba(255,255,255,.08); }
.cost .metric { color:var(--pastel); }

/* FOOTER */
.footer { position:relative; z-index:2; display:flex; align-items:end; justify-content:space-between; gap:20px; color:var(--subtle); font-size:12px; line-height:1.36; }
.dark .footer, .cover .footer { color:rgba(255,255,255,.72); }
.sources { max-width:920px; }

/* PROGRESS DOTS */
.progress { display:grid; grid-auto-flow:column; grid-auto-columns:28px; gap:5px; flex:0 0 auto; }
.progress span { display:block; height:4px; background:var(--green-20); }
.progress span.on { background:var(--green); }
.dark .progress span, .cover .progress span { background:rgba(255,255,255,.28); }
.dark .progress span.on, .cover .progress span.on { background:var(--pastel); }

/* NAV BUTTONS */
.nav { position:fixed; right:24px; bottom:18px; z-index:20; display:flex; gap:8px; }
.nav button { width:42px; height:38px; border:1px solid rgba(255,255,255,.28); border-radius:6px; background:rgba(21,43,71,.92); color:white; cursor:pointer; font-size:0; }
.nav button::before { content:""; display:inline-block; width:10px; height:10px; border-top:2px solid white; border-left:2px solid white; }
#prev::before { transform:rotate(-45deg); }
#next::before { transform:rotate(135deg); }

/* === 21st.dev — MARQUEE === */
.marquee { width:100%; overflow:hidden; padding:24px 0; mask-image:linear-gradient(90deg, transparent, black 8%, black 92%, transparent); -webkit-mask-image:linear-gradient(90deg, transparent, black 8%, black 92%, transparent); }
.marquee-track { display:flex; gap:48px; width:max-content; animation:marqueeScroll 28s linear infinite; }
.marquee:hover .marquee-track { animation-play-state:paused; }
.marquee-logo { width:120px; height:48px; flex:0 0 auto; background-position:center; background-size:contain; background-repeat:no-repeat; opacity:.78; transition:opacity 220ms var(--ease); filter:grayscale(.2); }
.marquee-logo:hover { opacity:1; filter:grayscale(0); }
@keyframes marqueeScroll { from { transform:translateX(0); } to { transform:translateX(-50%); } }

/* === 21st.dev — BENTO GRID === */
.bento { display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); grid-auto-rows:130px; gap:14px; }
.bento-cell { padding:20px; border:1px solid var(--border); border-radius:8px; background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); display:flex; flex-direction:column; justify-content:space-between; gap:8px; overflow:hidden; position:relative; transition:transform 220ms var(--ease), box-shadow 220ms var(--ease); }
.bento-cell:hover { transform:translateY(-2px); box-shadow:var(--shadow); }
.bento-cell.big { grid-column:span 2; grid-row:span 2; }
.bento-cell.tall { grid-row:span 2; }
.bento-cell.wide { grid-column:span 2; }
.bento-cell.green { background:linear-gradient(135deg, var(--green-10), var(--green-05)); border-color:var(--green-20); }
.bento-cell.dark { background:linear-gradient(135deg, var(--navy), var(--blue-green)); color:white; border-color:transparent; }
.bento-cell.dark h3, .bento-cell.dark p { color:white; }
.bento-cell .metric.pastel { color:var(--pastel); }
.slide.active .bento-cell { animation:fadeScale 520ms var(--ease) both; }
.slide.active .bento-cell:nth-child(1) { animation-delay:90ms; }
.slide.active .bento-cell:nth-child(2) { animation-delay:170ms; }
.slide.active .bento-cell:nth-child(3) { animation-delay:240ms; }
.slide.active .bento-cell:nth-child(4) { animation-delay:310ms; }
.slide.active .bento-cell:nth-child(5) { animation-delay:380ms; }

/* === 21st.dev — ANIMATED SHINY TEXT === */
.shiny-text { background:linear-gradient(110deg, currentColor 30%, rgba(255,255,255,.95) 45%, currentColor 60%); background-size:250% 100%; -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; color:white; animation:shinySweep 3.2s linear infinite; }
.shiny-text.dark-bg { color:var(--navy); background:linear-gradient(110deg, var(--navy) 30%, var(--green) 45%, var(--navy) 60%); background-size:250% 100%; -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
@keyframes shinySweep { 0% { background-position:200% 0; } 100% { background-position:-100% 0; } }

/* === 21st.dev — SPOTLIGHT CARD (mouse-following radial) === */
.spotlight-card { --mx:50%; --my:50%; position:relative; padding:24px; border:1px solid rgba(255,255,255,.18); border-radius:8px; background:rgba(255,255,255,.04); color:white; overflow:hidden; transition:border-color 220ms var(--ease); }
.spotlight-card::before { content:""; position:absolute; inset:0; background:radial-gradient(420px circle at var(--mx) var(--my), rgba(140,202,174,.22), transparent 45%); pointer-events:none; transition:opacity 220ms var(--ease); }
.spotlight-card:hover { border-color:rgba(140,202,174,.5); }
.spotlight-card h3, .spotlight-card p { color:white; position:relative; }

/* === LOTTIE ICONS === */
.lottie-icon { width:56px; height:56px; flex:0 0 auto; }
.fact-card .lottie-icon { margin-bottom:8px; }

/* === TS PARTICLES === */
#tsparticles { position:absolute; inset:0; z-index:0; pointer-events:none; }
.cover.particles .body, .cover.particles .brand, .cover.particles .footer, .cover.particles .globe { position:relative; z-index:2; }

/* === PRESENTER MODE === */
.notes { display:none; }

.overview-grid { position:fixed; inset:0; z-index:50; display:none; padding:32px 48px; background:rgba(21,43,71,.96); overflow:auto; }
.overview-grid.active { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:18px; align-content:start; animation:fadeScale 240ms var(--ease) both; }
.overview-thumb { aspect-ratio:16/10; padding:14px; border:1px solid rgba(255,255,255,.18); border-radius:6px; background:white; color:var(--navy); cursor:pointer; overflow:hidden; transition:transform 200ms var(--ease), border-color 200ms var(--ease); display:flex; flex-direction:column; gap:6px; font-family:inherit; text-align:left; }
.overview-thumb:hover { transform:translateY(-2px); border-color:var(--pastel); }
.overview-thumb.current { border-color:var(--green); border-width:2px; }
.overview-thumb .num { color:var(--green); font-size:11px; font-weight:800; letter-spacing:.1em; }
.overview-thumb .title { font-size:13px; font-weight:700; line-height:1.3; color:var(--navy); }
.overview-thumb .preview { flex:1; font-size:10px; line-height:1.3; color:var(--muted); overflow:hidden; }

.shortcuts-modal { position:fixed; inset:0; z-index:51; display:none; place-items:center; padding:24px; background:rgba(21,43,71,.86); }
.shortcuts-modal.active { display:grid; animation:fadeScale 240ms var(--ease) both; }
.shortcuts-modal .panel { max-width:480px; width:100%; padding:28px; border-radius:8px; background:white; box-shadow:var(--shadow); }
.shortcuts-modal h3 { color:var(--navy); margin-bottom:16px; }
.shortcuts-modal dl { display:grid; grid-template-columns:auto 1fr; gap:10px 18px; margin:0; }
.shortcuts-modal dt { font-family:"SFMono-Regular", Consolas, monospace; padding:2px 8px; border-radius:4px; background:var(--green-10); border:1px solid var(--green-20); color:var(--green); font-size:13px; font-weight:700; justify-self:start; }
.shortcuts-modal dd { margin:0; color:var(--muted); font-size:14px; line-height:1.4; }

.notes-overlay { position:fixed; left:24px; right:24px; bottom:78px; z-index:40; display:none; padding:18px 22px; border-radius:8px; background:rgba(21,43,71,.96); color:white; box-shadow:var(--shadow); max-width:880px; margin:0 auto; }
.notes-overlay.active { display:block; animation:rise 240ms var(--ease) both; }
.notes-overlay .label { display:block; margin-bottom:8px; color:var(--pastel); font-size:11px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.notes-overlay .content { font-size:15px; line-height:1.5; color:rgba(255,255,255,.92); }

.timer-display { position:fixed; left:24px; bottom:18px; z-index:30; display:none; padding:8px 14px; border-radius:6px; background:rgba(21,43,71,.92); color:white; font:700 14px "SFMono-Regular", Consolas, monospace; border:1px solid rgba(255,255,255,.18); }
.timer-display.active { display:inline-flex; }
.timer-display.paused { background:rgba(176,48,31,.92); }

/* TABS (interactive) */
.tab-slide { display:flex; flex-direction:column; gap:18px; }
.tabs { display:flex; gap:6px; border-bottom:1px solid var(--border); }
.tab { padding:12px 20px; border:none; background:transparent; color:var(--muted); font:600 15px Raleway, sans-serif; cursor:pointer; border-bottom:3px solid transparent; transition:color 200ms var(--ease), border-color 200ms var(--ease); }
.tab:hover { color:var(--green); }
.tab.active { color:var(--green); border-bottom-color:var(--green); }
.tab-panels { position:relative; min-height:240px; }
.panel { display:none; }
.panel.active { display:block; animation:fadeScale 320ms var(--ease) both; }
.dark .tab { color:rgba(255,255,255,.7); }
.dark .tab:hover, .dark .tab.active { color:var(--pastel); }
.dark .tab.active { border-bottom-color:var(--pastel); }
.dark .tabs { border-bottom-color:rgba(255,255,255,.18); }

/* ACCORDION */
.accordion { display:grid; gap:8px; }
.accordion > div { display:flex; flex-direction:column; }
.acc-trigger { display:flex; justify-content:space-between; align-items:center; width:100%; padding:14px 18px; border:1px solid var(--border); border-radius:6px; background:var(--white); color:var(--navy); font:700 16px Raleway, sans-serif; cursor:pointer; text-align:left; transition:border-color 200ms var(--ease), background 200ms var(--ease); }
.acc-trigger:hover { border-color:var(--green); background:var(--green-05); }
.acc-trigger::after { content:""; flex:0 0 auto; width:10px; height:10px; border-right:2px solid var(--green); border-bottom:2px solid var(--green); transform:rotate(45deg); transition:transform 220ms var(--ease); margin-left:14px; }
.acc-trigger[aria-expanded="true"]::after { transform:rotate(-135deg); }
.acc-panel { padding:14px 18px; border:1px solid var(--border); border-top:none; border-radius:0 0 6px 6px; background:var(--green-05); color:var(--muted); font-size:15px; line-height:1.5; animation:rise 280ms var(--ease) both; }
.acc-trigger[aria-expanded="true"] { border-radius:6px 6px 0 0; border-bottom-color:transparent; }

/* HOVER-REVEAL CARDS */
.card.reveal { position:relative; overflow:hidden; cursor:pointer; }
.card.reveal .reveal-back { position:absolute; inset:0; padding:22px; background:linear-gradient(135deg, var(--navy), var(--green)); color:white; transform:translateY(100%); transition:transform 320ms var(--ease); display:flex; flex-direction:column; justify-content:center; gap:10px; }
.card.reveal:hover .reveal-back, .card.reveal:focus-within .reveal-back { transform:translateY(0); }
.card.reveal .reveal-back h3, .card.reveal .reveal-back p { color:white; }
.card.reveal::after { content:"+"; position:absolute; top:14px; right:16px; width:24px; height:24px; border-radius:50%; background:var(--green); color:white; display:grid; place-items:center; font-weight:700; font-size:18px; line-height:1; transition:transform 220ms var(--ease); z-index:2; }
.card.reveal:hover::after { transform:rotate(45deg); background:white; color:var(--green); }

/* TOOLTIPS */
.has-tooltip { position:relative; border-bottom:1px dotted var(--green); cursor:help; outline:none; }
.has-tooltip:focus-visible { outline:2px solid var(--green); outline-offset:2px; border-radius:2px; }
.has-tooltip::after { content:attr(data-tooltip); position:absolute; bottom:calc(100% + 10px); left:50%; transform:translateX(-50%) translateY(4px); padding:10px 14px; min-width:180px; max-width:300px; background:var(--navy); color:white; font-size:13px; line-height:1.42; font-weight:500; border-radius:6px; box-shadow:var(--shadow); opacity:0; visibility:hidden; transition:opacity 200ms var(--ease), visibility 200ms var(--ease), transform 200ms var(--ease); pointer-events:none; z-index:30; white-space:normal; text-align:left; }
.has-tooltip::before { content:""; position:absolute; bottom:calc(100% + 4px); left:50%; transform:translateX(-50%); border:6px solid transparent; border-top-color:var(--navy); opacity:0; transition:opacity 200ms var(--ease); pointer-events:none; z-index:30; }
.has-tooltip:hover::after, .has-tooltip:focus::after { opacity:1; visibility:visible; transform:translateX(-50%) translateY(0); }
.has-tooltip:hover::before, .has-tooltip:focus::before { opacity:1; }

/* RESPONSIVE */
@media (max-width: 980px) {
  body { overflow: auto; }
  .deck { height: auto; min-height: 100vh; }
  .slide { position:relative; min-height:100vh; height:auto; padding:30px 22px 44px; overflow:visible; }
  .slide.active { display: block; }
  h1 { font-size:38px; } h2 { font-size:30px; } p, li { font-size:16px; } .lead { font-size:18px; }
  .grid, .market-facts, .market-strip, .brick-wall, .provider-grid, .check-grid,
  .tradeoff-grid, .path, .timeline, .cost-band, .service-cloud { grid-template-columns: 1fr; }
  .tabs { flex-wrap:wrap; }
  .chart-wrap { height:200px; }
  .world-map { height:240px; }
  .bento { grid-template-columns:1fr; grid-auto-rows:auto; }
  .bento-cell.big, .bento-cell.tall, .bento-cell.wide { grid-column:auto; grid-row:auto; }
  .marquee-logo { width:90px; height:38px; }
  .overview-grid { padding:18px; }
  .overview-grid.active { grid-template-columns:repeat(2, 1fr); }
  .path::before { display:none; }
  .globe { opacity:.25; right:16px; bottom:40px; width:150px; height:150px; }
  .footer { margin-top:24px; }
  .nav { display:none; }
}

@media print {
  body { overflow:visible; background:white; }
  .slide { display:grid !important; position:relative; min-height:100vh; page-break-after:always; }
  .nav { display:none; }
}
```

---

## Navigation JavaScript (always include at end of `<body>`)

```javascript
const slides = Array.from(document.querySelectorAll('.slide'));
const progressBlocks = Array.from(document.querySelectorAll('.progress'));
const initialSlide = Number.parseInt(new URLSearchParams(window.location.search).get('slide') || '1', 10);
let current = Number.isFinite(initialSlide) ? initialSlide - 1 : 0;

function renderProgress() {
  progressBlocks.forEach((block) => {
    block.innerHTML = '';
    slides.forEach((_, index) => {
      const segment = document.createElement('span');
      if (index <= current) segment.classList.add('on');
      block.appendChild(segment);
    });
  });
}

function show(index) {
  current = Math.max(0, Math.min(slides.length - 1, index));
  slides.forEach((slide, i) => { slide.classList.toggle('active', i === current); });
  renderProgress();
  document.title = `${DECK_TITLE} - ${current + 1}/${slides.length}`;
}

document.getElementById('prev').addEventListener('click', () => show(current - 1));
document.getElementById('next').addEventListener('click', () => show(current + 1));

document.querySelectorAll('.check-card').forEach((card) => {
  card.addEventListener('click', () => {
    const isChecked = card.classList.toggle('checked');
    card.setAttribute('aria-pressed', String(isChecked));
  });
});

document.addEventListener('keydown', (event) => {
  if (event.target.closest && event.target.closest('.check-card')) return;
  if (['ArrowRight', 'PageDown', ' '].includes(event.key)) { event.preventDefault(); show(current + 1); }
  if (['ArrowLeft', 'PageUp'].includes(event.key)) { event.preventDefault(); show(current - 1); }
  if (event.key === 'Home') show(0);
  if (event.key === 'End') show(slides.length - 1);
});

show(current);
```
