// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! In an attended session, every push, merge, release, issue write and
//! governance change asks the person, once for each invocation, and a read,
//! a repository-local write or an unattended run gains no prompt (TSK-5150,
//! REQ-1420, REQ-1422, ADR-2750).

#![cfg(all(feature = "git", feature = "github", feature = "loop"))]

use serde_json::{Value, json};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        static COUNT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
        let count = COUNT.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "meow-irreversible-{name}-{}-{stamp}-{count}",
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

/// A repository with a profile declaring an unattended posture, one commit,
/// and a state directory of its own.
fn fixture(name: &str) -> (Dir, PathBuf) {
    let dir = Dir::new(name);
    git(&dir.0, &["init", "-q", "--template="]);
    std::fs::create_dir_all(dir.0.join(".meowpaw")).unwrap();
    std::fs::write(
        dir.0.join(".meowpaw/profile.toml"),
        "[stages]\nformat = \"true\"\nlint = \"true\"\ncheck = \"true\"\ntest = \"true\"\nbuild = \"true\"\n\n\
         [git]\ntrunk = \"main\"\n\n\
         [unattended]\npermission_mode = \"acceptEdits\"\ngates = [\"implement\"]\nrelease = false\n",
    )
    .unwrap();
    // An empty record, which a run reads its open counts from.
    std::fs::create_dir_all(dir.0.join("project")).unwrap();
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

/// `paw <args>` in `dir`, given `input` on standard input, with its standard
/// output.
fn paw(dir: &Path, state: &Path, args: &[&str], input: &str) -> (Option<i32>, String) {
    let mut child = Command::new(env!("CARGO_BIN_EXE_paw"))
        .args(args)
        .current_dir(dir)
        .env("XDG_STATE_HOME", state)
        .env("XDG_RUNTIME_DIR", state)
        .env("MEOWPAW_STATE_DIR", state)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .env(
            "MEOW_LAYOUT",
            concat!(
                env!("CARGO_MANIFEST_DIR"),
                "/../../plugins/meow-flow/lib/layout.toml"
            ),
        )
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    let out = child.wait_with_output().unwrap();
    (
        out.status.code(),
        String::from_utf8_lossy(&out.stdout).to_string(),
    )
}

/// A `PreToolUse` event for a Bash command in `dir`, in `mode`.
fn bash(dir: &Path, mode: &str, command: &str) -> String {
    json!({
        "hook_event_name": "PreToolUse",
        "session_id": "s1",
        "cwd": dir.display().to_string(),
        "permission_mode": mode,
        "tool_name": "Bash",
        "tool_input": {"command": command},
    })
    .to_string()
}

/// The guard each operation is asked about by: the unit and its subcommand.
fn guard_of(command: &str) -> (&'static str, &'static str) {
    if command.starts_with("git ") {
        ("git", "irreversible-guard")
    } else if command.contains("protection") || command.starts_with("gh secret") {
        ("github", "governance-guard")
    } else {
        ("github", "irreversible-guard")
    }
}

/// What every guard of the two units answers for `command`: the reason of
/// each `ask`, and a failure for any other answer.
fn asked(dir: &Path, state: &Path, mode: &str, command: &str) -> Vec<String> {
    let mut reasons = Vec::new();
    for (unit, subcommand) in [
        ("git", "irreversible-guard"),
        ("github", "irreversible-guard"),
        ("github", "governance-guard"),
    ] {
        let (code, out) = paw(dir, state, &[unit, subcommand], &bash(dir, mode, command));
        assert_eq!(code, Some(0), "{unit} {subcommand} on {command}: {out}");
        let out = out.trim();
        if out.is_empty() {
            continue;
        }
        let answer: Value = serde_json::from_str(out)
            .unwrap_or_else(|_| panic!("{unit} {subcommand} printed no JSON: {out}"));
        let hook = &answer["hookSpecificOutput"];
        assert_eq!(hook["hookEventName"], "PreToolUse", "{out}");
        assert_eq!(hook["permissionDecision"], "ask", "{out}");
        assert!(hook.get("updatedInput").is_none(), "{out}");
        reasons.push(format!(
            "{unit} {subcommand}: {}",
            hook["permissionDecisionReason"]
                .as_str()
                .unwrap_or_default()
        ));
    }
    reasons
}

/// One fixture command for each operation ADR-2750 names.
const IRREVERSIBLE: [&str; 13] = [
    "git push origin feat/x",
    "git -C sub push",
    "gh pr merge 12 --squash",
    "gh release create meow-x-v1.0.0 x.zip",
    "gh release upload meow-x-v1.0.0 x.zip",
    "gh issue create --title T --body B",
    "gh issue comment 4 --body B",
    "gh pr create --title T --body B",
    "gh api -X POST repos/o/r/issues -f title=T",
    "gh api repos/o/r/issues/4/comments -f body=B",
    "meow-github project EPC-0001",
    "gh api -X PUT repos/o/r/branches/main/protection",
    "gh secret set TOKEN",
];

/// TSK-5150 criterion 1, REQ-1420: in an attended session, each named
/// operation is asked about before it runs, by the guard of its unit, which
/// names the operation and not the command.
#[test]
fn each_irreversible_operation_asks_when_attended() {
    let (dir, state) = fixture("asks");
    for command in IRREVERSIBLE {
        let reasons = asked(&dir.0, &state, "default", command);
        assert_eq!(reasons.len(), 1, "{command}: {reasons:?}");
        let (unit, subcommand) = guard_of(command);
        assert!(
            reasons[0].starts_with(&format!("{unit} {subcommand}: meow-")),
            "{command}: {reasons:?}"
        );
        assert!(
            !reasons[0].contains("--body") && !reasons[0].contains("TOKEN"),
            "the reason names the operation and not the command: {reasons:?}"
        );
    }
}

/// TSK-5150 criterion 2, REQ-1422: approving one invocation approves nothing
/// after it, so the same command and the next one each ask again.
#[test]
fn a_second_invocation_asks_again() {
    let (dir, state) = fixture("again");
    for command in ["git push origin feat/x", "gh pr merge 12 --squash"] {
        for _ in 0..2 {
            assert_eq!(
                asked(&dir.0, &state, "default", command).len(),
                1,
                "{command}"
            );
        }
    }
    let entries = std::fs::read_dir(&state).unwrap().count();
    assert_eq!(entries, 0, "a guard keeps no approval between invocations");
}

/// TSK-5150 criterion 3, REQ-1420: a read and a repository-local write gain
/// no prompt from these guards.
#[test]
fn a_read_or_a_local_write_asks_nothing() {
    let (dir, state) = fixture("reads");
    for command in [
        "git status",
        "git log --oneline -3",
        "git commit -m 'feat: add a thing'",
        "git fetch origin",
        "gh pr view 12",
        "gh issue list",
        "gh release view meow-x-v1.0.0",
        "gh api repos/o/r/issues",
        "gh api -X GET repos/o/r/pulls",
        "meow-github project EPC-0001 --check",
        "meow-github history",
        "ls -la",
    ] {
        assert_eq!(
            asked(&dir.0, &state, "default", command),
            Vec::<String>::new(),
            "{command}"
        );
    }
}

/// TSK-5150 criterion 3, ADR-2750: an unattended run keeps the authority
/// ADR-2380 declares, so the attended rule adds no prompt to it: neither a
/// session in `dontAsk` nor one a `meow-loop` run holds.
#[test]
fn an_unattended_run_gains_no_prompt() {
    let (dir, state) = fixture("unattended");
    for command in [
        "git push origin feat/x",
        "gh pr merge 12",
        "gh issue create -t T -b B",
    ] {
        assert_eq!(
            asked(&dir.0, &state, "dontAsk", command)
                .iter()
                .filter(|r| r.contains("irreversible-guard"))
                .count(),
            0,
            "{command}"
        );
    }
    let start = json!({
        "hook_event_name": "UserPromptSubmit",
        "session_id": "s1",
        "cwd": dir.0.display().to_string(),
        "permission_mode": "acceptEdits",
        "prompt": "/meow-loop:run",
    })
    .to_string();
    let (code, out) = paw(&dir.0, &state, &["loop", "prompt"], &start);
    assert_eq!(code, Some(0), "{out}");
    assert!(!out.contains("unresolved"), "the run didn't start: {out}");
    for command in ["git push origin feat/x", "gh release create v1 x.zip"] {
        assert_eq!(
            asked(&dir.0, &state, "acceptEdits", command),
            Vec::<String>::new(),
            "{command}"
        );
    }
}

/// TSK-5150, REQ-1422: no file the harness ships requests a reusable
/// permission for a push, a merge, a release, an issue write or a
/// governance change, and both units register their guard on every Bash
/// call that can run one.
#[test]
fn nothing_shipped_requests_a_reusable_permission() {
    let repository = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let words = [
        "git push",
        "pr merge",
        "release",
        "issue",
        "gh api",
        "secret",
        "protection",
    ];
    let mut found = Vec::new();
    let mut stack = vec![repository.join("plugins"), repository.join("packages")];
    while let Some(dir) = stack.pop() {
        for entry in std::fs::read_dir(&dir).into_iter().flatten().flatten() {
            let path = entry.path();
            if path.is_dir() {
                if !path.ends_with("node_modules") && !path.ends_with("bin") {
                    stack.push(path);
                }
                continue;
            }
            if path.extension().is_none_or(|e| e != "json") {
                continue;
            }
            let Ok(value) =
                serde_json::from_str::<Value>(&std::fs::read_to_string(&path).unwrap_or_default())
            else {
                continue;
            };
            let allowed = value
                .pointer("/permissions/allow")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            for rule in allowed.iter().filter_map(Value::as_str) {
                if words.iter().any(|w| rule.contains(w)) {
                    found.push(format!("{}: {rule}", path.display()));
                }
            }
        }
    }
    assert!(found.is_empty(), "{found:?}");
    for (unit, guard) in [
        ("meow-git", "meow-git irreversible-guard"),
        ("meow-github", "meow-github irreversible-guard"),
    ] {
        let hooks =
            std::fs::read_to_string(repository.join(format!("plugins/{unit}/hooks/hooks.json")))
                .unwrap();
        assert!(hooks.contains(guard), "{unit} registers no {guard}");
    }
}
