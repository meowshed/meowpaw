---
id: TSK-5010
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2545
closes: [REQ-2250]
issue: 982
projected: 037b8f97b3d7
tracked: 15a9c761a414
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Add the question section to every specification in this repository

Every specification under `project/specs/` carries the template's question
section, each question answered from what the specification already states or
marked `unanswered`, so the specification is this repository's one
architecture description, as SPC-1090 states. One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given every file under `project/specs/`, when a test reads them, then each carries the question section with all seven questions, each answered or marked `unanswered` (REQ-2250). Closed by: a test under `tools/` naming REQ-2250, seen failing first.
2. Given the changed specifications, when `paw check` runs, then it reports nothing new. Closed by: `paw check`'s output.

## What to do

Answer each question only from what the specification already states or what
the tree shows, and mark the rest `unanswered`, because an answer invented to
fill the section hides the gap the question exists to show. Write each answer
to the writing standard. No specification gains a second architecture
document beside it.

## Depends on

- TSK-5000 (blocking): the section's wording is the template's.

## Evidence

Criterion 1 is closed by `tools/test_spec_questions.py` (REQ-2250): `test_each_specification_answers_each_question_or_marks_it_unanswered` runs over every file under `project/specs/` and failed on all 34 before the section existed, and `test_a_section_without_its_questions_fails` shows the check fails on a missing question or an empty answer. The test reads the questions from the `spec` template, so the wording is the template's, and `mise.toml`'s `test-tools` task runs it. Criterion 2 is closed by `paw check`: it reports nothing about the specifications, and its only findings are the unmarked-task lines `paw done` clears and the withdrawn REQ-4110 under SPC-1300, which this task didn't touch.

Whether an answer is right rests on judgement, because no program reads what a specification means. The answers are written from each specification's own scope and boundary, from `requires.toml` for what a unit depends on and what depends on it, and from `packages/` for the Pi package. A section the specification doesn't settle says `unanswered`: what crosses a trust boundary for 27 of the 34, and the data of SPC-1240 and SPC-1300.

Every stage passed in pull request #PR.

## Left alone

Answering an `unanswered` question with new behaviour, which needs a decision
of its own.
