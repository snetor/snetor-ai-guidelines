# Templates de rapport de voyage Snetor

Deux trames officielles : **Polymers** et **Chemicals**. Un voyage peut mélanger les deux
(BU décidée **par client**, pas par voyage). Le template ordonne l'information à la fin —
il ne limite pas ce que le sales peut dire. Tout ce qui est dit en plus est conservé
(dans *Notes* ou en texte libre).

> **Note de rendu.** Les colonnes et le « — » ci-dessous décrivent **quels champs existent** —
> c'est une vue de référence, pas la mise en forme du rapport envoyé. Le **rapport final**
> (celui que le sales colle dans Outlook) suit les règles de la section « Format du rapport
> final » de `SKILL.md` : texte brut, **un bloc par produit** (pas de tableau). Les **attributs
> produit** manquants y sont rendus **explicitement** (`not mentioned` si jamais évoqué,
> `to confirm (…)` si le sales l'a oublié) pour faciliter l'extraction — jamais un « — » de
> remplissage. Les **sections entièrement vides** (plan d'action, notes…) sont en revanche
> **omises**. Ne reproduis donc pas les tableaux dans l'email.

---

## Template — Polymers

```
Travel report — Polymers
Sales rep:
Travel dates:
Location(s) — country / city:
With (GPM / colleagues):
General overview: market context, prices, trends, regulations, competition…

<CLIENT NAME> — <Sector> — <Client | Prospect>
Contact: <Name (role)>

Products consumed — one row per grade:

Family    Sub-family    Grade    Application    Volume/month

Family = PE, PP, PS, PET, PA, POM, PVC… · Sub-family = LLDPE, HDPE, PP Homo… ·
Grade = quality code, e.g. SABIC 218 · Application = film, injection, blow, roto…

Opportunities: interest / ready to test / sample / quote / project / target volume / recycled interest
Action plan:
Notes: current suppliers & competition, payment terms, alerts

Market level (optional — end of report)
Market sizing / needs:
New product opportunities:
Prospects to see next time:
```

---

## Template — Chemicals

```
Travel report — Chemicals
Sales rep:
Travel dates:
Location(s) — country / city:
With (colleagues):
General overview: market context, trends, competition…

<CLIENT NAME> — <Sector> — <Client | Prospect>
Contact: <Name (role)>

Needs — one row per product:

Product    Grade / spec    Volume/month    Current supplier    Conditions

Volume: leave « — » if not given · Current supplier = who they buy from now ·
Conditions = payment terms / incoterm if mentioned

Sourcing requests: products they want us to find / source
Opportunities: new product / sample / quote / interest / target volume
Action plan:
Notes: payment & credit, market intel, alerts

Market level (optional — end of report)
Market sizing / needs:
New product opportunities:
Prospects to see next time:
```

---

## Différence clé entre les deux blocs client

| | Polymers | Chemicals |
|---|---|---|
| Cœur produit | **Consommation par grade** : Family / Sub-family / Grade / Application / Volume·mois | **Besoins par produit** : Product / Grade-spec / Volume·mois / Current supplier / Conditions |
| Section spécifique | (recyclé dans Opportunities) | **Sourcing requests** (produits qu'ils veulent qu'on source) |
| Notes | fournisseurs & concurrence, paiement, alertes | paiement & crédit, market intel, alertes |

Le reste (en-tête, statut Client/Prospect, contact, opportunités, plan d'action, section
marché) est commun.
