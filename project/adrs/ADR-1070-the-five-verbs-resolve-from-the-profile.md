---
id: ADR-1070
artifact: adr
status: approved
revised: 2026-09-24
addresses:
  [
    REQ-0130,
    REQ-0131,
    REQ-0134,
    REQ-0135,
    REQ-0136,
    REQ-0144,
    REQ-0150,
    REQ-0154,
    REQ-0156,
    REQ-0158,
  ]
supersedes: []
---

# 1070. The five verbs resolve from the profile, and an unresolved verb is reported

**Amended by ADR-1110.** The program is a subcommand of one native tool,
`meow`, written in Rust and shipped as a binary inside the unit, not a program
for an interpreter already on the machine. What the program does stands.

## Decision

A new unit, `meow-verbs`, gives the harness its five verification verbs and
no others: `fmt`, `lint`, `typecheck`, `test` and `build` (REQ-0130,
REQ-0131). In this increment a verb resolves from one place only, the command
the repository declares for it in `.meowpaw/profile.toml`:

```toml
[verbs]
fmt = "mise run fmt-check"
lint = "mise run lint"
```

A verb the profile doesn't name is unresolved. The unit never guesses a
command, and never falls back to one it found some other way (REQ-0134,
REQ-0158).

The unit carries a program with two commands. `meow-verbs status` reports, for
each of the five verbs, the command it resolves to and where that came from,
or that it is unresolved and why, and runs nothing (REQ-0150). `meow-verbs run
<verb>...` runs each named verb and reports its exact command, its exit status
and its whole output (REQ-0144, REQ-0156), with the failing part of a failed
verb's output in the report itself (REQ-0135). An unresolved verb is reported
as unresolved and never as passed (REQ-0136).

An unresolved verb states which kind it is (REQ-0154). This increment has
three:

| Kind                | Means                                                             |
| ------------------- | ----------------------------------------------------------------- |
| undeclared          | The profile exists and doesn't name the verb                      |
| no profile          | The repository has no `.meowpaw/profile.toml`                     |
| profile unparseable | The profile exists and can't be read, so no verb resolves from it |

A key the unit doesn't recognise is ignored and reported, so an older harness
keeps working against a newer profile and the user learns why a setting had no
effect. An unparseable profile resolves nothing, and the unit doesn't fall back
to anything else, because falling back would ignore what the repository tried
to say (RES-0261).

A skill, `meow-verbs:verify`, carries the obligation to use the program in
place of a command the model would otherwise guess, in the description form
ADR-1050 states. It runs `status` before the first `run` in a session, so the
commands a profile names are on screen before anything executes.

The program is written in Python and uses the interpreter already on the
machine, from version 3.11, whose standard library reads TOML. Where no such
interpreter is found, every verb is reported unresolved with that reason, and
nothing is reported as passed (REQ-3178, REQ-0136).

This repository declares its own verbs in its profile, for the checks its gate
already runs, and leaves `typecheck` and `build` undeclared, so they report as
unresolved.

## Why

The vision names this as what sets the harness apart: it reports an unresolved
verb as unresolved and never as passed, which no other harness surveyed does.
Every later step that claims work is done, from implementing a task to
verifying an epic, needs a verb it can run and a result it can cite, so the
verbs come before those steps.

Resolving from the profile alone is the smallest version that works on its
own. A repository that declares its verbs gets an honest report, with no other
unit installed. A task runner can still be used: the repository writes the
runner's command as the verb's command, and the declaration stays the
repository's own. Binding to a runner's tasks directly needs the runner's
trust model and its enumeration, which RES-0121 and RES-0122 show are the
largest surfaces in this area, and a pack to carry that knowledge, since the
method names no tool.

Resolving and running are mechanical, so a program does them (REQ-0132). A
prompt asked to resolve a verb is where a guessed command comes from.

## Alternatives

