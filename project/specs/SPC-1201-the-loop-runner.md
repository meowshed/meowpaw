---
id: SPC-1201
artifact: spec
status: live
revised: 2026-10-03
states:
  [
    REQ-0870,
    REQ-0872,
    REQ-0874,
    REQ-0876,
    REQ-0878,
    REQ-0882,
    REQ-0884,
    REQ-0886,
    REQ-0890,
    REQ-0892,
    REQ-0894,
    REQ-1240,
    REQ-2654,
    REQ-2656,
    REQ-2658,
    REQ-2660,
    REQ-2962,
    REQ-3700,
    REQ-3702,
    REQ-3704,
    REQ-3706,
    REQ-3708,
    REQ-3710,
    REQ-3712,
  ]
---

# The loop runner

## Scope

This covers `meow-loop`, the method-layer unit that runs the chain inside the
Claude Code session where a person starts it (REQ-3700, REQ-0870). A program in
three command hooks holds the run. It starts the run from the person's prompt,
decides after every turn whether the next iteration starts, and denies the
edits and commands that would let the model change or end its own run. Each
iteration is one `/meow-flow:run`, and the run repeats until the record holds
no open work, a bound is reached, the run is stuck or the person cancels it.
This states the start command, the run's files, the order of the checks, the
six endings, the guards, and each state the unit refuses (REQ-1240).

It doesn't cover what an unattended run may decide, merge and release, which
SPC-1200 states as the posture, nor the steps an iteration runs, which
the chain's specification states. A run that outlives its session, a sandbox and a network
allowlist have no decision yet, because ADR-2380 postpones the isolation
requirements, so no specification states them.

ADR-2380 decides this part.

## Boundary

| Surface                                          | What it is                                                            |
| ------------------------------------------------ | --------------------------------------------------------------------- |
| `plugins/meow-loop/skills/run/SKILL.md`          | `/meow-loop:run`, the start command, which only a person can invoke   |
| `plugins/meow-loop/hooks/hooks.json`             | The `UserPromptSubmit`, `Stop` and `PreToolUse` command hooks         |
| `plugins/meow-loop/bin/meow-loop`                | The unit's program, which each hook runs with its subcommand          |
| `plugins/meow-loop/README.md`                    | The unit's page                                                       |
| `plugins/meow-loop/.claude-plugin/plugin.json`   | The unit's manifest                                                   |
| `plugins/meow-loop/budget.toml`                  | What the unit loads on every turn: the skill's description            |
| `plugins/meow-loop/requires.toml`                | The Claude Code version the unit needs                                |
| `crates/meow`, feature `loop`                    | The unit's program, which compiles in the `record` and `profile` code |
| `<state>/meowpaw/runs/<work tree key>/<run id>/` | One run's directory, outside the work tree                            |

`build-units` builds the program as SPC-1080 states. The unit finds the state
directory as the evidence ledger does, as SPC-1040 states, and writes nothing
into the work tree, because run state belongs outside the repository
(REQ-3072).

Each hook exits 0 and speaks through its JSON output, because a hook that
fails stops nothing it was meant to stop. Where a hook can't read a state it
needs, it reports `unresolved: <what>` in its `systemMessage` and lets the
session go on without a run, because a run whose state can't be read can't be
held to its bounds.

## Behaviour

### Starting a run

A person starts a run by typing:

```text
/meow-loop:run --iterations <n> --hours <h> --tokens <t>
```

All three bounds are required, so the run's limits are stated before it starts
(REQ-0872, REQ-3708). `--iterations` is an integer of 1 or more, `--hours` a
number above 0 and `--tokens` an integer of 1 or more, each written in digits.
The completion condition isn't a flag, because it's fixed: no requirement and
no defect open in the record (REQ-3704).

The skill sets `disable-model-invocation: true`, so neither the model nor a
scheduled task can invoke it (REQ-0894). The `UserPromptSubmit` hook,
`meow-loop prompt`, starts the run. When the prompt submitted is the start
command, the hook:

1. refuses a start where a run is already active in this work tree, or where
   the posture SPC-1200 states is unresolved, reporting each as `unresolved`;
2. computes the open counts with the `record` code `paw status` uses, and reads
   the tree id with `ledger::tree_id`;
3. writes the run's directory and returns `additionalContext` naming the run's
   id, its bounds, its progress file and the first iteration's prompt.

The model can't start a run, because the start is the hook reading what the
person typed, and the `PreToolUse` hook denies any command that runs
`meow-loop` itself.

### A run's files

| File                   | Holds                                                                                                                               |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `run.toml`             | The session id, the three bounds, who started the run and when, the start's open counts and tree id, and the ending once it has one |
| `progress/progress.md` | The file each iteration reads and writes to carry what it has done, empty at start (REQ-0882)                                       |
| `log.jsonl`            | One line per iteration                                                                                                              |
| `report.md`            | What the run decided, merged, released and couldn't do, which SPC-1200 states                                                       |

Each line of `log.jsonl` holds the iteration number, the tree id before and
after it, the open counts after it, whether `progress.md` changed and the
tokens so far, so every iteration ends in a recorded state (REQ-2654,
REQ-0892). The unit keeps the newest 20 run directories of a work tree and
removes older ones when a run starts, and `meow-loop purge` removes them all
(REQ-2962).

