---
id: TSK-5150
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2590
closes: [REQ-1420, REQ-1422]
issue: 1010
projected: 209d29cc2f3e
tracked: 026393f38749
---

# Require a fresh prompt for each attended irreversible action

Permission hooks and the method require one confirmation for each attended
push, merge, release, issue write or governance change.

## Acceptance criteria

1. Given each named operation in an attended fixture, when it is invoked,
   then the hook asks before allowing it. Closed by: hook fixtures for
   REQ-1420.
2. Given one allowed operation followed by another, when the second is
   invoked, then it asks again. Closed by: a two-invocation fixture for
   REQ-1422.
3. Given a read, a repository-local write or an unattended run, when the same
   hooks evaluate it, then this rule adds no prompt. Closed by: negative hook
   fixtures.

## What to do

Name the operations in the relevant hook units and method step, request no
reusable prefix for them, and keep ADR-2380's unattended path separate.

## Depends on

Nothing.

## Evidence

Two hook subcommands ask the person, once for each invocation, in a session
they attend: `meow-git irreversible-guard` before a push, and
`meow-github irreversible-guard` before a merge, a release, an issue or pull
request write, a `gh api` write outside the governance list, and
`meow-github project` or `sync` without `--check`. A governance change stays
with `governance-guard`, which already asked, so the person is asked once.
Both answer `ask` and nothing else, and keep no state, so an answer approves
no later call. A session is unattended in `dontAsk` or while a `meow-loop`
run holds it, which keeps ADR-2380's path separate. The method's rule M25
names the five operations and forbids asking for an approval that covers
the next one, in both trees. The Pi extensions ask through `ctx.ui.confirm`
for each call the model runs, and leave a call with no UI to the run's
posture.

The criteria are closed by `crates/meow/tests/irreversible.rs`, which runs
both guards and `governance-guard` on every fixture command. Each test failed
first, before either subcommand existed.

1. `each_irreversible_operation_asks_when_attended` closes criterion 1: a
   push in two forms, one through `git -C`, a merge, two release writes,
   two issue writes, a pull request write, two `gh api` writes,
   `meow-github project`, and two governance changes each get one `ask`
   from the guard of their unit, naming the operation and not the command
   (REQ-1420).
2. `a_second_invocation_asks_again` closes criterion 2: a push and a merge
   each ask on the first and on the second invocation, and the guards write
   nothing to the state directory (REQ-1422).
3. `a_read_or_a_local_write_asks_nothing` and
   `an_unattended_run_gains_no_prompt` close criterion 3: reads, a commit, a
   fetch and `project --check` get no prompt, and neither does a push, a
   merge, a release or an issue write in `dontAsk` or under an active
   `meow-loop` run.

`nothing_shipped_requests_a_reusable_permission` holds that no JSON file
under `plugins/` or `packages/` carries a `permissions.allow` rule for these
operations, and that both units register their guard. No such file exists
today, so the scan guards against a future one and found nothing to refuse.

`Guard.test_the_hook_runs_the_guard_on_bash`, in
`plugins/meow-github/tests/test_github.py`, asserted that the unit declares
one hook. It now names the two hooks, in a commit of its own that says why.

Whether Claude Code's prompt for a hook's `ask` offers a choice that approves
later calls is the platform's own prompt text, which the task leaves alone,
and only a session shows it.

Every stage passed in pull request #PR.

## Left alone

The platform's own prompt text and unattended authority.
