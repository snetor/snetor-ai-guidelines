#Requires -Version 5.1

<#
.SYNOPSIS
    Desinstallation de ce que pose deploy-claude.ps1 (Desktop + Code + M365 + Snetor).
.DESCRIPTION
    Defait les 6 phases de deploy-claude.ps1, dans l'ordre inverse, avec les memes modes
    d'execution :
      - Session Windows du collab (UAC classique, une seule boite d'elevation)
      - Deploiement NinjaOne (script lance en SYSTEM, detection auto du collab connecte)

    Rien n'est retire sans l'accord du collab : une boite de confirmation s'affiche dans sa
    session, Claude est ensuite ferme d'office, une barre d'avancement reste affichee pendant
    tout le retrait, et un bilan s'affiche a la fin.

    Retrait chirurgical : seul ce que le deploiement a ecrit s'en va. Dans settings.json,
    claude_desktop_config.json, CLAUDE.md et .npmrc, une valeur n'est retiree que si elle vaut
    encore ce que le deploiement y a mis ; le reste du fichier est rendu tel quel.

    Sans -Purge, restent en place : les plugins que Claude Code a telecharges (~/.claude/plugins),
    les jonctions de memoire de worktree (~/.claude/projects), l'historique, la memoire et le jeton
    de connexion. Ce sont des donnees de Claude Code, pas des ecritures du deploiement.

    Fichier volontairement 100 % ASCII, pour la meme raison que deploy-claude.ps1 : colle dans
    NinjaOne, un script perd son BOM, et powershell.exe 5.1 lit alors le fichier en ANSI. Les
    accents des fenetres passent par des entites HTML (voir ConvertFrom-UiText).
.PARAMETER TargetUser
    Nom d'utilisateur du collab. Auto-detecte depuis la session interactive (NinjaOne)
    ou depuis la session courante.
.PARAMETER TargetProfile
    Chemin vers le profil Windows du collab. Auto-detecte si absent.
.PARAMETER TargetEmail
    Email du collab. Son identite Git (user.email) n'est retiree que si elle vaut cet email.
    Auto-detecte comme dans deploy-claude.ps1.
.PARAMETER KeepNodeJs
    Garde Node.js. Sans ce switch, le Node.js installe par MSI (la forme que pose le deploiement)
    est desinstalle, meme s'il etait la avant : le deploiement ne note pas ce qu'il a pose.
.PARAMETER KeepGit
    Garde Git. Sans ce switch, le Git installe pour la machine est desinstalle. Un Git installe
    par utilisateur (AppData\Local\Programs\Git) n'est jamais touche : le deploiement n'en pose pas.
.PARAMETER Purge
    Efface en plus les donnees personnelles de Claude : ~/.claude entier (historique, memoire,
    plugins), ~/.claude.json (jeton de connexion), les caches de Claude Code et de Claude Desktop.
.EXAMPLE
    .\uninstall-claude.ps1 -WhatIf
    Montre ce qui serait retire : sans elevation, sans fenetre, sans rien modifier.
.EXAMPLE
    .\uninstall-claude.ps1 -KeepGit -Purge
.NOTES
    Codes de sortie, lus par NinjaOne :
      0  desinstallation terminee sans echec (ou simulation -WhatIf)
      1  au moins une etape en echec, ou aucun collab en session
      2  le collab a reporte la desinstallation : rien n'est retire
      3  pas de reponse du collab dans le delai : rien n'est retire
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$TargetUser    = '',
    [string]$TargetProfile = '',
    [string]$TargetEmail   = '',
    [switch]$KeepNodeJs,
    [switch]$KeepGit,
    [switch]$Purge
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# -WhatIf pose $WhatIfPreference dans la portee du script. On le fige ici, puis on le coupe :
# laisse actif, il atteint les modules que le script charge (CimCmdlets, Appx, Dism), qui ne
# definissent alors plus leurs alias (vu en simulation le 2026-09-28). La seule porte de chaque
# ecriture est Invoke-Change.
$script:DryRun   = [bool]$WhatIfPreference
$WhatIfPreference = $false

# --- Helpers console ---------------------------------------------------------
function Write-Step { param($msg) Write-Host "`n>>  $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "   [OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "   [!]  $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "   [ECHEC] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "      $msg" -ForegroundColor Gray }

# Toute ecriture passe par ici : cmdlets, executables natifs (msiexec, git, unins000) et appels
# .NET. En simulation elle est decrite et sautee ; sinon elle est jouee, puis annoncee.
# Noms de parametres volontairement rares : le bloc lit les variables de l'appelant.
function Invoke-Change {
    param([string]$ChangeText, [scriptblock]$ChangeBlock)
    if ($script:DryRun) {
        Write-Host "   [SIMULATION] $ChangeText" -ForegroundColor Magenta
        return
    }
    & $ChangeBlock
    Write-Ok $ChangeText
}

# --- Detection du collab (reprise de deploy-claude.ps1) --------------------------
# Trois contextes d'execution :
#   - SYSTEM (NinjaOne) : aucun lien avec le collab, il faut le trouver ;
#   - session du collab, avant elevation : le collab est l'utilisateur courant ;
#   - relance elevee sous le compte admin DSI : $TargetUser et $TargetProfile arrivent
#     en parametres, mais l'utilisateur courant est l'admin, pas le collab.
# Le proprietaire du processus explorer.exe designe le collab dans les trois cas.
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
        # Sans collab detecte, $TargetUser/$TargetProfile retomberaient sur le profil systeme :
        # on arrete plutot que de nettoyer au mauvais endroit en silence.
        Write-Fail "Aucune session interactive detectee sur ce poste (contexte SYSTEM) : desinstallation annulee."
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
            Write-Fail "Profil Windows de $script:TargetUserFull introuvable : desinstallation annulee ($_)"
            exit 1
        }
    }
} elseif (-not $script:TargetUserFull) {
    $script:TargetUserFull = if ($TargetUser) { $TargetUser } else { "$env:USERDOMAIN\$env:USERNAME" }
}

# --- Resolution de l'email du collab (reprise de deploy-claude.ps1) ----------
# Sert a reconnaitre l'identite Git posee par le deploiement, et seulement elle.
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
# Meme convention de dernier recours que le deploiement : c'est ce qu'il aura ecrit.
if (-not $TargetEmail)   { $TargetEmail   = "$TargetUser@snetor.com" }

