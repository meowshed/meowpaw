---
id: EPC-2300
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2380
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A run lives in the session, and decides, merges and releases on its own

Realises exactly one authorising record, ADR-2380. The epic is complete when a
person types `/meow-loop:run` in a session and the chain repeats there until
the record holds no open work, a bound is reached, the run is stuck or the
person cancels it. During the run, the run decides each gate, merges and
releases itself and reports what it did, as SPC-1201 and SPC-1200 state.

## Acceptance criteria

Taken from ADR-2380's list of how it will be known realised:

1. In a session, a fixture start command with all three bounds writes a run state, and a Bash call that runs the start
   logic from the model is denied.
2. With a run active, the `Stop` hook blocks with the frozen prompt while a
   requirement is open, and allows the stop with `finished` once a fixture
   record has none open.
3. Two fixture iterations that change nothing end the run `stuck` with the
   counts named, and a reached ceiling, time or token bound ends it with that
   bound's ending.
4. Any prompt other than the start command during a run ends it `cancelled`,
   and the next `Stop` allows the stop.
5. An edit of the run's state during a run is denied in every permission mode.
6. `report.md` lists each approval, merge and release a fixture run recorded.
7. A start in a session whose permission mode differs from the declared one is
   refused with the two modes named.
8. Every requirement ADR-2380 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [x] T-001 TSK-4100 start a run from the person's prompt and cancel it on the next one, in `plugins/meow-loop` and `crates/meow` (done: pull request 881)
      closes: REQ-0872, REQ-0874, REQ-0890, REQ-0894, REQ-2660, REQ-2962, REQ-3700, REQ-3712

- [ ] T-002 TSK-4110 decide each iteration in the `Stop` hook, from the record, the bounds and the transcript
      closes: REQ-0870, REQ-0876, REQ-0878, REQ-0882, REQ-0884, REQ-0886, REQ-0892, REQ-2654, REQ-2656, REQ-2658, REQ-3702, REQ-3704, REQ-3706, REQ-3708, REQ-3710
      depends: TSK-4100 (blocking) - the `Stop` hook reads the run state the start writes

- [ ] T-003 [P] TSK-4120 resolve the posture, check the session's mode at start and deny what the posture forbids
      closes: REQ-2370, REQ-2388, REQ-3722
      depends: TSK-4100 (blocking) - the start hook refuses on an unresolved posture

- [ ] T-004 [P] TSK-4130 make `/meow-flow:run` decide gates, land and release, report, and choose the next block in a run
      closes: REQ-2380, REQ-2382, REQ-2384, REQ-2386, REQ-2402, REQ-3714, REQ-3716, REQ-3718, REQ-3720
      depends: TSK-4110 (not blocking) - the skill reads the run id the frozen prompt names, and works in a fixture without a live run

## Coverage

TSK-4100 to TSK-4130 close every requirement ADR-2380 addresses. REQ-1240,
which SPC-1201 states, is closed already by an earlier task, and the failure
tables in SPC-1201 and SPC-1200 keep it true. TSK-4110 is the smallest task
that tests the decision, because it holds the loop and its endings.

## Not covered

REQ-2396, REQ-2398, REQ-2400 and REQ-2404 are postponed by ADR-2380, so no task
names them. Removing `meow-loop start` after its deprecation release is a
later change, because REQ-3004 puts the removal in the release after the one
that announces it.
