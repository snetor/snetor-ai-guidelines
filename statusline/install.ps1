<#
.SYNOPSIS
    Installe la status line Snetor dans Claude Code.
.DESCRIPTION
    Copie statusline-command.js dans ~/.claude/ et injecte la config
    statusLine dans ~/.claude/settings.json avec le chemin absolu correct.
#>

$ErrorActionPreference = "Stop"

$claudeDir    = "$env:USERPROFILE\.claude"
$scriptSrc    = Join-Path $PSScriptRoot "statusline-command.js"
$scriptDest   = Join-Path $claudeDir "statusline-command.js"
$settingsFile = Join-Path $claudeDir "settings.json"

# 1. Copier le script
Copy-Item $scriptSrc $scriptDest -Force
Write-Host "Copied statusline-command.js to $claudeDir"

# 2. Lire ou initialiser settings.json
if (Test-Path $settingsFile) {
    $raw      = Get-Content $settingsFile -Raw -Encoding utf8
    $settings = $raw | ConvertFrom-Json
} else {
    $settings = [PSCustomObject]@{}
}

# 3. Injecter la config statusLine avec le chemin absolu correct
$jsPath = $scriptDest -replace '\\', '/'
$statusLineConfig = [PSCustomObject]@{
    type            = "command"
    command         = "node $jsPath"
    padding         = 1
    refreshInterval = 5
}
$settings | Add-Member -MemberType NoteProperty -Name "statusLine" -Value $statusLineConfig -Force

# 4. Sauvegarder
$settings | ConvertTo-Json -Depth 10 | Set-Content $settingsFile -Encoding utf8
Write-Host "settings.json updated. Status line active at next Claude Code restart."
