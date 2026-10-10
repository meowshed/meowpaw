---
id: TSK-5272
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2760
closes: [REQ-4200]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A check fails on "verb" in living and shipped text

A script under `tools/` fails the gate, naming the file and the line, on "verb"
or "verbs" in a living or shipped file outside an allow-list, so the word
doesn't return the first time a page is written from memory.

## Acceptance criteria

1. Given a living file that says "the five verbs", when the check runs, then it
   exits 1 and names that file and line. Closed by: a test in `tools/`.
2. Given a frozen record that says "verb", when the check runs, then it
   reports nothing about it. Closed by: a test in `tools/`.
3. Given an allow-listed file, when the check runs, then it reports nothing
   about it. Closed by: a test in `tools/`.
4. Given this repository, when the check runs, then it exits 0. Closed by: the
   gate running it with the `test` stage.

## What to do

Read the tracked files with `git ls-files`, exclude the record kinds that
freeze on approval, and keep the allow-list in the script's own constant with
a reason beside each entry. The word's own definition in SPC-1040 and the
page that explains the old name to a reader of an old profile are the entries
it starts with. Add the script to the `test` stage the way the other scripts
under `tools/` are.

## Depends on

- TSK-5271 (blocking): the check fails on every page until the pages change.

## Evidence

Pull request 877. The tests are in `tools/test_check_terms.py`:

- Criterion 1: `test_a_living_file_that_says_verbs_fails_naming_its_line`.
- Criterion 2: `test_a_frozen_record_that_says_verb_is_not_reported`.
- Criterion 3: `test_an_allow_listed_file_is_not_reported` and
  `test_a_line_naming_a_retired_unit_or_the_loop_argument_is_not_reported`.
- Criterion 4: `test_this_repository_passes`, and the `test` stage, which runs
  `tools/check_terms.py` after `check_workflows.py`.

The check also fails on a tree it read no file of
(`test_a_tree_with_no_file_to_read_fails`), because a run that read nothing
has held nothing to the word. Two fixtures written first read no file and
passed on the exit status alone, so a commit of its own gives them a page to
read.

## Left alone

The Rust modules and directories named for "verbs", and the text of frozen
records.
