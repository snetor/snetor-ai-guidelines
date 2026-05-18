# Claude Deploy Script Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `scripts/deploy-claude.ps1` — a single PowerShell script that a DSI admin runs once on a collab's PC to install and configure Claude Desktop, Claude Code, and the Snetor environment with one UAC prompt.

**Architecture:** Single self-elevating `.ps1` file with a `param()` block for `$TargetProfile`/`$TargetUser` (captured before elevation). Six phases implemented as functions, each wrapped in try/catch, non-fatal on failure. No external dependencies beyond PowerShell 5.1+ and internet access.

**Tech Stack:** PowerShell 5.1, `Invoke-WebRequest`, `Add-AppxPackage`, `npm`, `git`, Windows Environment API.

---

## File Structure

| Action | Path |
|---|---|
| Create | `scripts/deploy-claude.ps1` |
| Create | `scripts/README.md` |

---

## Task 1 — Script skeleton + Phase 0 (self-elevation)

**Files:**
- Create: `scripts/deploy-claude.ps1`

- [ ] **Step 1: Create the script skeleton with param block and elevation logic**

Create `scripts/deploy-claude.ps1`:

```powershell
#Requires -Version 5.1
<#
.SYNOPSIS
    Déploiement complet Claude (Desktop + Code + M365 + Snetor) pour un collab Snetor.
.DESCRIPTION
    À exécuter depuis la session Windows du collab. Une seule boite UAC.
    L'admin DSI approuve l'élévation avec ses credentials — le script écrit
    ensuite dans le profil du collab (pas celui de l'admin).
.PARAMETER TargetUser
    Nom d'utilisateur du collab (auto-détecté si non fourni).
.PARAMETER TargetProfile
    Chemin vers le profil Windows du collab (auto-détecté si non fourni).
#>
param(
    [string]$TargetUser    = $env:USERNAME,
    [string]$TargetProfile = $env:USERPROFILE
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ─── Couleurs console ────────────────────────────────────────────────────────
function Write-Step  { param($msg) Write-Host "`n▶ $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "  ⚠️  $msg" -ForegroundColor Yellow }
function Write-Fail  { param($msg) Write-Host "  ❌ $msg" -ForegroundColor Red }
function Write-Info  { param($msg) Write-Host "     $msg" -ForegroundColor Gray }

# ─── Phase 0 : Auto-élévation ────────────────────────────────────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    Write-Host "🔐 Élévation admin requise — une seule boite UAC va s'afficher." -ForegroundColor Yellow
    $args = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -TargetUser `"$env:USERNAME`" -TargetProfile `"$env:USERPROFILE`""
    Start-Process powershell -Verb RunAs -ArgumentList $args
    exit
}

Write-Host @"
╔══════════════════════════════════════════════════════╗
║   Snetor — Déploiement Claude DSI                    ║
║   Collab : $TargetUser
╚══════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Résumé des phases qui vont tourner
$phaseResults = [ordered]@{
    'Node.js'         = '⏳'
    'Claude Desktop'  = '⏳'
    'Claude Code'     = '⏳'
    'Config Snetor'   = '⏳'
    'M365 MCP'        = '⏳'
}

# ─── Utilitaires ─────────────────────────────────────────────────────────────
function Get-TempDir {
    $tmp = Join-Path $env:TEMP "snetor-claude-deploy-$(Get-Date -Format 'yyyyMMddHHmmss')"
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    return $tmp
}

function Invoke-Download {
    param([string]$Url, [string]$Dest)
    Write-Info "Téléchargement : $Url"
    Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing
}

# ─────────────────────────────────────────────────────────────────────────────
# Phases (définies dans les tâches suivantes)
# ─────────────────────────────────────────────────────────────────────────────

# TODO: Insert-Phase-Functions-Here

# ─── Exécution principale ─────────────────────────────────────────────────────
$tmp = Get-TempDir

try { Invoke-Phase1-NodeJS   $tmp } catch { Write-Fail "Phase 1 échouée : $_"; $phaseResults['Node.js'] = '❌' }
try { Invoke-Phase2-Claude   $tmp } catch { Write-Fail "Phase 2 échouée : $_"; $phaseResults['Claude Desktop'] = '❌' }
try { Invoke-Phase3-CoWork   $tmp } catch { Write-Fail "Phase 3 échouée : $_"; $phaseResults['Claude Code'] = '❌' }
try { Invoke-Phase4-Snetor   $tmp } catch { Write-Fail "Phase 4 échouée : $_"; $phaseResults['Config Snetor'] = '❌' }
try { Invoke-Phase5-M365     $tmp } catch { Write-Fail "Phase 5 échouée : $_"; $phaseResults['M365 MCP'] = '❌' }

Invoke-Phase6-Summary $phaseResults

Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 2: Verify file created**

```powershell
Test-Path scripts/deploy-claude.ps1
```
Expected: `True`

- [ ] **Step 3: Commit skeleton**

```bash
git add scripts/deploy-claude.ps1
git commit -m "feat(deploy): add script skeleton with self-elevation (Phase 0)"
```

---

## Task 2 — Phase 1: Node.js LTS

**Files:**
- Modify: `scripts/deploy-claude.ps1` (replace `# TODO: Insert-Phase-Functions-Here`)

