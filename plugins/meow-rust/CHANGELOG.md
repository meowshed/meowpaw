# meow-rust

## 0.1.0

- Detects Rust from each tracked `Cargo.toml`, and reports a directory for each.
- `bind` prints a `[stages]` table bound from the manifests, and runs `cargo test --doc` after cargo-nextest where the workspace has a library.
- `check` reports a manifest with no edition, a member that doesn't inherit the workspace's lints and a `target` no ignore file covers.
- `toolchain` compares the pinned toolchain with the installed one.
- The page states the toolchain versions the pack is current as of, and which generated files to commit and which to ignore.
