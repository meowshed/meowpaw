---
id: TSK-5212
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2730
closes: [REQ-4144]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ship the meow binary with the core package alone

The core package's extension puts the platform binary's directory on PATH
beside the wrappers' directory, every other package drops its installer
and its binary, and each of their launchers falls back to `meow` on PATH
before reporting unrun.

## Acceptance criteria

1. Given the core npm tarball, when its contents are listed, then it
   carries `bin/<triple>/meow` for all six platforms. Closed by: the
   packing step's dry run.
2. Given the other five packages, when their files are listed, then no
   `install-meow.mjs` and no platform binary sits in them. Closed by:
   listing the packages.
3. Given the core package installed and any other package beside it, when
   a launcher in that package runs, then it executes its subcommand
   through the core binary. Closed by: a session dispatching a guard.
4. Given no core package installed, when a launcher in another package
   runs, then it reports unrun and lets the command through. Closed by:
   the launcher's fallback shape and a session test.

## What to do

Drop `install-meow.mjs` and the postinstall script from the five non-core
packages; add the PATH fallback to each of their launchers; prepend the
core binary's directory to PATH in the core extension; update the install
sections of the five READMEs and the specification.

## Depends on

- TSK-5211 (not blocking): the split decides where the binaries come
  from; this task's fallback works whichever source fills them.

## Evidence

`npm pack --dry-run` for `@meowshed/meow-core@0.4.0` lists the six
platform binaries beside the wrapper and the prose gate, and the five
non-core packages carry no `install-meow.mjs` after their removal; the
registry tarball for `@meow-flow@0.47.0` and the others is the same shape.
A Pi session with the npm-installed packages quotes the reply shape's R1
and runs `paw ready research` through `meow-flow`'s launcher, which
resolves the binary on PATH from the core package's install, proving
criteria 1 and 3; the fallback guard in every launcher is the criterion 4
shape, exercised earlier when the local install ran without a binary and
reported unrun.

## Left alone

The core package's installer, which the git-source install still needs;
the Claude Code plugins' per-unit binaries, which their own release
contract keeps; the budget files, which the launchers' names do not
change.
