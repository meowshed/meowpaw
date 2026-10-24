---
reader: someone choosing or running meow-typescript
answers: what meow-typescript does, what it adds to a session and how to run it
kind: reference
describes: [meow-typescript@0.1.0]
description: "Detects a TypeScript and JavaScript package from the package.json git tracks, reads the package manager it declares, prints a stages table bound from the tools it configured and run through that manager, reports a stage that runs a tool outside the manager or leaves a linter or compiler setting without effect, and carries what a reviewer of TypeScript checks that no command reports, writing no file."
---

# meow-typescript

`meow-typescript` tells you which TypeScript and JavaScript packages your
repository holds, which package manager each declares, and which tools each
configured. It prints a `[stages]` table bound from that configuration, with
every tool run through the manager, and checks the settings behind your
stages. Its skill tells Claude Code what a reviewer of TypeScript checks that
no command reports. It writes no file. `status`, `bind` and `check` read the
files git tracks and run git alone, so they start neither Node nor a tool they
name. It installs on its own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://paw.retran.me/meowpaw/marketplace.json
claude plugin install meow-typescript@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Run it

<!-- host-specific: claude -->

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-typescript status
```

From your own shell, run the same launcher by its path in the installed unit.

The program counts a repository as TypeScript or JavaScript where git tracks a
`package.json` outside `node_modules`. It reports once for each directory that
holds one, so a repository with two packages gets two reports.

`status` prints, for each package directory:

1. `scope: <directory>`, or `scope: <part> <directory>` where your profile's
   `[parts]` declares a part holding it.
2. `marker: <file>`, naming the `package.json`.
3. `package manager: <name>, declared by <file>`, or `package manager:
unresolved, <reason>`.
4. `pinned: <name> <version> in <file>` for the version the `packageManager`
   field pins, and for a `.nvmrc` or `.node-version` beside the package, which
   pins Node. `status` compares it with no installed version, because it
   starts no tool.
5. `configured: <file>: <tool>` for each configuration it recognises:
   Prettier, Biome, oxlint, ESLint, the `tsconfig.json`, Vitest, Jest, and a
   `turbo.json` or `nx.json` at the root. An `.eslintrc*` is named as read by
   ESLint 9 alone.

Every command that reads the profile first prints its state, `profile: absent`,
`profile: unparseable` or `profile: parsed`, and `unknown key: <path>` for
each key no unit reads. `bind` prints them on standard error, so what it
prints on standard output stays ready to paste. None of them changes the exit
status.

## The package manager

The program reads the manager from what you committed, and never from what is
installed. The `packageManager` field of the `package.json`, or of the nearest
one above it, names it as `npm`, `pnpm`, `yarn` or `bun`. A lockfile in the
package's directory, or in the nearest directory above it, names it too:
`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, and `bun.lock` or
`bun.lockb`. The field decides where it names a manager one of the lockfiles
locks, and a lone lockfile decides where the field is absent. In every other
case the manager is unresolved and `bind` prints every stage as unresolved
with the reason:

| Case                                 | Reason printed                                                             |
| ------------------------------------ | -------------------------------------------------------------------------- |
| Neither a field nor a lockfile       | `no package manager declared: commit a lockfile or set packageManager`     |
| The field names another tool         | `packageManager names <name>, which this pack doesn't know`                |
| The field and the lockfiles disagree | `<file> declares <name>, and <lockfile> locks <name>`                      |
| Two lockfiles and no field           | `<lockfile> and <lockfile> both lock this package; declare packageManager` |

A tool runs through the manager as `npm exec -- <tool>`, `pnpm exec <tool>`,
`yarn run <tool>` or `bun x <tool>`. `npm exec` and `bun x` fetch a tool that
no dependency of yours provides, so `bind` adds a comment saying so under the
npm and bun tables.

## Bind your stages

