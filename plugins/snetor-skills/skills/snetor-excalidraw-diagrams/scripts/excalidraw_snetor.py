#!/usr/bin/env python3
"""
Snetor Excalidraw builder — a small toolkit to compose branded `.excalidraw` diagrams
with embedded logos/icons.

Why a library (and not the Excalidraw MCP `create_view`): that tool renders an animated
preview but CANNOT display image/PNG elements. The `.excalidraw` *format* itself supports
images (an `image` element + a base64 entry in the `files` map), so we build the scene as a
real `.excalidraw` file — self-contained and editable on excalidraw.com or the VS Code
"Excalidraw" extension.

Usage (from a build script you write in the output folder):

    import sys
    sys.path.insert(0, "<skill>/scripts")        # the skill's scripts/ dir
    from excalidraw_snetor import Scene, GREEN, NAVY, BLUE_GREEN, GREEN05, GREEN10, EMERALD

    s = Scene()
    s.image(120, 52, 46, "snetor_full_logo.png")            # header logo (branding)
    s.text(300, 30, "My title", size=27, color=NAVY)
    s.card(352, 240, 156, 180, "Twenty\n(CRM)", icon="twenty.png",
           fill=GREEN10, stroke=EMERALD)
    s.arrow(250, 207, 330, 285, color=BLUE_GREEN, label="HTTPS")
    s.save("my-diagram.excalidraw")                          # writes next to the script

Then render a PNG preview with render_preview.py and LOOK at it before delivering.

Logos resolve from the shared Snetor asset folders (the sibling `snetor-html-slides` skill),
or from $SNETOR_LOGO_DIR if set. See logo-catalog.md / available_logos().
"""
import base64, json, hashlib, io, time, random, os
from PIL import Image

# ----------------------------------------------------------------------------- paths / logos
HERE = os.path.dirname(os.path.abspath(__file__))                 # .../snetor-excalidraw-diagrams/scripts
SKILL_ROOT = os.path.dirname(HERE)                                # .../snetor-excalidraw-diagrams
SKILLS_DIR = os.path.dirname(SKILL_ROOT)                          # .../skills
_SHARED = os.path.join(SKILLS_DIR, "snetor-html-slides", "assets")
# Search order: $SNETOR_LOGO_DIR (if set), then shared logos/ then branding/.
LOGO_DIRS = [d for d in [os.environ.get("SNETOR_LOGO_DIR"),
                         os.path.join(_SHARED, "logos"),
                         os.path.join(_SHARED, "branding")] if d]
OUT = os.getcwd()           # save() writes here unless an absolute path is given
MAXPX = 256                 # icons display ~30-40px; cap source for small files + uniform sizing

def L(name):
    """Resolve a logo/icon file name to an absolute path across the search dirs."""
    if os.path.isabs(name) and os.path.exists(name):
        return name
    for d in LOGO_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        f"Logo '{name}' not found in {LOGO_DIRS}. Run available_logos() to list, "
        f"or set $SNETOR_LOGO_DIR.")

def available_logos():
    """Sorted list of available logo/icon file names (deduplicated across search dirs)."""
    seen = {}
    for d in LOGO_DIRS:
        if d and os.path.isdir(d):
            for f in os.listdir(d):
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".svg")):
                    seen.setdefault(f, d)
    return sorted(seen)

# ----------------------------------------------------------------------------- Snetor palette
GREEN="#007D36"; GREEN_DARK="#006028"; GREEN20="#CCE0CD"; GREEN10="#E5EFE5"; GREEN05="#F2F7F2"
NAVY="#152B47"; BLUE_GRAY="#293F52"; BLUE_GREEN="#2A5458"; EMERALD="#168C74"; PASTEL="#8CCAAE"
WHITE="#FFFFFF"; MUTED="#4A5A6E"; SUBTLE="#7E8A9A"; BORDER="#E0E5DF"
PALETTE = dict(green=GREEN, green_dark=GREEN_DARK, green20=GREEN20, green10=GREEN10,
               green05=GREEN05, navy=NAVY, blue_gray=BLUE_GRAY, blue_green=BLUE_GREEN,
               emerald=EMERALD, pastel=PASTEL, white=WHITE, muted=MUTED, subtle=SUBTLE,
               border=BORDER)

def _rid():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=20))
def _nonce(): return random.randint(1, 2**31)
def _now(): return int(time.time()*1000)

