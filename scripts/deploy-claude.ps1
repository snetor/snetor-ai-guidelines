#Requires -Version 5.1

<#
.SYNOPSIS
    Déploiement complet Claude (Desktop + Code + M365 + Snetor) pour un collab Snetor.
.DESCRIPTION
    Compatible avec deux modes d'exécution :
      - Session Windows du collab (UAC classique, une seule boite d'élévation)
      - Déploiement NinjaOne (script lancé en SYSTEM, détection auto du collab connecté)

    Dans les deux cas, l'installation s'écrit dans le profil du collab.
.PARAMETER TargetUser
    Nom d'utilisateur du collab. Auto-détecté depuis la session interactive (NinjaOne)
    ou depuis la session courante.
.PARAMETER TargetProfile
    Chemin vers le profil Windows du collab. Auto-détecté si absent.
.EXAMPLE
    .\deploy-claude.ps1
#>

param(
    [string]$TargetUser    = '',
    [string]$TargetProfile = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# TLS 1.2 obligatoire : Windows PowerShell 5.1 négocie TLS 1.0/1.1 par défaut, ce que
# nodejs.org / api.github.com / claude.ai refusent → tous les téléchargements échoueraient.
[Net.ServicePointManager]::SecurityProtocol = `
    [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

# ─── Helpers console ─────────────────────────────────────────────────────────
function Write-Step { param($msg) Write-Host "`n▶  $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "   ✅ $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "   ⚠️  $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "   ❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "      $msg" -ForegroundColor Gray }

# ─── Detection de l'utilisateur interactif (contexte SYSTEM NinjaOne) ────────
# Quand NinjaOne exécute ce script, le processus tourne en SYSTEM.
# On détecte la session console active pour écrire dans le bon profil et
# afficher les notifications GUI dans la bonne session Windows.
$script:TargetUserFull = $null   # 'DOMAINE\user' — utilisé par Invoke-AsLoggedInUser

$isSystem = [Security.Principal.WindowsIdentity]::GetCurrent().IsSystem

if ($isSystem) {
    Write-Host "  Contexte SYSTEM detecte (NinjaOne) — detection de la session interactive ..." -ForegroundColor DarkGray

    # Résout le profil Windows à partir d'un SID via ProfileList dans le registre.
    # C'est la seule méthode fiable : le nom de dossier peut différer du nom de session.
    function Resolve-ProfileFromSid {
        param([string]$Sid)
        $key = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\$Sid"
        $prop = Get-ItemProperty $key -Name ProfileImagePath -ErrorAction SilentlyContinue
        return $prop.ProfileImagePath
    }

    # Methode 1 : query user — renvoie la session console/RDP active
    try {
        $quserLines = & query user 2>$null
        if ($quserLines) {
            # Ligne active : commence par '>' ou contient 'Active'
            $activeLine = $quserLines | Where-Object { $_ -match 'Active' } | Select-Object -First 1
            if ($activeLine -and $activeLine -match '^\s*>?\s*(\S+)') {
                $detectedShort = $Matches[1].TrimStart('>')
                if (-not $TargetUser) { $TargetUser = $detectedShort }

                # Résoudre le SID du compte, puis le profil via ProfileList
                try {
                    $account = New-Object System.Security.Principal.NTAccount($detectedShort)
                    $userSid = $account.Translate([System.Security.Principal.SecurityIdentifier]).Value
                    $script:TargetUserFull = $account.Value

                    if (-not $TargetProfile) {
                        $resolved = Resolve-ProfileFromSid $userSid
                        if ($resolved) { $TargetProfile = $resolved }
                    }
                } catch {
                    $script:TargetUserFull = $detectedShort
                }
            }
        }
    } catch {
        Write-Warn "query user a echoue : $_"
    }

    # Methode 2 fallback : Win32_ComputerSystem.UserName ('DOMAINE\user')
    if (-not $script:TargetUserFull) {
        try {
            $cs = Get-CimInstance Win32_ComputerSystem -ErrorAction SilentlyContinue
            if ($cs -and $cs.UserName) {
                $script:TargetUserFull = $cs.UserName
                $shortName = $cs.UserName -replace '^.*\\', ''
                if (-not $TargetUser) { $TargetUser = $shortName }

                if (-not $TargetProfile) {
                    try {
                        $account = New-Object System.Security.Principal.NTAccount($cs.UserName)
                        $userSid = $account.Translate([System.Security.Principal.SecurityIdentifier]).Value
                        $resolved = Resolve-ProfileFromSid $userSid
                        if ($resolved) { $TargetProfile = $resolved }
                    } catch { }
                }
            }
        } catch {
            Write-Warn "Win32_ComputerSystem.UserName indisponible : $_"
        }
    }

    if ($script:TargetUserFull) {
        Write-Host "  Utilisateur interactif : $script:TargetUserFull" -ForegroundColor DarkGray
    } else {
        Write-Warn "Aucune session interactive detectee — les notifications GUI seront ignorees"
    }
} else {
    # Session normale (non-SYSTEM) : l'utilisateur courant est le collab
    $script:TargetUserFull = "$env:USERDOMAIN\$env:USERNAME"
}

# Valeurs par défaut si non renseignées et non-SYSTEM
if (-not $TargetUser)    { $TargetUser    = $env:USERNAME }
if (-not $TargetProfile) { $TargetProfile = $env:USERPROFILE }

# ─── Phase 0 : Auto-élévation (ignorée en contexte SYSTEM NinjaOne) ──────────
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    Write-Host "🔐 Élévation admin requise — une seule boite UAC va s'afficher." -ForegroundColor Yellow
    $escapedScript  = $PSCommandPath -replace '"', '\"'
    $escapedUser    = $TargetUser    -replace '"', '\"'
    $escapedProfile = $TargetProfile -replace '"', '\"'
    $psArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$escapedScript`" -TargetUser `"$escapedUser`" -TargetProfile `"$escapedProfile`""
    # 'powershell.exe' = Windows PowerShell 5.1 (jamais pwsh 7, absent du parc Snetor)
    Start-Process powershell.exe -Verb RunAs -ArgumentList $psArgs
    exit 0
}

Write-Host ""
Write-Host "  Snetor -- Deploiement Claude DSI" -ForegroundColor Cyan
Write-Host "  Collab  : $TargetUser" -ForegroundColor Cyan
Write-Host "  Profil  : $TargetProfile" -ForegroundColor Cyan
Write-Host ""

# Pointer les variables d'env vers le profil du collab (pas celui de l'admin élevé)
$env:USERPROFILE = $TargetProfile
$env:APPDATA     = "$TargetProfile\AppData\Roaming"

$phaseResults = [ordered]@{
    'Node.js'        = '⏳'
    'Git'            = '⏳'
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

# Écrit du JSON en UTF-8 SANS BOM. En PS 5.1, 'Set-Content -Encoding UTF8' ajoute un BOM
# qui casse certains parseurs (Claude Desktop, npm) → on passe par .NET sans BOM.
function Set-JsonFile {
    param([object]$Object, [string]$Path)
    $json = $Object | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($Path, $json, (New-Object System.Text.UTF8Encoding($false)))
}

# Résout le dernier asset d'une release GitHub. L'API exige un User-Agent (sinon 403).
function Get-GitHubLatestAsset {
    param([string]$Repo, [string]$NamePattern)
    $api = "https://api.github.com/repos/$Repo/releases/latest"
    $rel = Invoke-RestMethod -Uri $api -UseBasicParsing -Headers @{ 'User-Agent' = 'snetor-deploy-claude' }
    $asset = $rel.assets | Where-Object { $_.name -match $NamePattern } | Select-Object -First 1
    if (-not $asset) { throw "Aucun asset '$NamePattern' dans la dernière release de $Repo" }
    return [PSCustomObject]@{ Name = $asset.name; Url = $asset.browser_download_url }
}

# ─── Notifications GUI dans la session du collab ──────────────────────────────
# Construit puis affiche une boite de dialogue WinForms (style Snetor) DANS la
# session interactive du collab, via Invoke-AsLoggedInUser (cmdlet NinjaOne).
# En session non-SYSTEM, Invoke-AsLoggedInUser n'existe pas — on tombe en catch.
# Les jetons __XXX__ sont remplacés avant encodage Base64/UTF16 (les symboles
# unicode sont donc préservés).
function Show-SnetorDialog {
    param(
        [string]$Title,
        [string]$IconChar,                  # ex : '0x26A0' (avertissement), '0x2713' (coche)
        [int]$IconR, [int]$IconG, [int]$IconB,
        [string]$BodyBlock,                 # lignes PowerShell : $body.AppendText(...) / $body.SelectionFont
        [string]$ButtonText = "J'ai compris",
        [int]$TimeoutSec    = 18
    )
    if (-not $script:TargetUserFull) {
        Write-Warn "Aucun utilisateur interactif - notification ignoree"
        return
    }

    $template = @'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text            = "Deploiement Claude AI - Snetor DSI"
$form.Size            = New-Object System.Drawing.Size(660, 495)
$form.StartPosition   = 'CenterScreen'
$form.BackColor       = [System.Drawing.Color]::FromArgb(15, 30, 60)
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox     = $false
$form.MinimizeBox     = $false
$form.TopMost         = $true

# Bande verte en haut
$header           = New-Object System.Windows.Forms.Panel
$header.Size      = New-Object System.Drawing.Size(660, 8)
$header.Location  = New-Object System.Drawing.Point(0, 0)
$header.BackColor = [System.Drawing.Color]::FromArgb(0, 200, 120)
$form.Controls.Add($header)

# Icone
$icon           = New-Object System.Windows.Forms.Label
$icon.Text      = [char]__ICONCHAR__
$icon.Font      = New-Object System.Drawing.Font("Segoe UI", 46, [System.Drawing.FontStyle]::Regular)
$icon.ForeColor = [System.Drawing.Color]::FromArgb(__ICONR__, __ICONG__, __ICONB__)
$icon.Size      = New-Object System.Drawing.Size(88, 88)
$icon.Location  = New-Object System.Drawing.Point(33, 33)
$form.Controls.Add($icon)

# Titre
$title           = New-Object System.Windows.Forms.Label
$title.Text      = "__TITLE__"
$title.Font      = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Bold)
$title.ForeColor = [System.Drawing.Color]::White
$title.Size      = New-Object System.Drawing.Size(506, 44)
$title.Location  = New-Object System.Drawing.Point(127, 39)
$form.Controls.Add($title)

# Sous-titre
$sub           = New-Object System.Windows.Forms.Label
$sub.Text      = "Service DSI Snetor"
$sub.Font      = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Regular)
$sub.ForeColor = [System.Drawing.Color]::FromArgb(0, 200, 120)
$sub.Size      = New-Object System.Drawing.Size(506, 26)
$sub.Location  = New-Object System.Drawing.Point(127, 84)
$form.Controls.Add($sub)

# Separateur
$sep           = New-Object System.Windows.Forms.Panel
$sep.Size      = New-Object System.Drawing.Size(594, 1)
$sep.Location  = New-Object System.Drawing.Point(33, 132)
$sep.BackColor = [System.Drawing.Color]::FromArgb(50, 70, 100)
$form.Controls.Add($sep)

# Corps du message (RichTextBox pour le gras partiel)
$body             = New-Object System.Windows.Forms.RichTextBox
$body.BackColor   = [System.Drawing.Color]::FromArgb(15, 30, 60)
$body.ForeColor   = [System.Drawing.Color]::FromArgb(200, 215, 235)
$body.BorderStyle = 'None'
$body.ReadOnly    = $true
$body.ScrollBars  = 'None'
$body.Size        = New-Object System.Drawing.Size(594, 220)
$body.Location    = New-Object System.Drawing.Point(33, 149)

$fontNormal = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Regular)
$fontBold   = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)

