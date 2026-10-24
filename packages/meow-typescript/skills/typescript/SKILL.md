---
name: typescript
description: The stages a TypeScript or JavaScript package binds, the package manager it runs its tools through, and what a reviewer of its code checks. It MUST be loaded before binding a stage in, reporting the tools of, or reviewing code in a repository with a package.json. It MUST NOT be used to write the profile or a tool's configuration.
---

<role>
You read what a package configured through the pack's program, and you report
what it printed. The program binds each stage from the files the repository
commits and runs none of the tools it names, so its table is a proposal the
person accepts, never a result. This ecosystem has three linters and four
package managers, and the repository chose among them, so you read its choice
first and never make one.
</role>

<steps name="read the configuration">
1. Run `meow-typescript status` and show its
   output.
2. If it exits 3, report the line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report, for each `scope:` line, the package manager and the tool
   configurations it lists, and stop.
</steps>

<steps name="bind the stages">
1. Run `meow-typescript bind` for the root
   package, or `bind <directory>` for another, and show the table it prints,
   each comment included.
2. Give the table to the person to put in the profile file its first line
   names, and stop.
</steps>

<steps name="check the stages">
1. Run `meow-typescript check` and show each
   finding as it printed it.
2. Report a line starting `unresolved:` as unresolved, never as a pass, and
   stop.
</steps>

<steps name="review TypeScript">
1. Run `meow-typescript status` for the package
   manager and the configured tools.
2. Read `reviewing.md` before you review code, and hold the
   code to each point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the package manager">
- M1. Read the lockfile before you run or report any command, because it names
  the package manager, and `npm install` in a workspace locked by pnpm
  rewrites the dependency tree and leaves a second lockfile behind.
- M2. Run every tool through the declared manager (`npm exec -- <tool>`,
  `pnpm exec <tool>`, `yarn run <tool>` or `bun x <tool>`), never as a global
  binary, because the version that counts is the one the project pinned.
- M3. Where `status` reports the manager unresolved, report every stage
  unresolved with its reason and run nothing, because a command from the wrong
  manager succeeds and changes the tree.
- M4. In a monorepo, read the orchestrator the program names (`turbo` or
  `nx`) before you resolve a task, because it owns what a task means across
  packages and a binding without it covers one package.
</rules>

<rules name="the stages">
- M5. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- M6. Detect the linter and never prefer one: Biome, oxlint and ESLint may all
  be present, and oxlint is designed to run beside ESLint, so two linters
  together are a design somebody chose.
- M7. Resolve `check` to `tsc --noEmit` and never to `tsgo`, because `tsgo` is
  the name of the preview binary and the released TypeScript 7 compiler is
  `tsc`.
- M8. Write only flat ESLint configuration (`eslint.config.*`), and report a
  repository that carries `.eslintrc*` as pinned to ESLint 9, because ESLint
  10 no longer reads the old format.
- M9. Before you report a pass, read whether `--max-warnings 0` or
  `--deny-warnings` was passed, which strictness flags the `tsconfig.json`
  turns on, and whether type-aware lint rules ran, because a lint that exits 0
  on warnings and a type check without strictness each say less than the word
  pass.
- M10. Write the profile only when the person asks, because the profile is the
  repository's declaration.
- M11. Name the versions the pack is current as of, TypeScript 7.0.2, ESLint
  10.12.0, Prettier 3.9.10, Biome 2.5.15, oxlint 1.88.0, Vitest 5.0.4 and Jest
  30.5.2 (RES-0362), and where the installed tool is newer, say an observation
  may be stale, because a tool that moved on can change what its output means.
</rules>

<rules name="what must never happen">
- M12. Never run a package manager the project doesn't declare, because it
  rewrites the lockfile of the one it does.
- M13. Never turn on a strictness flag the repository didn't ask for, because
  the errors it produces block the build where a lint only complains.
- M14. Never author an `.eslintrc` file or translate one, because a
  translation that cannot be exact approximates, and Biome's own migration
  declines the rules it cannot match.
- M15. Never report provenance as a guarantee about the code, because
  `npm publish --provenance` proves where an artifact was built, and npm's own
  documentation says it does not guarantee the package has no malicious code.
- M16. Name the coverage provider in a coverage report, `v8` or `istanbul`,
  because the two measure differently and their percentages are not
  comparable.
</rules>
