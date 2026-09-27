---
id: EPC-1510
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1530
checked-at: "#559"
---

# Cited evidence is kept in the repository, and the ledger is held to the state rules

Realises exactly one authorising record, ADR-1530. The epic is complete when a
cited record can be kept in the repository and compared with a commit, the
ledger holds to the state rules, and a run cut short is recorded as
interrupted.

## Acceptance criteria

Taken from ADR-1530, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show `evidence --keep` writing a current record's file with its
   header and whole output, refusing a stale record, and leaving the tree id
   unchanged; and a changed `evidence_dir` used.
2. Fixtures show the repository's identity in each record; a corrupt line
   reported as absent; a started record reported as running while its process
   lives and interrupted after; a verb killed by a signal recorded as
   interrupted, with exit 4 from `run` and `evidence`; records older than 30
   days dropped by a run under the lock; `state --purge` emptying the ledger;
   a stale lock replaced; an append made during a prune kept; a dropped
   record's output file deleted; `MEOWPAW_STATE=off` writing nothing;
   `MEOWPAW_STATE_DIR` moving it; `state` printing the ledger's facts;
   `tree <commit>` matching a kept record's tree id; bare `--keep` keeping
   every current verb; and `evidence --all` listing a second work tree's
   records.
3. The `verify` skill and the implement step cite the kept path, traced in the
   task's evidence.
4. Every requirement ADR-1530 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2340 keep a cited record in the repository, leave the evidence
      directory out of the tree id, and add `meow-verbs tree`, with the skill
      and the implement step citing the kept path
      closes: REQ-2956, REQ-2964, REQ-3072
      evidence: five fixtures, four seen failing first, and the skill traced,
      in #547.

- [x] T-002 TSK-2350 hold the ledger to the state rules: identity, lock,
      prune, purge, `state`, the environment switches and `evidence --all`
      closes: REQ-0752, REQ-0754, REQ-0756, REQ-0758, REQ-2958, REQ-2960,
      REQ-2962, REQ-2966, REQ-2967, REQ-2970
      evidence: ten fixtures seen failing first, in #548.

- [x] T-003 TSK-2360 record a verb as started and ended, and report
      `interrupted` and `running`
      closes: REQ-2968, REQ-2969
      evidence: three fixtures seen failing first, in #549.

## Verified

I checked this under #559 on `main` after #558, gathering the evidence there
rather than carrying it over from the tasks. `meow-verbs evidence --keep
format lint test` exits 0 on this change's own tree, each result kept in
`project/evidence/`, as the pull request cites. The `Kept`, `State` and
`Interrupted` fixtures, 21 tests, pass. Every criterion is met:

| Criterion                                                                                                                                                                                                         | Evidence on `main` after #558                                                                          |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1. `--keep` writes a current record with its header and output, refuses a stale one, leaves the tree id unchanged, and obeys `evidence_dir`                                                                       | The `Kept` fixtures pass, under ADR-1550's name and place                                              |
| 2. Identity, absent lines, running and interrupted, the signal, pruning, purging, the stale lock, the append during a prune, output deleted, the environment switches, `state`, `tree`, bare `--keep` and `--all` | The `State`, `Interrupted` and `Kept` fixtures pass                                                    |
| 3. The `verify` skill and the implement step cite the kept path                                                                                                                                                   | Step 6 and V7 of the skill and step 4 of the implement step, traced in TSK-2340                        |
| 4. Every requirement lands in exactly one closed task                                                                                                                                                             | `paw show` derives all 15 requirements ADR-1530 addresses as closed by TSK-2340, TSK-2350 and TSK-2360 |

ADR-1550 changed criterion 1's directory and name from
`.meowpaw/evidence/<record>.log` to `project/evidence/<record>.txt`; the
criterion is met as amended.

### Documentation

TSK-2340, TSK-2350 and TSK-2360 described keeping, the ledger's state and the
interrupted outcome on `meow-verbs`' page, at 0.6.0. The `test` verb checked
it, running `tools/check_docs.py`.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1530 addresses 15 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001. T-002 and T-003 change the
same ledger code, so they run in order after T-001.

## Not covered

Nothing ADR-1530 addresses. Keeping evidence outside the main history and the
method's own run state are left out, as ADR-1530 says.
