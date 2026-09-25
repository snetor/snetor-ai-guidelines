# Workflow — general working method

These rules apply across projects. `deploy-claude.ps1` copies this file to
`~/.claude/workflow.md`; do not edit that generated copy.

## Plan in proportion to the risk

- For a bounded task, state the intended result and how you will verify it in a
  few lines.
- Use plan mode and a written spec for architectural decisions, high-risk or
  ambiguous work, or several dependent workstreams. Three mechanical steps alone
  do not justify a spec.
- If a key assumption fails, stop execution and revise the plan.
- Keep one source of progress: an issue for multi-session work; `tasks/todo.md`
  only for local work without an issue. Do not duplicate status.

## Parallelize with clear boundaries

- Start with one session. By default, keep at most two or three active workstream
  owners with independent files and deliverables; exceed that only when the
  expected benefit is explicit. Bring in a reviewer when needed. Do not create
  nested teams by default.
- Use subagents for bounded research or checks: a precise question, reading
  scope, expected evidence, and stopping condition. Close idle sessions.
- For each workstream, record in the chosen tracker: owner, owned files or
  resources, dependencies, definition of done, write scope, and acceptance
  evidence. In Git projects, also record the branch or worktree and, where the
  project uses PRs, the PR. Have only one concurrent editor per shared file.
- Keep sensitive details out of public trackers. Use a private issue or a
  redacted public contract, with evidence stored in an authorized location.
- Use direct messages for urgent decisions and require acknowledgment. Keep
  durable decisions in the chosen tracker, not only in comments.
- Name one write coordinator for shared or production resources. Measure the
  current state, announce the exact target, then wait for the coordinator's go.
- Report agent results in four parts: outcome, evidence, limitations, next
  action. An unverified claim remains a hypothesis.

## Manage context cost

- Select model capability and reasoning effort by task: strongest available for
  architecture, security, or difficult diagnosis; balanced for routine
  implementation and review; fast for bounded searches. Avoid pinning model
  versions in shared guidance.
- Find relevant files before loading long logs or directories. Send other
  sessions a summary and a pointer to evidence, not a full transcript.
- After a completed milestone, start with a short context if the old history no
  longer helps. Compare quality and tokens across comparable workstreams;
  cache-read tokens are neither unique text nor a bill.

## Learn without bloating the preamble

- After a correction, record a reusable rule and the incident behind it in the
  project's lessons register (`tasks/lessons.md` if present), not a session
  diary. Search for relevant lessons on demand.
- Where the project uses this standard, keep active lessons below 300 lines and
  archive older ones in `tasks/lessons/YYYY-MM.md`.
- Keep personal memory outside Git for facts that cannot be derived from code
  or history. Back it up before using a tool that rewrites it.

## Verify before concluding

- Prove the requested behavior with relevant tests and, when appropriate, a
  real user's workflow. A build or code review alone does not prove usability.
- Separate pre-existing failures from regressions and state the limits of the
  evidence. Do not mark work done while an acceptance condition remains untested.
- Fix a bug at its cause without silently expanding scope. Touch adjacent files
  only when needed; prefer the simplest solution that holds.