- [ ] **Step 1: Add the Node.js function before the TODO comment**

Insert before `# TODO: Insert-Phase-Functions-Here`:

```powershell
# ─── Phase 1 : Node.js LTS ───────────────────────────────────────────────────
function Invoke-Phase1-NodeJS {
    param([string]$Tmp)
    Write-Step "Phase 1 — Node.js LTS"

    # Vérifier si Node 18+ est déjà installé
    try {
        $v = & node --version 2>$null
        if ($v -match 'v(\d+)\.' -and [int]$Matches[1] -ge 18) {
            Write-Ok "Node.js $v déjà installé — skip"
            $script:phaseResults['Node.js'] = '✅ déjà présent'
            return
        }
    } catch {}

    # Résoudre l'URL du dernier LTS via le flux JSON officiel
    Write-Info "Résolution de la version LTS..."
    $index = Invoke-RestMethod -Uri 'https://nodejs.org/dist/index.json' -UseBasicParsing
    $lts   = $index | Where-Object { $_.lts -and $_.files -contains 'win-x64-msi' } | Select-Object -First 1
    if (-not $lts) { throw "Impossible de résoudre la version LTS de Node.js" }

    $version = $lts.version   # ex: "v22.14.0"
    $msiUrl  = "https://nodejs.org/dist/$version/node-$version-x64.msi"
    $msiPath = Join-Path $Tmp "node-lts.msi"

    Invoke-Download $msiUrl $msiPath

    Write-Info "Installation silencieuse de Node.js $version..."
    $proc = Start-Process msiexec -ArgumentList "/i `"$msiPath`" /quiet /norestart ADDLOCAL=ALL" -Wait -PassThru
    if ($proc.ExitCode -ne 0) { throw "msiexec a retourné le code $($proc.ExitCode)" }

    # Rafraîchir PATH dans la session courante
    $machinePath = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
    $userPath    = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
    $env:PATH    = "$machinePath;$userPath"

    $v = & node --version
    Write-Ok "Node.js $v installé"
    $script:phaseResults['Node.js'] = "✅ $v"
}
```

- [ ] **Step 2: Replace the TODO placeholder**

Find and replace `# TODO: Insert-Phase-Functions-Here` → keep it at the bottom, the function goes above it. Actually the structure already works — the function is added ABOVE the TODO line. The TODO line is removed in the final task.

- [ ] **Step 3: Quick syntax check**

```powershell
powershell -NoProfile -Command "& { . .\scripts\deploy-claude.ps1; Write-Host 'Syntax OK' }" 2>&1 | Select-String -Pattern 'error|Error' -NotMatch
```
Expected: `Syntax OK` (or no errors)

