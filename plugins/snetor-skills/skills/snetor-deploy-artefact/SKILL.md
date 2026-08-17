---
name: snetor-deploy-artefact
description: >
  Déploie un artefact métier autonome (page HTML de power user, classeur devenu
  application) vers la voie pavée Snetor - audite ce que l artefact ré-embarque,
  sort les données personnelles vers l état partagé, branche identité et droits
  sur Easy Auth, monte un contexte de build explicite, puis ouvre la PR qui ne
  change que la balise d image. USE THIS SKILL dès qu un utilisateur veut mettre
  en ligne ou mettre à jour une application métier venue d un fichier ("déployer
  cet artefact", "nouvelle version du HTML", "le power user a livré une v2",
  "mettre son outil sur la voie pavée", "deploy this artifact", "paved road"), et
  AVANT de toucher au Dockerfile ou de lancer un build. Ne pas utiliser pour
  onboarder une application qui a déjà son dépôt et sa CI - celle-ci patche sa
  propre clé d image.
---

# Déployer un artefact métier sur la voie pavée

Un artefact métier est une page autonome, écrite par quelqu un du métier, qui
marche déjà sur son poste. Le déployer n est pas un portage technique : c est
faire tenir dans une architecture partagée un objet conçu pour circuler en pièce
jointe.

**Le principe qui gouverne tout le reste : une image de conteneur est une copie
durable.** Retirer une donnée du fichier après coup ne la retire pas des balises
déjà poussées. Tout ce qui suit en découle.

## Ce qui rend ce déploiement différent d un autre

Une v2 d artefact **ne descend pas de la version déployée.** Elle descend de la
version locale de son auteur, qui n a jamais vu vos adaptations et n avait aucune
raison de les connaître. Elle ré-embarque donc exactement ce que le déploiement
précédent avait fait sortir.

C est le piège central, et il ne se voit pas : l artefact s ouvre, il est plus
riche qu avant, tout va bien. Constaté en vrai — un artefact livré en v2
ré-embarquait les trois noms sortis un mois plus tôt, plus cent adresses de plus.

## Étape 1 — Auditer, avant tout plan

Ne rien planifier avant d avoir comparé le nouvel artefact à celui qui tourne, sur
**quatre axes**. Ils régressent ensemble, parce qu ils viennent tous du même
fichier local.

| Axe | Ce qu on compte | Ce que ça veut dire |
|---|---|---|
| Données personnelles | noms, adresses e-mail, téléphones, identifiants | doit valoir 0, hors exception nommée |
| Persistance | `localStorage`, `sessionStorage`, `indexedDB` | doit valoir 0 : l état est partagé ou il n existe pas |
| Authentification | mots de passe, empreintes, `crypto.subtle`, écrans de connexion | doit valoir 0 : c est Easy Auth |
| Diffusion | régénération du fichier, « télécharger et remplacer » | l image remplace le fichier, pas l inverse |

Compter, pas parcourir. Sur les deux fichiers, côte à côte :

```bash
for f in "ancien.html" "nouveau.html"; do
  echo "== $f"
  for p in localStorage sessionStorage "/api/etat" "/api/moi" "@votredomaine.com" "fetch("; do
    printf "%-22s %s\n" "$p" "$(grep -o -- "$p" "$f" | wc -l)"
  done
done
```

Un `localStorage` à 18 et un `fetch(` à 0 disent tout : l artefact ignore qu il
existe un serveur.

**Chercher ensuite le point de greffe.** Un artefact de power user mûr a presque
toujours une frontière interne — un noyau, un registre de modules, une fonction de
sérialisation. Les modules y lisent leur état au démarrage et le réécrivent au
même endroit. Un seul motif, répété : on le remplace une fois. Chercher cette
frontière **avant** de proposer une réécriture, elle existe plus souvent qu on ne
croit.

## Étape 2 — Le contrôle de sortie, écrit avant la chirurgie

