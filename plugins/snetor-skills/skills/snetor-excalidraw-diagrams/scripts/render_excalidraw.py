#!/usr/bin/env python3
"""Rend un `.excalidraw` en PNG avec le VRAI moteur Excalidraw (police Excalifont, trait a
main levee), dans Edge headless via Playwright.

Pourquoi a cote de render_preview.py : l'apercu maison dessine en police systeme et en trait
droit. Il suffit pour chasser les chevauchements, pas pour juger la direction artistique
« brouillon propre ». Ce script-ci est le rendu de reference.

    python render_excalidraw.py schema.excalidraw schema.png

Prerequis : `pip install playwright` et Microsoft Edge (present sur les postes Snetor).
Le moteur est charge depuis cdn.jsdelivr.net et esm.sh ; la scene reste locale, rien n'est
envoye. Hors reseau, se replier sur render_preview.py.
"""
import base64
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

VERSION = "0.18.0"
HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<script>window.EXCALIDRAW_ASSET_PATH="https://cdn.jsdelivr.net/npm/@excalidraw/excalidraw@{VERSION}/dist/prod/";</script>
<script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script>
</head><body><script type="module">
import * as X from "https://esm.sh/@excalidraw/excalidraw@{VERSION}?bundle";
window.X = X; window.ready = true;
</script></body></html>"""

EXPORT = """async (s) => {
    const blob = await window.X.exportToBlob({
        elements: s.elements, files: s.files || {},
        appState: {exportBackground: true, viewBackgroundColor: "#ffffff", exportScale: 2},
        mimeType: "image/png", exportPadding: 24});
    const buf = new Uint8Array(await blob.arrayBuffer());
    let bin = ""; for (const c of buf) bin += String.fromCharCode(c);
    return btoa(bin);
}"""


def render(src, dst):
    scene = json.loads(Path(src).read_text(encoding="utf-8"))
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page()
        page.set_content(HTML)
        page.wait_for_function("window.ready === true", timeout=90000)
        Path(dst).write_bytes(base64.b64decode(page.evaluate(EXPORT, scene)))
        browser.close()
    print(f"render -> {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: render_excalidraw.py <in.excalidraw> <out.png>")
    render(sys.argv[1], sys.argv[2])
