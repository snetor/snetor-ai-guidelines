---
name: snetor-excalidraw-diagrams
description: >
  Create Snetor-branded architecture diagrams as editable Excalidraw files with embedded service
  icons (Azure services, SAP, Fabric, Twenty, LiteLLM, GitHub, Terraform, PostgreSQL, Redis, Entra ID…)
  and the Snetor palette. USE THIS SKILL whenever someone asks for an architecture diagram, a
  "schéma d'architecture", an infra / network / data-flow / cloud diagram, a diagram of a landing
  zone or deployment, a RACI/governance flow, or wants to visualize how systems connect — for Snetor.
  Produces a self-contained `.excalidraw` (editable on excalidraw.com or the VS Code Excalidraw
  extension) plus a PNG preview. Do NOT use this for HTML slide decks (use snetor-html-slides) nor
  for throwaway mermaid snippets in markdown.
---

# Snetor Excalidraw Diagrams

## What this produces

A real `.excalidraw` file with **embedded logos/icons** (base64, self-contained), branded with the
Snetor design system, plus a PNG **preview** for embedding in docs/PRs. The `.excalidraw` is the
deliverable: editable on [excalidraw.com](https://excalidraw.com) (drag-drop) or the VS Code
*Excalidraw* extension (`pomdtr.excalidraw-editor`).

## Why a Python script and NOT the Excalidraw MCP `create_view`

The MCP `create_view` renders a nice animated preview but **cannot display image/PNG elements** — so
it can't show real logos. The `.excalidraw` *format* supports images (an `image` element + a base64
entry in the `files` map), so we build the scene as a `.excalidraw` file with a small Python toolkit.
This keeps the (large) base64 out of the conversation and makes the result editable and versionable.

Full rationale + format details: `references/excalidraw-format.md`.

## Workflow

Follow these four steps. Don't hand-write Excalidraw JSON — use the toolkit.

### 1. Understand the diagram

Clarify (infer from context where you can, ask only if truly blocking):
- **Purpose & audience** — an executive/vulgarized overview reads very differently from a technical
  one. Executive: few boxes, plain labels, one icon per box. Technical: resource groups, services,
  flows, denser icons.
- **The elements** — systems/components, how they group (layers, resource groups, zones), and the
  **flows** between them (who calls/feeds whom).
- **One diagram per concern.** If asked for "the architecture", a good default set is: (a) a
  conceptual layered view (foundation + applications), (b) a global technical view (groups +
  services + flows), (c) a governance/CI-CD or network view. Build them as separate files.

### 2. Compose with the toolkit

Write a short build script (in the output folder) that imports the toolkit and lays out the scene.
The toolkit lives in this skill's `scripts/` — add it to `sys.path`:

```python
import sys
sys.path.insert(0, "<THIS-SKILL>/scripts")   # the dir holding excalidraw_snetor.py
from excalidraw_snetor import (Scene, L, GREEN, GREEN_DARK, GREEN05, GREEN10, GREEN20,
                               NAVY, EMERALD, BLUE_GREEN, MUTED, SUBTLE, WHITE)

s = Scene()
s.image(120, 52, 46, "snetor_full_logo.png")                       # header brand logo
s.text(300, 30, "Mon architecture — DEV", size=27, color=NAVY)
s.rect(300, 120, 920, 660, fill=GREEN05, stroke=GREEN, sw=3)       # a container / zone
s.card(352, 240, 156, 180, "Twenty\n(CRM)", icon="twenty.png",
       fill=GREEN10, stroke=EMERALD)                                # a box with an icon + title
s.icon_row(430, 400, ["azure-aca.png","postgresql.png","redis.png"])   # a row of service icons
s.arrow(250, 207, 330, 285, color=BLUE_GREEN, label="HTTPS")        # a flow
s.save("01-mon-architecture.excalidraw")
```

The API (every helper, with signatures and the coordinate model) is in `references/library-api.md`.
A complete worked example is `scripts/example_diagram.py` → renders to `example-architecture.png`
(look at it to see the target quality).

### 3. Render a preview and LOOK at it — then iterate

You cannot judge a diagram you haven't seen. After every build, render a PNG and **actually read the
image**, then fix overlaps, mis-routed arrows, text overflow, missing icons. Re-render. Repeat until
it's clean. This iteration is the difference between a sloppy diagram and a great one.

```bash
python <THIS-SKILL>/scripts/render_excalidraw.py 01-mon-architecture.excalidraw 01-mon-architecture.png
```

`render_excalidraw.py` runs the **real** Excalidraw engine in headless Edge (Playwright), so the PNG
shows the Excalifont and the hand-drawn stroke exactly as excalidraw.com will. It loads the engine
from a CDN; offline, fall back to `render_preview.py` (same arguments) — a flat approximation in a
system font, good for catching overlaps, useless for judging the style.

### 4. Deliver

- Save the `.excalidraw` (the editable source) and the `.png` (preview) where they belong (e.g. a
  `diagrams/` folder next to the docs).
