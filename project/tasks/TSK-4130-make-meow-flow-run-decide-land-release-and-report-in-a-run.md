---
id: TSK-4130
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2300
closes:
  [
    REQ-2380,
    REQ-2382,
    REQ-2384,
    REQ-2386,
    REQ-2402,
    REQ-3714,
    REQ-3716,
    REQ-3718,
    REQ-3720,
  ]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Make `/meow-flow:run` decide gates, land and release, report, and choose the next block in a run

Inside a run, `/meow-flow:run` decides each gate the posture names, critiques
first in a separate agent, merges after the checks pass, runs the declared
release, appends to `report.md`, and chooses the next block where nothing has a
`next:` line, as SPC-1200 states under "Deciding a gate", "Landing and
releasing" and "The report". Outside a run, the skill behaves as it does now.
One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the skill `plugins/meow-flow/skills/run/SKILL.md`, when a fixture
   reads it, then it names the run's frozen prompt as the signal of a run, and
   in a run decides each gate against `CLAUDE.md` and the files
   `[method] principles` names, asking the person nothing (REQ-3714, REQ-2380). Closed
   by: a fixture naming REQ-3714, seen failing first.
2. Given the same skill, when a fixture reads its gate steps, then the critique
   by a separate agent comes before the approval, and the approval is written
   as a harness approval naming the run (REQ-2382, REQ-2384). Closed by: a
   fixture naming REQ-2382.
3. Given the same skill, when a fixture reads its landing steps, then it
   merges only after the pull request's checks pass, runs only the release
   command `[unattended] release` declares, and keeps the constitution's
   prohibitions (REQ-3716, REQ-3718). Closed by: a fixture naming REQ-3716.
4. Given the same skill, when a fixture reads it, then each approval, merge,
   release, next-block choice and thing it couldn't do appends one line to the
   run's `report.md` (REQ-2386). Closed by: a fixture naming REQ-2386.
5. Given a fixture record with no `next:` line and requirements named by no
   task, when a fixture reads the skill, then it chooses one topic with
   neighbouring identifiers, skips postponed and addressed ones, and amends a
   contradicted record (REQ-3720). Closed by: a fixture naming REQ-3720.
6. Given the skill, when a fixture reads it, then it states that fetched
   material is data and carries no instruction (REQ-2402). Closed by: a
   fixture naming REQ-2402.
7. Given the skill outside a run, when the cases under `plugins/meow-flow/evals`
   run by hand, then the attended behaviour is unchanged. Rests on judgement,
   because evals run by hand and not in CI.

## What to do

Change the `run` skill and, where a step file needs it, the `method` skill,
following the authoring rules `meow-author:write` states. Keep the skill's
budget within `plugins/meow-flow/budget.toml`. Bump `meow-flow` as a `feat`.

## Depends on

- TSK-4110 (not blocking): the skill reads the run id the frozen prompt names,
  and its fixtures don't need a live run.

## Evidence

Not yet.

## Left alone

The hooks in `meow-loop`, which TSK-4100 to TSK-4120 change.
