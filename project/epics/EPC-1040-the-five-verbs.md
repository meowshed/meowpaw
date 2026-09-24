---
id: EPC-1040
artifact: epic
status: draft
revised: 2026-09-24
realises: ADR-1070
checked-at:
---

# The five verbs, resolved from the profile

Realises exactly one authorising record, ADR-1070. The epic is complete when
`meow-verbs` resolves the five verbs from a repository's profile, reports each
as resolved or as unresolved and of which kind without running anything, runs
a verb recording its command, exit status and whole output, and never reports
an unresolved verb as passed, and when this repository uses it for its own
verbs.

## Acceptance criteria

Taken from ADR-1070, from its list of how I will know it was realised, before
the tasks below were written:

1. In a repository with no profile, `meow-verbs status` reports all five verbs
   unresolved as "no profile", and `meow-verbs run lint` reports lint
   unresolved and exits with a status that is not success.
2. With a profile that can't be parsed, all five verbs report "profile
   unparseable", and nothing runs.
3. With a profile declaring `lint` as a command that fails, `run lint` reports
   the exact command, its exit status and its whole output, with the failing
   lines in the report.
4. A key the unit doesn't recognise is reported, and every declared verb still
   resolves.
5. With the interpreter missing, every verb reports unresolved, and nothing
   reports passed.
6. This repository's `meow-verbs status` shows `fmt`, `lint` and `test`
   resolved from its profile, and `typecheck` and `build` undeclared.
7. Every requirement ADR-1070 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1280 `plugins/meow-verbs/`: the manifest, the launcher and the
      program's `status` and `run`, each failure path in SPC-1040 a fixture
      closes: REQ-0130, REQ-0131, REQ-0134, REQ-0135, REQ-0136, REQ-0144,
      REQ-0150, REQ-0154, REQ-0156

- [ ] T-002 TSK-1290 the skill, the documentation page, the budget, the
      marketplace entry and this repository's own profile
      closes: REQ-0158
      depends: TSK-1280 - the skill calls the program, and the profile is read
      by it

## Coverage

ADR-1070 addresses ten requirements. Each lands in exactly one task above, and
`tools/check_coverage.py` compares the decision's `addresses` against the
union of the tasks' `closes`.

T-001 alone is the smallest subset that tests the decision: with it closed, a
repository that declares its verbs gets the honest report ADR-1070 promises.
T-002 puts it in front of the model and uses it here.

## Not covered

Nothing ADR-1070 addresses is left out. What ADR-1070 leaves to later
decisions, runner binding, packs, subsets and evidence, is outside this epic.
