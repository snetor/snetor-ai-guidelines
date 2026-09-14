# Snetor HTML Slides — Stand-alone mode (offline)

By default a Snetor deck loads three things from the internet: the **Raleway** font (Google Fonts),
the **Phosphor** icons, and if needed **Chart.js** / **jsvectormap**. Offline, all of that falls
over: the deck renders in a system font, without icons, and the charts stay empty.

This document describes how to produce a deck that **depends on no network**.

---

## 1. When to switch to stand-alone

Switch as soon as one of these is true:

- the user says **stand-alone**, **autonome**, **hors ligne**, **offline**, **sans internet**,
  **package**, or asks for a deck **to send by e-mail** / **à envoyer par mail** ;
- the deck will be shown at a **customer / supplier** site, or in a room whose Wi-Fi is not
  guaranteed;
- the deck must be **archived** and stay readable years from now (CDNs move, URLs die);
- the deck leaves the Snetor perimeter (external sharing, tender annex).

When in doubt, ask the question in Step 1 of the wizard (see `SKILL.md`, question 5).

> **A deck for a meeting on Snetor premises does not need stand-alone mode.** Do not turn it on by
> default: it costs a heavier assets folder and it rules out Chart.js charts.

---

## 2. Two levels

| Level | What it is | When |
|---|---|---|
| **L1 — self-contained package** *(default)* | 1 `.html` file + an **adjacent** `assets/` folder. Zero network calls. Copies and zips as one block. | Common case. Offline presentation, archiving. |
| **L2 — single file** | Everything is `base64`-encoded **inside** the HTML. One file, nothing around it. | Sending by e-mail, uploading to a tool that accepts a single file only. |

**L1 is the default.** Only go to L2 if the user explicitly asks for *one single file*.
L2 inflates the HTML by roughly +33 % of the asset weight (the 4 fonts alone weigh ~740 kB in
base64): past ~5 MB the file becomes painful to open and to send.

---

## 3. Asset paths

In stand-alone mode the assets folder sits **next to the HTML**, not in the shared
`03-Outputs/assets/`. The deck and its assets form a pair that travels together.

```
03-Outputs/<folder>/
├── 2026-07-23 - My deck - Audience.html
└── assets/
    └── <deck-slug>/
        ├── snetor_full_logo.png
        ├── snetor_full_logo_reversed.png
        ├── Hero-banner-abstrait.jpg
        └── Raleway-*.ttf
```

In the CSS, paths therefore become `assets/<deck-slug>/…` (and not `../assets/<deck-slug>/…`):

```css
--logo: url("assets/<deck-slug>/snetor_full_logo.png");
--logo-reversed: url("assets/<deck-slug>/snetor_full_logo_reversed.png");
--hero: url("assets/<deck-slug>/Hero-banner-abstrait.jpg");
```

---

## 4. Fonts — replacing Google Fonts

**Delete** the three Google Fonts `<link>` tags from the `<head>`. **Copy** the four files from the
skill's `assets/fonts/` into the deck's assets folder, and **declare** the `@font-face` rules at the
top of the `<style>` block, before the `:root`:

```css
@font-face { font-family:"Raleway"; src:url("assets/<deck-slug>/Raleway-Regular.ttf")  format("truetype"); font-weight:400; font-display:swap; }
@font-face { font-family:"Raleway"; src:url("assets/<deck-slug>/Raleway-Medium.ttf")   format("truetype"); font-weight:500; font-display:swap; }
@font-face { font-family:"Raleway"; src:url("assets/<deck-slug>/Raleway-SemiBold.ttf") format("truetype"); font-weight:600; font-display:swap; }
@font-face { font-family:"Raleway"; src:url("assets/<deck-slug>/Raleway-Bold.ttf")     format("truetype"); font-weight:700; font-display:swap; }
```

The rest of the CSS is unchanged: `font-family: "Raleway", system-ui, …` keeps working.

> **Verified trap**: never remove the Google Fonts `<link>` without having declared the
> `@font-face` rules first. The deck silently falls back to a system font and nobody notices it
> before the meeting.

---

## 5. Icons — replacing Phosphor

The Phosphor CDN is forbidden in stand-alone mode. Two strategies, in order of preference:

**A. Do without icons** *(recommended)*. The design system components (`fact-card`, `card`,
`brick`, `phase`…) are built to work without icons: a figure, a title and a sentence are enough.
An airy deck loses little by having no icons.

