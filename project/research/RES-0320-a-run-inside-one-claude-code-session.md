---
id: RES-0320
artifact: research
status: approved
revised: 2026-10-03
elaborates: RES-0300, RES-0074
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A run can live inside one Claude Code session, held by a command Stop hook, and the platform keeps its conversation bounded by compaction

## Summary

Claude Code now gives a session three ways to keep working without a person
typing each turn: `/loop`, `/goal` and a Stop hook. Only the Stop hook lets a
program, and not a model, decide whether the next turn starts: a `command`
hook that exits 2 or returns `decision: "block"` keeps the session working,
and its `reason` reaches the model as the next instruction. The platform
compacts the conversation when it nears the window, so a long run doesn't
overflow. It still doesn't start each turn from the same context, which is
the reason ADR-2010 gave for keeping the loop outside the session. A Stop hook
doesn't fire on a person's interrupt, and a skill marked
`disable-model-invocation: true` can't be started by the model or by a
scheduled task. So a person can start and stop a run from inside the session,
and the model can't do either.

This note covers what the platform offers a run inside one session. It
doesn't measure a run: nothing here was built or timed.

## The question

ADR-2010 put the loop in a program outside Claude Code, started from a
terminal, and rejected "a Stop hook inside one session" because the
conversation grows each iteration, so no iteration starts from the same context (RES-0300). The
owner asked on 2026-10-03 for the loop and the unattended run to work inside
the session they are typing in, with no command run elsewhere. What does the
platform now offer for that, and which of the loop's requirements can it hold?

## Method

On 2026-10-03 I read five pages of the Claude Code documentation: scheduled
tasks and `/loop`, `/goal`, the hooks reference, the hooks guide, skills and
costs. I compared what each says against the requirements ADR-2010 addresses
and against the guards SPC-1201 states. I also read the running session's own
tool list, which has `ScheduleWakeup` and the `/loop` skill. Nothing was
implemented, so each conclusion is a reading of the documentation and not an
observation of a run.

## Findings

### Three ways to keep a session working, and only one is decided by a program

`/loop` re-runs a prompt on an interval, or at a delay the model chooses each
iteration. In the self-paced form the model ends the loop: "Claude can also end
the loop on its own once the task is complete" by calling `ScheduleWakeup` with
`stop: true`. A loop is session-scoped, a recurring task expires after seven
days, and "tasks only fire while Claude Code is running and idle".

`/goal` sets a condition and starts another turn until it holds. It is "a
wrapper around a session-scoped prompt-based Stop hook": after each turn a
small model reads "the condition and the conversation so far" and returns met,
not yet met or impossible. The evaluator "doesn't run commands or read files
independently", so it judges only what the conversation shows.

A Stop hook of type `command` runs a program after every turn. It "blocks the
stopping action through exit code 2 or through a top-level `decision` field",
and "the `reason` field is fed to Claude as context so it understands why it
cannot stop". The hook's input carries `stop_hook_active`, so the program can
tell a turn it started from one the person started.

The run's finish condition has to be computed from the record and its bounds held outside the model, as RES-0074 found, so `/loop` loses because the model ends it and `/goal`
loses because a model judges it from the conversation. The command Stop hook
is the one form where a program decides and the model can't extend the run.

### The platform caps a Stop hook that blocks without progress

"Claude Code overrides a Stop hook after it blocks eight times in a row without
progress." The guide's own example lets the session stop whenever
`stop_hook_active` is true. A run that blocks on every turn therefore has to
show progress the platform counts, or the platform ends it. `/goal` describes
progress as tool use: it stops after "no tool use for several turns in a row".
An iteration of the chain always calls tools, so the cap ends only an
iteration that does nothing, which a run already ends after two idle iterations.

### The conversation grows, and compaction bounds it

Claude Code "sends your full conversation with every request", and
auto-compaction "summarizes conversation history when approaching context
limits". So an in-session run doesn't overflow, which was half of RES-0300's
concern. The other half stands: after the first iteration each turn starts
from a different context, the earlier turns or a summary of them. No in-session form gives each iteration the same context. What a
program can give is the same stated input: the hook's `reason` can restate
the frozen prompt and the path of the progress file on every block, so every
iteration receives the same instruction and the same durable state, whatever
the conversation holds.

