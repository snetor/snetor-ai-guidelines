---
name: snetor-html-slides
description: >
  Generate Snetor-branded animated HTML presentation decks using the official Snetor design system
  (Raleway 400/500/600/700, green/navy palette, animated components, logos, hero imagery).
  USE THIS SKILL whenever someone asks for: slides, a presentation deck, a COMEX deck,
  a stakeholder presentation, a pitch deck, a slide on [any topic] for Snetor,
  or any request that would result in a set of slides or a presentation.
  Also triggers on the same request in French: "fais-moi des slides", "un deck",
  "une presentation pour le COMEX", "une presentation pour le CODIR", "des diapos",
  "prepare une presentation", "monte-moi un support de presentation".
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
- `references/standalone.md` — **only if the deck must be stand-alone / offline** (see Step 1, question 5)

You need the CSS from `css-system.md` to produce correct output. Do not reconstruct it from memory.

---

## Step 1 — Intake wizard (frame the need before generating)

Before planning or writing any HTML, **frame the need with the requester** through the
`AskUserQuestion` tool (multiple choice + native "Other"). Goal: a targeted deck, not a generic
template.

**Language detection** first, per `references/i18n.md` (FR by default, EN/ES depending on the
request, an explicit "in [language]" override wins). Ask the wizard questions in the requester's
language.

### Express mode (default) — 3 rounds

1. **Objective & framing** — one `AskUserQuestion` covering: audience (COMEX / technical
   leadership / team / customer / other), objective (decide / inform / convince / train), and the
   **key message** (the 1 decision or insight to take away).
2. **Structure** — propose **2-3 outlines** (each option = a mini-ASCII outline: slide titles + the
   role of each slide), with an indicative slide count. The requester picks one or amends it
   through "Other".
3. **Visual style** — one question where each option carries a `preview` field holding a **mini
   ASCII mockup**: theme (light / dark / mixed) and cover style. The requester can ask for
   something else through "Other".
4. **Density** — one `AskUserQuestion`: **Airy (default)** — a deck readable from a distance (large
   room / small TV), large type, 1 idea per slide, macro visuals (`macro cost-code`, `big-number`,
   CSS bars); or **Rich / deep-dive** — multi-series charts, radars, bubble matrix, tooltips
   (technical audience / annex). **Default to Airy**: it is the explicit preference of the Snetor
   CEO for live presentations (see "Default density" in Step 4).
5. **Stand-alone** — **only ask this question if a stand-alone signal is present** (the words
   "stand-alone", "autonome", "hors ligne", "offline", "sans internet", "package", "to send by
   e-mail" / "à envoyer par mail"; a presentation outside Snetor premises; a deck meant for
   archiving or external sharing). Two levels: **self-contained package** (HTML + an adjacent
   `assets/` folder, zero network — default) or **single file** (everything in base64, one file
   only). With no signal, do not ask: connected mode stays the default. See
   `references/standalone.md`.

### Guided mode (on request)

If the requester wants fine-grained control, go slide by slide: title, subtitle, and the proposed
main component (with 1-2 alternatives). One `AskUserQuestion` per slide or per small group.

### Anti-friction guard

If the initial request is **already detailed** (explicit audience + objective + outline), **do not
run the 3 rounds**: present a **single recap to validate** (audience, objective, outline, theme)
and move to Step 2 once approved. The wizard is there to remove ambiguity, not to slow down a clear
brief.

### Source material

Identify the sources to draw on (vault pages, interview notes, wikis) — cite them in the slides'
`.sources` (Step 4, rule 9).

---

## Step 2 — Plan the slide structure

Start from the outline validated in Step 1.

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

**Theme & accent rhythm (spec §1):**
- Pick a deck theme from the style validated in Step 1: `theme-light` (default), `theme-dark`, or
  mixed. Set it on `<main class="deck theme-...">`.
- Use **accent slides** for rhythm: `dark` in a light deck, `light` in a dark deck. Reserve accents
  for key moments (transition, quote, decision, big-number).
- **Alternation rules**: never two accent slides in a row; an accent marks a break, not a dense
  content slide.

**Airy archetypes (spec §2):** interleave `section-divider` (breathing space between parts),
`agenda` (up front), `quote`, `big-number` (one strong KPI), `closing`. See
`references/components.md`.

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
- `tradeoff-grid` — pros/cons, good/watch (e.g. buy vs build)
- `macro cost-code` — executive cost / TCO: CSS composition bars coloured per macro-component + a
  large total, readable from a distance; **preferred over stacked multi-series charts for a COMEX**
  (see `references/components.md`)
