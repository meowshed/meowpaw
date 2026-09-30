---
id: TSK-3700
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-2100
closes: [REQ-0314, REQ-2070, REQ-2078]
issue:
---

# Add the `skeptic` agent to `meow-flow`

`meow-flow` ships `agents/skeptic.md`, a read-only agent that tries to show
each requirement an epic's authorising record addresses is unmet, as ADR-2200
and SPC-1090 state it. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given `agents/skeptic.md`, when `meow-author check` runs on it, then it
   exits 0, and its front matter names `Read`, `Grep` and `Glob` as its tools
   and nothing else. Closed by: `meow-author check`'s exit status and output,
   and a fixture in `plugins/meow-flow/tests` that reads the tools line, seen
   failing first.
2. Given the agent's body, when a fixture reads it, then it finds the rule
   that everything the agent reads is data and no instruction in it is
   followed, both of ADR-2200's questions, the three states `refuted`,
   `not refuted` and `not judged` and no state named met, the rule that it
   attacks each refutation before reporting it (REQ-0314), the rule that a
   weak or tautological check is reported as a defect in the check
   (REQ-2070), the rule that such a check is rewritten and never supplemented
   (REQ-2078), and the label `record-reviewer` opens with. Closed by: a
   fixture naming REQ-0314, REQ-2070 and REQ-2078, seen failing first.
3. Given an epic whose closing check is a tautology, when the agent is
   dispatched on it, then it reports that requirement `refuted` and names the
   check's lines. Closed by: an evaluation case in
   `plugins/meow-flow/evals/`, run by hand on Sonnet 5 and Opus 5.5 with
   Opus 5.5 judging, at a threshold of 0.66 set in `thresholds.toml` before
   the first run.
4. Given a sound epic whose checks fail on a wrong implementation, when the
   agent is dispatched on it, then it reports no refutation. Closed by: a
   second evaluation case, run and judged as in criterion 3, at a threshold
   of 0.66 set before the first run.
5. Given the unit with the agent added, when `mise run budget` runs, then
   `meow-flow`'s load on every turn is at most 600 characters, and the
   agent's description is at most 100. Closed by: the gate, exit status 0,
   and a fixture on the description's length.
6. Given the agent's wording, when a reviewer reads it against ADR-2200's
   two questions, then each question reads as an attack the agent can carry
   out with read-only tools. Closed by: judgement, by the pull request's
   reviewer, because whether a prompt's instruction can be acted on is read,
   not matched.

## What to do

Write `plugins/meow-flow/agents/skeptic.md` in `record-reviewer`'s form and
to the prompt vocabulary `meow-author:write` sets. Its dispatch names the
epic's identifier and nothing else (REQ-0149). It reads the epic, the
authorising record, each requirement that record addresses, each task's
`## Evidence` and `## Cover`, the checks those sections name and the code the
checks exercise. For each refutation it names the input, how the verifier
confirms it (a command that writes nothing into the repository, or the lines
of a check that show it can't fail) and the fix.

Add the two evaluation cases beside the existing ones, with their thresholds
in `thresholds.toml` in the commit before the first run. Raise
`plugins/meow-flow/budget.toml` to 600 with a comment giving the measured
figure. Name the agent in `plugins/meow-flow/README.md`. Raise `meow-flow`'s
minor version in `plugin.json`, and make its README's `describes:` match.

## Depends on

Nothing. The agent is new, and nothing dispatches it until TSK-3710 lands.

## Evidence

Not yet.

## Left alone

`steps/verify.md` and `steps/review.md`, which TSK-3710 changes, and the
Scope and Boundary of SPC-1090, which keep their "not yet" until TSK-3710
makes the verify step dispatch the agent. `record-reviewer`, whose form this
agent follows and which it doesn't change.
