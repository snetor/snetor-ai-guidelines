# Excalidraw format — what you need to know

## Why images can't go through the MCP `create_view`

The Excalidraw MCP tool `create_view` renders an animated preview but only supports
`rectangle`, `ellipse`, `diamond`, `arrow`, `text`. It does **not** render `image` elements — so it
cannot show real logos/icons. (It also can't render emoji.)

The Excalidraw **file format**, however, fully supports images. So to get logos, we generate a real
`.excalidraw` file (which opens on excalidraw.com / the VS Code Excalidraw extension) rather than
using `create_view`. The toolkit (`scripts/excalidraw_snetor.py`) does this for you — you should not
need to hand-write this JSON.

## Scene file shape

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [ ... ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": null },
  "files": { "<fileId>": { "mimeType": "image/png", "id": "<fileId>",
                           "dataURL": "data:image/png;base64,...." } }
}
```

## Image elements (the logo mechanism)

An image is two parts that must agree on a `fileId`:

1. An element in `elements`:
   ```json
   { "type": "image", "id": "...", "x": .., "y": .., "width": .., "height": ..,
     "fileId": "<sha1>", "status": "saved", "scale": [1,1], "crop": null,
     "strokeColor": "transparent", "backgroundColor": "transparent" }
   ```
2. An entry in `files` keyed by that same `fileId`, holding the base64 `dataURL`.

The toolkit uses the image bytes' SHA-1 as the `fileId`, so the same logo embeds once and is reused.
Before embedding it **normalizes to PNG** (handles a WebP mislabeled `.png`), **trims transparent
margins** (so every icon sizes uniformly), and **downscales to ≤256px** (keeps files small — icons
display at ~30–40px anyway).

## Common element fields

Every element needs: `type`, `id` (unique), `x`, `y`, `width`, `height`, plus the usual
`angle, strokeColor, backgroundColor, fillStyle, strokeWidth, strokeStyle, roughness, opacity,
groupIds, frameId, roundness, seed, version, versionNonce, isDeleted, boundElements, updated, link,
locked`. The toolkit fills sensible defaults (`roughness=0` for clean lines, `fontFamily=2`
Helvetica, rounded rectangles).

- **Text**: `text`, `originalText`, `fontSize`, `fontFamily` (1=hand-drawn, 2=normal, 3=mono),
  `textAlign`, `verticalAlign`, `lineHeight`. `x` is the LEFT edge of the text box.
- **Bound text** (a label centered in a shape): a `text` element with `containerId` pointing at the
  shape, and the shape's `boundElements: [{"type":"text","id":<textId>}]`. Excalidraw re-centers it
  when the shape moves. The toolkit's `boxlabel` does this.
- **Arrow**: `points` are `[dx,dy]` offsets relative to the element's `x,y`; `endArrowhead:"arrow"`;
  `roundness:{type:2}`. For a poly-line, give multiple points. The toolkit's `arrow`/`arrowp` handle
  this and attach labels.

## Coordinates

A single global canvas in px; no required viewport. Design for an inline display width of roughly
700–1400px. The preview renderer auto-crops to content + padding. Leave ≥ 20–30px gaps between
elements; keep `fontSize` ≥ 12 (body) / ≥ 14 (titles) so it stays legible when scaled down.
