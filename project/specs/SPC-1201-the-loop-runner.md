---
id: SPC-1201
artifact: spec
status: live
revised: 2026-09-29
checked-at:
states:
  [
    REQ-0870,
    REQ-0872,
    REQ-0874,
    REQ-0876,
    REQ-0878,
    REQ-0880,
    REQ-0882,
    REQ-0886,
    REQ-0894,
  ]
---

# The loop runner

## Scope

This covers `meow-loop`, the method-layer unit that runs one frozen prompt
again and again in fresh `claude -p` sessions until a condition on the verbs
holds or a bound ends the run. It states the command a person runs, the terms
it takes, the files a run keeps, each call it makes, the order of its checks,
the six endings, the guards that stop the model starting a run, and each state
it refuses.

It doesn't cover the authority an unattended run is planned from, which
SPC-1200 states, and the runner doesn't read that plan. Stopping a run by any
means other than the terminal's interrupt, completion from kept evidence or
the plan's marks, the sandbox, the network allowlist and credential removal
have no decision yet, so no specification states them. The runner also
doesn't guard the files the condition's commands read in the work tree, such
as a task runner's configuration or the tests, because those files are the
work a run is meant to change. Neither a call nor an evaluation of the
condition has a time limit, so a run's wall time is bounded only by its
ceiling, and a call that hangs holds the run and its lock until a person
interrupts it, because ADR-2010 chose no timeout.

ADR-2010 decides this part and EPC-1910 realises it.

## Boundary

| Surface                                          | What it is                                                        |
| ------------------------------------------------ | ----------------------------------------------------------------- |
| `plugins/meow-loop/bin/meow-loop start`          | Starts a run in the current work tree and holds it until it ends  |
| `plugins/meow-loop/skills/loop/SKILL.md`         | A skill only a person invokes, which helps write the prompt file  |
| `plugins/meow-loop/hooks/hooks.json`             | A PreToolUse hook on Bash, Edit and Write                         |
| `plugins/meow-loop/README.md`                    | The unit's page                                                   |
| `plugins/meow-loop/.claude-plugin/plugin.json`   | The unit's manifest, which Claude Code loads it from              |
| `plugins/meow-loop/budget.toml`                  | What the unit loads on every turn: the skill's description        |
| `plugins/meow-loop/requires.toml`                | The Claude Code version the unit needs, 2.1.280                   |
| `.claude-plugin/marketplace.json`                | The unit's entry                                                  |
| `crates/meow`, feature `loop`                    | The unit's program, which compiles in the `verbs` feature's code  |
| `<state>/meowpaw/runs/<work tree key>/`          | Where a work tree's runs and its lock live, outside the work tree |
| `<state>/meowpaw/runs/<work tree key>/<run id>/` | One run's directory                                               |

`build-units` builds the program as SPC-1080 states. The runner finds the
state directory as the evidence ledger does, as SPC-1040 states:
`MEOWPAW_STATE_DIR` replaces `<state>/meowpaw`, and the work tree key is the
one the ledger files a work tree under, a hash of the work tree's absolute
path with every symbolic link resolved.

The runner writes nothing into the work tree, because run state belongs
outside the repository (REQ-3072) and a write there would change the tree id
the idle rule reads. Every file it writes is under the state directory.

Exit status is 0 for a run that ended `finished`, 1 for a run that ended any
other way, 2 for a usage error, and 3 for a state the runner can't read past,
at start or during a run. A run interrupted by a signal exits with the status
the shell reports for that signal. A 1 answers whether the condition held,
and the ending printed on the last line says why it didn't. A 2 means the
command as typed can't start a run, so the person corrects the command. A 3
means the command is right but the machine or the work tree isn't ready, so
the person repairs the environment; a start from inside Claude Code is a 3,
because the same command starts from a terminal outside it (ADR-2010).

## Behaviour

### The terms

A person starts a run from a terminal outside Claude Code:

```text
meow-loop start --prompt <file> --until verbs=<verb>[,<verb>...]
                --iterations <n> --budget-usd <amount>
                --permission-mode dontAsk [--allowed-tools <rule>]...
                [--plugin-dir <dir>]...
```

`--prompt`, `--until`, `--iterations`, `--budget-usd` and `--permission-mode`
are each required, so the condition and both bounds are stated before a run
starts (REQ-0872), and no call inherits the platform's default mode.
`--iterations` is an integer of 1 or more, and `--budget-usd` a number above
0, in US dollars. `--permission-mode` accepts `dontAsk` alone, because it's
the one mode RES-0300 saw run a call. `bypassPermissions` is refused, because
a run would then cross every permission the person hasn't declared
(ADR-2010).
`--allowed-tools` and `--plugin-dir` repeat, and each value passes to every
call unchanged.

