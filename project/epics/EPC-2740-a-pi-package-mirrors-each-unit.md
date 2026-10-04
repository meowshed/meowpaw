---
id: EPC-2740
artifact: epic
status: approved
revised: 2026-10-04
realises: ADR-2820
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A Pi package mirrors each unit, and one tag releases both

Realises exactly one authorising record, ADR-2820. The epic is complete
when the sixteen Pi packages mirror the sixteen units, their versions
agree with the units' manifests, and one unit tag runs both releases.

## Acceptance criteria

Taken from ADR-2820's list of how it will be known realised:

1. `npm view @meowshed/<unit> version` agrees with the unit's
   `.claude-plugin/plugin.json` for all sixteen.
2. A `meow-flow-v<version>` tag runs both the Claude release and the Pi
   release, and neither runs for the other's artifacts.
3. The guards run from their own packages: a commit blocked by
   `meow-git`'s package, a publish blocked by `meow-prose-gate`'s.
4. The meow binary still sits in the core package alone.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-5213 mirror the sixteen units as Pi packages
      closes: REQ-4146
- [ ] T-002 TSK-5214 release both registries from one unit tag
      closes: REQ-4146

## Coverage

ADR-2820 addresses one requirement, and it lands in two tasks: TSK-5213
mirrors the units and splits the guards to the units that own them,
TSK-5214 points both release workflows at one tag. Together they are the
smallest set that tests the decision, because the mirror and the tag are
one observable result.

## Not covered

The four bumped patch versions' immediate release, which the next run
answers by publishing what npm does not hold. The npm bundle versions'
deprecation, which a stub or a note may address later.
