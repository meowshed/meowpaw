---
id: TSK-1290
artifact: task
status: approved
revised: 2026-09-24
epic: EPC-1040
closes: [REQ-0158]
issue: 111
---

# Put the verbs in front of the model, and use them here

One task, one branch, one pull request, one review.

## What to do

Write `plugins/meow-verbs/skills/verify/SKILL.md` in the form SPC-1030 states,
with a description in the obligation form ADR-1050 gives: it MUST be used to
format, lint, type-check, test or build, in place of any command the model
would otherwise choose (REQ-0158). Its body runs `status` before the first
`run` in a session and reports each verb with the kind of result the program
gave. It names no language, tool or file extension.

Add the unit's `budget.toml`, its documentation page in `docs/` and its entry
in `.claude-plugin/marketplace.json` and `docs/README.md`.

Declare this repository's verbs in `.meowpaw/profile.toml`: `fmt` and `lint`
for the checks `mise run all` runs, and `test` for the record's own checks and
the fixtures TSK-1280 writes. Leave `typecheck` and `build` undeclared.

## Depends on

TSK-1280, because the skill calls the program and the profile is read by it.

## Evidence

Not yet. The task closes on this repository's `meow-verbs status` showing
`fmt`, `lint` and `test` resolved and `typecheck` and `build` undeclared, on
`meow-verbs run fmt lint test` passing here, and on one session where the
model, asked to run the tests, calls the program and not a command of its own.

## Left alone

Measuring the skill's routing on both models, which waits with the other
evaluations the owner postponed.
