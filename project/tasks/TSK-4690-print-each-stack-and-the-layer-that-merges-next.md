---
id: TSK-4690
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2430
closes: [REQ-1816, REQ-1830]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Print each stack and the layer that merges next in `paw status`

`paw status` prints each blocking chain among an epic's open tasks as a
stack, the layer that merges next, why each layer above waits, and each task
blocked by a dropped layer, as SPC-1090 states under "The state". One task,
one branch, one pull request, one review: the tests first, then the change,
its documentation and its marks.

## Acceptance criteria

1. Given a fixture epic whose open tasks TSK-a, TSK-b and TSK-c each block the
   next, when `paw status` runs, then it prints `stack: TSK-a <- TSK-b <-
TSK-c`, `next to merge: TSK-a`, and `TSK-b waits on TSK-a, not merged` and
   `TSK-c waits on TSK-b, not merged` (REQ-1816). Closed by: a crate test
   naming REQ-1816, seen failing first.
2. Given the same epic with TSK-a dropped, when `paw status` runs, then it
   prints `TSK-b blocked by TSK-a` and `TSK-c blocked by TSK-a` (REQ-1830).
   Closed by: a crate test naming REQ-1830.
3. Given a fixture epic whose tasks block none of each other, when
   `paw status` runs, then it prints no `stack:` line. Closed by: a crate test.

## What to do

Compute the stacks in the `record` feature of `crates/meow/` from the blocking
dependencies `ready implement` already reads, so the two never disagree. Pin
the new lines in the subcommand's test. Document them on
`plugins/meow-flow/README.md` where it shows `status`.

## Depends on

- TSK-4330 (not blocking): both pin `paw status`'s output lines, and whichever lands second updates the other's pin.

## Evidence

Not yet.

## Left alone

A layer closed or ejected on the code host, which `paw status` can't see
because it reads the record alone; TSK-4670 has the implement step report it.
