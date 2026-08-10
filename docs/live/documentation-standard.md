---
regime: live
audience: [agent, dev, newcomer]
reviewed: 2026-08-10
ttl: 180d
---

# Standard de documentation Snetor

Une documentation de repo dérape toujours de la même façon : elle grossit à
chaque session, personne ne sait plus quel fichier fait foi, et le travail en
cours devient introuvable. Ce standard existe pour que la documentation reste
petite, navigable, et honnête sur sa propre fraîcheur.

## Le principe : ranger par régime de mise à jour

Un document ne se classe pas par sujet ni par lecteur, mais par la façon dont
il vieillit.

| | `docs/live/` | `docs/dated/` |
|---|---|---|
| Promesse | c est vrai maintenant | c était vrai à cette date |
| Contenu | architecture, modèle de données, runbooks, références | décisions, audits, mesures |
| Mise à jour | on réécrit le fichier | on écrit un successeur |
| Périmer | c est un défaut à corriger | c est normal |

Un ADR ne périme pas : il déclare une décision à une date. Un runbook, si.
C est pour cela qu ils ne vivent pas dans le même dossier.

Les sous-dossiers sont libres. On en crée un quand un type dépasse cinq
fichiers, pas avant.

## Le lecteur est déclaré, pas rangé

L audience vit dans le frontmatter, jamais dans l arborescence. Ranger par
lecteur obligerait à réécrire la même règle dans chaque dossier concerné, et
une règle écrite deux fois finit toujours par se contredire.

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
---
```

Audiences : `agent`, `dev`, `newcomer`, `ops`, `business`.
Statuts `dated` : `draft`, `proposed`, `decided`, `applied`, `superseded`.

En `live`, `reviewed` est obligatoire ; `ttl` est **optionnel** et vaut `90d`
quand il est absent. Son format est `<n>d`, en jours. Ne l écrire que lorsque la
péremption réelle du document s écarte du défaut : `180d` pour une doctrine
stable, `30d` pour un runbook qui suit une infrastructure mouvante.

La distinction entre `decided` et `applied` compte : une décision prise dont
rien n est déployé est un piège classique, et le champ le rend visible dès
l en-tête.

Deux champs `dated` optionnels relient un document à son successeur :

- `supersedes` : chemin relatif à la racine du repo vers le document que
  celui-ci remplace. Le fichier cité doit exister.
- `superseded_by` : chemin relatif, obligatoire dès que `status` vaut
  `superseded`. Le fichier cité doit exister.

Ces deux champs remplacent la suppression. Un document `dated` ne se
réécrit jamais et ne s efface jamais : quand il cesse de valoir, on écrit
son successeur et on relie les deux. La chaîne reste navigable, et un
lecteur qui tombe sur l ancien document est renvoyé vers le nouveau au lieu
de croire à une information périmée. C est ce qui distingue le régime
`dated` du régime `live`, où le fichier se réécrit sur place.

## L index est généré

`docs/README.md` est produit par `scripts/check_docs.py` depuis les
frontmatters. Ne jamais l éditer à la main. Un index tenu à la main périme
toujours ; un index généré ne peut pas périmer, et aucun fichier ne peut
devenir orphelin.

## Le plan meurt, la spec est arbitrée

Le flux de travail ne change pas : brainstorming, spec, plan revu, exécution.
Ce qui change est ce qui reste après le merge.

`docs/superpowers/plans/` est gitignoré. Un plan d implémentation fait des
milliers de lignes, sert une fois, et le diff de la pull request documente
mieux que lui ce qui a été livré.

`docs/superpowers/specs/` est versionné, parce que faire relire une spec en
pull request est utile. Mais c est une zone de travail : au-delà de 30 jours,
le vérificateur bloque.

À la clôture d une branche, chaque spec reçoit un arbitrage :

- elle a tranché quelque chose de durable : la **réécrire** en décision courte
  dans `docs/dated/decisions/`, puis la supprimer ;
- elle décrit un état du système : fondre son contenu dans le fichier
  `docs/live/` concerné, puis la supprimer ;
- elle était tactique : la supprimer.

Une spec n est **ni déplacée ni copiée : réécrite**. Copier une spec de trois
cents lignes reproduit le volume qu on cherche à supprimer ; une décision utile
tient en quarante à cent lignes.

La suppression d une spec se confirme auprès de l utilisateur. Et le plan ne se
supprime qu une fois entièrement exécuté et l arbre commité : gitignoré, il n a
aucun blob git derrière lui.

## Le routeur et les tâches

`HANDOFF.md` répond à deux questions et rien d autre : où on en est, où
chercher. Plafond de 150 lignes, vérifié par la CI. Le plafond est le
mécanisme : c est lui qui force à déplacer le contenu vers sa vraie
destination au lieu de l empiler dans le fichier déjà ouvert.

`tasks/todo.md` ne contient que des items ouverts. Un item livré est
**supprimé**, pas coché : sa trace vit dans le numéro de pull request.

`tasks/lessons.md` est un journal append-only. C est l artefact le mieux tenu
de tous les repos Snetor, parce que son format est constant. Ne pas y toucher.

## Clôturer une branche

Le skill `snetor-docs-close` déroule les cinq étapes : purge des plans,
arbitrage des specs, leçons, nettoyage du todo, réécriture du routeur. Il
finit par régénérer l index et afficher le rapport du vérificateur.

## Ce que la CI refuse

Bloquant : frontmatter absent ou invalide, lien interne mort, `docs/README.md`
non régénéré, `HANDOFF.md` absent ou au-delà de 150 lignes, spec de plus de 30
jours dans la zone de travail, markdown rangé ailleurs que dans `live/`,
`dated/` ou `superpowers/`, fichier markdown illisible — encodage non UTF-8,
fichier verrouillé, ou disparu entre le parcours et la lecture.

Warning : document `live` dont le `ttl` est dépassé, document `dated` en
`draft` ou `proposed` depuis plus de 90 jours.

On bloque sur ce qui est cassé, jamais sur ce qui est vieux. Une pull request
de code refusée parce qu un runbook a quatre-vingt-dix jours, c est un check
désactivé dans la semaine.

## Brancher un repo

```yaml
# .github/workflows/docs.yml
name: docs
on: [pull_request]
jobs:
  check:
    uses: snetor/snetor-ai-guidelines/.github/workflows/check-docs.yml@v1
```

Le workflow pose un second checkout du repo standard dans `.docs-standard/`. Le
vérificateur ignore tout dossier dont le nom commence par un point, donc ce
sous-checkout — comme `.terraform` ou `.venv` — reste hors de l index et hors du
scan de liens. Le verdict est le même en local et en CI.

En local :

```
python scripts/check_docs.py --repo-root .
python scripts/check_docs.py --repo-root . --fix
```

`--today` accepte une date ISO pour figer la référence des checks de fraîcheur.
Une valeur qui n est pas une date ISO fait échouer le vérificateur, plutôt que
de retomber en silence sur la date du jour.
