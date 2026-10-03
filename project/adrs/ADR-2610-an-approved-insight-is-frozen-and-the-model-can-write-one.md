---
id: ADR-2610
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2142, REQ-2662]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2610. An approved insight is frozen, and the model can write one

## Decision

An insight freezes on approval like every other record, so `paw check
frozen` fails a change to an approved insight (REQ-2662). This already holds:
`check_frozen` in `crates/meow/src/record.rs` allows a change after approval
only to an epic, a task or a defect's mutable parts, and treats every other
kind, the insight among them, as frozen whole. The task for REQ-2662 is a test
that pins it. A later lesson on the same subject is a new insight that cites
the first.

The method's rule M11 lets the model write an insight as a draft when the work
taught something that holds past its case, with no person's prompt, and a
person approves it as they would any record (REQ-2142). ADR-1220 already made
the insight a kind open to the model.

Once this is accepted, a test holds what the tree already does, and an
insight cited by a later record says what it said when it was cited. What still doesn't work: an insight carries no date, see
the last section.

## Why

RES-0159 found that a lessons file edited in place loses the version that
other notes cited, and that the party that did the work holds the numbers
the lesson rests on, so the model has to be able to write it. ADR-1170
already holds approved records frozen with `paw check frozen`.

## Alternatives

| Option                        | Better at                     | Why it lost                                             |
| ----------------------------- | ----------------------------- | ------------------------------------------------------- |
| Do nothing                    | No change                     | An insight can be edited after a record cited it        |
| Insights as a living document | One file to read              | A living file rewrites the lesson a record cited        |
| Only a person writes insights | Fewer insights, each reviewed | The person doesn't hold the numbers the lesson rests on |

## What it costs

A wrong insight can't be fixed in place, and its correction is a second
insight that a reader has to find.

## What would reverse it

- Insights that correct an earlier insight outnumber insights that teach
  something new, which would show freezing them costs more than it keeps.

## Consequences

The crate gains a test for a changed approved insight. The method's step
files say the model may write an insight draft unprompted.

## How I will know it was realised

1. `paw check frozen` fails a change to a fixture insight (REQ-2662).
2. The method's step files let the model write an insight with no person's
   prompt (REQ-2142).

## What this does not settle

- REQ-2666, which asks that an insight carry its date. CLAUDE.md says that no
  path or field records when work happened, so the two disagree, and a later
  decision has to withdraw one of them.
