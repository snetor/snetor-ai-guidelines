# Presenter Mode — Shortcuts & Speaker Notes

Five keyboard shortcuts for live presentation, plus a speaker notes pattern. All vanilla JS, ~80 lines total. Append the bootstrap script after the navigation JS, before chart bootstrap.

---

## Keyboard shortcuts

| Key | Action |
|---|---|
| `F` | Toggle fullscreen (Fullscreen API) |
| `O` | Toggle overview — clickable grid of all slides |
| `?` | Toggle shortcuts modal |
| `N` | Toggle speaker notes overlay (reads `<aside class="notes">` of active slide) |
| `T` | Start / pause mini-timer (bottom-left) |
| `Esc` | Close any active overlay |

`F`, `O`, `?`, `N`, `T` are blocked while typing in inputs or pressing inside `.tab` / `.acc-trigger`. The standard nav (`←`, `→`, `Space`, `PageUp`, `PageDown`, `Home`, `End`) continues to work.

---

## Speaker notes pattern

```html
<section class="slide">
  <header class="brand"><!-- ... --></header>
  <div class="body"><!-- ... --></div>
  <aside class="notes">
    Speaker notes for this slide. Backstory, numbers, anecdote.
    Hidden by default. Press N to show.
  </aside>
  <footer class="footer"><!-- ... --></footer>
</section>
```

The `<aside class="notes">` is `display:none` by default. The overlay reads its content when `N` is toggled.

---

## Required DOM additions

