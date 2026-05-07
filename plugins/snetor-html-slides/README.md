# snetor-html-slides

Claude Code skill for generating Snetor-branded animated HTML presentation decks.

## What it does

When invoked, this skill produces a single self-contained `.html` file with:
- Full Snetor design system (Raleway font, green/navy palette, all components)
- Animated entry transitions per slide element
- Keyboard + button navigation
- Interactive check-cards for validation slides
- Progress indicator

## What's new in 1.2

- **21st.dev components** — Snetor-branded marquee, bento grid, animated shiny text, spotlight cards (no dependencies). See `references/external-libs.md`.
- **Lottie icons** — animated SVG icons on fact-cards via lottie-web CDN.
- **tsParticles cover** — subtle particle effect on cover slides via `.particles` class.
- **Presenter mode** — `F` (fullscreen) / `O` (overview grid) / `N` (speaker notes) / `T` (timer) / `?` (shortcuts modal). See `references/presenter-mode.md`.
- **Speaker notes** — `<aside class="notes">` per slide, hidden by default, revealed via `N`.
- **Rules updated** — 23 non-negotiable rules now (was 15).

## What's new in 1.1

- **Multilingual** — auto-detection FR / EN / ES from the request, override via explicit mention. Other languages best-effort with EN UI fallback. See `references/i18n.md`.
- **Dynamic charts** — Chart.js integration with Snetor theme (`bar`, `line`, `donut`, `radar`, `area`) via the `chart-card` component. See `references/charts.md`.
- **Animated counters** — `.metric.counter` with `data-target`, counts up on slide activation.
- **World map** — `world-map` component for implantations / coverage slides (jsvectormap, Snetor-themed).
- **Interactive components** — `tab-slide`, `accordion`, hover-reveal cards (`.card.reveal`), and `data-tooltip`. See `references/interactivity.md`.
- **Less text mandate** — new rule 14: max 30 words of body per slide outside statements; push detail into accordions and tooltips.

## Installation

### Via the marketplace (recommended)

```
/plugin marketplace add snetor/snetor-ai-guidelines
/plugin install snetor-html-slides@snetor-ai-guidelines
```

### Manually

```bash
git clone https://github.com/snetor/snetor-ai-guidelines.git
```

Then in Claude Code: `/plugin install` and select `plugins/snetor-html-slides`.

The skill `snetor-html-slides:snetor-html-slides` will now appear in `/skills`.

### Triggering the skill

The skill auto-triggers whenever you ask for slides, a presentation, or a COMEX deck.
You can also invoke it explicitly with the `Skill` tool or via `/skills`.

## Assets

- `skills/snetor-html-slides/assets/branding/` — Snetor logos, globe, hero banner
- `skills/snetor-html-slides/assets/logos/` — 29 technology/vendor logos

## Updating the skill

When a new component pattern or layout improvement is found:
1. Pull the latest `snetor-ai-guidelines`
2. Run `/reload-plugins` — the skill updates automatically (it reads from your local clone)

To contribute improvements:
1. Edit `skills/snetor-html-slides/references/components.md` or `SKILL.md`
2. Commit and push to `snetor-ai-guidelines`
3. Other users pull and run `/reload-plugins`

## Structure

```
snetor-html-slides/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── snetor-html-slides/
│       ├── SKILL.md               ← main skill instructions
│       ├── assets/
│       │   ├── branding/          ← logos, globe, hero banner
│       │   └── logos/             ← technology logos
│       └── references/
│           ├── css-system.md      ← full CSS design system + nav JS
│           └── components.md      ← HTML component catalog
└── README.md
```
