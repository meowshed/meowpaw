---
id: RES-0160
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0062, RES-0056
---

# `/meow:doctor`

## Summary

Nobody in the survey has this command, and that absence is the finding. Every
harness can fail because a tool is missing or a verb does not resolve, and none
says so. It answers whether the repository can be worked on at all, which is
what turns the gate's unresolved outcome into an action, and it never collapses
unresolved into installed-but-missing. It repairs nothing, because a diagnostic
that repairs cannot be run to find out what is wrong.

The read-only command that answers whether the repository can be worked on at
all. Its sibling [RES-0062-status.md](RES-0062-status.md) answers where the
work stands.

## Who has an equivalent

Nobody, in the survey. The nearest is `sdd-harness`'s
`/kiro:harness-validate`, which is a structural-integrity check over the
harness's own files rather than a diagnosis of the repository's environment.

That absence is itself the finding: every harness in the survey can fail
because a tool is missing, a verb does not resolve or a profile does not parse,
and none of them has a command that says so.

## Method

The surveyed harnesses' own command templates and the internal repositories'
commands were read on 2026-09-20 for what a comparable command does, and the
platform's command documentation was fetched for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## The question it answers

Not _where is the work_ but _can this repository be worked on_:

- **Which verbs resolve, to what, and from where** - the profile, or a named
  pack, or not at all.
- **Which resolve to a command whose tool is not installed.** This is the
  fourth outcome the gate reports and cannot explain, and it is where the
  explanation lives.
- **Which packs are installed and which markers they matched.**
- **Which optional tool packs are installed and which of their tools are
  missing.**
- **Whether the profile parses**, and which keys are defaulted.
- **State**: present, absent or unreadable.

## Its purpose is to make an unresolved verb actionable

The gate reports three outcomes - pass, fail, unresolved - and separately
distinguishes an environment failure where the command resolved but its tool is
absent. All of those are facts. None of them says what to do.

`doctor` is what turns each into an action: _this verb is unresolved because no
pack matched and the profile declares nothing; installing this pack or
declaring this command would resolve it._

The distinction it must never collapse is **unresolved** against
installed-but-missing. The first is a gap in configuration and the second
is a gap in the machine, and they have different fixes performed by different
people.

## It repairs nothing, which is the point

A diagnostic command that repairs what it finds cannot be run to find out what
is wrong. The moment it fixes something, its output stops describing the
repository and starts describing the repository after it ran.

It also writes no cache. A diagnosis that reads a cache reports what was true
when the cache was written, which is exactly the failure a diagnostic exists to
catch elsewhere.

## The environment belongs in the report

Because several findings here depend on the machine rather than the project -
a tool version, a missing binary, a filesystem that does not support a feature
another tool wanted - the report names the machine-dependent ones as such.

Otherwise a user reads _this repository is broken_ when the correct reading is
_this machine cannot build this repository_, and the two produce very different
next actions.

## What it must refuse

To install anything.

To repair a profile, rewrite a configuration, or create a missing file.

To report a missing optional tool as a failure. An optional pack whose tool is
absent is a capability the harness does not have here, which is a statement
rather than a defect.

## Conclusions

1. It answers whether the repository can be worked on, distinctly from
   where the work stands.
2. It says what would resolve each unresolved verb, which is what turns the
   gate's unresolved outcome into an action.
3. It distinguishes unresolved from installed-but-missing, because one is a
   configuration gap and the other is a machine gap with a different fix.
4. It names machine-dependent findings as such, so a user does not read
   _this machine cannot build this_ as _this repository is broken_.
5. It repairs nothing and writes nothing, including a cache, because a
   diagnostic that repairs cannot be run to find out what is wrong, and one
   that reads a cache reports what was true earlier.
6. A missing optional tool is reported as an absent capability, not as a
   failure.
7. It reports which packs matched which markers, so a wrong detection is
   visible rather than inferred from a wrong command.

## Sources

All read 2026-09-20.

- [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness) -
  `/kiro:harness-validate` as a structural-integrity check, the nearest
  equivalent found in the survey.
- [RES-0056-gate.md](RES-0056-gate.md) - the three gate outcomes and the fourth
  case where the command resolved but its tool is absent.
- [RES-0062-status.md](RES-0062-status.md) - the sibling command and the
  read-only discipline both hold.
