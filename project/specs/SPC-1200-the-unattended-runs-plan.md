---
id: SPC-1200
artifact: spec
status: live
revised: 2026-09-29
checked-at: "#626"
states: [REQ-2388, REQ-2392]
---

# The unattended run's plan

## Scope

This covers `meow-unattended`, the method-layer unit that plans an unattended
run, and its one command, `plan`. It states the `[unattended]` table `plan`
reads from the profile, the command line it prints, the snapshot it writes as
the run's authority, what it reports, and each state it refuses.

`plan` starts nothing, and nothing in the harness starts a run from the
plan. The loop runner `meow-loop`, once it is built, starts and repeats a run
from terms a person types, and doesn't read the snapshot. Starting a run from
the plan, stopping a run by any means other than the terminal's interrupt and
the runner's own endings, crossing a declared gate, the sandbox and the
removal of the run's credentials have no decision yet, so no specification
states them.

ADR-2000 decides this part and EPC-1900 realises it. TSK-3300 built `plan`,
and TSK-3310 made it load each unit by name.

## Boundary

| Surface                                                    | What it is                                                         |
| ---------------------------------------------------------- | ------------------------------------------------------------------ |
| `plugins/meow-unattended/bin/meow-unattended plan`         | Prints the plan, and writes the snapshot where state writing is on |
| `plugins/meow-unattended/bin/meow-unattended plan --purge` | Removes every snapshot of the work tree                            |
| `plugins/meow-unattended/README.md`                        | The unit's page, which states the four limits of the deny rules    |
| `plugins/meow-unattended/requires.toml`                    | The Claude Code version the unit needs, 2.1.283                    |
| `.meowpaw/profile.toml`, `[unattended]`                    | What `plan` reads; the unit never writes it                        |
| `crates/meow`, feature `unattended`                        | The unit's program, built by `build-units` as SPC-1080 states      |
| `<state>/meowpaw/unattended/<work tree key>/`              | Where the snapshots live, outside the work tree                    |

The unit ships no skill, so it keeps nothing in context on every turn, and its
budget states zero characters.

`plan` writes nothing into the work tree. Where state writing is on, it writes
one snapshot under the state directory, which it finds as the evidence ledger
does, as SPC-1040 states: `MEOWPAW_STATE_DIR` moves it, and the key is the one
the ledger records for the repository. With `MEOWPAW_STATE=off`, `plan` writes
nothing.

Exit status is 0 for a plan, 3 for an unresolved state and 2 for a usage
error.

## Behaviour

### The authority table

A repository declares what an unattended run may do in an `[unattended]`
table in `.meowpaw/profile.toml`, and the run's permission posture comes from
that table and from nothing the session would default to (REQ-2388):

| Key               | Holds                                                                                                                          | Where it's absent  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------ |
| `permission_mode` | One of `manual`, `plan`, `dontAsk`, `acceptEdits` or `auto`                                                                    | unresolved, exit 3 |
| `budget_usd`      | The spend ceiling, a positive number                                                                                           | unresolved, exit 3 |
| `gates`           | A list of the gates the run may cross, each one of `research`, `requirements`, `design`, `epic`, `verify`, `review` or `merge` | unresolved, exit 3 |
| `units`           | A list of the units the run loads, each the path of one unit's own directory                                                   | unresolved, exit 3 |
| `merge_protected` | Whether the run may push to the profile's `[git] trunk`                                                                        | `false`            |
| `amend_approved`  | Whether the run may amend an approved requirement or withdraw an approved decision                                             | `false`            |

An empty `gates` list is a declaration that the run crosses no gate, and
`plan` accepts it. `merge` names a merge into a branch other than the trunk.
Each path in `units` resolves against the work tree's root.

### The command line

`plan` prints the command that would start the run, one argument per line, in
this order:

```text
claude -p --bare
  --plugin-dir <unit directory>  once for each declared unit, absolute
  --permission-mode <declared>
  --permission-prompts none
  --disallowed-tools AskUserQuestion
  --output-format stream-json --verbose
  --max-budget-usd <declared>
  --settings <snapshot>
```

`--permission-mode` carries the declared `permission_mode` and
`--max-budget-usd` the declared `budget_usd`, so the printed command states
the posture and the budget it runs under (REQ-2388).

`--bare` and one `--plugin-dir` for each entry in `units`, in the order
declared, load the harness by name. The run loads no installed plugin, hook,
MCP server or `CLAUDE.md` by discovery, and the command names no hook or MCP
server the repository configures (REQ-2392). Each entry in `units` is a
directory holding `.claude-plugin/plugin.json`.

Each `--plugin-dir` names the unit's directory as an absolute path, resolved
against the work tree's root with every symbolic link resolved, because `plan`
runs from any directory in the work tree and a relative path would name a
directory under wherever the command runs.

### The snapshot

The snapshot is the file `--settings` names, and it holds the run's
authority. `plan` writes it as JSON to
`<state>/meowpaw/unattended/<work tree key>/<sha256>.json`, where `<sha256>` is
the hex digest of the file's content, so a later change to the profile leaves
an earlier snapshot's content and name unchanged. It holds no credential and
no `apiKeyHelper`. It holds:

