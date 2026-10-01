"""Check a business artifact against the Snetor app contract.

Usage: python check_artefact.py <page.html> [--fiche app.json] [--deploy]

Exit 0 when every axis passes, 1 otherwise. --deploy adds the gate the developer runs before the
image build: the store must be switched to "server". Standard library only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

STORE = Path(__file__).resolve().parent.parent / "assets/snetor-store.js"
BLOCK = re.compile(r"/\* snetor-store:begin.*?/\* snetor-store:end \*/", re.S)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.(?!(?:png|jpe?g|gif|svg|webp|js|css)\b)[a-z]{2,}", re.I)
# ponytail: a bare 10-digit run is a code or an amount far more often than a phone; it is not flagged.
PHONE = re.compile(r"(?<![\w.])(?:\+\d{2,3}[ .-]?\d(?:[ .-]?\d{2}){4}|0[1-9](?:[ .-]\d{2}){4})(?![\w.])")
AXES = [
    ("persistence", re.compile(r"localStorage|sessionStorage|indexedDB")),
    ("authentication", re.compile(r"type\s*=\s*[\"']?password|crypto\.subtle")),
    ("external calls", re.compile(r"(?:fetch|open)\(\s*[\"'`]https?://|new\s+WebSocket\(")),
    ("distribution", re.compile(r"documentElement\.outerHTML")),
]
KEY_USE = re.compile(r"snetorStore\.(?:load|save)\(\s*[\"'`]([^\"'`]*)[\"'`]")
KEY_OK = re.compile(r"[a-z0-9_-]{1,40}")


def check(html, fiche=None, deploy=False):
    """-> [(axis, ok, detail)]"""
    blocks = BLOCK.findall(html)
    body = BLOCK.sub("", html)
    results = []

    personal, scan = [], body
    for e in (fiche or {}).get("exceptions", []):
        found = scan.count(e["text"])
        if found != e["count"]:
            personal.append(f"exception '{e['text']}': {found} found, {e['count']} decided")
        scan = scan.replace(e["text"], "")
    personal += [f"email {m}" for m in EMAIL.findall(scan)] + [f"phone {m}" for m in PHONE.findall(scan)]
    results.append(("personal data", not personal, personal))

    for axis, pattern in AXES:
        hits = sorted(set(pattern.findall(body)))
        results.append((axis, not hits, hits))

    if len(blocks) > 1:
        results.append(("store", False, [f"{len(blocks)} store blocks, expected one"]))
    bad_keys = sorted({k for k in KEY_USE.findall(body) if not KEY_OK.fullmatch(k)})
    results.append(("state keys", not bad_keys, [f"'{k}': use a-z 0-9 _ - only, 40 max" for k in bad_keys]))

    if deploy:
        server = len(blocks) == 1 and 'SNETOR_MODE = "server"' in blocks[0]
        results.append(("mode", server, [] if server else ['set SNETOR_MODE = "server" in the store block']))
    return results


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("page", type=Path)
    p.add_argument("--fiche", type=Path)
    p.add_argument("--deploy", action="store_true")
    a = p.parse_args(argv)
    fiche = json.loads(a.fiche.read_text(encoding="utf-8")) if a.fiche else None
    results = check(a.page.read_text(encoding="utf-8"), fiche, a.deploy)
    for axis, ok, detail in results:
        print(f"{'ok   ' if ok else 'FAIL '} {axis}" + ("" if ok else ": " + "; ".join(map(str, detail[:5]))))
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
