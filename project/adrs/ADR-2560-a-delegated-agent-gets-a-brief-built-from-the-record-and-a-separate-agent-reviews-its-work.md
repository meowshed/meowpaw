---
id: ADR-2560
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-0810,
    REQ-0812,
    REQ-0814,
    REQ-0818,
    REQ-0824,
    REQ-0826,
    REQ-0828,
    REQ-1764,
    REQ-2980,
    REQ-2986,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2560. A delegated agent gets a brief built from the record, and a separate agent reviews its work

## Decision

A step delegates a task to an agent with a brief built from the task's
records, never from the conversation (REQ-0810). The brief stands alone: what
to build, the constraints that bind it, the interfaces it touches and what to
report back, each written out (REQ-0812). The constraints are copied word for
word from the records they come from (REQ-0814). `paw brief <task>` prints
that brief from the task, its epic or decision, and the requirements it
names, so the step doesn't assemble it by hand.

A step delegates for one of two reasons: to keep a context clean, or to run
independent tracks at once. It never delegates because a task is large
(REQ-0826, REQ-0828). An agent sent to implement in parallel declares
`isolation: worktree` in its dispatch and doesn't arrange a directory itself
(REQ-2980).

A separate agent reviews delegated work, dispatched fresh and never forked
from the conversation that produced it (REQ-0818). Where the implementer and
the reviewer disagree, a third agent resolves it in a fresh context, given
both positions and the brief (REQ-0824). Each delegated artifact names the
agent and the brief that produced it in its pull request, so the harness can
say who made what (REQ-1764). A repository can replace any agent the harness
ships by defining one of the same name in its own `.claude/agents/`, which the
platform loads in place of the plugin's (REQ-2986).

Once this is accepted, a delegated task's agent sees the same constraints the
record states, and its review isn't by its author. What still doesn't work:
`paw brief` reads the record, so a constraint that lives only in the
conversation doesn't reach the agent, which is the point of REQ-0810.

## Why

RES-0016 found that an agent briefed from the conversation inherits its
mistakes and that a summarised constraint loses the clause that mattered.
RES-0003 found that harnesses which delegate because a task is big split the
context without isolating anything. RES-0263 found that the platform lets a
project's agent of the same name replace a plugin's, and that a dispatch can
ask for its own worktree. ADR-1710 already gives a delegated agent four
outcomes to report.

## Alternatives

| Option                        | Better at                 | Why it lost                                                       |
| ----------------------------- | ------------------------- | ----------------------------------------------------------------- |
| Do nothing                    | No new subcommand         | Each step writes its brief by hand and copies constraints loosely |
| Fork the conversation instead | The agent sees everything | It carries the conversation's mistakes into the review            |
| Review in the implementer     | One dispatch              | A review by the author of the change is not a review              |

## What it costs

Each delegated task costs at least two dispatches, the work and its review,
and a third where they disagree.

## What would reverse it

- The platform gives a fork a way to drop the conversation and keep only
  named files, which would make a forked brief as clean as a built one.

## Consequences

The native tool gains `paw brief`. The implement step's file states when to
delegate and how. The pull request template names the agent and its brief.

## How I will know it was realised

1. `paw brief` on a fixture task prints its constraints word for word from
   its requirements (REQ-0812, REQ-0814).
2. The implement step's file names the two reasons to delegate and forbids
   the third (REQ-0826, REQ-0828).
3. A fixture review dispatch is a fresh agent and not a fork (REQ-0818).
4. A project agent named like a shipped one replaces it in a fixture
   repository (REQ-2986).

## What this does not settle

- Which steps delegate by default.
