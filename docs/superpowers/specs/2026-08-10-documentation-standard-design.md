# Standard de documentation Snetor — conception

**Date :** 2026-08-10
**Statut :** validé en atelier, en attente de plan d'implémentation
**Périmètre :** `snetor-ai-guidelines`, `client-matrix`, `snetor-ai-hub`, `snetor-pim`, `azure-landing-zone`, et tout repo Snetor futur
**Origine :** inventaire documentaire des quatre repos applicatifs, 2026-08-10

## 1. Problème

L'inventaire des quatre repos applicatifs relève 225 fichiers markdown pour environ 70 000 lignes. Trois pathologies expliquent ce volume et le rendent nuisible.

**Le volume vient d'un seul endroit.** Les plans et specs générés par le skill `superpowers` pèsent 69 % du corpus de `client-matrix` (43 fichiers archivés), 74 % de celui de `snetor-ai-hub` (7 plans plus 5 specs) et 48 % de celui de `snetor-pim` (12 plans archivés). Un plan d'implémentation fait de 900 à 4 200 lignes, contient du code recopié, sert une seule fois. Les sept plans de `snetor-ai-hub` portent zéro case cochée sur 538, donc ils ne documentent même pas ce qui a été livré. `azure-landing-zone` a supprimé les siens en PR #80 — 31 fichiers d'un coup — et reste le repo le plus complexe des cinq avec 40 fichiers et 11 938 lignes.

**Les index divergent et fabriquent des orphelins.** `client-matrix` a quatre index concurrents, aucun exhaustif, et 13 des 15 liens de la table « Documentation de référence » de son `README.md` sont morts. Au total 40 chemins de documents référencés n'existent plus, séquelles d'une réorganisation de `docs/` en sous-dossiers. 31 fichiers n'ont aucune référence entrante, dont le handoff du 2026-08-07, la spec du lot B et le plan du lot C — soit exactement le travail en cours, atteignable uniquement par `git log`. La table « Où chercher » de `snetor-pim` oublie le seul livrable métier du repo, le rapport d'audit qualité des données SAP. Celle de `azure-landing-zone` n'indexe ni ses quatre READMEs situés hors de `docs/`, ni ses workflows.

**L'état courant est écrit deux fois.** Dans chaque repo, un routeur de session et un fichier de tâches décrivent tous deux ce qui vient ensuite. `azure-landing-zone` cumule 701 lignes de `HANDOFF.md` et 987 lignes de `tasks/todo.md`, et la collision est si connue que les deux fichiers portent des notes croisées pour se renvoyer l'un à l'autre. La dérive du fichier de tâches a une cause précise : on coche au lieu de supprimer. `AGENTS.md` de ce repo écrit noir sur blanc « `todo.md` ouvert seulement, supprimé quand fait — pas archivé », et le fichier contient 55 items cochés avec leurs numéros de PR.

Deux constats orientent la solution. D'abord, tous les documents périmés relevés sont des documents d'état : le `README.md` de `snetor-pim` qui prescrit encore Azure Cloud Shell abandonné depuis le 6 août, `crm-roadmap.md` figé au 2026-06-08, `runbooks/pim.md` étiqueté « État (2026-06-12) », l'en-tête de `docs/architecture.md` daté du 2026-06-12 quand son corps dit 2026-08-06. À l'inverse aucun ADR n'est périmé : les neuf ADR de `azure-landing-zone` datent pour la plupart du 2026-06-16 et restent vrais, parce qu'ils déclarent une décision à une date. Le bon axe de rangement est donc le régime de mise à jour, pas l'audience.

Ensuite, `tasks/lessons.md` est le fichier le mieux tenu des quatre repos, sans exception : format constant, contenu dense, quasi zéro obsolescence, 74 entrées dans `azure-landing-zone`. C'est le seul artefact dont l'écriture soit disciplinée par un format. La leçon est que le format tient, et que la règle écrite sans mécanisme ne tient pas.

## 2. Décisions

Quatre arbitrages, validés en atelier le 2026-08-10.