__BODYBLOCK__
$form.Controls.Add($body)

# Bouton
$btn                           = New-Object System.Windows.Forms.Button
$btn.Text                      = "__BUTTON__"
$btn.Font                      = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$btn.ForeColor                 = [System.Drawing.Color]::White
$btn.BackColor                 = [System.Drawing.Color]::FromArgb(0, 160, 95)
$btn.FlatStyle                 = 'Flat'
$btn.FlatAppearance.BorderSize = 0
$btn.Size                      = New-Object System.Drawing.Size(176, 46)
$btn.Location                  = New-Object System.Drawing.Point(231, 405)
$btn.Add_Click({ $form.Close() })
$form.Controls.Add($btn)
$form.AcceptButton = $btn

$form.ShowDialog() | Out-Null
'@

    $dlg = $template.
        Replace('__ICONCHAR__', $IconChar).
        Replace('__ICONR__', "$IconR").Replace('__ICONG__', "$IconG").Replace('__ICONB__', "$IconB").
        Replace('__TITLE__',  $Title).
        Replace('__BUTTON__', $ButtonText).
        Replace('__BODYBLOCK__', $BodyBlock)

    try {
        # Invoke-AsLoggedInUser est fourni par l'agent NinjaOne (contexte SYSTEM).
        # En session utilisateur classique, la commande n'existe pas → catch silencieux.
        Invoke-AsLoggedInUser -Command $dlg -TimeoutSec $TimeoutSec | Out-Null
        Write-Ok "Notification affichee a $script:TargetUserFull : $Title"
    } catch {
        Write-Warn "Impossible d'afficher la notification GUI : $_"
    }
}

