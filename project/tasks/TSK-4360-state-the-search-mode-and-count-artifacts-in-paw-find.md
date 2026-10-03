---
id: TSK-4360
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2410
closes: [REQ-2590, REQ-2592, REQ-2594, REQ-2595, REQ-2596, REQ-2597]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# State the search mode and count artifacts in `paw find`

`paw find` prints its mode first, the file and the heading on each hit, and a
count of matching artifacts last, and the method's rule M7 says which answer
each mode supports, as SPC-1100 states under "Searching". One task, one
branch, one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given a fixture record, when `paw find` runs on a word it holds, then the
   first line is `exhaustive: read <n> artifacts` with the fixture's count,
   and the last is `artifacts matched: <m>` (REQ-2590, REQ-2595). Closed by: a
   fixture naming both, seen failing first.
2. Given a fixture requirement whose title, statement and summary each hold
   the word, when `paw find` runs on it, then the last line is
   `artifacts matched: 1` (REQ-2595). Closed by: a
   fixture naming REQ-2595.
3. Given that fixture, when `paw find` runs, then each hit line ends with the
   artifact's file and a heading or `front matter` (REQ-2594). Closed by: a
   fixture naming REQ-2594.
4. Given twenty-five matching artifacts, when `paw find` runs, then it prints
   twenty hits and `artifacts matched: 25`. Closed by: a fixture naming
   REQ-2595.
5. Given `plugins/meow-flow/skills/method/SKILL.md`, when a fixture reads
   rule M7, then it says an absence comes only from an exhaustive search, a
   hit is read with `paw show` before it is quoted, and an index is refreshed
   before a miss is relied on, resolved to its file before a citation and
   reported as local (REQ-2592, REQ-2594, REQ-2596, REQ-2597). Closed by: a
   fixture naming the four.

## What to do

Change `find` in the `record` feature of `crates/meow/` to print the mode
line, the file and heading on each hit, and the artifact count, and keep its
ranking and its limit of twenty. Pin the new lines in the test TSK-4330 adds
where that test has landed, and in a fixture of this task's own otherwise.

Reword rule M7 in the method's `SKILL.md` and hold it to SPC-1030 and the
unit's `budget.toml`. Update `plugins/meow-flow/README.md` where it shows
`find`'s output.

## Depends on

- TSK-4330 (not blocking): both pin `find`'s output lines, and whichever lands second updates the other's pin.

## Evidence

Not yet.

## Left alone

An index of any kind, because ADR-2430 postpones the query tool, so REQ-2596
and REQ-2597 land as rules in M7 and in no program.
