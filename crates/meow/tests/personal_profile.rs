// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The personal profile, as `meow-checks` reads and writes it in a fixture
//! repository (TSK-4310, SPC-1040 "What `status` reports", SPC-1080).

#![cfg(feature = "verbs")]

use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

const PERSONAL: &str = ".meowpaw/profile.local.toml";

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "meow-personal-{name}-{}-{stamp}",
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

fn git(dir: &Path, args: &[&str]) -> Output {
    Command::new("git")
        .args(args)
        .current_dir(dir)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap()
}

/// A git repository at `dir`, so the root is the top of a working tree.
fn init(dir: &Path) {
    let done = git(dir, &["init", "-q", "--template="]);
    assert!(done.status.success(), "git init failed: {done:?}");
}

fn write(dir: &Path, path: &str, text: &str) {
    let file = dir.join(path);
    std::fs::create_dir_all(file.parent().unwrap()).unwrap();
    std::fs::write(file, text).unwrap();
}

/// `paw verbs <args>` in `dir`, with a state directory of the fixture's own.
fn checks(dir: &Path, state: &Path, args: &[&str]) -> (Output, String) {
    let done = Command::new(env!("CARGO_BIN_EXE_paw"))
        .arg("verbs")
        .args(args)
        .current_dir(dir)
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

fn line_for<'a>(stdout: &'a str, verb: &str) -> &'a str {
    stdout
        .lines()
        .find(|line| line.starts_with(&format!("{verb} ")))
        .unwrap_or_else(|| panic!("no line for {verb} in:\n{stdout}"))
}

