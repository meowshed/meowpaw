---
id: TSK-3400
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1910
closes: [REQ-0894]
issue: 730
projected: 11479fab2500
---

# Let only a person start a run

Four guards stop the model starting a run: the skill `meow-loop:loop` can't
be invoked by the model, `start` refuses when `CLAUDECODE` is set, the hook
denies a Bash command that runs `meow-loop start` or the native program's
`meow loop start`, and every call passes a deny rule on each name. One task, one branch, one pull request, one review.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py` and counts
what it matched, failing on a count of zero where one was expected (EPC-1910
criterion 13).

1. Given the unit, when `skills/loop/SKILL.md`'s front matter is parsed, then
   it holds `disable-model-invocation: true`. Closed by:
   `Guards.test_skill_is_person_only` (REQ-0894, EPC-1910 criterion 9).
2. Given `CLAUDECODE=1` in the environment, complete terms, and a state
   directory holding an earlier run, when `start` runs, then it exits 3,
   prints the refusal SPC-1201 gives, leaves the state directory exactly as
   it was, compared file by file before and after, and holds no lock
   afterwards. Closed by: `Guards.test_claudecode_refused` (REQ-0894, EPC-1910
   criterion 9).
3. Given the hook fed each of these PreToolUse Bash commands, when it runs,
   then it denies each: `meow-loop start ...`; the same after `cd x &&`; a
   path-qualified `${CLAUDE_PLUGIN_ROOT}/bin/meow-loop start ...`;
   `env -u CLAUDECODE meow-loop start ...`; `bash -c 'meow-loop start ...'`;
   and the native program's `<unit>/bin/<arch>/meow loop start ...`. Given
   `meow-loop --help` and `meow-loop status`, then it allows each. `start` is
   the word right after the one ending in `meow-loop`, or after `loop` where
   the word before ends in `meow`.
   Closed by: `Hook.test_start_is_denied` (REQ-0894, EPC-1910 criterion 9).
4. Given a run of at least two calls, when the recorded argv are read, then
   each holds `--disallowedTools` followed by `Bash(meow-loop *)` and
   `Bash(meow loop *)`. Closed by:
   `Guards.test_deny_rule_on_every_call` (REQ-0894, EPC-1910 criterion 6, the
   `--disallowedTools` part).
5. Given the skill invoked by a person, when its text is read, then it helps
   write the prompt file, prints the `start` command for the person to run in
   a terminal, and runs nothing.
   Judgement, because what a skill makes the model do is a model's behaviour,
   which no check in CI runs; the reviewer reads the skill against SPC-1201.
6. Given the unit's `budget.toml`, when the `budget` check in the `lint` verb
   runs, then it passes with the skill's description counted. Given the
   README, when `tools/check_docs.py` in the `test` verb runs, then its
   `describes:` matches the version in `plugin.json`. Closed by: the kept
   evidence of criterion 8's run.
7. Given the diff against TSK-3390's tree, when a reviewer reads it, then
   `plugin.json` carries a minor version above TSK-3390's, and the README says
   a run starts from a terminal outside Claude Code, such as a tmux window.
   Judgement, because no check compares a version with the one before it or
   reads what a sentence says.
8. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

Add the four guards as SPC-1201's section "Who starts a run" states. Write
the skill by the rules `meow-author:write` loads, because that skill holds
this repository's rules for a skill, and state its description's size in the
unit's `budget.toml`, because the `budget` check fails a unit that loads
more than it states (criterion 6). Add the Bash matcher to the hook TSK-3390
adds.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because the unit gains a skill and a refusal. The README
says a run starts from a terminal outside Claude Code, such as a tmux window.

Write the checks for criteria 1 to 4 first, in a commit of their own, and
see them fail, because the cover step keeps that failing run as the evidence
that the checks can fail (EPC-1910, Coverage).

## Depends on

TSK-3390, because this task extends the hook that task adds.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

A model that hides the runner's name in a script file, a variable such as
`M=meow-loop; $M start` or a command substitution such as
`$(echo meow-loop) start`, with `CLAUDECODE` dropped, which passes all four
guards, because the hook and the deny rule read the command text and not what
it runs or expands to, as ADR-2010's strongest objection says. The sandbox a
later decision adds is where that stops. A harmless command whose text holds
`meow-loop start`, such as a search, which the hook also denies, as SPC-1201
states.
