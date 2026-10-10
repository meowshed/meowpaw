---
id: TSK-5250
artifact: task
status: done
revised: 2026-10-10
realises: ADR-2840
closes: [REQ-3035]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Fail the gate on a workflow that makes a model call

`tools/check_workflows.py` reports a workflow that names the suite's `eval`
task or a model credential, so the by-hand rule of REQ-3035 holds without a
person reading each workflow.

## Acceptance criteria

1. Given a workflow whose step runs `mise run eval`, when `check_workflows`
   reads it, then it reports the file and the line of that step. Closed by:
   a test in `tools/test_check_workflows.py`.
2. Given a workflow that names `ANTHROPIC_API_KEY` or
   `CLAUDE_CODE_OAUTH_TOKEN`, as a key under `env:` or inside a value, when
   `check_workflows` reads it, then it reports the file and the line. Closed
   by: a test in `tools/test_check_workflows.py`.
3. Given this repository's workflows, when `check_workflows` runs, then it
   reports no model call. Closed by: the existing
   `test_this_repository_s_workflows_pass`.

## What to do

Add the rule to `tools/check_workflows.py` beside the rules it already holds,
and keep the list of names in one place in that file. SPC-1210 states the rule
under "The workflows", so the file's own docstring is the only prose the change
touches besides the tests.

## Depends on

Nothing.

## Evidence

Pull request 871. The tests are in `tools/test_check_workflows.py`:

- Criterion 1: `test_a_step_that_runs_the_suite_fails_naming_its_line`.
- Criterion 2: `test_a_model_credential_as_an_env_key_fails_naming_its_line` and
  `test_a_model_credential_inside_a_value_fails_naming_its_line`.
- Criterion 3: `test_this_repository_s_workflows_pass`, which ran unchanged.

`meow-checks run format lint check test build` passed on every verb at one
tree. The first `lint` run reported `unchecked` because the new worktree had
no `meow-licence` binary until `build` made it, and the second run passed.

## Left alone

The `eval` task in `mise.toml`, which stays out of `all`, and the documentation
pages that say a new model is a reason to run the suite (TSK-1210).
