---
id: RES-0350
artifact: research
status: approved
revised: 2026-10-10
elaborates: RES-0027
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Four of the 65 rules of the writing standard have a reviewer case, and five of them no text can show

## Summary

The writing standard states 65 rules, and the reviewer's labelled set holds 52
cases, of which four name a rule by its identifier in their grader (B6, G1, H6
and T2). The 21 pattern pairs test patterns, which the rules don't cover one
for one. Five rules describe the review or the writer's process and no text can
show them, so 60 rules need a case, and 56 of them have none. A program can read
the rules and the cases and fail when one is missing, because the rules carry
identifiers and each case can carry a tag that names its rule.

The document covers whether a case exists for each rule. It doesn't cover how
well the reviewer does on those cases, which is an evaluation and waits with the
evaluations the owner postponed.

## The question

Does the reviewer's labelled set test each rule a reader can see in a text, and
if not, how would a program tell which are missing?

The assumption behind the question is that a case per rule is worth its cost.
A rule is reviewed by a model, and a model that names 21 patterns may or may
not name a break of D4. The only way to know is a case, and a case costs a text
and a paragraph of grader. A measured rate that rests on some of the rules
reads as a rate for all of them, which BUG-1100 records.

## Method

I read the rules with `grep -hE '^- [A-Z][0-9]+\.'` over
`plugins/meow-prose/skills/writing/SKILL.md` and `documents.md` at
`origin/main` on 2026-10-10. I counted the cases under
`plugins/meow-prose/evals/` with `git ls-tree`, and the rule identifiers in
their graders with `git grep`, leaving out the `write-` cases, which measure a
writer and not the reviewer. I read each rule that no case names and decided
whether a reader can see a break of it in a text. I did not run the reviewer on
any case.

## Findings

### The set holds 52 reviewer cases and 15 writer cases

`plugins/meow-prose/evals/` holds 67 case directories and `thresholds.toml`. The
15 `write-` cases score a writer with and without the skill and don't test the
reviewer. The other 52 do: 42 come from the 21 failing and corrected pairs in
`patterns/en.md`, and ten were written for a rule or a defect.

### Four rules are named in a reviewer grader

`git grep` over the reviewer graders finds one citation each of B6, G1, H6 and
T2. The `write-` graders cite B5, B6, F4, T6 and others as a checklist for the
writer, and BUG-1100 counted about seven rules from cases whose graders name
the defect and not the rule, such as C1 inside `bold-count-long`.

### 60 rules can be shown by a text and 5 cannot

The 65 rules are 49 in `SKILL.md` and 16 in `documents.md`. Five describe the
process or the review and no span of a text breaks them: D10 (read the sentence
aloud), E15 (a cold read of the order), E1 (follow the repository's template),
X1 (an editor treats the author's facts as outranking style) and S3 (a review
comment names the line, the fault and the fix). A case for each would test the
reviewer's own report and not a defect in a text, and the reviewer's report is
covered by SPC-1030.

### The rules carry identifiers and the cases can

Each rule starts with its identifier as `- X0.`, so a program lists them with
one pattern. A case's `prompt.md` has a `tags` field, and the cases written so
far use `defect`, `clean`, `named` and `content`. A `rule-<ID>` tag per case
gives a program the link, and a case may carry one tag for each rule it tests.

### A rule that has no text must be stated, not skipped

A check that fails on a rule with no case also fails on the five rules above.
A list of exempt rules with a reason each keeps the check strict, and a rule
dropped from the list shows in the diff.

## Conclusions

1. The reviewer's labelled set holds at least one case for every rule a reader
   can see in a text (Findings: four rules are named in a reviewer grader; 60
   rules can be shown by a text and 5 cannot).
2. A check reads the rules from the standard and the cases from the set, and
   fails with each rule that has no case named (Findings: the rules carry
   identifiers and the cases can).
3. A rule no text can show is listed with its reason, and the check accepts
   only a listed rule without a case (Findings: a rule that has no text must be
   stated, not skipped).
4. The cases are written and checked in the same change as the check, and
   running them stays an evaluation (Findings: the set holds 52 reviewer
   cases and 15 writer cases).

## Sources

- `plugins/meow-prose/skills/writing/SKILL.md` and `documents.md`, as of `origin/main` at pull request 886, read 2026-10-10 - the 65 rules and their identifiers.
- `plugins/meow-prose/evals/`, as of `origin/main` at pull request 886, read 2026-10-10 - the cases, their tags and their graders.
- `project/bugs/BUG-1100-the-reviewer-is-unmeasured-on-most-rules.md`, read 2026-10-10 - the count the defect gave at revision `2b613b6`.
