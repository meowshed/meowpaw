---
id: ADR-1210
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-0510,
    REQ-0516,
    REQ-0518,
    REQ-0519,
    REQ-0527,
    REQ-0582,
    REQ-0584,
    REQ-0586,
    REQ-0591,
    REQ-0690,
    REQ-0694,
    REQ-0696,
    REQ-0704,
    REQ-0706,
    REQ-0710,
    REQ-0712,
    REQ-0714,
    REQ-0716,
  ]
supersedes: []
---

# 1210. The record reports where it contradicts itself, and derives each requirement's state

## Decision

`meow record check` reports each place the record contradicts itself, and the
program derives each requirement's state from the tree instead of reading it
from a field:

- `check coverage` reports a task whose Evidence section is written while its
  epic still marks it not started, and a task that closes a withdrawn
  requirement inside an epic not yet verified. It already reports a task
  marked done with no evidence.
- `check relations` reads the body as well as the front matter, and reports an
  identifier of a known kind that resolves to no artifact.
- `show` prints a requirement's derived state: the tasks that close it, whether
  each is marked done, and the issue its epic was verified under, or that
  nothing checks it.
- `status` counts the requirements in force by derived state: verified, closed
  by a task, and checked by nothing. It reports an epic as verified only when
  `check` reports nothing on the epic, its decision or its tasks, and names the
  count where it does.
- `status` says the record is local to this machine where its root is under no
  version control.

The status rules that already hold are recorded with their evidence: the
vocabulary of stored statuses, the amendment path `check frozen` holds, the
record's layout by kind, and new identifiers entering an approved set.

After this decision a person asking what state a requirement is in gets an
answer computed from the tree, and a record that says one thing while the tree
says another fails the check. What still doesn't work: a requirement's state
knows only the checks the record names, a task's evidence and an epic's
verification, and not a test naming the requirement, which no test in the
harness does yet.

## Why

RES-0019, RES-0028 and RES-0067 record traceability that rots once nobody
checks it in both directions, and an index claiming work that the tree doesn't
show. ADR-1150 made a closed task carry its evidence, and ADR-1170 held an
approval frozen; the gaps left are the reverse direction, work landed and
unmarked, and a reported state nobody computed. REQ-0584 asks that an observed
status be derived, which means a requirement's state is a query, never a
field.

The strongest objection: a body check on identifiers reports prose that names
an identifier on purpose, such as an example. It would, and an example in the
record uses a placeholder such as `REQ-NNNN`, which matches no identifier.

## Alternatives

| Option                                              | Better at                                 | Why it lost                                                        |
| --------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------ |
| Findings in `check`, derived state in `show`        | One program answers and one program fails | Chosen                                                             |
| An `implemented` field on each requirement          | Readable without the program              | A stored observed status is a second source of truth, REQ-0586     |
| A report on requirements with no check as a finding | Fails loudly                              | Two thirds of the requirements have no task yet, so the gate fails |
| Do nothing                                          | Costs nothing                             | A task left unmarked, and a verified epic that drifted, go unseen  |

## What it costs

Two new findings in `coverage`, a body scan in `relations`, a derived state in
`show` and `status`, and a task of recorded evidence.

## What would reverse it

- A test naming a requirement becomes the way this repository checks one, and
  the derived state reads tests too.

## Consequences

- `check` fails on a task with evidence left unmarked, and on an identifier in
  a body that resolves to nothing.
- `show` and `status` report each requirement's derived state.
- `status` withholds "verified" from an epic `check` reports on.

## How I will know it was realised

1. A fixture with a task whose evidence is written and whose epic leaves it
   unmarked fails `check coverage`, and one whose body names a missing
   identifier fails `check relations`.
2. A fixture shows `show` printing a requirement's closing task and its
   verification, and "checked by nothing" for one with none.
3. A fixture shows `status` withholding "verified" from an epic with a finding,
   and reporting a record under no version control as local.
4. Each requirement ADR-1210 addresses that already holds has its evidence
   recorded in the task that closes it.
5. Every requirement ADR-1210 addresses lands in exactly one closed task.

## What this does not settle

- Reading tests that name a requirement.
- The migration path for a change to the record's shape, REQ-3008 to REQ-3020.
