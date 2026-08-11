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

## NEW TO THE TEAM? START HERE

New to Claude Code at Snetor? Open the **interactive onboarding guide** — paste it into Claude Code
and you get a guided, hands-on walkthrough (machine setup, repos, plugins, team conventions and a
safe first task):

> **https://claude.ai/claude-code/onboard/BMojJDEZzfOV**

It covers how the team actually uses Claude, the setup checklist, the hard-won landing-zone gotchas
(`merge = apply`, never `apply` locally, PowerShell for `terraform import`, the SSL CA bundle…) and
a first PR to learn the branch → PR → CI plan → merge loop.

---

## CONTENTS

| File / Folder | Description |
|---|---|
| `CLAUDE.md` | Repo-local rules — how to work inside this repo, not a template |
| `claude-config/` | Team rules — two files of different scope: `workflow.md` (generic method) and `snetor-guidelines.md` (Snetor-specific) |
| `scripts/` | DSI deployment scripts — onboard a collaborator in one run |
| `output-styles/` | Custom output styles — how Claude phrases its answers |
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

Four skills for Snetor teams: **`snetor-html-slides`** (animated HTML decks) and
**`snetor-excalidraw-diagrams`** (architecture diagrams with embedded service icons) for branded
visuals, **`snetor-travel-report`** — helps sales reps dictate client-visit reports (in any
language) and drafts them in English, Outlook-ready — and **`snetor-docs-close`**, which closes a
branch against the Snetor documentation standard: plan purge, spec arbitration, lessons, todo
cleanup, `HANDOFF.md` rewrite, then index regeneration and verification.

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

### Team guidelines (workflow.md / snetor-guidelines.md)

`claude-config/` holds two rule files with different scope:

- `workflow.md` — generic working method, valid on any project.
- `snetor-guidelines.md` — Snetor-specific rules (git discipline, documentation standard). It
  complements `workflow.md`, it does not replace it.

`deploy-claude.ps1` distributes them to whatever agent profiles it finds on the machine, across two
families, each with its own instructions file and its own delivery mechanism:

- **Claude Code family** — directories named `.claude`, or `.claude` plus a suffix. Instructions file:
  `CLAUDE.md`. The rule files are copied next to it and pulled in with Claude Code's `@path` import
  directive — the personal `CLAUDE.md` is never rewritten wholesale, only missing import lines are
  appended.
- **Codex family** — directories named `.codex`, or `.codex` plus a suffix. Instructions file:
  `AGENTS.md`. Codex CLI has no import directive to point at — the feature is requested but not
  implemented upstream (tracked as [`openai/codex#17401`](https://github.com/openai/codex/issues/17401),
  open). So `AGENTS.md` is **generated** on every deployment instead: the script concatenates
  `contexte-perso.md` (personal context, never touched by the script) with the rule files, in that
  order. `CODEX_HOME` controls where Codex looks for its configuration directory — it defaults to
  `~/.codex` — and Codex reads `AGENTS.override.md` ahead of `AGENTS.md` when both are present.

**Scope rule**, the same for both families: a directory named **exactly** `.claude` or `.codex` is the
**enterprise** profile and receives both rule files. Any directory of the same family with a suffix —
e.g. `.claude-foo` — is a **personal** profile specific to that workstation and receives `workflow.md`
only. A machine with no suffixed directory simply has no personal profile to distribute to; that is
the normal case, not an error.

Running `deploy-claude.ps1` is the supported way to apply this — especially for the Codex family,
where reproducing the generation step by hand is error-prone. For the Claude family only, the
equivalent manual step is:

```powershell
$claudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
$import   = '@~/.claude/snetor-guidelines.md'
Copy-Item claude-config\snetor-guidelines.md "$env:USERPROFILE\.claude\snetor-guidelines.md" -Force
if (-not (Test-Path $claudeMd)) { New-Item -ItemType File $claudeMd | Out-Null }
if (-not (Select-String -Path $claudeMd -SimpleMatch $import -Quiet)) {
    [System.IO.File]::AppendAllText($claudeMd, "`r`n$import`r`n", (New-Object System.Text.UTF8Encoding($false)))
}
```

Your personal `CLAUDE.md` is never overwritten — it only imports the team file. The snippet is
idempotent: it appends the import line only if it is not already there, so running it twice does not
duplicate it. It writes UTF-8 **without** BOM, like `deploy-claude.ps1` does, because a BOM at the
head of `CLAUDE.md` can upset the memory-file parser. Check that it loads with `/context`, section
**Memory files**.

> **Migration note (team rules used to be inlined):** for the **Claude family**, machines provisioned
> before this split had the team rules **copied into** `~/.claude/CLAUDE.md` by the old
> `deploy-claude.ps1`. The current script never overwrites that file — it only adds the import line —
> so those machines now load the team rules **twice**: once from the inlined copy, which is frozen and
> will never be updated again, and once from the import. Open `~/.claude/CLAUDE.md`, delete the
> inlined team-rules block by hand, and keep only your own personal context plus the
> `@~/.claude/snetor-guidelines.md` line. This step is deliberately manual: stripping a block of text
> out of a collaborator's personal file by script risks losing local personalisations, which is a
> worse outcome than the duplicate it would fix.
>
> For the **Codex family**, the equivalent risk is sharper: `AGENTS.md` is regenerated wholesale on
> every deployment, so on the first deployment under this mechanism whatever was in the existing
> `AGENTS.md` is replaced outright unless it was moved first. Before that first run, move your
> personal context out of `AGENTS.md` into `contexte-perso.md`, or the generated file will come out
> amputated of it. The cut point: the team block starts at the `# Workflow Orchestration` heading;
> everything above that heading is personal context. As above, this extraction is deliberately manual
> and not something to script — pulling a block out of a collaborator's personal file programmatically
> risks losing content the tool cannot tell apart from the block it means to remove.

---

### Output styles

An output style changes **how** Claude answers — tone, length, structure — without touching its
coding instructions. Styles live in `~/.claude/output-styles`, one markdown file per style.

`output-styles/snetor-brief.md` is the Snetor default: short sentences and plain words, but the exact
technical term is always kept and explained right after — written for people who know the stack and
have no time to decode. Every answer ends with *what was done, whether it worked, what to do next*.
Decisions come as 3 options max with a recommendation. Two things are never compressed: warnings
before an irreversible action, and the recap after Claude has been working on its own (done /
blocked / needs you).

```powershell
Copy-Item -Recurse output-styles "$env:USERPROFILE\.claude\output-styles" -Force
```

Then restart Claude Code and pick it with `/config` → **Output style** → `Snetor Brief`
(or set `"outputStyle": "Snetor Brief"` in `~/.claude/settings.json`).

> Write your own style: drop a `.md` file in that folder with a `name` / `description` frontmatter
> and `keep-coding-instructions: true`, then reselect it via `/config`.

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
  "outputStyle": "Snetor Brief",
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
