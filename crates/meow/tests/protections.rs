// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-github protections` reports which of six protections are in force on
//! the declared trunk, reading through the request layer and writing nothing
//! (TSK-4640, REQ-2194, SPC-1080 "Reporting the trunk's protections").

#![cfg(feature = "github")]

use serde_json::{Value, json};
use std::path::PathBuf;
use std::process::{Command, Output};

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
            "meow-protections-{name}-{}-{stamp}-{count}",
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

/// A stand-in `gh` that answers `gh api <endpoint> --include` from the
/// answers file by the endpoint's path, and logs every call's arguments.
const STAND_IN: &str = r#"#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
with open(os.environ["GH_LOG"], "a") as log:
    log.write(json.dumps(args) + "\n")
path = args[1].split("?")[0]
answer = json.load(open(os.environ["GH_ANSWERS"])).get(path, {"status": 404, "body": {"message": "Not Found"}})
status, body = answer["status"], answer["body"]
print(f"HTTP/2.0 {status} X")
print("Date: Tue, 29 Sep 2026 14:30:37 GMT")
print()
print(json.dumps(body))
if status >= 400:
    print(f"gh: {body.get('message', '')} (HTTP {status})", file=sys.stderr)
    sys.exit(1)
"#;

const PROTECTION: &str = "repos/o/r/branches/main/protection";
const RULES: &str = "repos/o/r/rules/branches/main";

/// Runs `paw github protections o/r` in a repository whose profile holds
/// `profile`, against the stand-in answering `answers`, and returns the
/// output and the arguments of every call the stand-in received.
fn protections(profile: &str, answers: Value) -> (Output, Vec<Vec<String>>) {
    let dir = Dir::new("run");
    let bin = dir.0.join("bin");
    std::fs::create_dir_all(&bin).unwrap();
    let gh = bin.join("gh");
    std::fs::write(&gh, STAND_IN).unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&gh, std::fs::Permissions::from_mode(0o755)).unwrap();
    }
    std::fs::create_dir_all(dir.0.join(".meowpaw")).unwrap();
    std::fs::write(dir.0.join(".meowpaw/profile.toml"), profile).unwrap();
    std::fs::write(dir.0.join("answers.json"), answers.to_string()).unwrap();
    let log = dir.0.join("log");
    let path = format!(
        "{}:{}",
        bin.display(),
        std::env::var("PATH").unwrap_or_default()
    );
    let output = Command::new(env!("CARGO_BIN_EXE_paw"))
        .args(["github", "protections", "o/r"])
        .current_dir(&dir.0)
        .env("PATH", path)
        .env("GH_ANSWERS", dir.0.join("answers.json"))
        .env("GH_LOG", &log)
        .env("GIT_CEILING_DIRECTORIES", dir.0.parent().unwrap())
        .env_remove("GH_TOKEN")
        .env_remove("GITHUB_TOKEN")
        .env_remove("GITHUB_ACTIONS")
        .output()
        .unwrap();
    let calls = std::fs::read_to_string(&log)
        .unwrap_or_default()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    (output, calls)
}

const TRUNK: &str = "[git]\ntrunk = \"main\"\n";

/// The report's lines between its profile line and its four budget lines,
/// after checking the lines around them.
fn report(output: &Output) -> Vec<String> {
    let text = String::from_utf8_lossy(&output.stdout).to_string();
    let lines: Vec<String> = text.lines().map(str::to_string).collect();
    assert!(lines.len() >= 6, "{text}");
    assert_eq!(lines[0], "credential: gh's stored credential", "{text}");
    assert_eq!(
        lines[1], "meow-github protections: profile: parsed",
        "{text}"
    );
    let budget = &lines[lines.len() - 4..];
    for (line, first) in budget.iter().zip([
        "primary requests:",
        "secondary points:",
        "content creation:",
        "spacing:",
    ]) {
        assert!(line.starts_with(first), "{text}");
    }
    lines[2..lines.len() - 4].to_vec()
}

/// A classic protection answer with each setting as named.
fn classic(force_pushes: bool, deletions: bool, signatures: bool, linear: bool) -> Value {
    json!({
        "url": "https://api.github.com/repos/o/r/branches/main/protection",
        "allow_force_pushes": {"enabled": force_pushes},
        "allow_deletions": {"enabled": deletions},
        "required_signatures": {"url": "x", "enabled": signatures},
        "required_linear_history": {"enabled": linear},
        "enforce_admins": {"enabled": false},
    })
}

/// TSK-4640 criterion 4, REQ-2194: the report writes nothing, so every call
/// it sends is a read.
fn every_call_reads(calls: &[Vec<String>]) {
    assert!(!calls.is_empty());
    for call in calls {
        assert_eq!(call[0], "api", "{call:?}");
        assert!(
            !call
                .iter()
                .any(|a| a == "-X" || a == "--method" || a == "-f" || a == "-F"),
            "{call:?} isn't a GET"
        );
    }
}

