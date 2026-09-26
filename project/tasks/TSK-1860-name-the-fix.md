---
id: TSK-1860
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1270
closes: [REQ-0036, REQ-0038, REQ-0040]
issue: 337
---

# An unavailable capability names what would supply it

An unavailable capability names what would supply it, as ADR-1270 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a profile declaring no `test`, when `meow-verbs status` runs, then the line names `.meowpaw/profile.toml` and `[verbs]` and says unresolved. Closed by: a fixture.
2. Given a unit with no binary for the machine, when its launcher runs, then it names the machine and the reinstall and exits as unchecked. Closed by: a fixture.

## What to do

Make `meow-verbs status` and `run` say, for an undeclared verb, to declare it under `[verbs]` in `.meowpaw/profile.toml`, and for a value that isn't one command, to write one. Make each launcher's report of a missing binary name the machine's system and processor and say to reinstall the unit. Keep every such outcome unresolved or unchecked.

## Depends on

Nothing. ADR-1270 is approved.

## Evidence

An undeclared verb now says to declare it under `[verbs]` in
`.meowpaw/profile.toml`, a value that isn't one command says to write one,
and a missing profile says to write it; each stays unresolved. Each of the four launchers, `meow-verbs`, `meow-scm`,
`meow-git` and `meow-method`, reports a missing binary with the machine's
system and processor and says to reinstall the unit, and keeps its outcome:
unresolved, unchecked, unrun or not checked, with its exit status unchanged.

A fixture in each unit copies its launcher alone into an empty directory and
runs it. All four were seen failing against the launchers before the change,
and pass after it; they test the launcher script, which the stub program
doesn't replace. The verbs fixture for an undeclared verb reads the new
detail from the JSON report.

```text
$ meow-verbs status          # in a repository with no profile
typecheck  unresolved  no profile: .meowpaw/profile.toml doesn't exist; write it, declaring each verb under [verbs]

$ meow-verbs status          # with a profile declaring only test
typecheck  unresolved  undeclared: the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml

$ sh bin/meow-verbs status   # the launcher alone, with no binary
fmt        unresolved  no interpreter: no meow binary was found for this machine, Darwin on arm64; reinstall the unit, which ships one for macOS, Linux and Windows on arm64 and x86_64
lint       unresolved  no interpreter: no meow binary was found for this machine, Darwin on arm64; reinstall the unit, which ships one for macOS, Linux and Windows on arm64 and x86_64
```

Every unit's fixtures pass: meow-verbs 13, meow-scm 15, meow-git 17 and
meow-method 113, and the crate's own tests pass.

## Left alone

A doctor that reports every unit's capabilities at once, which ADR-1270
leaves.
