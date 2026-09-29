"""inline_deck.py: the deck gets the design-system CSS and navigation JS by injection, not by hand.

The model used to re-type the whole CSS block (about 78,000 characters) into every deck. A
transcription that long drifts, and costs minutes of output per deck. These tests pin the
contract that replaced it: the injected CSS is the asset file byte for byte, paths filled in.
"""
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parent.parent / "plugins/snetor-skills/skills/snetor-html-slides"
sys.path.insert(0, str(SKILL / "scripts"))

from inline_deck import CSS, JS, inline  # noqa: E402

DECK = """<!doctype html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Raleway" rel="stylesheet">
<style>/* @snetor-css */</style></head><body>
<main class="deck"><section class="slide cover active"></section></main>
<script>/* @snetor-nav-js */</script></body></html>"""


def test_connected_mode_injects_the_asset_files_with_paths_filled():
    out = inline(DECK, "my-deck", 'Plan "IA" — 2026', standalone=False)
    css = CSS.read_text(encoding="utf-8").replace("../assets/DECK_NAME/", "../assets/my-deck/")
    assert css in out
    assert JS.read_text(encoding="utf-8") in out
    assert "DECK_NAME" not in out and "@snetor-" not in out
    assert 'const DECK_TITLE = "Plan \\"IA\\" — 2026";' in out
    assert "@font-face" not in out


def test_standalone_mode_uses_local_paths_and_declares_every_shipped_weight():
    deck = DECK.replace(DECK.splitlines()[1] + "\n", "")
    out = inline(deck, "my-deck", "T", standalone=True)
    assert 'url("assets/my-deck/snetor_full_logo.png")' in out
    assert "../assets/" not in out
    shipped = sorted((SKILL / "assets/fonts").glob("Raleway-*.ttf"))
    assert out.count("@font-face") == len(shipped) >= 4
    assert out.index("@font-face") < out.index(":root")


def test_standalone_refuses_a_deck_that_still_links_google_fonts():
    with pytest.raises(ValueError, match="Google Fonts"):
        inline(DECK, "my-deck", "T", standalone=True)


@pytest.mark.parametrize("deck", [DECK.replace("/* @snetor-css */", ""),
                                  DECK.replace("</script>", "/* @snetor-nav-js */</script>")])
def test_a_missing_or_doubled_marker_is_refused(deck):
    with pytest.raises(ValueError, match="exactly once"):
        inline(deck, "my-deck", "T", standalone=False)


def test_a_slug_that_is_not_a_folder_name_is_refused():
    with pytest.raises(ValueError, match="slug"):
        inline(DECK, "../evil", "T", standalone=False)
