#Requires -Version 5.1
<#
.SYNOPSIS
    Déploiement complet Claude (Desktop + Code + M365 + Snetor) pour un collab Snetor.
.DESCRIPTION
    À exécuter depuis la session Windows du collab. Une seule boite UAC.
    L'admin DSI approuve l'élévation — le script écrit ensuite dans le profil
    du collab (pas celui de l'admin).
.PARAMETER TargetUser
    Nom d'utilisateur du collab (auto-détecté depuis la session courante).
.PARAMETER TargetProfile
    Chemin vers le profil Windows du collab (auto-détecté depuis la session courante).
.EXAMPLE
    .\deploy-claude.ps1
#>
param(
    [string]$TargetUser    = $env:USERNAME,
    [string]$TargetProfile = $env:USERPROFILE
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ─── Helpers console ─────────────────────────────────────────────────────────
function Write-Step { param($msg) Write-Host "`n▶  $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "   ✅ $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "   ⚠️  $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "   ❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "      $msg" -ForegroundColor Gray }

# ─── Phase 0 : Auto-élévation ─────────────────────────────────────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    Write-Host "🔐 Élévation admin requise — une seule boite UAC va s'afficher." -ForegroundColor Yellow
    $escapedScript  = $PSCommandPath -replace '"', '\"'
    $escapedUser    = $TargetUser    -replace '"', '\"'
    $escapedProfile = $TargetProfile -replace '"', '\"'
    $psArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$escapedScript`" -TargetUser `"$escapedUser`" -TargetProfile `"$escapedProfile`""
    Start-Process powershell -Verb RunAs -ArgumentList $psArgs
    exit 0
}

Write-Host ""
Write-Host "  Snetor -- Deploiement Claude DSI" -ForegroundColor Cyan
Write-Host "  Collab  : $TargetUser" -ForegroundColor Cyan
Write-Host "  Profil  : $TargetProfile" -ForegroundColor Cyan
Write-Host ""

$phaseResults = [ordered]@{
    'Node.js'        = '⏳'
    'Claude Desktop' = '⏳'
    'Claude Code'    = '⏳'
    'Config Snetor'  = '⏳'
    'M365 MCP'       = '⏳'
}

# ─── Utilitaires ──────────────────────────────────────────────────────────────
function Get-TempDir {
    $tmp = Join-Path $env:TEMP "snetor-claude-$(Get-Date -Format 'yyyyMMddHHmmss')"
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    return $tmp
}

function Invoke-Download {
    param([string]$Url, [string]$Dest)
    Write-Info "Téléchargement : $Url"
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing
    $ProgressPreference = 'Continue'
}

function Refresh-PATH {
    $m = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
    $u = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
    $env:PATH = "$m;$u"
}

# ─── Phase 1 : Node.js LTS ────────────────────────────────────────────────────
function Invoke-Phase1-NodeJS {
    param([string]$Tmp)
    Write-Step "Phase 1 — Node.js LTS"

    # Vérifier si Node 18+ déjà présent
    try {
        $v = & node --version 2>$null
        if ($v -match 'v(\d+)\.' -and [int]$Matches[1] -ge 18) {
            Write-Ok "Node.js $v déjà installé — skip"
            $script:phaseResults['Node.js'] = "✅ déjà présent ($v)"
            return
        }
    } catch { }

    Write-Info "Résolution de la version LTS via nodejs.org/dist/index.json ..."
    $index = Invoke-RestMethod -Uri 'https://nodejs.org/dist/index.json' -UseBasicParsing
    $lts = $index | Where-Object { $_.lts -and ($_.files -contains 'win-x64-msi') } | Select-Object -First 1
    if (-not $lts) { throw "Impossible de résoudre la version LTS de Node.js" }

    $version = $lts.version
    $msiUrl  = "https://nodejs.org/dist/$version/node-$version-x64.msi"
    $msiPath = Join-Path $Tmp 'node-lts.msi'

    Invoke-Download $msiUrl $msiPath

    Write-Info "Installation silencieuse de Node.js $version ..."
    $proc = Start-Process msiexec -ArgumentList "/i `"$msiPath`" /quiet /norestart ADDLOCAL=ALL" -Wait -PassThru
    if ($proc.ExitCode -ne 0) { throw "msiexec a retourné le code $($proc.ExitCode)" }

    Refresh-PATH

    $v = & node --version 2>$null
    Write-Ok "Node.js $v installé"
    $script:phaseResults['Node.js'] = "✅ $v"
}

# ─── Phase 2 : Claude Desktop ─────────────────────────────────────────────────
function Invoke-Phase2-Claude {
    param([string]$Tmp)
    Write-Step "Phase 2 — Claude Desktop"

    $existing = Get-AppxPackage -Name '*Claude*' -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Ok "Claude Desktop déjà installé (v$($existing.Version)) — skip"
        $script:phaseResults['Claude Desktop'] = "✅ déjà présent v$($existing.Version)"
        return
    }

    # Squirrel exe (format principal distribué par Anthropic)
    $exeUrl  = 'https://storage.googleapis.com/osprey-downloads-c02f6a0d-347c-492b-a752-3e0651722e97/nest-win-x64/Claude-Setup.exe'
    $exePath = Join-Path $Tmp 'Claude-Setup.exe'

    Invoke-Download $exeUrl $exePath

    Write-Info "Installation de Claude Desktop (Squirrel) ..."
    Start-Process $exePath -ArgumentList '--silent' -Wait
    # Squirrel installe en arrière-plan après le processus parent — attendre
    Write-Info "En attente de la fin de l'installation Squirrel ..."
    $deadline = (Get-Date).AddSeconds(60)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 5
        if (Get-AppxPackage -Name '*Claude*' -ErrorAction SilentlyContinue) { break }
        # Squirrel peut aussi installer sans package Appx (exe dans AppData)
        $claudeExe = Join-Path $TargetProfile 'AppData\Local\AnthropicClaude\claude.exe'
        if (Test-Path $claudeExe) { break }
    }

    $installed = Get-AppxPackage -Name '*Claude*' -ErrorAction SilentlyContinue
    $claudeExe = Join-Path $TargetProfile 'AppData\Local\AnthropicClaude\claude.exe'

    if ($installed) {
        Write-Ok "Claude Desktop v$($installed.Version) installé"
        $script:phaseResults['Claude Desktop'] = "✅ v$($installed.Version)"
    } elseif (Test-Path $claudeExe) {
        Write-Ok "Claude Desktop installé (Squirrel — $claudeExe)"
        $script:phaseResults['Claude Desktop'] = '✅ Squirrel'
    } else {
        Write-Warn "Installation non vérifiable — vérifier manuellement"
        Write-Info "URL : https://claude.ai/download"
        $script:phaseResults['Claude Desktop'] = '⚠️ vérification manuelle'
    }
}

# ─── Phase 3 : Claude Code (Cowork) ──────────────────────────────────────────
function Invoke-Phase3-CoWork {
    param([string]$Tmp)
    Write-Step "Phase 3 — Claude Code (Cowork)"

    Refresh-PATH

    $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
    if (-not $npmCmd) { throw "npm introuvable — vérifier l'installation Node.js (Phase 1)" }

    # Pointer le prefix npm vers le profil du collab (pas celui de l'admin)
    $npmPrefix = "$TargetProfile\AppData\Roaming\npm"
    New-Item -ItemType Directory -Path $npmPrefix -Force | Out-Null
    $env:APPDATA = "$TargetProfile\AppData\Roaming"
    & npm config set prefix $npmPrefix 2>$null

    # Vérifier si déjà installé
    $globalList = & npm list -g --depth=0 2>$null
    if ($globalList -match 'claude-code') {
        Write-Ok "Claude Code déjà installé — skip"
        $script:phaseResults['Claude Code'] = '✅ déjà présent'
        return
    }

    Write-Info "npm install -g @anthropic-ai/claude-code ..."
    & npm install -g '@anthropic-ai/claude-code'
    if ($LASTEXITCODE -ne 0) { throw "npm install a échoué (code $LASTEXITCODE)" }

    # Ajouter le prefix npm au PATH utilisateur persistant
    $currentUserPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
    if ($currentUserPath -notlike "*$npmPrefix*") {
        [System.Environment]::SetEnvironmentVariable('PATH', "$currentUserPath;$npmPrefix", 'User')
        Write-Info "PATH utilisateur mis à jour : +$npmPrefix"
    }

    Write-Ok "Claude Code installé"
    $script:phaseResults['Claude Code'] = '✅'
}

# ─── Phase 4 : Config Snetor ──────────────────────────────────────────────────
function Invoke-Phase4-Snetor {
    param([string]$Tmp)
    Write-Step "Phase 4 — Configuration Snetor"

    $claudeDir = "$TargetProfile\.claude"
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null

    # Télécharger le repo snetor-ai-guidelines
    $repoDir = Join-Path $Tmp 'snetor-ai-guidelines'
    $gitCmd  = Get-Command git -ErrorAction SilentlyContinue

    if ($gitCmd) {
        Write-Info "Clone du repo snetor-ai-guidelines ..."
        & git clone --depth=1 'https://github.com/snetor/snetor-ai-guidelines.git' $repoDir 2>&1 | Out-Null
    } else {
        Write-Info "git absent — téléchargement du zip ..."
        $zipPath = Join-Path $Tmp 'repo.zip'
        Invoke-Download 'https://github.com/snetor/snetor-ai-guidelines/archive/refs/heads/main.zip' $zipPath
        Expand-Archive -Path $zipPath -DestinationPath $Tmp -Force
        $repoDir = Join-Path $Tmp 'snetor-ai-guidelines-main'
    }

    if (-not (Test-Path $repoDir)) { throw "Impossible de récupérer le repo snetor-ai-guidelines" }

    # 1. CLAUDE.md global
    $claudeMdSrc = Join-Path $repoDir 'CLAUDE.md'
    if (Test-Path $claudeMdSrc) {
        Copy-Item $claudeMdSrc "$claudeDir\CLAUDE.md" -Force
        Write-Ok "CLAUDE.md global copié"
    } else {
        Write-Warn "CLAUDE.md introuvable dans le repo"
    }

    # 2. settings.json (fusion si existant)
    $settingsPath    = "$claudeDir\settings.json"
    $snetorPlugins   = [ordered]@{
        'superpowers@claude-plugins-official'     = $true
        'context7@claude-plugins-official'        = $true
        'snetor-html-slides@snetor-ai-guidelines' = $true
    }
    $snetorDefaults  = [ordered]@{
        theme        = 'dark'
        effortLevel  = 'medium'
    }

    if (Test-Path $settingsPath) {
        Write-Info "settings.json existant — fusion ..."
        try {
            $cfg = Get-Content $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            Write-Warn "settings.json illisible — réinitialisation"
            $cfg = [PSCustomObject]@{}
        }
    } else {
        $cfg = [PSCustomObject]@{}
    }

    # Appliquer les defaults Snetor seulement si la clé n'existe pas
    foreach ($k in $snetorDefaults.Keys) {
        if (-not ($cfg.PSObject.Properties.Name -contains $k)) {
            $cfg | Add-Member -MemberType NoteProperty -Name $k -Value $snetorDefaults[$k]
        }
    }

    # Fusionner enabledPlugins
    if (-not ($cfg.PSObject.Properties.Name -contains 'enabledPlugins')) {
        $cfg | Add-Member -MemberType NoteProperty -Name 'enabledPlugins' -Value ([PSCustomObject]@{})
    }
    foreach ($plugin in $snetorPlugins.Keys) {
        $cfg.enabledPlugins | Add-Member -MemberType NoteProperty -Name $plugin -Value $true -Force
    }

    $cfg | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
    Write-Ok "settings.json configuré (plugins Snetor activés)"

    # 3. Status line
    $statuslineScript = Join-Path $repoDir 'statusline\install.ps1'
    if (Test-Path $statuslineScript) {
        Write-Info "Installation de la status line ..."
        & powershell -NoProfile -ExecutionPolicy Bypass -File $statuslineScript
        Write-Ok "Status line installée"
    } else {
        Write-Warn "statusline/install.ps1 introuvable dans le repo — skip"
    }

    $script:phaseResults['Config Snetor'] = '✅'
}

# ─── Phase 5 : M365 MCP Config ────────────────────────────────────────────────
function Invoke-Phase5-M365 {
    param([string]$Tmp)
    Write-Step "Phase 5 — Connecteur Microsoft 365 MCP"

    # Résoudre le chemin réel du config (bug MSIX : %APPDATA%\Claude != chemin réel)
    $claudePkg = Get-AppxPackage -Name '*Claude*' -ErrorAction SilentlyContinue

    if ($claudePkg) {
        $configDir = "$TargetProfile\AppData\Local\Packages\$($claudePkg.PackageFamilyName)\LocalCache\Roaming\Claude"
    } else {
        # Squirrel ou vérification manuelle — utiliser le chemin de secours
        $configDir = "$TargetProfile\AppData\Roaming\Claude"
        Write-Warn "Package Appx Claude non détecté — chemin de secours : $configDir"
    }

    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    $configPath = Join-Path $configDir 'claude_desktop_config.json'

    # Lire config existante ou créer un objet vide
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            Write-Warn "claude_desktop_config.json illisible — réinitialisation"
            $config = [PSCustomObject]@{}
        }
    } else {
        $config = [PSCustomObject]@{}
    }

    # Assurer que mcpServers existe
    if (-not ($config.PSObject.Properties.Name -contains 'mcpServers')) {
        $config | Add-Member -MemberType NoteProperty -Name 'mcpServers' -Value ([PSCustomObject]@{})
    }

    # Ajouter microsoft365 seulement si absent
    if ($config.mcpServers.PSObject.Properties.Name -contains 'microsoft365') {
        Write-Ok "Entrée microsoft365 déjà présente dans claude_desktop_config.json — skip"
    } else {
        $m365 = [PSCustomObject]@{
            command = 'npx'
            args    = @('-y', '@anthropic-ai/mcp-server-microsoft365')
        }
        $config.mcpServers | Add-Member -MemberType NoteProperty -Name 'microsoft365' -Value $m365
        Write-Ok "Entrée microsoft365 ajoutée"
    }

    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    Write-Info "Config écrite dans : $configPath"
    $script:phaseResults['M365 MCP'] = '✅ pré-configuré'
}

# ─── Phase 6 : Récapitulatif ──────────────────────────────────────────────────
function Invoke-Phase6-Summary {
    param([System.Collections.Specialized.OrderedDictionary]$Results)

    Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host   "║        Déploiement terminé — Récapitulatif               ║" -ForegroundColor Cyan
    Write-Host   "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    foreach ($phase in $Results.Keys) {
        $icon = $Results[$phase]
        Write-Host "  $icon  $phase"
    }

    Write-Host "`n📋 Actions manuelles restantes (à faire par le collab) :" -ForegroundColor Yellow
    Write-Host "  1. Ouvrir Claude Desktop → Se connecter avec le compte @snetor.com"
    Write-Host "  2. Dans Claude Desktop : Paramètres → Extensions → Microsoft 365 → Autoriser"
    Write-Host "  3. Dans un terminal : taper [claude] → s'authentifier via le navigateur"

    Write-Host "`n📋 Action admin DSI — une seule fois pour tout le tenant :" -ForegroundColor Yellow
    Write-Host "  4. https://entra.microsoft.com → Applications d'entreprise"
    Write-Host "     → 'M365 MCP Client for Claude' → Accorder le consentement administrateur"

    Write-Host "`n✨ Déploiement Snetor Claude terminé pour : $script:TargetUser`n" -ForegroundColor Green
}

# ─── Exécution principale ─────────────────────────────────────────────────────
$tmp = Get-TempDir

try { Invoke-Phase1-NodeJS  $tmp } catch { Write-Fail "Phase 1 échouée : $_"; $phaseResults['Node.js']        = '❌' }
try { Invoke-Phase2-Claude  $tmp } catch { Write-Fail "Phase 2 échouée : $_"; $phaseResults['Claude Desktop'] = '❌' }
try { Invoke-Phase3-CoWork  $tmp } catch { Write-Fail "Phase 3 échouée : $_"; $phaseResults['Claude Code']    = '❌' }
try { Invoke-Phase4-Snetor  $tmp } catch { Write-Fail "Phase 4 échouée : $_"; $phaseResults['Config Snetor'] = '❌' }
try { Invoke-Phase5-M365    $tmp } catch { Write-Fail "Phase 5 échouée : $_"; $phaseResults['M365 MCP']       = '❌' }

Invoke-Phase6-Summary $phaseResults

Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue

# Maintenir la fenêtre ouverte si lancée en double-clic
if ($Host.Name -eq 'ConsoleHost' -and -not $psISE) {
    Write-Host "Appuyez sur une touche pour fermer ..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
}
