---
name: snetor-docs-close
description: >
  Cloture proprement une branche dans un repo Snetor en appliquant le standard de
  documentation - purge le plan d implementation, arbitre chaque spec vers sa destination
  durable, consigne les lecons, nettoie les items livres du todo, reecrit le routeur
  HANDOFF.md sous 150 lignes, puis regenere l index et lance le verificateur.
  USE THIS SKILL avant d ouvrir ou de merger une pull request dans un repo Snetor, et des
  que l utilisateur dit qu un chantier est termine, livre, ou pret a merger
  ("on cloture", "c est fini", "prepare la PR", "nettoie la doc", "close the branch").
  Ne pas utiliser pour rediger une spec ou un plan - c est le role des skills
  brainstorming et writing-plans.
---

# Cloture de branche — standard de documentation Snetor

Doctrine complete : `docs/live/documentation-standard.md` du repo
`snetor-ai-guidelines`.

Deroule les cinq etapes dans l ordre. Ne pas en sauter une : chacune retire du
volume que la suivante n aura pas a trier.

## Condition d entree — a etablir avant la moindre suppression

Ce skill detruit des fichiers que git ne peut pas rendre. Il ne demarre que si
les deux points suivants sont **etablis**, pas supposes :

1. **Le plan est entierement execute.** Toutes ses taches sont livrees, aucune
   n est en attente ni en cours. Relire le plan et le confronter a ce qui est
   reellement dans l arbre — ne pas se fier a un souvenir de session.
2. **L arbre de travail est commite.** `git status --porcelain` ne renvoie
   rien.

Si l un des deux est faux, **s arreter et le dire** a l utilisateur : nommer ce
qui reste a faire ou a commiter, et ne rien supprimer, ne rien editer.

Ce garde-fou n est pas theorique. Le skill se declenche sur « prepare la PR »
et « nettoie la doc », ce qu un utilisateur dit couramment **en cours**
d execution d un plan. Supprimer le plan a la tache 3 sur 8 emporte les taches
4 a 8, et `docs/superpowers/plans/` etant gitignore, il n existe aucun blob git
pour les rendre.

## Etape 1 — supprimer le plan

La condition d entree ci-dessus doit etre verifiee. Supprimer alors tout
fichier de `docs/superpowers/plans/`, sans archivage. Le dossier est gitignore,
donc rien a desindexer si le repo est deja conforme ; sinon utiliser `git rm`.

Un plan fait des milliers de lignes, sert une fois, et le diff de la pull
request documente mieux que lui ce qui a ete livre.

## Etape 2 — arbitrer chaque spec

Pour chaque fichier de `docs/superpowers/specs/`, demander a l utilisateur
laquelle des trois sorties s applique, en proposant celle qui parait juste :

1. **Elle a tranche quelque chose de durable.** La reecrire en decision courte
   dans `docs/dated/decisions/YYYY-MM-DD-<slug>.md`, frontmatter
   `regime: dated`, `status` parmi `decided`, `applied` ou `proposed`. Puis
   supprimer la spec.
2. **Elle decrit un etat du systeme.** Fondre son contenu dans le fichier
   `docs/live/` concerne, mettre a jour son `reviewed` a la date du jour, puis
   supprimer la spec.
3. **Elle etait tactique.** La supprimer.

Une spec n est **ni deplacee ni copiee : reecrite**. Une decision utile tient en
quarante a cent lignes ; copier une spec de trois cents lignes reproduit le
volume qu on cherche a supprimer.

## Etape 3 — consigner les lecons

Ajouter a `tasks/lessons.md` ce que cette session a appris et qui reviendrait
mordre plus tard. Respecter le format deja en place dans le fichier. Ne
consigner que du durable : un symptome, sa cause, la regle qui evite la
recidive. Pas de recit de session.

**Ajouter seulement.** `tasks/` est gitignore dans certains repos : une entree
reecrite ou reordonnee y est perdue definitivement. Ne jamais reformuler,
fusionner ni supprimer une entree existante.

## Etape 4 — nettoyer le todo

Supprimer de `tasks/todo.md` les items livres. Les **supprimer**, pas les
cocher : leur trace vit dans le numero de pull request. Un `tasks/todo.md` qui
accumule des cases cochees redevient un journal en quelques semaines.

`tasks/` pouvant etre gitignore, cette edition est elle aussi irrecuperable :
soumettre a l utilisateur la liste des items qu on s apprete a retirer et
attendre son accord. Un item dont la livraison n est pas etablie reste.

## Etape 5 — reecrire le routeur

Reecrire `HANDOFF.md` sous 150 lignes. Deux questions, rien d autre : ou on en
est, ou chercher. Si ca ne tient pas, c est que du contenu doit partir dans
`docs/live/` ou `docs/dated/` — pas que le plafond est trop bas.

## Verification finale

Lancer, depuis la racine du repo :

```
python scripts/check_docs.py --repo-root . --fix
```

Si le repo n embarque pas le script, utiliser celui du repo
`snetor-ai-guidelines`.

Afficher le rapport a l utilisateur. Ne jamais annoncer la cloture terminee
sans montrer la sortie `OK — 0 erreur`. Les warnings de fraicheur ne bloquent
pas, mais les signaler : ils constituent la liste de dette documentaire.
