---
reader: someone choosing or running meow-loop
answers: what meow-loop start repeats, what bounds a run and what a run keeps
kind: reference
describes: [meow-loop@0.6.0]
---

# meow-loop

`meow-loop start` repeats one prompt in fresh `claude -p` calls until the
verification verbs you name pass, or until the number of iterations you state
has run, the next call could pass the budget you state, or two iterations in a
row change nothing. The runner is a
program outside the model, so nothing a call prints or writes extends the run,
and the runner alone decides whether the work is done, from each verb's exit
status.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-loop@meowpaw
```

## Start a run

Only a person starts a run, from a terminal outside Claude Code, such as a
separate tmux window, because the run holds that terminal until it ends. In a
Claude Code session, `/meow-loop:loop` helps you write the prompt file and
prints the command; it runs nothing, and the model can't invoke it.

Before you start, declare each verb the run waits for under `[verbs]` in your
repository's `.meowpaw/profile.toml`, and write the prompt to a file. Then run
the launcher by its path in the installed unit, from a terminal in the
repository, replacing `./scripts/prompt.md` with your prompt file:

```bash
meow-loop start --prompt ./scripts/prompt.md --until verbs=test \
  --iterations 5 --budget-usd 10 --permission-mode dontAsk
```

The run holds the terminal until it ends, and its last line is the ending.

| Term                | Holds                                                                         | Required |
| ------------------- | ----------------------------------------------------------------------------- | -------- |
| `--prompt`          | The file whose bytes every call gets on its standard input                    | yes      |
| `--until`           | `verbs=` and one or more of `format`, `lint`, `check`, `test` and `build`     | yes      |
| `--iterations`      | The ceiling: the most calls the run makes, an integer of 1 or more            | yes      |
| `--budget-usd`      | The budget in US dollars, a decimal number above 0, such as `2.50`            | yes      |
| `--permission-mode` | `dontAsk`, the only mode accepted                                             | yes      |
| `--allowed-tools`   | One permission rule each call may use without asking. Repeat it for each rule | no       |
| `--plugin-dir`      | One unit's directory each call loads. Repeat it for each unit                 | no       |

`start` refuses a run with no condition, no ceiling or no budget, because a
loop with a bound missing stops only when you notice it. It refuses
`bypassPermissions` and every other mode, because `dontAsk` denies what you
didn't allow where another mode would ask a person who isn't there, or allow
everything.

## What a run does

The runner resolves each named verb to the command your profile declares,
holds that command for the whole run and records it in `run.toml`, so a call
that rewrites `.meowpaw/profile.toml` changes nothing the run checks. It runs
the verbs once before any call. If every one passes, the run ends
`finished` with no call. Otherwise each iteration makes one call:

```text
claude -p --output-format json --no-session-persistence
       --setting-sources project --plugin-dir <meow-loop> --plugin-dir <dir>...
       --permission-mode dontAsk --allowedTools <rule>...
       --allowedTools "Edit(/<run>/progress/progress.md)"
       --allowedTools "Write(/<run>/progress/progress.md)"
       --permission-prompts none --add-dir <run>/progress
       --max-budget-usd <budget left> --append-system-prompt <preamble>
