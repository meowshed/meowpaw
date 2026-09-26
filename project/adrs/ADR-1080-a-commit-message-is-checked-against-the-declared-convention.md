---
id: ADR-1080
artifact: adr
status: draft
revised: 2026-09-26
addresses:
  [
    REQ-1290,
    REQ-1294,
    REQ-1295,
    REQ-1302,
    REQ-1304,
    REQ-1308,
    REQ-1310,
    REQ-1314,
    REQ-1318,
    REQ-2816,
  ]
supersedes: []
---

# 1080. A commit message is checked against the convention the repository declares

## Decision

A new unit, `meow-scm`, holds the commit message to the convention the
repository declares in `.meowpaw/profile.toml` (REQ-1290):

```toml
[commits]
subject_limit = 72
trailers = ["Signed-off-by"]

[commits.types]
feat = "minor"
fix = "patch"
docs = "none"
```

The table declares the types a subject may carry and what each means for a
release (REQ-1318), the subject's character limit (REQ-1302), and the trailers
every message carries (REQ-1308). Where the limit is not declared it is 72, the
default RES-0014 settles on. The unit validates types against the declaration
and never against a list of its own, because the specification the grammar
comes from defines two types and permits any other (RES-0221).

The unit carries a program with two commands. `meow-scm convention` prints the
convention the profile declares, or says that none is declared. `meow-scm
check-message` reads a message and reports every way it breaks the convention:
a subject not in the form `type(scope)!: description`, a type the profile
doesn't declare, a subject over the limit, a subject ending in a full stop, a
missing declared trailer (REQ-1310), and attribution to a tool, an agent or a
vendor anywhere in the message (REQ-1294, REQ-1295). It exits non-zero on any
violation, so a message that fails isn't committed (REQ-1314).

The attribution ban holds with or without a declared convention, and nothing
in the profile turns it off, because it admits no exception (RES-0224). Where
the profile declares no `[commits]` table, the check applies the ban alone and
reports the convention as undeclared, never as met.

A skill, `meow-scm:commit`, carries the obligation to load before any commit
message, squash message or pull request title is written, in the description
form ADR-1050 states. It holds the parts of the convention a program can't
check, each as a judgement (REQ-0147): a subject in the imperative that names
the change and not the process that produced it (REQ-2816), and a body written
only where the reason isn't evident from the change, saying why and never
giving a transcript (REQ-1304). It runs `check-message` on every message before
the message is used, and carries the attribution ban as a rule in its first
screen, where compaction doesn't reach it (RES-0224).

The unit names no version control tool. Committing, signing, branching and
the working trees are a tool's, and belong to a pack.

This repository declares its convention in its profile, the five types
`CLAUDE.md` names with their release meaning, a limit of 72 and the sign-off
trailer, and retires `.claude/skills/commits/` in favour of the unit.

## Why

The temporary `commits` skill says of itself that it "retires into `meow-scm`
once that plugin is specified", and every commit this repository makes rests
on it today. It holds the convention in prose inside one repository, where a
unit would carry it to any repository that declares one.

The message is the part of source control that is text, so a tool-neutral unit
can own it, and a check over text needs no tool. The attribution ban is the
one rule RES-0224 found broken by being forgotten, not disagreed with, which is
why it needs a check that runs every time and doesn't depend on the model
recalling it.

## Alternatives

| Option                                                 | Better at                                         | Why it lost                                                                                                 |
| ------------------------------------------------------ | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| The message convention and its check, with no tool     | Working in any repository, whatever tool it uses  | Chosen                                                                                                      |
| The whole of source control in one unit, tool included | One install for commits, signing and branches     | The method may not name a tool, and signing and worktrees double the surface of a first increment           |
| A skill alone, as the temporary one is                 | Needing no program                                | A model checking its own message is how attribution slips through, and REQ-1295 asks for a mechanical check |
| A hook that blocks the commit command                  | Enforcing the check without the model choosing to | The hook would match a tool's command, which puts it in a pack, and the pack comes later                    |
| Leaving the temporary skill in place                   | Costing nothing                                   | It holds the convention for one repository in prose that no check reads                                     |

## What it costs

One more unit, with a skill description in context on every turn, measured
and budgeted as SPC-1030 requires. The program uses the interpreter ADR-1070
already depends on, and reports that it can't check a message where the
interpreter is missing, never that the message passed.

Until the pack exists, the check runs because the skill tells the model to run
it, which is weaker than a hook, and this record says so. The continuous
integration job that searches each pull request's commits for attribution
stays, because it runs whatever the model did.

## What would reverse it

- A measurement shows the model committing with `meow-scm` loaded and without
  running the check. The check would then need the hook, and the pack that
  carries it would move ahead of other work.
- The platform starts offering a unit a way to block a command without naming
  the tool. The check would then move into that.

## Consequences

- `plugins/meow-scm/` carries the program, the skill, a manifest, a budget and
  a documentation page, and the marketplace lists it.
- A specification for the commit convention states the profile's `[commits]`
  table, what `check-message` checks and how it reports.
- `.meowpaw/profile.toml` in this repository gains the `[commits]` table, and
  `.claude/skills/commits/` is deleted, with `CLAUDE.md` pointing at the unit.

## How I will know it was realised

1. `check-message` passes a message in this repository's convention, and fails
   a message with an undeclared type, a subject over the limit, a subject
   ending in a full stop and a missing sign-off, naming each.
2. It fails a message carrying a co-author trailer naming a model, or a
   "Generated with" footer, with or without a declared convention.
3. With no `[commits]` table, it applies the attribution ban, reports the
   convention as undeclared, and passes nothing as meeting a convention.
4. With the interpreter missing, it reports that it couldn't check, and exits
   non-zero.
5. This repository's last ten commits on `main` pass `check-message`.
6. `.claude/skills/commits/` is gone, and a session asked to write a commit
   message loads `meow-scm:commit` and runs the check.

The first five are fixtures a program checks. The sixth is one session.

## What this does not settle

- Signing, and verifying a signature against the named keys (REQ-1320 to
  REQ-1326, REQ-2530, REQ-2532).
- Branches, worktrees, the protected branch and squash merging (REQ-1292,
  REQ-1296, REQ-1306, REQ-1328, REQ-2534 onwards).
- Detecting a version control tool other than the default (REQ-1300).
- Whether a subject describes the process, beyond the skill's judgement: no
  check decides it, because deciding it needs a reader.
