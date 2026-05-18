# Design Spec — `deploy-claude.ps1` (Snetor DSI)

**Date:** 2026-05-18  
**Author:** DSI Snetor  
**Status:** Approved

---

## 1. Goal

Single PowerShell script (`deploy-claude.ps1`) that a DSI admin runs **once** on a collaborator's Windows PC to deliver:

- **Claude Desktop** (MSIX) — signed in via claude.ai Teams account
- **Claude Code / Cowork** (CLI) — authenticated via browser on first use
- **M365 MCP connector** — pre-configured JSON; OAuth completed by user on first launch
- **Snetor config** — CLAUDE.md global, settings.json with plugins, status line

One UAC prompt at the top. No re-prompts after that.

---

## 2. Architecture

```
deploy-claude.ps1
│
├─ Phase 0 — Self-elevation (UAC × 1)
├─ Phase 1 — Node.js LTS         [admin required — system install]
├─ Phase 2 — Claude Desktop      [admin required — MSIX provisioning]
├─ Phase 3 — Claude Code CLI     [npm global install, PATH update]
├─ Phase 4 — Snetor config       [user profile writes — no admin needed]
│    ├─ Clone/download snetor-ai-guidelines repo
│    ├─ Copy CLAUDE.md → %USERPROFILE%\.claude\CLAUDE.md
│    ├─ Write settings.json (plugins, theme, effortLevel)
│    └─ Run statusline/install.ps1
└─ Phase 5 — M365 MCP config     [write claude_desktop_config.json]
     └─ Phase 6 — Summary + manual steps checklist
```

---

## 3. Components

### Phase 0 — Self-elevation

Detect admin role via `WindowsPrincipal.IsInRole(Administrator)`.  
If not admin → capture `$env:USERPROFILE` and `$env:USERNAME` of the **current (collab) session**, then re-launch:

```powershell
Start-Process powershell -Verb RunAs `
  -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -TargetUser `"$env:USERNAME`" -TargetProfile `"$env:USERPROFILE`""
```

The elevated session receives `$TargetProfile` as a parameter and uses it for all user-profile writes (CLAUDE.md, settings.json, status line, M365 config). This ensures the config lands in the **collab's** profile regardless of which admin account approved the UAC prompt.

> **Prerequisite for DSI admin:** Run the script from the **collab's Windows session** (not from your own admin session). Standard scenario: admin sits at the collab's PC, collab is logged in → admin right-clicks → "Exécuter en tant qu'administrateur" → saisit ses credentials admin dans la boite UAC. `$TargetProfile` = collab's profile. ✅

### Phase 1 — Node.js

1. Check `node --version`; if Node 18+ exists → skip.
2. Download Node.js LTS installer from `https://nodejs.org/dist/latest-lts/` (resolve current LTS URL via JSON feed `https://nodejs.org/dist/index.json`).
3. Silent install: `msiexec /i node.msi /quiet /norestart ADDLOCAL=ALL`.
4. Refresh PATH in current session (`[System.Environment]::GetEnvironmentVariable("PATH","Machine")`).

### Phase 2 — Claude Desktop

1. Resolve the current installer URL at runtime by querying `https://claude.ai/api/download-links` or scraping the `https://claude.com/download` page — this avoids hardcoding a CDN URL that may rotate. Fallback: hardcoded known-good URL `https://storage.googleapis.com/osprey-downloads-c02f6a0d-347c-492b-a752-3e0651722e97/nest-win-x64/Claude-Setup.exe` (Squirrel installer, also observed in the wild alongside MSIX).
2. **Format detection:** Anthropic ships either an `.exe` (Squirrel) or `.msix`. The script handles both:
   - `.msix` → `Add-AppxProvisionedPackage -Online -PackagePath $file -SkipLicense` (machine-wide)
   - `.exe` → `Start-Process $file -ArgumentList "--silent" -Wait` (user-scope Squirrel install)
3. Verify post-install: `Get-AppxPackage -Name "*Claude*"` → if found, ✅; else print manual URL.

### Phase 3 — Claude Code

```powershell
npm install -g @anthropic-ai/claude-code
```

npm global installs go to `%APPDATA%\npm` by default. Since the script runs elevated but uses `$TargetProfile` for the user-profile writes, we set the npm prefix explicitly before installing:

```powershell
$env:APPDATA = "$TargetProfile\AppData\Roaming"
npm config set prefix "$TargetProfile\AppData\Roaming\npm"
npm install -g @anthropic-ai/claude-code
```

This ensures the `claude` binary lands in the collab's PATH, not the admin's.

### Phase 4 — Snetor Config

Steps:
1. **Clone repo** — `git clone https://github.com/snetor/snetor-ai-guidelines.git` to a temp dir (or download as zip if git unavailable).
2. **CLAUDE.md** — `Copy-Item .\CLAUDE.md "$env:USERPROFILE\.claude\CLAUDE.md" -Force`
3. **settings.json** — Write the reference block from the README to `%USERPROFILE%\.claude\settings.json` (merge with existing if present, to avoid clobbering user customizations).
4. **Status line** — `& .\statusline\install.ps1`

Settings.json written:
```json
{
  "theme": "dark",
  "effortLevel": "medium",
  "enabledPlugins": {
    "superpowers@claude-plugins-official": true,
    "context7@claude-plugins-official": true,
    "snetor-html-slides@snetor-ai-guidelines": true
  }
}
```

### Phase 5 — M365 MCP Config

**Path gotcha (MSIX bug):** Claude Desktop reads config from:
```
%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```
NOT from `%APPDATA%\Claude\`. The script resolves the correct path dynamically:
```powershell
$claudePkg = Get-AppxPackage -Name "Claude" | Select-Object -First 1
$configPath = "$env:LOCALAPPDATA\Packages\$($claudePkg.PackageFamilyName)\LocalCache\Roaming\Claude\claude_desktop_config.json"
```

Config written:
```json
{
  "mcpServers": {
    "microsoft365": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-microsoft365"]
    }
  }
}
```

If an existing config is present, the script **merges** `mcpServers` rather than overwriting.

### Phase 6 — Summary

Print a colored checklist:
```
✅ Node.js 22 LTS — installed
✅ Claude Desktop — installed (all users)
✅ Claude Code (cowork) — installed globally
✅ Snetor CLAUDE.md — applied
✅ Snetor plugins — configured
✅ Status line — active
✅ M365 MCP — pre-configured

📋 Actions manuelles restantes :
  1. Ouvrir Claude Desktop → Se connecter avec le compte claude.ai Snetor
  2. Connecteur M365 : Paramètres → Extensions → Microsoft 365 → Autoriser
  3. [Admin Entra — 1x pour tout le tenant] Accorder le consentement admin :
     https://entra.microsoft.com → Applications d'entreprise → M365 MCP Client for Claude
  4. Lancer Claude Code une fois : taper `claude` dans un terminal → s'authentifier via le navigateur
```

---

## 4. Error Handling

| Scenario | Behaviour |
|---|---|
| Node.js download fails | Print error + URL to download manually; continue other phases |
| MSIX install fails | Print error + link to manual installer; continue |
| npm install fails | Print error; suggest manual: `npm install -g @anthropic-ai/claude-code` |
| Git unavailable | Fall back to downloading repo as .zip via `Invoke-WebRequest` |
| Config path not found (Claude not installed) | Skip Phase 5, add note to summary |
| Existing settings.json | Deep-merge, never overwrite user keys |

Each phase is wrapped in `try/catch`. A failed phase does not abort the script — it logs the error and continues to the next phase.

---

## 5. Security Considerations

- No API key stored anywhere in the script.
- No credentials hardcoded. Admin password is only used by Windows for the UAC elevation.
- The script only writes to `%USERPROFILE%` (settings, CLAUDE.md) and system paths (Node.js, Appx).
- MSIX is downloaded from the official Anthropic CDN and hash-verified before install.
- npm package is the official `@anthropic-ai/claude-code` from the public registry.

---

## 6. Deliverables

| File | Location in repo |
|---|---|
| `deploy-claude.ps1` | `scripts/deploy-claude.ps1` |
| README usage section | `scripts/README.md` |

---

## 7. Out of Scope

- Automated Entra admin consent (requires interactive browser with tenant admin credentials)
- Automated claude.ai OAuth login (requires browser session)
- Multi-machine / GPO deployment (single-machine only)
- Uninstall script (future)
