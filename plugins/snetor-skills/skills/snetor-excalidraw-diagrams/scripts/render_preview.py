#!/usr/bin/env python3
"""Render a .excalidraw scene to PNG so you can SEE the layout and verify it before delivering.

This is an *approximation* (clean flat render, system font) — good enough to catch overlaps,
mis-routed arrows, missing icons. The reference rendering is Excalidraw itself.

Usage:  python render_preview.py <scene.excalidraw> <out.png>
"""
import json, base64, io, sys, os, math
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = r"C:\Windows\Fonts"
def font(size, bold=False):
    for cand in ([ "arialbd.ttf"] if bold else ["arial.ttf"]) + ["DejaVuSans.ttf"]:
        try: return ImageFont.truetype(os.path.join(FONT_DIR, cand) if not os.path.isabs(cand) else cand, size)
        except Exception: continue
    try: return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception: return ImageFont.load_default()

def _c(c):
    return None if (not c or c == "transparent") else c

def render(path, out):
    scene = json.load(open(path, encoding="utf-8"))
    els = scene["elements"]; files = scene.get("files", {})
    pad = 30
    minx = min(e["x"] for e in els)-pad; miny = min(e["y"] for e in els)-pad
    W = int(max(e["x"]+e.get("width", 0) for e in els)-minx+pad)
    H = int(max(e["y"]+e.get("height", 0) for e in els)-miny+pad)
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    TX = lambda x: int(x-minx); TY = lambda y: int(y-miny)
    for e in els:
        t = e["type"]; x = TX(e["x"]); y = TY(e["y"]); w = int(e.get("width", 0)); h = int(e.get("height", 0))
        if t == "rectangle":
            r = 12 if e.get("roundness") else 0
            d.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=_c(e.get("backgroundColor")),
                                outline=_c(e.get("strokeColor")), width=int(e.get("strokeWidth", 2)))
        elif t == "image":
            fid = e.get("fileId")
            if fid in files:
                im = Image.open(io.BytesIO(base64.b64decode(files[fid]["dataURL"].split(",", 1)[1]))).convert("RGBA")
                im = im.resize((max(1, w), max(1, h))); img.paste(im, (x, y), im)
        elif t == "text":
            size = int(e.get("fontSize", 16)); fo = font(size); col = _c(e.get("strokeColor")) or "#000"
            align = e.get("textAlign", "left"); lh = int(size*1.25)
            for i, line in enumerate(e.get("text", "").split("\n")):
                tw = d.textlength(line, font=fo)
                lx = x+(w-tw)/2 if align == "center" else (x+w-tw if align == "right" else x)
                d.text((lx, y+i*lh), line, fill=col, font=fo)
        elif t == "arrow":
            col = _c(e.get("strokeColor")) or "#000"
            pts = [(x+px, y+py) for px, py in e.get("points", [[0, 0], [w, h]])]
            for j in range(len(pts)-1):
                d.line([pts[j][0], pts[j][1], pts[j+1][0], pts[j+1][1]], fill=col, width=int(e.get("strokeWidth", 2)))
            (x1, y1), (x2, y2) = pts[-2], pts[-1]; ang = math.atan2(y2-y1, x2-x1)
            for da in (math.radians(150), math.radians(-150)):
                d.line([x2, y2, x2+12*math.cos(ang+da), y2+12*math.sin(ang+da)], fill=col, width=2)
    img.save(out); print(f"preview -> {out} ({W}x{H})")

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
