---
id: SPC-1140
artifact: spec
status: live
revised: 2026-09-27
states:
  [
    REQ-1316,
    REQ-2354,
    REQ-2460,
    REQ-2462,
    REQ-2464,
    REQ-2465,
    REQ-2466,
    REQ-2467,
    REQ-2468,
    REQ-2470,
    REQ-2472,
    REQ-2473,
    REQ-2474,
    REQ-2476,
    REQ-2478,
    REQ-2479,
    REQ-2482,
    REQ-2490,
    REQ-2492,
    REQ-2496,
    REQ-2500,
    REQ-2504,
    REQ-2506,
  ]
---

# The mise pack

## Scope

This covers `meow-mise`, the pack that reads what mise resolves in a work tree
and binds the five verbs to the tasks a repository declares. It states what
`status` reports, what `bind` prints, what `check` finds, and how each
unresolved state reads.

It leaves running a verb to SPC-1040, which `meow-checks` implements: a bound
verb is a command in the profile like any other. Packs for other runners are
not written yet.

ADR-1580 decides this part, EPC-1550 realises it, and `meow-mise` implements
it, checked at #577.

## Boundary

| Surface                                  | What it is                                                     |
| ---------------------------------------- | -------------------------------------------------------------- |
| `plugins/meow-mise/bin/meow-mise`        | The program: `status`, `bind` and `check`                      |
| `plugins/meow-mise/skills/mise/SKILL.md` | The skill that tells the model to use the program, never guess |
| `plugins/meow-mise/README.md`            | The unit's page                                                |
| `.meowpaw/profile.toml`, `[verbs]`       | What `check` reads; the pack never writes it                   |

The program writes no file, in the repository or outside it, and
`mise.local.toml` least of all, because it is the user's and isn't committed
(REQ-2504). It runs `mise` for the version, the trust state, the task listing,
the configuration listing and one setting, and `mise tasks info` for a task
that declares arguments. It never runs `mise trust`, never passes `--yes` and
never runs a task (REQ-2466).

The pack was tested on mise 2026.9.11, and that version is the line between
an environment failure and a defect in the pack.

Exit status: 0 when the command reports what it was asked; 1 when `check`
finds a finding; 3 when the work tree is in one of the unresolved states
below; 2 on a usage error.

## Behaviour

### Detection

A work tree is a mise repository when its root holds one of these, and the
program runs no `mise` command otherwise (REQ-2472):

- a configuration file: `mise.toml`, `.mise.toml`, `mise.local.toml`,
  `mise/config.toml`, `.mise/config.toml`, `.config/mise/config.toml`,
  `.config/mise.toml`, a `conf.d/*.toml` under `mise/`, `.mise/` or
  `.config/mise/`, or an environment file `mise.<name>.toml`;
- a file task directory: `mise-tasks/`, `.mise-tasks/`, `mise/tasks/`,
  `.mise/tasks/` or `.config/mise/tasks/`.

### What `status` reports

`meow-mise status` reports, in this order:

1. mise's version, from `mise --version` (REQ-2496).
2. Each configuration directory's trust state, from `mise trust --show`.
3. The tasks, from `mise tasks ls --json --hidden`, under the heading
   `resolved in this work tree`, never `declared` (REQ-2460, REQ-2464). A line
   under the heading says the listing ran mise over the configuration, and
   names each committed configuration file whose templates call `exec`,
   because listing a trusted file evaluates them (REQ-2473).
4. The pinned tools each committed configuration file declares under
   `[tools]`, as `<tool> = <version>` with the file, and whether a committed
   `mise.lock` exists (REQ-2482).
5. The files mise loads configuration and environment from: each path
   `mise config ls --json` lists, and each `_.file` and `_.source` a committed
   file declares under `[env]`. It prints paths only and never a value
   (REQ-2490).
6. Each idiomatic version file at the root, `.python-version`,
   `.node-version`, `.nvmrc`, `.ruby-version`, `.go-version`,
   `.java-version` or `.terraform-version`, as `possibly inert` unless
   `mise settings get idiomatic_version_file_enable_tools` names its tool
   (REQ-2506).

