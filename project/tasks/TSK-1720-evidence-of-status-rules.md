---
id: TSK-1720
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1210
closes:
  [
    REQ-0510,
    REQ-0516,
    REQ-0518,
    REQ-0519,
    REQ-0582,
    REQ-0586,
    REQ-0690,
    REQ-0694,
    REQ-0696,
    REQ-0716,
  ]
issue: 283
---

# Record the evidence for the status rules that already hold

Record the evidence for the status rules that already hold, as ADR-1210 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given each requirement this task closes, when its evidence is gathered at the current revision, then the task records a command and its output, or the file and line, that shows it holds. Closed by: the evidence table.

## What to do

Gather, at the current revision, the evidence that each requirement this task closes already holds, and record it: the stored status vocabulary in `lib/layout.toml`, the amendment path `check frozen` holds, the layout by kind and the `epic` field, the record under version control, the rule on marking a task in the commit that closes it, and `new` allocating after approval.

## Depends on

Nothing. ADR-1210 is approved.

## Evidence

Gathered at the revision this task's change lands on. Every requirement held
already, and nothing changed but this record.

| Requirement | Evidence                                                                                                                                                                                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| REQ-0510    | `git ls-files project` counts 1359 files and the tree holds 1359, and `status` prints no line saying the record is local: `grep -c` finds 0.                                                                                                                       |
| REQ-0516    | `plugins/meow-method/lib/layout.toml` ships in the unit and fixes the meaning of 8 kinds, each with its directory, prefix, statuses and sections; a repository declares only where the record lives.                                                               |
| REQ-0518    | `known()` in `crates/meow/src/record.rs` keys every artifact by the `id` in its front matter, and the kind comes from the directory the layout declares. The file name is only checked against the `id`, by `check identifiers`, and never read as the identifier. |
| REQ-0519    | A task names its epic in its own `epic` field, and the record divides by kind alone: `ls project` lists adrs bugs epics requirements research specs tasks.                                                                                                         |
| REQ-0582    | The layout's stored statuses are the decided ones only: approved, draft, live, rejected, superseded, withdrawn.                                                                                                                                                    |
| REQ-0586    | The fixture `test_an_observed_status_is_never_stored` shows `check front-matter` refusing `status: verified`, and TSK-1710 derives each requirement's state from the tasks closing it and stores none.                                                             |
| REQ-0690    | Step 5 of `steps/implement.md` marks the task in its epic in the same change, and `check coverage` now reports a task claiming done in an epic that leaves it unmarked.                                                                                            |
| REQ-0694    | M9 in the `method` skill writes a durable finding back into the artifact it belongs to, and step 2 of `steps/implement.md` routes a contradiction with an approved requirement to an amendment. TSK-1700 did so: ADR-1210 carries "Amended by EPC-1210".           |
| REQ-0696    | `check frozen` refuses an approved record changed without a line naming its authority; the fixtures `test_a_change_naming_its_authority_passes` and `test_a_verified_epic_is_frozen` pass, and `check frozen --base origin/main` reports `frozen: 0 findings`.     |
| REQ-0716    | REQ-1485 entered the approved set on 2026-09-26 with an identifier of its own, and `meow-method new requirement --topic artifacts` prints the next free identifier in the topic's block, which `show` resolves to nothing, so no file names it yet.                |

```text
$ python3 -m unittest plugins/meow-method/tests/test_record.py -k observed_status_is_never_stored -k named_for_its_identifier -k naming_its_authority -k verified_epic_is_frozen
Ran 4 tests in 0.398s
OK
```

## Left alone

Reading tests that name a requirement, which ADR-1210 leaves.
