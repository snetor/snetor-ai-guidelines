---
name: snetor-test-pruning
description: >
  Finds and deletes the tests that no longer serve a purpose in a Snetor repo - test of a dead
  module, sleeping test (unconditional skip/xfail), test of a constant, duplicate coverage - with
  the proof required for each category and the before/after count. USE THIS SKILL when the test
  suite only ever grows, when the CI slows down or costs too much, when a user says "we have too
  many tests", "on a trop de tests", "the CI takes forever", "la CI prend des plombes", "what are
  these tests even for", "ces tests servent a quoi", when dead code has just been removed and its
  tests remain, and after a large refactor. Useful too when a suite is green but suspicious - a
  skipped test reads like coverage. Do not use it to write tests nor to fix a red suite - a red
  test is saying something, it gets read, not deleted.
---

# Pruning the test suite

## Why this routine exists

A suite that only ever grows ends up costing CI time and reading time without guaranteeing anything
more. And, worse, **a dead test reads like coverage**.

The case measured on `snetor-pim` points the other way and says the same thing: **95 tests on the
`app/` side were skipped on every PR while the CI stayed green**. A test that does not run and a
test that exercises dead code pose the same problem — they count in the figures and verify nothing.

## The four categories, and the proof required for each

| Category | Proof required | Action |
|---|---|---|
| **Test of a dead module** | no `import` from a real entry point — a `run_*.py`, a deployment manifest, a runbook, an app route, or another live module | delete the test **and** the module, in the same commit |
| **Sleeping test** | `@pytest.mark.skip` / `xfail` **with no condition**, `allow_module_level=True`, `describe.skip(`, `it.skip(`, `.todo(` | fix it, or delete it — never leave it asleep |
| **Test of a constant** | the assertion restates a literal value from the code, with no behaviour | delete |
| **Duplicate coverage** | two files cover the same function with the same cases | keep the one closest to the business behaviour |

⛔ **A conditional `skipif` is NOT a sleeping test.** Markers expressing a **real prerequisite** — a
local database, an `importorskip`, a CI environment variable — are genuinely executed by the
workflows that provide them. Deleting them would reopen exactly the hole we are trying to close.

## Sequence

1. **Measure first.** Run the suite and note the number of **passed** and **skipped** tests,
   separately. Without that starting point, the pass cannot be proven.

   ```bash
   python -m pytest -q          # Python
   npx vitest run               # front
   ```

2. **Look for modules with no live caller.** For each package, walk the import chain up to a real
   entry point. A module that only its own tests mention is dead.

   ⚠️ **Check package by package, never in bulk.** Real case: inside the same package, one module
   had been dead for two months while its neighbour was writing to production. Deleting the whole
   package would have broken production.

3. **List the sleeping tests.** If the repo has a hygiene suite that fails when one exists, run it;
   otherwise `grep` the markers from the table above.

4. **Look for duplicates**: two files importing the same function and making the same assertions.

5. **Delete, one subject per commit.** The test and the module it covers go together. Never mix a
   deletion with a behaviour change — that is the only way to read back a `git revert` later.

6. **Measure afterwards**, and state the difference.

## Verification barrier

The number of **passed** tests must drop by **exactly** the number of tests deleted, and the number
of **skipped** tests must not move.

If it moves, a deletion broke an import and switched something else off along the way — that is the
only signal separating a pruning pass from a silent regression.

## What to report at the end of the pass

1. **What was deleted**, with the proof it was dead — the module, and who no longer calls it.
2. **What was kept despite appearances**, and why. That is the part people read back.
3. **The before / after count**, passed and skipped separately.

⚠️ **Never delete a test because it fails.** A red test is saying something.
