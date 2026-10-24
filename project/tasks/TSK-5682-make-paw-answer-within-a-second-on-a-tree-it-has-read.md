---
id: TSK-5682
artifact: task
status: done
revised: 2026-10-24
epic: EPC-2850
closes: [REQ-2800]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Make `paw` answer within a second on a tree it has read

`paw check` took 3.5 seconds and `paw status --brief` 1.2 seconds on this repository's record of about 2,200 artifacts on 2026-10-24, with nothing changed between calls. Both have to complete in under one second when nothing changed, and read only what changed when something did.

## Acceptance criteria

1. Given this repository's record read once, when `paw check` runs again with no file changed, then it completes in under 1 second, and `paw status --brief` does too (REQ-2800). The predicted number is under 1 second on the machine that ran the gate. Closed by: a script or test timing the second call, with the measured seconds in the Evidence.
2. Given one record file edited since the last call, when `paw check` runs, then it re-reads that file and no unchanged one, and its findings equal what a run from scratch reports (REQ-2800). Closed by: a crate test that counts file reads and compares the findings with a cold run, seen failing against a cache that ignores the edit.
3. Given a cache that is missing, unreadable or written by another version, when `paw check` runs, then it reads everything and reports the same findings, never a stale result (REQ-2800). Closed by: a crate test for each of the three states.

## What to do

Profile first and say what the 3.5 seconds are spent on. A fix in the hot spot that reaches the second needs no cache, and then the second and third criteria hold trivially and say so. Where a cache is needed, keep it under a state directory the tool owns, never in the record, never committed, and key each entry by the file's path, size and modification time.

## Depends on

Nothing.

## Evidence

Profile, on this repository's record of 2,220 artifacts, with the release
binary run through `plugins/meow-flow/bin/paw` and
`CLAUDE_PLUGIN_DATA=/nonexistent/u`: the time was CPU and not disk (3.40 s of
user time in a 3.55 s call). Reading the record took 0.10 s. The rest was
repeated work inside the checks: `rules` 1.50 s, `identifiers` 0.48 s,
`front-matter` 0.30 s. Three causes held nearly all of it. A regular
expression was compiled once per artifact (`identifiers`) or once per call of
`entries`, `unmarked_entry` and `depends_on`, which the derived-done and mark
lookups call for every task. `rules` rebuilt the identifier map for every epic
and task it checked. `closing_tasks` and `violated_by` ran the identifier
pattern over every task and defect for every requirement.

The fix compiles each pattern once, builds the map once, and tests for the
identifier as a substring before the pattern runs. It needs no cache, so
criteria 2 and 3 hold trivially: there is no cache that could ignore an edit
or be missing, unreadable or written by another version, and every call reads
every file, so its findings are those of a run from scratch.

Measured before and after, same machine, nothing changed between calls:

| Call                 | Before | After  |
| -------------------- | ------ | ------ |
| `paw check`          | 3.55 s | 0.49 s |
| `paw status --brief` | 1.36 s | 0.31 s |

- Criterion 1 (REQ-2800): the test
  `a_second_call_on_an_unchanged_record_takes_under_a_second` in
  `crates/meow/tests/record_speed.rs` times the second call of both commands on
  a generated record of 2,080 artifacts, against the release build. It failed
  with the old binary (`paw ["check"] took 2.679s`) and passes with the new.
- Criterion 2 (REQ-2800): holds trivially, as above. No test counts reads,
  because the tool keeps no cache between calls.
- Criterion 3 (REQ-2800): holds trivially, as above.
- What `paw` reports stayed byte-identical: `check`, `status`, `status
--brief`, `count`, `find` and `ready` printed the same bytes before and
  after on this record, and `check`, `status`, `status --brief`, `count` and
  `ready` did on a copy with nine injected defects (71 lines of findings).
- No criterion rests on judgement.

Every stage passed in pull request #1081.

## Left alone

What `paw` reports, which must stay byte-identical to a cold run.