These elements must exist somewhere in `<body>` (the bootstrap script auto-injects them if missing, but it's cleaner to include them in the template):

```html
<!-- Overview grid (auto-populated) -->
<div class="overview-grid" id="overview-grid" aria-hidden="true"></div>

<!-- Shortcuts modal -->
<div class="shortcuts-modal" id="shortcuts-modal" aria-hidden="true">
  <div class="panel">
    <h3>Keyboard shortcuts</h3>
    <dl>
      <dt>← →</dt><dd>Previous / next slide</dd>
      <dt>Space</dt><dd>Next slide</dd>
      <dt>Home / End</dt><dd>First / last slide</dd>
      <dt>F</dt><dd>Toggle fullscreen</dd>
      <dt>O</dt><dd>Slide overview</dd>
      <dt>N</dt><dd>Speaker notes</dd>
      <dt>T</dt><dd>Timer</dd>
      <dt>?</dt><dd>This help</dd>
      <dt>Esc</dt><dd>Close overlay</dd>
    </dl>
  </div>
</div>

<!-- Notes overlay (filled per-slide) -->
<div class="notes-overlay" id="notes-overlay" aria-hidden="true">
  <span class="label">Speaker notes</span>
  <div class="content"></div>
</div>

<!-- Timer display -->
<div class="timer-display" id="timer-display" aria-hidden="true">00:00</div>
```

---

## Bootstrap script

Append once after the navigation JS:

```javascript
// === FULLSCREEN ===
function toggleFullscreen() {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen();
  else document.exitFullscreen();
}

// === OVERVIEW ===
const overviewEl = document.getElementById('overview-grid');
function buildOverview() {
  overviewEl.innerHTML = '';
  slides.forEach((slide, i) => {
    const thumb = document.createElement('button');
    thumb.type = 'button';
    thumb.className = 'overview-thumb' + (i === current ? ' current' : '');
    const heading = slide.querySelector('h1, h2');
    const body = slide.querySelector('.body');
    thumb.innerHTML = `
      <span class="num">${String(i + 1).padStart(2, '0')}</span>
      <span class="title">${heading ? heading.textContent.slice(0, 60) : 'Slide ' + (i + 1)}</span>
      <span class="preview">${body ? body.textContent.replace(/\s+/g, ' ').trim().slice(0, 90) : ''}</span>
    `;
    thumb.addEventListener('click', () => {
      show(i);
      toggleOverview(false);
    });
    overviewEl.appendChild(thumb);
  });
}
function toggleOverview(force) {
  const next = typeof force === 'boolean' ? force : !overviewEl.classList.contains('active');
  if (next) buildOverview();
  overviewEl.classList.toggle('active', next);
  overviewEl.setAttribute('aria-hidden', String(!next));
}

// === SHORTCUTS MODAL ===
const shortcutsEl = document.getElementById('shortcuts-modal');
function toggleShortcuts(force) {
  const next = typeof force === 'boolean' ? force : !shortcutsEl.classList.contains('active');
  shortcutsEl.classList.toggle('active', next);
  shortcutsEl.setAttribute('aria-hidden', String(!next));
}
shortcutsEl.addEventListener('click', (e) => { if (e.target === shortcutsEl) toggleShortcuts(false); });

// === SPEAKER NOTES ===
const notesEl = document.getElementById('notes-overlay');
const notesContentEl = notesEl.querySelector('.content');
function refreshNotes() {
  const note = slides[current].querySelector('.notes');
  notesContentEl.textContent = note ? note.textContent.trim() : '(No speaker notes for this slide.)';
}
function toggleNotes(force) {
  const next = typeof force === 'boolean' ? force : !notesEl.classList.contains('active');
  if (next) refreshNotes();
  notesEl.classList.toggle('active', next);
  notesEl.setAttribute('aria-hidden', String(!next));
}

// === TIMER ===
const timerEl = document.getElementById('timer-display');
let timerStart = null;
let timerElapsed = 0;
let timerHandle = null;
let timerRunning = false;
function formatTime(ms) {
  const total = Math.floor(ms / 1000);
  const m = String(Math.floor(total / 60)).padStart(2, '0');
  const s = String(total % 60).padStart(2, '0');
  return `${m}:${s}`;
}
function tickTimer() {
  if (!timerRunning) return;
  const ms = timerElapsed + (Date.now() - timerStart);
  timerEl.textContent = formatTime(ms);
}
function toggleTimer() {
  if (!timerEl.classList.contains('active')) {
    timerEl.classList.add('active');
    timerEl.classList.remove('paused');
    timerStart = Date.now();
    timerRunning = true;
    timerHandle = setInterval(tickTimer, 500);
    return;
  }
  if (timerRunning) {
    timerElapsed += Date.now() - timerStart;
    timerRunning = false;
    timerEl.classList.add('paused');
    clearInterval(timerHandle);
  } else {
    timerStart = Date.now();
    timerRunning = true;
    timerEl.classList.remove('paused');
    timerHandle = setInterval(tickTimer, 500);
  }
}

// === KEYBOARD ===
document.addEventListener('keydown', (event) => {
  if (event.target.closest && event.target.closest('input, textarea, .tab, .acc-trigger, .check-card')) return;
  const k = event.key;
  if (k === 'Escape') {
    toggleOverview(false); toggleShortcuts(false); toggleNotes(false);
    return;
  }
  if (k === 'f' || k === 'F') { event.preventDefault(); toggleFullscreen(); return; }
  if (k === 'o' || k === 'O') { event.preventDefault(); toggleOverview(); return; }
  if (k === 'n' || k === 'N') { event.preventDefault(); toggleNotes(); return; }
  if (k === 't' || k === 'T') { event.preventDefault(); toggleTimer(); return; }
  if (k === '?') { event.preventDefault(); toggleShortcuts(); return; }
});

// Refresh notes overlay if it's open when slide changes — patch into show():
const originalShow = show;
show = function(index) {
  originalShow(index);
  if (notesEl.classList.contains('active')) refreshNotes();
};
```

---

## Notes on integration

- The `show = function(index)` reassignment patches the existing nav `show()` so notes auto-refresh on slide change. Place this script AFTER the navigation JS that defines `show`.
- The required DOM elements (`#overview-grid`, `#shortcuts-modal`, `#notes-overlay`, `#timer-display`) should be added directly to the `<body>`, after the `<main class="deck">` and `<nav class="nav">` blocks.
- The shortcuts modal includes the standard nav keys too — keep the list in sync if you add new shortcuts.
