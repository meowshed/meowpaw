---
id: RES-0361
artifact: research
status: approved
revised: 2026-10-13
elaborates: RES-0101
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# What cargo, clippy and rustup decide for the Rust pack

## Summary

Doctests come from the library target alone, and `--all-targets` leaves them
out, so a `test` stage that runs `cargo test` runs them and one that names its
targets doesn't. Cargo writes its build output to `target/` at the
workspace's root unless a variable or a setting moves it. Clippy turns five
lint groups on by default and leaves four off, and `clippy.toml` can't change
a group's level. rustup's proxies run whatever toolchain a
`rust-toolchain.toml` or `rust-toolchain` file names, walking up from the
current directory. This adds to RES-0101 what the Rust pack needs to bind its
stages and to report what it checked.

## The question

RES-0101 records which tools serve each stage and the doctest gap in
cargo-nextest. It doesn't record which targets carry doctests, where cargo
writes its output, which clippy groups run when nothing configures them, or
how a toolchain file is found. The pack's bindings, its findings and its clean
report each turn on one of those four.

## Method

I read four vendor pages on 2026-10-13: the `cargo test` command reference,
the rust-clippy README, and rustup's page on overrides. Nothing was installed
or run.

## Findings

### Doctests come from the library target, and `--all-targets` leaves them out

The `cargo test` reference says documentation tests run by default, and that
rustdoc "extracts code samples from documentation comments of the library
target, and then executes them". `--doc` is "Test only the library's
documentation. This cannot be mixed with other target options." `--all-targets`
is "equivalent to specifying `--lib --bins --tests --benches --examples`", and
"Passing target selection flags will test only the specified targets".

So `cargo test` with no target flag runs the doctests, `cargo test
--all-targets` doesn't, and a package with no library target has no doctests
to run. A manifest can turn them off with `doctest = false` under `[lib]`.

### Cargo writes `target/` at the workspace's root

The same reference gives `--target-dir` as the "Directory for all generated
artifacts and intermediate files", set also by `CARGO_TARGET_DIR` or
`build.target-dir`, and says it "Defaults to `target` in the root of the
workspace". `--all-features` activates "all available features of all selected
packages", and `--workspace` tests "all members in the workspace".

### Clippy runs five groups by default

The rust-clippy README lists the groups and their default levels:
`correctness` at deny, `suspicious`, `style`, `complexity` and `perf` at warn,
and `pedantic`, `restriction`, `nursery` and `cargo` at allow. It says a
`clippy.toml` holds lint-specific settings and "cannot be used to allow/deny
lints". It gives `cargo clippy -- -D warnings` as the way to deny all warnings
before Cargo 1.97, and `CARGO_BUILD_WARNINGS=deny` from then on.

A group's level is therefore set by a `[lints.clippy]` table, which RES-0101
records, or by an attribute in source, and never by `clippy.toml`.

### rustup's proxies read the toolchain file nearest the directory

rustup's overrides page names the file `rust-toolchain.toml` or
`rust-toolchain`, and where one directory holds both, rustup reads
`rust-toolchain`. A closer file wins, found by walking up the directory tree.
The precedence is a `+name` argument, then `RUSTUP_TOOLCHAIN`, then a
directory override, then the toolchain file, then the default toolchain. The
`channel` is `stable`, `beta`, `nightly`, a `<major.minor>` or a
`<major.minor.patch>` version, with an optional date, or a custom toolchain's
name. The proxies, `cargo` and `rustc` among them, run the toolchain this
selects.

## Conclusions

1. A `test` stage bound to `cargo test` with no target flag runs the
   doctests, and one bound to a runner that skips them adds `cargo test
--doc` where a library target exists.
2. A crate with no library target has no doctests, so `cargo test --doc` has
   nothing to run there and isn't added.
3. Cargo's build output lands in `target/` at the workspace's root unless
   `CARGO_TARGET_DIR` or `build.target-dir` moves it, so a repository that
   doesn't ignore that directory gets it in its working tree.
4. A clean clippy run is clean against `correctness`, `suspicious`, `style`,
   `complexity` and `perf`, plus each group a `[lints.clippy]` table raises
   above allow, less each it sets to allow.
5. A pinned Rust toolchain is the `channel` of the `rust-toolchain` or
   `rust-toolchain.toml` file nearest the directory, `rust-toolchain` first,
   and `rustc --version` run there reports the toolchain rustup selected.

## Sources

- Read 2026-10-13: [cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html) -
  doctests from the library target, `--doc`, `--all-targets` and its
  equivalent target flags, target selection, `--target-dir` and its default,
  `--all-features`, `--workspace` and `doctest = false`.
- Read 2026-10-13: [rust-clippy README](https://github.com/rust-lang/rust-clippy/blob/master/README.md) -
  the lint groups with their default levels, that `clippy.toml` can't allow
  or deny lints, and `-D warnings` against `CARGO_BUILD_WARNINGS=deny`.
- Read 2026-10-13: [rustup, overrides](https://rust-lang.github.io/rustup/overrides.html) -
  the toolchain file's two names and which wins, the walk up the tree, the
  precedence and the `channel` grammar.
