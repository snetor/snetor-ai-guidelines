#Requires -Version 5.1

<#
.SYNOPSIS
    Deploiement Claude pour un collab Snetor : Claude Desktop + Git, ou complet
    (Desktop + Code + M365 + Snetor), au choix du collab.
.DESCRIPTION
    Compatible avec deux modes d'execution :
      - Session Windows du collab (UAC classique, une seule boite d'elevation)
      - Deploiement NinjaOne (script lance en SYSTEM, detection auto du collab connecte)

    Dans les deux cas, l'installation s'ecrit dans le profil du collab, et rien ne
    s'installe sans son accord : une boite de consentement s'affiche d'abord dans sa
    session, puis une barre d'avancement qui reste affichee jusqu'a la fin, et un bilan.

    C'est le collab qui choisit, dans cette boite, ce qui s'installe :
      - "Claude Desktop + Git" : les phases Git et Claude Desktop seulement ;
      - "Tout installer"       : les six phases (Node.js, Git, Claude Desktop,
                                 Claude Code, configuration Snetor, connecteur M365).
    Relancer le script plus tard permet de passer au complet : les phases deja faites
    sont detectees et sautees.

    Fichier volontairement 100 % ASCII. Colle dans NinjaOne, un script perd son BOM,
    et powershell.exe 5.1 lit un fichier sans BOM en ANSI : un tiret cadratin dans
    une chaine y devient un guillemet fermant, et le script entier refuse de demarrer.
    Les accents des fenetres passent par des entites HTML (voir ConvertFrom-UiText).
.PARAMETER TargetUser
    Nom d'utilisateur du collab. Auto-detecte depuis la session interactive (NinjaOne)
    ou depuis la session courante.
.PARAMETER TargetProfile
    Chemin vers le profil Windows du collab. Auto-detecte si absent.
.PARAMETER TargetEmail
    Email du collab, pour l'identite Git (git config --global user.email). Auto-detecte
    (UPN de session ou attribut AD 'mail') si absent.
.EXAMPLE
    .\deploy-claude.ps1
.NOTES
    Codes de sortie, lus par NinjaOne :
      0  deploiement termine sans echec
      1  au moins une phase en echec, ou aucun collab en session
      2  le collab a reporte l'installation : rien n'est installe
      3  pas de reponse du collab dans le delai : rien n'est installe
#>

param(
    [string]$TargetUser    = '',
    [string]$TargetProfile = '',
    [string]$TargetEmail   = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# TLS 1.2 obligatoire : Windows PowerShell 5.1 negocie TLS 1.0/1.1 par defaut, ce que
# nodejs.org / api.github.com / claude.ai refusent -> tous les telechargements echoueraient.
[Net.ServicePointManager]::SecurityProtocol = `
    [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

# --- Helpers console ---------------------------------------------------------
function Write-Step { param($msg) Write-Host "`n>>  $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "   [OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "   [!]  $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "   [ECHEC] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "      $msg" -ForegroundColor Gray }

# --- Detection du collab --------------------------------------------------------
# Trois contextes d'execution :
#   - SYSTEM (NinjaOne) : aucun lien avec le collab, il faut le trouver ;
#   - session du collab, avant elevation : le collab est l'utilisateur courant ;
#   - relance elevee sous le compte admin DSI : $TargetUser et $TargetProfile arrivent
#     en parametres, mais l'utilisateur courant est l'admin, pas le collab.
# Le proprietaire du processus explorer.exe designe le collab dans les trois cas.
# `query user`, utilise auparavant, ecrit "Actif" et non "Active" sur un Windows
# francais : cette detection ne trouvait personne sur le parc Snetor.
$isSystem = [Security.Principal.WindowsIdentity]::GetCurrent().IsSystem

function Get-InteractiveUser {
    param([string]$Preferred)
    $owners = @()
    try {
        $owners = @(Get-CimInstance Win32_Process -Filter "Name = 'explorer.exe'" -ErrorAction Stop | ForEach-Object {
            $o = Invoke-CimMethod -InputObject $_ -MethodName GetOwner -ErrorAction SilentlyContinue
            if ($o -and $o.ReturnValue -eq 0 -and $o.User) { "$($o.Domain)\$($o.User)" }
        } | Select-Object -Unique)
    } catch { }
    if ($Preferred) {
        $match = @($owners | Where-Object { ($_ -replace '^.*\\', '') -eq $Preferred })
        if ($match.Count -gt 0) { return $match[0] }
    }
    if ($owners.Count -gt 0) { return $owners[0] }
    # Repli : l'utilisateur de la session console
    try {
        $cs = Get-CimInstance Win32_ComputerSystem -ErrorAction Stop
        if ($cs.UserName) { return $cs.UserName }
    } catch { }
    return $null
}

# 'DOMAINE\user' du collab : c'est sous ce compte que tournent les fenetres
$script:TargetUserFull = Get-InteractiveUser -Preferred $TargetUser

if ($isSystem) {
    Write-Host "  Contexte SYSTEM detecte (NinjaOne)" -ForegroundColor DarkGray
    if (-not $script:TargetUserFull) {
        # Sans collab detecte, $TargetUser/$TargetProfile retomberaient plus bas sur
        # $env:USERNAME/$env:USERPROFILE, qui valent ici 'SYSTEM' et le profil systeme
        # (C:\Windows\system32\config\systemprofile). Une policy NinjaOne qui cible un
        # poste sans collab connecte installerait alors tout dans ce profil : on arrete
        # plutot que de deployer au mauvais endroit en silence.
        Write-Fail "Aucune session interactive detectee sur ce poste (contexte SYSTEM) : deploiement annule."
        Write-Info "Ce script cible un poste avec un collab connecte. Relancer une fois le collab en session."
        exit 1
    }
    Write-Host "  Utilisateur interactif : $script:TargetUserFull" -ForegroundColor DarkGray
    if (-not $TargetUser) { $TargetUser = $script:TargetUserFull -replace '^.*\\', '' }

    # Profil resolu par le SID dans ProfileList : le nom du dossier peut differer du
    # nom de session, et $env:USERPROFILE designe ici le profil systeme.
    if (-not $TargetProfile) {
        try {
            $userSid = (New-Object System.Security.Principal.NTAccount($script:TargetUserFull)).Translate(
                           [System.Security.Principal.SecurityIdentifier]).Value
            $key = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\$userSid"
            $TargetProfile = (Get-ItemProperty $key -Name ProfileImagePath -ErrorAction Stop).ProfileImagePath
        } catch {
            Write-Fail "Profil Windows de $script:TargetUserFull introuvable : deploiement annule ($_)"
            exit 1
        }
    }
} elseif (-not $script:TargetUserFull) {
    $script:TargetUserFull = if ($TargetUser) { $TargetUser } else { "$env:USERDOMAIN\$env:USERNAME" }
}

# --- Resolution de l'email du collab (identite Git) --------------------------
# Objectif : eviter au collab de taper `git config --global user.email ...` a la main
# sur chaque nouveau poste. Deux contextes, deux sources - jamais devinees si evitable :
#   - Session interactive (avant elevation) : whoami /upn renvoie l'UPN de la session
#     en cours, qui correspond a l'email chez Snetor.
#   - Contexte SYSTEM (NinjaOne) : pas de session a interroger, on lit l'attribut AD
#     'mail' du samAccountName deja detecte ci-dessus.
# En dernier recours seulement (plus bas, une fois $TargetUser fige), on deduit
# l'email par convention <samAccountName>@snetor.com, avec un avertissement explicite.
if (-not $TargetEmail) {
    if ($isSystem) {
        if ($TargetUser) {
            try {
                $searcher = [adsisearcher]"(&(objectCategory=User)(samAccountName=$TargetUser))"
                $searcher.PropertiesToLoad.Add('mail') | Out-Null
                $adUser = $searcher.FindOne()
                if ($adUser -and $adUser.Properties['mail'] -and $adUser.Properties['mail'].Count -gt 0) {
                    $TargetEmail = [string]$adUser.Properties['mail'][0]
                }
            } catch {
                Write-Warn "Resolution AD de l'email a echoue : $_"
            }
        }
    } else {
        try {
            $upn = & whoami /upn 2>$null | Select-Object -First 1
            if ($upn) { $upn = $upn.ToString().Trim() }
            if ($upn -match '^[^@\s]+@[^@\s]+\.[^@\s]+$') { $TargetEmail = $upn }
        } catch { }
    }
}

# Valeurs par defaut si non renseignees et non-SYSTEM
if (-not $TargetUser)    { $TargetUser    = $env:USERNAME }
if (-not $TargetProfile) { $TargetProfile = $env:USERPROFILE }

if (-not $TargetEmail) {
    # Dernier recours : convention Snetor <samAccountName>@snetor.com - a verifier,
    # la resolution AD/UPN ci-dessus est toujours preferee quand elle aboutit.
    $TargetEmail = "$TargetUser@snetor.com"
    Write-Warn "Email deduit par convention (a verifier aupres du collab) : $TargetEmail"
}

# --- Phase 0 : Auto-elevation (ignoree en contexte SYSTEM NinjaOne) ----------
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    Write-Host "Elevation admin requise - une seule boite UAC va s'afficher." -ForegroundColor Yellow
    $escapedScript  = $PSCommandPath -replace '"', '\"'
    $escapedUser    = $TargetUser    -replace '"', '\"'
    $escapedProfile = $TargetProfile -replace '"', '\"'
    $escapedEmail   = $TargetEmail   -replace '"', '\"'
    $psArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$escapedScript`" -TargetUser `"$escapedUser`" -TargetProfile `"$escapedProfile`" -TargetEmail `"$escapedEmail`""
    # 'powershell.exe' = Windows PowerShell 5.1 (jamais pwsh 7, absent du parc Snetor)
    Start-Process powershell.exe -Verb RunAs -ArgumentList $psArgs
    exit 0
}

Write-Host ""
Write-Host "  Snetor -- Deploiement Claude DSI" -ForegroundColor Cyan
Write-Host "  Collab  : $TargetUser" -ForegroundColor Cyan
Write-Host "  Profil  : $TargetProfile" -ForegroundColor Cyan
Write-Host "  Email   : $TargetEmail" -ForegroundColor Cyan
Write-Host ""

# Pointer les variables d'env vers le profil du collab (pas celui de l'admin eleve).
# HOME est inclus : Git for Windows resout l'emplacement de son config --global via
# HOME en priorite, et retombe sur HOMEDRIVE+HOMEPATH (ceux de l'admin eleve, pas
# du collab) avant d'essayer USERPROFILE. Sans ce override, `git config --global`
# ecrirait dans le profil de l'admin DSI au lieu de celui du collab.
$env:USERPROFILE = $TargetProfile
$env:APPDATA     = "$TargetProfile\AppData\Roaming"
$env:HOME        = $TargetProfile

# Dossier d'echange avec les fenetres du collab (scripts, reponse au consentement). Dans
# son profil : il y ecrit sans qu'on ouvre a tout le poste un dossier dont les scripts
# seraient executes.
$script:UiDir = Join-Path $TargetProfile 'AppData\Local\Temp\SnetorClaude'

# --- Utilitaires --------------------------------------------------------------
function Get-TempDir {
    $tmp = Join-Path $env:TEMP "snetor-claude-$(Get-Date -Format 'yyyyMMddHHmmss')"
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    return $tmp
}

function Invoke-Download {
    param([string]$Url, [string]$Dest)
    Write-Info "Telechargement : $Url"
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing
    $ProgressPreference = 'Continue'
}

function Refresh-PATH {
    $m = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
    $u = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
    $env:PATH = "$m;$u"
}

# Ecrit du JSON en UTF-8 SANS BOM. En PS 5.1, 'Set-Content -Encoding UTF8' ajoute un BOM
# qui casse certains parseurs (Claude Desktop, npm) -> on passe par .NET sans BOM.
function Set-JsonFile {
    param([object]$Object, [string]$Path)
    $json = $Object | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($Path, $json, (New-Object System.Text.UTF8Encoding($false)))
}

# Resout le dernier asset d'une release GitHub. L'API exige un User-Agent (sinon 403).
function Get-GitHubLatestAsset {
    param([string]$Repo, [string]$NamePattern)
    $api = "https://api.github.com/repos/$Repo/releases/latest"
    $rel = Invoke-RestMethod -Uri $api -UseBasicParsing -Headers @{ 'User-Agent' = 'snetor-deploy-claude' }
    $asset = $rel.assets | Where-Object { $_.name -match $NamePattern } | Select-Object -First 1
    if (-not $asset) { throw "Aucun asset '$NamePattern' dans la derniere release de $Repo" }
    return [PSCustomObject]@{ Name = $asset.name; Url = $asset.browser_download_url }
}

# Configure l'identite Git du collab (email auto-detecte plus haut). Idempotent :
# ne touche jamais une valeur deja definie par le collab lui-meme.
function Set-CollabGitIdentity {
    if (-not $TargetEmail) {
        Write-Warn "Email du collab non resolu - identite Git a configurer manuellement (git config --global user.email ...)"
        return
    }
    # Sans `2>$null` : sous PowerShell 5.1 et ErrorActionPreference Stop, cette redirection
    # rend terminante la moindre ligne de stderr, exactement comme `2>&1` (verifie le
    # 2026-09-28). Une cle absente fait sortir git en code 1 sans rien ecrire : rien a taire.
    $existingEmail = & git config --global user.email
    if ($existingEmail) {
        Write-Info "Identite Git deja configuree ($existingEmail) - inchangee"
        return
    }
    & git config --global user.email $TargetEmail
    Write-Ok "Identite Git configuree : $TargetEmail"
}

# --- Fenetres dans la session du collab -----------------------------------------
# Ce script tourne en SYSTEM (NinjaOne) ou sous le compte admin DSI (relance UAC) : une
# fenetre ouverte par ce processus n'apparait pas sur le bureau du collab. On passe donc
# par une tache planifiee ephemere, executee SOUS LE COMPTE DU COLLAB dans sa session
# ouverte, qui lance powershell.exe masque via wscript (sans wscript, une console noire
# s'ouvrirait a l'ecran). Meme mecanique que le deploiement SAP GUI 8.00, eprouvee sur
# le parc.
#
# Elle remplace Invoke-AsLoggedInUser, qui n'existe pas dans NinjaOne (le nom rappelle
# Invoke-AsCurrentUser du module communautaire RunAsUser, absent des postes) : chaque
# appel tombait dans le catch, et aucune fenetre ne s'est jamais affichee.

# Texte des fenetres : ce fichier reste 100 % ASCII, les accents passent par des entites
# HTML (&eacute; e accent aigu, &egrave; e grave, &agrave; a grave, &ecirc; e circonflexe,
# &icirc; i circonflexe, &ccedil; c cedille, &Eacute; E accent aigu, &bull; puce).
function ConvertFrom-UiText {
    param([string]$Text)
    [System.Net.WebUtility]::HtmlDecode($Text)
}

# Meme texte pour la console et le journal NinjaOne : sans accents, qui y arriveraient
# mal encodes.
function ConvertTo-LogText {
    param([string]$Text)
    $decoded = (ConvertFrom-UiText $Text).Normalize([System.Text.NormalizationForm]::FormD)
    -join ($decoded.ToCharArray() | Where-Object {
        [System.Globalization.CharUnicodeInfo]::GetUnicodeCategory($_) -ne 'NonSpacingMark'
    })
}

# Chaine -> litteral PowerShell entre apostrophes, pour l'injecter dans un script genere
# sans qu'elle puisse en sortir. PowerShell ferme aussi une chaine sur une apostrophe
# typographique : on les double toutes.
function ConvertTo-PsLiteral {
    param([string]$Text)
    $quotes = "['" + [char]0x2018 + [char]0x2019 + [char]0x201A + [char]0x201B + "]"
    "'" + ($Text -replace $quotes, "''") + "'"
}

# Supprime une tache par l'API COM du planificateur. Get-ScheduledTask et
# Unregister-ScheduledTask enumerent toutes les taches du poste avant d'agir : 4,5 a 4,8 s
# par appel, mesure le 2026-09-28. Avec eux, chaque notification de 6 s en coutait 35.
function Remove-UiTask {
    param([string]$TaskName)
    try {
        $service = New-Object -ComObject Schedule.Service
        $service.Connect()
        $service.GetFolder('\').DeleteTask($TaskName, 0)
    } catch { }
}

function Invoke-InUserSession {
    param(
        [string]$ScriptContent,
        [string]$Name,
        [int]$TimeoutSec = 30,
        [switch]$NoWait
    )
    if (-not $script:UiDir) {
        Write-Warn "Fenetre '$Name' ignoree : dossier d'echange non initialise"
        return $false
    }

    # Fichiers uniques par appel : en -NoWait, le powershell lance n'a pas forcement lu son
    # script quand un appel suivant du meme nom viendrait l'ecraser (vu au banc le 2026-09-28).
    $id       = [guid]::NewGuid().ToString('N').Substring(0, 8)
    $ps1      = Join-Path $script:UiDir "$Name-$id.ps1"
    $vbs      = Join-Path $script:UiDir "$Name-$id.vbs"
    $taskName = "SnetorClaude-$Name"
    $shown    = $false
    try {
        New-Item -ItemType Directory -Path $script:UiDir -Force | Out-Null

        # UTF-8 AVEC BOM : c'est ainsi que powershell.exe 5.1 lit un script sans le prendre
        # pour de l'ANSI. Le script s'efface des son lancement (il est deja en memoire) : en
        # -NoWait, personne n'attend sa fin pour faire le menage.
        $selfDelete = 'Remove-Item -LiteralPath $PSCommandPath -Force -ErrorAction SilentlyContinue'
        [System.IO.File]::WriteAllText($ps1, "$selfDelete`r`n$ScriptContent", (New-Object System.Text.UTF8Encoding($true)))

        # wscript lance powershell masque (style 0). En attente, il rend le code de sortie de
        # powershell, que la tache remonte dans LastTaskResult. Fichier en UTF-16 : wscript
        # le lit avec son BOM, un profil au nom accentue ne casse donc pas le chemin.
        $wait = if ($NoWait) { 'False' } else { 'True' }
        $cmd  = 'powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File ""' + $ps1 + '""'
        [System.IO.File]::WriteAllText($vbs, ('WScript.Quit CreateObject("WScript.Shell").Run("' + $cmd + '", 0, ' + $wait + ')'), [System.Text.Encoding]::Unicode)

        $action    = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "//B //Nologo `"$vbs`""
        $principal = New-ScheduledTaskPrincipal -UserId $script:TargetUserFull -LogonType Interactive -RunLevel Limited
        # Sans ces deux reglages, Task Scheduler ne lance pas la tache sur un portable qui
        # tourne sur batterie : la fenetre ne s'afficherait pas, sans la moindre erreur.
        $settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
                         -ExecutionTimeLimit (New-TimeSpan -Minutes ([Math]::Ceiling($TimeoutSec / 60) + 2))
        Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Settings $settings -Force | Out-Null
        Start-ScheduledTask -TaskName $taskName

        # Suivi par LastTaskResult seul (0,08 s par lecture) : 267011 = pas encore lancee,
        # 267009 = en cours, sinon le code de sortie de powershell. Sans le cas 267011, on
        # croirait la fenetre deja fermee juste apres Start-ScheduledTask, et on effacerait
        # son script avant que powershell ne l'ait lu.
        $deadline = (Get-Date).AddSeconds($TimeoutSec)
        do {
            Start-Sleep -Milliseconds 400
            $info    = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
            $result  = if ($info) { $info.LastTaskResult } else { $null }
            $pending = ($null -eq $result) -or ($result -eq 267009) -or ($result -eq 267011)
        } while ($pending -and (Get-Date) -lt $deadline)

        if ($pending) {
            Write-Warn "Fenetre '$Name' : jamais lancee ou toujours ouverte apres $TimeoutSec s"
        } elseif ($result -ne 0) {
            Write-Warn "Fenetre '$Name' : le script d'affichage a echoue (code $result)"
        } else {
            $shown = $true
            $verbe = if ($NoWait) { 'ouverte' } else { 'affichee' }
            Write-Ok "Fenetre '$Name' $verbe chez $script:TargetUserFull"
        }
    } catch {
        Write-Warn "Fenetre '$Name' non affichee : $_"
    } finally {
        Remove-UiTask $taskName
        Remove-Item -LiteralPath $vbs -Force -ErrorAction SilentlyContinue
        if (-not $NoWait) { Remove-Item -LiteralPath $ps1 -Force -ErrorAction SilentlyContinue }
    }
    return $shown
}