**D1 — Le plan meurt, la spec est arbitrée.** Le workflow `superpowers` ne change pas : brainstorming, spec, plan revu et challengé, exécution. Le changement porte uniquement sur l'après-merge. Le plan d'implémentation n'est jamais conservé. La spec survit seulement si elle a tranché quelque chose de durable, et sous forme réécrite, jamais copiée.

**D2 — Rangement par régime de mise à jour, audience en frontmatter.** Deux régimes dans `docs/` : `live/` pour ce qui doit être vrai maintenant, `dated/` pour ce qui est vrai à sa date. L'audience est déclarée en frontmatter, pas matérialisée en dossiers. Un rangement par audience multiplierait les endroits où la même règle se réécrit, ce qui est déjà la pathologie mesurée : « Terraform s'exécute dans le VNet » est réénoncé dans 15 fichiers de `azure-landing-zone`, et le bandeau signalant l'abandon de Cloud Shell est copié mot pour mot dans trois runbooks de `snetor-pim` mais manque dans le quatrième, `consolidation.md`, qui devient de ce fait le document le plus trompeur du repo.

**D3 — Routeur et tâches séparés, avec plafond.** Le routeur répond à deux questions et rien d'autre : où on en est, où chercher. Plafond de 150 lignes. Le fichier de tâches ne contient que des items ouverts ; un item livré est supprimé, sa trace vit dans le numéro de PR. Le plafond n'est pas cosmétique : c'est lui qui force à déplacer le contenu vers sa vraie destination au lieu de l'empiler dans le fichier déjà ouvert.

**D4 — CI bloquante sur ce qui est cassé, warning sur ce qui est vieux.** La règle écrite ne suffit pas, les 55 items cochés et les 40 liens morts le démontrent. Mais bloquer une PR de code parce qu'un runbook a 90 jours garantit que le check sera désactivé dans la semaine.

## 3. Taxonomie

Structure identique dans tous les repos.

```
HANDOFF.md              routeur de session — plafond 150 lignes
CLAUDE.md               règles projet uniquement
docs/
  README.md             généré, jamais édité à la main
  live/                 doit être vrai maintenant, réécrit en place
  dated/                vrai à sa date, jamais réécrit
  superpowers/specs/    zone de travail, vidée à la clôture
  superpowers/plans/    zone de travail, non versionnée
tasks/
  todo.md               items ouverts seulement
  lessons.md            journal append-only
```

Les sous-dossiers dans `live/` et `dated/` sont autorisés mais pas imposés. On en crée un quand un type dépasse cinq fichiers : `snetor-ai-hub` n'a qu'un seul runbook et n'a pas besoin de `docs/live/runbooks/`, `azure-landing-zone` en a six et l'aura.

`HANDOFF.md` à la racine est obligatoire dans tout repo. Il est créé là où il manque : `client-matrix` et `snetor-ai-hub` n'en ont pas aujourd'hui, ce qui explique en partie leurs index concurrents. Le format un-fichier-par-session est proscrit — les sept `docs/handoffs/handoff-YYYY-MM-DD*.md` de `client-matrix`, dont deux portant la même date, sont supprimés après remontée de leur contenu encore valide dans `HANDOFF.md` ou dans le fichier `live/` concerné. Un routeur d'état n'a de sens qu'au singulier.

| | `live/` | `dated/` |
|---|---|---|
| Contenu | architecture, modèle de données, runbooks, références stables | ADR, audits, mesures, specs survivantes |
| Mise à jour | réécriture en place | jamais — on écrit un successeur |
| Obsolescence | c'est un défaut à corriger | c'est le fonctionnement normal |
| Nom de fichier | pas de date | date en préfixe |

Ce découpage supprime par construction deux cas réels. `docs/reference/fabric-reservation-verification.md` de `azure-landing-zone` est une vérification ponctuelle du 2026-06-15 rangée à côté de la référence de l'API GLPI, faute d'un dossier daté où la mettre ; le choix est désormais forcé à la création du fichier. Et `docs/reference/pim-data-model.md`, étiqueté « design en cours de validation » et figé au 2026-06-09, cohabite aujourd'hui avec des références stables ; placé en `dated/` avec `status: draft`, il ne trompe plus personne.

