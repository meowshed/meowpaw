---
id: SPC-1320
artifact: spec
status: live
revised: 2026-10-13
states:
  [
    REQ-0083,
    REQ-0085,
    REQ-0133,
    REQ-2338,
    REQ-2420,
    REQ-2426,
    REQ-2428,
    REQ-2432,
    REQ-2434,
    REQ-2442,
    REQ-2450,
    REQ-3048,
  ]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The TypeScript and JavaScript pack

## Scope

This covers `meow-typescript`, the language pack for TypeScript and
JavaScript. It states what `status` detects and lists, which package manager
each package runs its tools through, what `bind` prints and what `check`
finds, and what the skill and `reviewing.md` carry.

Every rule SPC-1190 states for a language pack holds here, and this document
states only what is TypeScript's and JavaScript's. It leaves the publishing
checks, the monorepo orchestrators' tasks, coverage and the browser test
runners unbound. Running a stage is SPC-1040's.

ADR-2660 orders the packs and EPC-2560 realises this one.

## Boundary

| Surface                                                  | What it is                                                            |
| -------------------------------------------------------- | --------------------------------------------------------------------- |
| `plugins/meow-typescript/bin/meow-typescript`            | The program: `status`, `bind [<directory>]` and `check [<directory>]` |
| `plugins/meow-typescript/skills/typescript/SKILL.md`     | The skill                                                             |
| `plugins/meow-typescript/skills/typescript/reviewing.md` | What a reviewer of TypeScript needs beyond the commands               |
| `plugins/meow-typescript/README.md`                      | The unit's page                                                       |
| `.meowpaw/profile.toml`, `[stages]`                      | What `check` reads                                                    |

The program is the `typescript` feature of `crates/meow`. `status`, `bind`
and `check` read the files git tracks and run git alone, as SPC-1190 states,
so none of them starts Node, a package manager or a tool it names. The pack
reads no settings table of its own, so the profile holds no `[typescript]`
table.

The pack is current as of TypeScript 7.0.2, ESLint 10.12.0, Prettier 3.9.10,
Biome 2.5.15, oxlint 1.88.0, Vitest 5.0.4, Jest 30.5.2, pnpm 12.11.2, npm
12.2.0 and yarn 1.22.22, and its README names them (REQ-0085, RES-0362).

## Behaviour

### Detection

Each `package.json` git tracks marks its directory as a package, and the pack
reports for each such directory (REQ-2338, REQ-0133, REQ-3048, RES-0104). A
tool's configuration counts for a package where it sits in the package's
directory or in a directory above it, up to the root, because ESLint,
Prettier and Biome search upwards for theirs (RES-0362).

### The package manager

Each package runs its tools through one package manager, read from what the
repository commits and never from what is installed (REQ-2426, RES-0104):

1. The `packageManager` field of the package's `package.json`, or of the
   nearest `package.json` above it that has one, names it as
   `<name>@<version>`, where the name is `npm`, `pnpm`, `yarn` or `bun`.
2. The lockfile in the package's directory, or in the nearest directory above
   it holding one, names it: `package-lock.json` npm, `pnpm-lock.yaml` pnpm,
   `yarn.lock` yarn, and `bun.lock` or `bun.lockb` bun.

The field decides where it names a manager one of the lockfiles locks, or
where no lockfile exists, and a lone lockfile decides where the field is
absent. Every other case leaves the manager unresolved, and `bind` then prints
every stage unresolved with the reason:

| Case                                 | Reason                                                                     |
| ------------------------------------ | -------------------------------------------------------------------------- |
| Neither a field nor a lockfile       | `no package manager declared: commit a lockfile or set packageManager`     |
| The field names another tool         | `packageManager names <name>, which this pack doesn't know`                |
| The field and the lockfiles disagree | `<file> declares <name>, and <lockfile> locks <name>`                      |
| Two or more lockfiles and no field   | `<lockfile> and <lockfile> both lock this package; declare packageManager` |

A tool runs through the manager as `npm exec -- <tool>`, `pnpm exec <tool>`,
`yarn run <tool>` or `bun x <tool>`, and a script as `<manager> run <script>`
(RES-0362).

### What `status` reports

