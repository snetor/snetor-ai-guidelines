# Claude Code status line (Windows / PowerShell 5.1)
# Reads JSON from stdin, prints a single colored line:
#   <model> | <cwd> | git:<branch> | ctx <bar> NN% (Xk/Yk) | 5h <bar> NN%

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'SilentlyContinue'

$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) {
    [Console]::Out.WriteLine("Claude statusline OK")
    exit 0
}

try {
    $d = $raw | ConvertFrom-Json
} catch {
    [Console]::Out.WriteLine("Claude statusline JSON error")
    exit 0
}

$model = if ($d.model.display_name) { $d.model.display_name } else { 'Claude' }
$cwd = if ($d.workspace.current_dir) { $d.workspace.current_dir } else { $d.cwd }

$usedPct = $d.context_window.used_percentage
$ctxIn = $d.context_window.total_input_tokens
$ctxOut = $d.context_window.total_output_tokens
$ctxTot = $d.context_window.effective_context_window
$fiveH = $d.rate_limits.five_hour.used_percentage

$ESC = [char]27
$RESET   = "$ESC[0m"
$CYAN    = "$ESC[38;5;39m"
$YELLOW  = "$ESC[38;5;220m"
$GREEN   = "$ESC[38;5;83m"
$ORANGE  = "$ESC[38;5;208m"
$RED     = "$ESC[38;5;196m"
$BLUE    = "$ESC[38;5;69m"
$MAGENTA = "$ESC[38;5;171m"
$GRAY    = "$ESC[38;5;245m"
$WHITE   = "$ESC[38;5;255m"
$SEP     = "$GRAY | $RESET"

# Shorten cwd: replace home with ~, keep last 2 segments if still long
$short = ($cwd -as [string]) -replace '\\', '/'
if ($env:USERPROFILE) {
    $home_unix = $env:USERPROFILE -replace '\\', '/'
    if ($short -and $short.ToLower().StartsWith($home_unix.ToLower())) {
        $short = '~' + $short.Substring($home_unix.Length)
    }
}

if ($short -and $short.Length -gt 40) {
    $segs = $short.Split('/') | Where-Object { $_ }
    if ($segs.Count -ge 2) {
        $short = "$([char]0x2026)/" + $segs[-2] + '/' + $segs[-1]
    }
}

# Git branch (safe, silent on failure)
$branch = $null
if ($cwd -and (Test-Path -LiteralPath $cwd)) {
    $insideGit = & git -C "$cwd" rev-parse --is-inside-work-tree 2>$null
    if ($LASTEXITCODE -eq 0 -and $insideGit -eq "true") {
        $branch = & git -C "$cwd" symbolic-ref --short HEAD 2>$null
        if ($LASTEXITCODE -ne 0) {
            $branch = $null
        }
    }
}

function New-Bar {
    param([int]$pct, [string]$fc)

    $w = 10
    $safePct = [Math]::Max(0, [Math]::Min($pct, 100))
    $f = [Math]::Min([Math]::Floor($safePct * $w / 100.0), $w)
    $e = $w - $f

    $fill = '#' * $f
    $blank = '-' * $e

    return "$fc$fill$GRAY$blank$RESET"
}

# Context section
$ctxPart = $null
if ($null -ne $usedPct) {
    $u = [int][Math]::Round([double]$usedPct)

    if ($u -ge 80) {
        $c = $RED
    } elseif ($u -ge 50) {
        $c = $ORANGE
    } else {
        $c = $GREEN
    }

    $bar = New-Bar -pct $u -fc $c

    if ($null -ne $ctxIn -and $null -ne $ctxTot -and [int]$ctxTot -gt 0) {
        $ck = [int][Math]::Floor([int]$ctxIn / 1000)
        $tk = [int][Math]::Floor([int]$ctxTot / 1000)
        $ctxPart = "${WHITE}ctx${RESET} $bar ${c}${u}%${RESET} ${GRAY}(${ck}k/${tk}k)${RESET}"
    } else {
        $ctxPart = "${WHITE}ctx${RESET} $bar ${c}${u}%${RESET}"
    }
}

# 5-hour rate limit section
$ratePart = $null
if ($null -ne $fiveH) {
    $r = [int][Math]::Round([double]$fiveH)

    if ($r -ge 80) {
        $rc = $RED
    } elseif ($r -ge 50) {
        $rc = $ORANGE
    } else {
        $rc = $BLUE
    }

    $rbar = New-Bar -pct $r -fc $rc
    $ratePart = "${WHITE}5h${RESET} $rbar ${rc}${r}%${RESET}"
}

$parts = @()
$parts += "${CYAN}${model}${RESET}"

if ($short) {
    $parts += "${YELLOW}${short}${RESET}"
}

if ($branch) {
    $parts += "${MAGENTA}git:${branch}${RESET}"
}

if ($ctxPart) {
    $parts += $ctxPart
}

if ($ratePart) {
    $parts += $ratePart
}

[Console]::Out.WriteLine(($parts -join $SEP))
exit 0
