---
reader: someone choosing or running meow-unattended
answers: what meow-unattended plans, what it writes and what its deny rules don't stop
kind: reference
describes: [meow-unattended@0.3.0]
---

# meow-unattended

`meow-unattended plan` reads the `[unattended]` table in your repository's
`.meowpaw/profile.toml`, prints the command that would start an unattended
Claude Code run under the posture and budget the table declares, and writes a
snapshot of the run's authority as a settings file outside the work tree. It
starts nothing: you read the plan, and you start the command yourself.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-unattended@meowpaw
```

## Declare the authority

A run's permission posture comes from this table and never from what a session
would default to:

```toml
[unattended]
permission_mode = "dontAsk"
budget_usd = 2.5
gates = ["verify", "review"]
units = ["vendor/meow-checks", "vendor/meow-flow"]
```

| Key               | Holds                                                                                                                | Where it's absent  |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------ |
| `permission_mode` | One of `manual`, `plan`, `dontAsk`, `acceptEdits` or `auto`                                                          | unresolved, exit 3 |
| `budget_usd`      | The spend ceiling, a positive number                                                                                 | unresolved, exit 3 |
| `gates`           | The gates the run may cross, each one of `research`, `requirements`, `design`, `epic`, `verify`, `review` or `merge` | unresolved, exit 3 |
| `units`           | The units the run loads, each the path of one unit's own directory from the work tree's root                         | unresolved, exit 3 |
| `merge_protected` | Whether the run may push to the profile's `[git] trunk`                                                              | `false`            |
| `amend_approved`  | Whether the run may amend an approved requirement or withdraw an approved decision                                   | `false`            |

`gates = []` declares that the run crosses no gate, and `plan` accepts it.
`merge` names a merge into a branch other than the trunk.

Each entry in `units` must be a directory, relative to the work tree's root,
that holds `.claude-plugin/plugin.json`. `plan` refuses a URL, because a unit
loads from a directory, and a folder of units that isn't a unit itself, because
the run would load its children by discovery. It also refuses a repository
whose `.claude/settings.json` or `.claude/settings.local.json` has an `env`
block, because those variables would reach the run without the table naming
them.

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-unattended plan
```

From your own shell, run the same launcher by its path in the installed unit.
`plan` prints, in order, and exits 0:

1. The resolved `[unattended]` table, with each default filled in.
2. Each unit, with the `name` and `version` its `plugin.json` holds.
3. The command that would start the run, one argument a line:
   `claude -p --bare`, one `--plugin-dir` for each unit, naming its directory's
   absolute path so the command runs from any directory, `--permission-mode`
   with the declared mode, `--permission-prompts none`,
   `--disallowed-tools AskUserQuestion`, `--output-format stream-json`,
   `--verbose`, `--max-budget-usd` with the declared budget, and `--settings`
   with the snapshot's path.
4. The snapshot's path.
5. Each deny rule the snapshot holds, one a line, and `no record to protect`
   where the profile declares no `[record]`.
6. That a requirement or decision approved after the plan isn't protected
   until you run `plan` again.
7. The four limits of the deny rules, listed below.
8. That the command needs `ANTHROPIC_API_KEY` in its environment, because a
   bare run reads no subscription login and the snapshot holds no credential.

`meow-unattended plan --purge` removes every snapshot of the work tree and
prints how many it removed.

## The snapshot

`plan` writes the snapshot as JSON to
`<state>/meowpaw/unattended/<work tree key>/<sha256>.json`, where `<sha256>` is
the hex digest of the file's content. So a later change to your profile leaves
an earlier snapshot's content and name unchanged, and whatever starts the run
can check that the file is the one planned. `<state>` is `$XDG_STATE_HOME`,
or `~/.local/state` where that isn't set, and `MEOWPAW_STATE_DIR` moves it, as
it moves the evidence ledger. With `MEOWPAW_STATE=off`, `plan` writes no file,
prints the snapshot's content and says no snapshot was kept.

The snapshot holds the resolved table, each unit's `name` and `version`
under `meowpaw.units`, and these deny rules under
`permissions.deny`, each path written as an absolute path with a leading `//`:

