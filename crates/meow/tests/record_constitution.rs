// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `paw check` reports a constitution over its target length as advice
//! (TSK-4700, REQ-2734, SPC-1220 "Its length").

#![cfg(feature = "record")]

use std::path::{Path, PathBuf};
use std::process::{Command, Output};

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "meow-constitution-{name}-{}-{stamp}",
            std::process::id()
        ));
        std::fs::create_dir_all(&path).unwrap();
        Dir(path)
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn write(root: &Path, name: &str, text: &str) {
    let path = root.join(name);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// A repository with an empty record and a constitution of `lines` lines, or
/// none, plus an optional record finding (a requirement with no status).
fn fixture(name: &str, lines: Option<usize>, finding: bool) -> Dir {
    let dir = Dir::new(name);
    write(
        &dir.0,
        ".meowpaw/profile.toml",
        "[record]\nroot = \"project\"\n",
    );
    for index in [
        "README.md",
        "adrs/README.md",
        "requirements/README.md",
        "research/RES-0001-synthesis.md",
    ] {
        let text = if index.starts_with("research") {
            "---\nid: RES-0001\nartifact: research\nstatus: approved\nrevised: 2026-01-01\n---\n\n# Research\n"
        } else {
            "# Index\n"
        };
        write(&dir.0.join("project"), index, text);
    }
    if let Some(n) = lines {
        write(&dir.0, "CLAUDE.md", &"A rule.\n".repeat(n));
    }
    if finding {
        write(
            &dir.0.join("project"),
            "requirements/REQ-0001-broken.md",
            "---\nid: REQ-0001\nartifact: requirement\n---\n\n# REQ-0001\n",
        );
    }
    dir
}

fn check(dir: &Path) -> Output {
    let layout =
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/lib/layout.toml");
    Command::new(env!("CARGO_BIN_EXE_paw"))
        .args(["record", "check"])
        .current_dir(dir)
        .env("MEOW_LAYOUT", layout)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap()
}

fn stdout(output: &Output) -> String {
    String::from_utf8_lossy(&output.stdout).into_owned()
}

const ADVICE: &str = "CLAUDE.md: over its target of 200 lines at 449; cut it";

/// Criterion 1 (REQ-2734): 449 lines on a clean record print the advice and exit 0.
#[test]
fn a_long_constitution_is_advice_and_the_exit_stays_clean() {
    let dir = fixture("long", Some(449), false);
    let output = check(&dir.0);
    let out = stdout(&output);
    assert!(out.contains(ADVICE), "{out}");
    assert_eq!(output.status.code(), Some(0), "{out}");
}

/// Criterion 2 (REQ-2734): the advice changes no count and no exit status.
#[test]
fn the_advice_changes_no_finding_count_or_exit_status() {
    let with = fixture("with", Some(449), true);
    let without = fixture("without", Some(10), true);
    let (a, b) = (check(&with.0), check(&without.0));
    assert_eq!(a.status.code(), Some(1), "{}", stdout(&a));
    assert_eq!(b.status.code(), Some(1), "{}", stdout(&b));
    let counts = |o: &Output| -> Vec<String> {
        stdout(o)
            .lines()
            .filter(|l| l.contains(" finding"))
            .map(String::from)
            .collect()
    };
    assert_eq!(counts(&a), counts(&b));
    assert!(stdout(&a).contains(ADVICE));
}

/// Criterion 3 (REQ-2734): 200 lines, or no file, print nothing about it.
#[test]
fn a_short_or_absent_constitution_prints_nothing() {
    for (name, lines) in [("exact", Some(200)), ("none", None)] {
        let dir = fixture(name, lines, false);
        let output = check(&dir.0);
        let out = stdout(&output);
        assert!(!out.contains("CLAUDE.md"), "{name}: {out}");
        assert_eq!(output.status.code(), Some(0), "{name}: {out}");
    }
}
