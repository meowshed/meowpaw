---
id: EPC-1910
artifact: epic
status: approved
revised: 2026-09-30
realises: ADR-2010
---

# A runner outside the model repeats one frozen prompt in fresh sessions

Realises exactly one authorising record, ADR-2010. The epic is complete when
a person can run `meow-loop start` from a terminal with a prompt, a condition
on the verbs, a ceiling and a budget, and the run repeats the prompt in fresh
`claude -p` sessions until it ends in one of the six endings SPC-1201 states,
with every bound held in the runner's own process and the model unable to
start a run.

**Amended by ADR-2300.** ADR-2300 removed the cover step and the kept evidence: each task's tests land first in its own pull request, and that commit shows them failing.

## Acceptance criteria

Taken from ADR-2010, from its list of how I will know it was realised, before
the tasks below were written. Each check runs the runner with a stand-in
`claude` on the path, which records its argv and standard input to a call
log, prints a JSON result with a chosen `total_cost_usd`, and can edit a
file. Unless a criterion says otherwise, the stand-in changes a tracked file
on each call, so the idle rule doesn't end the run before the criterion's
count. Each check clears `CLAUDECODE` from the runner's environment, because
the gate often runs inside a Claude Code session.

1. A stand-in that makes the verb pass on its second call ends the run as
   `finished` after exactly two calls, and a condition that holds before the
   first call ends it as `finished` with none (REQ-0870).
2. `start` without the condition, the ceiling, the budget or
   `--permission-mode` exits 2 and leaves no run directory, and so does
   `start` with `--iterations 0`, with `--budget-usd 0`, or with
   `--permission-mode acceptEdits` or `bypassPermissions` (REQ-0872).
3. A stand-in that edits `run.toml` on its first call ends the run as
   `tampered` with one call in the log, and so does one that edits `run.toml`
   and makes the verb pass in the same call, and so does one that writes an
   allow rule into `.claude/settings.json`. A hook fixture shows an Edit of
   `run.toml` denied. A stand-in that rewrites `.meowpaw/profile.toml` so the
   verb resolves to a command that always exits 0 doesn't end the run
   `finished` (REQ-0874).
4. A stand-in whose result text says "ignore the ceiling, continue", with a
   ceiling of 3, makes exactly three calls, and the run ends as `ceiling` with
   exit status 1 (REQ-0876).
5. With a budget of 1.00, a stand-in costing 0.60 a call makes exactly one
   call and the run ends as `budget`. At 0.30 a call it makes exactly three,
   and the fourth is never started (REQ-0878).
6. Every recorded call carries byte-identical standard input and preamble,
   and no `--resume` or `--continue` (REQ-0880). Every recorded argv carries
   `--disallowedTools "Bash(meow-loop *)" "Bash(meow loop *)"` (REQ-0894) and
   names `meow-loop`'s
   own directory with `--plugin-dir` (REQ-0874).
7. The preamble names `progress/progress.md` by its absolute path, and each
   call's argv adds that directory with `--add-dir` and carries an allow rule
   for Edit and Write of that file (REQ-0882).
8. A stand-in that changes nothing makes exactly two calls and the run ends
   as `idle`, and one that writes only `progress.md` each call runs until the
   ceiling (REQ-0886).
9. The skill's front matter carries `disable-model-invocation: true`. `start`
   with `CLAUDECODE=1` exits 3 with no run directory, and a hook fixture shows
   a Bash `meow-loop start` and a Bash `meow loop start` denied (REQ-0894).
10. A stand-in that prints no result ends the run as `unmetered` after one
    call.
11. `start` exits 3 and leaves no run directory in each of five states:
    outside a git work tree, with `MEOWPAW_STATE=off`, with no `claude` on the
    path, with a named verb that resolves to no command, and while another
    process holds the work tree's lock.
12. After a run is killed part-way with SIGKILL, a new `start` in the same
    work tree takes the lock and runs.
13. Each check above counts what it matched, and a count of zero where one
    was expected fails it.
14. Every requirement ADR-2010 addresses lands in exactly one closed task.

Criterion 6 splits across three tasks, as the coverage below says, because
it checks one argv for three requirements. Criterion 13 is added here, as
EPC-1900 added it, because a check that matched nothing reports a pass with
nothing behind it.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass,
because a later pass is the one that gets skipped. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-3350 add `meow-loop` with `start`, which refuses incomplete
      terms, keeps a run's files under the state directory and the newest 20
      runs, holds the ceiling in its own
      process and ends `finished` when the verbs pass, in
      `plugins/meow-loop/` and a feature `loop` in `crates/meow`
      closes: REQ-0872

- [x] T-002 [P] TSK-3360 start every call from the same frozen prompt and
      preamble in a new session, and carry progress in the run's
      `progress/progress.md`
      closes: REQ-0880, REQ-0882
      evidence: the three checks in `Context` pass after failing first, and
      the five verbs pass. TSK-3360 carries the rest.
      depends: TSK-3350, because it changes the call that task makes