# Notification en bas a droite, facon Windows 11 : se ferme seule, ou au clic.
function Show-Toast {
    param(
        [string]$Name,
        [ValidateSet('ok', 'warn', 'fail', 'info')][string]$Status = 'info',
        [string]$Title,
        [string]$Message,
        [int]$DurationSec = 6
    )
    # Glyphes de la police Segoe MDL2 Assets : coche, triangle, erreur, info
    $style = @{
        ok   = @{ Color = '0, 200, 120';  Glyph = '0xE73E' }
        warn = @{ Color = '255, 170, 40'; Glyph = '0xE7BA' }
        fail = @{ Color = '235, 87, 87';  Glyph = '0xE783' }
        info = @{ Color = '0, 200, 120';  Glyph = '0xE946' }
    }[$Status]

    $template = @'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$accent = [System.Drawing.Color]::FromArgb(__ACCENT__)

$form = New-Object System.Windows.Forms.Form
$form.FormBorderStyle = 'None'
$form.ShowInTaskbar   = $false
$form.TopMost         = $true
$form.StartPosition   = 'Manual'
$form.ClientSize      = New-Object System.Drawing.Size(380, 96)
$form.BackColor       = [System.Drawing.Color]::FromArgb(15, 30, 60)
$area = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$form.Location = New-Object System.Drawing.Point(($area.Right - 396), ($area.Bottom - 112))

$bar = New-Object System.Windows.Forms.Panel
$bar.BackColor = $accent
$bar.SetBounds(0, 0, 5, 96)

$icon = New-Object System.Windows.Forms.Label
$icon.Text      = [string][char]__GLYPH__
$icon.Font      = New-Object System.Drawing.Font('Segoe MDL2 Assets', 18)
$icon.ForeColor = $accent
$icon.TextAlign = 'MiddleCenter'
$icon.SetBounds(16, 28, 40, 40)

$brand = New-Object System.Windows.Forms.Label
$brand.Text      = 'SNETOR DSI  |  CLAUDE AI'
$brand.Font      = New-Object System.Drawing.Font('Segoe UI', 7.5, [System.Drawing.FontStyle]::Bold)
$brand.ForeColor = [System.Drawing.Color]::FromArgb(0, 200, 120)
$brand.SetBounds(66, 12, 300, 16)

$title = New-Object System.Windows.Forms.Label
$title.Text         = __TITLE__
$title.Font         = New-Object System.Drawing.Font('Segoe UI', 11, [System.Drawing.FontStyle]::Bold)
$title.ForeColor    = [System.Drawing.Color]::White
$title.AutoEllipsis = $true
$title.SetBounds(66, 29, 300, 24)

$msg = New-Object System.Windows.Forms.Label
$msg.Text         = __MESSAGE__
$msg.Font         = New-Object System.Drawing.Font('Segoe UI', 9)
$msg.ForeColor    = [System.Drawing.Color]::FromArgb(200, 215, 235)
$msg.AutoEllipsis = $true
$msg.SetBounds(66, 55, 302, 36)

$form.Controls.AddRange(@($bar, $icon, $brand, $title, $msg))
foreach ($c in @($form, $bar, $icon, $brand, $title, $msg)) { $c.Add_Click({ $form.Close() }) }

# Coins arrondis de Windows 11 ; sans effet, et sans erreur, sous Windows 10
try {
    Add-Type -Namespace SnetorUi -Name Dwm -MemberDefinition '[DllImport("dwmapi.dll")] public static extern int DwmSetWindowAttribute(System.IntPtr hwnd, int attribute, ref int value, int size);'
    $corner = 2
    [void][SnetorUi.Dwm]::DwmSetWindowAttribute($form.Handle, 33, [ref]$corner, 4)
} catch { }

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = __DURATIONMS__
$timer.Add_Tick({ $timer.Stop(); $form.Close() })
$timer.Start()

[void]$form.ShowDialog()
'@

    $ui = $template.
        Replace('__ACCENT__', $style.Color).
        Replace('__GLYPH__', $style.Glyph).
        Replace('__DURATIONMS__', [string]($DurationSec * 1000)).
        Replace('__TITLE__', (ConvertTo-PsLiteral $Title)).
        Replace('__MESSAGE__', (ConvertTo-PsLiteral $Message))
    [void](Invoke-InUserSession -ScriptContent $ui -Name "toast-$Name" -TimeoutSec ($DurationSec + 25))
}