The one condition kind is `verbs=`, naming one or more of the five verbs. At
start the runner resolves each named verb to its command and holds the
command in memory with the other terms, because `.meowpaw/profile.toml` is in
the work tree and a call could otherwise point a verb at a command that
always exits 0 (REQ-0874). The condition holds when every held command exits
0 at the current tree (REQ-0870). The runner evaluates it itself, through the
`verbs` feature's code, and runs no other unit's program to do it, because a
unit's file runs no path outside its own directory, which the `standalone`
check enforces, and so the unit works whether or not `meow-verbs` is
installed.

### A run's files

`start` works in this order: it checks the command line, then checks each
state it can't read past, taking the work tree's lock as the last of those
checks, then removes old runs, then writes the run's directory, named by a
run id unique within the work tree. A refused start therefore creates no run
directory and removes none. The only refusal that reaches the lock is a lock
another process holds, and that lock's file already exists, so a refused
start writes nothing. The directory `runs/<work tree key>/` and its lock
file, which hold no run, stay after a run ends. The lock is an advisory lock the operating system holds on an
open file in `<state>/meowpaw/runs/<work tree key>/` for the runner's
process, so it ends whenever the process ends, and an interrupted run leaves
no lock behind. One run holds a work tree at a time, because a second run's
edits would change the tree id the first reads for its condition and its
idle rule.

The run's directory holds four files:

| File                   | Holds                                                                                                                                                                                                                                                                                                      |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run.toml`             | The prompt's sha256, the condition and each verb's resolved command, the ceiling, the budget, the permission mode, each allowed rule, each plugin directory, the sha256 of `.claude/settings.json` or its absence, who started the run and when, the repository's identity, and the ending once it has one |
| `prompt.md`            | A copy of the prompt file as it was at start                                                                                                                                                                                                                                                               |
| `progress/progress.md` | The file the model reads and writes to carry what it has done across iterations, empty at start (REQ-0882)                                                                                                                                                                                                 |
| `log.jsonl`            | One line per iteration                                                                                                                                                                                                                                                                                     |

Each line of `log.jsonl` holds the iteration number, the tree id before and
after the call, whether `progress.md` changed, the call's `total_cost_usd`,
the sum so far, the count of `permission_denials`, the call's exit status,
and the condition's result where the runner evaluated one. A tree the runner
can't identify is logged as `unidentified`, and a call that reported no cost
has `total_cost_usd` set to null. The tree id before a call is taken after the
previous evaluation of the condition, so a verb that writes to the tree, such
as `format`, never counts as a change the next call made.

Before it first evaluates the condition, the runner records in its own memory the sha256 of
`run.toml`, of `prompt.md` and of the work tree's `.claude/settings.json`, or
that the settings file is absent. It hashes the settings file because
`--setting-sources project` makes every call reread it, and a call that added
an allow rule, a hook or an enabled plugin there would give the next call
authority the person never typed (ADR-2010). `run.toml` records the settings
file's sha256 too. A run whose `run.toml` has no ending was
interrupted, and the last line of its log says how far it got.

When a run starts, the runner keeps the newest 20 run directories of the work
tree, counting the new run, removes the older ones and prints the id of each
it removed. Run state needs a bounded retention (REQ-2962), and 20 is the
default ADR-2010 chose.

### The loop

The runner reads the terms once, at start, and holds them in its own process
until the run ends. It reads no bound back from a file after start, so an
edit to `run.toml` changes no bound (REQ-0874).

Before the first call the runner evaluates the condition. If it holds, the
run ends `finished` with no call.

Before each call the runner checks, in this order, and the first check that
fails ends the run. The order decides which ending is reported when two
checks fail at once, and a changed term comes first, because a run that
tried to change its terms has to be reported as that whichever bound it also
reached:

1. The sha256 of `run.toml`, of `prompt.md` and of `.claude/settings.json`
   match the recorded values, or the run ends `tampered` (REQ-0874).
2. The iterations done are fewer than the ceiling, or the run ends `ceiling`
   (REQ-0876).
3. The spend so far plus the largest single call's spend so far is at most the
   budget, or the run ends `budget` (REQ-0878). Before the first call both
   terms are 0, so the first call starts.

When all three pass, the runner starts the call, whatever the prompt, the
progress file or the previous call's output says (REQ-0876).

After each call, the runner, in this order:

1. appends the call's line to `log.jsonl`;
2. checks the three sha256 values again, and ends the run `tampered` on a
   mismatch, so a call that changes `run.toml` and also makes the verbs pass
   never ends `finished`;
3. ends the run `unmetered` if the call printed no JSON result, or a result
   without `total_cost_usd`, and otherwise adds that cost to the spend;
4. ends the run `budget` if the result's subtype is `error_max_budget_usd`;
5. evaluates the condition if the tree id changed or couldn't be identified,
   and ends the run `finished` if it holds, because an unchanged tree would
   repeat the last result;
6. ends the run `idle` if this iteration and the one before it both changed
   nothing (REQ-0886).

Steps 3 and 4 come before the condition, because a call whose spend can't be
counted, or that passed its own cap, has broken a bound the person stated,
and a broken bound is reported before a success. So a call that prints no
cost and also makes the verbs pass ends `unmetered`, and its log line holds
no condition result.

A call that exits non-zero, or prints a result with any other error subtype,
counts as an iteration, and the ceiling and the budget bound it like any
other.

An iteration changes nothing when the work tree's id, as `ledger::tree_id`
computes it, and the sha256 of `progress/progress.md` are both the same after
the call as before it. An iteration whose tree the runner can't identify, such
as one with a dirty submodule, counts as a change.

### Each call

Each call is one process, with the prompt's bytes on its standard input from
the runner's memory:

```text
claude -p --output-format json --no-session-persistence
       --setting-sources project --plugin-dir <meow-loop> --plugin-dir <dir>...
       --permission-mode dontAsk --allowedTools <rule>...
       --allowedTools <Edit and Write of <run>/progress/progress.md>
       --permission-prompts none
       --add-dir <run>/progress --max-budget-usd <budget left>
       --disallowedTools "Bash(meow-loop *)" "Bash(meow loop *)"
       --append-system-prompt <the fixed preamble>
