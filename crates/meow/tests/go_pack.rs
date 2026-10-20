// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The Go pack on fixture repositories (TSK-5090, SPC-1340). Each test writes
//! a git repository in a scratch directory and puts a stand-in executable
//! first on `PATH`, so no toolchain is installed or reached.

#![cfg(feature = "go")]

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
            std::env::temp_dir().join(format!("meow-go-{name}-{}-{stamp}", std::process::id()));
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
const MODULE: &str = "module example.com/x\n\ngo 1.26\n";
const GOLANGCI_V2: &str = "version: \"2\"\nlinters:\n  default: standard\n";

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

/// `paw go <args>` in `dir`, with the stand-in tools first on `PATH`.
fn go(dir: &Path, bin: &Path, args: &[&str]) -> (Output, String) {
    let path = format!("{}:/usr/bin:/bin", bin.display());
    let done = Command::new(env!("CARGO_BIN_EXE_paw"))
        .arg("go")
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
        .map(|l| l.replace("\\\"", "\""))
}

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

#[test]
fn tsk_5090_criterion_1_status_reports_the_directory_and_names_the_marker() {
    // TSK-5090 criterion 1, REQ-2334: a go.mod in a subdirectory makes
    // `status` report for that directory and name the marker.
    let (dir, bin) = fixture(
        "marker",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("services/api/go.mod", MODULE),
            ("README.md", "# r\n"),
        ],
        &[],
    );
    let (done, stdout) = go(&dir.0, &bin.0, &["status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let scopes: Vec<&str> = stdout.lines().filter(|l| l.starts_with("scope:")).collect();
    assert_eq!(scopes, ["scope: services/api"], "{stdout}");
    assert!(
        stdout.lines().any(|l| l == "marker: services/api/go.mod"),
        "{stdout}"
    );
    assert!(stdout.lines().any(|l| l == "go: 1.26 minimum"), "{stdout}");
}

#[test]
fn tsk_5090_criterion_1_with_no_marker_the_repository_is_not_go() {
    // TSK-5090 criterion 1, REQ-2334: no tracked go.mod prints
    // `unresolved: not a Go repository` and exits 3, for every command, and
    // starts no tool.
    let (dir, bin) = fixture(
        "none",
        &[(".meowpaw/profile.toml", PROFILE), ("README.md", "# r\n")],
        &[("go", "touch \"$HOME/ran\"\n")],
    );
    for command in ["status", "bind", "check", "toolchain"] {
        let (done, stdout) = go(&dir.0, &bin.0, &[command]);
        assert_eq!(done.status.code(), Some(3), "{command}: {stdout}");
        assert!(
            stdout
                .lines()
                .any(|l| l == "unresolved: not a Go repository"),
            "{command}: {stdout}"
        );
    }
    assert!(!bin.0.join("ran").exists(), "a tool started");
}

/// Whether `bind` printed `stage` bound, or unresolved or unbound with a reason.
fn settled(stdout: &str, stage: &str) -> bool {
    bound(stdout, stage).is_some()
        || stdout.lines().any(|l| {
            l.strip_prefix(&format!("# {stage}: unresolved, "))
                .or_else(|| l.strip_prefix(&format!("# {stage}: unbound, ")))
                .is_some_and(|reason| !reason.trim().is_empty())
        })
}

#[test]
fn tsk_5090_criterion_2_bind_prints_all_five_stages_bound_or_with_a_reason() {
    // TSK-5090 criterion 2, REQ-2334: on a fixture with only a go.mod, and on
    // one with a golangci-lint v2 configuration that has formatters, each of
    // the five stages is bound or printed unresolved or unbound with a reason.
    let (dir, bin) = fixture(
        "bind-bare",
        &[(".meowpaw/profile.toml", PROFILE), ("go.mod", MODULE)],
        &[],
    );
    let (done, stdout) = go(&dir.0, &bin.0, &["bind"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(settled(&stdout, stage), "{stage}: {stdout}");
    }
    assert_eq!(
        bound(&stdout, "format").as_deref(),
        Some("test -z \"$(gofmt -l .)\"")
    );
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with("# lint: unbound, looked for")),
        "{stdout}"
    );
    assert_eq!(bound(&stdout, "check").as_deref(), Some("go vet ./..."));
    assert_eq!(bound(&stdout, "build").as_deref(), Some("go build ./..."));
    let (dir, bin) = fixture(
        "bind-formatters",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("go.mod", MODULE),
            (
                ".golangci.yml",
                "version: \"2\"\nformatters:\n  enable:\n    - gofumpt\n",
            ),
        ],
        &[],
    );
    let (_, stdout) = go(&dir.0, &bin.0, &["bind"]);
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(settled(&stdout, stage), "{stage}: {stdout}");
    }
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with("# format: unresolved, .golangci.yml configures formatters")),
        "{stdout}"
    );
    assert_eq!(
        bound(&stdout, "lint").as_deref(),
        Some("golangci-lint run"),
        "{stdout}"
    );
}