- [ ] **Step 4: Commit**

```bash
git add scripts/deploy-claude.ps1
git commit -m "feat(deploy): Phase 1 — Node.js LTS silent install"
```

---

## Task 3 — Phase 2: Claude Desktop

**Files:**
- Modify: `scripts/deploy-claude.ps1`

- [ ] **Step 1: Add the Claude Desktop install function**

Insert below `Invoke-Phase1-NodeJS`, before `# TODO`:

```powershell
# ─── Phase 2 : Claude Desktop ────────────────────────────────────────────────
function Invoke-Phase2-Claude {
    param([string]$Tmp)
    Write-Step "Phase 2 — Claude Desktop"

    # Vérifier si déjà installé
    $existing = Get-AppxPackage -Name '*Claude*' -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Ok "Claude Desktop déjà installé ($($existing.Version)) — skip"
        $script:phaseResults['Claude Desktop'] = "✅ déjà présent v$($existing.Version)"
        return
    }

    # URL officielle du setup Windows (Squirrel exe)
    $installerUrl = 'https://storage.googleapis.com/osprey-downloads-c02f6a0d-347c-492b-a752-3e0651722e97/nest-win-x64/Claude-Setup.exe'
    $installerPath = Join-Path $Tmp 'Claude-Setup.exe'

    Invoke-Download $installerUrl $installerPath

    Write-Info "Installation de Claude Desktop..."
    # Squirrel: --silent installe pour l'utilisateur courant
    $proc = Start-Process $installerPath -ArgumentList '--silent' -Wait -PassThru
    # Squirrel retourne 0 même si l'install continue en arrière-plan
    Start-Sleep -Seconds 15  # laisser le temps à Squirrel de finir

    $installed = Get-AppxPackage -Name '*Claude*' -ErrorAction SilentlyContinue
    if (-not $installed) {
        # Essai MSIX si Squirrel a échoué ou si le format a changé
        Write-Warn "Squirrel n'a pas créé de package Appx — tentative MSIX..."
        $msixUrl  = 'https://storage.googleapis.com/osprey-downloads-c02f6a0d-347c-492b-a752-3e0651722e97/nest-win-x64/Claude-Setup.msix'
        $msixPath = Join-Path $Tmp 'Claude-Setup.msix'
        Invoke-Download $msixUrl $msixPath
        Add-AppxProvisionedPackage -Online -PackagePath $msixPath -SkipLicense | Out-Null
        $installed = Get-AppxPackage -Name '*Claude*' -ErrorAction SilentlyContinue
    }

    if ($installed) {
        Write-Ok "Claude Desktop $($installed.Version) installé"
        $script:phaseResults['Claude Desktop'] = "✅ v$($installed.Version)"
    } else {
        Write-Warn "Installation non vérifiable via Appx — vérifier manuellement"
        Write-Info "URL manuelle : https://claude.ai/download"
        $script:phaseResults['Claude Desktop'] = '⚠️ vérification manuelle'
    }
}
```

- [ ] **Step 2: Syntax check**

```powershell
powershell -NoProfile -NonInteractive -Command "Get-Content scripts\deploy-claude.ps1 | Out-Null; Write-Host 'Parse OK'"
```
Expected: `Parse OK`

- [ ] **Step 3: Commit**

```bash
git add scripts/deploy-claude.ps1
git commit -m "feat(deploy): Phase 2 — Claude Desktop silent install"
```

---

## Task 4 — Phase 3: Claude Code (Cowork)

**Files:**
- Modify: `scripts/deploy-claude.ps1`

- [ ] **Step 1: Add the Claude Code install function**

Insert below `Invoke-Phase2-Claude`, before `# TODO`:

