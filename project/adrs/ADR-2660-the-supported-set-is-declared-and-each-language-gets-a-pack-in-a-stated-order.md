---
id: ADR-2660
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-2330,
    REQ-2332,
    REQ-2334,
    REQ-2336,
    REQ-2338,
    REQ-2340,
    REQ-2342,
    REQ-2344,
    REQ-2346,
    REQ-2348,
    REQ-2350,
    REQ-2358,
    REQ-2360,
    REQ-2364,
  ]
postpones: [REQ-2356]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2660. The supported set is declared, and each language gets a pack in a stated order

## Decision

The harness declares the languages and tools it supports on one page under
`docs/`, each with the pack that serves it and the state of that pack:
shipped, planned or postponed (REQ-2330). A claim on the page is one a
person can falsify by installing the pack on a repository of that kind.

Each language gets a pack that follows SPC-1190, detected from its marker
and binding the five verbs from what the repository commits. They ship one
at a time in this order:

1. Rust, from `Cargo.toml` (REQ-2332), first because this repository's crate
   is Rust and the pack then gates the harness's own code.
2. TypeScript and JavaScript, from `package.json` (REQ-2338).
3. Python, from `pyproject.toml` (REQ-2336).
4. Go, from `go.mod` (REQ-2334).
5. C#, from a `.sln` or `.csproj` (REQ-2340).
6. Lua, from a rockspec or `.luarc.json` (REQ-2342), and Neovim plugins,
   from a `lua/` tree with a `plugin/` directory, in the same pack because
   one is the other's host (REQ-2344).
7. Godot and GDScript, from `project.godot` (REQ-2346).
8. Starlark, from a Bazel or Buck workspace (REQ-2348).
9. Scheme, from a Scheme project file (REQ-2350).

The order runs from the repositories most likely to install the harness to
the least, which is my judgement from the six source harnesses RES-0002
describes, and each pack is its own decision's task.

The code host, GitHub, is served by `meow-github` (REQ-2358), and GitHub
Issues as the tracker by the same pack, as a mapping (REQ-2360). A worktree
manager, worktrunk, is used through `git worktree` operations under the
limits ADR-2420 sets (REQ-2364). A version control system other than git is
postponed under ADR-1340's condition, so REQ-2356 joins the eight it already
postpones.

Once this is accepted, the supported set is a page anyone can check, and the
Rust pack is the next language work. What still doesn't work: only the
Markdown pack ships today, so every language in the list reads as planned.

## Why

RES-0006 surveyed the verification toolchains for each language and found
that each has a marker file that identifies it without running anything. It
found that a catalogue implies support it doesn't have unless the set is
declared. SPC-1190 already states what every language pack keeps, so a new
pack follows it.

## Alternatives

| Option                    | Better at              | Why it lost                                                    |
| ------------------------- | ---------------------- | -------------------------------------------------------------- |
| Do nothing                | No packs to build      | Eleven requirements stay open, and support stays an impression |
| All packs in one release  | Every language at once | No pack gets used before the next is built, so mistakes repeat |
| Only the languages in use | Less work              | The requirements name ten, and the owner kept them in force    |

## What it costs

Nine packs, each a unit with a program, a skill and a page, and each needs a
fixture repository for its language in the crate's tests.

## What would reverse it

- A repository using the harness adopts a version control tool other than
  git, or the owner asks for one.

## Consequences

The supported set page lands under `docs/`. Each pack becomes a decision's
task in the order above. `paw status` lists REQ-2356 as postponed by this
record.

## How I will know it was realised

1. The page lists every language and tool in REQ-2330 with its state.
2. The Rust pack's `bind` on this repository prints a `[verbs]` table that
   matches the commands the crate's own gate runs (REQ-2332).
3. Each later pack's `bind` on a fixture of its language prints all five
   verbs, bound or unresolved with a reason.

## What this does not settle

- Each pack's bindings and findings, which its own specification states.