### A person starts and stops the run, and the model can do neither

A skill with `disable-model-invocation: true` runs only when a person types
it: "Claude can invoke it via the Skill tool: No", and since v2.1.196 it also
doesn't run "when a scheduled task fires with the skill as its prompt". So a
start command in that form is one only a person can run inside the session.

"`Stop` hooks fire whenever Claude finishes responding ... They don't fire on
user interrupts." Pressing `Esc` therefore ends the turn without the hook
starting another, so a person can stop a run at any point. The documentation I read doesn't say
what happens to the run's state after an interrupt. A program that keeps the
run active would restart it at the end of the person's next turn, so the
person's next prompt has to end the run. A `UserPromptSubmit` hook, which runs
when the person sends a prompt, can do that. I didn't read its reference
section, so its input fields are unverified.

A `PreToolUse` hook "fires before any permission-mode check, in every
permission mode", and a deny "blocks the tool even in `bypassPermissions`
mode". So the guard ADR-2010 runs on the run's own state files holds inside
the session as well.

### Spend is reported to the person, and a hook's view of it is unverified

`/usage` shows the session's cost, computed "locally from token counts at list
price", and the status line carries the same figure. `--max-budget-usd` is a
command-line flag for a `-p` call and has no in-session form in what I read.
A hook's input includes the transcript path, and the transcript records each
response's token usage, so a program can count tokens. I found no field that
hands a hook the session's spend in dollars.

## Conclusions

1. A command Stop hook is the only in-session form where a program, and not a
   model, decides whether the next turn starts.
2. `/loop` and `/goal` both let a model end or judge the run, so neither holds
   a finish condition computed from the record.
3. The hook's `reason` can restate the frozen prompt and the progress file on
   every iteration, which gives each iteration the same stated input, though
   not the same context.
4. Compaction keeps a long run inside the window, so the growing conversation
   costs tokens and summarised history but doesn't stop the run.
5. A rule that each iteration starts from the same stated context can't hold inside one session, and a decision that moves the run into the session has to replace it.
6. A skill marked `disable-model-invocation: true` is started only by a person,
   and not by the model or a scheduled task.
7. A Stop hook doesn't fire on an interrupt, so `Esc` stops a run, and the
   person's next prompt has to end the run's state, or the hook restarts it.
8. A `PreToolUse` deny holds in every permission mode, so the run's state can
   be kept out of the model's reach.
9. The platform ends a Stop hook that blocks eight times in a row without
   progress, which an iteration that calls tools doesn't trigger.
10. A hook can count the run's tokens from the transcript, and no field I read
    gives it the spend in dollars.

## Sources

- [Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks), read 2026-10-03
  - `/loop`, its fixed and self-paced forms, the model ending a self-paced loop
    with `ScheduleWakeup`, the seven-day expiry, and that tasks fire only while
    the session is open and idle.
- [Keep Claude working toward a goal](https://code.claude.com/docs/en/goal), read 2026-10-03 -
  `/goal` as a prompt-based Stop hook, its evaluator reading only the
  conversation, and its stop after several turns without tool use.
- [Hooks reference](https://code.claude.com/docs/en/hooks), read 2026-10-03 - the Stop hook's
  input, `stop_hook_active`, blocking by exit 2 or `decision: "block"`, the
  `reason` fed to Claude, and `${CLAUDE_PLUGIN_DATA}`.
- [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide), read 2026-10-03 -
  the block cap of eight, that Stop hooks don't fire on interrupts, and that a
  `PreToolUse` deny holds in every permission mode.
- [Skills](https://code.claude.com/docs/en/skills), read 2026-10-03 -
  `disable-model-invocation: true`, which the model and a scheduled task can't
  invoke.
- [Manage costs effectively](https://code.claude.com/docs/en/costs), read 2026-10-03 - `/usage`,
  the locally computed cost, auto-compaction, and `--max-budget-usd`.
- [RES-0300](RES-0300-print-mode-as-a-loop-runner-observed.md), read 2026-10-03 - the evidence ADR-2010 rejected the
  in-session loop on.
