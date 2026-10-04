---
id: TSK-3810
artifact: task
status: done
revised: 2026-09-29
epic: EPC-2200
closes: [REQ-3638, REQ-3630]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Give `paw` seven steps, drop the Cover gate, and let a task realise a decision

`paw ready` knows research, requirements, design, spec, epic, implement and review, `ready implement` reads no `## Cover`, and a task may name `realises: ADR-NNNN` in place of `epic:`. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given any record, when `paw ready bogus TSK-0001` runs, then it exits 2 naming the seven steps in order. Closed by: a fixture test.
2. Given an approved task with no `## Cover` section under an approved epic, when `paw ready implement` runs, then it exits 0. Closed by: a fixture test.
3. Given an approved task naming `realises: ADR-NNNN` and no epic, when `paw check` and `paw status` run, then check reports nothing and status names `implement` for it. Closed by: a fixture test.
4. Given a task with no epic, when `meow-github project` plans it, then it plans an issue with no parent. Closed by: a `meow-github` fixture test.

## What to do

Change `crates/meow/src/record.rs` and `lib/layout.toml` in `meow-flow`, and the projection in `meow-github`. The `cover`, `document` and `verify` names are read for one release and refused with a message naming the step that replaced them.

## Depends on

- TSK-3800 (not blocking): both change `record.rs`, so the second to land rebases.

## Evidence

In #753. The class `SevenSteps` in `plugins/meow-flow/tests/test_record.py`
holds 15 checks and `Project` in `plugins/meow-github/tests/test_github.py`
holds three for criterion 4. The seven in the pull request's first commit
failed against `main`, and `meow-verbs run format lint check test` passed all
four verbs. An agent's code review found 16 defects in the first version,
among them a decision called closed beside an open direct task and a direct
task that could never be dropped, and the pull request fixes each but one:
`realises: [ADR-NNNN]` written as a list isn't unwrapped, as an epic's isn't.

## Left alone

The method's prompts still name the cover, document and verify steps until
TSK-3820 lands, so a session following them meets the exit 2 that names the
replacing step.

The in-flight worktrees for TSK-2703, TSK-2950, TSK-3350 and TSK-3700 are
postponed by the owner and left as they are.
