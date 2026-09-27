---
id: TSK-2200
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1430
closes:
  [
    REQ-1110,
    REQ-1111,
    REQ-1112,
    REQ-1114,
    REQ-1120,
    REQ-1122,
    REQ-1124,
    REQ-1128,
    REQ-1142,
    REQ-1672,
    REQ-1678,
    REQ-2688,
  ]
issue: 485
projected: f5a6d085e3b8
---

# `meow-author check` holds the form of any repository's skills and agents

A new unit, `meow-author`, ships a check in the native tool's `author`
subcommand that holds the form SPC-1030 states, on this repository's units or
on the paths a repository gives it, and this repository's gate runs it in
place of `tools/check_prompts.py`. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given this repository, when `plugins/meow-author/bin/meow-author check`
   runs, then it exits 0. Closed by: its output, and the `lint` verb running
   it.
2. Given fixtures breaking each condition SPC-1030 lists for the check, when
   the check runs, then it exits 1 and names the file, the line and the
   failure. Closed by: fixtures naming their requirement, seen failing first.
3. Given a scratch repository with a skill under `.claude/skills/`, when
   `meow-author check .claude` runs, then it reads that skill. Closed by: a
   fixture naming REQ-1678.

## What to do

Create `plugins/meow-author/` with a manifest, a page, a budget, a
`requires.toml` and a launcher. Port `tools/check_prompts.py` to the native
tool's `author` subcommand behind its own feature, and add the checks SPC-1030
lists for descriptions, `commands/`, supporting files nobody names, paths
without the directory variable and procedures without a stopping point. State
where each of `meow-code:change`, `meow-code:debug` and `meow-scm:commit`
stops, so the check passes on them, and move those units by a patch. Make the
`prompts` task in `mise.toml` run the check, which puts it in the `lint` verb
and `mise run all`, and delete `tools/check_prompts.py`. Add the unit to the
catalogue.

## Depends on

Nothing. ADR-1450 is approved.

## Evidence

Not yet.

## Left alone

The skill, which TSK-2210 adds.