#[test]
fn local_writes_the_personal_file_and_excludes_it() {
    // TSK-4310 criterion 1, REQ-2944.
    let root = Dir::new("write");
    let state = Dir::new("write-state");
    init(&root.0);
    let (done, stdout) = checks(&root.0, &state.0, &["local", "test", "mise run test"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let table: toml::Table = std::fs::read_to_string(root.0.join(PERSONAL))
        .expect("no personal profile was written")
        .parse()
        .unwrap();
    assert_eq!(
        table["stages"]["test"].as_str(),
        Some("mise run test"),
        "{table:?}"
    );
    let exclude = std::fs::read_to_string(root.0.join(".git/info/exclude")).unwrap();
    assert!(
        exclude.lines().any(|l| l == "/.meowpaw/profile.local.toml"),
        "{exclude}"
    );
    let porcelain = git(&root.0, &["status", "--porcelain"]);
    assert_eq!(
        String::from_utf8_lossy(&porcelain.stdout),
        "",
        "the personal file shows as a change"
    );
}

#[test]
fn a_second_local_call_excludes_the_file_once() {
    // TSK-4310 criterion 2, REQ-2944.
    let root = Dir::new("twice");
    let state = Dir::new("twice-state");
    init(&root.0);
    checks(&root.0, &state.0, &["local", "test", "mise run test"]);
    let (done, stdout) = checks(&root.0, &state.0, &["local", "lint", "mise run lint"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let exclude = std::fs::read_to_string(root.0.join(".git/info/exclude")).unwrap();
    let count = exclude
        .lines()
        .filter(|l| *l == "/.meowpaw/profile.local.toml")
        .count();
    assert_eq!(count, 1, "{exclude}");
    let table: toml::Table = std::fs::read_to_string(root.0.join(PERSONAL))
        .unwrap()
        .parse()
        .unwrap();
    assert_eq!(table["stages"]["test"].as_str(), Some("mise run test"));
    assert_eq!(table["stages"]["lint"].as_str(), Some("mise run lint"));
}

#[test]
fn a_personal_stage_replaces_the_shared_one_and_names_its_file() {
    // TSK-4310 criterion 3.
    let root = Dir::new("replace");
    let state = Dir::new("replace-state");
    init(&root.0);
    write(
        &root.0,
        ".meowpaw/profile.toml",
        "[stages]\ntest = \"true\"\n",
    );
    write(&root.0, PERSONAL, "[stages]\ntest = \"false\"\n");
    let (done, stdout) = checks(&root.0, &state.0, &["status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let line = line_for(&stdout, "test");
    assert!(line.contains("resolved"), "{line}");
    assert!(line.contains("false"), "{line}");
    assert!(!line.contains("true"), "{line}");
    assert!(line.contains(PERSONAL), "{line}");
}

#[test]
fn a_machine_path_in_the_personal_profile_is_unresolved_and_runs_nothing() {
    // TSK-4310 criterion 4, REQ-2946.
    let root = Dir::new("machine");
    let state = Dir::new("machine-state");
    init(&root.0);
    let command = "/Users/someone/bin/runner";
    write(
        &root.0,
        PERSONAL,
        &format!("[stages]\ntest = \"{command}\"\n"),
    );
    let (done, stdout) = checks(&root.0, &state.0, &["run", "test"]);
    assert_eq!(done.status.code(), Some(3), "{stdout}");
    assert!(
        stdout.contains("== test: unresolved (machine path:"),
        "{stdout}"
    );
    assert!(
        stdout.contains(command),
        "the report names no path:\n{stdout}"
    );
    assert!(stdout.contains("not run"), "{stdout}");

    // The same value in the shared profile resolves.
    let shared = Dir::new("machine-shared");
    init(&shared.0);
    write(
        &shared.0,
        ".meowpaw/profile.toml",
        &format!("[stages]\ntest = \"{command}\"\n"),
    );
    let (_, status) = checks(&shared.0, &state.0, &["status"]);
    assert!(
        line_for(&status, "test").contains("resolved    "),
        "{status}"
    );
    assert!(
        !line_for(&status, "test").contains("machine path"),
        "{status}"
    );
}

#[test]
fn a_personal_profile_with_a_commits_table_names_it_unknown() {
    // TSK-4310 criterion 5, ADR-2370.
    let root = Dir::new("unknown");
    let state = Dir::new("unknown-state");
    init(&root.0);
    write(
        &root.0,
        PERSONAL,
        "[commits]\nsubject_limit = 50\n[stages]\ntest = \"true\"\n",
    );
    let (done, stdout) = checks(&root.0, &state.0, &["status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with("unknown key: commits")),
        "{stdout}"
    );
    // The setting has no effect, and the stage it didn't touch still resolves.
    assert!(line_for(&stdout, "test").contains("resolved"), "{stdout}");
}

#[test]
fn local_outside_a_working_tree_writes_nothing_and_fails() {
    // TSK-4310 criterion 6.
    let root = Dir::new("nogit");
    let state = Dir::new("nogit-state");
    let (done, stdout) = checks(&root.0, &state.0, &["local", "test", "true"]);
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert!(
        !root.0.join(PERSONAL).exists(),
        "a personal file was written outside a working tree"
    );
    assert!(!root.0.join(".meowpaw").exists());
}

/// A personal profile holding `command` as its `test` stage, written as TOML
/// so the command's own quotes survive.
fn personal_with(dir: &Path, command: &str) {
    let mut stages = toml::Table::new();
    stages.insert("test".into(), toml::Value::String(command.into()));
    let mut table = toml::Table::new();
    table.insert("stages".into(), toml::Value::Table(stages));
    write(dir, PERSONAL, &toml::to_string(&table).unwrap());
}

#[test]
fn every_spelling_of_a_path_on_this_machine_is_a_machine_path() {
    // TSK-4310 criterion 4, REQ-2946: the symptom is the path, however the
    // command spells it.
    let root = Dir::new("spellings");
    let state = Dir::new("spellings-state");
    init(&root.0);
    let top = root.0.canonicalize().unwrap();
    let escaping = format!("{}/../elsewhere/runner", top.display());
    let flagged = [
        "~/bin/runner",
        "~someone/bin/runner",
        "\"/Users/someone/bin/runner\" --flag",
        "'~/bin/runner'",
        "$HOME/bin/runner",
        "${HOME}/bin/runner",
        "../tools/runner",
        escaping.as_str(),
    ];
    for command in flagged {
        personal_with(&root.0, command);
        let (_, stdout) = checks(&root.0, &state.0, &["status"]);
        assert!(
            line_for(&stdout, "test").contains("unresolved  machine path:"),
            "{command:?} wasn't a machine path:\n{stdout}"
        );
    }
    let inside = format!("{}/tools/runner --all", top.display());
    for command in [
        "./tools/runner",
        "tools/runner --all",
        "mise run test",
        &inside,
    ] {
        personal_with(&root.0, command);
        let (_, stdout) = checks(&root.0, &state.0, &["status"]);
        assert!(
            line_for(&stdout, "test").contains("resolved    "),
            "{command:?} was refused:\n{stdout}"
        );
    }
}

#[test]
fn local_refuses_a_machine_path_and_writes_nothing() {
    // TSK-4310 criterion 4, REQ-2946: the command that creates the file is
    // where the symptom is cheapest to report.
    let root = Dir::new("local-machine");
    let state = Dir::new("local-machine-state");
    init(&root.0);
    let (done, stdout) = checks(&root.0, &state.0, &["local", "test", "~/bin/runner"]);
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert!(!root.0.join(PERSONAL).exists());
    let exclude = std::fs::read_to_string(root.0.join(".git/info/exclude")).unwrap_or_default();
    assert!(!exclude.contains("profile.local.toml"), "{exclude}");
}

#[test]
fn an_unparseable_shared_profile_resolves_nothing_for_the_personal_one() {
    // TSK-4310, REQ-2948: nothing falls back, the personal file included.
    let root = Dir::new("shared-broken");
    let state = Dir::new("shared-broken-state");
    init(&root.0);
    write(&root.0, ".meowpaw/profile.toml", "[stages\n");
    write(&root.0, PERSONAL, "[stages]\ntest = \"true\"\n");
    let (_, stdout) = checks(&root.0, &state.0, &["status"]);
    assert!(
        line_for(&stdout, "test").contains("unresolved  profile unparseable:"),
        "{stdout}"
    );
}

#[test]
fn an_unparseable_personal_profile_is_named_and_leaves_the_shared_stage() {
    // TSK-4310: a personal file that doesn't parse is told apart from one
    // that holds nothing, and replaces nothing.
    let root = Dir::new("personal-broken");
    let state = Dir::new("personal-broken-state");
    init(&root.0);
    write(
        &root.0,
        ".meowpaw/profile.toml",
        "[stages]\ntest = \"true\"\n",
    );
    write(&root.0, PERSONAL, "[stages\n");
    let (done, stdout) = checks(&root.0, &state.0, &["status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(
        stdout
            .lines()
            .any(|l| l.starts_with("personal profile: unparseable")),
        "{stdout}"
    );
    assert!(line_for(&stdout, "test").contains("true"), "{stdout}");
    assert!(
        line_for(&stdout, "test").contains(".meowpaw/profile.toml"),
        "{stdout}"
    );
}

#[test]
fn local_keeps_the_stages_a_file_already_holds_under_verbs() {
    // TSK-4310: a personal file written before `[stages]` keeps its table.
    let root = Dir::new("old-table");
    let state = Dir::new("old-table-state");
    init(&root.0);
    write(&root.0, PERSONAL, "[verbs]\nlint = \"make lint\"\n");
    let (done, stdout) = checks(&root.0, &state.0, &["local", "test", "make test"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    let table: toml::Table = std::fs::read_to_string(root.0.join(PERSONAL))
        .unwrap()
        .parse()
        .unwrap();
    assert!(!table.contains_key("stages"), "{table:?}");
    assert_eq!(table["verbs"]["lint"].as_str(), Some("make lint"));
    assert_eq!(table["verbs"]["test"].as_str(), Some("make test"));
}

#[test]
fn local_refuses_a_symlinked_personal_file() {
    // TSK-4310, REQ-1563: it writes only the two files it names, and a link
    // would make it write a third.
    let root = Dir::new("symlink");
    let state = Dir::new("symlink-state");
    let outside = Dir::new("symlink-outside");
    init(&root.0);
    std::fs::create_dir_all(root.0.join(".meowpaw")).unwrap();
    let target = outside.0.join("elsewhere.toml");
    std::fs::write(&target, "").unwrap();
    std::os::unix::fs::symlink(&target, root.0.join(PERSONAL)).unwrap();
    let (done, stdout) = checks(&root.0, &state.0, &["local", "test", "make test"]);
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert_eq!(std::fs::read_to_string(&target).unwrap(), "");
}

#[test]
fn local_refuses_a_personal_file_the_repository_already_tracks() {
    // TSK-4310, REQ-2944: an exclusion does nothing for a tracked file, so
    // saying the file is excluded would be false.
    let root = Dir::new("tracked");
    let state = Dir::new("tracked-state");
    init(&root.0);
    write(&root.0, PERSONAL, "[stages]\ntest = \"true\"\n");
    assert!(git(&root.0, &["add", "-f", PERSONAL]).status.success());
    let before = std::fs::read_to_string(root.0.join(PERSONAL)).unwrap();
    let (done, stdout) = checks(&root.0, &state.0, &["local", "lint", "make lint"]);
    assert_eq!(done.status.code(), Some(1), "{stdout}");
    assert!(
        stdout.contains("tracked") || String::from_utf8_lossy(&done.stderr).contains("tracked")
    );
    assert_eq!(
        std::fs::read_to_string(root.0.join(PERSONAL)).unwrap(),
        before
    );
}

#[test]
fn local_excludes_the_file_from_a_linked_working_tree() {
    // TSK-4310 criterion 1, REQ-2944: in a linked working tree `.git` is a
    // file, and the exclusion still has to hide the personal file.
    let root = Dir::new("linked");
    let state = Dir::new("linked-state");
    init(&root.0);
    let commit = git(
        &root.0,
        &[
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.com",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "start",
        ],
    );
    assert!(commit.status.success(), "{commit:?}");
    let linked = root.0.join("linked");
    let added = git(
        &root.0,
        &[
            "worktree",
            "add",
            "-q",
            linked.to_str().unwrap(),
            "-b",
            "side",
        ],
    );
    assert!(added.status.success(), "{added:?}");
    let (done, stdout) = checks(&linked, &state.0, &["local", "test", "make test"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(linked.join(PERSONAL).is_file());
    let porcelain = git(&linked, &["status", "--porcelain"]);
    assert_eq!(String::from_utf8_lossy(&porcelain.stdout), "");
}