| Option                                                     | Better at                                                | Why it lost                                                                                           |
| ---------------------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| The profile only, a program and a thin skill               | Working alone, and testable without a model              | Chosen                                                                                                |
| The profile, then a runner's tasks, in one increment       | Resolving without the repository writing a line          | Needs the runner's trust boundary and a pack protocol, twice the surface for the first increment      |
| A skill that tells the model how to resolve and run a verb | Needing no program                                       | A model resolving a verb is how a command gets guessed, and it can't record output exactly (REQ-0144) |
| The program only resolves, and the model runs each command | The platform's permission prompt shows each real command | The exit status and the whole output would be what the model copies, not what the command produced    |
| A shell script                                             | Running wherever a shell does                            | It can't read TOML without a parser, and a hand-written one reads a subset and misreports the rest    |
| A program in the language Claude Code itself runs on       | An interpreter present wherever Claude Code is           | A native build of Claude Code needs no such runtime, so it isn't guaranteed on the machine either     |
| Do nothing                                                 | Costing nothing                                          | Every "done" the harness reports would rest on commands a model chose                                 |

## What it costs

One more unit, and a skill description in context on every turn where it is
installed, measured and budgeted as SPC-1030 requires.

A dependency on an interpreter the harness doesn't install. Where it is
missing, the unit reports every verb unresolved, which is honest and useless
until somebody installs it.

A repository that uses a runner writes each verb's command once, where a later
increment could read the runner's tasks.

A program's command runs behind the one permission a person grants to
`meow-verbs run`. Running `status` first puts the commands on screen, and the
platform's permission settings remain the person's to set.

## What would reverse it

- The owner reads the constitution's rule that no file in the method layer
  contains "a language name ... or a source file extension" as covering the
  program's own source. The program would then have to move into a pack, and
  the unit would carry only the skill and a protocol the pack implements.
- A measurement shows the model running a guessed command with `meow-verbs`
  installed and the skill loaded. The skill's description would then need the
  routing work ADR-1050 describes.
- The platform starts giving a unit a sandboxed runtime of its own. The
  interpreter dependency would then go.

## Consequences

- `plugins/meow-verbs/` carries the program in `bin/`, the skill, a manifest,
  a budget and a documentation page, and the marketplace lists it.
- A specification for the verbs states the profile's `[verbs]` table, the
  three kinds of unresolved, and the shape of `status` and `run`.
- `.meowpaw/profile.toml` appears in this repository, declaring `fmt` and
  `lint` for what `mise run all` runs, and `test` for the record's own checks.
- The kernel stays unaware of the unit (ADR-1060).

## How I will know it was realised

1. In a repository with no profile, `meow-verbs status` reports all five verbs
   unresolved as "no profile", and `meow-verbs run lint` reports lint
   unresolved and exits with a status that is not success.
2. With a profile that can't be parsed, all five verbs report "profile
   unparseable", and nothing runs.
3. With a profile declaring `lint` as a command that fails, `run lint` reports
   the exact command, its exit status and its whole output, with the failing
   lines in the report.
4. A key the unit doesn't recognise is reported, and every declared verb still
   resolves.
5. With the interpreter missing, every verb reports unresolved, and nothing
   reports passed.
6. This repository's `meow-verbs status` shows `fmt`, `lint` and `test`
   resolved from its profile, and `typecheck` and `build` undeclared.

Each is a fixture a program checks, and none needs a model.

## What this does not settle

- Binding a verb to a runner's tasks, and the runner's trust boundary.
- Language packs, and resolving a verb from what a repository's files show.
- Running a verb over part of the work (REQ-0140, REQ-0142).
- Keeping results where evidence can cite them (REQ-0146), and evidence
  expiring when the tree changes.
- Whether the program's source is bound by the constitution's rule on language
  names is settled, and not here: the owner approved this record reading the
  rule as governing what the harness says to a repository, not what its own
  programs are written in, and the constitution now says so.
