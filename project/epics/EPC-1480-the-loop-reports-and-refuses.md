---
id: EPC-1480
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1500
checked-at: "#531"
---

# The evaluation loop reports what a measurement rests on, and refuses what it can't hold

Realises exactly one authorising record, ADR-1500. The epic is complete when
`tools/loop.py` runs both arms in every mode, reports each result's error, run
count, judge family and threshold commit, labels each case, and refuses an
uncommitted threshold file and a `baseline` grader.

## Acceptance criteria

Taken from ADR-1500, from its list of how I will know it was realised, before
the task below was written:

1. Unit tests of `tools/loop.py`, run by the `test` verb with no model call,
   show a case whose interval lies within the margin of zero flagged for
   deletion, a case whose interval is wider than the margin reported as
   undetermined, a rate reported with its error, the judge's family computed
   from its identifier and the header's wording for each family, a run of 3 or
   fewer said to support no claim, a candidate landing only within twice the
   combined error, a case falling short of its threshold given no pass, a case
   with no threshold given no verdict, the threshold commit named in the
   header, and each refusal: a threshold file differing from the last commit,
   and a `baseline` grader.
2. A loop run by hand on `meow-flow`'s cases prints both arms, the error of
   each rate, the run count and the judge's family.
3. Every requirement ADR-1500 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2310 make `tools/loop.py` report what each result rests on and
      refuse what it can't hold, with its unit tests
      closes: REQ-0153, REQ-0159, REQ-0160, REQ-1759, REQ-3022, REQ-3026,
      REQ-3028
      evidence: 18 unit tests, 17 seen failing first, and a two-arm run on
      `meow-flow`, in #529.

## Verified

I checked this under #531 on `main` after #530, gathering the evidence there
rather than carrying it over from the task. `meow-verbs evidence format lint
test` exits 0, each current at tree `cbd733e923bd`, and
`python3 -m unittest tools/test_loop.py` runs 18 tests, OK. Every criterion is
met:

| Criterion                                                                                                                                                     | Evidence on `main` after #530                                                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. Unit tests show each label, each rate's error, the judge's family and wording, the run count rule, the landing rule, the threshold rules and both refusals | `Labels`, `Rates`, `Judge`, `Verdicts` and `Refusals` in `tools/test_loop.py` pass, 18 tests, run by the `test` verb                                                                                         |
| 2. A run by hand on `meow-flow` prints both arms, each rate's error, the run count and the judge's family                                                     | TSK-2310's run, made with `tools/loop.py` as #530 merged it, since the file was not edited between that run and the merge; not repeated, because it costs a paid run and the tests hold each line it printed |
| 3. Every requirement lands in exactly one closed task                                                                                                         | `paw show` derives all 7 requirements ADR-1500 addresses as closed, by TSK-2310                                                                                                                              |

The error of 0 at a rate of exactly 0 or 1, which TSK-2310 recorded, stays a
known limit of the loop.

### Documentation

The loop is repository tooling with no page of its own; SPC-1020 states its
report and refusals, and its docstring names the `--allow-tool` option.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1500 addresses 7 requirements, and each lands in the one task above,
because every one of them is a change to the same program and its tests, and
splitting them would put one file's change in several pull requests.

## Not covered

Nothing ADR-1500 addresses. A cross-family judge and which judge counts as
stronger are left out, as ADR-1500 says.
