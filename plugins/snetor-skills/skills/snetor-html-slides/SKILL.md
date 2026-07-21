---
name: snetor-html-slides
description: >
  Generate Snetor-branded animated HTML presentation decks using the official Snetor design system
  (Raleway font, green/navy palette, animated components, logos, hero imagery).
  USE THIS SKILL whenever someone asks for: slides, a presentation deck, a COMEX deck,
  a stakeholder presentation, a pitch deck, a slide on [any topic] for Snetor,
  or any request that would result in a set of slides or a presentation.
  Also use when updating or adding slides to an existing Snetor HTML deck.
  Do not use for Marp markdown decks — this skill generates self-contained .html files only.
---

# Snetor HTML Slides Skill

## What this produces

A single self-contained `.html` file with:
- Full Snetor design system (colors, fonts, components, animations)
- Keyboard + button navigation (← → arrows, Space, PageUp/Down, Home, End)
- Slide progress indicator
- Interactive check-cards where appropriate
- Responsive fallback and print layout

Saved to: `03-Outputs/slides/<YYYY-MM-DD> - <Title> - <Audience>.html`
Assets copied to: `03-Outputs/assets/<deck-slug>/`

---

## Step 0 — Read references before generating

Before writing any HTML, read:
- `references/css-system.md` — full CSS + color tokens + navigation JS (copy verbatim)
- `references/components.md` — HTML patterns for every component type

You need the CSS from `css-system.md` to produce correct output. Do not reconstruct it from memory.

---

## Step 1 — Intake wizard (cadrer avant de générer)

Avant de planifier ou d'écrire du HTML, **cadrer le besoin avec le collaborateur** via l'outil `AskUserQuestion` (choix multiples + « Autre » natif). Objectif : un deck ciblé, pas un template générique.

**Détection de langue** d'abord, selon `references/i18n.md` (FR par défaut, EN/ES selon la requête, override « in [language] » prioritaire). Poser les questions du wizard dans la langue du collaborateur.

### Mode express (défaut) — 3 tours

1. **Objectif & cadrage** — une question `AskUserQuestion` couvrant : audience (COMEX / direction technique / équipe / client / autre), objectif (décider / informer / convaincre / former), et **message clé** (la 1 décision ou insight à retenir).
2. **Structure** — proposer **2-3 plans** (chaque option = un outline en mini-ASCII : titres de slides + rôle de chaque slide), avec un nombre de slides indicatif. Le collaborateur choisit ou amende via « Autre ».
3. **Style visuel** — une question avec, pour chaque option, un champ `preview` contenant une **mini-maquette ASCII** : thème (clair / foncé / mixte) et style de cover. Le collaborateur choisit via « Autre » s'il veut autre chose.
4. **Densité** — une question `AskUserQuestion` : **Aérée (défaut)** — deck lisible de loin (grande salle / petite télé), gros texte, 1 idée/slide, visuels macro (`macro cost-code`, `big-number`, barres CSS) ; ou **Riche / deep-dive** — charts multi-séries, radars, matrice bulles, tooltips (audience technique / annexe). **Par défaut, choisir Aérée** : c'est la préférence explicite du CEO Snetor pour les présentations en séance (voir « Densité par défaut » au Step 4).

### Mode guidé (sur demande)

Si le collaborateur veut un contrôle fin, dérouler slide par slide : titre, sous-titre, et composant principal proposé (avec 1-2 alternatives). Une question `AskUserQuestion` par slide ou par petit groupe.

### Garde-fou anti-friction

Si la requête initiale est **déjà détaillée** (audience + objectif + plan explicites), **ne pas dérouler les 3 tours** : présenter un **récap unique à valider** (audience, objectif, plan, thème) et passer à Step 2 après accord. Le wizard sert à lever l'ambiguïté, pas à ralentir un brief clair.

### Source material

