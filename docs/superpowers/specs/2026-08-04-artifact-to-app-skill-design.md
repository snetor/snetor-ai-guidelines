# Skill `snetor-artifact-to-app` — Design

**Date :** 2026-08-04
**Statut :** Design validé, **en attente de sa dépendance d'infrastructure** — ne pas lancer
`skill-creator` avant que la voie pavée existe (voir *Dépendances*)
**Auteur :** c.peponnet@snetor.com

---

## Problème

Les power users équipés de Claude Enterprise produisent des artefacts `.html` autoportants de plus en
plus aboutis. Tant que l'artefact reste un fichier, tout va bien. Le besoin apparaît quand il lui faut
**une URL partagée, des données qui survivent au rechargement, un panneau d'administration et un
retour arrière**.

Aujourd'hui, deux chemins existent et aucun n'est bon :

- **le low-code laissé libre** — rapide au premier écran, mais il produit structurellement des
  applications hors cadre : environnement inadapté à un usage réel, rollback à granularité
  *environnement* plutôt qu'applicative, et un coût de licence qui n'apparaît qu'au moment de
  régulariser. Il cède par ailleurs dès qu'il faut appeler une API externe ou planifier un traitement ;
- **une landing zone Terraform** — solide, mais son ticket d'entrée réel (écrire du Terraform, faire
  poser des attributions de rôles par un administrateur, créer un utilisateur de base par un job,
  respecter un ordre imposé de fichiers de variables) est hors de portée d'un power user seul.

Ce skill comble le second écart : il rend la landing zone **empruntable** sans en abaisser les
garde-fous.

---

## Principe directeur n°1 — Le skill n'est pas un garde-fou

C'est la règle qui gouverne tout le reste, et celle qui est la plus facile à oublier en cours de
route.

Un skill est de la prose interprétée par un modèle : non déterministe, contournable, et il ne
s'exécute que si quelqu'un l'invoque. **Aucune garantie de sécurité ne repose sur lui.** La contrainte
vit dans le module Terraform, dans le job de validation de la CI et dans les politiques Azure.

Conséquence pratique, à écrire noir sur blanc dans le `SKILL.md` :

> **Le skill produit du code et une pull request. Jamais une infrastructure.**
> Il n'exécute jamais `terraform apply`, ne crée jamais de ressource Azure, n'écrit jamais un secret,
> n'invente jamais un subnet, ne modifie jamais un module. S'il lui manque quelque chose, il
> **s'arrête et le dit** — il ne contourne pas.

Si le skill est mal invoqué, ignoré, ou si le modèle dérive, le pire résultat possible doit être
**une PR qui échoue en CI**. Jamais une ressource orpheline, jamais un accès ouvert.

---

## Principe directeur n°2 — Savoir dire non

La tentation naturelle d'un générateur est de générer. La valeur du skill est en grande partie dans
son refus.

Avant toute génération, quatre questions, dans cet ordre :

1. **Quelle classe de données ?** `publique` / `interne-legere` / `confidentielle` — grille de
   gouvernance Snetor existante.
2. **Combien d'utilisateurs**, et l'artefact doit-il **conserver un état** entre deux usages ?
3. **Quelle durée de vie** — quelques semaines, une saison, durable ?
4. **Quelles intégrations** — API externe, traitement planifié, appel de modèle ?

Trois issues possibles, et **deux sur trois ne produisent pas d'application** :

| Réponses | Issue |
|---|---|
| pas de persistance, ou durée de vie < 3 mois, ou moins de ~5 utilisateurs | **« garde ton HTML »** — le skill explique pourquoi et s'arrête. Un artefact régénérable ne coûte rien et ne se maintient pas. |
| `data_class: confidentielle` | **arrêt** — renvoi vers la DSI. Le skill ne génère rien, même si l'utilisateur insiste. |
| persistance réelle, `interne-legere` ou moins, durée de vie > 3 mois | **génération** |

> Le skill doit énoncer son refus **une fois, brièvement, sans moraliser**, puis proposer la
> meilleure alternative concrète. Pas de sermon sur la gouvernance.

---

## Principe directeur n°3 — Zéro identifiant Snetor dans le skill

`snetor-ai-guidelines` est **public sur GitHub**. Or ce que le skill doit respecter — noms de
ressources, plan d'adressage, identifiants de souscription et de tenant, noms de Key Vault — est de la
topologie interne.

**Le skill ne contient aucun identifiant.** Il lit la topologie **au moment de son exécution** dans le
dépôt `azure-landing-zone` cloné localement, en particulier :

- le document d'arbitrage de la voie pavée, pour les noms du runtime partagé et le périmètre autorisé ;
- le plan IPAM, pour vérifier qu'il n'a **pas** à allouer de subnet ;
- `CLAUDE.md` et `tasks/lessons.md`, pour les pièges déjà connus.

