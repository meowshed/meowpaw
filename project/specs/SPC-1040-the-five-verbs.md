---
id: SPC-1040
artifact: spec
status: live
revised: 2026-09-24
checked-at: "#115"
states:
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
---

# The five verbs

## Scope

This covers the five verification verbs a repository declares and the unit
that resolves, reports and runs them, `meow-verbs`. It states where a verb
resolves from, what an unresolved verb reports, and what a run records.

It leaves binding a verb to a runner's tasks, language packs, running a verb
over part of the work and keeping results for evidence to later decisions,
which ADR-1070 names. How the unit's skill is written is SPC-1030's.

ADR-1070 decides it, EPC-1040 realises it, and `meow-verbs` implements it,
checked at #115.

## Boundary

| Surface                             | What it is                                                     |
| ----------------------------------- | -------------------------------------------------------------- |
| `.meowpaw/profile.toml`, `[verbs]`  | The repository's declaration: one command per verb it declares |
| `plugins/meow-verbs/bin/meow-verbs` | The program: `status` and `run <verb>...`                      |
| `plugins/meow-verbs/skills/verify/` | The skill that tells the model to use the program, not a guess |
| `docs/meow-verbs.md`                | The unit's documentation page                                  |

## Behaviour

### The verbs

There are five verbs and no others: `fmt` for formatting, `lint` for static
analysis, `typecheck` for type checking, `test` for tests and `build` for the
build (REQ-0130). A unit adds no sixth (REQ-0131), because a sixth verb is a
check with no agreed meaning across repositories.

### Where a verb resolves from

A verb resolves from the command the repository declares for it, and from
nowhere else (REQ-0134):

```toml
[verbs]
fmt = "mise run fmt-check"
lint = "mise run lint"
```

The value is one command, run by the shell from the repository's root. The
unit never guesses a command and never substitutes one it found another way
(REQ-0158), because a guessed command produces a green report with nothing
behind it.

The profile is read from the repository's root only, found as the top of the
version control working tree the program runs in, or the current directory
where there is none. It doesn't walk further up, because a repository has one
answer to what a verb means.

### What `status` reports

`meow-verbs status` reports all five verbs and runs none of them (REQ-0150).
For a resolved verb it gives the command and the file it came from. For an
unresolved verb it gives the kind, one of five (REQ-0154):

| Kind                  | Means                                                                    |
| --------------------- | ------------------------------------------------------------------------ |
| undeclared            | The profile exists and doesn't name the verb                             |
| no profile            | The repository has no `.meowpaw/profile.toml`                            |
| profile unparseable   | The profile exists and can't be read; the parser's message is shown      |
| malformed declaration | The profile names the verb with a value that isn't one command           |
| no interpreter        | The program can't run on this machine: the unit carries no binary for it |

A key under `[verbs]` that is not one of the five, and a table the unit
doesn't read, are listed as ignored, so the person learns why a setting had no
effect. An unparseable profile resolves no verb, and nothing falls back.

`status --json` gives the same report as one JSON object, for a program to
read.

### What `run` reports

`meow-verbs run <verb>...` runs each named verb in the order given and reports
each one (REQ-0144, REQ-0156):

- a verb that ran: the exact command, its exit status, how long it took, and
  its whole output, standard output and standard error in the order they
  arrived
- a verb that failed: the same, led by the last lines of its output, where a
  failing tool almost always puts its error (REQ-0135)
- an unresolved verb: its kind, and the words "not run"

An unresolved verb is never reported as passed (REQ-0136). The program ends
with a summary line naming each verb as passed, failed or unresolved, and
exits with 0 only when every named verb ran and passed: 1 when any failed, and
3 when none failed and any was unresolved. `run` with no verb named is an
error, because a run of every declared verb would pass while the undeclared
ones went unmentioned.

### The skill

`meow-verbs:verify` carries the obligation to use the program whenever the
model would format, lint, type-check, test or build, in the description form
SPC-1030 states. It runs `status` before the first `run` in a session, so the
commands the profile names are on screen before anything executes, and it
reports each verb with the kind of result the program gave, never rounding an
unresolved verb into a pass.

### The program

The program is the `verbs` subcommand of the native tool SPC-1080 states,
shipped as a binary inside the unit, so it needs nothing installed on the
machine. The launcher runs the binary for the machine's target, and where
there is none, every verb reports the kind "no interpreter" and nothing reports
passed. The kind keeps the name it had when the program needed an interpreter,
so the fixtures that define it didn't change in the port; it means the program
can't run on this machine.

## Failure paths

| Condition                                     | What happens                                                                     |
| --------------------------------------------- | -------------------------------------------------------------------------------- |
| No profile                                    | Every verb is unresolved, of kind "no profile"; `run` runs nothing and exits 3   |
| The profile doesn't parse                     | Every verb is unresolved, of kind "profile unparseable", with the parser's error |
| A verb's value isn't a string                 | That verb is unresolved, reported as a malformed declaration                     |
| The declared command exits non-zero           | The verb failed: its command, status and whole output, led by its last lines     |
| The declared command isn't found by the shell | The verb failed, with the shell's own message, because the repository named it   |
| No binary for the machine's target            | Every verb is unresolved, of kind "no interpreter"                               |
| `run` with no verb                            | An error naming the five verbs, and nothing runs                                 |
