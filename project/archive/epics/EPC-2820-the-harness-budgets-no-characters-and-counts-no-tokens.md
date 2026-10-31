---
id: EPC-2820
artifact: epic
status: done
revised: 2026-10-11
realises: ADR-2970
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The harness budgets no characters and counts no tokens

Realises exactly one authorising record, ADR-2970. The epic is complete when
no `budget.toml` exists in either tree, the gate holds no budget task, the
measurement suite prints no token count, the platform cap keeps a check in
`meow author check`, and the seven withdrawn requirements carry the decision's
name.

## Acceptance criteria

Taken from ADR-2970's list of how it will be known realised:

1. No `budget.toml` exists under `plugins/` or `packages/`, and `grep` over
   `plugins/`, `packages/` and `crates/meow/` for `permanent_characters`
   matches nothing (REQ-2748).
2. `mise.toml` names no `budget` task, and `.meowpaw/profile.toml`'s `lint`
   stage names none.
3. `meow author check` fails a fixture description over the cap of 1,536
   characters (REQ-1060).
4. `tools/loop.py` prints no `Tokens` column and no money cost, and its
   landing rule cites the difference alone.
5. REQ-1056, REQ-1057, REQ-1058, REQ-1072, REQ-1074, REQ-1676, REQ-3164 and
   REQ-4120 carry `status: withdrawn`, each naming ADR-2970, and REQ-5000 and
   REQ-3194 carry what survives them.
6. Every requirement ADR-2970 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [x] T-001 TSK-5510 withdraw the seven budget requirements and write the two replacements, in `project/requirements/`
      closes: REQ-2748, REQ-5000

- [x] T-002 [P] TSK-5520 remove `author cost` from the native tool, move the platform-cap check into `author check`, and drop the `budget` task from the gate, in `crates/meow/src/author.rs`, `mise.toml` and `.meowpaw/profile.toml`
      closes: REQ-1060
      depends: TSK-5510 (not blocking) - the requirement the cap check keeps is written by the other task

- [x] T-003 [P] TSK-5530 delete every unit's `budget.toml` in both trees, and stop requiring a description to name its ceiling, in `plugins/`, `packages/` and `tools/check_docs.py`
      closes: REQ-2748
      depends: TSK-5510 (not blocking) - the requirement is written by the other task

- [x] T-004 [P] TSK-5540 drop the token probe and the `Tokens` and cost columns from the measurement suite, in `tools/loop.py` and `project/specs/SPC-1020-measuring-the-harness.md`
      closes: none
      depends: nothing

- [x] T-005 TSK-5550 update the documentation and the specs that state a budget or a token count, and run the gate, across `project/specs/`, `CLAUDE.md` and the units' READMEs and skills
      closes: none
      depends: TSK-5520 (blocking) - the gate runs only once the budget task is gone from it

## Coverage

REQ-2748, REQ-5000 and REQ-3194, the requirements ADR-2970 writes, land in TSK-5510, with REQ-2748 closed again by TSK-5530, which makes the tree match it. REQ-1060 stays in force and moves its check in TSK-5520. The seven withdrawn requirements are named by TSK-5510, which writes their withdrawals; a withdrawal closes nothing, so they name no task's `closes`. TSK-5510 and TSK-5520 are the smallest set that tests the decision, because the files gone and the cap kept are its two checkable claims. TSK-5520, TSK-5530 and TSK-5540 run in parallel; TSK-5550 waits on the gate.

## Not covered

The published results under `plugins/meow-core/evals/results/`, which keep
their token and cost tables as the history of runs already made. The run
bounds and the code host's request budget, which ADR-2970 leaves in force.
The frozen records that cite a budget, such as TSK-4935 and ADR-1460, which
keep the rules they were approved under.
