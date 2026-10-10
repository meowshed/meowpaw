---
id: RES-0351
artifact: research
status: approved
revised: 2026-10-10
elaborates: RES-0320
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A token total from the transcript counts each cache read again

## Summary

The token bound of a run ended it in its first iteration at 24.7 million
tokens, against a budget of 10 million, because the total sums every usage
field of every message in the session, and 98 per cent of what it summed were
cache reads of a context already counted. The total measures how many turns the
session has taken times how large its context is, which no budget a person
states in tokens means. The iteration ceiling and the time limit are counted
outside the model and measure what a person meant, so the document concludes
that the run keeps those two, gives each a default and drops the token bound.
It covers what the hook counts and what it could count instead, and it doesn't
cover the price of a token.

## The question

What should bound a run that works in one session, besides its iteration
ceiling and its time limit?

The assumption behind the question is that a person's budget has to be a number
of tokens, because RES-0320 found that a hook can count them and found no field
that gives the spend in dollars. The finding below shows that what a hook can
count isn't the quantity a person budgets, so the assumption is challenged
first: the question isn't which count is right but whether a count the hook can
make is a bound at all.

## Method

Read the program that counts, `crates/meow/src/runloop.rs`, and the run's own
log, `log.jsonl`, in the run directory of run 01791654480077684000. Summed the
`usage` object of every message in the session's transcript by field with a
short script, on 2026-10-10. Read the specification of the bound, SPC-1201, and
the requirements it states. Couldn't obtain what the account was charged, which
no field of the transcript carries (RES-0320, conclusion 10).

## Findings

### The hook sums every usage field of every message in the whole transcript

`transcript_tokens` in `crates/meow/src/runloop.rs` reads the transcript the
hook is given and adds `input_tokens`, `output_tokens`,
`cache_creation_input_tokens` and `cache_read_input_tokens` of every message
that carries them. It takes no starting point, so the sum begins with the first
message of the session. Source: that function, read 2026-10-10 at commit
`db188733`.

### The sum is almost all cache reads

The session of run 01791654480077684000 held 226 messages with usage. Their
fields summed to 33,326,808, of which 32,770,613 were `cache_read_input_tokens`
(98.3 per cent), 397,715 `cache_creation_input_tokens`, 158,010
`output_tokens` and 470 `input_tokens`. Each turn rereads the whole cached
context, so the cache-read sum grows with turns multiplied by context size,
and it passes a stated budget on a session that has done little new work.
Source: the transcript of that session, summed 2026-10-10.

### The first iteration is charged with everything before the run

The run's first log line records `tokens` 24,737,266 and `iteration_tokens`
24,737,266, equal, with the run seconds old. The session already held three
earlier runs and a merged pull request, and the count has no baseline from the
run's start. A person who states a budget for a run is charged for the session
they started it in. Source: `log.jsonl` of that run, read 2026-10-10.

### The check counts the same total twice before the first iteration ends

The ending `tokens` holds where `total + largest > tokens`, and `largest` is the
greatest single iteration so far. In the first iteration `largest` equals
`total`, so 49.5 million was compared with the stated 10 million. SPC-1201
states the doubling as the way the budget is checked before the next iteration
starts. Source: `runloop.rs`, the `ending` chain of `stop`, and SPC-1201,
"Each iteration", read 2026-10-10.

### The other two bounds are counted outside the model and measure what was meant

The iteration ceiling counts log lines and the time limit compares the start
time with the clock. Neither reads the transcript, so neither depends on how
large the context has grown. A run that changes nothing ends as `stuck` after
two iterations whatever the bounds are. Source: `runloop.rs` and SPC-1201,
read 2026-10-10.

### The person asked for the bound to go

On 2026-10-10 the repository's owner, whose run had just ended on the token
bound, said the check fired wrongly and asked for the token limit to be removed
and for the remaining parameters to get defaults. Source: the owner's
instruction in the session.

## Options

**Keep the bound and count from the run's start, without cache reads.** Better
at keeping a brake on expensive iterations in a currency a person thinks in.
Against it: what to leave out is the hook's guess, because no field gives the
spend, and the guess changes when the platform's caching changes. A new count
also has to be validated against a bill nobody can read from the transcript.

**Keep the bound and count output and input tokens only.** Better at being
simple and at ignoring the cache entirely. Against it: output tokens understate
a run that reads large files, so the bound would not stop the expensive
iteration it exists for, and it too leaves the choice of what counts to the
hook.

**Drop the bound and keep the iteration ceiling and the time limit, each with a
default.** Better at being a bound the person can predict: ten iterations and
four hours mean the same thing on every session. This option leads. The case
against it is that an iteration that does a great deal of work in four hours
has no cost brake, and the person finds out from the bill. The ceiling and the
time limit are the brake, and `stuck` ends a run that does nothing.

## Conclusions

1. A run ends on the iteration ceiling or the time limit and on no count of
   tokens, because the only total the hook can make from the transcript counts
   each cache read again and grows with turns and not with work.
2. Each of the two remaining bounds has a default, so a start command that
   names neither still states what the run is held to.
3. A run states the bounds it runs under, defaults included, before its first
   iteration, because a default nobody was told is a bound nobody chose.
4. A start command that still names `--tokens` starts the run and says the
   bound no longer exists, for one release, because a command typed from
   habit shouldn't be refused over a bound that isn't enforced.

## Sources

- `crates/meow/src/runloop.rs` at `db188733`, read 2026-10-10: `transcript_tokens`
  and the ending chain of `stop`.
- `project/specs/SPC-1201-the-loop-runner.md`, read 2026-10-10: "Starting a
  run", "Each iteration" and "Endings".
- `log.jsonl` of run 01791654480077684000, read 2026-10-10: the run's own
  count, from its state directory.
- The transcript of the session that run lived in, summed 2026-10-10: the
  usage fields by name.
- RES-0320, conclusions 9 and 10, read 2026-10-10: what a hook can count and
  that no field gives the spend.