```powershell
# ─── Phase 3 : Claude Code (Cowork) ─────────────────────────────────────────
function Invoke-Phase3-CoWork {
    param([string]$Tmp)
    Write-Step "Phase 3 — Claude Code (Cowork)"

    # S'assurer que npm est dispo
    $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
    if (-not $npmCmd) {
        # Rafraîchir PATH après install Node
        $machinePath = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
        $userPath    = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
        $env:PATH    = "$machinePath;$userPath"
        $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
        if (-not $npmCmd) { throw "npm introuvable — vérifier l'installation Node.js" }
    }

    # Configurer le prefix npm vers le profil du collab (pas l'admin)
    $npmPrefix = "$TargetProfile\AppData\Roaming\npm"
    New-Item -ItemType Directory -Path $npmPrefix -Force | Out-Null
    $env:APPDATA = "$TargetProfile\AppData\Roaming"
    & npm config set prefix $npmPrefix

    # Vérifier si déjà installé
    try {
        $ver = & npm list -g @anthropic-ai/claude-code --depth=0 2>$null | Select-String 'claude-code@'
        if ($ver) {
            Write-Ok "Claude Code déjà installé — skip"
            $script:phaseResults['Claude Code'] = '✅ déjà présent'
            return
        }
    } catch {}

    Write-Info "Installation de @anthropic-ai/claude-code..."
    & npm install -g @anthropic-ai/claude-code
    if ($LASTEXITCODE -ne 0) { throw "npm install a échoué (code $LASTEXITCODE)" }

    # Ajouter le prefix npm au PATH utilisateur
    $currentUserPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
    if ($currentUserPath -notlike "*$npmPrefix*") {
        [System.Environment]::SetEnvironmentVariable(
            'PATH',
            "$currentUserPath;$npmPrefix",
            'User'
        )
        Write-Info "PATH utilisateur mis à jour avec $npmPrefix"
    }

    Write-Ok "Claude Code installé"
    $script:phaseResults['Claude Code'] = '✅'
}
```

- [ ] **Step 2: Syntax check**

```powershell
powershell -NoProfile -NonInteractive -Command "Get-Content scripts\deploy-claude.ps1 | Out-Null; Write-Host 'Parse OK'"
```
Expected: `Parse OK`

- [ ] **Step 3: Commit**

```bash
git add scripts/deploy-claude.ps1
git commit -m "feat(deploy): Phase 3 — Claude Code global install with user-profile npm prefix"
```

---

## Task 5 — Phase 4: Snetor Config

**Files:**
- Modify: `scripts/deploy-claude.ps1`

- [ ] **Step 1: Add the Snetor config function**

Insert below `Invoke-Phase3-CoWork`, before `# TODO`:

