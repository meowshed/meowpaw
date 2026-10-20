// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The Rust pack on fixture repositories (TSK-5075, SPC-1310). Each test
//! writes a git repository in a scratch directory and puts a stand-in
//! executable first on `PATH`, so no toolchain is installed or reached.

#![cfg(feature = "rust")]

#[path = "packs_common/mod.rs"]
mod packs_common;

use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path =
            std::env::temp_dir().join(format!("meow-rust-{name}-{}-{stamp}", std::process::id()));
        std::fs::create_dir_all(&path).unwrap();
        Dir(std::fs::canonicalize(&path).unwrap())
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

const PROFILE: &str = "# stages are declared elsewhere\n";
const MANIFEST: &str = "[package]\nname = \"x\"\nversion = \"0.1.0\"\nedition = \"2024\"\n";

/// A git repository holding `files`, each tracked, and a directory of
/// stand-in tools, each a shell script.
fn fixture(name: &str, files: &[(&str, &str)], tools: &[(&str, &str)]) -> (Dir, Dir) {
    let dir = Dir::new(name);
    let bin = Dir::new(&format!("{name}-bin"));
    for (file, text) in files {
        let path = dir.0.join(file);
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(&path, text).unwrap();
    }
    for (tool, script) in tools {
        let path = bin.0.join(tool);
        std::fs::write(&path, format!("#!/bin/sh\n{script}")).unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o755)).unwrap();
        }
    }
    for args in [&["init", "-q", "--template="][..], &["add", "-A"]] {
        let done = Command::new("git")
            .args(args)
            .current_dir(&dir.0)
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .output()
            .unwrap();
        assert!(done.status.success(), "git {args:?} failed: {done:?}");
    }
    (dir, bin)
}

/// `paw rust <args>` in `dir`, with the stand-in tools first on `PATH`.
fn rust(dir: &Path, bin: &Path, args: &[&str]) -> (Output, String) {
    let path = packs_common::isolated_path(bin);
    let done = Command::new(env!("CARGO_BIN_EXE_paw"))
        .arg("rust")
        .args(args)
        .current_dir(dir)
        .env("PATH", path)
        .env("HOME", bin)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .stdin(Stdio::null())
        .output()
        .unwrap();
    let stdout = String::from_utf8_lossy(&done.stdout).into_owned();
    (done, stdout)
}

/// The value of `stage = "..."` in what `bind` printed.
fn bound(stdout: &str, stage: &str) -> Option<String> {
    stdout
        .lines()
        .find_map(|l| l.strip_prefix(&format!("{stage} = \"")))
        .and_then(|l| l.strip_suffix('"'))
        .map(str::to_string)
}

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