# --- Barre d'avancement ------------------------------------------------------------
# Fenetre sans bordure en bas a droite de l'ecran du collab, affichee du debut a la fin :
# une case par etape, verte, orange ou rouge selon son resultat, et celle en cours pulse. Le
# script ecrit l'etat dans un fichier du dossier d'echange, la fenetre le relit toutes les
# demi-secondes : ouverte en -NoWait, elle ne ralentit aucune etape.
#
# Elle se ferme seule, en effacant ce fichier : a la fin (done=1), des que le processus de ce
# script n'existe plus, ou si le fichier n'a pas bouge depuis 45 minutes. Ce dernier garde-fou
# couvre un script arrete en cours de route dont le PID serait repris par un autre processus :
# Windows recycle vite ses PID.
$script:ProgressFile   = $null
$script:ProgressSteps  = @()
$script:ProgressStates = @()

function Write-ProgressFile {
    param([switch]$Done)
    if (-not $script:ProgressFile) { return }
    $running = [array]::IndexOf($script:ProgressStates, 'run')
    $label   = if ($running -ge 0) { $script:ProgressSteps[$running] } else { '' }
    $flag    = if ($Done) { '1' } else { '0' }
    $text    = "states=$($script:ProgressStates -join ',')`r`nlabel=$label`r`ndone=$flag`r`n"
    # La fenetre lit en partageant l'ecriture, mais un antivirus peut tenir le fichier un
    # instant : on reessaie, et une mise a jour perdue ne fait jamais echouer une etape.
    for ($essai = 1; $essai -le 5; $essai++) {
        try {
            [System.IO.File]::WriteAllText($script:ProgressFile, $text, (New-Object System.Text.UTF8Encoding($false)))
            return
        } catch {
            if ($essai -eq 5) { Write-Warn "Barre d'avancement non mise a jour : $_" }
            else { Start-Sleep -Milliseconds 100 }
        }
    }
}

# Resultat inscrit par une etape ([OK] ..., [!] ..., [ECHEC]) -> couleur de sa case
function ConvertTo-ProgressState {
    param([string]$Result)
    if ($Result -eq '[ECHEC]') { return 'fail' }
    if ($Result.StartsWith('[!]')) { return 'warn' }
    return 'ok'
}

# Etat d'une case : run (en cours), ok, warn ou fail
function Set-ProgressStep {
    param([int]$Index, [string]$State)
    if ($Index -lt $script:ProgressStates.Count) { $script:ProgressStates[$Index] = $State }
    Write-ProgressFile
}

# Derniere mise a jour : la fenetre affiche 100 %, puis se ferme d'elle-meme
function Close-ProgressWindow { Write-ProgressFile -Done }

