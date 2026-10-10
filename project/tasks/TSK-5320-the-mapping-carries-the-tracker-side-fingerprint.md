---
id: TSK-5320
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2810
closes: [REQ-4704]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The mapping carries the tracker side's fingerprint

The mapping on a task holds a fingerprint of the issue's title, body and state at the
last synchronisation, beside the record side's.

## Acceptance criteria

1. Given a projected task, when `meow-github project` finishes, then `projected:`
   holds a record fingerprint and a tracker fingerprint. Closed by: a test in
   `plugins/meow-github/tests/test_github.py`.
2. Given an existing mapping with the record fingerprint only, when `project`
   runs, then it adds the tracker fingerprint and changes nothing else. Closed
   by: a test in the same file.

## What to do

Extend the mapping and read it with both forms (expand, migrate, contract), and
name the release that drops the older form.

## Depends on

Nothing.

## Evidence

Pull request 886. The tests are in `plugins/meow-github/tests/test_github.py`,
class `Sync`, and in `plugins/meow-flow/tests/test_record.py`:

- Criterion 1: `test_project_writes_the_tracker_fingerprint_beside_the_record_s`.
- Criterion 2: `test_a_mapping_with_the_record_side_only_gains_the_tracker_side`.
- The frozen check allows the new field after approval:
  `test_a_task_may_gain_the_tracker_side_fingerprint`.

The mapping is read in both forms: a task with `projected:` alone is judged by
its title and body against `projected:`, and gains `tracked:` at the next
`project` or `sync`. The older single-field form is read until the second
release after 0.15.0 of `meow-github`, which drops that fallback. Two older
tests asserted that the front matter ends at `projected:`, and a commit of its
own makes them accept `tracked:` after it.

`meow-checks run format lint check test` passed on every stage with this
branch's binary, `test` in 155 seconds.

## Left alone

The request layer's limits and spacing (ADR-1810), which every write already
goes through.
