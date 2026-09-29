---
id: TSK-2577
artifact: task
status: approved
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

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

An idiom in its literal sense, such as `out of the box it ships in`, which P1
blocks as ADR-1600's closed list decides; that is a question for a decision,
not for this task's checks.
