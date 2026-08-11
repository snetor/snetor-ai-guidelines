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
| `claude-config/workflow.md` | chaque profil `.claude*` / `.codex*` du poste, entreprise et personnel | `scripts/deploy-claude.ps1` |
| `claude-config/snetor-guidelines.md` | profils d entreprise seulement (`.claude`, `.codex`) | `scripts/deploy-claude.ps1` |
| `output-styles/*.md` | `~/.claude/output-styles/` | `scripts/deploy-claude.ps1` |
| `plugins/snetor-skills/` | cache de plugins | marketplace Claude Code |
| `statusline/` | `~/.claude/` | `statusline/install.ps1` |

Deux familles, deux mécanismes : la famille Claude Code (fichier `CLAUDE.md`)
charge les règles par la directive d import `@` ; la famille Codex (fichier
`AGENTS.md`) n a pas d équivalent et régénère son fichier d instructions par
concaténation à chaque déploiement. La phrase qui suit sur l import ne vaut
que pour la famille Claude Code : le `CLAUDE.md` personnel de l utilisateur
n est **jamais** écrasé en entier, seuls les imports manquants y sont ajoutés.
Toute règle d équipe va dans un fichier importé ou régénéré, jamais écrite en
dur dans le `CLAUDE.md` du poste. Détail des deux mécanismes et de la règle de
portée entreprise/personnel : `README.md`, section installation.

## Conséquences à ne pas oublier

Modifier `claude-config/snetor-guidelines.md` change le comportement de tous
les agents Snetor d entreprise. Modifier `claude-config/workflow.md` change
aussi le comportement des profils **personnels**, ce qui n était pas le cas
avant ce découpage en deux fichiers. Modifier un `SKILL.md` du plugin le
propage à tous les postes, le marketplace étant en mise à jour automatique.
Dans les deux cas, bumper la version dans
`plugins/snetor-skills/.claude-plugin/plugin.json` et
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
