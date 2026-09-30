---
id: ADR-2010
artifact: adr
status: approved
revised: 2026-09-29
addresses:
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
supersedes: []
---

# 2010. A runner outside the model repeats one frozen prompt in fresh sessions, and holds its bounds in its own process

## Decision

**Amended by ADR-2020.** A run is bound to one step and its input. The
condition adds the step's own test to the verbs, both at one tree, and a run
ends `crossed` or `off-step` when a call decides a status, changes an approved
record or writes another step's files. The rest stands.

A new method-layer unit, `meow-loop`, ships a program that a person starts from
a terminal. The program runs one `claude -p` call per iteration, and the model
never holds the loop, its count or its budget. The unit also ships a skill the
model can't invoke, a hook, a README, a budget and a marketplace entry. The
program is a native feature `loop` in `crates/meow`, built by `build-units`,
and it compiles in the `verbs` feature's code so it resolves and runs a verb
without running another unit's program.

`meow-loop start` takes the run's terms, and refuses to start unless the three
bounds are all stated (REQ-0872):

```text
meow-loop start --prompt <file> --until verbs=<verb>[,<verb>...]
                --iterations <n> --budget-usd <amount>
                --permission-mode dontAsk [--allowed-tools <rule>]...
                [--plugin-dir <dir>]...
```

A missing condition, ceiling, budget or permission mode, a ceiling below 1,
a budget of 0 or less, and any permission mode other than `dontAsk` each exit
2 and write nothing. A missing `--permission-mode` is refused and never
defaulted, because a call without the flag would inherit whatever mode the
platform defaults to. `dontAsk` is the one mode RES-0300 saw run a call, with an allowed
rule letting a command through, so the other modes wait on an observation of
how each behaves when nobody can answer a prompt. `bypassPermissions` stays
refused whatever that observation shows, because the run would then cross
every permission the person hasn't declared, which REQ-2372 and its
neighbours settle.
A state the runner can't read past exits 3 and writes nothing. Exit 2 means
the command as typed can't start a run, and exit 3 means the command is right
but the machine or the work tree isn't ready for it, so a script can tell a
command to correct from an environment to repair. A start from inside Claude
Code is a 3 for that reason: the same command, run from a terminal outside it,
starts, so the person changes where it runs and not what it says. The states
that exit 3 are: `CLAUDECODE` set in the runner's environment; no git work
tree, since the tree id that measures change needs one; state writing turned
off by `MEOWPAW_STATE=off`; `claude` not on the path; a named verb that
resolves to no command, because an unresolved verb is never a pass; and a run
already holding this work tree's lock.

The only condition kind in this increment is `verbs=`, and the runner
evaluates it itself (REQ-0870). The runner resolves each named verb to its
command once, at start, and holds the command in memory with the other terms,
because `.meowpaw/profile.toml` is in the work tree, and a call that pointed a
verb at a command that always exits 0 would otherwise extend the condition
(REQ-0874). The same reason applies to the work tree's
`.claude/settings.json`: `--setting-sources project` makes every call reread
it, and a call that added an allow rule, a hook or an enabled plugin there
would give the next call authority the person never typed. A hook added that
way runs outside any Bash tool call, so neither the deny rule nor the unit's
hook would see it. The runner therefore hashes that file, or records that it
is absent, with the run's own terms, and a change ends the run as `tampered`
before the next call reads it. The condition holds when every held command
exits 0 at the current tree. The runner evaluates it once before
the first call, where a condition already holding ends the run as `finished`
with no call, and again after each iteration that changed the tree. It
evaluates nothing after an iteration that left the tree unchanged, because
the result would repeat the last one. I chose verbs over the plan's ceiling
and budget alone, because a run whose only endings are running out can never
finish, and REQ-0870 asks for a condition that holds.

