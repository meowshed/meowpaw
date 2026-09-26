---
id: ADR-1340
artifact: adr
status: draft
revised: 2026-09-26
addresses: []
postpones:
  [
    REQ-1300,
    REQ-2520,
    REQ-2542,
    REQ-2546,
    REQ-2548,
    REQ-2550,
    REQ-2552,
    REQ-2554,
  ]
supersedes: []
---

# 1340. Version control tools other than git are postponed

## Decision

The harness supports git alone for now, and postpones the 8 requirements
that exist only for a version control tool other than git: detecting one and
using its commands, reading only its stable output, inspecting through the
tool beneath it, reporting the hooks, capabilities and signatures it lacks,
citing the identifier that survives a rewrite, and owning the templates it
reads through.

Nothing is built. The requirements stay in force and read as postponed, and
every verification lists them with the condition below.

After this decision the harness is honest about supporting git alone. What
still doesn't work: a repository on Jujutsu or another tool gets git's
behaviour, which RES-0132 found can commit what `status` looked at.

## Why

The owner postponed version control tools other than git on 2026-09-26, so
that the remaining work goes to what every repository using the harness today
needs. RES-0132 found Jujutsu supportable as a front end over git's storage,
and found the cost: no read-only invocation, hooks that don't run, and
signatures it can drop, each needing its own handling. None of that serves a
git repository.

The strongest objection: a repository on Jujutsu gets wrong behaviour rather
than a refusal. It does, and REQ-1300's detection is the first thing to take
up when the condition below holds.

## Alternatives

| Option                                     | Better at                               | Why it lost                                                          |
| ------------------------------------------ | --------------------------------------- | -------------------------------------------------------------------- |
| Postpone, and revisit at each verification | Work goes to what git repositories need | Chosen                                                               |
| Support Jujutsu now                        | A second tool served                    | The owner postponed it, and no repository using the harness needs it |
| Withdraw the requirements                  | A shorter list                          | They remain true, and withdrawing loses the research behind them     |

## What it costs

Nothing now. The 8 requirements read as postponed until a task closes
them.

## What would reverse it

- A repository using the harness adopts a version control tool other than
  git, or the owner asks for one.

## Consequences

- `status` counts 8 requirements as postponed, and shows this decision as
  postponing them.

## How I will know it was realised

1. `meow-method status` counts the 8 requirements as postponed, and
   `show` names this decision for each.
2. Each verification lists the postponement with its condition.

## What this does not settle

- How the harness supports a second version control tool, which a decision
  of its own takes when the condition holds.