`docs/superpowers/plans/` est ajouté au `.gitignore`. Ce n'est pas un durcissement gratuit : c'est ce qui rend D1 automatique. Le plan vit sur le disque pendant la branche, n'est jamais commité, et il n'y a donc plus rien à purger ni à surveiller. Le rapport de volume justifie de traiter les deux dossiers différemment — dans `snetor-ai-hub`, le plan MVP fait 4 182 lignes contre 381 pour sa spec.

`docs/superpowers/specs/` reste versionné, parce que faire relire une spec en PR est un usage réel et souhaitable : la PR #9 de ce repo a mergé la spec du skill `snetor-artifact-to-app` seule, précisément pour être revue.

## 4. Frontmatter

Obligatoire sur tout fichier de `docs/live/**` et `docs/dated/**`. Exemptés : les fichiers de la racine, `tasks/**`, `docs/superpowers/**`, et tout markdown situé hors de `docs/`.

Champs communs obligatoires :

- `regime` — `live` ou `dated`, doit correspondre au dossier
- `audience` — liste non vide parmi `agent`, `dev`, `newcomer`, `ops`, `business`

Champs du régime `live` :

- `reviewed` — date ISO, obligatoire
- `ttl` — durée au format `<n>d`, optionnel, valeur par défaut `90d`

Champs du régime `dated` :

- `date` — date ISO, obligatoire
- `status` — `draft`, `proposed`, `decided`, `applied` ou `superseded`, obligatoire
- `supersedes` — chemin relatif à la racine du repo, optionnel, le fichier doit exister
- `superseded_by` — chemin relatif, obligatoire si `status: superseded`, le fichier doit exister

Champ optionnel partout : `owner`.

```yaml
---
regime: live
audience: [dev, ops]
reviewed: 2026-08-10
ttl: 90d
---
```

```yaml
---
regime: dated
audience: [dev, business]
date: 2026-08-03
status: decided
supersedes: docs/dated/decisions/ancien-slug.md
---
```

Le champ `audience` est ce qui répond au besoin — la bonne information au bon niveau de lecteur — sans dupliquer les fichiers. Un agent filtre par `grep -l "audience:.*agent"`, un nouvel arrivant lit la section `newcomer` de l'index.

La distinction entre `decided` et `applied` n'est pas de la coquetterie. `azure-landing-zone` porte un ADR `internal-apps-paved-road.md` qui est une proposition dont aucune ressource n'existe, et un runbook `internal-apps.md` de 138 lignes qui explique comment exploiter ce runtime jamais déployé. Le champ rend le piège visible dès l'en-tête.

## 5. Index généré

`docs/README.md` est produit par le script depuis les frontmatters. Il commence par un marqueur explicite :

```
<!-- GENERATED — ne pas editer. Regenerer via check_docs.py --fix -->
```

L'index est groupé par audience, puis dans chaque audience les fichiers `live` d'abord, les `dated` ensuite triés par date décroissante. Chaque ligne porte le titre, le chemin, et selon le régime la date de revue ou le statut. Un fichier déclarant deux audiences apparaît deux fois : un index est une vue, pas un rangement.

Le script indexe en outre, dans une section distincte, tout `**/README.md` situé hors de `docs/`, sans exiger de frontmatter. Cela comble un trou identifié : rien n'indexe aujourd'hui les quatre READMEs hors `docs/` de `azure-landing-zone`, dont `tests/pim-sql/README.md` et `modules/pim/scripts/README.md`, tous deux orphelins et le second porteur d'un lien mort.

C'est la pièce qui résout la pathologie la plus coûteuse. Un index tenu à la main périme toujours ; un index généré ne peut pas périmer, et il n'y a plus d'orphelin possible puisque tout fichier porteur d'un frontmatter y figure.