**B. Inline SVG.** If iconography is indispensable, embed the SVGs directly in the markup.
Keep the `ph-icon` class to inherit the frame and the tones (`.navy`, `.teal`, dark-safe):

```html
<span class="ph-icon" aria-hidden="true">
  <svg viewBox="0 0 256 256" width="32" height="32" fill="currentColor">
    <path d="M128 24a104 104 0 1 0 104 104A104.1 104.1 0 0 0 128 24Z"/>
  </svg>
</span>
```

Fetch the paths from <https://phosphoricons.com> (MIT) at generation time, one per icon actually
used. Do not embed a whole icon font for three pictograms.

---

## 6. Charts — without a CDN

**By default: do not use Chart.js in stand-alone mode.** The design system ships purely CSS visuals
that cover most of the needs, and that are the preferred form for an airy deck anyway (see rule 28,
"default density"):

| Need | CSS component |
|---|---|
| Breakdown in a single bar | `.stacked` + `.legend` |
| Comparing a few values | `.impact-bars` |
| Executive cost / TCO | `macro cost-code` |
| One strong figure | `big-number` |
| 4 metrics | `market-facts` / `fact-card` |
| Sequence, milestones | `path`, `timeline`, `gantt`, `journey` |

**If a Chart.js chart really is indispensable** (deep-dive, radar, bubble matrix): download
`chart.umd.min.js` into the deck's assets folder and reference it locally.

```html
<script src="assets/<deck-slug>/chart.umd.min.js"></script>
```

The bootstrap and the lazy-init of `references/charts.md` are unchanged — including rule 22
(build inside `requestAnimationFrame` on slide activation). **jsvectormap / world-map is not
supported in stand-alone mode**: the base map loads from the network. Replace it with a country
list or a `market-strip`.

---

## 7. Level 2 — single file (base64)

On explicit request only. Encode each asset and inline it:

```css
@font-face { font-family:"Raleway"; src:url("data:font/ttf;base64,AAEAAA…") format("truetype"); font-weight:400; }
:root { --logo: url("data:image/png;base64,iVBORw0…"); }
```

Encoding (PowerShell):

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("path\to\asset.png")) | Set-Clipboard
```

Constraints to respect:
- images as `data:image/png;base64,` / `data:image/jpeg;base64,` ;
- fonts as `data:font/ttf;base64,` ;
- **compress the hero** before encoding (a 1920px banner is enough);
- announce the final weight to the user — past ~5 MB, offer to go back to L1.

---

## 8. Mandatory verification

A stand-alone deck is verified, never assumed. Three checks, in order:

**1. No network reference left.**

```powershell
Select-String -Path "<deck>.html" -Pattern "https?://" |
  Where-Object { $_.Line -notmatch 'rel="noreferrer"' }
```

Only clickable `href` links to internal applications are acceptable — they are deliberate and do
not block rendering. Any occurrence in `<link>`, `<script src>`, `@import` or `url()` is a defect.

**2. Every referenced asset exists on disk.**

```powershell
$html = "<deck>.html"; $dir = Split-Path $html
Select-String -Path $html -Pattern 'assets/[A-Za-z0-9._/-]+' -AllMatches |
  ForEach-Object { $_.Matches.Value } | Sort-Object -Unique |
  ForEach-Object { if (Test-Path (Join-Path $dir $_)) { "OK   $_" } else { "MISSING $_" } }
```

**3. Real rendering, network off.** Open the deck in Edge and check it visually: the font must be
Raleway (not a system font), and the logo and the hero must display. Headless:

```powershell
& $edge --headless=new --disable-gpu --window-size=1600,1000 --virtual-time-budget=4000 `
        --screenshot="out.png" "file:///…/<deck>.html?slide=1"
```

> Check 3 is not optional: checks 1 and 2 do not detect a badly declared font.

---

## 9. Summary of the deviations from normal mode

| `SKILL.md` rule | Normal mode | Stand-alone mode |
|---|---|---|
| Google Fonts | 3 `<link>` in the `<head>` | removed, replaced by 4 `@font-face` |
| 13 — CDN libs | Chart.js / jsvectormap via CDN | forbidden; Chart.js vendored if indispensable, jsvectormap unsupported |
| 19 — Phosphor | `<i class="ph ph-…">` via CDN | no icons, or inline SVG |
| Step 3 — paths | `../assets/<deck-slug>/` | `assets/<deck-slug>/` next to the HTML |
| 22 — chart lazy-init | unchanged | unchanged (if Chart.js is vendored) |

All the other rules apply unchanged.
