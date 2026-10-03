---
id: EPC-2560
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2660
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The supported set is declared, and each language gets a pack in the stated order

Realises exactly one authorising record, ADR-2660. The epic is complete when
`docs/README.md` lists the supported set with each pack's state, and each of
the nine packs SPC-1190 orders under "The supported packs" has shipped in
that order.

## Acceptance criteria

Taken from ADR-2660's list of how it will be known realised:

1. `docs/README.md` lists every language and tool REQ-2330 asks for, each
   with its pack and its state.
2. The Rust pack's `bind` on this repository prints a `[verbs]` table that
   matches the commands the crate's own gate runs (REQ-2332).
3. Each later pack's `bind` on a fixture of its language prints all five
   verbs, bound or unresolved with a reason.
4. Every requirement ADR-2660 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-5070 list the supported set in `docs/README.md`, and document the code host, the tracker and the worktree manager
      closes: REQ-2330, REQ-2358, REQ-2360, REQ-2364
- [ ] T-002 TSK-5075 the Rust pack, `meow-rust`, detected from `Cargo.toml`
      closes: REQ-2332
      depends: TSK-5120 (blocking) - a pack meets EPC-2565's shared rules from its first release
      depends: TSK-5125 (blocking) - a pack meets EPC-2565's shared rules from its first release
      depends: TSK-5130 (blocking) - a pack meets EPC-2565's shared rules from its first release
      depends: TSK-5135 (blocking) - a pack meets EPC-2565's shared rules from its first release
      depends: TSK-5070 (not blocking) - it moves the pack's row to shipped, which either task can write
- [ ] T-003 TSK-5080 the TypeScript and JavaScript pack, detected from `package.json`
      closes: REQ-2338
      depends: TSK-5075 (blocking) - the packs ship one at a time in the order SPC-1190 states
- [ ] T-004 TSK-5085 the Python pack, detected from `pyproject.toml`
      closes: REQ-2336
      depends: TSK-5080 (blocking) - the packs ship one at a time in the order SPC-1190 states
- [ ] T-005 TSK-5090 the Go pack, detected from `go.mod`
      closes: REQ-2334
      depends: TSK-5085 (blocking) - the packs ship one at a time in the order SPC-1190 states
- [ ] T-006 TSK-5095 the C# pack, detected from a `.sln` or `.csproj` file
      closes: REQ-2340
      depends: TSK-5090 (blocking) - the packs ship one at a time in the order SPC-1190 states
- [ ] T-007 TSK-5100 the Lua and Neovim plugins pack, detected from a rockspec or `.luarc.json`
      closes: REQ-2342, REQ-2344
      depends: TSK-5095 (blocking) - the packs ship one at a time in the order SPC-1190 states
- [ ] T-008 TSK-5105 the Godot and GDScript pack, detected from `project.godot`
      closes: REQ-2346
      depends: TSK-5100 (blocking) - the packs ship one at a time in the order SPC-1190 states
- [ ] T-009 TSK-5110 the Starlark pack, detected from a Bazel or Buck workspace file
      closes: REQ-2348
      depends: TSK-5105 (blocking) - the packs ship one at a time in the order SPC-1190 states
- [ ] T-010 TSK-5115 the Scheme pack, detected from a Scheme project file
      closes: REQ-2350
      depends: TSK-5110 (blocking) - the packs ship one at a time in the order SPC-1190 states

## Coverage

Each of the fourteen requirements ADR-2660 addresses lands in exactly one
task. TSK-5070 and TSK-5075 are the smallest set that tests the decision,
because a declared set and the first pack shipped against it is the claim.
TSK-5070 runs in parallel with everything. The nine pack tasks run one after
another, in the order ADR-2660 states, and TSK-5075 waits on EPC-2565's four
tasks. The first thing the epic can measure before the packs ship is the
supported set's table, all nine rows `planned` and the Markdown pack's
`shipped`.

## Not covered

REQ-2356, a version control system other than git, which ADR-2660 postpones
under ADR-1340's condition, so no task is written for it. Each pack's
bindings and findings, which ADR-2660 leaves to each pack's own document,
written through the spec step before that pack's task is implemented.