# --- Auto-elevation (ignoree en contexte SYSTEM NinjaOne et en simulation) --------
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    if ($script:DryRun) {
        # Une simulation ne demande pas d'UAC : elle lit ce qui se lit sans elevation, et le dit.
        Write-Warn "Simulation sans elevation : paquets provisionnes et paquets des autres comptes non lisibles"
    } else {
        Write-Host "Elevation admin requise - une seule boite UAC va s'afficher." -ForegroundColor Yellow
        $escapedScript  = $PSCommandPath -replace '"', '\"'
        $escapedUser    = $TargetUser    -replace '"', '\"'
        $escapedProfile = $TargetProfile -replace '"', '\"'
        $escapedEmail   = $TargetEmail   -replace '"', '\"'
        $psArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$escapedScript`" -TargetUser `"$escapedUser`" -TargetProfile `"$escapedProfile`" -TargetEmail `"$escapedEmail`""
        if ($KeepNodeJs) { $psArgs += ' -KeepNodeJs' }
        if ($KeepGit)    { $psArgs += ' -KeepGit' }
        if ($Purge)      { $psArgs += ' -Purge' }
        # 'powershell.exe' = Windows PowerShell 5.1 (jamais pwsh 7, absent du parc Snetor)
        Start-Process powershell.exe -Verb RunAs -ArgumentList $psArgs
        exit 0
    }
}

Write-Host ""
Write-Host "  Snetor -- Desinstallation Claude DSI" -ForegroundColor Cyan
Write-Host "  Collab  : $TargetUser" -ForegroundColor Cyan
Write-Host "  Profil  : $TargetProfile" -ForegroundColor Cyan
Write-Host "  Email   : $TargetEmail" -ForegroundColor Cyan
Write-Host "  Options : Node.js $(if ($KeepNodeJs) { 'garde' } else { 'retire' }), Git $(if ($KeepGit) { 'garde' } else { 'retire' }), purge $(if ($Purge) { 'oui' } else { 'non' })$(if ($script:DryRun) { ', SIMULATION' })" -ForegroundColor Cyan
Write-Host ""

# Pointer les variables d'env vers le profil du collab (pas celui de l'admin eleve), comme le
# deploiement : `git config --global` resout son fichier par HOME, et %APPDATA% doit designer
# celui du collab quand on developpe une entree de son PATH.
$env:USERPROFILE = $TargetProfile
$env:APPDATA     = "$TargetProfile\AppData\Roaming"
$env:HOME        = $TargetProfile

# Dossier d'echange avec les fenetres du collab : le meme que celui du deploiement.
$script:UiDir     = Join-Path $TargetProfile 'AppData\Local\Temp\SnetorClaude'
$script:ClaudeDir = Join-Path $TargetProfile '.claude'
# Prefix npm pose par la Phase 4 du deploiement
$script:NpmPrefix = "$TargetProfile\AppData\Roaming\npm"
$script:RebootRequired = $false

$phaseResults = [ordered]@{
    'Fermeture de Claude' = '...'
    'M365 MCP'            = '...'
    'Config Snetor'       = '...'
    'Claude Code'         = '...'
    'Claude Desktop'      = '...'
    'Git'                 = '...'
    'Node.js'             = '...'
    'Restes'              = '...'
}
if ($Purge) { $phaseResults['Donn&eacute;es personnelles'] = '...' }

# --- Ce que le deploiement a ecrit -------------------------------------------------
# A tenir alignees avec les Phases 4 a 6 de deploy-claude.ps1 et avec le depot
# snetor-ai-guidelines (claude-config/, output-styles/, hooks/, statusline/). Un nouveau hook
# y exigerait de toute facon une nouvelle entree de settings.json, donc une mise a jour ici.
$script:SnetorPlugins  = @(
    'superpowers@claude-plugins-official'
    'context7@claude-plugins-official'
    'snetor-skills@snetor-ai-guidelines'
)
# Defauts poses seulement si la cle manquait : on ne les retire que s'ils valent encore cela.
# Un collab qui avait deja choisi 'dark' le perd, c'est indiscernable d'un defaut Snetor.
$script:SnetorDefaults = [ordered]@{
    theme       = 'dark'
    effortLevel = 'medium'
    outputStyle = 'Snetor Brief'
}
$script:SnetorEnv = [ordered]@{
    NX_DAEMON = 'false'
}
$script:SnetorHookPattern = '\.claude[\\/]hooks[\\/](guard|worktree_memory|az_ensure_login)\.py'
$script:SnetorFiles = @(
    'workflow.md'
    'snetor-guidelines.md'
    'statusline-command.js'
    'output-styles\snetor-brief.md'
    'hooks\guard.py'
    'hooks\worktree_memory.py'
    'hooks\az_ensure_login.py'
)
$script:SnetorClaudeMdLines = @(
    '@~/.claude/workflow.md'
    '@~/.claude/snetor-guidelines.md'
    "Regles d'equipe Snetor (ecrasees a chaque deploiement) :"
)

# --- Utilitaires fichiers et JSON ----------------------------------------------

# Ecrit du JSON en UTF-8 SANS BOM, comme le deploiement. Profondeur 32 et non 10 : ce fichier
# appartient au collab, rien de ce qu'il contient ne doit etre tronque en chaine.
function Set-JsonFile {
    param([object]$Object, [string]$Path)
    $json = $Object | ConvertTo-Json -Depth 32
    [System.IO.File]::WriteAllText($Path, $json, (New-Object System.Text.UTF8Encoding($false)))
}

# $null si le fichier est absent. Exception s'il est illisible : l'etape laisse alors le fichier
# intact, la ou le deploiement le reinitialiserait.
function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $raw = [System.IO.File]::ReadAllText($Path)
    if (-not $raw.Trim()) { return [PSCustomObject]@{} }
    return ($raw | ConvertFrom-Json)
}

function Test-JsonObject {
    param([object]$Value)
    return ($Value -is [System.Management.Automation.PSCustomObject])
}

function Get-PropertyCount {
    param([object]$Object)
    return @($Object.PSObject.Properties).Count
}

# Retire $Name de $Object. Avec $Expected, seulement si la valeur est encore cette chaine exacte.
function Remove-JsonValue {
    param([object]$Object, [string]$Name, [object]$Expected = $null)
    if (-not (Test-JsonObject $Object)) { return $false }
    $p = $Object.PSObject.Properties[$Name]
    if (-not $p) { return $false }
    if ($null -ne $Expected -and -not ($p.Value -is [string] -and $p.Value -ceq $Expected)) { return $false }
    $Object.PSObject.Properties.Remove($Name)
    return $true
}

# Retire la propriete $Name de $Parent si c'est un objet devenu vide.
function Remove-EmptyObject {
    param([object]$Parent, [string]$Name)
    $p = $Parent.PSObject.Properties[$Name]
    if ($p -and (Test-JsonObject $p.Value) -and (Get-PropertyCount $p.Value) -eq 0) {
        $Parent.PSObject.Properties.Remove($Name)
    }
}

# Retire de settings.json (objet deja lu) ce que la Phase 5 et statusline/install.ps1 y ont mis.
# Modifie l'objet et rend la liste de ce qui a ete retire.
function Remove-SnetorSettings {
    param([object]$Cfg)
    $removed = @()

    $plugins = $Cfg.PSObject.Properties['enabledPlugins']
    if ($plugins -and (Test-JsonObject $plugins.Value)) {
        foreach ($name in $script:SnetorPlugins) {
            if (Remove-JsonValue $plugins.Value $name) { $removed += "enabledPlugins.$name" }
        }
        Remove-EmptyObject $Cfg 'enabledPlugins'
    }

    foreach ($k in $script:SnetorDefaults.Keys) {
        if (Remove-JsonValue $Cfg $k $script:SnetorDefaults[$k]) { $removed += $k }
    }

    $envProp = $Cfg.PSObject.Properties['env']
    if ($envProp -and (Test-JsonObject $envProp.Value)) {
        foreach ($k in $script:SnetorEnv.Keys) {
            if (Remove-JsonValue $envProp.Value $k $script:SnetorEnv[$k]) { $removed += "env.$k" }
        }
        Remove-EmptyObject $Cfg 'env'
    }

    # Hooks : on retire la commande Snetor, puis l'entree si elle n'a plus de commande, puis
    # l'evenement s'il n'a plus d'entree. Une entree qui porte aussi un hook du collab reste.
    # Tableaux reconstruits par @() : un tableau d'un element ecrit en objet casserait Claude Code.
    $hooksProp = $Cfg.PSObject.Properties['hooks']
    if ($hooksProp -and (Test-JsonObject $hooksProp.Value)) {
        $hooks = $hooksProp.Value
        foreach ($evt in @($hooks.PSObject.Properties | ForEach-Object { $_.Name })) {
            $kept    = @()
            $changed = $false
            foreach ($entry in @($hooks.$evt)) {
                $inner = if ($null -ne $entry) { $entry.PSObject.Properties['hooks'] } else { $null }
                if (-not $inner) { $kept += $entry; continue }
                $cmds     = @($inner.Value)
                $keepCmds = @($cmds | Where-Object {
                    -not ($null -ne $_ -and $_.PSObject.Properties['command'] -and [string]$_.command -match $script:SnetorHookPattern)
                })
                if ($keepCmds.Count -eq $cmds.Count) { $kept += $entry; continue }
                $changed = $true
                foreach ($c in $cmds) {
                    if ($null -ne $c -and $c.PSObject.Properties['command'] -and [string]$c.command -match $script:SnetorHookPattern) {
                        $removed += "hooks.$evt ($($Matches[1]).py)"
                    }
                }
                if ($keepCmds.Count -gt 0) {
                    $entry.hooks = $keepCmds
                    $kept += $entry
                }
            }
            if ($changed) {
                if ($kept.Count -gt 0) { $hooks.$evt = $kept } else { $hooks.PSObject.Properties.Remove($evt) }
            }
        }
        Remove-EmptyObject $Cfg 'hooks'
    }

    $sl = $Cfg.PSObject.Properties['statusLine']
    if ($sl -and (Test-JsonObject $sl.Value) -and $sl.Value.PSObject.Properties['command'] -and
        [string]$sl.Value.command -match 'statusline-command\.js') {
        $Cfg.PSObject.Properties.Remove('statusLine')
        $removed += 'statusLine'
    }

    return $removed
}

# Retire d'un texte les lignes que $Match reconnait, puis les lignes vides laissees en fin de
# fichier. Fins de ligne d'origine conservees. Rend Changed, Text et Lines (lignes gardees).
function Remove-TextLines {
    param([string]$Text, [scriptblock]$Match)
    $nl    = if ($Text.Contains("`r`n")) { "`r`n" } else { "`n" }
    $lines = @($Text -split "`r?`n")
    $kept  = @($lines | Where-Object { -not (& $Match $_) })
    if ($kept.Count -eq $lines.Count) {
        return [PSCustomObject]@{ Changed = $false; Text = $Text; Lines = $lines }
    }
    $end = $kept.Count
    while ($end -gt 0 -and -not $kept[$end - 1].Trim()) { $end-- }
    # @() autour du if : un if affecte deroule son resultat, un tableau vide y deviendrait $null
    $kept = @(if ($end -gt 0) { $kept[0..($end - 1)] })
    $newText = if ($kept.Count -gt 0) { ($kept -join $nl) + $nl } else { '' }
    return [PSCustomObject]@{ Changed = $true; Text = $newText; Lines = $kept }
}

