# snetor-skills

Snetor skills for Claude Code. Eight skills in three families: **branded-visual generators** that
share the same brand assets (Raleway font, green/navy palette, logos, service icons), **business
assistants**, and **maintenance routines** that keep a Snetor repo honest without anyone having to
remember to ask.

### Branded visuals

| Skill | Produces | Triggers on |
|---|---|---|
| **`snetor-html-slides`** | A self-contained animated `.html` presentation deck | slides, presentation, COMEX deck, pitch |
| **`snetor-excalidraw-diagrams`** | An editable `.excalidraw` diagram with embedded logos/icons (+ PNG preview) | architecture diagram, schéma, flow/network diagram |

### Business assistants

| Skill | Produces | Triggers on |
|---|---|---|
| **`snetor-travel-report`** | An English, Outlook-ready travel report drafted from a sales rep's dictation (any language) | travel report, rapport de voyage, compte rendu de visite, "today I visited…" |
| **`snetor-deploy-artefact`** | A PR shipping a power-user artifact onto the internal container platform | "déployer cet artefact", "nouvelle version du HTML", paved road |

### Maintenance routines

These are the ones nobody thinks to invoke. They trigger on **situations**, not requests — that is
the point: a routine you have to remember is a routine you run once.

| Skill | Checks | Triggers on |
|---|---|---|
| **`snetor-docs-close`** | Documentation standard on branch close: plan purged, specs arbitrated, lessons recorded, todo cleaned, router rewritten under 150 lines, index regenerated | before opening/merging a PR, "on clôture", "c'est fini", "close the branch" |
| **`snetor-doc-vs-infra`** | Every infrastructure claim in the docs against a dated Azure execution — proven / unproven / contradicted | "according to the HANDOFF", "the runbook says", "d'après le HANDOFF", before citing any infra state |
| **`snetor-lessons-to-guardrails`** | Turns repeated lessons into executable guardrails (hook, test) instead of more prose | "we have been burned by this before", "that is the second time", "on s'est déjà fait avoir", `lessons.md` near its 300-line cap |
| **`snetor-test-pruning`** | Dead modules, sleeping tests, constant assertions, duplicate coverage — with the before/after count | "the CI takes forever", "we have too many tests", "la CI prend des plombes", after a large refactor |

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

> **Migration note (rename from `snetor-html-slides`):** machines provisioned before the rename have
> `snetor-html-slides@snetor-ai-guidelines` in their `~/.claude/settings.json`. Re-run
> `scripts/deploy-claude.ps1` (or replace that key with `snetor-skills@snetor-ai-guidelines`) to
> re-enable the plugin under its new name.

## Shared assets

The two **visual** skills (`snetor-html-slides` and `snetor-excalidraw-diagrams`) read the same
brand assets, maintained in **one place**:

- `skills/snetor-html-slides/assets/branding/` — Snetor logos, hero banner
- `skills/snetor-html-slides/assets/logos/` — technology / vendor / Azure service icons

`snetor-excalidraw-diagrams` references these logos (no duplication) — update a logo once and both
visual skills pick it up. The six other skills are text-only and use no brand assets.

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
│   │   └── references/
│   ├── snetor-excalidraw-diagrams/  ← architecture diagrams
│   │   ├── SKILL.md
│   │   ├── scripts/                     ← excalidraw builder + preview renderer
│   │   └── references/
│   ├── snetor-travel-report/        ← sales travel reports
│   │   ├── SKILL.md
│   │   └── references/                  ← templates, glossaire, report-style
│   ├── snetor-deploy-artefact/      ← ship an artifact onto the paved road
│   │   └── SKILL.md
│   ├── snetor-docs-close/           ← branch-closing assistant
│   │   └── SKILL.md
│   ├── snetor-doc-vs-infra/         ← doc claims vs. real Azure executions
│   │   └── SKILL.md
│   ├── snetor-lessons-to-guardrails/ ← lessons → executable guardrails
│   │   └── SKILL.md
│   └── snetor-test-pruning/          ← dead-test removal
│       └── SKILL.md
└── README.md
```
