// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! This repository's record sits in the layout the harness gives its users, and
//! a requirement names one of the four kinds of check (TSK-5035, ADR-2690,
//! SPC-1090 "This repository's own work", SPC-1070).
//!
//! The layout is read from `plugins/meow-flow/lib/layout.toml` at run time and
//! never from a list of the test's own, so the test moves with the layout.

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
        let path =
            std::env::temp_dir().join(format!("meow-layout-{name}-{}-{stamp}", std::process::id()));
        std::fs::create_dir_all(&path).unwrap();
        Dir(path)
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn layout_path() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/lib/layout.toml")
}

fn record_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../project")
}

/// Each kind's directory with its identifier prefix, each file a kind names,
/// and the name an index file carries.
struct Layout {
    directories: Vec<(String, String)>,
    files: Vec<String>,
    index_name: String,
}

fn read_layout() -> Layout {
    let text = std::fs::read_to_string(layout_path()).expect("the layout file is readable");
    let data: toml::Table = text.parse().expect("the layout parses");
    let mut directories = Vec::new();
    let mut files = Vec::new();
    for kind in data["kind"].as_array().expect("the layout lists kinds") {
        let kind = kind.as_table().expect("a kind is a table");
        if let Some(file) = kind.get("file").and_then(|v| v.as_str()) {
            files.push(file.to_string());
        }
        if let (Some(dir), Some(prefix)) = (
            kind.get("dir").and_then(|v| v.as_str()),
            kind.get("prefix").and_then(|v| v.as_str()),
        ) {
            directories.push((dir.to_string(), prefix.to_string()));
        }
    }
    let index_name = data
        .get("index_name")
        .and_then(|v| v.as_str())
        .unwrap_or("README.md")
        .to_string();
    Layout {
        directories,
        files,
        index_name,
    }
}

fn files_under(dir: &Path, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir)
        .expect("the record is readable")
        .flatten()
    {
        let path = entry.path();
        if path.is_dir() {
            files_under(&path, out);
        } else {
            out.push(path);
        }
    }
}

/// Each file under `root` that no kind of the layout gives a place: one that is
/// not a kind's own file, not the root index, and not an index or a record
/// named for the kind's prefix in the kind's directory.
fn outside_the_layout(layout: &Layout, root: &Path) -> Vec<String> {
    let mut files = Vec::new();
    files_under(root, &mut files);
    files.sort();
    let mut found = Vec::new();
    for path in files {
        let relative = path
            .strip_prefix(root)
            .unwrap()
            .to_string_lossy()
            .replace('\\', "/");
        let placed = layout.files.contains(&relative)
            || relative == layout.index_name
            || layout.directories.iter().any(|(dir, prefix)| {
                relative
                    .strip_prefix(&format!("{dir}/"))
                    .is_some_and(|name| {
                        name == layout.index_name
                            || (name.starts_with(&format!("{prefix}-")) && name.ends_with(".md"))
                    })
            });
        if !placed {
            found.push(relative);
        }
    }
    found
}

fn copy(from: &Path, to: &Path) {
    std::fs::create_dir_all(to).unwrap();
    for entry in std::fs::read_dir(from).unwrap().flatten() {
        let target = to.join(entry.file_name());
        if entry.path().is_dir() {
            copy(&entry.path(), &target);
        } else {
            std::fs::copy(entry.path(), target).unwrap();
        }
    }
}

#[test]
fn a_file_in_no_kinds_directory_is_named() {
    // TSK-5035 criterion 1, REQ-1668, REQ-1660: a copy of the record with one
    // file added under the root in no kind's directory fails, naming it.
    let layout = read_layout();
    let copied = Dir::new("copy");
    copy(&record_root(), &copied.0);
    std::fs::create_dir_all(copied.0.join("notes")).unwrap();
    std::fs::write(copied.0.join("notes/stray.md"), "A note.\n").unwrap();
    std::fs::write(copied.0.join("specs/notes.md"), "Not a specification.\n").unwrap();
    assert_eq!(
        outside_the_layout(&layout, &copied.0),
        vec!["notes/stray.md".to_string(), "specs/notes.md".to_string()]
    );
}

#[test]
fn this_repositorys_record_is_inside_the_layout() {
    // TSK-5035 criterion 2, REQ-1668: the record as it stands has no file
    // outside the layout, and the walk read files.
    let mut files = Vec::new();
    files_under(&record_root(), &mut files);
    assert!(!files.is_empty(), "the record root holds no file to check");
    assert_eq!(
        outside_the_layout(&read_layout(), &record_root()),
        Vec::<String>::new()
    );
}

fn paw(dir: &Path, args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_paw"))
        .arg("record")
        .args(args)
        .current_dir(dir)
        .env("MEOW_LAYOUT", layout_path())
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .expect("paw runs")
}

fn requirement_with(verification: &str) -> Dir {
    let dir = Dir::new("verification");
    std::fs::create_dir_all(dir.0.join(".meowpaw")).unwrap();
    std::fs::write(
        dir.0.join(".meowpaw/profile.toml"),
        "[record]\nroot = \"project\"\n",
    )
    .unwrap();
    std::fs::create_dir_all(dir.0.join("project/requirements")).unwrap();
    std::fs::write(
        dir.0.join("project/requirements/REQ-0001-an-obligation.md"),
        format!(
            "---\nid: REQ-0001\nartifact: requirement\ntopic: a\nclass: functional\nstatus: approved\nrevised: 2026-01-01\nverification: {verification}\n---\n\n# REQ-0001\n\nThe harness MUST do it.\n"
        ),
    )
    .unwrap();
    dir
}

#[test]
fn a_verification_outside_the_four_kinds_fails_the_check() {
    // TSK-5035 criterion 3, REQ-1662: `manual` is a fifth kind, so the check
    // reports it and exits 1; each of the four passes. The program holds the
    // rule in its `rules` check, which reads the requirement's front matter,
    // and `paw check` with no name runs that check among the others.
    let manual = requirement_with("manual");
    let done = paw(&manual.0, &["check", "rules"]);
    let said = String::from_utf8_lossy(&done.stdout).to_string();
    assert_eq!(done.status.code(), Some(1), "{said}");
    assert!(
        said.contains(
            "verification manual is not one of static, behavioural, evaluation and judgement"
        ),
        "{said}"
    );
    let whole = paw(&manual.0, &["check"]);
    assert_eq!(whole.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&whole.stdout).contains("verification manual is not one of"));
    for kind in ["static", "behavioural", "evaluation", "judgement"] {
        let allowed = requirement_with(kind);
        let done = paw(&allowed.0, &["check", "rules"]);
        let said = String::from_utf8_lossy(&done.stdout).to_string();
        assert!(!said.contains("is not one of static"), "{kind}: {said}");
    }
}