function Open-ProgressWindow {
    param([string]$Title, [string]$DoneText, [string]$Glyph, [string[]]$Steps)

    $script:ProgressSteps  = @($Steps | ForEach-Object { ConvertFrom-UiText $_ })
    $script:ProgressStates = @($Steps | ForEach-Object { 'pending' })
    $script:ProgressFile   = Join-Path $script:UiDir 'progression.txt'
    try { New-Item -ItemType Directory -Path $script:UiDir -Force | Out-Null } catch { }
    # Ecrit AVANT d'ouvrir la fenetre : elle s'affiche d'emblee avec ses cases.
    Write-ProgressFile

    $template = @'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$statusFile = __STATUSFILE__
$ownerId    = __OWNERID__
$count      = __COUNT__
$stepFormat = __STEPFORMAT__
$doneText   = __DONETEXT__

$navy   = [System.Drawing.Color]::FromArgb(15, 30, 60)
$green  = [System.Drawing.Color]::FromArgb(0, 200, 120)
$deep   = [System.Drawing.Color]::FromArgb(40, 60, 95)
$grey   = [System.Drawing.Color]::FromArgb(140, 160, 190)
$colors = @{
    ok   = $green
    warn = [System.Drawing.Color]::FromArgb(255, 170, 40)
    fail = [System.Drawing.Color]::FromArgb(235, 87, 87)
}

$form = New-Object System.Windows.Forms.Form
$form.FormBorderStyle = 'None'
$form.ShowInTaskbar   = $false
$form.TopMost         = $true
$form.StartPosition   = 'Manual'
$form.ClientSize      = New-Object System.Drawing.Size(400, 132)
$form.BackColor       = $navy
$area = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$form.Location = New-Object System.Drawing.Point(($area.Right - 416), ($area.Bottom - 148))

$accent = New-Object System.Windows.Forms.Panel
$accent.BackColor = $green
$accent.SetBounds(0, 0, 5, 132)

$icon = New-Object System.Windows.Forms.Label
$icon.Text      = [string][char]__GLYPH__
$icon.Font      = New-Object System.Drawing.Font('Segoe MDL2 Assets', 18)
$icon.ForeColor = $green
$icon.TextAlign = 'MiddleCenter'
$icon.SetBounds(16, 30, 40, 40)

$brand = New-Object System.Windows.Forms.Label
$brand.Text      = 'SNETOR DSI  |  CLAUDE AI'
$brand.Font      = New-Object System.Drawing.Font('Segoe UI', 7.5, [System.Drawing.FontStyle]::Bold)
$brand.ForeColor = $green
$brand.SetBounds(66, 12, 318, 16)

$title = New-Object System.Windows.Forms.Label
$title.Text         = __TITLE__
$title.Font         = New-Object System.Drawing.Font('Segoe UI', 11, [System.Drawing.FontStyle]::Bold)
$title.ForeColor    = [System.Drawing.Color]::White
$title.AutoEllipsis = $true
$title.SetBounds(66, 29, 318, 24)

$step = New-Object System.Windows.Forms.Label
$step.Font         = New-Object System.Drawing.Font('Segoe UI', 9)
$step.ForeColor    = [System.Drawing.Color]::FromArgb(200, 215, 235)
$step.AutoEllipsis = $true
$step.SetBounds(66, 56, 262, 20)

$pct = New-Object System.Windows.Forms.Label
$pct.Font      = New-Object System.Drawing.Font('Segoe UI', 9, [System.Drawing.FontStyle]::Bold)
$pct.ForeColor = $green
$pct.TextAlign = 'TopRight'
$pct.SetBounds(328, 56, 56, 20)

# Une case par etape, separees par un filet du fond
$track = New-Object System.Windows.Forms.Panel
$track.BackColor = $navy
$track.SetBounds(66, 82, 318, 8)
$gap      = 3
$segWidth = [int][Math]::Floor((318 - $gap * ($count - 1)) / $count)
$segments = @()
for ($i = 0; $i -lt $count; $i++) {
    $seg = New-Object System.Windows.Forms.Panel
    $seg.BackColor = $deep
    $x = $i * ($segWidth + $gap)
    $w = if ($i -eq $count - 1) { 318 - $x } else { $segWidth }
    $seg.SetBounds($x, 0, $w, 8)
    $track.Controls.Add($seg)
    $segments += $seg
}

$foot = New-Object System.Windows.Forms.Label
$foot.Text      = __FOOT__
$foot.Font      = New-Object System.Drawing.Font('Segoe UI', 8, [System.Drawing.FontStyle]::Italic)
$foot.ForeColor = $grey
$foot.SetBounds(66, 100, 262, 18)

$clock = New-Object System.Windows.Forms.Label
$clock.Font      = New-Object System.Drawing.Font('Segoe UI', 8)
$clock.ForeColor = $grey
$clock.TextAlign = 'TopRight'
$clock.SetBounds(328, 100, 56, 18)

$form.Controls.AddRange(@($accent, $icon, $brand, $title, $step, $pct, $track, $foot, $clock))

# Coins arrondis de Windows 11 ; sans effet, et sans erreur, sous Windows 10
try {
    Add-Type -Namespace SnetorUi -Name Dwm -MemberDefinition '[DllImport("dwmapi.dll")] public static extern int DwmSetWindowAttribute(System.IntPtr hwnd, int attribute, ref int value, int size);'
    $corner = 2
    [void][SnetorUi.Dwm]::DwmSetWindowAttribute($form.Handle, 33, [ref]$corner, 4)
} catch { }

$script:running = -1
$script:pulse   = 0.0
$script:ticks   = 0
$script:closeIn = -1
$script:missing = 0
$watch = [System.Diagnostics.Stopwatch]::StartNew()

# Lecture en partageant l'ecriture et la suppression : le script ecrit pendant qu'on lit. Un
# fichier lu au milieu d'une ecriture n'a pas sa derniere ligne : on garde alors l'affichage.
function Read-Status {
    if (-not [System.IO.File]::Exists($statusFile)) { return 'MISSING' }
    try {
        $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
        $fs = New-Object System.IO.FileStream($statusFile, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, $share)
        try { $text = (New-Object System.IO.StreamReader($fs, [System.Text.Encoding]::UTF8)).ReadToEnd() } finally { $fs.Dispose() }
    } catch { return $null }
    $h = @{}
    foreach ($line in ($text -split "`r?`n")) {
        $i = $line.IndexOf('=')
        if ($i -gt 0) { $h[$line.Substring(0, $i)] = $line.Substring($i + 1) }
    }
    if (-not ($h.ContainsKey('states') -and $h.ContainsKey('done'))) { return $null }
    return $h
}

function Update-View($h) {
    $states = @($h['states'] -split ',')
    $script:running = [array]::IndexOf($states, 'run')
    for ($i = 0; $i -lt [Math]::Min($count, $states.Count); $i++) {
        if ($colors.ContainsKey($states[$i])) { $segments[$i].BackColor = $colors[$states[$i]] }
        elseif ($i -ne $script:running)       { $segments[$i].BackColor = $deep }
    }
    if ($h['done'] -eq '1') {
        $watch.Stop()
        $script:running = -1
        $script:closeIn = 4
        $step.Text = $doneText
        $pct.Text  = '100 %'
        return
    }
    $finished = @($states | Where-Object { $colors.ContainsKey($_) }).Count
    $pct.Text = '{0} %' -f [int][Math]::Round(100 * $finished / $count)
    if ($script:running -ge 0) { $step.Text = $stepFormat -f ($script:running + 1), $count, $h['label'] }
}

function Update-Clock {
    $e = $watch.Elapsed
    $clock.Text = '{0}:{1:00}' -f [int][Math]::Floor($e.TotalMinutes), $e.Seconds
}

function Get-Mix($a, $b, [double]$k) {
    [System.Drawing.Color]::FromArgb(
        [int]($a.R + ($b.R - $a.R) * $k), [int]($a.G + ($b.G - $a.G) * $k), [int]($a.B + ($b.B - $a.B) * $k))
}

$first = Read-Status
if ($first -is [hashtable]) { Update-View $first }
Update-Clock

# Toutes les 80 ms la case en cours pulse ; toutes les 6 (~0,5 s) on relit le fichier
$tick = New-Object System.Windows.Forms.Timer
$tick.Interval = 80
$tick.Add_Tick({
    $script:ticks++
    if ($script:running -ge 0 -and $script:running -lt $count) {
        $script:pulse += 0.25
        $segments[$script:running].BackColor = Get-Mix $deep $green (0.2 + 0.8 * (1 + [Math]::Sin($script:pulse)) / 2)
    }
    if ($script:ticks % 6 -ne 0) { return }

    # Termine : 100 % reste affiche deux secondes
    if ($script:closeIn -ge 0) {
        $script:closeIn--
        if ($script:closeIn -le 0) { $form.Close() }
        return
    }
    Update-Clock

    $h = Read-Status
    if ($h -is [string]) {
        $script:missing++
        if ($script:missing -ge 20) { $form.Close() }
        return
    }
    $script:missing = 0
    if ($h -is [hashtable]) {
        Update-View $h
        if ($script:closeIn -ge 0) { return }
    }

    # Le script qui a ouvert la fenetre n'existe plus, ou ne donne plus signe de vie
    try { [void][System.Diagnostics.Process]::GetProcessById($ownerId) } catch { $form.Close(); return }
    try {
        if (([DateTime]::UtcNow - [System.IO.File]::GetLastWriteTimeUtc($statusFile)).TotalMinutes -gt 45) { $form.Close() }
    } catch { }
})
$form.Add_FormClosed({
    $tick.Stop()
    try { [System.IO.File]::Delete($statusFile) } catch { }
})

$tick.Start()
[void]$form.ShowDialog()
'@

    $ui = $template.
        Replace('__STATUSFILE__', (ConvertTo-PsLiteral $script:ProgressFile)).
        Replace('__OWNERID__', [string]$PID).
        Replace('__COUNT__', [string]$script:ProgressSteps.Count).
        Replace('__GLYPH__', $Glyph).
        Replace('__TITLE__', (ConvertTo-PsLiteral (ConvertFrom-UiText $Title))).
        Replace('__STEPFORMAT__', (ConvertTo-PsLiteral (ConvertFrom-UiText '&Eacute;tape {0} sur {1} : {2}'))).
        Replace('__DONETEXT__', (ConvertTo-PsLiteral (ConvertFrom-UiText $DoneText))).
        Replace('__FOOT__', (ConvertTo-PsLiteral (ConvertFrom-UiText "N'&eacute;teignez pas l'ordinateur.")))
    if (-not (Invoke-InUserSession -ScriptContent $ui -Name 'progression' -TimeoutSec 30 -NoWait)) {
        # Sans fenetre pour le lire, le fichier n'a plus de raison d'etre
        Remove-Item -LiteralPath $script:ProgressFile -Force -ErrorAction SilentlyContinue
        $script:ProgressFile = $null
    }
}

# Boite de consentement : rien ne s'installe sans un clic explicite sur l'un des deux
# boutons d'installation, et c'est ce clic qui fixe ce qui s'installe.
# Renvoie DESKTOP (Claude Desktop + Git), FULL (tout), REFUSE ou TIMEOUT.
function Request-UserConsent {
    param([int]$Seconds = 120)

    $resultFile = Join-Path $script:UiDir 'consentement.txt'
    try {
        New-Item -ItemType Directory -Path $script:UiDir -Force | Out-Null
        # PENDING ecrit AVANT d'ouvrir la fenetre : un choix laisse par un passage
        # precedent ne doit jamais etre relu comme la reponse de celui-ci.
        [System.IO.File]::WriteAllText($resultFile, 'PENDING')
    } catch {
        Write-Warn "Consentement impossible a recueillir : $_"
        return 'TIMEOUT'
    }

    $body = ConvertFrom-UiText (
        "La DSI va installer Claude AI sur votre poste. Choisissez ci-dessous ce que vous souhaitez installer.`r`n`r`n" +
        "Dur&eacute;e estim&eacute;e : 5 &agrave; 10 minutes pour tout installer, moins pour Claude Desktop seul. " +
        "Une barre d'avancement restera affich&eacute;e en bas &agrave; droite de l'&eacute;cran.`r`n`r`n" +
        "Merci de ne pas &eacute;teindre votre ordinateur et de ne pas ouvrir Claude pendant l'installation."
    )
    $captionDesktop = ConvertFrom-UiText "L'application Claude Desktop et Git, rien d'autre."
    $captionFull    = ConvertFrom-UiText "Claude Desktop et Git, plus Claude Code, la configuration Snetor et le connecteur Microsoft 365."
    $countdown = ConvertFrom-UiText "Sans r&eacute;ponse, l'installation sera report&eacute;e dans {0}"

    $template = @'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$resultFile      = __RESULTFILE__
$countdownFormat = __COUNTDOWN__
$total           = __SECONDS__
$script:remain   = $total

$navy  = [System.Drawing.Color]::FromArgb(15, 30, 60)
$green = [System.Drawing.Color]::FromArgb(0, 200, 120)
$light = [System.Drawing.Color]::FromArgb(200, 215, 235)
$deep  = [System.Drawing.Color]::FromArgb(40, 60, 95)

$form = New-Object System.Windows.Forms.Form
$form.Text            = 'Snetor DSI : installation de Claude AI'
$form.FormBorderStyle = 'FixedDialog'
$form.ControlBox      = $false
$form.StartPosition   = 'CenterScreen'
$form.TopMost         = $true
$form.ClientSize      = New-Object System.Drawing.Size(560, 530)
$form.BackColor       = $navy
$form.Add_Shown({ $form.Activate() })

$top = New-Object System.Windows.Forms.Panel
$top.BackColor = $green
$top.SetBounds(0, 0, 560, 6)

$icon = New-Object System.Windows.Forms.Label
$icon.Text      = [string][char]0xE896
$icon.Font      = New-Object System.Drawing.Font('Segoe MDL2 Assets', 28)
$icon.ForeColor = $green
$icon.TextAlign = 'MiddleCenter'
$icon.SetBounds(26, 28, 60, 60)

$title = New-Object System.Windows.Forms.Label
$title.Text      = 'Installation de Claude AI'
$title.Font      = New-Object System.Drawing.Font('Segoe UI', 17, [System.Drawing.FontStyle]::Bold)
$title.ForeColor = [System.Drawing.Color]::White
$title.SetBounds(96, 26, 440, 36)

$sub = New-Object System.Windows.Forms.Label
$sub.Text      = 'Service DSI Snetor'
$sub.Font      = New-Object System.Drawing.Font('Segoe UI', 10.5)
$sub.ForeColor = $green
$sub.SetBounds(98, 64, 440, 22)

$sep = New-Object System.Windows.Forms.Panel
$sep.BackColor = [System.Drawing.Color]::FromArgb(50, 70, 100)
$sep.SetBounds(32, 104, 496, 1)

$body = New-Object System.Windows.Forms.Label
$body.Text      = __BODY__
$body.Font      = New-Object System.Drawing.Font('Segoe UI', 10.5)
$body.ForeColor = $light
$body.SetBounds(32, 120, 496, 170)

function New-FlatButton([string]$Text, $Back, $Fore, [int]$X, [int]$Y, [int]$Width, [int]$Height) {
    $b = New-Object System.Windows.Forms.Button
    $b.Text      = $Text
    $b.Font      = New-Object System.Drawing.Font('Segoe UI', 10.5, [System.Drawing.FontStyle]::Bold)
    $b.BackColor = $Back
    $b.ForeColor = $Fore
    $b.FlatStyle = 'Flat'
    $b.FlatAppearance.BorderSize = 0
    $b.Cursor    = [System.Windows.Forms.Cursors]::Hand
    $b.SetBounds($X, $Y, $Width, $Height)
    $b
}

# Le texte sous chaque bouton dit ce qu'il installe : les deux choix se valent, aucun
# n'est mis en avant, c'est au collab de trancher.
function New-Caption([string]$Text, [int]$X) {
    $c = New-Object System.Windows.Forms.Label
    $c.Text      = $Text
    $c.Font      = New-Object System.Drawing.Font('Segoe UI', 9)
    $c.ForeColor = $light
    $c.SetBounds($X, 356, 240, 52)
    $c
}

$btnDesktop = New-FlatButton 'Claude Desktop + Git' $green ([System.Drawing.Color]::White) 32 302 240 46
$btnFull    = New-FlatButton 'Tout installer' $green ([System.Drawing.Color]::White) 288 302 240 46
$capDesktop = New-Caption __CAPTIONDESKTOP__ 32
$capFull    = New-Caption __CAPTIONFULL__ 288

$countdown = New-Object System.Windows.Forms.Label
$countdown.Font      = New-Object System.Drawing.Font('Segoe UI', 9, [System.Drawing.FontStyle]::Italic)
$countdown.ForeColor = [System.Drawing.Color]::FromArgb(140, 160, 190)
$countdown.SetBounds(32, 420, 496, 20)

$track = New-Object System.Windows.Forms.Panel
$track.BackColor = $deep
$track.SetBounds(32, 446, 496, 6)
$fill = New-Object System.Windows.Forms.Panel
$fill.BackColor = $green
$fill.SetBounds(0, 0, 496, 6)
$track.Controls.Add($fill)

$btnLater = New-FlatButton 'Reporter' $deep $light 190 468 180 38

function Send-Answer([string]$Answer) {
    $tick.Stop()
    [System.IO.File]::WriteAllText($resultFile, $Answer)
    $form.Close()
}
$btnDesktop.Add_Click({ Send-Answer 'DESKTOP' })
$btnFull.Add_Click({ Send-Answer 'FULL' })
$btnLater.Add_Click({ Send-Answer 'REFUSE' })

function Update-Countdown {
    $mmss = '{0}:{1:00}' -f [int][Math]::Floor($script:remain / 60), [int]($script:remain % 60)
    $countdown.Text = $countdownFormat -f $mmss
    $fill.Width = [Math]::Max(1, [int](496 * $script:remain / $total))
}

$tick = New-Object System.Windows.Forms.Timer
$tick.Interval = 1000
$tick.Add_Tick({
    $script:remain--
    if ($script:remain -le 0) { $tick.Stop(); $form.Close(); return }
    Update-Countdown
})

$form.Controls.AddRange(@($top, $icon, $title, $sub, $sep, $body, $btnDesktop, $btnFull, $capDesktop, $capFull, $countdown, $track, $btnLater))
# Le focus va sur Reporter : une touche Entree ou Espace frappee par megarde, pendant que
# le collab ecrivait ailleurs, ne declenche pas l'installation.
$form.ActiveControl = $btnLater
$form.CancelButton  = $btnLater

Update-Countdown
$tick.Start()
[void]$form.ShowDialog()
'@

    $ui = $template.
        Replace('__SECONDS__', [string]$Seconds).
        Replace('__RESULTFILE__', (ConvertTo-PsLiteral $resultFile)).
        Replace('__COUNTDOWN__', (ConvertTo-PsLiteral $countdown)).
        Replace('__CAPTIONDESKTOP__', (ConvertTo-PsLiteral $captionDesktop)).
        Replace('__CAPTIONFULL__', (ConvertTo-PsLiteral $captionFull)).
        Replace('__BODY__', (ConvertTo-PsLiteral $body))
    [void](Invoke-InUserSession -ScriptContent $ui -Name 'consentement' -TimeoutSec ($Seconds + 30))

    $raw = Get-Content -LiteralPath $resultFile -Raw -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $resultFile -Force -ErrorAction SilentlyContinue
    $answer = if ($raw) { $raw.Trim() } else { '' }
    # Seul un clic explicite sur un bouton d'installation l'autorise. Refus, silence, fenetre
    # qui n'a jamais pu s'afficher : tout le reste laisse le poste intact.
    if ($answer -ceq 'DESKTOP') { return 'DESKTOP' }
    if ($answer -ceq 'FULL')    { return 'FULL' }
    if ($answer -ceq 'REFUSE')  { return 'REFUSE' }
    return 'TIMEOUT'
}

