---
id: TSK-3850
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-2200
closes: [REQ-3634, REQ-3636]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Rename `meow-verbs` to `meow-checks`, and keep `meow-verbs` one release as a stub

The unit that runs a repository's declared checks ships as `meow-checks`, and `meow-verbs` stays in the marketplace for one release, installing nothing but a note that names its replacement. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the marketplace, when `claude plugin install meow-checks@meowpaw` runs, then it installs the unit and its skill loads as `meow-checks:verify`. Closed by: a marketplace fixture test.
2. Given the marketplace, when `claude plugin install meow-verbs@meowpaw` runs, then it installs a stub whose page and description say it is deprecated in favour of `meow-checks`. Closed by: a marketplace fixture test.
3. Given the live files outside `project/`, when they are searched, then only the stub and the release notes name `meow-verbs`. Closed by: a `tools/` test.

## What to do

Rename `plugins/meow-verbs/` and its binary, the crate feature, the marketplace entry, the profile's commands and every live page. The `[verbs]` table and the five verb names stay. Frozen records keep the old name.

## Depends on

- TSK-3830 (not blocking): both change the unit, and the second rebases.

## Cover

Not yet. The cover step replaces this line with four, `Checks`,
`Failing run`, `Landed in` and `Judgement`, and `paw ready implement` refuses
the task until they are filled.

## Evidence

`Renamed` in `tools/test_marketplace.py` holds three checks, one for each
criterion, and each failed at the pull request's first commit. The third was
widened in a commit of its own, which says why: the marketplace lists the
stub, the documentation index rows it, SPC-1040 says what the unit was
called, and the project index quotes one frozen title. The unit's 52 fixtures
pass under the new name, and `meow-verbs run format lint check test`, run as
`meow-checks`, passed all four verbs.

Left alone: frozen records keep the old name, and the ledger stays under
`meowpaw/evidence` in the state directory, so no result is lost by the move.
The crate's feature and module stay `verbs`, though What to do names the
feature, because they name the code that runs the verbs and no user types
them. The repository keeps no release notes file, so the old name lives only
in the stub, the troubleshooting page and the check. The agent's review found
a stub check that failed on a checkout built before the rename, and a release
fixture that no longer held `-v` in a unit's name; both are fixed here.

## Left alone

The in-flight worktrees for TSK-2703, TSK-2950, TSK-3350 and TSK-3700 are
postponed by the owner and left as they are.