```

A call passes no `--resume` and no `--continue`, so each iteration is a new
session. `--output-format json` is there because the runner reads the cost
and the subtype from the result. `--no-session-persistence` is there because
nothing resumes a call, so a saved session would only fill the person's
session list. `--setting-sources project` keeps the person's installed
plugins out, so the harness a call loads is the directories the runner
names. `--permission-prompts none` is there because nobody is present to
answer a prompt. The preamble is the same bytes on every call and holds no iteration
number and no spend, so every iteration begins from the same stated context
(REQ-0880). The preamble names `progress/progress.md` by its absolute path,
states the condition, and says the runner decides completion and holds the
bounds. `--add-dir` names the run's `progress` directory, so the progress file
is meant to be reachable from the call, and the runner adds an allow rule for Edit and
Write of that file, because its run id is fixed only at start and so no rule
the person types can name it (REQ-0882).

`<meow-loop>` is the unit's own directory, which the runner names on every
call, so the unit's hook loads in every call of a run. Each `--plugin-dir`
the person named follows it, in the order given. `<budget left>` is the budget
minus the spend so far. It's a second limit on one call, and the runner's own
check before the call is what bounds the run.

Six behaviours of a real call are unobserved, and a stand-in `claude` can't
show them (ADR-2010): whether the model can write `progress.md` under
`dontAsk` through `--add-dir` and the allow rule, what
`--permission-prompts none` does, which plugins a repository's own settings
add under `--setting-sources project`, whether the unit's hook fires in a
`-p` call, whether `CLAUDECODE` is set in a Bash call inside one, and whether
the user's own instruction files and memory load. The hash check decides
whether the terms changed, whether or not the hook fires.

### Endings

A run that isn't interrupted and doesn't stop on a failure after start ends
in exactly one of six endings. The runner writes the ending into
`run.toml` and prints it on the last line of its output:

| Ending      | When                                                                | Exit status |
| ----------- | ------------------------------------------------------------------- | ----------- |
| `finished`  | The condition held at the current tree                              | 0           |
| `budget`    | The next call could pass the budget, or a call reported its cap hit | 1           |
| `ceiling`   | The stated number of iterations ran                                 | 1           |
| `idle`      | Two iterations in a row changed nothing                             | 1           |
| `tampered`  | `run.toml` or `prompt.md` changed during the run                    | 1           |
| `unmetered` | A call reported no cost, so the spend can't be summed               | 1           |

### Who starts a run

Only a person starts a run, and four guards stop the model starting one
(REQ-0894):

- The skill `meow-loop:loop` sets `disable-model-invocation: true`. Invoked by
  a person, it helps write the prompt file and prints the `start` command for
  the person to run in a terminal.
- `start` exits 3 and writes nothing when `CLAUDECODE` is set in its
  environment.
- The hook denies a Bash command whose text holds a word ending in
  `meow-loop` followed by `start`, or a word ending in `meow` followed by
  `loop start`, the native program `bin/meow-loop` runs, in any session where
  the unit is loaded, and so in every call of a run where the hook fires.
  Matching the text catches a path-qualified runner, a start after
  `env -u CLAUDECODE` and one inside `bash -c`, which the deny rule's prefix
  doesn't match. It doesn't catch a name hidden in a script file, a variable
  or a command substitution, because it reads the command text and not what
  the text expands to. It also denies a harmless command whose text holds
  those words, such as a search for `meow-loop start` in a file, which is the
  price of matching text and not a defect in the hook.
- Every call passes `--disallowedTools "Bash(meow-loop *)" "Bash(meow loop *)"`,
  so a call can't start a nested run by either name.

The hook also denies an Edit or a Write of any path under
`<state>/meowpaw/runs/` other than a run's `progress/progress.md`. The hash
check before and after each call decides whether the terms changed, whether
or not the hook loaded.

## Failure paths

Each usage error exits 2, creates no run directory and removes none:

| State                                                                               | Reported as                                      |
| ----------------------------------------------------------------------------------- | ------------------------------------------------ |
| `--prompt`, `--until`, `--iterations`, `--budget-usd` or `--permission-mode` absent | `usage: <flag> is required`, once for each       |
| The prompt file is missing or can't be read                                         | `usage: --prompt <file> can't be read`           |
| `--until verbs=` names no verb                                                      | `usage: --until names no verb`                   |
| `--until verbs=` names something other than the five verbs                          | `usage: <name> is not a verb`, once for each     |
| `--iterations` isn't an integer of 1 or more                                        | `usage: --iterations <value> is not at least 1`  |
| `--budget-usd` isn't a number above 0                                               | `usage: --budget-usd <value> is not above 0`     |
| `--until` names a kind other than `verbs=`                                          | `usage: --until <value> is not a condition kind` |
| `--permission-mode` is anything but `dontAsk`                                       | `usage: --permission-mode <value> is refused`    |

