---
name: snetor-lessons-outillage
description: >
  Transforme les lecons de tasks/lessons.md d un depot Snetor en garde-fous executables - classe
  chaque lecon en geste (hook PreToolUse), invariant (test), fait d environnement (phrase de
  CLAUDE.md) ou jugement (reste narratif), ecrit le mecanisme manquant, et marque celles qui sont
  deja outillees. USE THIS SKILL des qu une erreur se repete - "on s est deja fait avoir",
  "c est la deuxieme fois", "recidive", "je te l avais dit" - des qu une correction de
  l utilisateur ressemble a une lecon deja ecrite, quand tasks/lessons.md approche ses 300 lignes
  ou que check_docs.py bloque dessus, et lors d une passe de nettoyage de la dette d outillage.
  Ne pas utiliser pour ecrire une lecon apres une simple correction - une lecon s ajoute a
  lessons.md sans cette routine ; celle-ci sert quand la lecon n a PAS suffi.
---

# Outiller les leçons — une règle vérifiable ne reste pas en prose

## Pourquoi cette routine existe

`tasks/lessons.md` est append-only par doctrine, ce qui est juste — mais un fichier qu'on n'ouvre
plus n'est plus un garde-fou. La preuve est dans le fichier lui-même : sur `snetor-pim`, **quatre
leçons y étaient annotées « récidive exacte » ou « troisième variante »**. Elles étaient écrites,
relues, et refaites quand même.

Le même constat a produit le plafond de 300 lignes : le fichier avait atteint 42 000 tokens que
personne ne lisait.

**Une leçon qu'on répète est une leçon qui demande un mécanisme, pas une phrase de plus.**

## Le principe — quatre cases, une seule par leçon

| Case | Mécanisme | Où |
|---|---|---|
| **Geste** — une commande, un chemin, un ordre d'exécution | hook `PreToolUse` | `snetor-ai-guidelines`, `hooks/guard.py` **+ son test** |
| **Invariant** — une propriété du code ou du schéma | test | la suite du dépôt concerné |
| **Fait d'environnement** — un plafond, un délai, une page de codes | phrase dans `CLAUDE.md` | rien à exécuter |
| **Jugement** — un arbitrage, un seuil, une lecture métier | rien | reste narratif |

Les trois premières se marquent `outillée : <chemin>` sous la leçon, dans `lessons.md`.

La quatrième reste telle quelle : **essayer d'automatiser un jugement produit un garde-fou qui se
déclenche à tort, et un garde-fou qui se déclenche à tort est désactivé dans la semaine.**

## Séquence

1. **Lire `tasks/lessons.md` en entier** — c'est le seul moment où on le lit en entier ; le reste
   du temps on le `grep`. Lire aussi `tasks/lessons/AAAA-MM.md` si la passe est complète : les
   récidives se comptent sur l'archive, pas sur le fichier actif.

2. **Classer chaque leçon** dans une des quatre cases. Une leçon déjà marquée `outillée :` se
   **vérifie** plutôt que de se reclasser — le chemin cité existe-t-il encore, le test tourne-t-il ?
   Un marqueur qui pointe vers un fichier disparu est pire que pas de marqueur.

3. **Chercher les répétitions.** Deux leçons qui décrivent le même mode de défaillance sous deux
   habillages différents comptent double : c'est le signal le plus fiable qu'un mécanisme manque.

4. **Écrire le mécanisme** pour les leçons de type geste ou invariant qui n'en ont pas. **Un
   mécanisme à la fois, avec son test, dans un commit dédié.** Un garde-fou de geste va dans
   `snetor-ai-guidelines/hooks/guard.py` — il couvre alors les quatorze dépôts, pas un seul.

5. **Marquer** dans `lessons.md` sans réécrire le texte de la leçon : ajouter une ligne
   `outillée : <chemin>` sous elle.

## Ce qu'il ne faut pas faire

- ⛔ **Ne pas supprimer une leçon parce qu'elle est outillée.** C'est ce qui permet de compter les
  récidives, et donc de savoir qu'un mécanisme manque. Une leçon sort du fichier actif par
  l'archive mensuelle, jamais par la suppression.
- ⛔ **Ne pas écrire un garde-fou large « pour couvrir plusieurs leçons à la fois ».** Un motif
  large attrape des cas légitimes, et c'est la première chose qu'on désactive.
- ⛔ **Ne pas outiller un jugement.** « Un taux ment sans son dénominateur » ne devient pas un
  test : publier la distribution est mécanisable, choisir le seuil ne l'est pas.
- ⛔ **Ne pas écrire une règle sans son incident.** Une règle dont on ne sait plus ce qu'elle a
  coûté se fait supprimer par le prochain lecteur qui ne la comprend pas.

## Barrière de vérification

La suite de tests du dépôt concerné doit passer, **et** — pour chaque nouveau mécanisme — la preuve
qu'il attrape le cas réel : rejouer la commande ou l'état qui avait causé l'incident, et montrer
qu'il est refusé. Un garde-fou dont on n'a pas vu le refus n'est pas vérifié.

Pour un hook ajouté à `guard.py` :

```bash
python -m pytest tests/ -q     # depuis snetor-ai-guidelines
```

## Ce qu'il faut dire en fin de passe

1. **Les leçons nouvellement outillées**, avec leur mécanisme et la preuve qu'il attrape le cas.
2. **Les répétitions trouvées** — les leçons qui décrivent deux fois le même défaut.
3. **Ce qui reste du jugement**, et pourquoi ça ne s'automatise pas.