Un script, versionné, pas une relecture. Une relecture ne rattrape pas la même
chose deux fois de suite ; c est précisément pourquoi la v2 arrive chargée.

Il affirme, sur le fichier, ce que l image n a pas le droit d emporter :
identités attendues à zéro, `localStorage` et compagnie à zéro hors commentaire,
et **le compte exact** de chaque exception.

**Le lancer d abord sur l artefact reçu, et vérifier qu il ÉCHOUE.** Un contrôle
qui passe du premier coup ne contrôle rien : un motif mal échappé donne un `OK`
rassurant sur un artefact plein d adresses. Lui donner aussi son propre auto-test
— la fonction de contrôle doit détecter ce qu on lui injecte exprès.

### Les exceptions se comptent

Quand le métier obtient de garder une donnée personnelle — l adresse de contact du
propriétaire, typiquement —, la règle ne devient pas « aucune donnée, sauf… », ce
qui ne veut plus rien dire. Elle devient un **compte exact**, avec sa date et son
décideur :

> exactement 1 occurrence de ce nom et 3 de cette adresse, aucune autre.

Le compte fait plus que documenter : un dérapage signale que la donnée est
**ressortie ailleurs**, typiquement dans une liste de destinataires.

## Étape 3 — Sortir les données, sans écrire de code d amorçage

Les données personnelles quittent l artefact et vont dans l état partagé. Le
partage à tenir : **le code porte l organisation, la base porte qui occupe la
place.** Des règles indexées sur `0/1/2` fonctionnent avant même que les noms
soient saisis — l écran affiche « Collaborateur 1/2/3 » et rien ne casse.

Pour les remettre : **utiliser les écrans de saisie qui existent déjà.** Un
artefact qui portait 60 adresses de destinataires a forcément un écran pour les
éditer, et son collage accepte probablement déjà le format Outlook. Écrire un
mécanisme d amorçage serait du code neuf pour un geste unique.

Garder les données sorties dans un dossier de graines, **hors de l image**, avec un
fichier qui dit pourquoi elles n y sont pas — sinon quelqu un ajoutera un
`COPY . /app` un jour de fatigue. La graine doit avoir la forme que l écran
d import attend : si l import *remplace* une liste, une graine réduite aux seules
adresses effacerait tout le reste.

## Étape 4 — ⚠️ Le contexte de build est explicite, jamais implicite

**`az acr build` n honore pas `.dockerignore`.** Vérifié : un marqueur de 40 Mo
posé dans un dossier ignoré fait passer le contexte annoncé de 6,58 à 46,6 Mio.
Le dossier de graines part donc avec le contexte, vers le service de build.

Le `Dockerfile` nomme ses `COPY`, donc rien n entre dans l image — mais **« pas
dans l image » n est pas « pas transmis »**.

Ne pas construire depuis le dossier de travail. Copier les fichiers **nommés** dans
un dossier temporaire, **afficher le contexte**, puis construire depuis là. Un
contexte qu on voit vaut mieux qu un contexte qu on espère. Faire du contrôle de
sortie un barrage : rien ne part au registre s il échoue, c est le dernier moment
où la donnée n est pas encore devenue une couche d image.

## Étape 5 — Un contrôle qui EXÉCUTE

« Ça demande un navigateur connecté, donc c est invérifiable » est presque toujours
faux, et ça coûte un déploiement non vérifié. Easy Auth et la base ne sont pas
nécessaires pour éprouver la logique du client : ce sont deux réponses HTTP.

Servir la page depuis le disque et **stubber les routes** — l identité et l état
partagé — puis jouer chaque grade. Un faux serveur d état en mémoire respectant le
même contrat que le vrai, numéro de version compris, tient en trente lignes.

**Le contrôle qui compte le plus : deux écritures concurrentes.** C est le seul
défaut grave d un état partagé naïf, et le seul qui ne se voit pas quand il se
produit — la dernière sauvegarde écrase le travail de l autre en silence. Vérifier
que la seconde échoue, que l écran nomme l auteur, et que rien n est écrasé.

