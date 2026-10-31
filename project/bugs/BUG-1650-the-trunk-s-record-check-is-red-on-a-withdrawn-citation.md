---
id: BUG-1650
artifact: bug
status: done
severity: major
violates: REQ-3074
enters: implement
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The trunk's record check is red, on an approved defect that cites a withdrawn requirement

`paw check` exits 1 on `main`, so `mise run test-record` fails on the trunk and
a verification run records nothing: every stage `meow-checks evidence`
reports is stale, because a red run binds no result to the tree.

## Reproduction

Seen on the trunk at `6536d751`, and on `main` before the two changes this
session merged.

1. Run `mise run test-record`.
2. Read its last lines: `paw check` prints
   `project/specs/SPC-1300-the-pi-packages.md: rests on REQ-4110, which is
withdrawn, through SPC-1300 -> REQ-4130 -> BUG-1400 -> REQ-4110` and exits 1.

## What the system does

`paw check` walks a provider chain and reports a specification resting on a
withdrawn requirement: SPC-1300 states REQ-4130, whose provider is BUG-1400,
whose `violates:` names REQ-4110. ADR-2930 withdrew REQ-4110 when it deleted the
router agent, and the withdrawal did not migrate BUG-1400's citation, so the
record keeps a chain that ends at a requirement no longer in force, and the
gate is red on the trunk for it.

## What it should do, and why

REQ-3074 says the trunk's gate passes, so a verification run records its
results against the tree it ran on. ADR-2930's withdrawal should have
migrated BUG-1400's citation in the same change, as the method's migration
rule asks; nothing did, and every pull request since inherits a red gate.

## Triage

`implement`: the fix is a record change, repointing or removing BUG-1400's
`violates:` so no chain in force ends at a withdrawn requirement. Major: the
whole repository's verification evidence is stale while it stands, and
nothing a pull request does can make its stage reports bind.

## Closed by

The reproduction, now passing, and `paw check` reporting 0 findings from the
chain, in the gate's `test-record` task.

## Tasks

- [x] T-001 Repoint BUG-1400's `violates:` away from the withdrawn REQ-4110,
      in `project/bugs/BUG-1400*.md`, and rerun the record check on the trunk
      — done, then undone in the same pull request. The rerun on the trunk
      showed the record check passing with the original citation, because a
      fresh build of the checker excludes a defect's `violates` from the
      provider walk (TSK-5500, ADR-2960), so the finding this defect records
      came from the installed `meow-core` 0.9.0 binary the launchers prefer,
      not from the tree (BUG-1680). The repoint undid history the exclusion
      keeps by design, so it was reverted; the citation stays.
