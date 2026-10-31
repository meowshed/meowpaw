---
id: TSK-5208
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2710
closes: [REQ-4136, REQ-4138]
issue: 850
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold the installer and the downloads

Each package's install script downloads the one meow-full release archive —
the meow binary built once with every unit's feature — extracts the platform
binary, names it `meow`, removes the archive, runs on ESM with no `require`,
and exits 0 on any failure. The repository ignores the platform directories
the scripts fill. Fixes BUG-1403.

## Acceptance criteria

1. Given each package's install script, when its download source is read,
   then it names the meow-full release, the same one for all six packages.
   Closed by: reading the six scripts.
2. Given the kernel package's install script run twice, when it finishes,
   then no `.tmp-*.zip` remains in `bin/`. Closed by: running the script
   twice and listing the directory.
3. Given the install script on a machine its download cannot reach, when
   the download fails, then the script exits 0 and prints a warning. Closed
   by: the script's catch path, which warns and exits 0.
4. Given a clean clone after an install, when `git status` runs, then no
   platform binary or archive is reported. Closed by: the `.gitignore`
   pattern covering `packages/*/bin/*-*/`.

## What to do

One canonical `install-meow.mjs` copied to all six packages, resolving the
target triple, following redirects, unzipping on POSIX and expanding on
Windows, renaming `meow-<triple>` to `meow`, and cleaning up in a
`finally`. The build workflow gains a `full` job building `--all-features`
for six targets; the pi-release workflow publishes the meow-full release
and the package archives.

## Depends on

Nothing.

## Evidence

`paw check` reports no finding; the repository gate passes. All six
packages' `install-meow.mjs` name the meow-full release; two runs in a
clean copy leave no `.tmp-*.zip` and place `meow` where the wrappers find
it (`meow-prose-gate status` and `paw ready research` both resolve); the
catch path warns and exits 0; `.gitignore` covers `packages/*/bin/*-*/`,
and `git status` after an install reports nothing. The meow-full release
exists as `meow-full-v0.1.0`, and the build workflow's `full` job builds
the remaining five platforms.

## Left alone

npm publication, which ADR-2790 leaves unsettled; the five platforms the
local meow-full release does not carry yet, which the release workflow
completes; the eval suites, which no Pi runner exists for.
