# HANDOFF — snetor-ai-guidelines

**Derniere revision :** 2026-08-10

Routeur d etat, pas un journal. L historique vit dans `git log`.

## Ou on en est

Le repo distribue la configuration Claude Code de Snetor : les regles d equipe
de `claude-config/`, importees dans chaque session depuis le `CLAUDE.md`
personnel du poste, un style de sortie, un statusline, un script de deploiement
poste, et le plugin `snetor-skills` (quatre skills) via le marketplace Claude
Code.

Le standard de documentation est livre et applique a ce repo : `docs/live/`,
`docs/dated/`, index genere, verificateur en CI.

## Prochaine action

Brancher les repos applicatifs internes sur le workflow `check-docs.yml@v1`,
une pull request par repo. Le rapport du verificateur produit la liste de
travail de chacun. L ordre de passage et le perimetre restant se suivent hors
de ce depot, qui est public.

## Ou chercher

| Besoin | Fichier |
|---|---|
| Comprendre le standard de documentation | `docs/live/documentation-standard.md` |
| Cloturer une branche proprement | skill `snetor-docs-close` |
| Verifier la documentation d un repo | `scripts/check_docs.py` |
| Brancher un repo sur la CI documentaire | `.github/workflows/check-docs.yml` |
| Installer le poste d un nouveau developpeur | `README.md`, `scripts/README.md` |
| Deployer la configuration Claude Code | `scripts/deploy-claude.ps1` |
| Regles d equipe chargees dans chaque session | `claude-config/snetor-guidelines.md` |
| Regles de travail propres a ce repo | `CLAUDE.md` |
| Statusline | `statusline/README.md` |
| Skills Snetor | `plugins/snetor-skills/README.md` |
| Index complet de la documentation | `docs/README.md` |

## Decisions en attente

Le skill `snetor-artifact-to-app` reste une proposition : voir
`docs/dated/decisions/2026-08-04-skill-artifact-to-app.md`. Il attend le
runtime partage des applications internes.

## Pieges du poste

Le shell de reference est PowerShell ; Git Bash est instable sur les postes
Snetor. Les variables d environnement dont Claude Code a besoin sont posees par
`scripts/deploy-claude.ps1` : ne pas les redefinir a la main, sous peine de
masquer la valeur deployee. Les specificites reseau du poste ne sont pas
documentees ici, ce depot etant public.

## Sessions parallelles

Un worktree par tache. Ne jamais changer la branche du checkout principal, ne
jamais pousser sur une branche dont la pull request est deja mergee.
