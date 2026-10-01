---
id: TSK-3390
artifact: task
status: approved
revised: 2026-09-30
epic: EPC-1910
closes: [REQ-0874]
issue: 729
projected: 323390752993
---

# End a run that changes its own terms, and deny an edit of a run's files

The runner checks the sha256 of `run.toml`, `prompt.md` and the work tree's
`.claude/settings.json` before and after each call and ends the run `tampered` on a mismatch. It names `meow-loop`'s
own directory with `--plugin-dir` on every call, so the unit's PreToolUse
hook, which this task adds, can deny an Edit or a Write under the runs
directory other than a run's progress file. Whether the hook fires in a `-p`
call is unobserved (EPC-1910, Not covered), and the hash check decides
either way. The condition runs the command
each verb resolved to at start, so an edit to `.meowpaw/profile.toml` can't
weaken it. One task, one branch, one pull
request, one review.

**Amended by ADR-2300.** Its verbs criterion is closed by the pull request's gate, since no run output is kept, and it names the checks unit `meow-checks`.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py` and counts
what it matched, failing on a count of zero where one was expected (EPC-1910
criterion 13).

1. Given a stand-in that edits `run.toml` on its first call, when the run
   ends, then the call log holds one call and `run.toml`'s ending is
   `tampered`; given a stand-in that edits `run.toml` and makes the verb pass
   in the same call, then it also ends `tampered` and not `finished`. Closed
   by: `Terms.test_tampered_run_toml` (REQ-0874, EPC-1910 criterion 3).
2. Given a stand-in that edits `prompt.md` on its first call, when the run
   ends, then it ends `tampered` after one call; given one that writes an
   allow rule into `.claude/settings.json`, then it also ends `tampered`
   after one call. Closed by: `Terms.test_tampered_prompt` and
   `Terms.test_tampered_settings` (REQ-0874, EPC-1910 criterion 3).
3. Given a run in progress, when `run.toml` is edited, then no bound
   changes, because the runner reads no bound from a file after start.
   Judgement, because the hash check ends the run before any later read of a
   changed bound could show, so no run observes it; the reviewer reads that
   the runner opens `run.toml` after start only to hash it and to write the
   ending.
4. Given the hook fed a PreToolUse Edit of a run's `run.toml`, a Write of its
   `prompt.md` and an Edit of its `log.jsonl`, when it runs, then it denies
   each; given an Edit of the run's `progress/progress.md`, and an Edit of a
   tracked file in the work tree, then it allows each. Closed by:
   `Hook.test_run_files_are_denied` (REQ-0874, EPC-1910 criterion 3).
5. Given the unit, when `hooks/hooks.json` is parsed, then it registers a
   PreToolUse entry whose matcher covers Edit and Write and whose command is
   the handler criterion 4 runs. Closed by: `Hook.test_hook_is_registered`.
6. Given a stand-in that rewrites `.meowpaw/profile.toml` on its first call so
   the `test` verb resolves to a command that always exits 0, while the verb
   resolved at start never passes, and `--iterations 2`, when the run ends,
   then it ends `ceiling` after two calls and not `finished`, and
   `run.toml` records the command resolved at start. Closed by:
   `Terms.test_profile_edit_changes_no_condition` (REQ-0874, EPC-1910
   criterion 3).
7. Given a run of at least two calls started with two `--plugin-dir` values,
   when the recorded argv are read, then each names `meow-loop`'s own
   directory first, followed by the two in the order given. Closed by:
   `Terms.test_own_unit_on_every_call` (EPC-1910 criterion 6, the
   `--plugin-dir` part).
8. Given a held verb command that edits `run.toml` and exits non-zero, when
   the run ends, then it ends `tampered` with no call in the call log, which
   only the check before the first call can produce. Closed by:
   `Terms.test_tampered_before_the_call` (REQ-0874).
9. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's pull request.

## What to do

Add the first check before each call and step 2 after it, over all three
hashes, as SPC-1201's section "The loop" states, and the unit's own `--plugin-dir`, as its section
"Each call" states. Add `hooks/hooks.json` and the hook's handler to the
unit's program, matching Edit and Write, and give the handler a path from the
PreToolUse input on standard input. Find the state directory as the ledger
does (SPC-1040), and resolve the path the input names, and the runs
directory, with every symbolic link before comparing, so `progress/../run.toml`
or a `/var` path under `/private/var` can't slip past. Hold each verb's command, which TSK-3350
resolves at start, in memory with the other terms, write it into `run.toml`,
and run that command at each evaluation of the condition, as SPC-1201's
section "The terms" states.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because a run gains an ending and the unit a hook.

Write the checks for criteria 1, 2 and 4 to 8 first, in a commit of their
own, and see them fail, because that commit is the evidence that the checks can fail (EPC-1910, Coverage).

## Depends on

TSK-3350, because this task checks the files that task writes.

## Evidence

`run` in `crates/meow/src/runloop.rs` seals the sha256 of the run's
`run.toml` and `prompt.md` and of the work tree's `.claude/settings.json` at
start, checks them before each call, after each call's log line, and before
it reports `ceiling`, and ends the run `tampered` on a change. `evaluate`
runs the command each verb resolved to at start, which `Context` holds and
`run.toml` records. `call` names the unit's own directory, found from the
program's path, with the first `--plugin-dir`. `meow-loop guard`, which
`plugins/meow-loop/hooks/hooks.json` runs on every Edit and Write, denies a
write under the runs directory other than a run's `progress/progress.md`,
after resolving every link and `..` in both paths.

Each criterion a program checks is closed by the check it names, in
`plugins/meow-loop/tests/test_loop.py`:

1. `Terms.test_tampered_run_toml`
2. `Terms.test_tampered_prompt` and `Terms.test_tampered_settings`
3. `Hook.test_run_files_are_denied`
4. `Hook.test_hook_is_registered`
5. `Terms.test_profile_edit_changes_no_condition`
6. `Terms.test_own_unit_on_every_call`
7. `Terms.test_tampered_before_the_call`

Criterion 3 rests on judgement, as the task says: after start the runner
opens `run.toml` only to hash it, in `Context::seal`, and to write the
ending, and it reads no bound from it. The checks failed first, in the commit
that holds them alone, where the `test` verb exited 1. That commit also
changes `Call.test_flags_and_prompt`, whose argv now names the unit's own
directory first. `format`, `lint`, `check`, `test` and `build` each pass on
the change's tree, as the pull request cites.

I made three choices the task leaves open. The hook's subcommand is
`meow-loop guard`, and with no binary for the machine the launcher lets
every write through, because a hook that fails blocks every Edit and Write.
A watched file that can't be read seals as unreadable, so it ends the run
only if it later reads differently. The run checks its terms once more
before it reports `ceiling`, so a change made by the last evaluation is
reported as `tampered`.

`meow-loop` goes to 0.5.0, and its README states the ending, the hook and
the held commands.

## Left alone

The hook's Bash rule, which TSK-3400 adds to the same hook. A script that
opens a run's file without an Edit or a Write, which the hook can't see and
the hash check catches.
