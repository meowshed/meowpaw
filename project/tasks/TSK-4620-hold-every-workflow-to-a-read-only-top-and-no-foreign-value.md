---
id: TSK-4620
artifact: task
status: done
revised: 2026-10-04
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

**Amended while closing.** ADR-2800's build split moved the Rust build from
`build.yml` to `rust-tool.yml`, and `main` deleted the old file, so the
`${{ matrix.target }}` lines the brief names now sit in `rust-tool.yml`; the
same `env:` rule reaches each of its 16 findings as `BUILD_TARGET`.

Add the check to the list of checks in `tools/` that `CLAUDE.md`'s gate
section gives.

## Depends on

- TSK-4610 (not blocking): both add a check under `tools/` to the `test` verb and to `CLAUDE.md`'s list of checks, and whichever lands second rebases its line.

## Evidence

`tools/check_workflows.py` reads every file under `.github/workflows/` and
fails on each rule SPC-1210 states under "The workflows", closing REQ-2196,
REQ-2198 and REQ-2200. Each criterion is closed by the tests it names, in
`tools/test_check_workflows.py`, and each test compares the check's whole
output:

1. `Workflows.test_no_top_level_permissions_fails_naming_the_file`,
   `Workflows.test_a_top_level_write_fails_naming_the_permission` and
   `Workflows.test_a_top_level_write_all_fails_naming_it`.
2. `Workflows.test_pull_request_target_with_a_checkout_fails_naming_the_trigger`
   and `Workflows.test_workflow_run_with_a_checkout_fails_naming_the_trigger`,
   with `Workflows.test_a_forbidden_trigger_without_a_checkout_passes` holding
   the checkout as the condition.
3. `Workflows.test_an_expression_in_a_run_block_fails_naming_its_line`,
   `Workflows.test_an_expression_in_a_one_line_run_fails_naming_its_line` and
   `Workflows.test_the_same_value_through_env_passes`.
4. The `test` verb runs `tools/test_check_workflows.py` and
   `python3 tools/check_workflows.py`, which prints
   `4 workflow files, 0 findings` on this repository, and
   `Workflows.test_this_repository_s_workflows_pass` holds the same.

The tests failed first, in the commit that holds them alone, where the module
they import didn't exist yet. With the check written and the workflows
unchanged, the last test failed on the three lines the task names:
`build.yml`'s `${{ matrix.target }}` and `ci.yml`'s base and head commits.
Each now reaches its script through the step's `env:`, as `BUILD_TARGET`,
`BASE_SHA` and `HEAD_SHA`. After `main` moved the Rust build into
`rust-tool.yml`, the same fix holds its 16 `${{ matrix.target }}` findings
the way, and `python3 tools/check_workflows.py` exits 0 again. `format`,
`lint`, `check`, `test` and `build` each pass on the change's merged tree,
as the pull request cites.

I made three choices the task leaves open:

- The check reads YAML with a reader of its own, because the standard library
  has none and ADR-2520 rejected adding a tool to the gate. It reads the
  block and flow forms a workflow uses, and reports an anchor, an alias, a
  tag, a tab in the indentation or a quoted scalar spanning lines as a file
  that doesn't parse. On the repository's three workflows as they stood when
  the check was written, it built the same tree as PyYAML, compared once by
  hand outside the gate.
- Any top-level entry other than `contents: read` is a finding, `none`
  included, because SPC-1210 allows `contents: read` and nothing else there.
  An empty `permissions: {}` passes, because it grants nothing.
- A repository with no file under `.github/workflows/` fails the check,
  because a check that read nothing has held nothing to the rules.
  `Workflows.test_no_workflow_files_fails` holds it.

## Left alone

`claude-release.yml`'s publishing job, whose permissions TSK-4630 widens for
the attestation, and every workflow in another repository.