```

`<run>` is the run's directory, an absolute path with every link resolved, and
a permission rule writes an absolute path after one more slash. `<meow-loop>`
is the unit's own directory, named first so the unit's hook loads in every
call, and each `--plugin-dir` you named follows it in the order given.

Before each call and after it, the runner compares the sha256 of the run's
`run.toml` and `prompt.md` and of the work tree's `.claude/settings.json`
with their values at start, and ends the run `tampered` where one changed. It
checks this before the ceiling and the budget, so a run that changed its own
terms is reported as that whatever bound it also reached. The unit's
`PreToolUse` hook on Edit and Write denies a write of any path under the runs
directory other than a run's `progress/progress.md`. No real call has been
observed running the hook, so the sha256 check decides either way.

Each call is a new session: the runner passes no `--resume` and no
`--continue`. `--setting-sources project` keeps the plugins you installed for
yourself out of the call, so a call loads only the directories you name with
`--plugin-dir` and what the repository's own settings add.

The runner reads the prompt file once, at start, and every call gets those
bytes on its standard input, so an edit to the file during a run reaches no
call. Every call also gets the same preamble, appended to the system prompt.
The preamble names the run's `progress/progress.md` by its absolute path and
the condition, and says the runner decides whether the run is finished and
holds its bounds. It holds no iteration number and no spend, so each iteration
begins from the same stated context.

What one iteration leaves for the next goes in `progress/progress.md`, which
the preamble tells the model to read first and to write before it stops.
`--add-dir` and the two rules are there to let a call write that file. No real
call has been observed writing it under `dontAsk` yet.

Before each call the runner adds the largest single call's cost so far to the
spend so far, and ends the run `budget` if the sum is above the budget, so the
run stops before the call that could pass it. Before the first call both are
0, so the first call always starts. `<budget left>` is the budget less the
spend so far. It caps that one call on the platform's side, and the runner's
own check is what bounds the run.

After a call the runner reads `total_cost_usd` from the call's result and adds
it to the spend. A call that prints no result, or a result whose cost is
absent, negative or no number, ends the run `unmetered`, because a spend the
runner can't sum bounds nothing. That call's line in the log holds `null` for
`sum_usd`. A call whose result has the subtype `error_max_budget_usd` ends the
run `budget`. Both come before the condition, so a call that reports no cost
and also makes the verbs pass ends `unmetered`.

Then the runner compares the work tree's tree id with the one before
the call. The tree id covers every tracked file and every untracked file git
doesn't ignore. If the tree id changed or couldn't be identified, the runner
runs the verbs again, and
the run ends `finished` when every one exits 0 and the verbs left the tree as
they found it. An unchanged tree would repeat the last result, so the runner
skips the verbs and makes the next call. Where a verb changes the tree, such
as a formatter that rewrites files, the runner runs the verbs a second time at
once, and that second result stands.

| Ending      | When                                                                      | Exit status |
| ----------- | ------------------------------------------------------------------------- | ----------- |
| `finished`  | Every named verb passed at one tree                                       | 0           |
| `budget`    | The next call could pass the budget, or a call reached its own cap        | 1           |
| `ceiling`   | The stated number of iterations ran                                       | 1           |
| `unmetered` | A call reported no cost, so the spend can't be summed                     | 1           |
| `idle`      | Two iterations in a row changed neither the tree nor the progress file    | 1           |
| `tampered`  | `run.toml`, `prompt.md` or `.claude/settings.json` changed during the run | 1           |

`meow-loop` runs the verbs itself and needs no other unit. It records each
verb's result in the ledger `meow-checks` reads, so where that unit is
installed, `meow-checks evidence` prints the run's last results.

## What a run keeps

A run writes nothing into your work tree. Its files go to
`<state>/meowpaw/runs/<work tree key>/<run id>/`, where `<state>` is
`$XDG_STATE_HOME`, or `~/.local/state` where that isn't set, and
`MEOWPAW_STATE_DIR` replaces `<state>/meowpaw`. `start` prints the directory
when the run begins.

| File                   | Holds                                                                                                                                                                                                                                                                                                        |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `run.toml`             | The prompt's sha256, the sha256 of `.claude/settings.json` at start or `absent`, the condition with each verb's command, the ceiling, the budget, the permission mode, each rule and plugin directory, who started the run and when, and the ending                                                          |
| `prompt.md`            | A copy of the prompt file as it was at start                                                                                                                                                                                                                                                                 |
| `progress/progress.md` | What each iteration wrote for the next one. It starts empty                                                                                                                                                                                                                                                  |
| `log.jsonl`            | One line per call: the iteration, the tree id before and after, the call's `total_cost_usd`, `sum_usd` with the spend up to and including it, the count of `permission_denials`, its exit status, `progress_changed`, `unidentified` where either tree id is `none`, and the condition's result where it ran |

A `run.toml` with no `ending` belongs to a run that was interrupted, and the
last line of its log says how far it got. One run holds a work tree at a time,
through a lock the operating system releases when the runner's process ends,
so a killed run never blocks the next one. When a run starts, the runner keeps
the newest 20 runs of the work tree, counting the new one, and prints the id
of each run it removes.

## What this version doesn't bound yet

The budget bounds the run before a call and not during one. A call that costs
more than every call before it can take the spend past the budget by the
difference, and the first call is held only by the platform's cap.

An iteration changes nothing when the tree id and the sha256 of
`progress/progress.md` are the same after the call as before it. Two such
iterations in a row end the run `idle`. A call that removes the progress file
changes it, and an absent file is the same before and after a later call. A
file the runner can't read counts as changed. An iteration whose tree id is `none`,
as with a dirty submodule, counts as a change, so a run in such a work tree
never ends `idle`.

A held command still runs files in the work tree: a call that rewrites a
script or a task file the command runs changes what the condition checks,
and no sha256 covers those files. Read the run's diff before you trust a
`finished`.

Four guards stop the model starting a run: the skill `meow-loop:loop` only a
person invokes, `start` refusing when `CLAUDECODE` is set, the hook denying a
Bash command that runs `meow-loop start` or `meow loop start`, and every call
passing `--disallowedTools "Bash(meow-loop *)" "Bash(meow loop *)"`. The hook
reads the command's text, not what it expands to, so it misses a name hidden
in a script, a variable or a command substitution, or split by quotes or a
backslash, as in `st""art` or `st\art`, and it also denies a harmless command whose text
holds those words, such as a search for `meow-loop start`.

## What it reports instead of a run

A usage error exits 2 and prints `usage: <what>` for every error in the
command, so one attempt names every flag to fix:

| Line                                                            | Means                                                                          |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `usage: <flag> is required`                                     | A required term is absent                                                      |
| `usage: --prompt <file> can't be read`                          | The prompt file is missing or unreadable                                       |
| `usage: --until names no verb`                                  | `verbs=` is followed by nothing                                                |
| `usage: <name> is not a verb`                                   | `verbs=` names something other than the five verbs                             |
| `usage: --until <value> is not a condition kind`                | The condition doesn't start with `verbs=`                                      |
| `usage: --iterations <value> is not at least 1`                 | The ceiling isn't an integer of 1 or more                                      |
| `usage: --iterations <value> is above 9223372036854775807`      | The ceiling is larger than `run.toml` can hold                                 |
| `usage: --budget-usd <value> is not a decimal number`           | The budget isn't digits with one optional point, so `1e1` and `+1` are refused |
| `usage: --budget-usd <value> is not above 0`                    | The budget is 0                                                                |
| `usage: --budget-usd <value> is too large or too small to hold` | The budget has more digits than the runner's number holds                      |
| `usage: --permission-mode <value> is refused`                   | The mode is anything but `dontAsk`                                             |
| `usage: <flag> needs a value`                                   | A term is the last word of the command                                         |
| `usage: <word> is not a term of start`                          | The command holds a word that is no term                                       |

