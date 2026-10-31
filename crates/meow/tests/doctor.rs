// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-checks doctor` answers whether the repository can be worked on here,
//! names each installed pack and the marker it matched, marks a finding that
//! depends on this machine, and writes nothing (TSK-4965, SPC-1040 "Whether
//! the repository can be worked on").

#![cfg(all(
    feature = "verbs",
    feature = "record",
    feature = "mise",
    feature = "gotask",
    feature = "markdown"
))]

use std::collections::BTreeMap;
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
            std::env::temp_dir().join(format!("meow-doctor-{name}-{}-{stamp}", std::process::id()));
        std::fs::create_dir_all(&path).unwrap();
        Dir(std::fs::canonicalize(&path).unwrap())
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn write(dir: &Path, name: &str, text: &str) {
    let path = dir.join(name);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(&path, text).unwrap();
}

fn git(dir: &Path, args: &[&str]) {
    let done = Command::new("git")
        .args(args)
        .current_dir(dir)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap();
    assert!(done.status.success(), "git {args:?} failed: {done:?}");
}

/// Every stage resolves to a shell builtin, except where `stages` says.
fn profile(stages: &str) -> String {
    format!(
        "[stages]\nformat = \"true\"\ncheck = \"true\"\ntest = \"true\"\n{stages}\n[record]\nroot = \"project\"\n"
    )
}

/// A repository with a markdownlint file and a `mise.toml`, the given
/// profile, and a home whose plugin cache holds `meow-markdown` and
/// `meow-mise`.
struct Fixture {
    repo: Dir,
    home: Dir,
    state: Dir,
}

fn fixture(name: &str, stages: &str) -> Fixture {
    let repo = Dir::new(name);
    let home = Dir::new(&format!("{name}-home"));
    let state = Dir::new(&format!("{name}-state"));
    git(&repo.0, &["init", "-q", "--template="]);
    write(&repo.0, ".meowpaw/profile.toml", &profile(stages));
    write(
        &repo.0,
        ".markdownlint-cli2.yaml",
        "config:\n  MD013: false\n",
    );
    write(&repo.0, "mise.toml", "[tasks.test]\nrun = \"true\"\n");
    write(&repo.0, "README.md", "# r\n");
    write(&repo.0, "project/README.md", "# record\n");
    git(&repo.0, &["add", "-A"]);
    for unit in ["meow-markdown", "meow-mise"] {
        write(
            &home.0,
            &format!(".claude/plugins/cache/meowpaw/{unit}/1.0.0/bin/{unit}"),
            "#!/bin/sh\n",
        );
    }
    Fixture { repo, home, state }
}

/// `paw <args>` in the fixture, with only the system's own tools on `PATH`.
fn paw(fixture: &Fixture, args: &[&str]) -> (Output, String) {
    let state = &fixture.state.0;
    let done = Command::new(env!("CARGO_BIN_EXE_paw"))
        .args(args)
        .current_dir(&fixture.repo.0)
        .env("PATH", "/usr/bin:/bin")
        .env("HOME", &fixture.home.0)
        .env_remove("CLAUDE_CONFIG_DIR")
        .env("XDG_STATE_HOME", state)
        .env("XDG_RUNTIME_DIR", state)
        .env("MEOWPAW_STATE_DIR", state)
        .env(
            "MEOW_LAYOUT",
            Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/lib/layout.toml"),
        )
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .stdin(Stdio::null())
        .output()
        .unwrap();
    let stdout = String::from_utf8_lossy(&done.stdout).into_owned();
    (done, stdout)
}

/// Every file under `dir`, by path, with its bytes.
fn snapshot(dir: &Path) -> BTreeMap<PathBuf, Vec<u8>> {
    fn walk(dir: &Path, out: &mut BTreeMap<PathBuf, Vec<u8>>) {
        for entry in std::fs::read_dir(dir).unwrap().flatten() {
            let path = entry.path();
            if path.is_dir() {
                walk(&path, out);
            } else {
                out.insert(path.clone(), std::fs::read(&path).unwrap_or_default());
            }
        }
    }
    let mut out = BTreeMap::new();
    walk(dir, &mut out);
    out
}

