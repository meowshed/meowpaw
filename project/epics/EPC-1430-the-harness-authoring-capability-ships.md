---
id: EPC-1430
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1450
checked-at:
---

# An authoring unit ships how the harness's own material is written, and a check any repository runs

Realises exactly one authorising record, ADR-1450. The epic is complete when
`meow-author` ships its check and its skill, and this repository's gate runs
the shipped check in place of its own script.

## Acceptance criteria

Taken from ADR-1450, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-author check` passes on this repository's units, and fixtures show it
   failing on each condition it lists.
2. `meow-author check .claude` runs on a repository's own skills, shown by a
   fixture holding a skill outside any unit.
3. The skill's rules carry each requirement ADR-1450 addresses, traced in the
   task's evidence, and the check passes on the skill.
4. The skill's description loads it before a skill is written in at least
   four of five sessions on each of Sonnet 5 and Opus 5.5, and on no more than
   one of five near misses that change code.
5. Every requirement ADR-1450 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [ ] T-001 TSK-2200 ship `meow-author check`, run it in this repository's
      gate, and retire `tools/check_prompts.py`
      closes: REQ-1110, REQ-1111, REQ-1112, REQ-1114, REQ-1120, REQ-1122,
      REQ-1124, REQ-1128, REQ-1142, REQ-1672, REQ-1678, REQ-2688

- [ ] T-002 TSK-2210 give `meow-author` the skill that carries the rules a
      program can't settle
      closes: REQ-1116, REQ-1118, REQ-1126, REQ-2680, REQ-2682, REQ-2684,
      REQ-2686, REQ-2690, REQ-2692, REQ-2706, REQ-2708
      depends: TSK-2200 - the skill ships in the unit T-001 creates

## Coverage

ADR-1450 addresses 23 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001: once it lands, a repository
can check its own material with the shipped program.

## Not covered

Nothing ADR-1450 addresses. Context cost and loading are a later decision, as
ADR-1450 says.
