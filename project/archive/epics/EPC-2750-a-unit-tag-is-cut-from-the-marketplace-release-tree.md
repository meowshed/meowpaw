---
id: EPC-2750
artifact: epic
status: done
revised: 2026-10-04
realises: ADR-2830
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A unit tag is cut from the marketplace release tree, and one version holds on every platform

Realises exactly one authorising record, ADR-2830. The epic is complete
when every unit tag points at its marketplace release's tree or its own
release commit, no tag moved twice in the release, and the sixteen npm
versions agree with their manifests.

## Acceptance criteria

Taken from ADR-2830's list of how it will be known realised:

1. Every unit tag on the trunk points at the commit its marketplace
   release was cut from, or at the unit's own release commit, and no tag
   moved twice in one release.
2. The Pi registry holds every unit version exactly once, and no npm
   version was ever moved.
3. `npm view @meowshed/<unit> version` and the unit's
   `.claude-plugin/plugin.json` agree for all sixteen.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-5215 hold the re-tag rule and the one-version identity
      closes: REQ-4148

## Coverage

ADR-2830 addresses one requirement, and it lands in one task: TSK-5215
holds the tags where they sit, verifies the sixteen versions agree, and
records the three moved tags as the release's one re-tag. It is the
smallest set that tests the decision, because the rule and its evidence
are one observable result.

## Not covered

A future distribution's own tags. The per-unit-per-release bound, which
the decision leaves as a question.
