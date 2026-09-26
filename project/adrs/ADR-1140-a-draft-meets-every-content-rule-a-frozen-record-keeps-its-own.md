---
id: ADR-1140
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-0216,
    REQ-0219,
    REQ-0223,
    REQ-0234,
    REQ-0247,
    REQ-0262,
    REQ-0266,
    REQ-0309,
    REQ-0512,
    REQ-0514,
    REQ-0538,
    REQ-0540,
    REQ-0546,
    REQ-0556,
    REQ-0558,
    REQ-0560,
    REQ-0562,
    REQ-0587,
    REQ-0588,
    REQ-0589,
    REQ-0592,
    REQ-0593,
    REQ-2668,
    REQ-2864,
    REQ-2866,
    REQ-2868,
    REQ-2878,
    REQ-2882,
    REQ-2884,
    REQ-2886,
    REQ-2898,
    REQ-2912,
    REQ-2914,
    REQ-2923,
    REQ-2924,
    REQ-3102,
  ]
supersedes: []
---

# 1140. A draft meets every content rule, and a frozen record keeps the rules it was approved under

## Decision

`meow-method check` holds each kind's content rules that a program can settle:
the sections it carries, the section it opens with, the fields it must fill
and the fields it must not carry, and five named rules that need more than a
section heading. `lib/layout.toml` declares them per kind, so a repository
reads them and the unit's code doesn't hide them.

A rule applies to every record of its kind, except where the approved record
already breaks it. Such a rule applies to drafts only, and the layout says so,
because an approved record is frozen and a check that fails on it can't be
fixed without rewriting what someone accepted. A draft is what its author can
still change, so a draft meets every rule, and the `ready` gate of the next
step refuses until it is approved, which is after it was checked.

The rules, by kind:

| Kind        | Every record                                                                                                                                                         | Drafts only                                                              |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| research    | sections Summary, Method, Conclusions and Sources, opening with Summary; the kind's index exempt from sections                                                       | every source carries the date it was read; the body cites no requirement |
| requirement | carries no `priority`, `owner` or `difficulty`                                                                                                                       | one verified by judgement names its `verifier`                           |
| decision    | `addresses` names a requirement; sections Decision, Why, Alternatives, What it costs, What would reverse it, Consequences; the alternatives table says why each lost | sections How I will know it was realised and What this does not settle   |
| epic        | `realises` names exactly one decision or defect; sections Acceptance criteria, Tasks, Coverage and Not covered                                                       |                                                                          |
| defect      | sections Reproduction, What the system does, What it should do and why, Triage and Closed by; no `priority`                                                          |                                                                          |

The status vocabulary, the one-file-per-artifact layout and the coverage check
already hold REQ-0512, REQ-0514, REQ-0538, REQ-0540, REQ-0546, REQ-0587 to
REQ-0593, REQ-2668, REQ-0266 and REQ-3102, and this decision records that they
do, with a fixture for each where none exists.

After this decision a draft that leaves out a section its kind carries, cites a
requirement from research, or lists an undated source fails `meow-method
check`, and the approved record passes as it does today. What still doesn't
work: indexes are kept by hand and aren't checked for order, and a rule that
needs judgement, such as whether a title states a position, isn't checked.

## Why

The probe of this repository on 2026-09-26 found that 126 of 131 approved
research records have a source with no date, three cite a requirement, seven
requirements verified by judgement name no verifier, and two decisions lack
the section saying how they will be known realised. `CLAUDE.md` freezes a
record on approval and routes a correction through an amendment, so the record
can't be brought up to the new rules, and a check that fails on it is switched
off within a week, as `CLAUDE.md`'s gate section says. Holding drafts is where
the rule still does its work: at the moment someone writes the record.

REQ-2694 asks that a rule a program can settle be a check, and every rule here
is a section, a field or a pattern. Declaring them in the layout keeps the
rules readable by a repository that overrides them, as REQ-0516 fixes each
kind's meaning in the harness.

The strongest objection: an approved record that breaks a rule stays broken,
and a reader citing RES-0270 meets a research record that cites a requirement.
That's true, and the alternative, rewriting approved records to the new rule,
is the failure the method exists to prevent. Where a frozen record is wrong in
substance and not only in form, a defect record corrects it, as BUG-1110 did.

## Alternatives

| Option                                                             | Better at                                     | Why it lost                                                                                   |
| ------------------------------------------------------------------ | --------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Every rule on every record, drafts only where the corpus breaks it | Holds the most, fails on nothing it can't fix | Chosen                                                                                        |
| Every rule on every record                                         | One rule, one scope                           | Fails on 126 frozen records the day it lands, and gets switched off                           |
| Every rule on drafts only                                          | Simplest to state                             | Stops checking the frozen record for rules it already meets, so a later edit could break them |
| Rules checked by the step's prose, not the program                 | No code                                       | A model skips a rule it was told about; REQ-2694 asks for a check                             |
| Do nothing                                                         | Costs nothing                                 | The content rules hold by discipline, and the probe shows how often discipline missed them    |

## What it costs

The layout grows per-kind keys, the checker reads them, five named rules are
written in the crate, and a fixture is added for each rule and each scope. The
frozen record's breaches stay, named in this decision.

## What would reverse it

- A repository needs a rule applied to its frozen records, and the per-kind
  scope can't express which.
- The platform or a later decision lets an approved record be migrated
  mechanically, and the drafts-only scope becomes unnecessary.

## Consequences

- `lib/layout.toml` gains `sections` and `draft_sections`, `first_section`,
  `required_values`, `forbidden_fields` and `rules` per kind.
- `meow-method check shape` and `front-matter` read them, and a new check,
  `rules`, runs the named rules.
- SPC-1070 states the rules and their scope.

## How I will know it was realised

1. A draft research record with an undated source fails `meow-method check
rules`, naming the line, and the approved record's undated sources don't.
2. A draft decision without a section saying how it will be known realised
   fails `shape`, and ADR-1000 doesn't.
3. A requirement carrying `priority` fails `front-matter`, draft or approved.
4. `meow-method check` on this repository reports 0 findings.

## What this does not settle

- Generating the indexes from the tree, and checking their order.
- Rules that need judgement, such as a title stating a position or a
  requirement standing alone.
- Correcting the frozen records that break a drafts-only rule.