#[test]
fn tsk_5075_criterion_1_status_reports_the_directory_and_names_the_marker() {
    // TSK-5075 criterion 1, REQ-2332: a Cargo.toml in a subdirectory makes
    // `status` report for that directory and name the marker.
    let (dir, bin) = fixture(
        "marker",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("crates/x/Cargo.toml", MANIFEST),
            ("README.md", "# r\n"),
        ],
        &[],
    );
    let (done, stdout) = rust(&dir.0, &bin.0, &["status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let scopes: Vec<&str> = stdout.lines().filter(|l| l.starts_with("scope:")).collect();
    assert_eq!(scopes, ["scope: crates/x"], "{stdout}");
    assert!(
        stdout.lines().any(|l| l == "marker: crates/x/Cargo.toml"),
        "{stdout}"
    );
}

#[test]
fn tsk_5075_criterion_1_with_no_marker_the_repository_is_not_rust() {
    // TSK-5075 criterion 1, REQ-2332: no tracked Cargo.toml prints
    // `unresolved: not a Rust repository` and exits 3, for every command.
    let (dir, bin) = fixture(
        "none",
        &[(".meowpaw/profile.toml", PROFILE), ("README.md", "# r\n")],
        &[("rustc", "touch \"$HOME/ran\"\n")],
    );
    for command in ["status", "bind", "check", "toolchain"] {
        let (done, stdout) = rust(&dir.0, &bin.0, &[command]);
        assert_eq!(done.status.code(), Some(3), "{command}: {stdout}");
        assert!(
            stdout
                .lines()
                .any(|l| l == "unresolved: not a Rust repository"),
            "{command}: {stdout}"
        );
    }
    assert!(!bin.0.join("ran").exists(), "a tool started");
}

/// The words of a command in `mise.toml` or `build-units` that this pack's
/// binding leaves out: quiet output, the release profile and the target
/// directory, none of which changes what the command checks.
fn comparable(command: &str) -> Vec<String> {
    let mut words = Vec::new();
    let mut skip = false;
    for word in command.replace("\\\n", " ").split_whitespace() {
        let word = word.trim_matches('"').replace("$root/", "");
        if skip {
            skip = false;
            continue;
        }
        match word.as_str() {
            "--quiet" | "--release" | "$@" => {}
            "--target-dir" => skip = true,
            _ => words.push(word),
        }
    }
    words
}

#[test]
fn tsk_5075_criterion_2_bind_matches_the_commands_this_repositorys_gate_runs() {
    // TSK-5075 criterion 2, REQ-2332: `bind` on this repository's crate
    // prints the cargo commands `mise.toml` runs. The repository's own
    // profile declares every stage, and `bind` prints none of those, so the
    // fixture holds a copy of the crate's manifest and no profile stages.
    let manifest = std::fs::read_to_string(repo_root().join("crates/meow/Cargo.toml")).unwrap();
    let (dir, bin) = fixture(
        "own",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("crates/meow/Cargo.toml", &manifest),
            ("crates/meow/src/main.rs", "fn main() {}\n"),
        ],
        &[],
    );
    let (done, stdout) = rust(&dir.0, &bin.0, &["bind"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let mise: toml::Table = std::fs::read_to_string(repo_root().join("mise.toml"))
        .unwrap()
        .parse()
        .unwrap();
    let task = |name: &str| {
        mise["tasks"][name]["run"]
            .as_str()
            .unwrap_or_else(|| panic!("mise.toml has no task {name}"))
            .to_string()
    };
    let units = std::fs::read_to_string(repo_root().join("crates/meow/build-units")).unwrap();
    let at = units
        .find("cargo build")
        .expect("build-units runs no cargo build");
    let mut release = String::new();
    for line in units[at..].lines() {
        release.push_str(line);
        release.push('\n');
        if !line.ends_with('\\') {
            break;
        }
    }
    for (stage, gate) in [
        ("format", task("crate-fmt")),
        ("lint", task("crate-lint")),
        ("check", task("crate-check")),
        ("test", task("crate")),
        ("build", release),
    ] {
        let printed = bound(&stdout, stage).unwrap_or_else(|| panic!("{stage} unbound: {stdout}"));
        assert_eq!(comparable(&printed), comparable(&gate), "{stage}");
    }
}

#[test]
fn tsk_5075_criterion_3_a_runner_without_doctests_is_followed_by_them() {
    // TSK-5075 criterion 3, REQ-2412, REQ-2420: cargo-nextest runs no
    // doctests, so where the repository configured it and has a library
    // target, `test` runs `cargo test --doc` after it. Without nextest the
    // stage is `cargo test`, which runs them.
    let (dir, bin) = fixture(
        "doc",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("Cargo.toml", MANIFEST),
            ("src/lib.rs", "//! x\n"),
            (".config/nextest.toml", "[profile.default]\n"),
        ],
        &[],
    );
    let (_, stdout) = rust(&dir.0, &bin.0, &["bind"]);
    assert_eq!(
        bound(&stdout, "test").as_deref(),
        Some("cargo nextest run && cargo test --doc"),
        "{stdout}"
    );
    let (dir, bin) = fixture(
        "doc-bin",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("Cargo.toml", MANIFEST),
            ("src/main.rs", "fn main() {}\n"),
            (".config/nextest.toml", "[profile.default]\n"),
        ],
        &[],
    );
    let (_, stdout) = rust(&dir.0, &bin.0, &["bind"]);
    assert_eq!(
        bound(&stdout, "test").as_deref(),
        Some("cargo nextest run"),
        "a crate with no library has no doctests: {stdout}"
    );
    let (dir, bin) = fixture(
        "doc-plain",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("Cargo.toml", MANIFEST),
            ("src/lib.rs", "//! x\n"),
        ],
        &[],
    );
    let (_, stdout) = rust(&dir.0, &bin.0, &["bind"]);
    assert_eq!(
        bound(&stdout, "test").as_deref(),
        Some("cargo test"),
        "{stdout}"
    );
}

