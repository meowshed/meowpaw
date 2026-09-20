---
id: RES-0264
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0004, RES-0261
---

# Versioning and release

## Summary

The harness ships as a set of plugins with declared dependencies, and nothing
in this corpus says what a version number means, what a breaking change is, or
how a repository upgrades. The platform's own answer has a sharp edge: a plugin
that omits its version updates automatically, so leaving the field out is a
decision to give every installation whatever is current. Versioning
conventions require a declared public interface, which for a harness is neither
obvious nor small - a pack's contract is the verbs, the artifact kinds, the
front-matter fields and the record's paths. And a plugin caches per version
with a fortnight's grace, which is the upgrade story the design has to fit.

Research for how the harness is versioned, released and upgraded. It does not
cover what a repository declares, which is
[RES-0261-the-profile.md](RES-0261-the-profile.md), nor the platform's plugin
mechanism generally, which is [RES-0004-platform.md](RES-0004-platform.md).

## The question

A repository installs a dozen plugins from a marketplace. One of them changes.
Nothing currently says whether the repository's record is still valid, whether
the other eleven still work with it, or how anyone would find out.

## Method

The published versioning specification and the changelog convention were
fetched and read on 2026-09-20 for their normative rules, which we quote in
full.

The platform's plugin reference was fetched and read for the manifest schema,
the version-resolution order, dependency constraints, and the caching and
update behaviour.

Nothing was released. No plugin of this project's has been versioned or
published, so this document describes a process that has not been run.

## Findings

### Omitting the version is a decision somebody takes

The manifest's only required field is the name. Version is optional, and the
behaviour when it is absent is the finding:

- **With a version set**, the plugin pins to it and users receive updates only
  when it is bumped.
- **Without one**, the version comes from the marketplace entry, then a git
  tag, and failing both there is no pinning - users receive updates
  automatically.

So a harness that ships without versions hands every installation whatever is
current at the moment they sync. For a tool that writes to people's
repositories and changes what their checks mean, that is not a neutral default.

The corollary matters for development: a plugin loaded in place does not
auto-update and its root path is stable, which is why local iteration behaves
differently from an installed copy and why a bug that only appears after
installation is a real category.

### A version requires a declared public interface, and the harness's is not obvious

The specification is explicit: software using it _"MUST declare a public API.
This API could be declared in the code itself or exist strictly in
documentation."_ Major is for incompatible changes, minor for backward
compatible additions, patch for backward compatible fixes.

For a plugin that is a library the interface is the functions. For this harness
it is none of those, and enumerating it is most of the work:

| Surface                                          | Breaking a promise means                                             |
| ------------------------------------------------ | -------------------------------------------------------------------- |
| The five verbs and their outcomes                | A verb changes meaning, or an outcome is added that callers collapse |
| The artifact kinds and their front-matter fields | A field is renamed, or one becomes required                          |
| The record's paths and identifier formats        | An existing corpus stops being found or parsed                       |
| The profile's keys                               | A repository's declaration stops taking effect                       |
| Command names and their arguments                | A user's invocation or another plugin's call breaks                  |
| The evidence format                              | Past evidence stops being readable                                   |

That table is the public interface, and it is why a harness's major version is
expensive: most of those surfaces have a corpus already written against them.

### Version zero exists for exactly this project's situation

_"Major version zero (0.y.z) is for initial development. Anything MAY change at
any time. The public API SHOULD NOT be considered stable."_

This harness has no released version, no installed users and a design that is
still moving - two artifact kinds were renamed and a template was rewritten in
a single day's work. Claiming stability now would be false, and the convention
already has the honest option.

The useful consequence is that the expensive obligations - migration,
deprecation windows, compatibility ranges - attach to the first release and not
to today, and the research says when they attach, pretending nothing about
today.

### Released versions are immutable, which is the same rule the record follows

_"Once a versioned package has been released, the contents of that version MUST
NOT be modified. Any modifications MUST be released as a new version."_

That is precisely the rule this corpus already applies to a record: a decision
is superseded, and edited never. The same reasoning produces both - a reader
has to be able to rely on what a name refers to.

The platform reinforces it mechanically: each version is cached in its own
directory, so two versions coexist on disk, and neither overwrites the other.

### Dependencies between plugins have constraints, and auto-enabling has a consequence

A plugin may declare dependencies with version ranges, and a required plugin
auto-enables when its dependent is enabled - after which it cannot be disabled
until the dependent is.

For a harness split into a kernel, method plugins and packs, that is the
mechanism which makes the split safe: a pack depends on the kernel's contract
version and assumes nothing about it.

