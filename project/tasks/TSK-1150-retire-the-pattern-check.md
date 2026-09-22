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

Not yet. The task closes on `grep -rn check_prose` over the tree returning
nothing outside the record of this task, the seven remaining checks over the
record passing, `mise run all` passing, and `claude plugin list` showing
`meow-prose` enabled at user scope.

## Left alone

The other checks over the record. They read structure and never prose, and
REQ-3186 says nothing about them.