const RUSTC: &str = "echo 'rustc 1.99.0 (abcdef 2026-09-01)'\n";

#[test]
fn tsk_5075_criterion_3_a_pinned_toolchain_is_compared_with_the_installed_one() {
    // TSK-5075 criterion 3, REQ-2428: `toolchain` names the pin and the
    // installed version when they differ, and says they match when they do.
    let pinned = |channel: &str| format!("[toolchain]\nchannel = \"{channel}\"\n");
    let files = |channel: &str| {
        vec![
            (".meowpaw/profile.toml".to_string(), PROFILE.to_string()),
            ("Cargo.toml".to_string(), MANIFEST.to_string()),
            ("rust-toolchain.toml".to_string(), pinned(channel)),
        ]
    };
    let run = |name: &str, channel: &str, tools: &[(&str, &str)]| {
        let owned = files(channel);
        let borrowed: Vec<(&str, &str)> = owned
            .iter()
            .map(|(a, b)| (a.as_str(), b.as_str()))
            .collect();
        let (dir, bin) = fixture(name, &borrowed, tools);
        let (done, stdout) = rust(&dir.0, &bin.0, &["toolchain"]);
        (done.status.code(), stdout)
    };
    let (code, out) = run("pin-same", "1.99.0", &[("rustc", RUSTC)]);
    assert_eq!(code, Some(0), "{out}");
    assert!(
        out.contains("toolchain: rust 1.99.0, pinned in rust-toolchain.toml and installed"),
        "{out}"
    );
    let (code, out) = run("pin-minor", "1.99", &[("rustc", RUSTC)]);
    assert_eq!(code, Some(0), "a pin of 1.99 holds 1.99.0: {out}");
    let (code, out) = run("pin-differs", "1.80.0", &[("rustc", RUSTC)]);
    assert_eq!(code, Some(3), "{out}");
    assert!(
        out.lines()
            .any(|l| l == "unresolved: rust 1.80.0 pinned, 1.99.0 installed"),
        "{out}"
    );
    let (code, out) = run(
        "pin-missing",
        "1.80.0",
        &[("rustc", "echo 'error: toolchain missing' >&2; exit 1\n")],
    );
    assert_eq!(code, Some(3), "{out}");
    assert!(
        out.lines()
            .any(|l| l.starts_with("unresolved: rust 1.80.0 pinned, none installed")),
        "{out}"
    );
    let (code, out) = run("pin-absent", "1.80.0", &[]);
    assert_eq!(code, Some(3), "{out}");
    assert!(out.lines().any(|l| l == "tool absent: rustc"), "{out}");
    let (code, out) = run("pin-channel", "stable", &[("rustc", RUSTC)]);
    assert_eq!(code, Some(0), "{out}");
    assert!(
        out.contains("toolchain: rust-toolchain.toml pins the stable channel, no version"),
        "{out}"
    );
}

