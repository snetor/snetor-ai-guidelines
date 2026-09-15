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

# ------------------------------------------------------------------ zone accents
# Couleurs de CADRE pour les zones imbriquees. Le principe du style : une couleur
# par niveau d'imbrication, pour qu'on lise l'emboitement sans lire les titres.
#
# Elles doivent se distinguer AU PREMIER COUP D'OEIL : deux verts voisins ne
# donnent aucune information. Le vert et le navy Snetor ouvrent la serie, les
# trois suivantes sont des accents choisis pour trancher en teinte tout en
# restant sobres a cote de la charte.
# Accents repris du nuancier Excalidraw, pas inventes : ces teintes sont concues
# par paires (une bordure saturee, un fond tres clair de la meme famille) et
# c'est ce qui donne au rendu son air d'Excalidraw plutot que de PowerPoint.
AMBER="#E8590C"; VIOLET="#6741D9"; SKY="#1971C2"; CORAL="#E03131"
GRAY="#868E96"
ZONE_LEVELS = [NAVY, GREEN, AMBER, VIOLET, SKY]

# Fonds associes. Ils sont CLAIRS mais pas delaves : une premiere version tirait
# vers le blanc (#F2F7F2) et les zones ne se distinguaient plus du fond de page.
# Un cadre se lit d'abord par sa bordure, mais son fond doit quand meme exister.
ZONE_TINTS = {NAVY: "#F1F3F5", GREEN: "#EBFBEE", AMBER: "#FFF4E6",
              VIOLET: "#F3F0FF", SKY: "#E7F5FF", EMERALD: "#E6FCF5",
              BLUE_GREEN: "#E3FAFC", CORAL: "#FFF5F5", GRAY: "#F8F9FA"}

# ------------------------------------------------------------- rythme vertical
# Toutes les zones alignent leur contenu sur les MEMES offsets. Sans cette
# constante, chaque zone place son premier element a l'oeil et le schema perd
# son alignement horizontal — c'est le defaut le plus visible et le moins
# conscient d'une composition improvisee.
ZONE_TITLE_Y = 28      # ligne de base du titre, depuis le bord haut
ZONE_SUB_Y = 64        # ligne de base du sous-titre
ZONE_HEAD = 110        # ou commence le contenu d'une zone titree
ZONE_PAD = 25          # marge interne laterale, partout