# CLAUDE.md : retire les imports et l'en-tete de la Phase 5. Delete = il ne reste que le titre
# que le deploiement avait lui-meme ecrit.
function Remove-SnetorClaudeMd {
    param([string]$Text)
    $r = Remove-TextLines -Text $Text -Match { param($l) $script:SnetorClaudeMdLines -contains $l.Trim() }
    $meaningful = @($r.Lines | Where-Object { $_.Trim() -and $_.Trim() -ne '# Contexte personnel' })
    return [PSCustomObject]@{ Changed = $r.Changed; Delete = ($r.Changed -and $meaningful.Count -eq 0); Text = $r.Text }
}

function ConvertTo-ComparablePath {
    param([string]$Path)
    $p = [Environment]::ExpandEnvironmentVariables($Path.Trim().Trim('"'))
    return $p.TrimEnd('\').ToLowerInvariant()
}

# .npmrc : retire la ligne `prefix=` que `npm config set prefix` a ecrite, si elle vaut $Prefix.
function Remove-NpmPrefixLine {
    param([string]$Text, [string]$Prefix)
    $target = ConvertTo-ComparablePath $Prefix
    $r = Remove-TextLines -Text $Text -Match {
        param($l)
        $l -match '^\s*prefix\s*=\s*(.+?)\s*$' -and (ConvertTo-ComparablePath $Matches[1]) -eq $target
    }
    $rest = @($r.Lines | Where-Object { $_.Trim() })
    return [PSCustomObject]@{ Changed = $r.Changed; Delete = ($r.Changed -and $rest.Count -eq 0); Text = $r.Text }
}

# PATH : retire les entrees qui designent $Entry (forme developpee ou %VAR%, casse et barre
# finale indifferentes). Les autres segments, vides compris, restent tels quels.
function Remove-PathEntry {
    param([string]$PathValue, [string]$Entry)
    $target = ConvertTo-ComparablePath $Entry
    $parts  = @($PathValue -split ';')
    $kept   = @($parts | Where-Object { -not ($_.Trim() -and (ConvertTo-ComparablePath $_) -eq $target) })
    return [PSCustomObject]@{ Changed = ($kept.Count -ne $parts.Count); Value = ($kept -join ';') }
}

# Reecrit un fichier texte du collab en gardant son BOM s'il en avait un.
function Set-TextFileLike {
    param([string]$Path, [string]$Text, [bool]$Bom)
    [System.IO.File]::WriteAllText($Path, $Text, (New-Object System.Text.UTF8Encoding($Bom)))
}

function Test-Utf8Bom {
    param([string]$Path)
    $b = [System.IO.File]::ReadAllBytes($Path)
    return ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
}

# Suppression recursive qui ne suit jamais un point de reanalyse (jonction, lien symbolique) :
# le lien est retire, sa cible reste. Le hook worktree_memory.py pose des jonctions dans
# ~/.claude/projects : plutot que de dependre de la facon dont Remove-Item -Recurse traite les
# liens selon les versions, la regle est tenue ici par construction.
function Remove-TreeNoFollow {
    param([string]$Path)
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $item) { return }
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        if ($item.PSIsContainer) { [System.IO.Directory]::Delete($item.FullName, $false) }
        else { [System.IO.File]::Delete($item.FullName) }
        return
    }
    if ($item.PSIsContainer) {
        foreach ($child in @(Get-ChildItem -LiteralPath $item.FullName -Force)) {
            Remove-TreeNoFollow $child.FullName
        }
        $item.Attributes = [System.IO.FileAttributes]::Directory
        [System.IO.Directory]::Delete($item.FullName, $false)
    } else {
        $item.Attributes = [System.IO.FileAttributes]::Normal
        [System.IO.File]::Delete($item.FullName)
    }
}

# Supprime un dossier seulement s'il est vide. $true s'il l'a supprime.
function Remove-DirIfEmpty {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) { return $false }
    if (@(Get-ChildItem -LiteralPath $Path -Force).Count -gt 0) { return $false }
    if ($script:DryRun) { return $false }
    [System.IO.Directory]::Delete($Path, $false)
    return $true
}

# Message d'erreur sur une ligne : Appx et DISM en rendent sur plusieurs, qui cassent le journal
function ConvertTo-OneLine {
    param([string]$Text)
    return ($Text -replace '\s+', ' ').Trim()
}

# --- Utilitaires paquets ----------------------------------------------------------

# Claude Desktop : Name exact et editeur, la ou le deploiement filtre '*Claude*' (qui ramasserait
# n'importe quel paquet contenant le mot). -AllUsers exige l'elevation : en simulation non elevee,
# repli sur les paquets du compte courant.
function Get-ClaudeDesktopState {
    $installed = @()
    $errors    = @()
    try {
        $installed = @(Get-AppxPackage -AllUsers -Name 'Claude' -ErrorAction Stop)
    } catch {
        $installed = @(Get-AppxPackage -Name 'Claude' -ErrorAction SilentlyContinue)
        $errors   += "paquets des autres comptes non lisibles ($(ConvertTo-OneLine $_.Exception.Message))"
    }
    $installed = @($installed | Where-Object { $_.Publisher -match 'Anthropic' })
    $provisioned = @()
    try {
        $provisioned = @(Get-AppxProvisionedPackage -Online -ErrorAction Stop | Where-Object { $_.DisplayName -eq 'Claude' })
    } catch {
        $errors += "provisionnement non lisible ($(ConvertTo-OneLine $_.Exception.Message))"
    }
    return [PSCustomObject]@{ Installed = $installed; Provisioned = $provisioned; Errors = $errors }
}

# Paquets npm globaux du prefix qui ne sont pas Claude Code (ni ses paquets de plateforme)
function Get-OtherGlobalPackages {
    param([string]$Prefix)
    $nm = Join-Path $Prefix 'node_modules'
    if (-not (Test-Path -LiteralPath $nm)) { return @() }
    $names = @()
    foreach ($d in @(Get-ChildItem -LiteralPath $nm -Force | Where-Object { $_.Name -notlike '.*' })) {
        if ($d.PSIsContainer -and $d.Name -like '@*') {
            foreach ($s in @(Get-ChildItem -LiteralPath $d.FullName -Force | Where-Object { $_.Name -notlike '.*' })) {
                $n = "$($d.Name)/$($s.Name)"
                if ($n -notlike '@anthropic-ai/claude-code*') { $names += $n }
            }
        } else {
            $names += $d.Name
        }
    }
    return $names
}

$script:UninstallRoots = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
)

function Get-UninstallEntries {
    foreach ($root in $script:UninstallRoots) {
        foreach ($k in @(Get-ChildItem -LiteralPath $root -ErrorAction SilentlyContinue)) {
            $p = Get-ItemProperty -LiteralPath $k.PSPath -ErrorAction SilentlyContinue
            if ($p) { $p }
        }
    }
}

function Get-RegValue {
    param([object]$Entry, [string]$Name)
    $p = $Entry.PSObject.Properties[$Name]
    if ($p) { return $p.Value }
    return $null
}

# Git installe pour la machine (cle Inno Setup Git_is1 sous HKLM) : la seule forme que pose la
# Phase 2, lancee elevee. Un Git par utilisateur s'inscrit sous HKCU et n'est pas vu ici.
# Lecture directe de la cle : elle est relue toutes les 2 s pendant le retrait.
function Get-MachineGit {
    foreach ($root in $script:UninstallRoots) {
        $p = Get-ItemProperty -LiteralPath "$root\Git_is1" -ErrorAction SilentlyContinue
        if ($p) { return $p }
    }
    return $null
}

