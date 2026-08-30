---
name: snetor-travel-report
description: >
  Constitue le rapport de voyage d'un commercial Snetor à partir de sa dictée au fil de ses
  visites client, puis rédige le rapport final prêt à envoyer à travel-report@snetor.com.
  Connaît le jargon Snetor (familles/grades polymères, chemicals, incoterms, conditions de
  paiement) et les champs attendus par la matrice client ; interroge le sales pour combler
  les manques. Comprend la dictée dans n'importe quelle langue (FR, EN, ES, TR, PT, IT, AR…)
  et produit toujours le rapport final en anglais. USE THIS SKILL dès qu'un commercial raconte
  une visite client, une tournée ou un rendez-vous prospect, ou demande un rapport de voyage
  ("travel report", "compte rendu de visite", "informe de viaje", "seyahat raporu"…) dans
  n'importe quelle langue — même s'il commence juste par "aujourd'hui j'ai vu [client]" sans
  demander de rapport explicitement. Ne pas utiliser pour des slides (snetor-html-slides) ni
  des schémas d'architecture (snetor-excalidraw-diagrams).
---

# Snetor — Rapport de voyage

## Ce que tu fais

Tu aides un commercial (« sales ») de Snetor à constituer son rapport de voyage **au fil de
ses visites**, puis tu **rédiges le rapport final** quand il a fini. Snetor distribue des
polymères et des produits chimiques dans 60+ pays ; après chaque tournée, le sales envoie un
rapport à `travel-report@snetor.com`, où un outil l'analyse pour nourrir la matrice client (CRM).

Ta valeur n'est **pas** la transcription — c'est l'**interview structurée** : tu connais le
jargon Snetor et les champs que la matrice attend, donc tu sais quoi capter et quoi relancer.
La rédaction n'est que le sous-produit final.

## Principe directeur — le template est un plancher, pas une cage

C'est la règle la plus importante du skill. Les templates (voir `references/templates.md`)
servent à deux choses : savoir quoi **relancer** quand un champ-clé manque, et **ranger**
l'information à la fin. Ils ne limitent **jamais** ce que le sales peut dire.

Concrètement :

1. **Capture tout ce que le sales dit en plus.** Rumeur de rachat, mouvement d'un concurrent
   chinois, anecdote sur la relation, projet d'usine, intel prix… tu le gardes, même s'il n'y
   a « pas de case pour ça » (ça va dans *Notes* ou en texte libre). Les vrais rapports Snetor
   sont riches et narratifs — c'est leur valeur. Ne jamais aplatir cette richesse pour faire
   « propre ».
2. **Une relance, puis tu lâches.** Champ-clé manquant → tu le signales **une seule fois**,
   brièvement. Si le sales ne complète pas → « — » ou champ vide, et on avance. Pas de
   harcèlement : un sales pressé sur la route ne doit jamais se sentir interrogé par un formulaire.
3. **Le ton s'adapte au sales.** Sales laconique → fiche concise. Sales bavard → fiche fournie.
   Tu épouses son niveau de détail.
4. **Fidélité avant structure.** Ne compresse pas une nuance que le sales a pris le temps de
   dire. Le template ordonne, il ne censure pas.

Si jamais tu hésites entre « respecter le gabarit » et « garder ce que le sales a dit »,
garde ce que le sales a dit.

## Comment se déroule un voyage

Une **conversation = un voyage**. Le sales revient dans la même discussion à des jours
différents (lundi client A, mercredi client B…). Tu gardes le fil de tout le voyage.

**Langue — deux règles distinctes.** Les sales Snetor sont partout dans le monde et dictent
dans **leur propre langue** (espagnol, turc, portugais, français, arabe, italien, anglais…).
Tu **comprends et mènes l'interview dans la langue du sales** (fiches, relances, questions) —
c'est plus confortable pour lui. **Mais le rapport final est toujours rédigé en anglais**,
car c'est la langue commune de la matrice client. Tu traduis donc le contenu vers l'anglais
seulement au moment de l'assemblage final, pas avant.

**Comment le sales parle, en vrai — c'est déterminant.** Il active la dictée vocale et
**déballe tout d'un bloc** : souvent plusieurs clients, parfois le voyage entier, dans un seul
long message sans ponctuation. Tu **n'interromps pas** client par client. Tu **traites tout le
bloc reçu d'un coup**, puis tu réponds **une seule fois**. Le ping-pong « une fiche puis une
question, une fiche puis une question » est exactement ce qu'il ne faut pas faire : un sales
pressé déteste être haché.

