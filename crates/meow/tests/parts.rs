// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Each stage resolves and reports per part, from a fixture repository whose
//! root profile declares two parts (TSK-5055, SPC-1040 "A stage in each part").

#![cfg(feature = "verbs")]

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
            std::env::temp_dir().join(format!("meow-parts-{name}-{}-{stamp}", std::process::id()));
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
    std::fs::write(path, text).unwrap();
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

const ROOT: &str = "[stages]\ntest = \"echo root-test\"\nlint = \"echo root-lint\"\n\n[parts]\nsite = \"site\"\nengine = \"crates/engine\"\n";

/// A repository with two parts, each binding `test` to its own command, and
/// a state directory of its own.
fn fixture(name: &str) -> (Dir, Dir) {
    let dir = Dir::new(name);
    let state = Dir::new(&format!("{name}-state"));
    git(&dir.0, &["init", "-q", "--template="]);
    write(&dir.0, ".meowpaw/profile.toml", ROOT);
    write(
        &dir.0,
        "site/.meowpaw/profile.toml",
        "[stages]\ntest = \"echo site-test && pwd\"\n",
    );
    write(
        &dir.0,
        "crates/engine/.meowpaw/profile.toml",
        "[stages]\ntest = \"echo engine-test && pwd\"\n",
    );
    (dir, state)
}

/// `paw verbs <args>` in `cwd`, with the fixture's state directory.
fn checks(cwd: &Path, state: &Path, args: &[&str]) -> (Output, String) {
    let done = Command::new(env!("CARGO_BIN_EXE_paw"))
        .arg("verbs")
        .args(args)
        .current_dir(cwd)
        .env("XDG_STATE_HOME", state)
        .env("XDG_RUNTIME_DIR", state)
        .env("MEOWPAW_STATE_DIR", state)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .stdin(Stdio::null())
        .output()
        .unwrap();
    let stdout = String::from_utf8_lossy(&done.stdout).into_owned();
    (done, stdout)
}

/// Every JSON line the ledger under `state` holds.
fn ledger(state: &Path) -> Vec<serde_json::Value> {
    fn walk(dir: &Path, out: &mut Vec<serde_json::Value>) {
        let Ok(entries) = std::fs::read_dir(dir) else {
            return;
        };
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                walk(&path, out);
            } else if path.extension().is_some_and(|e| e == "jsonl") {
                for line in std::fs::read_to_string(&path).unwrap().lines() {
                    out.push(serde_json::from_str(line).unwrap());
                }
            }
        }
    }
    let mut out = Vec::new();
    walk(state, &mut out);
    out
}

