---
regime: dated
audience: [agent, dev, newcomer]
date: 2026-09-28
status: decided
---

# Everything written in a repo is in English

## Decision

From 2026-09-28, everything written in a Snetor repo is in English: code, comments, commit
messages, pull requests, and documentation (`HANDOFF.md`, `docs/`, `tasks/`).

Existing French text is **not** translated. It changes language only when someone rewrites it for
another reason. Agents keep talking to the user in the user's language: this rule covers what is
written in the repo, not the conversation.

## What it replaces

PR #40 (2026-09-22) split the work in two: identifiers in English, documentation, comments and
commit messages in French. Six days later, that split cost more than it saved. A reader who does not
speak French could read the names but not the reasons behind them, and two languages in one
file made every contribution a question of which one to use.

`docs/live/code-conventions.md` is rewritten to carry the new rule.

## What stays as it is

- Keys of a shared contract (a database column, a persisted state key, an HTTP route in
  production) are not renamed in passing, whatever their language.
- Business terms that have no English equivalent at Snetor stay as they are, as proper nouns.
- Quoting French verbatim (an error string, a user's words) is fine.

## How it is enforced

`hooks/guard.py` refuses a commit message or a PR title that looks French: two signals among
French function words, elisions (`l'`, `n'`...) and one accented letter. Text inside backticks and
the `Co-Authored-By:` line are ignored. It is a heuristic, not a language detector. If it refuses an
English message, fix the heuristic and add the case to `tests/test_guard.py`. Do not reword the
message just to get past it.

Documentation and comments are not checked by a program. For those, the rule lives in
`claude-config/snetor-guidelines.md`, which every session loads.
