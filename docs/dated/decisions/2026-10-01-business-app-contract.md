---
regime: dated
audience: [dev, business]
date: 2026-10-01
status: decided
supersedes: docs/dated/decisions/2026-08-04-skill-artifact-to-app.md
---

# Business app contract: build deployable, instead of fixing at deployment

## Context

Business artifacts reached the internal platform through `snetor-deploy-artefact`, a developer
skill that runs **after** the fact. It takes personal data out, replaces browser storage with
shared state, and replaces home-made logins with Entra sign-in. Every new version undid that
work. A v2 descends from its author's local copy, which never saw the fixes, so it brings them
all back.

The three apps already deployed show the cost:

- They converged on the same files: server, Dockerfile, build script, a verify workflow, and a
  deliver workflow.
- Each one rewrote them anyway. The servers run to 967 and 1,399 lines with 8% of their lines in
  common, and the delivery files are only 26 to 47% alike.

The 2026-08-04 proposal (a skill generating a full app skeleton) was never built. It waited for a
runtime that now exists, and it put the work at the wrong end of the chain.

## Decision

Move the rules to where the artifact is built, and make them checkable:

1. **A contract.** One HTML file. State only through a pasted store module
   (`snetor-store.js`) that talks to the platform's existing state API (`/api/moi`, and
   `/api/etat/<key>` with a version number, so a stale write fails instead of overwriting).
   No login screen. No personal data, except exceptions with an exact count. The page never
   regenerates itself.
2. **A check, `check_artefact.py`.** The business user runs it while building; the developer
   reruns it with `--deploy` as the gate before the image build.
3. **`snetor-app-artefact`**, in `snetor-skills` (everyone), which builds and evolves tools
   to that contract.
4. **Hand-over on two paths.** By default the business user never touches GitHub and sends
   the page, `app.json`, and the check output. A power user on Claude Code works in an app repo,
   on a branch, through a reviewed PR.

The wire names of the API (`valeur`, `version`, `maj_par`, `grade`) stay in French. They are an
interface already in production, not prose.

## Phases

1. Contract, check, skill. Done with this decision. On the original artifacts of two deployed
   apps, the check fails on exactly what their deployment had to remove: login screens, browser
   storage, self-download.
2. Slim `snetor-deploy-artefact`. Its audit and extraction steps become "run the check". Its
   persistence count moves to "zero outside the store block".
3. An app repo template extracted from the deployed apps, when the next app arrives.

## Not decided here

Whether app repos get their own CI. Each one adds GitHub Actions minutes on a plan whose quota
has already run out once.
