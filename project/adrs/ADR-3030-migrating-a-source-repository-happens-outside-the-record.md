---
id: ADR-3030
artifact: adr
status: approved
revised: 2026-10-24
addresses: []
postpones: [REQ-1666]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3030. Migrating a source repository happens outside the record

## Decision

I postpone REQ-1666, which asks that the six source harnesses migrate onto this
harness without losing behaviour they rely on, and I withdraw TSK-5045, the one
task that closed it. The owner migrates the repositories by hand, in those
repositories, and records a result in this one only when it shows a defect or a
missing capability in the harness, as ADR-2690 and the method's rule on a
missing capability already say. This repository records no task for work that
runs in another.

Once this is accepted, REQ-1666 reads as postponed, EPC-2570 closes with the
tasks it still has, and `paw status` names no `next:` for it. What still doesn't
work: the vision's success test, that the six repositories drop their private
copies and lose nothing, has no task behind it here, and nothing in this record
shows whether it was met.

## Why

The owner said on 2026-10-24 that the migrations will be done separately. A
task whose work runs in another repository can't be built, tested or reviewed
in a pull request of this one, so it would stay open for as long as the
migration takes, and `paw status` would name it as the next step all that time.

## Alternatives

| Option                                       | Better at                          | Why it lost                                                                       |
| -------------------------------------------- | ---------------------------------- | --------------------------------------------------------------------------------- |
| Do nothing                                   | Keeps the success test in the plan | Names a task as next that no session here can do                                  |
| Withdraw the task and keep REQ-1666 in force | Keeps the obligation visible       | A requirement in force with no task fails `paw check`, so the gate would stay red |

## What it costs

The record no longer tracks the migration, so a migration that never happens
leaves no open item here to show it.

## What would reverse it

- The owner asks for a migration to be recorded here, or a migration shows a
  defect in the harness, which opens a defect and its own tasks.

## Consequences

REQ-1666 reads as postponed, TSK-5045 is withdrawn, and EPC-2570 and ADR-2690
close.

## How I will know it was realised

1. `paw status` lists REQ-1666 under Postponed and names no `next:` for
   EPC-2570.
2. `paw check` reports no finding.

## What this does not settle

- Whether the migrations succeed, which only the repositories themselves show.
