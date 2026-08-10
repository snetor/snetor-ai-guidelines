---
regime: dated
audience: [dev, business]
date: 2026-08-04
status: proposed
---

# Skill de conversion d un artefact HTML en application interne

## Contexte

Les artefacts HTML produits en conversation servent de maquettes convaincantes
mais ne sont pas des applications : pas d authentification, pas de persistance,
pas de déploiement. Le passage de la maquette à l application interne est
aujourd hui entièrement manuel.

## Proposition

Un skill `snetor-artifact-to-app` qui prend un artefact HTML autonome et
produit le squelette d une application interne conforme à la voie pavée :
structure de projet, authentification d entreprise, manifeste de déploiement,
et une pull request. Le skill génère du code et une pull request, jamais de
l infrastructure.

## Statut

Proposition non implémentée au 2026-08-10. Le séquencement retenu la place
après la voie pavée des applications internes : sans runtime partagé déployé,
le skill produirait du code qui n a nulle part où aller.

## Ce qui déclenchera la reprise

La disponibilité du runtime partagé des applications internes. La conception
détaillée est à refaire à ce moment-là : la spec d origine de 288 lignes a été
écrite avant la décision d exécution de Terraform dans le réseau virtuel et
n en tient pas compte.
