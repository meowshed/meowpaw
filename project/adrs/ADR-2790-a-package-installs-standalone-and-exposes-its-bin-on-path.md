---
id: ADR-2790
artifact: adr
status: done
revised: 2026-10-04
addresses:
  [
    REQ-4108,
    REQ-4110,
    REQ-4112,
    REQ-4130,
    REQ-4132,
    REQ-4134,
    REQ-4136,
    REQ-4138,
  ]
supersedes: []
---

# 2790. A package installs standalone and exposes its bin on PATH

## Decision

Each Pi package installs and works on its own, wherever Pi puts it, with no
checkout of the meowpaw repository beside it. Five rules hold that:

1. **A package bundles every file it loads.** The reply shape, the judge
   prompt and the router prompt ship inside the package that uses them, in
   its `prompts/` directory, and the extension resolves them from the
   package root (REQ-4130). No extension walks up past its package root.

2. **The extension puts its bin on PATH.** Each package's extension
   prepends the package's `bin/` directory to `process.env.PATH` at load
   (REQ-4132). The skills name their binary plainly — `paw check`,
   `meow-scm convention` — and name supporting files relative to the skill's
   own directory. Claude Code puts a plugin's `bin/` on PATH natively, so
   the same phrasing serves both platforms.

3. **Only the kernel injects the reply shape.** The `@meowshed/meow-core`
   extension alone pushes the reply shape into the system prompt
   guidelines (REQ-4134). A package that makes a nested model call — the
   router — carries its own bundled copy into that call's messages, because
   a nested call runs its own prompt.

4. **The install script names the one meow-full release.** Each package's
   `install-meow.mjs` downloads the meow-full release archive — the one meow
   binary built once with every unit's feature for six platforms — extracts
   the binary for the machine it runs on (unzip on POSIX, PowerShell on
   Windows), names it `meow` where the wrappers look for it, removes the
   archive, and exits 0 on any failure, leaving the wrappers to report unrun
   (REQ-4136). The script is ESM throughout. A unit's own release archive
   cannot serve a package, because each unit's binary is compiled with only
   its own feature (SPC-1080) and a package bundles several units: one
   all-features binary, built once and reused by every package and both
   harnesses, is the one download that serves them all.

5. **Downloaded binaries are never committed.** The repository ignores
   `packages/*/bin/*-*/`, so the platform directory an install fills is
   invisible to source control (REQ-4138).

The meow binary is still built once by the build workflow and reused; this
decision changes only where a package finds its files at runtime.

## Why

BUG-1400 found every shipped extension reading the monorepo's `plugins/`
directory, which holds nowhere the package installs: the reply shape, the
judge prompt and the router prompt all silently loaded as empty strings.
BUG-1401 found fourteen skills naming `${CLAUDE_SKILL_DIR}`, a variable Pi
never sets, so the very first command the method skill asks for answers
`command not found`. BUG-1402 found every package injecting the reply shape,
so two installed layers charge the same text twice on every turn.
BUG-1403 found a `require` call in an ESM script and four installers naming
another unit's release.

The common cause: the packages were built and marked done from inside the
monorepo, where every accidental path and variable happens to hold. A
package's real environment is Pi's package directory, alone, and the only
way to know it works there is to bundle, name things plainly, and install
before marking anything done.

## Alternatives

| Option                                                          | Better at                           | Why it lost                                                                                                                                 |
| --------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Bundle prompts and expose bin on PATH, kernel-only injection    | Works wherever Pi puts the package  | Chosen                                                                                                                                      |
| Keep reading the monorepo's plugins and require a checkout      | Zero duplication of prompt files    | The package then installs nowhere but beside a checkout, which is no distribution at all                                                    |
| Env-var indirection per package (`${MEOW_BIN_DIR}/paw`)         | Explicit, no PATH mutation          | A second variable to document and set, where PATH already is the platform's own mechanism and Claude Code resolves the same phrasing        |
| One shared `@meowshed/meow-core` dependency for the reply shape | No bundled copies in other packages | A nested call cannot read another package's files reliably, and version skew between packages would break the very text a nested call needs |
| Ship the meow binary in each npm tarball                        | No postinstall, no download         | Six platforms × six packages of 1.3 MB each, and a release workflow change for no gain the download doesn't already give                    |

## What it costs

Each package carries a copy of the prompt files it loads; the reply shape
sits in the kernel and in the flow package (for the router's nested call),
so a wording change must be copied while the copies are not yet generated.
The skills in the Pi packages now differ from the Claude Code plugins'
skills in their path phrasing, so the two copies drift until the plugins
adopt the same phrasing in their next versions. The PATH prepend is a
process-wide side effect of loading a package, which is the same effect a
Claude Code plugin has natively.

## What would reverse it

- Pi ships its own mechanism for exposing a package's binaries to the
  Bash tool, making the PATH prepend unnecessary.
- The plugins adopt the plain phrasing and a generator replaces the copies,
  making the bundled-prompt duplication a build step rather than a rule.
- Pi packages gain a reliable way to reference another package's files,
  making the shared-dependency option workable.

## Consequences

- A package installed alone loads its own prompts, so the reply shape and
  the judge prompt reach the model from the package itself.
- The skills' commands resolve on both platforms with one phrasing.
- Installing the kernel and any other layer injects the reply shape once.
- A failed binary download never fails an install; the wrappers report
  unrun, which is the designed behaviour.
- The four defects BUG-1400 to BUG-1403 are fixed by the task that closes
  the requirements this decision addresses.

## How I will know it was realised

1. A package installed from a copy outside any meowpaw checkout loads its
   reply shape and prompts, verified by a Pi session started with no
   `plugins/` directory anywhere on the path.
2. The method skill's step 3, `paw ready research`, runs in a Pi session
   from the plain command name.
3. Installing the kernel and the method together shows the reply shape
   once in the system prompt.
4. Two runs of an install script leave no temporary archive behind.
5. `git status` after an install in a clean clone reports nothing.

## What this does not settle

- Whether the plugins adopt the plain phrasing and the copies become
  generated rather than sed-adapted.
- npm publication; the packages install from a local path or a git source
  today, and publishing is a separate decision.
- Whether the eval suites ever run on Pi.