Identifier les sources à exploiter (pages du vault, notes d'entretien, wikis) — les citer dans les `.sources` des slides (Step 4, règle 9).

---

## Step 2 — Plan the slide structure

Partir du plan validé au Step 1.

Choose a logical arc. Common patterns:

**Decision deck (COMEX):**
`Cover → Context/Problem → Market insight → Options or Cost of inaction → Decision slide`

**Deep-dive (technical audience):**
`Cover → Problem statement → Current state → Solution → Requirements/Risks → Roadmap`

**Use-case pitch:**
`Cover → Opportunity → How it works → ROI / Business case → Next steps`

For each slide, decide the layout:
- `cover` class — slide 1 only, with hero image and h1
- `dark`/`light` — accent slide for rhythm at key moments; no two accent slides in a row
- plain — default for all content slides

**Theme & accent rhythm (spec §1) :**
- Choisir un thème de deck selon le style validé au Step 1 : `theme-light` (défaut), `theme-dark`, ou mixte. Le poser sur `<main class="deck theme-...">`.
- Utiliser les **slides d'accent** pour rythmer : `dark` dans un deck clair, `light` dans un deck foncé. Réserver les accents aux moments-clés (transition, citation, décision, big-number).
- **Règles d'alternance** : pas deux slides d'accent consécutives ; un accent marque une rupture, pas une slide de contenu dense.

**Archétypes aérés (spec §2) :** intercaler `section-divider` (respiration entre parties), `agenda` (en tête), `quote`, `big-number` (un KPI fort), `closing` (clôture). Voir `references/components.md`.

And the primary component:
- `market-facts` / `fact-card` — for 4 stats/metrics in a row
- `loss-hero` + `loss-list` — problem/cost of inaction slides
- `check-grid` + `timeline` — validation / prerequisites slides
- `brick-wall` — feature/capability lists
- `path` — roadmap / 4-step sequence
- `flow` — "how it works / our method" sequence (big icon nodes, richer than `path`)
- `gantt` — roadmap when phases overlap across time (bars + `.g-today` marker)
- `product-grid` + `foundation` — app/product portfolio with clickable screenshots, over a base platform band
- bubble matrix + `cat-legend` — value × complexity prioritization (see `references/charts.md`)
- `journey` — premium closing milestone bar ("we are here")
- `provider-grid` — technology comparison (2–3 providers)
- `grid cols-2` with `card` — paired concepts
- `tradeoff-grid` — pros/cons, good/watch (ex. acheter vs construire)
- `macro cost-code` — coût / TCO exécutif : barres de composition CSS colorées par macro-composant + gros total, lisible de loin ; **préféré aux charts empilés multi-séries pour un COMEX** (voir `references/components.md`)
- `scope-ribbon` — bandeau de périmètre rappelé sous le titre des slides coût / programme / décision (ex. « PIM + CRM interne »)

---

## Step 3 — Prepare assets

1. Identify which logos and branding assets are needed based on the topic.
2. Create the output assets folder: `03-Outputs/assets/<deck-slug>/`
3. Copy from the skill's `assets/` folder:
   - Always: `snetor_full_logo.png`, `snetor_full_logo_reversed.png`, `snetor_globe.png`, `Hero-banner-abstrait.jpg`
   - Topic-specific: relevant tech logos from `assets/logos/`

**Path convention:** The HTML file is at `03-Outputs/slides/<file>.html`.
Asset paths from the HTML file: `../assets/<deck-slug>/filename.png`

---

## Step 4 — Generate the HTML

### Document template

```html
<!doctype html>
<html lang="{{LANG}}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DECK TITLE</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    /* === FULL CSS FROM references/css-system.md === */
    /* Replace DECK_NAME in CSS variable URLs with the actual deck slug */
  </style>
</head>
<body>
  <main class="deck theme-light"><!-- theme-light (default) | theme-dark -->
    <!-- SLIDES HERE -->
    <!-- First slide gets class="slide cover active" -->
    <!-- Others get class="slide" -->
  </main>

  <nav class="nav" aria-label="{{nav_aria}}">
    <button type="button" id="prev" aria-label="{{prev_aria}}"></button>
    <button type="button" id="next" aria-label="{{next_aria}}"></button>
  </nav>

  <!-- Presenter mode overlays — see references/presenter-mode.md -->
  <div class="overview-grid" id="overview-grid" aria-hidden="true"></div>
  <div class="shortcuts-modal" id="shortcuts-modal" aria-hidden="true">
    <div class="panel">
      <h3>Keyboard shortcuts</h3>
      <dl>
        <dt>← →</dt><dd>{{prev_next_shortcut_label}}</dd>
        <dt>Space</dt><dd>{{next_slide_label}}</dd>
        <dt>Home / End</dt><dd>{{first_last_label}}</dd>
        <dt>F</dt><dd>{{fullscreen_label}}</dd>
        <dt>O</dt><dd>{{overview_label}}</dd>
        <dt>N</dt><dd>{{notes_label}}</dd>
        <dt>T</dt><dd>{{timer_label}}</dd>
        <dt>?</dt><dd>{{help_label}}</dd>
        <dt>Esc</dt><dd>{{close_label}}</dd>
      </dl>
    </div>
  </div>
  <div class="notes-overlay" id="notes-overlay" aria-hidden="true">
    <span class="label">{{presenter_notes_label}}</span>
    <div class="content"></div>
  </div>
  <div class="timer-display" id="timer-display" aria-hidden="true">00:00</div>

  <script>
    /* === NAVIGATION JS FROM references/css-system.md === */
    /* Replace DECK_TITLE with the actual title string */
    /* Append in this order after navigation JS: */
    /* 1. Interactivity bootstrap from references/interactivity.md (always) */
    /* 2. Chart.js bootstrap from references/charts.md (only if deck uses charts) */
    /* 3. Counter animation from references/charts.md (only if deck uses .counter) */
    /* 4. World map bootstrap from references/charts.md (only if deck uses .world-map) */
    /* 5. Lazy-init charts on slide activation (charts.md) — REQUIRED for correct tooltips */
  </script>
</body>
</html>
```

### Densité par défaut = aérée (préférence explicite du CEO Snetor)

Par défaut, un deck Snetor est **aéré et lisible de loin** (grande salle, petite télé). C'est la forme attendue **sauf demande contraire explicite** (densité « Riche » choisie au Step 1, ou audience technique / annexe).

Un deck aéré, c'est :
- **gros titres**, 1 idée par slide, ≤ ~25 mots de corps ;
- des **visuels macro** qui se lisent en 2 secondes : `big-number`, `macro cost-code` (barres de composition CSS + gros total), `scope-ribbon`, `fact-card`, `.stacked` / `.impact-bars` CSS ;
- un **code couleur sémantique** (≤ 3-4 codes) plutôt qu'une légende à 7 postes ;
- **5-8 slides** pour une décision.

La version **riche / deep-dive** (Chart.js multi-séries, radars superposés, matrice bulles, tooltips denses — voir `references/charts.md` § Deep-dive) est un **opt-in** : ne pas y aller par défaut. En cas de doute, poser la question de densité (Step 1) et choisir **Aérée**.

### Garde-fous anti-surcharge (stricts — spec §4)

Une slide doit respirer. Règles dures, appliquées à toute génération :

- **1 idée par slide.** **1 composant principal max** par slide (le chrome — eyebrow, footer — ne compte pas).
- **Budget mots strict** : ≤ ~25 mots de texte courant par slide (hors titres, statements, speaker notes).
- **Détails ailleurs** : pousser le détail en speaker notes (`N`), `accordion`, ou slide d'annexe (`annex-tag`) — jamais entassé sur la slide.
- **Auto-split** : si le contenu dépasse le budget, **scinder** la slide en deux plutôt que tasser.
- **Refus de surcharger** : même sur demande explicite (« mets tout sur une slide »), proposer le split au lieu d'entasser.

### Non-negotiable rules

1. **Copy the CSS verbatim** from `references/css-system.md`. Do not paraphrase, shorten, or reconstruct from memory. Replace `DECK_NAME` with the actual folder name.
2. **Language detection** — detect deck language from the request following `references/i18n.md` rules (FR/EN/ES priority, others best-effort). Set `<html lang="...">` to ISO code. Use the i18n dictionary for UI chrome strings (check-card labels, nav aria-labels, "Sources" footer).
3. **One cover slide** — always `class="slide cover active"`. Subsequent slides have no `cover` class and no `active` class (JS adds it).
4. **Eyebrow labels in headers** — every content slide header gets an `<div class="eyebrow">` with a 2–3 word section label.
5. **Footer on every slide** — include `.footer` with `.sources` (cite vault pages or external URLs) and `.progress`.
6. **`animate` + delay classes** — apply `class="animate d1/d2/d3/d4"` to all major content blocks so they fade in sequentially.
7. **No inline styles for layout** — use the documented CSS classes. Add inline style only for dynamic values like `--w: 72%` on bar fills, or logo background-image URLs.
8. **Interactive check-cards** — use them on slides asking for validation (prerequisites, next steps). Pre-check items already confirmed in the vault.
9. **Source attribution** — link external stats to their source URLs. Cite vault pages by their relative path in the `.sources` div.
10. **Slide count** — 4–6 slides for COMEX decks; up to 8 for technical deep-dives. No padding slides.
11. **Charts** — for any non-trivial quantitative comparison (multi-series, donut, line trend, radar, area), use `chart-card` from `references/charts.md`. Do NOT generate raw `<canvas>` or hand-coded SVG bars. The CSS-based `.stacked` and `.impact-bars` remain valid for simple single-row visualizations.
12. **Counters** — for hero metrics on cover/dark slides or fact-cards, prefer `.metric.counter` with `data-target` over static text.
13. **CDN libs** — only include Chart.js / jsvectormap when the deck actually uses them. Pin versions per `references/charts.md`.
14. **Prefer interactivity over text** — if a slide compares 3+ options, use `tab-slide` instead of bullet lists. If a slide has details that interrupt the main message, push them into `accordion` or `tooltip`. Respecter le budget mots des garde-fous anti-surcharge (≤ ~25 mots de corps/slide) ; au-delà, split ou renvoi en notes/accordion/annexe.
15. **Hover-reveal cards** — use sparingly (max 1 row per deck) for "punchline + reveal" effects on metric cards. See `references/interactivity.md`.
16. **Marquee** — for ecosystem / partner / client logo slides with 6+ logos only. ≤5 logos = static row. Duplicate the logo set twice in the markup for seamless infinite scroll. See `references/external-libs.md`.
17. **Bento grid** — for "value prop synthesis" / "what we do" slides only. Max 1 bento per deck. 5 cells with mixed `.big` / `.tall` / `.wide` / `.green` / `.dark` modifiers.
18. **Spotlight cards** — `.dark` slides only, max 1 row per deck.
19. **Phosphor icons** — for fact-card iconography and inline iconography. Use class `<i class="ph ph-<name> ph-icon">`. Prefer regular weight by default, `ph-fill` for KPI cards needing more visual weight. Tone variants: default (green), `.navy`, `.teal`. See `references/external-libs.md`.
20. **Speaker notes** — for any slide whose body text exceeds the word budget (~25 words, see Garde-fous anti-surcharge), add `<aside class="notes">` with the detail. Presenter accesses via `N` key. See `references/presenter-mode.md`.
21. **Presenter mode DOM** — every deck must include the 4 overlays (`#overview-grid`, `#shortcuts-modal`, `#notes-overlay`, `#timer-display`) after the `<main class="deck">` block. Bootstrap script from `references/presenter-mode.md` is always included.
22. **Charts lazy-init (REQUIRED)** — never build charts eagerly at load. A chart built while its slide is `display:none` sizes to 0px → blank render ("reload to see it") AND dead tooltips (hit model stuck at 0px). Build on slide activation, **inside `requestAnimationFrame`** (so layout settles), keep the instance, and `resize()` on every (re)activation. Builders must `return` the `Chart`. Use the exact `initChartsOnActive()` pattern in `references/charts.md`, hooked into `show()`. Verify hover with trusted CDP mouse events, not synthetic `MouseEvent`s.
23. **Roadmap** — when chantiers overlap across time, prefer the `gantt` component over `path`; add a `.g-today` "now" marker and use `.done` / `.prog` / `.plan` bar states.
24. **Product portfolio** — use `product-grid` cards with real screenshots (copied into the deck assets folder, like any logo) to make products tangible and clickable; place the `foundation` band below them as the common base.
25. **Prioritization** — use the value × complexity bubble matrix with a per-point `ex` (concrete example) so tooltips read "name + example + axes"; show a pruned `key` subset on the main slide and keep the full dataset / sensitive figures (e.g. effort) on annex slides marked with `annex-tag`.
26. **Themes & accents** — set `theme-light` (default) or `theme-dark` on `<main class="deck">`. Use accent slides (`dark` in a light deck, `light` in a dark deck) for rhythm at key moments. No two accent slides in a row. On dark slides use the dark-safe component palette (see `references/css-system.md` → Deck Themes).
27. **Archetypes** — use the aerated archetypes (`section-divider`, `agenda`, `quote`, `big-number`, `closing`) to vary rhythm and avoid the same arc every time. `big-number` uses `.bn-metric.counter`; `agenda` items may link via `?slide=N`.
28. **Densité par défaut = aérée** (préférence CEO). Générer un deck aéré par défaut (voir « Densité par défaut »). Réserver les visuels denses (charts multi-séries, radars superposés, matrice bulles, tooltips denses) aux deep-dives / annexes ou à une demande explicite. En cas de doute, choisir aéré.
29. **Coût / TCO** — pour un slide coût exécutif, préférer le `macro cost-code` (barres CSS colorées par macro-composant + gros total, ≤ 3-4 codes couleur sémantiques) au chart empilé multi-séries. Le stacked multi-séries reste pour un deep-dive. Voir `references/components.md`.
30. **Scope ribbon** — quand un chiffrage / une décision couvre plusieurs livrables ou un périmètre non évident, rappeler le périmètre via un `scope-ribbon` sous le titre, répété sur les slides coût / programme / décision.

---

## Step 5 — Save and link back

1. Save the HTML to `03-Outputs/slides/<YYYY-MM-DD> - <Title> - <Audience>.html`
2. If vault wiki pages cover this topic, add a link to the deck in their `## Outputs` or `## Livrables` section.
3. Update `log.md` with a dated entry.
4. Update `index.md` if this is a major deliverable.

---

## Updating an existing deck

When the user asks to update or add slides to an existing HTML file:
1. Read the existing file to understand its current structure and asset paths.
2. Identify which slides to add, modify, or remove.
3. Apply changes while preserving the existing CSS, navigation JS, and folder structure.
4. Do not regenerate slides that are unchanged.

---

## Self-improvement notes

This skill improves over time. After generating a deck:
- If a new component pattern was invented that worked well, add it to `references/components.md`.
- If color or layout adjustments improve readability for a specific slide type, document them in `references/css-system.md` as an addendum.
- If slide structure patterns emerge per audience type, add them to the plan-the-slide-structure section above.

The skill maintainer (Clément Peponnet) can commit improvements back to `snetor-ai-guidelines/plugins/snetor-skills/` for the org.

---

## Available assets quick reference

**Branding** (always copy to deck assets folder):
`snetor_full_logo.png` · `snetor_full_logo_reversed.png` · `snetor_globe.png` · `Hero-banner-abstrait.jpg`
`snetor_shapes.png` (optional — decorative wavy backdrop for the `foundation` band and `deco-shapes` on closing slides; copy when used)

**Technology logos available** (copy only those needed):
`azure.png` · `microsoft.png` · `microsoft_fabric.png` · `gcp.png` · `google.png` · `aws.png` · `amazon.png`
`anthropic.png` · `claude.png` · `openai.png` · `vertex-ai.png` · `azure-ai-foundry.png` · `amazon-bedrock.png`
`powerbi.png` · `sharepoint.png` · `copilot.png` · `copilot-studio.png` · `copilot-cowork.png` · `power-automate.png`
`sap.png` · `sap-b1.png` · `sap-concur.png` · `s4-hana.png` · `opentext.png`
`kantox.png` · `xeneta.png` · `buyco.png` · `datasur.png` · `alpega-tms.png`

**Iconography:** use [Phosphor Icons](https://phosphoricons.com) via CDN — see `references/external-libs.md` for the recommended icon set per topic and weight variants. No copy needed; the script tag pulls all weights.

All asset files live in this skill's `assets/branding/` and `assets/logos/` subdirectories.
Copy them to `03-Outputs/assets/<deck-slug>/` before referencing them from the HTML.