#[test]
fn tsk_5090_criterion_2_a_module_below_the_root_is_reached_with_cd() {
    // TSK-5090 criterion 2, REQ-2334: a single module below the root binds
    // each stage with `cd <directory> &&`, and two modules bind none.
    let (dir, bin) = fixture(
        "below",
        &[(".meowpaw/profile.toml", PROFILE), ("api/go.mod", MODULE)],
        &[],
    );
    let (_, stdout) = go(&dir.0, &bin.0, &["bind"]);
    assert_eq!(
        bound(&stdout, "build").as_deref(),
        Some("cd api && go build ./...")
    );
    let (dir, bin) = fixture(
        "two",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("a/go.mod", MODULE),
            ("b/go.mod", MODULE),
        ],
        &[],
    );
    let (done, stdout) = go(&dir.0, &bin.0, &["bind"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(
            stdout.lines().any(|l| l.starts_with(&format!(
                "# {stage}: unresolved, several Go modules and no single command reaching them"
            ))),
            "{stage}: {stdout}"
        );
    }
}

#[test]
fn tsk_5090_criterion_3_the_race_detector_is_on_and_turning_it_off_is_recorded() {
    // TSK-5090 criterion 3, REQ-2414, REQ-2412: `test` is `go test`, which
    // runs the documentation examples that state their output, with the race
    // detector on, and a profile recording otherwise is named in a comment.
    let (dir, bin) = fixture(
        "race",
        &[(".meowpaw/profile.toml", PROFILE), ("go.mod", MODULE)],
        &[],
    );
    let (_, stdout) = go(&dir.0, &bin.0, &["bind"]);
    assert_eq!(
        bound(&stdout, "test").as_deref(),
        Some("go test -race ./...")
    );
    let (dir, bin) = fixture(
        "race-off",
        &[
            (".meowpaw/profile.toml", "[go]\nrace = false\n"),
            ("go.mod", MODULE),
        ],
        &[],
    );
    let (_, stdout) = go(&dir.0, &bin.0, &["bind"]);
    assert_eq!(bound(&stdout, "test").as_deref(), Some("go test ./..."));
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with('#') && l.contains("[go] race = false")),
        "{stdout}"
    );
    let (done, status) = go(&dir.0, &bin.0, &["status"]);
    assert_eq!(done.status.code(), Some(0), "{status}");
    assert!(
        status
            .lines()
            .any(|l| l == "race detector: off, as [go] race = false records"),
        "{status}"
    );
    assert!(
        !status.lines().any(|l| l.starts_with("unknown key")),
        "[go] race is a key the profile knows: {status}"
    );
}

#[test]
fn tsk_5090_criterion_3_only_the_configured_linter_is_bound() {
    // TSK-5090 criterion 3, REQ-2420: staticcheck binds where only
    // staticcheck is configured, and golangci-lint where both are, with the
    // other named.
    let (dir, bin) = fixture(
        "staticcheck",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("go.mod", MODULE),
            ("staticcheck.conf", "checks = [\"all\"]\n"),
        ],
        &[],
    );
    let (_, stdout) = go(&dir.0, &bin.0, &["bind"]);
    assert_eq!(bound(&stdout, "lint").as_deref(), Some("staticcheck ./..."));
    let (dir, bin) = fixture(
        "both",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("go.mod", MODULE),
            ("staticcheck.conf", "checks = [\"all\"]\n"),
            (".golangci.yml", GOLANGCI_V2),
        ],
        &[],
    );
    let (_, stdout) = go(&dir.0, &bin.0, &["bind"]);
    assert_eq!(bound(&stdout, "lint").as_deref(), Some("golangci-lint run"));
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with('#') && l.contains("staticcheck.conf")),
        "{stdout}"
    );
}

const GO: &str =
    "[ \"$GOTOOLCHAIN\" = local ] || exit 9\necho 'go version go1.26.0 darwin/arm64'\n";

