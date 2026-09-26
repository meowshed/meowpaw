---
id: TSK-1970
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1320
closes: [REQ-2818]
issue: 382
projected: 1151b3b1d51b
---

# A branch name carries nothing the forge stores

A branch name carries nothing the forge stores, as ADR-1320 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a branch named with a date, or with the author's name, when `push-guard` runs, then it refuses the push naming the rule. Closed by: a fixture.

## What to do

In `meow-git push-guard`, refuse a push from a branch whose name holds a date, as four digits followed by a separator and two, or eight digits in a row, or the author's name as git reports it.

## Depends on

Nothing. ADR-1320 is approved.

## Evidence

`meow-git push-guard` refuses a push from a branch whose name carries a date,
a year of the 1900s or 2000s with a real month either packed as eight digits
or separated, or the author's name from `git config user.name` joined by a
hyphen, a dot, an underscore or nothing. Two fixtures:

- `fix/2026-09-26-links`, `fix/20260926` and `a-person/links` are each refused
  with the branch named and what it carries, exit 2. This fixture fails
  against a stub that returns nothing.
- `fix/1234-12-factor-names`, an issue number followed by a number, goes
  through. The first version read it as a date, and requiring a real year and
  month fixed that; this fixture guards the false positive and passes against
  a stub by design.

```text
$ python3 -m unittest discover -s plugins/meow-git/tests
Ran 19 tests in 5.413s
OK

$ MEOW_GIT_BIN=stub python3 -m unittest plugins/meow-git/tests/test_git.py -k branch_named_for_a_date
FAILED (failures=1)
```

## Left alone

A version control tool other than git, which ADR-1320 leaves.
