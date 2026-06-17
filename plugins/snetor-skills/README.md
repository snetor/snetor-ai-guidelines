# snetor-skills

Snetor-branded visuals for Claude Code. The plugin bundles two skills that share the same brand
assets (Raleway font, green/navy palette, logos, service icons):

| Skill | Produces | Triggers on |
|---|---|---|
| **`snetor-html-slides`** | A self-contained animated `.html` presentation deck | slides, presentation, COMEX deck, pitch |
| **`snetor-excalidraw-diagrams`** | An editable `.excalidraw` diagram with embedded logos/icons (+ PNG preview) | architecture diagram, schéma, flow/network diagram |

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

The skills `snetor-skills:snetor-html-slides` and `snetor-skills:snetor-excalidraw-diagrams` will
appear in `/skills`. Both auto-trigger from context; you can also invoke them explicitly.

> **Migration note (rename from `snetor-html-slides`):** machines provisioned before the rename have
> `snetor-html-slides@snetor-ai-guidelines` in their `~/.claude/settings.json`. Re-run
> `scripts/deploy-claude.ps1` (or replace that key with `snetor-skills@snetor-ai-guidelines`) to
> re-enable the plugin under its new name.

## Shared assets

Both skills read the same brand assets, maintained in **one place**:

- `skills/snetor-html-slides/assets/branding/` — Snetor logos, globe, hero banner
- `skills/snetor-html-slides/assets/logos/` — technology / vendor / Azure service icons

`snetor-excalidraw-diagrams` references these logos (no duplication) — update a logo once and both
skills pick it up.

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
│   ├── snetor-html-slides/        ← animated HTML decks
│   │   ├── SKILL.md
│   │   ├── assets/{branding,logos}/   ← shared brand assets (source of truth)
│   │   └── references/
│   └── snetor-excalidraw-diagrams/    ← architecture diagrams
│       ├── SKILL.md
│       ├── scripts/                   ← excalidraw builder + preview renderer
│       └── references/
└── README.md
```
