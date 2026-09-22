---
regime: live
audience: [agent, dev]
reviewed: 2026-09-22
---

# Convention de langue dans le code

L'équipe s'agrandit et Snetor est une multinationale : un repo doit rester
lisible par quelqu'un qui ne parle pas français. Cette règle sépare ce qui
change de ce qui reste tel quel.

## La règle

**En anglais** : identifiants de code — noms de fonctions, variables,
classes, méthodes, paramètres — ainsi que les noms de fichiers et dossiers
structurels, et les noms de skills Claude Code (`name:` du frontmatter d'un
`SKILL.md`, nom du dossier qui le porte).

**En français, sans changement** : documentation (`HANDOFF.md`,
`tasks/lessons.md`, `docs/`), commentaires métier, messages de commit. C'est
déjà la règle Snetor — voir `documentation-standard.md` — elle ne bouge pas.
Un commentaire qui explique *pourquoi* une ligne de code existe reste en
français ; le nom de la fonction qu'il commente passe en anglais.

Exemple :

```js
// Reporté de 400 ms : une frappe utilisateur = un seul enregistrement en base.
function loadData() { ... }
```

## Ce que ça ne couvre pas

Les clés d'un contrat partagé (nom d'une colonne en base, clé d'un état
persistant, route HTTP déjà en production) ne se renomment pas au passage :
un renommage là casse un consommateur qui ne lit pas ce document. Le
périmètre de cette règle est le code qu'un développeur lit et modifie, pas
les contrats déjà publiés.

## Repos existants

Une passe de mise en conformité a été faite en septembre 2026 sur les repos
qui en avaient le plus besoin. Au-delà, cette règle ne déclenche pas un audit
récurrent : un identifiant français qui subsiste se renomme à l'occasion d'un
chantier qui touche déjà ce fichier, pas par une passe dédiée systématique.
