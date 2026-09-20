---
id: RES-0261
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0031, RES-0058
---

# The repository profile

## Summary

The profile is what a repository declares to the harness, and seventeen
documents in this corpus depend on one without any of them saying what it
contains or where it lives. The two closest precedents disagree productively:
one walks up the directory tree and stops at a marked root, the other has five
fixed scopes with a managed level nothing can override. Both ignore keys they
do not recognise, which is the rule that lets the format change without
breaking installations. And a profile that names commands is executable by
proxy, so it inherits the trust question that the task runners already answer.

Research for the file the initialisation step writes, the diagnostic reads, and
verb resolution consults. It does not cover what the harness does with the
answers, which is [RES-0031-routing.md](RES-0031-routing.md), nor the
initialisation step itself, which is [RES-0058-init.md](RES-0058-init.md).

## The question

The gate resolves a verb from the profile before any pack is consulted. The
diagnostic reports which verbs resolve and from where. Onboarding writes one.
Seventeen documents refer to it.

Nothing says what is in it, what format it is, where it sits, what happens when
it is malformed, or what happens when two of them disagree.

## Method

We fetched and read the two closest precedents on 2026-09-20. The
per-repository style declaration that many tools read gave its discovery and
compatibility rules. The platform's own settings documentation gave its scope
model and its treatment of shared against personal files.

The task-runner research already in this corpus supplied the trust question,
and the survey documents supplied what other harnesses put in their equivalent
files.

Nothing was implemented. No profile was written and no schema was validated, so
every statement here is a design claim measured against two working precedents
rather than a result.

## Findings

### Two precedents, and they disagree about discovery

The style declaration walks up. A tool searches the current directory and
then each parent, stopping at the filesystem root or at a file marked as the
root. Properties from closer files take precedence, and sections are applied in
the order they are read.

The platform's settings do not walk. Five named scopes - managed, command
line, project local, shared project, user - with a fixed precedence, and the
managed level is one _"nothing you set overrides"_ apart from a few
security-sensitive exceptions.

The difference is about what the file describes. A style declaration describes
files, which nest, so walking up is natural. Settings describe a session, which
does not nest, so scopes are fixed.

A profile describes a repository. That is closer to settings than to style. A
repository has one answer to _what does `test` mean here_, and a nested
directory that needs a different answer is a different part of the project, and
never a different project.

So the profile does not walk up past the repository root. What it does do is
allow a part to declare its own, which is the monorepo question and belongs to
that document.

### Both precedents ignore the keys they fail to recognise, which is the compatibility rule

The style specification is explicit: a tool should _"ignore any unrecognized
properties and property values ... for future compatibility, since new
properties and permitted values will be added in the future."_

That single rule is what allows a format to grow while old installations keep
working, and it is the opposite of what a schema validator does by default.

The resolution for a profile is that **an unknown key is ignored and reported**
rather than being an error or being silent. Ignoring it keeps an old harness
working against a new profile. Reporting it tells the user why the thing they
configured is having no effect, which otherwise takes an afternoon to find.

### The shared-against-personal split is not optional

Both precedents have it, and the platform's version carries two details this
profile copies. The tool that creates the personal file keeps it out of version
control, and the user is told to exclude it themselves where they create it by
hand.

For a profile the split falls in an obvious place. What `test` means is the
repository's. Which of three installed type checkers _this developer_ wants is
theirs. The first is committed and the second is not.

The trap is the middle case: a machine-specific path to a tool. That looks like
a personal setting and is usually a symptom - the tool should be found through
the project's own toolchain declaration rather than named by path.

### A profile that names commands is executable by proxy

The task runners in this survey both have a trust boundary. One requires a
configuration to be trusted before it parses it, because it may execute code.
The other prompts on first use of a remote definition and remembers the answer.

A profile naming the command that `test` runs is the same hazard wearing
different clothes. Reading it is safe; acting on it runs whatever a repository's
author wrote, with the user's environment.

Two consequences follow, and they are the same ones the runner research
reached. The harness does not grant trust on the user's behalf. And a profile
from a repository the user has not worked in is reported before it is used
rather than silently obeyed.

The platform supplies the mechanism for the second half. A repository's own
permission settings are where a person pre-approves the commands the gate will
run, and the initialisation step proposes them and imposes nothing.

### What belongs in it, and what does not

The test for inclusion is whether the harness would otherwise have to guess.

In:

- **Verb resolution.** What each of the five verbs runs, per part where the
  repository has parts. This is the reason the file exists.
- **Where the record lives.** The paths for each artifact kind, because the
  harness fixes what a kind means and the repository declares where it sits.