/// TSK-5055 criterion 1, REQ-0078, REQ-3042: `test` runs each part's own
/// command in that part's directory, by `--part` and from inside the part.
#[test]
fn each_part_runs_its_own_test() {
    let (dir, state) = fixture("run");
    for (part, word, directory) in [
        ("site", "site-test", "site"),
        ("engine", "engine-test", "crates/engine"),
    ] {
        let (done, stdout) = checks(&dir.0, &state.0, &["run", "test", "--part", part]);
        assert_eq!(done.status.code(), Some(0), "{stdout}");
        assert!(
            stdout.contains(&format!("== test: `echo {word} && pwd`")),
            "{stdout}"
        );
        let ran_in = dir.0.join(directory).display().to_string();
        assert!(
            stdout.lines().any(|line| line == ran_in),
            "{part}'s test didn't run in {ran_in}:\n{stdout}"
        );
    }
    let (done, stdout) = checks(&dir.0.join("site"), &state.0, &["run", "test"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(
        stdout.contains("== test: `echo site-test && pwd`"),
        "{stdout}"
    );
    // The root runs the root's, and a part leaves out the root's lint.
    let (_, stdout) = checks(&dir.0, &state.0, &["run", "test"]);
    assert!(stdout.contains("== test: `echo root-test`"), "{stdout}");
    let (done, stdout) = checks(&dir.0, &state.0, &["run", "lint", "--part", "site"]);
    assert_eq!(done.status.code(), Some(3), "{stdout}");
    assert!(
        stdout.contains("== lint: unresolved (undeclared"),
        "{stdout}"
    );
}

/// TSK-5055 criterion 2, REQ-3043: `status`, `run` and `evidence` name the
/// part and its directory, and a repository with no parts names itself.
#[test]
fn every_report_names_its_scope() {
    let (dir, state) = fixture("scope");
    let want = "scope: engine crates/engine";
    for args in [
        &["status", "--part", "engine"][..],
        &["run", "test", "--part", "engine"],
        &["evidence", "--part", "engine"],
    ] {
        let (_, stdout) = checks(&dir.0, &state.0, args);
        assert!(stdout.lines().any(|l| l == want), "{args:?}:\n{stdout}");
    }
    let (_, stdout) = checks(&dir.0.join("crates/engine"), &state.0, &["status"]);
    assert!(stdout.lines().any(|l| l == want), "{stdout}");
    let (done, stdout) = checks(&dir.0, &state.0, &["status", "--json", "--part", "engine"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let json: serde_json::Value = serde_json::from_str(&stdout).unwrap();
    assert_eq!(json["scope"]["part"], "engine", "{stdout}");
    assert_eq!(json["scope"]["directory"], "crates/engine", "{stdout}");

    let plain = Dir::new("plain");
    git(&plain.0, &["init", "-q", "--template="]);
    write(
        &plain.0,
        ".meowpaw/profile.toml",
        "[stages]\ntest = \"true\"\n",
    );
    for args in [&["status"][..], &["run", "test"], &["evidence"]] {
        let (_, stdout) = checks(&plain.0, &state.0, args);
        assert!(
            stdout.lines().any(|l| l == "scope: repository"),
            "{args:?}:\n{stdout}"
        );
    }
}

/// TSK-5055 criterion 2, REQ-3042: a part's evidence counts the part's runs
/// alone, so a pass at the root never stands for a part.
#[test]
fn a_parts_evidence_counts_its_own_runs() {
    let (dir, state) = fixture("evidence");
    let (done, _) = checks(&dir.0, &state.0, &["run", "test"]);
    assert_eq!(done.status.code(), Some(0));
    let (done, stdout) = checks(&dir.0, &state.0, &["evidence", "test", "--part", "site"]);
    assert_eq!(done.status.code(), Some(3), "{stdout}");
    assert!(
        stdout.contains("test: no record of a whole run"),
        "{stdout}"
    );
}

/// TSK-5055 criterion 3, REQ-3044: the ledger record carries the directory
/// the run started in beside its scope.
#[test]
fn a_record_carries_the_directory_the_run_started_in() {
    let (dir, state) = fixture("ledger");
    let started = dir.0.join("site");
    let (done, stdout) = checks(&started, &state.0, &["run", "test"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let records = ledger(&state.0);
    assert!(!records.is_empty(), "nothing was recorded");
    for record in &records {
        assert_eq!(record["scope"], "site", "{record}");
        assert_eq!(
            record["directory"],
            started.display().to_string(),
            "{record}"
        );
    }
}

/// TSK-5055 criterion 4: `--part` naming no declared part is an error naming
/// the declared parts, and nothing runs.
#[test]
fn an_undeclared_part_runs_nothing() {
    let (dir, state) = fixture("undeclared");
    let (done, stdout) = checks(&dir.0, &state.0, &["run", "test", "--part", "docs"]);
    let stderr = String::from_utf8_lossy(&done.stderr);
    assert_eq!(done.status.code(), Some(2), "{stdout}{stderr}");
    assert!(stderr.contains("docs"), "{stderr}");
    assert!(stderr.contains("site, engine"), "{stderr}");
    assert!(!stdout.contains("=="), "{stdout}");
    assert!(ledger(&state.0).is_empty(), "a record was written");
}
