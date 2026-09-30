---
id: RES-0300
artifact: research
status: approved
revised: 2026-09-29
elaborates: RES-0024, RES-0059, RES-0074
---

# Print mode can run each iteration of a loop, and its spend cap is checked after the spend

## Summary

On Claude Code 2.1.280, one `claude -p` call per iteration gives a runner what
a loop outside the model needs: each call starts a new session, reports its
cost as `total_cost_usd` in its result, loads a plugin named by `--plugin-dir`,
and denies a command matched by a `--disallowedTools` rule, recording the
denial in `permission_denials`. In a directory with no project settings,
`--setting-sources project` left out every plugin the user had installed, so
the named directory and two built-in plugins were all that loaded. The platform's own spend cap, `--max-budget-usd`, is
checked after the spend and not before it: a cap of $0.001 ended a call only
after three turns and $0.011, eleven times the cap. The official loop plugin runs inside
one session and keeps its iteration count in a file in the work tree, which
the model can edit.

Research for the loop runner. It adds observations to
[RES-0024-loop.md](RES-0024-loop.md) and [RES-0059-loop.md](RES-0059-loop.md),
which ran nothing, and to [RES-0074-unattended-mode.md](RES-0074-unattended-mode.md),
which read the documentation for print mode. It covers the result fields, the
loading of plugins, rule matching and the spend cap. It leaves out sandboxing,
the permission modes other than `dontAsk`, what `--permission-prompts none`
does in a call, whether `--add-dir` lets an edit through, a call inside a
repository that declares its own settings, the user's own instruction files
and memory, which this record didn't examine, and streaming input.

## The question

A runner that repeats a prompt has to count calls, sum their cost before the
next one, start each from the same context and stop a model from starting a
run of its own. Each of those depends on what print mode reports and enforces,
and the earlier research read the documentation without running a call. The
assumption behind the question is that the model's session is the wrong place
to hold the bounds, so the question is also whether the official loop, which
holds them there, can be reused.

## Method

I ran four calls on 2026-09-28 on this machine, a Mac on arm64, with Claude
Code 2.1.280 from `claude --version`, in a scratch directory outside any
repository. Each passed `--model haiku`, `--no-session-persistence` and a
`--max-budget-usd` cap:

1. A one-word reply with `--output-format stream-json --verbose` and
   `--plugin-dir` naming this repository's `plugins/meow-verbs`, to read the
   init message and the result.
2. The same, adding `--setting-sources project`, `--permission-mode dontAsk`
   and `--disallowedTools "Bash(meow-loop *)"`, with a prompt asking for one
   Bash call running `meow-loop start --probe`.
3. `--setting-sources project`, `--permission-mode dontAsk`,
   `--allowedTools Bash` and the same deny rule, with a prompt asking for
   `echo hi`, then `meow-loop start --probe`, then
   `true && meow-loop start --probe .`, so the deny rule was the only thing
   that could refuse the second and third.
4. `--output-format json` with `--max-budget-usd 0.001`, asking for two Bash
   calls.

The four calls cost $0.071 together, by their own `total_cost_usd`. I also
read `claude --help`, printed which environment variables a Bash tool call
inherits in my own interactive session, and read the official loop plugin's
hook from GitHub at commit `c2022d3698c2`.

I didn't observe `--max-turns`, which `claude --help` doesn't list. A
reviewer recalls earlier releases accepting it in print mode, so it may be a
hidden flag, and I didn't try it. Nor did I observe a call
that fails before it prints a result, nor what a nested `claude -p` inherits
from a parent that isn't Claude Code. I didn't observe the environment inside
a `claude -p` call, a call under any permission mode other than `dontAsk`, a
call with `--permission-prompts none` or `--add-dir`, a hook refusing
anything, or `--bare` combined with `--plugin-dir`. Preparing a second round
of calls, inside a repository whose settings enable a plugin, was refused by
the session's permission settings, so none of those gaps is closed here.

## Findings

### Each call is a new session, and its result carries its cost

