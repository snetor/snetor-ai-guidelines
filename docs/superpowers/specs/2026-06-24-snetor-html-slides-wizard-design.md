# Refonte snetor-html-slides — wizard d'intake, thèmes & anti-surcharge

**Date :** 2026-06-24
**Branche :** `feat/snetor-html-slides-wizard`
**Statut :** design validé, prêt pour plan d'implémentation

---

## Problème

Le skill `snetor-html-slides` produit des decks perçus comme :
1. **Répétitifs** — toujours le même arc (cover → contexte → … → décision) et la même cover ; pas de slides de respiration ; variété de fond limitée à `.dark` (max 1/deck).
2. **Surchargés** — trop de contenu/composants par slide.
3. **Sans dialogue** — le Step 1 actuel *infère* le besoin (« plutôt qu'en posant des questions ») au lieu de cadrer l'objectif du collaborateur.

## Objectif

Refondre le skill pour : (a) cadrer le besoin via un **wizard d'intake** à choix multiples, (b) offrir une **vraie variété visuelle** (thème clair/foncé/mixte + slides d'accent dans les deux sens + nouveaux archétypes aérés), (c) **imposer des garde-fous anti-surcharge stricts** — **sans casser** aucun composant, animation ou comportement existant.

## Contrainte non négociable : non-régression

Tous les composants existants doivent rester **strictement intacts** : animations (`rise`, `growBar`, `growLine`, `pulseDot`, `fadeScale`, `checkPop`), `gantt` (+ `.g-today`), `journey`, `flow`, `path`, `product-grid`, `bento`, `marquee`, `spotlight`, charts Chart.js + lazy-init, presenter mode, i18n, navigation clavier, responsive, print.

**Règle de mise en œuvre :** toutes les évolutions CSS sont **additives**. On n'édite ni ne supprime aucune règle existante du bloc CSS ; on **ajoute** un calque thème, le symétrique `.light`, et le CSS des nouveaux archétypes. Critère de vérification : le `git diff` de `css-system.md` ne contient que des ajouts dans les zones existantes (hormis l'extension de sélecteurs déjà prévue, voir §1).

---

## §1 — Architecture du thème (approche A : composer avec l'existant)

Aujourd'hui : `light` est le défaut codé en dur (`.deck` blanc, `.slide` gradient clair, texte navy) ; `.dark` et `.cover` surchargent en texte blanc par slide. Aucune notion de thème de deck.

### Ajouts

- **Classe de deck** sur `<main class="deck">` :
  - `theme-light` (défaut, = comportement actuel — peut être implicite/omis).
  - `theme-dark` : applique le traitement foncé à **toutes** les slides par défaut.
