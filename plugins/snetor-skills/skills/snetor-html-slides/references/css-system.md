# Snetor HTML Slides — CSS Design System

This file contains the full CSS and design tokens for Snetor-branded HTML presentations.
Always include this CSS verbatim in generated slides (inside a `<style>` tag in `<head>`).
Adapt only the `--logo`, `--logo-reversed`, `--hero` and provider logo paths
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

## Échelle typographique (charte Snetor — Brand Book p. 29-30)

Police unique : **Raleway**. Quatre graisses seulement, celles qui sont réellement chargées :

| Poids | Graisse Raleway | Rôle | Exemples |
|---|---|---|---|
| `400` | Regular | corps de texte | `p`, `li`, `.sources`, captions |
| `500` | Medium | sous-titres | `.lead`, `.sd-sub` |
| `600` | SemiBold | titres | `h1`, `h2`, `.statement`, `.closing-title`, `.sd-title`, `blockquote` |
| `700` | Bold | accents, micro-labels, chiffres | `h3`, `.eyebrow`, `.metric`, `.pill`, `.g-head`, `.annex-tag`… |

**Règle dure : aucun `font-weight` en dehors de `400 / 500 / 600 / 700`.**
Un `font-weight:800` (ExtraBold) ou `900` (Black) n'est pas chargé — ni par le `<link>` Google Fonts
(`wght@400;500;600;700`), ni par les quatre `@font-face` du mode stand-alone. Le navigateur retombe
alors sur le 700 et lui applique un **gras synthétique** : les glyphes sont épaissis par le moteur de
rendu, pas dessinés par le typographe. Ce n'est plus du Raleway. Si un ExtraBold est un jour
nécessaire, il faut d'abord ajouter `800` à l'URL Google Fonts **et** livrer `Raleway-ExtraBold.ttf`
dans `assets/fonts/` — jamais déclarer le poids seul.

Couleur du texte : **navy `#152B47`**, jamais du noir (règle de charte). Aucun `#000` dans le
système ; `--muted` / `--subtle` sont des dérivés navy pour le texte secondaire.

---

## Deck Themes

Set the theme on `<main class="deck ...">`:
- `theme-light` (default — may be omitted) — unchanged base styling.
- `theme-dark` — every content slide dark by default. Use the **dark-safe** component palette (`.dark-card`, `.cost`, `.chart-card`, `.brick`, `.foundation`, `.ph-icon`, `.tab`, `.spotlight-card`, `.big-message`, + archetypes). Light-card components are meant for light slides.

Per-slide accent (rhythm): add `dark` to a slide in a light deck, or `light` to a slide in a dark deck. `.light` opts the slide out of `theme-dark` back to the light styling.

### Lisibilité sur fond foncé — l'invariant des deux chemins

Trois surfaces sont foncées : `.cover`, une slide d'accent `.dark` dans un deck
clair, et une slide de contenu d'un deck `theme-dark`. **Toute règle de couleur
écrite pour l'une doit être écrite pour les autres**, dans la couche
« COUCHE FONCÉE COMMUNE » du bloc CSS, avec les deux sélecteurs sur la même
règle. La couche `theme-dark` a été créée par duplication de la cascade `.dark`,
et les règles ajoutées ensuite ne sont parties que d'un côté : `.statement
strong` restait en `--green` `#007D36` sur navy, soit **2,11:1**, sous le
plancher WCAG AA de 3:1 en gros texte. Invisible en séance.

Seuls les composants dont le texte se pose **à même le fond de slide** ont
besoin d'une variante foncée. Un composant qui porte son propre fond clair
(`card`, `check-card`, `chart-card`, `agenda-item`, `brick`, `mini-table`,
`market-cell`, `readiness-rail`, `pill`, `provider-tag`) n'en a pas besoin :
son backdrop n'est pas le dégradé.

⚠️ **`step` est l'exception qui prouve la règle.** Il porte bien une carte
blanche, mais il ne redéclare pas la couleur de son texte, contrairement à
`card` qui a sa variante `dark-card`. Sur une slide d'accent, son `h3` et son
`p` héritaient donc du `color:white` de la cascade foncée : blanc sur blanc, la
slide paraissait vide à l'écran. Sa variante est désormais dans la couche
commune. Porter son propre fond ne suffit pas — **il faut aussi porter sa
couleur de texte.**

Correspondances à respecter quand un nouveau composant arrive :

| Sur fond clair | Sur fond foncé |
|---|---|
| `var(--navy)` (titre, valeur) | `white` |
| `var(--muted)` (corps, légende) | `rgba(255,255,255,.78)` |
| `var(--subtle)` (caption, en-tête de colonne) | `rgba(255,255,255,.72)` à `.78` |
| `var(--green)` (accent, lien, icône) | `var(--pastel)` |
| `var(--border)` (filet) | `rgba(255,255,255,.24)` |

Le blanc est le plafond : quand un texte blanc ne passe toujours pas, ce n'est
plus un problème de palette mais de fond — c'est le cas de l'en-tête de cover,
traité par un voile navy et documenté à sa règle.

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
  --hero: url("../assets/DECK_NAME/Hero-banner-abstrait.jpg");
  --shapes: url("../assets/DECK_NAME/snetor_shapes.png");
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
/* Voile de l'en-tête de cover. La cover est le SEUL fond dont le dégradé est en
   90deg : le vert #007D36 court le long de tout le bord droit, là où se pose le
   texte méta de l'en-tête (blanc 16px). Mesuré sans voile : 4,07:1, sous le
   plancher WCAG AA de 4,5 — et le blanc est déjà la couleur de contraste
   maximal, donc aucune règle de couleur ne peut le corriger. Le voile ramène le
   fond sous l'en-tête à 4,90:1. Une slide d'accent `.dark` n'en a pas besoin :
   son dégradé est en 135deg, le vert n'atteint que le coin bas-droit, et son
   en-tête mesure 6,36:1. z-index 1 : au-dessus du fond, sous `.brand` (z-index 2). */