`meow-typescript bind [<directory>]` prints a `[stages]` table for the package
in `<directory>`, or the root, to paste into the profile file its first line
names. It never writes the profile itself:

```toml
[stages]
format = "pnpm exec prettier --check ."
lint = "pnpm exec eslint --max-warnings 0 ."
check = "pnpm exec tsc --noEmit"
test = "pnpm exec vitest run"
build = "pnpm run build"
```

Each stage takes the first binding that applies:

| Stage    | Bound to                                              | When                                                                             |
| -------- | ----------------------------------------------------- | -------------------------------------------------------------------------------- |
| `format` | `prettier --check .`                                  | A `.prettierrc*`, a `prettier.config.*`, or a `prettier` key or dependency       |
| `format` | nothing, printed as unbound                           | A `biome.json` or `biome.jsonc`, whose `biome ci` in `lint` checks formatting    |
| `lint`   | `biome ci --error-on-warnings .`                      | A `biome.json` or `biome.jsonc`                                                  |
| `lint`   | `oxlint --deny-warnings && eslint --max-warnings 0 .` | An oxlint configuration and an `eslint.config.*` file                            |
| `lint`   | `oxlint --deny-warnings`                              | A `.oxlintrc.json`, `.oxlintrc.jsonc`, `oxlint.config.ts` or `oxlint.config.mts` |
| `lint`   | `eslint --max-warnings 0 .`                           | An `eslint.config.js`, `.mjs`, `.cjs`, `.ts`, `.mts` or `.cts`                   |
| `check`  | `tsc --noEmit`                                        | A `tsconfig.json` beside the `package.json`                                      |
| `test`   | `vitest run`                                          | A `vitest.config.*` file or a `vitest` dependency                                |
| `test`   | `jest`                                                | A `jest.config.*` file, a `jest` key or a `jest` dependency                      |
| `test`   | `node --test`                                         | A `test` script that runs `node --test`                                          |
| `build`  | `<manager> run build`                                 | A `build` script in the `package.json`                                           |

The `--max-warnings 0` and `--deny-warnings` flags make a warning fail the
stage, because without them both linters exit 0 on a file full of warnings.
`--noEmit` keeps `tsc` from writing JavaScript beside your sources. The
released TypeScript 7 compiler is `tsc`, and `tsgo` names the preview binary,
so no stage uses it. `node --test` is the one command not run through the
manager, because `node` is the runtime and no package.

A stage with no binding is a comment naming what the program looked for. Where
you configured two tools for one stage, the stage binds the first in this
table and a comment under it names the other with its file. An oxlint
configuration beside an ESLint one binds both, because oxlint is designed to
run beside ESLint. An `.eslintrc*` binds nothing, and a comment says ESLint 10
no longer reads it. Where the root holds a `turbo.json` or an `nx.json`, a
comment names it as the orchestrator that runs a task across the workspace's
packages, which the pack binds none of. `bind` prints nothing for a stage your
profile already declares, names a `mise.toml` or a `Taskfile.yml` with the
runner's pack, `meow-mise` or `meow-gotask`, and exits 0 once it prints the
table.

## Check your settings

`meow-typescript check [<directory>]` reads the stages of the profile that
governs the package and reports each setting that is missing or has no effect,
one line for each finding, and exits 1 on any:

