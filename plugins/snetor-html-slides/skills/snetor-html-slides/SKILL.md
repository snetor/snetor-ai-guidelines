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

## Step 1 — Understand the request

Identify:
1. **Topic** — what the slides are about
2. **Audience** — COMEX, direction technique, équipe, client... This shapes the level of detail
3. **Key messages** — what the audience must leave with (1–3 decisions or insights)
4. **Slide count** — default to 4–6 slides; COMEX decks stay at 4–5
5. **Source material** — vault pages, interview notes, existing wikis to draw from

If the request is ambiguous, infer from context in the vault (`index.md`, relevant `02-Wiki/` pages) rather than asking — then confirm the structure before generating HTML.

---

## Step 2 — Plan the slide structure

Choose a logical arc. Common patterns:

**Decision deck (COMEX):**
`Cover → Context/Problem → Market insight → Options or Cost of inaction → Decision slide`

**Deep-dive (technical audience):**
`Cover → Problem statement → Current state → Solution → Requirements/Risks → Roadmap`

**Use-case pitch:**
`Cover → Opportunity → How it works → ROI / Business case → Next steps`

For each slide, decide the layout:
- `cover` class — slide 1 only, with hero image and h1
- `dark` class — emphasis slide (1 per deck maximum, for a key decision moment)
- plain — default for all content slides

And the primary component:
- `market-facts` / `fact-card` — for 4 stats/metrics in a row
- `loss-hero` + `loss-list` — problem/cost of inaction slides
- `check-grid` + `timeline` — validation / prerequisites slides
- `brick-wall` — feature/capability lists
- `path` — roadmap / 4-step sequence
- `provider-grid` — technology comparison (2–3 providers)
- `grid cols-2` with `card` — paired concepts
- `tradeoff-grid` — pros/cons, good/watch

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
<html lang="fr">
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
  <main class="deck">
    <!-- SLIDES HERE -->
    <!-- First slide gets class="slide cover active" -->
    <!-- Others get class="slide" -->
  </main>

  <nav class="nav" aria-label="Navigation slides">
    <button type="button" id="prev" aria-label="Slide précédente"></button>
    <button type="button" id="next" aria-label="Slide suivante"></button>
  </nav>

  <script>
    /* === NAVIGATION JS FROM references/css-system.md === */
    /* Replace DECK_TITLE with the actual title string */
  </script>
</body>
</html>
```

### Non-negotiable rules

1. **Copy the CSS verbatim** from `references/css-system.md`. Do not paraphrase, shorten, or reconstruct from memory. Replace `DECK_NAME` with the actual folder name.
2. **French language** — all slide content must be in French unless the user asks otherwise.
3. **One cover slide** — always `class="slide cover active"`. Subsequent slides have no `cover` class and no `active` class (JS adds it).
4. **Eyebrow labels in headers** — every content slide header gets an `<div class="eyebrow">` with a 2–3 word section label.
5. **Footer on every slide** — include `.footer` with `.sources` (cite vault pages or external URLs) and `.progress`.
6. **`animate` + delay classes** — apply `class="animate d1/d2/d3/d4"` to all major content blocks so they fade in sequentially.
7. **No inline styles for layout** — use the documented CSS classes. Add inline style only for dynamic values like `--w: 72%` on bar fills, or logo background-image URLs.
8. **Interactive check-cards** — use them on slides asking for validation (prerequisites, next steps). Pre-check items already confirmed in the vault.
9. **Source attribution** — link external stats to their source URLs. Cite vault pages by their relative path in the `.sources` div.
10. **Slide count** — 4–6 slides for COMEX decks; up to 8 for technical deep-dives. No padding slides.

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

The skill maintainer (Clément Peponnet) can commit improvements back to `snetor-ai-guidelines/plugins/snetor-html-slides/` for the org.

---

## Available assets quick reference

**Branding** (always copy to deck assets folder):
`snetor_full_logo.png` · `snetor_full_logo_reversed.png` · `snetor_globe.png` · `Hero-banner-abstrait.jpg`

**Technology logos available** (copy only those needed):
`azure.png` · `microsoft.png` · `microsoft_fabric.png` · `gcp.png` · `google.png` · `aws.png` · `amazon.png`
`anthropic.png` · `claude.png` · `openai.png` · `vertex-ai.png` · `azure-ai-foundry.png` · `amazon-bedrock.png`
`powerbi.png` · `sharepoint.png` · `copilot.png` · `copilot-studio.png` · `copilot-cowork.png` · `power-automate.png`
`sap.png` · `sap-b1.png` · `sap-concur.png` · `s4-hana.png` · `opentext.png`
`kantox.png` · `xeneta.png` · `buyco.png` · `datasur.png` · `alpega-tms.png`

All asset files live in this skill's `assets/branding/` and `assets/logos/` subdirectories.
Copy them to `03-Outputs/assets/<deck-slug>/` before referencing them from the HTML.
