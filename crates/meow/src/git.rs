// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Refuse a commit on the trunk, and check every commit a push would publish.
//!
//! SPC-1060 states the behaviour. The hooks pass the tool call as JSON on
//! standard input; a guard blocks by exiting 2 with its reason on standard
//! error, and lets the command through by exiting 0. `commit-guard` blocks a
//! commit on the declared trunk (REQ-1292). `push-guard` checks each commit a
//! push would publish through `meow-scm check-message` where that unit is
//! installed, and reports the check as unrun where it isn't (REQ-0079), and
//! passes only a good signature from a trusted key where the repository
//! requires one (REQ-1326, REQ-2530).

use crate::profile::{self, Profile};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

const KEYS: [&str; 2] = ["trunk", "require_signatures"];
const BLOCK: u8 = 2;
const ALLOW: u8 = 0;

fn git(root: &Path, args: &[&str]) -> (bool, String) {
    let done = Command::new("git")
        .args(args)
        .current_dir(root)
        .env("GIT_TERMINAL_PROMPT", "0")
        .env("GIT_PAGER", "cat")
        .stdin(Stdio::null())
        .output();
    match done {
        Ok(out) => (out.status.success(), String::from_utf8_lossy(&out.stdout).into_owned()),
        Err(_) => (false, String::new()),
    }
}

/// The session's directory, from the hook's input where it names one.
fn working_directory() -> PathBuf {
    let mut text = String::new();
    let _ = std::io::stdin().read_to_string(&mut text);
    let event: serde_json::Value = serde_json::from_str(if text.trim().is_empty() { "{}" } else { &text })
        .unwrap_or(serde_json::Value::Null);
    match event.get("cwd").and_then(|cwd| cwd.as_str()) {
        Some(cwd) if !cwd.is_empty() => PathBuf::from(cwd),
        _ => std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")),
    }
}

struct Policy {
    trunk: Option<String>,
    signatures: bool,
    declared: bool,
    ignored: Vec<String>,
}

fn policy(root: &Path) -> Policy {
    let data = match profile::read(root) {
        Profile::Parsed(data) => data,
        _ => toml::Table::new(),
    };
    let empty = toml::Table::new();
    let table = match data.get("git") {
        Some(toml::Value::Table(table)) => table,
        _ => &empty,
    };
    Policy {
        trunk: table.get("trunk").and_then(|value| value.as_str()).map(str::to_string),
        signatures: table.get("require_signatures").and_then(|value| value.as_bool()) == Some(true),
        declared: !table.is_empty(),
        ignored: table.keys().filter(|key| !KEYS.contains(&key.as_str())).map(|key| format!("git.{key}")).collect(),
    }
}

/// `meow-scm`'s launcher, where it is installed, and never installed by this pack.
fn find_meow_scm() -> Option<PathBuf> {
    if let Ok(named) = std::env::var("MEOW_SCM") {
        let named = PathBuf::from(named);
        return named.is_file().then_some(named);
    }
    // The binary sits at <pack>/bin/<target>/meow.
    let pack = std::env::current_exe().ok()?.canonicalize().ok()?.parent()?.parent()?.parent()?.to_path_buf();
    let beside = pack.parent()?.join("meow-scm").join("bin").join("meow-scm");
    if beside.is_file() {
        return Some(beside);
    }
    let home = std::env::var_os("HOME").or_else(|| std::env::var_os("USERPROFILE"))?;
    let cache = PathBuf::from(home).join(".claude").join("plugins").join("cache");
    let mut found: Vec<(Vec<u64>, PathBuf)> = Vec::new();
    for marketplace in std::fs::read_dir(&cache).ok()?.flatten() {
        let Ok(versions) = std::fs::read_dir(marketplace.path().join("meow-scm")) else { continue };
        for version in versions.flatten() {
            let launcher = version.path().join("bin").join("meow-scm");
            if launcher.is_file() {
                let name = version.file_name().to_string_lossy().into_owned();
                let key = name.split(|c: char| !c.is_ascii_digit()).filter_map(|n| n.parse().ok()).collect();
                found.push((key, launcher));
            }
        }
    }
    found.sort();
    found.pop().map(|(_, launcher)| launcher)
}

fn commit_guard(root: &Path) -> u8 {
    let trunk = match policy(root).trunk {
        Some(trunk) => trunk,
        None => {
            println!("meow-git commit-guard: no trunk declared under [git]; nothing refused");
            return ALLOW;
        }
    };
    let (ok, branch) = git(root, &["symbolic-ref", "--short", "-q", "HEAD"]);
    let branch = branch.trim();
    if ok && branch == trunk {
        eprintln!(
            "meow-git: refused a commit on `{trunk}`, the trunk this repository declares. Take a branch and commit there."
        );
        return BLOCK;
    }
    let shown = if branch.is_empty() { "a detached head" } else { branch };
    println!("meow-git commit-guard: `{shown}` isn't the trunk `{trunk}`");
    ALLOW
}

