---
id: EPC-2850
artifact: epic
status: done
revised: 2026-10-24
realises: ADR-3040
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ten requirements that no task names get one epic

Realises exactly one authorising record, ADR-3040. The epic is complete when
every requirement the decision addresses is named by a task that is done.

## Acceptance criteria

1. The shared executable's name, its distribution, the equal versions of a
   plugin and its package, and the trunk's passing gate each have a test that
   cites the requirement it proves.
2. A hook that asks a judge fires only on a publishing command.
3. `paw check` completes in under one second on a tree it has read.
4. A unit's committed launcher and Pi extension equal what a generator writes,
   a unit's description and page agree across their four copies, and a
   launcher resolves its binary once per machine.
5. Every requirement ADR-3040 addresses is named by a closed task.

## Tasks

- T-001 [P] TSK-5680 name the requirements the existing checks prove, in `tools/`
  closes: REQ-4610, REQ-4612, REQ-4614, REQ-3074

- T-002 [P] TSK-5681 hold a judge hook's matchers to publishing commands, in `tools/`
  closes: REQ-2798

- T-003 [P] TSK-5682 make `paw` answer within a second on a tree it has read, in `crates/meow/`
  closes: REQ-2800

- T-004 [P] TSK-5683 generate each unit's launcher and Pi extension and hold the copies of its description and page to each other
  closes: REQ-4624, REQ-3196, REQ-4622

- T-005 TSK-5684 resolve a launcher's binary once per machine
  closes: REQ-4510
  depends: TSK-5683 (blocking) - the generated launcher carries the cache

## Coverage

Each of the ten requirements ADR-3040 addresses lands in exactly one task. The
two tasks that name existing behaviour are the smallest set that tests the
decision's claim that those requirements already hold.

## Not covered

How a package's host-specific sections are marked, which TSK-5683 settles when
it meets the first one.
