---
id: RES-0362
artifact: research
status: approved
revised: 2026-10-13
elaborates: RES-0104
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# How each JavaScript tool is run and configured

## Summary

Each of the four package managers runs a tool the project installed: `npm
exec --`, `pnpm exec`, `yarn run` and `bun x`, and `npm exec` parses a flag
before `--` as its own. Prettier's `--check` exits 1 on an unformatted file
and writes nothing. ESLint 10 reads `eslint.config.js`, `.mjs`, `.cjs`, `.ts`,
`.mts` or `.cts`, oxlint reads `.oxlintrc.json` and three other names, and
both fail on a warning only when told to: `--max-warnings 0` for ESLint and
`--deny-warnings` for oxlint. Biome reads `biome.json` or `biome.jsonc`, and
`biome ci` checks formatting and lint without changing a file, while its
documentation states no exit status for `biome format` without `--write`.
`tsc` writes JavaScript beside each source unless `noEmit` or `outDir` says
otherwise. Vitest reads `vitest.config.*` before `vite.config.*`, Jest reads
`jest.config.*` or a `jest` key in `package.json`, and `node --test` finds its
files by name. This adds to RES-0104 the command lines and file names a pack
binds; it leaves out publishing, the monorepo orchestrators and coverage.

## The question

RES-0104 names the tools that serve each stage and says every tool runs
through the project's package manager, but not the words that do it, nor the
file each tool reads, nor which command checks without writing. A pack that
binds a stage prints those words, so each has to come from the tool's own
documentation and not from memory.

## Method

I read each tool's own documentation on 2026-10-13, as listed under Sources,
and the current version of each from the npm registry the same day. I ran
none of the tools. One question stayed open: Biome's command reference and
its formatter page say `biome format` without `--write` "emits text
differences", and neither states its exit status, so the pack binds no
format command to it.

## Findings

### Each package manager runs a project's tool by its own words

`npm exec -- <pkg> [args...]` runs a package's executable, and npm adds "any
locally installed package executables" to `PATH`. Without `--`, npm parses a
flag such as `--package` itself, so a tool's own flags have to follow `--`.
`pnpm exec` executes "a shell command in scope of a project", with the
project's `node_modules/.bin` on `PATH`. `yarn run <name>` runs a script of
that name, and where none exists, "if one of the local workspace's
dependencies exposes a binary with a matching name, this binary will get
executed". `bun x`, and its alias `bunx`, "checks for a locally installed
package first, then falls back to auto-installing it from `npm`", and so does
`npm exec`, so a tool the project never installed is fetched rather than
reported absent.

A script declared in `package.json` runs as `<manager> run <script>` under all
four.

### Prettier checks without writing, and says so in its exit status

`prettier --check` "will output a human-friendly message and a list of
unformatted files", writes none, and exits 0 when every file is formatted, 1
when one isn't and 2 when Prettier itself failed.

### ESLint reads one family of files, and a warning passes unless told otherwise

ESLint looks for `eslint.config.js`, `eslint.config.mjs`, `eslint.config.cjs`,
`eslint.config.ts`, `eslint.config.mts` and `eslint.config.cts`, in that order,
starting in the directory of each file it lints and moving up. RES-0104 records
that ESLint 10 no longer reads `.eslintrc.*`, and that `--max-warnings 0` is
what makes a warning a finding.

### oxlint fails on a warning only under `--deny-warnings`

oxlint's `--deny-warnings` makes it "Ensure warnings produce a non-zero exit
code". Without a configuration file named on the command line, oxlint looks in
the working directory for `.oxlintrc.json`, then `.oxlintrc.jsonc`,
`oxlint.config.ts` and `oxlint.config.mts`.

### Biome checks formatting and lint together in `biome ci`

Biome reads `biome.json` or `biome.jsonc`. `biome ci` "Runs formatting checks,
linting checks, and assist actions in CI without modifying files", and
`--error-on-warnings` "Exits with an error status if any warning diagnostics
are emitted". `biome format` "Formats the specified files", applies the
changes only under `--write`, and its documentation states no exit status for
a run without `--write`.

### `tsc` writes its output into the tree unless told not to

Where `outDir` is unset, "`.js` files will be emitted in the same directory as
the `.ts` files they were generated from". `noEmit`, as an option in
`tsconfig.json` or as `--noEmit`, means the compiler does "not emit compiler
output files like JavaScript source code, source-maps or declarations", which
leaves it a type checker.

### Each test runner has its own configuration files