- Embed the PNG in the relevant doc and link the `.excalidraw` as the editable source.
- Tell the user how to open it: drag the `.excalidraw` onto excalidraw.com, or open it with the
  VS Code Excalidraw extension.

## Snetor conventions (what makes a diagram look "Snetor")

**Palette** (imported as constants — use them, don't invent colors):
`GREEN #007D36` (primary), `GREEN_DARK #006028`, `NAVY #152B47` (titles/text), `EMERALD #168C74`
(box borders), `BLUE_GREEN #2A5458` (**all flow arrows** — this is the house arrow color),
`GREEN05/10/20` (light fills/tints), `MUTED #4A5A6E` / `SUBTLE #7E8A9A` (secondary text).

**Art direction — « brouillon propre » (clean sketch), the default since 2026-09-25.** Excalifont
(`fontFamily=5`), hand-drawn stroke (`roughness=1`), thin lines (`strokeWidth=1.5`), rounded corners,
solid light fills. A diagram that looks like a sketch reads as an idea to discuss rather than a
frozen blueprint — which is what makes it land with an executive. It stays *propre*: the grid, the
palette and the composition rules below still apply; only the stroke and the font loosen up.
`Scene()` applies it; `Scene(sketch=False)` gives the old corporate-clean style (Helvetica, straight
lines) for the rare technical doc that must look like a spec.

**Layout** — group with translucent zones, stack in bands:
- A big rounded container per boundary (a subscription, a VPC, a system). Light fill `GREEN05`,
  `GREEN` border, brand/cloud logo in a corner.
- Inside, horizontal **bands** for layers (e.g. "Socle / plateforme" on top, "Applications" below),
  each a white/`GREEN20` rounded rect with a small `GREEN_DARK` label.
- Inside bands, a row of **cards** (`s.card`): one representative icon + a short title. For technical
  app boxes, add a small **icon row** of the underlying services at the bottom (`s.icon_row`).

**Arrows — keep them disciplined (this is the #1 thing that makes diagrams look messy):**
- One color: `BLUE_GREEN`.
- **Route orthogonally in the margins/gutters**, never diagonally across boxes. Use `arrowp` with
  right-angle points (e.g. `[(x1,y1),(xlane,y1),(xlane,y2),(x2,y2)]`).
- For external actors entering a container, prefer **short arrows to the system boundary at the
  height of their target**, and order the actors by target height so the arrows don't cross. Put a
  caption under the actor box instead of a long crossing arrow when the target is far.
- Labels sit on the longest (clearest) segment automatically; keep them short.

**Icons** — one clear icon per box; a row of 2–4 service icons under technical app boxes. Don't
overcrowd. The toolkit auto-trims transparent margins and downscales, so icons size uniformly.

## Composition rules — check these before you render

These come from the Excalidraw community's own best-practice guides, and they are not decoration:
a diagram of ours violated **seven of the eight** and that is exactly what made it look amateur.
Go through the list before delivering. Every one of them is mechanical.

| rule | what it means concretely |
|---|---|
| **Snap to a grid** | Every coordinate and every size is a multiple of 25 (ideally 50). Hand-tuned values like `44`, `46`, `34` are what makes a diagram look "composed by eye" — because it was. |
| **Nothing below 14px** | Title 26–30, zone title 22, box label 20, description 15–17, annotation 14. A 12px caption is unreadable on a projector and reads as clutter even when it isn't. |
| **Three accents, maximum** | One colour for the container, one per *opposing* idea. Everything else is grey (`#868E96`). A neutral is not an accent — and five accents means none of them signals anything. |
| **60-30-10** | Roughly 60% white space. Tint only the zones that genuinely oppose each other; a container that holds other zones stays **white**, otherwise you stack three coloured fills and kill all contrast. |
| **Boxes ≥ 120×80** | A 620×48 strip is not a box, it's a bar. Give content boxes real height or merge them. |
| **Aspect ratio near 16∶9** | Target ~1800×1050. A 2400×780 canvas produces bands, not zones, and every slide that embeds it will letterbox it into illegibility. |
| **Consistent gaps** | Same spacing between siblings, same padding inside every zone. Pick two values (e.g. 25 inside, 50 between) and never improvise a third. |
| **No repeated element between siblings** | If all five boxes say "its own database", say it **once** in the zone subtitle. Fifteen identical chips is noise wearing the costume of information. |

The sketch style is the toolkit default. It loosens the stroke, never the grid: a hand-drawn diagram
with improvised coordinates looks careless, one on a 25px grid looks deliberate.

**Check your logo files too.** `s4-hana.png` shipped with a transparency checkerboard *baked into
the pixels* — someone had screenshotted an editor. It rendered as a grey grid behind the logo on
every diagram that used it. If a logo looks dirty on a white background, open it and check: the fix
is a flood-fill of light pixels from the edges (not a colour threshold, which would punch holes in
white lettering inside the mark).

## The house style: nested zones

This is the default for an architecture diagram, and what makes ours look designed rather than
drawn. Three rules, and they are worth more than any amount of extra content.

**1. One frame per level of nesting, one colour per level.** The reader must see the nesting before
reading a single label. Use `s.zone(...)` with `level=0,1,2…` (or an explicit `color`), which draws
a coloured border, a very light tint, and a centred title in the border's colour. The level palette
(`ZONE_LEVELS`) deliberately jumps hue — `NAVY → GREEN → AMBER → VIOLET → SKY` — because two
neighbouring greens carry no information.

**2. A logo sits ASTRIDE the frame's top edge.** `s.zone(..., logo="azure.png")` places it via
`s.badge()`, which paints a white pill under the logo so it interrupts the border. This is the
signature of the style: the logo belongs to the *boundary*, so it says what kind of place you are
entering. A logo dropped inside the box would just be more content.

**3. Beaucoup de vide.** What makes a diagram beautiful is what you leave out. Prefer one `s.chip()`
per idea over a stack of labelled rows, and never repeat the same chip across sibling boxes — if
all five applications have "its own database", say it *once* in the zone's subtitle.

```python
s.zone(90, 200, 1880, 560, "Notre compte Azure", color=NAVY, logo="azure.png",
       subtitle="tout ce qui suit est facturé et gouverné ici")
s.zone(134, 300, 470, 236, "L'ATELIER", color=GREEN, logo="azure-aca.png",
       subtitle="aujourd'hui")
s.chip(660, 424, 232, 68, "CRM")                      # the elementary brick
s.logo_strip(1000, 900, [("sap.png", "SAP"), ("powerbi.png", "Power BI")])
```

**When NOT to nest.** Two things that are *not* inside each other must not be drawn inside each
other. The Fabric diagram is the canonical case: the Microsoft 365 tenant and the Azure
subscription are two separate frames side by side, joined by one arrow — drawing them nested would
tell the reader that moving the bill moves the data, which is exactly the fear you are trying to
kill.

**Colour comes in pairs.** `ZONE_TINTS` maps every frame colour to its fill, and the pairs are
lifted from Excalidraw's own palette rather than invented — a saturated border with a light fill of
the same family. That pairing is what makes a render read as *Excalidraw* rather than as PowerPoint.
An earlier version used near-white tints (`#F2F7F2`) and the zones stopped separating from the page
at all: a frame is read by its border, but its fill still has to exist.

**Vertical rhythm is a constant, not a judgement call.** `ZONE_TITLE_Y=28`, `ZONE_SUB_Y=64`,
`ZONE_HEAD=110`, `ZONE_PAD=25`. Every zone starts its content at `y + ZONE_HEAD`, so sibling zones
align horizontally without anyone computing it. Placing the first element by eye in each zone is the
most visible — and least conscious — symptom of an improvised composition.

**Zone sizing gotchas the toolkit handles for you** — all three were real defects caught by looking
at a render, never by re-reading code:
- A wide logotype (SAP S/4 HANA, Microsoft: 4–6∶1 ratios) produced a badge three times wider than a
  square icon and covered the centred title. `badge(..., max_w=132)` caps the pill's *width* and
  shrinks the height to match.
- **Badge placement follows the zone's width.** Wide zone (≥600px): badge in the top-left corner,
  title centred normally — the badge is far from the centre and does not collide. Narrow zone: there
  is no room for both side by side, so the badge **centres itself** on the top edge and the title
  stays centred underneath. An intermediate version pushed the title to the right of the badge
  instead, and the resulting off-centre alignment was the first thing anyone noticed.

## Logos & icons

Logos resolve from the shared Snetor asset set (the sibling `snetor-html-slides` skill), so there's a
single source of truth — or from `$SNETOR_LOGO_DIR` if you set it. List what's available:

```bash
python <THIS-SKILL>/scripts/excalidraw_snetor.py     # prints search dirs + all logo names
```

Catalog with suggested uses (Azure services, vendors, AI, brand): `references/logo-catalog.md`.
If a needed logo is missing, add it to `snetor-html-slides/assets/logos/` (PNG, transparent
background) — both skills then pick it up.

## Gotchas

- **Build files small/legible**: design for ~700–1400px wide; `fontSize` ≥ 12 for body, ≥ 14 titles.
- **A WebP saved as `.png`** is handled (the toolkit normalizes to real PNG on embed) — but fix the
  source file name when you can.
- **Bound labels** (`boxlabel`) re-center automatically in Excalidraw; standalone `text` does not —
  position standalone text by its left edge (or pass `align="center"` + a width).
- **Don't reopen the `.excalidraw` to "verify" by reading JSON** — render the PNG and look.
- **Windows paths**: when adding `scripts/` to `sys.path`, use a Windows-style path (`C:/...` or
  `C:\\...`), not a Git-Bash `/c/...` path — Python on Windows won't find the module otherwise. The
  skill base directory you're given is already Windows-style.
