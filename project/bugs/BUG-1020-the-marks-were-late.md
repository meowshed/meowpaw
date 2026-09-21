---
id: BUG-1020
artifact: bug
status: approved
severity: major
violates: REQ-0690
found: 2026-09-21
revised: 2026-09-21
unit: U-0001
issue: 18
---

# Two closed tasks stayed unmarked, and their records carry no evidence

## Reproduction

After `403e823` and `b228817` merged, at `21c7887`:

```bash
grep -n "T-001\|T-002" project/epics/EPC-1000-the-reply-shape-in-the-kernel.md
sed -n '/## Evidence/,/## Left alone/p' project/tasks/TSK-1010-the-kernel-plugin.md
```

The epic prints `[ ] T-001` and `[ ] T-002`. The task prints the evidence it
intends to gather, in the future tense, and none it gathered.

## What the system does

Both tasks are closed on the forge, their issues are closed, and the record
says neither has started. A reader with the repository and no access to the
pull requests cannot tell that any work happened.

## What it should do, and why

REQ-0690 says a stored status is updated in the same change that moves the work
it describes. EPC-1000 states the same rule in its own words: a task is marked
in the commit that advances it, never in a later pass. Neither merged commit
touched the epic.

REQ-0692 says a completed task records what closed it, the evidence and the
requirement identifiers it satisfied. The evidence existed in the bodies of #14
and #15 and never reached the records, and a pull request body is not the
record.

The reason the rule says never in a later pass is that a mark written later is
written from memory, and a status nobody can check is the unearned answer in
another form.

## Triage

A requirement in force covers it, so this enters at implementation. No
amendment: the records are approved, and filling in a field the template
declares is completing the record rather than changing what it says.

## Closed by

T-001 and T-002 marked `[x]` in EPC-1000, each with the command that closed it
and the revision it ran at. TSK-1010 and TSK-1020 carry the same evidence under
their own heading, TSK-1010 stating plainly that its evidence does not close
REQ-0932.

This correction is itself the later pass the rule forbids, and it is recorded
here rather than folded into unrelated work. The next three tasks mark
themselves in the commit that advances them.