Vérifier aussi ce qu on n aurait pas pensé à vérifier :

- **la fréquence d écriture.** Une fonction d enregistrement appelée à la frappe
  fait un appel réseau par caractère, donc un conflit par caractère. Compter les
  écritures pour une saisie.
- **le grade le plus faible.** Il doit voir les chiffres et se faire refuser
  l écriture avec un message qui nomme ce qu il faut demander.
- **l artefact seul**, sans amorçage : le manque doit être annoncé, pas silencieux.

Aucun contrôle statique ne remplace ça. Constaté : `node --check` vert, contrôle de
sortie vert, et la page **morte au démarrage** — une suppression avait retiré une
définition en laissant son appel. Seul le contrôle qui ouvre la page l a vue.

## Étape 6 — La PR ne change qu une chose

Une balise d image. Le manifeste garde son nom, ses rôles, sa base, son
`cost_center`. **Toute ressource ajoutée ou détruite dans le plan est un signal
d arrêt.**

Ne pas renommer l application parce que le produit a changé de nom : renommer, c
est un nouvel onboardage — application, groupes, URI de redirection, base — et l
état déjà écrit ne suit pas. Un nom de clé n est pas un nom de produit ; la
description du manifeste, elle, se met à jour.

Écrire dans le commentaire de la clé **ce que la balise apporte**, pas seulement
son numéro. La personne qui lira ce fichier dans six mois cherche à savoir
laquelle rétablir.

## Découvrir les valeurs, ne pas les supposer

Ne coder en dur ni registre, ni groupe de ressources, ni serveur. Les relever à l
exécution :

```bash
az acr list --query "[].name" -o tsv
az containerapp list --query "[].{nom:name, rg:resourceGroup, fqdn:properties.configuration.ingress.fqdn}" -o table
az containerapp auth show -n <app> -g <rg> --query "identityProviders.azureActiveDirectory.validation.jwtClaimChecks.allowedGroups"
```

Le manifeste de l application et la table des balises d image vivent dans le dépôt
de la landing zone, sous `environments/<env>/`. Ce sont eux qui font foi.

## Tableau des justifications

| Ce qu on se dit | Ce qui est vrai |
|---|---|
| « C est la même app avec des modules en plus » | Non : c est une autre lignée. Compter les quatre axes avant de le croire. |
| « Je change la ligne `COPY` et je reconstruis » | C est ainsi qu on republie les données sorties au déploiement précédent. |
| « J ai mis un `.dockerignore` » | Il ne protège que `docker build`. `az acr build` l ignore. |
| « Les contrôles statiques sont verts » | Ils ne prouvent pas que la page s ouvre. Faire un contrôle qui exécute. |
| « Le comportement authentifié demande un navigateur » | Deux routes stubbées suffisent. Nommer ce qui reste vraiment invérifiable. |
| « Une seule adresse, c est le demandeur lui-même » | Alors elle s écrit comme exception datée et **comptée**, pas comme oubli. |
| « Je saisirai les données plus tard » | Décrire le geste dans un fichier, sinon la donnée revient dans l artefact. |
| « J écris un petit script d amorçage » | L écran de saisie existe déjà. Le code neuf, c est la dette. |

## Signaux d arrêt

- On s apprête à lancer `az acr build .` depuis le dossier de travail.
- Le contrôle de sortie passe du premier coup, avant toute modification.
- Le plan Terraform annonce autre chose qu un changement de balise.
- Le mot « invérifiable » est sur le point d être écrit.
- On a modifié l artefact **après** avoir construit l image.
- On s apprête à renommer l application pour suivre le nom du produit.

## Ce qui reste au métier, et se dit explicitement

Trois choses ne peuvent pas être faites depuis un poste d agent, et doivent être
rendues comme telles, avec le geste exact : l amorçage des données par les écrans
de saisie, l ouverture depuis un compte de chaque groupe, et le merge de la PR
quand `merge = apply`. Les lister nommément vaut mieux qu un « à vérifier ».
