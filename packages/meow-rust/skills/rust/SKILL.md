---
name: rust
description: The stages a Rust repository binds, what its manifests say, and what a reviewer of Rust checks. It MUST be loaded before binding a stage in, reporting the tools of, or reviewing Rust in a repository that tracks a Cargo.toml. It MUST NOT be used to write the profile, a manifest or a tool's configuration.
---

<role>
You read what a repository's manifests call for through the pack's program,
and you report what it printed. The program binds each stage from the files the
repository commits, and its binding runs none of the tools it names, so its
table is a proposal the person accepts, never a result. The pack was observed
against Rust 1.99 and cargo 1.99, so where the installed toolchain is newer,
an observation may be stale.
</role>

<steps name="read the configuration">
1. Run `meow-rust status` and show its output.
2. If it exits 3, report the line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report each manifest's edition, the toolchain file, the clippy
   groups and whether nextest is configured, and stop.
</steps>

<steps name="bind the stages">
1. Run `meow-rust bind` and show the table it
   prints, each comment included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and stop.
</steps>

<steps name="check before reporting a pass">
1. Run `meow-rust check` and
   `meow-rust toolchain`, and show both.
2. Report each finding as the line, what is wrong and what would fix it. If
   `toolchain` exits 3, report its `unresolved:` line and say the stages ran
   under an unknown toolchain, and stop.
</steps>

<steps name="review Rust">
1. Run `meow-rust status` for the edition and the
   clippy groups.
2. Read `reviewing.md` before you review Rust, and hold
   the code to each point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the stages">
- M1. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- M2. Write the profile only when the person asks, because the profile is the
  repository's declaration.
- M3. Bind `test` to cargo-nextest only with `cargo test --doc` after it,
  because nextest runs no doctests, so a green run would leave the
  documentation examples uncompiled and say nothing.
- M4. Read the edition before you report a pass, because a manifest with no
  `edition` is compiled as 2015, and the pass is then about rules nobody
  chose.
- M5. Name the clippy groups a clean `lint` ran, because a clean run under the
  default groups is a statement about those groups and not about the code.
</rules>

<rules name="what must never happen">
- M6. Never enable clippy's `pedantic` group wholesale, because its findings
  are style preferences that a reader can't tell from defects. Promote named
  lints in `[workspace.lints.clippy]` instead.
- M7. Never write `#![deny(...)]` into source for lint policy, because Cargo
  has taken policy from `[lints]` in the manifest since 1.74.
- M8. Never report a licence or advisory finding as a lint finding, because it
  reaches a different reader and belongs in a supply-chain check the
  repository declares.
- M9. Never edit a manifest as text, because TOML has several spellings of one
  table and a textual edit can pick the wrong one.
</rules>
