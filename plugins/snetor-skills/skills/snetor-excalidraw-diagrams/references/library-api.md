# Toolkit API — `excalidraw_snetor.py`

Import after adding the skill's `scripts/` to `sys.path`:

```python
import sys; sys.path.insert(0, "<THIS-SKILL>/scripts")
from excalidraw_snetor import Scene, L, available_logos, PALETTE, \
    GREEN, GREEN_DARK, GREEN05, GREEN10, GREEN20, NAVY, BLUE_GRAY, BLUE_GREEN, EMERALD, \
    PASTEL, WHITE, MUTED, SUBTLE, BORDER
```

## Coordinate model

A single px canvas. `x,y` is the **top-left** of rectangles/images-bounding-box; for `text`, `x` is
the left edge. Helpers that take a center use `cx,cy`. Y grows downward.

## Palette constants

`GREEN #007D36` · `GREEN_DARK #006028` · `GREEN20/10/05` (tints) · `NAVY #152B47` ·
`BLUE_GRAY #293F52` · `BLUE_GREEN #2A5458` (arrows) · `EMERALD #168C74` (borders) ·
`PASTEL #8CCAAE` · `WHITE` · `MUTED #4A5A6E` · `SUBTLE #7E8A9A` · `BORDER #E0E5DF`.
Also `PALETTE` (a dict) for programmatic access.

## `Scene`

Create one per diagram, add elements in back-to-front order (later = on top), then `save`.

| Method | Purpose |
|---|---|
| `rect(x,y,w,h, fill="transparent", stroke=NAVY, sw=2, rounded=True, opacity=100)` | A rectangle / zone / container. |
| `text(x,y, txt, size=16, color=NAVY, align="left", w=None)` | Standalone text (titles, notes, captions). `\n` for multi-line. `align="center"` needs a width `w`. |
| `boxlabel(x,y,w,h, txt, fill=WHITE, stroke=EMERALD, size=16, color=NAVY, sw=2)` | Rectangle with an auto-centered **bound** label (re-centers in Excalidraw). |
| `image(cx,cy, target_h, name)` | Place a logo centered at `(cx,cy)`, scaled to `target_h` px (aspect preserved). `name` resolved via `L`. |
| `card(x,y,w,h, title, icon=None, fill=WHITE, stroke=EMERALD, size=14, color=NAVY, icon_h=44, icon_frac=0.30, title_frac=0.58)` | A box with an icon near the top and a centered multi-line title below. The workhorse for component boxes. |
| `icon_row(cx,y, icons, ih=24, gap=12)` | A horizontal, centered row of small icons — use under a technical app box to show its services. |
| `logo_box(x,y,w,h, logo, caption, ...)` | A box with a logo in the upper area and a caption below (good for external systems like SAP). |
| `arrow(x1,y1,x2,y2, color=BLUE_GREEN, label=None, sw=2, dashed=False)` | Straight arrow. |
| `arrowp(points, color=BLUE_GREEN, label=None, sw=2, dashed=False)` | Poly-line arrow through `points=[(x,y),...]`; label lands on the longest segment. Use for clean orthogonal routing. |
| `save(name)` | Write the `.excalidraw` (absolute path or relative to CWD); validates JSON; prints a summary. |

## Logo helpers

- `L(name)` → absolute path for a logo file name (searches the shared dirs / `$SNETOR_LOGO_DIR`).
  You normally pass the bare name to `image`/`card`/`icon_row`; they call `L` for you.
- `available_logos()` → sorted list of available file names.
- Run `python scripts/excalidraw_snetor.py` to print the search dirs and the full list.

## Recipes

**Container with two layered bands** (the standard architecture look):

```python
s.rect(300,120, 920,660, fill=GREEN05, stroke=GREEN, sw=3)          # boundary
s.text(322,134, "Abonnement Azure — DEV", size=18, color=GREEN_DARK)
s.image(1170,150, 40, "azure.png")
s.rect(330,190, 860,250, fill=WHITE, stroke=GREEN20)                # band 1: foundation
s.text(352,202, "Socle / plateforme", size=16, color=GREEN_DARK)
s.rect(330,480, 860,280, fill=GREEN10, stroke=NAVY)                 # band 2: applications
```

**A card with services row** (technical app box):

```python
x,y,w,h = 352,556,240,262
s.rect(x,y,w,h, fill=GREEN10, stroke=EMERALD)
s.image(x+w/2, y+58, 50, "twenty.png")
s.text(x+6, y+104, "rg-twenty-dev", size=15, color=NAVY, align="center", w=w-12)
s.icon_row(x+w/2, y+h-30, ["azure-aca.png","postgresql.png","redis.png","azure-acr.png"], ih=26)
```

**Clean orthogonal flow in a gutter** (don't cut diagonally across boxes):

```python
# external actor at left enters the container at its target's height:
s.arrowp([(260,589),(300,589)], color=BLUE_GREEN)                   # short, no crossing
# a routed internal flow:
s.arrowp([(1240,372),(1240,576)], color=BLUE_GREEN, label="Fabric → PIM")
```

See `scripts/example_diagram.py` for a full, runnable diagram.
