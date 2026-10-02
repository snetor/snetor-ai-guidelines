# Claude deployment scripts (DSI)

Two PowerShell scripts that install and remove Claude on a Snetor workstation:

| Script | Role |
|---|---|
| `deploy-claude.ps1` | Installs Claude Desktop, Git and, if the collab agrees, Node.js, Claude Code, the Snetor configuration and the Microsoft 365 connector |
| `uninstall-claude.ps1` | Removes what `deploy-claude.ps1` installed, in reverse order, without touching anything the deployment did not write |

Both run from the collab's own Windows session (one UAC prompt) or from NinjaOne (as SYSTEM, no prompt).
Nothing is installed or removed without the collab's consent: a dialog opens in their session first.

## deploy-claude.ps1

### What the collab sees

1. **Consent box** (120 seconds to answer). Three buttons, labelled in French:
   - *Claude Desktop + Git*: phases 2 and 3 only.
   - *Tout installer*: the six phases below.
   - *Reporter*: nothing is installed. It holds the keyboard focus, so a stray Enter or Space cannot start an install.
2. **Progress window**: borderless, always on top, bottom right of the screen, one square per phase (green, orange or red; the running one pulses). It stays up until the end and replaces the per-phase notifications. It closes itself when the run is done, when the process that owns it dies, or after 45 minutes without an update.
3. **Final dialog**: what failed, if anything, and the manual steps left for the collab.

Running the script again later is safe: phases already done are detected and skipped, so a collab who first chose *Claude Desktop + Git* can move to the full install.

### What the script does

| Phase | Action | Full install only |
|---|---|---|
| 0 | Self-elevation (one UAC prompt), collab profile preserved. In a SYSTEM context (NinjaOne) the elevation is skipped and the collab is detected automatically | |
| 1 | Node.js LTS: detects the current version, installs the MSI silently if absent | yes |
| 2 | Git for Windows: installs the latest official release (GitHub `git-for-windows`) if absent, then sets the collab's global Git email unless one is already set | |
| 3 | Claude Desktop: official signed MSIX, machine-wide provisioning (`Add-AppxProvisionedPackage`) | |
| 4 | Claude Code: `npm install -g @anthropic-ai/claude-code` into the collab's profile, npm prefix and PATH pointed at that profile | yes |
| 5 | Snetor configuration: clones this repo, copies the team rules (`workflow.md`, `snetor-guidelines.md`) and imports them from the collab's global `CLAUDE.md`, installs the output styles, the three hooks (`guard.py`, `worktree_memory.py`, `az_ensure_login.py`), writes `settings.json` (plugins, defaults, env) and the status line | yes |
| 6 | Microsoft 365 MCP: pre-configures `claude_desktop_config.json` (real MSIX path) | yes |
| 7 | Colored summary and checklist of the manual steps | |

### Parameters

All three are auto-detected; pass them only to override.

| Parameter | Meaning |
|---|---|
| `-TargetUser` | The collab's user name. Taken from the interactive session |
| `-TargetProfile` | Path of the collab's Windows profile |
| `-TargetEmail` | The collab's email, used for the Git identity. Session UPN, then the AD `mail` attribute, then the `<samAccountName>@snetor.com` convention with an explicit warning |

### Exit codes (read by NinjaOne)

| Code | Meaning |
|---|---|
| 0 | Deployment finished with no failed phase |
| 1 | At least one phase failed, or no collab is logged on |
| 2 | The collab postponed: nothing was installed |
| 3 | No answer within the delay: nothing was installed |

## uninstall-claude.ps1

### Steps

