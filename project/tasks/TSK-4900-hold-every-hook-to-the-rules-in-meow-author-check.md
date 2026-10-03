---
id: TSK-4900
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2520
closes: [REQ-2716, REQ-2718, REQ-2720, REQ-2722, REQ-2724, REQ-2726, REQ-2727]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold every hook to the rules in `meow-author check`

`meow-author check` reads every `hooks/hooks.json` and fails a hook that
breaks a rule SPC-1240 states under "The check", and a crate test holds the
hook subcommands' own output and writes. One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given a fixture unit whose hook script prints `"permissionDecision":
"allow"`, or one that prints an `updatedInput`, when `meow-author check`
   runs on it, then it exits 1 naming the file and the hook (REQ-2720,
   REQ-2718). Closed by: a crate test naming both requirements, seen failing
   first.
2. Given a fixture hook whose command is `curl https://example.org`, or a
   pipeline of two commands, when the check runs, then it fails naming the
   network command or the command that isn't the launcher with one
   subcommand (REQ-2727, REQ-2716). Closed by: a crate test.
3. Given a fixture hook in a unit other than `meow-prose-gate` whose command
   runs `claude -p`, when the check runs, then it fails; given this
   repository's `plugins/`, the check passes `meow-prose-gate check` with its
   judge (REQ-2727, REQ-2716). Closed by: a crate test and the gate's `lint`
   verb.
4. Given a fixture unit with a hook and no sentence naming its subcommand
   under `## Hooks` in its README, when the check runs, then it fails naming
   the unit and the hook (REQ-2726). Closed by: a crate test.
5. Given each hook subcommand the crate ships, when a crate test runs it on a
   fixture input, then its output carries no `allow` decision and no
   `updatedInput`, it opens no file for writing except `meow-checks
revision`'s counter, and an asking hook answers through
   `permissionDecision` `ask` and never reads a terminal (REQ-2718, REQ-2720,
   REQ-2722, REQ-2724). Closed by: a crate test per subcommand.

## What to do

Add the hook rules to the `author` feature of `crates/meow/`, reading each
`hooks/hooks.json` under `plugins/` and each script a declaration runs, as
SPC-1240 lists them. Declare the prose gate's exception in the check by unit
and subcommand only, so no other hook inherits it (ADR-2700). Add the
`## Hooks` sentence to each hook unit's README in the same change, enough for
the check to pass; TSK-4905 completes the sections. Document the rules on
`plugins/meow-author/README.md`.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The gate check and skill each hook names, which TSK-4905 writes, and a hook
that builds a network call at run time, which no reading of the declaration
finds.
