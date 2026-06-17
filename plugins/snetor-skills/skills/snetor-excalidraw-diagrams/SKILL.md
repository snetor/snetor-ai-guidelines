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
python <THIS-SKILL>/scripts/render_preview.py 01-mon-architecture.excalidraw 01-mon-architecture.png
```

(The preview is a faithful *approximation* — clean flat render; the reference is Excalidraw itself.)

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
`GREEN05/10/20` (light fills/tints), `MUTED #4A5A6E` / `SUBTLE #7E8A9A` (secondary text). Clean lines
(`roughness=0`), not the sketchy hand-drawn look — Snetor diagrams are corporate-clean.

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
