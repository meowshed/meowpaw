---
id: TSK-5272
artifact: task
status: approved
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

Not yet.

## Left alone

The Rust modules and directories named for "verbs", and the text of frozen
records.
