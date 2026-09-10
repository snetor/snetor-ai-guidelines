# Snetor Guidelines — règles propres à Snetor

Ce fichier porte les règles propres à Snetor. Il complète `workflow.md` et ne
le remplace pas. Il est écrasé à chaque déploiement.

# Git Hygiene

- **Une branche = une PR = un sujet** (`feat/`, `fix/`, `docs/`, `chore/` + kebab). Brancher depuis `origin/main` à jour.
- **Squash merge + suppression auto de la branche** (réglés sur les repos). Ne pas laisser traîner de branches mergées ; `git fetch --prune` régulier.
- **⚠️ Ne JAMAIS pousser sur une branche après le merge de sa PR** — le commit pend hors de `main`. Repartir d'une nouvelle branche depuis `origin/main`.
- **Worktrees** : un par tâche ; `git worktree remove` après merge. Ne jamais changer la branche du checkout principal partagé ni toucher aux branches ou worktrees d'un autre agent (sessions parallèles).
- **Un repo dont la CI applique de l'infrastructure : `merge = apply`** — ne merger qu'avec plan CI vert et PR relue ; pas d'`apply` local.
- Détail : le `docs/git-workflow.md` du repo concerné, s'il existe.

# Documentation

Standard complet : `docs/live/documentation-standard.md` du repo
`snetor-ai-guidelines`. Les invariants, applicables à tous les repos Snetor :

## Structure

```
HANDOFF.md              routeur d état — 150 lignes maximum
docs/live/              doit être vrai maintenant, réécrit en place
docs/dated/             vrai à sa date, jamais réécrit, remplacé par un successeur
docs/README.md          généré — ne jamais éditer à la main
docs/superpowers/specs/ zone de travail, vidée à la clôture
docs/superpowers/plans/ zone de travail, gitignorée
tasks/todo.md           items ouverts seulement
tasks/lessons.md        règles encore actives — 300 lignes maximum
tasks/lessons/          archive mensuelle AAAA-MM.md, jamais plafonnée
```

Les deux plafonds (`HANDOFF.md` 150, `tasks/lessons.md` 300) sont vérifiés par
`scripts/check_docs.py` et bloquent la CI.

## Frontmatter obligatoire dans docs/live/ et docs/dated/

`regime` (`live` ou `dated`), `audience` (liste parmi `agent`, `dev`,
`newcomer`, `ops`, `business`). En `live` : `reviewed` en date ISO, `ttl`
optionnel au format `<n>d` (défaut `90d`). En `dated` : `date` en date ISO,
`status` parmi `draft`, `proposed`, `decided`, `applied`, `superseded`.

Chaînage `dated`, optionnel sauf mention : `supersedes` et `superseded_by`,
chemins relatifs à la racine du repo. `superseded_by` est **obligatoire** dès
que `status` vaut `superseded`. Les deux doivent pointer un fichier qui existe :
sinon la CI bloque.

## Clôture de branche — cinq étapes

Utiliser le skill `snetor-docs-close`. À défaut, dans cet ordre : supprimer le
plan ; arbitrer chaque spec (réécrite en décision datée, fondue dans un fichier
`live`, ou supprimée) ; ajouter les leçons à `tasks/lessons.md` — et si le
plafond de 300 lignes est franchi, basculer les sessions closes dans
`tasks/lessons/AAAA-MM.md` ; supprimer de `tasks/todo.md` les items livrés, sans
les cocher ; réécrire `HANDOFF.md` sous 150 lignes. Puis régénérer l index.

Condition d entrée, avant la moindre suppression : le plan doit être
**entièrement exécuté** — toutes ses tâches livrées — et l arbre de travail
commité. `docs/superpowers/plans/` étant gitignoré, un plan supprimé en cours
d exécution emporte les tâches restantes sans aucun blob git pour les rendre.
Si l une des deux conditions manque, s arrêter et le dire ; ne rien supprimer.

La suppression d une spec **se confirme** auprès de l utilisateur : proposer
l arbitrage, attendre l accord, puis seulement supprimer. Même prudence sur
`tasks/`, gitignoré dans certains repos : ces éditions y sont irrécupérables.

## Mémoire — deux magasins, deux métiers

Claude Code dispose de **deux** endroits où il capitalise. Les confondre est la
cause des `lessons.md` de 3 000 lignes que plus personne ne lit.

