# Workflow — méthode de travail générique

Règles valables sur tout projet. `deploy-claude.ps1` copie ce fichier vers
`~/.claude/workflow.md` ; ne pas éditer cette copie, qui sera écrasée.

## Planifier à la bonne échelle

- Pour une tâche bornée, annoncer le résultat attendu et sa vérification en quelques lignes.
- Utiliser le mode plan et une spec pour une décision d'architecture, un risque élevé,
  une demande ambiguë ou plusieurs chantiers dépendants. Trois étapes mécaniques ne
  justifient pas à elles seules une spec.
- Si une hypothèse importante tombe, arrêter l'exécution et réviser le plan.
- Choisir une seule source de suivi : issue pour un chantier multi-session ;
  `tasks/todo.md` seulement pour un travail local sans issue. Ne pas dupliquer l'état.

## Paralléliser avec des frontières nettes

- Commencer avec une session. Par défaut, garder au plus 2 à 3 responsables de
  lots actifs, avec des fichiers et livrables indépendants ; dépasser ce nombre
  seulement si le gain attendu est explicite. Un relecteur intervient à la
  demande. Ne pas créer de sous-équipes imbriquées par défaut.
- Réserver les sous-agents aux recherches ou vérifications bornées : question précise,
  périmètre de lecture, preuve attendue et condition d'arrêt. Arrêter les sessions
  devenues inactives.
- Pour chaque lot, consigner dans le suivi choisi : propriétaire, fichiers ou
  ressources possédés, dépendances, critère de fin, portée des écritures et
  preuve de recette. En dépôt Git, préciser aussi branche/worktree et PR du lot.
  Un seul éditeur simultané par fichier partagé.
- Si le suivi est public, ne pas y exposer de données sensibles : utiliser une
  issue privée ou un contrat public expurgé, avec la preuve dans un espace autorisé.
- Les messages directs servent aux décisions urgentes et demandent un accusé de
  réception. L'issue porte les décisions durables ; son corps est tenu à jour,
  pas seulement ses commentaires.
- Pour une ressource partagée ou de production, nommer un coordinateur unique des
  écritures. Mesurer l'état, annoncer la cible exacte, puis attendre son feu vert.
- Un rapport d'agent tient en quatre points : résultat, preuve, limites, prochaine
  action. Une affirmation non vérifiée reste une hypothèse.

## Gérer le coût de contexte

- Choisir le modèle par tâche : modèle fort pour architecture, sécurité ou diagnostic
  difficile ; modèle intermédiaire pour implémentation et revue courantes ; modèle
  léger pour une recherche bornée. Ajuster l'effort de réflexion de la même façon.
- Chercher les fichiers pertinents avant de charger de longs journaux ou dossiers.
  Transmettre aux autres sessions un résumé et un lien vers la preuve, pas le transcript.
- Après un jalon terminé, repartir d'un contexte court si l'historique ne sert plus.
  Comparer qualité et tokens avant/après sur des chantiers comparables ; les tokens
  relus du cache ne sont ni du texte unique ni une facture.

## Apprendre sans grossir le préambule

- Après une correction, inscrire une règle réutilisable avec l'incident qui
  l'explique dans le registre prévu par le projet (`tasks/lessons.md` s'il existe) ;
  éviter le journal de session. Chercher les leçons pertinentes à la demande.
- Garder les leçons actives sous 300 lignes ; archiver les anciennes dans
  `tasks/lessons/AAAA-MM.md` lorsque le dépôt utilise ce standard.
- La mémoire personnelle hors Git ne garde que les faits non déductibles du code ou
  de l'historique. Sauvegarder cette mémoire avant tout outil qui la réécrit.

## Vérifier avant de conclure

- Prouver le comportement demandé avec les tests et, si pertinent, le parcours réel
  d'un utilisateur. Un build ou une relecture du code ne prouvent pas l'usage final.
- Distinguer les échecs préexistants des régressions ; documenter les limites de la
  preuve. Ne pas marquer « terminé » si une condition d'acceptation reste non testée.
- Corriger un bug à sa cause, sans élargir silencieusement la portée. Ne pas changer
  des fichiers adjacents sans besoin ; préférer la solution la plus simple qui tient.
