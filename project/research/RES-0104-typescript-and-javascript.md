---
id: RES-0104
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# TypeScript and JavaScript

## Summary

This ecosystem moved twice in eight months. The compiler was rewritten and its
binary renamed back to the ordinary name, and the dominant linter deleted its
old configuration format outright. Three linters are in use and two of them are
meant to coexist, so the rule is detect and never prefer. And publishing is a
discipline with its own tools, catching failures that every one of the five
verbs is blind to.

Research for one supported language, or two that share a toolchain. A toolchain
is a set of tools, and this is the largest set in the survey. Four package
managers, three linters, several test runners, and a separate class of tool
that exists only because publishing a package is its own discipline.

It covers what marks the project, what each verb resolves to, the two changes
this year that make an earlier description wrong, what the pack authors, and
what the skill has to contain.

It does not cover what every toolchain document shares, which is
[RES-0006-toolchains.md](RES-0006-toolchains.md), nor what a skill costs, which
is [RES-0005-skill-format.md](RES-0005-skill-format.md).

## The question

This ecosystem has the most tools per verb and the least agreement about which.
It also moved most in 2026: the compiler was rewritten and renamed back, and
the dominant linter deleted its old configuration format outright.

So the question is how a pack stays correct where the right answer changed
twice in eight months. The second question is how it avoids imposing one of
several live choices on a project that made a different one.

## Method

The primary sources were fetched and read on 2026-09-20: the compiler port's
staging repository, which records its own archival and the command rename, and
the linter's release announcement, which lists exactly what was removed.

The comparison of the three linters and the publishing checks came from
independent guides, and from none of the tools' own pages, and are marked as
secondary where they carry numbers.

The claim about when the compiler's programmatic interface will return is
secondary reporting and is recorded as reported; the repository itself says
only that it is not ready.

Nothing was installed or run.

## Findings

### The markers include the lockfile, and the lockfile is not optional to read

`package.json` and `tsconfig.json` mark the project. The lockfile -
`pnpm-lock.yaml`, `bun.lock`, `package-lock.json`, `yarn.lock` - names the
package manager, and `package.json` may state it outright in a `packageManager`
field, which `corepack` uses to run the right one.

Reading it is not bookkeeping. Running `npm install` in a workspace that locks
with `pnpm` rewrites the dependency tree and leaves a second lockfile behind,
and the cost falls on whoever notices. A pack reads the lockfile before it runs
anything.

A monorepo adds a second layer: `pnpm-workspace.yaml`, npm or yarn workspaces
in `package.json`, and a task orchestrator above them - `turbo` or `nx` - which
owns what "build" means across packages. Resolving a verb in a monorepo without
reading the orchestrator resolves it for one package out of forty.

### The compiler was rewritten, and the binary name went back to `tsc`

The native port is finished. Its staging repository was _"archived by the owner
on Sep 1, 2026"_, recording that _"This was the staging repo for the TypeScript
7.0 release during the native port process, which is now completed!"_

The naming matters more than the speed. During the preview the package was
`@typescript/native-preview` and the binary `tsgo`. The repository now states
that _"For TypeScript 7.0 RC and later, the command name is `tsc`."_ A pack
resolving `typecheck` to `tsgo` names a preview binary the released compiler
does not install.

The programmatic API is the live limitation. The repository lists its status as
_"not ready"_: _"either haven't even started yet, or far enough from ready that
you shouldn't bother messing with it yet."_ Every tool that reads the type
graph depends on it, where the compiler would otherwise run: typescript-eslint,
the template checkers for the component frameworks, and the refactoring tools
built on `ts-morph`. Secondary reporting puts the API in a 7.1 release some
months out, which is recorded as reported.

The consequence a pack has to represent: `typecheck` may run on the new
compiler while type-aware linting still needs the old one, and a project may
reasonably have both installed.

### ESLint deleted its old configuration format outright

ESLint v10.0.0 was released on 6 February 2026, and _"the eslintrc config
system has been completely removed in ESLint v10.0.0."_ The removal is
thorough. `.eslintrc.*` and `.eslintignore` are no longer read, and
`ESLINT_USE_FLAT_CONFIG` is not recognised. `--no-eslintrc`, `--env` and
`--rulesdir` are gone, and an `/* eslint-env */` comment is now an error.

For a pack this is the cleanest possible signal. One configuration format
remains to author, `eslint.config.js`, and a repository still carrying
`.eslintrc.json` is pinned to ESLint 9 whether or not anyone wrote that down.

