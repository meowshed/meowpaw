---
id: ADR-2820
artifact: adr
status: done
revised: 2026-10-04
addresses: [REQ-4146]
supersedes: []
---

# 2820. A Pi package mirrors each unit one to one, and one tag releases both

## Decision

The Pi packages stop being layer bundles and mirror the Claude Code units
one to one: sixteen packages, `@meowshed/<unit>`, each carrying its unit's
skills, launcher and extension, each carrying its unit's version, so the
Claude Code manifest and the npm manifest agree on what a version names.

One tag releases both distributions. A tag named
`<unit>-v<version>` pushed from the trunk runs the Claude release for the
unit's marketplace archive and the Pi release for the unit's npm package;
each publishes only what its registry does not hold yet. The meow-full tag
stays the Rust Tool's alone, because the crate version is not a unit
version.

The layer bundles (`meow-core` as kernel-plus-prose, `meow-flow` as seven
units, `meow-code` as three) dissolve into their units. The guards move to
the units that own them: the prose gate's handlers to `meow-prose-gate`,
the git guards to `meow-git`, the governance guard to `meow-github`, the
loop guard to `meow-loop`. The kernel's reply-shape injection stays in
`meow-core`, the router and the step commands in `meow-flow`. The meow
binary still ships with `meow-core` alone, and every other package's
launcher falls back to `meow` on PATH (REQ-4144).

## Why

The two distributions described the same work at different granularities:
sixteen units on Claude Code, six bundles on Pi, with versions taken from
whichever unit a bundle's author happened to copy. A tag could not release
both, because no Pi package corresponded to the unit the tag named, and a
version on npm named different content than the same version in the
marketplace. One unit, one version, one tag, two registries: the history
reads the same on both sides.

## Alternatives

| Option                                                                | Better at                                                             | Why it lost                                                                                                                  |
| --------------------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Sixteen Pi packages mirroring the units, one tag for both             | The same granularity on both registries, versions that mean one thing | Chosen                                                                                                                       |
| Keep the six bundles and map a unit tag onto the bundle that holds it | Fewer packages                                                        | A bundle's version would still come from another unit's, and one tag would release a bundle whose other units did not change |
| One tag per platform, versions synced by hand                         | No restructure                                                        | Two tags for one version is the drift this decision exists to end                                                            |
| A single package for everything                                       | One tag, one install                                                  | Loses the install-only-what-you-need property on both platforms                                                              |

## What it costs

Sixteen npm packages where six stood, each with a manifest, a page and a
budget. Four units bump a patch version, because npm holds their bundle
version already and a version never republishes: `meow-flow` to 0.47.1,
`meow-mise` and `meow-gotask` to 0.2.1, `meow-markdown` to 0.6.1, in the
Claude Code manifest as well, so both sides name the same release. The
guards' extension code splits into the units that own it, which is editing
tested behaviour to move it.

## What would reverse it

- npm or Pi adds a way for one package to bundle others' resources under
  one version, and a bundle-per-layer returns.
- The sixteen packages' maintenance cost outgrows the alignment, and a
  bundle returns with versions taken from the units it holds.

## How I will know it was realised

1. `npm view @meowshed/<unit> version` agrees with the unit's
   `.claude-plugin/plugin.json` for all sixteen.
2. A `meow-flow-v<version>` tag runs both the Claude release and the Pi
   release, and neither runs for the other's artifacts.
3. The guards run from their own packages: a commit blocked by
   `meow-git`'s package, a publish blocked by `meow-prose-gate`'s.
4. The meow binary still sits in the core package alone.

## Consequences

- The two registries agree on what a version names; a reader of the npm
  history reads the same releases the marketplace history holds.
- One tag drives both releases, and each side skips what it holds.
- The guards' extension code sits in the units that own it, and the kernel
  carries only the reply shape and the binary.
- Four units carry a bumped patch version in both manifests, because npm
  held their bundle versions.
- The npm bundle versions stay published as history until a stub or a
  deprecation note addresses them.

## What this does not settle

- Whether the four bumped versions release immediately or wait for their
  next change.
- Whether the npm `0.4.0` of the old bundle `meow-core` is deprecated with
  a stub or left as history.
