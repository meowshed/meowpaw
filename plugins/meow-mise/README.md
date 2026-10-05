---
reader: someone choosing or running meow-mise
answers: what meow-mise does, what it adds to a session and how to run it
kind: reference
describes: [meow-mise@0.2.2]
---

# meow-mise

`meow-mise` reports the tasks mise resolves in your repository, where each one
came from and what would stop a check running it unattended, and binds your
verbs to the tasks you declare. It never trusts
a configuration, answers a prompt, runs a task or writes a file. It installs
on its own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-mise@meowpaw
```

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-mise status
```

From your own shell, run the same launcher by its path in the installed unit.

It prints mise's version and each directory's trust state, then every task
mise resolves in this work tree, which may differ from what your repository
declares. mise also reads parent directories, your own configuration and
`mise.local.toml`, so each task carries its origin: `repository` for a file
git tracks, `work tree only` for a file inside the work tree that git doesn't
track, and `outside` for a file beyond it. A task a committed file declares
and another file replaces says so.

Under a task, `blocked:` names what stops a check running it unattended:

| Block               | Means                                                   |
| ------------------- | ------------------------------------------------------- |
| `hidden`            | Its author marked it private                            |
| `asks for a person` | It sets `confirm`, as a TOML key or a `#MISE` header    |
| `needs <args>`      | It takes a required argument, read without running it   |
| `not committed`     | It comes from a file git doesn't track, or was replaced |
| `unknown <field>`   | mise's listing didn't say, so the program can't tell    |

A task declaring `sources` and `outputs` carries `can skip as fresh`: mise
exits 0 on a task it skipped, so a green result from it may be a previous
run's.

After the tasks it names what mise carries beyond them, by path and version
only, never a value a file holds:

- `tools pinned by committed files:` each tool a committed configuration file
  pins under `[tools]`, with its version and file, and whether `mise.lock` is
  committed.
- `configuration and environment loaded from:` each configuration file mise
  reads, your own among them, and each `_.file` and `_.source` a committed
  file names under `[env]`.
- `idiomatic version files:` each such file at the root, such as
  `.python-version`, as `read by mise` where the setting
  `idiomatic_version_file_enable_tools` names its tool, and as possibly inert
  where it doesn't, which is mise's default.

## Bind your verbs to your tasks

`meow-mise bind` prints a `[verbs]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself:

```toml
[verbs]
test = "mise run --force test"
# lint: task lint is blocked: hidden
```

It binds a verb only to the task of exactly its name, so a task named `tests`
or `unit` is never bound to `test`, and only a task that carries no block.
Every binding runs the task with `--force`, so a task mise would skip as fresh
runs, and a passing verb is never a skip. Each verb it leaves unbound is a
comment with the reason.

`meow-mise check` reads your profile's `[verbs]`, finds each `mise run <task>`
in a verb's command, including each part of a chain joined by `&&`, `||` or
`;`, and reports every block on that task, a task it can't find, and a task
that can skip as fresh run without `--force`. It exits 0 on no finding, 1 on a
finding and 3 when it can't read the profile or mise, so you can run it in
your own gate.

`check` reads the profile, so it prints the profile's state,
`profile: absent`, `profile: unparseable` or `profile: parsed`, and
`unknown key: <path>` for each key no unit reads, which changes no exit
status.

## What it reports instead of a list

`status` exits 0 when it reports the tasks and 3 when it can't, and no command
ever reports a state it couldn't read as an empty list:

| Line                                  | Means                                                                     |
| ------------------------------------- | ------------------------------------------------------------------------- |
| `unresolved: not a mise repository`   | No mise configuration file or task directory; mise didn't run             |
| `unresolved: mise not found`          | mise isn't on `PATH`                                                      |
| `unresolved: untrusted <directory>`   | mise needs the configuration trusted; read it, then run the command shown |
| `unresolved: environment: ...`        | Your mise is older than 2026.9.11, the version the unit was tested on     |
| `unresolved: meow-mise defect: ...`   | mise rejected a flag this unit passes; report it                          |
| `unresolved: unrecognised shape: ...` | mise printed a listing this unit can't read                               |
| `unresolved: mise failed ...`         | mise failed another way; its last lines follow                            |

Listing the tasks runs mise over your configuration, and on a trusted
configuration mise evaluates its templates, which can run code. The report
names each committed configuration file whose templates call `exec`.

## What it costs you

The skill's description stays in context on every turn, within the 380
characters the unit's budget states. The program is a native binary shipped
inside the unit, and needs mise and git on the machine. On a machine the unit
carries no binary for, it reports the repository as unresolved and exits 3.

## What it needs

Claude Code 2.1.280 or later, the version this unit was tested on, declared in
`plugins/meow-mise/requires.toml`; mise 2026.9.11 or later; and git.
