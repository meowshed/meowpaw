---
id: SPC-1201
artifact: spec
status: live
revised: 2026-10-02
states:
  [
    REQ-0870,
    REQ-0872,
    REQ-0874,
    REQ-0876,
    REQ-0878,
    REQ-0880,
    REQ-0882,
    REQ-0884,
    REQ-0886,
    REQ-0888,
    REQ-0894,
    REQ-1240,
  ]
---

# The loop runner

## Scope

This covers `meow-loop`, the method-layer unit that runs one frozen prompt
again and again in fresh `claude -p` sessions, bound to one step of the method
and its input, until the step's work is done and the verbs pass at one tree,
or a bound or a crossed gate ends the run. It states the command a person
runs, the terms it takes, the files a run keeps, each call it makes, the order
of its checks, the eight endings, the guards that stop the model starting a
run or deciding a status, and each state it refuses.

It doesn't cover the authority an unattended run is planned from, which
SPC-1200 states, and the runner doesn't read that plan. Stopping a run by any
means other than the terminal's interrupt, a run in the document or review
step, a run that approves a record through a separate judge, keeping a run's
results as evidence files, the sandbox, the network allowlist and credential
removal have no decision yet, so no specification states them. The runner also
doesn't guard the files the condition's commands read in the work tree, such
as a task runner's configuration or the tests, because those files are the
work a run is meant to change. Neither a call nor an evaluation of the
condition has a time limit, so a run's wall time is bounded only by its
ceiling, and a call that hangs holds the run and its lock until a person
interrupts it, because ADR-2010 chose no timeout.

ADR-2010 decides this part and EPC-1910 realises it. ADR-2020 amends it with
the step, the step's test and the endings `crossed` and `off-step`, and
EPC-1920 realises that amendment.

## Boundary

| Surface                                          | What it is                                                          |
| ------------------------------------------------ | ------------------------------------------------------------------- |
| `plugins/meow-loop/bin/meow-loop start`          | Starts a run in the current work tree and holds it until it ends    |
| `plugins/meow-loop/skills/loop/SKILL.md`         | A skill only a person invokes, which helps write the prompt file    |
| `plugins/meow-loop/hooks/hooks.json`             | A PreToolUse hook on Bash, Edit and Write                           |
| `plugins/meow-loop/README.md`                    | The unit's page                                                     |
| `plugins/meow-loop/.claude-plugin/plugin.json`   | The unit's manifest, which Claude Code loads it from                |
| `plugins/meow-loop/budget.toml`                  | What the unit loads on every turn: the skill's description          |
| `plugins/meow-loop/requires.toml`                | The Claude Code version the unit needs, 2.1.280                     |
| `.claude-plugin/marketplace.json`                | The unit's entry                                                    |
| `crates/meow`, feature `loop`                    | The unit's program, which compiles in the `verbs` and `record` code |
| `<state>/meowpaw/runs/<work tree key>/`          | Where a work tree's runs and its lock live, outside the work tree   |
| `<state>/meowpaw/runs/<work tree key>/<run id>/` | One run's directory                                                 |

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
meow-loop start --step <step> [--inputs <id>[,<id>...]]
                --prompt <file> --until verbs=<verb>[,<verb>...]
                --iterations <n> --budget-usd <amount>
                --permission-mode dontAsk [--allowed-tools <rule>]...
                [--plugin-dir <dir>]...