#[test]
fn tsk_5090_criterion_3_a_pinned_toolchain_is_compared_with_the_installed_one() {
    // TSK-5090 criterion 3, REQ-2428: `toolchain` names the pin and the
    // installed version when they differ, runs go with GOTOOLCHAIN=local so
    // it doesn't switch, and says they match when they do.
    let run = |name: &str, line: &str, tools: &[(&str, &str)]| {
        let module = format!("module example.com/x\n\ngo 1.26\n{line}");
        let (dir, bin) = fixture(
            name,
            &[(".meowpaw/profile.toml", PROFILE), ("go.mod", &module)],
            tools,
        );
        let (done, stdout) = go(&dir.0, &bin.0, &["toolchain"]);
        (done.status.code(), stdout)
    };
    let (code, out) = run("pin-same", "toolchain go1.26.0\n", &[("go", GO)]);
    assert_eq!(code, Some(0), "{out}");
    assert!(
        out.contains("toolchain: go 1.26.0, pinned in go.mod and installed"),
        "{out}"
    );
    let (code, out) = run("pin-differs", "toolchain go1.25.4\n", &[("go", GO)]);
    assert_eq!(code, Some(3), "{out}");
    assert!(
        out.lines()
            .any(|l| l == "unresolved: go 1.25.4 pinned, 1.26.0 installed"),
        "{out}"
    );
    let (code, out) = run(
        "pin-missing",
        "toolchain go1.25.4\n",
        &[("go", "echo 'go: no toolchain' >&2; exit 1\n")],
    );
    assert_eq!(code, Some(3), "{out}");
    assert!(
        out.lines()
            .any(|l| l.starts_with("unresolved: go 1.25.4 pinned, none installed")),
        "{out}"
    );
    let (code, out) = run("pin-absent", "toolchain go1.25.4\n", &[]);
    assert_eq!(code, Some(3), "{out}");
    assert!(out.lines().any(|l| l == "tool absent: go"), "{out}");
    let (code, out) = run("pin-none", "", &[("go", GO)]);
    assert_eq!(code, Some(0), "a go line is a minimum, not a pin: {out}");
    assert!(
        out.lines().any(|l| l == "toolchain: nothing pinned"),
        "{out}"
    );
}

#[test]
fn tsk_5090_criterion_3_a_supply_chain_check_states_its_reach() {
    // TSK-5090 criterion 3, REQ-2436: where govulncheck is a declared tool,
    // `check` states that it covers transitive dependencies and reports
    // reachability, and where none is, it says so.
    let (dir, bin) = fixture(
        "vuln",
        &[
            (".meowpaw/profile.toml", PROFILE),
            (
                "go.mod",
                "module example.com/x\n\ngo 1.26\n\ntool golang.org/x/vuln/cmd/govulncheck\n",
            ),
        ],
        &[],
    );
    let (done, stdout) = go(&dir.0, &bin.0, &["check"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(
        stdout.lines().any(|l| l
            == "supply chain: govulncheck: covers direct and transitive dependencies, and reports a vulnerable dependency only where the code reaches it, so reachability"),
        "{stdout}"
    );
    let (dir, bin) = fixture(
        "no-vuln",
        &[(".meowpaw/profile.toml", PROFILE), ("go.mod", MODULE)],
        &[],
    );
    let (_, stdout) = go(&dir.0, &bin.0, &["check"]);
    assert!(
        stdout.lines().any(|l| l == "supply chain: none configured"),
        "{stdout}"
    );
}

#[test]
fn tsk_5090_criterion_3_a_v1_configuration_is_a_finding() {
    // TSK-5090 criterion 3, REQ-2434, REQ-2432: a golangci-lint file with no
    // version "2", or naming a linter v2 merged or removed, is a finding; a
    // v2 file is clean, and the clean report names what it checked.
    let (dir, bin) = fixture(
        "v1",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("go.mod", MODULE),
            (
                ".golangci.yml",
                "linters:\n  disable-all: true\n  enable:\n    - stylecheck\n    - govet\n",
            ),
        ],
        &[],
    );
    let (done, stdout) = go(&dir.0, &bin.0, &["check"]);
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    for finding in [
        ".golangci.yml: declares no version \"2\", so it is a v1 configuration",
        ".golangci.yml names disable-all, which golangci-lint v2 merged or removed",
        ".golangci.yml names stylecheck, which golangci-lint v2 merged or removed",
    ] {
        assert!(stdout.lines().any(|l| l == finding), "{finding}: {stdout}");
    }
    let (dir, bin) = fixture(
        "v2",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("go.mod", MODULE),
            (".golangci.yml", GOLANGCI_V2),
        ],
        &[],
    );
    let (done, stdout) = go(&dir.0, &bin.0, &["check"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(
        stdout.contains("no findings; rule groups enabled:"),
        "{stdout}"
    );
    let (dir, bin) = fixture(
        "broken",
        &[
            (".meowpaw/profile.toml", PROFILE),
            ("go.mod", MODULE),
            (".golangci.json", "{ not json"),
        ],
        &[],
    );
    let (done, stdout) = go(&dir.0, &bin.0, &["check"]);
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with(".golangci.json doesn't parse as JSON:")),
        "{stdout}"
    );
}

#[test]
fn tsk_5090_criterion_3_the_page_states_its_generated_files() {
    // TSK-5090 criterion 3, REQ-2450: the page names what to commit and what
    // to ignore. The shared layer's own test holds the section's shape.
    let page = std::fs::read_to_string(repo_root().join("plugins/meow-go/README.md"))
        .expect("plugins/meow-go/README.md is missing");
    assert!(
        page.contains("## Generated files"),
        "no Generated files section"
    );
    let section = page.split("## Generated files").nth(1).unwrap();
    let section = section.split("\n## ").next().unwrap().to_lowercase();
    assert!(section.contains("go.sum") && section.contains("commit"));
    assert!(section.contains("*.test") && section.contains("ignore"));
}
