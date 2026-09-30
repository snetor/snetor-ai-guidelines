# snetor-dev

Snetor skills for the tech team, working in Snetor repos with Claude Code. Business users do not
need them: they belong on developer workstations only. The skills for everyone live in
[`snetor-skills`](../snetor-skills/README.md).

The three maintenance routines are the ones nobody thinks to invoke. They trigger on
**situations**, not requests — that is the point: a routine you have to remember is a routine you
run once.

| Skill | Does | Triggers on |
|---|---|---|
| **`snetor-docs-close`** | Documentation standard on branch close: plan purged, specs arbitrated, lessons recorded, todo cleaned, router rewritten under 150 lines, index regenerated | before opening/merging a PR, "on clôture", "c'est fini", "close the branch" |
| **`snetor-lessons-to-guardrails`** | Turns repeated lessons into executable guardrails (hook, test) instead of more prose | "we have been burned by this before", "that is the second time", "on s'est déjà fait avoir", `lessons.md` near its 300-line cap |
| **`snetor-test-pruning`** | Dead modules, sleeping tests, constant assertions, duplicate coverage — with the before/after count | "the CI takes forever", "we have too many tests", "la CI prend des plombes", after a large refactor |
| **`snetor-deploy-artefact`** | A PR shipping a power-user artifact onto the internal container platform | "déployer cet artefact", "nouvelle version du HTML", paved road |

## Installation

Once per developer workstation:

```
claude plugin install snetor-dev@snetor-ai-guidelines
```

`scripts/deploy-claude.ps1` never enables it on its own, so a business user never gets it. Once it
is installed, the deployer refreshes it and reports its version, like `snetor-skills`.

## Structure

```
snetor-dev/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── snetor-docs-close/             ← branch-closing assistant
│   ├── snetor-lessons-to-guardrails/  ← lessons → executable guardrails
│   ├── snetor-test-pruning/           ← dead-test removal
│   └── snetor-deploy-artefact/        ← ship an artifact onto the paved road
└── README.md
```
