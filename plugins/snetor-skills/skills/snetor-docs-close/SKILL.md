---
name: snetor-docs-close
description: >
  Cleanly closes a branch in a Snetor repo by applying the documentation standard - deletes
  the implementation plan, routes every spec to its lasting destination, records the lessons,
  removes delivered items from the todo, rewrites the HANDOFF.md router under 150 lines, then
  regenerates the index and runs the checker.
  USE THIS SKILL before opening or merging a pull request in a Snetor repo, and as soon as the
  user says a piece of work is finished, delivered, or ready to merge
  ("on cloture", "c est fini", "prepare la PR", "nettoie la doc", "close the branch",
  "we are closing this out", "it is done", "prep the PR", "clean up the docs",
  "wrap up this branch").
  Do not use to write a spec or a plan - that is the job of the brainstorming and
  writing-plans skills.
---

# Branch closure — Snetor documentation standard

Full doctrine: `docs/live/documentation-standard.md` in the `snetor-ai-guidelines`
repo.

Run the five steps in order. Do not skip one: each removes volume the next will
not have to sort.

## Entry condition — to establish before deleting anything

This skill destroys files that git cannot bring back. It only starts if both of
the following are **established**, not assumed:

1. **The plan is fully executed.** Every one of its tasks is delivered, none is
   pending or in progress. Re-read the plan and check it against what is really
   in the tree — do not rely on a memory of the session.
2. **The working tree is committed.** `git status --porcelain` returns nothing.

If either is false, **stop and say so** to the user: name what is left to do or
to commit, and delete nothing, edit nothing.

This guardrail is not theoretical. The skill triggers on "prep the PR" and
"clean up the docs", which a user commonly says **while** a plan is still
running. Deleting the plan at task 3 of 8 takes tasks 4 to 8 with it, and since
`docs/superpowers/plans/` is gitignored, there is no git blob to bring them
back.

## Step 1 — delete the plan

The entry condition above must be verified first. Then delete every file in
`docs/superpowers/plans/`, with no archiving. The folder is gitignored, so there
is nothing to unstage if the repo already complies; otherwise use `git rm`.

A plan runs to thousands of lines, serves once, and the pull request diff
documents what was delivered better than it does.

## Step 2 — rule on every spec

For each file in `docs/superpowers/specs/`, ask the user which of the three
outcomes applies, proposing the one that looks right:

1. **It settled something lasting.** Rewrite it as a short decision in
   `docs/dated/decisions/YYYY-MM-DD-<slug>.md`, frontmatter `regime: dated`,
   `status` one of `decided`, `applied` or `proposed`. Then delete the spec.
2. **It describes a state of the system.** Fold its content into the relevant
   `docs/live/` file, update that file `reviewed` to today, then delete the
   spec.
3. **It was tactical.** Delete it.

A spec is **neither moved nor copied: rewritten**. A useful decision fits in
forty to a hundred lines; copying a three-hundred-line spec reproduces the very
volume being removed.

## Step 3 — record the lessons

Add to `tasks/lessons.md` what this session learned and would come back to bite
later. Follow the format already in place in the file. Record only what lasts: a
symptom, its cause, the rule that prevents a repeat. No session narrative.

**Append only.** `tasks/` is gitignored in some repos: an entry rewritten or
reordered there is lost for good. Never reword, merge or delete an existing
entry.

## Step 4 — clean up the todo

Remove the delivered items from `tasks/todo.md`. **Remove** them, do not tick
them: their trace lives in the pull request number. A `tasks/todo.md` that piles
up ticked boxes turns back into a journal within weeks.

Since `tasks/` may be gitignored, this edit is just as unrecoverable: submit to
the user the list of items about to be removed and wait for approval. An item
whose delivery is not established stays.

## Step 5 — rewrite the router

Rewrite `HANDOFF.md` under 150 lines. Two questions, nothing else: where things
stand, where to look. If it does not fit, content has to move out to
`docs/live/` or `docs/dated/` — not that the ceiling is too low.

## Final check

Run, from the repo root:

```
python scripts/check_docs.py --repo-root . --fix
```

If the repo does not ship the script, use the one from the
`snetor-ai-guidelines` repo.

Show the report to the user. Never announce the closure as done without showing
the `OK — 0 erreur` output. Freshness warnings do not block, but flag them: they
make up the documentation debt list.