| Step | Action |
|---|---|
| 1 | Closes Claude: the Claude Desktop, Claude Code and Microsoft 365 MCP server processes are stopped |
| 2 | Microsoft 365 MCP: removes the `microsoft365` entry from `claude_desktop_config.json` |
| 3 | Snetor configuration: removes the plugins, defaults, env and hooks the deployment put in `settings.json`, the imports and rules block in `CLAUDE.md`, and the files copied from this repo (rules, output style, hooks, status line) |
| 4 | Claude Code: removes the npm package, the npm prefix in `.npmrc` and the PATH entry |
| 5 | Claude Desktop: removes the provisioned MSIX and the per-user packages |
| 6 | Git for Windows: uninstalls the machine-wide install. A per-user Git is never touched |
| 7 | Node.js: uninstalls the MSI install |
| 8 | Leftovers of an interrupted deployment: `SnetorClaude-*` scheduled tasks, `snetor-claude-*` temp folders, the `az_ensure_login.py` token-expiry cache |
| 9 | Personal data, only with `-Purge` |

The removal is surgical. In `settings.json`, `claude_desktop_config.json`, `CLAUDE.md` and `.npmrc`, a value goes away only if it still equals what the deployment wrote; the rest of the file is returned as is. A collab who had already chosen the `dark` theme loses it anyway, since it cannot be told apart from the Snetor default.

### Parameters

`-TargetUser`, `-TargetProfile` and `-TargetEmail` work as above (the Git identity is removed only if it equals the email). In addition:

| Parameter | Meaning |
|---|---|
| `-KeepNodeJs` | Keeps Node.js. Without it, an MSI-installed Node.js is removed even if it was there before the deployment, because the deployment does not record what it installed |
| `-KeepGit` | Keeps Git |
| `-Purge` | Also deletes the collab's personal Claude data: the whole `~/.claude` (history, memory, plugins), `~/.claude.json` (login token) and the Claude Code and Claude Desktop caches |
| `-WhatIf` | Prints what would be removed, marked `[SIMULATION]`. No elevation, no consent box, no window, nothing modified |

Without `-Purge`, these stay on the workstation: the plugins Claude Code downloaded (`~/.claude/plugins`), the worktree memory junctions (`~/.claude/projects`), the history, the memory and the login token. They are Claude Code data, not something the deployment wrote.

```powershell
.\scripts\uninstall-claude.ps1 -WhatIf
.\scripts\uninstall-claude.ps1 -KeepGit -Purge
```

### Exit codes (read by NinjaOne)

| Code | Meaning |
|---|---|
| 0 | Removal finished with no failed step (or `-WhatIf` simulation) |
| 1 | At least one step failed, or no collab is logged on |
| 2 | The collab postponed: nothing was removed |
| 3 | No answer within the delay: nothing was removed |

Not yet tested end to end through NinjaOne on a test workstation.

## Prerequisites

- Windows 10/11 x64
- Windows PowerShell 5.1 (both scripts force TLS 1.2 and run under `powershell.exe`)
- Internet access (Node.js, Git, Claude Desktop, Claude Code and this repo are downloaded)
- DSI admin credentials to approve the UAC prompt (not needed from NinjaOne)

## Usage

### From the collab's session

1. Open a Windows session with the collab's account (the collab is logged on)
2. Download this repo or copy the scripts onto the workstation
3. Open a PowerShell terminal (not admin: the script elevates itself)
4. Run:

```powershell
.\scripts\deploy-claude.ps1
```

5. Approve the UAC prompt with the DSI admin credentials
6. The collab answers the consent box, then the script runs alone to the final dialog (about 5 to 10 minutes for the full install)

### From NinjaOne (no intervention)

Paste the script into NinjaOne. It detects that it runs as SYSTEM, finds the logged-on collab (`query user`, then `Win32_ComputerSystem.UserName` as a fallback) and their profile through the SID in `ProfileList`. No UAC prompt: the NinjaOne agent is already elevated.

The windows have to appear in the collab's session, not in SYSTEM's, so the script registers an ephemeral scheduled task (`SnetorClaude-<name>`) that runs under the collab's account and starts a hidden `powershell.exe` through `wscript`.

## Manual steps after deployment (collab)

These need the browser and cannot be automated:

