# Snetor HTML Slides — CSS Design System

This file explains the design system of Snetor-branded HTML presentations: tokens, type scale,
themes and legibility rules. The CSS itself is `assets/deck/snetor-deck.css`, injected into
each deck by `scripts/inline_deck.py`, which also fills in the asset paths.

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

## Type Scale (Snetor brand guidelines — Brand Book p. 29-30)

A single typeface: **Raleway**. Four weights only — the ones actually loaded:

| Weight | Raleway face | Role | Examples |
|---|---|---|---|
| `400` | Regular | body text | `p`, `li`, `.sources`, captions |
| `500` | Medium | subheadings | `.lead`, `.sd-sub` |
| `600` | SemiBold | headings | `h1`, `h2`, `.statement`, `.closing-title`, `.sd-title`, `blockquote` |
| `700` | Bold | accents, micro-labels, figures | `h3`, `.eyebrow`, `.metric`, `.pill`, `.g-head`, `.annex-tag`… |

**Hard rule: no `font-weight` outside `400 / 500 / 600 / 700`.**
A `font-weight:800` (ExtraBold) or `900` (Black) is not loaded — neither by the Google Fonts `<link>`
(`wght@400;500;600;700`), nor by the four `@font-face` rules of stand-alone mode. The browser then
falls back to 700 and applies **synthetic bold** to it: the glyphs are thickened by the rendering
engine, not drawn by the type designer. That is no longer Raleway. If an ExtraBold ever becomes
necessary, you must first add `800` to the Google Fonts URL **and** ship `Raleway-ExtraBold.ttf`
in `assets/fonts/` — never declare the weight on its own.

Text color: **navy `#152B47`**, never black (brand rule). No `#000` anywhere in the
system; `--muted` / `--subtle` are navy derivatives for secondary text.

---

## Deck Themes

Set the theme on `<main class="deck ...">`:
- `theme-light` (default — may be omitted) — unchanged base styling.
- `theme-dark` — every content slide dark by default. Use the **dark-safe** component palette (`.dark-card`, `.cost`, `.chart-card`, `.brick`, `.foundation`, `.ph-icon`, `.tab`, `.spotlight-card`, `.big-message`, + archetypes). Light-card components are meant for light slides.

Per-slide accent (rhythm): add `dark` to a slide in a light deck, or `light` to a slide in a dark deck. `.light` opts the slide out of `theme-dark` back to the light styling.

### Legibility on a dark background — the two-path invariant

Three surfaces are dark: `.cover`, a `.dark` accent slide inside a light deck,
and a content slide of a `theme-dark` deck. **Any color rule written for one
must be written for the others**, in the
"COUCHE FONCÉE COMMUNE" layer of the CSS block, with both selectors on the same
rule. The `theme-dark` layer was created by duplicating the `.dark` cascade,
and rules added afterwards only landed on one side: `.statement
strong` stayed `--green` `#007D36` on navy, i.e. **2.11:1**, below the
WCAG AA floor of 3:1 for large text. Invisible in the room.

Only components whose text sits **directly on the slide background** need a
dark variant. A component that carries its own light background
(`card`, `check-card`, `chart-card`, `agenda-item`, `brick`, `mini-table`,
`market-cell`, `readiness-rail`, `pill`, `provider-tag`) does not:
its backdrop is not the gradient.

⚠️ **`step` is the exception that proves the rule.** It does carry a white
card, but it does not redeclare its text color, unlike
`card` which has its `dark-card` variant. On an accent slide, its `h3` and its
`p` therefore inherited `color:white` from the dark cascade: white on white, and
the slide looked empty on screen. Its variant now lives in the common
layer. Carrying your own background is not enough — **you must also carry your
text color.**

Mappings to respect when a new component arrives:

| On a light background | On a dark background |
|---|---|
| `var(--navy)` (heading, value) | `white` |
| `var(--muted)` (body, caption) | `rgba(255,255,255,.78)` |
| `var(--subtle)` (caption, column header) | `rgba(255,255,255,.72)` to `.78` |
| `var(--green)` (accent, link, icon) | `var(--pastel)` |
| `var(--border)` (rule) | `rgba(255,255,255,.24)` |

White is the ceiling: when white text still does not pass, it is no longer a
palette problem but a background one — that is the case of the cover header,
handled by a navy scrim and documented at its rule.

---

## Full CSS Block

The block lives in `assets/deck/snetor-deck.css`. Do not copy it into the deck by hand:
`scripts/inline_deck.py` injects it at the `/* @snetor-css */` marker (see SKILL.md, Step 4).
To change the design system, edit that file; the "COUCHE FONCÉE COMMUNE" layer is in it.

---

## Navigation JavaScript

Lives in `assets/deck/snetor-deck.js`, injected by `scripts/inline_deck.py` at the
`/* @snetor-nav-js */` marker, with `DECK_TITLE` declared from `--title`.
