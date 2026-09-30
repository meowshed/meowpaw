---
id: ADR-1580
artifact: adr
status: approved
revised: 2026-09-27
addresses:
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
postpones:
  [
    REQ-2480,
    REQ-2484,
    REQ-2486,
    REQ-2487,
    REQ-2488,
    REQ-2494,
    REQ-2498,
    REQ-2502,
    REQ-2508,
    REQ-2510,
  ]
supersedes: []
---

# 1580. A mise pack reads the tasks a repository declares, and binds a verb only to a task that can run unattended

## Decision

A new pack, `meow-mise`, ships a program with three commands and a skill that
tells the model to use them. It is the first runner pack, and it reads mise
alone; go-task, just and make each get a pack of their own later.

`meow-mise status` reports what mise resolves in this work tree, and runs
nothing a task declares:

- It detects mise statically first, by the configuration files RES-0122 lists
  and the five file task directories RES-0126 observed, and runs no mise
  command where none exists (REQ-2472).
- It reports mise's version (REQ-2496) and each configuration directory's
  trust state from `mise trust --show`, which changes nothing. It never runs
  `mise trust` and never passes `--yes` (REQ-2466).
- It lists the tasks from `mise tasks ls --json --hidden` (REQ-2460) under the
  heading "resolved in this work tree", never "declared" (REQ-2464). It says
  that listing ran mise over the configuration, and names each file whose
  templates call `exec`, since listing a trusted file evaluates them
  (REQ-2473).
- Each task carries where it came from: a file the repository commits, a file
  in the work tree git doesn't track, such as `mise.local.toml`, or a file
  outside the repository (REQ-2465). A task a committed file declares, whose
  listed source is another file, is reported as replaced by that file
  (REQ-2500).
- Each task carries what stops a verb binding to it: marked hidden (REQ-2479),
  asking for confirmation (REQ-2478), taking a required argument (REQ-2476),
  or declared outside a committed file or replaced (REQ-2465, REQ-2500).
- A task declaring `sources` and `outputs` is reported as able to skip as
  fresh, by a method mise doesn't report (REQ-2470), and bound only with
  `--force`.
- It names the pinned tools each committed configuration file declares under
  `[tools]`, and whether a committed `mise.lock` records them (REQ-2482).
- It names the files mise loads the environment from: each configuration file
  `mise config ls --json` lists, and each `_.file` and `_.source` a committed
  file names, without reading any of their values (REQ-2490).
- It reports each idiomatic version file at the repository's root, where the
  verbs run, as possibly
  inert unless `idiomatic_version_file_enable_tools` names its tool
  (REQ-2506).

Confirmation and arguments come from two places, because mise's listing
leaves `confirm` out (RES-0126). `confirm` is read from the task's own
definition in a committed file, as a TOML key or a file task's header line.
Required arguments come from `mise tasks info <name> --json`, never from
running the task (REQ-2476).

The listing is parsed defensively (REQ-2462). An array of objects each
holding a string `name` and `source` is a listing, and anything else is
unresolved of the kind `unrecognised shape`, never an empty list. A missing
optional field reads as unknown, and an unknown blocks binding, because a task
that might be hidden or might ask for a person isn't one to bind blind.

Five states that would otherwise look like "no tasks" each report as
themselves, unresolved, and every unresolved state exits 3 from all three
commands:

| State                         | Reported as                                                                                                                                                             |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No configuration file         | `not a mise repository`                                                                                                                                                 |
| mise isn't installed          | `mise not found`                                                                                                                                                        |
| The listing needs trust       | `untrusted`, with the directory and the command a person runs, never run (REQ-2467)                                                                                     |
| mise rejects a flag           | `environment: mise <version> predates <flag>` below the version SPC-1140 names as tested, a defect in the pack at or above it, and never a repository defect (REQ-2496) |
| The listing has another shape | `unrecognised shape` (REQ-2462)                                                                                                                                         |

`meow-mise bind` prints a `[verbs]` table for the repository to paste into its
profile. It binds a verb only to a task named exactly as the verb, never to a
near name and never by reading a task's body or dependencies (REQ-2474,
REQ-2492), because RES-0121 found a near name the likeliest wrong answer, and
a `tests` or `test:unit` may run something else entirely. It binds only a task whose listed source is a file the repository
commits, and which isn't hidden, asks for no confirmation and takes no
required argument. The binding runs the
task as `mise run --force <task>`, so a task that could skip as fresh always
runs, and a green result is never a skip (REQ-2468). Each verb it leaves
unbound is printed with the reason. It prints and never writes, because the
profile is the repository's declaration (ADR-1070). The pack writes no file at
all, `mise.local.toml` included (REQ-2504).

`meow-mise check` reads the profile's `[verbs]`, finds each `mise run <task>`
in a verb's command, and reports each finding `status` would give that task. A
task that can skip as fresh, run without `--force`, is a finding, because that
verb can pass without running. It exits 1 on a finding, so a repository can
put it in its own gate, and 3 on each unresolved state, which a gate treats
as not passed.

Binding through the profile satisfies REQ-1316 and REQ-2354 without teaching
`meow-verbs` a runner. The verb's command is the task, so work goes through
the task list, and `meow-verbs` stays unaware of mise, as the method layer has
to.

Ten requirements are postponed, each with its condition:

