---
id: ADR-1510
artifact: adr
status: approved
revised: 2026-09-27
addresses: [REQ-1664]
supersedes: []
---

# 1510. A requirement declares one of four kinds of check, and the record holds it

## Decision

`paw check rules` gains `verification-kind`, a rule on every requirement: its
`verification` field holds exactly one of `static`, `behavioural`,
`evaluation` and `judgement`, and anything else is a finding naming the four
(REQ-1664). The record already requires the field on every requirement, so
this rule checks its value, which nothing checks today: `paw status` counts a
value outside the four as unstated and fails nothing.

The rule applies to approved requirements as well as drafts, with no
migration, because all 1,091 requirements in force already carry one of the
four, as `paw status` counts them on `main` after #532: 491 static, 539
behavioural, 19 evaluation and 42 judgement, and none unstated.

Whether a requirement can really be checked the way its field says is a
judgement a program can't make, so the record reviewer's question for a
requirement, whether it can be tested by the check its `verification` names,
asks that half of REQ-1662 for every requirement written from now on, as
ADR-1490 put it there. This decision doesn't address REQ-1662, because nothing
here reaches the approved requirements that question was never asked of.

After this decision a requirement naming no kind of check, or a fifth one,
fails the check in the change that writes it. What still doesn't work:
whether an approved requirement is really checkable as it says was never
reviewed against that question, and nothing asks it again.

## Why

RES-0070 found that the check vocabulary needs a fourth value, judgement, so
the corpus can report how much of itself rests on judgement, and that a
requirement no check can settle can't be said to be met or unmet. A declared
kind is only a declaration if its value is one the harness knows: a field
reading `verification: statc` today passes `paw check` and reads as unstated
in `paw status`, which is the drift a check exists to stop.

The value is mechanical and the checkability is not, so each goes where
ADR-1490 and REQ-0132 send it: the program checks the value, and the agent
judges the claim.

The strongest objection: this breaks the pattern the record's other rules
follow, where a new rule applies to drafts only, such as the rule that a judged
requirement names its verifier, so a record approved under the old rules
keeps them. The pattern protects approved records that break a new rule, and
none breaks this one. Applying it to them is worth doing because `paw status`
counts every requirement in force by its `verification` to report how much
rests on judgement (REQ-0161), and a value outside the four in an approved
record would miscount that share for as long as the record stands.

## Alternatives

| Option                                | Better at                           | Why it lost                                                                                                                                  |
| ------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                            | No change                           | A misspelt kind passes the check, and `paw status` silently counts it as unstated                                                            |
| A draft rule only                     | Leaves approved records as they are | No approved record breaks the rule, and the share `paw status` reports reads every approved record, which a draft rule would leave unchecked |
| Check checkability with a program too | One place for both halves           | Whether a requirement can be tested is a judgement, and a check encoding one fires wrongly and is switched off (REQ-0147)                    |

## What it costs

`meow-flow` gains one rule, and an author who writes a kind outside the four
has to fix it in the same change. Because the rule reaches approved records,
renaming or removing a kind later means superseding every approved
requirement that holds it, since a frozen record can't be edited, paid by
whoever proposes the change. Adding a kind costs nothing, because every
approved record still holds one of the kinds it would allow.

## What would reverse it

I would move the rule to drafts only if someone proposed renaming or removing
a kind, because approved records holding it would then fail and could only be
superseded. A fifth kind of check would need a new requirement superseding
REQ-1664, which fixes the set at four, before the rule could change.

## Consequences

- `paw check rules` gains `verification-kind`, listed in `lib/layout.toml`
  for requirements.
- SPC-1070 states it.

## How I will know it was realised

1. A fixture shows `paw check rules` failing on a requirement whose
   `verification` is outside the four, on an approved one as well as a draft,
   and passing on each of the four.
2. `paw check` passes on the project record.
3. REQ-1664 lands in exactly one closed task.

## What this does not settle

- REQ-1662, that every requirement is checkable: the reviewer asks it of new
  requirements, and nobody has asked it of the approved ones.
- REQ-1662 declares `verification: static`, though what can settle it is a
  judgement, the reviewer's question; the requirement that fixes that
  supersedes it.

## Open review findings

- An alternative between the two in the table: fail on drafts and only warn
  on approved records. Left open: no approved record holds a value outside the
  four, so a warning would never fire, and the choice matters only when a
  kind is renamed or removed, which the reversal above already covers.