Its first line is `meow-typescript status`, followed by the profile's state as
SPC-1080 states. Then, for each package, in the order of its directory:

1. `scope: <directory>`, or `scope: <part> <directory>` where a declared part
   holds it (REQ-3048).
2. `marker: <path>`, naming its `package.json`.
3. `package manager: <name>, declared by <file>`, or `package manager:
unresolved, <reason>`.
4. `pinned: <name> <version> in <file>` for the version the `packageManager`
   field pins, and for a `.nvmrc` or `.node-version` in the package's
   directory, which pins Node.
5. `configured: <file>: <tool>` for each configuration it recognises:
   Prettier, Biome, oxlint, ESLint, an `.eslintrc*` named as read by ESLint 9
   alone, `tsconfig.json`, Vitest, Jest, `turbo.json` and `nx.json`.

`status` compares no pinned version with an installed one, because it runs no
tool; corepack runs the version the `packageManager` field pins where it is
enabled (REQ-2428, RES-0104). With no `package.json` tracked, it prints
`unresolved: not a TypeScript and JavaScript repository` and exits 3.

### What `bind` prints

`bind [<directory>]` binds the package in `<directory>`, the root where none
is given. The root's package is bound into `.meowpaw/profile.toml`, and a
declared part's package into the part's own profile, which the first line
names. Each stage takes the first row that applies, and each tool's command
runs through the package manager, except `node --test`, because `node` is the
runtime and no package (REQ-2338, REQ-2420, REQ-2426, RES-0362):

| Stage    | Printed as                                                                                 | When                                                                                         |
| -------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `format` | `prettier --check .`                                                                       | A `.prettierrc*`, a `prettier.config.*`, or a `prettier` key or dependency in `package.json` |
| `format` | `# format: unbound, <file> configures Biome, whose biome ci in lint checks the formatting` | A `biome.json` or `biome.jsonc`                                                              |
| `lint`   | `biome ci --error-on-warnings .`                                                           | A `biome.json` or `biome.jsonc`                                                              |
| `lint`   | `oxlint --deny-warnings && eslint --max-warnings 0 .`                                      | An oxlint configuration and an `eslint.config.*` file                                        |
| `lint`   | `oxlint --deny-warnings`                                                                   | A `.oxlintrc.json`, `.oxlintrc.jsonc`, `oxlint.config.ts` or `oxlint.config.mts`             |
| `lint`   | `eslint --max-warnings 0 .`                                                                | An `eslint.config.js`, `.mjs`, `.cjs`, `.ts`, `.mts` or `.cts`                               |
| `check`  | `tsc --noEmit`                                                                             | A `tsconfig.json` in the package's directory                                                 |
| `test`   | `vitest run`                                                                               | A `vitest.config.*` file or a `vitest` dependency                                            |
| `test`   | `jest`                                                                                     | A `jest.config.*` file, a `jest` key or a `jest` dependency                                  |
| `test`   | `node --test`                                                                              | A `test` script that runs `node --test`                                                      |
| `build`  | `<manager> run build`                                                                      | A `build` script in `package.json`                                                           |
| any      | `# <stage>: unbound, looked for <files>`                                                   | No row above applies                                                                         |

A dependency is a key of `dependencies` or `devDependencies`. oxlint and
ESLint both bind where both are configured, because oxlint is meant to run
beside ESLint (RES-0104); with any other two configured for one stage, the
first binds and a comment names the other, as SPC-1190 states. An `.eslintrc*`
configures nothing, and a comment under `lint` says ESLint 9 alone reads it.
Where the manager is npm or bun, a comment under the table's first line says
the manager fetches a tool the project never installed (RES-0362). Where the
root holds a `turbo.json` or an `nx.json`, a comment under `build` names it as
the orchestrator that runs a task across the workspace's packages, which the
pack doesn't bind. A `mise.toml`, `.mise.toml`, `Taskfile.yml` or
`Taskfile.yaml` at the root is named with the runner's pack. A stage the
profile already declares is left out, and `bind` exits 0 once it prints the
table.

### What `check` finds

`check [<directory>]` reads the stages of the profile that governs the package
in `<directory>`, the root where none is given, and exits 1 on any finding,
each on a line of its own:

