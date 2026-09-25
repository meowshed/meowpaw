---
id: BUG-1100
artifact: bug
status: approved
severity: minor
violates: REQ-3184
found: 2026-09-26
revised: 2026-09-26
issue: 120
---

# The reviewer is unmeasured on most of the rules it holds

## Reproduction

At revision `2b613b6`, count the rules the writing standard states and the
cases in the reviewer's labelled set that test one:

```text
$ grep -c "^- [A-Z][0-9]*\." plugins/meow-prose/skills/writing/SKILL.md plugins/meow-prose/skills/writing/documents.md
plugins/meow-prose/skills/writing/documents.md:16
plugins/meow-prose/skills/writing/SKILL.md:49
```

The set in `plugins/meow-prose/evals/` holds 52 reviewer cases: 42 from the
21 failing and corrected pairs in `patterns/en.md`, and ten written for it, of
which about seven test a rule rather than a pattern (T2, B6, H6, G1 three ways,
and C1 inside `bold-count-long`).

## What the system does

The reviewer reads a text against all 65 rules, and its measured rates, 0.98
of defects named on Sonnet 5 and 1.00 on Opus 5.5, rest on cases for the 21
patterns and about seven rules. Whether it names a break of D4, H3, A1 or any
other rule without a case has never been measured.

## What it should do, and why

REQ-3184 holds the standard by a line-by-line review. A review measured on a
few of the rules it claims hasn't shown that it holds the rest, and the rate
it publishes reads as if it covered them all. ADR-1010's ninth criterion asks
for a case for every rule a reader can see in a text, and EPC-1010 closes with
that criterion unmet.

## Triage

No requirement in force says the reviewer's labelled set covers every rule:
ADR-1010 asked for it as a criterion, and no requirement carries it. The fix
enters at requirements: an obligation that every rule a reader can see in a
text has a case, and then the cases, which cost no model to write. Running
them is an evaluation, and it waits with the evaluations the owner postponed.

## Closed by

Open.
