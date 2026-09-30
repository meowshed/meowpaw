---
id: EPC-2200
artifact: epic
status: approved
revised: 2026-09-29
realises: ADR-2300
checked-at:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A requirement closes with its tasks, and the chain runs seven steps with no verification, evidence or record review

Realises exactly one authorising record, ADR-2300. The epic is complete when
`paw` derives each requirement's state from the tasks, epics and defects that
name it, knows seven steps, reads no Cover, and accepts a task that realises a
decision directly; the method's prompts ask for tests first and a code review
in the pull request and dispatch no record reviewer; the repository holds no
kept evidence; a page stating the wrong step count fails the documentation
check; `meow-verbs` is `meow-checks`; every record meets the new shape; and
`meow-method` is gone.

## Acceptance criteria

Taken from ADR-2300's list of how it will be known realised:

1. On a fixture record, `paw show` reports a requirement closed when its only
   task is done, open when one of two tasks naming it is open, open when no
   task names it, and open when an open defect violates it.
2. On a fixture where one requirement is named by two tasks and one task
   names three requirements, `paw check coverage` reports nothing.
3. `paw status` prints no `verified` count, no `verify`, `document` or
   `cover` step, and lists each postponed requirement with its condition.
4. `paw ready bogus TSK-0001` names seven steps, and `method/SKILL.md` names
   the same seven.
5. `paw ready implement` accepts a task with no `## Cover` section, and
   `project/evidence/` doesn't exist.
6. `paw check` accepts a task that names `realises: ADR-NNNN` and no epic.
7. The documentation check fails a fixture page naming a step count other
   than seven.
8. `claude plugin install meow-verbs@meowpaw` still works and says it is
   deprecated in favour of `meow-checks`.
9. No file under `plugins/meow-flow/` dispatches `record-reviewer` or
   `skeptic`.
10. No record under `project/` carries `## Cover`, `## Verified`,
    `checked-at` or `## Open review findings`.
11. `meow-method` is not in the marketplace.
12. Every requirement ADR-2300 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-3800 derive each requirement's state from the tasks, epics and defects that name it
      closes: REQ-3600, REQ-3602, REQ-3604, REQ-3608, REQ-3610, REQ-3620, REQ-3622, REQ-3646, REQ-3648
      evidence: 15 checks in `RequirementState`, 9 seen failing at the
      pull request's first commit, and 241 `meow-flow` fixtures passing, in
      #752.

- [x] T-002 TSK-3810 give `paw` seven steps, drop the Cover gate, and let a task realise a decision
      closes: REQ-3638, REQ-3630
      depends: TSK-3800 (not blocking)
      evidence: 15 checks in `SevenSteps` and 3 in `meow-github`'s `Project`,
      7 seen failing at the pull request's first commit, in #753.

- [x] T-003 TSK-3820 rewrite the method's prompts and templates for the seven-step chain
      closes: REQ-3606, REQ-3612, REQ-3616, REQ-3618, REQ-3624, REQ-3626, REQ-3628, REQ-3640, REQ-3642, REQ-3644, REQ-3650
      depends: TSK-3810 (not blocking)
      evidence: 7 checks in `ShortChainPrompts`, each seen failing at the pull
      request's first commit, and the budget at 818 of 820 characters.

- [x] T-004 TSK-3830 remove kept evidence from the repository and from `meow-verbs`
      closes: REQ-3614
      evidence: 4 checks in `meow-verbs`' `NoKeptEvidence` and 2 in
      `tools/test_no_kept_evidence.py`, each seen failing at the pull request's
      first commit.

- [x] T-005 TSK-3840 make the documentation check report a page stating the wrong step count
      closes: REQ-3632
      evidence: 5 checks in `tools/test_check_docs.py`, 3 seen failing at the
      pull request's first commit.
      depends: TSK-3820 (blocking)

- [ ] T-006 TSK-3850 rename `meow-verbs` to `meow-checks`, and keep `meow-verbs` one release as a stub
      closes: REQ-3634, REQ-3636
      depends: TSK-3830 (not blocking)

- [ ] T-007 TSK-3860 migrate every record to the seven-step chain's shape
      closes: REQ-3652
      depends: TSK-3800 (blocking), TSK-3830 (blocking)

- [x] T-008 [P] TSK-3870 remove the `meow-method` stub from the marketplace
      closes: REQ-3654
      evidence: 3 checks in `tools/test_marketplace.py`, seen failing at the
      pull request's first commit and passing after it.

## Coverage

ADR-2300 addresses 28 requirements, and each lands in one task. TSK-3800
holds the state the program derives, TSK-3810 the chain `paw` knows, TSK-3820
what the prompts and templates ask of a session, TSK-3830 the removal of kept
evidence, TSK-3840 the step-count check, TSK-3850 the rename, TSK-3860 the migration
of the existing record and TSK-3870 the removal of `meow-method`. TSK-3800 and
TSK-3820 are the smallest set that tests the decision: with them a
requirement closes with its task and a session writes no verification or
record review.

Until TSK-3800 lands, the program still reports a requirement named by two
tasks, so each requirement here lands in one task.

## Not covered

- The in-flight tasks TSK-2703, TSK-2950 and TSK-3350, whose worktrees the
  owner postponed; they finish under whichever rules are in force when they
  resume.
- Rewriting frozen records that name `meow-verbs` or the verify step, which
  keep the words they were approved with.
