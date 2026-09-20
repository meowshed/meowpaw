---
id: RES-0101
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# Rust

## Summary

Rust's toolchain is the one where the compiler already does most of what the
verbs ask for elsewhere, which makes the mapping easy and hides where it is
wrong. Lint policy belongs in the manifest and never in source, a manifest with
no edition compiles as the oldest one, and supply-chain checking asks four
questions. The finding that matters most: the faster test runner does not run
doctests, so a `test` verb resolved to it alone stops checking a whole category
and reports success.

Research for one supported language. A toolchain is a set of tools. This covers
which tools make up Rust's, what each one answers that the others cannot, and
what the five verbs resolve to. It also covers what the pack authors, what a
reviewer needs beyond the commands, and what the skill has to contain.

It does not cover what every toolchain document shares, which is
[RES-0006-toolchains.md](RES-0006-toolchains.md), nor what a skill costs, which
is [RES-0005-skill-format.md](RES-0005-skill-format.md).

## The question

Rust is the language where the compiler already does most of what the verbs ask
for elsewhere, which makes the five-verb mapping easy and misleading. The
interesting questions are what the compiler does not cover, which of the dozens
of cargo extensions are load-bearing, and where a plausible resolution silently
stops checking something.

## Method

We fetched and read the vendor documentation on 2026-09-20. The manifest
reference gave the lint table and the edition defaults, and the request for
comment gave the move of lint policy into the manifest. The test runner's own
documentation is where the doctest gap is stated.

The tool inventory came from a published index of Rust tooling, read for what
each tool answers, and we took none of its recommendations. One search found
current practice on the pedantic lint group.

Nothing was installed or run. We quote the doctest gap from the runner's
documentation and reproduced none of it.

## Findings

### The marker is the manifest, and the manifest now carries the lint policy

`Cargo.toml` marks the project. A workspace is the same file carrying a
`[workspace]` table, with the members enumerated there, so nothing discovers
them. `Cargo.lock` is present for a binary and is a decision for a library.
`rust-toolchain.toml` pins the toolchain for everyone who checks the repository
out, and is the file that makes a local run reproducible.

The manifest reference states the four levels a `[lints]` table may assign -
`forbid`, `deny`, `warn`, `allow` - and records the table as **respected as of
Cargo 1.74**. It also states the limitation that decides where policy may go:
_"Cargo only applies these to the current package and not to dependencies."_

So lint policy is manifest data, and no source file carries it. A crate
inherits the workspace policy with `lints.workspace = true`, and a pack writing
`#![deny(...)]` into `lib.rs` is writing where the ecosystem stopped writing in 2023.

### The edition is a silent default, and the silence means 2015