# Node.js installe par MSI (Phase 1)
function Get-NodeMsi {
    return @(Get-UninstallEntries | Where-Object {
        (Get-RegValue $_ 'DisplayName') -eq 'Node.js' -and (Get-RegValue $_ 'WindowsInstaller') -eq 1
    })
}

# --- Fenetres dans la session du collab (reprises de deploy-claude.ps1) ------------
# Ce script tourne en SYSTEM (NinjaOne) ou sous le compte admin DSI (relance UAC) : une
# fenetre ouverte par ce processus n'apparait pas sur le bureau du collab. On passe donc
# par une tache planifiee ephemere, executee SOUS LE COMPTE DU COLLAB dans sa session
# ouverte, qui lance powershell.exe masque via wscript.

# Texte des fenetres : ce fichier reste 100 % ASCII, les accents passent par des entites
# HTML (&eacute; e accent aigu, &egrave; e grave, &agrave; a grave, &ecirc; e circonflexe,
# &Eacute; E accent aigu, &bull; puce).
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

# Supprime une tache par l'API COM du planificateur (Get-ScheduledTask et
# Unregister-ScheduledTask enumerent toutes les taches du poste avant d'agir : 4,5 s par appel).
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
    # script quand un appel suivant du meme nom viendrait l'ecraser.
    $id       = [guid]::NewGuid().ToString('N').Substring(0, 8)
    $ps1      = Join-Path $script:UiDir "$Name-$id.ps1"
    $vbs      = Join-Path $script:UiDir "$Name-$id.vbs"
    $taskName = "SnetorClaude-$Name"
    $shown    = $false
    try {
        New-Item -ItemType Directory -Path $script:UiDir -Force | Out-Null

        # UTF-8 AVEC BOM : c'est ainsi que powershell.exe 5.1 lit un script sans le prendre
        # pour de l'ANSI. Le script s'efface des son lancement (il est deja en memoire).
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

        # Suivi par LastTaskResult seul : 267011 = pas encore lancee, 267009 = en cours, sinon
        # le code de sortie de powershell.
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

# Texte de la boite de confirmation, selon les options
function Get-ConsentBody {
    $lines = @(
        "La DSI va retirer Claude AI de votre poste :"
        "     &bull;  Claude Desktop et Claude Code"
        "     &bull;  la configuration Snetor et le connecteur Microsoft 365"
    )
    $tools = @()
    if (-not $KeepNodeJs) { $tools += 'Node.js' }
    if (-not $KeepGit)    { $tools += 'Git' }
    if ($tools.Count -gt 0) { $lines += "     &bull;  $($tools -join ' et ')" }
    if ($Purge) { $lines += "     &bull;  vos conversations, votre m&eacute;moire et vos r&eacute;glages Claude" }
    $lines += @(
        ''
        "Claude sera ferm&eacute; automatiquement : enregistrez votre travail en cours."
        ''
        "Dur&eacute;e estim&eacute;e : 2 &agrave; 5 minutes. Une barre d'avancement restera affich&eacute;e en bas &agrave; droite de l'&eacute;cran."
    )
    return ($lines -join "`r`n")
}

# Boite de confirmation : rien n'est retire sans un clic explicite sur "Desinstaller".
# Renvoie ACCEPT, REFUSE ou TIMEOUT.
function Request-UserConsent {
    param([int]$Seconds = 120)

    $resultFile = Join-Path $script:UiDir 'consentement-retrait.txt'
    try {
        New-Item -ItemType Directory -Path $script:UiDir -Force | Out-Null
        # PENDING ecrit AVANT d'ouvrir la fenetre : un ACCEPT laisse par un passage
        # precedent ne doit jamais etre relu comme la reponse de celui-ci.
        [System.IO.File]::WriteAllText($resultFile, 'PENDING')
    } catch {
        Write-Warn "Consentement impossible a recueillir : $_"
        return 'TIMEOUT'
    }

    $body      = ConvertFrom-UiText (Get-ConsentBody)
    $countdown = ConvertFrom-UiText "Sans r&eacute;ponse, la d&eacute;sinstallation sera report&eacute;e dans {0}"
    $caption   = ConvertFrom-UiText 'Snetor DSI : d&eacute;sinstallation de Claude AI'
    $title     = ConvertFrom-UiText 'D&eacute;sinstallation de Claude AI'
    $btnOk     = ConvertFrom-UiText 'D&eacute;sinstaller'

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
$form.Text            = __CAPTION__
$form.FormBorderStyle = 'FixedDialog'
$form.ControlBox      = $false
$form.StartPosition   = 'CenterScreen'
$form.TopMost         = $true
$form.ClientSize      = New-Object System.Drawing.Size(560, 440)
$form.BackColor       = $navy
$form.Add_Shown({ $form.Activate() })

$top = New-Object System.Windows.Forms.Panel
$top.BackColor = $green
$top.SetBounds(0, 0, 560, 6)

$icon = New-Object System.Windows.Forms.Label
$icon.Text      = [string][char]0xE74D
$icon.Font      = New-Object System.Drawing.Font('Segoe MDL2 Assets', 28)
$icon.ForeColor = $green
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
$sub.ForeColor = $green
$sub.SetBounds(98, 64, 440, 22)

$sep = New-Object System.Windows.Forms.Panel
$sep.BackColor = [System.Drawing.Color]::FromArgb(50, 70, 100)
$sep.SetBounds(32, 104, 496, 1)

$body = New-Object System.Windows.Forms.Label
$body.Text      = __BODY__
$body.Font      = New-Object System.Drawing.Font('Segoe UI', 10.5)
$body.ForeColor = $light
$body.SetBounds(32, 120, 496, 190)

$countdown = New-Object System.Windows.Forms.Label
$countdown.Font      = New-Object System.Drawing.Font('Segoe UI', 9, [System.Drawing.FontStyle]::Italic)
$countdown.ForeColor = [System.Drawing.Color]::FromArgb(140, 160, 190)
$countdown.SetBounds(32, 318, 496, 20)

$track = New-Object System.Windows.Forms.Panel
$track.BackColor = $deep
$track.SetBounds(32, 342, 496, 6)
$fill = New-Object System.Windows.Forms.Panel
$fill.BackColor = $green
$fill.SetBounds(0, 0, 496, 6)
$track.Controls.Add($fill)

function New-FlatButton([string]$Text, $Back, $Fore, [int]$X) {
    $b = New-Object System.Windows.Forms.Button
    $b.Text      = $Text
    $b.Font      = New-Object System.Drawing.Font('Segoe UI', 10.5, [System.Drawing.FontStyle]::Bold)
    $b.BackColor = $Back
    $b.ForeColor = $Fore
    $b.FlatStyle = 'Flat'
    $b.FlatAppearance.BorderSize = 0
    $b.Cursor    = [System.Windows.Forms.Cursors]::Hand
    $b.SetBounds($X, 372, 240, 46)
    $b
}
$btnRemove = New-FlatButton __BTNOK__ $green ([System.Drawing.Color]::White) 32
$btnLater  = New-FlatButton 'Reporter' $deep $light 288

function Send-Answer([string]$Answer) {
    $tick.Stop()
    [System.IO.File]::WriteAllText($resultFile, $Answer)
    $form.Close()
}
$btnRemove.Add_Click({ Send-Answer 'ACCEPT' })
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

$form.Controls.AddRange(@($top, $icon, $title, $sub, $sep, $body, $countdown, $track, $btnRemove, $btnLater))
# Le focus va sur Reporter : une touche Entree ou Espace frappee par megarde, pendant que
# le collab ecrivait ailleurs, ne declenche pas la desinstallation.
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
        Replace('__CAPTION__', (ConvertTo-PsLiteral $caption)).
        Replace('__TITLE__', (ConvertTo-PsLiteral $title)).
        Replace('__BTNOK__', (ConvertTo-PsLiteral $btnOk)).
        Replace('__BODY__', (ConvertTo-PsLiteral $body))
    [void](Invoke-InUserSession -ScriptContent $ui -Name 'consentement-retrait' -TimeoutSec ($Seconds + 30))

    $raw = Get-Content -LiteralPath $resultFile -Raw -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $resultFile -Force -ErrorAction SilentlyContinue
    $answer = if ($raw) { $raw.Trim() } else { '' }
    # Seul un ACCEPT explicite autorise le retrait. Refus, silence, fenetre qui n'a jamais pu
    # s'afficher : tout le reste laisse le poste intact.
    if ($answer -ceq 'ACCEPT') { return 'ACCEPT' }
    if ($answer -ceq 'REFUSE') { return 'REFUSE' }
    return 'TIMEOUT'
}

# Texte du bilan final : titre, corps, couleur, glyphe
function Get-FinalContent {
    param([string[]]$FailedPhases = @())
    if ($FailedPhases.Count -gt 0) {
        return [PSCustomObject]@{
            Accent = '255, 170, 40'
            Glyph  = '0xE7BA'
            # Court : le titre tient sur 440 px en 17 pt, un titre plus long est tronque
            Title  = 'D&eacute;sinstallation incompl&egrave;te'
            Body   = "Ces &eacute;tapes n'ont pas abouti : $($FailedPhases -join ', ').`r`n`r`n" +
                     "Contactez la DSI en lui indiquant ces &eacute;tapes. " +
                     "Le reste a bien &eacute;t&eacute; retir&eacute;."
        }
    }
    $body = "Claude Desktop, Claude Code, la configuration Snetor et le connecteur Microsoft 365 " +
            "ont &eacute;t&eacute; retir&eacute;s de votre poste."
    if ($Purge) { $body += "`r`n`r`nVos conversations, votre m&eacute;moire et vos r&eacute;glages Claude ont &eacute;t&eacute; effac&eacute;s." }
    if ($script:RebootRequired) {
        $body += "`r`n`r`nRed&eacute;marrez votre ordinateur pour terminer."
    } else {
        $body += "`r`n`r`nFermez puis rouvrez votre session Windows pour finaliser."
    }
    return [PSCustomObject]@{
        Accent = '0, 200, 120'
        Glyph  = '0xE930'
        Title  = 'Claude AI est d&eacute;sinstall&eacute;'
        Body   = $body
    }
}

# Bilan final : reste ouvert jusqu'au clic (on n'attend pas sa fermeture pour terminer).
function Show-FinalDialog {
    param([string[]]$FailedPhases = @())

    $c = Get-FinalContent -FailedPhases $FailedPhases

    $template = @'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$accent = [System.Drawing.Color]::FromArgb(__ACCENT__)

$form = New-Object System.Windows.Forms.Form
$form.Text            = __CAPTION__
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

# Dernier occupant du dossier d'echange : on le retire s'il est vide (Delete non recursif).
try { [System.IO.Directory]::Delete((Split-Path -Parent $PSCommandPath)) } catch { }
'@

    $ui = $template.
        Replace('__ACCENT__', $c.Accent).
        Replace('__GLYPH__', $c.Glyph).
        Replace('__CAPTION__', (ConvertTo-PsLiteral (ConvertFrom-UiText 'Snetor DSI : d&eacute;sinstallation de Claude AI'))).
        Replace('__TITLE__', (ConvertTo-PsLiteral (ConvertFrom-UiText $c.Title))).
        Replace('__BODY__', (ConvertTo-PsLiteral (ConvertFrom-UiText $c.Body)))
    [void](Invoke-InUserSession -ScriptContent $ui -Name 'bilan-retrait' -TimeoutSec 30 -NoWait)
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

# --- Etape 1 : fermeture de Claude ---------------------------------------------------
# Claude Desktop (exe sous WindowsApps\Claude_*), Claude Code (exe natif sous le prefix npm,
# restes de mise a jour compris) et le connecteur M365 lance par Claude Desktop via npx.
# Toutes sessions : on tourne en admin ou en SYSTEM.
function Invoke-Step1-StopClaude {
    Write-Step "Etape 1 - Fermeture de Claude"
    $prefixAi = "$script:NpmPrefix\node_modules\@anthropic-ai\"
    $procs = @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
        $exe = [string]$_.ExecutablePath
        $cmd = [string]$_.CommandLine
        $_.ProcessId -ne $PID -and (
            ($exe -like '*\WindowsApps\Claude_*') -or
            ($exe -and $exe.StartsWith($prefixAi, [StringComparison]::OrdinalIgnoreCase)) -or
            ($cmd -match 'node_modules[\\/]@anthropic-ai[\\/]claude-code') -or
            ($cmd -match 'mcp-server-microsoft365'))
    })
    if ($procs.Count -eq 0) {
        Write-Ok "Aucun processus Claude en cours"
        $script:phaseResults['Fermeture de Claude'] = '[OK] Aucun processus'
        return
    }
    $ids   = @($procs | ForEach-Object { [int]$_.ProcessId })
    $noms  = (@($procs | Group-Object Name | ForEach-Object { "$($_.Name) x$($_.Count)" }) -join ', ')
    Invoke-Change "arret de $($procs.Count) processus ($noms)" {
        foreach ($i in $ids) { Stop-Process -Id $i -Force -ErrorAction SilentlyContinue }
        Wait-Process -Id $ids -Timeout 15 -ErrorAction SilentlyContinue
        $alive = @($ids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue })
        if ($alive.Count -gt 0) { throw "processus toujours actifs apres 15 s : $($alive -join ', ')" }
    }
    $script:phaseResults['Fermeture de Claude'] = "[OK] $($procs.Count) processus"
}

