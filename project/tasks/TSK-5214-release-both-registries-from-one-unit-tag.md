---
id: TSK-5214
artifact: task
status: approved
revised: 2026-10-04
epic: EPC-2740
closes: [REQ-4146]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Release both registries from one unit tag

The Pi release triggers on the same `meow-*-v*` tags the Claude release
does, resolves the unit from the tag, and publishes only that unit's npm
package; the meow-full tag runs the Rust Tool's release alone.

## Acceptance criteria

1. Given a `meow-flow-v<version>` tag pushed from the trunk, when both
   release workflows evaluate, then the Claude release packs the unit's
   marketplace archive and the Pi release publishes the unit's npm
   package. Closed by: pushing a tag and reading both runs.
2. Given the `meow-full-v<version>` tag, when the workflows evaluate,
   then the Rust Tool publishes the meow-full release and neither release
   workflow runs. Closed by: the guards in both release workflows.
3. Given a registry that holds the tagged version already, when the
   release runs, then it skips that side. Closed by: the marketplace's
   released-archive path and npm's already-published check.

## What to do

Point the Pi release's trigger at `meow-*-v*`, resolve the unit from the
tag without the `-pi-` infix, and guard both release workflows against
the `meow-full-v*` tag.

## Depends on

- TSK-5213 (blocking): the sixteen mirrored packages, whose versions the
  tag names.

## Evidence

Not yet. This line stays first until every verb has passed.

## Left alone

The Rust Tool's triggers, which the crate owns; the dispatch routes,
which the person runs by hand; the marketplace's released-archive reuse,
which the pack step keeps.