The reference is exact, and the exactness is the finding: _"By default `cargo
new` creates a manifest with the 2024 edition currently. If the `edition` field
is not present in `Cargo.toml`, then the 2015 edition is assumed for backwards
compatibility."_

A manifest with no `edition` is not an unset field. It is a declaration of the
oldest edition, and the project is being compiled under rules nobody chose.
That is reportable without running anything.

`rust-version` is a separate field and answers a different question - the
minimum version the package supports, where the toolchain field says what this
checkout uses. A project may set either without the other, and a project that
sets `rust-version` without testing against it has an untested claim.

### The toolchain, tool by tool

Three of these ship with rustup. Everything else is a separate binary, which is
what makes the fallback rules necessary.

| Role                | Tool                      | Ships with rustup | What only it answers                                                       |
| ------------------- | ------------------------- | ----------------- | -------------------------------------------------------------------------- |
| Driver              | `cargo`                   | yes               | Resolution, features, workspace layout                                     |
| Format              | `rustfmt`                 | yes               | -                                                                          |
| Format, manifest    | `taplo`                   | no                | Whether `Cargo.toml` itself is formatted and valid against a schema        |
| Lint                | `clippy`                  | yes               | Correctness and idiom beyond the compiler                                  |
| Typecheck           | the compiler              | yes               | -                                                                          |
| Test                | `cargo test`              | yes               | Doctests                                                                   |
| Test                | `cargo-nextest`           | no                | Per-test process isolation, parallel across binaries, JUnit XML            |
| Coverage            | `cargo-llvm-cov`          | no                | Which lines and branches the tests reached                                 |
| Advisories          | `cargo-audit`             | no                | The lockfile against the RustSec database                                  |
| Policy              | `cargo-deny`              | no                | Advisories, licences, banned crates and sources in one pass                |
| Provenance          | `cargo-vet`               | no                | Which dependencies a human reviewed                                        |
| Unsafe census       | `cargo-geiger`            | no                | How much `unsafe` the dependency tree contains                             |
| Unused deps         | `cargo-machete`           | no                | A fast heuristic answer, suitable for a gate                               |
| Unused deps         | `cargo-udeps`             | no                | An accurate answer from compiler output                                    |
| Compatibility       | `cargo-semver-checks`     | no                | Whether a release breaks the published API                                 |
| Undefined behaviour | `miri`                    | component         | What `unsafe` code does that the compiler permits and the machine does not |
| Concurrency         | `loom`                    | no                | Thread interleavings in lock-free code                                     |
| Test quality        | `cargo-mutants`           | no                | Whether the assertions would notice a change                               |
| Inputs              | `proptest`, `quickcheck`  | no                | Inputs nobody thought to write down                                        |
| Snapshots           | `insta`                   | no                | Large outputs, reviewed as diffs                                           |
| Fuzzing             | `cargo-fuzz`, `cargo-afl` | no                | Crashes found by coverage-guided search                                    |
| Benchmark           | `criterion`, `divan`      | no                | Whether a change is a regression or noise                                  |
| Expansion           | `cargo-expand`            | no                | What a derive or proc-macro actually generated                             |
| Intelligence        | `rust-analyzer`           | yes               | Editing, navigation, refactors                                             |
| Loop                | `bacon`                   | no                | Check, clippy and test repeated on save                                    |

The column that matters to a pack is the third. A verb resolved to a tool in
the "no" rows fails on a clean machine, and the failure is the pack's rather
than the project's.

### `typecheck` is the compiler, and saying so beats inventing a tool

| Verb        | Command                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------- |
| `fmt`       | `cargo fmt --all`, with `--check` to verify; `taplo fmt` where the manifest is in scope  |
| `lint`      | `cargo clippy --workspace --all-targets -- -D warnings`                                  |
| `typecheck` | the compiler; `cargo check --workspace` as the fast pass                                 |
| `test`      | `cargo nextest run --workspace` **and** `cargo test --doc`, falling back to `cargo test` |
| `build`     | `cargo build --workspace`                                                                |

`typecheck` has no separate tool because nothing is left for one to do. A pack
resolving it to `cargo check` is being honest; a pack naming a third-party
checker is adding a dependency to repeat `build`.

`--all-targets` on the lint verb is what puts tests, examples and benches under
the same policy as the library. Without it a warning in a test is invisible,
and tests are where the sloppiest code in a repository lives.

### The `test` verb has a hole in it, and the hole is silent

nextest is the better runner. It runs tests in parallel across binaries with a
process per test, retries flaky tests, and emits JUnit XML, which is what makes
its result citable as evidence where terminal output is not.

And it does not run doctests. The documentation is direct: _"Doctests are
currently not supported because of limitations in stable Rust. For now, run
doctests in a separate step with `cargo test --doc`."_

So a `test` verb resolved to nextest alone stops running a whole category of
test that the project believes is running. Nothing reports the gap: the run is
green, the count is plausible, and the examples in the documentation are no
longer compiled. A pack that swaps in nextest without adding `cargo test --doc`
has quietly reduced what the repository checks.

This is the sharpest instance of a general rule. **A faster tool that covers
less is a regression that reports success.**

### Supply-chain checking is four questions, and only one of them is vulnerabilities

`cargo-deny` is a policy gate over the dependency graph, with four classes of
check. **Advisories** for known vulnerabilities, **bans** for crates the
project has decided against, **licences** for compliance, and **sources** for
where a dependency came from. It is configured in `deny.toml` and initialised
with `cargo deny init`.

The other three tools answer questions `deny` does not. `cargo-audit` checks
the lockfile against RustSec alone and is the lighter option. `cargo-vet`
records which dependencies a human actually reviewed and shares those audits
between teams, which is the only one of the four that is about trust rather
than about metadata. `cargo-geiger` counts `unsafe` across the tree, which
feeds a review and gates nothing. `cargo-auditable` embeds the dependency list
in the binary so it can be scanned after deployment.

None of these is one of the five verbs, and reporting a licence violation as a
lint finding puts it in front of the wrong reader. They belong where the
repository declares extra checks.

### Unused dependencies have two tools and the difference is precision against cost

`cargo-machete` is a fast heuristic suitable for a gate; `cargo-udeps` inspects
compiler output and is accurate. The heuristic has false positives, which in a
gate means a check that fires wrongly and then gets disabled.

So the pairing is the design: the fast one where a gate runs on every change,
the accurate one where a human is going to act on the answer.

### A published crate has a verb nobody runs

`cargo-semver-checks` flags a breaking API change before a release. Nothing
else in the toolchain does: the code compiles, the tests pass, the lint is
clean, and the release breaks every consumer.

It is broadly adopted and the cargo team has expressed interest in merging it
into cargo, which is a fact with a date on it, and it will change.

For a pack the rule is narrow: a crate that publishes has a check the others do
not, and it runs at release, not on every change.

### Correctness beyond tests is where Rust has more than most languages

`miri` interprets the program and flags undefined behaviour in `unsafe` code
that compiles and runs correctly on the developer's machine. `loom` explores
thread interleavings for lock-free code. `cargo-mutants` changes the code and
reruns the tests to find assertions that would not have noticed.
`proptest` and `quickcheck` generate inputs and shrink a failure to its
smallest form.

These are slow, and the shape that has emerged in practice is tiers: the fast
checks on every change, the policy checks on a pull request, and the slow ones
on a schedule. That is a scheduling decision and says nothing about quality, so
the pack describes the tier and pretends nothing about what runs every time.

### The pedantic question has a conventional answer, and it is not "deny"

Clippy's `pedantic` group is opt-in by design, and the lint count is in the
hundreds. The convention the ecosystem settled on is a workspace table that
allows the group and promotes individual lints from it - `float_cmp`,
`cast_possible_truncation`, `redundant_clone`, `missing_const_for_fn` - rather
than denying the group wholesale.

That decides what a pack may author unasked. `pedantic = "deny"` in a
repository that did not ask produces findings that are style preferences, and a
reviewer cannot tell them from defects. Promoted named lints produce findings
that were each chosen.

### What a reviewer needs that no command reports

Ownership and lifetimes as a design constraint, and never as an argument with
the compiler: a signature that borrows where it should own is a decision, and
both compile.

The error boundary - where an error is wrapped, where context is added, where
it becomes an exit code. Every arrangement compiles and one of them is usable.

`unwrap` and `expect` outside tests, which a lint catches only where the policy
says so.

Feature flags as the source of untested combinations: the default set passes
and a consumer enabling two features gets code no run has covered.
`cargo-hack` exists for exactly this and is rarely wired up.

`unsafe` blocks and whether the invariant they rely on is written down beside
them, which is the one thing `miri` cannot supply.

Public API surface: what `pub` exposes that the crate will have to keep.

### What the skill has to contain

The budget is the constraint: the obligations go in the part of the body that
survives compaction, and the rest moves to supporting files.

In the body, in this order:

1. Detection. `Cargo.toml`, the `[workspace]` table, `rust-toolchain.toml`,
   `Cargo.lock` and what its presence or absence means for a library. 2. Verb
   resolution with its fallbacks, stated as a resolution, where a table would
   hide the order: which tools are not installed by default and what happens
   when they are missing. 3. The doctest rule. `test` means nextest plus `cargo