| | `tasks/lessons.md` | `memory/` |
|---|---|---|
| Emplacement | dans le repo, versionné | `%USERPROFILE%\.claude\projects\<repo>\memory\` |
| Chargement | **jamais** en entier — on y `grep` | injecté automatiquement au démarrage |
| Contenu | la règle **et l incident qui la justifie** | un fait par fichier, formulation courte |
| Survit à un changement de poste | oui | **non** — ni versionné, ni sauvegardé |
| Plafond | 300 lignes, CI bloquante | `MEMORY.md` reste un index d une ligne par fait |

Conséquence pratique : ce qui doit survivre au poste s écrit **aussi** dans
`tasks/lessons.md`. `memory/` est un cache de travail, pas une archive.

### Consolider `memory/` avec `/dream`

`/dream` relit les fichiers de `memory/`, fusionne les doublons, remplace ce qui
a été démenti par la dernière valeur connue et réécrit l index. `AutoDream` fait
la même chose tout seul après environ 24 h d inactivité. La commande **ne touche
jamais** `tasks/lessons.md`.

Avant le premier passage sur un projet, sauvegarder le dossier : `/dream`
réécrit tous les fichiers, et `memory/` n est pas dans Git.

```powershell
Copy-Item -Recurse "$env:USERPROFILE\.claude\projects\<projet>\memory" `
  "$env:USERPROFILE\.claude\backups\memory-<projet>-$(Get-Date -Format yyyy-MM-dd)"
```

Au moment où `/dream` propose son résultat, protéger les mémoires qui portent une
**correction** (« j avais conclu l inverse », « mon premier classement était
faux »). Compacter une correction en ne gardant que sa conclusion supprime le
garde-fou : c est la trace de l erreur qui empêche de la refaire.

## Le garde-fou — une règle vérifiable ne reste pas en prose

`~/.claude/hooks/guard.py` refuse, avant exécution, les gestes qui ont déjà coûté quelque chose :
commit ou écriture sur `main`, push sur une branche dont la PR est mergée, `Set-Content` sur du
contenu accentué, heredoc ou `git commit -m "…"` en PowerShell, pipe tronquant derrière
`gh pr checks` ou `az`. `gh pr merge` et `git push --force` remontent à l'humain.

Il est déployé par `scripts/deploy-claude.ps1`, donc **actif sur tous les dépôts** ouverts avec
Claude Code. Un dépôt qui a besoin d'une règle en propre pose son propre hook dans son
`.claude/settings.json` : il s'ajoute au garde global, il ne le remplace pas.

**Le partage des rôles avec `tasks/lessons.md` est le point important.** Une règle qu'un programme
peut vérifier n'a rien à faire en prose : elle y sera lue une fois, puis enfreinte. Chaque règle
qui migre du fichier vers le garde-fou est une règle qu'on **retire du texte** et qui devient
**vraiment respectée** — le seul mouvement qui allège la doctrine et durcit la pratique en même
temps. `lessons.md` garde ce qu'aucune machine ne saura juger.

⚠️ **Un blocage n'est pas un bug.** Chaque règle cite l'incident qui la justifie : lire le motif,
pas contourner. Si le motif est manifestement à côté, c'est le garde-fou qu'on corrige — avec son
test — pas le geste qu'on déguise.

Deux limites connues, à savoir avant de crier au faux positif :

- Le garde lit la commande **privée du corps de ses heredocs** : un texte qui *cite* `git push`
  n'est pas un `git push`. En revanche un `echo '… | tail …'` reste vu comme une commande. Écrire
  la charge dans un fichier lève l'ambiguïté.
- Il résout le `cd` de tête avec `pathlib` **côté Windows** : un chemin Git Bash `/c/Users/…` n'y
  est pas absolu et le garde retombe sur le checkout partagé, souvent `main`. En worktree, écrire
  `cd "C:/Users/…"`.

## Règles non négociables

Ne jamais éditer `docs/README.md` à la main : le régénérer par
`python scripts/check_docs.py --repo-root . --fix`.

Ne jamais commiter un plan d implémentation.

Une spec n est **ni déplacée ni copiée : réécrite** vers sa destination. Une
décision utile tient en quarante à cent lignes.

Un item de `tasks/todo.md` livré est supprimé, pas coché.

Ne jamais créer un fichier par session (`handoff-2026-08-10.md`,
`SUMMARY.md`, `PHASE2_COMPLETE.md`). Le routeur est unique et se réécrit.
