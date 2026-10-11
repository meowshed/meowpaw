---
id: RES-0353
artifact: research
status: approved
revised: 2026-10-11
elaborates: RES-0266
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# What prompt evaluation covers in the record and the trees

## Summary

Prompt evaluation — measuring a prompt's behaviour with model runs — is one
specification, SPC-1020, one runner, `tools/loop.py`, one classifier runner,
`tools/measure_gate.py`, four units' case sets under `evals/`, and the
requirements that make a measurement obligatory. This document lists every
place both the record and the trees carry it, so a decision to remove it names
what goes and what stays. It covers this repository only.

## The question

The owner asked to remove and reject everything related to prompt evaluation,
because it will be redesigned in future. What constrains it: the prose gate
(ADR-2390, ADR-2700) judges a text at review time and is the review flow's
mechanism, not the measurement of a prompt, so it stays; and the frozen
records whose verification names evaluation — routing descriptions, migration
coverage — keep the rules they were approved under (ADR-1140), with their
verification resting on review until the redesign.

## Method

Searched the record with `paw find evaluation`, `paw find eval` and `paw find
judge`, each exhaustive over 2,155 artifacts, and `grep` over
`project/requirements/` for `measurement`, `measured`, `case set`, `grader`,
`rubric` and `suite`. Searched the trees with `grep -rln` for `loop.py`,
`measure_gate` and `evals/` over `tools/`, `mise.toml`, `plugins/`,
`packages/`, `crates/` and `docs/`. Read each hit that carries behaviour or
states an obligation.

## Findings

- **The runner and its specification.** `SPC-1020` states the whole
  measurement system: the case set, the two arms, the judge, the thresholds,
  the regression rule and the loop. `tools/loop.py` runs it (delta and
  classifier modes), `tools/test_loop.py` tests it, and `tools/measure_gate.py`
  measures a blocking hook as a classifier. The `eval` task in `mise.toml`
  runs `loop.py` over every unit by hand, and no workflow does, which
  ADR-2840 settled.
- **Four units carry case sets.** `plugins/meow-core/evals/` (four reply-shape
  cases, thresholds, and the published results of five runs), `plugins/meow-author/evals/`
  (one case), `plugins/meow-flow/evals/` (route cases) and
  `plugins/meow-prose/evals/` (126 labelled cases for the prose reviewer's
  prompt, with thresholds). Each case names `runs` and tags, so all four exist
  to be run by the loop.
- **The prose reviewer's case set is prompt evaluation.** Its 126 cases
  measure the reviewer's prompt by model runs, and the static check over rule
  coverage (`plugins/meow-prose/tests/test_rule_cases.py`) exists to keep the
  set complete for those runs. With the loop gone the set is a fixture for a
  runner that no longer exists, so the set and its coverage requirements go
  with it.
- **The requirements that state a measurement MUST run.** Twenty requirements
  make prompt evaluation obligatory: the pair on what an evaluation states and
  reports, the shape's and the routing's measurements, the measurable change to
  harness material, the baseline, judge, run-count, threshold, regression and
  shuffle rules, the by-hand and re-run rules for the suite, the suites' Pi
  deferral, and the reviewer's case set. Each carries `verification:
  evaluation` or cites the suite directly.
- **What stays.** The prose gate keeps its runtime judge and its pre-release
  hand run, because it is the review flow's enforcement, not a measurement of
  a prompt. The four verification kinds keep `evaluation` as a declared value,
  because frozen records carry it. The status report's line on how much rests
  on judgement reports the record's weights and doesn't run anything. No workflow under `.github/workflows/` names the suite, so nothing
  there changes.
- **The record's other uses of the word.** SPC-1090's migration paragraph and
  the status report's line on how much rests on judgement use "evaluation" for
  things that aren't the suite; neither changes.

## Conclusions

1. The harness runs no measurement of a prompt, and keeps no case set whose
   runner is gone.
2. The specification that stated the measurement states its absence, and the
   living specifications name review where they named measurement.
3. The requirements that made a measurement obligatory are withdrawn, naming
   the decision; one requirement replaces the obligation to show a move out of
   always-loaded material safe, held by review rather than by a run.
4. The prose gate and the four verification kinds stand, and a frozen
   record's evaluation-verified obligation rests on review until the
   redesign.

## Sources

- `project/specs/SPC-1020-measuring-the-harness.md` at `6868f6a8`, 2026-10-11 - the measurement system's statement.
- `tools/loop.py`, `tools/measure_gate.py`, `tools/test_loop.py` at `6868f6a8`, 2026-10-11 - the runners and their tests.
- `plugins/meow-core/evals/`, `plugins/meow-author/evals/`, `plugins/meow-flow/evals/`, `plugins/meow-prose/evals/` at `6868f6a8`, 2026-10-11 - the case sets, thresholds and published results.
- `mise.toml` at `6868f6a8`, 2026-10-11 - the `eval` task.
- `paw find evaluation`, `paw find eval`, `paw find judge`, 2026-10-11, exhaustive - the requirements named above.