test --doc`, and never nextest alone. This is the single obligation most
   likely to be lost, because losing it looks like success. 4. What to read
   before reporting a pass. The edition field, the lint table, whether
   `--all-targets` was in the lint invocation. 5. What must never happen.
   Enabling `pedantic` wholesale. Writing `#![deny]` into source. Resolving
   `test` to nextest alone. Reporting a licence or advisory finding as a lint.

In supporting files:

- The tool inventory above, with what each answers and whether it ships with
  rustup.
- Authoring templates: a workspace `[lints]` table, a `deny.toml`, a
  `rust-toolchain.toml`, a coverage invocation.
- The tiering: what runs per change, per pull request and on a schedule.
- The reviewer's knowledge, which is the part that cannot be generated from
  documentation.
- The dated facts and what to re-check: the default edition, the Cargo version
  that respects `[lints]`, whether `cargo-semver-checks` has merged into cargo.

### What the plugin has to do beyond running commands

Authoring is half the pack. For Rust that means editing `Cargo.toml` and the
workspace - members, features, the `[lints.rust]` and `[lints.clippy]` tables -
as structured data and never as text, plus `deny.toml`, `clippy.toml`,
`rustfmt.toml` and `rust-toolchain.toml`.

Editing a manifest as text is where a pack corrupts a project, because TOML has
several correct spellings of the same table and a naive edit picks the wrong
one. `taplo` exists partly for this, and a pack that writes manifests should
verify with it.

## Conclusions

