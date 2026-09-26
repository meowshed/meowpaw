---
id: TSK-1460
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1110
closes: [REQ-0223, REQ-0262, REQ-0558, REQ-2868, REQ-2882]
issue: 200
---

# The rules check

One task, one branch, one pull request, one review.

## What to do

Add a seventh check, `rules`, running the named rules the layout lists per kind, each with its scope: a research draft's source lines each carry a date, a research draft's body cites no requirement, a requirement draft verified by judgement carries `verifier`, an epic's `realises` names exactly one decision or defect, and a decision's alternatives table has a column saying why each lost. Write a fixture for each, seen failing first.

## Depends on

TSK-1450, because the rules read the scope the layout declares.

## Evidence

`meow-method check rules` is the seventh check. It runs the named rules each
kind lists in `lib/layout.toml`, under `rules` for every record and
`draft_rules` for drafts: a research draft dates each source and cites no
requirement, a judged requirement draft names its verifier, an epic realises
exactly one decision or defect, and a decision's alternatives table says why
each lost. A rule the layout names and the program doesn't know is itself a
finding, so a typo can't switch a rule off.

Five new fixtures, each showing the rule and, for the drafts-only ones, the
approved record passing:

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 48 tests in 2.086s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=47, errors=1)

$ meow-method check rules
rules: 0 findings
```

On this repository every decision's alternatives say why each lost and every
epic realises one record, and the approved research and requirements that
break the drafts-only rules pass, as ADR-1140 decides. `docs/meow-method.md`
lists the check, and `meow-method` is 0.3.0.

## Left alone

Rules that need judgement, as ADR-1140 says.
