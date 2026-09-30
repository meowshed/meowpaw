---
id: TSK-3710
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-2100
closes: [REQ-3520, REQ-3522, REQ-3524]
issue:
---

# Make the verify step dispatch the skeptic and record each refutation it confirms

The verify step dispatches `meow-flow:skeptic` before it writes
`## Verified`, writes a draft defect for each refutation it confirms and a
`Refutation` paragraph for the outcome, and the review step judges each
refutation the verifier rejected, as ADR-2200 and SPC-1090 state. One task,
one branch, one pull request, one review.

## Acceptance criteria

1. Given `steps/verify.md`, when a fixture reads it, then it finds the
   dispatch of `meow-flow:skeptic` in a step numbered before the one that
   writes `## Verified`, the `Refutation` paragraph with each of its four
   parts, and the form that reads `not attempted` and names the cause where
   no agent could be dispatched (REQ-3522). Closed by: a fixture naming
   REQ-3522, seen failing first.
2. Given `steps/verify.md`, when a fixture reads rule V2, then it names the
   three things verification may write, `## Verified`, `checked-at` and a
   draft defect for each confirmed refutation, and rule V9 records the
   outcome in `## Verified` and `checked-at` in place of a stored status
   (REQ-3520). Closed by: a fixture naming REQ-3520, seen failing first.
3. Given `steps/verify.md`, when a fixture reads it, then it finds the draft
   defect from `paw template bug` with `violates`, `severity`, the
   reproduction's input and revision, an empty `## Triage` and no `enters`,
   and the rule that an open defect for the same requirement and cause is
   cited and not written twice (REQ-3524). Closed by: a fixture naming
   REQ-3524, seen failing first.
4. Given `steps/review.md`, when a fixture reads it, then it finds the rule
   that review judges each rejected refutation, returns the work to verify
   where it sides with the skeptic over lines the verifier read, and reports
   only a finding where the verifier's run showed no break. Closed by: a
   fixture, seen failing first.
5. Given a fixture record holding a draft defect with `violates` and
   `severity` set, a reproduction, an empty `## Triage` and no `enters`, when
   `paw check` runs on it, then it reports no finding on that defect. Closed
   by: a fixture in `plugins/meow-flow/tests`.
6. Given the verify step and a refutation it confirms, when the evaluation
   case runs, then the step writes a draft defect whose `violates` names the
   requirement, whose reproduction names the refutation's input and its
   revision, with a `severity`, `## Triage` empty and no `enters`. Closed by:
   an evaluation case in `plugins/meow-flow/evals/`, run by hand on Sonnet 5
   and Opus 5.5 with Opus 5.5 judging, at a threshold of 0.66 set in
   `thresholds.toml` before the first run.
7. Given the changed prompts, when `mise run prompts` and `mise run budget`
   run, then both pass. Closed by: the gate, exit status 0.

## What to do

Change `plugins/meow-flow/skills/method/steps/verify.md` and
`steps/review.md` as ADR-2200's sections on the verify step and the review
step decide, to the prompt vocabulary `meow-author:write` sets. The verify
step dispatches once per verification, runs or reads what each refutation
names, and writes nothing a refutation's command would write into the
repository. Where closing over a confirmed defect isn't right, it writes no
`## Verified` and stops at the defect's approval gate.

Remove the "not yet" markers from SPC-1090's Scope, Boundary and step tables
in the same change, because the specification states the present and the
verify step then dispatches the agent. Raise `meow-flow`'s minor version above
the one TSK-3700 landed with, and make its README's `describes:` match.

## Depends on

TSK-3700, because the verify step dispatches `meow-flow:skeptic`, and a
dispatch of an agent the unit doesn't ship fails in every session.

## Evidence

Not yet.

## Left alone

The epics verified before ADR-2200, whose `## Verified` sections keep their
wording, because the `Refutation` paragraph binds the step from now on and no
program checks old sections for it. `crates/meow/src/record.rs`, unless the
fixture in criterion 5 fails, because as its rules read, `paw check` asks
for `enters` only on a defect whose `## Triage` is written. The agent itself, which TSK-3700
owns.