/// TSK-4640 criterion 1, REQ-2194: a protection that blocks force pushes and
/// requires signed commits prints the six lines in order, those two in force
/// and the other four absent, and exits 0.
#[test]
fn a_classic_protection_reports_each_of_the_six() {
    let (output, calls) = protections(
        TRUNK,
        json!({
            PROTECTION: {"status": 200, "body": classic(false, true, true, false)},
            RULES: {"status": 200, "body": []},
        }),
    );
    assert_eq!(
        report(&output),
        [
            "force pushes blocked: in force",
            "deletion blocked: absent",
            "required reviews: absent",
            "required checks: absent",
            "signed commits: in force",
            "linear history: absent",
        ]
    );
    assert_eq!(output.status.code(), Some(0));
    every_call_reads(&calls);
    let endpoints: Vec<&str> = calls
        .iter()
        .map(|c| c[1].split('?').next().unwrap())
        .collect();
    assert_eq!(endpoints, [PROTECTION, RULES]);
}

/// TSK-4640 criterion 2, REQ-2194: a 404 for the protection makes every
/// classic protection absent, and a ruleset requiring linear history puts
/// that one in force.
#[test]
fn a_ruleset_counts_where_the_branch_has_no_protection() {
    let (output, calls) = protections(
        TRUNK,
        json!({
            PROTECTION: {"status": 404, "body": {"message": "Branch not protected"}},
            RULES: {"status": 200, "body": [
                {"type": "required_linear_history", "ruleset_source_type": "Repository",
                 "ruleset_source": "o/r", "ruleset_id": 1}
            ]},
        }),
    );
    assert_eq!(
        report(&output),
        [
            "force pushes blocked: absent",
            "deletion blocked: absent",
            "required reviews: absent",
            "required checks: absent",
            "signed commits: absent",
            "linear history: in force",
        ]
    );
    assert_eq!(output.status.code(), Some(0));
    every_call_reads(&calls);
}

/// The rules of every kind a ruleset can set, each counted as in force.
#[test]
fn every_ruleset_rule_counts() {
    let rules: Vec<Value> = [
        "non_fast_forward",
        "deletion",
        "pull_request",
        "required_status_checks",
        "required_signatures",
        "required_linear_history",
    ]
    .iter()
    .map(|t| json!({"type": t}))
    .collect();
    let (output, calls) = protections(
        TRUNK,
        json!({
            PROTECTION: {"status": 404, "body": {"message": "Branch not protected"}},
            RULES: {"status": 200, "body": rules},
        }),
    );
    assert!(
        report(&output).iter().all(|l| l.ends_with(": in force")),
        "{output:?}"
    );
    assert_eq!(output.status.code(), Some(0));
    every_call_reads(&calls);
}

/// TSK-4640 criterion 3, REQ-2194: a 403 for the rules names each protection
/// the report couldn't read as unread, none as absent, and exits 3. A
/// protection the classic answer shows in force stays in force.
#[test]
fn a_refused_read_leaves_each_protection_it_holds_unread() {
    for (answer, first) in [
        (
            json!({"status": 404, "body": {"message": "Branch not protected"}}),
            "unread",
        ),
        (
            json!({"status": 200, "body": classic(false, true, false, false)}),
            "in force",
        ),
    ] {
        let (output, calls) = protections(
            TRUNK,
            json!({
                PROTECTION: answer,
                RULES: {"status": 403, "body": {"message": "Resource not accessible by integration"}},
            }),
        );
        let lines = report(&output);
        assert_eq!(
            lines,
            [
                "refused: GET repos/o/r/rules/branches/main?per_page=100 needs a permission: GitHub named no permission and said \"Resource not accessible by integration\"".to_string(),
                format!("force pushes blocked: {first}"),
                "deletion blocked: unread".to_string(),
                "required reviews: unread".to_string(),
                "required checks: unread".to_string(),
                "signed commits: unread".to_string(),
                "linear history: unread".to_string(),
            ],
            "{output:?}"
        );
        assert!(!lines.iter().any(|l| l.ends_with(": absent")));
        assert_eq!(output.status.code(), Some(3));
        every_call_reads(&calls);
    }
}

/// SPC-1080: where no trunk is declared, the report says so, sends nothing
/// and exits 3.
#[test]
fn no_trunk_is_reported_and_reads_nothing() {
    let (output, calls) = protections("", json!({}));
    let text = String::from_utf8_lossy(&output.stdout);
    assert!(
        text.lines().any(|l| l
            == "meow-github protections: no trunk declared under [git] in .meowpaw/profile.toml, so no protection is read; declare `[git] trunk`"),
        "{text}"
    );
    assert_eq!(output.status.code(), Some(3));
    assert!(calls.is_empty(), "{calls:?}");
}
