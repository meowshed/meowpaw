---
id: ADR-2830
artifact: adr
status: done
revised: 2026-10-04
addresses: [REQ-4148]
supersedes: []
---

# 2830. A unit tag is cut from the marketplace release tree, once per release

## Decision

A unit's release tag is cut from the commit the marketplace release is cut
from, not from the unit's own history, and a marketplace release cuts each
unit's tag at most once. The marketplace archive for a unit is rebuilt
from that tree, so the tag and the archive name the same content even
where the tag moves: the archive is semver-compatible with the version it
carries, and the ref it sits on is the release's, not the unit's.

The Pi registry's versions are immutable and its tags are never moved: a
version published to npm holds forever, and where a version cannot publish
because the registry holds a higher one, the unit bumps a patch and both
manifests take the bump, as the four bumped units did (ADR-2820).

The version of a unit is one number across every agent platform that
ships it: the Claude Code manifest, the npm manifest and any later
distribution name the same release by the same version, so an agent's
install of a unit at a version is the same content whichever harness
loads it.

## Why

The per-unit mirror (ADR-2820) left the marketplace tags pointing at
their units' own history, but the marketplace release rebuilds each unit's
archive from the tree it runs on, so a unit whose files did not change
since its last release still ships an archive cut from a newer tree. The
first clean release cut sixteen tags and three of them sat on the
release's commit rather than any unit's own — a deviation that would have
stayed invisible, because the archive a tag names is rebuilt from the tree
the tag sits on and no check tells the two apart.

## Alternatives

| Option                                                    | Better at                                                                    | Why it lost                                                                                                                       |
| --------------------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Cut each unit tag from the release tree, once per release | The tag and the archive name the same content, and a re-tag is a bounded act | Chosen                                                                                                                            |
| Cut each unit tag from the unit's own last change         | A tag that names the unit's history                                          | The marketplace archive is rebuilt from the release tree, so the tag and the archive would name different content                 |
| Never move a tag; bump a version for every release        | Immutable refs everywhere                                                    | A release that changes nothing in a unit would still move its version, and the marketplace history would fill with empty releases |

## What it costs

A tag that moved names a commit the unit's own history does not hold, and
a reader of the tag's tree sees the release's tree, not the unit's last
change. One re-tag attempt per release bounds the churn: a second attempt
at moving the same unit's tag in one release is a finding, not a fix.

## What would reverse it

- The marketplace archive stops being rebuilt per release and becomes a
  frozen artifact of the unit's own commit, and the tags return to the
  units' own history.
- A re-tag is found to have shipped content the version does not name,
  and the rule tightens to no re-tags at all.

## Consequences

- A unit tag may sit on the marketplace release's tree, and the archive it
  names is rebuilt from that tree, so the tag and the archive agree.
- One re-tag attempt per release bounds the churn, and the three moved
  tags of the first clean release are that release's recorded re-tag.
- The npm registry's immutability is now the rule: a version conflict is
  resolved by a patch bump on both manifests, never by moving a version.
- Any future distribution inherits the one-version identity the moment it
  ships a unit.

## How I will know it was realised

1. Every unit tag on the trunk points at the commit its marketplace
   release was cut from, or at the unit's own release commit, and no tag
   moved twice in one release.
2. The Pi registry holds every unit version exactly once, and no npm
   version was ever moved.
3. `npm view @meowshed/<unit> version` and the unit's
   `.claude-plugin/plugin.json` agree for all sixteen.

## What this does not settle

- Whether a future distribution cuts its own tags or reads the
  marketplace's.
- Whether the one-re-tag bound is per release or per unit per release.