Each state the runner can't read past exits 3, reported as
`unresolved: <what>`, and creates no run directory and removes none:

| State                                          | Reported as                                                    |
| ---------------------------------------------- | -------------------------------------------------------------- |
| `CLAUDECODE` is set                            | `unresolved: a run starts from a terminal outside Claude Code` |
| The current directory isn't in a git work tree | `unresolved: not a git work tree`                              |
| `MEOWPAW_STATE=off`                            | `unresolved: state writing is off, and a run needs state`      |
| No `claude` on the path                        | `unresolved: claude is not on the path`                        |
| A verb in the condition resolves to no command | `unresolved: verb <verb> resolves to no command`               |
| Another process holds the work tree's lock     | `unresolved: a run already holds this work tree`               |

A failure to remove an old run doesn't refuse the start: the runner prints
`can't remove <run id>: <error>` and goes on, because retention is
housekeeping and the new run doesn't depend on it. After start, a write the
runner can't make to `log.jsonl` or `run.toml`, or a held verb command or
`claude` it can't spawn, stops the run at once, before any further call. The
runner prints `unresolved: <what>`, exits 3 and writes no ending, so the run
reads as interrupted, and an unspawned verb counts neither as a pass nor as a
fail, because an unresolved verb is never a pass.

The runner reports every usage error it finds before it exits, so one attempt
names every flag to fix. The runner installs no signal handler, so a run
interrupted by a signal exits with the status the shell reports for that
signal and without an ending in `run.toml`, and the next `start` in that work
tree takes the lock. It needs none, because the operating system frees the
lock when the process ends, and stopping a run and recording who stopped it
belong to a later decision (ADR-2010).

## Open review findings

- The reviewer suggested keeping the changed `run.toml` beside the run before
  the runner writes the `tampered` ending into it, since the changed content
  is the only evidence of what a call tried. Left open: it adds a file to the
  run's layout that ADR-2010 doesn't name and no task builds, so it belongs
  in the next change to the runner.
