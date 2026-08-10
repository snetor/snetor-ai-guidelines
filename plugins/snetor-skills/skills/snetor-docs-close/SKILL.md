---
name: snetor-docs-close
description: >
  Clôture proprement une branche dans un repo Snetor en appliquant le standard de
  documentation - purge le plan d implémentation, arbitre chaque spec vers sa destination
  durable, consigne les leçons, nettoie les items livrés du todo, réécrit le routeur
  HANDOFF.md sous 150 lignes, puis régénère l index et lance le vérificateur.
  USE THIS SKILL avant d ouvrir ou de merger une pull request dans un repo Snetor, et dès
  que l utilisateur dit qu un chantier est terminé, livré, ou prêt à merger
  ("on cloture", "c est fini", "prepare la PR", "nettoie la doc", "close the branch").
  Ne pas utiliser pour rédiger une spec ou un plan - c est le rôle des skills
  brainstorming et writing-plans.
---

# Clôture de branche — standard de documentation Snetor

Doctrine complète : `docs/live/documentation-standard.md` du repo
`snetor-ai-guidelines`.

Déroule les cinq étapes dans l ordre. Ne pas en sauter une : chacune retire du
volume que la suivante n aura pas à trier.

## Condition d entrée — à établir avant la moindre suppression

Ce skill détruit des fichiers que git ne peut pas rendre. Il ne démarre que si
les deux points suivants sont **établis**, pas supposés :

1. **Le plan est entièrement exécuté.** Toutes ses tâches sont livrées, aucune
   n est en attente ni en cours. Relire le plan et le confronter à ce qui est
   réellement dans l arbre — ne pas se fier à un souvenir de session.
2. **L arbre de travail est commité.** `git status --porcelain` ne renvoie
   rien.

Si l un des deux est faux, **s arrêter et le dire** à l utilisateur : nommer ce
qui reste à faire ou à commiter, et ne rien supprimer, ne rien éditer.

Ce garde-fou n est pas théorique. Le skill se déclenche sur « prepare la PR »
et « nettoie la doc », ce qu un utilisateur dit couramment **en cours**
d exécution d un plan. Supprimer le plan à la tâche 3 sur 8 emporte les tâches
4 à 8, et `docs/superpowers/plans/` étant gitignoré, il n existe aucun blob git
pour les rendre.

## Étape 1 — supprimer le plan

La condition d entrée ci-dessus doit être vérifiée. Supprimer alors tout
fichier de `docs/superpowers/plans/`, sans archivage. Le dossier est gitignoré,
donc rien à désindexer si le repo est déjà conforme ; sinon utiliser `git rm`.

Un plan fait des milliers de lignes, sert une fois, et le diff de la pull
request documente mieux que lui ce qui a été livré.

## Étape 2 — arbitrer chaque spec

Pour chaque fichier de `docs/superpowers/specs/`, demander à l utilisateur
laquelle des trois sorties s applique, en proposant celle qui paraît juste :

1. **Elle a tranché quelque chose de durable.** La réécrire en décision courte
   dans `docs/dated/decisions/YYYY-MM-DD-<slug>.md`, frontmatter
   `regime: dated`, `status` parmi `decided`, `applied` ou `proposed`. Puis
   supprimer la spec.
2. **Elle décrit un état du système.** Fondre son contenu dans le fichier
   `docs/live/` concerné, mettre à jour son `reviewed` à la date du jour, puis
   supprimer la spec.
3. **Elle était tactique.** La supprimer.

Une spec n est **ni déplacée ni copiée : réécrite**. Une décision utile tient en
quarante à cent lignes ; copier une spec de trois cents lignes reproduit le
volume qu on cherche à supprimer.

## Étape 3 — consigner les leçons

Ajouter à `tasks/lessons.md` ce que cette session a appris et qui reviendrait
mordre plus tard. Respecter le format déjà en place dans le fichier. Ne
consigner que du durable : un symptôme, sa cause, la règle qui évite la
récidive. Pas de récit de session.

**Ajouter seulement.** `tasks/` est gitignoré dans certains repos : une entrée
réécrite ou réordonnée y est perdue définitivement. Ne jamais reformuler,
fusionner ni supprimer une entrée existante.

## Étape 4 — nettoyer le todo

Supprimer de `tasks/todo.md` les items livrés. Les **supprimer**, pas les
cocher : leur trace vit dans le numéro de pull request. Un `tasks/todo.md` qui
accumule des cases cochées redevient un journal en quelques semaines.

`tasks/` pouvant être gitignoré, cette édition est elle aussi irrécupérable :
soumettre à l utilisateur la liste des items qu on s apprête à retirer et
attendre son accord. Un item dont la livraison n est pas établie reste.

## Étape 5 — réécrire le routeur

Réécrire `HANDOFF.md` sous 150 lignes. Deux questions, rien d autre : où on en
est, où chercher. Si ça ne tient pas, c est que du contenu doit partir dans
`docs/live/` ou `docs/dated/` — pas que le plafond est trop bas.

## Vérification finale

Lancer, depuis la racine du repo :

```
python scripts/check_docs.py --repo-root . --fix
```

Si le repo n embarque pas le script, utiliser celui du repo
`snetor-ai-guidelines`.

Afficher le rapport à l utilisateur. Ne jamais annoncer la clôture terminée
sans montrer la sortie `OK — 0 erreur`. Les warnings de fraîcheur ne bloquent
pas, mais les signaler : ils constituent la liste de dette documentaire.
