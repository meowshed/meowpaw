// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The commit type check reads the profile's own list and no other
//! (TSK-4320, REQ-2952, SPC-1050).

#![cfg(feature = "scm")]

use std::io::Write;
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
            std::env::temp_dir().join(format!("meow-types-{name}-{}-{stamp}", std::process::id()));
        std::fs::create_dir_all(path.join(".meowpaw")).unwrap();
        Dir(path)
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

/// `meow scm check-message` in `dir`, given `message` on standard input.
fn check(dir: &Path, message: &str) -> (Output, String) {
    let mut child = Command::new(env!("CARGO_BIN_EXE_meow"))
        .args(["scm", "check-message"])
        .current_dir(dir)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(message.as_bytes())
        .unwrap();
    let done = child.wait_with_output().unwrap();
    let stdout = String::from_utf8_lossy(&done.stdout).into_owned();
    (done, stdout)
}

fn spec_and_chore_only() -> Dir {
    let dir = Dir::new("declared");
    std::fs::write(
        dir.0.join(".meowpaw/profile.toml"),
        "[commits.types]\nspec = \"none\"\nchore = \"none\"\n",
    )
    .unwrap();
    dir
}

#[test]
fn a_type_the_profile_doesnt_declare_fails_the_declared_type_check() {
    // TSK-4320 criterion 1, REQ-2952: `feat` is a conventional type, and the
    // profile didn't declare it.
    let dir = spec_and_chore_only();
    let (done, stdout) = check(&dir.0, "feat: add a verb\n");
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert!(
        stdout.contains("declared type: `feat` isn't a declared type (spec, chore)"),
        "{stdout}"
    );
}

#[test]
fn a_declared_type_passes_the_declared_type_check() {
    // TSK-4320 criterion 2, REQ-2952.
    let dir = spec_and_chore_only();
    let (done, stdout) = check(&dir.0, "spec: state the profile\n");
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(!stdout.contains("declared type"), "{stdout}");
}

#[test]
fn the_scm_source_holds_no_list_of_conventional_types() {
    // TSK-4320 criterion 3, REQ-2952: a built-in list would accept a type the
    // repository never declared.
    let source = include_str!("../src/scm.rs");
    let program = source
        .split("#[cfg(test)]\nmod tests")
        .next()
        .expect("the source has a program part");
    let conventional = [
        "feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore",
        "revert", "spec",
    ];
    let found: Vec<&str> = conventional
        .iter()
        .copied()
        .filter(|name| program.contains(&format!("\"{name}\"")))
        .collect();
    assert!(
        program.contains("declared type"),
        "the search stopped before the type check"
    );
    assert!(
        found.is_empty(),
        "the program names conventional types as literals: {found:?}"
    );
}
