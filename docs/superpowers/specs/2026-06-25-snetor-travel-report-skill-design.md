# Skill `snetor-travel-report` — Design

**Date :** 2026-06-25
**Statut :** Design validé, prêt pour `skill-creator`
**Auteur :** a.lagache@snetor.com

---

## Problème

Les sales de Snetor doivent rédiger un rapport après chaque voyage (visite d'un ou
plusieurs clients) et l'envoyer à `travel-report@snetor.com`. Un pipeline existant
(client-matrix → Twenty CRM) lit cette boîte, extrait les données même non structurées
et nourrit la matrice client.

Aujourd'hui, écrire le rapport est un effort manuel, souvent fait de mémoire au retour,
avec des oublis. On veut que le sales puisse **dicter** son rapport à Claude **au fil du
voyage**, et que Claude — qui connaît le jargon Snetor et les champs attendus — **interagisse**
(relance sur ce qui manque) puis produise une **première version rédigée** du rapport
quand le sales dit « voyage fini ».

Ce n'est PAS une simple transcription : la valeur est dans l'**interview structurée**
(jargon + champs + relances), pas dans la rédaction.

---

## Principe directeur n°1 — Le template est un plancher, pas une cage

Le risque majeur identifié : un skill trop rigide qui colle aux templates et aplatit la
richesse de ce que dit le sales. Quatre règles de comportement prévalent sur tout le reste :

1. **Capturer tout ce que le sales dit en plus.** Rumeur de rachat, mouvement d'un
   concurrent, anecdote relationnelle, projet d'usine… c'est gardé (dans les *notes* ou en
   texte libre), même sans champ dédié. On ne jette jamais de l'info parce qu'elle ne rentre
   pas dans une case. Les vrais rapports Snetor sont riches et narratifs — préserver cette
   richesse.
2. **Une relance, puis on lâche.** Champ-clé manquant → signalé **une seule fois**,
   brièvement. Si le sales ne complète pas → « — » ou champ vide, et on avance. Zéro harcèlement.
3. **Le ton s'adapte au sales.** Sales laconique → fiche concise. Sales bavard → fiche fournie.
4. **Fidélité avant structure.** Ne pas compresser une nuance que le sales a pris le temps
   de dire. Le template *ordonne* l'info, il ne la censure pas.

Le template sert à deux choses seulement : (a) savoir quoi **relancer** quand un champ-clé
manque, (b) **ranger** l'info à la fin.

---

## Architecture

### Nature & emplacement

- **Skill portable** `snetor-travel-report` dans le plugin existant :
  `plugins/snetor-skills/skills/snetor-travel-report/`
- **Source unique de vérité** = `SKILL.md` + fichiers de référence (versionné dans le repo).
- Fichiers de référence :
  - `references/templates.md` — les deux trames (polymères + chemicals).
  - `references/glossaire.md` — copie du glossaire Snetor (normalisation du jargon).
  - `references/report-style.md` — 2-3 extraits de vrais rapports comme modèles de ton/structure.

### Canal de déploiement — à confirmer par test (hors périmètre immédiat)

On construit le skill d'abord (95 % du travail, commun à tous les canaux). Le canal mobile
sera tranché **par un test réel** après coup :

- **Option par défaut :** Projet Claude sur mobile. Les instructions du Projet = le contenu
  du skill ; fichiers de référence déposés dans le Projet. « Une conversation = un voyage »
  → règle la continuité (le sales rouvre son voyage en cours) et le déclenchement (instructions
  toujours actives).
- **Si le skill se déclenche bien seul sur mobile :** pas besoin d'enveloppe Projet.

Décision : on ne tranche pas le canal maintenant. Le Projet Claude sera traité dans un
chantier séparé une fois le skill construit et testé.

---

## Modèle d'interaction (approche « fiche client »)

L'unité de travail est la **fiche client compacte**. Elle joue trois rôles : relance (les ❓
montrent les trous), validation (le sales corrige tout de suite), état durable (courte,
scannable ; reste le registre canonique même sur une longue conversation).

1. **Début de voyage** — Claude récupère l'en-tête : sales rep, dates, localisation(s),
   accompagnants (GPM/collègues), et capte la vue générale (contexte marché) si le sales a
   déjà des choses à dire.
