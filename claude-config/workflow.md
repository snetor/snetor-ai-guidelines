# Workflow — méthode de travail générique

Règles de méthode de travail, valables sur n'importe quel projet, distribuées
par `deploy-claude.ps1` et **écrasées à chaque déploiement**.

# Workflow Orchestration

## 1. Plan Mode Default

- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)

- If something goes sideways, STOP and re-plan immediately – don't keep pushing

- Use plan mode for verification steps, not just building

- Write detailed specs upfront to reduce ambiguity

---

## 2. Subagent Strategy

- Use subagents liberally to keep main context window clean

- Offload research, exploration, and parallel analysis to subagents

- For complex problems, throw more compute at it via subagents

- One task per subagent for focused execution

---

## 3. Self-Improvement Loop

- After ANY correction from the user: update `tasks/lessons.md` with the pattern

- Write rules for yourself that prevent the same mistake

- Ruthlessly iterate on these lessons until mistake rate drops

- Review lessons at session start for relevant project

---

## 4. Verification Before Done

- Never mark a task complete without proving it works

- Diff behavior between main and your changes when relevant

- Ask yourself: "Would a staff engineer approve this?"

- Run tests, check logs, demonstrate correctness

---

## 5. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"

- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"

- Skip this for simple, obvious fixes – don't over-engineer

- Challenge your own work before presenting it

---

## 6. Think Before Coding

- State your assumptions explicitly before implementing. If uncertain, ask.

- If multiple interpretations exist, present them – don't pick one silently.

- If a simpler approach exists, say so. Push back when warranted.

- If something is unclear, stop and name what's confusing before continuing.

---

# Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding

- Point at logs, errors, failing tests – then resolve them

- Zero context switching required from the user

- Go fix failing CI tests without being told how

---

# Task Management

- **Plan First:** Write plan to `tasks/todo.md` with checkable items

- **Verify Plan:** Check in before starting implementation

- **Track Progress:** Mark items complete as you go

- **Explain Changes:** High-level summary at each step

- **Document Results:** Add review section to `tasks/todo.md`

- **Capture Lessons:** Update `tasks/lessons.md` after corrections

- **Success Criteria First:** Transform each task into a verifiable goal — "fix the bug" → "write a test that reproduces it, then make it pass." For multi-step tasks, state a brief plan with a verify check per step.

---

# Core Principles

- **Simplicity First:** No features beyond what was asked. No abstractions for single-use code. No unasked configurability. If 50 lines could replace 200, rewrite.

- **Surgical Changes:** Touch only what's necessary for the task. Don't improve adjacent code, comments, or formatting. Match existing style. If you notice unrelated dead code, mention it — clean it in a dedicated separate commit, never mixed silently into the current change.

- **No Laziness:** Find root causes. No temporary fixes. Senior developer standards.
