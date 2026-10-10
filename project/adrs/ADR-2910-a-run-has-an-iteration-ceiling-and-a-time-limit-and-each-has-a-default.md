---
id: ADR-2910
artifact: adr
status: done
revised: 2026-10-10
addresses: [REQ-3724, REQ-3726, REQ-3728, REQ-3730, REQ-3732]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2910. A run has an iteration ceiling and a time limit, and each has a default

## Decision

A run is held to two bounds, `--iterations` and `--hours`, and to no token
count. The `tokens` ending and the `--tokens` flag go. Each remaining bound has
a default, so `/meow-loop:run` typed with no argument starts a run:

| Bound          | Default |
| -------------- | ------- |
| `--iterations` | 10      |
| `--hours`      | 4       |

The two values are the ones the owner has typed on every run so far, chosen
because a default somebody already trusts is the one least likely to surprise
(a choice made here, because no record held one). The start context names the
bounds the run runs under, defaults included, in the same sentence that names
them today (REQ-3728). A command that still carries `--tokens` starts the run
and the start context says that the bound no longer exists (REQ-3730). The
notice is withdrawn in the release after the one that adds it, so a person has
one release to drop the flag, and the release after that treats `--tokens` as
an unknown flag.

This decision amends the three bounds ADR-2380 chose. REQ-3708 is withdrawn
and REQ-3724 replaces it, REQ-0878 is withdrawn because the budget it checks no
longer exists, and REQ-0872 is withdrawn and REQ-3728 replaces it, because the
bounds are now stated by the run and not required of the command.

Once this is accepted, a run ends as `finished`, `ceiling`, `time`, `stuck` or
`cancelled`, and a bare `/meow-loop:run` works. What still doesn't exist is a
brake on an iteration's cost: nothing here measures spend, and a run that does
a great deal of work in four hours isn't stopped for it.

## Why

The hook can count tokens only by summing the transcript's usage fields, and
the sum is 98 per cent cache reads of a context already counted, taken from the
session's start and not the run's (RES-0351, the findings on the sum, its cache reads and its baseline). In the run that
prompted this record it reached 24.7 million in the first iteration, against a
stated budget of 10 million, and ended the run before its work began. The
bound measures turns multiplied by context and not work, so no budget a person
states means what the hook enforces (RES-0351, conclusion 1).

The iteration ceiling and the time limit are counted outside the model and
mean the same on every session (RES-0351, the finding on the other two bounds). Defaults let a person
start a run without remembering what to type, and stating the values at the
start keeps the default a choice somebody was told about (RES-0351,
conclusions 2 and 3).

## Alternatives

| Option                                               | Better at                                    | Why it lost                                                                                           |
| ---------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Do nothing                                           | Keeps REQ-3708 whole                         | A run ends in its first iteration on a count that measures the session, so no run gets to work.       |
| Count from the run's start and leave out cache reads | Keeps a brake on expensive iterations        | What to leave out is a guess, because no field gives the spend, and the guess ages with the platform. |
| Count output and input tokens only                   | Simple, and ignores the cache entirely       | Understates a run that reads large files, so it misses the iterations it exists to stop.              |
| Drop the token bound and default the other two       | A bound that means the same in every session | Has no brake on cost inside the time limit.                                                           |

## What it costs

A run can spend more inside four hours than a token budget the person would
have chosen. The limit is the only brake on an expensive iteration, and the
person learns what it cost from the bill. A person who wants less lowers
`--hours`.

The strongest objection is that the token bound existed to stop exactly this
spend, and removing it for being miscounted gives up the intent with the
fault. The answer is that a bound which ends the run before its first
iteration protects nobody, and that a replacement needs a measure of spend the
transcript doesn't carry (RES-0320, conclusion 10), so it waits on the
platform and not on this record.

## What would reverse it

- The transcript or the hook input gains a field that gives a run's own
  spend, apart from cache reads. Then a token or cost bound returns as a new
  decision that names the field.
- A run is found to have spent beyond what its owner accepted inside its time
  limit, twice, with the default limit in force.

## Consequences

REQ-3708, REQ-0872 and REQ-0878 are withdrawn with tombstones, and REQ-3724,
REQ-3726, REQ-3728 and REQ-3730 are added. SPC-1201 loses the third bound, the
`tokens` ending and the missing-bound refusals, and gains the defaults and the
`--tokens` notice. `crates/meow/src/runloop.rs`,
`plugins/meow-loop/skills/run/SKILL.md`, `plugins/meow-loop/README.md` and the
unit's tests change, and `run.toml` stops carrying `tokens` and `log.jsonl`
stops carrying the running total. The unit's version rises by a minor, because
a command that was refused starts a run.

## How I will know it was realised

1. `/meow-loop:run` with no argument starts a run whose start context names
   `--iterations 10` and `--hours 4`.
2. A run named with `--iterations 3` and no `--hours` ends as `ceiling` after
   three iterations and names `--hours 4` at its start.
3. A run ends as `tokens` in no case: the ending is absent from the program,
   from `run.toml` and from the report.
4. `/meow-loop:run --iterations 10 --hours 4 --tokens 10000000` starts a run
   and its start context says that the token bound no longer exists.

## What this does not settle

- A measure of spend, or any bound on cost.
- Whether `meow-loop start`, the terminal runner, takes the same defaults: its
  own deprecation (REQ-3004) removes it first.
- The release that removes the `--tokens` notice, which is the one after the
  release that adds it.
