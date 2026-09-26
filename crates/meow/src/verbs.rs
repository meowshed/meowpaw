// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Resolve the five verbs from the repository's profile, report them, and run them.
//!
//! SPC-1040 states the behaviour. A verb resolves only from the command the
//! repository declares under `[verbs]` (REQ-0134), and a verb that resolves to
//! nothing is reported as unresolved and of which kind, never as passed
//! (REQ-0136, REQ-0154). `status` runs nothing (REQ-0150). `run` records each
//! verb's exact command, exit status and whole output (REQ-0144, REQ-0156), and
//! leads a failed verb with its last lines (REQ-0135).

use crate::profile::{self, Profile, PROFILE};
use serde_json::{json, Map, Value};
use std::io::Read;
use std::path::Path;
use std::process::{Command, Stdio};
use std::time::Instant;

const VERBS: [&str; 5] = ["fmt", "lint", "typecheck", "test", "build"];
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
            verbs: every("no profile", format!("{PROFILE} doesn't exist")),
            ignored: Vec::new(),
        },
        Profile::Unparseable(error) => Report {
            path,
            state: "unparseable",
            error: Some(error.clone()),
            verbs: every("profile unparseable", error),
            ignored: Vec::new(),
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
                    };
                }
            };
            ignored.extend(
                declared.keys().filter(|key| !VERBS.contains(&key.as_str())).map(|key| format!("verbs.{key}")),
            );
            let verbs = VERBS
                .iter()
                .map(|verb| {
                    let entry = match declared.get(*verb) {
                        None => Entry::Unresolved { kind: "undeclared", detail: "the profile doesn't name it".into() },
                        Some(toml::Value::String(command)) if !command.trim().is_empty() => {
                            Entry::Resolved { command: command.clone() }
                        }
                        Some(_) => Entry::Unresolved {
                            kind: "malformed declaration",
                            detail: "the value isn't one command".into(),
                        },
                    };
                    (*verb, entry)
                })
                .collect();
            Report { path, state: "present", error: None, verbs, ignored }
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
    let mut outcomes: Vec<(String, &str)> = Vec::new();
    for name in names {
        let entry = &report.verbs.iter().find(|(verb, _)| verb == name).expect("a known verb").1;
        let command = match entry {
            Entry::Unresolved { kind, detail } => {
                println!("== {name}: unresolved ({kind}: {detail}), not run\n");
                outcomes.push((name.clone(), "unresolved"));
                continue;
            }
            Entry::Resolved { command } => command,
        };
        let started = Instant::now();
        let (code, output) = execute(root, command);
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
    if outcomes.iter().any(|(_, result)| *result == "failed") {
        FAILED
    } else if outcomes.iter().any(|(_, result)| *result == "unresolved") {
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
        _ => {
            eprintln!("usage: meow-verbs status [--json] | meow-verbs run <verb>...");
            USAGE
        }
    }
}