#[test]
fn tsk_5075_criterion_3_build_output_must_be_ignored() {
    // TSK-5075 criterion 3, REQ-2442: cargo writes `target/` into the working
    // tree, so a repository that doesn't ignore it has a finding, and one
    // that does has none.
    let (dir, bin) = fixture(
        "target",
        &[(".meowpaw/profile.toml", PROFILE), ("Cargo.toml", MANIFEST)],
        &[],
    );
    let (done, stdout) = rust(&dir.0, &bin.0, &["check"]);
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert!(
        stdout
            .lines()
            .any(|l| l == "target isn't ignored, and cargo writes its build output there"),
        "{stdout}"
    );
    let (dir, bin) = fixture(
        "target-ignored",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("Cargo.toml", MANIFEST),
            (".gitignore", "/target\n"),
        ],
        &[],
    );
    let (done, stdout) = rust(&dir.0, &bin.0, &["check"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
}

#[test]
fn tsk_5075_criterion_3_the_manifest_is_checked_for_what_it_leaves_unsaid() {
    // TSK-5075 criterion 3, REQ-2434: a manifest with no edition compiles as
    // 2015, and a member that doesn't inherit the workspace's lints runs
    // without them.
    let workspace =
        "[workspace]\nmembers = [\"m\"]\n\n[workspace.lints.clippy]\npedantic = \"warn\"\n";
    let (dir, bin) = fixture(
        "findings",
        &[
            (".meowpaw/profile.toml", PROFILE),
            (".gitignore", "target\n"),
            ("Cargo.toml", workspace),
            (
                "m/Cargo.toml",
                "[package]\nname = \"m\"\nversion = \"0.1.0\"\n",
            ),
        ],
        &[],
    );
    let (done, stdout) = rust(&dir.0, &bin.0, &["check"]);
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert!(
        stdout
            .lines()
            .any(|l| l == "m/Cargo.toml: no edition, so cargo compiles it as the 2015 edition"),
        "{stdout}"
    );
    assert!(
        stdout.lines().any(|l| l
            == "m/Cargo.toml doesn't inherit the workspace's lints: set workspace = true under [lints]"),
        "{stdout}"
    );
}

#[test]
fn tsk_5075_criterion_3_a_clean_report_names_the_clippy_groups_it_ran() {
    // TSK-5075 criterion 3, REQ-2432: a clean `check` names the groups clippy
    // runs: the five it turns on by default, plus each the manifest raises.
    let (dir, bin) = fixture(
        "groups",
        &[
            (".meowpaw/profile.toml", PROFILE),
            (".gitignore", "target\n"),
            (
                "Cargo.toml",
                "[package]\nname = \"x\"\nversion = \"0.1.0\"\nedition = \"2024\"\n\n[lints.clippy]\npedantic = { level = \"warn\", priority = -1 }\nstyle = \"allow\"\n",
            ),
        ],
        &[],
    );
    let (done, stdout) = rust(&dir.0, &bin.0, &["check"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(
        stdout.contains("no findings; rule groups enabled:"),
        "{stdout}"
    );
    assert!(
        stdout
            .lines()
            .any(|l| l == "clippy groups: correctness, suspicious, complexity, perf, pedantic"),
        "{stdout}"
    );
    let (_, bound_out) = rust(&dir.0, &bin.0, &["bind"]);
    assert!(
        bound_out
            .lines()
            .any(|l| l.starts_with('#') && l.contains("clippy groups") && l.contains("pedantic")),
        "{bound_out}"
    );
    assert_eq!(
        bound(&bound_out, "lint").as_deref(),
        Some("cargo clippy --all-targets -- -D warnings"),
        "the pack turns on no group itself: {bound_out}"
    );
}

#[test]
fn tsk_5075_criterion_3_the_page_states_its_generated_files() {
    // TSK-5075 criterion 3, REQ-2450: the page names what to commit and what
    // to ignore. The shared layer's own test holds the section's shape.
    let page = std::fs::read_to_string(repo_root().join("plugins/meow-rust/README.md"))
        .expect("plugins/meow-rust/README.md is missing");
    assert!(
        page.contains("## Generated files"),
        "no Generated files section"
    );
    let section = page.split("## Generated files").nth(1).unwrap();
    let section = section.split("\n## ").next().unwrap().to_lowercase();
    assert!(section.contains("cargo.lock") && section.contains("commit"));
    assert!(section.contains("target/") && section.contains("ignore"));
}

#[test]
fn tsk_5075_criterion_3_several_manifests_outside_one_workspace_are_unresolved() {
    // TSK-5075, SPC-1310 "Detection": no one cargo command reaches two
    // separate workspaces, so every stage is unresolved and none guessed.
    let (dir, bin) = fixture(
        "several",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("a/Cargo.toml", MANIFEST),
            ("b/Cargo.toml", MANIFEST),
        ],
        &[],
    );
    let (done, stdout) = rust(&dir.0, &bin.0, &["bind"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(
            stdout.lines().any(|l| l.starts_with(&format!(
                "# {stage}: unresolved, several Cargo manifests outside one workspace"
            ))),
            "{stage}: {stdout}"
        );
    }
}