## 6. Cycle de vie d'une clôture de branche

Pendant la session, rien ne change. À la clôture, cinq étapes dans cet ordre.

**Étape 1.** Le contenu de `docs/superpowers/plans/` est supprimé du disque. Aucune exception, aucun archivage. Sa trace vit dans le diff de la PR, qui est plus fiable que le plan lui-même.

**Étape 2.** Chaque spec de `docs/superpowers/specs/` reçoit un arbitrage, avec trois sorties possibles. Si elle a tranché quelque chose qui survivra au changement, elle est réécrite en ADR court dans `docs/dated/decisions/`. Si elle décrit un état de système, son contenu est fondu dans le fichier `live/` concerné — modèle de données ou architecture — puis elle est supprimée. Si elle est purement tactique, elle est supprimée.

Le mot déterminant est *réécrite*, pas *déplacée*. Copier une spec de 300 lignes dans `dated/decisions/` reproduit le volume qu'on cherche à supprimer. Un ADR utile fait 40 à 100 lignes : `acr-acces-public-dev.md` de `azure-landing-zone` tranche en 103 lignes pourquoi les quatre ACR restent publics en environnement DEV, chiffre à 160 € par mois le coût de les fermer, et c'est complet. Les 23 specs archivées de `client-matrix` font de 69 à 353 lignes chacune. Réécrire divise par trois à cinq.

**Étape 3.** Les leçons de la session sont ajoutées à `tasks/lessons.md`, au format existant. Rien ne change ici, ce fichier fonctionne.

**Étape 4.** Les items livrés sont supprimés de `tasks/todo.md`. Pas cochés, supprimés. Ce qui rend la règle enfin applicable, c'est que la trace de l'achèvement a désormais un autre foyer : le numéro de PR. Aujourd'hui on coche parce que supprimer donne l'impression de perdre la preuve du travail.

**Étape 5.** `HANDOFF.md` est réécrit sous 150 lignes, avec l'état courant et la table « où chercher ».

Le script est ensuite exécuté avec `--fix` pour régénérer l'index, et son rapport est affiché.

Appliqué au corpus actuel, ce cycle retire environ 35 000 des 70 000 lignes : le volume documentaire des quatre repos applicatifs est divisé par deux.

## 7. Distribution

Trois niveaux, une seule source par règle.

**Niveau 1 — `~/.claude/CLAUDE.md`, environ 30 lignes.** Les invariants : structure des dossiers, les deux régimes, frontmatter obligatoire, index généré, les cinq étapes de clôture, plafond du routeur. Assez pour qu'un agent applique la méthode sans rien ouvrir d'autre, dans n'importe quel repo. Un renvoi vers la doctrine pour le reste.

Le `CLAUDE.md` de ce repo a déjà dérivé : il en porte une version de 111 lignes, le `~/.claude/CLAUDE.md` réel en fait 146, avec un bloc « Contexte — Head of AI @ Snetor » et une section « Git Hygiene » jamais réinjectés. Le mode de distribution étant un `Copy-Item` manuel, rien ne resynchronise. Ajouter la mécanique documentaire sans traiter cette dérive créerait une troisième version divergente.

On scinde donc en deux fichiers reliés par un import :

```
~/.claude/CLAUDE.md              contexte personnel — jamais ecrase
~/.claude/snetor-guidelines.md   copie par deploy-claude.ps1 — ecrase a chaque fois
```

Le premier importe le second par la directive `@~/.claude/snetor-guidelines.md`. La syntaxe d'import, sa disponibilité au niveau utilisateur, le support de `~`, la limite de quatre niveaux d'imbrication et le fait que les imports soient ignorés à l'intérieur des blocs de code sont vérifiés dans la documentation officielle de Claude Code. Le chargement effectif se contrôle par `/context`, section « Memory files ».

`deploy-claude.ps1` ne touche plus que le second fichier. Le bloc personnel ne peut donc plus être perdu, ni se retrouver dans un repo public, et un autre développeur Snetor qui installe le pack ne se déclare pas Head of AI.

