---
id: BUG-1403
artifact: bug
status: approved
severity: minor
violates: REQ-4118
enters: implement
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The installer script cannot run on ESM and names the wrong releases

The `install-meow.mjs` shipped in `@meowshed/meow-core` calls
`require("node:fs")` inside an `.mjs` module, where `require` does not
exist: the ReferenceError is swallowed by its own `try` block and the
temporary archive is left on disk. The copies in `@meowshed/meow-code`,
`meow-mise`, `meow-gotask` and `meow-markdown` name `meow-prose-gate`
v0.4.0 as their download source, so all four claim the kernel's release
instead of their own unit's, and a reader of the log cannot tell which
unit's binary the package fetched. Neither the broken statement nor the
mislabelled source stops the install, which is why neither was seen.

## Expected

The installer downloads the package's own unit's release archive, extracts
the platform binary and cleans up after itself, on every platform the binary
ships for (REQ-4118), because the shell wrappers report unrun without it and
a wrapper that reports unrun teaches the person to uninstall the gate.

## Actual

At `84f8ee63`:
`grep -n 'require(' packages/meow-core/install-meow.mjs` finds
`require("node:fs").unlinkSync(tmp)` in a `.mjs` file;
`grep -h 'const UNIT' packages/*/install-meow.mjs` shows four packages
naming `meow-prose-gate` where only the kernel should.

## Reproduction

1. `cd packages/meow-core && node install-meow.mjs` twice.
2. The second run leaves `bin/.tmp-aarch64-apple-darwin.zip` behind,
   because the cleanup line raised a ReferenceError that its own `try`
   swallowed.
3. `grep 'const UNIT' packages/meow-code/install-meow.mjs` prints
   `meow-prose-gate`, not `meow-author`.

## Environment

Node 24 on macOS 15 (aarch64); meowpaw at `84f8ee63`; the
`install-meow.mjs` files as shipped by EPC-2700.
