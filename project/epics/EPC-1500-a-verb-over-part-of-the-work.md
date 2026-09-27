---
id: EPC-1500
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1520
checked-at: "#543"
---

# A verb runs over part of the work only through a form the repository declares

Realises exactly one authorising record, ADR-1520. The epic is complete when
`meow-verbs run <verb> -- <targets>` runs a declared subset form, reports a
verb with none as `no subset form`, keeps subset records out of the whole
verb's evidence, and the `verify` skill runs a part only through the program.

## Acceptance criteria

Taken from ADR-1520, from its list of how I will know it was realised, before
the task below was written:

1. Fixtures show a declared subset form run with two targets, quoted, in place
   of `{targets}`; a verb with no subset form reported as `no subset form`,
   with nothing run and exit 3; a string value still resolving as before;
   `--` with no target refused; a `subset` without `{targets}` reported as a
   malformed declaration; a run naming a verb with a form and one without
   running the first, reporting the second and exiting 3; and `status` showing
   each verb's subset form or its absence.
2. A fixture shows `evidence test` ignoring a later subset record, printing it
   as `subset only`, and reporting the whole run's record.
3. The `verify` skill carries the subset rule, traced in the task's evidence,
   and `meow-author check` passes on it.
4. Every requirement ADR-1520 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2330 run a verb over part of the work through its declared
      form, in `meow-verbs` and its `verify` skill
      closes: REQ-0140, REQ-0142
      evidence: eight fixtures seen failing first, and the skill traced, in
      #541.

## Verified

I checked this under #543 on `main` after #542, gathering the evidence there
rather than carrying it over from the task. `meow-verbs evidence format lint
test` exits 0 on this change's own tree, as the pull request cites, and the
eight `Subset` fixtures pass. Every criterion is met:

| Criterion                                                                                                                                                                                                                                   | Evidence on `main` after #542                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 1. The subset form runs quoted targets; a verb with none is `no subset form`, runs nothing and exits 3; a string still resolves; an empty `--`, a form without `{targets}` and a mixed run each behave as decided; `status` shows each form | The seven `Subset` fixtures on `run` and `status` pass                                       |
| 2. `evidence test` ignores a later subset record and prints it as `subset only`                                                                                                                                                             | `Subset.test_a_subset_record_never_stands_for_the_whole_verb` passes                         |
| 3. The `verify` skill carries the subset rule, and `meow-author check` passes                                                                                                                                                               | Step 2 and V6 carry it, traced in TSK-2330; `meow-author check` reports 0 authoring failures |
| 4. Every requirement lands in exactly one closed task                                                                                                                                                                                       | `paw show` derives REQ-0140 and REQ-0142 as closed by TSK-2330                               |

### Documentation

TSK-2330 described the subset form on `meow-verbs`' page, at 0.5.0. The
`test` verb checked it, running `tools/check_docs.py`.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1520 addresses 2 requirements, and both land in the one task above,
because the program and the skill that names its new option change together.

## Not covered

Nothing ADR-1520 addresses. A pack's subset form and a check that a form
narrows the run are left out, as ADR-1520 says.
