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

The skill `meow-scm:commit` carries its description in the obligation form
ADR-1050 gives, at 263 characters, states the attribution ban on its first
screen, and names no version control tool. The unit's budget is 380, its page
is `docs/meow-scm.md`, and it is in the marketplace at 0.2.0. This repository
declares its convention under `[commits]`, and `CLAUDE.md` tells an author to
run the check before a message is used.

Run over the last ten commits on `main`, the check failed exactly one:

```text
e51ac8a exit 1  spec: verify the writing standard and close it with one ...
     line 1: subject length: 78 characters, over the limit of 72
```

That is #119, a real break of the convention: its subject was written before
the pull request's number was added to it. The other nine passed.

`.claude/skills/commits/` was deleted on the owner's machine on 2026-09-26.
The directory is ignored, so the deletion shows in no diff.

Asked on Sonnet 5, with this unit alone installed, to write the commit message
for a staged change, the model loaded `meow-scm:commit`, ran `meow-scm
convention`, passed its message to `meow-scm check-message` and used it only
once it passed. It left out a co-author trailer its own session instructions
asked for, saying the skill forbids crediting a tool. REQ-1304 and REQ-2816
are closed.

## Left alone

Measuring the skill's routing on both models, which waits with the other
evaluations the owner postponed.