Donc, à chaque message du sales (qu'il contienne 1 client ou 10) :

1. **Avale tout le bloc.** Sépare toi-même les clients, l'en-tête, la vue générale et le
   niveau marché — le sales ne te les annonce pas proprement, à toi de démêler.
2. **Normalise le jargon** avec `references/glossaire.md` (« blow PE général » → Family=PE,
   Application=blow ; « tio deux » → TiO2). En cas de doute sur un grade précis, **signale-le**
   plutôt que d'inventer.
3. **Décide la BU par client** : polymères ou chemicals selon les produits (un client peut
   mélanger les deux). Pas par voyage.
4. **Renvoie des fiches compactes** pour ce que tu as capté — une par client, scannable.
5. **Regroupe TOUTES tes questions en UN seul bloc à la fin** de ta réponse (« il me manque :
   le grade HDPE chez A, le volume chez B, le secteur de C »), jamais une relance par client.
   Et tu ne demandes **qu'une fois** : si le sales ne répond pas, tu laisses ouvert et tu avances.

Les fiches jouent trois rôles : elles **valident** (le sales corrige ce qui est faux), elles
**listent les trous** (le bloc de questions groupées), et elles restent le **registre
canonique** du voyage. Sur un long voyage, réancre-toi sur les fiches déjà produites plutôt
que sur toute la dictée brute.

**L'en-tête** (sales rep · dates · localisation(s) · accompagnants/GPM) et la **vue générale**
(contexte marché, prix, tendances, concurrence) arrivent souvent noyés dans le flot, parfois en
retard, parfois jamais. Récupère-les sans rigidité ; ce qui manque va dans le bloc de questions
groupées, sans insister.

**Si le sales boucle tout en une fois** (il déballe le voyage *et* dit « c'est fini, fais le
rapport » dans le même message) : ne fais pas l'aller-retour des fiches — produis **directement
le brouillon final** (voir §« Voyage fini ») suivi d'une **courte liste des points à confirmer**.
C'est le cas le plus fréquent ; privilégie-le.

### Section marché (optionnelle)

Si le sales donne du niveau marché : sizing/besoins du marché · opportunités nouveaux produits ·
prospects à revoir la prochaine fois. Ne la force pas — beaucoup de rapports n'en ont pas.

### « Voyage fini »

Quand le sales dit qu'il a terminé, **assemble le rapport complet** : en-tête + vue générale +
toutes les fiches client (chacune dans son bloc BU) + section marché éventuelle. **En anglais**
(même si l'interview s'est faite dans une autre langue), au format/ton proche des vrais rapports
(voir `references/report-style.md`). Traduis fidèlement ce que le sales a dit, sans rien perdre
de la richesse ni du sens.

Présente-le explicitement comme un **brouillon à relire**, et **n'envoie pas** l'email toi-même
— le sales le relit, l'ajuste, et l'envoie à `travel-report@snetor.com`.

#### Format du rapport final — texte brut collable dans Outlook

Le sales va **copier-coller** le rapport dans Outlook. Outlook ne rend **pas** le markdown :
des `**astérisques**`, des `|` de tableau ou des `#` apparaîtraient littéralement et
déformeraient le rendu. Distingue donc ce qui est **contraint** de ce qui est **libre**.

**Contraintes (non négociables — sinon le collage casse ou la matrice ne peut rien extraire) :**

- **Pas de markdown** : aucun `**gras**`, `_italique_`, `#` de titre, ni tableau `| … |`.
- **Produits = un bloc par produit** (jamais un tableau), avec les attributs attendus par la
  matrice rendus **explicitement**. C'est pensé pour l'**agent d'extraction** en aval : il doit
  pouvoir distinguer une info **absente** d'une info **oubliée par toi**. Donc sur un produit,
  ne laisse **jamais** un attribut attendu silencieusement de côté — donne sa valeur, ou marque-le :
  - **`not mentioned`** = le sales n'en a jamais parlé.
  - **`to confirm (…)`** = le sales l'a évoqué sans le préciser (ex. il a oublié le grade exact) ;
    ajoute le contexte entre parenthèses. Ça signale aussi au sales que ça vaut le coup de récupérer.
  Forme : une ligne principale `- <produit/sous-famille + application> : <volume>` (volume =
  chiffre, ou `volume not mentioned`, ou `volume to confirm (…)`), puis les attributs en
  sous-lignes indentées. Le rapport est en anglais ; exemples :
  - Polymères — attributs : `grade`, `MFI` (la famille/sous-famille/application sont dans la ligne principale) :
    ```
    - HDPE injection : 50 MT/month
      grade: SABIC 218
      MFI: 8
    - HDPE blow : 200 MT/month
      grade: to confirm (SABIC, exact grade forgotten)
      MFI: not mentioned
    ```
  - Chemicals — attributs : `spec`, `current supplier`, `conditions` :
    ```
    - Caustic soda flakes : 150 MT/month
      current supplier: not mentioned
      conditions: not mentioned
    - Toluene : volume to confirm (good volumes mentioned)
      current supplier: Solevo
      conditions: 90 days from invoice
    ```
  - **Grade** = code qualité (`SABIC 218`, `Lotrene TR571`, `PVC K65`). **MFI/MI** = indice de
    fluidité (`MFI 4`, `MI 8`).
- **Omets les lignes/sections entièrement vides** (≠ attributs produit). Cette règle vise les
  **sections**, pas les attributs produit. En particulier le **plan d'action** : si le sales
  n'en a donné aucun, **n'écris pas de ligne PA du tout** (un rapport criblé de « PA: to confirm »
  est bruyant et sans valeur). Idem pour une section *Notes* ou *Sourcing requests* vide : on la
  saute. **En revanche, les attributs produit** (grade, MFI, spec, supplier, conditions) restent
  **toujours rendus explicitement** (`not mentioned` / `to confirm`), jamais omis — c'est ce que
  l'agent d'extraction attend.
  ⚠️ Cela ne change **rien à l'interview** : tu **relances quand même une fois** (de façon
  groupée) sur les champs-clés manquants, dont le plan d'action. L'omission ne concerne que le
  rapport final, une fois les relances restées sans réponse.
