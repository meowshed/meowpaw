// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The revision counter `meow-checks` keeps per work tree, advanced by every
//! tool use, a failed one included (TSK-4910, SPC-1240 "The revision
//! counter", SPC-1040).

#![cfg(feature = "verbs")]

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
        let path = std::env::temp_dir().join(format!(
            "meow-revision-{name}-{}-{stamp}",
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

/// A repository whose profile binds the lint stage to a command that passes,
/// with one commit, and a state directory beside it.
fn fixture(name: &str) -> (Dir, PathBuf) {
    let dir = Dir::new(name);
    git(&dir.0, &["init", "-q"]);
    std::fs::create_dir_all(dir.0.join(".meowpaw")).unwrap();
    std::fs::write(
        dir.0.join(".meowpaw/profile.toml"),
        "[stages]\nlint = \"true\"\n",
    )
    .unwrap();
    git(&dir.0, &["add", "-A"]);
    git(
        &dir.0,
        &[
            "-c",
            "user.email=a@b",
            "-c",
            "user.name=n",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "-m",
            "chore: seed",
        ],
    );
    let state = dir.0.join(".state");
    std::fs::create_dir_all(&state).unwrap();
    (dir, state)
}

fn meow(dir: &Path, state: &Path, off: bool, args: &[&str], input: &str) -> Output {
    let mut command = Command::new(env!("CARGO_BIN_EXE_meow"));
    command
        .args(args)
        .current_dir(dir)
        .env("XDG_STATE_HOME", state)
        .env("XDG_RUNTIME_DIR", state)
        .env("MEOWPAW_STATE_DIR", state)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    if off {
        command.env("MEOWPAW_STATE", "off");
    }
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}

const FAILED: &str = r#"{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","tool_input":{"command":"false"}}"#;
const USED: &str =
    r#"{"hook_event_name":"PostToolUse","tool_name":"Edit","tool_input":{"file_path":"a"}}"#;

fn revision(dir: &Path, state: &Path) -> u64 {
    let state_report = meow(dir, state, false, &["verbs", "state"], "");
    String::from_utf8_lossy(&state_report.stdout)
        .lines()
        .find_map(|line| line.strip_prefix("revision: "))
        .unwrap_or_else(|| panic!("verbs state prints no `revision:` line: {state_report:?}"))
        .trim()
        .parse()
        .unwrap()
}

/// REQ-2728: a failed tool use and a successful one each add one.
#[test]
fn a_failed_tool_use_advances_the_counter_and_so_does_a_successful_one() {
    let (dir, state) = fixture("advance");
    for _ in 0..4 {
        let done = meow(&dir.0, &state, false, &["verbs", "revision"], USED);
        assert!(done.status.success(), "{done:?}");
    }
    assert_eq!(revision(&dir.0, &state), 4);
    let failed = meow(&dir.0, &state, false, &["verbs", "revision"], FAILED);
    assert!(failed.status.success(), "{failed:?}");
    assert_eq!(revision(&dir.0, &state), 5);
    let used = meow(&dir.0, &state, false, &["verbs", "revision"], USED);
    assert!(used.status.success(), "{used:?}");
    assert_eq!(revision(&dir.0, &state), 6);
}

/// REQ-2728, REQ-2724: the subcommand prints nothing and writes nothing of
/// its input.
#[test]
fn the_counter_holds_a_count_and_nothing_the_hook_read() {
    let (dir, state) = fixture("input");
    let marker = r#"{"tool_name":"Bash","tool_input":{"command":"echo MARKER-8c1f"}}"#;
    let done = meow(&dir.0, &state, false, &["verbs", "revision"], marker);
    assert!(done.status.success(), "{done:?}");
    assert!(done.stdout.is_empty(), "{done:?}");
    fn walk(dir: &Path, out: &mut Vec<PathBuf>) {
        for entry in std::fs::read_dir(dir).unwrap() {
            let path = entry.unwrap().path();
            if path.is_dir() {
                walk(&path, out);
            } else {
                out.push(path);
            }
        }
    }
    let mut files = Vec::new();
    walk(&state, &mut files);
    assert!(
        !files.is_empty(),
        "the counter wrote no file under the state directory"
    );
    for file in files {
        let text = String::from_utf8_lossy(&std::fs::read(&file).unwrap()).to_string();
        assert!(
            !text.contains("MARKER-8c1f"),
            "{} holds the hook's input",
            file.display()
        );
    }
}

/// REQ-2728: a record carries the counter at its run, and `evidence` shows it
/// beside the current one while the tree id alone decides whether it is current.
#[test]
fn evidence_prints_the_records_revision_and_the_current_one() {
    let (dir, state) = fixture("evidence");
    for _ in 0..5 {
        meow(&dir.0, &state, false, &["verbs", "revision"], USED);
    }
    let run = meow(&dir.0, &state, false, &["verbs", "run", "lint"], "");
    assert!(run.status.success(), "{run:?}");
    for _ in 0..2 {
        meow(&dir.0, &state, false, &["verbs", "revision"], FAILED);
    }
    let evidence = meow(&dir.0, &state, false, &["verbs", "evidence", "lint"], "");
    let text = String::from_utf8_lossy(&evidence.stdout).to_string();
    assert!(evidence.status.success(), "{evidence:?}");
    assert!(
        text.contains("revision 5, now 7"),
        "evidence names no revision pair: {text}"
    );
    assert!(
        text.contains("current at tree"),
        "the tree id decides: {text}"
    );
}

/// REQ-2728, REQ-2960: with state writing off the subcommand writes nothing.
#[test]
fn state_off_writes_nothing_and_exits_zero() {
    let (dir, state) = fixture("off");
    let done = meow(&dir.0, &state, true, &["verbs", "revision"], USED);
    assert_eq!(done.status.code(), Some(0), "{done:?}");
    assert!(std::fs::read_dir(&state).unwrap().next().is_none());
}
