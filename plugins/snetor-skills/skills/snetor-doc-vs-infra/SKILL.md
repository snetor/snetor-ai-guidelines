---
name: snetor-doc-vs-infra
description: >
  Confronts what the documentation of a Snetor repo CLAIMS about its infrastructure with what
  Azure ACTUALLY ran - collects every claim (a job runs, an image is current, a resource is
  reachable, a circuit applies), looks for the dated execution that proves it, and sorts it into
  proven / unproven / contradicted. USE THIS SKILL whenever you are about to rely on an
  infrastructure claim written somewhere - "according to the HANDOFF", "d apres le HANDOFF",
  "the runbook says", "le runbook dit que", "this job applies the migrations", "ce job applique
  les migrations", "the app is live", "l app est en ligne", "the CI deploys", "la CI deploie" -
  and whenever a user asks if the docs are up to date, if a runbook still works, or starts work
  on a repo that has Azure infrastructure. Use it BEFORE quoting any infra state, never after.
  Do not use it to check the documentation against itself - that is check_docs.py.
---

# The docs claim, the infrastructure runs

## Why this routine exists

This is the most expensive repeat failure measured across the Snetor repos — **five occurrences in
eight days** on `snetor-pim`, all of the same shape: **a sentence written in a document was taken
for an execution**.

- A Container App job was described as the circuit that applies the migrations. It had **never been
  executed**, and its image froze a schema three months old.
- "`merge = apply`" was written in a context note. It was **false**: `Terraform Apply` ran on a
  manual `workflow_dispatch`.
- A storage account was described as "reachable". It returned `blocked by network rules`.
- **The most expensive one**: "the source being read is S/4HANA production". The assumption held for
  **two months**, carried 6,941 product records, the vocabularies, the row-level security axis and
  an audit delivered to the MDM team. It was caught by a business user, not by the team.

A runbook that has never been executed is not a runbook. A line in `HANDOFF.md` is not a
measurement.

## What you need to know before starting

- ⚠️ **This routine cannot be scheduled in the cloud.** The Entra token expires after ~2 h, and
  delete operations require fresh MFA. Run it from the workstation, signed in.
- **The first `az` call that fails after two hours of session is the token.** Do not look anywhere
  else: `az login` first.
- ⛔ **Never truncate an `az` output through a pipe** (`| tail`, `| head`, `| Select-Object`): the
  exit code gets swallowed with it. The `PreToolUse` guardrail refuses it — read the reason, do not
  work around it.
- On a workstation tunnelled through Cato, outbound SQL (1433) is blocked: a data-plane check goes
  through a job inside the VNet, not from the workstation.

## Sequence

1. **Collect the infrastructure claims.** Sweep `CLAUDE.md`, `HANDOFF.md`, `docs/live/runbooks/`
   and every module `README.md`: note every statement claiming that a job runs, that an image is
   current, that a resource is reachable, that a circuit applies, that an environment is populated.
   List them with their file and line.

2. **Confront each one with a dated execution.** The useful commands:

   ```bash
   az containerapp job execution list -n <job> -g <rg> -o json
   az acr repository show-tags -n <registre> --repository <image> --orderby time_desc -o json
   az containerapp job list -g <rg> --query "[].{nom:name, image:properties.template.containers[0].image}" -o json
   az containerapp revision list -n <app> -g <rg> --query "[?properties.active].{rev:name, image:properties.template.containers[0].image}" -o json
   gh run list --workflow <fichier.yml> --limit 5 --json conclusion,createdAt,event
   ```

   A claim is **proven** if a successful execution carries it, **with its date**. Otherwise it is
   **unproven** — which does not mean false.

3. **Check what the manifests declare against what exists.** A versioned manifest is **not** the
   deployed state: a job created by hand appears in no manifest, and a manifest edited without a
   redeployment changes nothing. Compare the file with the resource group.

4. **Correct nothing in the docs without a measurement.** An unproven claim is marked as such, with
   the date of the attempt to prove it. It is not deleted and not rewritten on a hunch.

## Verification barrier

Every line of the report carries **the command that establishes it and its date**. A line with no
proof of execution does not enter the report: it enters the "unproven" list.

## What to report at the end of the pass

Three lists, in this order:

1. **What is proven** — the claim, the execution that carries it, its date.
2. **What is unproven** — the claim, what was attempted, why it came back empty.
3. **What is contradicted** — the claim, the measurement that disproves it. This is the only
   category that calls for an immediate correction of the docs, in a dedicated commit.

⚠️ Never publish a figure without its denominator and its date.
