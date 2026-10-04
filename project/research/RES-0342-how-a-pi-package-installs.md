---
id: RES-0342
artifact: research
status: approved
revised: 2026-10-04
elaborates: RES-0340
---

# How a Pi package installs

## Summary

Pi installs packages from three sources — npm, git and a local path — and
the three behave differently in exactly the places the install-time design
relied on. A local path loads the package in place without copying it and
runs no lifecycle script, so an install through it stays dependent on the
checkout and a `postinstall` never fires. An npm install copies the
tarball, runs the package's lifecycle scripts, and the tarball carries
whatever the package holds — the gitignored platform binaries included.

Sources: `docs/packages.md` in Pi 1.0.2, read 2026-10-04, and the behaviour
observed while installing the six meowpaw packages on 2026-10-04.

## Method

The packages documentation was read, then each install source was
exercised against the meowpaw packages on this machine: all six installed
from local paths, the load behaviour observed in sessions, the tarball
shape checked with `npm pack --dry-run`, and the missing postinstall
observed when the platform binaries were found absent after an install
that succeeded.

Nothing was measured beyond the observed behaviour; each claim names the
observation it rests on.

## What each source does

|                           | npm                             | git                                | local path                      |
| ------------------------- | ------------------------------- | ---------------------------------- | ------------------------------- |
| Where the package lives   | a copy under Pi's npm directory | a checkout reconciled to the ref   | the path given, loaded in place |
| Copied?                   | yes                             | yes                                | no                              |
| Lifecycle scripts run     | yes, npm install semantics      | yes, installed with npm            | no                              |
| What carries the binaries | the tarball, whatever it holds  | the clone, gitignored files absent | the checkout, whatever it holds |

The local-path behaviour is the one that broke the install-time design:
the packages are installed from `packages/` in this repository's checkout,
so the install dies with the checkout, and `install-meow.mjs` named as
`postinstall` never runs — the six platform binaries were found absent
after an install that reported success, and had to be fetched by hand.

The npm tarball, packed from a package whose platform directories are
gitignored, carried the binaries anyway: `npm pack --dry-run` in
`packages/meow-core` lists `bin/aarch64-apple-darwin/meow` at 2.2 MB. The
tarball therefore carries whatever platform binaries are present in
`bin/` at pack time, whatever source control says about them.

## What this means for the design

A distribution that must survive the checkout being deleted has to reach
the person through npm or git, because a local path is a pointer into the
checkout and nothing else. An npm install that must run no download
carries the binaries in the tarball, because the tarball is the whole
package. A git install that must work without a download has to fetch the
binary some other way, because the clone obeys `.gitignore` and the
platform directories are ignored — the `postinstall` is that other way,
and it fires there because a git source installs with npm.

## Conclusions

1. npm publication is the one install source that is both
   checkout-independent and free of a download at install time, provided
   the tarball carries the platform binaries.
2. A local-path install is a development install: it tracks the checkout
   and runs nothing at install time. The person installing that way runs
   the installer by hand.
3. A git-source install copies the clone without the gitignored binaries
   and runs the lifecycle scripts, so the `postinstall` downloads the
   binary there; under npm the same script is a no-op, because the
   tarball already carries every platform.
4. The npm tarball includes the platform binaries present in `bin/` at
   pack time regardless of `.gitignore`, so the release workflow must
   place all six platforms before packing, which it does from the build
   workflow's artifacts.

## Sources

Read 2026-10-04, Pi release 1.0.2:

- `docs/packages.md` — the install sources, what each copies, and when
  dependencies and scripts install.

Observed 2026-10-04 on macOS 15 (aarch64):

- All six meowpaw packages installed from local paths; `pi list` shows the
  checkout's paths.
- `node install-meow.mjs` run by hand in each package after the binaries
  were found absent.
- `npm pack --dry-run` in `packages/meow-core` showing the platform
  binary in the tarball contents.
