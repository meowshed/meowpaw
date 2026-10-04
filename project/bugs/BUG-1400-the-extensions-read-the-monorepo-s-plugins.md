---
id: BUG-1400
artifact: bug
status: approved
severity: major
violates: REQ-4108, REQ-4110, REQ-4112
enters: implement
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Pi extensions read the monorepo's plugins directory

Every Pi package extension shipped in EPC-2700 loads its prompt files
through a path that walks up to this repository's `plugins/` directory:
`join(packageRoot, "..", "..", "plugins", plugin, ...)`. That path holds
only in a checkout of the meowpaw monorepo. After `pi install`, the
package sits in Pi's own package directory with no `plugins/` beside it,
so every read fails and the extension silently runs with empty strings.

## Reproduction

Pi 1.0.2 on macOS 15 (aarch64), the packages at `84f8ee63`:

1. `cp -r packages/meow-core /tmp/` and `pi -e ./meow-core -p '...'` from
   `/tmp`.
2. Ask the model which reply-shape rules it holds: it answers none,
   because `before_agent_start` pushed an empty string into the guidelines.
3. `grep -n 'readPluginFile' packages/*/extensions/*.ts` shows every prompt
   load resolving `packages/<name>/../../plugins/<plugin>/...`.

## What the system does

Installed alone, `@meowshed/meow-core` injects no reply shape, the prose
gate's judge prompt loads as an empty string, and `@meowshed/meow-flow`'s
router answers "Router unavailable" for every request, each with no error
reported, because the failed read is swallowed and the empty string carried
on. The TSK-5201 and TSK-5202 acceptance criteria named manual session
tests that were never run against an installed package; the packages were
marked done from a monorepo checkout where the path accidentally holds.

## What it should do, and why

The kernel injects the reply shape (REQ-4108), the flow loads the router's
prompt and carries the reply shape into its nested call (REQ-4110,
REQ-4112), from files bundled inside each installed package. A package that
reads its own directory works wherever Pi puts it, and one that cannot find
its files fails visibly instead of running on empty strings.

## Triage

Enters at implement, because the requirements named the behaviour and the
extension shipped a mechanism they don't cover. Major, because every
behavioural feature of the shipped packages silently no-ops outside the
monorepo, and nothing reported it.

## Closed by

TSK-5206. Installing `packages/meow-core` copied to `/tmp` and asking
which reply-shape rules the model holds returns R1, R2 and R10 quoted, and
`grep -rn 'readPluginFile\|\.\./\.\./plugins' packages/` reports no match.
