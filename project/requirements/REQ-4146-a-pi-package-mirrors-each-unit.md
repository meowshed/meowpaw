---
id: REQ-4146
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
elaborates: RES-0341
verification: behavioural
---

# A Pi package mirrors each unit, and one unit tag releases both

For every unit the marketplace lists there is a Pi package under the
`@meowshed` scope carrying that unit's skills, launcher and extension, and
its manifest states the same version the unit's `.claude-plugin/plugin.json`
states. A tag named `<unit>-v<version>` pushed from the trunk releases the
unit to both registries: the Claude release packs the marketplace archive
and the Pi release publishes the npm package, each skipping what its
registry already holds. The meow-full tag names the crate, not a unit, and
runs neither.

Rationale: ADR-2820 found the two registries describing the same work at
different granularities, so a version on npm named different content than
the same version in the marketplace and no tag could release both. One
unit, one version, one tag: the two histories read the same.
