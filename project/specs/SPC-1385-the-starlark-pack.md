---
id: SPC-1385
artifact: spec
status: live
revised: 2026-10-20
states:
  [
    REQ-2348,
    REQ-2416,
    REQ-2420,
    REQ-2422,
    REQ-2442,
    REQ-2446,
    REQ-2450,
    REQ-3048,
  ]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Starlark pack

## Scope

This covers `meow-starlark`, the language pack for Starlark in a Bazel or Buck
workspace. It states what `status` detects, what `bind` prints and what
`check` finds. Every rule SPC-1190 states for a language pack holds here, and
this document states only what is Starlark's. It leaves `buildozer`, a pinned
Bazel version, and any Buck2 build or test unbound.

ADR-2660 decides this pack.

## Boundary

| Surface                                              | What it is                                                      |
| ---------------------------------------------------- | --------------------------------------------------------------- |
| `plugins/meow-starlark/bin/meow-starlark`            | The program: `status`, `bind` and `check`                       |
| `plugins/meow-starlark/skills/starlark/SKILL.md`     | The skill                                                       |
| `plugins/meow-starlark/skills/starlark/reviewing.md` | What a reviewer of Starlark needs beyond the program            |
| `plugins/meow-starlark/README.md`                    | The unit's page, with the toolchain versions it's current as of |

The program is the `starlark` feature of `crates/meow`. It runs git alone, as
`git ls-files` and `git check-ignore`, and starts no Bazel, Buck or buildifier
process (SPC-1190). The pack reads no table of its own in the profile.

## Behaviour

### Detection

A directory activates the pack where git tracks a `MODULE.bazel`, a
`REPO.bazel`, a `WORKSPACE` or a `WORKSPACE.bazel` in it, which marks a Bazel
workspace, or a `.buckconfig`, which marks a Buck project (REQ-2348, RES-0360).
Each report opens with the directory's scope line and names the markers
(REQ-3048).

### The build system

The pack decides which build system evaluates the directory's Starlark before
it binds a stage (REQ-2446, RES-0109). A Bazel marker makes it Bazel, and a
`.buckconfig` makes it Buck. A directory with both prints `unresolved: Bazel
and Buck are all detected, so which one evaluates the language isn't known`,
and `bind` prints each of its stages unresolved with that reason, because a
file that formats cleanly may call a function its build system doesn't have.

### What `bind` prints

Each command runs in the directory the markers activate, as `cd <directory> &&`
where that isn't the root:

| Stage    | Printed as                                                                   | When                                                                  |
| -------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `format` | `buildifier --mode=check -r .`                                               | A `.buildifier.json` in the directory                                 |
| `lint`   | `buildifier --mode=check --lint=warn -r .`                                   | A `.buildifier.json` whose `lint` key is `warn`                       |
| `check`  | `# check: unresolved, Starlark has no static types`                          | Always                                                                |
| `test`   | `bazel test --symlink_prefix=/ --build_event_json_file=<out>/bep.json //...` | The directory is a Bazel workspace                                    |
| `build`  | `bazel build --symlink_prefix=/ //...`                                       | The directory is a Bazel workspace                                    |
| `test`   | `# test: unbound, ...`                                                       | The directory is a Buck project, because `buck-out` lands in the tree |
| `build`  | `# build: unbound, ...`                                                      | The directory is a Buck project, for the same reason                  |
| any      | `# <stage>: unbound, looked for ...`                                         | No row above applies                                                  |

The pack binds buildifier where the repository committed its configuration,
and binds neither `buildozer` nor any tool the repository didn't configure
(REQ-2420, RES-0109). `lint` turns on the default warnings only where
`.buildifier.json` sets `lint` to `warn`, because the repository then asked
for them (REQ-2422).

Every buildifier command passes `--mode=check`, because its default mode
rewrites the files it checks, and none passes `--format`, because buildifier
exits 0 whenever it's given one, so a stage reading its exit status would pass
whatever it found. The evidence of those two stages is captured output: exit
4 means a file needs reformatting or a lint warning was found (REQ-2416,
RES-0366).

Every Bazel command passes `--symlink_prefix=/`, because the convenience
symlinks are the only output Bazel writes into the workspace, and `test` asks
for the build event protocol as JSON in `<out>/bep.json`, which is the
ecosystem's machine-readable report (REQ-2442, REQ-2416, RES-0360).
`<out>` is
`${XDG_STATE_HOME:-$HOME/.local/state}/meowpaw/packs/meow-starlark/<directory>`,
made with `mkdir -p` before the run. A workspace that defines no test target
makes `bazel test` exit 4, which the comment under `test` says (RES-0366).

Where several directories activate, a stage joins each directory's command with
`&&`, and a directory that leaves the stage unbound or unresolved is a comment
naming the directory. `bind` prints nothing for a stage the profile declares,
exits 3 where any directory's build system isn't known, and exits 0 otherwise.

### Generated files

`status` prints, for each directory, `commit: the workspace markers and
.buildifier.json, which are project state` and `ignore: bazel-*, which are
Bazel's convenience symlinks, and buck-out/, which is Buck's output`, because
the symlinks and `buck-out` are the only output either system writes into the
tree (REQ-2450, RES-0360).

### What `check` finds

| Finding                                                           | When                                                                       |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `<dir>: buck-out/ isn't ignored`                                  | A Buck project and `git check-ignore` finds no rule ignoring `buck-out`    |
| `<stage> runs buildifier with --format; its exit status is 0 ...` | A stage's command runs `buildifier` with `--format`                        |
| `<stage> runs buildifier without --mode=check, which rewrites`    | A stage's command runs `buildifier` and names no `--mode=check`            |
| `<stage> runs bazel without --symlink_prefix=/`                   | A stage's command runs `bazel build` or `bazel test` without it            |
| `<dir>: bazel-* symlinks aren't ignored`                          | A stage runs `bazel` without `--symlink_prefix=/` and nothing ignores them |

`check` exits 1 on any finding, and prints `no findings` with what it checked
and exits 0 when there is none (REQ-2442, REQ-2416).

## Failure paths

| State                                            | Reported as                                           | Exit |
| ------------------------------------------------ | ----------------------------------------------------- | ---- |
| No marker is tracked                             | `unresolved: not a Starlark repository`               | 3    |
| A directory holds both a Bazel and a Buck marker | `unresolved: Bazel and Buck are all detected, so ...` | 3    |
| The profile doesn't parse                        | `unresolved: the profile doesn't parse: ...`          | 3    |
| `check` finds no profile                         | `unresolved: no profile at .meowpaw/profile.toml`     | 3    |
| An unknown argument                              | the usage line                                        | 2    |

## Questions

Answer each question from what this document states, or leave `unanswered`,
because a gap left visible is one a reader can act on, and a gap left out
reads as covered.

### What the part is for

Detects Starlark in a Bazel or Buck workspace, binds its stages and checks its configuration.

### What it depends on

`meow-starlark` lists `meow-core` in its `requires.toml`.

### What depends on it

No unit lists `meow-starlark` in its `requires.toml`.

### Where its data lives

It holds none of its own: it reads the files git tracks and the profile, and SPC-1190 states that a pack's program writes no file.

### What crosses a trust boundary

unanswered

### How it fails

Stated under "Failure paths" in this document.

### How it is deployed

`meow-starlark` installs as a plugin from the marketplace, `plugins/meow-starlark/`, and ships as the Pi package `packages/meow-starlark/`.
