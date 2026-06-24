# Refonte snetor-html-slides — wizard, thèmes & anti-surcharge — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Doter le skill `snetor-html-slides` d'un wizard d'intake, d'un thème de deck clair/foncé avec slides d'accent dans les deux sens, de 5 archétypes aérés, et de garde-fous anti-surcharge stricts — sans casser aucun composant existant.

**Architecture:** Approche **additive** (spec §1). On n'édite ni ne supprime aucune règle CSS existante : on **ajoute** un calque thème scopé `.deck.theme-dark .slide:not(.cover):not(.light)`, le CSS des nouveaux archétypes, les patterns HTML correspondants, et on réécrit uniquement des sections d'instructions de `SKILL.md`. Le `.light` est un simple « escape hatch » du thème foncé (aucune règle propre nécessaire).

**Tech Stack:** HTML/CSS/JS vanilla, Raleway (Google Fonts), Phosphor Icons + Chart.js via CDN (inchangé). Aucune nouvelle dépendance.

## Global Constraints

- **Non-régression totale** : aucune règle CSS existante de `references/css-system.md` n'est éditée ou supprimée. Tout est ajouté. Critère vérifiable : `git diff` de `css-system.md` = insertions uniquement (aucune ligne existante modifiée hors ajout en fin de bloc/section).
- **Animations & composants intacts** : `rise`, `growBar`, `growLine`, `growPath`, `pulseDot`, `fadeScale`, `checkPop`, `marqueeScroll` ; `gantt`/`.g-today`, `journey`, `flow`, `path`, `product-grid`, `bento`, `marquee`, `spotlight`, `chart-card` + lazy-init, presenter mode, i18n, nav clavier, responsive, print.
- **Tokens de couleur** : réutiliser les variables existantes (`--green`, `--navy`, `--pastel`, `--green-20`, `--muted`, `--subtle`, `--border`, `--blue-green`, `--emerald`). Ne pas introduire de nouvelle couleur en dur.
- **Thème par défaut** : `theme-light` (implicite). Un deck sans classe de thème reste strictement identique à aujourd'hui.
- **Contrat thème foncé** : sur slide foncée, n'utiliser que la palette « dark-safe » (`.dark-card`, `.cost`, `.chart-card`, `.brick`, `.foundation`, `.ph-icon`, `.tab`, `.spotlight-card`, `.big-message`, archétypes `section-divider`/`quote`/`big-number`/`closing`). Les composants « light-card » (`fact-card`, `provider-card`, `mini-table`, `timeline`, `check-card`, `step`, `loss-item`, `tradeoff-card`, `product-card`, `agenda`) sont prévus pour slides claires (ou sur une slide `.light`).
- **Langue** : contenu des exemples et du deck de démo en français.

---

## File Structure

| Action | Fichier | Responsabilité |
|--------|---------|----------------|
| Modifier | `plugins/snetor-skills/skills/snetor-html-slides/references/css-system.md` | + calque thème (`theme-dark`, contrat `.light`), + CSS des 5 archétypes (Tasks 1-2) |
| Modifier | `plugins/snetor-skills/skills/snetor-html-slides/references/components.md` | + patterns HTML des 5 archétypes + exemples thème/accent (Task 3) |
| Créer | `plugins/snetor-skills/skills/snetor-html-slides/examples/theme-demo.html` | deck de démo / non-régression visuelle (Task 4) |
| Modifier | `plugins/snetor-skills/skills/snetor-html-slides/SKILL.md` | wizard Step 1 (Task 5), guidance thème/archétypes/accent + règles (Task 6), garde-fous anti-surcharge (Task 7) |

Ordre d'exécution : CSS d'abord (1-2), puis patterns (3), puis deck de démo (4 = point de validation visuelle avec Clément), puis les 3 tâches d'instructions `SKILL.md` (5-7).

---

## Task 1 : Calque thème de deck (`theme-dark` + escape hatch `.light`)

**Files:**
- Modify: `plugins/snetor-skills/skills/snetor-html-slides/references/css-system.md` (ajout en fin du bloc CSS, juste avant la ligne `/* RESPONSIVE */`)

**Interfaces:**
- Produces (classes consommées par les tâches suivantes et les decks) :
  - `.deck.theme-dark` — pose le thème foncé sur tout le deck.
  - `.deck.theme-light` — défaut (implicite, aucune règle : documentaire).
  - `.slide.light` — opte une slide hors du thème foncé (accent clair), symétrique de `.slide.dark`.

