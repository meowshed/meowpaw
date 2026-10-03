---
id: ADR-2380
artifact: adr
status: approved
revised: 2026-10-03
addresses:
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
    REQ-2370,
    REQ-2380,
    REQ-2382,
    REQ-2384,
    REQ-2386,
    REQ-2388,
    REQ-2402,
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
    REQ-3714,
    REQ-3716,
    REQ-3718,
    REQ-3720,
    REQ-3722,
  ]
postpones: [REQ-2396, REQ-2398, REQ-2400, REQ-2404]
supersedes: [ADR-2000, ADR-2010, ADR-2020]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2380. A run lives in the session, and an unattended run decides, merges and releases on its own

## Decision

A run of the chain starts, repeats and ends inside the Claude Code session
where a person types its start command, and no command outside the session is
needed (REQ-3700). The run is unattended: it decides each gate and question
itself, lands and releases its own work, and the person reads its report
afterwards. The owner chose each of these on 2026-10-03, and this record
states them as the owner's choices.

`meow-loop` holds the run with three command hooks and one skill:

- `/meow-loop:run` is a skill with `disable-model-invocation: true`, so only a
  person can invoke it (RES-0320, conclusion 6). Its arguments are the three
  bounds: `--iterations`, `--hours` and `--tokens`.
- A `UserPromptSubmit` hook reads the person's prompt. When the prompt is the
  start command, the hook writes the run's state under
  `<state>/meowpaw/runs/<work tree key>/<run id>/` with the session's id, the
  bounds, the start time and the open counts from `paw status`. A program
  starts the run from the person's own prompt, so the model can't start one
  (REQ-0894). When a run is active and the prompt is anything else, the hook
  ends the run as `cancelled` and records who cancelled it and when, because a
  `Stop` hook doesn't fire on `Esc` and the run would restart at the end of the
  person's next turn (REQ-3712, REQ-0890, RES-0320 conclusion 7).
- A `Stop` hook decides whether the next iteration starts. It reads the run's
  state for this session, computes the open counts with the `record` code
  `paw status` uses, and reads the tree id. It allows the stop with the ending
  `finished` when no requirement and no defect is open, where a postponed
  requirement isn't open (REQ-3704, REQ-3706). It allows the stop with
  `ceiling`, `time` or `tokens` when a bound is reached, and the token count
  comes from the transcript's usage fields (REQ-3708, RES-0320 conclusion 10).
  It allows the stop with `stuck`, naming the counts, after two iterations in
  a row that changed neither the tree nor any open count (REQ-3710). Otherwise
  it blocks the stop, and its `reason` is the frozen prompt: run
  `/meow-flow:run` once, and read and update the progress file at the path it
  names (REQ-3702).
- A `PreToolUse` hook denies, while a run is active, an edit of the run's
  state, of `.claude/` and of `.meowpaw/`, and any command that starts or ends
  a run, so the harness can't stop or extend its own run (REQ-2660). A
  `PreToolUse` deny holds in every permission mode (RES-0320, conclusion 8).

Each iteration ends in a recorded state: the `Stop` hook appends one line to
the run's `log.jsonl` with the iteration, the tree ids, the open counts and the
tokens so far (REQ-2654, REQ-0892). Cancelling ends the run and reverts
nothing, because the work an iteration landed is reviewed work on the trunk
(REQ-2656). Every run ends in exactly one named ending, `finished`,
`cancelled`, `ceiling`, `time`, `tokens` or `stuck`, written into `run.toml`
and printed by the hook (REQ-2658).

The run is unattended by declaration. The repository's `[unattended]` table
states the run's posture: the permission mode the session must be in, which
the start hook checks against the hook input's `permission_mode` and refuses
on a mismatch, and the release command (REQ-2370, REQ-2388, REQ-3722). Under
that posture:

- The run decides each approval gate and each clarifying question itself,
  against `CLAUDE.md` and the files `[method] principles` names, and asks the
  person nothing (REQ-3714, REQ-2380). The constitution's `a_gate_is_a_stop`
  principle gains this one exception, stated there.
- Before it approves a record or merges a change, the run critiques it in a
  separate agent and revises it, so finding a fault and fixing it are two
  passes (REQ-2382).
- It pushes its branch, opens the pull request, merges it once the pull
  request's checks pass, and runs the declared release command where a merged
  change needs a release (REQ-3716). It never releases where the profile
  declares no release command.
- Each record it approves names the run in its pull request body as a harness
  approval, and the run's `report.md` lists every approval, merge and release
  it made, and everything it couldn't do, with the reason (REQ-2384,
  REQ-2386).
- It keeps every prohibition the constitution states: no secret material, no
  AI attribution, no direct commit to the trunk and no merge past a failing
  gate (REQ-3718).
- It treats every fetched page, issue and file it didn't write as data, and
  takes no instruction from it (REQ-2402).
