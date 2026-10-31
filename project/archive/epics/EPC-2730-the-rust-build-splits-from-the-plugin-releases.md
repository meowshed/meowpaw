---
id: EPC-2730
artifact: epic
status: done
revised: 2026-10-04
realises: ADR-2810
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Rust build splits from the plugin releases, and the core package alone carries the binary

Realises exactly one authorising record, ADR-2810. The epic is complete
when a plugin-only change starts no Rust build, the release workflows
fetch their binaries from the last Rust Tool run, and the meow binary
ships with the core package alone.

## Acceptance criteria

Taken from ADR-2810's list of how it will be known realised:

1. A push that changes only a plugin file starts no Rust build.
2. A plugin release fetches its binaries from the last `rust-tool` run and
   completes in minutes.
3. The core npm tarball carries six platform binaries; the other five
   carry none.
4. With the core package installed, a wrapper in any other package runs
   its subcommand through the core binary; without it, the wrapper reports
   unrun.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-5211 split the workflows and fetch the binaries from the Rust Tool run
      closes: REQ-4142
- [x] T-002 TSK-5212 ship the meow binary with the core package alone
      closes: REQ-4144

## Coverage

ADR-2810 addresses one requirement, and it lands in one task: TSK-5211
holds the workflow split and the artifact fetch, TSK-5212 the core-only
binary and the launchers' fallback. Together they are the smallest set
that tests the decision, because the split and the fallback are one
observable result.

## Not covered

The Claude Code units' switch to the shared binary. Artifact retention
beyond the platform default. Whether the meow-full release version and
the installers' pinned version converge on one source.
