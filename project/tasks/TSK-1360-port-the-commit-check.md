---
id: TSK-1360
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1080
closes: []
issue:
---

# Port the commit check to the native tool

One task, one branch, one pull request, one review.

## What to do

Port `meow-scm`'s program to the `scm` subcommand behind its feature, change
its launcher as SPC-1080 states, and delete `lib/meow_scm.py`.

## Depends on

TSK-1350, which builds the crate and the shared module.

## Evidence

`meow scm` is `meow-scm`'s program, ported line for line behind the `scm`
feature, which alone pulls in the regular-expression crate. The launcher runs
the binary for the machine and reports the message unchecked where there is
none, and `lib/meow_scm.py` is deleted. The types keep the order the profile
declares them in, as they did. The port landed in #155; its records land here,
because the edit that carried them failed and the commit ran without it.

```text
$ git diff --stat origin/main -- plugins/meow-scm/tests
(nothing: the fixtures are unchanged)

$ python3 -m unittest discover -s plugins/meow-scm/tests
Ran 14 tests in 0.579s
OK

$ MEOW_SCM_BIN=stub/meow-scm python3 -m unittest discover -s plugins/meow-scm/tests
FAILED (failures=14)

$ python3 -m unittest discover -s plugins/meow-git/tests   # which calls meow-scm
OK
```

The `scm` binary for `aarch64-apple-darwin` is 1,334,192 bytes, most of it the
regular-expression engine.

## Left alone

What the check checks, which SPC-1050 states.
