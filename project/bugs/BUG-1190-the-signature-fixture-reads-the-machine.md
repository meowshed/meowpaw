---
id: BUG-1190
artifact: bug
status: approved
severity: minor
violates: REQ-2530
found: 2026-09-27
revised: 2026-09-27
issue: 410
---

# The `meow-git` signature fixture reads the machine's git configuration

## Reproduction

With `meow-git` 0.2.1 and git 2.55.0 on macOS, on the trunk after #408, on a
machine whose global git configuration names an allowed signers file:

```text
$ git config --global gpg.ssh.allowedSignersFile
/Users/retran/.ssh/allowed_signers
$ python3 -m unittest discover -s plugins/meow-git/tests
FAIL: test_a_signature_nobody_can_verify_is_unverifiable
AssertionError: 'unverifiable' not found in "meow-git: refused the push; 1
problem in the 1 commit it would publish: ... signature: the commit signed
by a key this repository doesn't trust"
Ran 19 tests
FAILED (failures=1)
```

## What the system does

The fixture's scratch repository inherits the global and system git
configuration. With a global allowed signers file, git can check the orphan
key's signature, finds the key missing from that file and reports `U`, so the
guard says the key is untrusted. The fixture expects `N`, which git reports
only where no allowed signers file is configured at all. The `test` verb runs
the suites with `&&`, so every check after this suite, `paw check` among them,
never ran on that machine.

## What it should do, and why

REQ-2530 has the gate report a signature it can't verify as unverifiable, and
this fixture is the check that proves that path. A check proving it has to
give the same verdict on every machine, or its failure says nothing about the
gate. The guard itself is right to read the machine's configuration, because
that is where a person's own signers file lives.

## Triage

A defect in a check, not in the guard, so it enters at implementation and
needs no decision. Minor, because the guard behaves correctly and CI, which
has no global signers file, passed; the cost is a `test` verb that fails on a
configured machine and hides every check after it.

## Closed by

The fixture module sets `GIT_CONFIG_GLOBAL` to the null device and
`GIT_CONFIG_NOSYSTEM`, so every git command it runs, the guard's included,
reads the scratch repository's configuration alone. On the machine above the
suite failed 1 of 19 before the change and passes 19 of 19 after it, and the
fixture stays in `plugins/meow-git/tests/test_git.py` as the regression
check.
