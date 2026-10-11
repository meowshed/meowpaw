---
id: ADR-2980
artifact: adr
status: done
revised: 2026-10-11
addresses: [REQ-2750, REQ-5100]
postpones:
  [
    REQ-1138,
    REQ-1140,
    REQ-1144,
    REQ-1146,
    REQ-1148,
    REQ-1666,
    REQ-1758,
    REQ-3184,
    REQ-3188,
    REQ-3214,
    REQ-3215,
    REQ-3524,
  ]
supersedes: ADR-1500
withdraws:
  [
    REQ-0153,
    REQ-0159,
    REQ-0160,
    REQ-0956,
    REQ-1078,
    REQ-1150,
    REQ-1759,
    REQ-3022,
    REQ-3024,
    REQ-3026,
    REQ-3028,
    REQ-3030,
    REQ-3032,
    REQ-3035,
    REQ-3036,
    REQ-3038,
    REQ-4124,
    REQ-4800,
    REQ-4802,
    REQ-4804,
  ]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2980. The harness measures no prompt

## Decision

Prompt evaluation — measuring a prompt's behaviour with model runs — is
removed whole, because the owner will redesign it in future.

The trees lose the runners and the case sets: `tools/loop.py`,
`tools/measure_gate.py` and their tests, the `eval` task in `mise.toml`, and
the `evals/` directories of `meow-core` (its cases, thresholds and the
published results of the runs already made), `meow-author`, `meow-flow` and
`meow-prose`. The prose reviewer's labelled set of 126 cases goes with them,
because its cases name `runs` and exist to be run by the loop that is gone,
and its coverage check `test_rule_cases.py` with it.

The record loses the twenty requirements that made a measurement obligatory
(REQ-0153, REQ-0159, REQ-0160, REQ-0956, REQ-1078, REQ-1150, REQ-1759,
REQ-3022, REQ-3024, REQ-3026, REQ-3028, REQ-3030, REQ-3032, REQ-3035,
REQ-3036, REQ-3038, REQ-4124, REQ-4800, REQ-4802, REQ-4804), and writes
REQ-2750 in REQ-1078's place: a move out of always-loaded material is
reviewed against behaviour, not asserted. SPC-1020 is rewritten to state the
absence, and SPC-1000, SPC-1010, SPC-1030 and SPC-1090 name review where they
named measurement.

This supersedes ADR-1500, whose subject was the loop's reporting, and amends
ADR-2840: its suite is gone, and the prohibition it carried stands as
REQ-5100 — no workflow under `.github/workflows/` runs a model call, names a
model credential, or runs the measurement of a prompt, and
`tools/check_workflows.py` keeps failing the gate on one.

Staying, because they are a different mechanism: the prose gate (ADR-2390,
ADR-2700) judges a text at review time, not a prompt in a suite, and keeps its
pre-release hand run (REQ-3752). The four verification kinds keep `evaluation`
as a declared value, because frozen records carry it (ADR-1140). The
evaluation-verified requirements still in force (REQ-1140, REQ-1144,
REQ-1146, REQ-1148, REQ-1666, REQ-1758, REQ-3184, REQ-3188, REQ-3214,
REQ-3215, REQ-3524, with REQ-1138 already postponed by ADR-1360) are
postponed by this decision until the redesign: their obligations stand, their
programme rests on review until then, and `paw status` names them under
Postponed.

After this decision no prompt in the harness is measured by a model run, and
the review before publishing is the one check on what the harness says. What
still doesn't work: a regression in what a prompt produces is seen by review
alone, not by a case set, until the redesign.

## Why

The suite's own record shows what it earned: the published results are five
runs from September, each resting on the owner's hand run because no workflow
may make a model call, and the one measurement the chain actually cited — a
move of explanation between files — was a gain on one case of four with the
arms overlapping (RES-0353). A system that costs money each run, is run by
hand five times in a month, and whose results no later decision cites, is
carried maintenance. The redesign will ask a different question of the same
machinery, so removing it whole and recording what the removal covers beats
half-keeping a runner nobody runs.

## Alternatives

| Option                             | Better at                       | Why it lost                                                                                   |
| ---------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------- |
| Keep the runners, run nothing      | A redesign that reuses the code | The runner's value was its case sets, and dead runners rot faster than deleted ones           |
| Keep the published results' dirs   | The history of the runs         | They are kept: the removal deletes the cases the results measured, not the results themselves |
| Keep the prose reviewer's case set | The reviewer's case coverage    | Its cases exist to be run by the loop, and a fixture for a runner that is gone is drift       |

## What it costs

The trees lose about 140 case files, two runners and a task. The reviewer's
rule coverage loses its program check, and a rule of the writing standard
added without a case is seen by review alone. The evaluation-verified
obligations rest on review until the redesign.

## What would reverse it

I would rebuild the machinery before the redesign if a review missed a
regression in what a prompt produces — a shipped rule change whose behaviour
a reader faulted and review had passed — because that is the failure the case
set existed to catch.

## Consequences

- The twenty requirements carry `status: withdrawn`, each naming this
  decision; REQ-2750 carries REQ-1078's surviving obligation, and REQ-5100
  carries the prohibition half of REQ-3035.
- SPC-1020 states the absence; SPC-1000, SPC-1010, SPC-1030, SPC-1090 name
  review; the `eval` task, the runners and the four case sets are deleted.
- ADR-1500 is superseded; ADR-2840 stands amended, its prohibition intact.

## How I will know it was realised

1. `find plugins tools -name "loop.py" -o -name "measure_gate.py"` matches
   nothing, and `mise.toml` names no `eval` task.
2. `plugins/meow-core/evals`, `plugins/meow-author/evals`,
   `plugins/meow-flow/evals` and `plugins/meow-prose/evals` don't exist, and
   `plugins/meow-prose-gate/evals/hand_run.py` still does.
3. The twenty requirements carry `status: withdrawn`, each naming ADR-2980,
   and REQ-2750 carries the reviewed move.
4. SPC-1020 states that no prompt is measured, the other living specs
   name review where they named measurement, and SPC-1210 names the
   workflow prohibition (REQ-5100).
5. The twelve postponed requirements are named under Postponed in `paw
status`, with this decision's condition.
6. Every requirement this decision addresses lands in exactly one closed
   task.

## What this does not settle

The redesign itself: what measures a prompt after it, which cases survive it,
and whether the prose gate's acceptance joins it. This decision only clears
the ground.
