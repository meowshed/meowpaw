---
id: TSK-5030
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2550
closes: [REQ-3050]
issue: 986
projected: a1078b191263
tracked: 047d93f9d49e
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold a unit's description to the words a request contains

`meow-author check` fails a description whose first sentence carries none of
the verbs its unit's `when_to_use` names, as SPC-1030 states under "The
check". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture skill whose `when_to_use` names `commit` and whose description's first sentence carries no verb from it, when `meow-author check` runs, then it fails naming the file and the field (REQ-3050). Closed by: a test under `plugins/meow-author/tests/` naming REQ-3050, seen failing first.
2. Given every unit under `plugins/`, when `meow-author check` runs, then it passes. Closed by: the `lint` verb's `prompts` task.

## What to do

Add the rule to the `author` feature of `crates/meow/`, beside the
description rule ADR-1050 decided. Where a shipped description fails it,
rewrite the description in the same change, measured as SPC-1030 states
under "Descriptions and loading", because a description change is measured
before it ships.

## Depends on

Nothing.

## Evidence

Criterion 1 is closed by
`test_a_description_that_leads_with_none_of_the_when_to_use_words_fails` in
`plugins/meow-author/tests/test_author.py`, seen failing first, with
`test_a_description_that_carries_one_of_the_when_to_use_words_passes`,
`test_a_word_in_the_second_sentence_does_not_count` and
`test_a_skill_with_no_when_to_use_is_not_read_by_the_rule` holding its edges.
Criterion 2 is closed by `test_every_shipped_unit_passes_the_rule` and by the
`prompts` task of the `lint` stage. No shipped skill or agent carries a
`when_to_use`, so no description needed rewriting and none was measured.

Two choices were made where the specification leaves a gap. The words
`when_to_use` names are the ones it writes in code font, because free text has
no list of verbs a program can read, and a word of the first sentence meets one
where it starts with it, so `commit` is met by `commits`. A `when_to_use` with
no word in code font is not read, the same as one that is absent.

Every stage passed in pull request #PR.

## Left alone

A skill with no `when_to_use`, which the rule doesn't read, so it passes as
it does today.
