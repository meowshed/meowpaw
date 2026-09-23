---
id: TSK-1150
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-3186, REQ-1671]
issue: 52
---

# Retire the pattern check over prose

One task, one branch, one pull request, one review.

## What to do

Delete `tools/check_prose.py` (REQ-3186). It reads words, and the defects that
reached `main` were shape, so it reported none of them. Confirm that no
artifact, task in `mise.toml` or workflow in `.github/` still names it, and
change any that does.

Move this repository onto the harness's own mechanism (REQ-1671). The standard
is held here by `meow-prose`, installed from this marketplace, and not by a
script beside the harness that no other repository runs.

Change `CLAUDE.md` so that it names `meow-prose` as the standard and stops
restating the standard's rules. Keep the constitution's reasons for holding a
standard at all, which belong to this repository.

On the owner's machine, delete `.claude/skills/technical-english/` once the
unit is installed. The directory is ignored, so the deletion produces no diff,
and the task records that it happened.

## Depends on

TSK-1120, because removing the pattern check before the reviewer ships would
leave this repository with nothing holding the standard.

## Evidence

`tools/check_prose.py` is deleted. No task in `mise.toml` and no workflow in
`.github/` named it. `CLAUDE.md` names `meow-prose` as the standard and its
reviewer as the review before publishing, and no longer restates the rules.

```text
$ grep -rn check_prose --exclude-dir=.git . | grep -v '^./project/'
(nothing)

$ mise run all
exit 0

$ claude plugin list
meow-prose@meowpaw  Version: 0.2.2  Scope: user  Status: enabled
```

Inside `project/`, the grep finds this task, EPC-1010, and approved records
that describe the check's history: ADR-1010, BUG-1010, BUG-1070 and RES-0224.
They are frozen, and they describe what happened, so they stay as they are.
The remaining checks over the record report no failure apart from a dangling
link in RES-0036 that predates this task.

`.claude/skills/technical-english/` was deleted on the owner's machine on
2026-09-23, after `meow-prose` was installed. The directory is ignored, so the
deletion shows in no diff. REQ-3186 and REQ-1671 are closed.

## Left alone

The other checks over the record. They read structure and never prose, and
REQ-3186 says nothing about them.
