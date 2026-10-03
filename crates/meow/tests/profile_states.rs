// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The profile's three states and its unknown keys, as `meow-checks` prints
//! them from a fixture repository (TSK-4300, SPC-1080 "The profile").

#![cfg(feature = "verbs")]

use std::path::{Path, PathBuf};
use std::process::{Command, Output};

const VERBS: [&str; 5] = ["format", "lint", "check", "test", "build"];

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "meow-profile-{name}-{}-{stamp}",
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

fn write_profile(dir: &Path, text: &str) {
    std::fs::create_dir_all(dir.join(".meowpaw")).unwrap();
    std::fs::write(dir.join(".meowpaw/profile.toml"), text).unwrap();
}

/// A git repository at `dir`, so the root is the top of a working tree.
fn init(dir: &Path) {
    let done = Command::new("git")
        .args(["init", "-q"])
        .current_dir(dir)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap();
    assert!(done.status.success(), "git init failed: {done:?}");
}

/// `meow verbs <args>` in `dir`, with a state directory of the fixture's own.
fn checks(dir: &Path, state: &Path, args: &[&str]) -> (Output, String) {
    let done = Command::new(env!("CARGO_BIN_EXE_meow"))
        .arg("verbs")
        .args(args)
        .current_dir(dir)
        .env("XDG_STATE_HOME", state)
        .env("XDG_RUNTIME_DIR", state)
        .env("MEOWPAW_STATE_DIR", state)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap();
    let stdout = String::from_utf8_lossy(&done.stdout).into_owned();
    (done, stdout)
}

fn lines(stdout: &str) -> Vec<&str> {
    stdout.lines().map(str::trim_end).collect()
}

#[test]
fn a_profile_above_the_root_is_absent() {
    // TSK-4300 criterion 1, REQ-2940: no profile is read from above the root.
    let parent = Dir::new("above");
    let state = Dir::new("above-state");
    write_profile(&parent.0, "[verbs]\ntest = \"true\"\n");
    let root = parent.0.join("repository");
    std::fs::create_dir_all(&root).unwrap();
    init(&root);
    let (done, stdout) = checks(&root, &state.0, &["status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(
        lines(&stdout).contains(&"profile: absent"),
        "no `profile: absent` line in:\n{stdout}"
    );
    for verb in VERBS {
        let line = lines(&stdout)
            .into_iter()
            .find(|line| line.starts_with(&format!("{verb} ")))
            .unwrap_or_else(|| panic!("no line for {verb} in:\n{stdout}"));
        assert!(
            line.contains("unresolved  no profile:"),
            "{verb} isn't unresolved as `no profile`: {line}"
        );
    }
}

#[test]
fn an_unparseable_profile_names_the_parser_message_and_line_and_runs_nothing() {
    // TSK-4300 criterion 2, REQ-2948: a broken profile is told apart from an
    // absent one, every verb stays unresolved and nothing falls back.
    let root = Dir::new("broken");
    let state = Dir::new("broken-state");
    init(&root.0);
    let text = "[verbs]\ntest = \"touch ran\"\n[verbs\n";
    write_profile(&root.0, text);
    let message = text
        .parse::<toml::Table>()
        .expect_err("the fixture doesn't parse")
        .message()
        .to_string();
    let first = message.lines().next().unwrap_or_default().to_string();
    assert!(!first.is_empty(), "the parser gave no message");

    let (status, status_out) = checks(&root.0, &state.0, &["status"]);
    let (run, run_out) = checks(&root.0, &state.0, &["run", "test"]);
    for (name, stdout) in [("status", &status_out), ("run test", &run_out)] {
        let found = lines(stdout);
        assert!(
            found.contains(&"profile: unparseable"),
            "{name} prints no `profile: unparseable` line:\n{stdout}"
        );
        let error = found
            .iter()
            .find(|line| line.starts_with("profile error: "))
            .unwrap_or_else(|| panic!("{name} prints no `profile error:` line:\n{stdout}"));
        assert!(
            error.starts_with("profile error: line 3: "),
            "{name} doesn't give line 3: {error}"
        );
        assert!(
            error.contains(&first),
            "{name} doesn't carry the parser's message {first:?}: {error}"
        );
    }
    assert_eq!(status.status.code(), Some(0), "{status_out}");
    for verb in VERBS {
        let line = lines(&status_out)
            .into_iter()
            .find(|line| line.starts_with(&format!("{verb} ")))
            .unwrap_or_else(|| panic!("no line for {verb} in:\n{status_out}"));
        assert!(
            line.contains("unresolved  profile unparseable:"),
            "{verb} isn't unresolved as `profile unparseable`: {line}"
        );
    }
    assert!(
        run_out.contains("== test: unresolved (profile unparseable:"),
        "{run_out}"
    );
    assert_eq!(run.status.code(), Some(3), "{run_out}");
    assert!(
        !root.0.join("ran").exists(),
        "a command ran from a profile that doesn't parse"
    );
}

#[test]
fn an_unknown_key_is_named_once_and_changes_no_exit_status() {
    // TSK-4300 criterion 3, REQ-2942: an unknown key is ignored and reported.
    let with = Dir::new("tset");
    let without = Dir::new("no-tset");
    let state = Dir::new("tset-state");
    for (dir, text) in [
        (&with, "[verbs]\ntset = \"true\"\ntest = \"true\"\n"),
        (&without, "[verbs]\ntest = \"true\"\n"),
    ] {
        init(&dir.0);
        write_profile(&dir.0, text);
    }
    let (done, stdout) = checks(&with.0, &state.0, &["run", "test"]);
    let (plain, plain_out) = checks(&without.0, &state.0, &["run", "test"]);
    assert!(
        lines(&stdout).contains(&"profile: parsed"),
        "no `profile: parsed` line in:\n{stdout}"
    );
    let named: Vec<&str> = lines(&stdout)
        .into_iter()
        .filter(|line| line.contains("verbs.tset"))
        .collect();
    assert_eq!(
        named,
        ["unknown key: verbs.tset"],
        "verbs.tset isn't named once as unknown in:\n{stdout}"
    );
    assert!(stdout.contains("summary: test passed"), "{stdout}");
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert_eq!(done.status.code(), plain.status.code(), "{plain_out}");
    assert!(
        !lines(&plain_out)
            .iter()
            .any(|line| line.starts_with("unknown key:")),
        "a profile of known keys names an unknown one:\n{plain_out}"
    );
}
