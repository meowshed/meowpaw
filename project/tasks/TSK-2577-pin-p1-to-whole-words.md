---
id: TSK-2577
artifact: task
status: done
revised: 2026-09-29
bug: BUG-1267
closes: []
issue: 719
---

# Pin the prose gate's P1 to whole words

Add checks holding an idiom's words inside longer words, so a P1 that matches
a fragment of a word fails them. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a commit message holding `circle backend`, `deep diver` and
   `undercircle back`, when the launcher runs `check`, then it exits 0 and
   prints nothing. Closed by:
   `ReadableTexts.test_an_idiom_inside_longer_words_passes` in
   `plugins/meow-prose-gate/tests/test_gate.py`.
2. Given the same texts, when `findings` reads them, then it returns no
   finding. Closed by: `an_idiom_inside_longer_words_is_no_finding` in
   `crates/meow/src/prose.rs`.
3. Given P1 with the two `\b` removed from its pattern, when the checks of
   criteria 1 and 2 run, then each fails. Closed by: the failing run the Cover
   names.

## What to do

Add the two checks. They pass against the current program, because P1
already matches whole words, so see them fail against the mutation the defect
names: remove the two `\b` in `rule_p1` in the working tree, rebuild, run the
`test` verb, keep that run with `meow-verbs evidence --keep test`, and restore
`rule_p1` before any commit. Change no behaviour of the program, so
`meow-prose-gate` keeps its version.

## Depends on

Nothing. BUG-1267 is approved.

## Evidence

`ReadableTexts.test_an_idiom_inside_longer_words_passes` in
`plugins/meow-prose-gate/tests/test_gate.py` and
`an_idiom_inside_longer_words_is_no_finding` in `crates/meow/src/prose.rs`
each hold `circle backend`, `deep diver` and `undercircle back` and expect no
finding. The program is unchanged.

Against P1 with its word boundaries removed, the `test` verb exited 1 with
`an_idiom_inside_longer_words_is_no_finding --- FAILED` and
`test result: FAILED. 38 passed; 1 failed`, seen in
the run under #720, whose output is no longer kept. The Python fixture failed against the
same build:

```text
$ python3 -m unittest test_gate    # in plugins/meow-prose-gate/tests
FAIL: test_an_idiom_inside_longer_words_passes
  (2, 'P1 | "circle back" | ...', '') != (0, '', '')
Ran 34 tests
FAILED (failures=1)                # exit 1
```

With `rule_p1` restored and the units rebuilt, both pass: the same command
prints `Ran 34 tests` and `OK`, exit 0.

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

An idiom in its literal sense, such as `out of the box it ships in`, which P1
blocks as ADR-1600's closed list decides; that is a question for a decision,
not for this task's checks.
