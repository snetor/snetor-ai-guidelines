#!/usr/bin/env bash
# Claude Code status line — works on Windows (Git Bash) and Linux/macOS
input=$(cat)

# --- Extract fields from JSON ---
model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
ctx_input=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // empty')
ctx_total=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
five_hour_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')

# --- ANSI color helpers ---
C_RESET='\033[0m'
C_DIM='\033[2m'
C_CYAN='\033[38;5;39m'
C_YELLOW='\033[38;5;220m'
C_GREEN='\033[38;5;83m'
C_ORANGE='\033[38;5;208m'
C_RED='\033[38;5;196m'
C_BLUE='\033[38;5;69m'
C_MAGENTA='\033[38;5;171m'
C_GRAY='\033[38;5;245m'
C_WHITE='\033[38;5;255m'
SEP="$(printf "${C_GRAY} | ${C_RESET}")"

# --- Shorten path: replace Windows-style home or Unix home with ~ ---
short_cwd="$cwd"
# Normalize backslashes to forward slashes
short_cwd="${short_cwd//\\//}"
# Try stripping $HOME (Git Bash exposes Unix-style home)
if [ -n "$HOME" ]; then
  home_unix="${HOME//\\//}"
  short_cwd="${short_cwd/#$home_unix/\~}"
fi
# Keep only the last 2 path components if still long
if [ "${#short_cwd}" -gt 40 ]; then
  short_cwd="…/$(echo "$short_cwd" | sed 's|.*/\([^/]*/[^/]*\)$|\1|')"
fi

# --- Git branch ---
git_branch=""
if [ -n "$cwd" ]; then
  git_branch=$(GIT_OPTIONAL_LOCKS=0 git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null)
fi

# --- Build a mini progress bar (10 chars wide) ---
# Usage: make_bar <percentage_int> <filled_color> <empty_color>
make_bar() {
  local pct=$1
  local fc=$2
  local ec=$3
  local width=10
  local filled=$(( pct * width / 100 ))
  [ "$filled" -gt "$width" ] && filled=$width
  local empty=$(( width - filled ))
  local bar=""
  local i
  for (( i=0; i<filled; i++ )); do bar="${bar}#"; done
  for (( i=0; i<empty; i++ )); do bar="${bar}-"; done
  printf "${fc}${bar:0:$filled}${ec}${bar:$filled}${C_RESET}"
}

# --- Context window section ---
ctx_part=""
if [ -n "$used_pct" ]; then
  used_int=$(printf '%.0f' "$used_pct")

  # Choose color based on usage
  if [ "$used_int" -ge 80 ]; then
    bar_color="$C_RED"
    pct_color="$C_RED"
  elif [ "$used_int" -ge 50 ]; then
    bar_color="$C_ORANGE"
    pct_color="$C_ORANGE"
  else
    bar_color="$C_GREEN"
    pct_color="$C_GREEN"
  fi

  bar=$(make_bar "$used_int" "$bar_color" "$C_GRAY")

  # Show tokens if available (in k)
  if [ -n "$ctx_input" ] && [ -n "$ctx_total" ] && [ "$ctx_total" -gt 0 ]; then
    ctx_k=$(( ctx_input / 1000 ))
    total_k=$(( ctx_total / 1000 ))
    ctx_part="$(printf "${C_WHITE}ctx${C_RESET} ${bar} ${pct_color}%d%%${C_RESET} ${C_GRAY}(%dk/%dk)${C_RESET}" "$used_int" "$ctx_k" "$total_k")"
  else
    ctx_part="$(printf "${C_WHITE}ctx${C_RESET} ${bar} ${pct_color}%d%%${C_RESET}" "$used_int")"
  fi
fi

# --- 5-hour rate limit section ---
rate_part=""
if [ -n "$five_hour_pct" ]; then
  rate_int=$(printf '%.0f' "$five_hour_pct")

  if [ "$rate_int" -ge 80 ]; then
    rbar_color="$C_RED"
    rpct_color="$C_RED"
  elif [ "$rate_int" -ge 50 ]; then
    rbar_color="$C_ORANGE"
    rpct_color="$C_ORANGE"
  else
    rbar_color="$C_BLUE"
    rpct_color="$C_BLUE"
  fi

  rbar=$(make_bar "$rate_int" "$rbar_color" "$C_GRAY")
  rate_part="$(printf "${C_WHITE}5h${C_RESET} ${rbar} ${rpct_color}%d%%${C_RESET}" "$rate_int")"
fi

# --- Assemble parts ---
parts=()

# Model name
parts+=("$(printf "${C_CYAN}%s${C_RESET}" "$model")")

# Directory
parts+=("$(printf "${C_YELLOW}%s${C_RESET}" "$short_cwd")")

# Git branch
if [ -n "$git_branch" ]; then
  parts+=("$(printf "${C_MAGENTA}git:%s${C_RESET}" "$git_branch")")
fi

# Context window
if [ -n "$ctx_part" ]; then
  parts+=("$ctx_part")
fi

# 5-hour rate limit
if [ -n "$rate_part" ]; then
  parts+=("$rate_part")
fi

# --- Join with separator ---
result=""
for part in "${parts[@]}"; do
  if [ -z "$result" ]; then
    result="$part"
  else
    result="${result}${SEP}${part}"
  fi
done

printf "%b\n" "$result"
