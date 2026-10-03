---
id: ADR-2700
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2716, REQ-2727, REQ-2728]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2700. The prose gate is the one hook that may reach the network, and it waits on a bounded judge

## Decision

This amends ADR-2450 in one place. ADR-2450 says no hook the harness ships
reaches the network (REQ-2727) and a blocking hook does a small, fixed amount
of work (REQ-2716). `meow-prose-gate check` is the one named exception to
both, because ADR-2390, which the owner asked for, has it ask a model through
`claude -p` and wait for two judgements of at most 45 seconds each. The
exception covers that judge call and nothing else in the gate: the exact
rules P1, P2 and P3 still run locally and first, and the hook's timeout of
120 seconds is the bound ADR-2390 sets.

Every other hook keeps both rules as ADR-2450 states them. `meow-author
check` fails a hook that names a network command, and it accepts the prose
gate's judge only because the exception is declared in the check by the
unit's name and the subcommand's, so a second exception needs a decision of
its own.

The revision counter (REQ-2728) is built as ADR-2450 says: it advances after
a failed tool use as well as a successful one. I place it in `meow-checks`,
beside the ledger SPC-1040 states, because that ledger is what reads a result
as stale, and ADR-2450 named the crate and not a unit.

The rest of ADR-2450 stands, and its file stays as it was approved. No
requirement is withdrawn.

Once this is accepted, ADR-2450 and ADR-2390 no longer contradict each
other, and the record says which hook may wait on a model. What still
doesn't work: REQ-2727 and REQ-2716 are worded without an exception, so the
specification states the exception beside them, and a reader of the
requirement alone doesn't see it.

## Why

ADR-2390 is the owner's own request, and its Why records that request
(RES-0330). ADR-2450 came later and stated its two rules for every hook
without naming the prose gate, so the record held two approved decisions
that a spec step couldn't follow at once. RES-0203 found that a slow hook
stalls every call it matches. The prose gate matches only a publishing
command, so its wait falls on a commit or a pull request and never on an
edit or a read.

## Alternatives

| Option                                   | Better at                                 | Why it lost                                                                                           |
| ---------------------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Name the prose gate as the one exception | Both decisions can be built as they stand | Chosen                                                                                                |
| Do nothing                               | No new record                             | The spec step can't state ADR-2450 and ADR-2390 together, so neither is built                         |
| Move the judge out of the hook           | Every hook keeps both rules               | The owner asked for the gate to judge the text before it is published, which only the hook can stop   |
| Withdraw REQ-2727 and REQ-2716           | The requirements say what the record does | Every other hook still needs both rules, and the owner kept the requirements in force for that reason |

## What it costs

A publish that passes the exact rules waits for the judge, up to 45 seconds
for each of two calls started side by side, which ADR-2390 already pays.
`meow-author check` carries a named exception, and the exception has to be
read beside REQ-2727 wherever the requirement is cited.

## What would reverse it

- ADR-2390 is withdrawn, or its judge moves out of the hook, which removes the
  only network call a hook makes.
- A second hook needs the network, which would show the exception is a rule
  and needs a decision that rewords REQ-2727.

## Consequences

SPC-1030 states the hook rules with the exception named beside REQ-2727 and
REQ-2716, and SPC-1010 states the judge as the exception. `meow-author check`
declares the exception by unit and subcommand. SPC-1040 states the revision
counter in `meow-checks`.

## How I will know it was realised

1. `meow-author check` fails a fixture hook that calls `curl`, and passes
   `meow-prose-gate check` with its judge (REQ-2727).
2. `meow-author check` fails a fixture hook in any other unit whose command
   runs `claude -p` (REQ-2727, REQ-2716).
3. A fixture tool use that fails advances the revision counter in
   `meow-checks`' run state (REQ-2728).

## What this does not settle

- Whether the judge's 45-second bound is the right one, which ADR-2390 leaves
  to the task that times it.
- Which other hooks exist, which ADR-2450 leaves open as well.
