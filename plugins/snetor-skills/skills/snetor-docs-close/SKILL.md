---
name: snetor-docs-close
description: Cloture proprement une branche dans un repo Snetor en appliquant le standard de documentation - purge le plan d implementation, arbitre chaque spec vers sa destination durable, consigne les lecons, nettoie les items livres du todo, reecrit le routeur HANDOFF.md sous 150 lignes, puis regenere l index et lance le verificateur. USE THIS SKILL avant d ouvrir ou de merger une pull request dans un repo Snetor, et des que l utilisateur dit qu un chantier est termine, livre, ou pret a merger ("on cloture", "c est fini", "prepare la PR", "nettoie la doc", "close the branch"). Ne pas utiliser pour rediger une spec ou un plan - c est le role des skills brainstorming et writing-plans.
---

# Cloture de branche — standard de documentation Snetor

Doctrine complete : `docs/live/documentation-standard.md` du repo
`snetor-ai-guidelines`.

Deroule les cinq etapes dans l ordre. Ne pas en sauter une : chacune retire du
volume que la suivante n aura pas a trier.

## Etape 1 — supprimer le plan

Supprimer tout fichier de `docs/superpowers/plans/`. Sans exception, sans
archivage. Le dossier est gitignore, donc rien a desindexer si le repo est
deja conforme ; sinon utiliser `git rm`.

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

Reecrire, jamais copier. Une decision utile tient en quarante a cent lignes ;
copier une spec de trois cents lignes reproduit le volume qu on cherche a
supprimer.

## Etape 3 — consigner les lecons

Ajouter a `tasks/lessons.md` ce que cette session a appris et qui reviendrait
mordre plus tard. Respecter le format deja en place dans le fichier. Ne
consigner que du durable : un symptome, sa cause, la regle qui evite la
recidive. Pas de recit de session.

## Etape 4 — nettoyer le todo

Supprimer de `tasks/todo.md` les items livres. Les **supprimer**, pas les
cocher : leur trace vit dans le numero de pull request. Un `tasks/todo.md` qui
accumule des cases cochees redevient un journal en quelques semaines.

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
