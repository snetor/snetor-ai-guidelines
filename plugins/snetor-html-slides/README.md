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

### Prerequisites

- Claude Code installed (desktop app or CLI)
- The `snetor-ai-guidelines` repo cloned locally

### Steps

1. **Clone the repo** (if not already done):
   ```
   git clone https://github.com/snetor/snetor-ai-guidelines.git
   ```

2. **Add the Snetor marketplace** in Claude Code:
   - Open `/plugin` → **Add Marketplace**
   - Enter the local path to the repo, e.g.:
     ```
     C:\path\to\snetor-ai-guidelines
     ```
     or on macOS/Linux:
     ```
     /path/to/snetor-ai-guidelines
     ```

3. **Install the plugin** from the Installed tab or by running:
   ```
   /plugin install snetor-ai-guidelines/snetor-html-slides
   ```

4. **Reload plugins**:
   ```
   /reload-plugins
   ```

The skill `snetor-html-slides:snetor-html-slides` will now appear in `/skills`.

### Triggering the skill

The skill auto-triggers whenever you ask for slides, a presentation, or a COMEX deck.
You can also invoke it explicitly with the `Skill` tool or via `/skills`.

## Assets

- `skills/snetor-html-slides/assets/branding/` — Snetor logos, globe, hero banner
- `skills/snetor-html-slides/assets/logos/` — 29 technology/vendor logos

## Updating the skill

When a new component pattern or layout improvement is found:
1. Pull the latest `snetor-ai-guidelines`
2. Run `/reload-plugins` — the skill updates automatically (it reads from your local clone)

To contribute improvements:
1. Edit `skills/snetor-html-slides/references/components.md` or `SKILL.md`
2. Commit and push to `snetor-ai-guidelines`
3. Other users pull and run `/reload-plugins`

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
