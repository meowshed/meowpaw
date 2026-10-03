---
id: TSK-5015
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2550
closes: [REQ-0070, REQ-0072, REQ-0084]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Fail a method prompt, template or page that names a language or a tool

`tools/check_language.py`, run by the `test` verb, reads every prompt,
template and page of the kernel, method and practice units and fails on a
word from its list, as SPC-1030 states under "What the method names", and
CLAUDE.md's `the_method_names_no_language` stops saying no check enforces the
rule. One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture method skill naming a programming language from the list, when `python3 tools/check_language.py` runs over it, then it prints the file, the line and the word and exits 1 (REQ-0070). Closed by: a test under `tools/` naming REQ-0070, seen failing first.
2. Given a fixture pack's README naming the same language, and a fenced block in a method page whose info string names the pack whose output it shows, when the check runs, then it reports neither (REQ-0072, REQ-0084). Closed by: a test under `tools/` naming REQ-0072.
3. Given this repository, when the `test` verb runs, then the check runs and passes, and its count of files read is above zero. Closed by: the `test` verb's output.
4. Given `CLAUDE.md`, when it is read after the change, then `the_method_names_no_language` names the check and no longer says no check enforces the rule. Closed by: the pull request's diff, resting on judgement.

## What to do

Write `tools/check_language.py` with its word list of languages, frameworks,
build tools, package managers and file extensions, and its list of the units
it reads, kept beside `tools/check_kernel.py`'s kernel list. Packs are never
read, a unit's program is exempt, and an exempt fence names its pack in its
info string. The check fails on an empty run, because a check over nothing
is no pass. Join it and its test to `test` in `.meowpaw/profile.toml`. Fix or
exempt each hit the first run finds in the method's own files in the same
change, and rewrite the sentence in `CLAUDE.md`'s
`the_method_names_no_language`.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The catalogue's layers, which ADR-2640 leaves to a later decision, so the unit
list lives in the check.