The constraint syntax matters for what the harness promises. A pack that
depends on a minor-compatible range accepts new kernel features; one that pins
a patch range rejects them. The choice is a statement about how tightly the
pack is coupled to the kernel's behaviour, and somebody takes it deliberately,
where a template would decide it by accident.

### Upgrades have a grace period, and it is the shape of the rollout problem

When a plugin updates, the previous version's directory is orphaned for about
a fortnight, which is a grace period for sessions still running against it. The
plugin root path changes on update, and a reload switches to the new one.

Two things follow. A running session is not disturbed by an upgrade, which is
correct. And anything a plugin stores relative to its own root is lost on
update, which is why the platform supplies a separate persistent directory that
survives updates - a distinction that has to be respected or a version bump
quietly deletes state.

### The changelog is for people and is not the commit log

The convention's first principle is that changelogs are _"for humans, not
machines"_, and it discourages commit dumps directly: commits document steps in
the source's evolution, while a changelog communicates noteworthy differences
to users, and a commit log carries noise - merges, documentation, refactoring.

Its six sections are added, changed, deprecated, removed, fixed and security,
with an unreleased section at the top.

The deprecation guidance is the operationally useful part: a user should be
able to upgrade to a version that _lists_ deprecations, remove what is
deprecated, and upgrade again when those become removals. That is a two-release
window, stated as a property of the changelog, which no policy document
carries.

For this harness the same rule applies to the record, where the convention
applies it to code. A front-matter field that is going away is announced as
deprecated while both forms are accepted, and removed in a later release -
because the thing that breaks is not a caller but a corpus somebody already
wrote.

### What a release of this harness has to contain

Reading the above against what the harness actually ships:

- **A version on every plugin**, so nobody is upgraded without choosing to.
- **A declared contract version** for the kernel, which packs depend on with a
  range.
- **A changelog per plugin**, written for the person whose repository it
  changes.
- **A stated compatibility claim**: which platform versions, and which record
  formats.
- **Migration notes wherever the record's shape changed**, which is the
  neighbouring research.

## Conclusions

1. Every plugin the harness ships carries a version, because omitting it gives
   every installation whatever is current, and this tool writes to people's
   repositories. 2. The public interface is declared explicitly and includes
   the verbs and their outcomes, the artifact kinds and their front matter, the
   record's paths and identifier formats, the profile's keys, the command
   surface and the evidence format. 3. The harness stays at major version zero
   until its interface stops moving, which is the convention's own provision
   for a design still changing, and it claims no stability nobody can keep. 4.
   Migration, deprecation windows and compatibility ranges attach at the first
   release, and the design says so, implying nothing about today. 5. A released
   version is never modified; a change is a new version, which is the same rule
   the record already follows for decisions. 6. A pack depends on the kernel's
   contract version with a deliberate range, and the tightness of that range is
   a statement about coupling. 7. A required dependency auto-enables and cannot
   be disabled while its dependent is enabled, which is what makes the plugin
   split safe and has to be accounted for when recommending an installation. 8.
   Nothing is stored relative to the plugin's own root if it must survive an
   upgrade, because that path changes on update and the previous directory is
   orphaned after a grace period. 9. A changelog is written for the person
   whose repository changes, not generated from commits, and carries the six
   standard sections. 10. A deprecation is announced in one release and removed
   in a later one, so a user can upgrade, remove what is deprecated, and
   upgrade again. 11. A deprecated front-matter field is accepted alongside its
   replacement during that window, because what breaks is a corpus somebody
   already wrote, where a caller could be changed. 12. A release states which
   platform versions it supports, since the platform's own surface is versioned
   and several fields this design relies on arrived in specific releases.

## Sources

All read 2026-09-20.

- [Semantic Versioning 2.0.0](https://semver.org/) - the meanings of major,
  minor and patch increments; the requirement to declare a public interface in
  code or in documentation; major version zero as initial development where
  anything may change and the interface should not be considered stable; and
  the rule that a released version's contents must not be modified. - [Keep a
  Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) - that changelogs are
  written for people, and never for machines; the six sections; the unreleased
  section; the argument against commit dumps, with merge and documentation
  noise as the reason; and the deprecation guidance that a user should be able
  to upgrade, remove what is deprecated, and upgrade again. - [Plugins
  reference](https://code.claude.com/docs/en/plugins-reference) - the manifest
  schema with only the name required; the version-resolution order through the
  manifest, the marketplace entry and a git tag, with automatic updates when
  none is set; dependency declarations with range constraints and the
  auto-enable behaviour; per-version caching with the previous version orphaned
  for about a fortnight; the plugin root changing on update against the
  persistent data directory that survives it; and that plugins loaded in place
  do not auto-update.
