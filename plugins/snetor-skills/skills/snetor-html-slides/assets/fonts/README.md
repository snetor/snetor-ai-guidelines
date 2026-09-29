# Raleway fonts — stand-alone mode

These files are used **only in stand-alone mode** (`references/standalone.md`).
In connected mode the deck loads Raleway from Google Fonts (`wght@300..900`) and these files are not
copied. `scripts/inline_deck.py --standalone` declares one `@font-face` per `Raleway-<Weight>.ttf`
found here: adding a weight means adding its file, nothing else.

| File | Weight | Use in the design system |
|---|---|---|
| `Raleway-Light.ttf` | 300 | the thin line of the closing signature |
| `Raleway-Regular.ttf` | 400 | body text (`p`, `li`, `.sources`, captions) |
| `Raleway-Medium.ttf` | 500 | subtitles (`.lead`, `.sd-sub`), tooltips |
| `Raleway-SemiBold.ttf` | 600 | headings (`h1`, `h2`, `.statement`, `.closing-title`) |
| `Raleway-Bold.ttf` | 700 | accents, micro-labels, figures (`h3`, `.eyebrow`, `.metric`, `.pill`) |
| `Raleway-ExtraBold.ttf` | 800 | key figures, a title used alone |
| `Raleway-Black.ttf` | 900 | a title used alone, sparingly |

A weight declared in the CSS without its file here is rendered as synthetic bold in stand-alone mode:
the browser thickens the nearest weight and the result is no longer Raleway. See
`references/css-system.md` → Type Scale.

## Provenance and licence

- **Font**: Raleway, version `4.026`
- **Copyright**: "Copyright 2010 The Raleway Project Authors (impallari@gmail.com)"
- **Licence**: SIL Open Font License 1.1 — <https://openfontlicense.org>
- **Upstream project**: <https://github.com/theleagueof/raleway>
- **Source of these files**: `ofl/raleway/Raleway[wght].ttf` in <https://github.com/google/fonts>,
  version `4.026`. That repository only ships the variable font; each static file here is one
  instance of it (`fontTools.varLib.instancer`, `wght` = 300 … 900). The seven files share the same
  version, the same 936 glyphs (Latin Extended included) and the same vertical metrics.

The font ships under the OFL, so it can be redistributed with the skill. That licence is **distinct
from the repository's MIT licence**: it applies only to the files in this folder. Its full text is
`OFL.txt`, copied verbatim from the same `google/fonts` folder.

## Checking a font file

```powershell
$b = [IO.File]::ReadAllBytes("Raleway-Regular.ttf")
($b[0..3] | % { $_.ToString("X2") }) -join ""            # must be 00010000 (TrueType)
([Text.Encoding]::ASCII.GetString($b) -replace "\x00","") -match "Raleway"
```
