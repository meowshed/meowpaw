---
id: EPC-2710
artifact: epic
status: done
revised: 2026-10-04
realises: ADR-2790
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A Pi package installs standalone

Realises exactly one authorising record, ADR-2790. The epic is complete when
every meowpaw Pi package installs on its own, wherever Pi puts it: the
kernel's reply shape reaches the model from files bundled inside the
package, every skill names its binary by its plain command and finds it on
PATH, the installer downloads the one meow-full release and cleans up after
itself, and no download is ever committed. The four defects BUG-1400 to
BUG-1403 are closed, and every requirement ADR-2790 addresses is closed by a
task.

## Acceptance criteria

Taken from ADR-2790's list of how it will be known realised:

1. A package installed from a copy outside any meowpaw checkout loads its
   reply shape and prompts, verified by a Pi session started with no
   `plugins/` directory anywhere on the path.
2. The method skill's step 3, `paw ready research`, runs in a Pi session
   from the plain command name.
3. Installing the kernel and the method together shows the reply shape
   once in the system prompt.
4. Two runs of an install script leave no temporary archive behind.
5. `git status` after an install in a clean clone reports nothing.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-5206 make the kernel package install standalone
      closes: REQ-4108, REQ-4130, REQ-4134
- [x] T-002 TSK-5207 name each binary without a platform variable
      closes: REQ-4110, REQ-4112, REQ-4132
- [x] T-003 TSK-5208 hold the installer and the downloads
      closes: REQ-4136, REQ-4138

## Coverage

ADR-2790 addresses five requirements, and each lands in one task: TSK-5206
holds the bundling and the kernel's one injection, TSK-5207 the plain
command names and the router's bundled prompts, TSK-5208 the installer and
the ignored downloads. The three together are the smallest set that tests
the decision: with them a package installed from anywhere but a checkout
works.

## Not covered

npm publication, which ADR-2790 leaves unsettled. The five platforms the
local meow-full release does not carry yet, which the release workflow
completes. A scripted comparison of skill output on both platforms, which
needs an eval runner no decision asks for yet.