def zone_color(level):
    """Couleur de cadre pour un niveau d'imbrication (0 = le plus exterieur)."""
    return ZONE_LEVELS[level % len(ZONE_LEVELS)]

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

    # ===================================================================== zones
    # Le style "cadres imbriques" : un contenant par niveau, une couleur par
    # niveau, un logo pose A CHEVAL sur le bord superieur pour dire de quelle
    # technologie releve la zone. C'est ce chevauchement qui fait lire le
    # schema comme une carte plutot que comme un tableau — le logo appartient
    # a la frontiere, pas au contenu.

    def zone(self, x, y, w, h, title=None, color=None, level=0, logo=None,
             logo_h=38, size=17, tint=True, sw=2.5, subtitle=None, logo_x=56):
        """Un cadre de zone : bordure coloree, fond tres clair, titre centre en haut,
        logo optionnel a cheval sur le bord superieur gauche.

        color prime sur level. Retourne (x, y, w, h) pour chainer les zones filles.
        """
        c = color or zone_color(level)
        fill = ZONE_TINTS.get(c, "#F7F8F9") if tint else "transparent"
        self.rect(x, y, w, h, fill=fill, stroke=c, sw=sw)
        # Le badge occupe le coin superieur gauche : on centre le titre sur ce
        # qui RESTE a sa droite, sinon il passe dessous des que la zone est
        # etroite. Sur une zone large le decalage est imperceptible.
        # Placement du badge selon la largeur, et c'est la seule facon propre :
        #  - zone LARGE  : badge au coin haut-gauche, titre centre normalement.
        #    Le badge est loin du centre, il ne gene pas.
        #  - zone ETROITE : pas la place de mettre les deux cote a cote. Le badge
        #    se CENTRE sur le bord haut et le titre reste centre dessous. Decaler
        #    le titre a droite, comme dans une version precedente, donnait un
        #    alignement de travers visible au premier coup d'oeil.
        etroite = w < 600
        if logo and etroite:
            logo_x = w / 2
        tx, tw = x + ZONE_PAD, w - 2 * ZONE_PAD
        if title:
            self.text(tx, y + ZONE_TITLE_Y, title, size=size, color=c,
                      align="center", w=tw)
        if subtitle:
            self.text(tx, y + ZONE_SUB_Y, subtitle, size=max(14, int(size * 0.68)),
                      color=SUBTLE, align="center", w=tw)
        if logo:
            # logo_x doit laisser la pastille blanche ENTIEREMENT a droite du coin :
            # a 34 px elle debordait dans la marge et donnait un schema qui bave.
            self.badge(x + logo_x, y, logo, logo_h)
        return (x, y, w, h)

    def badge(self, cx, cy, logo, logo_h=38, pad=9, max_w=132):
        """Un logo pose a cheval sur une bordure, avec une pastille blanche dessous
        qui interrompt le trait. A utiliser sur le bord superieur d'une zone.

        max_w plafonne la LARGEUR de la pastille. Sans ce plafond, un logotype
        allonge (SAP S/4 HANA, Microsoft : des ratios de 4 a 6 pour 1) produit a
        hauteur egale une pastille trois fois plus large que celle d'une icone
        carree, qui vient recouvrir le titre centre de la zone. On reduit alors la
        hauteur pour tenir dans le plafond : mieux vaut un logo un peu plus petit
        qu'un titre illisible."""
        im = _prep(L(logo)); w0, h0 = im.size
        w = logo_h * w0 / h0
        if w > max_w:
            logo_h = logo_h * max_w / w
            w = max_w
        self.rect(cx - w / 2 - pad, cy - logo_h / 2 - pad,
                  w + 2 * pad, logo_h + 2 * pad,
                  fill=WHITE, stroke="transparent", sw=1, rounded=True)
        return self.image(cx, cy, logo_h, logo)

    def chip(self, x, y, w, h, label, logo=None, color=NAVY, size=15, fill=WHITE,
             logo_h=22, sw=2):
        """La brique elementaire du style : boite arrondie, bordure fine coloree,
        libelle centre, petit logo optionnel a gauche du texte."""
        self.rect(x, y, w, h, fill=fill, stroke=color, sw=sw)
        if logo:
            im = _prep(L(logo)); lw = logo_h * im.size[0] / im.size[1]
            tw = len(label) * size * 0.52
            bloc = lw + 10 + tw
            lx = x + (w - bloc) / 2
            self.image(lx + lw / 2, y + h / 2, logo_h, logo)
            self.text(lx + lw + 10, y + h / 2 - size * 0.62, label, size=size, color=color)
        else:
            self.text(x + 8, y + h / 2 - size * 0.62, label, size=size, color=color,
                      align="center", w=w - 16)

    def actor(self, cx, cy, label, logo=None, logo_h=42, size=14, color=MUTED):
        """Un acteur externe : une icone et son nom dessous, sans cadre.
        Sert a poser l'utilisateur ou un systeme tiers en marge du schema."""
        if logo:
            self.image(cx, cy, logo_h, logo)
        self.text(cx - 70, cy + logo_h / 2 + 8, label, size=size, color=color,
                  align="center", w=140)

    def logo_strip(self, cx, y, entries, logo_h=40, gap=34, size=12, color=MUTED):
        """Une rangee centree de logos legendes — les sources de donnees d'un schema.
        `entries` est une liste de (nom_de_logo, legende)."""
        dims = []
        for name, _ in entries:
            im = _prep(L(name)); dims.append(logo_h * im.size[0] / im.size[1])
        cell = max(max(dims), 90) + gap
        total = cell * len(entries)
        x = cx - total / 2 + cell / 2
        for (name, cap), _wd in zip(entries, dims):
            self.image(x, y, logo_h, name)
            if cap:
                self.text(x - cell / 2 + 6, y + logo_h / 2 + 9, cap, size=size,
                          color=color, align="center", w=cell - 12)
            x += cell

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
