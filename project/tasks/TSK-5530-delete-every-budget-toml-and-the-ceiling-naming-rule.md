---
id: TSK-5530
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2820
closes: [REQ-2748]
issue: 1104
projected: be5b773e5666
tracked: f5fd87ca6533
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Delete every unit's `budget.toml` and the ceiling-naming rule

All 16 Claude plugins and all 16 Pi packages lose their `budget.toml`, and the
documentation check stops requiring a description to name its unit's ceiling.
The 23 unit pages and the manifests that state a character count drop the
phrase.

## Acceptance criteria

1. Given `plugins/` and `packages/`, when `find` looks for `budget.toml`, then
   it matches nothing in either tree. Closed by: `find` in the pull request.
2. Given `tools/check_docs.py`, when its tests run, then the ceiling function
   and its two findings are gone, the rest of the check unchanged, and the
   documentation stage passes. Closed by: the updated
   `tools/test_check_docs.py` and `mise run lint`.

## What to do

Delete the 32 `budget.toml` files. Remove `ceiling` from `check_catalogue` in
`tools/check_docs.py` and its fixture line in `tools/test_check_docs.py`.
Strip the ceiling phrase from every `plugin.json` and package manifest
description and from the unit READMEs that state a character count. Update
`plugins/meow-author/README.md`, the `write` skill's step naming
`meow-author cost`, and `packages/meow-loop/README.md`.

## Depends on

- TSK-5510 (not blocking): the requirement this task makes true is written by
  the other task, which runs in parallel.

## Evidence

No `budget.toml` remains under `plugins/` or `packages/`; the 32 files are
deleted (criterion 1). `tools/check_docs.py` lost the `ceiling` function and
its two findings, `tools/test_check_docs.py` its ceiling case, its 29 tests
pass, and the check reports 19 pages, 0 documentation failures (criterion 2).
The unit pages and the manifests that stated a character count drop the
phrase, `plugins/meow-author/README.md` and its `write` skill drop
`meow-author cost`, and `packages/meow-loop/README.md` drops the budget
phrase.

## Left alone

The published evaluation results, and any frozen record citing a budget.