.cover::before {
  content:""; position:absolute; inset:0 0 auto 0; height:108px; z-index:1; pointer-events:none;
  background:linear-gradient(180deg, rgba(21,43,71,.40), rgba(21,43,71,0));
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
.lead { max-width:850px; font-size:22px; line-height:1.45; font-weight:500; color:rgba(255,255,255,.84); margin-top:20px; }
.hero-line { width:172px; height:4px; background:linear-gradient(90deg, var(--pastel), var(--white)); margin-top:34px; transform-origin:left center; }
.slide.active .hero-line { animation: growLine 720ms var(--ease) 360ms both; }

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
.wordmark { min-height:64px; display:flex; align-items:center; gap:12px; color:var(--navy); font-size:19px; font-weight:700; }

/* PROVIDER CARDS */
.provider-grid { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:14px; }
.provider-card { min-height:240px; padding:20px; border:1px solid var(--border); border-radius:6px; background:var(--white); box-shadow:0 2px 6px rgba(21,43,71,.08); display:flex; flex-direction:column; justify-content:space-between; gap:18px; }
.provider-card.featured { border-color:rgba(0,125,54,.42); background:linear-gradient(180deg, rgba(242,247,242,.95), white); box-shadow:var(--shadow); }
.provider-tag { display:inline-flex; width:fit-content; padding:7px 10px; border-radius:999px; color:var(--green); background:var(--green-10); border:1px solid var(--green-20); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }

/* BIG MESSAGE BAND */
.big-message { padding:18px 22px; border-radius:6px; color:white; background:linear-gradient(135deg, var(--navy), var(--green)); font-size:22px; line-height:1.28; font-weight:700; box-shadow:var(--shadow); }

/* LOSS / PROBLEM HERO PANEL */
.loss-hero { min-height:420px; padding:30px; border-radius:6px; color:white; background: linear-gradient(135deg, rgba(21,43,71,.98), rgba(176,48,31,.84)), radial-gradient(circle at 86% 18%, rgba(255,255,255,.18), transparent 35%); box-shadow:var(--shadow); display:flex; flex-direction:column; justify-content:space-between; overflow:hidden; }
.loss-hero .label { color:rgba(255,255,255,.72); font-size:13px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
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
.box { width:28px; height:28px; display:grid; place-items:center; border:2px solid var(--green-20); border-radius:6px; background:white; color:white; font-size:20px; font-weight:700; line-height:1; }
.check-card.checked .box { border-color:var(--green); background:var(--green); animation: checkPop 220ms var(--ease) both; }
.check-card.checked .box::before { content:""; width:8px; height:14px; border-right:3px solid white; border-bottom:3px solid white; transform:rotate(42deg) translateY(-1px); }
.check-card strong { display:block; margin-bottom:5px; color:var(--navy); font-size:16px; line-height:1.2; }
.check-card span { color:var(--muted); font-size:13px; line-height:1.28; font-weight:600; }
.check-card .suggestion { display:inline-flex; width:fit-content; margin-bottom:7px; padding:4px 8px; border-radius:999px; color:var(--green); background:var(--green-10); border:1px solid var(--green-20); font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.04em; }

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
.readiness-rail span { min-height:54px; display:grid; place-items:center; padding:10px; border-radius:6px; color:var(--navy); background:var(--green-10); border:1px solid var(--green-20); font-size:13px; line-height:1.18; font-weight:700; text-align:center; }
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

/* === 21st.dev — SPOTLIGHT CARD (mouse-following radial) === */
.spotlight-card { --mx:50%; --my:50%; position:relative; padding:24px; border:1px solid rgba(255,255,255,.18); border-radius:8px; background:rgba(255,255,255,.04); color:white; overflow:hidden; transition:border-color 220ms var(--ease); }
.spotlight-card::before { content:""; position:absolute; inset:0; background:radial-gradient(420px circle at var(--mx) var(--my), rgba(140,202,174,.22), transparent 45%); pointer-events:none; transition:opacity 220ms var(--ease); }
.spotlight-card:hover { border-color:rgba(140,202,174,.5); }
.spotlight-card h3, .spotlight-card p { color:white; position:relative; }

/* === PHOSPHOR ICONS (Snetor sizing/color override) ===
   Default tone = green. Variants: .navy (dark blue), .teal (blue-green/emerald).
   Mix tones across a deck to add visual rhythm — e.g. green for growth/finance,
   navy for security/risk, teal for tech/AI. */
.ph-icon { display:inline-flex; align-items:center; justify-content:center; width:48px; height:48px; font-size:32px; color:var(--green); background:var(--green-10); border:1px solid var(--green-20); border-radius:12px; flex:0 0 auto; }
.ph-icon.large { width:56px; height:56px; font-size:38px; }
.ph-icon.navy { color:var(--navy); background:rgba(21,43,71,.08); border-color:rgba(21,43,71,.18); }
.ph-icon.teal { color:var(--blue-green); background:rgba(42,84,88,.08); border-color:rgba(42,84,88,.20); }
.dark .ph-icon, .cover .ph-icon { color:var(--pastel); background:rgba(255,255,255,.08); border-color:rgba(255,255,255,.18); }
.dark .ph-icon.navy, .cover .ph-icon.navy { color:var(--white); background:rgba(255,255,255,.10); border-color:rgba(255,255,255,.22); }
.fact-card .ph-icon { margin-bottom:8px; }
.bento-cell .ph-icon { width:36px; height:36px; font-size:22px; border-radius:8px; }

/* === PRESENTER MODE === */
.notes { display:none; }

.overview-grid { position:fixed; inset:0; z-index:50; display:none; padding:32px 48px; background:rgba(21,43,71,.96); overflow:auto; }
.overview-grid.active { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:18px; align-content:start; animation:fadeScale 240ms var(--ease) both; }
.overview-thumb { aspect-ratio:16/10; padding:14px; border:1px solid rgba(255,255,255,.18); border-radius:6px; background:white; color:var(--navy); cursor:pointer; overflow:hidden; transition:transform 200ms var(--ease), border-color 200ms var(--ease); display:flex; flex-direction:column; gap:6px; font-family:inherit; text-align:left; }
.overview-thumb:hover { transform:translateY(-2px); border-color:var(--pastel); }
.overview-thumb.current { border-color:var(--green); border-width:2px; }
.overview-thumb .num { color:var(--green); font-size:11px; font-weight:700; letter-spacing:.1em; }
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
.notes-overlay .label { display:block; margin-bottom:8px; color:var(--pastel); font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
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

/* === TWO-COLUMN HELPERS === */
.two-col { display:grid; gap:24px; align-items:start; }
.two-col.left-wide { grid-template-columns:1.35fr .65fr; }
.two-col.even { grid-template-columns:1fr 1fr; }

/* === METHOD FLOW (icon nodes on a connected line) ===
   Richer alternative to the 4-step .path for a "how it works / method" slide.
   Big circular Phosphor icons over an animated connector. */
.flow { display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:18px; position:relative; }
.flow::before { content:""; position:absolute; left:11%; right:11%; top:38px; height:2px; background:var(--green-20); transform-origin:left center; z-index:0; }
.slide.active .flow::before { animation: growLine 900ms var(--ease) 220ms both; }
.flow-node { position:relative; z-index:1; text-align:center; padding:0 6px; }
.flow-node .ph-icon { margin:0 auto 14px; width:76px; height:76px; font-size:40px; border-radius:50%; box-shadow:0 6px 18px rgba(21,43,71,.10); background:var(--white); }
.flow-node h3 { font-size:18px; margin-bottom:6px; }
.flow-node p { font-size:14px; line-height:1.4; }
.slide.active .flow-node { animation: rise 560ms var(--ease) both; }
.slide.active .flow-node:nth-child(1){animation-delay:120ms}
.slide.active .flow-node:nth-child(2){animation-delay:230ms}
.slide.active .flow-node:nth-child(3){animation-delay:340ms}
.slide.active .flow-node:nth-child(4){animation-delay:450ms}

/* === CATEGORY LEGEND (counts with colored dots) ===
   Pairs well with a Chart.js bubble matrix. Dot colors match the matrix categories. */
.cat-legend { display:grid; gap:12px; }
.cat-row { display:grid; grid-template-columns:auto 1fr; gap:12px; align-items:center; }
.cat-dot { width:18px; height:18px; border-radius:50%; flex:0 0 auto; box-shadow:0 0 0 4px rgba(0,0,0,.04); }
.cat-dot.qw { background:var(--green); } .cat-dot.ps { background:var(--navy); } .cat-dot.exp { background:var(--blue-green); } .cat-dot.ac { background:#b43232; }
.cat-row .n { color:var(--navy); font-weight:700; font-size:22px; line-height:1; }
.cat-row .l { color:var(--muted); font-size:13px; font-weight:600; }

/* === PRODUCT PREVIEW CARDS (clickable, with screenshot) ===
   For a product / app portfolio slide. Each card shows a screenshot thumbnail that
   zooms on hover, a tag, a title, a one-liner and a status/CTA. Wrap in an <a> for live links.
   Use 3 cards (cols-3, default) or set grid-template-columns:repeat(4,...) inline for 4. */
.product-grid { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:16px; }
.product-card { display:flex; flex-direction:column; border:1px solid var(--border); border-radius:12px; overflow:hidden; background:#fff; box-shadow:0 2px 8px rgba(21,43,71,.08); text-decoration:none; transition:transform .24s var(--ease), box-shadow .24s var(--ease); }
.product-card:hover { transform:translateY(-5px); box-shadow:var(--shadow); }
.product-card .shot-wrap { height:152px; overflow:hidden; background:var(--navy); position:relative; }
.product-card .shot { width:100%; height:100%; object-fit:cover; object-position:top center; transition:transform .5s var(--ease); display:block; }
.product-card:hover .shot { transform:scale(1.06); }
.product-card .shot-wrap::after { content:""; position:absolute; inset:0; background:linear-gradient(180deg, transparent 60%, rgba(21,43,71,.18)); }
.product-card .pbody { padding:14px 16px 16px; display:flex; flex-direction:column; gap:6px; }
.product-card .ptag { display:inline-flex; align-items:center; gap:8px; color:var(--green); font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.product-card .pbody strong { color:var(--navy); font-size:18px; }
.product-card .pbody p { font-size:13px; line-height:1.4; color:var(--muted); }
.product-card .open { margin-top:2px; color:var(--green); font-weight:700; font-size:13px; display:inline-flex; align-items:center; gap:6px; }
.slide.active .product-card { animation: fadeScale 560ms var(--ease) both; }
.slide.active .product-card:nth-child(1){animation-delay:200ms}
.slide.active .product-card:nth-child(2){animation-delay:300ms}
.slide.active .product-card:nth-child(3){animation-delay:400ms}
.slide.active .product-card:nth-child(4){animation-delay:480ms}

/* === FOUNDATION STRIP (full-width gradient base band) ===
   For a "the common foundation / platform everything sits on" band, typically placed
   below a product grid. Holds an icon, a short text block, and 1-3 logo chips. */
.foundation { position:relative; padding:20px 26px; border-radius:12px; color:#fff; overflow:hidden;
  background:linear-gradient(120deg, var(--navy), var(--blue-green) 62%, var(--green)); box-shadow:var(--shadow);
  display:flex; align-items:center; gap:20px; }
.foundation::after { content:""; position:absolute; right:-40px; top:-30px; width:360px; height:200px; background:var(--shapes) right center / contain no-repeat; opacity:.16; pointer-events:none; }
.foundation .ph-icon { background:rgba(255,255,255,.12); border-color:rgba(255,255,255,.22); color:#fff; }
.foundation .f-txt { position:relative; z-index:1; }
.foundation .f-txt .eyebrow { color:var(--pastel); margin-bottom:6px; }
.foundation .f-txt .eyebrow::before { background:var(--pastel); }
.foundation .f-txt strong { display:block; font-size:21px; margin-bottom:4px; color:#fff; }
.foundation .f-txt p { color:rgba(255,255,255,.85); font-size:14px; line-height:1.4; max-width:640px; }
.foundation .f-logos { position:relative; z-index:1; margin-left:auto; display:flex; gap:10px; flex:0 0 auto; }
.foundation .f-logos .chip { width:58px; height:44px; border-radius:8px; background:#fff center / 38px no-repeat; box-shadow:0 4px 10px rgba(0,0,0,.18); }

/* === GANTT (roadmap timeline) ===
   Grid-based Gantt for a roadmap slide. Column 1 = labels, columns 2..N = time buckets.
   Place each label and bar with explicit grid-row; place bars across time with grid-column:start/end.
   Bar status: .done (green), .prog (navy), .plan (hatched). Optional .g-today dashed "now" line. */
.gantt { display:grid; grid-template-columns:190px repeat(7, 1fr); gap:9px 6px; position:relative; align-items:center; }
.gantt .g-corner { grid-column:1; grid-row:1; }
.gantt .g-head { grid-row:1; font-size:12px; font-weight:700; color:var(--subtle); text-transform:uppercase; letter-spacing:.05em; text-align:center; padding-bottom:4px; border-bottom:2px solid var(--border); }
.gantt .g-label { grid-column:1; font-size:14px; font-weight:700; color:var(--navy); display:flex; align-items:center; gap:8px; }
.gantt .g-label i { font-size:18px; color:var(--green); }
.gantt .g-bar { height:32px; border-radius:8px; display:flex; align-items:center; padding:0 14px; color:#fff; font-size:12px; font-weight:700; white-space:nowrap; overflow:hidden; box-shadow:0 2px 8px rgba(21,43,71,.14); transform-origin:left center; }
.slide.active .gantt .g-bar { animation: growBar 760ms var(--ease) both; }
.gantt .g-bar.done { background:linear-gradient(90deg, var(--green), var(--emerald)); }
.gantt .g-bar.prog { background:linear-gradient(90deg, var(--navy), var(--blue-green)); }
.gantt .g-bar.plan { background:repeating-linear-gradient(45deg, var(--green-10), var(--green-10) 8px, #fff 8px, #fff 16px); color:var(--green-dark); border:1px solid var(--green-20); box-shadow:none; }
.gantt .g-today { grid-row:2 / -1; width:0; border-left:2px dashed #b43232; justify-self:start; position:relative; z-index:3; pointer-events:none; }
.gantt .g-today::after { content:"Aujourd'hui"; position:absolute; top:-22px; left:50%; transform:translateX(-50%); white-space:nowrap; font-size:11px; font-weight:700; color:#b43232; }

/* === JOURNEY STEPPER (premium horizontal milestone bar) ===
   For a closing / status slide. 5 nodes over a connector line: .done filled green,
   .current pulsing ring (= "we are here"), plain = future. */
.journey { display:flex; align-items:flex-start; justify-content:space-between; position:relative; margin-top:14px; padding:0 2%; }
.journey::before { content:""; position:absolute; left:9%; right:9%; top:30px; height:3px; background:var(--green-20); z-index:0; }
.slide.active .journey::before { animation: growLine 900ms var(--ease) 240ms both; transform-origin:left center; }
.j-step { position:relative; z-index:1; flex:1; text-align:center; padding:0 6px; }
.j-step .j-ic { width:60px; height:60px; border-radius:50%; margin:0 auto 12px; display:grid; place-items:center; font-size:28px; background:#fff; border:3px solid var(--green-20); color:var(--subtle); }
.j-step.done .j-ic { background:linear-gradient(135deg, var(--green), var(--emerald)); border-color:transparent; color:#fff; box-shadow:0 8px 18px rgba(0,125,54,.22); }
.j-step.current .j-ic { border-color:var(--green); color:var(--green); box-shadow:0 0 0 7px var(--green-10); animation:pulseDot 1600ms var(--ease) infinite; }
.j-step strong { display:block; color:var(--navy); font-size:15px; line-height:1.2; }
.j-step span { display:block; margin-top:3px; color:var(--subtle); font-size:12px; font-weight:600; }
.slide.active .j-step { animation: rise 560ms var(--ease) both; }
.slide.active .j-step:nth-child(1){animation-delay:120ms}
.slide.active .j-step:nth-child(2){animation-delay:220ms}
.slide.active .j-step:nth-child(3){animation-delay:320ms}
.slide.active .j-step:nth-child(4){animation-delay:420ms}
.slide.active .j-step:nth-child(5){animation-delay:520ms}

/* === DECORATIVE SHAPES + ANNEX TAG === */
.deco-shapes { position:absolute; right:0; bottom:0; width:420px; height:300px; background:var(--shapes) right bottom / contain no-repeat; opacity:.10; z-index:0; pointer-events:none; }
.annex-tag { display:inline-flex; align-items:center; gap:8px; padding:4px 12px; border-radius:999px; background:var(--navy); color:#fff; font-size:11px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }

/* === SCOPE RIBBON (bandeau de périmètre sous le titre) ===
   Rappelle en une ligne le périmètre/scope d'une slide de coût ou de décision
   (ex. « Périmètre : PIM + CRM interne — une équipe, un budget »). À placer
   juste après le <h2>, avec la même classe animate que le titre. */
.scope-ribbon { display:inline-flex; align-items:center; gap:10px; margin-top:14px; padding:8px 16px; border-radius:999px; background:var(--green-05); border:1px solid var(--border); color:var(--navy); font-size:15px; font-weight:700; line-height:1.3; }
.scope-ribbon::before { content:""; width:9px; height:9px; border-radius:50%; background:var(--green); flex:0 0 auto; }
.scope-ribbon strong { color:var(--green); font-weight:700; }
.scope-ribbon em { font-style:normal; color:var(--muted); font-weight:600; }
.dark .scope-ribbon, .deck.theme-dark .slide:not(.cover):not(.light) .scope-ribbon { background:rgba(255,255,255,.08); border-color:rgba(255,255,255,.24); color:#fff; }
.dark .scope-ribbon em, .deck.theme-dark .slide:not(.cover):not(.light) .scope-ribbon em { color:rgba(255,255,255,.72); }

/* === MACRO COST-CODE (barres de composition lisibles de loin, SANS Chart.js) ===
   Pour un slide coût / TCO exécutif : chaque ligne = un scénario, barre segmentée
   par MACRO-composant (couleur = sémantique, pas décoratif) + gros total à droite.
   Longueur de barre = part du plus gros total (mettre width:% sur .macro-bar pour
   comparer les totaux entre lignes) ; largeur des segments = part du total de la
   ligne. Préférer ce composant aux charts empilés multi-séries pour un COMEX. */
.macro-legend { display:flex; flex-wrap:wrap; gap:30px; }
.macro-legend .mi { display:flex; align-items:center; gap:12px; font-size:19px; font-weight:700; color:var(--navy); }
.macro-legend .sw { width:24px; height:24px; border-radius:6px; flex:0 0 auto; }
.cost-rows { display:grid; gap:22px; }
.cost-row { display:grid; grid-template-columns:180px 1fr 150px; gap:24px; align-items:center; }
.cost-row .cr-label b { display:block; font-size:26px; color:var(--navy); font-weight:700; line-height:1.1; }
.cost-row .cr-label span { font-size:15px; color:var(--subtle); font-weight:700; }
.cost-row .cr-bar-wrap { min-width:0; }
.macro-bar { height:76px; display:flex; overflow:hidden; border-radius:8px; box-shadow:0 2px 8px rgba(21,43,71,.12); }
.macro-bar .seg { display:flex; align-items:center; justify-content:center; color:#fff; font-size:18px; font-weight:700; transform-origin:left center; white-space:nowrap; }
.slide.active .macro-bar .seg { animation: growBar 820ms var(--ease) both; }
.cost-row .cr-total { text-align:right; }
.cost-row .cr-total b { display:block; font-size:48px; line-height:1; color:var(--navy); font-weight:700; }
.cost-row .cr-total span { font-size:14px; font-weight:700; color:var(--subtle); }
/* Palette macro (sémantique — adapter les noms au sujet, garder ≤ 3-4 codes) :
   intern = construit / internalisé (vert), buy = acheté / éditeur / licence (navy),
   base = socle neutre (gris). */
.macro-legend .sw.intern, .macro-bar .seg.intern { background:var(--green); }
.macro-legend .sw.buy, .macro-bar .seg.buy { background:var(--navy); }
.macro-legend .sw.base { background:var(--green-20); border:1px solid var(--border); }
.macro-bar .seg.base { background:var(--green-20); color:var(--navy); }
.dark .macro-legend .mi, .deck.theme-dark .slide:not(.cover):not(.light) .macro-legend .mi { color:#fff; }
.dark .cost-row .cr-label b, .dark .cost-row .cr-total b,
.deck.theme-dark .slide:not(.cover):not(.light) .cost-row .cr-label b,
.deck.theme-dark .slide:not(.cover):not(.light) .cost-row .cr-total b { color:#fff; }

/* === CARD SEMANTIC ACCENTS (liseré haut coloré par sens) ===
   Par défaut .card::before est vert. Ces variantes recolorent le liseré pour
   coder deux volets d'une paire (ex. PIM vs CRM, construire vs acheter). */
.card.accent-navy::before, .card.buy::before { background:var(--navy); }
.card.accent-teal::before { background:var(--emerald); }

@media (max-width: 980px) {
  .cost-row { grid-template-columns:1fr; gap:10px; }
  .cost-row .cr-total { text-align:left; }
  .macro-bar { width:100% !important; }
}

/* === DECK THEME LAYER (additif — spec §1) ===
   theme-light (défaut, implicite) = styling de base inchangé.
   theme-dark = chaque slide de contenu foncée par défaut, en réutilisant la
   cascade .dark existante (dupliquée ici en sélecteurs scopés, sans éditer
   les règles .dark d'origine).
   .light sur une slide = escape hatch : exclut la slide du thème foncé via
   :not(.light), elle retombe sur le styling clair de base. Aucun style propre. */

.deck.theme-dark .slide:not(.cover):not(.light) {
  background: linear-gradient(135deg, var(--navy), var(--blue-green) 72%, var(--green));
  color: white;
}
.deck.theme-dark .slide:not(.cover):not(.light) h2,
.deck.theme-dark .slide:not(.cover):not(.light) h3,
.deck.theme-dark .slide:not(.cover):not(.light) p,
.deck.theme-dark .slide:not(.cover):not(.light) li { color: white; }
.deck.theme-dark .slide:not(.cover):not(.light) .logo { background-image: var(--logo-reversed); }
.deck.theme-dark .slide:not(.cover):not(.light) .eyebrow { color: rgba(255,255,255,.82); }
.deck.theme-dark .slide:not(.cover):not(.light) .eyebrow::before { background: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .statement { color: white; border-left-color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .statement strong { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .metric { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .footer { color: rgba(255,255,255,.72); }
.deck.theme-dark .slide:not(.cover):not(.light) .source-note { color: rgba(255,255,255,.6); }
.deck.theme-dark .slide:not(.cover):not(.light) .source-note a { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .progress span { background: rgba(255,255,255,.28); }
.deck.theme-dark .slide:not(.cover):not(.light) .progress span.on { background: var(--pastel); }
/* dark-safe components inside a theme-dark slide (mirror existing .dark variants) */
.deck.theme-dark .slide:not(.cover):not(.light) .chart-card { background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.24); box-shadow: none; }
.deck.theme-dark .slide:not(.cover):not(.light) .chart-card h3 { color: white; }
.deck.theme-dark .slide:not(.cover):not(.light) .chart-card .source-note { color: rgba(255,255,255,.7); }
.deck.theme-dark .slide:not(.cover):not(.light) .chart-card .source-note a { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .ph-icon { color: var(--pastel); background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.18); }
.deck.theme-dark .slide:not(.cover):not(.light) .ph-icon.navy { color: var(--white); background: rgba(255,255,255,.10); border-color: rgba(255,255,255,.22); }
.deck.theme-dark .slide:not(.cover):not(.light) .tab { color: rgba(255,255,255,.7); }
.deck.theme-dark .slide:not(.cover):not(.light) .tab:hover,
.deck.theme-dark .slide:not(.cover):not(.light) .tab.active { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .tab.active { border-bottom-color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .tabs { border-bottom-color: rgba(255,255,255,.18); }

/* === COUCHE FONCÉE COMMUNE — lisibilité sur fond foncé ===

   Trois surfaces sont foncées et ne diffèrent que par le sélecteur qui les
   désigne : `.cover`, une slide d'accent `.dark` dans un deck clair, et une
   slide de contenu d'un deck `theme-dark`. Le fond est le même dégradé
   navy #152B47 -> blue-green #2A5458 -> green #007D36.

   INVARIANT : toute règle de cette couche porte les sélecteurs des DEUX
   chemins foncés. La couche ci-dessus a été écrite par duplication et elle a
   dérivé — `.statement strong` n'avait reçu sa variante pastel que du côté
   `theme-dark`, et sur une slide d'accent `dark` d'un deck clair le gras
   restait en `--green` #007D36 sur navy, mesuré à 2,11:1 (plancher WCAG AA en
   gros texte : 3:1). Illisible de loin, donc inutilisable en séance.

   PÉRIMÈTRE : seuls les composants dont le texte se pose À MÊME le fond de
   slide ont besoin d'une variante ici. Un composant qui porte son propre fond
   clair — `card`, `check-card`, `chart-card`, `agenda-item`, `brick`,
   `mini-table`, `market-cell`, `readiness-rail`, `pill`, `provider-tag` — n'en
   a pas besoin : son backdrop n'est pas le dégradé. Ajouter un composant posé
   à même le fond sans sa variante foncée le rend invisible sur une slide
   d'accent : c'est le mode de défaillance que cette couche existe pour fermer. */

/* rattrapage de l'asymétrie — n'existait que du côté theme-dark */
.dark .statement, .cover .statement { color: white; border-left-color: var(--pastel); }
.dark .statement strong, .cover .statement strong { color: var(--pastel); }
.dark .source-note, .cover .source-note { color: rgba(255,255,255,.72); }
.dark .source-note a, .cover .source-note a { color: var(--pastel); }

/* composants posés à même le fond — cassés dans les DEUX chemins jusqu'ici */
.dark .legend-item, .cover .legend-item,
.deck.theme-dark .slide:not(.cover):not(.light) .legend-item { color: rgba(255,255,255,.78); }
.dark .cat-row .n, .cover .cat-row .n,
.deck.theme-dark .slide:not(.cover):not(.light) .cat-row .n { color: white; }
.dark .cat-row .l, .cover .cat-row .l,
.deck.theme-dark .slide:not(.cover):not(.light) .cat-row .l { color: rgba(255,255,255,.78); }
.dark .scope-ribbon strong, .cover .scope-ribbon strong,
.deck.theme-dark .slide:not(.cover):not(.light) .scope-ribbon strong { color: var(--pastel); }
.dark .gantt .g-label, .cover .gantt .g-label,
.deck.theme-dark .slide:not(.cover):not(.light) .gantt .g-label { color: white; }
.dark .gantt .g-label i, .cover .gantt .g-label i,
.deck.theme-dark .slide:not(.cover):not(.light) .gantt .g-label i { color: var(--pastel); }
.dark .gantt .g-head, .cover .gantt .g-head,
.deck.theme-dark .slide:not(.cover):not(.light) .gantt .g-head { color: rgba(255,255,255,.78); border-bottom-color: rgba(255,255,255,.24); }
.dark .j-step strong, .cover .j-step strong,
.deck.theme-dark .slide:not(.cover):not(.light) .j-step strong { color: white; }
.dark .j-step span, .cover .j-step span,
.deck.theme-dark .slide:not(.cover):not(.light) .j-step span { color: rgba(255,255,255,.78); }
.dark .cost-row .cr-label span, .dark .cost-row .cr-total span,
.cover .cost-row .cr-label span, .cover .cost-row .cr-total span,
.deck.theme-dark .slide:not(.cover):not(.light) .cost-row .cr-label span,
.deck.theme-dark .slide:not(.cover):not(.light) .cost-row .cr-total span { color: rgba(255,255,255,.78); }
/* `.step` porte une carte BLANCHE, et son texte heritait du blanc de la cascade
   foncee : blanc sur blanc, la slide paraissait vide. Rencontre en seance.
   `.step` n est donc PAS dans la liste des composants qui n ont besoin de rien —
   il porte son propre fond clair, mais il ne redeclare pas la couleur de son
   texte, contrairement a `.card` qui a sa variante `.dark-card`. */
.dark .step h3, .cover .step h3,
.deck.theme-dark .slide:not(.cover):not(.light) .step h3 { color: var(--navy); }
.dark .step p, .cover .step p,
.deck.theme-dark .slide:not(.cover):not(.light) .step p { color: var(--muted); }

/* guillemet ouvrant de la citation : décoratif, mais en --green à .55 d'opacité
   il tombe à 1,65:1 sur navy — présent dans le DOM, absent à l'écran */
.quote.dark blockquote::before, .quote.cover blockquote::before,
.deck.theme-dark .slide.quote:not(.light) blockquote::before { color: var(--pastel); }

/* === SLIDE ARCHETYPES (aerated, low-density — spec §2) ===
   Theme-adaptive via color:inherit + opacity. Reuse existing animations only. */

/* SECTION DIVIDER — chapter break */
.section-divider .body { justify-content: center; gap: 16px; }
.section-divider .sd-index { font-size: 84px; font-weight: 700; line-height: 1; color: currentColor; opacity: .18; }
.section-divider .sd-title { font-size: 52px; line-height: 1.1; font-weight: 600; color: inherit; max-width: 920px; }
.section-divider .sd-sub { font-size: 20px; line-height: 1.4; font-weight: 500; color: inherit; opacity: .72; max-width: 760px; }

/* QUOTE — full-bleed citation */
.quote .body { justify-content: center; gap: 22px; }
.quote blockquote { margin: 0; padding-left: 34px; position: relative; font-size: 38px; line-height: 1.26; font-weight: 600; color: inherit; max-width: 1000px; }
.quote blockquote::before { content: "\201C"; position: absolute; left: -4px; top: -22px; font-size: 92px; line-height: 1; color: var(--green); opacity: .55; }
.quote .q-author { display: flex; align-items: center; gap: 14px; }
.quote .q-author::before { content: ""; width: 34px; height: 2px; background: var(--green); flex: 0 0 auto; }
.quote .q-name { font-size: 18px; font-weight: 700; color: inherit; }
.quote .q-role { font-size: 15px; color: inherit; opacity: .66; }

/* AGENDA — numbered outline (light-card; safe on any background) */
.agenda .agenda-list { display: grid; gap: 12px; max-width: 940px; }
.agenda .agenda-item { display: grid; grid-template-columns: 46px 1fr; gap: 18px; align-items: center; padding: 14px 18px; border: 1px solid var(--border); border-radius: 8px; background: var(--white); box-shadow: 0 2px 6px rgba(21,43,71,.08); text-decoration: none; transition: transform .2s var(--ease), border-color .2s var(--ease); }
.agenda a.agenda-item:hover { transform: translateX(4px); border-color: rgba(0,125,54,.42); }
.agenda .ai-num { font-size: 24px; font-weight: 700; color: var(--green); line-height: 1; }
.agenda .ai-title { display: block; font-size: 19px; font-weight: 700; color: var(--navy); }
.agenda .ai-sub { display: block; font-size: 14px; color: var(--muted); margin-top: 2px; }
.slide.active .agenda-item { animation: rise 480ms var(--ease) both; }
.slide.active .agenda-item:nth-child(1) { animation-delay: 90ms; }
.slide.active .agenda-item:nth-child(2) { animation-delay: 160ms; }
.slide.active .agenda-item:nth-child(3) { animation-delay: 230ms; }
.slide.active .agenda-item:nth-child(4) { animation-delay: 300ms; }
.slide.active .agenda-item:nth-child(5) { animation-delay: 370ms; }
.slide.active .agenda-item:nth-child(6) { animation-delay: 440ms; }

/* CLOSING — final message + next steps + contact */
.closing .body { justify-content: center; gap: 22px; }
.closing .closing-title { font-size: 46px; line-height: 1.12; font-weight: 600; color: inherit; max-width: 920px; }
.closing .closing-contact { display: flex; align-items: center; gap: 12px; font-size: 16px; color: inherit; opacity: .88; }
.closing .closing-contact i { color: var(--green); font-size: 22px; }
.closing.dark .closing-contact i, .deck.theme-dark .slide.closing:not(.light) .closing-contact i { color: var(--pastel); }

/* BIG NUMBER — single giant KPI */
.big-number .body { justify-content: center; align-items: center; text-align: center; gap: 10px; }
.big-number .bn-metric { font-size: 160px; line-height: .95; font-weight: 700; color: var(--green); }
.big-number .bn-label { font-size: 24px; font-weight: 600; color: inherit; max-width: 700px; }
.big-number .bn-sub { font-size: 16px; color: inherit; opacity: .66; }
.section-divider.dark .sd-title, .deck.theme-dark .slide.section-divider:not(.light) .sd-title { color: white; }
.big-number.dark .bn-metric, .deck.theme-dark .slide.big-number:not(.light) .bn-metric { color: var(--pastel); }

/* === ACCENT ROUGE SUR UNE CARTE DE CONSTAT ===
   Trois `card.accent-warn` remplacent avantageusement `loss-list` quand les
   constats sont au nombre de trois : voir le piege de mise en page documente
   dans `components.md` a l entree Loss / Problem Hero. */
.card.accent-warn::before { background:#B0301F; }
.card.accent-warn { background:linear-gradient(180deg, rgba(176,48,31,.05), #fff); }

/* === CHIFFRES NUS — `.stat-row` et `.duo` ===
   Des chiffres poses a meme le fond, sans cadre, sans barre, sans remplissage.
   A preferer chaque fois que la GRANDEUR du nombre n est pas le message : une
   barre de composition dit "volume", et sur un montant faible c est le
   contresens exact. Deux chiffres poses sur du blanc ne disent rien d autre
   qu eux-memes.
   `.stat-row` pour trois reperes, `.duo` pour deux chiffres heros. */
.stat-row { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:2.3rem; }
.stat { padding-left:1.5rem; border-left:.18rem solid var(--green-20); }
.stat b { display:block; font-size:5.5rem; line-height:.95; font-weight:700; color:var(--green); letter-spacing:-.025em; }
.stat span { display:block; margin-top:1rem; font-size:1.5rem; font-weight:600; line-height:1.32; color:var(--muted); }
.slide.active .stat { animation: rise 600ms var(--ease) both; }
.slide.active .stat:nth-child(1){animation-delay:140ms}
.slide.active .stat:nth-child(2){animation-delay:240ms}
.slide.active .stat:nth-child(3){animation-delay:340ms}

.duo { display:grid; grid-template-columns:1fr 1fr; gap:3.7rem; }
.duo .d-item { padding-left:1.7rem; border-left:.24rem solid var(--green); }
.duo .d-item b { display:block; font-size:7.4rem; line-height:.92; font-weight:700; color:var(--green); letter-spacing:-.035em; }
.duo .d-item span { display:block; margin-top:1rem; font-size:1.56rem; font-weight:600; line-height:1.3; color:var(--navy); }
.duo .d-item em { display:block; margin-top:.5rem; font-style:normal; font-size:1.31rem; font-weight:600; line-height:1.35; color:var(--subtle); }
.slide.active .d-item { animation: rise 640ms var(--ease) both; }
.slide.active .d-item:nth-child(1){animation-delay:150ms}
.slide.active .d-item:nth-child(2){animation-delay:300ms}

/* === `.footnote` — la ligne discrete qui suit un bloc heros === */
.footnote { font-size:1.56rem; font-weight:600; line-height:1.4; color:var(--subtle); }

/* === `.ratio` — une proportion DESSINEE, pas ecrite ===
   Dix pastilles, une pleine, pour dire "un sur dix". Un pourcentage se lit, un
   dessin se voit : de loin, personne n a besoin de convertir 10 % en une
   proportion. Le nombre de pastilles est libre ; garder un denominateur qui se
   compte d un coup d oeil (5, 10, 20 au maximum). */
.ratio { display:flex; align-items:center; gap:.95rem; flex-wrap:wrap; }
.ratio .rd { width:3.1rem; height:3.1rem; border-radius:50%; border:.18rem solid var(--green-20); background:transparent; flex:0 0 auto; }
.ratio .rd.on { background:var(--green); border-color:var(--green); }
.slide.active .ratio .rd { animation: fadeScale 460ms var(--ease) both; }
.slide.active .ratio .rd:nth-child(1){animation-delay:80ms}
.slide.active .ratio .rd:nth-child(2){animation-delay:130ms}
.slide.active .ratio .rd:nth-child(3){animation-delay:180ms}
.slide.active .ratio .rd:nth-child(4){animation-delay:230ms}
.slide.active .ratio .rd:nth-child(5){animation-delay:280ms}
.slide.active .ratio .rd:nth-child(6){animation-delay:330ms}
.slide.active .ratio .rd:nth-child(7){animation-delay:380ms}
.slide.active .ratio .rd:nth-child(8){animation-delay:430ms}
.slide.active .ratio .rd:nth-child(9){animation-delay:480ms}
.slide.active .ratio .rd:nth-child(10){animation-delay:530ms}

/* === `.calc` — L ECHELLE DE CALCUL ===
   Le composant de cout a preferer des que l audience doit pouvoir REFAIRE le
   calcul. Un badge d operation a gauche, le libelle au milieu, le montant a
   droite ; les dernieres lignes surlignees sont les seules a retenir.
   Deux regles dures, apprises en seance :
   1. Afficher des MONTANTS, pas des grandeurs intermediaires. Un tableau de
      volumes ne repond pas a "combien coute une unite".
   2. Les montants affiches doivent TOMBER JUSTE a l ecran, quitte a mettre les
      valeurs exactes en notes. Un calcul dont les lignes ne s additionnent pas
      fait douter de tout le reste, meme quand l ecart n est qu un arrondi. */
.calc { display:grid; border:1px solid var(--border); border-radius:10px; overflow:hidden;
  background:#fff; box-shadow:var(--shadow); }
.calc-row { display:grid; grid-template-columns:3.2rem 1fr auto; align-items:center; gap:1.4rem;
  padding:1.25rem 1.75rem; border-bottom:1px solid var(--border); }
.calc-row:last-child { border-bottom:0; }
.calc-row .op { width:3rem; height:3rem; border-radius:50%; display:grid; place-items:center;
  font-size:2.3rem; font-weight:700; line-height:1; color:var(--green);
  background:var(--green-10); border:1px solid var(--green-20); }
/* Les glyphes + et x de Raleway ont une hauteur d oeil bien moindre qu une
   lettre : a taille egale ils paraissent minuscules dans leur pastille. Passer
   par une icone, dont l epaisseur de trait est constante. */
.calc-row .op i { font-size:2.1rem; }
.calc-row .lab { font-size:1.63rem; font-weight:600; color:var(--navy); line-height:1.25; }
.calc-row .lab small { display:block; margin-top:.25rem; font-size:1.25rem; font-weight:600; color:var(--subtle); }
.calc-row .amt { font-size:2.63rem; font-weight:700; color:var(--navy); white-space:nowrap;
  font-variant-numeric:tabular-nums; letter-spacing:-.02em; }
.calc-row.sum { background:var(--green-05); }
.calc-row.sum .op { color:#fff; background:var(--green); border-color:var(--green); }
.calc-row.sum .amt { color:var(--green); font-size:3.5rem; }
.calc-row.final .amt { font-size:4.25rem; }
.slide.active .calc-row { animation: rise 500ms var(--ease) both; }
.slide.active .calc-row:nth-child(1){animation-delay:140ms}
.slide.active .calc-row:nth-child(2){animation-delay:240ms}
.slide.active .calc-row:nth-child(3){animation-delay:340ms}
.slide.active .calc-row:nth-child(4){animation-delay:440ms}

/* === `.sieves` — DEUX ETAGES DE TRI, AVEC LEUR TRANSITION CHIFFREE ===
   Pour la slide qui explique comment un dispositif filtre, et surtout ou il est
   perfectible. Chaque tamis porte son libelle, sa transition (`289 -> 14`), son
   principe, et une ligne de LIMITE. Cette derniere ligne est le composant :
   une slide qui nomme sa faiblesse desarme le challenge au lieu de l attendre. */
.sieves { display:grid; grid-template-columns:1fr 1fr; gap:1.3rem; }
.sieve { padding:1.6rem 1.75rem; border:1px solid var(--border); border-radius:8px; background:#fff; box-shadow:var(--shadow); }
.sieve .sv-lab { display:block; margin-bottom:.85rem; font-size:1.25rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--subtle); }
.sieve .sv-num { display:block; margin-bottom:1rem; font-size:3.38rem; line-height:1; font-weight:700; color:var(--green); letter-spacing:-.02em; }
.sieve h3 { font-size:1.81rem; margin-bottom:.6rem; }
.sieve p { font-size:1.44rem; line-height:1.42; }
.sieve .sv-limit { margin-top:1.1rem; padding-top:1rem; border-top:1px solid var(--border); font-size:1.38rem; font-weight:600; color:var(--muted); }
.sieve.ai .sv-num { color:var(--emerald); }
.slide.active .sieve { animation: rise 600ms var(--ease) both; }
.slide.active .sieve:nth-child(1){animation-delay:150ms}
.slide.active .sieve:nth-child(2){animation-delay:280ms}

/* === `.edition-item` — UN EXTRAIT REEL DU PRODUIT ===
   Montrer le produit vaut mieux que le decrire. Cette carte porte la source
   CLIQUABLE, le contenu non retouche, et un encart de mise en perspective.
   La source cliquable est le composant : c est la demonstration la plus rapide
   que rien n est invente. */
.edition-item { padding:1.7rem 2rem; border:1px solid var(--border); border-radius:8px;
  background:var(--white); box-shadow:var(--shadow); }
.edition-item .ei-src { display:inline-flex; align-items:center; gap:.6rem; margin-bottom:1rem;
  font-size:1.31rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--green);
  text-decoration:none; border-bottom:2px solid var(--green-20); }
.edition-item a.ei-src:hover { border-bottom-color:var(--green); }
.edition-item h3 { font-size:2.06rem; line-height:1.2; margin-bottom:.7rem; color:var(--navy); }
.edition-item p { font-size:1.5rem; line-height:1.45; color:var(--muted); }
.edition-item .ei-why { margin-top:1.3rem; padding:1rem 1.4rem; border-left:4px solid var(--green);
  background:var(--green-05); border-radius:0 6px 6px 0; }
.edition-item .ei-why b { display:block; margin-bottom:.6rem; font-size:1.25rem; font-weight:700;
  letter-spacing:.1em; text-transform:uppercase; color:var(--green); }
.edition-item .ei-why p { font-size:1.56rem; font-weight:600; color:var(--navy); }
/* Le titre de l extrait, cite tel quel, pose a meme le fond. */
.edition-head { font-size:2.06rem; line-height:1.3; font-weight:600; color:var(--navy);
  padding-left:1.5rem; border-left:.24rem solid var(--green-20); max-width:69rem; }
.dark .edition-head, .cover .edition-head,
.deck.theme-dark .slide:not(.cover):not(.light) .edition-head { color:#fff; border-left-color:rgba(255,255,255,.28); }

/* === `.cols-list` — LISTE D ANNEXE EN COLONNES ===
   Une annexe reste une annexe : elle liste. Mais elle se lit de loin comme le
   reste. Puce PLEINE pour ce qui existe, puce CREUSE pour ce qui reste a faire
   — un vert et un navy se distinguent mal a distance, un plein et un creux se
   voient toujours. */
.cols-list { column-count:3; column-gap:2.3rem; margin:0; padding:0; }
.cols-list li { list-style:none; break-inside:avoid; margin:0 0 .7rem; padding-left:1.05rem;
  position:relative; font-size:1.63rem; font-weight:600; line-height:1.3; color:var(--navy); }
.cols-list li::before { content:""; position:absolute; left:0; top:.52em; width:.44rem; height:.44rem;
  border-radius:50%; background:var(--green); }
.cols-list.two { column-count:2; }
.cols-list.one { column-count:1; }
.cols-list.todo li::before { background:transparent; border:.13rem solid var(--navy); width:.7rem; height:.7rem; top:.44em; }
.cols-list li em { font-style:normal; font-weight:600; color:var(--subtle); }
.annex-block h3 { font-size:1.81rem; margin-bottom:1.25rem; color:var(--green); }
.dark .annex-block h3, .cover .annex-block h3,
.deck.theme-dark .slide:not(.cover):not(.light) .annex-block h3 { color:var(--pastel); }
.dark .cols-list li, .cover .cols-list li,
.deck.theme-dark .slide:not(.cover):not(.light) .cols-list li { color:#fff; }
.dark .cols-list li::before, .cover .cols-list li::before,
.deck.theme-dark .slide:not(.cover):not(.light) .cols-list li::before { background:var(--pastel); }
.dark .cols-list.todo li::before, .cover .cols-list.todo li::before,
.deck.theme-dark .slide:not(.cover):not(.light) .cols-list.todo li::before { background:transparent; border-color:var(--pastel); }
.dark .cols-list li em, .cover .cols-list li em,
.deck.theme-dark .slide:not(.cover):not(.light) .cols-list li em { color:rgba(255,255,255,.7); }
/* Une annexe porte plus de blocs qu une slide de seance : elle respire moins. */
.slide.annex .body { gap:2rem; justify-content:center; }
.slide.annex h2 { font-size:3.13rem; }

/* === `.fn-tag` — L ETAT D UNE ETAPE, POSE SUR LE SCHEMA ===
   Une etiquette par noeud de `.flow` pour dire ce qui tourne deja et ce qui
   reste a construire. Elle remplace une slide d inventaire entiere : le schema
   porte lui-meme son etat d avancement. */
.flow-node .fn-tag { display:inline-block; margin-top:.8rem; padding:.35rem .85rem; border-radius:999px;
  font-size:1.13rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase; }
.fn-tag.ok { color:var(--green); background:var(--green-10); border:1px solid var(--green-20); }
.fn-tag.todo { color:var(--blue-gray); background:rgba(21,43,71,.06); border:1px solid rgba(21,43,71,.20); }
.dark .fn-tag.ok, .cover .fn-tag.ok,
.deck.theme-dark .slide:not(.cover):not(.light) .fn-tag.ok { color:var(--navy); background:var(--pastel); border-color:var(--pastel); }
.dark .fn-tag.todo, .cover .fn-tag.todo,
.deck.theme-dark .slide:not(.cover):not(.light) .fn-tag.todo { color:#fff; background:rgba(255,255,255,.10); border-color:rgba(255,255,255,.30); }

/* Un `.flow` a cinq etapes : la grille de base en porte quatre. */
.flow.five { grid-template-columns:repeat(5, minmax(0,1fr)); gap:1.1rem; }
.flow.five::before { left:10%; right:10%; }
.flow.five .ph-icon { width:4.8rem; height:4.8rem; font-size:2.5rem; }
.flow.five h3 { font-size:1.56rem; line-height:1.2; }
.flow.five p { font-size:1.31rem; }

/* ============================================================================
   ECHELLE RELATIVE A L ECRAN — a garder telle quelle
   ============================================================================
   **C est la correction la plus importante de ce fichier, et elle a coute
   quatre relevements de police inutiles avant d etre comprise.**

   Tout ce qui precede est calibre en pixels sur une base de 1600 px de large.
   Un titre de `60px` ne rapetisse pas sur une tele 4K : il occupe
   proportionnellement DEUX FOIS MOINS de place, donc il paraît deux fois plus
   petit. Grossir les pixels ne corrige rien — le rapport au format reste le
   meme. Le collaborateur qui repete "la police est trop petite" apres trois
   corrections a raison, et ce n est pas la valeur qui est en cause, c est
   l unite.

   La taille de base suit donc la fenetre. `min(vw, vh)` prend la dimension la
   plus CONTRAIGNANTE : un ecran large mais bas ne peut plus faire grandir le
   texte au-dela de ce que sa hauteur accepte. Sans ce `min`, une slide dense
   deborde en `1366x768` et `.slide { overflow:hidden }` la coupe sans rien
   dire — c est arrive, sur la derniere ligne d un calcul, donc sur sa
   conclusion.

   | Fenetre | `1 rem` | rapport a la base |
   |---|---|---|
   | 1366 x 768 | 14,2 px | 0,89 |
   | 1600 x 1000 | 18,4 px | 1,00 |
   | 1920 x 1080 | 20,0 px | 1,09 |
   | 3840 x 2160 | 26,0 px | 1,41 (plafond) |

   Les composants ci-dessus sont deja exprimes en `rem`, taille ET espacement.
   **Un demi-passage a l echelle est pire qu aucun** : si le texte grandit mais
   pas les marges, le contenu deborde. Tout nouveau composant se declare donc
   en `rem`, sans exception. */

html { font-size: clamp(10px, min(1.15vw, 1.85vh), 26px); }

/* Le socle typographique, remis a l echelle. */
h1 { font-size:4.63rem; line-height:1.02; max-width:71rem; }
h2 { font-size:3.75rem; line-height:1.07; max-width:74rem; }
h3 { font-size:1.5rem; }
p, li { font-size:1.44rem; line-height:1.45; }
.lead { font-size:1.69rem; line-height:1.4; max-width:54rem; margin-top:1.5rem; }
.statement { font-size:2.13rem; line-height:1.28; padding-left:1.6rem; max-width:69rem; }
.eyebrow { font-size:1.19rem; letter-spacing:.16em; gap:.9rem; }
/* Le filet de l eyebrow etait un bloc de 3x18 px fixes : a l echelle haute il
   touchait la premiere lettre, et on lisait "ICE QUE CA COUTE". */
.eyebrow::before { width:.2rem; height:1.3rem; }
.footer { font-size:1.31rem; line-height:1.36; }
.slide { padding:2.9rem 5.1rem 2rem; gap:1.3rem; }
.body { gap:2.4rem; }
.hero-line { width:12rem; height:.3rem; margin-top:2.2rem; }
.big-message { padding:1.4rem 1.75rem; font-size:1.63rem; line-height:1.26; }
.card.tight { min-height:0; padding:1.6rem 1.5rem 1.5rem; display:flex; flex-direction:column; }
.card .metric { font-size:4.13rem; margin-bottom:.6rem; letter-spacing:-.03em; }
.card h3 { font-size:1.56rem; line-height:1.22; margin-bottom:.6rem; }
.card p { font-size:1.38rem; line-height:1.4; }
.step-tag { display:block; margin-top:auto; padding-top:1rem; font-size:1.13rem; font-weight:700;
  letter-spacing:.14em; text-transform:uppercase; color:var(--subtle); }
.card.dark-card .step-tag { color:rgba(255,255,255,.52); }
.card.dark-card .step-tag.ia { color:var(--pastel); }
.flow { gap:1.5rem; }
.flow::before { top:2.75rem; left:12%; right:12%; }
.flow-node .ph-icon { margin:0 auto 1.4rem; width:5.5rem; height:5.5rem; font-size:2.8rem; }
.flow-node h3 { font-size:2.88rem; line-height:1; font-weight:700; color:var(--green); margin-bottom:.7rem; letter-spacing:-.02em; }
.flow-node p { font-size:1.38rem; line-height:1.35; }
.dark .flow-node h3, .cover .flow-node h3,
.deck.theme-dark .slide:not(.cover):not(.light) .flow-node h3 { color:var(--pastel); }
.pill { padding:.85rem 1.45rem; font-size:1.25rem; }
.scope-ribbon { margin-top:.8rem; padding:.7rem 1.3rem; font-size:1.4rem; gap:.7rem; }
.scope-ribbon em { font-size:1.25rem; }
.annex-tag { font-size:1.13rem; padding:.5rem 1.15rem; }
.source-note { font-size:1.13rem; }
.two-col { gap:1.4rem; }
.closing .closing-title { font-size:3.63rem; }
.closing .closing-contact { font-size:1.44rem; }
.closing .closing-contact i { font-size:1.75rem; }
.closing .body { gap:1.8rem; }

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
  .flow, .product-grid, .two-col, .two-col.left-wide, .two-col.even { grid-template-columns:1fr; }
  .flow::before, .journey::before { display:none; }
  .journey { flex-wrap:wrap; gap:16px; }
  .j-step { flex:0 0 30%; }
  .foundation { flex-direction:column; align-items:flex-start; }
  .foundation .f-logos { margin-left:0; }
  .gantt { grid-template-columns:120px repeat(7,1fr); }
  .footer { margin-top:24px; }
  .nav { display:none; }
  .section-divider .sd-title { font-size: 34px; } .section-divider .sd-index { font-size: 56px; }
  .quote blockquote { font-size: 26px; } .closing .closing-title { font-size: 30px; }
  .big-number .bn-metric { font-size: 92px; } .agenda .agenda-list { max-width: none; }
  .stat-row, .duo, .sieves, .two-col.even { grid-template-columns:1fr; }
  .flow.five { grid-template-columns:1fr; }
  .calc-row { grid-template-columns:2.4rem 1fr auto; gap:.8rem; padding:.9rem 1rem; }
  .ratio .rd { width:1.9rem; height:1.9rem; }
  .cols-list { column-count:1; }
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
