---
id: EPC-2720
artifact: epic
status: approved
revised: 2026-10-04
realises: ADR-2800
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The packages publish to npm, and every target builds under Linux

Realises exactly one authorising record, ADR-2800. The epic is complete
when every meowpaw Pi package installs from npm on a machine that holds no
checkout, carries its binaries in the tarball, and makes no request at
install or load time; and when the build workflow produces all six targets
under Linux runners, with the darwin binaries signed and the Claude Code
marketplace archives unchanged in shape.

## Acceptance criteria

Taken from ADR-2800's list of how it will be known realised:

1. `npm pack --dry-run` in each package lists `bin/<triple>/meow` for all
   six platforms.
2. `pi install npm:@meowshed/meow-core` succeeds on a machine with no
   meowpaw checkout, and a Pi session from it quotes the reply shape.
3. The `postinstall` in an npm install leaves no archive and makes no
   request.
4. The workflow run's publish step reports six packages published with
   provenance.
5. A workflow run on the new build jobs produces the `bin-<target>`
   artifacts for all six targets from Linux runners.
6. A darwin binary from that run carries an ad-hoc signature, and a Pi
   session on this machine runs it.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-5209 publish the packages to npm and verify the install
      closes: REQ-4140
- [x] T-002 TSK-5210 build every target under Linux
      closes: REQ-4142

## Coverage

ADR-2800 addresses two requirements, and each lands in one task: TSK-5209
places the platforms before packing, publishes with provenance and verifies
the install from a machine with no checkout; TSK-5210 builds the six
targets under Linux and signs the darwin binaries. Together they are the
smallest set that tests the decision, because the publish, the build and
the install they are verified from are one observable result.

## Not covered

The npm account and the `NPM_TOKEN` secret, which a person holds and sets
once. Whether the packs ship to npm before the layers do, which the same
task answers by publishing all six or none.