### Each iteration

After every turn of the session the `Stop` hook, `meow-loop stop`, runs. With
no active run for the session's id it allows the stop and does nothing else.
With one, it appends the iteration's log line and then checks the run, in this
order, and the first check that holds ends the run with its ending:

1. The record has no requirement open and no defect open, where a postponed
   requirement doesn't count: `finished` (REQ-3704, REQ-3706, REQ-0884).
2. The iterations done reached `--iterations`: `ceiling` (REQ-0876).
3. The time since start reached `--hours`: `time`.
4. The tokens the transcript's usage fields sum to, plus the largest single
   iteration's tokens so far, exceed `--tokens`: `tokens`. Adding the largest
   iteration checks the budget before the next iteration starts (REQ-0878).
5. This iteration and the one before it both left the tree id, the open counts
   and `progress.md` unchanged: `stuck`, naming the counts (REQ-3710,
   REQ-0886).

`finished` comes first because a run whose work is done has met its condition
whichever bound it also reached. When no check holds, the hook blocks the stop
with `decision: "block"`, and its `reason` is the frozen prompt, the same bytes
on every iteration (REQ-3702):

```text
meow-loop run <run id>: run /meow-flow:run once and carry the chain to its next
stop. Read <progress file> first and update it before you finish. The record
decides when this run ends; you don't.
```

A program decides every ending from the record and the transcript, and nothing
the model printed changes it (REQ-3706, REQ-0876). The platform overrides a
`Stop` hook that blocks eight times in a row without the model calling a tool
(RES-0320, conclusion 9). An iteration that runs `/meow-flow:run` calls tools,
so a working run never meets that limit.

### Cancelling

A `Stop` hook doesn't fire when the person presses `Esc` (RES-0320,
conclusion 7). So the `UserPromptSubmit` hook ends an active run as
`cancelled` when the person submits any prompt other than the start command.
It records `cancelled_by = "person"` and the time in `run.toml`, and lets the
prompt through (REQ-3712, REQ-0890). Cancelling reverts nothing: the work an
iteration merged stays merged, and a branch it left open stays open
(REQ-2656).

### The guards

While a run is active, the `PreToolUse` hook, `meow-loop guard`, denies:

- an Edit or a Write of any path under `<state>/meowpaw/runs/` other than the
  run's `progress/progress.md` and `report.md`, so the model can't change its
  bounds or its ending (REQ-0874);
- the deny rules SPC-1200 derives from the posture;
- a Bash command whose text holds a word ending in `meow-loop`, or `meow`
  followed by `loop`, so the harness can't start, cancel or extend its own run
  (REQ-2660).

A deny holds in every permission mode (RES-0320, conclusion 8). The command
match reads the text and not what it expands to, so a name hidden in a script
file passes it. The `Stop` hook still decides the ending from the record, so a
hidden command can't make a run finish.

### Endings

Every run ends in exactly one of six endings, written into `run.toml` and
printed in the hook's `systemMessage` (REQ-2658):

| Ending      | When                                                   |
| ----------- | ------------------------------------------------------ |
| `finished`  | No requirement and no defect is open                   |
| `ceiling`   | The stated number of iterations ran                    |
| `time`      | The stated hours passed                                |
| `tokens`    | The next iteration could pass the stated token budget  |
| `stuck`     | Two iterations in a row changed nothing                |
| `cancelled` | The person submitted a prompt while the run was active |

A session that ends while a run is active leaves a run with no ending, which
reads as interrupted. The next start in that work tree replaces it, because
its session id no longer matches the session.

### `meow-loop start`

`meow-loop start`, the runner a person ran from a terminal outside Claude
Code, keeps working for one release. It first prints
`meow-loop start is deprecated: a run now lives in the session, so type /meow-loop:run there`,
because REQ-3004 announces a removal one release before it lands. The release
after removes it.

## Failure paths

Each refused start reports `unresolved: <what>` in the hook's `systemMessage`,
writes no run directory and lets the prompt through as an ordinary prompt:

| State                                          | Reported as                                                                     |
| ---------------------------------------------- | ------------------------------------------------------------------------------- |
| A bound is missing                             | `unresolved: /meow-loop:run needs --<bound>`, once for each                     |
| A bound isn't a number above 0 in digits       | `unresolved: --<bound> <value> is not a number above 0`                         |
| A run is already active in this work tree      | `unresolved: a run already holds this work tree`                                |
| The posture is unresolved                      | each line SPC-1200 gives                                                        |
| The record can't be read                       | `unresolved: the record can't be read: <reason>`                                |
| The current directory isn't in a git work tree | `unresolved: not a git work tree`                                               |
| `MEOWPAW_STATE=off`                            | `unresolved: state writing is off, and a run needs state`                       |
| No state directory can be named                | `unresolved: no state directory: set XDG_STATE_HOME, MEOWPAW_STATE_DIR or HOME` |
| The run's directory can't be written           | `unresolved: can't create a run in <directory>: <error>`                        |

During a run, a `Stop` hook that can't read `run.toml`, the record or the
transcript allows the stop, writes no ending and reports `unresolved: <what>`.
The run then reads as interrupted and never continues past a bound it couldn't
check. A `log.jsonl` line the hook can't write is reported the same way.