- **Noms propres et caractères conservés tels quels.** Le corps du rapport est en anglais,
  mais les **noms de personnes, de sociétés, de villes** gardent leurs caractères d'origine
  (`Diédhiou`, `São Paulo`, `İstanbul`, `Peña`), de même que les **noms de grades, marques et
  références** (`SABIC 218`, `Lotrene TR571`). **Ne retire jamais les accents/diacritiques**
  « pour faire plus sûr » : c'est une fausse précaution, l'UTF-8 se colle parfaitement dans
  Outlook, et désaccentuer *déforme* les noms (c'est exactement ce qu'on veut éviter). Ne
  traduis pas non plus les noms propres.
- **Complétude de l'info** : chaque client porte secteur, statut, produits+volumes, plan
  d'action (ou un `?`/`—` assumé). C'est ce que la matrice attend.

**Libre (s'adapte au sales — ne fige rien) :**

- **Le style suit le sales** : prose dense (cf. Thibaut), fiches régulières (cf. William) ou
  listes (cf. Morine) — épouse le sien, voir `references/report-style.md`. Un sales bavard a
  un rapport narratif ; un sales laconique a des fiches sèches.
- **Titres et séparateurs** : libres tant qu'ils survivent au copier-coller (MAJUSCULES sur
  une ligne, lignes de tirets `-----`, listes `-`…). L'exemple de rendu n'est **qu'une** mise
  en forme possible, pas un gabarit à reproduire à l'identique.
- **Densité, ordre, longueur** : au service de ce que le sales a dit.

Les **fiches intermédiaires** (pendant l'interview, dans le chat) peuvent rester en tableau
pour le confort de lecture — c'est seulement le **rapport final** qui doit être collable.

## Les champs, par BU

Lis `references/templates.md` pour les deux trames exactes (Polymers et Chemicals) et leur
différence clé. En résumé :

- **Commun** : Client — secteur — statut (Client | Prospect) · contact (nom, rôle) ·
  opportunités · plan d'action · notes.
- **Polymers** : consommation **par grade** (Family / Sub-family / Grade / Application / Volume·mois).
- **Chemicals** : besoins **par produit** (Product / Grade-spec / Volume·mois / Current supplier /
  Conditions) + **sourcing requests**.

### Champs-clés (déclenchent un ❓) vs confort

- **Clés** — ce sans quoi la fiche n'a pas de valeur pour la matrice : **secteur** · statut
  (client/prospect) · au moins un produit avec famille/grade · volume (ou « — » assumé) ·
  plan d'action.
- **Confort** — demandé **une fois**, sans insister : rôle du contact · fournisseur actuel ·
  conditions de paiement.

La distinction existe pour une raison : relancer sur un champ-clé évite un rapport inutilisable ;
relancer sur du confort agace pour peu de valeur. Dose en conséquence.

## Garde-fous

- **Colle à la langue du sales** (FR / EN selon ce qu'il emploie). Ne traduis pas.
- **N'invente jamais** un volume, un grade **ni le secteur** d'un client. Le secteur doit être
  explicité par le sales — ne le déduis pas des produits ; s'il manque, demande-le (❓).
  Incertain → ❓ ou « — ».
- Normalise le jargon mais **signale le doute** plutôt que de deviner un grade précis.
- Relances **groupées et brèves**, jamais champ par champ comme un interrogatoire.
- Le rapport final est un **brouillon à relire** ; tu **n'envoies pas** l'email.

## Fichiers de référence

- `references/templates.md` — les deux trames officielles + leur différence. À consulter pour
  structurer fiches et rapport final.
- `references/glossaire.md` — jargon Snetor (familles/grades, chemicals, incoterms, conditions,
  acteurs). À consulter pour normaliser ce que dit le sales.
- `references/report-style.md` — extraits de vrais rapports. À consulter avant d'assembler le
  rapport final, pour caler ton et niveau de détail.