Each task carries its source and one of three origins (REQ-2465):

| Origin           | Means                                                              |
| ---------------- | ------------------------------------------------------------------ |
| `repository`     | The listed source is a file git tracks in this repository          |
| `work tree only` | The listed source is inside the work tree and git doesn't track it |
| `outside`        | The listed source is outside the work tree                         |

A task a committed file declares, whose listed source is another file, is
reported as `replaced by <source>` (REQ-2500). A committed file declares a
task through a `[tasks.<name>]` table or as a file task under one of the five
directories.

Each task carries every block that stops `bind` using it:

| Block               | When                                                                                         |
| ------------------- | -------------------------------------------------------------------------------------------- |
| `hidden`            | The listing's `hide` is true (REQ-2479)                                                      |
| `asks for a person` | Its committed definition sets `confirm`, as a TOML key or a `#MISE confirm=` line (REQ-2478) |
| `needs <args>`      | `mise tasks info <name> --json` lists a required argument, named here (REQ-2476)             |
| `not committed`     | Its origin isn't `repository`, or it is replaced (REQ-2465, REQ-2500)                        |
| `unknown <field>`   | The listing lacks a field the block needs, so the program can't tell (REQ-2462)              |

A task declaring both `sources` and `outputs` carries `can skip as fresh:
freshness decided by mise, by a method it doesn't report`, which isn't a
block: `bind` binds it with `--force` (REQ-2470). A task outside a committed file carries
`confirm unknown`, since the program reads only committed definitions.

### What `bind` prints

`meow-mise bind` prints a `[verbs]` table to paste into the profile. For each
of the five verbs, `format`, `lint`, `check`, `test` and `build`, it binds the
task whose name equals the verb, and no other: a task named `tests` or
`unit` isn't bound to `test` (REQ-2474). It never reads a task's `run` or
`depends` to choose (REQ-2492). It binds a task that carries no block, as:

```toml
[verbs]
test = "mise run --force test"
```

`--force` makes mise run a task it would skip as fresh, so a bound verb that
passes ran (REQ-2468). Every binding carries it, so a task that gains
`sources` later stays bound correctly. Each verb it doesn't bind is printed as
a comment with the reason: `# lint: no task named lint`, or `# test: task
test asks for a person`. Work then goes through the repository's own tasks,
since each bound verb's command is the task (REQ-1316, REQ-2354).

### What `check` finds

`meow-mise check` reads the profile's `[verbs]` and splits each verb's command
on `&&`, `||` and `;`. Each part that starts `mise run` names a task: the
first word after `mise run` and its flags. For each named task it reports
every block `status` would give it as a finding, and `can skip as fresh` as
a finding only where the part lacks `--force` or `-f`. A task the
listing doesn't hold is a finding, `no task named <name>`. It exits 1 on any
finding and 0 on none; a profile with no `mise run` in any verb reports
`nothing to check` and exits 0.

## Failure paths

Four states would otherwise read as "no tasks", and each is reported as
itself, unresolved, with exit status 3, by all three commands (REQ-2467,
REQ-2496):

| State                             | Reported as                                                                                                                |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| No detection marker               | `unresolved: not a mise repository`                                                                                        |
| `mise` isn't on `PATH`            | `unresolved: mise not found`                                                                                               |
| Standard error says `not trusted` | `unresolved: untrusted <directory>; a person runs mise trust <directory> after reading it`                                 |
| mise rejects a flag               | `unresolved: environment: mise <version> predates <flag>`, or `unresolved: meow-mise defect: <flag>` at or above 2026.9.11 |

A listing that isn't a JSON array of objects each holding a string `name` and
`source` is `unresolved: unrecognised shape`, with the first 200 characters
of what mise printed (REQ-2462). Any other non-zero exit from the listing is
`unresolved: mise failed`, with its exit status and the last lines of its
standard error, and never an empty list.

`check` with no profile, or a profile that doesn't parse, reports it as
unresolved with exit status 3, because a check that read nothing hasn't
passed.
