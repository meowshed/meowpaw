---
reader: someone choosing or running meow-loop
answers: what meow-loop start repeats, what bounds a run and what a run keeps
kind: reference
describes: [meow-loop@0.10.0]
---

# meow-loop

`meow-loop start` repeats one prompt in fresh `claude -p` calls, bound to one
step of the method. It ends when the step's work is done in the record and the
verification verbs you name pass at one tree. It also ends when the number of
iterations has run, when the next call could pass the budget you state, or
when two iterations in a row change nothing. The runner is a program outside
the model, so nothing a call prints or writes extends the run. The runner
alone decides whether the work is done, from the record and each verb's exit
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
meow-loop start --step implement --inputs TSK-0042 \
  --prompt ./scripts/prompt.md --until verbs=test \
  --iterations 5 --budget-usd 10 --permission-mode dontAsk
```

The run holds the terminal until it ends. Its last line is the ending. For
`crossed` and `off-step` it also names each record or path that caused it and,
for an evaluation, the verb that ran.

| Term                | Holds                                                                                       | Required                                      |
| ------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------- |
| `--step`            | The step the run takes: `research`, `requirements`, `design`, `spec`, `epic` or `implement` | yes                                           |
| `--inputs`          | The identifiers the step reads, separated by commas. `research` takes none                  | yes, except with `research`, which refuses it |
| `--prompt`          | The file whose bytes every call gets on its standard input                                  | yes                                           |
| `--until`           | `verbs=` and one or more of `format`, `lint`, `check`, `test` and `build`                   | yes                                           |
| `--iterations`      | The ceiling: the most calls the run makes, an integer of 1 or more                          | yes                                           |
| `--budget-usd`      | The budget in US dollars, a decimal number above 0, such as `2.50`                          | yes                                           |
| `--permission-mode` | `dontAsk`, the only mode accepted                                                           | yes                                           |
| `--allowed-tools`   | One permission rule each call may use without asking. Repeat it for each rule               | no                                            |
| `--plugin-dir`      | One unit's directory each call loads. Repeat it for each unit                               | no                                            |

`start` refuses a run whose inputs aren't ready for the step, printing each
line `paw ready` would print, because a step run over unapproved inputs builds
on work nobody accepted. It refuses a run whose record root is missing,
ignored by git or outside the work tree, because the tree id would then leave
the record out. `review` is no step a run takes, because a person reviews.
`start` refuses a run with no step, no condition, no ceiling or no budget, because a
loop with a bound missing stops only when you notice it. It refuses
`bypassPermissions` and every other mode, because `dontAsk` denies what you
didn't allow where another mode would ask a person who isn't there, or allow
everything.

## What a run does

The runner resolves each named verb to the command your profile declares,
holds that command for the whole run and records it in `run.toml`, so a call
that rewrites `.meowpaw/profile.toml` changes nothing the run checks.

The condition has two terms, and both must hold at one tree: the step's test
on the record, and every named verb exiting 0. A record counts whatever its
status, so a draft counts:

| Step           | Its test holds when                                                                                               |
| -------------- | ----------------------------------------------------------------------------------------------------------------- |
| `research`     | A research record exists that wasn't there at start                                                               |
| `requirements` | Each input research record is in the `elaborates` of some requirement new or changed since start                  |
| `design`       | Each input requirement is in the `addresses` or `postpones` of some decision new since start                      |
| `spec`         | Each requirement the input decision addresses is in the `states` of some specification new or changed since start |
| `epic`         | An epic new since start names the input in `realises`                                                             |
| `implement`    | Each input task is marked `x` by the record that authorises it, and its `## Evidence` holds text                  |

"Since start" compares with the copy of the record the runner takes just after
its first evaluation. A verb that rewrote a record in that evaluation then
isn't counted as the first call's change. A task marked `~`, dropped, doesn't pass
`implement`. The runner reads no pass from the ledger and nothing a call
printed, so a result saying the work is done changes nothing.

The runner evaluates the condition once before any call. An `implement` run
whose work is done and whose verbs pass ends `finished` with no call. Every
other step's test counts only a record new or changed since start, so those
runs always make at least one call. While the condition doesn't hold, each
iteration makes one call:

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
directory other than a run's `progress/progress.md`.

Every call's environment holds `MEOW_LOOP_RUN`, set to the run's id. Where
that variable is set, the same hook denies an Edit or a Write that would give
a file under the record root a decided status. The model then hears the
refusal before it spends the iteration. The hook reads the file's kind from
its directory, so `live` passes in a specification and not in a requirement.
It reads the file on disk, so an Edit of an approved task's Evidence, which
leaves the status as it is, passes. Without the variable, the rule allows
every Edit and Write, because in a session the model writes an approval a
person gave. A variable set to an empty string counts as set. The hook allows
a write where it can't read the layout or the profile. It doesn't see a Bash
command or a MultiEdit that writes a record. The comparison after each call
decides whether a gate was crossed in those cases. Nobody has observed a real call run the hook or
see the variable, so treat the hook as a first warning and the comparison as
the check.

Each call is a new session: the runner passes no `--resume` and no
`--continue`. `--setting-sources project` keeps the plugins you installed for
yourself out of the call, so a call loads only the directories you name with
`--plugin-dir` and what the repository's own settings add.

The runner reads the prompt file once, at start, and every call gets those
bytes on its standard input, so an edit to the file during a run reaches no
call. Every call also gets the same preamble, appended to the system prompt.
The preamble names the run's `progress/progress.md` by its absolute path and
the condition, and says the runner decides whether the run is finished and
holds its bounds. It names the step, its inputs and what the step may write.
It says that a decided status, a change to an approved record or a change to
another step's files ends the run early. Where the work shows an approved
artifact is wrong, it tells the model to record a defect as a draft. It holds no iteration number and no spend, so each iteration
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

