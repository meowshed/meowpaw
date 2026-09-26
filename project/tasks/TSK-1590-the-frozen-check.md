---
id: TSK-1590
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1170
closes: [REQ-0396, REQ-0398, REQ-0622, REQ-0626, REQ-0630, REQ-0634, REQ-0635]
issue: 242
---

# The frozen check

The frozen check, as ADR-1170 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an approved requirement committed at `HEAD`, when its obligation is reworded, then `check frozen` exits 1 naming it. Closed by: a fixture.
2. Given the same rewording with an added `**Amended by ADR-0001.**` line, when `check frozen` runs, then it exits 0. Closed by: a fixture.
3. Given an approved task and an unverified epic, when evidence and a mark are added, then `check frozen` exits 0; given a verified epic, when a mark changes, then it exits 1. Closed by: fixtures.
4. Given a specification, when it is rewritten, then `check frozen` exits 0. Closed by: a fixture.

## What to do

Add `frozen` to `meow record check`, run only by name, with `--base <rev>` defaulting to `HEAD`. For each record approved at the base, read its text there with `git show`, compare it with the current file, and report a change outside what its kind may change, as SPC-1070 states, unless the change adds a line naming its authority. Run it in this repository's ship step against the trunk.

## Depends on

Nothing. ADR-1170 is approved.

## Evidence

`meow record check frozen [--base <rev>]` reads each record approved at the
base through `git show`, compares it with the current file, and reports a
change outside what its kind may change: a task's evidence, issue and date, an
epic until it carries `checked-at`, a move to `withdrawn` or `superseded`, and
any change adding a line that names its authority. Living documents and each
kind's own index are never frozen. Nine fixtures cover each criterion and
each allowance:

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 66 tests in 4.102s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=59, errors=2)
```

Run against this repository's own history, from the revision before BUG-1110's
fix, it finds the 9 records changed since without a line naming
their authority: the eight requirements BUG-1110 corrected and EPC-1080, whose
mark BUG-1160 corrected after its verification. Both corrections went through a
defect record, and neither added the line, which is what the check now asks:

```text
$ meow-method check frozen --base 2a19c76^
frozen: 9 findings
$ meow-method check frozen --base origin/main
frozen: 0 findings
```

The first run also flagged the research index, RES-0001, a false positive: an
index changes as its kind grows, so each kind's own index is now exempt, with a
fixture. The ship step in this repository runs the check against the trunk.

## Left alone

Running the frozen check in continuous integration, which ADR-1170 leaves.
