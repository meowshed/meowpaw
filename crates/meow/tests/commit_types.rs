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

/// `paw scm check-message` in `dir`, given `message` on standard input.
fn check(dir: &Path, message: &str) -> (Output, String) {
    let mut child = Command::new(env!("CARGO_BIN_EXE_paw"))
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

fn with_profile(name: &str, text: &str) -> Dir {
    let dir = Dir::new(name);
    std::fs::write(dir.0.join(".meowpaw/profile.toml"), text).unwrap();
    dir
}

fn spec_and_chore_only() -> Dir {
    with_profile(
        "declared",
        "[commits.types]\nspec = \"none\"\nchore = \"none\"\n",
    )
}

const CONVENTIONAL: [&str; 12] = [
    "feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert",
    "spec",
];

#[test]
fn a_type_the_profile_doesnt_declare_fails_the_declared_type_check() {
    // TSK-4320 criterion 1, REQ-2952: `feat` is a conventional type, and the
    // profile didn't declare it.
    let dir = spec_and_chore_only();
    for subject in [
        "feat: add a verb",
        "feat(scm): add a verb",
        "feat!: add a verb",
    ] {
        let (done, stdout) = check(&dir.0, &format!("{subject}\n"));
        assert_eq!(done.status.code(), Some(1), "{subject}: {stdout}");
        assert!(
            stdout.contains("declared type: `feat` isn't a declared type (spec, chore)"),
            "{subject}: {stdout}"
        );
    }
}

#[test]
fn every_conventional_type_the_profile_leaves_out_fails_the_check() {
    // TSK-4320 criterion 3, REQ-2952: a list in any form, a split string or a
    // pattern included, would let one of these through.
    let dir = with_profile("leaves-out", "[commits.types]\nzzz = \"none\"\n");
    for name in CONVENTIONAL {
        let (done, stdout) = check(&dir.0, &format!("{name}: change\n"));
        assert_eq!(done.status.code(), Some(1), "{name}: {stdout}");
        assert!(
            stdout.contains(&format!(
                "declared type: `{name}` isn't a declared type (zzz)"
            )),
            "{name}: {stdout}"
        );
    }
}

#[test]
fn a_type_no_list_holds_passes_when_the_profile_declares_it() {
    // TSK-4320 criterion 2, REQ-2952: the declared list replaces any other, so
    // a name outside every conventional list is accepted.
    let dir = with_profile("unconventional", "[commits.types]\nzzz = \"none\"\n");
    let (done, stdout) = check(&dir.0, "zzz: change\n");
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(!stdout.contains("declared type"), "{stdout}");
}

#[test]
fn no_declared_type_means_no_fallback_list() {
    // TSK-4320, REQ-2952, SPC-1050: with nothing declared the type check
    // doesn't run, and no built-in list takes its place.
    let empty = with_profile("empty", "[commits]\nsubject_limit = 72\n[commits.types]\n");
    let malformed = with_profile("malformed", "[commits]\ntypes = \"feat\"\n");
    let invalid = with_profile("invalid", "[commits.types]\nzzz = \"huge\"\n");
    for (name, dir) in [
        ("empty", &empty),
        ("malformed", &malformed),
        ("invalid", &invalid),
    ] {
        let (_, stdout) = check(&dir.0, "yyy: change\n");
        assert!(!stdout.contains("declared type"), "{name}: {stdout}");
    }
    let (_, stdout) = check(&malformed.0, "yyy: change\n");
    assert!(stdout.contains("`types` isn't a table"), "{stdout}");
}

#[test]
fn a_declared_type_passes_the_declared_type_check() {
    // TSK-4320 criterion 2, REQ-2952.
    let dir = spec_and_chore_only();
    let (done, stdout) = check(&dir.0, "spec: state the profile\n");
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(!stdout.contains("declared type"), "{stdout}");
    // A conventional name that is capitalised isn't a type of any list.
    let (done, stdout) = check(&dir.0, "Spec: state the profile\n");
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert!(stdout.contains("subject form"), "{stdout}");
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
