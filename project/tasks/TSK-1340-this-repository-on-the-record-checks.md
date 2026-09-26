---
id: TSK-1340
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1070
closes: [REQ-1673]
issue: 145
---

# Move this repository onto the record checks the harness ships

One task, one branch, one pull request, one review.

## What to do

Declare `root = "project"` under `[record]` in `.meowpaw/profile.toml`, run
`meow-method check` from the `test` verb in place of `check_coverage.py`,
`check_front_matter.py`, `check_ids.py` and `check_research.py`, and delete
those four (REQ-1673). Change `CLAUDE.md`'s gate section to name the unit where
it names them. Add the unit's page, its entry in the marketplace and in
`docs/README.md`.

## Depends on

TSK-1330, because the verb runs the program and parity has to hold before the
scripts go.

## Evidence

Not yet. The task closes on the four scripts gone, `meow-verbs run test`
passing with `meow-method check` in it, and `grep` finding no reference to the
deleted scripts outside the record.

## Left alone

`tools/check_index.py`, `tools/check_links.py` and the checks over the
harness's own units.