The run lives in the state directory, outside the repository, because the
runner's log is run state and REQ-3072 puts run state there. Its directory is
`<state>/meowpaw/runs/<work tree key>/<run id>/`, under the same base the
ledger uses and keyed by the work tree's path as REQ-0752 asks. A work tree
holds one run at a time, through a lock in the work tree key's directory,
because a second run's edits would change the tree id the first reads for its
condition and its idle rule, and neither run's ending would then say what its
own calls did. The lock is an advisory lock the operating system holds on an
open file for the runner's process, so it ends when the process ends, however
the process ends. An interrupted or killed run therefore leaves no stale lock,
and the next `start` in that work tree takes the lock without anyone clearing
it. The run's directory holds:

- `run.toml`: the prompt's sha256, the condition and each verb's resolved
  command, the ceiling, the budget, the
  permission mode, each plugin directory, the sha256 of the work tree's
  `.claude/settings.json` or its absence, who started the run and when, the
  repository's identity, and the run's ending once it has one. The runner
  records the file's own sha256 before the first call.
- `prompt.md`: a copy of the prompt file as it was at start.
- `progress/progress.md`: the file the model reads and writes to carry what it
  has done across iterations (REQ-0882). It starts empty.
- `log.jsonl`: one line per iteration, holding the iteration number, the tree
  id before and after, whether `progress.md` changed, the call's
  `total_cost_usd`, the sum so far, the count of `permission_denials`, the
  call's exit status, and the condition's result where the runner evaluated
  one. The tree id before a call is taken after the previous evaluation of the
  condition, so a verb that writes to the tree, such as `format`, never counts
  as a change the next call made.

The runner keeps the newest 20 runs per work tree, removes older ones when a
run starts and says which it removed, because run state needs a bounded
retention (REQ-2962). The number 20 is a default I chose: enough to compare a
week of nightly runs, and a count a person can list on one screen.

The runner reads the terms once, at start, and holds them in its own process
for the whole run. Nothing it does after start reads a bound back from a file,
so editing `run.toml` changes no bound (REQ-0874). Before each call it checks,
in this order, and the first that fails ends the run. The order decides which
ending is reported when two checks fail at once. A changed term comes first,
because a run that tried to change its terms is misbehaving whichever bound
it also reached, and the person needs to hear that before anything else:

1. The sha256 of `run.toml`, of `prompt.md` and of the work tree's
   `.claude/settings.json` still match what the runner recorded at start. A
   mismatch ends the run as `tampered`, because a run that tries to change its
   own terms or its own authority is misbehaving, even where the change to
   `run.toml` has no effect.
2. The iterations done are below the ceiling, or the run ends as `ceiling`.
3. The spend so far plus the largest single iteration's spend so far is
   within the budget, or the run ends as `budget` (REQ-0878). Before the first
   call nothing has been spent, so the first call starts whenever the budget
   is above 0.

When all three hold, it starts the call (REQ-0876), and so a prompt that
tells the model to keep going changes nothing. Each call is:

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

