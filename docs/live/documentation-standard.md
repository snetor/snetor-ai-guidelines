---
regime: live
audience: [agent, dev, newcomer]
reviewed: 2026-08-10
ttl: 180d
---

# Standard de documentation Snetor

Une documentation de repo derape toujours de la meme facon : elle grossit a
chaque session, personne ne sait plus quel fichier fait foi, et le travail en
cours devient introuvable. Ce standard existe pour que la documentation reste
petite, navigable, et honnete sur sa propre fraicheur.

## Le principe : ranger par regime de mise a jour

Un document ne se classe pas par sujet ni par lecteur, mais par la facon dont
il vieillit.

| | `docs/live/` | `docs/dated/` |
|---|---|---|
| Promesse | c est vrai maintenant | c etait vrai a cette date |
| Contenu | architecture, modele de donnees, runbooks, references | decisions, audits, mesures |
| Mise a jour | on reecrit le fichier | on ecrit un successeur |
| Perimer | c est un defaut a corriger | c est normal |

Un ADR ne perime pas : il declare une decision a une date. Un runbook, si.
C est pour cela qu ils ne vivent pas dans le meme dossier.

Les sous-dossiers sont libres. On en cree un quand un type depasse cinq
fichiers, pas avant.

## Le lecteur est declare, pas range

L audience vit dans le frontmatter, jamais dans l arborescence. Ranger par
lecteur obligerait a reecrire la meme regle dans chaque dossier concerne, et
une regle ecrite deux fois finit toujours par se contredire.

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

La distinction entre `decided` et `applied` compte : une decision prise dont
rien n est deploye est un piege classique, et le champ le rend visible des
l en-tete.

## L index est genere

`docs/README.md` est produit par `scripts/check_docs.py` depuis les
frontmatters. Ne jamais l editer a la main. Un index tenu a la main perime
toujours ; un index genere ne peut pas perimer, et aucun fichier ne peut
devenir orphelin.

## Le plan meurt, la spec est arbitree

Le flux de travail ne change pas : brainstorming, spec, plan revu, execution.
Ce qui change est ce qui reste apres le merge.

`docs/superpowers/plans/` est gitignore. Un plan d implementation fait des
milliers de lignes, sert une fois, et le diff de la pull request documente
mieux que lui ce qui a ete livre.

`docs/superpowers/specs/` est versionne, parce que faire relire une spec en
pull request est utile. Mais c est une zone de travail : au-dela de 30 jours,
le verificateur bloque.

A la cloture d une branche, chaque spec recoit un arbitrage :

- elle a tranche quelque chose de durable : la **reecrire** en decision courte
  dans `docs/dated/decisions/`, puis la supprimer ;
- elle decrit un etat du systeme : fondre son contenu dans le fichier
  `docs/live/` concerne, puis la supprimer ;
- elle etait tactique : la supprimer.

Reecrire, pas deplacer. Copier une spec de trois cents lignes reproduit le
volume qu on cherche a supprimer ; une decision utile tient en quarante a cent
lignes.

## Le routeur et les taches

`HANDOFF.md` repond a deux questions et rien d autre : ou on en est, ou
chercher. Plafond de 150 lignes, verifie par la CI. Le plafond est le
mecanisme : c est lui qui force a deplacer le contenu vers sa vraie
destination au lieu de l empiler dans le fichier deja ouvert.

`tasks/todo.md` ne contient que des items ouverts. Un item livre est
**supprime**, pas coche : sa trace vit dans le numero de pull request.

`tasks/lessons.md` est un journal append-only. C est l artefact le mieux tenu
de tous les repos Snetor, parce que son format est constant. Ne pas y toucher.

## Cloturer une branche

Le skill `snetor-docs-close` deroule les cinq etapes : purge des plans,
arbitrage des specs, lecons, nettoyage du todo, reecriture du routeur. Il
finit par regenerer l index et afficher le rapport du verificateur.

## Ce que la CI refuse

Bloquant : frontmatter absent ou invalide, lien interne mort, `docs/README.md`
non regenere, `HANDOFF.md` absent ou au-dela de 150 lignes, spec de plus de 30
jours dans la zone de travail, markdown range ailleurs que dans `live/`,
`dated/` ou `superpowers/`.

Warning : document `live` dont le `ttl` est depasse, document `dated` en
`draft` ou `proposed` depuis plus de 90 jours.

On bloque sur ce qui est casse, jamais sur ce qui est vieux. Une pull request
de code refusee parce qu un runbook a quatre-vingt-dix jours, c est un check
desactive dans la semaine.

## Brancher un repo

```yaml
# .github/workflows/docs.yml
name: docs
on: [pull_request]
jobs:
  check:
    uses: snetor/snetor-ai-guidelines/.github/workflows/check-docs.yml@v1
```

En local :

```
python scripts/check_docs.py --repo-root .
python scripts/check_docs.py --repo-root . --fix
```