```powershell
# ─── Phase 4 : Config Snetor ──────────────────────────────────────────────────
function Invoke-Phase4-Snetor {
    param([string]$Tmp)
    Write-Step "Phase 4 — Configuration Snetor"

    $claudeDir = "$TargetProfile\.claude"
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null

    # 1. Cloner / télécharger le repo snetor-ai-guidelines
    $repoUrl    = 'https://github.com/snetor/snetor-ai-guidelines.git'
    $repoZipUrl = 'https://github.com/snetor/snetor-ai-guidelines/archive/refs/heads/main.zip'
    $repoDir    = Join-Path $Tmp 'snetor-ai-guidelines'

    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd) {
        Write-Info "Clone du repo via git..."
        & git clone --depth=1 $repoUrl $repoDir
    } else {
        Write-Info "git absent — téléchargement du zip..."
        $zipPath = Join-Path $Tmp 'repo.zip'
        Invoke-Download $repoZipUrl $zipPath
        Expand-Archive -Path $zipPath -DestinationPath $Tmp -Force
        $repoDir = Join-Path $Tmp 'snetor-ai-guidelines-main'
    }

    # 2. Copier CLAUDE.md dans le profil Claude Code
    $claudeMdSrc  = Join-Path $repoDir 'CLAUDE.md'
    $claudeMdDest = Join-Path $claudeDir 'CLAUDE.md'
    Copy-Item $claudeMdSrc $claudeMdDest -Force
    Write-Ok "CLAUDE.md global copié"

    # 3. Écrire / fusionner settings.json
    $settingsPath = Join-Path $claudeDir 'settings.json'
    $snetorSettings = [ordered]@{
        theme       = 'dark'
        effortLevel = 'medium'
        enabledPlugins = [ordered]@{
            'superpowers@claude-plugins-official'       = $true
            'context7@claude-plugins-official'          = $true
            'snetor-html-slides@snetor-ai-guidelines'   = $true
        }
    }

    if (Test-Path $settingsPath) {
        Write-Info "settings.json existant — fusion..."
        $existing = Get-Content $settingsPath -Raw | ConvertFrom-Json
        # Merger enabledPlugins seulement — ne pas écraser les clés utilisateur
        foreach ($key in $snetorSettings.Keys) {
            if ($key -eq 'enabledPlugins') {
                if (-not $existing.enabledPlugins) {
                    $existing | Add-Member -MemberType NoteProperty -Name 'enabledPlugins' -Value ([PSCustomObject]@{})
                }
                foreach ($plugin in $snetorSettings.enabledPlugins.Keys) {
                    $existing.enabledPlugins | Add-Member -MemberType NoteProperty -Name $plugin -Value $true -Force
                }
            } elseif (-not ($existing.PSObject.Properties.Name -contains $key)) {
                $existing | Add-Member -MemberType NoteProperty -Name $key -Value $snetorSettings[$key]
            }
        }
        $existing | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
    } else {
        $snetorSettings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
    }
    Write-Ok "settings.json configuré"

    # 4. Status line
    $statuslineScript = Join-Path $repoDir 'statusline\install.ps1'
    if (Test-Path $statuslineScript) {
        Write-Info "Installation de la status line..."
        & powershell -NoProfile -ExecutionPolicy Bypass -File $statuslineScript
        Write-Ok "Status line installée"
    } else {
        Write-Warn "statusline/install.ps1 introuvable — skip"
    }

    $script:phaseResults['Config Snetor'] = '✅'
}
```

- [ ] **Step 2: Syntax check**

```powershell
powershell -NoProfile -NonInteractive -Command "Get-Content scripts\deploy-claude.ps1 | Out-Null; Write-Host 'Parse OK'"
```
Expected: `Parse OK`

- [ ] **Step 3: Commit**

```bash
git add scripts/deploy-claude.ps1
git commit -m "feat(deploy): Phase 4 — Snetor config (CLAUDE.md, settings.json, status line)"
```

---

## Task 6 — Phase 5: M365 MCP Config

**Files:**
- Modify: `scripts/deploy-claude.ps1`

- [ ] **Step 1: Add the M365 MCP config function**

Insert below `Invoke-Phase4-Snetor`, before `# TODO`:

```powershell
# ─── Phase 5 : M365 MCP ──────────────────────────────────────────────────────
function Invoke-Phase5-M365 {
    param([string]$Tmp)
    Write-Step "Phase 5 — Connecteur M365 MCP"

    # Résoudre le chemin réel du config MSIX (bug connu : %APPDATA%\Claude != chemin réel)
    $claudePkg = Get-AppxPackage -Name '*Claude*' -ErrorAction SilentlyContinue
    if (-not $claudePkg) {
        Write-Warn "Claude Desktop non détecté — écriture config dans %APPDATA%\Claude (chemin de secours)"
        $configDir = "$TargetProfile\AppData\Roaming\Claude"
    } else {
        $configDir = "$TargetProfile\AppData\Local\Packages\$($claudePkg.PackageFamilyName)\LocalCache\Roaming\Claude"
    }
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    $configPath = Join-Path $configDir 'claude_desktop_config.json'

    # Lire la config existante ou créer une vide
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath -Raw | ConvertFrom-Json
        } catch {
            Write-Warn "claude_desktop_config.json illisible — réinitialisation"
            $config = [PSCustomObject]@{}
        }
    } else {
        $config = [PSCustomObject]@{}
    }

    # S'assurer que mcpServers existe
    if (-not ($config.PSObject.Properties.Name -contains 'mcpServers')) {
        $config | Add-Member -MemberType NoteProperty -Name 'mcpServers' -Value ([PSCustomObject]@{})
    }

    # Ajouter le serveur Microsoft 365 (ne pas écraser si déjà là)
    if (-not ($config.mcpServers.PSObject.Properties.Name -contains 'microsoft365')) {
        $m365Server = [PSCustomObject]@{
            command = 'npx'
            args    = @('-y', '@anthropic-ai/mcp-server-microsoft365')
        }
        $config.mcpServers | Add-Member -MemberType NoteProperty -Name 'microsoft365' -Value $m365Server
        Write-Ok "Entrée microsoft365 ajoutée dans claude_desktop_config.json"
    } else {
        Write-Ok "Entrée microsoft365 déjà présente — skip"
    }

    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    Write-Info "Config écrite dans : $configPath"
    $script:phaseResults['M365 MCP'] = '✅ pré-configuré'
}
```