# Bilan final : reste ouvert jusqu'au clic (on n'attend pas sa fermeture pour terminer).
function Show-FinalDialog {
    param([string[]]$FailedPhases = @(), [switch]$DesktopOnly)

    if ($FailedPhases.Count -gt 0) {
        $accent = '255, 170, 40'
        $glyph  = '0xE7BA'
        $title  = 'Installation termin&eacute;e avec des erreurs'
        $body   = "Ces &eacute;tapes n'ont pas abouti : $($FailedPhases -join ', ').`r`n`r`n" +
                  "Contactez la DSI en lui indiquant ces &eacute;tapes. " +
                  "Les autres composants sont bien install&eacute;s."
    } elseif ($DesktopOnly) {
        $accent = '0, 200, 120'
        $glyph  = '0xE930'
        $title  = 'Claude AI est install&eacute;'
        $body   = "Pour commencer :`r`n`r`n" +
                  "1.  Fermez puis rouvrez votre session Windows : Claude Desktop appara&icirc;tra dans le menu D&eacute;marrer.`r`n`r`n" +
                  "2.  Ouvrez Claude Desktop et connectez-vous avec votre compte @snetor.com.`r`n`r`n" +
                  "Claude Code et le connecteur Microsoft 365 n'ont pas &eacute;t&eacute; install&eacute;s : " +
                  "demandez-les &agrave; la DSI si vous en avez besoin."
    } else {
        $accent = '0, 200, 120'
        $glyph  = '0xE930'
        $title  = 'Claude AI est install&eacute;'
        $body   = "Pour commencer :`r`n`r`n" +
                  "1.  Fermez puis rouvrez votre session Windows : Claude Desktop appara&icirc;tra dans le menu D&eacute;marrer.`r`n`r`n" +
                  "2.  Ouvrez Claude Desktop et connectez-vous avec votre compte @snetor.com.`r`n`r`n" +
                  "3.  Autorisez le connecteur Microsoft 365 (Param&egrave;tres, puis Extensions).`r`n`r`n" +
                  "4.  Pour Claude Code : ouvrez un nouveau terminal et tapez  claude"
    }

    $template = @'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$accent = [System.Drawing.Color]::FromArgb(__ACCENT__)

$form = New-Object System.Windows.Forms.Form
$form.Text            = 'Snetor DSI : installation de Claude AI'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox     = $false
$form.MinimizeBox     = $false
$form.StartPosition   = 'CenterScreen'
$form.TopMost         = $true
$form.ClientSize      = New-Object System.Drawing.Size(560, 420)
$form.BackColor       = [System.Drawing.Color]::FromArgb(15, 30, 60)
$form.Add_Shown({ $form.Activate() })

$top = New-Object System.Windows.Forms.Panel
$top.BackColor = $accent
$top.SetBounds(0, 0, 560, 6)

$icon = New-Object System.Windows.Forms.Label
$icon.Text      = [string][char]__GLYPH__
$icon.Font      = New-Object System.Drawing.Font('Segoe MDL2 Assets', 28)
$icon.ForeColor = $accent
$icon.TextAlign = 'MiddleCenter'
$icon.SetBounds(26, 28, 60, 60)

$title = New-Object System.Windows.Forms.Label
$title.Text      = __TITLE__
$title.Font      = New-Object System.Drawing.Font('Segoe UI', 17, [System.Drawing.FontStyle]::Bold)
$title.ForeColor = [System.Drawing.Color]::White
$title.SetBounds(96, 26, 440, 36)

$sub = New-Object System.Windows.Forms.Label
$sub.Text      = 'Service DSI Snetor'
$sub.Font      = New-Object System.Drawing.Font('Segoe UI', 10.5)
$sub.ForeColor = [System.Drawing.Color]::FromArgb(0, 200, 120)
$sub.SetBounds(98, 64, 440, 22)

$sep = New-Object System.Windows.Forms.Panel
$sep.BackColor = [System.Drawing.Color]::FromArgb(50, 70, 100)
$sep.SetBounds(32, 104, 496, 1)

$body = New-Object System.Windows.Forms.Label
$body.Text      = __BODY__
$body.Font      = New-Object System.Drawing.Font('Segoe UI', 10.5)
$body.ForeColor = [System.Drawing.Color]::FromArgb(200, 215, 235)
$body.SetBounds(32, 120, 496, 214)

$btn = New-Object System.Windows.Forms.Button
$btn.Text      = 'Fermer'
$btn.Font      = New-Object System.Drawing.Font('Segoe UI', 10.5, [System.Drawing.FontStyle]::Bold)
$btn.BackColor = $accent
$btn.ForeColor = [System.Drawing.Color]::White
$btn.FlatStyle = 'Flat'
$btn.FlatAppearance.BorderSize = 0
$btn.Cursor    = [System.Windows.Forms.Cursors]::Hand
$btn.SetBounds(200, 350, 160, 46)
$btn.Add_Click({ $form.Close() })

$form.Controls.AddRange(@($top, $icon, $title, $sub, $sep, $body, $btn))
$form.AcceptButton = $btn

[void]$form.ShowDialog()
'@

    $ui = $template.
        Replace('__ACCENT__', $accent).
        Replace('__GLYPH__', $glyph).
        Replace('__TITLE__', (ConvertTo-PsLiteral (ConvertFrom-UiText $title))).
        Replace('__BODY__', (ConvertTo-PsLiteral (ConvertFrom-UiText $body)))
    [void](Invoke-InUserSession -ScriptContent $ui -Name 'bilan' -TimeoutSec 30 -NoWait)
}

