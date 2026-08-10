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
pas de deploiement. Le passage de la maquette a l application interne est
aujourd hui entierement manuel.

## Proposition

Un skill `snetor-artifact-to-app` qui prend un artefact HTML autonome et
produit le squelette d une application interne conforme a la voie pavee :
structure de projet, authentification d entreprise, manifeste de deploiement,
et une pull request. Le skill genere du code et une pull request, jamais de
l infrastructure.

## Statut

Proposition non implementee au 2026-08-10. Le sequencement retenu la place
apres la voie pavee des applications internes : sans runtime partage deploye,
le skill produirait du code qui n a nulle part ou aller.

## Ce qui declenchera la reprise

La disponibilite du runtime partage des applications internes. La conception
detaillee est a refaire a ce moment-la : la spec d origine de 288 lignes a ete
ecrite avant la decision d execution de Terraform dans le reseau virtuel et
n en tient pas compte.