- **Declared vocabularies.** The commit types this repository uses, the artifact
  kinds it has added, the statuses it recognises - each of which a check
  validates against the declaration rather than against a built-in list.
- **The supported set.** Which languages and tools this repository expects to
  be resolvable, so a silently missing pack is a finding rather than a
  surprise.
- **Named exceptions.** What is exempt from which check, with a reason,
  because an exemption with no reason becomes permanent.

Out:

- **Anything the ecosystem already declares.** The toolchain versions are in
  the toolchain manager's file; the package manager is in the lockfile. A
  profile that repeats them creates a second copy that drifts.
- **Permissions.** The platform owns those, and a second permission model that
  the platform does not enforce is decoration.
- **Prose.** What the project is and how it works belongs to the constitution
  and the documentation; a profile is data.
- **Anything derivable.** If detection can answer it, detection answers it and
  the profile is consulted only to override.

### The format follows from who writes it

Three parties read a profile: a person, the harness, and a check. Two of them
write it: a person by hand and the harness during onboarding.

That argues for a format with comments, because the exceptions need reasons and
a reason that cannot sit beside the thing it justifies ends up nowhere. It
argues against the one format that has no comments at all, which is the same
format the platform's own settings use. This document names that instead of
glossing it, since consistency with the platform pulls the other way.

The corpus's own material is Markdown with structured front matter, and the
front matter is where every artifact's machine-readable facts already live. A
profile in the same shape is one parser for the whole record.

### Malformed is a distinct outcome from absent

A profile that does not parse is no repository without a profile. Collapsing
the two produces the worst possible report - _this project declares nothing_ -
when what happened is that line fourteen has a tab in it.

So three states, and each has a different action: absent, unparseable with the
location of the fault, and parsed with unknown keys named.

The diagnostic reports all three. The gate treats the second as unresolved
rather than as an absent declaration, because falling back to detection after a
parse failure silently ignores what the repository tried to say.

## Conclusions

1. The profile is the repository's declaration to the harness, and exists
   so that the harness does not guess what the repository could have said.
2. It does not walk up past the repository root, because a repository has
   one answer to what a verb means, unlike a style declaration that describes
   files.
3. An unknown key is ignored and reported, which keeps an older harness
   working against a newer profile while telling the user why their setting had
   no effect.
4. A shared file and a personal file are separate, the first committed and
   the second excluded, and the harness excludes it when it creates it.
5. A machine-specific tool path in a personal profile is reported as a
   symptom, since the tool should be found through the project's toolchain
   declaration.
6. A profile that names commands carries the same trust question as a task
   runner's configuration, so the harness never grants trust on the user's
   behalf and reports an unfamiliar repository's profile before acting on it.
7. Pre-approval of gate commands belongs to the platform's permission
   settings, which the harness proposes and does not impose.
8. It carries verb resolution, the record's paths, the declared
   vocabularies, the supported set and the named exceptions with reasons.
9. It carries nothing the ecosystem already declares, nothing the platform
   owns, no prose, and nothing detection can answer.
10. Every declared vocabulary is what its check validates against, rather
    than a list built into a tool.
11. The format carries comments, because an exemption without its reason
    becomes permanent, and it shares the record's front-matter shape so one
    parser reads the whole corpus.
12. Absent, unparseable and parsed-with-unknown-keys are three distinct
    outcomes, each reported differently.
13. An unparseable profile resolves verbs as unresolved rather than falling
    back to detection, because falling back silently ignores what the
    repository tried to say.

## Sources

All read 2026-09-20.

- [EditorConfig](https://editorconfig.org/) - discovery by walking up from the
  current directory until the filesystem root or a file marked `root = true`;
  properties from closer files taking precedence and sections applied in read
  order; and the instruction to ignore unrecognised properties and values for
  future compatibility because new ones will be added.
- [Settings files and precedence](https://code.claude.com/docs/en/settings) -
  the five scopes from managed down to user and their fixed precedence; that
  nothing a user sets overrides managed settings apart from a few
  security-sensitive exceptions; the shared project file against the project
  local file; and that the tool keeps the local file out of version control
  when it creates it and tells the user to exclude it when they create it by
  hand.
- [RES-0122-mise.md](RES-0122-mise.md) and
  [RES-0123-go-task.md](RES-0123-go-task.md) - the trust boundaries on
  configuration that may execute code, and the rule that the harness does not
  grant trust.
- [RES-0056-gate.md](RES-0056-gate.md) and
  [RES-0160-doctor-command.md](RES-0160-doctor-command.md) - the consumers of
  the profile, and the outcome vocabulary the parse states have to fit into.