# --- Phase 1 : Node.js LTS ----------------------------------------------------
function Invoke-Phase1-NodeJS {
    param([string]$Tmp)
    Write-Step "Phase 1 - Node.js LTS"

    # Verifier si Node 18+ deja present
    try {
        $v = & node --version 2>$null
        if ($v -match 'v(\d+)\.' -and [int]$Matches[1] -ge 18) {
            Write-Ok "Node.js $v deja installe - skip"
            $script:phaseResults['Node.js'] = "[OK] D&eacute;j&agrave; pr&eacute;sent ($v)"
            return
        }
    } catch { }

    Write-Info "Resolution de la version LTS via nodejs.org/dist/index.json ..."
    $index = Invoke-RestMethod -Uri 'https://nodejs.org/dist/index.json' -UseBasicParsing
    $lts = $index | Where-Object { $_.lts -and ($_.files -contains 'win-x64-msi') } | Select-Object -First 1
    if (-not $lts) { throw "Impossible de resoudre la version LTS de Node.js" }

    $version = $lts.version
    $msiUrl  = "https://nodejs.org/dist/$version/node-$version-x64.msi"
    $msiPath = Join-Path $Tmp 'node-lts.msi'

    Invoke-Download $msiUrl $msiPath

    Write-Info "Installation silencieuse de Node.js $version ..."
    $proc = Start-Process msiexec -ArgumentList "/i `"$msiPath`" /quiet /norestart ADDLOCAL=ALL" -Wait -PassThru
    if ($proc.ExitCode -ne 0) { throw "msiexec a retourne le code $($proc.ExitCode)" }

    Refresh-PATH

    $v = & node --version 2>$null
    Write-Ok "Node.js $v installe"
    $script:phaseResults['Node.js'] = "[OK] Install&eacute; ($v)"
}

# --- Phase 2 : Git for Windows ------------------------------------------------
function Invoke-Phase2-Git {
    param([string]$Tmp)
    Write-Step "Phase 2 - Git for Windows"

    # Deja present et fonctionnel ?
    try {
        $v = & git --version 2>$null
        if ($v -match 'git version') {
            Write-Ok "$v deja installe - skip"
            $script:phaseResults['Git'] = "[OK] D&eacute;j&agrave; pr&eacute;sent ($($v -replace 'git version ',''))"
            Set-CollabGitIdentity
            return
        }
    } catch { }

    Write-Info "Resolution de la derniere release via api.github.com/git-for-windows ..."
    $asset   = Get-GitHubLatestAsset -Repo 'git-for-windows/git' -NamePattern '^Git-.*-64-bit\.exe$'
    $exePath = Join-Path $Tmp 'git-setup.exe'

    Invoke-Download $asset.Url $exePath

    Write-Info "Installation silencieuse de $($asset.Name) ..."
    $gitArgs = '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES /NOCANCEL /SP- /CLOSEAPPLICATIONS /NORESTARTAPPLICATIONS'
    $proc = Start-Process $exePath -ArgumentList $gitArgs -Wait -PassThru
    if ($proc.ExitCode -ne 0) { throw "L'installeur Git a retourne le code $($proc.ExitCode)" }

    Refresh-PATH

    $v = & git --version 2>$null
    Write-Ok "$v installe"
    $script:phaseResults['Git'] = "[OK] Install&eacute; ($($v -replace 'git version ',''))"
    Set-CollabGitIdentity
}

# --- Phase 3 : Claude Desktop -------------------------------------------------
function Invoke-Phase3-Claude {
    param([string]$Tmp)
    Write-Step "Phase 3 - Claude Desktop"

    # Deja provisionne machine-wide ? (contexte admin : on interroge le provisioning,
    # pas Get-AppxPackage qui ne verrait que les packages de l'admin eleve)
    $existing = Get-AppxProvisionedPackage -Online |
                Where-Object { $_.DisplayName -like '*Claude*' } | Select-Object -First 1
    if ($existing) {
        Write-Ok "Claude Desktop deja provisionne (v$($existing.Version)) - skip"
        $script:phaseResults['Claude Desktop'] = "[OK] D&eacute;j&agrave; pr&eacute;sent (v$($existing.Version))"
        return
    }

    # MSIX officiel signe Anthropic - l'endpoint redirige vers la derniere version (parc Snetor = x64).
    $msixUrl  = 'https://claude.ai/api/desktop/win32/x64/msix/latest/redirect'
    $msixPath = Join-Path $Tmp 'Claude.msix'

    Invoke-Download $msixUrl $msixPath

    # Provisioning machine-wide : Claude est enregistre pour TOUS les utilisateurs du poste
    # (modele DSI). Le collab l'obtient a sa prochaine ouverture de session Windows.
    Write-Info "Provisioning machine-wide du MSIX (Add-AppxProvisionedPackage) ..."
    Add-AppxProvisionedPackage -Online -PackagePath $msixPath -SkipLicense -Regions 'all' | Out-Null

    $installed = Get-AppxProvisionedPackage -Online |
                 Where-Object { $_.DisplayName -like '*Claude*' } | Select-Object -First 1
    if ($installed) {
        Write-Ok "Claude Desktop v$($installed.Version) provisionne (dispo a la prochaine session du collab)"
        $script:phaseResults['Claude Desktop'] = "[OK] Install&eacute; (v$($installed.Version)), visible &agrave; la prochaine ouverture de session"
    } else {
        Write-Warn "Provisioning non verifiable - verifier manuellement"
        Write-Info "URL : https://claude.com/download"
        $script:phaseResults['Claude Desktop'] = '[!] V&eacute;rification manuelle requise par la DSI'
    }
}

# --- Phase 4 : Claude Code (Cowork) ------------------------------------------
function Invoke-Phase4-CoWork {
    param([string]$Tmp)
    Write-Step "Phase 4 - Claude Code (Cowork)"

    Refresh-PATH

    $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
    if (-not $npmCmd) { throw "npm introuvable - verifier l'installation Node.js (Phase 1)" }

    # Pointer le prefix npm vers le profil du collab (pas celui de l'admin).
    # Aucune redirection `2>$null` sur npm : sous 5.1 + Stop, elle rend terminante la moindre
    # ligne de stderr (verifie le 2026-09-28), et npm y ecrit ses "npm notice" de mise a jour.
    $npmPrefix = "$TargetProfile\AppData\Roaming\npm"
    New-Item -ItemType Directory -Path $npmPrefix -Force | Out-Null
    & npm config set prefix $npmPrefix
    if ($LASTEXITCODE -ne 0) { throw "npm config set prefix a echoue (code $LASTEXITCODE)" }

    # Deja installe ? On regarde le paquet sur disque plutot que la sortie de `npm list`,
    # qui ecrit sur stderr et sort en erreur des que l'arbre global a un souci sans rapport.
    if (Test-Path -LiteralPath "$npmPrefix\node_modules\@anthropic-ai\claude-code\package.json") {
        Write-Ok "Claude Code deja installe - skip"
        $script:phaseResults['Claude Code'] = '[OK] D&eacute;j&agrave; pr&eacute;sent'
        return
    }

    Write-Info "npm install -g @anthropic-ai/claude-code ..."
    & npm install -g '@anthropic-ai/claude-code'
    if ($LASTEXITCODE -ne 0) { throw "npm install a echoue (code $LASTEXITCODE)" }

    # npm sur Windows ecrit parfois un BOM UTF-8 (EF BB BF) en tete des wrappers .ps1.
    # PowerShell 5.1 interprete ce BOM comme un nom de commande -> CommandNotFoundException
    # au premier lancement de 'claude'. On reecrit sans BOM tous les .ps1 du prefix.
    $noBom = New-Object System.Text.UTF8Encoding($false)
    Get-ChildItem -Path $npmPrefix -Filter '*.ps1' -ErrorAction SilentlyContinue | ForEach-Object {
        $raw = [System.IO.File]::ReadAllText($_.FullName)
        # Supprimer le BOM si present (U+FEFF en tete)
        if ($raw.StartsWith([char]0xFEFF)) {
            [System.IO.File]::WriteAllText($_.FullName, $raw.TrimStart([char]0xFEFF), $noBom)
            Write-Info "BOM supprime : $($_.Name)"
        }
    }

    # Ajouter le prefix npm au PATH du collab via son hive registre
    # (SetEnvironmentVariable('User') ciblerait l'admin eleve, pas le collab)
    try {
        $sid     = (New-Object System.Security.Principal.NTAccount($TargetUser)).Translate(
                       [System.Security.Principal.SecurityIdentifier]).Value
        $regPath = "Registry::HKEY_USERS\$sid\Environment"
        $currentUserPath = (Get-ItemProperty -Path $regPath -Name PATH -ErrorAction SilentlyContinue).PATH
        if ($currentUserPath -notlike "*$npmPrefix*") {
            $newPath = if ($currentUserPath) { "$currentUserPath;$npmPrefix" } else { $npmPrefix }
            Set-ItemProperty -Path $regPath -Name PATH -Value $newPath
            Write-Info "PATH du collab mis a jour : +$npmPrefix"
        }
    } catch {
        Write-Warn "Impossible de mettre a jour le PATH du collab : $_"
        Write-Info "Action manuelle : ajouter $npmPrefix au PATH utilisateur"
    }

    Write-Ok "Claude Code installe"
    $script:phaseResults['Claude Code'] = '[OK] Install&eacute;'
}

# --- Phase 5 : Config Snetor --------------------------------------------------
function Invoke-Phase5-Snetor {
    param([string]$Tmp)
    Write-Step "Phase 5 - Configuration Snetor"

    $claudeDir = "$TargetProfile\.claude"
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null

    # Telecharger le repo snetor-ai-guidelines
    $repoDir = Join-Path $Tmp 'snetor-ai-guidelines'
    $gitCmd  = Get-Command git -ErrorAction SilentlyContinue

    if ($gitCmd) {
        Write-Info "Clone du repo snetor-ai-guidelines ..."
        # [!] Ni `2>&1`, ni pipe vers Out-Null sur un executable natif.
        #
        # `git clone` ecrit son "Cloning into 'x'..." sur **stderr**, y compris quand tout va
        # bien. En PowerShell 5.1, `2>&1` emballe chaque ligne de stderr dans un ErrorRecord ;
        # avec le `$ErrorActionPreference = 'Stop'` pose en tete de ce script, cet ErrorRecord
        # devient **terminant**. La phase mourait donc sur sa toute premiere action, et le
        # `try/catch` de l'execution principale l'affichait en "Phase 5 echouee" sans que
        # rien - regles d'equipe, hooks, settings.json, status line - ne soit jamais copie.
        #
        # Diagnostique le 2026-09-14 : le poste de l'auteur du depot tournait depuis des
        # semaines sans `workflow.md` ni `snetor-guidelines.md`, avec un `CLAUDE.md` portant une
        # copie collee a la main. `--quiet` supprime le message a la source ; le code de retour
        # est lu explicitement plutot qu'avale.
        & git clone --quiet --depth=1 'https://github.com/snetor/snetor-ai-guidelines.git' $repoDir
        if ($LASTEXITCODE -ne 0) {
            throw "git clone a echoue (code $LASTEXITCODE) - verifier l'acces reseau a github.com"
        }
    } else {
        Write-Info "git absent - telechargement du zip ..."
        $zipPath = Join-Path $Tmp 'repo.zip'
        Invoke-Download 'https://github.com/snetor/snetor-ai-guidelines/archive/refs/heads/main.zip' $zipPath
        Expand-Archive -Path $zipPath -DestinationPath $Tmp -Force
        $repoDir = Join-Path $Tmp 'snetor-ai-guidelines-main'
    }

    if (-not (Test-Path $repoDir)) { throw "Impossible de recuperer le repo snetor-ai-guidelines" }

    # 1. Regles d'equipe (workflow.md + snetor-guidelines.md), importees depuis
    # le CLAUDE.md personnel. Le CLAUDE.md du poste n'est JAMAIS ecrase - seuls
    # les fichiers importes le sont a chaque deploiement - sinon toute
    # personnalisation locale du collab serait perdue (cf. commentaire Phase 5
    # ci-dessus).
    $guidelinesFiles = @(
        @{ Name = 'workflow.md';          Import = '@~/.claude/workflow.md' }
        @{ Name = 'snetor-guidelines.md'; Import = '@~/.claude/snetor-guidelines.md' }
    )

    $importLines = @()
    foreach ($guidelinesFile in $guidelinesFiles) {
        $guidelinesSrc = Join-Path $repoDir "claude-config\$($guidelinesFile.Name)"
        if (Test-Path $guidelinesSrc) {
            Copy-Item $guidelinesSrc "$claudeDir\$($guidelinesFile.Name)" -Force
            Write-Ok "$($guidelinesFile.Name) copie"
            $importLines += $guidelinesFile.Import
        } else {
            Write-Warn "claude-config\$($guidelinesFile.Name) introuvable dans le repo"
        }
    }

    if ($importLines.Count -gt 0) {
        $personalClaudeMd = "$claudeDir\CLAUDE.md"

        # Ecriture sans BOM (System.Text.UTF8Encoding($false)) : meme precaution que
        # Set-JsonFile plus haut, un BOM en tete de CLAUDE.md pourrait perturber le
        # parseur de memory files de Claude Code.
        if (-not (Test-Path $personalClaudeMd)) {
            $lines = @(
                '# Contexte personnel',
                '',
                "Regles d'equipe Snetor (ecrasees a chaque deploiement) :"
            ) + $importLines
            [System.IO.File]::WriteAllText($personalClaudeMd, ($lines -join "`r`n") + "`r`n", (New-Object System.Text.UTF8Encoding($false)))
            Write-Ok "CLAUDE.md personnel cree avec l'import des regles d'equipe"
        } else {
            # Detection ancree ligne entiere : une simple sous-chaine (Select-String
            # -SimpleMatch) matcherait aussi l'import cite dans un commentaire, et
            # l'import reel ne serait alors jamais ajoute.
            $existingLines = Get-Content -Path $personalClaudeMd | ForEach-Object { $_.Trim() }
            foreach ($importLine in $importLines) {
                if ($existingLines -notcontains $importLine.Trim()) {
                    [System.IO.File]::AppendAllText($personalClaudeMd, "`r`n$importLine`r`n", (New-Object System.Text.UTF8Encoding($false)))
                    Write-Ok "Import de $importLine ajoute au CLAUDE.md personnel"
                } else {
                    Write-Ok "CLAUDE.md personnel - import $importLine deja present, inchange"
                }
            }
        }
    }

    # 2. Output styles (styles de reponse selectionnables via /config)
    $stylesSrc = Join-Path $repoDir 'output-styles'
    if (Test-Path $stylesSrc) {
        $stylesDst = "$claudeDir\output-styles"
        New-Item -ItemType Directory -Path $stylesDst -Force | Out-Null
        Copy-Item "$stylesSrc\*.md" $stylesDst -Force
        Write-Ok "Output styles copies ($stylesDst)"
    } else {
        Write-Warn "output-styles introuvable dans le repo - skip"
    }

    # 2 bis. Hooks (hooks/*.py) : garde-fou PreToolUse, memoire de worktree SessionStart
    #
    # Il vivait dans `snetor-pim/ingestion/scripts/claude/` jusqu'au 2026-09-10 : neuf regles
    # protegeaient un depot sur quatorze, pendant que les treize autres n'avaient contre les memes
    # erreurs que de la prose. Les regles sont etroites - celles qui ne concernent pas un depot ne
    # s'y declenchent jamais.
    $hooksSrc = Join-Path $repoDir 'hooks'
    if (Test-Path $hooksSrc) {
        $hooksDst = "$claudeDir\hooks"
        New-Item -ItemType Directory -Path $hooksDst -Force | Out-Null
        Copy-Item "$hooksSrc\*.py" $hooksDst -Force
        $hooksCopies = (Get-ChildItem "$hooksDst\*.py" | ForEach-Object { $_.Name }) -join ', '
        Write-Ok "Hooks copies dans $hooksDst : $hooksCopies"
    } else {
        Write-Warn "hooks/ introuvable dans le repo - skip"
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
        outputStyle  = 'Snetor Brief'
    }

    if (Test-Path $settingsPath) {
        Write-Info "settings.json existant - fusion ..."
        try {
            $cfg = Get-Content $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            Write-Warn "settings.json illisible - reinitialisation"
            $cfg = [PSCustomObject]@{}
        }
    } else {
        $cfg = [PSCustomObject]@{}
    }

    # Appliquer les defaults Snetor seulement si la cle n'existe pas
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

    # Variables d'environnement imposees aux sessions Claude Code.
    #
    # `NX_DAEMON = false` - le 2026-09-14, pendant la montee du fork Twenty de `twenty/v2.30.0`
    # a `twenty/v2.39.0`, `nx build twenty-shared` est reste bloque **11 heures** sur son etape
    # `generateBarrels` : aucun log ecrit, aucun CPU consomme. Un blocage silencieux ressemble a
    # une lenteur, donc on l'attend au lieu de le diagnostiquer. Le daemon Nx en est la cause.
    #
    # Posee ici, au niveau utilisateur, et non dans le fork : le `.claude/settings.json` de
    # `snetor/twenty` est un fichier **amont** - son contenu est identique a `upstream/main`, et
    # Twenty l'a reecrit 5 fois en 6 mois. Y ecrire la variable fabriquerait un point d'ancrage de
    # plus a recoller a chaque montee, exactement ce que le fork cherche a eviter.
    #
    # Verifie le 2026-09-16 : une cle `env` du settings utilisateur arrive bien dans une session
    # ouverte dans le fork, alors meme que le depot a son propre `settings.json` - un settings de
    # projet ne masque que les cles qu'il declare, et celui-la ne declare pas `env`.
    #
    # Un depot qui voudrait le daemon le reactive dans son propre `.claude/settings.json`, qui
    # prime sur celui-ci.
    $snetorEnv = [ordered]@{
        NX_DAEMON = 'false'
    }

    if (-not ($cfg.PSObject.Properties.Name -contains 'env')) {
        $cfg | Add-Member -MemberType NoteProperty -Name 'env' -Value ([PSCustomObject]@{})
    }
    foreach ($k in $snetorEnv.Keys) {
        $cfg.env | Add-Member -MemberType NoteProperty -Name $k -Value $snetorEnv[$k] -Force
    }

    # Brancher le garde-fou en PreToolUse, sans toucher aux autres hooks du poste.
    #
    # [!] Le detour par `runpy` n'est pas de la coquetterie : appeler le script directement
    # verrouille la session des qu'il est absent. `python fichier-inexistant.py` sort en code 2,
    # et 2 est precisement le code qui BLOQUE l'appel d'outil - un poste sans le fichier ne
    # pourrait plus lancer une seule commande (rencontre le 2026-08-14). On teste la presence
    # avant d'executer, et on ne garde le code 2 que quand c'est le garde-fou qui le decide.
    $gardeCommande = @'
python -c "import os,sys,runpy; p=os.path.expanduser('~/.claude/hooks/guard.py'); sys.exit(runpy.run_path(p)['main']() if os.path.isfile(p) else 0)"
'@.Trim()

    if (-not ($cfg.PSObject.Properties.Name -contains 'hooks')) {
        $cfg | Add-Member -MemberType NoteProperty -Name 'hooks' -Value ([PSCustomObject]@{})
    }
    if (-not ($cfg.hooks.PSObject.Properties.Name -contains 'PreToolUse')) {
        $cfg.hooks | Add-Member -MemberType NoteProperty -Name 'PreToolUse' -Value @()
    }

    # Idempotent : on reconnait notre entree a `hooks/guard.py` dans sa commande. Une execution
    # repetee du deployeur ne doit pas empiler dix fois le meme garde-fou.
    $dejaBranche = $false
    foreach ($entree in @($cfg.hooks.PreToolUse)) {
        foreach ($h in @($entree.hooks)) {
            if ($h.command -and $h.command -match 'hooks[\\/]guard\.py') { $dejaBranche = $true }
        }
    }

    if ($dejaBranche) {
        Write-Info "Garde-fou deja branche dans settings.json - inchange"
    } else {
        $entreeGarde = [PSCustomObject]@{
            matcher = 'Bash|PowerShell|Write|Edit|NotebookEdit'
            hooks   = @([PSCustomObject]@{
                type    = 'command'
                command = $gardeCommande
                timeout = 10
            })
        }
        $cfg.hooks.PreToolUse = @($cfg.hooks.PreToolUse) + $entreeGarde
        Write-Ok "Garde-fou branche en PreToolUse"
    }

    # Brancher la memoire de worktree en SessionStart.
    #
    # Claude Code range la memoire d'un projet dans un dossier nomme d'apres le CHEMIN du
    # repertoire de travail. Un worktree est le meme depot dans un autre chemin, donc un autre
    # dossier, vide. Or Git Hygiene impose de travailler en worktree : la regle desarmait la
    # memoire a chaque chantier serieux (mesure le 2026-09-14 sur `snetor-pim` - 52 fichiers de
    # memoire cote checkout principal, 0 dans les trois projets worktree, 8 sessions).
    #
    # Meme precaution `runpy` que pour le garde-fou : un poste sans le fichier ne doit pas voir
    # ses sessions echouer au demarrage.
    $memoireCommande = @'
python -c "import os,sys,runpy; p=os.path.expanduser('~/.claude/hooks/worktree_memory.py'); sys.exit(runpy.run_path(p)['main']() if os.path.isfile(p) else 0)"
'@.Trim()

    if (-not ($cfg.hooks.PSObject.Properties.Name -contains 'SessionStart')) {
        $cfg.hooks | Add-Member -MemberType NoteProperty -Name 'SessionStart' -Value @()
    }

    $memoireDejaBranchee = $false
    foreach ($entree in @($cfg.hooks.SessionStart)) {
        foreach ($h in @($entree.hooks)) {
            if ($h.command -and $h.command -match 'worktree_memory\.py') { $memoireDejaBranchee = $true }
        }
    }

    if ($memoireDejaBranchee) {
        Write-Info "Memoire de worktree deja branchee dans settings.json - inchange"
    } else {
        $entreeMemoire = [PSCustomObject]@{
            hooks = @([PSCustomObject]@{
                type    = 'command'
                command = $memoireCommande
                timeout = 15
            })
        }
        $cfg.hooks.SessionStart = @($cfg.hooks.SessionStart) + $entreeMemoire
        Write-Ok "Memoire de worktree branchee en SessionStart"
    }

    # Brancher le controle de session Azure, en SessionStart ET en PreToolUse.
    #
    # Le 2026-09-15, pendant la montee du fork Twenty, la session `az` a expire **deux fois en
    # pleine sequence** (`AADSTS70043`, duree de vie 7200 s imposee par le controle de frequence de
    # connexion). Chaque expiration a interrompu l'owner au milieu d'un enchainement. La regle
    # "la session `az` expire apres ~2 h" etait ecrite depuis L41 : c'est une recidive.
    #
    # [!] Les DEUX branchements comptent, et le second est celui qui traite l'incident. Au demarrage
    # de session, le jeton etait vivant les deux fois - c'est en cours de sequence qu'il est tombe.
    # Le hook ne coute rien sur une commande qui ne parle pas a `az`, et lit une date d'expiration
    # en cache le reste du temps : il n'invoque `az` que quand cette date approche.
    #
    # Meme precaution `runpy` que pour les deux autres : un poste sans le fichier ne doit pas voir
    # ses sessions echouer au demarrage, ni ses commandes bloquees.
    $jetonCommande = @'
python -c "import os,sys,runpy; p=os.path.expanduser('~/.claude/hooks/az_ensure_login.py'); sys.exit(runpy.run_path(p)['main']() if os.path.isfile(p) else 0)"
'@.Trim()

    $jetonDejaBranche = $false
    foreach ($entree in @($cfg.hooks.SessionStart) + @($cfg.hooks.PreToolUse)) {
        foreach ($h in @($entree.hooks)) {
            if ($h.command -and $h.command -match 'az_ensure_login\.py') { $jetonDejaBranche = $true }
        }
    }

    if ($jetonDejaBranche) {
        Write-Info "Controle de session Azure deja branche dans settings.json - inchange"
    } else {
        $cfg.hooks.SessionStart = @($cfg.hooks.SessionStart) + ([PSCustomObject]@{
            hooks = @([PSCustomObject]@{ type = 'command'; command = $jetonCommande; timeout = 90 })
        })
        $cfg.hooks.PreToolUse = @($cfg.hooks.PreToolUse) + ([PSCustomObject]@{
            matcher = 'Bash|PowerShell'
            hooks   = @([PSCustomObject]@{ type = 'command'; command = $jetonCommande; timeout = 90 })
        })
        Write-Ok "Controle de session Azure branche en SessionStart et PreToolUse"
    }

    Set-JsonFile -Object $cfg -Path $settingsPath
    Write-Ok "settings.json configure (plugins Snetor actives)"

    # 4. Status line
    $statuslineScript = Join-Path $repoDir 'statusline\install.ps1'
    if (Test-Path $statuslineScript) {
        Write-Info "Installation de la status line ..."
        & powershell -NoProfile -ExecutionPolicy Bypass -File $statuslineScript
        Write-Ok "Status line installee"
    } else {
        Write-Warn "statusline/install.ps1 introuvable dans le repo - skip"
    }

    $script:phaseResults['Config Snetor'] = '[OK] R&egrave;gles, hooks et r&eacute;glages Snetor en place'
}

# --- Phase 6 : M365 MCP Config ------------------------------------------------
function Invoke-Phase6-M365 {
    param([string]$Tmp)
    Write-Step "Phase 6 - Connecteur Microsoft 365 MCP"

    # Le MSIX lit sa config dans %LOCALAPPDATA%\Packages\<PFN>\LocalCache\Roaming\Claude.
    # On resout <PackageFamilyName> par ordre de fiabilite decroissante :
    $pfn = $null

    # 1) Package enregistre pour un utilisateur du poste (-AllUsers visible en admin)
    $claudePkg = Get-AppxPackage -AllUsers -Name '*Claude*' -ErrorAction SilentlyContinue |
                 Select-Object -First 1
    if ($claudePkg) { $pfn = $claudePkg.PackageFamilyName }

    # 2) Pas encore enregistre (collab pas reconnecte) : deriver le PFN du package
    #    provisionne - PackageName 'AnthropicClaude_<ver>_x64__<hash>' -> '<Name>_<hash>'
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
        # 3) Dernier recours - le chemin reel se resoudra a la 1re ouverture de Claude Desktop
        $configDir = "$TargetProfile\AppData\Roaming\Claude"
        Write-Warn "Package Claude non resolu - chemin de secours : $configDir"
        Write-Info "Si Claude ne lit pas la config M365, ouvrir Claude Desktop une fois puis relancer cette phase."
    }

    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    $configPath = Join-Path $configDir 'claude_desktop_config.json'

    # Lire config existante ou creer un objet vide
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            Write-Warn "claude_desktop_config.json illisible - reinitialisation"
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
        Write-Ok "Entree microsoft365 deja presente dans claude_desktop_config.json - skip"
    } else {
        $m365 = [PSCustomObject]@{
            command = 'npx'
            args    = @('-y', '@anthropic-ai/mcp-server-microsoft365')
        }
        $config.mcpServers | Add-Member -MemberType NoteProperty -Name 'microsoft365' -Value $m365
        Write-Ok "Entree microsoft365 ajoutee"
    }

    Set-JsonFile -Object $config -Path $configPath
    Write-Info "Config ecrite dans : $configPath"
    $script:phaseResults['M365 MCP'] = '[OK] Connecteur pr&eacute;-configur&eacute;'
}

# --- Phase 7 : Recapitulatif --------------------------------------------------
function Invoke-Phase7-Summary {
    param([System.Collections.Specialized.OrderedDictionary]$Results, [switch]$DesktopOnly)

    Write-Host "`n+==========================================================+" -ForegroundColor Cyan
    Write-Host   "|        Deploiement termine - Recapitulatif               |" -ForegroundColor Cyan
    Write-Host   "+==========================================================+" -ForegroundColor Cyan

    foreach ($phase in $Results.Keys) {
        Write-Host "  $(ConvertTo-LogText $Results[$phase])  $phase"
    }

    Write-Host "`nActions manuelles restantes (a faire par le collab) :" -ForegroundColor Yellow
    Write-Host "  0. Claude Desktop a ete provisionne - il apparait a la prochaine ouverture de session Windows"
    Write-Host "  1. Ouvrir Claude Desktop -> Se connecter avec le compte @snetor.com"
    if ($DesktopOnly) {
        Write-Host "`nChoix du collab : Claude Desktop + Git (ni Node.js, ni Claude Code, ni config Snetor, ni M365)." -ForegroundColor Yellow
        Write-Host "  Pour completer plus tard : relancer ce script et choisir 'Tout installer'."
    } else {
        Write-Host "  2. Dans Claude Desktop : Parametres -> Extensions -> Microsoft 365 -> Autoriser"
        Write-Host "  3. Dans un terminal : taper [claude] -> s'authentifier via le navigateur"

        Write-Host "`nAction admin DSI - une seule fois pour tout le tenant :" -ForegroundColor Yellow
        Write-Host "  4. https://entra.microsoft.com -> Applications d'entreprise"
        Write-Host "     -> 'M365 MCP Client for Claude' -> Accorder le consentement administrateur"
    }

    Write-Host "`nDeploiement Snetor Claude termine pour : $script:TargetUser`n" -ForegroundColor Green
}

