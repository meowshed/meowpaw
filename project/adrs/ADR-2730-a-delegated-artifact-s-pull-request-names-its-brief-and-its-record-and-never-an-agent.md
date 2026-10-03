---
id: ADR-2730
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-1764]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2730. A delegated artifact's pull request names its brief and its record, and never an agent

## Decision

This amends ADR-2560 in one sentence. ADR-2560 says each delegated artifact
names the agent and the brief that produced it in its pull request
(REQ-1764). That sentence contradicts CLAUDE.md's `no_ai_attribution` and
REQ-1294, which forbid naming the agent, a model or a vendor in pull request
text. The owner wrote both, so they win.

A delegated artifact's pull request names the record that produced it, the
task's identifier, and the brief, as the command that prints it,
`paw brief <task>`. It names no agent, no model and no vendor. REQ-1764 is met
through the brief: `paw brief` prints the name of the shipped agent definition
the brief is written for, by its `<unit>:<agent>` name, beside the
constraints, so the harness can say which agent produced which artifact by
reading the task the pull request names and printing its brief again. The
pull request carries the pointer, and the brief carries the agent.

The rest of ADR-2560 stands, and its file stays as it was approved. No
requirement is withdrawn.

Once this is accepted, ADR-2560 can be built without breaking the
attribution ban. What still doesn't work: a brief printed later reads the
record as it is then, so a task edited after the pull request merged prints
a brief that differs from the one the agent got. An approved task is frozen,
which keeps the two the same for every task the method dispatches.

## Why

REQ-1294 elaborates RES-0014 and RES-0002, which found that attribution to a
tool in a commit or a pull request names a party nobody can ask about the
work, and CLAUDE.md states the ban for every pull request in this
repository. REQ-1764 elaborates RES-0016, which asks that the harness can say
who made what under which brief, and says nothing about where the answer is
written. A shipped agent definition's name is the harness's own identifier
for a role, and it lives in the brief, which the pull request points to and
doesn't quote.

## Alternatives

| Option                                 | Better at                                  | Why it lost                                                                      |
| -------------------------------------- | ------------------------------------------ | -------------------------------------------------------------------------------- |
| The pull request names the brief only  | Meets both requirements, and the ban holds | Chosen                                                                           |
| Do nothing                             | ADR-2560 as written                        | It can't be built without breaking REQ-1294 and CLAUDE.md                        |
| Name the agent in a trailer of its own | The commit alone answers who made it       | A trailer naming an agent is the attribution REQ-1294 forbids                    |
| Withdraw REQ-1764                      | No pointer to keep                         | The owner kept REQ-1764 in force, and the brief meets it without the agent named |

## What it costs

Finding which agent produced a change takes two reads, the pull request and
then the brief, where ADR-2560 offered one. `paw brief` has to print the
agent definition's name.

## What would reverse it

- The owner withdraws `no_ai_attribution` and REQ-1294, which would let the
  pull request name the agent as ADR-2560 wrote.

## Consequences

SPC-1090 states what a delegated artifact's pull request names, and that
`paw brief` prints the agent definition. The pull request template the
implement step uses names the task and the brief command. `meow-scm
check-message` and `meow-prose-gate` keep holding the ban as they do.

## How I will know it was realised

1. `paw brief` on a fixture task prints the agent definition's name it is
   written for (REQ-1764).
2. The implement step's file tells a delegated pull request to name the task
   and `paw brief <task>`, and names no agent, model or vendor (REQ-1764,
   REQ-1294).

## What this does not settle

- Which steps delegate by default, which ADR-2560 leaves open.
