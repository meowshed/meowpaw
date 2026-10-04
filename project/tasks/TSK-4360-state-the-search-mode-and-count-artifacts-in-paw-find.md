---
id: TSK-4360
artifact: task
status: done
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

`find` in `crates/meow/src/record.rs` prints `exhaustive: read <n>
artifacts` first, ends each hit with the file and `front matter` or
`Summary`, and prints `artifacts matched: <n>` last, so it closes REQ-2590,
REQ-2594 and REQ-2595. Rule M7 in `plugins/meow-flow/skills/method/SKILL.md`
now carries REQ-2592, REQ-2594, REQ-2596 and REQ-2597.

Each criterion is closed by the check it names, in `Find` in
`plugins/meow-flow/tests/test_record.py`:

1. `test_find_states_its_mode_first_and_its_artifact_count_last`
2. `test_three_matches_in_one_requirement_count_as_one_artifact`
3. `test_each_hit_ends_with_its_file_and_its_section`
4. `test_twenty_five_matches_print_twenty_hits_and_count_twenty_five`
5. `test_rule_m7_says_what_each_search_supports`

No criterion rests on judgement. Every check failed first in 4ce47af5, the
commit that holds the checks alone. That commit also moves the two earlier
pins in `Find` one line down, because the mode line now opens the output.
TSK-4330 hasn't landed, so these pins are this task's own. `format`, `lint`,
`check`, `test` and `build` each pass on the change's tree, as the pull
request cites.

I made two choices the task leaves open. A hit names `Summary` only for a
research record whose match sits in its summary alone, because every other
conclusion `find` reads is a title or a statement, which SPC-1100 calls
`front matter`. The line `... and <n> more; narrow the words` goes, because
the count line now says how many hits the limit left out.

Review found that the README and M7 let an `exhaustive` miss stand for the
whole record, though `find` reads only identifiers, titles and conclusions.
Both now limit the claim to those three. Review also found that no check pinned
`front matter` on a research hit, and criterion 3's check now does, in
53691d1f.

`meow-flow` goes to 0.47.0, and its README describes the new lines.

## Left alone

An index of any kind, because ADR-2430 postpones the query tool, so REQ-2596
and REQ-2597 land as rules in M7 and in no program.