A call ends the run `crossed` when the record, compared with the copy the
runner took at start, shows one of four changes:

- a record's stored status became a decided status, which is any status except
  `draft`, and except `live` in a living kind such as a specification,
  because a specification is `live` from its first draft;
- a record new since start carries a decided status;
- an approved record is gone from the path it had at start, deleted or
  renamed;
- an approved record changed outside what a run may change in it.

The runner makes this comparison after every call, unless it can identify the
work tree before and after the call and finds it unchanged. A changed term, a
missing cost and a call's own cap end the run first. The comparison comes
before the condition, so a call that approves a draft and also makes the
verbs pass ends `crossed`, not `finished`.

A run may change an approved task only in its Evidence, its Left alone
section, its issue, its projection and its revision date. It may change an
approved epic or defect only in its task marks and the evidence lines written
with them, and only in an `implement` run. The comparison takes none of
`paw check frozen`'s exemptions, because a person makes those decisions. A
status now `withdrawn` or `superseded` crosses. So does a line naming an
authority.

The runner makes the same comparison after each verb of its own evaluation
that changed the tree, so a verb that crosses a gate ends the run `crossed`.
The last line of the output then names each record that crossed and, for an
evaluation, the verb that ran.

When a call writes another step's files or leaves its input unready, the
runner ends the run `off-step`, after the comparison for `crossed`. A step
writes only what its row names:

| Step           | May write                                                                        |
| -------------- | -------------------------------------------------------------------------------- |
| `research`     | Research records                                                                 |
| `requirements` | Requirements                                                                     |
| `design`       | Decisions                                                                        |
| `spec`         | Specifications                                                                   |
| `epic`         | Epics and tasks                                                                  |
| `implement`    | Tasks, the task marks of epics and defects, and any path outside the record root |

Every step may also write a draft defect, because a run records a defect it
finds, and a draft insight, because a run records what it learns. It may write
a file under the record root that is no record, such as an index, because
`paw index --write` regenerates those. A step other than `implement` may not
change a path outside the record root. Where the record root is the work tree
itself, that limit has no effect, because every path is inside it.

The runner lists the paths a call changed with `git diff-tree` between the
tree id it read just before the call and the one after. A path a verb rewrote
in an evaluation is therefore not listed, because the runner read the first
id after that evaluation. Where the runner can't identify either tree, it
can't list the paths. It then compares the records with its copy instead, so a
record of the wrong kind still ends the run. A step that writes only records
ends `off-step` for that reason alone, because nothing shows that the call
kept to the record root. An `implement` run doesn't end `off-step` for that
reason, because it may write any path outside the record root.

An input is unready when the test `paw ready` applies no longer passes for it,
for example after a call clears the mark of a task the input depends on. The
last line names each record or path, or the reason the runner can't list the
paths.

If the tree id changed or couldn't be identified, the runner then evaluates
the condition. The tree id covers every tracked file and every untracked file
git doesn't ignore. When the step's test holds, every verb exits 0 and the
evaluation left the tree as it found it, the run ends `finished`. An
unidentified tree, such as one with a dirty submodule, holds no condition. An
unchanged tree would repeat the last result, so the runner skips the
evaluation and makes the next call. Where a verb changes the tree, such as a
formatter that rewrites files, the runner evaluates a second time at once, and
that second result stands.

| Ending      | When                                                                               | Exit status |
| ----------- | ---------------------------------------------------------------------------------- | ----------- |
| `finished`  | The step's test held and every named verb passed at one tree                       | 0           |
| `budget`    | The next call could pass the budget, or a call reached its own cap                 | 1           |
| `ceiling`   | The stated number of iterations ran                                                | 1           |
| `unmetered` | A call reported no cost, so the spend can't be summed                              | 1           |
| `idle`      | Two iterations in a row changed neither the tree nor the progress file             | 1           |
| `tampered`  | `run.toml`, `prompt.md` or `.claude/settings.json` changed during the run          | 1           |
| `crossed`   | A call or an evaluation decided a status, or changed or removed an approved record | 1           |
| `off-step`  | A call wrote another step's files, or left its input unready                       | 1           |

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
| `run.toml`             | The step, the inputs as a list, the prompt's sha256, the sha256 of `.claude/settings.json` at start or `absent`, the condition with each verb's command, the ceiling, the budget, the permission mode, each rule and plugin directory, who started the run and when, and the ending                          |
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
| `usage: --step <value> is not a step a run takes`               | The step is none of the six, `review` among them                               |
| `usage: research takes no --inputs`                             | `--inputs` is given with `--step research`                                     |
| `usage: --step <step> needs --inputs`                           | `--inputs` is absent with any other step                                       |
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
| `unresolved: record root <path> is missing`                                     | The record root, `[record] root` or `project`, doesn't exist                                         |
| `unresolved: record root <path> is ignored by git`                              | Git ignores the record root, so the tree id leaves the record out                                    |
| `unresolved: record root <path> is outside the work tree`                       | The record root resolves to a path outside the work tree                                             |
| `unresolved: can't check whether record root <path> is ignored by git: <error>` | `git check-ignore` failed, so nothing shows that the tree id covers the record                       |
| `unresolved: <line>`                                                            | An input isn't ready for the step: one line for each line `paw ready <step> <inputs>` would print    |
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
