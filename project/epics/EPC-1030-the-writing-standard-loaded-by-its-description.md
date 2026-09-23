---
id: EPC-1030
artifact: epic
status: approved
revised: 2026-09-23
realises: ADR-1050
checked-at:
---

# The writing standard loaded by its description

Realises exactly one authorising record, ADR-1050. The epic is complete when
the writing skill carries the description ADR-1050 states, `meow-prose` ships
no hook for loading it, and the routing measurement shows the skill loading on
writing requests and not on near misses, on Sonnet 5 and on Opus 5.5.

## Acceptance criteria

Taken from ADR-1050, from its list of how I will know it was realised, before
the task below was written:

1. The writing skill loads in at least nine runs of ten on the writing
   requests RES-0272 lists, on Sonnet 5 and on Opus 5.5, with the published
   plugin installed.
2. On the same two models, the near misses that change code load it in no
   more than one run of ten. Answers in chat and edits to a Markdown file are
   prose, and loading on them is not a miss.
3. `meow-prose` ships no hook, and SPC-1010 and SPC-1030 name none.
4. Every requirement ADR-1050 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1270 give the writing skill the description ADR-1050 states,
      and publish its routing on both models
      closes: REQ-1144, REQ-1146, REQ-1148, REQ-1150
      evidence: 36 of 36 writing runs on Sonnet 5 and 33 of 33 on Opus 5.5,
      none on work that changes code, in #84. TSK-1270 carries the table.

## Coverage

ADR-1050 addresses four requirements, and T-001 closes all of them, which
`tools/check_coverage.py` compares against the decision's `addresses`. The one
task is the smallest subset that tests the decision.

## Not covered

The descriptions of the other shipped units, which TSK-1240 rewrites in the
third person under EPC-1020. None of them has to be in context before the
model acts, so ADR-1050 does not apply to them.
