# Snetor HTML Slides — CSS Design System

This file explains the design system of Snetor-branded HTML presentations: tokens, type scale,
themes and legibility rules. The CSS itself is `assets/deck/snetor-deck.css`, injected into
each deck by `scripts/inline_deck.py`, which also fills in the asset paths.

---

## Color Tokens

Canonical source: the Snetor design system published at
<https://claude.ai/artifact/3KP5MLUABUrR5gXhBa4Tzb>, built from marketing's
`colors_and_type.css`. The deck tokens below are its short names; when they disagree, the
published page wins and `assets/deck/snetor-deck.css` is fixed.

```
--green: #007D36         primary brand green (Pantone 356)
--green-80: #339153      tint steps (Brand Book p.25)
--green-60: #66A87B
--green-40: #99C2A3
--green-20: #CCE0CD      borders, accents
--green-10: #E5EFE5      card backgrounds
--green-05: #F2F7F2      subtle fills
--green-dark: #006028    link hover ONLY — not a palette colour
--navy: #152B47          primary dark, all text (Pantone 540C)
--navy-80: #455570
--navy-60: #737F94
--navy-40: #A1AAB8
--navy-10: #E7E9ED
--blue-gray: #293F52     mid dark (Pantone 548)
--blue-green: #2A5458    teal dark, start of the brand gradient (Pantone 5473)
--emerald: #168C74       teal accent (Pantone 562)
--emerald-80: #45A38C
--emerald-20: #D0E8E1
--pastel: #8CCAAE        light green, accents on dark (Pantone 337)
--pastel-60: #B7DCC8
--pastel-30: #DCEEE2
--midnight: #1E1B2F      deep dark (Pantone 539C)
--white: #FFFFFF
--muted: #4A5A6E         body text on light
--subtle: #7E8A9A        captions, small labels
--border: #E0E5DF        card borders
--border-strong: #C7CFC9 table rules, stronger separators
--bg-muted: #F4F7F4      faint green-tinted neutral background
--warning: #C77E0A       semantic
--danger: #B0301F        semantic (findings, loss, paused timer)
--accent-office: #F2B53D map pin — offices
--accent-warehouse: #3FA3E0 map pin — warehouses
--gradient-brand: linear-gradient(90deg, #2A5458, #007D36)
--gradient-band: linear-gradient(90deg, #007D36, #168C74)   data bars
```

### Gradient and shapes (Brand Book p.32-33)

The brand gradient is **horizontal, blue-green to green**. It fills brand rectangles — `big-message`,
`foundation`, `service-chip.primary`, `readiness-rail span.on`, `reveal-back` — and the cover
overlay. Only **white** text goes on it: at its green end, pastel reads 2.80:1 and
`rgba(255,255,255,.78)` 3.82:1, both below their floor. The eyebrow of `foundation` is therefore
white `.82`, not pastel.

Brand rectangles are square-cornered (`border-radius:0`): the Brand Book allows rectangles, straight
lines and right angles, and forbids circle and arch image frames. No gradient outside the two tokens
above.

---

## Type Scale (Snetor brand guidelines — Brand Book p. 29-30)

A single typeface: **Raleway**, loaded from `300` to `900` (`wght@300..900`; in stand-alone mode,
one `Raleway-<Weight>.ttf` per weight in `assets/fonts/`).

| Weight | Raleway face | Role | Examples |
|---|---|---|---|
| `300` | Light | the thin line of the signature only | `.closing-signature .sig` |
| `400` | Regular | body text | `p`, `li`, `.sources`, captions |
| `500` | Medium | subheadings | `.lead`, `.sd-sub` |
| `600` | SemiBold | headings | `h1`, `h2`, `.statement`, `.closing-title`, `.sd-title`, `blockquote` |
| `700` | Bold | accents, micro-labels, figures | `h3`, `.eyebrow`, `.metric`, `.pill`, `.g-head`, `.annex-tag`… |
| `800` | ExtraBold | key figures, a title used alone | `.metric`, `.bn-metric` when the figure is the message |
| `900` | Black | a title used alone, sparingly | section divider |

The Brand Book sets titles "from Medium to Black" and shows ExtraBold at 30 pt. Body text stays
Regular. Keep title / body contrast moderate: a huge title over tiny text is a p.32 restriction.
A weight is only declared if its file is loaded — otherwise the browser thickens the nearest one into
**synthetic bold**, which is no longer Raleway.

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
