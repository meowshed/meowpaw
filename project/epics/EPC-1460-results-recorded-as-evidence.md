---
id: EPC-1460
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1480
checked-at: "#517"
---

# `meow-verbs` records each result against the tree it ran on, and evidence cites the record

Realises exactly one authorising record, ADR-1480. The epic is complete when
`meow-verbs run` records each result in a ledger bound to a tree id,
`meow-verbs evidence` reports whether each still holds, and the `verify`
skill and the method's implement step cite records and check them before the
work is called done.

## Acceptance criteria

Taken from ADR-1480, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show `run` writing one record per verb, an unresolved verb
   included, with its whole output, under a state directory the fixture sets,
   outside the repository.
2. Fixtures show `evidence` exiting 0 after a passing run, 1 after a file in
   the tree changes, 1 after a failing run, 1 after a verb that rewrote a
   file, 1 after going back to a tree that passed earlier, and 3 for a verb
   never run.
3. A fixture shows the recorded tree id equal to the tree of a commit that
   adds every file it counted.
4. A fixture shows a directory that isn't a git work tree recorded as bound to
   nothing, and `evidence` exiting 3 for it.
5. The `verify` skill and the implement step carry the order, the citation
   and the check, traced in the task's evidence.
6. Every requirement ADR-1480 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2270 record each result against its tree id, and report it
      with `meow-verbs evidence`
      closes: REQ-0146
      evidence: six fixtures seen failing first, and `meow-verbs evidence`
      current at tree 8c370dc87ab6, in #513.

- [x] T-002 TSK-2280 cite records and check them before calling work done, in
      `meow-verbs:verify` and the implement step
      closes: REQ-0148
      evidence: the skill's order, citation and check traced, and
      `meow-verbs evidence` current at tree 2d628eaf70ea, in #514.

## Verified

I checked this under #517 on `main` after #516, gathering the evidence there
rather than carrying it over from the tasks. `meow-verbs evidence format lint
test` exits 0, each current at tree `a050b2b80365`, which is the tree of
`main` after #516, and the six `Ledger` fixtures pass. Every criterion is met:

| Criterion                                                                                                               | Evidence on `main` after #516                                                                                       |
| ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 1. `run` writes a record per verb, an unresolved one included, with its whole output, outside the repository            | `Ledger.test_run_records_every_verb_outside_the_repository` passes                                                  |
| 2. `evidence` exits 0, 1 after an edit, a failure, a rewrite or a return to an earlier tree, and 3 for a verb never run | The three `Ledger` fixtures on staleness pass, and the one on a rewriting verb                                      |
| 3. The recorded tree id equals the tree of a commit adding every file                                                   | `Ledger.test_the_tree_id_is_the_tree_of_a_commit_adding_every_file` passes, and `a050b2b80365` is `main`'s own tree |
| 4. Outside git a record is bound to nothing and `evidence` exits 3                                                      | `Ledger.test_outside_git_a_record_is_bound_to_no_tree` passes                                                       |
| 5. The `verify` skill and the implement step carry the order, the citation and the check                                | Traced in TSK-2280: steps 2 and 5 and V1 to V5 of the skill, and step 4 and I7 of the implement step                |
| 6. Every requirement lands in exactly one closed task                                                                   | `paw show` derives REQ-0146 and REQ-0148 as closed, by TSK-2270 and TSK-2280                                        |

Each fixture was seen failing on the program before TSK-2270. The rule that
calls work done only on `evidence` exiting 0 is an instruction to the model,
as ADR-1480 says, so no program holds it.

### Documentation

TSK-2270 described the ledger and `meow-verbs evidence` on `meow-verbs`' page,
at 0.4.0. The `test` verb checked it, running `tools/check_docs.py`.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1480 addresses 2 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001. T-002 names the command
T-001 adds, so it follows it.

## Not covered

Nothing ADR-1480 addresses. Pruning the ledger and running a verb over part of
the work are left out, as ADR-1480 says.
