---
id: BUG-1403
artifact: bug
status: approved
severity: minor
violates:
enters: requirements
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The installer script cannot run on ESM and names the wrong releases

The `install-meow.mjs` shipped in `@meowshed/meow-core` calls
`require("node:fs")` inside a `.mjs` module, where `require` does not
exist: the ReferenceError is swallowed by its own `try` block and the
temporary archive is left on disk. The copies in `@meowshed/meow-code`,
`meow-mise`, `meow-gotask` and `meow-markdown` name `meow-prose-gate`
v0.4.0 as their download source, so all four claim the kernel's release
instead of their own unit's, and a reader of the log cannot tell which
unit's binary the package fetched.

## Reproduction

Node 24 on macOS 15 (aarch64), the scripts at `84f8ee63`:

1. `cd packages/meow-core && node install-meow.mjs` twice.
2. The second run leaves `bin/.tmp-aarch64-apple-darwin.zip` behind,
   because the cleanup line raised a ReferenceError that its own `try`
   swallowed.
3. `grep 'const UNIT' packages/meow-code/install-meow.mjs` prints
   `meow-prose-gate`, not `meow-author`.

## What the system does

The cleanup silently fails and the log names a unit whose release the
package does not ship. Neither stops the install, which is why neither was
seen. The deeper finding followed in testing: any unit's own release
binary carries only that unit's feature (SPC-1080), so no per-unit download
can serve a package that bundles several units at all.

## What it should do, and why

The installer downloads a binary that serves every unit the package
bundles, extracts the platform binary, names it `meow` where the shell
wrappers look, removes the archive, and exits 0 where any step fails,
because a failed download must stop no install — the wrappers' unrun
report is the designed behaviour for a missing binary, not an error.
What the deeper finding showed wrong is REQ-4118 itself — no unit's own
release can serve a package that bundles several — so the requirements
step withdrew it and REQ-4136 states what holds in its place, which
TSK-5208 implements.

## Triage

Enters at implement, because the requirement named the binary being
findable and the shipped script missed both the ESM contract and its own
unit. Minor, because no install fails: the wrappers report unrun and the
commands pass through unchecked.

## Closed by

TSK-5208. The six scripts import everything they call, name the one
meow-full release, and two runs leave no `.tmp-*.zip` in any `bin/`;
`git status` after an install in a clean clone reports nothing.