Every call printed a different `session_id`, and none passed `--resume` or
`--continue`, so a call begins from the prompt and the loaded configuration
alone. A new session isn't an identical context, because the user's own
instruction files and memory also load, and this record didn't examine them.
The result message carried `type`, `subtype`, `is_error`, `num_turns`,
`total_cost_usd`, `permission_denials`, `terminal_reason`, `stop_reason`,
`modelUsage` and `usage`, among others. The first call returned
`subtype: success`, `num_turns: 1` and `total_cost_usd: 0.0204211`. RES-0074
already records that the documentation calls the cost a client-side estimate
that can differ from the bill.

### A plugin directory loads under print mode, and the user's plugins load too unless the setting sources leave them out

In call 1, the init message listed `meow-verbs` with the source
`meow-verbs@inline` and its skill `meow-verbs:verify`. It also listed
seventeen more plugins: every plugin this user has installed, and the built-in
`agents-md` and `telemetry`. In call 2, with `--setting-sources project`, the
list was `meow-verbs`, `agents-md` and `telemetry`. So a call loads the
harness by name only when the runner also removes the user's settings, and a
runner passing `--plugin-dir` alone gets whatever the person running it
installed. The scratch directory had no project settings, so this doesn't show
what a call loads inside a repository whose `.claude/settings.json` enables a
plugin, which `--setting-sources project` still reads. `--bare`, which RES-0074
records as loading no plugins, combined with `--plugin-dir` is an alternative
nobody tried.

### A deny rule refuses a command, compound or not, and the refusal is in the result

In call 3, `echo hi` ran and printed `hi`. `meow-loop start --probe` and
`true && meow-loop start --probe .` were each refused with "Permission to use
Bash with command ... has been denied", and both appear in the result's
`permission_denials` with the command the model tried. The rule matched the
second command of a compound line. I didn't try an absolute path to the
program, `bash -c` or `env`, so the rule is shown to match these two forms and
no others.

### The platform's spend cap is checked after the spend

Call 4 ended with `subtype: error_max_budget_usd`, `terminal_reason:
budget_exhausted`, `errors: ["Reached maximum budget ($0.001)"]`, exit status
1 and `total_cost_usd: 0.0109538` after three turns. So the platform ended
the call only after it had spent eleven times the cap. Call 1, with different
flags and a one-word reply, cost $0.0204 in a single turn, twenty times this
cap, so I infer that call 4's first turn already spent past the cap and that
two more turns ran after it. The cap therefore isn't enforced even between
turns. I didn't split call 4's usage by turn, so this one call can't show when
the platform checks. RES-0024 says a budget has to be checked before the next
paid call, and this cap is checked after it.

### A Bash call from an interactive Claude Code session carries a marker in its environment

A Bash tool call in my interactive session inherits `CLAUDECODE=1`,
`CLAUDE_CODE_ENTRYPOINT=cli`, `CLAUDE_CODE_SESSION_ID` and others. A program
can read `CLAUDECODE` to tell that such a session started it, and a person
running the same program from a plain terminal has no such variable. I saw
this only in an interactive session, not inside a `claude -p` call, where
`CLAUDE_CODE_ENTRYPOINT` at least could differ. I didn't try removing the
variable. `env -u` removes a variable for any program it starts, so I expect a
model to be able to remove it the same way, but that is untested.

### The official loop keeps its bound where the model can reach it

The official plugin's `stop-hook.sh` reads `iteration`, `max_iterations` and
`completion_promise` from `.claude/ralph-loop.local.md`, a file in the work
tree. It blocks the session's exit with `"decision": "block"` and feeds the
same prompt back as the reason, and its README says the loop runs "inside your
current session". So the conversation grows with each iteration, and the model
can edit the ceiling it runs under with an ordinary file edit.

## The case against one call per iteration

