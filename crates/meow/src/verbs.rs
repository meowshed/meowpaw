// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Resolve the five verbs from the repository's profile, report them, and run them.
//!
//! SPC-1040 states the behaviour. A verb resolves only from the command the
//! repository declares under `[verbs]` (REQ-0134), and a verb that resolves to
//! nothing is reported as unresolved and of which kind, never as passed
//! (REQ-0136, REQ-0154). `status` runs nothing (REQ-0150). `run` records each
//! verb's exact command, exit status and whole output (REQ-0144, REQ-0156), and
//! leads a failed verb with its last lines (REQ-0135). Each result goes into a
//! ledger bound to the tree it ran on, which `evidence` reads back (ADR-1480).

mod ledger;

use crate::profile::{self, Profile, PROFILE};
use serde_json::{json, Map, Value};
use std::io::Read;
use std::path::Path;
use std::process::{Command, Stdio};
use std::time::Instant;

const VERBS: [&str; 5] = ["format", "lint", "check", "test", "build"];
const TAIL: usize = 20;
const PASSED: u8 = 0;
const FAILED: u8 = 1;
const USAGE: u8 = 2;
const UNRESOLVED: u8 = 3;

enum Entry {
    Resolved { command: String },
    Unresolved { kind: &'static str, detail: String },
}

struct Report {
    path: String,
    state: &'static str,
    error: Option<String>,
    verbs: Vec<(&'static str, Entry)>,
    ignored: Vec<String>,
    notices: Vec<String>,
}

fn resolve(root: &Path) -> Report {
    let path = root.join(PROFILE).display().to_string();
    let every = |kind: &'static str, detail: String| {
        VERBS.iter().map(|verb| (*verb, Entry::Unresolved { kind, detail: detail.clone() })).collect()
    };
    match profile::read(root) {
        Profile::Absent => Report {
            path,
            state: "absent",
            error: None,
            verbs: every("no profile", format!("{PROFILE} doesn't exist; write it, declaring each verb under [verbs]")),
            ignored: Vec::new(),
            notices: Vec::new(),
        },
        Profile::Unparseable(error) => Report {
            path,
            state: "unparseable",
            error: Some(error.clone()),
            verbs: every("profile unparseable", error),
            ignored: Vec::new(),
            notices: Vec::new(),
        },
        Profile::Parsed(data) => {
            let mut ignored: Vec<String> =
                data.keys().filter(|key| *key != "verbs").map(|key| format!("[{key}]")).collect();
            let empty = toml::Table::new();
            let declared = match data.get("verbs") {
                None => &empty,
                Some(toml::Value::Table(table)) => table,
                Some(_) => {
                    return Report {
                        path,
                        state: "present",
                        error: None,
                        verbs: every("malformed declaration", "`verbs` isn't a table".to_string()),
                        ignored,
                        notices: Vec::new(),
                    };
                }
            };
            ignored.extend(
                declared
                    .keys()
                    .filter(|key| !VERBS.contains(&key.as_str()))
                    .map(|key| format!("verbs.{key}")),
            );
            let verbs = VERBS
                .iter()
                .map(|verb| {
                    let entry = match declared.get(*verb) {
                        None => Entry::Unresolved {
                            kind: "undeclared",
                            detail: "the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml".into(),
                        },
                        Some(toml::Value::String(command)) if !command.trim().is_empty() => {
                            Entry::Resolved { command: command.clone() }
                        }
                        Some(_) => Entry::Unresolved {
                            kind: "malformed declaration",
                            detail: "the value isn't one command; write one command as a string under [verbs]".into(),
                        },
                    };
                    (*verb, entry)
                })
                .collect();
            Report { path, state: "present", error: None, verbs, ignored, notices: Vec::new() }
        }
    }
}

fn status(root: &Path, as_json: bool) -> u8 {
    let report = resolve(root);
    if as_json {
        let mut verbs = Map::new();
        for (verb, entry) in &report.verbs {
            let value = match entry {
                Entry::Resolved { command } => json!({"state": "resolved", "command": command, "source": PROFILE}),
                Entry::Unresolved { kind, detail } => json!({"state": "unresolved", "kind": kind, "detail": detail}),
            };
            verbs.insert(verb.to_string(), value);
        }
        let profile = if report.state == "absent" { Value::Null } else { Value::from(report.path.clone()) };
        let out = json!({
            "profile": profile,
            "profile_state": report.state,
            "error": report.error,
            "verbs": verbs,
            "ignored": report.ignored,
            "notices": report.notices,
        });
        println!("{}", serde_json::to_string_pretty(&out).unwrap_or_default());
        return PASSED;
    }
    let where_ = if report.state == "absent" { format!("{} (absent)", report.path) } else { report.path.clone() };
    println!("meow-verbs status, profile {where_}\n");
    for (verb, entry) in &report.verbs {
        match entry {
            Entry::Resolved { command } => println!("{verb:<10} resolved    {command}   (from {PROFILE})"),
            Entry::Unresolved { kind, detail } => println!("{verb:<10} unresolved  {kind}: {detail}"),
        }
    }
    if !report.ignored.is_empty() {
        println!("\nNot read by meow-verbs: {}", report.ignored.join(", "));
    }
    for notice in &report.notices {
        println!("\nnotice: {notice}");
    }
    PASSED
}

/// Runs a declared command through the shell, with standard output and
/// standard error interleaved in the order they arrive.
fn execute(root: &Path, command: &str) -> (i32, String) {
    let (mut reader, writer) = match std::io::pipe() {
        Ok(pair) => pair,
        Err(error) => return (127, format!("meow: can't open a pipe: {error}\n")),
    };
    let mut shell = if cfg!(windows) {
        let mut shell = Command::new("cmd");
        shell.args(["/C", command]);
        shell
    } else {
        let mut shell = Command::new("/bin/sh");
        shell.args(["-c", command]);
        shell
    };
    let spawned = match writer.try_clone() {
        Ok(copy) => shell.current_dir(root).stdin(Stdio::null()).stdout(copy).stderr(writer).spawn(),
        Err(error) => return (127, format!("meow: can't share the pipe: {error}\n")),
    };
    drop(shell);
    let mut child = match spawned {
        Ok(child) => child,
        Err(error) => return (127, format!("meow: can't start the shell: {error}\n")),
    };
    let mut bytes = Vec::new();
    let _ = reader.read_to_end(&mut bytes);
    let code = match child.wait() {
        Ok(status) => status.code().unwrap_or_else(|| signal_code(status)),
        Err(_) => 127,
    };
    (code, String::from_utf8_lossy(&bytes).into_owned())
}

#[cfg(unix)]
fn signal_code(status: std::process::ExitStatus) -> i32 {
    use std::os::unix::process::ExitStatusExt;
    -status.signal().unwrap_or(0)
}

#[cfg(not(unix))]
fn signal_code(_: std::process::ExitStatus) -> i32 {
    -1
}

fn run(root: &Path, names: &[String]) -> u8 {
    if names.is_empty() {
        eprintln!("meow-verbs run: name the verbs to run, from: {}", VERBS.join(" "));
        return USAGE;
    }
    let unknown: Vec<&str> = names.iter().map(String::as_str).filter(|name| !VERBS.contains(name)).collect();
    if !unknown.is_empty() {
        eprintln!("meow-verbs run: {} isn't a verb; the five are {}", unknown.join(", "), VERBS.join(" "));
        return USAGE;
    }

    let report = resolve(root);
    for notice in &report.notices {
        println!("notice: {notice}\n");
    }
    let mut outcomes: Vec<(String, &str)> = Vec::new();
    let mut recorded: Vec<String> = Vec::new();
    let mut keep = |result: ledger::Result| match ledger::record(root, &result) {
        Ok(id) => recorded.push(format!("recorded: {} {id} at tree {}", result.verb, ledger::short(result.after))),
        Err(reason) => recorded.push(format!("not recorded: {} ({reason})", result.verb)),
    };
    for name in names {
        let entry = &report.verbs.iter().find(|(verb, _)| verb == name).expect("a known verb").1;
        let command = match entry {
            Entry::Unresolved { kind, detail } => {
                println!("== {name}: unresolved ({kind}: {detail}), not run\n");
                outcomes.push((name.clone(), "unresolved"));
                let tree = ledger::tree_id(root);
                keep(ledger::Result { verb: name, command: None, outcome: "unresolved", status: None, before: &tree, after: &tree, output: "" });
                continue;
            }
            Entry::Resolved { command } => command,
        };
        let before = ledger::tree_id(root);
        let started = Instant::now();
        let (code, output) = execute(root, command);
        let after = ledger::tree_id(root);
        let outcome = if code == 0 { "passed" } else { "failed" };
        keep(ledger::Result { verb: name, command: Some(command), outcome, status: Some(code), before: &before, after: &after, output: &output });
        let seconds = started.elapsed().as_secs_f64();
        println!("== {name}: `{command}`");
        if code == 0 {
            println!("passed, exit status 0 after {seconds:.1}s\n");
            outcomes.push((name.clone(), "passed"));
        } else {
            let lines: Vec<&str> = output.trim_end_matches('\n').lines().collect();
            let shown = lines.len().min(TAIL);
            println!("failed, exit status {code} after {seconds:.1}s; the last {shown} lines of its output:");
            println!("{}", lines[lines.len() - shown..].join("\n"));
            println!();
            outcomes.push((name.clone(), "failed"));
        }
        println!("-- whole output of {name}:");
        print!("{output}");
        if !output.is_empty() && !output.ends_with('\n') {
            println!();
        }
        println!("-- end of {name}\n");
    }

    let summary: Vec<String> = outcomes.iter().map(|(verb, result)| format!("{verb} {result}")).collect();
    println!("summary: {}", summary.join(", "));
    for line in &recorded {
        println!("{line}");
    }
    if outcomes.iter().any(|(_, result)| *result == "failed") {
        FAILED
    } else if outcomes.iter().any(|(_, result)| *result == "unresolved") {
        UNRESOLVED
    } else {
        PASSED
    }
}

/// Whether each verb's latest recorded result holds for the tree as it is
/// now: 0 when every one passed on it, 1 when one failed, went stale or
/// changed during its run, and 3 when one has no record, was unresolved or is
/// bound to no tree (REQ-0146, REQ-0148).
fn evidence(root: &Path, names: &[String]) -> u8 {
    let unknown: Vec<&str> = names.iter().map(String::as_str).filter(|name| !VERBS.contains(name)).collect();
    if !unknown.is_empty() {
        eprintln!("meow-verbs evidence: {} isn't a verb; the five are {}", unknown.join(", "), VERBS.join(" "));
        return USAGE;
    }
    let records = ledger::records(root);
    let text = |record: &Value, key: &str| record.get(key).and_then(Value::as_str).unwrap_or("").to_string();
    let wanted: Vec<String> = if names.is_empty() {
        VERBS.iter().filter(|verb| records.iter().any(|r| text(r, "verb") == **verb)).map(|v| v.to_string()).collect()
    } else {
        names.to_vec()
    };
    if wanted.is_empty() {
        println!("no verb has a record for this work tree; run one with `meow-verbs run <verb>`");
        return UNRESOLVED;
    }
    let now = ledger::tree_id(root);
    let (mut failed, mut unresolved) = (false, false);
    for verb in &wanted {
        let Some(latest) = records.iter().rev().find(|r| text(r, "verb") == *verb) else {
            println!("{verb}: no record");
            unresolved = true;
            continue;
        };
        let (id, outcome, tree, before) = (text(latest, "record"), text(latest, "outcome"), text(latest, "tree"), text(latest, "tree_before"));
        let head = format!("{verb}: {outcome}, record {id}");
        if outcome == "unresolved" {
            println!("{head}, not run");
            unresolved = true;
        } else if tree == ledger::UNBOUND || now == ledger::UNBOUND {
            println!("{head}, bound to no tree: this isn't a git work tree");
            unresolved = true;
        } else if before != tree {
            println!("{head}, stale: the tree changed during its run, from {} to {}", ledger::short(&before), ledger::short(&tree));
            failed = true;
        } else if tree != now {
            println!("{head}, stale: ran on tree {}, and the tree is now {}", ledger::short(&tree), ledger::short(&now));
            failed = true;
        } else {
            println!("{head}, current at tree {}", ledger::short(&tree));
            failed |= outcome != "passed";
        }
    }
    if failed {
        FAILED
    } else if unresolved {
        UNRESOLVED
    } else {
        PASSED
    }
}

pub fn main(args: &[String]) -> u8 {
    let root = profile::repository_root();
    let args: Vec<&str> = args.iter().map(String::as_str).collect();
    match args.as_slice() {
        ["status"] => status(&root, false),
        ["status", "--json"] => status(&root, true),
        ["run", rest @ ..] => run(&root, &rest.iter().map(|s| s.to_string()).collect::<Vec<_>>()),
        ["evidence", rest @ ..] => evidence(&root, &rest.iter().map(|s| s.to_string()).collect::<Vec<_>>()),
        _ => {
            eprintln!("usage: meow-verbs status [--json] | meow-verbs run <verb>... | meow-verbs evidence [verb...]");
            USAGE
        }
    }
}
