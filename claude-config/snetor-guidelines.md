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

---

# Documentation

Standard complet : `docs/live/documentation-standard.md` du repo
`snetor-ai-guidelines`. Les invariants, applicables a tous les repos Snetor :

## Structure

```
HANDOFF.md              routeur d etat — 150 lignes maximum
docs/live/              doit etre vrai maintenant, reecrit en place
docs/dated/             vrai a sa date, jamais reecrit, remplace par un successeur
docs/README.md          genere — ne jamais editer a la main
docs/superpowers/specs/ zone de travail, videe a la cloture
docs/superpowers/plans/ zone de travail, gitignoree
tasks/todo.md           items ouverts seulement
tasks/lessons.md        journal append-only
```

## Frontmatter obligatoire dans docs/live/ et docs/dated/

`regime` (`live` ou `dated`), `audience` (liste parmi `agent`, `dev`,
`newcomer`, `ops`, `business`). En `live` : `reviewed` en date ISO, `ttl`
optionnel au format `<n>d` (defaut `90d`). En `dated` : `date` en date ISO,
`status` parmi `draft`, `proposed`, `decided`, `applied`, `superseded`.

## Cloture de branche — cinq etapes

Utiliser le skill `snetor-docs-close`. A defaut, dans cet ordre : supprimer le
plan ; arbitrer chaque spec (reecrite en decision datee, fondue dans un fichier
`live`, ou supprimee) ; ajouter les lecons a `tasks/lessons.md` ; supprimer de
`tasks/todo.md` les items livres, sans les cocher ; reecrire `HANDOFF.md` sous
150 lignes. Puis regenerer l index.

## Regles non negociables

Ne jamais editer `docs/README.md` a la main : le regenerer par
`python scripts/check_docs.py --repo-root . --fix`.

Ne jamais commiter un plan d implementation.

Une spec est **reecrite** vers sa destination, jamais copiee ni deplacee telle
quelle : une decision utile tient en quarante a cent lignes.

Un item de `tasks/todo.md` livre est supprime, pas coche.

Ne jamais creer un fichier par session (`handoff-2026-08-10.md`,
`SUMMARY.md`, `PHASE2_COMPLETE.md`). Le routeur est unique et se reecrit.