The findings also carry the case against the leading option. Each call pays
for a fresh session, and a one-word call cost $0.020. Nothing observed limits
the turns or the spend of one call, since print mode lists no `--max-turns`
and the platform's cap let a call reach eleven times its value. A call that
prints no result can't be metered at all. A new session per call also drops
the context the official loop keeps, so whatever the model learnt in one
iteration survives only as far as it writes it down.

The official loop avoids the start-up cost and keeps its context, and still
loses, because it keeps its ceiling in a work tree file the model edits like
any other. A bound the model can change bounds nothing. Of the costs above,
a runner can measure the spend after each call that reports it. The spend
inside a call, and any call that prints no result, are the part it can't
measure, and a person accepts that part when they start a run.

## Conclusions

1. A loop runner can meter each iteration from the result's `total_cost_usd`,
   and must treat a call that prints no result as unmetered, because a sum
   missing a term enforces nothing. That figure is the platform's own
   client-side estimate, which RES-0074 records can differ from the bill, so a
   budget summed from it bounds the estimate and not the invoice.
2. A budget has to be checked by something other than the platform's cap,
   before each call, because the cap stopped a call only after it had spent
   past the cap. A check before a call sees only what earlier calls spent, so
   the run can still pass the budget by up to one call's cost, and nothing
   observed limits how large that one call can get.
3. In a directory with no project settings, loading the harness by name needs
   the user's settings left out as well as the plugin directory named, because
   `--plugin-dir` alone adds to what the person installed. What a repository's
   own settings add under `--setting-sources project` is unobserved.
4. A deny rule can refuse a start from a model session, and a program can read
   `CLAUDECODE` to tell that an interactive session started it. Neither is a
   boundary, because the rule matched only the two forms tried, and the
   marker is a variable I expect a process can drop, though I didn't test
   that. No hook was tried.
5. A loop's count and ceiling have to sit where the model can't edit them,
   because a bound the model can change bounds nothing. The official loop
   keeps them in a work tree file the model could change with an ordinary
   edit, though no call here saw a model edit it, so the official loop can't
   be reused as it is.
6. Each call starts a new session, but that isn't shown to be the same
   context on every call, because the user's own instruction files and memory
   may load in each call and this record didn't examine them. A runner that
   relies on `--setting-sources project` to keep a call's context fixed has to
   treat those files as unobserved.

## Sources

- `claude --version` and `claude --help`, run 2026-09-28 - version 2.1.280;
  `--print`, `--output-format`, `--plugin-dir`, `--setting-sources`,
  `--disallowedTools`, `--allowedTools`, `--permission-mode`,
  `--max-budget-usd` and `--no-session-persistence`, and no `--max-turns` in
  the listing. The listing also documents `--permission-prompts none` as
  denying anything that would prompt while the permission mode decides the
  rest; no call here used it.
- A Bash tool call's environment, printed 2026-09-28 in my interactive Claude
  Code session - `CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT` and
  `CLAUDE_CODE_SESSION_ID`.
- Four `claude -p` calls run 2026-09-28 as the method says - the result fields,
  the plugins loaded with and without `--setting-sources project`, the deny
  rule's matches and the spend cap's overshoot.
- [anthropics/claude-code `plugins/ralph-wiggum`](https://github.com/anthropics/claude-code/tree/c2022d3698c2/plugins/ralph-wiggum), read 2026-09-28,
  at commit `c2022d3698c2` - `hooks/stop-hook.sh` reading its
  bound from `.claude/ralph-loop.local.md` and blocking the exit with the same
  prompt, and the README's "inside your current session".
- [RES-0024-loop.md](RES-0024-loop.md), read 2026-09-28 - a budget checked
  before the next paid call, not after it.
- [RES-0059-loop.md](RES-0059-loop.md), read 2026-09-28 - the runner, not
  the model, enforcing the ceiling, two iterations that change nothing ending
  the run, and a loop the model can't invoke.
- [RES-0074-unattended-mode.md](RES-0074-unattended-mode.md), read 2026-09-28 - `total_cost_usd`
  as a client-side estimate, and `--bare` loading no plugins.