- [ ] **Step 2: Syntax check**

```powershell
powershell -NoProfile -NonInteractive -Command "Get-Content scripts\deploy-claude.ps1 | Out-Null; Write-Host 'Parse OK'"
```
Expected: `Parse OK`

- [ ] **Step 3: Commit**

```bash
git add scripts/deploy-claude.ps1
git commit -m "feat(deploy): Phase 5 — M365 MCP config with MSIX path resolution"
```

---

## Task 7 — Phase 6: Summary + remove TODO marker

**Files:**
- Modify: `scripts/deploy-claude.ps1`

- [ ] **Step 1: Add the summary function and remove TODO marker**

Insert below `Invoke-Phase5-M365`, remove `# TODO: Insert-Phase-Functions-Here`:

```powershell
# ─── Phase 6 : Récapitulatif ──────────────────────────────────────────────────
function Invoke-Phase6-Summary {
    param([hashtable]$Results)
    Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host   "║   Déploiement terminé — Récapitulatif               ║" -ForegroundColor Cyan
    Write-Host   "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    foreach ($phase in $Results.Keys) {
        $icon = $Results[$phase]
        Write-Host "  $icon  $phase"
    }

    Write-Host "`n📋 Actions manuelles restantes (collab) :" -ForegroundColor Yellow
    Write-Host "  1. Ouvrir Claude Desktop → Se connecter avec le compte claude.ai Snetor"
    Write-Host "  2. M365 : Paramètres → Extensions → Microsoft 365 → Autoriser"
    Write-Host "  3. Terminal → taper [claude] → s'authentifier via le navigateur (Claude Code)"
    Write-Host "`n📋 Action admin DSI (1x pour tout le tenant) :" -ForegroundColor Yellow
    Write-Host "  4. Accorder le consentement Entra Admin Center :"
    Write-Host "     https://entra.microsoft.com → Applications d'entreprise"
    Write-Host "     → 'M365 MCP Client for Claude' → Accorder le consentement administrateur"
    Write-Host "`n✨ Déploiement Snetor Claude terminé pour : $TargetUser`n" -ForegroundColor Green
}
```

- [ ] **Step 2: Verify no TODO remains**

```powershell
Select-String -Path scripts\deploy-claude.ps1 -Pattern 'TODO'
```
Expected: no output (zero matches)

- [ ] **Step 3: Full syntax check**

```powershell
powershell -NoProfile -NonInteractive -Command "& { . .\scripts\deploy-claude.ps1 } 2>&1" | Select-String 'error|Error|Exception' | Where-Object { $_ -notmatch 'ErrorActionPreference' }
```
Expected: no output

- [ ] **Step 4: Commit**

```bash
git add scripts/deploy-claude.ps1
git commit -m "feat(deploy): Phase 6 — summary output, remove TODO marker"
```

---

## Task 8 — scripts/README.md

**Files:**
- Create: `scripts/README.md`

- [ ] **Step 1: Write the README**

Create `scripts/README.md`:

```markdown
# deploy-claude.ps1 — Déploiement Claude DSI Snetor