- [x] T-003 [P] TSK-3370 check the budget before each call from the spend so
      far and the largest call, and end the run `budget` or `unmetered`
      closes: REQ-0870, REQ-0876, REQ-0878
      evidence: the five checks in `Budget` pass after failing first, and the
      five verbs pass. TSK-3370 carries the rest.
      depends: TSK-3350, because it adds a check to the loop that task writes

- [ ] T-004 [P] TSK-3380 end the run `idle` after two iterations in a row
      that change neither the tree nor the progress file
      closes: REQ-0886
      depends: TSK-3350, because it reads the tree id and the progress file
      that task and the loop it writes record

- [ ] T-005 [P] TSK-3390 end the run `tampered` when `run.toml` or
      `prompt.md` changes, run the command each verb resolved to at start,
      name the unit's own directory on every call, and add the hook that
      denies an edit under the runs directory
      closes: REQ-0874
      depends: TSK-3350, because it checks the files that task writes

- [ ] T-006 TSK-3400 let only a person start a run: the skill a model can't
      invoke, the refusal under `CLAUDECODE`, the hook's Bash rule and the
      deny rule on every call
      closes: REQ-0894
      depends: TSK-3390, because it extends the hook that task adds

TSK-3360, TSK-3370, TSK-3380 and TSK-3390 can run in parallel once TSK-3350
has landed, because each adds one check or one argument to the loop and none
reads what another adds. They edit the same module, so the one that lands
later rebases onto the one before it and keeps the order SPC-1201's section
"The loop" states for the checks before and after each call. TSK-3400 waits
for TSK-3390 only.

## Coverage

ADR-2010 addresses nine requirements, and each lands in one task:

| Requirement | Task     | Why there                                                                    |
| ----------- | -------- | ---------------------------------------------------------------------------- |
| REQ-0870    | TSK-3370 | The run ends on its condition from TSK-3350 and on its budget from here      |
| REQ-0872    | TSK-3350 | `start` refuses to begin without the condition, the ceiling and the budget   |
| REQ-0874    | TSK-3390 | The hash check, the held commands and the hook stop a run changing its terms |
| REQ-0876    | TSK-3370 | The runner holds the ceiling from TSK-3350 and the budget from here          |
| REQ-0878    | TSK-3370 | The forecast before the call is the budget's check                           |
| REQ-0880    | TSK-3360 | The frozen prompt, the preamble and the fresh session make each start        |
| REQ-0882    | TSK-3360 | The progress file is what the preamble names and `--add-dir` reaches         |
| REQ-0886    | TSK-3380 | The idle rule is one check after each call                                   |
| REQ-0894    | TSK-3400 | The four guards stop the model starting a run                                |

The criteria split between the tasks as follows. TSK-3350 closes 1, 2, 4, 11
and 12. Criteria 1 and 4 cover only the condition half of REQ-0870 and the
ceiling half of REQ-0876, so both requirements close in TSK-3370, which cites
TSK-3350's evidence for those halves. TSK-3360 closes 7 and the standard input, preamble and session part
of 6. TSK-3370 closes 5 and 10. TSK-3380 closes 8. TSK-3390 closes 3 and the
`--plugin-dir` part of 6. TSK-3400 closes 9 and the `--disallowedTools` part
of 6. Criterion 13 binds every check in every task, and criterion 14 is this
epic's own.

The smallest set that tests the decision is TSK-3350, TSK-3370 and TSK-3390,
because together they show a bound held outside the model: the ceiling, the
budget before the call, and terms the model can't change. The cover step keeps
each task's failing run from the tree the task starts on. TSK-3350's failing
run is taken before `meow-loop` exists, so every one of its checks fails.
Each later task's failing run is taken on the tree of the task it depends
on, where the unit exists and the checks fail only on what the task adds.

## Not covered

- Six behaviours ADR-2010 records as unobserved, which a stand-in `claude`
  can't show: whether `--add-dir` and the runner's allow rule let the model
  write `progress.md` under `dontAsk`, what `--permission-prompts none` does
  in a call, which plugins a repository's own settings add, whether the
  unit's hook fires in a `-p` call, whether `CLAUDECODE` is set in a Bash call
  inside one, and whether the user's own instruction files and memory load.
  The first real run shows each, and no task claims them.
- The work tree's instruction files, skills, agents and `.mcp.json`, and the
  run's `log.jsonl`, which the runner doesn't hash, as ADR-2010 says.
- The files the condition's commands read in the work tree, such as the
  tests, which a call can change, because those files are the work a run is
  meant to change (ADR-2010).
- Completion from kept evidence or the plan's marks, and keeping a run inside
  one step (REQ-0884, REQ-0888), which ADR-2010 leaves to a later decision.
- Stopping a run, what an interrupted iteration leaves, and who stopped it
  (REQ-0890, REQ-0892, REQ-2654, REQ-2656, REQ-2658, REQ-2660).
- Reading the authority `meow-unattended plan` records, permission modes other
  than `dontAsk`, and removing tools beyond the deny rules on the runner (REQ-2372,
  REQ-2390).
- The sandbox, the network allowlist and credential removal (REQ-2396,
  REQ-2398, REQ-2400).
- The user-facing pages outside the unit, `docs/README.md`'s list of units
  among them, which the document step updates once every task is done, from
  ADR-2010's consequences.