- REQ-2480, REQ-2486, REQ-2487, REQ-2488, REQ-2508 and REQ-2510 describe
  go-task's `ignore_error`, remote includes and their checksums, `requires`
  and output masking. They come with the go-task pack.
- REQ-2494 and REQ-2498 describe make's shadowing file targets and `-k`. They
  come with the make pack.
- REQ-2484 gives a manifest's scripts to the language pack that owns it, so it
  comes with the first language pack.
- REQ-2502 applies where the harness changes a tool version, and this pack
  changes none. It comes when a pack first writes one.

After this decision a repository using mise gets its verbs bound to its own
tasks, with every task that would run somebody else's code, ask for a person,
or need an argument reported instead of bound, and every task that could skip
bound with `--force`. What still doesn't work:

- `meow-verbs` runs whatever the profile says, so a hand-written `mise run`
  that can skip still passes when mise skips.
- A bound task that an uncommitted `mise.local.toml`, a parent directory or
  the user's configuration later replaces runs the replacement.
- The three other runners have no pack.
- A template evaluated during listing is named by a search for `exec`, and a
  template that runs code another way isn't.

Only `meow-mise check` catches the first two, and only when somebody runs it.

## Why

RES-0121 found that a declared task beats a detected command, that three
runners list their tasks in a machine-readable form without a stability
promise, and that every runner can resolve a task from outside the repository.
RES-0122 found mise's trust boundary, its replacing `[tasks]` merge, its file
tasks and its `usage`, `confirm` and freshness fields. RES-0126 observed that
the listing omits `confirm`, that `mise.local.toml` replaces a task
silently, that a skip exits 0 and `--force` prevents it, and that an
untrusted template fails the listing with exit status 1.

Binding through the profile keeps one place where a verb resolves, which
SPC-1040 states, and keeps runner knowledge in a pack, which the constitution
requires of the method layer.

## Alternatives

| Option                                          | Better at                                  | Why it lost                                                                                            |
| ----------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `meow-verbs` resolves a verb from mise directly | No line to paste                           | Puts a runner's name in the method layer, and a unit may not run another unit's program                |
| `bind` writes the profile                       | One step fewer                             | The profile is the repository's declaration, and a written one is a decision nobody read               |
| Parse `mise.toml` in place of listing           | No mise needed, no configuration evaluated | Misses file tasks and tasks from other files, which RES-0122 and RES-0126 show                         |
| Bind without `--force` and trust mise's cache   | A fresh task doesn't run twice             | A skip exits 0, so a verb could pass on a previous run's result                                        |
| Detect mise's skip line and report "skipped"    | Keeps the repository's caching             | `meow-verbs` runs the verb and names no runner, so it can't read the line, and the pack runs no verb   |
| One pack for all four runners                   | One unit to install                        | Each runner's trust and freshness rules differ, and a pack for a runner a repository lacks costs turns |
| Do nothing                                      | No new unit                                | A mise repository keeps writing each verb by hand, with no check on what the task can do               |

## What it costs

Every repository that installs the pack keeps its skill description in
context on every turn. The person running any of the three commands runs mise five
times, for the version, the trust state, the task listing, the configuration
listing and the idiomatic version setting, plus once per task that declares
arguments; on a trusted configuration each listing evaluates its templates,
which can run the repository's code on that person's machine. Whoever waits
on a gate, locally or in CI, pays for a fresh task running again under
`--force`, which throws away the caching the repository declared.

## What would reverse it

I would drop `--force` if mise's listing started to say which method decides
freshness and a verb's report could name a skip, because the skip would then
be visible. I would read `confirm` from the listing once mise includes it, and
drop the file read. I would move binding into `meow-verbs` if the platform
gave units a way to call each other that the standalone rule allows.

## Consequences

- A unit `meow-mise` with a program, a skill, a README, a budget and a
  marketplace entry.
- A native feature `mise` in `crates/meow`, built by `build-units`.
- A specification of the pack, SPC-1140, and the documentation index names
  the unit.
- This repository's profile keeps its hand-written verbs, and `meow-mise
check` runs over them.

## How I will know it was realised

1. Fixtures with real mise show `status` on a repository with a committed
   task, a hidden one, a confirm one, one taking a required argument, one
   with `sources` and `outputs`, a file task, a parent directory's task and a
   `mise.local.toml` replacing a committed task, each reported as this
   decision says.
2. A fixture with an untrusted template shows `untrusted` with exit status 3,
   and `mise trust --show` still reports the directory untrusted afterwards.
3. Fixtures with a stand-in mise show an unrecognised listing and an
   `unexpected argument` each reported as unresolved with exit status 3,
   never as an empty list.
4. A fixture shows `bind` binding `test` to `mise run --force test`, binding
   nothing to a near name, and leaving each blocked task unbound with its
   reason; another shows the work tree unchanged after all three commands.
5. A fixture shows `check` exiting 1 on a verb that runs a skippable task
   without `--force`, and 0 on this repository's profile.
6. Every requirement ADR-1580 addresses lands in exactly one closed task, and
   the ten it postpones read as postponed.

## What this does not settle

- Packs for go-task, just and make.
- A skip in a hand-written command that `check` never ran over, and a bound
  task replaced after `bind` or `check` last ran.
- A task declared in an environment file such as `mise.ci.toml`, which
  resolves only where `MISE_ENV` selects it, so a verb bound to it differs
  between machines.
- Templates that run code without `exec`.
