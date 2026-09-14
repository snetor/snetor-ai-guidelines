---
name: snetor-doc-vs-infra
description: >
  Confronte ce que la documentation d un depot Snetor AFFIRME sur son infrastructure a ce
  qu Azure a REELLEMENT execute - collecte chaque affirmation (un job tourne, une image est a
  jour, une ressource est joignable, un circuit s applique), cherche l execution datee qui la
  prouve, et classe en prouve / non prouve / contredit. USE THIS SKILL des qu il faut
  s appuyer sur une affirmation d infrastructure ecrite quelque part - "d apres le HANDOFF",
  "le runbook dit que", "ce job applique les migrations", "l app est en ligne", "la CI deploie" -
  et des qu un utilisateur demande si la doc est a jour, si un runbook marche encore, ou lance
  un chantier sur un depot avec de l infrastructure Azure. A utiliser AVANT de citer un etat
  d infra, jamais apres. Ne pas utiliser pour verifier la coherence de la documentation avec
  elle-meme - c est check_docs.py.
---

# La doc affirme, l'infra exécute

## Pourquoi cette routine existe

C'est la récidive la plus coûteuse mesurée sur les dépôts Snetor — **cinq occurrences en huit
jours** sur `snetor-pim`, toutes de la même forme : **une phrase écrite dans un document a été
prise pour une exécution**.

- Un job Container App était décrit comme le circuit d'application des migrations. Il **n'avait
  jamais été exécuté**, et son image figeait un schéma vieux de trois mois.
- « `merge = apply` » était écrit dans une note de contexte. C'était **faux** : le `Terraform
  Apply` partait en `workflow_dispatch` manuel.
- Un compte de stockage était décrit comme « joignable ». Il rendait `blocked by network rules`.
- **La plus chère** : « la source lue est la production S/4HANA ». L'hypothèse a tenu **deux mois**,
  porté 6 941 fiches produit, les vocabulaires, l'axe de sécurité au niveau ligne et un audit livré
  au MDM. Elle a été repérée par une utilisatrice métier, pas par l'équipe.

Un runbook qui n'a jamais été exécuté n'est pas un runbook. Une ligne de `HANDOFF.md` n'est pas
une mesure.

## Ce qu'il faut savoir avant de commencer

- ⚠️ **Cette routine ne se planifie pas dans le cloud.** Le token Entra expire à ~2 h, et les
  opérations de suppression exigent une MFA fraîche. Elle se lance depuis le poste, connecté.
- **Le premier `az` qui échoue après deux heures de session, c'est le token.** Ne pas chercher
  ailleurs : `az login` d'abord.
- ⛔ **Ne jamais tronquer une sortie `az` par un pipe** (`| tail`, `| head`, `| Select-Object`) :
  le code de sortie est avalé avec. Le garde-fou `PreToolUse` le refuse — lire le motif, pas
  contourner.
- Sur un poste tunnelisé par Cato, le SQL sortant (1433) est bloqué : une vérification data-plane
  passe par un job dans le VNet, pas depuis le poste.

## Séquence

1. **Collecter les affirmations d'infrastructure.** Balayer `CLAUDE.md`, `HANDOFF.md`,
   `docs/live/runbooks/` et tout `README.md` de module : relever chaque énoncé qui prétend qu'un
   job tourne, qu'une image est à jour, qu'une ressource est joignable, qu'un circuit s'applique,
   qu'un environnement est peuplé. Les lister avec leur fichier et leur ligne.

2. **Confronter chacune à une exécution datée.** Les commandes utiles :

   ```bash
   az containerapp job execution list -n <job> -g <rg> -o json
   az acr repository show-tags -n <registre> --repository <image> --orderby time_desc -o json
   az containerapp job list -g <rg> --query "[].{nom:name, image:properties.template.containers[0].image}" -o json
   az containerapp revision list -n <app> -g <rg> --query "[?properties.active].{rev:name, image:properties.template.containers[0].image}" -o json
   gh run list --workflow <fichier.yml> --limit 5 --json conclusion,createdAt,event
   ```

   Une affirmation est **prouvée** si une exécution réussie la porte, **avec sa date**. Sinon elle
   est **non prouvée** — ce qui ne veut pas dire fausse.

3. **Vérifier ce que les manifestes déclarent contre ce qui existe.** Un manifeste versionné
   n'est **pas** l'état déployé : un job créé à la main n'est dans aucun manifeste, et un manifeste
   modifié sans redéploiement ne change rien. Comparer le fichier au groupe de ressources.

4. **Ne rien corriger dans la doc sans mesure.** Une affirmation non prouvée se marque comme telle,
   avec la date de la tentative de preuve. Elle ne se supprime pas et ne se réécrit pas au jugé.

## Barrière de vérification

Chaque ligne du rapport porte **la commande qui l'établit et sa date**. Une ligne sans preuve
d'exécution n'entre pas dans le rapport : elle entre dans la liste « non prouvé ».

## Ce qu'il faut dire en fin de passe

Trois listes, dans cet ordre :

1. **Ce qui est prouvé** — l'affirmation, l'exécution qui la porte, sa date.
2. **Ce qui est non prouvé** — l'affirmation, ce qui a été tenté, pourquoi ça n'a rien donné.
3. **Ce qui est contredit** — l'affirmation, la mesure qui l'infirme. C'est la seule catégorie qui
   appelle une correction immédiate de la doc, dans un commit dédié.

⚠️ Ne jamais publier un chiffre sans son dénominateur et sa date.