It carries the prompt's bytes from the runner's memory. The runner adds the
allow rule for Edit and Write of the run's `progress/progress.md` to every
call itself, because the run id in that path is fixed only when `start` runs,
so the person can't name it in an `--allowed-tools` rule. Without that rule,
`dontAsk` would deny every write to the progress file that REQ-0882 depends
on. It passes no
`--resume` and no `--continue`, so each call is a new session (RES-0300), and
it passes `--no-session-persistence` because nothing resumes a call, so a
saved session would only fill the person's session list. `--permission-prompts
none` is there because nobody is present to answer a prompt, and `claude
--help` documents it as denying whatever would prompt; RES-0300 didn't
observe it in a call. The
fixed preamble names the progress file by its absolute path, states the
condition, and says that the runner decides completion and holds the bounds.
It is the same text on every call, with no iteration number or spend in it, so
every iteration begins from the same stated context (REQ-0880).
`--setting-sources project` keeps the person's installed plugins out, so in a
directory with no project settings the harness a call loads is the list of
directories the person named, plus `meow-loop`'s own directory, which the
runner always adds so the unit's hook loads in every call of a run.
RES-0300 saw a named unit load under `-p`, and never saw a hook fire in a
call. A repository whose own settings
enable a plugin adds that plugin too, as far as the documentation says, and
RES-0300 didn't observe it.
`--max-budget-usd` gives the platform the budget left as a second limit on a
single call, and is never the budget's bound, because the platform checks it
after the spend.

After each call the runner checks, in this order, and the first that ends
the run decides its ending:

1. The same three hashes, ending the run as `tampered`. A call that edits
   `run.toml` and also makes the verbs pass therefore ends `tampered` and not
   `finished`, because a run that tried to change its own terms can't have its
   success trusted.
2. The result's `total_cost_usd`. A call that prints no result, or a result
   without that field, ends the run as `unmetered`, because a budget missing a
   term is no longer enforced. Otherwise the runner adds the cost to the
   spend.
3. The result's subtype. `error_max_budget_usd` ends the run as `budget`.
4. The condition, evaluated only when the tree changed, ending the run as
   `finished` when it holds.
5. The idle rule, ending the run as `idle`.

The two meter checks come before the condition, because a call whose spend
can't be counted, or that passed its own cap, has broken a bound the person
stated, and the person needs to hear about a broken bound before a success,
as with a changed term. So a call that prints no cost and also makes the
verbs pass ends `unmetered` with exit 1, and the log line records that the
condition wasn't evaluated.

Any other error in a result is logged and counts as an iteration, bounded by the ceiling and the
budget like any other, because one failed call, such as a rate limit, can
pass on the next attempt. A call that fails the same way every time spends
the run's iterations up to the ceiling, and the log's exit status on each
line is how the person sees it.

An iteration changes nothing when the work tree's id and the sha256 of
`progress.md` are both the same after the call as before it. Two such
iterations in a row end the run as `idle` (REQ-0886). The tree id is
`ledger::tree_id`, and an iteration whose tree can't be identified, such as
one with a dirty submodule, counts as a change and is logged as unidentified,
so the ceiling and the budget still bound it.

A run ends in exactly one of six named endings, written into `run.toml` and
printed on the last line, each with one audience, the person who started it:

| Ending      | Means                                                      | Exit status |
| ----------- | ---------------------------------------------------------- | ----------- |
| `finished`  | The condition held at the current tree                     | 0           |
| `budget`    | The next call could pass the budget, or a call hit its cap | 1           |
| `ceiling`   | The stated number of iterations ran                        | 1           |
| `idle`      | Two iterations in a row changed nothing                    | 1           |
| `tampered`  | `run.toml` or `prompt.md` changed during the run           | 1           |
| `unmetered` | A call reported no cost, so the budget can't be summed     | 1           |

Every ending other than `finished` exits 1, because the status answers the
one question a script around the runner asks, whether the condition held. The
ending printed on the last line and written into `run.toml` says why it
didn't, and is the contract for anything that needs the reason.

A run with no ending in its `run.toml` was interrupted, and the log's last
line says how far it got. Stopping and cancelling are the next decisions'.

Four guards stop the model starting a run, because each covers a path the
others miss (REQ-0894):

- The skill `meow-loop:loop` sets `disable-model-invocation: true`. When a
  person invokes it, it helps them write the prompt file and prints the start
  command for them to run in a terminal. The model never runs the command,
  because a start from a model session is refused.
- The runner refuses to start with exit status 3 when `CLAUDECODE` is set,
  which RES-0300 observed in a Bash call from an interactive Claude Code
  session. A person starts a run from a terminal outside Claude Code, such as
  a tmux window.
- The unit's PreToolUse hook denies a Bash command that runs `meow-loop` with
  `start`, or the unit's native program with `loop start`, which is what
  `bin/meow-loop` runs, in any session where the unit is installed, and in every call of a
  run, because the runner names its own unit's directory with `--plugin-dir`
  on each call and `--setting-sources project` would otherwise keep the
  installed unit out (RES-0300). RES-0300 saw the unit load under `-p` and
  didn't see its hook fire there, so inside a run this guard is unobserved.
  It also denies an Edit or a Write of any path
  under the runs directory other than a run's `progress/progress.md`. The
  hash check stays the guard that decides, because a hook that fails to load
  must not leave a changed `run.toml` unnoticed.
- Each call passes `--disallowedTools "Bash(meow-loop *)"`, which RES-0300
  observed refusing the command both alone and inside a compound line, and
  `--disallowedTools "Bash(meow loop *)"` for the native program under its own
  name, so a run can't start a nested run by either name.

After this decision a person can start an unattended run from a terminal
with a prompt, a condition on the verbs, a ceiling and a budget. The run
repeats the prompt in fresh sessions until the verbs pass, the ceiling is
reached, the next call could pass the budget, two iterations change nothing,
its terms are changed or a call can't be metered. What still doesn't work:

- Completion rests on the verbs alone. Nothing reads the plan's task marks or
  binds the result to kept evidence, and nothing keeps a run inside one step
  (REQ-0884, REQ-0888).
- Stopping is the terminal's interrupt. Nothing records who stopped a run or
  when, and an interrupted iteration can leave the tree part-way through an
  edit (REQ-0890, REQ-0892, REQ-2654, REQ-2656, REQ-2658, REQ-2660).
- The allowed rules and the plugin directories are what the person typed,
  plus whatever the work tree's `.claude/settings.json` held at start, which
  the hash check keeps fixed for the run. `dontAsk` is the only mode. The runner doesn't read the authority that
  ADR-2000's `meow-unattended plan` records from the repository's
  declaration, and the run removes no tool beyond the deny rules on the runner
  (REQ-2372, REQ-2390).
- The condition runs the command resolved at start, and that command reads
  files in the work tree, such as its task runner's configuration and the
  tests, which a call can change. The runner guards which command runs and
  not the work it checks, because those files are the work the run is meant
  to change.
- Other files in the work tree load into every call and aren't hashed: the
  repository's instruction files, its skills and agents, and `.mcp.json`. A
  call can change them, so the next call starts from a different context,
  though not with more authority, because what may run is in
  `.claude/settings.json`. The user's own instruction files and memory may
  load too, and RES-0300 didn't examine them. A call that writes the user's
  memory would carry state outside `progress.md`, where neither the idle rule
  nor the hash check sees it. So REQ-0880's "same context" holds for the
  prompt and the preamble, and not yet for those files.
- A run whose edits are all denied, and whose model writes only
  `progress.md`, never goes idle and runs to its ceiling or its budget, as the
  premortem says. Until the escalation list exists, the only signal is the
  count of `permission_denials` on each line of `log.jsonl`. The log isn't
  hashed, and the hook guards it only where the hook fires, so a call that
  rewrites the log can erase that signal without ending the run.
- Six behaviours the decision relies on are unobserved, and a stand-in
  `claude` can't show any of them, so the first real run is where each shows:
  - whether `--add-dir` and the runner's allow rule let the model write
    `progress.md` under `dontAsk`;
  - what `--permission-prompts none` does in a call;
  - which plugins a repository's own settings add under `--setting-sources