1. A Rust project is marked by `Cargo.toml`, a workspace by a `[workspace]`
   table with enumerated members, and the pinned toolchain by
   `rust-toolchain.toml`. 2. Lint policy belongs in the manifest, as
   `[lints.rust]` and `[lints.clippy]` inherited with `lints.workspace = true`,
   rather than as attributes in source. 3. A manifest with no `edition` is
   reported, because the absence means the 2015 edition and no unset field. 4.
   `rust-version` and `rust-toolchain.toml` answer different questions, and a
   `rust-version` nothing is tested against is an untested claim. 5.
   `typecheck` resolves to the compiler, and the pack says so, naming no tool
   that adds nothing over `build`. 6. `lint` covers all targets and fails on
   warnings, so a warning in a test or an example is a finding. 7. `test` is
   nextest together with `cargo test --doc`, never nextest alone, because
   nextest does not run doctests and the omission reports success. 8. A faster
   tool that covers less is a regression that reports success, and a pack
   states what each substitution stops checking. 9. A verb whose tool is not
   installed by default declares a fallback, so a clean machine is not a
   failure attributed to the project. 10. Test results are collected as JUnit
   XML, which nextest emits, because evidence has to outlive the terminal. 11.
   Supply-chain checking asks four questions: advisories, bans, licences and
   sources, which `cargo-deny` covers in one pass from `deny.toml`. 12.
   Provenance is separate from metadata. `cargo-vet` records human review and
   is the only one of these tools about trust. 13. Supply checks are declared
   on their own and folded into no verb, because a licence violation is no lint
   and reaches a different reader. 14. Unused-dependency checking uses the
   heuristic tool in a gate and the accurate one where a person will act,
   because a gate that fires wrongly is disabled. 15. A crate that publishes
   runs `cargo-semver-checks` at release, since a breaking API change is
   invisible to every other verb. 16. The slow correctness tools are tiered,
   and none is omitted. `miri`, `loom`, `cargo-mutants` and fuzzing run on a
   schedule, and the pack states the tier, implying nothing about what runs
   every time. 17. A pack does not enable `pedantic` wholesale, because a
   finding that is a style preference is indistinguishable from a defect to
   whoever has to act on it. 18. Feature combinations are a declared gap unless
   something like `cargo-hack` is wired up, because the default feature set is
   the only one most projects test. 19. The manifest is edited as structured
   data and verified, and nothing rewrites it as text, because TOML admits
   several spellings of the same table. 20. The skill body carries detection,
   conditional verb resolution, the doctest rule, what to read before reporting
   a pass, and the prohibitions, in that order. 21. The tool inventory,
   templates, tiering, reviewer knowledge and dated facts live in supporting
   files, each with what to re-check and when.

## Sources

All read 2026-09-20.

- [The Cargo manifest
  reference](https://doc.rust-lang.org/cargo/reference/manifest.html) - the
  `[lints]` table with its four levels, respected as of Cargo 1.74; that Cargo
  applies lints to the current package and not to dependencies; that `cargo
new` writes the 2024 edition and that a manifest without an `edition` field
  is compiled as 2015; and the `rust-version` field. - [RFC 3389, lint
  configuration through
  Cargo](https://rust-lang.github.io/rfcs/3389-manifest-lint.html) - the
  motivation for moving lint levels out of source attributes into the manifest,
  and workspace inheritance as part of the same design. - [cargo-nextest,
  running tests](https://nexte.st/docs/running/) - the process-per-test model
  with parallel execution across binaries; JUnit XML and the libtest JSON
  message formats; and the explicit statement that doctests are not supported
  because of limitations in stable Rust, with the instruction to run them
  separately with `cargo test --doc`. -
  [cargo-deny](https://embarkstudios.github.io/cargo-deny/) - the four classes
  of check (advisories, bans, licences, sources), configuration in `deny.toml`,
  `cargo deny init` for a starting configuration, and the description of the
  tool as a lint over the dependency graph. - [The Rust tool
  index](https://tools.corrode.dev/) - the inventory by role: `cargo-nextest`,
  `insta`, `proptest`, `quickcheck`, `rstest`, `mockall`, `loom`,
  `cargo-mutants`, `cargo-llvm-cov`, `cargo-tarpaulin`, `cargo-fuzz`,
  `cargo-afl` and `miri` for testing; `clippy` and `cargo-semver-checks` for
  linting; `rustfmt` and `taplo` for formatting; `cargo-audit`, `cargo-deny`,
  `cargo-geiger`, `cargo-auditable` and `cargo-vet` for supply chain;
  `cargo-udeps` as accurate and `cargo-machete` as a fast heuristic for unused
  dependencies; `criterion` and `divan` for benchmarking; `cargo-expand`,
  `bacon` and `rust-analyzer` for working on the code. -
  [rust-clippy](https://github.com/rust-lang/rust-clippy) - the lint groups,
  and that `pedantic` is opt-in and absent from the default set. - [Modern Rust
  tooling in
  2026](https://blog.rajpoot.dev/posts/rust/rust-tooling-cargo-2026/) and
  [clippy::pedantic and workspace
  lints](https://coreyja.com/notes/clippy-pedantic-workspace) - the convention
  of allowing the pedantic group at the workspace root and promoting individual
  lints from it, where denying the group is the common mistake. - [Faster Rust
  tests with
  cargo-nextest](https://blog.jetbrains.com/rust/2026/05/01/faster-rust-tests-with-cargo-nextest/)
  - nextest's adoption across the ecosystem and its positioning for larger
    codebases and continuous integration, recorded as a secondary source.