```

`--step`, `--prompt`, `--until`, `--iterations`, `--budget-usd` and
`--permission-mode` are each required, so the step, the condition and both
bounds are stated before a run starts (REQ-0872, REQ-0888), and no call
inherits the platform's default mode. `--step` names one of the six steps in
the table under "The step's test". `--inputs` names the identifiers that step
reads, and every step but `research` requires it, while `research` refuses it,
even with an empty value. An `--inputs` value that holds no identifier, such as
a lone comma, counts as absent, each identifier is read without the spaces
round it, and an identifier named twice counts once. `review` isn't a step a run takes.
`--iterations` is an integer of 1 or more, written in digits alone, and
`--budget-usd` a number above 0, in US dollars, written as digits with at
most one point between them, because every reader of `run.toml`, the runner
and a person, then takes the same amount from it. A call gets the budget left
as a number, not as typed. `--permission-mode` accepts `dontAsk` alone, because it's
the one mode RES-0300 saw run a call. `bypassPermissions` is refused, because
a run would then cross every permission the person hasn't declared
(ADR-2010).
`--allowed-tools` and `--plugin-dir` repeat, and each value passes to every
call unchanged.

The one condition kind is `verbs=`, naming one or more of the five verbs. At
start the runner resolves each named verb to its command and holds the
command in memory with the other terms, because `.meowpaw/profile.toml` is in
the work tree and a call could otherwise point a verb at a command that
always exits 0 (REQ-0874). The runner evaluates the condition itself, through
the `verbs` and `record` features' code, and runs no other unit's program to
do it, because a unit's file runs no path outside its own directory, which
the `standalone` check enforces, and so the unit works whether or not
`meow-checks` or `meow-flow` is installed.

After the command line, `start` checks the inputs through the `record` code,
with the test `paw ready <step> <inputs>` applies. It exits 3 when an input
isn't ready, printing each line `paw ready` would print. It exits 3 as well
when an input is the wrong kind for the step, because the step's test could
never hold and the run would spend its whole ceiling and budget. A
`requirements` run reads research records, a `design` run requirements, a
`spec` and an `epic` run decisions, and an `implement` run tasks. Such an input
gets the one line the failure table gives, in which `a` reads `an` before a
vowel, as in `an epic run`, and none of the lines `paw ready` would print for
it, because the layout fixes the kind and those lines would blame the status or
a missing epic, which is not the fault.

It exits 3 as well when the record root, `[record] root` in
`.meowpaw/profile.toml` or `project/`, is missing, is ignored by git, or lies
outside the work tree, because the tree id would then leave the record out
and bind the step's test to no tree. It exits 3 when git can't say whether the
record root is ignored, and when the profile or the layout can't be read,
because a state the runner can't read is never a pass. It exits 3 when a
Markdown file under the record root can't be read, because the runner reads
such a file as empty text, never guards it and so can't tell a change to it
(REQ-1240).

At start, after the evaluation before the first call, the runner reads the
whole record and holds in memory each record's identifier, kind, path, stored
status and text. "The copy held at start" below means this copy. It's taken
after that evaluation because a verb that writes, such as `format`, can
rewrite a record then, and the first call must not be blamed for that.

### The step's test

The condition holds only when two terms hold at the same tree: every held
verb command exits 0, and the step's test passes (REQ-0870, REQ-0884). A
record counts whatever its status, so a draft counts.

| Step           | Its test holds when                                                                                               | The step may write                                                        |
| -------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `research`     | A research record exists that wasn't in the copy held at start                                                    | research records                                                          |
| `requirements` | Each input research record is in the `elaborates` of some requirement new or changed since start                  | requirements                                                              |
| `design`       | Each input requirement is in the `addresses` or `postpones` of some decision new since start                      | decisions                                                                 |
| `spec`         | Each requirement the input decision addresses is in the `states` of some specification new or changed since start | specifications                                                            |
| `epic`         | An epic new since start names the input in `realises`                                                             | epics and tasks                                                           |
| `implement`    | Each input task is marked `x` by the record that authorises it, and its `## Evidence` holds text                  | tasks, the task marks of epics and defects, and any path outside the root |

"New since start" means absent from the copy held at start, and "changed"
means present there with other text. The `implement` test reads the `x` mark
alone, so a task marked `~`, dropped, doesn't pass it. An `implement` run
whose work is already done ends `finished` with no call, and a run of any of
the five record steps always makes at least one call, because its test counts
only a record new or changed since start.

### Evaluating the condition

The runner evaluates the condition before the first call and after each call
whose tree id changed or couldn't be identified. One evaluation:

1. reads the tree id, applies the step's test to the record in the work tree,
   runs each held verb command, and reads the tree id again;
2. holds only when the test passes, every command exits 0, and the two tree
   ids are equal and identified. Where both are identified and differ, the
   runner repeats the evaluation once, at once, and the second result stands,
   so a verb that settles after one pass can finish the run and a verb that
   changes the tree on every pass never does. An unidentified tree, such as
   one with a dirty submodule, holds no condition;
3. records each verb's result in the evidence ledger through the `verbs`
   code, with the tree before and after, as SPC-1040 states, so the person can
   cite the run's final results as `meow-checks evidence` prints them.

The runner reads no pass back from the ledger and nothing the model printed,
so a result whose text claims the work is done changes nothing, and no option
takes a completion phrase (REQ-0884).

