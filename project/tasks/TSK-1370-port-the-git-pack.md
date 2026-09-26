---
id: TSK-1370
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1080
closes: []
issue:
---

# Port the git pack to the native tool

One task, one branch, one pull request, one review.

## What to do

Port `meow-git`'s program to the `git` subcommand behind its feature, change its
launcher as SPC-1080 states, and delete `lib/meow_git.py`. The pack keeps
finding `meow-scm` where it is installed, now through that unit's launcher.

## Depends on

TSK-1350, which builds the crate and the shared module.

## Evidence

`meow git` is `meow-git`'s program, ported line for line behind the `git`
feature. It finds `meow-scm` as before: from `MEOW_SCM`, beside the pack, or in
the plugin cache, now running that unit's launcher. The launcher runs the
binary for the machine, reports the checks unrun where there is none, and
`lib/meow_git.py` is deleted.

```text
$ git diff --stat origin/main -- plugins/meow-git/tests
(nothing: the fixtures are unchanged)

$ python3 -m unittest discover -s plugins/meow-git/tests
Ran 12 tests in 3.588s
OK

$ MEOW_GIT_BIN=stub/meow-git python3 -m unittest discover -s plugins/meow-git/tests
FAILED (failures=12)
```

The `git` binary for `aarch64-apple-darwin` is 521,056 bytes. With this port no
unit carries a program for an interpreter.

## Left alone

What the guards check, which SPC-1060 states.