# --- Etape 2 : connecteur M365 (inverse de la Phase 6) ------------------------------------
function Invoke-Step2-M365 {
    Write-Step "Etape 2 - Connecteur Microsoft 365 MCP"
    # Les deux emplacements que la Phase 6 a pu choisir : LocalCache du paquet (le PFN resolu,
    # ou tout reste de paquet Claude_*), et le repli AppData\Roaming\Claude.
    $paths = @()
    $pkgRoot = Join-Path $TargetProfile 'AppData\Local\Packages'
    if (Test-Path -LiteralPath $pkgRoot) {
        $paths += @(Get-ChildItem -LiteralPath $pkgRoot -Directory -Filter 'Claude_*' -Force -ErrorAction SilentlyContinue |
                    ForEach-Object { Join-Path $_.FullName 'LocalCache\Roaming\Claude\claude_desktop_config.json' })
    }
    $paths += Join-Path $TargetProfile 'AppData\Roaming\Claude\claude_desktop_config.json'

    $count = 0
    $warn  = $null
    foreach ($path in $paths) {
        if (-not (Test-Path -LiteralPath $path)) { continue }
        try { $config = Read-JsonFile $path } catch {
            Write-Warn "$path illisible : laisse tel quel ($_)"
            $warn = 'fichier illisible laiss&eacute; tel quel'
            continue
        }
        $servers = $config.PSObject.Properties['mcpServers']
        $m365    = if ($servers -and (Test-JsonObject $servers.Value)) { $servers.Value.PSObject.Properties['microsoft365'] } else { $null }
        $ours    = $m365 -and (Test-JsonObject $m365.Value) -and $m365.Value.PSObject.Properties['args'] -and
                   (@($m365.Value.args) -contains '@anthropic-ai/mcp-server-microsoft365')
        if (-not $ours) {
            Write-Info "Pas d'entree microsoft365 du deploiement dans $path"
            continue
        }
        $servers.Value.PSObject.Properties.Remove('microsoft365')
        Remove-EmptyObject $config 'mcpServers'
        if ((Get-PropertyCount $config) -eq 0) {
            Invoke-Change "suppression de $path (il ne contenait que le connecteur)" { Remove-Item -LiteralPath $path -Force }
            # La Phase 6 cree ce dossier au besoin ; celui du paquet part avec le paquet.
            [void](Remove-DirIfEmpty (Split-Path -Parent $path))
        } else {
            Invoke-Change "retrait de mcpServers.microsoft365 de $path" { Set-JsonFile -Object $config -Path $path }
        }
        $count++
    }
    $script:phaseResults['M365 MCP'] = if ($warn) { "[!] $warn" }
                                       elseif ($count -gt 0) { "[OK] Retrait du connecteur ($count fichier(s))" }
                                       else { '[OK] Absent' }
}

