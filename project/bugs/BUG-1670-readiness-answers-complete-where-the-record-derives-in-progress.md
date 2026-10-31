---
id: BUG-1670
artifact: bug
status: done
severity: minor
violates: REQ-0585
enters: implement
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# `paw ready implement` answers complete where `paw status` derives in-progress

The two subcommands answer one question, whether a task's work is complete,
from two sources: `ready` reads the task's Evidence opening line, `status`
derives from its epic's marks. Where the two disagree, the chain's driver
stops on one and the session's opener sees the other.

## Reproduction

Seen on the trunk at `6536d751`, and at `4f32e7ce` while TSK-4935 stood.

1. With a task whose Evidence opens with its result and whose epic mark
   stays `[>]`, run `plugins/meow-flow/bin/paw ready implement <task>` and
   `plugins/meow-flow/bin/paw status`.
2. Read `ready`: `ready; <task> approved and complete`. Read the epic's line
   in `status`: `<epic>, N of M tasks done`, and its T-004 marked in
   progress.

## What the system does

`paw ready implement TSK-4935` printed `ready; TSK-4935 approved and
complete` while `paw status` derived EPC-2525 as `3 of 4 tasks done`, because
`ready` reads the task's Evidence first line as its completion and `status`
reads the epic's task marks. TSK-4935's Evidence opened with its result
while its epic mark stayed `[>]`, and the two tools each answered their own
source.

## What it should do, and why

REQ-0585 says a decision, epic or task MUST NOT store `status: done` unless
the record derives its work as complete, and a tool's answer is a claim of the
same kind: the completion one subcommand reports MUST be the completion the
record derives, or the chain drives on one answer while the session opens on
another.

## Triage

`implement`: the fix is the tool, deriving `ready`'s completion from the
same source `status` derives from, or the two sharing one derivation. Minor:
both answers were conservative in the case seen, `ready` allowing a step and
`status` holding a task open, so the chain never ran ahead of the record, but
the disagreement invites the inverse.

## Closed by

The reproduction, now passing: `paw ready implement` on a task whose epic
mark stays `[>]` answers that its work is not complete, in
`crates/meow/src/record.rs`, with a test.

## Tasks

- [ ] T-001 Derive `paw ready`'s completion from the same source `paw status`
      derives from, in `crates/meow/src/record.rs`, with a test on a task
      whose Evidence is written and whose epic mark stays `[>]`
