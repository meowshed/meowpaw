---
id: TSK-4620
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2420
closes: [REQ-2196, REQ-2198, REQ-2200]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold every workflow to a read-only top, no untrusted checkout and no expression in a `run:` line

`tools/check_workflows.py` reads every file under `.github/workflows/` and
fails on each rule SPC-1210 states under "The workflows", and this
repository's workflows pass it. One task, one branch, one pull request, one
review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture workflow with no top-level `permissions`, when the check
   runs, then it exits 1 naming the file, and given one whose top level grants
   `contents: write`, it names the permission (REQ-2196). Closed by: a test
   naming REQ-2196, seen failing first.
2. Given a fixture workflow triggered by `pull_request_target` that runs
   `actions/checkout`, when the check runs, then it exits 1 naming the
   trigger, and the same for `workflow_run` (REQ-2198). Closed by: a test
   naming REQ-2198.
3. Given a fixture workflow with `${{ github.event.issue.title }}` in a
   `run:` line, when the check runs, then it exits 1 naming the line, and
   given the same value passed through `env:`, it exits 0 (REQ-2200). Closed
   by: a test naming REQ-2200.
4. Given this repository's workflows, when the `test` verb runs, then the
   check passes. Closed by: the `test` verb's output in the pull request.

## What to do

Write the check and its tests, and add it to the `test` verb in
`.meowpaw/profile.toml`. Today `build.yml` has `${{ matrix.target }}` in a
`run:` line and `ci.yml` has `${{ github.event.pull_request.base.sha }}` and
`head.sha` in one, so move each through the step's `env:` in this change, or
the check fails the gate it joins. Read the workflow files as YAML, and don't
match the text, because a `run:` value spans several lines.

Add the check to the list of checks in `tools/` that `CLAUDE.md`'s gate
section gives.

## Depends on

- TSK-4610 (not blocking): both add a check under `tools/` to the `test` verb and to `CLAUDE.md`'s list of checks, and whichever lands second rebases its line.

## Evidence

Not yet.

## Left alone

`release.yml`'s publishing job, whose permissions TSK-4630 widens for the
attestation, and every workflow in another repository.