A state the runner can't read past exits 3, prints `unresolved: <what>` and
creates no run directory:

| Line                                                                            | Means                                                                                                |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `unresolved: a run starts from a terminal outside Claude Code`                  | `CLAUDECODE` is set, so the command ran inside a Claude Code session                                 |
| `unresolved: not a git work tree`                                               | The current directory isn't inside one                                                               |
| `unresolved: state writing is off, and a run needs state`                       | `MEOWPAW_STATE=off` is set                                                                           |
| `unresolved: no state directory: set XDG_STATE_HOME, MEOWPAW_STATE_DIR or HOME` | None of the three variables names where state goes                                                   |
| `unresolved: claude is not on the path`                                         | No `claude` that can be run is on `PATH`                                                             |
| `unresolved: verb <verb> resolves to no command`                                | The profile declares no command for a named verb                                                     |
| `unresolved: a run already holds this work tree`                                | Another run's process holds the lock                                                                 |
| `unresolved: can't take the lock <path>: <error>`                               | The runner can't create or lock the work tree's lock file                                            |
| `unresolved: can't create a run in <directory>: <error>`                        | The runner can't create the run's directory                                                          |
| `unresolved: meow-loop's own directory can't be found from its program's path`  | The program doesn't sit in a unit whose manifest names `meow-loop`, so a call couldn't load its hook |
| `unresolved: can't resolve <directory>: <error>`                                | The runner can't resolve the run's progress directory                                                |

During a run, a file the runner can't write, or a `claude` or a verb's
command it can't start, stops the run with the same
`unresolved:` line and exit status 3. The run then has no ending, and reads as
interrupted.

## What it costs you

The unit's one skill, `meow-loop:loop`, is invoked only by a person, so its
description isn't loaded into context, and the unit keeps nothing in context
on every turn; its budget states zero characters. Its hook runs the native
program on every Bash command, Edit and Write, which loads nothing into
context; on a machine the unit carries no binary for, the hook lets every
command and write through. The program is a native binary shipped inside the unit. On a
machine the unit carries no binary for, `start` reports the run as unresolved
and exits 3. Each run leaves a directory of a few kilobytes in the state
directory until a later run removes it.

## What it needs

Claude Code 2.1.280 or later, declared in `plugins/meow-loop/requires.toml`,
with `claude` on your `PATH`, and git. It relies on a `PreToolUse` command
hook that answers `deny` through `hookSpecificOutput.permissionDecision`:
[documentation](https://code.claude.com/docs/en/hooks.md).
