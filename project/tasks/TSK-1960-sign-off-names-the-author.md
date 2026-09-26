---
id: TSK-1960
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1320
closes: [REQ-1312]
issue: 381
projected: a137b0a74372
---

# The sign-off names the commit's author

The sign-off names the commit's author, as ADR-1320 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a repository requiring the sign-off and a message signed off by someone other than the author, when `check-message` runs, then it reports the trailer naming both. Closed by: a fixture.

## What to do

In `meow-scm check-message`, where the profile's trailers include `Signed-off-by`, compare its value with the author identity `git var GIT_AUTHOR_IDENT` reports, and report a mismatch naming both.

## Depends on

Nothing. ADR-1320 is approved.

## Evidence

Where the profile's trailers include `Signed-off-by`, `meow-scm check-message`
compares each sign-off with the author `git var GIT_AUTHOR_IDENT` reports, and
reports one naming anybody else with both names; where git reports no author,
it says the sign-off wasn't compared. A fixture signs off as a second person
and sees the refusal naming both, exit 1, and fails against a stub that
returns nothing. The other fixtures now present their signer as the author.

The push guard checks commits already made, so it passes each commit's own
author to the check, and a sign-off is compared with the author of the commit
that carries it, not with whoever pushes.

```text
$ python3 -m unittest discover -s plugins/meow-scm/tests
Ran 16 tests in 0.352s
OK

$ python3 -m unittest discover -s plugins/meow-git/tests
Ran 17 tests in 4.255s
OK

$ MEOW_SCM_BIN=stub python3 -m unittest plugins/meow-scm/tests/test_scm.py -k sign_off_naming
FAILED (failures=1)

$ meow-scm check-message   # this repository, signed off by its author
meow-scm check-message: the message meets the declared convention
```

## Left alone

A version control tool other than git, which ADR-1320 leaves.
