---
id: TSK-5291
artifact: task
status: approved
revised: 2026-10-10
epic: EPC-2770
closes: [REQ-4400, REQ-4402, REQ-4404, REQ-4410, REQ-4414]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The constitution, the method unit and its templates say it

`CLAUDE.md`, the method unit's implement step and its task template say that the
work of one epic is one pull request, whether it runs from the research or from
approved records, and that a defect or a decision realised by one task follows
the same rule.

## Acceptance criteria

1. Given the living and shipped files, when `git grep -n 'one task, one branch'`
   runs over them outside the frozen records, then it prints nothing. Closed by:
   that command's exit status, 1.
2. Given `CLAUDE.md`, when its layout table and its principle `own_method_first`
   are read, then both say an epic is one pull request. Closed by: a test in
   `plugins/meow-flow/tests/test_record.py`.
3. Given the implement step, when it is read, then it says that the tasks of an
   epic are implemented on one branch and that each is marked in the commit that
   completes it. Closed by: a test in the same file.

## What to do

Change `CLAUDE.md` (the layout row of a task and the principle `own_method_first`),
`plugins/meow-flow/templates/task.md`, the implement step and the mirrored
package copies. Leave the commit skill to TSK-5292.

## Depends on

- TSK-5290 (blocking): the text says a task approved on the branch is ready, and
  that has to work before the text says it.

## Evidence

Not yet.

## Left alone

The commit skill, the specifications SPC-1060 and SPC-1090, which this change
already states, and frozen records.