# --- Etape 3 : configuration Snetor (inverse de la Phase 5 et de statusline/install.ps1) ---
function Invoke-Step3-Snetor {
    Write-Step "Etape 3 - Configuration Snetor ($script:ClaudeDir)"
    if (-not (Test-Path -LiteralPath $script:ClaudeDir)) {
        Write-Ok "Aucun dossier .claude"
        $script:phaseResults['Config Snetor'] = '[OK] Absente'
        return
    }
    $done  = 0
    $warns = @()

    # 1. settings.json
    $settingsPath = Join-Path $script:ClaudeDir 'settings.json'
    $cfg = $null
    try { $cfg = Read-JsonFile $settingsPath } catch {
        Write-Warn "settings.json illisible : laisse tel quel ($_)"
        $warns += 'settings.json illisible'
    }
    if ($null -ne $cfg) {
        $removed = @(Remove-SnetorSettings $cfg)
        if ($removed.Count -eq 0) {
            Write-Info "settings.json : aucun reglage Snetor"
        } elseif ((Get-PropertyCount $cfg) -eq 0) {
            Invoke-Change "suppression de settings.json (que des reglages Snetor : $($removed -join ', '))" {
                Remove-Item -LiteralPath $settingsPath -Force
            }
            $done++
        } else {
            Invoke-Change "retrait de settings.json : $($removed -join ', ')" { Set-JsonFile -Object $cfg -Path $settingsPath }
            $done++
        }
    }

    # 2. CLAUDE.md : les lignes d'import, jamais le contenu du collab
    $claudeMd = Join-Path $script:ClaudeDir 'CLAUDE.md'
    if (Test-Path -LiteralPath $claudeMd) {
        $bom = Test-Utf8Bom $claudeMd
        $r   = Remove-SnetorClaudeMd ([System.IO.File]::ReadAllText($claudeMd))
        if ($r.Delete) {
            Invoke-Change "suppression de CLAUDE.md (cree par le deploiement, sans contenu du collab)" {
                Remove-Item -LiteralPath $claudeMd -Force
            }
            $done++
        } elseif ($r.Changed) {
            Invoke-Change "retrait des imports Snetor de CLAUDE.md" { Set-TextFileLike -Path $claudeMd -Text $r.Text -Bom $bom }
            $done++
        } else {
            Write-Info "CLAUDE.md : aucun import Snetor"
        }
    }

    # 3. Fichiers copies depuis snetor-ai-guidelines
    foreach ($rel in $script:SnetorFiles) {
        $f = Join-Path $script:ClaudeDir $rel
        if (Test-Path -LiteralPath $f) {
            Invoke-Change "suppression de $rel" { Remove-Item -LiteralPath $f -Force }
            $done++
        }
    }
    foreach ($d in @('hooks', 'output-styles')) {
        if (Remove-DirIfEmpty (Join-Path $script:ClaudeDir $d)) { Write-Info "Dossier $d vide retire" }
    }
    if (Remove-DirIfEmpty $script:ClaudeDir) { Write-Info "Dossier .claude vide retire" }

    $script:phaseResults['Config Snetor'] = if ($warns.Count -gt 0) { "[!] $($warns -join ', ')" }
                                            elseif ($done -gt 0) { "[OK] $done retrait(s)" }
                                            else { '[OK] Absente' }
}

# --- Etape 4 : Claude Code (inverse de la Phase 4) ----------------------------------------
# Suppression directe plutot que `npm uninstall -g` : Node peut deja manquer (passage
# precedent interrompu), et un paquet global n'est rien d'autre que son dossier et ses shims.
function Invoke-Step4-ClaudeCode {
    Write-Step "Etape 4 - Claude Code"
    $prefix = $script:NpmPrefix
    $ai     = Join-Path $prefix 'node_modules\@anthropic-ai'
    $done   = 0
    $notes  = @()

    # Paquet, paquets de plateforme, et restes `.claude-code-XXXX` d'une mise a jour interrompue
    $dirs = @()
    if (Test-Path -LiteralPath $ai) {
        $dirs = @(Get-ChildItem -LiteralPath $ai -Directory -Force | Where-Object {
            $_.Name -like 'claude-code*' -or $_.Name -like '.claude-code-*'
        } | ForEach-Object { $_.FullName })
    }
    foreach ($d in $dirs) {
        Invoke-Change "suppression de $d" { Remove-TreeNoFollow $d }
        $done++
    }
    if (Remove-DirIfEmpty $ai) { Write-Info "Dossier @anthropic-ai vide retire" }

    # Shims : seulement ceux qui pointent sur Claude Code
    $shims = @()
    if (Test-Path -LiteralPath $prefix) {
        $shims = @(Get-ChildItem -LiteralPath $prefix -File -Force | Where-Object {
            @('claude', 'claude.cmd', 'claude.ps1') -contains $_.Name -and
            (Select-String -LiteralPath $_.FullName -Pattern '@anthropic-ai[\\/]claude-code' -Quiet)
        } | ForEach-Object { $_.FullName })
    }
    foreach ($s in $shims) {
        Invoke-Change "suppression du shim $s" { Remove-Item -LiteralPath $s -Force }
        $done++
    }

    # .npmrc : la ligne prefix= que `npm config set prefix` a ecrite
    $npmrc = Join-Path $TargetProfile '.npmrc'
    if (Test-Path -LiteralPath $npmrc) {
        $bom = Test-Utf8Bom $npmrc
        $r   = Remove-NpmPrefixLine -Text ([System.IO.File]::ReadAllText($npmrc)) -Prefix $prefix
        if ($r.Delete) {
            Invoke-Change "suppression de .npmrc (seulement le prefix du deploiement)" { Remove-Item -LiteralPath $npmrc -Force }
            $done++
        } elseif ($r.Changed) {
            Invoke-Change "retrait de la ligne prefix= de .npmrc" { Set-TextFileLike -Path $npmrc -Text $r.Text -Bom $bom }
            $done++
        }
    }

    # PATH du collab et prefix : seulement si plus aucun autre paquet global n'y vit
    $others = @(Get-OtherGlobalPackages $prefix)
    if ($others.Count -gt 0) {
        Write-Info "Autres paquets npm globaux dans $prefix : $($others -join ', ') -> PATH et prefix conserves"
        $notes += "PATH conserv&eacute; (autres paquets npm : $($others -join ', '))"
    } else {
        $path = Remove-CollabPathEntry -Entry $prefix
        if ($path.Note) { $notes += $path.Note }
        if ($path.Removed) { $done++ }
        # Le prefix part s'il ne reste que node_modules (vide de paquets) : tout autre occupant
        # est inconnu, donc garde.
        if (Test-Path -LiteralPath $prefix) {
            $unknown = @(Get-ChildItem -LiteralPath $prefix -Force | Where-Object {
                $shims -notcontains $_.FullName -and -not ($_.PSIsContainer -and $_.Name -eq 'node_modules')
            })
            if ($unknown.Count -eq 0) {
                Invoke-Change "suppression du prefix npm $prefix (plus aucun paquet)" { Remove-TreeNoFollow $prefix }
            } else {
                Write-Info "Prefix conserve : contenu inconnu ($(@($unknown | ForEach-Object { $_.Name }) -join ', '))"
            }
        }
    }

    $script:phaseResults['Claude Code'] = if ($notes.Count -gt 0 -and $done -gt 0) { "[OK] $done retrait(s), $($notes -join ', ')" }
                                          elseif ($notes.Count -gt 0) { "[OK] Absent, $($notes -join ', ')" }
                                          elseif ($done -gt 0) { "[OK] $done retrait(s)" }
                                          else { '[OK] Absent' }
}

# Retire $Entry du PATH utilisateur du collab, par sa ruche (SetEnvironmentVariable('User')
# viserait l'admin eleve). Le type de la valeur (REG_EXPAND_SZ le plus souvent) est conserve,
# et la valeur est lue sans developper les %VAR% pour ne pas les figer.
# Rend Removed (l'entree y etait et a ete retiree) et Note (ce qui n'a pas pu etre verifie).
function Remove-CollabPathEntry {
    param([string]$Entry)
    $unverified = [PSCustomObject]@{ Removed = $false; Note = 'PATH non v&eacute;rifi&eacute;' }
    try {
        $sid = (New-Object System.Security.Principal.NTAccount($script:TargetUserFull)).Translate(
                   [System.Security.Principal.SecurityIdentifier]).Value
    } catch {
        Write-Warn "SID de $script:TargetUserFull introuvable : PATH non verifie ($_)"
        return $unverified
    }
    $key = [Microsoft.Win32.Registry]::Users.OpenSubKey("$sid\Environment", (-not $script:DryRun))
    if (-not $key) {
        Write-Warn "Ruche du collab non chargee : PATH non verifie"
        return $unverified
    }
    try {
        return (Remove-PathEntryFromKey -Key $key -Entry $Entry)
    } finally {
        $key.Close()
    }
}