project`;
  - whether the unit's hook fires in a `-p` call. The hash check decides
    whether the terms changed either way;
  - whether `CLAUDECODE` is set in a Bash call inside a `-p` call, which
    RES-0300 saw only in an interactive session;
  - whether the user's own instruction files and memory load in a call under
    `--setting-sources project`.
- The run has no sandbox, no network allowlist and no credential scrubbing
  (REQ-2396, REQ-2398, REQ-2400).

## Why

RES-0024 and RES-0059 found that a bound the model is asked to respect is one
it can talk past, that the budget belongs before the next call, that each
iteration starts from the same context with progress in a file, and that two
iterations changing nothing end the run. RES-0300 observed on Claude Code
2.1.280 that each `claude -p` call is a new session reporting
`total_cost_usd`, that `--setting-sources project` with `--plugin-dir` loads
only the named plugins in a directory with no project settings, that a deny rule refuses a matching command, and that
the platform's spend cap is checked only after the spend. It also found that
the official loop holds its ceiling in a work tree file the model can edit.

A process the model can't reach is the one place a bound holds whatever the
model says. The runner is that process, which is why it reads its terms once
and keeps them in memory.

## Alternatives

| Option                                                                | Better at                                                     | Why it lost                                                                                                                                                      |
| --------------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A Stop hook inside one session, as the official loop does             | Starts from a slash command, with no terminal needed          | The conversation grows each iteration, so no iteration starts from the same context and REQ-0880 fails (RES-0300)                                                |
| Point at the official loop plugin                                     | No unit to build                                              | It ends on a phrase, has no budget and no idle rule, and holds its bound where the model can reach it (RES-0024, RES-0300)                                       |
| Check only that spend so far is below the budget                      | One more call, so more work per run                           | The call it lets through can spend past the budget by its whole cost, and a stated budget is a limit a person chose                                              |
| Rely on `--max-budget-usd` alone                                      | No arithmetic in the runner                                   | The platform checks it after the spend, and RES-0300 saw a call spend eleven times its cap                                                                       |
| Keep the run in `.meowpaw/runs/` in the repository                    | The person finds the run beside the work tree                 | Run state belongs outside the repository (REQ-3072), and every write to it would change the tree id that idle detection reads                                    |
| `--bare` with `--plugin-dir`, in place of `--setting-sources project` | Could keep out the plugins a repository's own settings enable | Unobserved: RES-0300 didn't try it, and RES-0074 records `--bare` as loading no plugins, which may drop the named directory too. Observing it is a trigger below |
| A shell script in the unit                                            | No native feature                                             | The unit's program has to hash, parse JSON and compute the tree id the ledger computes, and every other unit's program is the native tool (ADR-1110)             |
| Do nothing                                                            | No new unit, no new failure state                             | Nothing in the harness can run unattended, and a person copying the official loop gets a ceiling the model can edit and no budget at all                         |

## What it costs

The person starts a run from a terminal outside Claude Code, which is one more
window than a slash command. Each iteration pays for loading a fresh session,
out of the person's stated budget. The prompt cache holds for about five
minutes between calls, so a slow iteration pays for the whole context again,
also out of that budget, which is why the forecast's margin grows with slow
iterations. The run's verbs run after every
iteration that changed the tree, so a slow test suite multiplies the run's
wall time by the number of iterations that changed something. A call that costs more than
the largest before it can still pass the budget, by as much as the platform
lets a call pass its own cap, which RES-0300 saw reach eleven times. The budget is
in the platform's own estimate, which RES-0074 records can differ from the
bill. The forecast stops a run while up to one iteration's spend of the
budget is still unused, which the person pays in work left undone. A person
who turned state off with `MEOWPAW_STATE=off` can't run a loop at all, because
the run's log and lock are state. Every repository that installs the unit keeps its hook on every Bash,
Edit and Write call, and the skill's description on every turn.

The state directory grows by one directory per run, capped at 20 runs per
work tree. Left alone for a month, a work tree holds at most 20 runs, and
nothing waits on a person.

## What would reverse it

- The platform checks `--max-budget-usd` before a request. The forecast would
  then move into the call, and the runner would keep only the sum.
- `claude -p` stops reporting `total_cost_usd`. Every run would end
  `unmetered` after its first call, and the budget would need another meter.
- The platform ships a loop that holds its bounds outside the session and
  starts each iteration fresh. The unit would then wrap that loop, and the
  runner would retire.

Six unobserved behaviours would amend the decision and not reverse it, if
the first real run shows them false:

- The model can't write `progress.md` under `dontAsk` with `--add-dir` and
  the runner's allow rule. The progress file then moves into the work tree,
  where the model's other edits land, and the idle rule reads the tree id
  alone; or the question of the permission mode reopens.
- `--permission-prompts none` refuses a call or waits on a prompt. The runner
  then drops the flag and relies on `dontAsk`, which RES-0300 saw deny a
  command without prompting.
- A repository's own settings add plugins to a call. The runner then moves to
  `--bare` with `--plugin-dir`, once an observation shows that the named
  directory loads under `--bare`.
- The unit's hook doesn't fire in a `-p` call. The hash check then stays the
  only guard of the terms inside a run, the deny rule and the `CLAUDECODE`
  refusal the only guards against a nested start, and the hook guards only
  interactive sessions.
- `CLAUDECODE` isn't set in a Bash call inside a `-p` call. The runner then
  sets a variable of its own in each call's environment and refuses a start
  that carries it, because otherwise the deny rule and the hook are the only
  guards against a nested start.
- The user's own instruction files or memory load in a call. The runner then
  moves to `--bare` with `--plugin-dir`, or names the files it holds fixed,
  once an observation shows which of the two keeps them out.

## Consequences

- A unit `plugins/meow-loop/` with `bin/meow-loop`, `skills/loop/SKILL.md`,
  `hooks/hooks.json`, a README, `budget.toml`, `requires.toml`,
  `.claude-plugin/plugin.json` and an entry in `.claude-plugin/marketplace.json`.
- A native feature `loop` in `crates/meow`, which compiles in the `verbs`
  feature, and a line in `build-units`.
- A specification of the unit, written at the spec step.
- Fixtures that run the runner with a stand-in `claude` on the path, so no
  model runs in CI, and that clear `CLAUDECODE` from the runner's environment,
  because the gate itself often runs inside a Claude Code session.

## How I will know it was realised

Each fixture puts a stand-in `claude` on the path. The stand-in records its
argv and stdin to a call log, prints a JSON result with a chosen
`total_cost_usd`, and can edit a file. Unless a criterion says otherwise, the
stand-in changes a tracked file on each call, so the idle rule doesn't end the
run before the criterion's count.

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
6. Every recorded call carries byte-identical stdin and preamble, and no
   `--resume` or `--continue` (REQ-0880). Every recorded argv carries
   both deny rules and names `meow-loop`'s own
   directory with `--plugin-dir` (REQ-0894, REQ-0874).
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
11. `start` exits 3 and leaves no run directory in each of five states: outside
    a git work tree, with `MEOWPAW_STATE=off`, with no `claude` on the path,
    with a named verb that resolves to no command, and while another process
    holds the work tree's lock.
12. After a run is killed part-way with SIGKILL, a new `start` in the same
    work tree takes the lock and runs.
13. Every requirement ADR-2010 addresses lands in exactly one closed task.

## What this does not settle

- Completion from evidence bound to the tree, the plan's marks, and keeping a
  run inside one step.
- Stopping a run, what an interrupted iteration leaves, and the record of who
  stopped it.
- Where the run's authority comes from: the permission mode, the loaded
  units, the tools removed and the gates it may cross.
- Isolation of the filesystem and the network, and scrubbing credentials.
- Approving a record during a run, and the escalation list after it.
- Condition kinds other than verbs.
- Permission modes other than `dontAsk`, until an observation shows how each
  behaves in a call with nobody to answer a prompt.

## Strongest objection

The guards against a model starting a run are not a boundary. A model that
hides the runner's name from the command text, in a script, a variable or a
command substitution, and removes `CLAUDECODE` from its environment passes
all four, because the hook and the deny rule match the command text they are
shown and the variable is one a process can drop, which RES-0300 expects but
didn't test. Inside a run, a hook written into `.claude/settings.json` would
run outside any Bash call, and the hash check ends the run before the next
call reads it. The guards make a start an evasion that takes two deliberate acts,
hiding the name and dropping the variable, and never a side effect of a task the person asked for, which is what
"on its own initiative" in REQ-0894 asks. A boundary needs the sandbox the
unattended decisions will add. I keep the decision, because no guard a unit
can ship is a boundary, and the alternative is to ship no runner.

## Premortem

The run spent its whole budget and ended `budget` with nothing done. The
permission mode denied every edit, and each iteration wrote only
`progress.md` saying it couldn't edit, so idle detection never fired. The log
showed the permission denials climbing on every line, and nobody read it
until morning. The count of denials is in each log line for this reason, and
the escalation list decided later is where it gets read.
