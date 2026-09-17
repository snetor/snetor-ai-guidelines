---
regime: dated
audience: [agent, dev, ops]
date: 2026-09-17
status: applied
---

# Outiller les montées de version d'un fork — ce que la première a coûté

Une montée du fork Twenty, du 2026-09-14 au 2026-09-16, a demandé **environ 35 heures
calendaires** pour un chantier d'une demi-journée. Elle a réussi. Ce document garde ce qui ne vit
nulle part ailleurs : ce qu'elle a coûté, et où chaque mesure a fini.

Le détail de chaque règle vit désormais dans le code qui l'applique et dans ses tests — c'est le
principe du dépôt : *une règle qu'un programme peut vérifier n'a rien à faire en prose.*

## Les six pièges, et leur coût

| Piège | Coût | Nature |
|---|---|---|
| Un build resté bloqué sur son daemon — aucun log, aucun CPU | ~11 h de latence nocturne | variable d'environnement |
| Quatre lancements de job `az` avec une virgule prise pour un séparateur, échec **sans un seul log** | ~1 h 30 | geste refusable |
| Une extension PostgreSQL posée en CLI, effacée par un `terraform apply` **minutes avant** le job | ~40 min + un cycle de migration | geste refusable |
| Un squash sur la montée précédente → merge-base 3 mois trop tôt, **2 714 conflits** au lieu de 14 | ~20 min | réglage de dépôt |
| Session `az` expirée deux fois en pleine séquence | ~20 min + deux interruptions | contrôle au démarrage |
| `lessons.md` au plafond, condensé à la main | ~25 min | **déjà outillé, non utilisé** |

Le dernier est le plus instructif : la routine qui fait exactement ce travail existait, et n'a pas
été cherchée. Une partie du problème n'est jamais un manque d'outil.

## Où chaque mesure a fini

**Dans ce dépôt** — deux règles de `hooks/guard.py`, chacune avec son test et son incident cité
(paramètre de serveur posé en CLI contre Terraform ; virgule entre deux valeurs citées d'un
`--command`). Une variable d'environnement imposée par `scripts/deploy-claude.ps1` pour couper le
daemon du builder. Un hook `hooks/az_ensure_login.py` qui prévient qu'une session `az` est morte,
branché **au démarrage et avant chaque commande `az`** — le second branchement est celui qui traite
l'incident, puisque le jeton était vivant au démarrage les deux fois.

**Dans `azure-landing-zone`** — une règle chargée par chemin, qui n'apparaît que lorsqu'une session
touche un fichier Terraform, et l'issue de veille hebdomadaire qui annonce désormais ce qu'une
montée **coûtera** plutôt que depuis quand on est en retard.

**Dans le fork** — une section de `docs/snetor/FORK.md` disant où vit la variable d'environnement
et pourquoi elle n'est pas dans le dépôt.

**Dans `client-matrix`** — les leçons, avec leurs marqueurs `tooled:`.

## Les quatre prémisses fausses du plan

C'est le contenu le plus durable de ce document : **un plan écrit après coup se trompe sur des
faits qu'il croyait acquis**, et chacune de ces erreurs a changé le livrable.

1. **« Ce fichier de configuration est ajouté par le fork, il ne peut pas entrer en conflit. »**
   Faux : il vient de l'amont, qui l'a réécrit cinq fois en six mois. La variable est donc posée au
   niveau utilisateur, et le fork ne gagne aucun point d'ancrage de plus.
2. **« Les leçons de la montée sont écrites, il suffit de les consommer. »** La première lecture a
   conclu l'inverse — depuis un checkout partagé resté six merges en arrière. Elles existaient. Le
   vrai défaut était ailleurs : le fichier de règles actives renvoyait **cinq fois** à une archive
   qui n'existait dans aucune branche.
3. **« Le contrôle de session Azure reste à écrire. »** Il existait depuis six semaines, hors de
   tout dépôt, et son repli automatique ne pouvait pas fonctionner — voir plus bas.
4. **« Il suffit de déposer un fichier de règles dans le dépôt d'infrastructure. »** Son répertoire
   y était ignoré **en entier**, par deux mécanismes distincts. La règle n'aurait vécu que sur un
   poste.

**La règle qui en sort** : avant d'exécuter un plan, vérifier ses prémisses de fait contre l'arbre
à jour — pas contre le souvenir de la session qui l'a écrit, ni contre un checkout partagé.

## Deux décisions de ne pas faire

**Pas de routine d'upgrade dédiée.** Le seul gain qu'elle apportait était d'être invoquée sans
qu'on y pense. Or le `CLAUDE.md` du fork, chargé sans condition à chaque session dans ce dépôt, dit
déjà d'aller lire sa carte avant toute montée. Le routage existe, par le mécanisme qui ne peut pas
ne pas se charger.

**Pas d'identité de service pour reconnecter Azure toute seule.** Le contrôle existant prétendait
le faire ; l'identité n'avait jamais été créée, et le certificat posé sur le poste n'ouvrait rien.
La créer aurait remplacé une clé qui se périme toutes les deux heures par une clé valable un an,
en clair sur un portable — exactement l'écart que la fenêtre de connexion existe pour supprimer.
La doctrine du dépôt d'infrastructure tranchait déjà : pour un accès local, une connexion
interactive. Le hook prévient donc au bon moment, et ne répare rien.

## Ce qu'on retient pour la prochaine

Le nombre de versions de retard ne dit rien du coût. Trois mesures le disent, et la veille les
publie maintenant : combien de commandes de montée l'amont a ajoutées, combien de fichiers patchés
par le fork il a touchés, et **combien il en a supprimés**. Le dernier décide : au-dessus de zéro,
il n'y a plus d'ancrage où rejouer le patch — c'est une réécriture, pas un merge.
