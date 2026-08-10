---
regime: dated
audience: [agent, dev]
date: 2026-08-10
status: decided
---

# Règles de migration d'un repo vers le standard de documentation

Ce document porte les règles qui gouvernent la migration d'un repo existant vers
le standard, et les questions restées ouvertes après le lot pilote.

Il existe parce que ces règles vivaient dans la spec du standard, supprimée à la
clôture du pilote conformément à la méthode. Le pilote a ainsi produit sa
première démonstration, et à ses propres dépens : une information portée par un
artefact de travail doit être réécrite dans un document durable, sinon elle
disparaît. Le journal de la session pilote a d'ailleurs été effacé avant que son
contenu ne soit reporté — ce document est ce rattrapage.

Ce dépôt étant public, l'ordre de passage des repos, leur état documentaire et
les nettoyages de poste à effectuer ne figurent pas ici. Ils vivent dans le
premier repo migré.

## Règle de datation

Le champ `reviewed` d'un fichier migré vers `docs/live/` reçoit **la dernière
date de vérité connue du document** — celle de son en-tête « Dernière mise à
jour » ou équivalent — et **non la date du jour**.

Inscrire la date du jour sur un document dont le contenu est périmé serait un
mensonge inscrit dans le frontmatter. La conséquence est voulue : le warning de
fraîcheur se déclenche immédiatement sur les documents périmés, et la migration
produit ainsi la liste chiffrée de la dette documentaire au lieu de la masquer.

Cette règle diverge en apparence du skill `snetor-docs-close`, qui prescrit de
mettre `reviewed` à la date du jour lorsqu'une spec est fondue dans un fichier
`live/`. Les deux sont justes dans leur contexte : fondre une spec fraîche dans
un document le rend effectivement à jour, migrer un document périmé ne le rend
pas vrai. La question à se poser est « ce document est-il vrai aujourd'hui ? »,
jamais « quand l'ai-je touché ? ».

## Frontière de périmètre

La migration **déplace, annote et purge**. Elle **ne corrige pas le fond**.

Les corrections de contenu — une procédure abandonnée encore prescrite, une
version de dépendance périmée, un runbook dont le code est mort — se traitent
ensuite, chacune dans sa propre pull request. Les mêler à la migration
structurelle transforme un chantier de quelques jours en chantier de plusieurs
semaines.

## Ordre de passage

Du moins risqué au plus risqué, une pull request par repo, jamais de bascule
groupée. Le critère de risque n'est pas la taille du corpus documentaire mais ce
que la CI du repo déclenche : un repo dont l'intégration continue applique de
l'infrastructure passe en dernier, et un repo dont le fichier de règles porte des
consignes critiques mérite d'être traité une fois la méthode rodée ailleurs.

## Suppression du bloc de workflow dupliqué

Un repo dont le `CLAUDE.md` recopie le bloc de workflow générique déjà présent
dans les règles d'équipe le supprime : c'est une centaine de lignes relues à
chaque session pour rien.

Ce qui reste doit être préservé intégralement. Les vraies règles projet ont de la
valeur, en particulier celles qui encodent une leçon chèrement acquise — par
exemple qu'un plan d'infrastructure vert prouve le déploiement et jamais l'effet.
Les distinguer du bloc générique demande de lire, pas de couper au marqueur.

## Mécanique des imports, à connaître avant de toucher à la distribution

La directive `@chemin` d'un fichier de mémoire Claude Code : disponible au niveau
utilisateur, `~` supporté, chemins relatifs résolus par rapport au fichier qui
importe, **quatre niveaux d'imbrication au maximum**, et les imports situés à
l'intérieur d'un bloc de code sont **ignorés** — ce qui permet de citer la
directive dans de la documentation sans qu'elle soit interprétée. Le chargement
effectif se contrôle par `/context`, section « Memory files ».

Tout le modèle de distribution des règles d'équipe repose sur ces propriétés.

## Questions ouvertes, à trancher en branchant le premier repo

**Comment un développeur régénère-t-il l'index en local ?** La doctrine, les
règles d'équipe et le marqueur écrit en tête de chaque index généré prescrivent
`python scripts/check_docs.py`. Or un repo consommateur ne reçoit que le workflow
réutilisable, pas le script. Il portera donc un `docs/README.md` dont la première
ligne renvoie à un script absent, et la règle « ne jamais éditer à la main,
régénérer » y sera inexécutable. Trois pistes : distribuer le script dans chaque
repo, en faire un paquet installable, ou changer le marqueur et la doctrine pour
prescrire une commande qui fonctionne partout.

**Comment imposer le gitignore des plans ?** Les règles d'équipe classent « ne
jamais commiter un plan d'implémentation » parmi les règles non négociables, mais
rien ne l'amorce ni ne l'applique : le vérificateur laisse passer un plan
commité, et la procédure de branchement d'un repo ne dit pas d'ajouter
`docs/superpowers/plans/` au `.gitignore`.

**La règle des 30 jours est contournable.** Le vérificateur lit la date dans le
nom du fichier et parcourt `docs/superpowers/specs/` sans récursion. Une spec
sans préfixe de date, ou rangée dans un sous-dossier, échappe au blocage :
renommer un fichier suffit à le rendre éternel. Deux options de coût différent :
rendre le parcours récursif et bloquer les noms sans date, ou documenter la
convention de nommage comme règle bloquante à part entière.

## Limites connues du vérificateur

Relevées pendant le lot pilote et délibérément différées. Elles ne bloquent pas
une migration, mais il ne faut pas les redécouvrir comme des nouveautés.

- Un fichier illisible sous `docs/live/` ou `docs/dated/` produit deux messages
  d'erreur, un par vérification qui le parcourt. Le code de sortie reste unique.
- `find_side_readmes` n'a pas de canal d'erreur et s'appuie sur la vérification
  des liens pour signaler une lecture impossible. Valide aujourd'hui, fragile si
  le périmètre de cette vérification était un jour restreint à `docs/`.
- L'existence des liens est vérifiée sans tenir compte de la casse sous Windows
  et en la respectant sur le runner Linux : un lien mal capitalisé peut être vert
  en local et rouge en intégration continue.
- Les fins de ligne sont mixtes et aucun `.gitattributes` ne stabilise l'index
  généré entre plateformes.
- La détection de la ligne d'import par le script de déploiement est une
  recherche de sous-chaîne non ancrée.