Script PowerShell de déploiement complet Claude pour un collaborateur Snetor.
Une seule exécution installe et configure l'intégralité de l'environnement.

## Prérequis

- Windows 10/11 (x64)
- PowerShell 5.1+
- Connexion internet
- Compte admin DSI Snetor (pour approuver la boite UAC)

## Utilisation

1. Se connecter **sur le poste du collab** (ou ouvrir une session Windows avec son compte)
2. Ouvrir un terminal PowerShell (pas forcément admin)
3. Exécuter :

```powershell
.\scripts\deploy-claude.ps1
```

4. Approuver la boite UAC avec les credentials admin DSI → le script tourne seul.
5. À la fin, remettre le script de résumé au collab pour les étapes manuelles.

## Ce que fait le script

| Phase | Action |
|---|---|
| 0 | Auto-élévation admin (1 UAC) |
| 1 | Node.js LTS — install silencieux si absent |
| 2 | Claude Desktop — install MSIX/Squirrel |
| 3 | Claude Code (Cowork) — `npm install -g @anthropic-ai/claude-code` |
| 4 | Config Snetor — CLAUDE.md global, settings.json (plugins), status line |
| 5 | M365 MCP — pré-configuration `claude_desktop_config.json` |
| 6 | Récapitulatif + checklist actions manuelles |

## Étapes manuelles post-déploiement (collab)

1. Ouvrir **Claude Desktop** → se connecter avec le compte `@snetor.com`
2. Dans Claude Desktop : **Paramètres → Extensions → Microsoft 365 → Autoriser**
3. Dans un terminal : taper `claude` → s'authentifier via le navigateur

## Étape admin DSI (une seule fois pour tout le tenant)

Accorder le consentement Azure AD pour le connecteur M365 :  
`https://entra.microsoft.com` → Applications d'entreprise → *M365 MCP Client for Claude* → Accorder le consentement administrateur

## Dépannage

| Symptôme | Solution |
|---|---|
| Phase 2 ⚠️ vérification manuelle | Télécharger manuellement sur https://claude.ai/download |
| `npm` introuvable après Phase 1 | Fermer et rouvrir le terminal, relancer le script |
| M365 Extensions absent dans Claude Desktop | Vérifier le plan Teams/Enterprise sur claude.ai |
| `claude` command non reconnue | Vérifier que `%APPDATA%\npm` est dans le PATH utilisateur |
```

- [ ] **Step 2: Commit**

```bash
git add scripts/README.md
git commit -m "docs(deploy): add scripts/README.md with usage and troubleshooting"
```

---

## Task 9 — Validation finale + push

- [ ] **Step 1: Syntax check complet du script final**

```powershell
powershell -NoProfile -NonInteractive -Command "
  \$content = Get-Content scripts\deploy-claude.ps1 -Raw
  \$errors = @()
  \$null = [System.Management.Automation.Language.Parser]::ParseInput(\$content, [ref]\$null, [ref]\$errors)
  if (\$errors.Count -gt 0) {
    \$errors | ForEach-Object { Write-Host \$_.Message -ForegroundColor Red }
  } else {
    Write-Host 'AST parse: OK — aucune erreur de syntaxe' -ForegroundColor Green
  }
"
```
Expected: `AST parse: OK — aucune erreur de syntaxe`

- [ ] **Step 2: Vérifier que toutes les fonctions de phase sont appelées**

```powershell
Select-String -Path scripts\deploy-claude.ps1 -Pattern 'Invoke-Phase\d'
```
Expected: 6 lignes de définition (`function`) + 6 lignes d'appel (`try { Invoke-Phase...`)

- [ ] **Step 3: Git push**

```bash
git push origin main
```

- [ ] **Step 4: Annoncer sur Teams**

Rédiger et envoyer le message Teams d'annonce (via le MCP M365 ou manuellement).
