# snetor-skills

Snetor skills for everyone at Snetor, whatever their job: four skills a colleague outside the tech
team can use. Two **branded-visual generators** share the same brand assets (Raleway font,
green/navy palette, logos, service icons); one **business assistant** serves the sales reps; one
**app builder** helps a power user build a tool the tech team can deploy as is.

Developer routines (branch closing, lessons into guardrails, dead tests, artifact deployment) live
in the separate [`snetor-dev`](../snetor-dev/README.md) plugin, installed on developer workstations
only.

### Branded visuals

| Skill | Produces | Triggers on |
|---|---|---|
| **`snetor-html-slides`** | A self-contained animated `.html` presentation deck | slides, presentation, COMEX deck, pitch |
| **`snetor-excalidraw-diagrams`** | An editable `.excalidraw` diagram with embedded logos/icons (+ PNG preview) | architecture diagram, schéma, flow/network diagram |

### Business assistant

| Skill | Produces | Triggers on |
|---|---|---|
| **`snetor-travel-report`** | An English, Outlook-ready travel report drafted from a sales rep's dictation (any language) | travel report, rapport de voyage, compte rendu de visite, "today I visited…" |

### App builder

| Skill | Produces | Triggers on |
|---|---|---|
| **`snetor-app-artefact`** | A one-file business tool built to the platform contract (shared state, Entra identity, no personal data), its `app.json`, and the check that proves it | "outil métier", "app pour l'équipe", "dashboard partagé", "v2 of my tool" |

## Installation

### Via the marketplace (recommended)

```
/plugin marketplace add snetor/snetor-ai-guidelines
/plugin install snetor-skills@snetor-ai-guidelines
```

### Manually

```bash
git clone https://github.com/snetor/snetor-ai-guidelines.git
```

Then in Claude Code: `/plugin install` and select `plugins/snetor-skills`.

All skills auto-trigger from context; you can also invoke them explicitly from `/skills`.

> **Migration note (2.0.0):** the developer routines moved to `snetor-dev`, and
> `snetor-doc-vs-infra` left the org plugins. A developer who used them installs
> `snetor-dev@snetor-ai-guidelines` once; `scripts/deploy-claude.ps1` then keeps it up to date.

## Shared assets

The two **visual** skills (`snetor-html-slides` and `snetor-excalidraw-diagrams`) read the same
brand assets, maintained in **one place**:

- `skills/snetor-html-slides/assets/branding/` — Snetor logos, hero banner
- `skills/snetor-html-slides/assets/logos/` — technology / vendor / Azure service icons

`snetor-excalidraw-diagrams` references these logos (no duplication) — update a logo once and both
visual skills pick it up. `snetor-travel-report` is text-only and uses no brand assets.

## Updating

When a component pattern, layout improvement, or new logo is found:
1. Pull the latest `snetor-ai-guidelines`
2. Run `/reload-plugins` — the skills update automatically (they read from your local clone)

To contribute: edit the relevant skill under `skills/`, commit and push to `snetor-ai-guidelines`,
then other users pull and run `/reload-plugins`.

## Structure

```
snetor-skills/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── snetor-html-slides/          ← animated HTML decks
│   │   ├── SKILL.md
│   │   ├── assets/{branding,logos}/     ← shared brand assets (source of truth)
│   │   ├── assets/deck/                 ← design-system CSS + navigation JS
│   │   ├── scripts/inline_deck.py       ← injects them into a deck
│   │   └── references/
│   ├── snetor-excalidraw-diagrams/  ← architecture diagrams
│   │   ├── SKILL.md
│   │   ├── scripts/                     ← excalidraw builder + preview renderer
│   │   └── references/
│   └── snetor-travel-report/        ← sales travel reports
│       ├── SKILL.md
│       └── references/                  ← templates, glossaire, report-style
└── README.md
```
