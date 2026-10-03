---
id: TSK-4945
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2530
closes: [REQ-0810, REQ-0812, REQ-0814, REQ-1764]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Print a task's brief with `paw brief`

`paw brief <task>` prints the brief a delegated agent gets, built from the
task, its epic or the decision it realises, and the requirements it closes,
and never from a conversation, as SPC-1090 states under "Delegated work". One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture task closing two requirements in an approved epic, when
   `paw brief <task>` runs, then it prints what to build, the constraints, the
   interfaces it touches and what to report back, each under its own heading,
   and each constraint is the requirement's statement and the task's own
   constraint lines copied byte for byte (REQ-0810, REQ-0812, REQ-0814).
   Closed by: a crate test naming the three requirements, seen failing first.
2. Given a fixture task naming `realises: ADR-NNNN` in place of `epic:`, when
   `paw brief` runs, then it reads the decision in the epic's place. Closed
   by: a crate test.
3. Given a fixture task and the agent definition `meow-flow:router`, when
   `paw brief <task> --agent meow-flow:router` runs, then its first line
   names `meow-flow:router`, and without `--agent` it names the agent the
   implement step dispatches (REQ-1764). Closed by: a crate test naming
   REQ-1764.
4. Given a task identifier that doesn't resolve, when `paw brief` runs, then
   it exits 1 naming the identifier and prints no brief. Closed by: a crate
   test.

## What to do

Add `brief` to the `record` feature of `crates/meow/`, reading the record the
way `paw show` does. It prints and writes nothing, and its output follows
SPC-1080's rule that each kind of line opens with a word its help states.
Choose the `--agent` flag's default and state it in the help and on
`plugins/meow-flow/README.md`.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The implement step's file, which TSK-4950 changes to use the command, and a
constraint that lives only in a conversation, which by REQ-0810 never reaches
the brief.
