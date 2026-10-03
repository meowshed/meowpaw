---
id: SPC-1240
artifact: spec
status: live
revised: 2026-10-03
states:
  [
    REQ-2710,
    REQ-2712,
    REQ-2714,
    REQ-2716,
    REQ-2718,
    REQ-2720,
    REQ-2722,
    REQ-2724,
    REQ-2726,
    REQ-2727,
    REQ-2728,
    REQ-2730,
    REQ-1426,
  ]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The hooks the harness ships

## Scope

This covers every hook a unit of the harness declares: how it answers, how
much work it does, what it never does, how it is declared, what it does when
its program is missing, and the check that holds all of it. It is a contract
across the units that ship hooks, so each unit's own specification states
what its hook checks and this one states what every hook keeps.

It leaves what each hook checks to its unit's own specification, which cites
this one, and the text of a prompt hook to the specification of how the
harness writes a prompt.

ADR-2450 decides it, ADR-2700 names the prose gate as the one exception to
two of its rules, and ADR-2710 decides what a hook does when its program is
missing.

## Boundary

| Surface                                | What it is                                                                |
| -------------------------------------- | ------------------------------------------------------------------------- |
| `plugins/<unit>/hooks/hooks.json`      | The unit's hooks: the event, the matcher, the command and its timeout     |
| `plugins/<unit>/bin/<unit>`            | The launcher each hook's command runs, with one subcommand                |
| `plugins/<unit>/README.md`, `## Hooks` | One sentence per hook saying what it stops                                |
| `meow-author check`                    | The check that fails a hook breaking a rule below, run in the `lint` verb |

The hooks the units declare:

| Unit              | Event                                  | Subcommand         | What it stops                                                  |
| ----------------- | -------------------------------------- | ------------------ | -------------------------------------------------------------- |
| `meow-flow`       | `SessionStart`                         | `status --waiting` | Nothing: it reports what waits at a gate                       |
| `meow-git`        | `PreToolUse` on Bash                   | `commit-guard`     | A commit on the declared trunk                                 |
| `meow-git`        | `PreToolUse` on Bash                   | `push-guard`       | A push of a commit whose message or signature fails            |
| `meow-github`     | `PreToolUse` on Bash                   | `governance-guard` | A `gh` command that changes governance, until a person answers |
| `meow-loop`       | `PreToolUse` on Bash, Edit and Write   | `guard`            | A write into a run's own state, or a status the run can't give |
| `meow-prose-gate` | `PreToolUse` on Bash                   | `check`            | A publish whose text breaks a rule the gate holds              |
| `meow-checks`     | `PostToolUse` and `PostToolUseFailure` | `revision`         | Nothing: it advances the revision counter                      |

## Behaviour

### How a hook answers

A hook answers in one of three ways: it denies with a reason, it asks the
person through the platform, or it says nothing (REQ-2714). It denies by
exiting 2 with its reason on standard error, or by printing a
`permissionDecision` of `deny` with the reason, so the platform hands the
reason to the model. It asks by printing a `permissionDecision` of `ask`,
because a hook has no terminal of its own and the platform owns the prompt
(REQ-2722). `meow-github`'s governance guard is the one hook that asks.

A hook never answers `allow`, because that skips the permission flow the
repository owns for whatever the hook matched (REQ-2720). It never returns an
`updatedInput`, because a rewritten call runs something nobody asked for; it
denies with the reason, and the model redoes the call deliberately
(REQ-2718). Silence, a crash, an exit status other than 0 and 2, and a
timeout all read as abstention: the call goes through the repository's own
permission flow, never as approved by the hook (REQ-2714).

### How much a hook does

A blocking hook runs its unit's launcher with one subcommand, reads its input,
looks only at local files and exits, so its work is small and fixed, and
anything slower runs in the gate (REQ-2716). No hook reaches the network
(REQ-2727).

`meow-prose-gate check` is the one exception to both rules. After its exact
rules pass, it asks a model twice through `claude -p`, each call bounded at 45
seconds, under a hook timeout of 120 seconds, as the writing standard's
specification states. The
exception covers that judge call alone, and `meow-author check` names it by
unit and subcommand, so no other hook inherits it (ADR-2700).

