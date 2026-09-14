# Raleway fonts — stand-alone mode

These four files are used **only in stand-alone mode** (`references/standalone.md`).
In connected mode the deck loads Raleway from Google Fonts and these files are not copied.

| File | Weight | Use in the design system |
|---|---|---|
| `Raleway-Regular.ttf` | 400 | body text (`p`, `li`, `.sources`, captions) |
| `Raleway-Medium.ttf` | 500 | subtitles (`.lead`, `.sd-sub`), tooltips |
| `Raleway-SemiBold.ttf` | 600 | headings (`h1`, `h2`, `.statement`, `.closing-title`) |
| `Raleway-Bold.ttf` | 700 | accents, micro-labels, figures (`h3`, `.eyebrow`, `.metric`, `.pill`) |

These four weights are the **only** ones the design system allows, in stand-alone mode as well as in
connected mode. A `font-weight:800` / `900` has no matching font file: the browser thickens the 700
into synthetic bold and the result is no longer Raleway. Adding an ExtraBold requires the font file
**and** the `800` in the Google Fonts URL — see `references/css-system.md` → Type Scale.

## Provenance and licence

- **Font**: Raleway, version `4.026`
- **Copyright**: "Copyright 2010 The Raleway Project Authors (impallari@gmail.com)"
- **Licence**: SIL Open Font License 1.1 — <https://openfontlicense.org>
- **Upstream project**: <https://github.com/impallari/Raleway>

The font ships under the OFL, so it can be redistributed with the skill. That licence is **distinct
from the repository's MIT licence**: it applies only to the files in this folder.

> ⚠️ **To be completed**: the OFL requires the full licence text to accompany redistributed font
> files. Fetch `OFL.txt` from the official Raleway release and drop it here.
> Do not retype it from memory — it is a legal text and must be copied verbatim.

## Checking a font file

```powershell
$b = [IO.File]::ReadAllBytes("Raleway-Regular.ttf")
($b[0..3] | % { $_.ToString("X2") }) -join ""            # must be 00010000 (TrueType)
([Text.Encoding]::ASCII.GetString($b) -replace "\x00","") -match "Raleway"
```