# Notification 1 — debut de deploiement
function Show-UserWarning {
    $bodyBlock = @'
$body.SelectionFont = $fontNormal
$body.AppendText("L'installation comprend :`n")
$body.AppendText("   -  Claude Desktop`n")
$body.AppendText("   -  Claude Code (CLI)`n")
$body.AppendText("   -  Configuration Snetor`n")
$body.AppendText("   -  Connecteur Microsoft 365`n`n")
$body.AppendText("Duree estimee : 5 a 10 minutes.`n")
$body.SelectionFont = $fontBold
$body.AppendText("Merci de ne pas eteindre votre ordinateur.`n")
$body.AppendText("Ne pas tenter d'ouvrir l'application pendant ce delai.")
'@
    Show-SnetorDialog -Title 'Installation en cours sur votre poste' `
        -IconChar '0x26A0' -IconR 0 -IconG 200 -IconB 120 `
        -BodyBlock $bodyBlock -ButtonText "J'ai compris" -TimeoutSec 18
}

# Notification 2 — fin de deploiement (verte si OK, orange si avertissements)
function Show-UserComplete {
    param([bool]$HadFailure)

    if ($HadFailure) {
        $title    = 'Installation terminee avec avertissements'
        $iconChar = '0x26A0'; $r = 255; $g = 170; $b = 40
    } else {
        $title    = 'Installation terminee avec succes'
        $iconChar = '0x2713'; $r = 0; $g = 200; $b = 120
    }

    $bodyBlock = @'
$body.SelectionFont = $fontNormal
$body.AppendText("Claude AI est installe sur votre poste.`n`n")
$body.SelectionFont = $fontBold
$body.AppendText("Pour commencer :`n")
$body.SelectionFont = $fontNormal
$body.AppendText("   1. Ouvrir Claude Desktop et se connecter`n")
$body.AppendText("      avec votre compte @snetor.com`n")
$body.AppendText("   2. Autoriser le connecteur Microsoft 365`n")
$body.AppendText("      (Parametres -> Extensions)`n")
$body.AppendText("   3. Dans un terminal : taper la commande  claude`n`n")
$body.SelectionFont = $fontBold
$body.AppendText("En cas de souci : contacter le service DSI.")
'@
    Show-SnetorDialog -Title $title `
        -IconChar $iconChar -IconR $r -IconG $g -IconB $b `
        -BodyBlock $bodyBlock -ButtonText 'Fermer' -TimeoutSec 30
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

# ─── Phase 2 : Git for Windows ────────────────────────────────────────────────
function Invoke-Phase2-Git {
    param([string]$Tmp)
    Write-Step "Phase 2 — Git for Windows"

    # Déjà présent et fonctionnel ?
    try {
        $v = & git --version 2>$null
        if ($v -match 'git version') {
            Write-Ok "$v déjà installé — skip"
            $script:phaseResults['Git'] = "✅ déjà présent ($($v -replace 'git version ',''))"
            return
        }
    } catch { }

    Write-Info "Résolution de la dernière release via api.github.com/git-for-windows ..."
    $asset   = Get-GitHubLatestAsset -Repo 'git-for-windows/git' -NamePattern '^Git-.*-64-bit\.exe$'
    $exePath = Join-Path $Tmp 'git-setup.exe'

    Invoke-Download $asset.Url $exePath

    Write-Info "Installation silencieuse de $($asset.Name) ..."
    $gitArgs = '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES /NOCANCEL /SP- /CLOSEAPPLICATIONS /NORESTARTAPPLICATIONS'
    $proc = Start-Process $exePath -ArgumentList $gitArgs -Wait -PassThru
    if ($proc.ExitCode -ne 0) { throw "L'installeur Git a retourné le code $($proc.ExitCode)" }

    Refresh-PATH

    $v = & git --version 2>$null
    Write-Ok "$v installé"
    $script:phaseResults['Git'] = "✅ $($v -replace 'git version ','')"
}

# ─── Phase 3 : Claude Desktop ─────────────────────────────────────────────────
function Invoke-Phase3-Claude {
    param([string]$Tmp)
    Write-Step "Phase 3 — Claude Desktop"

    # Déjà provisionné machine-wide ? (contexte admin : on interroge le provisioning,
    # pas Get-AppxPackage qui ne verrait que les packages de l'admin élevé)
    $existing = Get-AppxProvisionedPackage -Online |
                Where-Object { $_.DisplayName -like '*Claude*' } | Select-Object -First 1
    if ($existing) {
        Write-Ok "Claude Desktop déjà provisionné (v$($existing.Version)) — skip"
        $script:phaseResults['Claude Desktop'] = "✅ déjà présent v$($existing.Version)"
        return
    }

    # MSIX officiel signé Anthropic — l'endpoint redirige vers la dernière version (parc Snetor = x64).
    $msixUrl  = 'https://claude.ai/api/desktop/win32/x64/msix/latest/redirect'
    $msixPath = Join-Path $Tmp 'Claude.msix'

    Invoke-Download $msixUrl $msixPath

    # Provisioning machine-wide : Claude est enregistré pour TOUS les utilisateurs du poste
    # (modèle DSI). Le collab l'obtient à sa prochaine ouverture de session Windows.
    Write-Info "Provisioning machine-wide du MSIX (Add-AppxProvisionedPackage) ..."
    Add-AppxProvisionedPackage -Online -PackagePath $msixPath -SkipLicense -Regions 'all' | Out-Null

    $installed = Get-AppxProvisionedPackage -Online |
                 Where-Object { $_.DisplayName -like '*Claude*' } | Select-Object -First 1
    if ($installed) {
        Write-Ok "Claude Desktop v$($installed.Version) provisionné (dispo à la prochaine session du collab)"
        $script:phaseResults['Claude Desktop'] = "✅ v$($installed.Version) (provisionné)"
    } else {
        Write-Warn "Provisioning non vérifiable — vérifier manuellement"
        Write-Info "URL : https://claude.com/download"
        $script:phaseResults['Claude Desktop'] = '⚠️ vérification manuelle'
    }
}

# ─── Phase 4 : Claude Code (Cowork) ──────────────────────────────────────────
function Invoke-Phase4-CoWork {
    param([string]$Tmp)
    Write-Step "Phase 4 — Claude Code (Cowork)"

    Refresh-PATH

    $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
    if (-not $npmCmd) { throw "npm introuvable — vérifier l'installation Node.js (Phase 1)" }

    # Pointer le prefix npm vers le profil du collab (pas celui de l'admin)
    $npmPrefix = "$TargetProfile\AppData\Roaming\npm"
    New-Item -ItemType Directory -Path $npmPrefix -Force | Out-Null
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

    # Ajouter le prefix npm au PATH du collab via son hive registre
    # (SetEnvironmentVariable('User') ciblerait l'admin élevé, pas le collab)
    try {
        $sid     = (New-Object System.Security.Principal.NTAccount($TargetUser)).Translate(
                       [System.Security.Principal.SecurityIdentifier]).Value
        $regPath = "Registry::HKEY_USERS\$sid\Environment"
        $currentUserPath = (Get-ItemProperty -Path $regPath -Name PATH -ErrorAction SilentlyContinue).PATH
        if ($currentUserPath -notlike "*$npmPrefix*") {
            $newPath = if ($currentUserPath) { "$currentUserPath;$npmPrefix" } else { $npmPrefix }
            Set-ItemProperty -Path $regPath -Name PATH -Value $newPath
            Write-Info "PATH du collab mis à jour : +$npmPrefix"
        }
    } catch {
        Write-Warn "Impossible de mettre à jour le PATH du collab : $_"
        Write-Info "Action manuelle : ajouter $npmPrefix au PATH utilisateur"
    }

    Write-Ok "Claude Code installé"
    $script:phaseResults['Claude Code'] = '✅'
}

# ─── Phase 5 : Config Snetor ──────────────────────────────────────────────────
function Invoke-Phase5-Snetor {
    param([string]$Tmp)
    Write-Step "Phase 5 — Configuration Snetor"

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

    # 2. Output styles (styles de réponse sélectionnables via /config)
    $stylesSrc = Join-Path $repoDir 'output-styles'
    if (Test-Path $stylesSrc) {
        $stylesDst = "$claudeDir\output-styles"
        New-Item -ItemType Directory -Path $stylesDst -Force | Out-Null
        Copy-Item "$stylesSrc\*.md" $stylesDst -Force
        Write-Ok "Output styles copiés ($stylesDst)"
    } else {
        Write-Warn "output-styles introuvable dans le repo — skip"
    }

    # 3. settings.json (fusion si existant)
    $settingsPath    = "$claudeDir\settings.json"
    $snetorPlugins   = [ordered]@{
        'superpowers@claude-plugins-official'     = $true
        'context7@claude-plugins-official'        = $true
        'snetor-skills@snetor-ai-guidelines'     = $true
    }
    $snetorDefaults  = [ordered]@{
        theme        = 'dark'
        effortLevel  = 'medium'
        outputStyle  = 'ELI5'
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

    Set-JsonFile -Object $cfg -Path $settingsPath
    Write-Ok "settings.json configuré (plugins Snetor activés)"

    # 4. Status line
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

# ─── Phase 6 : M365 MCP Config ────────────────────────────────────────────────
function Invoke-Phase6-M365 {
    param([string]$Tmp)
    Write-Step "Phase 6 — Connecteur Microsoft 365 MCP"

    # Le MSIX lit sa config dans %LOCALAPPDATA%\Packages\<PFN>\LocalCache\Roaming\Claude.
    # On résout <PackageFamilyName> par ordre de fiabilité décroissante :
    $pfn = $null

    # 1) Package enregistré pour un utilisateur du poste (-AllUsers visible en admin)
    $claudePkg = Get-AppxPackage -AllUsers -Name '*Claude*' -ErrorAction SilentlyContinue |
                 Select-Object -First 1
    if ($claudePkg) { $pfn = $claudePkg.PackageFamilyName }

    # 2) Pas encore enregistré (collab pas reconnecté) : dériver le PFN du package
    #    provisionné — PackageName 'AnthropicClaude_<ver>_x64__<hash>' → '<Name>_<hash>'
    if (-not $pfn) {
        $prov = Get-AppxProvisionedPackage -Online |
                Where-Object { $_.DisplayName -like '*Claude*' } | Select-Object -First 1
        if ($prov -and $prov.PackageName -match '^([^_]+)_[^_]+_[^_]+__(.+)$') {
            $pfn = "$($Matches[1])_$($Matches[2])"
        }
    }

    if ($pfn) {
        $configDir = "$TargetProfile\AppData\Local\Packages\$pfn\LocalCache\Roaming\Claude"
    } else {
        # 3) Dernier recours — le chemin réel se résoudra à la 1re ouverture de Claude Desktop
        $configDir = "$TargetProfile\AppData\Roaming\Claude"
        Write-Warn "Package Claude non résolu — chemin de secours : $configDir"
        Write-Info "Si Claude ne lit pas la config M365, ouvrir Claude Desktop une fois puis relancer cette phase."
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

    Set-JsonFile -Object $config -Path $configPath
    Write-Info "Config écrite dans : $configPath"
    $script:phaseResults['M365 MCP'] = '✅ pré-configuré'
}

# ─── Phase 7 : Récapitulatif ──────────────────────────────────────────────────
function Invoke-Phase7-Summary {
    param([System.Collections.Specialized.OrderedDictionary]$Results)

    Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host   "║        Déploiement terminé — Récapitulatif               ║" -ForegroundColor Cyan
    Write-Host   "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    foreach ($phase in $Results.Keys) {
        $icon = $Results[$phase]
        Write-Host "  $icon  $phase"
    }

    Write-Host "`n📋 Actions manuelles restantes (à faire par le collab) :" -ForegroundColor Yellow
    Write-Host "  0. Claude Desktop a été provisionné — il apparaît à la prochaine ouverture de session Windows"
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

# Notifier le collab que l'installation démarre (non bloquant — timeout 18 s)
Show-UserWarning

try { Invoke-Phase1-NodeJS  $tmp } catch { Write-Fail "Phase 1 échouée : $_"; $phaseResults['Node.js']        = '❌' }
try { Invoke-Phase2-Git     $tmp } catch { Write-Fail "Phase 2 échouée : $_"; $phaseResults['Git']            = '❌' }
try { Invoke-Phase3-Claude  $tmp } catch { Write-Fail "Phase 3 échouée : $_"; $phaseResults['Claude Desktop'] = '❌' }
try { Invoke-Phase4-CoWork  $tmp } catch { Write-Fail "Phase 4 échouée : $_"; $phaseResults['Claude Code']    = '❌' }
try { Invoke-Phase5-Snetor  $tmp } catch { Write-Fail "Phase 5 échouée : $_"; $phaseResults['Config Snetor'] = '❌' }
try { Invoke-Phase6-M365    $tmp } catch { Write-Fail "Phase 6 échouée : $_"; $phaseResults['M365 MCP']       = '❌' }

Invoke-Phase7-Summary $phaseResults

# Notifier le collab que l'installation est terminée
$hadFailure = $phaseResults.Values -contains '❌'
Show-UserComplete -HadFailure $hadFailure

Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue

# Maintenir la fenêtre ouverte si lancée en double-clic (hors NinjaOne)
if ($Host.Name -eq 'ConsoleHost' -and -not $psISE -and -not $isSystem) {
    Write-Host "Appuyez sur une touche pour fermer ..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
}