Si ce dépôt n'est pas trouvé, le skill **s'arrête** et demande son chemin. Il ne devine pas, il ne
code pas de valeur par défaut.

Ce que le skill contient, en revanche : la méthode, les gabarits de code, la structure du manifeste
(champs et validations, sans valeurs Snetor), et la liste de ses refus. Tout cela est générique et
publiable.

---

## Principe directeur n°4 — L'autorisation est une frontière de sécurité, donc elle est testée

C'est le point où un générateur d'applications peut faire le plus de dégâts.

Easy Auth ne fait que de l'**authentification** : sans contrôle supplémentaire, tout collaborateur du
tenant qui atteint l'application est traité comme un utilisateur légitime — et si l'application a un
panneau d'administration, comme un administrateur.

La régression classique est de poser un contournement « le temps de la V1 » puis de reporter le
durcissement. Un générateur d'applications industrialise cette régression : il faut donc que le
contrôle soit **généré et testé dès la première version**, pas ajouté ensuite.

Trois exigences non négociables sur le code généré :

1. **Chaque route déclare le rôle qu'elle exige**, et le contrôle est fait **côté serveur** à partir
   des claims injectés par Easy Auth. Aucun contrôle d'autorisation dans le HTML — le front peut
   masquer un bouton, il ne protège rien.
2. **Le mode d'authentification doit refuser les requêtes non authentifiées avant le conteneur.** Le
   skill vérifie que le manifeste demande bien ce mode, et le rappelle dans le runbook.
3. **Un test d'autorisation est généré et doit passer** : pour chaque route d'écriture, une requête
   portant un rôle de lecture seule doit recevoir `403`. Un test qui échoue bloque la PR.

L'audience du jeton étant partagée entre applications en V1, le contrôle serveur des rôles **est** la
frontière entre deux applications. Ce n'est pas un détail d'implémentation, c'est le mécanisme de
sécurité principal.

---

## Principe directeur n°5 — L'artefact est le design, on ne le réécrit pas

Le `.html` du power user porte souvent des heures de mise en forme et une identité visuelle qui lui
plaît. Le réflexe « je reconstruis proprement en React » détruit cette valeur et transforme une
conversion de deux heures en projet d'une semaine.

**Le HTML est servi tel quel, ou presque.** Le skill ajoute autour :

- un serveur minimal qui sert le fichier et expose une API JSON ;
- un remplacement des écritures en mémoire ou en `localStorage` par des appels à cette API ;
- rien d'autre.

Pas de migration vers un framework, pas de refonte de style, pas de découpage en composants. Si le
HTML est trop désordonné pour cela, le skill le dit et propose une réécriture **comme un choix
explicite de l'utilisateur**, jamais comme une décision silencieuse.

---

## Parcours

### Phase 1 — Triage

Les quatre questions du principe n°2. Le skill énonce son verdict et, si c'est un refus, s'arrête là.

### Phase 2 — Lecture de la topologie

Localise `azure-landing-zone`, lit la voie pavée, en déduit ce qui est autorisé. Vérifie que le
runtime partagé existe réellement — s'il n'est pas encore provisionné, **le skill s'arrête** : il n'y
a rien où déployer.

### Phase 3 — Extraction du modèle

Lit le `.html` et en déduit : les entités et leurs champs, les écrans, les actions d'écriture, les
rôles implicites (« cette page n'est visible que par l'organisateur » → rôle `admin`).

**Restitue ce modèle à l'utilisateur et le fait valider avant de générer une ligne.** Une inférence
silencieuse sur un modèle de données est la source d'erreur la plus coûteuse à rattraper : une fois la
base créée et remplie, la corriger demande une migration.

### Phase 4 — Génération

```
<nom-app>/
├── app.yaml                  # le manifeste, seul fichier d'infrastructure
├── Dockerfile
├── migrations/
│   └── 001_initial.sql       # forward-only, numérotées
├── public/
│   └── index.html            # l'artefact, quasi inchangé
├── src/
│   ├── server.ts             # serveur minimal + service des fichiers statiques
│   ├── auth.ts               # décodage des claims, exigence de rôle par route
│   ├── db.ts                 # connexion par identité managée, aucun mot de passe
│   └── routes/
├── tests/
│   ├── auth.spec.ts          # ← le test qui doit échouer si l'autorisation est trouée
│   └── api.spec.ts
├── RUNBOOK.md                # une page : à quoi ça sert, qui appeler, redémarrer, revenir en arrière
└── README.md
```

Contraintes sur le code généré :