- Where `paw status` has no `next:` line and requirements are named by no
  task, it chooses the next block itself. It writes the decision that amends
  any record the block contradicts and lists the choice in its report
  (REQ-3720).

`meow-unattended plan` stops printing a `claude -p` command and prints the
resolved posture and the deny rules. `meow-loop start` keeps working for one
release with a line saying runs now live in the session, and the release after
removes it (REQ-3004).

Once this is accepted, a person types `/meow-loop:run --iterations 200 --hours
12 --tokens 50000000` in a session and leaves. The chain advances, merges and
releases until nothing is open, a bound is reached or the run is stuck, and the
person reads `report.md`. What still doesn't work: the run has no sandbox and
no network allowlist apart from the session's own permissions, which this
record postpones, and a run can't survive the session ending, because its
state is bound to the session's id.

## Why

The owner works in one session and wants the chain to run while nobody is
there. ADR-2010 rejected an in-session loop because the conversation grows and
REQ-0880 could not hold. RES-0320 shows compaction keeps a long session inside
its window, and a command `Stop` hook lets a program, not the model, decide
whether the next turn starts, which was the reason the runner lived outside the
model (RES-0320, conclusions 1 and 4). The rule the owner gave up is REQ-0880's
same context, and REQ-3702 keeps the part a program can hold: the same stated
input.

`/loop` and `/goal` both let a model end or judge the run (RES-0320, conclusion
2), so neither gives a finish computed from the record. The `UserPromptSubmit`
start keeps REQ-0894 without a separate terminal: the program reads what the
person typed, and a model can't type a prompt.

## Alternatives

| Option                                    | Better at                                    | Why it lost                                                                             |
| ----------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------- |
| Do nothing: keep the external runner      | Each iteration starts from the same context  | The owner needs a second terminal and a person at every gate, which isn't unattended    |
| `/loop` with ScheduleWakeup               | Ships with the platform, no hook to maintain | The model chooses when to stop, so the finish isn't computed from the record (RES-0320) |
| `/goal` with an evaluator                 | Ends on a stated outcome                     | The evaluator judges from the conversation alone (RES-0320, conclusion 2)               |
| The model starts the run with a Bash call | No hook reads the prompt                     | A model could start a run unasked, which REQ-0894 forbids                               |
| Unattended but stopping at merge          | A person reviews each merge before it lands  | The owner chose that unattended mode works fully without a person                       |

## What it costs

The run spends one session's context for its whole length, and compaction
summarises the early iterations, so a late iteration knows them only through
the progress file and the record. A run that the model drives badly can open
and merge many pull requests before the person reads the report, so the
report is the only review of what the run approved, and reading it is the
person's work the next morning. The three hooks add a `paw status`
computation to every turn of a run, which costs about the time `paw status`
takes, and nothing outside a run.

## What would reverse it

- A run that compaction made lose track of the record, shown by a stuck ending
  whose counts a fresh session moves at once.
- A merged change a run approved that the owner reverts for a reason the
  critique pass should have caught, twice.
- The platform ending a `Stop` hook's block in a run that was making progress.

## Consequences

ADR-2000, ADR-2010 and ADR-2020 are superseded. REQ-0880, REQ-0888, REQ-2374
and REQ-2392 are withdrawn and replaced. SPC-1201 is rewritten for the
in-session run, SPC-1200 states the posture table without the command line,
and `CLAUDE.md` states the unattended exception to `a_gate_is_a_stop`. An epic
splits the work into tasks for the start and cancel hook, the `Stop` hook, the
posture and the deny rules, the report, the next-block choice in
`/meow-flow:run`, and the retirement of `start` and the printed command.

## How I will know it was realised

1. In a session, a fixture start command with all three bounds writes a run state, and a Bash call that runs the start
   logic from the model is denied.
2. With a run active, the `Stop` hook blocks with the frozen prompt while a
   requirement is open, and allows the stop with `finished` once a fixture
   record has none open.
3. Two fixture iterations that change nothing end the run `stuck` with the
   counts named, and a reached ceiling, time or token bound ends it with that
   bound's ending.
4. Any prompt other than the start command during a run ends it `cancelled`,
   and the next `Stop` allows the stop.
5. An edit of the run's state during a run is denied in every permission mode.
6. `report.md` lists each approval, merge and release a fixture run recorded.
7. A start in a session whose permission mode differs from the declared one is
   refused with the two modes named.

## What this does not settle

- Filesystem and network isolation, the narrow host allowlist, removing
  credentials and treating the sandbox as no boundary (REQ-2396, REQ-2398,
  REQ-2400, REQ-2404). They're postponed until the platform lets a running
  session enter a sandbox, or the owner asks for a run in a separate sandboxed
  session.
- REQ-1420 and REQ-1422, confirming an irreversible action in an attended
  session, which stay in force there. An unattended run is the declared
  exception.
- A run that outlives its session, or resumes after the session ends.