1. **Claude Desktop**: open the app and sign in with the `@snetor.com` account
2. **Microsoft 365 connector**: in Claude Desktop, Settings, Extensions, Microsoft 365, Authorize (full install only)
3. **Claude Code**: type `claude` in a terminal and authenticate in the browser (full install only)

## Admin action, once for the whole tenant

Before collabs can authorize the Microsoft 365 connector, the Entra admin has to grant consent:

1. Go to `https://entra.microsoft.com`
2. Enterprise applications, search for *M365 MCP Client for Claude*
3. Click **Grant admin consent**

This is needed once only; it unblocks the authorization for every user of the tenant.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Phase 3 "manual check" warning | Download the MSIX by hand from `https://claude.com/download` |
| `npm` not found after phase 1 | Close the terminal and run the script again: Node.js is installed but PATH is not refreshed yet |
| `claude` not recognized after phase 4 | Open a new terminal: the user PATH is updated when the shell restarts |
| Claude Desktop missing from the Start menu | Machine-wide provisioning: it appears at the collab's **next Windows logon** |
| Extensions / Microsoft 365 missing in Claude Desktop | Check that the claude.ai account is on a Teams or Enterprise plan |
| M365 config path warning (fallback) | Open Claude Desktop at least once (it creates the right folder), then run phase 6 again |
| No window appears from NinjaOne | Check the NinjaOne activity log: the script says whether the collab session and the scheduled task were found. Exit code 1 with "no collab" means nobody was logged on |
| Exit code 2 or 3 | The collab postponed or did not answer. Nothing was changed; run the script again later |

## Known issues

- **Phases 5 and 6 fail on a brand new profile.** `X.PSObject.Properties.Name -contains 'k'` throws `PropertyNotFoundStrict` under `Set-StrictMode` when `X` is empty, which is the case when `settings.json` or `claude_desktop_config.json` does not exist yet. A workstation that already ran Claude is not affected, so test on an empty profile, not on a developer's workstation. The *Claude Desktop + Git* choice does not run these phases.

## Technical notes

- **100% ASCII files**: a script pasted into NinjaOne loses its BOM, and `powershell.exe` 5.1 then reads a file without BOM as ANSI (an em dash in a string becomes a closing quote and the whole script refuses to start). The accents shown in the windows go through HTML entities (`ConvertFrom-UiText`). Keep it that way when editing.
- **Target profile**: the script captures `$env:USERPROFILE` before the elevation and passes the path to the admin session. Every write to the user profile (`settings.json`, `CLAUDE.md`, status line, M365 config) goes to the **collab's** profile, not the DSI admin's.
- **PowerShell 5.1**: TLS 1.2 is enabled explicitly (5.1 negotiates TLS 1.0/1.1 by default, which nodejs.org, GitHub and claude.ai refuse), and JSON is written as UTF-8 **without BOM** (the native `-Encoding UTF8` of 5.1 adds a BOM that breaks parsers).
- **Claude Desktop (MSIX)**: installed with `Add-AppxProvisionedPackage -Online`. The script runs elevated, so a per-user `Add-AppxPackage` would only target the admin; provisioning registers Claude for the collab at their next logon.
- **M365 config path**: the MSIX reads from `%LOCALAPPDATA%\Packages\<PackageFamilyName>\LocalCache\Roaming\Claude\`, not `%APPDATA%\Claude\`. The script resolves the `<PackageFamilyName>` with `Get-AppxPackage -AllUsers`, then by derivation from the provisioned package, and falls back to `%APPDATA%\Claude\`.
- **npm prefix**: set to `$TargetProfile\AppData\Roaming\npm` so Claude Code does not land in the admin profile.
- **Progress window**: it re-reads a small state file, `SnetorClaude\progression.txt` in the collab's temp folder, every 0.5 seconds. The uninstaller spares this file during its own run.
- **Keeping the two scripts aligned**: `uninstall-claude.ps1` lists what the deployment writes (plugins, defaults, env, hooks, copied files). A new hook or setting added to phase 5 needs a matching entry there.
