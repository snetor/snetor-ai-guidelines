# Claude Code — Status Line

Displays at the bottom of the terminal: active model, current directory, git branch, context window usage and 5-hour token quota.

```
Claude Sonnet 4.6 | ~/dev/my-project | git:main | ctx ████████░░░░ 67% (670k/1M tok) | 5h ████░░░░░░ 40%
```

## Installation

### Windows (automated)

```powershell
.\install.ps1
```

Copies `statusline-command.js` to `~/.claude/` and patches `~/.claude/settings.json` with the correct absolute path. Restart Claude Code — done.

### macOS / Linux (manual)

1. Copy the script:

```bash
cp statusline-command.sh ~/.claude/statusline-command.sh
chmod +x ~/.claude/statusline-command.sh
```

2. Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /home/<your-user>/.claude/statusline-command.sh",
    "padding": 1,
    "refreshInterval": 5
  }
}
```

### Available variants

| File | Environment |
|---|---|
| `statusline-command.js` | **Recommended** — Node.js (Windows, macOS, Linux) |
| `statusline-command.ps1` | PowerShell 5.1 (native Windows) |
| `statusline-command.sh` | Bash / Git Bash / macOS / Linux |

## Indicators

| Indicator | Description |
|---|---|
| Model | Active Claude model name (e.g. `Claude Sonnet 4.6`) |
| Directory | Abbreviated current path (`~` = home, `…/parent/project` if long) |
| `git:branch` | Active git branch (hidden if not in a git repo) |
| `ctx` | Context window usage — green < 60%, orange < 85%, red ≥ 85% |
| `5h` | 5-hour token quota — blue < 60%, orange < 85%, red ≥ 85% |