const ALL: &str = "lint = \"true\"\nbuild = \"true\"\n";

/// TSK-4965 criterion 1, REQ-3090: each installed pack is named with the
/// marker it matched and the directory the marker sits in.
#[test]
fn doctor_names_each_pack_and_the_marker_it_matched() {
    let fixture = fixture("packs", ALL);
    let (done, stdout) = paw(&fixture, &["verbs", "doctor"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let lines: Vec<&str> = stdout.lines().collect();
    assert!(
        lines.contains(&"pack: meow-markdown matched .markdownlint-cli2.yaml in ."),
        "{stdout}"
    );
    assert!(
        lines.contains(&"pack: meow-mise matched mise.toml in ."),
        "{stdout}"
    );
    assert!(
        !stdout.contains("meow-gotask"),
        "a pack not installed: {stdout}"
    );
}

/// TSK-4965 criterion 2, REQ-3084: a stage naming a tool not on `PATH` is a
/// finding marked `machine`, and doctor exits 3 where every finding is.
#[test]
fn a_missing_tool_is_a_machine_finding() {
    let fixture = fixture(
        "machine",
        "lint = \"no-such-tool-4965 --check '**/*.md'\"\nbuild = \"true\"\n",
    );
    let (done, stdout) = paw(&fixture, &["verbs", "doctor"]);
    assert_eq!(done.status.code(), Some(3), "{stdout}");
    let findings: Vec<&str> = stdout
        .lines()
        .filter(|l| l.starts_with("finding:"))
        .collect();
    assert_eq!(findings.len(), 1, "{stdout}");
    assert!(
        findings[0].starts_with("finding: machine: lint")
            && findings[0].contains("no-such-tool-4965"),
        "{stdout}"
    );
    // A finding about the repository makes it exit 1.
    let fixture = fixture_without_build();
    let (done, stdout) = paw(&fixture, &["verbs", "doctor"]);
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with("finding: repository: build")),
        "{stdout}"
    );
}

fn fixture_without_build() -> Fixture {
    fixture("repository", "lint = \"true\"\n")
}

/// TSK-4965 criterion 3, REQ-3086: the repository, the state directory with
/// its ledger and the home are byte-identical before and after doctor runs.
#[test]
fn doctor_writes_nothing() {
    let fixture = fixture("writes", ALL);
    let (done, _) = paw(&fixture, &["verbs", "run", "test"]);
    assert_eq!(done.status.code(), Some(0));
    let before = [
        snapshot(&fixture.repo.0),
        snapshot(&fixture.state.0),
        snapshot(&fixture.home.0),
    ];
    assert!(!before[1].is_empty(), "the fixture's ledger is empty");
    let (done, stdout) = paw(&fixture, &["verbs", "doctor"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let after = [
        snapshot(&fixture.repo.0),
        snapshot(&fixture.state.0),
        snapshot(&fixture.home.0),
    ];
    assert!(before == after, "doctor changed a file");
}

/// TSK-4965 criterion 4, REQ-3080: doctor names no step, gate or artifact,
/// and `paw status` names no stage's resolution or pack's detection.
#[test]
fn doctor_and_paw_status_answer_different_questions() {
    let fixture = fixture("questions", ALL);
    let (_, doctor) = paw(&fixture, &["verbs", "doctor"]);
    let (_, status) = paw(&fixture, &["record", "status"]);
    assert!(!status.trim().is_empty(), "paw status printed nothing");
    assert!(
        !status.contains("not checked"),
        "paw status read no record:\n{status}"
    );
    let doctor_words = doctor.to_lowercase();
    for word in [
        "research",
        "requirement",
        "design",
        "spec",
        "implement",
        "review",
        "gate",
        "artifact",
        "task",
        "decision",
    ] {
        assert!(
            !doctor_words.contains(word),
            "doctor names {word}:\n{doctor}"
        );
    }
    let status_words = status.to_lowercase();
    for word in [
        "resolved", "pack:", "marker", "matched", "machine", "scope:",
    ] {
        assert!(
            !status_words.contains(word),
            "paw status names {word}:\n{status}"
        );
    }
}
