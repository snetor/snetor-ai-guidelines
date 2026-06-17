<div align="center">
  <img src="assets/snetor_full_logo.png" alt="Snetor" height="56" />
  <br /><br />
  <p><strong>AI ENGINEERING GUIDELINES</strong></p>
  <p>Claude Code configurations, workflows and best practices for Snetor AI Engineers.</p>
  <br />
  <img src="https://img.shields.io/badge/Claude_Code-007D36?style=flat-square&logoColor=white" alt="Claude Code" />
  <img src="https://img.shields.io/badge/Superpowers-152B47?style=flat-square&logoColor=white" alt="Superpowers" />
  <img src="https://img.shields.io/badge/Context7-168C74?style=flat-square&logoColor=white" alt="Context7" />
  <img src="https://img.shields.io/badge/Node.js_18+-1E1B2F?style=flat-square&logoColor=white" alt="Node.js" />
</div>

---

## CONTENTS

| File / Folder | Description |
|---|---|
| `CLAUDE.md` | Global instructions injected into every Claude Code session |
| `scripts/` | DSI deployment scripts — onboard a collaborator in one run |
| `statusline/` | Custom status line — context usage, rate limit, git branch |
| `assets/` | Snetor brand assets |

---

## INSTALLATION

### DSI deployment (recommended)

For a full automated setup on a collaborator's PC — Node.js, Git, Claude Desktop, Claude Code, M365 connector, and Snetor config — run:

```powershell
.\scripts\deploy-claude.ps1
```

One UAC prompt. Everything else is automatic. See [`scripts/README.md`](scripts/README.md) for details.

---

### Prerequisites (manual install)

- [Claude Code](https://claude.ai/code) installed (desktop app or CLI)
- Node.js 18+

---

### Plugin snetor-skills

Snetor-branded visuals — two skills: **`snetor-html-slides`** (animated HTML decks) and
**`snetor-excalidraw-diagrams`** (architecture diagrams with embedded service icons).

#### Via the marketplace (recommended)

```
/plugin marketplace add snetor/snetor-ai-guidelines
/plugin install snetor-skills@snetor-ai-guidelines
```

#### Manually

```bash
git clone https://github.com/snetor/snetor-ai-guidelines.git
```

Then in Claude Code: `/plugin install` and select `plugins/snetor-skills`.

---

### Status line

Displays active model, git branch, context usage and token quota at the bottom of the terminal:

```
Claude Sonnet 4.6 | ~/dev/my-project | git:main | ctx ████████░░ 67% (670k/1M tok) | 5h ████░░ 40%
```

**Automated install (Windows):**

```powershell
.\statusline\install.ps1
```

Restart Claude Code — the status line is active.

> See [`statusline/README.md`](statusline/README.md) for details and Linux/macOS variants.

---

### Global CLAUDE.md

To apply Snetor conventions to all your projects:

```powershell
Copy-Item CLAUDE.md "$env:USERPROFILE\.claude\CLAUDE.md"
```

---

## RECOMMENDED PLUGINS

Enable via `/config` in Claude Code or directly in `~/.claude/settings.json`.

| Plugin | Role |
|---|---|
| `superpowers@claude-plugins-official` | Advanced workflows — brainstorming, TDD, debugging, plans, code review |
| `context7@claude-plugins-official` | Up-to-date library docs injected directly into context |
| `frontend-design@claude-plugins-official` | Production-quality frontend UI generation |

---

## SETTINGS.JSON REFERENCE

Reference block for `~/.claude/settings.json`:

```json
{
  "theme": "dark",
  "effortLevel": "medium",
  "enabledPlugins": {
    "superpowers@claude-plugins-official": true,
    "context7@claude-plugins-official": true,
    "frontend-design@claude-plugins-official": true,
    "snetor-skills@snetor-ai-guidelines": true
  }
}
```

> The `statusLine` key is injected automatically by `.\statusline\install.ps1`.

> **Windows only.** If Git Bash is not in the system PATH, add:
> ```json
> "env": { "CLAUDE_CODE_GIT_BASH_PATH": "C:\\...\\Git\\bin\\bash.exe" }
> ```

---

## WORKFLOWS

Workflows are managed by the `superpowers` plugin. Each skill activates automatically based on context — no manual commands required.

| Skill | Trigger | Role |
|---|---|---|
| `superpowers:brainstorming` | Before any feature creation | Explores requirements and design before code |
| `superpowers:writing-plans` | Multi-step task | Generates a detailed plan before implementation |
| `superpowers:executing-plans` | Executing an existing plan | Step-by-step execution with review checkpoints |
| `superpowers:test-driven-development` | Before writing code | Red-green-refactor cycle |
| `superpowers:systematic-debugging` | When hitting a bug | Structured diagnosis before fixing |
| `superpowers:requesting-code-review` | After implementation | Multi-agent review |
| `superpowers:verification-before-completion` | Before declaring done | Verifies actual behavior before commit |

---

## CONVENTIONS

### Standard workflow

1. **Plan first.** For any non-trivial task (3+ steps), write the plan in `tasks/todo.md` before touching code.
2. **Verify before done.** Never mark a task complete without proof it works.
3. **Subagents for research.** Delegate exploration and parallel analysis to dedicated agents.
4. **Lessons.** After any correction, document the pattern in `tasks/lessons.md`.

### Claude models

| Model | ID | Recommended use |
|---|---|---|
| Claude Opus 4.7 | `claude-opus-4-7` | Complex tasks, architecture decisions |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Daily use (default) |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Simple tasks, high volume, latency-sensitive |

Switch model in session: `/model`

---

## RESOURCES

- [Claude Code — Official documentation](https://docs.anthropic.com/claude/claude-code)
- [Anthropic API](https://docs.anthropic.com/claude/api)
- [Official Claude Code plugins](https://claude.ai/plugins)

---

<div align="center">
  <img src="assets/snetor_globe.png" alt="Snetor" height="32" />
  <br />
  <sub>Snetor Group — distributing polymers across 60+ countries since 1989.</sub>
</div>