- `scope-ribbon` — scope banner restated under the title of cost / programme / decision slides
  (e.g. "PIM + internal CRM")
- `calc` — the **calculation ladder**: the cost line by line, in euros, with its operators. The cost
  component to prefer as soon as the audience must be able to redo the maths (rule 36)
- `stat-row` / `duo` — **bare figures**, with no frame and no bar: three markers, or two hero
  figures. Prefer these when the magnitude of the number is not the message
- `ratio` — a **drawn proportion** (ten dots, one filled) rather than a written percentage
- `sieves` — the **two stages of a filter** with their quantified transition and, above all, their
  limit line (rule 39)
- `edition-item` — a **real extract from the product** with its clickable source, to be preferred
  over a mechanism slide (rule 38)
- `flow` + `fn-tag` — a step diagram that **carries its own progress state** (rule 40)
- `cols-list` — annex list in columns, filled bullet for what exists, hollow for what is left to do
- `card accent-warn` — three finding cards with a red edge, the safe replacement for `loss-list`

---

## Step 3 — Prepare assets

1. Identify which logos and branding assets are needed based on the topic.
2. Create the output assets folder: `03-Outputs/assets/<deck-slug>/`
3. Copy from the skill's `assets/` folder:
   - Always: `snetor_full_logo.png`, `snetor_full_logo_reversed.png`, `Hero-banner-abstrait.jpg`
   - Topic-specific: relevant tech logos from `assets/logos/`

**Path convention:** The HTML file is at `03-Outputs/slides/<file>.html`.
Asset paths from the HTML file: `../assets/<deck-slug>/filename.png`

**In stand-alone mode**, the assets folder sits **next to the HTML**
(`<deck folder>/assets/<deck-slug>/`) and paths become `assets/<deck-slug>/…`. Also copy the
**4 font files** from the skill's `assets/fonts/`. Full detail: `references/standalone.md`.

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
  <!-- Connected mode (default). In stand-alone mode: DELETE these 3 <link> tags and declare
       4 local @font-face rules at the top of the <style> — see references/standalone.md §4. -->
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

### Default density = airy (explicit preference of the Snetor CEO)

By default a Snetor deck is **airy and readable from a distance** (large room, small TV). That is
the expected form **unless explicitly asked otherwise** ("Rich" density chosen in Step 1, or a
technical / annex audience).

An airy deck means:
- **large titles**, 1 idea per slide, ≤ ~25 words of body copy;
- **macro visuals** that read in 2 seconds: `big-number`, `macro cost-code` (CSS composition bars +
  large total), `scope-ribbon`, `fact-card`, CSS `.stacked` / `.impact-bars`;
- a **semantic colour code** (≤ 3-4 codes) rather than a 7-entry legend;
- **5-8 slides** for a decision.

The **rich / deep-dive** version (multi-series Chart.js, overlaid radars, bubble matrix, dense
tooltips — see `references/charts.md` § Deep-dive) is **opt-in**: do not go there by default. When
in doubt, ask the density question (Step 1) and pick **Airy**.

### Anti-overload guards (strict — spec §4)

A slide must breathe. Hard rules, applied to every generation:

- **1 idea per slide.** **1 main component max** per slide (the chrome — eyebrow, footer — does not
  count).
- **Strict word budget**: ≤ ~25 words of running text per slide (excluding titles, statements,
  speaker notes).
- **Detail elsewhere**: push the detail into speaker notes (`N`), an `accordion`, or an annex slide
  (`annex-tag`) — never pile it onto the slide.