# --- Execution principale -----------------------------------------------------
# Rien ne s'installe sans l'accord explicite du collab.
$consent = Request-UserConsent -Seconds 120
if ($consent -eq 'REFUSE') {
    Write-Warn "Le collab a reporte l'installation : rien n'a ete installe."
    Show-Toast -Name 'report' -Status 'warn' -DurationSec 8 `
        -Title (ConvertFrom-UiText 'Installation report&eacute;e') `
        -Message (ConvertFrom-UiText "La DSI vous reproposera l'installation de Claude AI.")
    exit 2
}
if ($consent -ne 'DESKTOP' -and $consent -ne 'FULL') {
    Write-Warn "Pas de reponse du collab dans le delai : rien n'a ete installe."
    exit 3
}
$desktopOnly = $consent -eq 'DESKTOP'

$allPhases = [ordered]@{
    'Node.js'        = 'Invoke-Phase1-NodeJS'
    'Git'            = 'Invoke-Phase2-Git'
    'Claude Desktop' = 'Invoke-Phase3-Claude'
    'Claude Code'    = 'Invoke-Phase4-CoWork'
    'Config Snetor'  = 'Invoke-Phase5-Snetor'
    'M365 MCP'       = 'Invoke-Phase6-M365'
}
# Claude Desktop seul se passe de Node.js : c'est Claude Code, et le connecteur M365 lance
# par npx, qui en ont besoin. La configuration Snetor (~\.claude) est celle de Claude Code.
$desktopPhases = @('Git', 'Claude Desktop')