| Rule                                                                  | Present when                 |
| --------------------------------------------------------------------- | ---------------------------- |
| `Edit(//<work tree>/.meowpaw/**)`                                     | always                       |
| `Edit(//<work tree>/.claude/**)`                                      | always                       |
| `Edit(//<snapshot folder>/**)`                                        | always                       |
| `Bash(git push *<trunk>*)`, `Bash(git push)`, `Bash(git push *HEAD*)` | `merge_protected` is `false` |
| `Edit(//<path>)` for each requirement and decision recorded approved  | `amend_approved` is `false`  |

A deny rule passed with `--settings` holds against an allow rule from any other
settings file, so nothing your repository or your user settings allow lifts
it.

## What the deny rules don't stop

- A Bash deny rule stops only the forms it matches, so
  `git -C . push origin main` isn't denied, and neither is `git push origin` or
  `git push --force-with-lease` while the trunk is checked out.
- An `Edit` deny rule reaches the file tools and the file commands Claude Code
  recognises, and not a script that opens the file itself.
- A merge through the code host's interface isn't denied.
- A new record whose front matter supersedes or withdraws an approved one
  retires it without editing its file, so no deny rule stops it.

## What it reports instead of a plan

`plan` first prints the profile's state, `profile: absent`,
`profile: unparseable` or `profile: parsed`, and `unknown key: <path>` for
each key no unit reads, such as a mistyped `[unattended]` key. An unknown key
is no refusal.

`plan` reports every refusal it finds, each on its own line, exits 3 and
writes no snapshot:

| Line                                                                   | Means                                                           |
| ---------------------------------------------------------------------- | --------------------------------------------------------------- |
| `unresolved: no [unattended] table in .meowpaw/profile.toml`           | The repository has no profile, or its profile has no table      |
| `unresolved: the profile doesn't parse: ...`                           | The profile isn't valid TOML; the parser's message follows      |
| `unresolved: [unattended] <key> is not declared`                       | A required key is missing                                       |
| `unresolved: [unattended] permission_mode <value> is refused`          | `bypassPermissions`, or a mode outside the list                 |
| `unresolved: [unattended] budget_usd <value> is not a positive number` | The budget is zero, negative or not a number                    |
| `unresolved: [unattended] gates names <value>, which is not a gate`    | A gate outside the list                                         |
| `unresolved: [unattended] <key> <value> is not a list of strings`      | `gates` or `units` isn't a list of strings                      |
| `unresolved: [unattended] <key> <value> is not true or false`          | `merge_protected` or `amend_approved` isn't a boolean           |
| `unresolved: merge_protected is true and gates lacks merge`            | The run may push to the trunk but may not merge anywhere        |
| `unresolved: [git] trunk is not declared, so the push rules ...`       | `merge_protected` is `false` and no trunk names what to protect |
| `unresolved: unit <entry> is a URL, and a unit loads from a directory` | A `units` entry is a URL                                        |
| `unresolved: unit <entry> is not a unit's own directory`               | A `units` entry holds no `.claude-plugin/plugin.json`           |
| `unresolved: unit <entry> has a plugin.json that states no name ...`   | The unit's `plugin.json` lacks a `name` or a `version`          |
| `unresolved: <file> sets env <key>, ...`                               | A repository settings file has an `env` block, naming each key  |
| `unresolved: snapshot not written: <reason>`                           | The state directory can't be written                            |

`bypassPermissions` is refused because it skips the protection Claude Code
gives `.claude` and `.git`, where a run could write rules the next run applies.

## What it costs you

The unit ships no skill, so it keeps nothing in context on every turn, and its
budget states zero characters. The program is a native binary shipped inside
the unit, and needs git on the machine. On a machine the unit carries no binary
for, `plan` reports the repository as unresolved and exits 3. Each plan leaves
a snapshot of a few kilobytes in the state directory until `plan --purge`
removes it.

## What it needs

Claude Code 2.1.283 or later, declared in
`plugins/meow-unattended/requires.toml`, git, and `ANTHROPIC_API_KEY` in the
environment of whoever starts the printed command.
