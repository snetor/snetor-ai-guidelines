#!/usr/bin/env node

const fs = require("fs");
const { execSync } = require("child_process");

const ESC = "\x1b[";
const c = {
  reset: ESC + "0m",
  gray: ESC + "38;5;245m",
  white: ESC + "38;5;255m",
  cyan: ESC + "38;5;39m",
  yellow: ESC + "38;5;220m",
  green: ESC + "38;5;83m",
  orange: ESC + "38;5;208m",
  red: ESC + "38;5;196m",
  blue: ESC + "38;5;69m",
  magenta: ESC + "38;5;171m",
};

function colorForPct(pct, normal = c.green) {
  const n = Number(pct) || 0;
  if (n >= 85) return c.red;
  if (n >= 60) return c.orange;
  return normal;
}

function bar(pct, color) {
  const safe = Math.max(0, Math.min(100, Math.round(Number(pct) || 0)));
  const width = 12;
  const filled = Math.floor((safe * width) / 100);
  return `${color}${"█".repeat(filled)}${c.gray}${"░".repeat(width - filled)}${c.reset}`;
}

function fmtTokens(n) {
  n = Number(n) || 0;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${Math.round(n / 1000)}k`;
  return String(n);
}

function fmtReset(value) {
  if (!value) return null;

  let date = null;

  if (typeof value === "number") {
    date = new Date(value > 10_000_000_000 ? value : value * 1000);
  } else if (typeof value === "string") {
    date = new Date(value);
  }

  if (!date || isNaN(date.getTime())) return null;

  return date.toLocaleTimeString("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function shortPath(p) {
  if (!p) return "";
  let out = p.replaceAll("\\", "/");

  const home = (process.env.USERPROFILE || "").replaceAll("\\", "/");
  if (home && out.toLowerCase().startsWith(home.toLowerCase())) {
    out = "~" + out.slice(home.length);
  }

  if (out.length > 48) {
    const parts = out.split("/").filter(Boolean);
    if (parts.length >= 2) {
      out = `…/${parts.at(-2)}/${parts.at(-1)}`;
    }
  }

  return out;
}

function gitBranch(cwd) {
  try {
    return execSync("git symbolic-ref --short HEAD", {
      cwd,
      stdio: ["ignore", "pipe", "ignore"],
      encoding: "utf8",
      timeout: 500,
    }).trim();
  } catch {
    return "";
  }
}

try {
  let raw = fs.readFileSync(0, "utf8");
  // Strip a leading UTF-8 BOM (Windows can prepend one to the piped JSON,
  // which would otherwise make JSON.parse throw "Unexpected token ﻿").
  if (raw.charCodeAt(0) === 0xfeff) raw = raw.slice(1);

  if (!raw.trim()) {
    console.log(`${c.green}Claude statusline OK${c.reset}`);
    process.exit(0);
  }

  const d = JSON.parse(raw);

  const model = d?.model?.display_name || "Claude";
  const cwdRaw = d?.workspace?.current_dir || d?.cwd || process.cwd();
  const cwd = shortPath(cwdRaw);
  const branch = gitBranch(cwdRaw);

  // ---------- CONTEXT ----------
  const ctx = d?.context_window || {};

  const inputTokens = Number(ctx.total_input_tokens || 0);
  const outputTokens = Number(ctx.total_output_tokens || 0);

  const usedTokens =
    Number(ctx.used_tokens) ||
    Number(ctx.total_tokens) ||
    Number(ctx.current_usage?.total_tokens) ||
    Number(ctx.current_usage?.input_tokens || 0) +
      Number(ctx.current_usage?.output_tokens || 0) ||
    inputTokens + outputTokens;

  const totalTokens =
    Number(ctx.effective_context_window) ||
    Number(ctx.context_window_size) ||
    1_000_000;

  const pct =
    ctx.used_percentage !== undefined && ctx.used_percentage !== null
      ? Math.round(Number(ctx.used_percentage))
      : Math.round((usedTokens / totalTokens) * 100);

  // ---------- RATE LIMIT ----------
  const five = d?.rate_limits?.five_hour || {};
  const fivePct = five.used_percentage;

  const reset =
    fmtReset(five.reset_at) ||
    fmtReset(five.resets_at) ||
    fmtReset(five.reset_time) ||
    fmtReset(five.window_reset_at) ||
    null;

  // ---------- BUILD ----------
  const parts = [];

  parts.push(`${c.cyan}${model}${c.reset}`);

  if (cwd) parts.push(`${c.yellow}${cwd}${c.reset}`);

  if (branch) parts.push(`${c.magenta}git:${branch}${c.reset}`);

  const ctxColor = colorForPct(pct);

  parts.push(
    `${c.white}ctx${c.reset} ${bar(pct, ctxColor)} ${ctxColor}${pct}%${c.reset} ${c.gray}(${fmtTokens(
      usedTokens
    )}/${fmtTokens(totalTokens)} tok)${c.reset}`
  );

  if (fivePct !== undefined && fivePct !== null) {
    const r = Math.round(Number(fivePct));
    const rc = colorForPct(r, c.blue);

    let rate = `${c.white}5h${c.reset} ${bar(r, rc)} ${rc}${r}%${c.reset}`;

    if (reset) {
      rate += ` ${c.gray}reset ${reset}${c.reset}`;
    }

    parts.push(rate);
  }

  console.log(parts.join(`${c.gray} | ${c.reset}`));
  process.exit(0);
} catch (e) {
  console.log(`${c.red}Claude statusline error${c.reset}`);
  process.exit(0);
}
