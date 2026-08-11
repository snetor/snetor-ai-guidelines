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
tasks/lessons.md        journal append-only
```

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
`live`, ou supprimée) ; ajouter les leçons à `tasks/lessons.md` ; supprimer de
`tasks/todo.md` les items livrés, sans les cocher ; réécrire `HANDOFF.md` sous
150 lignes. Puis régénérer l index.

Condition d entrée, avant la moindre suppression : le plan doit être
**entièrement exécuté** — toutes ses tâches livrées — et l arbre de travail
commité. `docs/superpowers/plans/` étant gitignoré, un plan supprimé en cours
d exécution emporte les tâches restantes sans aucun blob git pour les rendre.
Si l une des deux conditions manque, s arrêter et le dire ; ne rien supprimer.

La suppression d une spec **se confirme** auprès de l utilisateur : proposer
l arbitrage, attendre l accord, puis seulement supprimer. Même prudence sur
`tasks/`, gitignoré dans certains repos : ces éditions y sont irrécupérables.

## Règles non négociables

Ne jamais éditer `docs/README.md` à la main : le régénérer par
`python scripts/check_docs.py --repo-root . --fix`.

Ne jamais commiter un plan d implémentation.

Une spec n est **ni déplacée ni copiée : réécrite** vers sa destination. Une
décision utile tient en quarante à cent lignes.

Un item de `tasks/todo.md` livré est supprimé, pas coché.

Ne jamais créer un fichier par session (`handoff-2026-08-10.md`,
`SUMMARY.md`, `PHASE2_COMPLETE.md`). Le routeur est unique et se réécrit.