### The toolchain, tool by tool

| Role               | Tool                                | What only it answers                                      |
| ------------------ | ----------------------------------- | --------------------------------------------------------- |
| Package manager    | `npm`, `pnpm`, `yarn`, `bun`        | What is installed, and how the tree is laid out           |
| Manager selection  | `corepack`, `packageManager`        | Which of the four this repository means                   |
| Compile, typecheck | `tsc`                               | Whether the types are consistent                          |
| Lint               | `eslint` with `typescript-eslint`   | Type-aware rules, custom rules, the plugin ecosystem      |
| Lint               | `biome`                             | Linting and formatting in one tool, one configuration     |
| Lint               | `oxlint`                            | The fast pre-check, designed to run beside another linter |
| Format             | `prettier`                          | The long-standing canonical form                          |
| Test               | `vitest`, `jest`, `node --test`     | The unit tests                                            |
| Test, browser      | `playwright`                        | What happens in a real browser                            |
| Coverage           | `v8`, `istanbul` providers          | Which lines ran, by two different mechanisms              |
| Dead weight        | `knip`                              | Unused files, exports, dependencies and types             |
| Structure          | `dependency-cruiser`                | Whether an import crossed a boundary the project forbids  |
| Cycles             | `madge`                             | Import cycles                                             |
| Package shape      | `publint`                           | Whether the published package's metadata is correct       |
| Consumer types     | `arethetypeswrong`                  | Whether a consumer's TypeScript resolves the types        |
| Release            | `changesets`, `semantic-release`    | Versioning and notes from the change record               |
| Provenance         | `npm publish --provenance`          | Where and how the artifact was built                      |
| Bundle             | `vite`, `esbuild`, `rollup`, `tsup` | What ships                                                |
| Size               | `size-limit`                        | Whether the bundle grew                                   |
| Monorepo           | `turbo`, `nx`                       | What a task means across packages                         |

### Three linters, and two of them are meant to coexist

Oxlint is the fastest and is designed as a pre-check alongside ESLint, and
replaces none of it; its April 2026 release ships roughly 700 built-in rules.
Biome is the one-tool answer covering formatting and linting together, with
roughly 470 rules. ESLint keeps the plugin ecosystem, custom rules and the
mature type-aware coverage.

Biome's migration command imports ESLint configuration with two stated limits.
It migrates no YAML configuration, and it separates rules it considers
equivalent to an ESLint rule from rules it considers merely inspired by one,
migrating only the first automatically.

That distinction is the finding a pack copies. A migration that silently
carried the inspired rules would change what the project checks while claiming
to preserve it, and the tool declining is the behaviour a pack imitates,
papering over nothing.

The practical rule is unchanged by any benchmark: detect, never prefer. All
three may be present, and in the oxlint case two of them are meant to be.

### Publishing is a discipline with its own tools, and no verb covers it

This is the class of tool the other languages do not have in this form. A
package can compile, lint, test and build, and still be broken for everyone who
installs it, because what breaks is the metadata, and never the code.

`publint` checks the published package's shape - the `exports` map, the files
actually included, the module format declarations. `arethetypeswrong` checks
the orthogonal question: whether a consumer's TypeScript, under each module
resolution mode, finds the types the package thinks it is publishing. `knip`
checks whether the package carries dead weight before it is published.

The recommended order is stated plainly by the comparison: start with publint
for exports correctness, then add arethetypeswrong for consumer type safety,
then knip for cleanup.

These findings are invisible to every one of the five verbs, and the failure
they catch is reported by users after a release, where no check catches it
before one.

### Provenance proves where an artifact was built

`npm publish --provenance` generates attestations signed through Sigstore's
public servers and logged to a public transparency ledger, linking the package
to its source and build instructions. It is supported on GitHub Actions with
`id-token: write` and on GitLab with `SIGSTORE_ID_TOKEN`, and on no other
provider.

The documentation states the limit directly: provenance _"does not guarantee
the package has no malicious code."_ It offers a verifiable link so a consumer
can decide, and assures them of nothing.

That sentence is the one a pack must carry, because provenance is exactly the
kind of feature a report will overstate. A green provenance badge says the
artifact came from the stated source; it says nothing about the source.

### Dead weight and structure are checkable here and rarely checked

`knip` finds unused files, unused exports, unused dependencies and unused
types, starting from entry points it derives from the frameworks in use. It
ships over 150 plugins, so it understands a repository that has configured it
for nothing.