/// None where the commit's signature is good, otherwise what is wrong with it.
fn signature(root: &Path, commit: &str) -> Option<String> {
    let verdict = git(root, &["log", "-1", "--format=%G?", commit]).1.trim().to_string();
    if verdict == "G" {
        return None;
    }
    let raw = git(root, &["cat-file", "commit", commit]).1;
    let signed = raw.contains("\ngpgsig ") || raw.starts_with("gpgsig ");
    Some(match verdict.as_str() {
        "E" | "N" if signed => "is signed, but the signature is unverifiable here: the key material or the list of allowed signers is missing".to_string(),
        "N" => "is unsigned".to_string(),
        "U" => "signed by a key this repository doesn't trust".to_string(),
        "B" => "carries a bad signature".to_string(),
        "X" => "carries a signature that has expired".to_string(),
        "Y" => "was signed by a key that has expired".to_string(),
        "R" => "was signed by a key that has been revoked".to_string(),
        other => format!("has the signature verdict '{other}'"),
    })
}

fn plural(count: usize) -> &'static str {
    if count > 1 { "s" } else { "" }
}

fn push_guard(root: &Path) -> u8 {
    let policy = policy(root);
    let (ok, listed) = git(root, &["rev-list", "--reverse", "HEAD", "--not", "--remotes"]);
    let commits: Vec<String> = if ok { listed.split_whitespace().map(str::to_string).collect() } else { Vec::new() };
    let mut notes: Vec<String> = Vec::new();
    if !policy.declared {
        notes.push("no [git] table: the trunk and the signing policy are undeclared".to_string());
    }
    if !policy.ignored.is_empty() {
        notes.push(format!("not read by meow-git: {}", policy.ignored.join(", ")));
    }
    if commits.is_empty() {
        println!("meow-git push-guard: no commit to publish was found; checked nothing");
        return ALLOW;
    }

    let scm = find_meow_scm();
    if scm.is_none() {
        notes.push("meow-scm isn't installed: the message check is unrun for every commit".to_string());
    }
    let mut failures: Vec<String> = Vec::new();
    for commit in &commits {
        let subject = git(root, &["log", "-1", "--format=%h %s", commit]).1.trim().to_string();
        if let Some(scm) = &scm {
            let message = git(root, &["log", "-1", "--format=%B", commit]).1;
            if let Some((code, stdout)) = run_check(scm, root, &message) {
                if code == 1 {
                    let lines: Vec<String> =
                        stdout.lines().filter(|line| line.starts_with("line ")).map(|line| format!("    {line}")).collect();
                    failures.push(format!("{subject}\n{}", lines.join("\n")));
                } else if code == 3 && !notes.iter().any(|note| note.contains("convention")) {
                    let last = stdout.trim().lines().last().unwrap_or_default().to_string();
                    notes.push(format!("meow-scm: {last}"));
                }
            }
        }
        if policy.signatures {
            if let Some(problem) = signature(root, commit) {
                failures.push(format!("{subject}\n    signature: the commit {problem}"));
            }
        }
    }

    for note in &notes {
        println!("meow-git push-guard: {note}");
    }
    if !failures.is_empty() {
        eprintln!(
            "meow-git: refused the push; {} problem{} in the {} commit{} it would publish:\n\n{}",
            failures.len(),
            plural(failures.len()),
            commits.len(),
            plural(commits.len()),
            failures.join("\n")
        );
        return BLOCK;
    }
    println!("meow-git push-guard: {} commit{} checked", commits.len(), plural(commits.len()));
    ALLOW
}

/// Runs `meow-scm check-message` on one message, as its exit status and output.
fn run_check(scm: &Path, root: &Path, message: &str) -> Option<(i32, String)> {
    let mut child = Command::new(scm)
        .arg("check-message")
        .current_dir(root)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .ok()?;
    if let Some(mut input) = child.stdin.take() {
        let _ = input.write_all(message.as_bytes());
    }
    let out = child.wait_with_output().ok()?;
    Some((out.status.code().unwrap_or(-1), String::from_utf8_lossy(&out.stdout).into_owned()))
}

pub fn main(args: &[String]) -> u8 {
    let name = match args {
        [name] if name == "commit-guard" || name == "push-guard" => name.as_str(),
        _ => {
            eprintln!("usage: meow-git commit-guard | meow-git push-guard");
            return 1;
        }
    };
    let start = working_directory();
    let (ok, top) = git(&start, &["rev-parse", "--show-toplevel"]);
    if !ok {
        println!("meow-git {name}: not inside a repository; checked nothing");
        return ALLOW;
    }
    let root = PathBuf::from(top.trim());
    if name == "commit-guard" { commit_guard(&root) } else { push_guard(&root) }
}
