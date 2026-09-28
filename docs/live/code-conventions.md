---
regime: live
audience: [agent, dev]
reviewed: 2026-09-28
---

# Language in a repo

The team is growing and Snetor is a multinational. A repo must be readable by someone who does not
speak French. Decision: `docs/dated/decisions/2026-09-28-english-in-every-repo.md`.

## The rule

**Everything written in a repo is in English**: identifiers, file and folder names, skill names,
comments, commit messages, PR titles and bodies, `HANDOFF.md`, `docs/`, `tasks/`.

A comment that explains *why* a line exists is written in English, like the rest:

```js
// Debounced by 400 ms: one keystroke = one database write.
function loadData() { ... }
```

## What it does not cover

- **Existing French text.** It is not translated. It changes language when someone rewrites it for
  another reason, not through a dedicated pass.
- **Shared contracts.** A database column, a persisted state key or an HTTP route in production is
  not renamed in passing. Renaming it breaks a consumer that never reads this document.
- **The conversation.** Agents answer the user in the user's language.

## Enforcement

`hooks/guard.py` refuses a French commit message or PR title. French inside backticks is ignored,
so a verbatim quote stays possible. Nothing checks docs or comments automatically.