- **`theme-dark` réutilise les primitives `.dark` existantes** en étendant les sélecteurs concernés à `.theme-dark .slide` (fond, couleurs de texte h2/h3/p/li, eyebrow, footer, progress, logo reversed, variantes de composants `.dark .card`, `.dark .chart-card`, `.dark .ph-icon`, `.dark .tab`, `.dark .metric`…).
  - Mécanisme : ajouter une **règle de base** `.deck.theme-dark .slide { background:…; color:white; }` puis, pour chaque variante `.dark X` existante, **ajouter** un sélecteur jumeau `.theme-dark .slide X` *via de nouvelles règles* (on ne touche pas aux règles `.dark X` d'origine). Les slides `cover` gardent leur traitement propre.
- **Slide d'accent `.light`** (symétrique manquant de `.dark`) : force fond clair + texte foncé, même à l'intérieur d'un `theme-dark`. Permet de ponctuer un deck foncé.
- **Mixte** = pas de CSS dédié : `theme-light` (ou `theme-dark`) + slides d'accent `.dark` (ou `.light`) placées intentionnellement.

### Règles d'auteur (dans SKILL.md)

- La limite « `dark` max 1/deck » est **levée** : les accents deviennent un outil de rythme.
- Garde-fous d'alternance : pas 2 slides d'accent consécutives ; un accent marque un moment-clé (transition, décision, citation), pas une slide de contenu dense.

### Vérification §1

Deck de test avec `theme-dark` : toutes les slides foncées, lisibilité OK, une slide d'accent `.light` au milieu. Deck `theme-light` inchangé pixel-près vs aujourd'hui (diff visuel nul sur un deck existant régénéré).

---

## §2 — Nouveaux archétypes de slides (variété + faible densité)

Cinq archétypes **aérés** ajoutés (CSS dans `css-system.md`, patterns HTML dans `components.md`). Chacun a un rôle narratif clair et un budget mots faible.

1. **`section-divider`** — slide de respiration : eyebrow + grand titre de chapitre + numéro de section optionnel. Idéale en accent (`dark`/`light`). Réutilise la typo `h1`/eyebrow existante.
2. **`quote`** — citation plein cadre (auteur + rôle). Va au-delà du `.statement` inline.
3. **`agenda`** — sommaire/plan en début de deck, items numérotés, optionnellement cliquables (ancre vers la slide).
4. **`closing`** — slide de clôture : message final + next steps courts + contact/CTA. Peut réutiliser `deco-shapes`.
5. **`big-number`** — un seul KPI géant centré (réutilise `.counter` + `.metric`), une ligne de contexte.

Contrainte : ces archétypes **réutilisent** les tokens, la typo et les animations existants ; aucun ne redéfinit de keyframe.

### Vérification §2

Chaque archétype rendu dans le deck de test, en thème clair ET foncé, animations actives.

---

## §3 — Wizard d'intake (mode express + guidé)

Nouveau **Step 1** dans `SKILL.md`, basé sur l'outil `AskUserQuestion` (choix multiples + « Autre » natif). Remplace l'inférence silencieuse actuelle.

### Mode express (défaut) — 3 tours

1. **Objectif & cadrage** — audience (COMEX / technique / équipe / client / autre), objectif (décider / informer / convaincre / former), **message clé** (1 décision ou insight à retenir).
2. **Structure** — Claude propose **2-3 plans** (outline en ASCII : titres de slides + rôle), nb de slides indicatif ; le collaborateur choisit/amende (« Autre »).
3. **Style visuel** — thème (clair / foncé / mixte) + style de cover, présentés avec **mini-maquettes ASCII** (champ `preview` d'`AskUserQuestion`) ; le collaborateur choisit (« Autre »).

### Mode guidé (sur demande)

Déroule slide par slide : titre, sous-titre, composant principal proposé (avec alternatives). Pour les decks où le collaborateur veut un contrôle fin.

### Garde-fou anti-friction

Si la requête initiale est déjà très détaillée (plan + audience + objectif explicites), Claude **collapse** les 3 questions en **un seul récap à valider** plutôt que de questionner inutilement. Le wizard sert à lever l'ambiguïté, pas à ralentir un brief déjà clair.

### Vérification §3

Simuler une demande floue → les 3 tours se déclenchent avec propositions + « Autre ». Simuler une demande détaillée → un seul récap de validation.

---

## §4 — Garde-fous anti-surcharge (stricts)

Section de règles dures dans `SKILL.md`, applicable à toute génération :

- **1 idée par slide.** **1 composant principal max** par slide (les éléments de chrome — eyebrow, footer — ne comptent pas).
- **Budget mots strict** sur le corps (hors titres/statements/notes). Cible : ≤ ~25 mots de texte courant par slide.
- **Détails → ailleurs** : speaker notes (`N`), `accordion`, ou slide d'annexe (`annex-tag`). Jamais entassés sur la slide principale.
- **Auto-split** : si le contenu dépasse le budget, Claude **scinde** la slide en deux plutôt que de tasser.
- **Refus de surcharger** : même sur demande explicite « mets tout sur une slide », Claude propose le split au lieu d'entasser.

Note : ces règles remplacent/durcissent les règles souples actuelles (ex. « max 30 mots ») — c'est une **modification de SKILL.md uniquement** (instructions), pas du CSS.

### Vérification §4

Deck de test : aucune slide ne dépasse le budget ; au moins une slide démontre le renvoi de détails en accordion/notes.

---

## §5 — Périmètre & livrables

### Dans le périmètre
- `SKILL.md` — nouveau Step 1 (wizard), section thèmes/archétypes dans le plan de structure, règles anti-surcharge, mention des classes `theme-*` et `.light`.
- `references/css-system.md` — calque thème (`theme-dark`), accent `.light`, CSS des 5 archétypes. **Additif uniquement.**
- `references/components.md` — patterns HTML des 5 archétypes + exemples thème/accent.
- **Deck de test** illustratif (un `.html` de démonstration couvrant : thème clair, thème foncé, slides d'accent dans les 2 sens, les 5 archétypes, un composant « riche » existant — ex. gantt — pour prouver la non-régression).

### Hors périmètre
- **Skill `snetor-ppt-slides`** (chantier 2) : conversion HTML → PPT **natif éditable** via `python-pptx`. À concevoir séparément (spec + plan dédiés). Compromis de fidélité à expliciter à ce moment-là.

### Git
- Branche dédiée `feat/snetor-html-slides-wizard` depuis `origin/main` (1 sujet = 1 PR). Squash merge.

---

## Critères de succès globaux

1. Un deck `theme-light` existant régénéré est **visuellement identique** à aujourd'hui (non-régression prouvée).
2. Un deck `theme-dark` est lisible et cohérent, avec au moins une slide d'accent `.light`.
3. Les 5 nouveaux archétypes rendent correctement dans les 2 thèmes, animations actives.
4. Le wizard se déclenche sur demande floue (3 tours + « Autre ») et se collapse sur demande détaillée.
5. Aucune slide du deck de test ne dépasse le budget mots ; détails renvoyés en notes/accordion/annexe.
6. `git diff` de `css-system.md` = ajouts uniquement (aucune règle existante supprimée/réécrite).
