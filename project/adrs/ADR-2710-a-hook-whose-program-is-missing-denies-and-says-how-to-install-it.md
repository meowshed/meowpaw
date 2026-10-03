---
id: ADR-2710
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-1426]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2710. A hook whose program is missing denies the command and says how to install it

## Decision

This amends ADR-2460 where it meets SPC-1060. ADR-2460 says a hook whose tool
is missing denies with a reason naming the tool (REQ-1426). SPC-1060 says the
`meow-git` launcher with no binary for the machine reports each check as
unrun and lets the command through. ADR-2460 is the newer record and wins:
where a blocking hook's program can't run, the hook denies the command, and
its reason names the program and the command that installs it again.

The rule covers the program each hook's launcher runs, in every unit that
ships a blocking hook: `meow-git`, `meow-github`, `meow-loop` and
`meow-prose-gate`. `meow-flow`'s `SessionStart` hook blocks nothing, so with
no binary it prints that the record wasn't checked and how to install the
binary, and the session starts. SPC-1060 and SPC-1010 are living, so both
are rewritten to say so, and ADR-2460's file stays as it was approved.

Two cases stay as they are, because neither is a hook's own program going
missing:

- `meow-scm` is another unit, which `meow-git` uses only where it is
  installed (REQ-0079). Where it isn't, the push guard reports the message
  check as unrun for every commit, as SPC-1060 states today.
- The prose gate's judge is a model call the program makes. Where it can't
  run, the gate lets the publish through with its not-checked message, as
  ADR-2390 decides for REQ-3748.

No requirement is withdrawn.

Once this is accepted, a missing binary stops the command it would have
checked, and the person reads what to install. What still doesn't work: on a
machine whose target the release doesn't build, every guarded command is
denied until the person removes the unit or builds the binary, which
SPC-1080's local build covers.

## Why

RES-0023 found that a check which skips when its tool is missing reports green
with nothing behind it, and RES-0006 found that a person reads a skipped
check as a passed one. A guard that lets a commit through because its binary
is missing lets through the commit it exists to stop, and a person who sees
only the unrun line has no reason to act on it. Naming the install command
turns the denial into one step the person can take.

## Alternatives

| Option                                 | Better at                              | Why it lost                                                                       |
| -------------------------------------- | -------------------------------------- | --------------------------------------------------------------------------------- |
| Deny, naming the program and its fix   | The guarded command never runs unheld  | Chosen                                                                            |
| Do nothing                             | No guarded command is ever blocked     | SPC-1060 and ADR-2460 stay in contradiction, and the guard skips what it holds    |
| Answer `ask` and let the person decide | The person can go on without the guard | In an unattended run nobody answers, so the call is denied anyway, without reason |
| Deny on a missing `meow-scm` as well   | One rule for every missing program     | REQ-0079 makes `meow-scm` optional, and a person may adopt `meow-git` alone       |

## What it costs

A person whose binary is missing can't run what the hooks match until they
install it or remove the unit. For `meow-git` and `meow-prose-gate` that is a
commit, a push or a publish. `meow-github`'s hook matches every Bash command
and `meow-loop`'s every Bash, Edit and Write, because a launcher with no
binary can't tell which call its program would have let through, so with
either unit installed and its binary missing the session can't run a shell
command or edit a file. Each blocking unit's launcher carries the install
command, and its fixtures change from "lets the command through" to
"denies".

## What would reverse it

- The platform skips a plugin whose binary is missing and says so itself,
  which would make the hook's own denial a second report of one fact.

## Consequences

SPC-1060's section on the program and its failure path, and SPC-1010's line
on a missing binary, state the denial. Each blocking unit's launcher denies
with exit 2 and the install command. Each unit's fixture with no binary
asserts the denial.

## How I will know it was realised

1. With no binary beside it, `meow-git`'s launcher denies a `git commit` with
   exit 2 and a reason naming `meow-git` and its install command (REQ-1426).
2. The same holds for `meow-prose-gate`, `meow-github` and `meow-loop`
   (REQ-1426).
3. With no `meow-scm`, a push is still let through with the message check
   reported unrun (REQ-0079).

## What this does not settle

- Which targets the release builds, which SPC-1080 states.
- What a verb reports when its tool is missing, which SPC-1040 states as an
  unresolved verb and this decision leaves as it is.
