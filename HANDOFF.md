# HANDOFF — snetor-ai-guidelines

**Derniere revision :** 2026-08-10

Routeur d etat, pas un journal. L historique vit dans `git log`.

## Ou on en est

Le repo distribue la configuration Claude Code de Snetor : un `CLAUDE.md`
d equipe, un style de sortie, un statusline, un script de deploiement poste,
et le plugin `snetor-skills` (quatre skills) via le marketplace Claude Code.

Le standard de documentation est livre et applique a ce repo : `docs/live/`,
`docs/dated/`, index genere, verificateur en CI.

## Prochaine action

Brancher les quatre repos applicatifs sur le workflow `check-docs.yml@v1`, dans
cet ordre : `snetor-ai-hub`, `client-matrix`, `snetor-pim`,
`azure-landing-zone`. Chaque repo fait l objet d une pull request distincte.
Le rapport du verificateur produit la liste de travail de chaque repo.

## Ou chercher

| Besoin | Fichier |
|---|---|
| Comprendre le standard de documentation | `docs/live/documentation-standard.md` |
| Cloturer une branche proprement | skill `snetor-docs-close` |
| Verifier la documentation d un repo | `scripts/check_docs.py` |
| Brancher un repo sur la CI documentaire | `.github/workflows/check-docs.yml` |
| Installer le poste d un nouveau developpeur | `README.md`, `scripts/README.md` |
| Deployer la configuration Claude Code | `scripts/deploy-claude.ps1` |
| Regles d equipe copiees sur les postes | `CLAUDE.md` |
| Statusline | `statusline/README.md` |
| Skills Snetor | `plugins/snetor-skills/README.md` |
| Index complet de la documentation | `docs/README.md` |

## Decisions en attente

Le skill `snetor-artifact-to-app` reste une proposition : voir
`docs/dated/decisions/2026-08-04-skill-artifact-to-app.md`. Il attend le
runtime partage des applications internes.

## Pieges du poste

Le shell de reference est PowerShell ; Git Bash est instable sur les postes
Snetor. Le proxy d entreprise impose un bundle de certificats : ne pas
reexporter la variable d environnement qui le designe, elle est deja posee par
le deploiement.

## Sessions parallelles

Un worktree par tache. Ne jamais changer la branche du checkout principal, ne
jamais pousser sur une branche dont la pull request est deja mergee.
