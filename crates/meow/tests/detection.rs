// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Each pack activates for each directory holding its marker, and its report
//! names that directory, and the part where one is declared (TSK-5060,
//! SPC-1190 "Detection").

#![cfg(all(feature = "mise", feature = "gotask", feature = "markdown"))]

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
        let path = std::env::temp_dir().join(format!(
            "meow-detection-{name}-{}-{stamp}",
            std::process::id()
        ));
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

/// A git repository holding `files`, each tracked, and a directory of
/// stand-in tools, each a shell script.
fn fixture(name: &str, files: &[(&str, &str)], tools: &[(&str, &str)]) -> (Dir, Dir) {
    let dir = Dir::new(name);
    let bin = Dir::new(&format!("{name}-bin"));
    for (file, text) in files {
        write(&dir.0, file, text);
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

/// `paw <args>` in `dir`, with the stand-in tools first on `PATH`.
fn paw(dir: &Path, bin: &Path, args: &[&str]) -> (Output, String) {
    let path = format!("{}:/usr/bin:/bin", bin.display());
    let done = Command::new(env!("CARGO_BIN_EXE_paw"))
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

fn scopes(stdout: &str) -> Vec<&str> {
    stdout
        .lines()
        .filter(|line| line.starts_with("scope:"))
        .collect()
}

const MISE: &str = "case \"$1\" in --version) echo '2026.9.11 macos-arm64';; tasks) echo '[]';; config) echo '[]';; *) exit 1;; esac\n";

/// TSK-5060 criterion 1, REQ-3048, REQ-0133: a `mise.toml` in `a/` and none
/// at the root makes `meow-mise status` report for `a/` alone.
#[test]
fn mise_reports_for_the_directory_holding_its_marker_alone() {
    let (dir, bin) = fixture(
        "mise",
        &[
            ("a/mise.toml", "[tasks.test]\nrun = \"true\"\n"),
            ("README.md", "# r\n"),
        ],
        &[("mise", MISE)],
    );
    let (done, stdout) = paw(&dir.0, &bin.0, &["mise", "status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert_eq!(scopes(&stdout), ["scope: a"], "{stdout}");
    assert!(
        stdout.lines().any(|l| l == "marker: a/mise.toml"),
        "{stdout}"
    );
}

/// TSK-5060 criterion 1, REQ-0133: a tree with no tracked marker starts no
/// mise and names no directory.
#[test]
fn mise_with_no_marker_reports_no_directory() {
    let (dir, bin) = fixture(
        "mise-none",
        &[("README.md", "# r\n")],
        &[("mise", "touch \"$HOME/ran\"\n")],
    );
    let (done, stdout) = paw(&dir.0, &bin.0, &["mise", "status"]);
    assert_eq!(done.status.code(), Some(3), "{stdout}");
    assert!(scopes(&stdout).is_empty(), "{stdout}");
    assert!(!bin.0.join("ran").exists(), "mise started");
}

/// TSK-5060 criterion 2, REQ-0133: Markdown markers in two directories make
/// `meow-markdown status` report once for each, naming it.
#[test]
fn markdown_reports_once_per_directory() {
    let (dir, bin) = fixture(
        "markdown",
        &[
            (".meowpaw/profile.toml", "[markdown]\ntarget = \"github\"\n"),
            ("README.md", "# r\n"),
            ("docs/.markdownlint.yaml", "default: true\n"),
            ("docs/guide.md", "# g\n"),
            ("site/.markdownlint-cli2.yaml", "config:\n  MD013: false\n"),
        ],
        &[],
    );
    let (done, stdout) = paw(&dir.0, &bin.0, &["markdown", "status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert_eq!(scopes(&stdout), ["scope: docs", "scope: site"], "{stdout}");
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with("marker: docs/.markdownlint.yaml")),
        "{stdout}"
    );
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with("marker: site/.markdownlint-cli2.yaml")),
        "{stdout}"
    );
}

/// TSK-5060 criterion 3, REQ-3048: a `Taskfile.yml` in one of two declared
/// parts makes `meow-gotask status` name the part and its directory.
#[test]
fn gotask_names_the_part_and_its_directory() {
    let (dir, bin) = fixture(
        "gotask",
        &[
            (
                ".meowpaw/profile.toml",
                "[parts]\nsite = \"site\"\nengine = \"engine\"\n",
            ),
            ("site/Taskfile.yml", "version: '3'\ntasks: {}\n"),
            ("engine/README.md", "# e\n"),
        ],
        &[(
            "task",
            "case \"$1\" in --version) echo 'Task version: v3.53.1';; *) echo '{\"tasks\": []}';; esac\n",
        )],
    );
    let (done, stdout) = paw(&dir.0, &bin.0, &["gotask", "status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert_eq!(scopes(&stdout), ["scope: site site"], "{stdout}");
    assert!(
        stdout.lines().any(|l| l == "marker: site/Taskfile.yml"),
        "{stdout}"
    );
}