- **Auto-split**: if the content exceeds the budget, **split** the slide in two rather than cram it.
- **Refuse to overload**: even on an explicit request ("put everything on one slide"), propose the
  split instead of cramming.

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
13. **CDN libs** — only include Chart.js / jsvectormap when the deck actually uses them. Pin versions per `references/charts.md`. **In stand-alone mode every CDN is forbidden**: favour CSS visuals, vendor `chart.umd.min.js` into the deck assets if a chart is indispensable, and give up jsvectormap (its base map loads from the network). See `references/standalone.md` §6.
14. **Prefer interactivity over text** — if a slide compares 3+ options, use `tab-slide` instead of bullet lists. If a slide has details that interrupt the main message, push them into `accordion` or `tooltip`. Respect the word budget of the anti-overload guards (≤ ~25 words of body copy per slide); beyond that, split the slide or move the detail into notes / accordion / annex.
15. **Hover-reveal cards** — use sparingly (max 1 row per deck) for "punchline + reveal" effects on metric cards. See `references/interactivity.md`.
16. **Marquee** — for ecosystem / partner / client logo slides with 6+ logos only. ≤5 logos = static row. Duplicate the logo set twice in the markup for seamless infinite scroll. See `references/external-libs.md`.
17. **Bento grid** — for "value prop synthesis" / "what we do" slides only. Max 1 bento per deck. 5 cells with mixed `.big` / `.tall` / `.wide` / `.green` / `.dark` modifiers.
18. **Spotlight cards** — `.dark` slides only, max 1 row per deck.
19. **Phosphor icons** — for fact-card iconography and inline iconography. Use class `<i class="ph ph-<name> ph-icon">`. Prefer regular weight by default, `ph-fill` for KPI cards needing more visual weight. Tone variants: default (green), `.navy`, `.teal`. See `references/external-libs.md`. **In stand-alone mode** the Phosphor CDN is unavailable: do without icons (recommended) or embed inline SVGs in a `<span class="ph-icon">`. See `references/standalone.md` §5.
20. **Speaker notes** — for any slide whose body text exceeds the word budget (~25 words, see Anti-overload guards), add `<aside class="notes">` with the detail. Presenter accesses via `N` key. See `references/presenter-mode.md`.
21. **Presenter mode DOM** — every deck must include the 4 overlays (`#overview-grid`, `#shortcuts-modal`, `#notes-overlay`, `#timer-display`) after the `<main class="deck">` block. Bootstrap script from `references/presenter-mode.md` is always included.
22. **Charts lazy-init (REQUIRED)** — never build charts eagerly at load. A chart built while its slide is `display:none` sizes to 0px → blank render ("reload to see it") AND dead tooltips (hit model stuck at 0px). Build on slide activation, **inside `requestAnimationFrame`** (so layout settles), keep the instance, and `resize()` on every (re)activation. Builders must `return` the `Chart`. Use the exact `initChartsOnActive()` pattern in `references/charts.md`, hooked into `show()`. Verify hover with trusted CDP mouse events, not synthetic `MouseEvent`s.
23. **Roadmap** — when workstreams overlap across time, prefer the `gantt` component over `path`; add a `.g-today` "now" marker and use `.done` / `.prog` / `.plan` bar states.
24. **Product portfolio** — use `product-grid` cards with real screenshots (copied into the deck assets folder, like any logo) to make products tangible and clickable; place the `foundation` band below them as the common base.
25. **Prioritization** — use the value × complexity bubble matrix with a per-point `ex` (concrete example) so tooltips read "name + example + axes"; show a pruned `key` subset on the main slide and keep the full dataset / sensitive figures (e.g. effort) on annex slides marked with `annex-tag`.
26. **Themes & accents** — set `theme-light` (default) or `theme-dark` on `<main class="deck">`. Use accent slides (`dark` in a light deck, `light` in a dark deck) for rhythm at key moments. No two accent slides in a row. On dark slides use the dark-safe component palette (see `references/css-system.md` → Deck Themes).
27. **Archetypes** — use the aerated archetypes (`section-divider`, `agenda`, `quote`, `big-number`, `closing`) to vary rhythm and avoid the same arc every time. `big-number` uses `.bn-metric.counter`; `agenda` items may link via `?slide=N`.
28. **Default density = airy** (CEO preference). Generate an airy deck by default (see "Default density"). Reserve dense visuals (multi-series charts, overlaid radars, bubble matrix, dense tooltips) for deep-dives / annexes, or for an explicit request. When in doubt, choose airy.
29. **Cost / TCO** — for an executive cost slide, prefer `macro cost-code` (CSS bars coloured per macro-component + large total, ≤ 3-4 semantic colour codes) over a stacked multi-series chart. Stacked multi-series stays for a deep-dive. See `references/components.md`.
30. **Scope ribbon** — when a costing or a decision covers several deliverables, or a scope that is not obvious, restate the scope with a `scope-ribbon` under the title, repeated on the cost / programme / decision slides.
31. **Stand-alone (on request)** — when the deck must be self-contained / offline, apply `references/standalone.md` **in full**: embedded `Raleway` fonts (the 3 Google Fonts `<link>` tags removed), assets in a folder **next to** the HTML, zero CDN, no `world-map`. **The 3-check verification is mandatory** (no residual network reference, every asset present on disk, real rendering checked) — a stand-alone deck is not assumed, it is verified. Do not turn this mode on by default: it makes the package heavier and rules out Chart.js charts.
32. **Font weights (brand guidelines)** — use only `400` (Regular, body), `500` (Medium, subtitles), `600` (SemiBold, headings) and `700` (Bold, accents / micro-labels / figures). **Never `800` or `900`**: those weights are not loaded (`wght@400;500;600;700`), so the browser thickens the 700 into **synthetic bold** — that is no longer Raleway. See `references/css-system.md` → Type Scale. Text is navy `#152B47`, never black.
33. **Colours on dark backgrounds (brand guidelines)** — `.cover`, a `.dark` accent slide and a `theme-dark` deck slide are the same background, and a colour rule written for one of the three must be written for the other two. The shipped CSS carries that layer: **do not rewrite a light colour by hand on a dark slide**, and do not invent an inline variant. Mappings: `--navy` → `white`, `--muted` → `rgba(255,255,255,.78)`, `--subtle` → `rgba(255,255,255,.72)`, `--green` → `var(--pastel)`, `--border` → `rgba(255,255,255,.24)`. A component that carries its own light background (`card`, `check-card`, `chart-card`, `agenda-item`, `brick`, `mini-table`) needs no variant at all. **If a new component puts text directly on the slide background, its dark variant is added in `references/css-system.md` → « COUCHE FONCÉE COMMUNE », with both selectors on the same rule** — not in the deck. Detail and rationale: `references/css-system.md` → Legibility on a dark background.