No hook writes its input to a file or a log (REQ-2724). The one hook that
writes is `meow-checks revision`, which writes a count to the unit's run state
and nothing it read.

### How a hook is declared

A unit declares each hook in its `hooks/hooks.json`, and its README carries a
`## Hooks` section with one sentence per hook naming the subcommand in code
font and saying what the hook stops (REQ-2726). The hooks stay few: the table
under Boundary lists every one, and a unit that adds a hook adds its row here
in the same change.

### How a rule is layered

A rule that has to hold is held three times: a hook stops the call, a check in
the gate finds a tree that breaks it, and an instruction says why
(REQ-2710). No design is safe only because a hook blocks something, so each
hook that stops a call names, in its README sentence, the gate check that
holds the same rule and the skill that explains it (REQ-2712). A rule with no
gate check is a finding against the unit until one exists.

### A pending gate

A pending gate reaches the model through the output of `meow-flow`'s
`SessionStart` hook, `paw status --waiting`, which the platform adds to the
context before the first reply, and never through a file the model has to
read (REQ-2730).

### The revision counter

`meow-checks` keeps a revision counter per work tree in its run state, beside
the ledger of the five verbs. Its `revision` subcommand runs on `PostToolUse`
and on `PostToolUseFailure` for Bash, Edit, Write and NotebookEdit, and adds
one each time, because a tool use that failed can still have changed the tree
(REQ-2728).

### A hook whose program is missing

Where a blocking hook's launcher finds no binary for the machine, it denies
with exit 2, and its reason names the unit, the machine's target, and the
command that installs the unit again (REQ-1426). It never reports the check
as unrun and lets the call through, because a guard that lets a call through
for a missing binary lets through the call it exists to stop (ADR-2710). A
launcher with no binary can't tell which call its program would have let
through, so it denies every call its hook matches.

`meow-flow`'s `SessionStart` hook blocks nothing, so with no binary it prints
that the record wasn't checked and the install command, and the session
starts. `meow-checks revision` with no binary prints the same and exits 0,
because a `PostToolUse` hook can't stop a call that already ran.

Two cases are not a hook's program going missing, and keep their own rules:
`meow-scm` missing from a push, which the git pack's specification states
under REQ-0079, and the prose gate's judge failing to run, which the writing
standard's specification states under REQ-3748.

### The check

`meow-author check` reads every `hooks/hooks.json` under `plugins/`, and each
script a declaration runs, and fails, naming the file and the hook, on:

- a hook that prints `allow` as its decision, or an `updatedInput`;
- a hook command that is anything other than the unit's launcher with one
  subcommand;
- a hook that names a network command, such as `curl`, `wget`, `ssh`, `gh`,
  `git fetch`, `git pull` or `claude -p`, other than the prose gate's judge;
- a hook with no sentence under its unit's `## Hooks`.

A test in the crate fails a hook subcommand whose output carries `allow` or
`updatedInput`, or that opens a file for writing, because the check reads the
declaration and the program's source is Rust.

## Failure paths

| Condition                                       | What happens                                                                |
| ----------------------------------------------- | --------------------------------------------------------------------------- |
| A hook crashes, times out or exits other than 2 | The call goes through the repository's permission flow; nothing is approved |
| A blocking hook's binary is missing             | Every call it matches is denied, exit 2, naming the unit and its install    |
| `meow-flow`'s binary is missing                 | The session starts, with a line saying the record wasn't checked            |
| `meow-checks`' binary is missing                | The counter doesn't advance, and the hook says so; nothing is blocked       |
| A hook answers `allow` or rewrites its input    | `meow-author check` fails in the gate, naming the file and the hook         |
| A hook names a network command                  | `meow-author check` fails, unless it is the prose gate's judge              |
| A hook has no sentence in its README            | `meow-author check` fails, naming the unit and the hook                     |
| A hook builds a network call at run time        | The check can't see it, and review holds it                                 |