**Niveau 2 — le repo `snetor-ai-guidelines`.**

```
docs/live/documentation-standard.md          la doctrine complete
scripts/check_docs.py                        environ 150 lignes
.github/workflows/check-docs.yml             workflow reutilisable (on: workflow_call)
plugins/snetor-skills/skills/snetor-docs-close/SKILL.md
```

Le repo étant public, son workflow réutilisable est appelable depuis n'importe quel repo, y compris privé, sans configuration d'accès. Le marketplace Claude Code est déjà installé en `scope: managed` avec `autoUpdate: true`, donc le skill parvient seul aux postes.

La doctrine complète est destinée aux humains. Les 30 lignes du niveau 1 suffisent à un agent, pas à un développeur qui doit comprendre pourquoi il supprime un plan de 4 000 lignes.

**Niveau 3 — le `CLAUDE.md` de chaque repo applicatif.** Règles projet uniquement. Le bloc « Workflow Orchestration », déjà présent dans le global, est supprimé des quatre repos applicatifs : environ 110 lignes par repo relues à chaque session pour rien. Le `CLAUDE.md` de `snetor-ai-guidelines` est le seul à conserver ce bloc, puisqu'il est par vocation le gabarit du niveau 1 et non un fichier de règles projet. Ce qui reste est précieux et doit être préservé intégralement — par exemple, dans `azure-landing-zone`, la règle « vérifier avant d'affirmer : un plan vert prouve le déploiement, jamais l'effet », avec son exemple chiffré d'un `min_replicas=0` inopérant pendant six semaines à 196 € par mois.

**Versionnement.** Le repo n'a aujourd'hui aucun tag git ni release ; le seul versionnement est le `1.6.0` des manifests de plugin. Pour un workflow réutilisable, c'est insuffisant : sans tag, les repos consommateurs pinnent sur `@main` et la première modification du script casse leur CI simultanément. On crée donc un tag mobile `v1`, que les repos consomment ainsi :

```yaml
uses: snetor/snetor-ai-guidelines/.github/workflows/check-docs.yml@v1
```

## 8. Ce que vérifie la CI

Bloquants :

1. Frontmatter absent ou invalide dans `docs/live/**` ou `docs/dated/**` — champ requis manquant, valeur hors énumération, date non ISO, `regime` incohérent avec le dossier, `supersedes` ou `superseded_by` pointant sur un fichier inexistant.
2. Lien markdown interne mort — tout lien relatif non HTTP pointant sur un fichier inexistant, cherché dans l'ensemble des markdown du repo, y compris la racine, `tasks/` et hors `docs/`.
3. `docs/README.md` différent de la sortie générée.
4. `HANDOFF.md` absent, ou de plus de 150 lignes.
5. Spec de `docs/superpowers/specs/` datant de plus de 30 jours, d'après la date de son nom de fichier. Une spec plus ancienne signifie soit un chantier mort, soit une clôture oubliée ; les deux méritent un blocage. Cette règle remplace un check plus subtil sur le diff de la PR, écarté pour son risque de faux positifs.
6. Markdown dans `docs/` en dehors de `live/`, `dated/`, `superpowers/` et du `README.md` généré, ce qui interdit le retour au fourre-tout.

Warnings :

7. Fichier `live/` dont `reviewed` plus `ttl` est dépassé.
8. Fichier `dated/` en `status: draft` ou `proposed` depuis plus de 90 jours. Cette règle aurait signalé `pim-data-model.md` et `pim-sap-source-tables.md` figés au 2026-06-09, ainsi que les cinq ADR de `azure-landing-zone` non tranchés ou non appliqués.

Le script s'exécute sur un runner GitHub public : c'est du markdown, il n'a pas besoin du job Container Apps dans le VNet utilisé par `azure-landing-zone` pour Terraform.

## 9. Migration

