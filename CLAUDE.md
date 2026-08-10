# snetor-ai-guidelines — règles projet

Ce repo distribue la configuration Claude Code de Snetor. Les règles d équipe
copiées sur les postes vivent dans `claude-config/snetor-guidelines.md`, pas
ici : ce fichier ne contient que ce qui concerne le travail **dans** ce repo.

## Point d entrée

Lire `HANDOFF.md` en premier, puis `docs/README.md` pour l index.

## Ce dépôt est public

Le `HANDOFF.md` d un repo public ne porte **ni inventaire de repos internes, ni
topologie réseau, ni posture de sécurité du poste**. Dire ce qui vient ensuite
sans dresser la carte. Le standard impose un routeur à la racine de tout repo :
dans un repo public, ce routeur est lu par n importe qui. Cela vaut aussi pour
`README.md` et les fichiers de `docs/`.

## Ce qui est distribué et comment

| Artefact | Destination sur le poste | Vecteur |
|---|---|---|
| `claude-config/snetor-guidelines.md` | `~/.claude/snetor-guidelines.md` | `scripts/deploy-claude.ps1` |
| `output-styles/*.md` | `~/.claude/output-styles/` | `scripts/deploy-claude.ps1` |
| `plugins/snetor-skills/` | cache de plugins | marketplace Claude Code |
| `statusline/` | `~/.claude/` | `statusline/install.ps1` |

Le `CLAUDE.md` personnel de l utilisateur n est **jamais** écrasé : il importe
`@~/.claude/snetor-guidelines.md`. Toute règle d équipe va dans le fichier
importé, jamais dans le `CLAUDE.md` du poste.

## Conséquences à ne pas oublier

Modifier `claude-config/snetor-guidelines.md` change le comportement de tous
les agents Snetor. Modifier un `SKILL.md` du plugin le propage à tous les
postes, le marketplace étant en mise à jour automatique. Dans les deux cas,
bumper la version dans `plugins/snetor-skills/.claude-plugin/plugin.json` et
`.claude-plugin/marketplace.json`.

Le workflow `.github/workflows/check-docs.yml` est consommé par les autres
repos via le tag `v1`. Toute modification du vérificateur exige de redéplacer
ce tag, sinon les repos consommateurs ne voient pas le changement.

## Vérifier avant d affirmer

Un test vert prouve que le code fait ce que le test dit, pas que le poste est
configuré. Pour toute affirmation sur la configuration d un poste, montrer la
sortie de `/context` ou du script concerné.

## Documentation

Ce repo applique le standard qu il définit. Voir
`docs/live/documentation-standard.md`. Avant de clôturer une branche, utiliser
le skill `snetor-docs-close`.
