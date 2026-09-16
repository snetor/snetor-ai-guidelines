---
regime: dated
audience: [dev, ops, agent]
date: 2026-09-16
status: proposed
---

# Outiller les montées de version du fork Twenty

> **Objet** : rendre la prochaine montée de version plus rapide et plus sûre, à partir de ce que
> celle du 2026-09-14/16 a réellement coûté.
> **Mesuré le** : 2026-09-16, sur la montée `twenty/v2.30.0` → `twenty/v2.39.0`.
> **Statut** : design validé avec l'owner le 2026-09-16, niveau « C » retenu, mesure 6 corrigée
> après qu'il a signalé un système de veille existant.

---

## 1. Ce que la montée a coûté

Commencée le 2026-09-14 vers 21 h, migration réussie le 2026-09-16 à 08 h 02 : **environ 35 heures
calendaires** pour un chantier d'une demi-journée. Six pièges, dont **cinq qu'un programme peut
refuser**.

| Piège | Coût | Nature |
|---|---|---|
| `nx build twenty-shared` bloqué sur son daemon — aucun log, aucun CPU | ~11 h de latence nocturne | variable d'environnement |
| Quatre échecs de `az containerapp job start --command "a","b"` — `az` n'accepte qu'UNE valeur, le conteneur rend `Failed` sans un log | ~1 h 30 | geste refusable |
| `citext` posée en CLI, effacée par mon propre `terraform apply` **minutes avant** le job | ~40 min + un cycle de migration | geste refusable |
| Squash de la PR #17 → merge-base calculé 3 mois trop tôt, **2 714 conflits fantômes** au lieu de 14 | ~20 min | geste refusable |
| Jeton Azure expiré deux fois en pleine séquence | ~20 min + deux interruptions de l'owner | contrôle au démarrage |
| `tasks/lessons.md` au plafond de 300 lignes, condensé à la main | ~25 min | **déjà outillé, non utilisé** |

Le dernier est le plus instructif : la skill `snetor-lessons-to-guardrails` existe, et son
déclencheur dit « when `tasks/lessons.md` nears its 300-line cap ». Elle n'a pas été invoquée. Une
partie du problème n'est pas un manque d'outil, c'est de ne pas l'avoir cherché.

### L'état de départ

- `snetor-ai-guidelines` porte `guard.py` (**31 tests**), `worktree_memory.py`, et huit skills.
- `client-matrix` et `snetor/twenty` n'ont **aucun** `.claude/settings.json` versionné — seulement
  un `settings.local.json` avec un `outputStyle`. Tout le garde-fou est global.

C'est là qu'est la place : le garde-fou global ne peut pas porter des règles propres à un dépôt.

---

### Deux capacités à vérifier avant d'exécuter

Ce design s'appuie sur deux mécanismes de Claude Code relevés dans un inventaire, **non testés sur
ce poste** :

- **`env` dans `.claude/settings.json`** (mesure 1) — donné comme stable.
- **`paths:` en frontmatter de `.claude/rules/*.md`** (mesure 3) — donné comme plus récent.

La première tâche du plan est de les vérifier chacune par un essai minimal. Si l'une n'existe pas
sous cette forme, sa mesure change de moyen, pas d'objectif : la mesure 1 retombe sur une variable
posée dans le script de build, la mesure 3 sur une section de `CLAUDE.md`. **Ne pas écrire les six
mesures avant d'avoir confirmé ces deux points.**

## 2. Les six mesures

### Mesure 1 — `NX_DAEMON=false` par variable d'environnement de dépôt

**Piège visé** : le build bloqué 11 heures.

`.claude/settings.json` accepte une clé `env`. Une ligne versionnée dans le fork :

```json
{ "env": { "NX_DAEMON": "false" } }
```

Aucune logique, aucune maintenance, et le piège le plus coûteux de la session disparaît. C'est la
mesure au meilleur rapport coût/effet du lot.

