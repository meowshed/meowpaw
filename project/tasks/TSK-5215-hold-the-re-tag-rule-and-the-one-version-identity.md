---
id: TSK-5215
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2750
closes: [REQ-4148]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold the re-tag rule and the one-version identity

The unit tags sit where the marketplace release cut them, the three tags
the first clean release moved are recorded as that release's one re-tag,
and the sixteen npm versions agree with their manifests.

## Acceptance criteria

1. Given the trunk's unit tags, when each tag's commit is read, then it is
   the marketplace release's commit or the unit's own release commit, and
   no tag moved twice in the release. Closed by: reading the tags' commits.
2. Given the Pi registry, when each unit's versions are listed, then the
   registry holds every published version exactly once and none was
   moved. Closed by: the registry's packuments.
3. Given all sixteen units, when `npm view @meowshed/<unit> version` runs,
   then it agrees with the unit's manifest. Closed by: the comparison run
   in the Evidence.

## What to do

Record the three tags the first clean release moved (meow-mise,
meow-gotask, meow-markdown) as the release's one re-tag; verify the
sixteen versions against their manifests; state the rule in the release
specification.

## Depends on

Nothing.

## Evidence

The first clean release cut sixteen unit tags, and three of them
(`meow-mise-v0.2.1`, `meow-gotask-v0.2.1`, `meow-markdown-v0.6.1`) were
cut from the marketplace release's tree at `7626afa1` because their tags
had never been created — that is the release's one re-tag, and no tag
moved twice. The Pi registry's packuments hold every published version
exactly once and none was moved; the five bundle versions stay as
deprecated history. `npm view @meowshed/<unit> version` agrees with each
unit's `.claude-plugin/plugin.json` for all sixteen, compared unit by
unit after the bumps. The release specification states the rule beside
its tag-driven release.

## Left alone

The five deprecated bundle versions on npm, which stay as history; the
Claude Code units' own history, which the tags follow where the release
did not move them; the per-unit-per-release bound, which the decision
leaves as a question.
