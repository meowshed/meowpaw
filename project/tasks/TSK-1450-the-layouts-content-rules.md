---
id: TSK-1450
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1110
closes:
  [
    REQ-0216,
    REQ-0219,
    REQ-0234,
    REQ-0247,
    REQ-0266,
    REQ-0309,
    REQ-0512,
    REQ-0514,
    REQ-0538,
    REQ-0540,
    REQ-0546,
    REQ-0556,
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
    REQ-2878,
    REQ-2884,
    REQ-2886,
    REQ-2898,
    REQ-2912,
    REQ-2914,
    REQ-2923,
    REQ-2924,
    REQ-3102,
  ]
issue: 199
---

# The layout's content rules and their scope

One task, one branch, one pull request, one review.

## What to do

Extend `lib/layout.toml` and the checker with the per-kind keys SPC-1070 states: `sections` for every record, `draft_sections` for drafts, `first_section`, `required_values` for fields that must be non-empty, and `forbidden_fields`. Exempt a kind's own index file from its sections. Write a fixture for each key, each showing a draft held to a drafts-only rule and an approved record not held to it, each seen failing first against a program that returns nothing. Add fixtures for the existing rules ADR-1140 records as held: one file per artifact, the numbered kinds, the status vocabulary and the unstored observed statuses.

## Depends on

Nothing. ADR-1140 and SPC-1070 are approved.

## Evidence

`lib/layout.toml` declares each kind's content rules and their scope, and the
checker reads them: `sections` and `draft_sections` in `shape`, with a kind's
own index exempt, `first_section` in `shape`, and `required_values` and
`forbidden_fields` in `front-matter`. Research gains `Method` and opens with
`Summary`; a decision gains `What would reverse it`, and as a draft `How I
will know it was realised` and `What this does not settle`; a defect gains
`Triage` and `Closed by` and never a `priority`; a requirement never carries a
`priority`, `owner` or `difficulty`; a decision's `addresses` is never empty.

Ten new fixtures, one per rule and scope, and one each for the rules ADR-1140
records as already held: the living vision stores only `live`, an observed
status is never stored, and a numbered kind is named for its identifier. The
clean record in the fixtures gains the sections the layout now requires.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 43 tests in 1.819s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=42, errors=1)

$ meow-method check
front-matter: 0 findings    identifiers: 0 findings    relations: 0 findings
index: 0 findings           coverage: 0 findings       shape: 0 findings
```

On this repository the approved record passes, because the rules it breaks
apply to drafts.

## Left alone

The named rules, which TSK-1460 adds.