2. **Par client dicté** — Claude :
   - infère la **BU du client** d'après les produits cités (confirme si ambigu) ;
   - **normalise le jargon** via le glossaire (ex. « blow PE » → famille/sous-famille/grade) ;
   - renvoie une **fiche structurée compacte** au bon format de bloc ;
   - met un **❓ sur les champs-clés manquants** + une relance ciblée et brève (une fois) ;
   - le sales valide / corrige / ignore.
3. **Section marché (optionnelle)** — sizing, opportunités nouveaux produits, prospects à revoir.
4. **« Voyage fini »** — Claude **assemble** le rapport complet (en-tête + vue générale +
   fiches + section marché), dans la **langue du sales**, prêt à relire puis envoyer à
   `travel-report@snetor.com`. Claude précise que c'est un **brouillon à relire** et
   **n'envoie pas** l'email lui-même.

### Mode mixte (BU par client)

Un voyage peut mélanger polymères et chemicals (cf. rapport Jamaïque de William Junco).
Le skill **tague la BU par client**, déroule le bon bloc, et assemble un rapport unique
pouvant contenir les deux types de blocs.

---

## Le cerveau — champs par BU

**En-tête (commun) :** sales rep · dates de voyage · localisation(s) (pays/ville) ·
avec (GPM/collègues) · vue générale (contexte marché, prix, tendances, réglementations, concurrence).

**Bloc client POLYMÈRES :**
- Client — secteur — statut (Client | Prospect)
- Contact (nom, rôle)
- Consommation par grade : Famille / Sous-famille / Grade / Application / Volume·mois
- Opportunités (intérêt / test / sample / quote / projet / volume cible / recyclé)
- Plan d'action
- Notes (fournisseurs actuels & concurrence, conditions de paiement, alertes)

**Bloc client CHEMICALS :**
- Client — secteur — statut (Client | Prospect)
- Contact (nom, rôle)
- Besoins par produit : Produit / Grade-spec / Volume·mois / Fournisseur actuel / Conditions
- Sourcing requests (produits qu'ils veulent qu'on source)
- Opportunités (nouveau produit / sample / quote / intérêt / volume cible)
- Plan d'action
- Notes (paiement & crédit, market intel, alertes)

**Section marché (fin, optionnelle) :** sizing / besoins · opportunités nouveaux produits ·
prospects à revoir la prochaine fois.

### Champs-clés (déclenchent un ❓) vs confort

- **Clés :** statut (client/prospect) · au moins un produit avec famille/grade · volume
  (ou « — » assumé) · plan d'action.
- **Confort (demandé une fois, sans insister) :** rôle du contact · fournisseur actuel ·
  conditions de paiement.

---

## Garde-fous

- **Colle à la langue du sales** (FR / EN selon ce qu'il utilise).
- **N'invente jamais** un volume ou un grade : incertain → ❓ ou « — ».
- Normalise le jargon mais **signale le doute** plutôt que de deviner un grade.
- Relances **groupées et brèves**, jamais champ par champ comme un formulaire.
- Rapport final = **brouillon à relire**, l'email n'est **pas** envoyé par Claude.

---

## Hors périmètre (YAGNI)

- Pas d'écriture directe dans Twenty/CRM (le parser email gère l'ingestion).
- Pas d'envoi d'email automatique.
- Pas de gestion de l'audio (l'app mobile transcrit ; le skill travaille sur le texte).
- Pas de mémoire multi-voyages (une conversation = un voyage).
- Le déploiement Projet Claude : chantier séparé, après construction et test du skill.

---

## Critères de réussite

1. Sur une dictée polymères, le skill produit une fiche client avec famille/grade/application/
   volume correctement normalisés depuis le langage naturel du sales.
2. Sur une dictée chemicals, idem avec produit/volume/fournisseur/conditions.
3. Quand le sales dit plus que le template (anecdote, intel marché), l'info est **conservée**
   dans le rapport final, pas jetée.
4. Quand un champ-clé manque, le skill relance **une fois** puis avance sans insister.
5. Sur un voyage mixte (polymères + chemicals), le rapport final contient les deux types de
   blocs, assemblés proprement.
6. Le rapport final est dans la langue du sales, au format/ton proche des vrais rapports Snetor,
   et présenté comme un brouillon à relire.

---

## Livrables

1. Le skill (`SKILL.md` + `references/`) dans `plugins/snetor-skills/skills/snetor-travel-report/`.
2. (Chantier séparé) Un bloc « instructions de Projet » + fichiers, prêts pour un Projet Claude
   mobile.