| Finding                                                            | When                                                                                                                                                 |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `<stage> runs <tool> outside <manager>: write <prefix> <tool>`     | A stage's command runs Prettier, ESLint, oxlint, Biome, `tsc`, Vitest or Jest by its bare name (REQ-2426)                                            |
| `<stage> runs <runner>, and <file> declares <manager>`             | A stage's command runs `npm`, `npx`, `pnpm`, `yarn`, `bun` or `bunx` of another manager (REQ-2426)                                                   |
| `<lockfile> and <lockfile> both lock this package`                 | Two or more lockfiles apply to the package (REQ-2426)                                                                                                |
| `eslint reads no configuration: ESLint 10 ignores <file>`          | A stage runs ESLint, an `.eslintrc*` applies and no `eslint.config.*` does (REQ-2434, RES-0104)                                                      |
| `eslint ignores <file>: ESLint 10 reads <config> alone`            | A stage runs ESLint, and both an `.eslintrc*` and an `eslint.config.*` apply (REQ-2434)                                                              |
| `eslint exits 0 on warnings: pass --max-warnings 0`                | A stage runs ESLint with no `--max-warnings` word (REQ-2434, RES-0104)                                                                               |
| `oxlint exits 0 on warnings: pass --deny-warnings`                 | A stage runs oxlint with neither `--deny-warnings` nor `--max-warnings` (REQ-2434, RES-0362)                                                         |
| `tsc writes JavaScript into the tree: pass --noEmit`               | The `format`, `lint`, `check` or `test` stage runs `tsc` with no `--noEmit`, and the package's `tsconfig.json` sets no `noEmit` (REQ-2442, RES-0362) |
| `<stage> runs tsgo, the TypeScript 7 preview; the compiler is tsc` | A stage's command runs `tsgo` (RES-0104)                                                                                                             |

A command runs a tool where a word at the start of the command, or after
`&&`, `||`, `;` or `|`, is the tool's name. A word after a manager's `exec`,
`run` or `x`, or after `npx` or `bunx`, runs that tool through the manager. A
command that runs a tool through a runner's task isn't read. `build` stays out
of the `tsc` finding, because its output is the point of the stage. With no
finding, `check` prints `no findings; rule groups enabled: the package
manager, the linter's settings, the compiler's output` and exits 0
(REQ-2432).

### Generated files

The README's `Generated files` section names the lockfile the package manager
writes as project state to commit, and `node_modules/`, a build's output
directory, `coverage/`, `*.tsbuildinfo` and `.eslintcache` as cache to ignore
(REQ-2450).

### What the skill carries

The skill's body gives, in order: detection with the lockfile first, the rule
that every tool runs through the project's package manager, the stages bound
by detection with no linter preferred, what to read before reporting a pass,
and the prohibitions (RES-0104). It forbids running a package manager the
project doesn't declare, resolving `check` to `tsgo`, writing an `.eslintrc`
file, turning on a strictness flag unasked, and reporting provenance as a
guarantee about the code. It names the versions the pack is current as of.

`reviewing.md` carries what a reviewer of TypeScript checks that no command
reports (REQ-0083, RES-0104): the strictness flags left off and
`noUncheckedIndexedAccess`, `any` and unchecked casts, the `exports` map and
the module format, floating promises, the targeted runtime, and the coverage
provider.

## Failure paths

Each is printed as SPC-1190 states, by every command it applies to:

| State                                          | Reported as                                                       | Exit |
| ---------------------------------------------- | ----------------------------------------------------------------- | ---- |
| No tracked `package.json`                      | `unresolved: not a TypeScript and JavaScript repository`          | 3    |
| `<directory>` holds no tracked `package.json`  | `unresolved: <directory> holds no package.json; one is in <dirs>` | 3    |
| `bind`: the profile doesn't parse              | `unresolved: the profile doesn't parse: <message>`                | 3    |
| `check`: no profile, or one that doesn't parse | `unresolved: <what is wrong with the profile>`                    | 3    |
| A `package.json` that doesn't parse            | `unresolved: <file> doesn't parse as JSON: <message>`             | 3    |
| An unknown argument                            | the usage line                                                    | 2    |
