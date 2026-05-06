# snetor-html-slides

Claude Code skill for generating Snetor-branded animated HTML presentation decks.

## What it does

When invoked, this skill produces a single self-contained `.html` file with:
- Full Snetor design system (Raleway font, green/navy palette, all components)
- Animated entry transitions per slide element
- Keyboard + button navigation
- Interactive check-cards for validation slides
- Progress indicator

## Installation

### For Clément (user scope)

The skill is installed at user scope via `~/.claude/plugins/cache/local/snetor-html-slides/`.
Run `/reload-plugins` in Claude Code after updating.

### For other Snetor collaborators

1. Clone or pull `snetor-ai-guidelines`
2. In Claude Code, run `/plugin install <path-to-this-folder>`
3. Run `/reload-plugins`

## Assets

- `skills/snetor-html-slides/assets/branding/` — Snetor logos, globe, hero banner
- `skills/snetor-html-slides/assets/logos/` — 29 technology/vendor logos

## Updating the skill

If you discover a new component pattern or layout improvement while generating a deck:
1. Add the pattern to `skills/snetor-html-slides/references/components.md`
2. Commit and push to `snetor-ai-guidelines`
3. Other users pull and reload plugins

## Structure

```
snetor-html-slides/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── snetor-html-slides/
│       ├── SKILL.md               ← main skill instructions
│       ├── assets/
│       │   ├── branding/          ← logos, globe, hero banner
│       │   └── logos/             ← technology logos
│       └── references/
│           ├── css-system.md      ← full CSS design system + nav JS
│           └── components.md      ← HTML component catalog
└── README.md
```