34. **Scale relative to the screen — never go back to pixels.** The shipped CSS carries
    `html { font-size: clamp(10px, min(1.15vw, 1.85vh), 26px) }` and expresses everything in `rem`,
    size **and** spacing. Reason: in fixed pixels, a `60px` title does not shrink on a large TV, it
    takes up proportionally half as much space — so it *looks* half as big, and enlarging the
    pixels changes nothing. **Every new component is declared in `rem`, no exception.** A half
    migration is worse than none: if the text grows but the margins do not, the content overflows
    and `.slide { overflow:hidden }` cuts it silently.

35. **Typographic floor: nothing below `1.1rem`.** That is ~`20px` at the reference scale.
    It applies to the chrome too — footer, `eyebrow`, labels. And when a sources line runs past one
    line on screen, the font is not what to shrink: **the text is what to shorten**, with the
    detail going into speaker notes. A three-line footer cannot be large.

36. **Cost: never a bar for a small amount.** A composition bar says "volume"; on a negligible cost
    it conveys exactly the opposite. Prefer `calc` (the calculation ladder, when the audience must
    be able to redo the maths) or `duo` (two bare figures). The `macro cost-code` of rule 29 remains
    the right component to **compare scenarios** whose masses differ, not to prove that a cost is
    negligible. And a cost slide shows **amounts**, never only intermediate quantities: a table of
    volumes does not answer "how much does one unit cost".

37. **A proportion is drawn.** For a striking ratio — one in ten, one in five — use `ratio` rather
    than a written percentage. From a distance, nobody converts `10 %` into a proportion.

38. **Show the product before explaining it.** When the subject is an existing deliverable, an
    `edition-item` slide with a real extract and its **clickable source** beats a mechanism slide.
    The mechanism goes down to the annex. Corollary: **the title must not suggest an adoption that
    does not exist** — say "the current beta" when it is a beta.

39. **Name the weakness of the setup.** On an AI topic, the "how do you know it is any good"
    question always comes. A `sieves` slide carrying its limit lines, plus the concrete example of
    the flaw and the workstream that would close it, defuses the challenge instead of waiting for
    it. A deck that names no limit gets taken apart on the first one.

40. **Let the diagram carry the progress.** An `fn-tag` label on each `flow` node (`Déjà là` /
    `À construire`) plus a `big-message` giving the count replaces an entire inventory slide.

41. **Name the decision-maker for every ask.** An ask with no decision-maker and no prerequisite is
    not actionable and ends in "sort that out between yourselves". If the requester does not want a
    decision slide, the closing carries the ask in one line and the prerequisites in a `statement`
    — not nothing.