⚠️ À écrire dans `snetor/twenty`, donc dans un fichier que le prochain merge amont verra. Comme
tout fichier **ajouté** par le fork, il ne peut pas entrer en conflit — mais il doit figurer dans
l'inventaire de `docs/snetor/FORK.md`, sans quoi personne ne saura pourquoi il est là.

### Mesure 2 — des règles de garde-fou, décidées par la skill et non à l'instinct

**Pièges visés** : CLI contre Terraform, virgule dans `--command`, généalogie perdue.

**Le geste n'est pas d'écrire trois motifs.** C'est de faire passer les leçons du 2026-09-16 par
`snetor-lessons-to-guardrails`, dont c'est exactement le métier : trier chaque leçon en *geste*
(hook `PreToolUse`), *invariant* (test), *fait d'environnement* (une phrase dans `CLAUDE.md`) ou
*jugement* (reste en prose).

Les trois candidats, avec l'incident qui les justifie :

| Candidat | Incident |
|---|---|
| `az … parameter set` sur une ressource déclarée en Terraform | `citext` effacée par l'apply suivant |
| `az containerapp job start` avec une virgule dans `--command`/`--args` | quatre jobs `Failed` sans un seul log |
| `git merge twenty/vX.Y.Z` quand `git merge-base` remonte à plus d'un mois | 2 714 conflits fantômes |

C'est la skill qui tranche lesquels deviennent des hooks. Chaque règle retenue arrive avec **son
test**, comme les 31 existants — c'est la forme du dépôt, elle ne se discute pas.

### Mesure 3 — des règles chargées par chemin

**Nature** : prévention, pas blocage.

`.claude/rules/*.md` accepte un frontmatter `paths:`. Un fichier chargé **seulement** quand la
session touche les fichiers concernés :

```yaml
---
paths:
  - "modules/twenty/**"
  - "environments/*/*.tf"
---
```

C'est le bon endroit pour « ce que Terraform gère ne se modifie jamais en CLI » : la règle apparaît
au moment précis où elle sert, et ne pèse sur aucune autre session. Elle complète la mesure 2 —
le hook refuse le geste, la règle explique pourquoi avant qu'on l'essaie.

### Mesure 4 — skill `snetor-twenty-upgrade`

**Nature** : la procédure de `FORK.md`, rendue exécutable.

⚠️ **C'est la mesure dont l'utilité est la moins établie, et elle est traitée en dernier.**
`docs/snetor/FORK.md` porte déjà la carte et la checklist ; une skill écrite pour soi-même se
périme vite. Elle est retenue parce que l'owner l'a demandée dans le niveau C, à une condition
explicite : **si, une fois les cinq autres mesures en place, elle paraît redondante, on le dit et
on ne l'écrit pas.** Tenir un périmètre n'est pas une raison d'écrire du code.

Si elle est écrite, elle porte la séquence : vérifier la généalogie, compter les migrations, lancer
les quatre sentinelles, la checklist d'image (`--target twenty`, `az acr build`), l'ordre des
redémarrages (serveur **puis** Redis), et la recette navigateur. Elle tourne en `context: fork`
pour ne pas encombrer la session principale.

### Mesure 5 — contrôle du jeton Azure au démarrage

**Piège visé** : deux interruptions de l'owner, dont une nuit entière perdue.

Un hook `SessionStart` qui lance `az account show` et prévient si le jeton est absent ou proche de
l'expiration. Il **ne bloque pas** — une session de lecture de code n'a pas besoin d'Azure. Il
informe, pour qu'une séquence longue ne démarre pas sur un jeton qui va tomber.

⚠️ Le contrôle doit être **silencieux quand tout va bien**. Un hook qui parle à chaque démarrage
devient un bruit qu'on cesse de lire — c'est le même mécanisme qui a rendu `lessons.md` illisible
à 3 000 lignes.

### Mesure 6 — enrichir l'issue de veille (corrigée après relecture de l'owner)

**La proposition initiale était un doublon.** `azure-landing-zone/.github/workflows/upstream-versions.yml`
existe depuis le 2026-08-06 : il tourne tous les lundis à 7 h 30 UTC, compare les versions déployées
à l'amont, et ouvre **une issue par composant**. Son en-tête explique même pourquoi il n'ouvre pas
de PR — un raisonnement plus fin que ce qui était proposé.