- endpoint `/api/healthz` **fonctionnel dès la première image** — une image dont la sonde échoue met la
  ressource en `provisioning failed`, ce qui empoisonne les opérations Terraform suivantes et se règle
  au `taint`. Piège classique, coûteux, évitable en une ligne ;
- **aucun secret** : la connexion à la base passe par l'identité managée ;
- migrations **forward-only**, jamais de `DROP` ni de `ALTER … DROP COLUMN` — le skill refuse d'en
  générer et explique pourquoi (le rollback de données est mutualisé, donc coûteux) ;
- image taguée par SHA de commit, jamais `latest`.

### Phase 5 — Sortie

Deux artefacts, et rien d'autre :

1. le dépôt applicatif, prêt à être poussé en privé ;
2. une **pull request** sur `azure-landing-zone` ajoutant le manifeste — accompagnée du texte de PR
   qui rappelle au relecteur ce qu'il doit vérifier.

Le skill **liste** les étapes manuelles restantes sans les exécuter : onboarding OIDC du nouveau
dépôt, création des groupes Entra, ajout de l'URI de redirection, puis apply au dispatch. Il fournit
les commandes, l'humain les lance.

### Phase 6 — Ce qu'il rappelle en partant

Le TTL, le nom du binôme, et la date de revue. Une application sans date de mort est une dette.

---

## Ce que le skill refuse, sans négociation

| Situation | Réponse |
|---|---|
| `data_class: confidentielle` | arrêt, renvoi DSI |
| besoin de stockage de fichiers, de file d'attente, ou d'un domaine personnalisé | arrêt — hors voie pavée V1 |
| pas de binôme désigné | arrêt |
| `ttl` absent ou au-delà de 12 mois | arrêt |
| runtime partagé introuvable ou non provisionné | arrêt |
| dépôt `azure-landing-zone` introuvable | arrêt, demande le chemin |
| demande d'exécuter `terraform apply` | refus, explication du dispatch manuel |
| demande d'écrire un secret dans le dépôt ou un `.auto.tfvars` | refus |

Un refus n'est pas un échec du skill : c'est sa fonction principale.

---

## Dépendances — ne pas écrire ce skill trop tôt

Le skill automatise un chemin. **Ce chemin doit exister avant.** Prérequis, dans l'ordre :

1. le runtime applicatif partagé est provisionné ;
2. le module `internal-app` et le job de validation du manifeste existent ;
3. **une première application a été déployée à la main par la DSI** — c'est ce déploiement qui révèle
   ce que le skill doit savoir, et aucune spéculation ne le remplace ;
4. le workflow de TTL existe.

Écrire le skill avant l'étape 3 produirait un générateur calé sur une infrastructure imaginaire.

> Détail de ces prérequis, coûts et risques : document d'arbitrage
> `docs/decisions/internal-apps-paved-road.md` du dépôt `azure-landing-zone` (privé).

---

## Hors périmètre

- toute forme d'application publique ou anonyme ;
- le stockage de fichiers, les files d'attente, les domaines personnalisés, la haute disponibilité ;
- la migration d'une application Power Platform existante — sujet distinct, à traiter au cas par cas ;
- le déploiement en production : il n'existe pas d'environnement de production à ce jour, et le skill
  doit le dire plutôt que de laisser croire le contraire.

---

## Critères de vérification

Le skill est considéré comme fonctionnel quand, sur trois artefacts de test :

1. un artefact **sans persistance** reçoit « garde ton HTML » et **rien n'est généré** ;
2. un artefact déclarant des données **confidentielles** est refusé et renvoyé à la DSI ;
3. un artefact légitime produit un dépôt dont `npm test` passe, dont le test d'autorisation
   **échoue** si l'on retire volontairement le contrôle de rôle d'une route d'écriture, et une PR dont
   le job de validation du manifeste est vert ;
4. dans les trois cas, **aucune ressource Azure n'a été créée** et aucun secret n'apparaît dans les
   fichiers générés.

Le point 3, deuxième moitié, est le test du test : un test d'autorisation qui passe quand le contrôle
est absent ne prouve rien.

---

## Points ouverts

- **Pile technique du serveur généré** — à figer au moment de l'écriture du skill, en s'alignant sur
  ce que la première application de référence aura utilisé. Ne pas trancher en spéculant.
- **Où vit le dépôt applicatif** : un dépôt privé par application dans l'organisation, ou un
  mono-dépôt d'applications internes ? Le premier est plus simple à cloisonner, le second réduit le
  coût d'onboarding OIDC répété.
- **Le skill doit-il gérer la mise à jour** d'une application déjà déployée, ou seulement la première
  conversion ? Une V1 limitée à la création est plus sûre ; la mise à jour touche aux migrations, donc
  au rollback.
