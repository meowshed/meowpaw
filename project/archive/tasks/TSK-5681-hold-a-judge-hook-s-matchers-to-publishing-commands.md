---
id: TSK-5681
artifact: task
status: done
revised: 2026-10-24
epic: EPC-2850
closes: [REQ-2798]
issue: 1120
projected: 031472b8ad53
tracked: 5f41dfbafeaf
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold a judge hook's matchers to publishing commands

The prose gate's hook asks a judge, and today its matchers name only commands that publish text. A test holds every such hook to that, so a broader matcher fails.

## Acceptance criteria

1. Given every `hooks.json` under `plugins/`, when a test reads it, then each hook whose command asks a judge carries an `if` matcher that names a command that publishes text or one of the four wrapper forms a publishing command can hide in, `git -C`, `git -c`, `gh -R` and `gh --repo`, and a hook that asks a judge on a bare `Bash` matcher fails the test naming the file (REQ-2798). Closed by: a test in `tools/` naming REQ-2798, seen failing against a copy of the gate's hooks with the `if` removed.
2. Given a command in a wrapper form that publishes no text, such as `git -C . status` or `gh -R owner/repo pr list`, when the gate's hook runs, then it calls no judge (REQ-2798). Closed by: a fixture in `plugins/meow-prose-gate/tests/test_gate.py` with a stub judge that records its calls, seen failing against a stub that is called.

## What to do

List the commands that publish text from the matchers the prose gate declares today, such as `git commit`, `gh pr create`, `gh pr edit`, `gh pr comment`, `gh issue create` and `gh release create`, and keep that list in the test with the reason. A hook asks a judge when its command is `meow-prose-gate check`.

## Depends on

Nothing.

## Evidence

Criterion 1 is closed by `JudgeHookMatchers` in `tools/test_judge_hook_matchers.py`, which
names REQ-2798: every hook that runs `meow-prose-gate check` carries an `if` matcher naming
a publishing command or one of the four wrapper forms. `test_a_judge_hook_with_no_matcher_fails`
was seen failing against a copy of the gate's hooks with the `if` removed.

Criterion 2 is closed by `test_a_wrapper_form_that_publishes_nothing_calls_no_judge` in
`plugins/meow-prose-gate/tests/test_gate.py`, which runs five wrapper-form commands that
publish nothing and sees the recording stub judge called zero times. The behaviour already
held, so the fixture was not seen failing, and `test_the_judge_reads_the_published_text`
shows the same stub records a call when a command does publish.

Every stage passed in pull request #1081.

## Left alone

The prose gate's rules, and any other hook that runs no judge.
