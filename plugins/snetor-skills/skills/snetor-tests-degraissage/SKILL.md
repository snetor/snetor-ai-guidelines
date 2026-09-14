---
name: snetor-tests-degraissage
description: >
  Trouve et supprime les tests qui ne servent plus dans un depot Snetor - test d un module mort,
  test endormi (skip/xfail inconditionnel), test d une constante, doublon de couverture - avec
  la preuve exigee pour chaque categorie et le compte avant/apres. USE THIS SKILL quand la suite
  de tests grossit sans jamais retrecir, quand la CI ralentit ou coute trop, quand un utilisateur
  dit "on a trop de tests", "la CI prend des plombes", "ces tests servent a quoi", quand du code
  mort vient d etre supprime et que ses tests restent, et apres un gros refactor. Utile aussi
  quand une suite est verte mais suspecte - un test sauté se lit comme une couverture.
  Ne pas utiliser pour ecrire des tests ni pour reparer une suite rouge - un test rouge dit
  quelque chose, il se lit, il ne se supprime pas.
---

# Dégraisser la suite de tests

## Pourquoi cette routine existe

Une suite qui grossit sans jamais rétrécir finit par coûter du temps de CI et de la lecture sans
rien garantir de plus. Et, pire, **un test mort se lit comme une couverture**.

Le cas mesuré sur `snetor-pim` va dans l'autre sens et dit la même chose : **95 tests côté `app/`
étaient sautés à chaque PR pendant que la CI restait verte**. Un test qui ne s'exécute pas et un
test qui teste du code mort posent le même problème — ils comptent dans les chiffres et ne
vérifient rien.

## Les quatre catégories, et la preuve exigée pour chacune

| Catégorie | Preuve exigée | Action |
|---|---|---|
| **Test d'un module mort** | aucun `import` depuis un point d'entrée réel — un `run_*.py`, un manifeste de déploiement, un runbook, une route de l'app, ou un autre module vivant | supprimer le test **et** le module, dans le même commit |
| **Test endormi** | `@pytest.mark.skip` / `xfail` **sans condition**, `allow_module_level=True`, `describe.skip(`, `it.skip(`, `.todo(` | réparer, ou supprimer — jamais laisser dormir |
| **Test d'une constante** | l'assertion réaffirme une valeur littérale du code, sans comportement | supprimer |
| **Doublon de couverture** | deux fichiers couvrent la même fonction avec les mêmes cas | garder le plus proche du comportement métier |

⛔ **Un `skipif` conditionnel n'est PAS un test endormi.** Les marqueurs qui expriment un
**prérequis réel** — une base de données locale, un `importorskip`, une variable d'environnement de
CI — sont exécutés pour de vrai par les workflows qui les fournissent. Les supprimer rouvrirait
exactement le trou qu'on cherche à fermer.

## Séquence

1. **Mesurer avant.** Lancer la suite et noter le nombre de tests **passés** et **sautés**,
   séparément. Sans ce point de départ, la passe ne se prouve pas.

   ```bash
   python -m pytest -q          # Python
   npx vitest run               # front
   ```

2. **Chercher les modules sans appelant vivant.** Pour chaque paquet, remonter la chaîne d'import
   jusqu'à un point d'entrée réel. Un module dont seuls ses propres tests parlent est mort.

   ⚠️ **Vérifier paquet par paquet, jamais en bloc.** Cas réel : dans un même paquet, un module
   était mort depuis deux mois pendant que son voisin écrivait en production. Supprimer le paquet
   entier aurait cassé la production.

3. **Lister les tests endormis.** Si le dépôt a une suite d'hygiène qui échoue quand il en existe
   un, la lancer ; sinon `grep` les marqueurs du tableau ci-dessus.

4. **Chercher les doublons** : deux fichiers qui importent la même fonction et posent les mêmes
   assertions.

5. **Supprimer, un sujet par commit.** Le test et le module qu'il couvre partent ensemble. Ne
   jamais mélanger une suppression à un changement de comportement — c'est la seule façon de
   relire un `git revert` plus tard.

6. **Mesurer après**, et dire la différence.

## Barrière de vérification

Le nombre de tests **passés** doit baisser **exactement** du nombre de tests supprimés, et le
nombre de tests **sautés** ne doit pas bouger.

S'il bouge, une suppression a cassé un import et éteint autre chose au passage — c'est le seul
signal qui distingue un dégraissage d'une régression silencieuse.

## Ce qu'il faut dire en fin de passe

1. **Ce qui a été supprimé**, avec la preuve que c'était mort — le module, et qui ne l'appelle plus.
2. **Ce qui a été gardé malgré les apparences**, et pourquoi. C'est la partie qu'on relit.
3. **Le compte avant / après**, passés et sautés séparément.

⚠️ **Ne jamais supprimer un test parce qu'il échoue.** Un test rouge dit quelque chose.
