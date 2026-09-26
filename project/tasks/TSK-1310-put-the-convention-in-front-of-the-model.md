---
id: TSK-1310
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1050
closes: [REQ-1304, REQ-2816]
issue: 127
---

# Put the convention in front of the model, and retire the temporary skill

One task, one branch, one pull request, one review.

## What to do

Write `plugins/meow-scm/skills/commit/SKILL.md` in the form SPC-1030 states,
with a description in the obligation form ADR-1050 gives: it MUST be loaded
before a commit message, a squash message or a pull request title is written.
Its body holds the two judgements: a subject in the imperative naming the
change and never the process (REQ-2816), and a body only where the reason
isn't evident, saying why and never a transcript (REQ-1304). It runs
`check-message` before a message is used and states the attribution ban on
its first screen. It names no version control tool.

Add the unit's budget, its documentation page, its entry in the marketplace
and in `docs/README.md`.

Declare this repository's convention under `[commits]` in
`.meowpaw/profile.toml`: the five types `CLAUDE.md` names with their release
meaning, a limit of 72 and the `Signed-off-by` trailer. Delete
`.claude/skills/commits/`, and point `CLAUDE.md`'s history principle at the
unit where it names the skill.

## Depends on

TSK-1300, because the skill runs the program and the convention is read by
it.

## Evidence

Not yet. The task closes on `check-message` run over the last ten commits on
`main`, on the temporary skill gone, and on one session where the model,
asked to write a commit message, loads `meow-scm:commit` and runs the check.

## Left alone

Measuring the skill's routing on both models, which waits with the other
evaluations the owner postponed.
