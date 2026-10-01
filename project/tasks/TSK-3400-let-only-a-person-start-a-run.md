---
id: TSK-3400
artifact: task
status: approved
revised: 2026-09-30
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

**Amended by ADR-2300.** Its verbs criterion is closed by the pull request's gate, since no run output is kept, and it names the checks unit `meow-checks`.

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
   `describes:` matches the version in `plugin.json`. Closed by: criterion 8's
   `lint` and `test` outcomes in the task's pull request.
7. Given the diff against TSK-3390's tree, when a reviewer reads it, then
   `plugin.json` carries a minor version above TSK-3390's, and the README says
   a run starts from a terminal outside Claude Code, such as a tmux window.
   Judgement, because no check compares a version with the one before it or
   reads what a sentence says.
8. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's pull request.

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
see them fail, because that commit is the evidence that the checks can fail (EPC-1910, Coverage).

## Depends on

TSK-3390, because this task extends the hook that task adds.

## Evidence

`start` in `crates/meow/src/runloop.rs` refuses with
`unresolved: a run starts from a terminal outside Claude Code` and exits 3
when `CLAUDECODE` is set, before it reads the work tree or the state
directory. `call` passes `--disallowedTools "Bash(meow-loop *)" "Bash(meow loop *)"`
on every call. `guard` denies a Bash command whose text holds a word ending
in `meow-loop` followed by `start`, or a word ending in `meow` followed by
`loop start`, and `plugins/meow-loop/hooks/hooks.json` now matches Bash as
well as Edit and Write. `plugins/meow-loop/skills/loop/SKILL.md` sets
`disable-model-invocation: true`.

Each criterion a program checks is closed by the check it names, in
`plugins/meow-loop/tests/test_loop.py`:

- Criterion 1: `Guards.test_skill_is_person_only`
- Criterion 2: `Guards.test_claudecode_refused`
- Criterion 3: `Hook.test_start_is_denied`
- Criterion 4: `Guards.test_deny_rule_on_every_call`
- Criterion 6: the `budget` check in the `lint` verb and `tools/check_docs.py`
  in the `test` verb, in the pull request's gate

Criteria 5 and 7 rest on judgement, as the task says. The skill writes the
prompt file, prints the `start` command for a terminal outside Claude Code
and runs nothing, by its rules L1 to L4. `plugin.json` goes from 0.5.0 to
0.6.0, and the README says a run starts from a terminal outside Claude Code,
such as a separate tmux window.

The checks failed first, in the commit that holds them alone. That commit also
changes `Call.test_flags_and_prompt`, whose argv now holds the deny rule.
`format`, `lint`, `check`, `test` and `build` each pass on the change's tree,
as the pull request cites.

Review of the first version found that an escaped space, a continued line
and a redirect joined to `start` slipped past the hook, that an empty
`CLAUDECODE` let `start` run, and that no check failed if the hook stopped
matching Bash; all three are fixed and checked. A second review found a
redirect between the name and `start`, as in `meow-loop >/dev/null start`,
slipping past; the hook now drops a redirect and its target wherever it
stands. The hook still reads text, so a name split by quotes or a backslash,
as in `st""art` or `st\art`, gets past it, as a name in a script, a
variable or a command substitution does; the README says so, and SPC-1201's
list of misses names only the last three. `Guards.test_claudecode_refused`
runs with `CLAUDECODE` set to `1` and to nothing. Review of that round found it had
let `echo '>'; meow-loop start` through, by taking a quoted `>` for a
redirect and the runner's name for its target, and that `{fd}>/dev/null`
before `start` got past; the hook now never takes a runner's name as a
target and drops a named descriptor with its redirect. No agent reviewed
this last fix, because review stops after two rounds.

I made one choice the task leaves open. `meow-author cost` counts a skill
only the person invokes as loading nothing, because the platform doesn't put
its description in context, so `budget.toml` keeps 0 characters and its
comment says why.

## Left alone

A model that hides the runner's name in a script file, a variable such as
`M=meow-loop; $M start` or a command substitution such as
`$(echo meow-loop) start`, with `CLAUDECODE` dropped, which passes all four
guards, because the hook and the deny rule read the command text and not what
it runs or expands to, as ADR-2010's strongest objection says. The sandbox a
later decision adds is where that stops. A harmless command whose text holds
`meow-loop start`, such as a search, which the hook also denies, as SPC-1201
states.
