---
name: snetor-lessons-to-guardrails
description: >
  Turns the lessons of tasks/lessons.md in a Snetor repo into executable guardrails - sorts each
  lesson into gesture (PreToolUse hook), invariant (test), environment fact (a sentence in
  CLAUDE.md) or judgement (stays narrative), writes the missing mechanism, and marks the ones
  already backed by tooling. USE THIS SKILL as soon as a mistake repeats - "we have been burned by
  this before", "on s est deja fait avoir", "that is the second time", "c est la deuxieme fois",
  "this is a repeat", "recidive", "I told you already", "je te l avais dit" - as soon as a
  correction from the user looks like a lesson already written down, when tasks/lessons.md nears
  its 300-line cap or check_docs.py blocks on it, and during a pass to clear the tooling debt.
  Do not use it to write a lesson after a plain correction - a lesson goes into lessons.md without
  this routine; this one is for when the lesson was NOT enough.
---

# Turning lessons into tooling — a checkable rule does not stay in prose

## Why this routine exists

`tasks/lessons.md` is append-only by doctrine, which is right — but a file nobody opens any more is
no longer a guardrail. The proof is in the file itself: on `snetor-pim`, **four lessons were
annotated "exact repeat" or "third variant"**. They had been written, re-read, and repeated anyway.

The same observation produced the 300-line cap: the file had reached 42,000 tokens that nobody read.

**A lesson that repeats is a lesson asking for a mechanism, not for one more sentence.**

## The principle — four boxes, exactly one per lesson

| Box | Mechanism | Where |
|---|---|---|
| **Gesture** — a command, a path, an order of execution | `PreToolUse` hook | `snetor-ai-guidelines`, `hooks/guard.py` **+ its test** |
| **Invariant** — a property of the code or of the schema | test | the suite of the repo concerned |
| **Environment fact** — a quota, a delay, a code page | a sentence in `CLAUDE.md` | nothing to run |
| **Judgement** — a trade-off, a threshold, a business reading | none | stays narrative |

The first three get marked `tooled: <path>` under the lesson, in `lessons.md`.

The fourth stays as it is: **trying to automate a judgement produces a guardrail that fires
wrongly, and a guardrail that fires wrongly is disabled within the week.**

## Sequence

1. **Read `tasks/lessons.md` in full** — this is the only moment it is read in full; the rest of the
   time you `grep` it. Also read `tasks/lessons/AAAA-MM.md` if the pass is a complete one: repeats
   are counted on the archive, not on the active file.

2. **Sort every lesson** into one of the four boxes. A lesson already marked `tooled:` gets
   **verified** rather than re-sorted — does the path it cites still exist, does the test still run?
   A marker pointing at a vanished file is worse than no marker.

3. **Look for repeats.** Two lessons describing the same failure mode under two different wrappings
   count double: that is the most reliable signal that a mechanism is missing.

4. **Write the mechanism** for the gesture or invariant lessons that have none. **One mechanism at a
   time, with its test, in a dedicated commit.** A gesture guardrail goes into
   `snetor-ai-guidelines/hooks/guard.py` — it then covers all fourteen repos, not just one.

5. **Mark it** in `lessons.md` without rewriting the text of the lesson: add a `tooled: <path>` line
   underneath it.

## What not to do

- ⛔ **Do not delete a lesson because it is tooled.** That is what makes it possible to count the
  repeats, and therefore to know that a mechanism is missing. A lesson leaves the active file
  through the monthly archive, never through deletion.
- ⛔ **Do not write a broad guardrail "to cover several lessons at once".** A broad pattern catches
  legitimate cases, and that is the first thing people disable.
- ⛔ **Do not tool a judgement.** "A rate lies without its denominator" does not become a test:
  publishing the distribution can be mechanised, choosing the threshold cannot.
- ⛔ **Do not write a rule without its incident.** A rule whose cost nobody remembers gets deleted by
  the next reader who does not understand it.

## Verification barrier

The test suite of the repo concerned must pass, **and** — for every new mechanism — the proof that
it catches the real case: replay the command or the state that caused the incident, and show that
it is refused. A guardrail whose refusal you have not seen is not verified.

For a hook added to `guard.py`:

```bash
python -m pytest tests/ -q     # from snetor-ai-guidelines
```

## What to report at the end of the pass

1. **The newly tooled lessons**, with their mechanism and the proof that it catches the case.
2. **The repeats found** — the lessons describing the same flaw twice.
3. **What is left to judgement**, and why it cannot be automated.
