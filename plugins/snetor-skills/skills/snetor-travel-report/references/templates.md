# Snetor travel report templates

Two official frames: **Polymers** and **Chemicals**. A trip can mix both (BU decided **per
client**, not per trip). The template orders the information at the end — it does not limit
what the sales rep can say. Everything said on top is kept (in *Notes* or in free text).

> **Rendering note.** The columns and the "—" below describe **which fields exist** — it is a
> reference view, not the layout of the report that gets sent. The **final report** (the one the
> sales rep pastes into Outlook) follows the rules of the "Final report format" section of
> `SKILL.md`: plain text, **one block per product** (no table). Missing **product attributes**
> are rendered there **explicitly** (`not mentioned` if never raised, `to confirm (…)` if the
> sales rep forgot it) to ease extraction — never a filler "—". **Entirely empty sections**
> (action plan, notes...), on the other hand, are **omitted**. So do not reproduce the tables in
> the email.

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

## Key difference between the two client blocks

| | Polymers | Chemicals |
|---|---|---|
| Product core | **Consumption per grade**: Family / Sub-family / Grade / Application / Volume·month | **Needs per product**: Product / Grade-spec / Volume·month / Current supplier / Conditions |
| Specific section | (recycled goes into Opportunities) | **Sourcing requests** (products they want us to source) |
| Notes | suppliers & competition, payment, alerts | payment & credit, market intel, alerts |

The rest (header, Client/Prospect status, contact, opportunities, action plan, market section)
is common.