`dependency-cruiser` is the structural tool: it validates rules about which
module may import which, which is the JavaScript answer to the architecture
question and has no equivalent among the five verbs. `madge` finds import
cycles.

The pattern across languages is holding: the structural check exists, is cheap,
and almost nobody has it configured.

### The verbs

| Verb        | Command                                                 |
| ----------- | ------------------------------------------------------- |
| `fmt`       | `biome format --write`, else `prettier --write`         |
| `lint`      | `biome check`, `oxlint`, else `eslint --max-warnings 0` |
| `typecheck` | `tsc --noEmit`                                          |
| `test`      | `vitest run`, else `jest`, else `node --test`           |
| `build`     | the project's declared `build` script                   |

`--max-warnings 0` is what makes a warning a finding; without it the verb exits
zero on a file full of them.

`build` is the one verb that is not a tool. A JavaScript project's build is
whatever its `package.json` says, and guessing a bundler is guessing.

Every one of these runs through the project's package manager - `pnpm exec`,
`npm exec`, `bun x` - and never a globally installed binary. The reason is the
one behind `uv run` in Python: the version that counts is the one the project
pinned.

### What the pack authors

`package.json` - scripts, the `packageManager` field, the `exports` map -
`tsconfig.json` strictness, and the linter's configuration in whichever of the
three shapes the repository uses.

`tsconfig.json` is the file a pack can change most with and the most dangerous
to change. Turning on a strictness flag in a repository that did not ask
produces hundreds of errors in code that was working, which is the same failure
as enabling `pedantic` in Rust. It is worse here, because the errors block the
build where a lint would only complain.

### What a reviewer needs that no command reports

`strict`, and the flags left off beside it. `noUncheckedIndexedAccess` is the
one that changes real code, because it turns every indexed read into something
that may be absent.

`any` and unchecked casts as the places type safety is actually lost - silent
by design, which is the point of the annotation.

Module boundaries: the `exports` map, and whether the package is ESM,
CommonJS, or claims both and is wrong about one.

Floating promises - an async call whose result nobody awaited, which fails by
not happening.

Which runtime is targeted, because the same source is correct in a browser and
wrong in Node.

Whether the coverage provider is `v8` or `istanbul`, because they measure
differently and a percentage from one is not comparable with the other.

### What the skill has to contain

In the body, in this order:

1. Detection, lockfile first. The four package managers, the `packageManager`
   field, the workspace files, and the orchestrator above them in a monorepo. 2. The invocation rule. Every tool runs through the project's package
   manager, never a global binary. 3. Verb resolution by detection, with the
   linter detected and never preferred, and two linters coexisting read as a
   design somebody chose. 4. What to read before reporting a pass. Whether
   `--max-warnings 0` was passed; which strictness flags are on; whether
   type-aware rules ran at all, which depends on the compiler version
   installed. 5. What must never happen. Running the wrong package manager.
   Resolving `typecheck` to `tsgo`. Authoring an eslintrc file. Turning on a
   strictness flag unasked. Reporting provenance as a guarantee about the code.

In supporting files: the tool inventory, the publishing checks with their
recommended order, and templates for `eslint.config.js`, `tsconfig.json` and a
`dependency-cruiser` configuration. Also the evidence recipe with a JUnit
reporter and a named coverage provider, the reviewer's knowledge, and the dated
facts with what to re-check: the compiler rename, the eslintrc removal, the
linter rule counts and the provenance providers.

## Conclusions