Le pilote est `snetor-ai-guidelines` lui-même. Il porte ses propres 1 301 lignes de plans `superpowers`, et sa spec `2026-08-04-artifact-to-app-skill-design.md`, 288 lignes non implémentées, est un cas d'école de `dated/` en `status: proposed`. Le repo qui porte la méthode l'applique d'abord à lui-même : risque nul, et cela valide le script sur un corpus de six fichiers.

| Rang | Repo | Fichiers markdown | Lignes à purger | Motif du rang |
|---|---|---|---|---|
| 1 | `snetor-ai-guidelines` | 6 dans `docs/` | 1 301 | pilote, porte la méthode |
| 2 | `snetor-ai-hub` | 22 | 8 754 | petit, risque faible |
| 3 | `client-matrix` | 89 | 17 055 | pire cas, gain maximal |
| 4 | `snetor-pim` | 57 versionnés, 17 non versionnés | 9 835 | plus `.superpowers/sdd/` à nettoyer du poste |
| 5 | `azure-landing-zone` | 40 | 0 | déjà purgé ; seuls structure et frontmatter changent |

`azure-landing-zone` vient en dernier parce que c'est le repo le plus sensible : son `CLAUDE.md` porte 757 lignes de règles critiques, et une erreur coûte plus cher dans un repo dont la CI applique de l'infrastructure.

Point spécifique à `snetor-pim` : ses 17 fichiers de `.superpowers/sdd/` non versionnés sont des résidus d'une session de fin juillet dont le plan a depuis été déclaré caduc. Ils sont gitignorés, donc invisibles en revue, mais présents sur le disque et lisibles par un agent qui parcourt le repo. C'est un risque concret de relecture d'un plan périmé : ils doivent être supprimés du poste, pas seulement du versionnement.

**Règle de datation à la migration.** Le champ `reviewed` d'un fichier migré vers `live/` reçoit la dernière date de vérité connue du document — celle de son en-tête « Dernière mise à jour » ou équivalent — et non la date du jour. Renseigner la date du jour sur le `README.md` de `snetor-pim` qui prescrit encore Cloud Shell serait un mensonge inscrit dans le frontmatter. La conséquence est voulue : le warning de fraîcheur se déclenche immédiatement sur les documents périmés, et la migration produit ainsi la liste chiffrée de la dette documentaire.

## 10. Hors périmètre

La migration déplace les fichiers, ajoute les frontmatters et purge les plans. Elle **ne corrige pas** le contenu périmé. Le `README.md` de `snetor-pim` qui prescrit Cloud Shell, les mentions de Next.js 15 alors que les repos sont en 16.2.4, le `ci.yml` inexistant cité par le `CLAUDE.md` de `snetor-pim`, les runbooks de `snetor-pim` bloqués depuis le 22 juillet : autant de corrections de fond, à traiter repo par repo, chacune dans sa propre PR. Les mêler à la migration structurelle transformerait un chantier de quelques jours en chantier de plusieurs semaines.

Sont également hors périmètre la refonte du contenu de `tasks/lessons.md`, qui fonctionne, et la renumérotation de ses entrées dans `azure-landing-zone`, dont la numérotation est cassée mais sert de référence croisée depuis `CLAUDE.md` et `HANDOFF.md`.

## 11. Critères de succès

Chacun est vérifiable par une commande.

1. `python scripts/check_docs.py` sort en code 0 sur les cinq repos.
2. Le volume markdown cumulé des quatre repos applicatifs passe sous 40 000 lignes, contre environ 70 000 au 2026-08-10.
3. Zéro orphelin : tout markdown de `docs/live/` et `docs/dated/` figure dans le `docs/README.md` généré.
4. Zéro lien interne mort dans les cinq repos, contre 40 dans `client-matrix` seul aujourd'hui.
5. `HANDOFF.md` est à 150 lignes ou moins dans les cinq repos.
6. `/context` affiche `snetor-guidelines.md` dans les fichiers mémoire chargés.
7. Le bloc « Workflow Orchestration » n'apparaît plus dans aucun `CLAUDE.md` de repo.
8. Le workflow `check-docs.yml` est appelé via `@v1` par les cinq repos et son exécution est visible dans leurs PR.
