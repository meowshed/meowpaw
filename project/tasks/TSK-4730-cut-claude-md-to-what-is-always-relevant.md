---
id: TSK-4730
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2440
closes: [REQ-2732, REQ-2736, REQ-2744, REQ-2745, REQ-2746]
issue: 957
projected: 53661caf5708
tracked: 23b023baacbc
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Cut this repository's `CLAUDE.md` to what is always relevant, each rule naming its check

`CLAUDE.md` carries what is always relevant, can't be checked and can't be
derived, each rule naming a command, a path or a value and the check that
holds it where one exists, and moves procedure and explanation into the skill
or step file that loads it on demand, as SPC-1220 states under "What it
carries". One task, one branch, one pull request, one review: the tests first,
then the change, its documentation and its marks.

## Acceptance criteria

1. Given the cut `CLAUDE.md`, when `wc -l CLAUDE.md` runs, then it prints at
   most 250, a prediction I record before the work: about 200 is the target
   REQ-2734 states, and the rules that can't move cost about 50 more. Closed
   by: the command's output in the pull request.
2. Given each principle in the cut file that must hold every time, when a
   reviewer reads it, then it names the check that holds it, such as
   `meow-scm check-message` or `paw check frozen`, or says that review holds
   it (REQ-2732, REQ-2736). Closed by: judgement in the pull request's review,
   because whether a rule must hold every time is read.
3. Given the pull request, when the owner reads it, then it lists each rule
   removed with where its content went, and each rule proposed for removal
   because its failure hasn't recurred in the evidence of the last ten merged
   tasks, with that count (REQ-2744, REQ-2745, REQ-2746). Closed by: the list
   in the pull request's body.
4. Given the cut file, when the `test` verb runs, then every check that reads
   `CLAUDE.md` passes. Closed by: the `test` verb's output.

## What to do

Move procedure, such as the step chain's explanation and the branch and
signing commands, into the skill or step file that already carries its
subject, and keep in `CLAUDE.md` only the rules, each with its reason and its
check. Keep the attribution ban, the secrets rule and the gate. Remove nothing
a check reads without changing the check in the same change.

## Depends on

- TSK-4700 (not blocking): its advice line measures the cut, and `wc -l` measures it without it.

## Evidence

Criterion 1: `wc -l CLAUDE.md` prints 250, at the prediction's limit, down
from 474. Criterion 4: the `test` verb passes with the cut file. The cut
removed the layout table, so `test_the_constitution_says_an_epic_is_one_pull_request`
in `plugins/meow-flow/tests/test_record.py` no longer reads the table row for
"one pull request" and reads the principle's sentence "An epic is one pull
request" alone.

Criteria 2 and 3 rest on judgement, because whether a rule must hold every
time is read, and the removal list belongs to the pull request body. This task
did not count recurrences over the last ten merged tasks, so it proposes no
removal under REQ-2746: the count is not measured here.

Every stage passed in pull request #1078.

## Left alone

The rules the owner keeps after reading the proposed removals, which this task
proposes and doesn't decide.