`vitest run` performs "a single run without watch mode". Vitest reads
`vitest.config.{ts,mts,cts,js,mjs,cjs}` first and `vite.config.*` second, and
runs with no configuration file where neither exists. Jest discovers
`jest.config.js|ts|mjs|mts|cjs|cts|json`, or takes its configuration from the
`jest` key in `package.json`. `node --test` with no arguments runs every file
matching patterns such as `**/*.test.{cjs,mjs,js}` and `**/test/**/*.{cjs,mjs,js}`,
and the TypeScript forms of the same patterns unless `--no-strip-types` is
given, so it needs no configuration file.

### The versions current on 2026-10-13

The npm registry gives TypeScript 7.0.2, ESLint 10.12.0, Prettier 3.9.10,
Biome 2.5.15, oxlint 1.88.0, Vitest 5.0.4, Jest 30.5.2, pnpm 12.11.2, npm
12.2.0 and yarn 1.22.22, the last being the classic line the `yarn` package
still publishes.

## Conclusions

1. A tool runs through the declared manager as `npm exec -- <tool>`, `pnpm
exec <tool>`, `yarn run <tool>` or `bun x <tool>`, and a script as
   `<manager> run <script>`, because those are the words each manager
   documents for running what the project installed.
2. A report states that `npm exec` and `bun x` fetch a tool the project never
   installed, because the run then uses a version nobody pinned.
3. `format` binds Prettier as `prettier --check .`, which writes nothing and
   fails on an unformatted file.
4. `format` binds nothing to Biome alone, because its documentation states no
   exit status for `biome format` without `--write`; `biome ci` in `lint`
   checks the formatting instead.
5. ESLint counts as configured by an `eslint.config.*` file of the six names,
   and its stage passes `--max-warnings 0`.
6. oxlint counts as configured by one of its four file names, and its stage
   passes `--deny-warnings`.
7. Biome counts as configured by `biome.json` or `biome.jsonc`, and its stage
   is `biome ci --error-on-warnings .`.
8. `check` runs `tsc --noEmit`, because without it the compiler writes a
   JavaScript file beside every source.
9. Vitest counts as configured by a `vitest.config.*` file or a `vitest`
   dependency, Jest by a `jest.config.*` file, a `jest` key or a `jest`
   dependency, and `node --test` by a `test` script that runs it.
10. A pack's page names the versions above as the ones it is current as of.

## Sources

- [npm exec](https://docs.npmjs.com/cli/v11/commands/npm-exec), read
  2026-10-13 - the synopsis with `--`, npm parsing flags before it, local
  executables on `PATH`, and fetching a package not installed.
- [pnpm exec](https://pnpm.io/cli/exec), read 2026-10-13 - running a command
  in the project's scope with its `node_modules/.bin` on `PATH`.
- [yarn run](https://yarnpkg.com/cli/run), read 2026-10-13 - a script, or a
  dependency's binary of the same name.
- [bunx](https://bun.com/docs/pm/bunx), read 2026-10-13 - a local package
  first, then an install from npm.
- [Prettier CLI](https://prettier.io/docs/cli), read 2026-10-13 - `--check`
  and its exit statuses.
- [ESLint configuration files](https://eslint.org/docs/latest/use/configure/configuration-files),
  read 2026-10-13 - the six file names and the upward search.
- [oxlint CLI](https://oxc.rs/docs/guide/usage/linter/cli.html), read
  2026-10-13 - `--deny-warnings` and the four default file names.
- [Biome CLI reference](https://biomejs.dev/reference/cli/) and
  [Biome formatter](https://biomejs.dev/formatter/), read 2026-10-13 - the
  configuration file names, `biome ci`, `--error-on-warnings`, and no exit
  status stated for `biome format` without `--write`.
- [TypeScript, `noEmit` and `outDir`](https://www.typescriptlang.org/tsconfig/#noEmit),
  read 2026-10-13 - output beside the sources and what `noEmit` turns off.
- [Vitest CLI](https://vitest.dev/guide/cli) and
  [Vitest configuration](https://vitest.dev/config/), read 2026-10-13 -
  `vitest run` and the configuration files in order.
- [Jest configuration](https://jestjs.io/docs/configuration), read 2026-10-13
  - the `jest.config` extensions and the `jest` key.
- [Node.js test runner](https://nodejs.org/api/test.html), read 2026-10-13 -
  the default file patterns of `node --test`.
- [The npm registry](https://registry.npmjs.org/), read 2026-10-13 - the
  latest version of each package named above.