def _prep(path):
    """Open, normalize to RGBA, trim transparent margins, downscale to MAXPX. Returns a PIL image.
    Handles any format incl. a WebP mislabeled '.png'."""
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    if bbox: im = im.crop(bbox)
    w, h = im.size; m = max(w, h)
    if m > MAXPX:
        sc = MAXPX/m; im = im.resize((max(1, int(w*sc)), max(1, int(h*sc))), Image.LANCZOS)
    return im


class Scene:
    """Accumulates Excalidraw elements + embedded image files, then writes a `.excalidraw`."""
    def __init__(self):
        self.elements = []; self.files = {}

    def _base(self, **kw):
        d = dict(angle=0, strokeColor=NAVY, backgroundColor="transparent", fillStyle="solid",
                 strokeWidth=2, strokeStyle="solid", roughness=0, opacity=100, groupIds=[],
                 frameId=None, roundness=None, seed=_nonce(), version=1, versionNonce=_nonce(),
                 isDeleted=False, boundElements=None, updated=_now(), link=None, locked=False)
        d.update(kw); return d

    def rect(self, x, y, w, h, fill="transparent", stroke=NAVY, sw=2, rounded=True, opacity=100):
        e = self._base(type="rectangle", id=_rid(), x=x, y=y, width=w, height=h,
                       backgroundColor=fill, strokeColor=stroke, strokeWidth=sw, opacity=opacity,
                       roundness={"type": 3} if rounded else None)
        self.elements.append(e); return e

    def text(self, x, y, txt, size=16, color=NAVY, align="left", w=None):
        """Standalone text. x is the LEFT edge; for centered text within a width, pass align and w."""
        h = int(size*1.25*(txt.count("\n")+1))
        if w is None:
            w = int(max(len(line) for line in txt.split("\n"))*size*0.55)
        e = self._base(type="text", id=_rid(), x=x, y=y, width=w, height=h, strokeColor=color,
                       text=txt, originalText=txt, fontSize=size, fontFamily=2, textAlign=align,
                       verticalAlign="top", lineHeight=1.25, autoResize=True, containerId=None)
        self.elements.append(e); return e

    def boxlabel(self, x, y, w, h, txt, fill=WHITE, stroke=EMERALD, size=16, color=NAVY, sw=2):
        """Rectangle with auto-centered bound text (the label re-centers if you move it in Excalidraw)."""
        r = self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw)
        tid = _rid(); th = int(size*1.25*(txt.count("\n")+1))
        t = self._base(type="text", id=tid, x=x+8, y=y+h/2-th/2, width=w-16, height=th,
                       strokeColor=color, text=txt, originalText=txt, fontSize=size, fontFamily=2,
                       textAlign="center", verticalAlign="middle", lineHeight=1.25,
                       autoResize=False, containerId=r["id"])
        r["boundElements"] = [{"type": "text", "id": tid}]
        self.elements.append(t); return r

    def image(self, cx, cy, target_h, name):
        """Place an icon centered at (cx,cy), scaled to target_h px (aspect preserved).
        `name` is a logo file name (resolved via L) or an absolute path."""
        im = _prep(L(name)); w0, h0 = im.size
        buf = io.BytesIO(); im.save(buf, format="PNG"); data = buf.getvalue()
        fid = hashlib.sha1(data).hexdigest()
        if fid not in self.files:
            self.files[fid] = {"mimeType": "image/png", "id": fid,
                               "dataURL": "data:image/png;base64," + base64.b64encode(data).decode(),
                               "created": _now(), "lastRetrieved": _now()}
        h = target_h; w = target_h*w0/h0
        e = self._base(type="image", id=_rid(), x=cx-w/2, y=cy-h/2, width=w, height=h,
                       strokeColor="transparent", backgroundColor="transparent",
                       fileId=fid, status="saved", scale=[1, 1], crop=None)
        self.elements.append(e); return e

    def card(self, x, y, w, h, title, icon=None, fill=WHITE, stroke=EMERALD, size=14, color=NAVY,
             icon_h=44, icon_frac=0.30, title_frac=0.58):
        """A box with an icon near the top and a centered multi-line title below it."""
        self.rect(x, y, w, h, fill=fill, stroke=stroke)
        if icon: self.image(x+w/2, y+h*icon_frac, icon_h, icon)
        self.text(x+6, y+h*title_frac, title, size=size, color=color, align="center", w=w-12)

    def icon_row(self, cx, y, icons, ih=24, gap=12):
        """A horizontal, centered row of small icons (e.g. the services inside an app box)."""
        dims = []
        for name in icons:
            im = _prep(L(name)); dims.append(ih*im.size[0]/im.size[1])
        total = sum(dims)+gap*(len(icons)-1); x = cx-total/2
        for name, wd in zip(icons, dims):
            self.image(x+wd/2, y, ih, name); x += wd+gap

    def logo_box(self, x, y, w, h, logo, caption, fill=WHITE, stroke=EMERALD, size=15, color=NAVY,
                 logo_h=34):
        """A box with a logo in the upper area and a caption underneath (good for external systems)."""
        self.rect(x, y, w, h, fill=fill, stroke=stroke)
        self.image(x+w/2, y+h*0.36, logo_h, logo)
        self.text(x+8, y+h-size*1.6, caption, size=size, color=color, align="center", w=w-16)

    def arrow(self, x1, y1, x2, y2, color=BLUE_GREEN, label=None, sw=2, dashed=False):
        """A straight arrow from (x1,y1) to (x2,y2)."""
        e = self._base(type="arrow", id=_rid(), x=x1, y=y1, width=x2-x1, height=y2-y1,
                       strokeColor=color, strokeWidth=sw, strokeStyle="dashed" if dashed else "solid",
                       points=[[0, 0], [x2-x1, y2-y1]], lastCommittedPoint=None, startBinding=None,
                       endBinding=None, startArrowhead=None, endArrowhead="arrow", roundness={"type": 2})
        self.elements.append(e)
        if label: self._arrow_label(e, label, (x1+x2)/2, (y1+y2)/2, color)
        return e

    def arrowp(self, points, color=BLUE_GREEN, label=None, sw=2, dashed=False):
        """A poly-line arrow through `points` (list of (x,y)). Use orthogonal points to route cleanly
        in the margins/gutters instead of cutting diagonally across boxes."""
        x0, y0 = points[0]; rel = [[px-x0, py-y0] for px, py in points]
        e = self._base(type="arrow", id=_rid(), x=x0, y=y0,
                       width=max(p[0] for p in rel)-min(p[0] for p in rel),
                       height=max(p[1] for p in rel)-min(p[1] for p in rel),
                       strokeColor=color, strokeWidth=sw, strokeStyle="dashed" if dashed else "solid",
                       points=rel, lastCommittedPoint=None, startBinding=None, endBinding=None,
                       startArrowhead=None, endArrowhead="arrow", roundness={"type": 2})
        self.elements.append(e)
        if label:  # place on the midpoint of the LONGEST segment (its clearest run)
            best = 0; bi = 0
            for k in range(len(points)-1):
                dl = abs(points[k+1][0]-points[k][0])+abs(points[k+1][1]-points[k][1])
                if dl > best: best = dl; bi = k
            self._arrow_label(e, label, (points[bi][0]+points[bi+1][0])/2,
                              (points[bi][1]+points[bi+1][1])/2, color)
        return e

    def _arrow_label(self, e, label, mx, my, color):
        tid = _rid(); size = 14; tw = int(len(label)*size*0.55); th = int(size*1.25)
        t = self._base(type="text", id=tid, x=mx-tw/2, y=my-th-4, width=tw, height=th,
                       strokeColor=color, text=label, originalText=label, fontSize=size, fontFamily=2,
                       textAlign="center", verticalAlign="middle", lineHeight=1.25,
                       autoResize=False, containerId=None)
        self.elements.append(t)

    def save(self, name):
        """Write the `.excalidraw` file (validates it round-trips as JSON). Returns the path."""
        scene = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
                 "elements": self.elements,
                 "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": self.files}
        path = name if os.path.isabs(name) else os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scene, f, ensure_ascii=False, indent=1)
        json.load(open(path, encoding="utf-8"))
        print(f"OK {os.path.basename(path)}: {len(self.elements)} elements, {len(self.files)} images -> {path}")
        return path


if __name__ == "__main__":
    print("Logo search dirs:")
    for d in LOGO_DIRS: print("  ", d, "(exists)" if os.path.isdir(d) else "(missing)")
    print(f"\n{len(available_logos())} logos available:")
    print("  " + "  ".join(available_logos()))