- the resolved `[unattended]` table, with each default filled in;
- each unit's absolute `path`, as `--plugin-dir` names it, and its `name` and
  `version`, read from its `plugin.json`;
- the deny rules below, under `permissions.deny`.

The rule on the snapshot names the folder that holds it, because the file's
name is the hash of the content that holds the rule.

Each path in a deny rule is an absolute path written with a leading `//`,
because a path with one leading `/` resolves against the settings file's own
directory, which is the state directory and not the work tree.

| Rule                                                                   | Present when                 |
| ---------------------------------------------------------------------- | ---------------------------- |
| `Edit(//<work tree>/.meowpaw/**)`                                      | always                       |
| `Edit(//<work tree>/.claude/**)`                                       | always                       |
| `Edit(//<snapshot folder>/**)`                                         | always                       |
| `Bash(git push *<trunk>*)`, `Bash(git push)`, `Bash(git push *HEAD*)`  | `merge_protected` is `false` |
| `Edit(//<path>)` for each requirement and decision recorded `approved` | `amend_approved` is `false`  |

`<trunk>` is the profile's `[git] trunk`. `plan` finds the approved
requirements and decisions from the `[record]` the profile declares, as they
stand when `plan` runs. It reads `artifact` and `status` as `paw check` does,
without a trailing comment or quotes, and reads a file with CRLF line endings
as one with LF, so a record `paw check` holds frozen gets its rule.

With `MEOWPAW_STATE=off`, `plan` prints the snapshot's content in place of
writing it, and says no snapshot was kept; its rule on the snapshot folder
still names the folder a kept snapshot would go to. `plan` creates the folder
before it writes the rule naming it, and names it with every symbolic link
resolved, as the rules on the work tree already are, so every path in the
snapshot names a file the same way. `plan --purge` removes every
snapshot under the work tree's key and prints how many it removed.

### What `plan` prints

On success, in this order, and exit status 0:

1. the resolved `[unattended]` table;
2. each unit with its name and version;
3. the command line;
4. the snapshot's path, or that none was kept;
5. each deny rule, one a line, or `no record to protect` where the profile
   declares no `[record]` and `amend_approved` is `false`;
6. that a requirement or decision approved after this plan isn't protected
   until `plan` runs again;
7. the four limits of the deny rules;
8. that the command needs `ANTHROPIC_API_KEY` in its environment.

The four limits, which the README states as well:

- A Bash deny rule stops only the forms it matches, so `git -C . push origin
main` isn't denied, and neither is `git push origin` or
  `git push --force-with-lease` while the trunk is checked out.
- An `Edit` deny rule reaches the file tools and the file commands Claude Code
  recognises, and not a script that opens the file itself.
- A merge through the code host's interface isn't denied.
- A new record whose front matter supersedes or withdraws an approved one
  retires it without editing its file, so no deny rule stops it.

## Failure paths

Each is reported as `unresolved: <what>`, with exit status 3, and `plan`
writes no snapshot:

| State                                                                       | Reported as                                                                           |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| No profile, or no `[unattended]` table                                      | `unresolved: no [unattended] table in .meowpaw/profile.toml`                          |
| The profile isn't valid TOML                                                | `unresolved: the profile doesn't parse: <reason>`                                     |
| A required key is missing                                                   | `unresolved: [unattended] <key> is not declared`, once for each                       |
| `permission_mode` is `bypassPermissions` or any value outside the list      | `unresolved: [unattended] permission_mode <value> is refused`                         |
| `budget_usd` isn't a positive number                                        | `unresolved: [unattended] budget_usd <value> is not a positive number`                |
| A gate outside the list                                                     | `unresolved: [unattended] gates names <value>, which is not a gate`                   |
| `gates` or `units` isn't a list of strings                                  | `unresolved: [unattended] <key> <value> is not a list of strings`                     |
| `merge_protected` or `amend_approved` isn't `true` or `false`               | `unresolved: [unattended] <key> <value> is not true or false`                         |
| `merge_protected = true` without `merge` in `gates`                         | `unresolved: merge_protected is true and gates lacks merge`                           |
| `merge_protected` is `false` and the profile declares no `[git] trunk`      | `unresolved: [git] trunk is not declared, so the push rules have no trunk to protect` |
| A unit entry is a URL                                                       | `unresolved: unit <entry> is a URL, and a unit loads from a directory`                |
| A unit entry holds no `.claude-plugin/plugin.json`                          | `unresolved: unit <entry> is not a unit's own directory`                              |
| A unit's `plugin.json` doesn't state a `name` and a `version` as strings    | `unresolved: unit <entry> has a plugin.json that states no name and version`          |
| `.claude/settings.json` or `.claude/settings.local.json` has an `env` block | `unresolved: <file> sets env <key>, ...`, naming each key on one line                 |
| The state directory can't be written                                        | `unresolved: snapshot not written: <reason>`                                          |

`plan --purge` with state writing off, or with no state directory, reports
`unresolved: snapshots not purged: <reason>` with exit status 3 and removes
nothing.

A folder holding several units, and not a unit itself, fails the
`plugin.json` check, so `plan` never passes a folder whose children would load
by discovery. `plan` reports every refusal it finds before it exits, so one
run names every key a repository has to fix.
