---
id: EPC-1150
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1150
checked-at: "#219"
---

# Identifiers resolved both ways, and closed tasks held to their evidence

Realises exactly one authorising record, ADR-1150. The epic is complete when
`meow-method show` resolves an identifier and lists what cites it, and the
epic's three new rules hold on every record.

## Acceptance criteria

Taken from ADR-1150, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-method show REQ-0190` prints its path, status and title, and lists
   ADR-1130 under `addresses` and SPC-1090 under `states` among what cites it.
2. `show` on a withdrawn requirement prints it as withdrawn.
3. An epic marking a task `[x]` whose evidence is only "Not yet." fails `check
rules`, naming the task.
4. `meow-method check` on this repository reports 0 findings.
5. Every requirement ADR-1150 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1500 `meow record show`, resolving an identifier and deriving
      what cites it, with fixtures for the relation rules it records
      closes: REQ-0237, REQ-0638, REQ-0640, REQ-0642, REQ-0644, REQ-0646, REQ-0648, REQ-0650, REQ-0652, REQ-0654, REQ-0658
      evidence: five fixtures, `show` seen resolving both ways, in #214.

- [x] T-002 TSK-1510 the epic's rules for a done, an added and a dropped task
      closes: REQ-0692, REQ-0698, REQ-0700, REQ-0702
      evidence: three fixtures, each rule seen failing and then passing, in
      #215.

## Verified

Checked under issue 219 at revision `85b9f5c`, with evidence gathered there
and not carried over from the tasks. Every criterion is met:

| Criterion                                                                                                          | Evidence at `85b9f5c`                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `show REQ-0190` prints path, status and title, and lists ADR-1130 under `addresses` and SPC-1090 under `states` | `meow-method show REQ-0190` prints the requirement, approved, with its path, and under `Cited by`: `addresses: ADR-1130`, `states: SPC-1090` |
| 2. `show` on a withdrawn requirement prints it as withdrawn                                                        | `meow-method show REQ-1140` opens with `REQ-1140 requirement, withdrawn`                                                                     |
| 3. An epic marking a task done whose evidence is only "Not yet." fails `check rules`                               | `test_a_task_marked_done_carries_evidence` runs `OK`                                                                                         |
| 4. `meow-method check` on this repository reports 0 findings                                                       | 7 checks report 0 findings                                                                                                                   |
| 5. Every requirement in one closed task, nothing outstanding                                                       | `coverage` reports 0 findings; the unit's fixtures run `OK`                                                                                  |

## Coverage

ADR-1150 addresses fifteen requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The two tasks can run in parallel, and T-001
alone tests the decision.

## Not covered

Listing checks and tests that name a requirement, unmarked work that landed,
and generated indexes, as ADR-1150 says.