---

## Step 4.b — Check the rendering, do not assume it

**A deck nobody has looked at is not finished.** Three defects from this session were invisible
when reading the HTML and obvious on screen: white text on a white card, text broken word by word,
a last calculation line that fell off the slide.

Headless screenshots catch the animations **in flight**: a slide looks empty when it is simply at
`opacity:0`. So go through a temporary copy whose animations are neutralised.

```bash
python -c "
src = open('<deck>.html', encoding='utf-8').read()
kill = '<style>*,*::before,*::after{animation:none !important;transition:none !important}</style>'
open('zz-tmp-check.html','w',encoding='utf-8').write(src.replace('</head>', kill + '</head>', 1))
"
```

Then capture, and **at both ends of the range**:

```powershell
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$u = "file:///<path>/zz-tmp-check.html"
# 1366x768 : the most CONSTRAINING size, the one that reveals overflows
& $edge --headless=new --disable-gpu --window-size=1366,768 --screenshot="chk.png" --virtual-time-budget=6000 "$u`?slide=6"
# 1920x1080 : the room size, the one that reveals fonts that are too small
& $edge --headless=new --disable-gpu --window-size=1920,1080 --screenshot="chk-hd.png" --virtual-time-budget=6000 "$u`?slide=6"
```

Look at every slide, then **delete the temporary copy**. The navigation's `?slide=N` parameter
captures any slide directly.

What to look for, in this order:

1. invisible text — the same colour as its background;
2. content cut off at the bottom of a slide, `overflow:hidden` gives no warning;
3. text breaking word by word — the `loss-item` trap;
4. missing glyphs — an empty square instead of an icon;
5. fonts too small for the format.

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
`snetor_full_logo.png` · `snetor_full_logo_reversed.png` · `Hero-banner-abstrait.jpg`

> **Brand rule:** the Snetor globe is **never** used on its own. It is part of the logotype and must
> not be cut out as a standalone mark or as decoration. Use `snetor_full_logo.png` (or its reversed
> version on a dark background). No globe asset ships with this skill.
`snetor_shapes.png` (optional — decorative backdrop for the `foundation` band; copy when used)

> ⚠️ **`snetor_shapes.png` is not a texture, it is a brand-guidelines plate** — a map, blocks of
> text, pictograms. Inside `foundation`, at `.16` opacity and cropped to the right, it works. As
> `deco-shapes` on a closing slide, at `.10` opacity, **it reads as a stray rectangle** and looks
> like a rendering defect. Do not use it as a slide background.

**Technology logos available** (copy only those needed):
`azure.png` · `microsoft.png` · `microsoft_fabric.png` · `gcp.png` · `google.png` · `aws.png` · `amazon.png`
`anthropic.png` · `claude.png` · `openai.png` · `vertex-ai.png` · `azure-ai-foundry.png` · `amazon-bedrock.png`
`powerbi.png` · `sharepoint.png` · `copilot.png` · `copilot-studio.png` · `copilot-cowork.png` · `power-automate.png`
`sap.png` · `sap-b1.png` · `sap-concur.png` · `s4-hana.png` · `opentext.png`
`kantox.png` · `xeneta.png` · `buyco.png` · `datasur.png` · `alpega-tms.png`

**Fonts** (stand-alone mode only, in `assets/fonts/`):
`Raleway-Regular.ttf` (400, body) · `Raleway-Medium.ttf` (500, subtitles) ·
`Raleway-SemiBold.ttf` (600, headings) · `Raleway-Bold.ttf` (700, accents and micro-labels).
In connected mode, do not copy them: Google Fonts does the job.
**These four weights are the only ones available** — no `font-weight:800/900` (rule 32).

**Iconography:** use [Phosphor Icons](https://phosphoricons.com) via CDN — see `references/external-libs.md` for the recommended icon set per topic and weight variants. No copy needed; the script tag pulls all weights. *(Unavailable in stand-alone mode — see `references/standalone.md` §5.)*

All asset files live in this skill's `assets/branding/`, `assets/logos/` and `assets/fonts/` subdirectories.
Copy them to `03-Outputs/assets/<deck-slug>/` before referencing them from the HTML
(or into `<deck folder>/assets/<deck-slug>/` in stand-alone mode).