# Lecture, retrait et reecriture du PATH d'une cle Environment deja ouverte
function Remove-PathEntryFromKey {
    param([Microsoft.Win32.RegistryKey]$Key, [string]$Entry)
    $absent = [PSCustomObject]@{ Removed = $false; Note = $null }
    $name = @($Key.GetValueNames() | Where-Object { $_ -eq 'Path' }) | Select-Object -First 1
    if (-not $name) { Write-Info "PATH du collab vide"; return $absent }
    $kind = $Key.GetValueKind($name)
    $raw  = [string]$Key.GetValue($name, '', [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
    $r    = Remove-PathEntry -PathValue $raw -Entry $Entry
    if (-not $r.Changed) { Write-Info "PATH du collab : $Entry absent"; return $absent }
    Invoke-Change "retrait de $Entry du PATH du collab" { $Key.SetValue($name, $r.Value, $kind) }
    return [PSCustomObject]@{ Removed = $true; Note = $null }
}

# --- Etape 5 : Claude Desktop (inverse de la Phase 3) --------------------------------------
function Invoke-Step5-Desktop {
    Write-Step "Etape 5 - Claude Desktop"
    $state = Get-ClaudeDesktopState
    $prov  = @($state.Provisioned)
    $inst  = @($state.Installed)
    # Une lecture refusee ne vaut pas absence : elle se dit, en simulation comme en vrai.
    foreach ($e in @($state.Errors)) { Write-Warn "Claude Desktop : $e" }
    $partial = if (@($state.Errors).Count -gt 0) { ', lecture partielle' } else { '' }
    if ($prov.Count -eq 0 -and $inst.Count -eq 0) {
        Write-Ok "Claude Desktop absent"
        $script:phaseResults['Claude Desktop'] = if ($partial) { "[!] Absent$partial" } else { '[OK] Absent' }
        return
    }
    # Le provisionnement d'abord : sinon Windows reinstalle le paquet au prochain compte ouvert.
    foreach ($p in $prov) {
        Invoke-Change "retrait du provisionnement $($p.PackageName)" {
            Remove-AppxProvisionedPackage -Online -PackageName $p.PackageName -ErrorAction Stop | Out-Null
        }
    }
    foreach ($p in $inst) {
        Invoke-Change "retrait de $($p.PackageFullName) pour tous les comptes" {
            Remove-AppxPackage -Package $p.PackageFullName -AllUsers -ErrorAction Stop
        }
    }
    if ($script:DryRun) {
        $status = if ($partial) { '!' } else { 'OK' }
        $script:phaseResults['Claude Desktop'] = "[$status] $($inst.Count) paquet(s), $($prov.Count) provisionnement(s)$partial"
        return
    }
    # Relecture : un paquet encore la apres coup se dit, il ne passe pas pour retire.
    $after = Get-ClaudeDesktopState
    $left  = @(@($after.Provisioned | ForEach-Object { $_.PackageName }) + @($after.Installed | ForEach-Object { $_.PackageFullName }))
    if ($left.Count -gt 0) {
        Write-Warn "Toujours present : $($left -join ', ')"
        $script:phaseResults['Claude Desktop'] = "[!] Toujours pr&eacute;sent : $($left -join ', ')"
    } elseif ($partial) {
        $script:phaseResults['Claude Desktop'] = "[!] Retir&eacute;$partial"
    } else {
        $script:phaseResults['Claude Desktop'] = '[OK] Retir&eacute; pour tous les comptes'
    }
}

# --- Etape 6 : Git (inverse de la Phase 2) --------------------------------------------------
function Invoke-Step6-Git {
    Write-Step "Etape 6 - Git for Windows"
    if ($KeepGit) {
        Write-Ok "Garde (-KeepGit)"
        $script:phaseResults['Git'] = '[OK] Gard&eacute; (-KeepGit)'
        return
    }
    $git = Get-MachineGit
    if (-not $git) {
        Write-Ok "Aucun Git installe pour la machine (un Git par utilisateur n'est jamais touche)"
        $script:phaseResults['Git'] = '[OK] Aucune installation machine'
        return
    }
    $uninstall = [string](Get-RegValue $git 'UninstallString')
    $exe = if ($uninstall -match '^\s*"([^"]+)"') { $Matches[1] } else { ($uninstall -split '\s+/')[0].Trim() }
    if (-not $exe -or -not (Test-Path -LiteralPath $exe)) { throw "desinstalleur Git introuvable ($uninstall)" }
    $version = Get-RegValue $git 'DisplayVersion'

    # Identite posee par Set-CollabGitIdentity, avec le git.exe de l'installation, avant qu'il ne
    # disparaisse. Seulement si elle vaut l'email du collab.
    $location = [string](Get-RegValue $git 'InstallLocation')
    $gitExe   = if ($location) { Join-Path $location 'cmd\git.exe' } else { $null }
    if ($gitExe -and (Test-Path -LiteralPath $gitExe)) {
        # Sans `2>$null` : sous 5.1 et Stop, cette redirection rend terminante la moindre ligne de
        # stderr. Une cle absente fait sortir git en code 1 sans rien ecrire.
        $email = & $gitExe config --global user.email
        if ($email -and $TargetEmail -and ([string]$email).Trim() -ieq $TargetEmail) {
            $gitconfig = Join-Path $TargetProfile '.gitconfig'
            Invoke-Change "retrait de user.email ($TargetEmail) du .gitconfig du collab" {
                & $gitExe config --global --unset user.email
                if ($LASTEXITCODE -ne 0) { throw "git config --unset a echoue (code $LASTEXITCODE)" }
                # Il ne reste parfois qu'un en-tete [user] vide : le fichier n'a alors plus rien du collab.
                if (Test-Path -LiteralPath $gitconfig) {
                    $rest = ([System.IO.File]::ReadAllText($gitconfig) -replace '(?m)^\s*\[user\]\s*$', '').Trim()
                    if (-not $rest) { Remove-Item -LiteralPath $gitconfig -Force }
                }
            }
        }
    }

    Invoke-Change "desinstallation de Git $version ($exe)" {
        $proc = Start-Process -FilePath $exe -ArgumentList '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES' -Wait -PassThru
        if ($proc.ExitCode -ne 0) { throw "le desinstalleur Git a retourne le code $($proc.ExitCode)" }
        # Inno Setup se recopie dans le Temp et s'y relance : le processus attendu peut rendre la
        # main avant la fin du retrait. La disparition de sa cle fait foi.
        $deadline = (Get-Date).AddSeconds(180)
        while ((Get-MachineGit) -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 2 }
        if (Get-MachineGit) { throw "Git toujours inscrit apres 180 s" }
    }
    $script:phaseResults['Git'] = "[OK] Retrait de Git $version"
}

# --- Etape 7 : Node.js (inverse de la Phase 1) ----------------------------------------------
function Invoke-Step7-NodeJS {
    Write-Step "Etape 7 - Node.js"
    if ($KeepNodeJs) {
        Write-Ok "Garde (-KeepNodeJs)"
        $script:phaseResults['Node.js'] = '[OK] Gard&eacute; (-KeepNodeJs)'
        return
    }
    $msis = @(Get-NodeMsi)
    if ($msis.Count -eq 0) {
        Write-Ok "Aucun Node.js installe par MSI"
        $script:phaseResults['Node.js'] = '[OK] Absent'
        return
    }
    foreach ($m in $msis) {
        $code    = $m.PSChildName
        $version = Get-RegValue $m 'DisplayVersion'
        Invoke-Change "desinstallation de Node.js $version ($code)" {
            $proc = Start-Process msiexec.exe -ArgumentList "/x $code /quiet /norestart" -Wait -PassThru
            # 1605 : produit deja absent ; 3010 : retrait fait, redemarrage requis
            if ($proc.ExitCode -eq 3010) { $script:RebootRequired = $true }
            elseif (@(0, 1605) -notcontains $proc.ExitCode) { throw "msiexec a retourne le code $($proc.ExitCode)" }
        }
    }
    # Signale ce que ce retrait casse, sans en faire un motif de garder Node : la decision est prise.
    $others = @(Get-OtherGlobalPackages $script:NpmPrefix)
    if ($others.Count -gt 0) {
        Write-Warn "Paquets npm globaux devenus inutilisables : $($others -join ', ')"
        $script:phaseResults['Node.js'] = "[!] Retrait de Node.js, paquets npm globaux sans Node.js : $($others -join ', ')"
    } elseif ($script:RebootRequired) {
        $script:phaseResults['Node.js'] = '[!] Retrait de Node.js, red&eacute;marrage requis'
    } else {
        $script:phaseResults['Node.js'] = '[OK] Retrait de Node.js'
    }
}

# --- Etape 8 : restes du deploiement --------------------------------------------------------
function Invoke-Step8-Remnants {
    Write-Step "Etape 8 - Restes du deploiement"
    $done = 0

    # Cache du hook az_ensure_login.py (une date d'expiration, aucun secret)
    $azDir   = Join-Path $TargetProfile '.azure-claude'
    $azCache = Join-Path $azDir '.expiration-jeton'
    if (Test-Path -LiteralPath $azCache) {
        Invoke-Change "suppression de $azCache" { Remove-Item -LiteralPath $azCache -Force }
        $done++
    }
    if (Remove-DirIfEmpty $azDir) { Write-Info "Dossier .azure-claude vide retire" }

    # Taches SnetorClaude-* laissees par un deploiement interrompu
    try {
        $service = New-Object -ComObject Schedule.Service
        $service.Connect()
        $folder = $service.GetFolder('\')
        foreach ($t in @($folder.GetTasks(1) | Where-Object { $_.Name -like 'SnetorClaude-*' } | ForEach-Object { $_.Name })) {
            Invoke-Change "suppression de la tache orpheline $t" { $folder.DeleteTask($t, 0) }
            $done++
        }
    } catch {
        Write-Warn "Taches planifiees non lisibles : $(ConvertTo-OneLine $_.Exception.Message)"
    }

    # Dossiers de telechargement du deploiement (Get-TempDir), s'il a ete interrompu
    if ($env:TEMP -and (Test-Path -LiteralPath $env:TEMP)) {
        foreach ($d in @(Get-ChildItem -LiteralPath $env:TEMP -Directory -Filter 'snetor-claude-*' -Force -ErrorAction SilentlyContinue)) {
            Invoke-Change "suppression de $($d.FullName)" { Remove-TreeNoFollow $d.FullName }
            $done++
        }
    }

    # Dossier d'echange des fenetres : scripts restes d'un passage interrompu. Le bilan le
    # recreera, et le retirera en se fermant. Le fichier de la barre d'avancement de CE passage
    # reste : la fenetre le lit encore, et l'efface elle-meme en se fermant.
    if (Test-Path -LiteralPath $script:UiDir) {
        $leftovers = @(Get-ChildItem -LiteralPath $script:UiDir -Force |
                       Where-Object { $_.FullName -ne $script:ProgressFile })
        if ($leftovers.Count -gt 0) {
            Invoke-Change "suppression de $($leftovers.Count) reste(s) dans $script:UiDir (passage interrompu)" {
                foreach ($left in $leftovers) { Remove-TreeNoFollow $left.FullName }
            }
            $done++
        }
    }
    [void](Remove-DirIfEmpty $script:UiDir)

    $script:phaseResults['Restes'] = if ($done -gt 0) { "[OK] $done retrait(s)" } else { '[OK] Aucun' }
}

# --- Etape 9 : donnees personnelles (seulement -Purge) ----------------------------------------
function Invoke-Step9-Purge {
    Write-Step "Etape 9 - Donnees personnelles (-Purge)"
    $targets = @(
        $script:ClaudeDir
        (Join-Path $TargetProfile 'AppData\Local\claude-cli-nodejs')
        (Join-Path $TargetProfile 'AppData\Roaming\Claude')
    )
    # ~/.claude.json (jeton, projets) et ses copies .backup / .tmp.*
    $targets += @(Get-ChildItem -LiteralPath $TargetProfile -File -Force -Filter '.claude.json*' -ErrorAction SilentlyContinue |
                  ForEach-Object { $_.FullName })
    # Donnees de Claude Desktop que Windows n'aurait pas retirees avec le paquet
    $pkgRoot = Join-Path $TargetProfile 'AppData\Local\Packages'
    if (Test-Path -LiteralPath $pkgRoot) {
        $targets += @(Get-ChildItem -LiteralPath $pkgRoot -Directory -Filter 'Claude_*' -Force -ErrorAction SilentlyContinue |
                      ForEach-Object { $_.FullName })
    }
    $done = 0
    foreach ($t in $targets) {
        if (-not (Test-Path -LiteralPath $t)) { continue }
        Invoke-Change "effacement de $t" { Remove-TreeNoFollow $t }
        $done++
    }
    $script:phaseResults['Donn&eacute;es personnelles'] = if ($done -gt 0) { "[OK] $done effacement(s)" } else { '[OK] Aucune' }
}

# --- Recapitulatif ---------------------------------------------------------------------------
function Show-Summary {
    param([System.Collections.Specialized.OrderedDictionary]$Results)

    $titre = if ($script:DryRun) { "SIMULATION - ce qui serait retire, rien n'a ete modifie" } else { 'Desinstallation terminee - Recapitulatif' }
    Write-Host "`n+==========================================================+" -ForegroundColor Cyan
    Write-Host   "  $titre" -ForegroundColor Cyan
    Write-Host   "+==========================================================+" -ForegroundColor Cyan

    foreach ($step in $Results.Keys) {
        Write-Host "  $(ConvertTo-LogText $Results[$step])  $(ConvertTo-LogText $step)"
    }
    if ($script:RebootRequired) {
        Write-Host "`nRedemarrage requis pour finir le retrait de Node.js." -ForegroundColor Yellow
    }
    Write-Host "`nDesinstallation Snetor Claude $(if ($script:DryRun) { 'simulee' } else { 'terminee' }) pour : $TargetUser`n" -ForegroundColor Green
}

# --- Execution principale ----------------------------------------------------------------------
if ($script:DryRun) {
    Write-Warn "SIMULATION (-WhatIf) : aucune fenetre, rien n'est modifie"
} else {
    # Rien n'est retire sans l'accord explicite du collab.
    $consent = Request-UserConsent -Seconds 120
    if ($consent -eq 'REFUSE') {
        Write-Warn "Le collab a reporte la desinstallation : rien n'a ete retire."
        exit 2
    }
    if ($consent -ne 'ACCEPT') {
        Write-Warn "Pas de reponse du collab dans le delai : rien n'a ete retire."
        exit 3
    }
    Write-Ok "Le collab a accepte la desinstallation"
}

$steps = [ordered]@{
    'Fermeture de Claude' = 'Invoke-Step1-StopClaude'
    'M365 MCP'            = 'Invoke-Step2-M365'
    'Config Snetor'       = 'Invoke-Step3-Snetor'
    'Claude Code'         = 'Invoke-Step4-ClaudeCode'
    'Claude Desktop'      = 'Invoke-Step5-Desktop'
    'Git'                 = 'Invoke-Step6-Git'
    'Node.js'             = 'Invoke-Step7-NodeJS'
    'Restes'              = 'Invoke-Step8-Remnants'
}
if ($Purge) { $steps['Donn&eacute;es personnelles'] = 'Invoke-Step9-Purge' }

# Pas de fenetre en simulation : la barre reste fermee, et Set-ProgressStep n'ecrit rien.
if (-not $script:DryRun) {
    Open-ProgressWindow -Title 'D&eacute;sinstallation de Claude AI' -DoneText 'D&eacute;sinstallation termin&eacute;e' `
        -Glyph '0xE74D' -Steps @($steps.Keys)
}

$index = 0
foreach ($step in $steps.Keys) {
    Set-ProgressStep -Index $index -State 'run'
    try { & $steps[$step] } catch {
        Write-Fail "Etape $(ConvertTo-LogText $step) echouee : $_"
        $phaseResults[$step] = '[ECHEC]'
    }
    Set-ProgressStep -Index $index -State (ConvertTo-ProgressState $phaseResults[$step])
    $index++
}
Close-ProgressWindow

Show-Summary $phaseResults

$failedPhases = @($phaseResults.Keys | Where-Object { $phaseResults[$_] -eq '[ECHEC]' })
if (-not $script:DryRun) { Show-FinalDialog -FailedPhases $failedPhases }

# Maintenir la fenetre ouverte si lancee en double-clic (hors NinjaOne). Le nom d'hote suffit
# a ecarter l'ISE : tester `$psISE`, absent en console, leverait une erreur sous StrictMode.
if (-not $isSystem -and -not $script:DryRun -and $Host.Name -eq 'ConsoleHost') {
    Write-Host "Appuyez sur une touche pour fermer ..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
}
# Code de sortie non-zero si au moins une etape a echoue : c'est ce que NinjaOne lit.
exit [int]($failedPhases.Count -gt 0)