**Ce qui manque n'est pas le système, c'est ce que l'issue dit.** Elle annonce « N versions
mineures de retard ». Or le nombre de versions ne dit **rien** du coût. Sur cette montée :

```
121 commandes de montée sur 9 paliers    ← le vrai coût, absent de l'issue
17 fichiers du fork touchés par l'amont  ← dont 4 supprimés
3 points d'ancrage disparus sur 5        ← une réécriture, pas un merge
```

Les trois ont été mesurés à la main. S'ils figuraient dans l'issue, la décision « monter maintenant
ou attendre » se prendrait sur des chiffres.

Greffe : `scripts/check-upstream-versions.py`, là où l'écart est déjà calculé. Trois mesures `git` :

```
git diff --name-status <actuelle> <cible> -- '**/upgrade-version-command/**'   → nb de commandes
comm -12 <fichiers du fork> <fichiers changés par l'amont>                     → intersection
git diff --diff-filter=D <actuelle> <cible> -- <fichiers patchés par le fork>  → ancrages disparus
```

⚠️ Ces mesures demandent de cloner le fork dans le job de veille, ce qu'il ne fait pas aujourd'hui.
C'est le seul coût réel de cette mesure, et il est à instruire avant de promettre les trois chiffres.

---

## 3. Répartition et ordre

| Dépôt | Mesures |
|---|---|
| `snetor-ai-guidelines` | 2 (garde-fou + tests), 4 (skill), 5 (hook `SessionStart`) |
| `snetor/twenty` | 1 (`settings.json`), 3 (`.claude/rules/`) |
| `azure-landing-zone` | 6 (script de veille) |

**Ordre d'exécution**, du plus rentable au plus incertain :

1. Mesure 1 — une ligne, effet immédiat
2. Mesure 2 — via la skill, avec ses tests
3. Mesure 5 — hook court, silencieux au vert
4. Mesure 3 — règles par chemin
5. Mesure 6 — après avoir instruit le coût du clone dans le job
6. Mesure 4 — **en dernier, et seulement si elle paraît encore utile**

Une branche par dépôt, une PR par sujet.

---

## 4. Critères de vérification

| # | Critère | Preuve exigée |
|---|---|---|
| 1 | Les règles de garde-fou refusent les gestes visés | Un test par règle, dans `tests/test_guard.py`, sur le modèle des 31 existants |
| 2 | Aucune règle ne refuse un geste légitime | La suite complète passe — un faux positif coûte plus cher que le piège qu'il couvre |
| 3 | `NX_DAEMON=false` est effectif | `nx build twenty-shared` aboutit sans variable passée à la main |
| 4 | Le hook de jeton est silencieux au vert | Démarrage avec un jeton valide : aucune sortie |
| 5 | L'issue de veille porte les trois chiffres | Un `workflow_dispatch` sur un écart connu |
| 6 | La doc ne dit pas deux fois la même chose | Ce qui devient un hook **sort** de `lessons.md` — c'est le seul mouvement qui allège la doctrine et durcit la pratique |

---

## 5. Risques

| Risque | Gravité | Traitement |
|---|---|---|
| Un garde-fou trop large refuse un geste légitime et se fait contourner | 🔴 un garde qu'on contourne ne protège plus rien | Motifs étroits, un test par règle, et le message cite l'incident — jamais « interdit » seul |
| La skill de la mesure 4 double `FORK.md` et se périme | 🟠 dette de doc | Traitée en dernier, avec autorisation explicite de ne pas l'écrire |
| Le hook de jeton devient bruyant | 🟠 on cesse de lire les hooks | Silencieux au vert, testé comme tel |
| La mesure 6 demande de cloner le fork dans la veille | 🟠 coût CI | À instruire avant de promettre les chiffres |
| L'outillage devient un projet en soi | 🟠 il sert les montées, il n'est pas le sujet | Six mesures, pas une de plus, et la 4 peut sauter |