### A run's files

`start` works in this order: it checks the command line, then checks each
state it can't read past, taking the work tree's lock as the last of those
checks, then writes the run's directory, named by a run id unique within the
work tree, then removes old runs. A refused start therefore keeps no run
directory and removes none: where the lock can't be taken or a file of the
new run can't be written, it removes what that attempt created before it
refuses. The directory `runs/<work tree key>/` and its lock
file, which hold no run, stay after a run ends. The lock is an advisory lock the operating system holds on an
open file in `<state>/meowpaw/runs/<work tree key>/` for the runner's
process, so it ends whenever the process ends, and an interrupted run leaves
no lock behind. One run holds a work tree at a time, because a second run's
edits would change the tree id the first reads for its condition and its
idle rule.

The run's directory holds four files:

| File                   | Holds                                                                                                                                                                                                                                                                                                                                                    |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run.toml`             | The step as one string, the inputs as a list, the prompt's sha256, the condition and each verb's resolved command, the ceiling, the budget, the permission mode, each allowed rule, each plugin directory, the sha256 of `.claude/settings.json` or its absence, who started the run and when, the repository's identity, and the ending once it has one |
| `prompt.md`            | A copy of the prompt file as it was at start                                                                                                                                                                                                                                                                                                             |
| `progress/progress.md` | The file the model reads and writes to carry what it has done across iterations, empty at start (REQ-0882)                                                                                                                                                                                                                                               |
| `log.jsonl`            | One line per iteration                                                                                                                                                                                                                                                                                                                                   |

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

1. appends the call's line to `log.jsonl`, with no result for the condition
   yet, so a run killed during the verbs keeps the call it made, and writes
   that line again with the result once step 6 has one;
2. checks the three sha256 values again, and ends the run `tampered` on a
   mismatch, so a call that changes `run.toml` and also makes the verbs pass
   never ends `finished`;
3. ends the run `unmetered` if the call printed no JSON result, or a result
   without `total_cost_usd`, and otherwise adds that cost to the spend;
4. ends the run `budget` if the result's subtype is `error_max_budget_usd`;
5. ends the run `crossed` if the call crossed a gate, and then `off-step` if
   it left its step, as "Keeping to one step" states (REQ-0888);
6. evaluates the condition if the tree id changed or couldn't be identified,
   and ends the run `finished` if it holds, because an unchanged tree would
   repeat the last result;
7. ends the run `idle` if this iteration and the one before it both changed
   nothing (REQ-0886).

Steps 3 to 5 come before the condition, because a call whose spend can't be
counted, that passed its own cap or that crossed a gate has broken a bound the
person stated, and a broken bound is reported before a success. So a call
that prints no cost and also makes the verbs pass ends `unmetered`, and its
log line holds no condition result.

A call that exits non-zero, or prints a result with any other error subtype,
counts as an iteration, and the ceiling and the budget bound it like any
other.

An iteration changes nothing when the work tree's id, as `ledger::tree_id`
computes it, and the sha256 of `progress/progress.md` are both the same after
the call as before it. An iteration whose tree the runner can't identify, such
as one with a dirty submodule, counts as a change.

### Keeping to one step

Step 5 after a call compares the record in the work tree with the copy held
at start, and reads the paths the call changed. The paths are those
`git diff-tree -r --name-only` lists between the tree id the runner read
immediately before the call, after its own evaluation, and the tree id after
the call, so a path a verb rewrote in an evaluation is never the call's. The
runner skips step 5 only when both ids are identified and equal, because then
the call changed no record and no path.

A decided status is any stored status except `draft`, and except `live` in a
kind the record declares living, such as a specification. The run ends
`crossed`, naming each record, when the comparison shows any of four changes:

- a record's stored status became a decided status;
- a record new since start carries a decided status;
- an approved record is gone from the path it had at start, deleted or
  renamed;
- an approved record changed outside what a run may change in it.

A run may change an approved task outside its frozen part, as the record's
frozen comparison allows. It may change an approved epic or an approved
defect only in the marks of its tasks and the `evidence:` lines written with
them, and only in an `implement` run, because the implement step writes an
evidence line with each mark. The mark of any task in the record may change,
not only the input's. Any other change to an approved epic or defect crosses. The runner takes none of the
frozen comparison's other allowances: a status now `withdrawn` or `superseded`
crosses, and so does an added line naming an authority. ADR-2300 removed the
cover and verify steps, so no run is bound to either.

The run ends `off-step`, naming each record or path, when the call:

- created or changed a record of a kind the step's row doesn't let it write.
  A defect or an insight as a draft is allowed in every step, and so is a
  file under the record root that is no record, such as an index;
- changed a path outside the record root in a step whose row doesn't allow
  it. Where either tree id is unidentified the runner can't list the paths,
  and it ends a run of a step that writes only records `off-step` for that
  reason;
- left an input failing the test `start` applied.

The runner checks `crossed` before `off-step`, so a call that does both ends
`crossed`.

After each of its own evaluations that changed the tree, the runner also
compares the record with the copy held at start. A decided status or a change
to an approved record found there ends the run `crossed`, naming the
evaluation and the verb that ran in it.

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
bounds. It names the step, its inputs and what the step may write, and the
three things that end the run early: a decided status, a change to an
approved record, and a change to another step's files. It tells the model to
record a defect as a draft where the work shows an approved artifact is wrong
(REQ-0888). Every call's environment sets `MEOW_LOOP_RUN` to the run's id. `--add-dir` names the run's `progress` directory, so the progress file
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
the user's own instruction files and memory load. Whether the hook sees
`MEOW_LOOP_RUN` in a `-p` call is unobserved as well (ADR-2020), and the
comparison after each call decides whether a gate was crossed, whether or not
the hook's status rule fired. The hash check decides
whether the terms changed, whether or not the hook fires.

### Endings

A run that isn't interrupted and doesn't stop on a failure after start ends
in exactly one of eight endings. The runner writes the ending into
`run.toml` and prints it on the last line of its output:

| Ending      | When                                                                               | Exit status |
| ----------- | ---------------------------------------------------------------------------------- | ----------- |
| `finished`  | The condition held at the current tree                                             | 0           |
| `budget`    | The next call could pass the budget, or a call reported its cap hit                | 1           |
| `ceiling`   | The stated number of iterations ran                                                | 1           |
| `idle`      | Two iterations in a row changed nothing                                            | 1           |
| `tampered`  | `run.toml` or `prompt.md` changed during the run                                   | 1           |
| `unmetered` | A call reported no cost, so the spend can't be summed                              | 1           |
| `crossed`   | A call or an evaluation decided a status, or changed or removed an approved record | 1           |
| `off-step`  | A call wrote another step's files, or the step's input stopped being ready         | 1           |

The last line of a run that ended `crossed` or `off-step` names each record
or path that caused it, and for an evaluation, the verb that ran in it.

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

### The status rule

When `MEOW_LOOP_RUN` is set, the hook denies an Edit whose `new_string`, or a
Write whose `content`, would change the stored status of a file under the
record root to a decided status, as "Keeping to one step" defines it. It reads
the kind from the file's directory, so it allows `live` in a specification,
and it reads the file on disk, so an edit that leaves a status already there
unchanged, such as an Edit of an approved task's `## Evidence`, passes. When
`MEOW_LOOP_RUN` isn't set, the rule allows every edit, because in a session
the model writes an approval a person gave, and a variable set to an empty
string counts as set. The rule covers Edit and Write. A Bash command, a
MultiEdit or a NotebookEdit passes the hook, so the comparison after each call
decides whether a gate was crossed (REQ-0888). The rule allows the write
where the hook can't read the layout or the profile, and it reads a file with
CRLF line endings as one with LF endings.

