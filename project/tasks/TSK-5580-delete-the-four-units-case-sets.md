---
id: TSK-5580
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2830
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Delete the four units' case sets

The case sets that existed to be run by the loop leave the repository, with
the reviewer's coverage test and the terms check's exception for them.

## Acceptance criteria

1. Given `plugins/`, when `find` looks for the four `evals/` directories of
   `meow-core`, `meow-author`, `meow-flow` and `meow-prose`, then it matches
   nothing, and `plugins/meow-prose-gate/evals/hand_run.py` still exists.
   Closed by: `find` in the pull request.
2. Given the remaining checks, when the `test` stage runs, then the tests that
   read the deleted sets are gone and no remaining test names them. Closed
   by: the `test` stage's output in the pull request.

## What to do

Delete `plugins/meow-core/evals/` (cases, thresholds and the published
results), `plugins/meow-author/evals/`, `plugins/meow-flow/evals/` and
`plugins/meow-prose/evals/`. Delete `plugins/meow-prose/tests/test_rule_cases.py`,
the coverage check over the reviewer's cases. Remove the `/evals/` entry from
`tools/check_terms.py`.

## Depends on

- TSK-5560 (not blocking): the requirements go in the same pull request.

## Evidence

The four `evals/` directories are gone and
`plugins/meow-prose-gate/evals/hand_run.py` remains (criterion 1).
`plugins/meow-prose/tests/test_rule_cases.py` and the `/evals/` entry in
`tools/check_terms.py` are gone (criterion 2).

## Left alone

`plugins/meow-prose-gate/evals/hand_run.py`, the prose gate's pre-release
hand run, and the frozen records citing a measurement.
