---
id: TSK-4905
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2520
closes: [REQ-2710, REQ-2712, REQ-2714]
issue: 964
projected: a8db883c0ba4
tracked: 2cd86ef24c44
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Layer each hook's rule, and show that a crashing hook abstains

Each unit that ships a hook names, in its README's `## Hooks` section, what
the hook stops, the gate check that holds the same rule and the skill that
explains it, as SPC-1240 states under "How a rule is layered". A fixture
shows a hook that crashes or times out lets the call reach the repository's
own permission flow. One task, one branch, one pull request, one review: the
tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given each hook in SPC-1240's table that stops a call, when a reader opens
   its unit's README, then its sentence names a gate check that exists in this
   repository's `mise.toml` or CI and a skill that exists in the unit
   (REQ-2710, REQ-2712). Closed by: a test under `tools/` that resolves each
   named check and skill, naming both requirements, seen failing first.
2. Given a hook whose rule has no gate check today, when this task lands,
   then the task either adds the check or records a defect naming the hook
   and the missing check (REQ-2712). Closed by: the pull request's list of
   hooks, each with its check or its defect.
3. Given each blocking hook's launcher run against a binary that exits 1,
   and one killed by its timeout, when the fixture reads the result, then the
   hook printed no decision and exited other than 2, so the platform reads it
   as abstention (REQ-2714). Closed by: a fixture per blocking unit.

## What to do

Write the `## Hooks` section for `meow-flow`, `meow-git`, `meow-github`,
`meow-loop`, `meow-prose-gate` and `meow-checks` in the form SPC-1240 states,
one sentence per hook. For each rule, name the gate check that finds a tree
breaking it and the skill that says why. Where none exists, add the check if
it is small, or write a defect record against REQ-2712.

## Depends on

- TSK-4900 (not blocking): its check reads the section this task writes, and
  either task can land first.

## Evidence

The tests came first, in a commit of their own, where
`test_each_blocking_hook_names_an_existing_check_and_skill_or_a_defect` in
`tools/test_hook_layering.py` failed. It closes criteria 1 and 2 (REQ-2710,
REQ-2712): for each hook SPC-1240 lists as stopping a call, its README sentence
names a gate check and a skill that exist, or the defect that records the gap,
and `test_a_hook_whose_rule_has_no_gate_check_is_a_finding_against_the_unit`
holds that such a defect violates REQ-2712 and names the hook. No unit has a
gate check for its hook's rule, and two of the five have no skill, so the pull
request lists the hooks with their records: `commit-guard` BUG-1560,
`push-guard` BUG-1561, `governance-guard` BUG-1562, `guard` BUG-1563 and
`check` BUG-1564. Four of the five name the skill that says why.

Criterion 3 is closed by `Abstention` in the same file, which runs each
blocking unit's launcher against a binary that exits 1 and against one killed
by a one-second timeout, and reads no decision and an exit status other than 2.
It passed before the change, because the platform's reading of a crash is its
own. Running the same launchers with no binary found that four of them exit 0
where SPC-1240 and ADR-2710 say they deny with exit 2, which BUG-1570 records
against REQ-1426 and which this task doesn't change.

`mise run all` passed with exit status 0.

## Left alone

Which hooks exist, which ADR-2450 leaves open, and the platform's own reading
of a crashed hook, which the fixture observes and doesn't change.
