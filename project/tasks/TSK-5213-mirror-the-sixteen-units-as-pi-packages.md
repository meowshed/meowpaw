---
id: TSK-5213
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2740
closes: [REQ-4146]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Mirror the sixteen units as Pi packages

The six layer bundles dissolve into sixteen packages named for their
units, each carrying its unit's skills, launcher and extension, its
budget, and the version the unit's Claude Code manifest states. The
guards move to the units that own them, and the four units whose bundle
versions npm holds bump a patch in both manifests.

## Acceptance criteria

1. Given the packages directory, when it is listed, then sixteen
   directories named for the sixteen units sit there and no bundle
   remains. Closed by: listing the directory.
2. Given each Pi package and its unit, when the versions are compared,
   then the package's manifest states the unit manifest's version. Closed
   by: reading the manifests.
3. Given the prose gate, the git guards, the governance guard and the
   loop guard, when their extension code runs, then each runs from its
   own unit's package. Closed by: reading the four extensions and a
   session dispatching a guard.
4. Given the meow binary, when the packages are listed for it, then the
   core package alone carries it. Closed by: the core tarball's contents
   and the other fifteen carrying none.

## What to do

Split `packages/meow-core` into core, prose and prose-gate;
`packages/meow-flow` into flow, checks, scm, git, github, loop and
unattended; `packages/meow-code` into code, author and licence. Move each
guard's handlers into its unit's extension, keep the reply-shape injection
in core and the router and step commands in flow, and place the prose
gate's fragments beside its binary's unit root, where the binary resolves
them.

## Depends on

Nothing.

## Evidence

`ls packages/` names sixteen directories, one per unit, and no bundle
remains; every package manifest's version equals its unit's
`.claude-plugin/plugin.json` version, checked unit by unit after the four
bumps. The prose gate's extension sits in `packages/meow-prose-gate` and
blocked a commit carrying `circle back` from its own package through the
core binary on PATH; `meow-git`'s extension refused a commit on the trunk
a fixture repository declares; `npm view @meowshed/meow-core` reports
0.6.1 while the other fifteen carry no binary — the core tarball's
contents list the six platform binaries alone.

## Left alone

The Claude Code plugins, whose layout the mirror follows; the meow-full
tag, which stays the Rust Tool's; the npm bundle versions already
published, which stay as history.