1. The lockfile is read before any command runs, because it names the package
   manager and using the wrong one rewrites the dependency tree. 2. Every tool
   is invoked through the project's package manager, never a globally installed
   binary, because the version that matters is the pinned one. 3. In a monorepo
   the orchestrator is read before a verb is resolved, since `turbo` or `nx`
   owns what a task means across packages and resolving without it covers one
   package. 4. `typecheck` resolves to `tsc`. The native compiler is the
   released TypeScript 7 under the ordinary name; `tsgo` names a preview binary
   and is not used. 5. The absence of a programmatic API is recorded as a
   constraint, because type-aware linting and template checking run through it,
   so a project may need two compiler versions at once and that is not a
   defect. 6. A release timing taken from secondary reporting is marked as
   reported. 7. Only flat configuration is authored, since ESLint 10 removed
   the eslintrc system on 6 February 2026 and no longer reads it. 8. A
   repository carrying eslintrc is reported as pinned to ESLint 9, which is a
   fact about the repository, and no style preference. 9. The linter is
   detected and never preferred. Three are in use, one is designed to run
   alongside another, and picking breaks the arrangement the project chose. 10.
   A migration that cannot be exact declines, and approximates nothing, which
   is what Biome's split between equivalent and inspired rules does and what a
   pack does with any translated configuration. 11. `lint` fails on warnings,
   through `--max-warnings 0` or the tool's equivalent, because a warning
   nobody fails on is a comment. 12. `build` resolves to the project's declared
   script and is never guessed. 13. A package that publishes has checks no verb
   covers, and they run in the stated order: `publint` for the exports shape,
   `arethetypeswrong` for consumer type resolution, `knip` for dead weight. 14.
   Provenance is reported as proving origin and not content, quoting that it
   does not guarantee the package has no malicious code, and its two supported
   providers are named. 15. Structural rules are named as available and usually
   absent. `dependency-cruiser` is the boundary check here and `madge` finds
   cycles, and a project without either has no mechanical architecture check. 16. The coverage provider is named in the report, because `v8` and
   `istanbul` measure differently and their percentages are not comparable. 17.
   A strictness flag is never turned on unasked, since the errors it produces
   block the build, where a lint would only complain. 18. The reviewer's
   knowledge is recorded with the pack: the strictness flags left off, `any`
   and casts, module boundaries and the `exports` map, floating promises, and
   the targeted runtime. 19. The skill body carries detection, the invocation
   rule, verb resolution by detection, what to read before reporting a pass,
   and the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [microsoft/typescript-go](https://github.com/microsoft/typescript-go) - the
  staging repository archived on 1 September 2026 with the native port
  completed; that the command name is `tsc` for TypeScript 7.0 RC and later
  where the preview used `tsgo`; and the programmatic API listed as not ready.
  - [ESLint v10.0.0
    released](https://eslint.org/blog/2026/02/eslint-v10.0.0-released/) - the
    release date of 6 February 2026; the complete removal of the eslintrc config
    system; and the specific removals of `.eslintrc.*`, `.eslintignore`,
    `ESLINT_USE_FLAT_CONFIG`, `--no-eslintrc`, `--env`, `--rulesdir` and `/*
eslint-env */`. - [Knip](https://knip.dev/) - unused files, exports,
    dependencies and types; analysis from entry points derived from the
    frameworks in use; and over 150 plugins so that a repository is understood
    without bespoke configuration. - [Generating provenance
    statements](https://docs.npmjs.com/generating-provenance-statements) -
    provenance and publish attestations signed through Sigstore and logged to a
    public transparency ledger; support limited to GitHub Actions with `id-token:
write` and GitLab with `SIGSTORE_ID_TOKEN`; and the statement that provenance
    does not guarantee the package has no malicious code. - [publint against
    arethetypeswrong against
    Knip](https://www.pkgpulse.com/guides/publint-vs-arethetypeswrong-vs-knip-2026)
  - the division of labour between package metadata shape, consumer type
    resolution and dead weight, and the recommended order of adoption. - [Biome,
    Oxlint and ESLint
    compared](https://www.pkgpulse.com/guides/biome-vs-eslint-vs-oxlint-2026) and
    [OXC against ESLint and
    Biome](https://www.pkgpulse.com/guides/oxc-vs-eslint-vs-biome-javascript-linting-2026)
  - oxlint at roughly 700 built-in rules as of its April 2026 release against
    Biome's roughly 470; oxlint positioned as a fast pre-check alongside ESLint;
    ESLint retained for plugins, custom rules and type-aware coverage; and
    Biome's migration command declining YAML configurations and migrating only
    the rules it considers equivalent, where it declines the inspired ones. -
    [TypeScript static analysis
    tools](https://www.in-com.com/blog/20-powerful-static-analysis-tools-every-typescript-team-needs/)
  - the layered inventory used for the tool table: linting, security,
    architectural tools including `dependency-cruiser`, dead-code analysis and
    compiler-level analysis. Recorded as a secondary source. - [TypeScript 7.0 RC
    moves the Go rewrite into the mainline
    compiler](https://visualstudiomagazine.com/articles/2026/06/22/typescript-7-0-rc-moves-microsofts-go-rewrite-into-the-mainline-compiler.aspx)
  - the RC on 18 June 2026 and the expectation of a programmatic API in a later
    release, recorded as secondary reporting, and never as fact.
