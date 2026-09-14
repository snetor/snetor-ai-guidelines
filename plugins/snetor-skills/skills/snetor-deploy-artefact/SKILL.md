---
name: snetor-deploy-artefact
description: >
  Deploys a self-contained business artifact (a power user HTML page, a spreadsheet
  turned application) onto the Snetor paved road - audits what the artifact brings back
  in, moves personal data out to the shared state, wires identity and permissions onto
  Easy Auth, builds an explicit build context, then opens the PR that changes nothing but
  the image tag. USE THIS SKILL as soon as a user wants to put online or update a business
  application that came from a file ("deployer cet artefact", "nouvelle version du HTML",
  "le power user a livre une v2", "mettre son outil sur la voie pavee", "deploy this
  artifact", "ship this artifact", "the power user shipped a v2", "new version of the
  HTML", "put their tool on the paved road", "paved road"), and BEFORE touching the
  Dockerfile or launching a build. Do not use to onboard an application that already has
  its own repo and CI - this one patches its own image key.
---

# Deploying a business artifact onto the paved road

A business artifact is a self-contained page, written by someone from the
business, that already works on their machine. Deploying it is not a technical
port: it is making an object designed to travel as an attachment fit inside a
shared architecture.

**The principle that governs everything else: a container image is a lasting
copy.** Removing a piece of data from the file afterwards does not remove it from
the tags already pushed. Everything below follows from that.

## What makes this deployment different from any other

An artifact v2 **does not descend from the deployed version.** It descends from
the local version of its author, who never saw your adaptations and had no reason
to know about them. So it brings back in exactly what the previous deployment had
taken out.

That is the central trap, and it does not show: the artifact opens, it is richer
than before, all is well. Seen for real — an artifact delivered as a v2 brought
back the three names taken out a month earlier, plus a hundred more addresses.

## Step 1 — Audit, before any plan

Plan nothing before comparing the new artifact to the one running, on **four
axes**. They regress together, because they all come from the same local file.

| Axis | What to count | What it means |
|---|---|---|
| Personal data | names, email addresses, phone numbers, identifiers | must be 0, apart from a named exception |
| Persistence | `localStorage`, `sessionStorage`, `indexedDB` | must be 0: the state is shared or it does not exist |
| Authentication | passwords, hashes, `crypto.subtle`, login screens | must be 0: that is Easy Auth |
| Distribution | regenerating the file, "download and replace" | the image replaces the file, not the other way round |

Count, do not skim. On both files, side by side:

```bash
for f in "ancien.html" "nouveau.html"; do
  echo "== $f"
  for p in localStorage sessionStorage "/api/etat" "/api/moi" "@votredomaine.com" "fetch("; do
    printf "%-22s %s\n" "$p" "$(grep -o -- "$p" "$f" | wc -l)"
  done
done
```

A `localStorage` at 18 and a `fetch(` at 0 say everything: the artifact does not
know a server exists.

**Then look for the graft point.** A mature power user artifact almost always has
an internal boundary — a core, a module registry, a serialization function.
Modules read their state there at startup and write it back to the same place. A
single pattern, repeated: it gets replaced once. Look for that boundary
**before** proposing a rewrite, it exists more often than expected.

## Step 2 — The exit check, written before the surgery

A script, versioned, not a read-through. A read-through does not catch the same
thing twice in a row; that is precisely why the v2 arrives loaded.

It asserts, on the file, what the image is not allowed to carry away: identities
expected at zero, `localStorage` and friends at zero outside comments, and **the
exact count** of every exception.

**Run it on the artifact as received first, and check that it FAILS.** A check
that passes on the first try checks nothing: a badly escaped pattern gives a
reassuring `OK` on an artifact full of addresses. Give it its own self-test too —
the checking function must detect what gets injected into it on purpose.

### Exceptions are counted

When the business wins the right to keep a piece of personal data — the contact
address of the owner, typically —, the rule does not become "no data, except…",
which no longer means anything. It becomes an **exact count**, with its date and
its decision maker:

> exactly 1 occurrence of this name and 3 of this address, no others.

The count does more than document: a drift signals that the data has **come back
out somewhere else**, typically in a recipient list.

## Step 3 — Take the data out, without writing seeding code

Personal data leaves the artifact and goes into the shared state. The split to
hold: **the code carries the organisation, the database carries who holds the
seat.** Rules indexed on `0/1/2` work before the names are even entered — the
screen shows "Collaborateur 1/2/3" and nothing breaks.

To put them back: **use the input screens that already exist.** An artifact that
carried 60 recipient addresses necessarily has a screen to edit them, and its
paste handler probably already accepts the Outlook format. Writing a seeding
mechanism would be new code for a one-time gesture.

Keep the extracted data in a seed folder, **outside the image**, with a file that
says why it is not in there — otherwise someone will add a `COPY . /app` on a
tired day. The seed must have the shape the import screen expects: if the import
*replaces* a list, a seed reduced to the addresses alone would wipe out
everything else.

## Step 4 — ⚠️ The build context is explicit, never implicit

**`az acr build` does not honour `.dockerignore`.** Verified: a 40 MB marker
dropped in an ignored folder moves the announced context from 6.58 to 46.6 MiB.
So the seed folder leaves with the context, towards the build service.

The `Dockerfile` names its `COPY` lines, so nothing enters the image — but **"not
in the image" is not "not transmitted"**.

Do not build from the working folder. Copy the **named** files into a temporary
folder, **print the context**, then build from there. A context you can see beats
a context you hope for. Make the exit check a gate: nothing goes to the registry
if it fails, that is the last moment where the data has not yet become an image
layer.

## Step 5 — A check that EXECUTES

"It needs an authenticated browser, so it cannot be verified" is almost always
false, and it costs one unverified deployment. Easy Auth and the database are not
needed to exercise the client logic: they are two HTTP responses.

Serve the page from disk and **stub the routes** — identity and shared state —
then play every role level. An in-memory fake state server honouring the same
contract as the real one, version number included, fits in thirty lines.

**The check that matters most: two concurrent writes.** That is the only serious
flaw of a naive shared state, and the only one that does not show when it happens
— the last save silently overwrites the work of the other. Check that the second
one fails, that the screen names the author, and that nothing is overwritten.

Also check what you would not have thought to check:

- **the write frequency.** A save function called on every keystroke makes one
  network call per character, so one conflict per character. Count the writes for
  one input.
- **the lowest role level.** It must see the figures and be refused the write
  with a message naming what to ask for.
- **the artifact on its own**, with no seeding: the gap must be announced, not
  silent.

No static check replaces that. Seen for real: `node --check` green, exit check
green, and the page **dead at startup** — a deletion had removed a definition and
left its call behind. Only the check that opens the page saw it.

## Step 6 — The PR changes one thing only

One image tag. The manifest keeps its name, its roles, its database, its
`cost_center`. **Any resource added or destroyed in the plan is a stop signal.**

Do not rename the application because the product changed name: renaming is a new
onboarding — application, groups, redirect URIs, database — and the state already
written does not follow. A key name is not a product name; the manifest
description, on the other hand, does get updated.

Write in the comment of the key **what the tag brings**, not just its number.
Whoever reads that file in six months is trying to find out which one to roll
back to.

## Discover the values, do not assume them

Hard-code neither a registry, nor a resource group, nor a server. Read them at
run time:

```bash
az acr list --query "[].name" -o tsv
az containerapp list --query "[].{nom:name, rg:resourceGroup, fqdn:properties.configuration.ingress.fqdn}" -o table
az containerapp auth show -n <app> -g <rg> --query "identityProviders.azureActiveDirectory.validation.jwtClaimChecks.allowedGroups"
```

The application manifest and the image tag table live in the landing zone repo,
under `environments/<env>/`. Those are the authority.

## Table of rationalisations

| What you tell yourself | What is true |
|---|---|
| "It is the same app with extra modules" | No: it is another lineage. Count the four axes before believing it. |
| "I change the `COPY` line and rebuild" | That is how the data taken out at the previous deployment gets republished. |
| "I added a `.dockerignore`" | It only protects `docker build`. `az acr build` ignores it. |
| "The static checks are green" | They do not prove the page opens. Run a check that executes. |
| "Authenticated behaviour needs a browser" | Two stubbed routes are enough. Name what really cannot be verified. |
| "A single address, it is the requester himself" | Then it is written as a dated and **counted** exception, not as an oversight. |
| "I will enter the data later" | Describe the gesture in a file, otherwise the data comes back into the artifact. |
| "I will write a small seeding script" | The input screen already exists. New code is the debt. |

## Stop signals

- You are about to run `az acr build .` from the working folder.
- The exit check passes on the first try, before any change.
- The Terraform plan announces something other than a tag change.
- The word "unverifiable" is about to be written.
- The artifact was modified **after** the image was built.
- You are about to rename the application to follow the name of the product.

## What stays with the business, and is said explicitly

Three things cannot be done from an agent machine, and must be handed back as
such, with the exact gesture: seeding the data through the input screens, opening
it from an account in each group, and merging the PR when `merge = apply`. Naming
them one by one beats a "to be checked".
