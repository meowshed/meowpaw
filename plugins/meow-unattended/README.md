---
reader: someone choosing or running meow-unattended
answers: what posture meow-unattended prints, what its deny rules stop and what they don't
kind: reference
describes: [meow-unattended@0.4.0]
---

# meow-unattended

`meow-unattended plan` reads the `[unattended]` table in your repository's
`.meowpaw/profile.toml` and prints the posture a run is held to: the table with
each default filled in, each deny rule one a line, and what the deny rules
don't stop. It writes nothing and starts nothing. The run itself lives in the
Claude Code session, started by `/meow-loop:run`, and `meow-loop`'s hooks hold
it to the posture this unit prints.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-unattended@meowpaw
```

## Declare the posture

A run's authority comes from this table and never from what a session would
default to:

```toml
[git]
trunk = "main"

[unattended]
permission_mode = "dontAsk"
gates = ["review", "merge"]
release = false
amend_approved = false
```

| Key               | Holds                                                                                           | Where it's absent  |
| ----------------- | ----------------------------------------------------------------------------------------------- | ------------------ |
| `permission_mode` | The mode the session must be in: one of `dontAsk`, `acceptEdits` or `auto`                      | unresolved, exit 3 |
| `gates`           | The gates the run may decide, each a step of the chain or `merge`; an empty list decides none   | unresolved, exit 3 |
| `release`         | The release command, run from the repository's root once after a merge, or `false` for none     | unresolved, exit 3 |
| `amend_approved`  | Whether the run may edit an approved requirement or decision in place, which the record forbids | `false`            |

The start command checks `permission_mode` against the mode the session is in
and refuses a mismatch with both modes named, because a run can't change the
session's mode and a mode it didn't declare is a posture nobody chose.
`bypassPermissions` is refused. `release = false` declares that the repository
has no release, and the run then releases nothing. `[git] trunk` has to be
declared, because the push rule needs a branch to protect.

## Print it

Run the launcher by its path in the installed unit, from the repository:

```bash
meow-unattended plan
```

It exits 0 for a resolved posture, 3 for an unresolved one and 2 for a usage
error, and it reports every refusal it finds before it exits, so one run names
every key a repository has to fix.

## What the deny rules stop

While a run is active, `meow-loop`'s guard denies:

- an Edit or a Write of `.meowpaw/**` and `.claude/**` in the work tree, so the
  run can't change its own posture or the session's settings;
- a `git push` whose text names the trunk or `HEAD`, or that names no branch,
  so the run lands work only through a pull request;
- an Edit or a Write of a requirement or a decision whose stored status is
  `approved`, where `amend_approved` is `false`, so the run changes an approved
  record only by writing a new one that amends it.

## What the deny rules don't stop

A Bash deny matches the command's text, so a push hidden in a script passes
it. A merge through the code host's interface needs no push, so no deny rule
stops it, and the checks the run makes before a merge hold it. A new record
whose front matter supersedes or withdraws an approved one retires it without
editing its file, so no deny rule stops that either.

## What it reports instead of a plan

Each refusal is a line starting `unresolved:` and the exit status is 3:

| State                                                  | Reported as                                                              |
| ------------------------------------------------------ | ------------------------------------------------------------------------ |
| No profile, or no `[unattended]` table                 | `unresolved: no [unattended] table in .meowpaw/profile.toml`             |
| The profile isn't valid TOML                           | `unresolved: the profile doesn't parse: <reason>`                        |
| A required key is missing                              | `unresolved: [unattended] <key> is not declared`, once for each          |
| `permission_mode` is `bypassPermissions` or not listed | `unresolved: [unattended] permission_mode <value> is refused`            |
| A gate outside the steps and `merge`                   | `unresolved: [unattended] gates names <value>, which is not a gate`      |
| `gates` isn't a list of strings                        | `unresolved: [unattended] gates <value> is not a list of strings`        |
| `release` is neither a string nor `false`              | `unresolved: [unattended] release <value> is not a command or false`     |
| `amend_approved` isn't `true` or `false`               | `unresolved: [unattended] amend_approved <value> is not true or false`   |
| The profile declares no `[git] trunk`                  | `unresolved: [git] trunk is not declared, so the push rule has no trunk` |

On a machine where the core unit's binary isn't found, the launcher reports
that and names `meow-core`, which ships the shared binary.

## What it costs you

The unit ships no skill, so it keeps nothing in context on every turn, and its
budget states zero characters. It runs the shared binary that `meow-core`
ships, and needs git on the machine.

## What it needs

Claude Code 2.1.283 or later, declared in
`plugins/meow-unattended/requires.toml`, git, and the `meow-core` unit.
