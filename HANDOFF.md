# HANDOFF — snetor-ai-guidelines

**Dernière révision :** 2026-08-10

Routeur d état, pas un journal. L historique vit dans `git log`.

## Où on en est

Le repo distribue la configuration Claude Code de Snetor : les règles d équipe
de `claude-config/`, importées dans chaque session depuis le `CLAUDE.md`
personnel du poste, un style de sortie, un statusline, un script de déploiement
poste, et le plugin `snetor-skills` (quatre skills) via le marketplace Claude
Code.

Le standard de documentation est livré et appliqué à ce repo : `docs/live/`,
`docs/dated/`, index généré, vérificateur en CI.

## Prochaine action

Brancher les repos applicatifs internes sur le workflow `check-docs.yml@v1`,
une pull request par repo. Le rapport du vérificateur produit la liste de
travail de chacun. L ordre de passage et le périmètre restant se suivent hors
de ce dépôt, qui est public.

## Où chercher

| Besoin | Fichier |
|---|---|
| Comprendre le standard de documentation | `docs/live/documentation-standard.md` |
| Clôturer une branche proprement | skill `snetor-docs-close` |
| Vérifier la documentation d un repo | `scripts/check_docs.py` |
| Brancher un repo sur la CI documentaire | `.github/workflows/check-docs.yml` |
| Installer le poste d un nouveau développeur | `README.md`, `scripts/README.md` |
| Déployer la configuration Claude Code | `scripts/deploy-claude.ps1` |
| Règles d équipe chargées dans chaque session | `claude-config/snetor-guidelines.md` |
| Règles de travail propres à ce repo | `CLAUDE.md` |
| Statusline | `statusline/README.md` |
| Skills Snetor | `plugins/snetor-skills/README.md` |
| Index complet de la documentation | `docs/README.md` |
| Migrer un repo vers le standard | `docs/dated/decisions/2026-08-10-regles-de-migration-d-un-repo.md` |

## Décisions en attente

Le skill `snetor-artifact-to-app` reste une proposition : voir
`docs/dated/decisions/2026-08-04-skill-artifact-to-app.md`. Il attend le
runtime partagé des applications internes.

## Pièges du poste

Le shell de référence est PowerShell ; Git Bash est instable sur les postes
Snetor. Les variables d environnement dont Claude Code a besoin sont posées par
`scripts/deploy-claude.ps1` : ne pas les redéfinir à la main, sous peine de
masquer la valeur déployée. Les spécificités réseau du poste ne sont pas
documentées ici, ce dépôt étant public.

## Sessions parallèlles

Un worktree par tâche. Ne jamais changer la branche du checkout principal, ne
jamais pousser sur une branche dont la pull request est déjà mergée.
