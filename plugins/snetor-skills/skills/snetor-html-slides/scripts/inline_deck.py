"""Inject the Snetor design-system CSS and navigation JS into a deck, in place.

The deck HTML carries two markers written by the model:
    <style>/* @snetor-css */</style>        in the <head>
    <script>/* @snetor-nav-js */ ...</script>  at the end of the <body>

Usage:
    python inline_deck.py <deck.html> --slug <deck-slug> --title "<deck title>" [--standalone]

Connected mode: asset URLs become ../assets/<slug>/ (the deck sits in slides/, assets beside it).
Stand-alone mode: asset URLs become assets/<slug>/, and one @font-face per Raleway file shipped in
assets/fonts/ is declared before the CSS. The Google Fonts <link> tags must already be gone.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CSS = SKILL / "assets" / "deck" / "snetor-deck.css"
JS = SKILL / "assets" / "deck" / "snetor-deck.js"
FONTS = SKILL / "assets" / "fonts"

CSS_MARKER = "/* @snetor-css */"
JS_MARKER = "/* @snetor-nav-js */"
WEIGHTS = {"Thin": 100, "ExtraLight": 200, "Light": 300, "Regular": 400, "Medium": 500,
           "SemiBold": 600, "Bold": 700, "ExtraBold": 800, "Black": 900}


def font_faces(slug):
    rules = []
    for ttf in sorted(FONTS.glob("Raleway-*.ttf"), key=lambda p: WEIGHTS.get(p.stem.split("-", 1)[1], 0)):
        weight = WEIGHTS.get(ttf.stem.split("-", 1)[1])
        if weight is None:
            continue  # italic or unknown face: not part of the system
        rules.append(f'@font-face {{ font-family:"Raleway"; src:url("assets/{slug}/{ttf.name}") '
                     f'format("truetype"); font-weight:{weight}; font-display:swap; }}')
    return "\n".join(rules) + "\n"


def inline(html, slug, title, standalone):
    for marker in (CSS_MARKER, JS_MARKER):
        count = html.count(marker)
        if count != 1:
            raise ValueError(f"expected the marker {marker} exactly once, found {count}")
    if standalone and "fonts.googleapis.com" in html:
        raise ValueError("stand-alone deck still links Google Fonts: remove the 3 <link> tags first")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", slug):
        raise ValueError(f"slug {slug!r} must be a plain folder name")

    prefix = f"assets/{slug}/" if standalone else f"../assets/{slug}/"
    css = CSS.read_text(encoding="utf-8").replace("../assets/DECK_NAME/", prefix)
    if "DECK_NAME" in css:
        raise ValueError("snetor-deck.css holds a DECK_NAME outside the ../assets/DECK_NAME/ pattern")
    if standalone:
        css = font_faces(slug) + css
    js = f"const DECK_TITLE = {json.dumps(title, ensure_ascii=False)};\n" + JS.read_text(encoding="utf-8")
    # str.replace, not re.sub: the CSS is full of backslashes and group-like sequences.
    return html.replace(CSS_MARKER, css).replace(JS_MARKER, js)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("deck", type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--standalone", action="store_true")
    args = parser.parse_args()
    html = args.deck.read_text(encoding="utf-8")
    try:
        out = inline(html, args.slug, args.title, args.standalone)
    except ValueError as err:
        sys.exit(f"inline_deck: {err}")
    args.deck.write_text(out, encoding="utf-8")
    print(f"inline_deck: {args.deck}: {len(html)} -> {len(out)} chars")


if __name__ == "__main__":
    main()
