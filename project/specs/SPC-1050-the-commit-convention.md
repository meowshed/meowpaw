---
id: SPC-1050
artifact: spec
status: live
revised: 2026-09-26
checked-at: "#130"
states:
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
---

# The commit convention

## Scope

This covers the commit message: the convention a repository declares for it,
the unit that checks a message against that convention and against the
attribution ban, `meow-scm`, and the skill that holds what no check can decide.

It leaves the commands that make a commit, signing, branches and working trees
to a pack, which ADR-1080 names, and how the skill is written to SPC-1030.

ADR-1080 decides it, EPC-1050 realises it, and `meow-scm` implements it,
verified under issue 130.

## Boundary

| Surface                              | What it is                                                         |
| ------------------------------------ | ------------------------------------------------------------------ |
| `.meowpaw/profile.toml`, `[commits]` | The repository's convention: types, subject limit and trailers     |
| `plugins/meow-scm/bin/meow-scm`      | The program: `convention` and `check-message`                      |
| `plugins/meow-scm/skills/commit/`    | The skill that writes a message and runs the check before using it |
| `docs/meow-scm.md`                   | The unit's documentation page                                      |

## Behaviour

### The convention

A repository declares its convention under `[commits]` (REQ-1290):

```toml
[commits]
subject_limit = 72
trailers = ["Signed-off-by"]

[commits.types]
feat = "minor"
fix = "patch"
docs = "none"
```

`types` names each type a subject may carry and what it means for a release,
one of `major`, `minor`, `patch` or `none` (REQ-1318). `subject_limit` is the
subject's length in characters, 72 where it isn't declared (REQ-1302).
`trailers` names each trailer every message carries (REQ-1308). A key the unit
doesn't read is reported as ignored, as `meow-verbs` reports one.

### What `convention` reports

`meow-scm convention` prints the declared types with their release meaning,
the limit, and the trailers. Where the profile has no `[commits]` table, or no
profile exists, it says the convention is undeclared.

### What `check-message` checks

`meow-scm check-message` reads a message from a file named on the command line,
or from standard input where none is named. It reports every violation, each
naming the rule and the line:

| Check          | Fails when                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------ |
| subject form   | The first line isn't `type(scope)!: description`, where the scope and the `!` are optional |
| declared type  | The type isn't one the convention declares                                                 |
| subject length | The first line is longer than the limit                                                    |
| subject ending | The first line ends in a full stop                                                         |
| blank line     | A body follows the subject without an empty line between them                              |
| trailer        | A trailer the convention declares is missing                                               |
| attribution    | Any line credits a tool, an agent or a vendor (REQ-1294, REQ-1295)                         |

The attribution check matches a co-author trailer naming a model or its
vendor, a "Generated with" footer, and a vendor's no-reply address. It holds
whatever the profile says and can't be turned off. It matches the attribution
pattern and not a bare name, so a path such as `plugins/meow-core/` or the
name of the product a harness targets doesn't trip it.

Where no convention is declared, only the attribution check runs, and the
report says the convention is undeclared: a message is never reported as
meeting a convention nobody stated. `check-message` exits 0 when nothing
failed and a convention was declared, 1 on any violation, and 3 when nothing
failed but the convention is undeclared (REQ-1314).

### The skill

`meow-scm:commit` carries the obligation to load before a commit message, a
squash message or a pull request title is written, in the form SPC-1030
states. It holds the two rules a program can't decide, as judgements: the
subject is in the imperative and names the change, never the process that
produced it (REQ-2816), and a body is written only where the reason isn't
evident from the change, says why, and is never a transcript (REQ-1304). It
runs `check-message` on the message before the message is used, and carries
the attribution ban as a rule on its first screen.

### The program

The program is the `scm` subcommand of the native tool SPC-1080 states,
shipped as a binary inside the unit. Where the unit carries no binary for the
machine, `check-message` says it couldn't check the message and exits 3, and
never reports a pass.

## Failure paths

| Condition                                      | What happens                                                                    |
| ---------------------------------------------- | ------------------------------------------------------------------------------- |
| No profile, or no `[commits]` table            | The attribution check runs alone; the convention is reported undeclared, exit 3 |
| The profile doesn't parse                      | Nothing is checked against a convention; the parser's error is shown, exit 3    |
| `types` isn't a table, or a meaning is unknown | The declaration is reported as malformed, and the type check doesn't run        |
| The message is empty                           | Reported as an empty message, exit 1                                            |
| No binary for the machine's target             | Reported as unchecked, exit 3                                                   |