| Line                                                               | When                                                                                                                |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| `<stage> runs <tool> outside <manager>: write <prefix> <tool>`     | A stage runs Prettier, ESLint, oxlint, Biome, `tsc`, Vitest or Jest by its bare name                                |
| `<stage> runs <runner>, and <file> declares <manager>`             | A stage runs `npm`, `npx`, `pnpm`, `yarn`, `bun` or `bunx` of another manager                                       |
| `<lockfile> and <lockfile> both lock this package`                 | Two or more lockfiles apply to the package                                                                          |
| `eslint reads no configuration: ESLint 10 ignores <file>`          | A stage runs ESLint, an `.eslintrc*` applies and no `eslint.config.*` does                                          |
| `eslint ignores <file>: ESLint 10 reads <config> alone`            | A stage runs ESLint, and both an `.eslintrc*` and an `eslint.config.*` apply                                        |
| `eslint exits 0 on warnings: pass --max-warnings 0`                | A stage runs ESLint with no `--max-warnings`                                                                        |
| `oxlint exits 0 on warnings: pass --deny-warnings`                 | A stage runs oxlint with neither `--deny-warnings` nor `--max-warnings`                                             |
| `tsc writes JavaScript into the tree: pass --noEmit`               | A `format`, `lint`, `check` or `test` stage runs `tsc` with no `--noEmit`, and the `tsconfig.json` sets no `noEmit` |
| `<stage> runs tsgo, the TypeScript 7 preview; the compiler is tsc` | A stage runs `tsgo`                                                                                                 |

A word after a manager's `exec`, `run` or `x`, or after `npx` or `bunx`, runs
that tool through the manager. A command that runs a tool through a runner's
task, such as `mise run lint`, isn't read. With no finding it prints `no
findings`, followed on the same line by the groups it checked: the package
manager, the linter's settings and the compiler's output. It exits 3 where the
profile is missing or doesn't parse, or where nothing is a finding and the
package manager is unresolved.

## Generated files

Commit the lockfile your package manager writes (`package-lock.json`,
`pnpm-lock.yaml`, `yarn.lock` or `bun.lock`), because it is the resolved
dependency tree every collaborator and every CI run installs from. Ignore
`node_modules/`, a build's output directory, `coverage/`, `*.tsbuildinfo` and
`.eslintcache`, because the next run regenerates each.

## What it reports instead of a table

Every command exits 0 when it reports what it was asked, `check` exits 1 on a
finding, and every command exits 3 when it can't:

| Line                                                                     | Means                                                           |
| ------------------------------------------------------------------------ | --------------------------------------------------------------- |
| `unresolved: not a TypeScript and JavaScript repository`                 | Git tracks no `package.json` outside `node_modules`             |
| `unresolved: <directory> holds no package.json; one is in <directories>` | The directory you named has no tracked `package.json`           |
| `unresolved: <file> doesn't parse as JSON: ...`                          | A `package.json` isn't valid JSON; the parser's message follows |
| `unresolved: no profile at <path>`                                       | `check` found no profile                                        |
| `unresolved: the profile doesn't parse: ...`                             | The profile isn't valid TOML; the parser's message follows      |

## Review code

When Claude Code reviews TypeScript or JavaScript, the skill has it read the
package manager and the configured tools first, and then load `reviewing.md`,
which holds eight points no command reports: the strictness flags left off,
`any` and casts, the `exports` map and the module format, floating promises,
the targeted runtime, the coverage provider, the publishing checks and the
absence of an architecture check. The skill never runs a package manager the
project doesn't declare, never resolves `check` to `tsgo`, never writes an
`.eslintrc` file, never turns on a strictness flag unasked, and never reports
provenance as a guarantee about the code.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when code is reviewed. The program is a native binary shipped
inside the unit, and needs git on the machine. It runs no package manager and
reaches no network. On a machine the unit carries no binary for, it reports
the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-typescript --help` lists the subcommands, and `meow-typescript
<subcommand> --help` names what it determines, what you read to reach the same
answer without the tool, and the first word of each kind of line it prints. A
test holds each subcommand's output to those words.

## What it needs

<!-- host-specific: claude -->

Claude Code 2.1.280 or later, declared in
`plugins/meow-typescript/requires.toml`, and git. The pack is current as of
TypeScript 7.0.2, ESLint 10.12.0, Prettier 3.9.10, Biome 2.5.15, oxlint
1.88.0, Vitest 5.0.4, Jest 30.5.2, pnpm 12.11.2, npm 12.2.0 and yarn 1.22.22.