## Failure paths

Each usage error exits 2, creates no run directory and removes none:

| State                                                                                         | Reported as                                                     |
| --------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `--step`, `--prompt`, `--until`, `--iterations`, `--budget-usd` or `--permission-mode` absent | `usage: <flag> is required`, once for each                      |
| `--step` names no step in the table, `review` among them                                      | `usage: --step <value> is not a step a run takes`               |
| `--inputs` given with `--step research`, even empty                                           | `usage: research takes no --inputs`                             |
| `--inputs` absent, or holding no identifier, with any other step                              | `usage: --step <step> needs --inputs`                           |
| The prompt file is missing or can't be read                                                   | `usage: --prompt <file> can't be read`                          |
| `--until verbs=` names no verb                                                                | `usage: --until names no verb`                                  |
| `--until verbs=` names something other than the five verbs                                    | `usage: <name> is not a verb`, once for each                    |
| `--iterations` isn't an integer of 1 or more                                                  | `usage: --iterations <value> is not at least 1`                 |
| `--iterations` is above 9223372036854775807                                                   | `usage: --iterations <value> is above 9223372036854775807`      |
| `--budget-usd` isn't digits with at most one point between them                               | `usage: --budget-usd <value> is not a decimal number`           |
| `--budget-usd` is a decimal number that is 0                                                  | `usage: --budget-usd <value> is not above 0`                    |
| `--budget-usd` is a decimal number the runner can't hold                                      | `usage: --budget-usd <value> is too large or too small to hold` |
| `--until` names a kind other than `verbs=`                                                    | `usage: --until <value> is not a condition kind`                |
| `--permission-mode` is anything but `dontAsk`                                                 | `usage: --permission-mode <value> is refused`                   |

Each state the runner can't read past exits 3, reported as
`unresolved: <what>`, and creates no run directory and removes none:

| State                                                | Reported as                                                                                                                        |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `CLAUDECODE` is set                                  | `unresolved: a run starts from a terminal outside Claude Code`                                                                     |
| The current directory isn't in a git work tree       | `unresolved: not a git work tree`                                                                                                  |
| `MEOWPAW_STATE=off`                                  | `unresolved: state writing is off, and a run needs state`                                                                          |
| No `claude` on the path that can be run              | `unresolved: claude is not on the path`                                                                                            |
| A verb in the condition resolves to no command       | `unresolved: verb <verb> resolves to no command`                                                                                   |
| The record root is missing                           | `unresolved: record root <path> is missing`                                                                                        |
| The record root is ignored by git                    | `unresolved: record root <path> is ignored by git`                                                                                 |
| The record root lies outside the work tree           | `unresolved: record root <path> is outside the work tree`                                                                          |
| An input isn't ready for the step                    | `unresolved: <line>`, once for each line `paw ready <step> <inputs>` prints, except for an input already refused as the wrong kind |
| An input is the wrong kind for the step              | `unresolved: <id>, a <kind>, is not a <expected kind>, which a <step> run reads`                                                   |
| Git can't say whether the record root is ignored     | `unresolved: can't check whether record root <path> is ignored by git: <error>`                                                    |
| The profile can't be read                            | `unresolved: the profile can't be read: <reason>`                                                                                  |
| The layout can't be read                             | `unresolved: <layout path>: <error>`                                                                                               |
| A Markdown file under the record root can't be read  | `unresolved: record file <path> can't be read: <error>`                                                                            |
| Another process holds the work tree's lock           | `unresolved: a run already holds this work tree`                                                                                   |
| No state directory can be named                      | `unresolved: no state directory: set XDG_STATE_HOME, MEOWPAW_STATE_DIR or HOME`                                                    |
| The lock file can't be opened                        | `unresolved: can't take the lock <path>: <error>`                                                                                  |
| The run's directory or a file in it can't be written | `unresolved: can't create a run in <directory>: <error>`, or `can't write <path>: <error>`                                         |

A failure to remove an old run doesn't refuse the start: the runner prints
`can't remove <run id>: <error>` and goes on, because retention is
housekeeping and the new run doesn't depend on it. After start, a write the
runner can't make to `log.jsonl` or `run.toml`, a layout it can't read, or a
held verb command or `claude` it can't spawn, stops the run at once, before
any further call. The
runner prints `unresolved: <what>`, exits 3 and writes no ending, so the run
reads as interrupted, and an unspawned verb counts neither as a pass nor as a
fail, because an unresolved verb is never a pass. For that verb it prints
`unresolved: verb <verb> didn't run: <reason>`. A `claude` that can be run
by its mode and still can't be started, such as a file with no program in
it, is found only at the first call, after the run directory exists: a call
that can't be spawned, or that exits 126 or 127 and prints no result, stops
the run as `unresolved: claude can't be started`, so it never spends the
ceiling on calls that didn't happen.

The runner reports every usage error it finds before it exits, so one attempt
names every flag to fix. The runner installs no signal handler, so a run
interrupted by a signal exits with the status the shell reports for that
signal and without an ending in `run.toml`, and the next `start` in that work
tree takes the lock. It needs none, because the operating system frees the
lock when the process ends, and stopping a run and recording who stopped it
belong to a later decision (ADR-2010).
