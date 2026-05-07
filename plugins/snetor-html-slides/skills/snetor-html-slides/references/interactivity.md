# Interactivity — Tabs, Accordion, Hover-reveal, Tooltips

Vanilla JS, no dependencies. Append the bootstrap script at the end of `<body>` after the navigation JS, before the chart bootstrap (if any).

The four components share one principle: **show less, reveal on demand.** Use them to keep slides under 30 words of body text while preserving depth.

---

## Bootstrap script (always include if the deck uses any of these components)

```javascript
// === TABS ===
document.querySelectorAll('.tab-slide').forEach((host) => {
  const tabs = host.querySelectorAll('.tab');
  const panels = host.querySelectorAll('.panel');
  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      tabs.forEach((t) => t.classList.toggle('active', t === tab));
      panels.forEach((p) => p.classList.toggle('active', p.id === target));
    });
  });
});

// === ACCORDION ===
document.querySelectorAll('.acc-trigger').forEach((trigger) => {
  trigger.addEventListener('click', () => {
    const expanded = trigger.getAttribute('aria-expanded') === 'true';
    trigger.setAttribute('aria-expanded', String(!expanded));
    const panel = trigger.nextElementSibling;
    if (panel) panel.hidden = expanded;
  });
});

// === TOOLTIPS ===
document.querySelectorAll('[data-tooltip]').forEach((el) => {
  if (!el.hasAttribute('tabindex')) el.tabIndex = 0;
  el.classList.add('has-tooltip');
});
```

Hover-reveal cards are pure CSS — no JS needed.

---

## Tabs (alternative to splitting one comparison across 3 slides)

```html
<div class="tab-slide">
  <div class="tabs" role="tablist">
    <button class="tab active" data-tab="opt1" role="tab">Option A</button>
    <button class="tab" data-tab="opt2" role="tab">Option B</button>
    <button class="tab" data-tab="opt3" role="tab">Option C</button>
  </div>
  <div class="tab-panels">
    <div class="panel active" id="opt1" role="tabpanel">
      <!-- content for option A — can include cards, charts, lists -->
    </div>
    <div class="panel" id="opt2" role="tabpanel">
      <!-- content for option B -->
    </div>
    <div class="panel" id="opt3" role="tabpanel">
      <!-- content for option C -->
    </div>
  </div>
</div>
```

Use when comparing 2-4 options where the audience may want to dive into any. Keeps the slide count down.

---

## Accordion (details on demand)

```html
<div class="accordion">
  <div>
    <button class="acc-trigger" aria-expanded="false">Risk #1 — Vendor lock-in</button>
    <div class="acc-panel" hidden>Detailed mitigation: dual-vendor architecture for core ML pipelines, exit clauses in MSAs.</div>
  </div>
  <div>
    <button class="acc-trigger" aria-expanded="false">Risk #2 — Data residency</button>
    <div class="acc-panel" hidden>EU regions only for customer data; LLM inference behind private endpoint.</div>
  </div>
</div>
```

Use for risk lists, FAQs, technical caveats — anything the audience may want to expand selectively rather than read inline.

---

## Hover-reveal Card (punchline + reveal)

```html
<article class="card reveal animate d1">
  <span class="metric counter" data-target="88" data-suffix="%">0%</span>
  <h3>Visible label</h3>
  <p>Short visible context.</p>
  <div class="reveal-back">
    <h3>Detail on hover</h3>
    <p>Extended explanation visible only when the card is hovered or focused.</p>
  </div>
</article>
```

The `+` icon top-right rotates 45° on hover, signaling interactivity. The back panel slides up from below.

Use sparingly — max 1 row of reveal cards per deck. If every card needs a back, use accordion instead.

---

## Tooltips (technical terms / acronyms)

```html
<p>We use <span data-tooltip="Retrieval-Augmented Generation: combine a search index with an LLM to ground answers in your data.">RAG</span> for the knowledge base, with <span data-tooltip="Hybrid search: dense vectors + BM25 keyword matching.">hybrid search</span>.</p>
```

The bootstrap script auto-adds `tabindex="0"` and the `has-tooltip` class. Tooltips appear on hover AND on keyboard focus (accessible).

Limit to 2-3 tooltips per slide. If you need more, the slide is too dense — split it or move detail into accordion.

---

## When to use which

| Situation | Component |
|---|---|
| Compare 3 cloud providers | `tab-slide` |
| 5 risks with details | `accordion` |
| 3 KPI cards where each has a story | `card.reveal` (or just put the story on the back of the deck verbally) |
| Acronym or term the audience may not know | `data-tooltip` |
| Dense text the audience might re-read later | accordion + speaker delivers the gist verbally |