- [ ] **Step 1 : Ajouter le bloc « DECK THEME LAYER » dans `css-system.md`**

Insérer ce bloc **dans le ``` ```css ``` block**, juste avant le commentaire `/* RESPONSIVE */` (donc avant `@media (max-width: 980px)`), sans toucher aux règles existantes :

```css
/* === DECK THEME LAYER (additif — spec §1) ===
   theme-light (défaut, implicite) = styling de base inchangé.
   theme-dark = chaque slide de contenu foncée par défaut, en réutilisant la
   cascade .dark existante (dupliquée ici en sélecteurs scopés, sans éditer
   les règles .dark d'origine).
   .light sur une slide = escape hatch : exclut la slide du thème foncé via
   :not(.light), elle retombe sur le styling clair de base. Aucun style propre. */

.deck.theme-dark .slide:not(.cover):not(.light) {
  background: linear-gradient(135deg, var(--navy), var(--blue-green) 72%, var(--green));
  color: white;
}
.deck.theme-dark .slide:not(.cover):not(.light) h2,
.deck.theme-dark .slide:not(.cover):not(.light) h3,
.deck.theme-dark .slide:not(.cover):not(.light) p,
.deck.theme-dark .slide:not(.cover):not(.light) li { color: white; }
.deck.theme-dark .slide:not(.cover):not(.light) .logo { background-image: var(--logo-reversed); }
.deck.theme-dark .slide:not(.cover):not(.light) .eyebrow { color: rgba(255,255,255,.82); }
.deck.theme-dark .slide:not(.cover):not(.light) .eyebrow::before { background: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .statement { color: white; border-left-color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .statement strong { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .metric { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .footer { color: rgba(255,255,255,.72); }
.deck.theme-dark .slide:not(.cover):not(.light) .source-note { color: rgba(255,255,255,.6); }
.deck.theme-dark .slide:not(.cover):not(.light) .source-note a { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .progress span { background: rgba(255,255,255,.28); }
.deck.theme-dark .slide:not(.cover):not(.light) .progress span.on { background: var(--pastel); }
/* dark-safe components inside a theme-dark slide (mirror existing .dark variants) */
.deck.theme-dark .slide:not(.cover):not(.light) .chart-card { background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.24); box-shadow: none; }
.deck.theme-dark .slide:not(.cover):not(.light) .chart-card h3 { color: white; }
.deck.theme-dark .slide:not(.cover):not(.light) .chart-card .source-note { color: rgba(255,255,255,.7); }
.deck.theme-dark .slide:not(.cover):not(.light) .chart-card .source-note a { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .ph-icon { color: var(--pastel); background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.18); }
.deck.theme-dark .slide:not(.cover):not(.light) .ph-icon.navy { color: var(--white); background: rgba(255,255,255,.10); border-color: rgba(255,255,255,.22); }
.deck.theme-dark .slide:not(.cover):not(.light) .tab { color: rgba(255,255,255,.7); }
.deck.theme-dark .slide:not(.cover):not(.light) .tab:hover,
.deck.theme-dark .slide:not(.cover):not(.light) .tab.active { color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .tab.active { border-bottom-color: var(--pastel); }
.deck.theme-dark .slide:not(.cover):not(.light) .tabs { border-bottom-color: rgba(255,255,255,.18); }
```

- [ ] **Step 2 : Documenter les classes en tête du fichier**

Sous la section « Color Tokens », ajouter une courte sous-section « Deck themes » :

```markdown
## Deck Themes

Set the theme on `<main class="deck ...">`:
- `theme-light` (default — may be omitted) — unchanged base styling.
- `theme-dark` — every content slide dark by default. Use the **dark-safe** component palette (`.dark-card`, `.cost`, `.chart-card`, `.brick`, `.foundation`, `.ph-icon`, `.tab`, `.spotlight-card`, `.big-message`, + archetypes). Light-card components are meant for light slides.

Per-slide accent (rhythm): add `dark` to a slide in a light deck, or `light` to a slide in a dark deck. `.light` opts the slide out of `theme-dark` back to the light styling.
```

- [ ] **Step 3 : Vérifier que l'ajout est purement additif**

Run:
```bash
git -C plugins/snetor-skills/skills/snetor-html-slides diff --stat references/css-system.md
git -C plugins/snetor-skills/skills/snetor-html-slides diff references/css-system.md | grep -E '^-' | grep -v '^---'
```
Expected : le 1er montre des insertions ; le 2e ne renvoie **aucune ligne** (aucune suppression).

- [ ] **Step 4 : Sanity-check des sélecteurs (pas de fuite hors thème)**

Run:
```bash
grep -c 'theme-dark .slide:not(.cover):not(.light)' plugins/snetor-skills/skills/snetor-html-slides/references/css-system.md
```
Expected : ≥ 20 (toutes les nouvelles règles sont scopées au thème ; aucune ne cible une classe nue existante).

- [ ] **Step 5 : Commit**

```bash
git add plugins/snetor-skills/skills/snetor-html-slides/references/css-system.md
git commit -m "feat(snetor-html-slides): add deck theme layer (theme-dark + .light accent)"
```

---

## Task 2 : CSS des 5 archétypes aérés

**Files:**
- Modify: `plugins/snetor-skills/skills/snetor-html-slides/references/css-system.md` (ajout dans le bloc CSS, juste après le calque thème de Task 1, toujours avant `/* RESPONSIVE */`)

**Interfaces:**
- Produces (classes de slide + éléments internes, consommés par Tasks 3-4) :
  - `section-divider` → `.sd-index`, `.sd-title`, `.sd-sub`
  - `quote` → `blockquote`, `.q-author`, `.q-name`, `.q-role`
  - `agenda` → `.agenda-list`, `.agenda-item`, `.ai-num`, `.ai-title`, `.ai-sub`
  - `closing` → `.closing-title`, `.closing-steps`, `.closing-contact`
  - `big-number` → `.bn-metric`, `.bn-label`, `.bn-sub`
- Principe : les éléments de texte centraux utilisent `color: inherit` + `opacity` pour s'adapter automatiquement au thème (navy sur clair, blanc sur foncé) sans règle par thème. Seuls `.sd-index` (ghost) et `.bn-metric` (accent vert/pastel) ont une nuance par thème.

- [ ] **Step 1 : Ajouter le bloc « SLIDE ARCHETYPES » dans `css-system.md`**

```css
/* === SLIDE ARCHETYPES (aerated, low-density — spec §2) ===
   Theme-adaptive via color:inherit + opacity. Reuse existing animations only. */

/* SECTION DIVIDER — chapter break */
.section-divider .body { justify-content: center; gap: 16px; }
.section-divider .sd-index { font-size: 84px; font-weight: 700; line-height: 1; color: currentColor; opacity: .18; }
.section-divider .sd-title { font-size: 52px; line-height: 1.1; font-weight: 600; color: inherit; max-width: 920px; }
.section-divider .sd-sub { font-size: 20px; line-height: 1.4; color: inherit; opacity: .72; max-width: 760px; }

/* QUOTE — full-bleed citation */
.quote .body { justify-content: center; gap: 22px; }
.quote blockquote { margin: 0; padding-left: 34px; position: relative; font-size: 38px; line-height: 1.26; font-weight: 600; color: inherit; max-width: 1000px; }
.quote blockquote::before { content: "\201C"; position: absolute; left: -4px; top: -22px; font-size: 92px; line-height: 1; color: var(--green); opacity: .55; }
.quote .q-author { display: flex; align-items: center; gap: 14px; }
.quote .q-author::before { content: ""; width: 34px; height: 2px; background: var(--green); flex: 0 0 auto; }
.quote .q-name { font-size: 18px; font-weight: 700; color: inherit; }
.quote .q-role { font-size: 15px; color: inherit; opacity: .66; }

/* AGENDA — numbered outline (light-card; safe on any background) */
.agenda .agenda-list { display: grid; gap: 12px; max-width: 940px; }
.agenda .agenda-item { display: grid; grid-template-columns: 46px 1fr; gap: 18px; align-items: center; padding: 14px 18px; border: 1px solid var(--border); border-radius: 8px; background: var(--white); box-shadow: 0 2px 6px rgba(21,43,71,.08); text-decoration: none; transition: transform .2s var(--ease), border-color .2s var(--ease); }
.agenda a.agenda-item:hover { transform: translateX(4px); border-color: rgba(0,125,54,.42); }
.agenda .ai-num { font-size: 24px; font-weight: 700; color: var(--green); line-height: 1; }
.agenda .ai-title { display: block; font-size: 19px; font-weight: 700; color: var(--navy); }
.agenda .ai-sub { display: block; font-size: 14px; color: var(--muted); margin-top: 2px; }
.slide.active .agenda-item { animation: rise 480ms var(--ease) both; }
.slide.active .agenda-item:nth-child(1) { animation-delay: 90ms; }
.slide.active .agenda-item:nth-child(2) { animation-delay: 160ms; }
.slide.active .agenda-item:nth-child(3) { animation-delay: 230ms; }
.slide.active .agenda-item:nth-child(4) { animation-delay: 300ms; }
.slide.active .agenda-item:nth-child(5) { animation-delay: 370ms; }
.slide.active .agenda-item:nth-child(6) { animation-delay: 440ms; }

/* CLOSING — final message + next steps + contact */
.closing .body { justify-content: center; gap: 22px; }
.closing .closing-title { font-size: 46px; line-height: 1.12; font-weight: 600; color: inherit; max-width: 920px; }
.closing .closing-contact { display: flex; align-items: center; gap: 12px; font-size: 16px; color: inherit; opacity: .88; }
.closing .closing-contact i { color: var(--green); font-size: 22px; }

/* BIG NUMBER — single giant KPI */
.big-number .body { justify-content: center; align-items: center; text-align: center; gap: 10px; }
.big-number .bn-metric { font-size: 160px; line-height: .95; font-weight: 700; color: var(--green); }
.big-number .bn-label { font-size: 24px; font-weight: 600; color: inherit; max-width: 700px; }
.big-number .bn-sub { font-size: 16px; color: inherit; opacity: .66; }
.section-divider.dark .sd-title, .deck.theme-dark .slide.section-divider:not(.light) .sd-title { color: white; }
.big-number.dark .bn-metric, .deck.theme-dark .slide.big-number:not(.light) .bn-metric { color: var(--pastel); }
```

- [ ] **Step 2 : Ajouter le responsive des archétypes**

Dans le bloc `@media (max-width: 980px)` existant, **ajouter** (sans modifier les lignes présentes) en fin de bloc :

```css
  .section-divider .sd-title { font-size: 34px; } .section-divider .sd-index { font-size: 56px; }
  .quote blockquote { font-size: 26px; } .closing .closing-title { font-size: 30px; }
  .big-number .bn-metric { font-size: 92px; } .agenda .agenda-list { max-width: none; }
```

- [ ] **Step 3 : Vérifier l'additivité**

Run:
```bash
git -C plugins/snetor-skills/skills/snetor-html-slides diff references/css-system.md | grep -E '^-' | grep -v '^---'
```
Expected : aucune ligne (sauf, dans le `@media`, la ligne `}` de fin est conservée — vérifier qu'aucune règle existante n'a disparu). Si l'ajout dans `@media` apparaît comme suppression+ajout d'accolade, vérifier manuellement que toutes les règles d'origine sont intactes.

- [ ] **Step 4 : Commit**

```bash
git add plugins/snetor-skills/skills/snetor-html-slides/references/css-system.md
git commit -m "feat(snetor-html-slides): add 5 aerated slide archetypes (divider, quote, agenda, closing, big-number)"
```

---

## Task 3 : Patterns HTML des archétypes dans `components.md`

**Files:**
- Modify: `plugins/snetor-skills/skills/snetor-html-slides/references/components.md` (ajouter une section avant `## Logo Usage in Slides`)

**Interfaces:**
- Consumes : classes de Task 2.
- Produces : patterns HTML copiables pour chaque archétype.

- [ ] **Step 1 : Ajouter la section « Slide Archetypes »**

Insérer avant `## Logo Usage in Slides` :

````markdown
## Slide Archetypes (aerated, low-density)

Use these for rhythm and to keep slides light. They adapt to the deck theme
automatically (text follows the slide color). `section-divider`, `quote` and
`big-number` shine as **accent** slides (`dark` in a light deck, `light` in a
dark deck).

### Section Divider (chapter break)

```html
<section class="slide section-divider dark">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Partie 2</div></header>
  <div class="body">
    <div class="sd-index animate d1">02</div>
    <h2 class="sd-title animate d2">Le titre du chapitre, court et net.</h2>
    <p class="sd-sub animate d3">Une ligne de contexte optionnelle.</p>
  </div>
  <footer class="footer"><div class="sources"></div><div class="progress" aria-hidden="true"></div></footer>
</section>
```

### Quote (full-bleed citation)

```html
<section class="slide quote">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Verbatim</div></header>
  <div class="body">
    <blockquote class="animate d1">Une citation marquante, en une à deux phrases maximum.</blockquote>
    <div class="q-author animate d2"><div><span class="q-name">Prénom Nom</span> · <span class="q-role">Rôle, Direction</span></div></div>
  </div>
  <footer class="footer"><div class="sources">Source : entretien interne.</div><div class="progress" aria-hidden="true"></div></footer>
</section>
```

### Agenda (numbered outline, optionally clickable)

Wrap items in `<a class="agenda-item" href="?slide=N">` to jump to a slide; use `<div class="agenda-item">` for a static outline.

```html
<section class="slide agenda">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Sommaire</div></header>
  <div class="body">
    <h2 class="animate d1">Au programme</h2>
    <div class="agenda-list animate d2">
      <a class="agenda-item" href="?slide=3"><span class="ai-num">1</span><span><span class="ai-title">Contexte</span><span class="ai-sub">Où en est-on aujourd'hui.</span></span></a>
      <a class="agenda-item" href="?slide=5"><span class="ai-num">2</span><span><span class="ai-title">Enjeux</span><span class="ai-sub">Ce qui est en jeu.</span></span></a>
      <a class="agenda-item" href="?slide=7"><span class="ai-num">3</span><span><span class="ai-title">Décision</span><span class="ai-sub">Ce qu'on demande.</span></span></a>
    </div>
  </div>
  <footer class="footer"><div class="sources"></div><div class="progress" aria-hidden="true"></div></footer>
</section>
```

### Big Number (single hero KPI)

```html
<section class="slide big-number dark">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Le chiffre</div></header>
  <div class="body">
    <span class="bn-metric counter animate d1" data-target="68" data-suffix="%">0%</span>
    <p class="bn-label animate d2">La phrase qui donne le sens du chiffre.</p>
    <p class="bn-sub animate d3">Précision / périmètre / source.</p>
  </div>
  <footer class="footer"><div class="sources">Source : ...</div><div class="progress" aria-hidden="true"></div></footer>
</section>
```

### Closing (final message + next steps + contact)

```html
<section class="slide closing dark">
  <header class="brand animate"><div class="logo" aria-label="Snetor"></div><div class="eyebrow">Prochaines étapes</div></header>
  <div class="body">
    <h2 class="closing-title animate d1">Ce qu'on retient, et la suite.</h2>
    <div class="closing-steps pill-row animate d2"><span class="pill">Valider le périmètre</span><span class="pill">Lancer le pilote</span><span class="pill">Point à J+30</span></div>
    <div class="closing-contact animate d3"><i class="ph ph-envelope-simple"></i> c.peponnet@snetor.com</div>
  </div>
  <div class="deco-shapes" aria-hidden="true"></div>
  <footer class="footer"><div class="sources"></div><div class="progress" aria-hidden="true"></div></footer>
</section>
```
````

- [ ] **Step 2 : Mettre à jour la note des classes de slide**

Dans la section « Slide Shell », remplacer la ligne :
```
<section class="slide [cover|dark|]">
```
par :
```
<section class="slide [cover|dark|light|section-divider|quote|agenda|big-number|closing|]">
```
et ajouter sous la liste des classes :
```markdown
- `light` — light accent slide inside a `theme-dark` deck (symmetric of `dark`)
- archetype classes (`section-divider`, `quote`, `agenda`, `big-number`, `closing`) — see "Slide Archetypes"
```

- [ ] **Step 3 : Commit**

```bash
git add plugins/snetor-skills/skills/snetor-html-slides/references/components.md
git commit -m "docs(snetor-html-slides): add HTML patterns for the 5 slide archetypes"
```

---

## Task 4 : Deck de démo / non-régression visuelle

**Files:**
- Create: `plugins/snetor-skills/skills/snetor-html-slides/examples/theme-demo.html`

**Interfaces:**
- Consumes : CSS de Tasks 1-2, patterns de Task 3.
- Assets : référencés directement depuis le dossier `assets/` du skill (pas de copie). Depuis `examples/`, les chemins sont `../assets/branding/...` et `../assets/logos/...`.

- [ ] **Step 1 : Créer le fichier en repartant du template de `SKILL.md`**

Construire `examples/theme-demo.html` avec :
- `<head>` : police Raleway + **tout le bloc CSS de `references/css-system.md` (verbatim, version à jour incluant Tasks 1-2)**. Dans `:root`, fixer les chemins :
  - `--logo: url("../assets/branding/snetor_full_logo.png");`
  - `--logo-reversed: url("../assets/branding/snetor_full_logo_reversed.png");`
  - `--globe: url("../assets/branding/snetor_globe.png");`
  - `--hero: url("../assets/branding/Hero-banner-abstrait.jpg");`
  - `--shapes: url("../assets/branding/snetor_shapes.png");`
- `<script src="https://unpkg.com/@phosphor-icons/web"></script>` dans `<head>` (icônes).
- `<main class="deck theme-dark">` — **on démontre le thème foncé**, avec des slides d'accent `.light`.
- La **navigation JS verbatim** de `css-system.md` en fin de `<body>` (remplacer `DECK_TITLE` par `"Snetor — démo thème & archétypes"`), + le bootstrap counters de `references/charts.md` (pour `big-number .counter`).
- Inclure le DOM presenter mode (4 overlays) comme dans le template SKILL.

Slides (dans l'ordre) :
1. `slide cover active` — cover standard (titre + lead + hero-line + globe).
2. `slide agenda` — sommaire 4 items (light-card, lisible sur deck foncé).
3. `slide section-divider light` — **accent clair** dans le deck foncé (prouve `.light`).
4. `slide` (foncée par thème) — `chart-card` avec un donut (dark-safe) + `statement`.
5. `slide big-number` — KPI géant animé (`.bn-metric.counter`), pastel sur fond foncé.
6. `slide quote` — citation.
7. `slide light` — **accent clair** contenant un **gantt** (composant riche dans son habitat clair → preuve de non-régression des animations `growBar`/`.g-today`).
8. `slide closing` — clôture + pills + contact + `deco-shapes`.

- [ ] **Step 2 : Vérifier la structure du fichier**

Run:
```bash
grep -c 'class="slide' plugins/snetor-skills/skills/snetor-html-slides/examples/theme-demo.html
grep -o 'theme-dark\|section-divider\|big-number\|quote\|closing\|agenda\|slide light\|gantt' plugins/snetor-skills/skills/snetor-html-slides/examples/theme-demo.html | sort -u
```
Expected : 8 occurrences de slides ; la 2e commande liste bien `theme-dark`, `agenda`, `section-divider`, `big-number`, `quote`, `closing`, `slide light`, `gantt`.

- [ ] **Step 3 : Validation visuelle (Clément)**

Ouvrir `examples/theme-demo.html` dans le navigateur et vérifier :
- Deck foncé lisible partout ; slides `.light` (3 et 7) bien claires.
- Les 5 archétypes rendent correctement ; `big-number` compte de 0 à la cible à l'activation.
- **Gantt** (slide 7) : barres animées, marqueur « Aujourd'hui », libellés navy lisibles.
- Animations d'entrée présentes sur chaque slide ; navigation clavier ←/→ OK.

> ⚠️ Point de revue : ne pas committer avant l'accord visuel de Clément.

- [ ] **Step 4 : Commit (après validation)**

```bash
git add plugins/snetor-skills/skills/snetor-html-slides/examples/theme-demo.html
git commit -m "docs(snetor-html-slides): add theme + archetypes demo deck"
```

---

## Task 5 : Wizard d'intake (SKILL.md — nouveau Step 1)

**Files:**
- Modify: `plugins/snetor-skills/skills/snetor-html-slides/SKILL.md` (remplacer la section « Step 1 — Understand the request »)

**Interfaces:**
- Produces : le déroulé d'intake que toute génération suit avant Step 2.

- [ ] **Step 1 : Remplacer la section Step 1**

Remplacer intégralement la section actuelle « ## Step 1 — Understand the request » (de son titre jusqu'au `---` qui la suit) par :

````markdown
## Step 1 — Intake wizard (cadrer avant de générer)

Avant de planifier ou d'écrire du HTML, **cadrer le besoin avec le collaborateur** via l'outil `AskUserQuestion` (choix multiples + « Autre » natif). Objectif : un deck ciblé, pas un template générique.

**Détection de langue** d'abord, selon `references/i18n.md` (FR par défaut, EN/ES selon la requête, override « in [language] » prioritaire). Poser les questions du wizard dans la langue du collaborateur.

### Mode express (défaut) — 3 tours

1. **Objectif & cadrage** — une question `AskUserQuestion` couvrant : audience (COMEX / direction technique / équipe / client / autre), objectif (décider / informer / convaincre / former), et **message clé** (la 1 décision ou insight à retenir).
2. **Structure** — proposer **2-3 plans** (chaque option = un outline en mini-ASCII : titres de slides + rôle de chaque slide), avec un nombre de slides indicatif. Le collaborateur choisit ou amende via « Autre ».
3. **Style visuel** — une question avec, pour chaque option, un champ `preview` contenant une **mini-maquette ASCII** : thème (clair / foncé / mixte) et style de cover. Le collaborateur choisit via « Autre » s'il veut autre chose.

### Mode guidé (sur demande)

Si le collaborateur veut un contrôle fin, dérouler slide par slide : titre, sous-titre, et composant principal proposé (avec 1-2 alternatives). Une question `AskUserQuestion` par slide ou par petit groupe.

### Garde-fou anti-friction

Si la requête initiale est **déjà détaillée** (audience + objectif + plan explicites), **ne pas dérouler les 3 tours** : présenter un **récap unique à valider** (audience, objectif, plan, thème) et passer à Step 2 après accord. Le wizard sert à lever l'ambiguïté, pas à ralentir un brief clair.

### Source material

Identifier les sources à exploiter (pages du vault, notes d'entretien, wikis) — les citer dans les `.sources` des slides (Step 4, règle 9).
````

- [ ] **Step 2 : Aligner le pointeur de Step 2**

Vérifier que « ## Step 2 — Plan the slide structure » suit toujours et commence par choisir l'arc. Ajouter en tête de Step 2 la phrase : `Partir du plan validé au Step 1.`

- [ ] **Step 3 : Vérifier la cohérence**

Run:
```bash
grep -n 'AskUserQuestion\|Mode express\|Garde-fou anti-friction' plugins/snetor-skills/skills/snetor-html-slides/SKILL.md
```
Expected : les 3 ancres présentes dans la nouvelle section Step 1.

- [ ] **Step 4 : Commit**

```bash
git add plugins/snetor-skills/skills/snetor-html-slides/SKILL.md
git commit -m "feat(snetor-html-slides): replace silent inference with an intake wizard (express + guided)"
```

---

## Task 6 : Guidance thème/archétypes/accent + règles (SKILL.md)

**Files:**
- Modify: `plugins/snetor-skills/skills/snetor-html-slides/SKILL.md` (Step 2 + template + règles non-négociables)

**Interfaces:**
- Consumes : classes de Tasks 1-2-3.

- [ ] **Step 1 : Étendre Step 2 — choix du thème & rythme d'accents**

Dans « ## Step 2 — Plan the slide structure », sous le choix du layout par slide, ajouter :

```markdown
**Theme & accent rhythm (spec §1) :**
- Choisir un thème de deck selon le style validé au Step 1 : `theme-light` (défaut), `theme-dark`, ou mixte. Le poser sur `<main class="deck theme-...">`.
- Utiliser les **slides d'accent** pour rythmer : `dark` dans un deck clair, `light` dans un deck foncé. Réserver les accents aux moments-clés (transition, citation, décision, big-number).
- **Règles d'alternance** : pas deux slides d'accent consécutives ; un accent marque une rupture, pas une slide de contenu dense.

**Archétypes aérés (spec §2) :** intercaler `section-divider` (respiration entre parties), `agenda` (en tête), `quote`, `big-number` (un KPI fort), `closing` (clôture). Voir `references/components.md`.
```

- [ ] **Step 2 : Mettre à jour le template HTML**

Dans la section « ### Document template », remplacer la ligne :
```
  <main class="deck">
```
par :
```
  <main class="deck theme-light"><!-- theme-light (default) | theme-dark -->
```

- [ ] **Step 3 : Lever la limite « dark max 1/deck » et documenter les nouvelles classes**

Dans « ### Non-negotiable rules », remplacer la règle existante sur l'usage de `dark` (la mention « 1 per deck maximum ») par :

```markdown
3. **Themes & accents** — set `theme-light` (default) or `theme-dark` on `<main class="deck">`. Use accent slides (`dark` in a light deck, `light` in a dark deck) for rhythm at key moments. No two accent slides in a row. On dark slides use the dark-safe component palette (see `references/css-system.md` → Deck Themes).
```

(Conserver la numérotation : adapter le numéro à la règle réellement présente ; ne pas dupliquer.)

- [ ] **Step 4 : Ajouter une règle archétypes**

Ajouter une règle non-négociable :
```markdown
26. **Archetypes** — use the aerated archetypes (`section-divider`, `agenda`, `quote`, `big-number`, `closing`) to vary rhythm and avoid the same arc every time. `big-number` uses `.bn-metric.counter`; `agenda` items may link via `?slide=N`.
```

- [ ] **Step 5 : Vérifier**

Run:
```bash
grep -n 'theme-dark\|theme-light\|Archetypes\|accent' plugins/snetor-skills/skills/snetor-html-slides/SKILL.md
```
Expected : présence du template `theme-light`, de la règle thèmes/accents et de la règle archétypes.

- [ ] **Step 6 : Commit**

```bash
git add plugins/snetor-skills/skills/snetor-html-slides/SKILL.md
git commit -m "feat(snetor-html-slides): document deck themes, accent rhythm and archetypes in SKILL"
```

---

## Task 7 : Garde-fous anti-surcharge stricts (SKILL.md)

**Files:**
- Modify: `plugins/snetor-skills/skills/snetor-html-slides/SKILL.md` (durcir la règle de densité + nouvelle section dédiée)

**Interfaces:** —

- [ ] **Step 1 : Ajouter une section « Anti-surcharge » avant « ### Non-negotiable rules »**

```markdown
### Garde-fous anti-surcharge (stricts — spec §4)

Une slide doit respirer. Règles dures, appliquées à toute génération :

- **1 idée par slide.** **1 composant principal max** par slide (le chrome — eyebrow, footer — ne compte pas).
- **Budget mots strict** : ≤ ~25 mots de texte courant par slide (hors titres, statements, speaker notes).
- **Détails ailleurs** : pousser le détail en speaker notes (`N`), `accordion`, ou slide d'annexe (`annex-tag`) — jamais entassé sur la slide.
- **Auto-split** : si le contenu dépasse le budget, **scinder** la slide en deux plutôt que tasser.
- **Refus de surcharger** : même sur demande explicite (« mets tout sur une slide »), proposer le split au lieu d'entasser.
```

- [ ] **Step 2 : Aligner la règle de densité existante**

Dans « ### Non-negotiable rules », remplacer le passage de la règle 14 « Aim for max 30 words of body text per slide » par : `Respecter le budget mots des garde-fous anti-surcharge (≤ ~25 mots de corps/slide) ; au-delà, split ou renvoi en notes/accordion/annexe.`

- [ ] **Step 3 : Vérifier**

Run:
```bash
grep -n 'anti-surcharge\|1 idée par slide\|Auto-split\|Refus de surcharger' plugins/snetor-skills/skills/snetor-html-slides/SKILL.md
```
Expected : la section et ses 4 ancres présentes.

- [ ] **Step 4 : Mettre à jour `tasks/todo.md` (review)**

Cocher les items réalisés et remplir la section « Review » de `tasks/todo.md`.

- [ ] **Step 5 : Commit**

```bash
git add plugins/snetor-skills/skills/snetor-html-slides/SKILL.md
git commit -m "feat(snetor-html-slides): add strict anti-overload guardrails"
```

---

## Self-Review (rempli par l'auteur du plan)

**Spec coverage :**
- §1 Thème → Tasks 1 (theme-dark + .light), 6 (guidance/règles). ✅
- §2 Archétypes → Tasks 2 (CSS), 3 (HTML). ✅
- §3 Wizard → Task 5. ✅
- §4 Anti-surcharge → Task 7. ✅
- §5 Périmètre / deck de test → Task 4. PPT explicitement hors périmètre. ✅
- Non-régression → Global Constraints + checks `git diff` (Tasks 1-2) + gantt dans le deck de démo (Task 4). ✅

**Placeholder scan :** aucun TODO/TBD ; tout le CSS et le HTML sont fournis intégralement.

**Type/identifier consistency :** classes définies en Task 2 (`sd-index`, `sd-title`, `sd-sub`, `q-author`, `q-name`, `q-role`, `agenda-item`, `ai-num`, `ai-title`, `ai-sub`, `closing-title`, `closing-steps`, `closing-contact`, `bn-metric`, `bn-label`, `bn-sub`) — identiques en Tasks 3 et 4. `theme-dark` / `theme-light` / `.light` cohérents Tasks 1, 4, 6.

**Note d'exécution :** ce plan touche un système CSS/docs sans tests automatisés ; la « vérification » de chaque tâche combine contrôles statiques `grep`/`git diff` et, pour le rendu, la validation visuelle du deck de démo (Task 4) — point de revue humaine obligatoire avant son commit.
