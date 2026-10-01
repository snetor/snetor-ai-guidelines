---
name: snetor-app-artefact
description: >
  Builds or evolves a business tool (an HTML page, a dashboard, a spreadsheet turned app) so the
  tech team can deploy it on the Snetor internal platform without rewriting it - shared state
  instead of browser storage, Entra sign-in instead of a login screen, no personal data in the
  file, a contract check that proves it. USE THIS SKILL whenever someone builds a tool that
  colleagues will use or that might go online ("faire une app pour l'équipe", "outil métier",
  "dashboard partagé", "mettre mon outil en ligne", "nouvelle version de mon outil", "build an
  app for my team", "shared dashboard", "v2 of my tool"), from the first version on. A developer
  shipping the result uses snetor-deploy-artefact.
---

# Building a business artifact the platform can deploy

The page will run in two places: alone (a file, a Claude artifact) while it is built, and on the
Snetor platform once deployed, behind Entra sign-in, with its state in a shared database. Build it
for both from the first line. Fixing it at deployment does not last: the next version starts from
the author's copy and brings everything back.

## The contract

1. **One HTML file.** Libraries from a public CDN are fine. No call to any other external service.
2. **State goes through the store, nothing else.** Paste `assets/snetor-store.js` as is, inside the
   page's `<script>`. Read with `snetorStore.load(key)`, write with
   `snetorStore.save(key, valeur, version)` and pass the version you loaded. Keys: `a-z 0-9 _ -`,
   40 characters max, a handful per app, each one a JSON value.
   - Handle the three outcomes of `save`. On `conflict`, name `maj_par`, reload, and never
     overwrite silently. On `forbidden`, show the message, which says what to ask for.
   - Save on an explicit action, or debounced. Never on every keystroke.
3. **No sign-in screen, no password, no hashing.** Who the user is comes from `snetorStore.me()`:
   `nom` to greet, `grade` to decide. `admin` and `writer` may save; `reader` sees everything and
   is refused the write, with the reason shown.
4. **No personal data in the file.** That means no names, emails, or phone numbers of colleagues,
   customers, or suppliers. Ship fictitious demo data, and an import screen (paste from Excel or
   Outlook, or a CSV) that writes the real data to the store. The code carries the organisation;
   the database carries who holds each seat.
   - A rule indexed on positions (`Collaborateur 1/2/3`) works before any name is entered.
   - If the business decides to keep one piece of personal data, for example the owner's contact
     address, it becomes an **exception with an exact count** in `app.json`.
5. **The page never regenerates itself.** Remove any "download the updated file" feature: the
   deployed version replaces the file, not the other way round.

## `app.json`, next to the page

```json
{
  "name": "stock-tracker",
  "purpose": "Monthly stock review for the distribution team",
  "owner": "<owner's role or team>",
  "users": {"admin": "<who>", "writer": "<who>", "reader": "<who>"},
  "data": "internal",
  "state_keys": ["stock-mensuel", "parametres"],
  "exceptions": [{"text": "<exact text>", "count": 1, "decided_by": "<who>", "date": "YYYY-MM-DD"}]
}
```

`name` is lowercase with dashes. It becomes the app's address and the name of its database, so it
never changes afterwards, even if the product is renamed. `data` is one of `public`, `internal`,
`confidential`.

## Prove it

```bash
python scripts/check_artefact.py page.html --fiche app.json
```

Every axis must read `ok`. On a page built before this skill, run it first and expect failures:
it is the to-do list. Then open the page and use it: two saves of the same key from two tabs must
produce the conflict message, not a silent overwrite.

## A new version

Start from the **latest shared version**: the repo, or the copy the tech team sent back. Never
start from an old local file. Rerun the check before handing it over; a drift in an exception
count means the data came back out somewhere else.

## Hand-over: two paths

- **Default: no GitHub.** Send the tech team three things: the page, `app.json`, and the check
  output. The team creates the repo and deploys it.
- **Power user with Claude Code.** The app lives in its own repo: `index.html`, `app.json`,
  `README.md`. Work on a branch and open a pull request for the tech team to review. Never push to
  `main`. The check output goes in the PR description.

Neither path deploys anything. Access groups, the database, and going online stay with the tech
team (snetor-deploy-artefact).