$phases       = [ordered]@{}
$phaseResults = [ordered]@{}
foreach ($phase in $allPhases.Keys) {
    if ($desktopOnly -and $desktopPhases -notcontains $phase) { continue }
    $phases[$phase]       = $allPhases[$phase]
    $phaseResults[$phase] = '...'
}

if ($desktopOnly) {
    Write-Ok "Le collab a choisi : Claude Desktop + Git"
} else {
    Write-Ok "Le collab a choisi : tout installer"
}
# La barre d'avancement tient lieu des notifications d'etape : elle reste affichee au meme
# endroit, et chaque notification bloquait le script ~7 s.
Open-ProgressWindow -Title 'Installation de Claude AI' -DoneText 'Installation termin&eacute;e' `
    -Glyph '0xE896' -Steps @($phases.Keys)

$tmp = Get-TempDir

$numero = 0
foreach ($phase in $phases.Keys) {
    Set-ProgressStep -Index $numero -State 'run'
    # Le nom et non le numero : en Claude Desktop seul, l'etape 1/2 est la Phase 2 (Git)
    # que la fonction annonce plus haut dans le journal.
    try { & $phases[$phase] $tmp } catch { Write-Fail "Phase $phase echouee : $_"; $phaseResults[$phase] = '[ECHEC]' }
    Set-ProgressStep -Index $numero -State (ConvertTo-ProgressState $phaseResults[$phase])
    $numero++
}
Close-ProgressWindow

Invoke-Phase7-Summary $phaseResults -DesktopOnly:$desktopOnly

$failedPhases = @($phaseResults.Keys | Where-Object { $phaseResults[$_] -eq '[ECHEC]' })
Show-FinalDialog -FailedPhases $failedPhases -DesktopOnly:$desktopOnly

Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue

# Maintenir la fenetre ouverte si lancee en double-clic (hors NinjaOne). Le nom d'hote suffit
# a ecarter l'ISE : tester `$psISE`, absent en console, leverait une erreur sous StrictMode.
if (-not $isSystem -and $Host.Name -eq 'ConsoleHost') {
    Write-Host "Appuyez sur une touche pour fermer ..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
}
# Code de sortie non-zero si au moins une phase a echoue : c'est ce que NinjaOne lit
# (activity log, policies, alerting) pour distinguer un deploiement reussi d'un echec.
# Sans ca, un run ou les 6 phases echouent remonterait quand meme en "Success".
exit [int]($failedPhases.Count -gt 0)
