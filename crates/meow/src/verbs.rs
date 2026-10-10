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

pub(crate) mod ledger;

use crate::profile::{self, PROFILE, Profile};
use serde_json::{Map, Value, json};
use std::io::Read;
use std::path::Path;
use std::process::{Command, Stdio};
use std::time::Instant;

pub(crate) const VERBS: [&str; 5] = ["format", "lint", "check", "test", "build"];
const TAIL: usize = 20;
const PASSED: u8 = 0;
const FAILED: u8 = 1;
const USAGE: u8 = 2;
const UNRESOLVED: u8 = 3;
/// A run cut short, which a new run can fix (ADR-1530).
const INTERRUPTED: u8 = 4;
const SIGINT: i32 = 2;
const SIGTERM: i32 = 15;

/// Where a verb's subset form puts the part of the work (ADR-1520).
const TARGETS: &str = "{targets}";

enum Entry {
    Resolved {
        command: String,
        subset: Option<String>,
    },
    Unresolved {
        kind: &'static str,
        detail: String,
    },
}

struct Report {
    path: String,
    state: &'static str,
    error: Option<String>,
    verbs: Vec<(&'static str, Entry)>,
    /// The lines naming the profile's state and its unknown keys (SPC-1080).
    profile: Vec<String>,
    /// Each key the profile holds that the table of keys doesn't list.
    unknown: Vec<String>,
    notices: Vec<String>,
}

fn resolve(root: &Path) -> Report {
    let path = root.join(PROFILE).display().to_string();
    let every = |kind: &'static str, detail: String| {
        VERBS
            .iter()
            .map(|verb| {
                (
                    *verb,
                    Entry::Unresolved {
                        kind,
                        detail: detail.clone(),
                    },
                )
            })
            .collect()
    };
    let read = profile::read(root);
    let lines = profile::report(&read);
    match read {
        Profile::Absent => Report {
            path,
            state: "absent",
            error: None,
            verbs: every(
                "no profile",
                format!("{PROFILE} doesn't exist; write it, declaring each verb under [verbs]"),
            ),
            profile: lines,
            unknown: Vec::new(),
            notices: Vec::new(),
        },
        Profile::Unparseable(error) => Report {
            path,
            state: "unparseable",
            error: Some(error.clone()),
            verbs: every("profile unparseable", error),
            profile: lines,
            unknown: Vec::new(),
            notices: Vec::new(),
        },
        Profile::Parsed(data, unknown) => {
            let empty = toml::Table::new();
            let declared = match data.get("verbs") {
                None => &empty,
                Some(toml::Value::Table(table)) => table,
                Some(_) => {
                    return Report {
                        path,
                        state: "parsed",
                        error: None,
                        verbs: every("malformed declaration", "`verbs` isn't a table".to_string()),
                        profile: lines,
                        unknown,
                        notices: Vec::new(),
                    };
                }
            };
            let verbs = VERBS
                .iter()
                .map(|verb| {
                    let entry = match declared.get(*verb) {
                        None => Entry::Unresolved {
                            kind: "undeclared",
                            detail: "the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml".into(),
                        },
                        Some(toml::Value::String(command)) if !command.trim().is_empty() => {
                            Entry::Resolved { command: command.clone(), subset: None }
                        }
                        Some(toml::Value::Table(table)) => from_table(table),
                        Some(_) => Entry::Unresolved {
                            kind: "malformed declaration",
                            detail: "the value isn't one command; write one command as a string under [verbs]".into(),
                        },
                    };
                    (*verb, entry)
                })
                .collect();
            Report {
                path,
                state: "parsed",
                error: None,
                verbs,
                profile: lines,
                unknown,
                notices: Vec::new(),
            }
        }
    }
}

/// The command a verb resolves to, or why it resolves to none, for a runner
/// that holds the command itself (SPC-1201).
#[cfg(feature = "loop")]
pub(crate) fn command_of(root: &Path, verb: &str) -> std::result::Result<String, String> {
    match resolve(root)
        .verbs
        .into_iter()
        .find(|(name, _)| *name == verb)
    {
        Some((_, Entry::Resolved { command, .. })) => Ok(command),
        Some((_, Entry::Unresolved { kind, detail })) => Err(format!("{kind}: {detail}")),
        None => Err(format!("{verb} is not a verb")),
    }
}

/// A verb declared as a table: `command` for the whole work, and an optional
/// `subset` with `{targets}` where the part goes (ADR-1520).
fn from_table(table: &toml::Table) -> Entry {
    let malformed = |detail: &str| Entry::Unresolved {
        kind: "malformed declaration",
        detail: detail.into(),
    };
    let Some(command) = table
        .get("command")
        .and_then(|v| v.as_str())
        .filter(|c| !c.trim().is_empty())
    else {
        return malformed(
            "the table has no `command`; write the whole command as a string under `command`",
        );
    };
    let subset = match table.get("subset") {
        None => None,
        Some(toml::Value::String(form)) if form.contains(TARGETS) => Some(form.clone()),
        Some(toml::Value::String(_)) => {
            return malformed(
                "`subset` has no {targets}, so it would run the whole work under the part's name",
            );
        }
        Some(_) => {
            return malformed("`subset` isn't one command; write it as a string holding {targets}");
        }
    };
    Entry::Resolved {
        command: command.to_string(),
        subset,
    }
}

/// A target quoted so the shell passes it to the tool as one argument.
fn quoted(target: &str) -> String {
    if cfg!(windows) {
        format!("\"{}\"", target.replace('"', "\\\""))
    } else {
        format!("'{}'", target.replace('\'', "'\\''"))
    }
}

fn status(root: &Path, as_json: bool) -> u8 {
    let report = resolve(root);
    if as_json {
        let mut verbs = Map::new();
        for (verb, entry) in &report.verbs {
            let value = match entry {
                Entry::Resolved { command, subset } => {
                    json!({"state": "resolved", "command": command, "subset": subset, "source": PROFILE})
                }
                Entry::Unresolved { kind, detail } => {
                    json!({"state": "unresolved", "kind": kind, "detail": detail})
                }
            };
            verbs.insert(verb.to_string(), value);
        }
        let profile = if report.state == "absent" {
            Value::Null
        } else {
            Value::from(report.path.clone())
        };
        let out = json!({
            "profile": profile,
            "profile_state": report.state,
            "error": report.error,
            "verbs": verbs,
            "unknown": report.unknown,
            "notices": report.notices,
        });
        println!("{}", serde_json::to_string_pretty(&out).unwrap_or_default());
        return PASSED;
    }
    let where_ = if report.state == "absent" {
        format!("{} (absent)", report.path)
    } else {
        report.path.clone()
    };
    println!("meow-checks status, profile {where_}\n");
    for line in &report.profile {
        println!("{line}");
    }
    println!();
    for (verb, entry) in &report.verbs {
        match entry {
            Entry::Resolved { command, subset } => {
                println!("{verb:<10} resolved    {command}   (from {PROFILE})");
                match subset {
                    Some(form) => println!("{:<10} subset      {form}", ""),
                    None => println!(
                        "{:<10} subset      none: `run {verb} -- <targets>` reports no subset form",
                        ""
                    ),
                }
            }
            Entry::Unresolved { kind, detail } => {
                println!("{verb:<10} unresolved  {kind}: {detail}")
            }
        }
    }
    for notice in &report.notices {
        println!("\nnotice: {notice}");
    }
    PASSED
}

/// Runs a declared command through the shell, with standard output and
/// standard error interleaved in the order they arrive.
fn execute(root: &Path, command: &str) -> (i32, String) {
    try_execute(root, command).unwrap_or_else(|reason| (127, format!("meow: {reason}\n")))
}

/// Runs a declared command as `execute` does, or says why it never started,
/// which is neither a pass nor a fail.
fn try_execute(root: &Path, command: &str) -> std::result::Result<(i32, String), String> {
    let (mut reader, writer) =
        std::io::pipe().map_err(|error| format!("can't open a pipe: {error}"))?;
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
        Ok(copy) => shell
            .current_dir(root)
            .stdin(Stdio::null())
            .stdout(copy)
            .stderr(writer)
            .spawn(),
        Err(error) => return Err(format!("can't share the pipe: {error}")),
    };
    drop(shell);
    let mut child = match spawned {
        Ok(child) => child,
        Err(error) => return Err(format!("can't start the shell: {error}")),
    };
    let mut bytes = Vec::new();
    let _ = reader.read_to_end(&mut bytes);
    let code = match child.wait() {
        Ok(status) => status.code().unwrap_or_else(|| signal_code(status)),
        Err(_) => 127,
    };
    Ok((code, String::from_utf8_lossy(&bytes).into_owned()))
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

/// What one recorded run of a verb's command left behind.
#[cfg(feature = "loop")]
pub(crate) struct Ran {
    pub status: i32,
    /// The tree id before the command ran and after it.
    pub before: String,
    pub after: String,
    /// The ledger record's identifier, or why nothing was recorded.
    pub recorded: std::result::Result<String, String>,
}

/// Runs a verb's whole command and records the result in the ledger with the
/// tree before and after it, as `run` does, for a runner that decides from the
/// exit status itself (SPC-1201). A command that never started is an error and
/// is recorded as unresolved, because an unresolved verb is never a pass.
#[cfg(feature = "loop")]
pub(crate) fn run_recorded(
    root: &Path,
    verb: &str,
    command: &str,
) -> std::result::Result<Ran, String> {
    let before = ledger::tree_id(root);
    let started = ledger::start(root, verb, command, None, &before);
    let ran = try_execute(root, command);
    let after = ledger::tree_id(root);
    let (outcome, status, output) = match &ran {
        Ok((0, output)) => ("passed", Some(0), output.as_str()),
        Ok((c, output)) if *c == -SIGINT || *c == -SIGTERM => {
            ("interrupted", Some(*c), output.as_str())
        }
        Ok((c, output)) => ("failed", Some(*c), output.as_str()),
        Err(reason) => ("unresolved", None, reason.as_str()),
    };
    let recorded = ledger::record(
        root,
        &ledger::Result {
            verb,
            command: Some(command),
            outcome,
            status,
            before: &before,
            after: &after,
            output,
            targets: None,
        },
        started.as_deref(),
    );
    let (status, _) = ran?;
    Ok(Ran {
        status,
        before,
        after,
        recorded,
    })
}

fn run(root: &Path, args: &[String]) -> u8 {
    // Everything after `--` is the part of the work to run over (ADR-1520).
    let (names, targets): (&[String], Option<&[String]>) = match args.iter().position(|a| a == "--")
    {
        Some(i) => (&args[..i], Some(&args[i + 1..])),
        None => (args, None),
    };
    if targets.is_some_and(|t| t.is_empty()) {
        eprintln!(
            "meow-checks run: `--` names no target, which could mean the whole work or nothing; name the targets or drop `--`"
        );
        return USAGE;
    }
    if names.is_empty() {
        eprintln!(
            "meow-checks run: name the verbs to run, from: {}",
            VERBS.join(" ")
        );
        return USAGE;
    }
    let unknown: Vec<&str> = names
        .iter()
        .map(String::as_str)
        .filter(|name| !VERBS.contains(name))
        .collect();
    if !unknown.is_empty() {
        eprintln!(
            "meow-checks run: {} isn't a verb; the five are {}",
            unknown.join(", "),
            VERBS.join(" ")
        );
        return USAGE;
    }

    let report = resolve(root);
    for line in &report.profile {
        println!("{line}");
    }
    println!();
    for notice in &report.notices {
        println!("notice: {notice}\n");
    }
    let pruned = ledger::prune(root);
    if pruned > 0 {
        println!("pruned {pruned} records older than 30 days from the ledger\n");
    }
    let mut outcomes: Vec<(String, &str)> = Vec::new();
    let mut recorded: Vec<String> = Vec::new();
    let mut keep = |result: ledger::Result, started: Option<&str>| match ledger::record(
        root, &result, started,
    ) {
        Ok(id) => recorded.push(format!(
            "recorded: {} {id} at tree {}",
            result.verb,
            ledger::short(result.after)
        )),
        Err(reason) => recorded.push(format!("not recorded: {} ({reason})", result.verb)),
    };
    for name in names {
        let entry = &report
            .verbs
            .iter()
            .find(|(verb, _)| verb == name)
            .expect("a known verb")
            .1;
        let command = match entry {
            Entry::Unresolved { kind, detail } => {
                println!("== {name}: unresolved ({kind}: {detail}), not run\n");
                outcomes.push((name.clone(), "unresolved"));
                let tree = ledger::tree_id(root);
                keep(
                    ledger::Result {
                        verb: name,
                        command: None,
                        outcome: "unresolved",
                        status: None,
                        before: &tree,
                        after: &tree,
                        output: "",
                        targets,
                    },
                    None,
                );
                continue;
            }
            Entry::Resolved { command, subset } => match (targets, subset) {
                (None, _) => command.clone(),
                (Some(parts), Some(form)) => form.replace(
                    TARGETS,
                    &parts
                        .iter()
                        .map(|t| quoted(t))
                        .collect::<Vec<_>>()
                        .join(" "),
                ),
                (Some(_), None) => {
                    let detail = format!(
                        "the profile declares no `subset` for {name}; declare one under [verbs.{name}] with {TARGETS}, or run the whole verb"
                    );
                    println!("== {name}: unresolved (no subset form: {detail}), not run\n");
                    outcomes.push((name.clone(), "unresolved"));
                    let tree = ledger::tree_id(root);
                    keep(
                        ledger::Result {
                            verb: name,
                            command: None,
                            outcome: "unresolved",
                            status: None,
                            before: &tree,
                            after: &tree,
                            output: "",
                            targets,
                        },
                        None,
                    );
                    continue;
                }
            },
        };
        let command = &command;
        let before = ledger::tree_id(root);
        let record = ledger::start(root, name, command, targets, &before);
        let started = Instant::now();
        let (code, output) = execute(root, command);
        let after = ledger::tree_id(root);
        // A verb ended by an interrupt or a termination signal says the run
        // stopped, and nothing about the work (REQ-2969).
        let outcome = match code {
            0 => "passed",
            c if c == -SIGINT || c == -SIGTERM => "interrupted",
            _ => "failed",
        };
        keep(
            ledger::Result {
                verb: name,
                command: Some(command),
                outcome,
                status: Some(code),
                before: &before,
                after: &after,
                output: &output,
                targets,
            },
            record.as_deref(),
        );
        let seconds = started.elapsed().as_secs_f64();
        println!("== {name}: `{command}`");
        if code == 0 {
            println!("passed, exit status 0 after {seconds:.1}s\n");
            outcomes.push((name.clone(), "passed"));
        } else if outcome == "interrupted" {
            println!(
                "interrupted by signal {} after {seconds:.1}s; the run stopped, and this says nothing about the work\n",
                -code
            );
            outcomes.push((name.clone(), "interrupted"));
        } else {
            let lines: Vec<&str> = output.trim_end_matches('\n').lines().collect();
            let shown = lines.len().min(TAIL);
            println!(
                "failed, exit status {code} after {seconds:.1}s; the last {shown} lines of its output:"
            );
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

    let summary: Vec<String> = outcomes
        .iter()
        .map(|(verb, result)| format!("{verb} {result}"))
        .collect();
    println!("summary: {}", summary.join(", "));
    for line in &recorded {
        println!("{line}");
    }
    if outcomes.iter().any(|(_, result)| *result == "failed") {
        FAILED
    } else if outcomes.iter().any(|(_, result)| *result == "interrupted") {
        INTERRUPTED
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
fn evidence(root: &Path, args: &[String]) -> u8 {
    // The repository keeps no run output (REQ-3614), so the two flags that
    // kept and listed it are refused, naming the decision, for one release.
    if args.iter().any(|a| a == "--keep" || a == "--kept") {
        eprintln!(
            "meow-checks evidence: kept evidence was removed by ADR-2300; cite the line `evidence` prints, and the pull request"
        );
        return USAGE;
    }
    // `--all` adds the other work trees of the same repository (ADR-1530).
    let all = args.iter().any(|a| a == "--all");
    let names: Vec<String> = args
        .iter()
        .filter(|a| a.as_str() != "--all")
        .cloned()
        .collect();
    let names = names.as_slice();
    let unknown: Vec<&str> = names
        .iter()
        .map(String::as_str)
        .filter(|name| !VERBS.contains(name))
        .collect();
    if !unknown.is_empty() {
        eprintln!(
            "meow-checks evidence: {} isn't a verb; the five are {}",
            unknown.join(", "),
            VERBS.join(" ")
        );
        return USAGE;
    }
    let records = ledger::records(root);
    let text = |record: &Value, key: &str| {
        record
            .get(key)
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string()
    };
    let wanted: Vec<String> = if names.is_empty() {
        VERBS
            .iter()
            .filter(|verb| records.iter().any(|r| text(r, "verb") == **verb))
            .map(|v| v.to_string())
            .collect()
    } else {
        names.to_vec()
    };
    if wanted.is_empty() {
        println!("no verb has a record for this work tree; run one with `meow-checks run <verb>`");
        return UNRESOLVED;
    }
    let now = ledger::tree_id(root);
    let (mut failed, mut unresolved, mut interrupted) = (false, false, false);
    for verb in &wanted {
        // A subset record never stands for the whole verb (ADR-1520); a record
        // from before targets were kept has none, and was a whole run.
        let whole = |r: &&Value| r.get("targets").is_none_or(Value::is_null);
        if let Some(part) = records
            .iter()
            .rev()
            .find(|r| text(r, "verb") == *verb)
            .filter(|r| !whole(r))
        {
            let parts: Vec<&str> = part["targets"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(Value::as_str)
                .collect();
            println!(
                "{verb}: subset only, {}, record {}, targets {}, at tree {}",
                text(part, "outcome"),
                text(part, "record"),
                parts.join(" "),
                ledger::short(&text(part, "tree"))
            );
        }
        let Some(latest) = records
            .iter()
            .rev()
            .filter(|r| text(r, "verb") == *verb)
            .find(whole)
        else {
            println!("{verb}: no record of a whole run");
            unresolved = true;
            continue;
        };
        let (id, outcome, tree, before) = (
            text(latest, "record"),
            text(latest, "outcome"),
            text(latest, "tree"),
            text(latest, "tree_before"),
        );
        let head = format!("{verb}: {outcome}, record {id}");
        if outcome == "running" || outcome == "interrupted" {
            println!(
                "{head}, {}",
                if outcome == "running" {
                    "still running in another session"
                } else {
                    "cut short; run it again"
                }
            );
            interrupted = true;
            continue;
        }
        if outcome == "unresolved" {
            println!("{head}, not run");
            unresolved = true;
        } else if tree == ledger::UNBOUND || now == ledger::UNBOUND {
            match ledger::dirty_submodule(root) {
                Some(sub) => println!(
                    "{head}, bound to no tree: the submodule {sub} has uncommitted changes"
                ),
                None => println!("{head}, bound to no tree: this isn't a git work tree"),
            }
            unresolved = true;
        } else if before != tree {
            println!(
                "{head}, stale: the tree changed during its run, from {} to {}",
                ledger::short(&before),
                ledger::short(&tree)
            );
            failed = true;
        } else if tree != now {
            println!(
                "{head}, stale: ran on tree {}, and the tree is now {}",
                ledger::short(&tree),
                ledger::short(&now)
            );
            failed = true;
        } else {
            println!("{head}, current at tree {}", ledger::short(&tree));
            failed |= outcome != "passed";
        }
    }
    if all {
        for (tree, found) in ledger::other_work_trees(root) {
            println!("\n== work tree {tree}");
            for verb in VERBS {
                if let Some(latest) = found.iter().rev().find(|r| {
                    text(r, "verb") == verb && r.get("targets").is_none_or(Value::is_null)
                }) {
                    println!(
                        "{verb}: {}, record {}, at tree {}",
                        text(latest, "outcome"),
                        text(latest, "record"),
                        ledger::short(&text(latest, "tree"))
                    );
                }
            }
        }
    }
    if failed {
        FAILED
    } else if interrupted {
        INTERRUPTED
    } else if unresolved {
        UNRESOLVED
    } else {
        PASSED
    }
}

/// Where the ledger is and what it holds, or, with `--purge`, an emptied one
/// (REQ-0756, REQ-2962).
fn state(root: &Path, args: &[&str]) -> u8 {
    match args {
        [] => {
            for line in ledger::facts(root) {
                println!("{line}");
            }
            PASSED
        }
        ["--purge"] => match ledger::purge(root) {
            Ok(count) => {
                println!("purged {count} ledger lines and their output");
                PASSED
            }
            Err(reason) => {
                eprintln!("meow-checks state: {reason}");
                FAILED
            }
        },
        _ => {
            eprintln!("usage: meow-checks state [--purge]");
            USAGE
        }
    }
}

pub fn main(args: &[String]) -> u8 {
    let root = profile::repository_root();
    let args: Vec<&str> = args.iter().map(String::as_str).collect();
    match args.as_slice() {
        ["status"] => status(&root, false),
        ["status", "--json"] => status(&root, true),
        ["run", rest @ ..] => run(
            &root,
            &rest.iter().map(|s| s.to_string()).collect::<Vec<_>>(),
        ),
        ["state", rest @ ..] => state(&root, rest),
        ["tree", commit] => match ledger::tree_of_commit(&root, commit) {
            Ok(tree) => {
                println!("{tree}");
                PASSED
            }
            Err(reason) => {
                eprintln!("meow-checks tree: {reason}");
                FAILED
            }
        },
        ["evidence", rest @ ..] => evidence(
            &root,
            &rest.iter().map(|s| s.to_string()).collect::<Vec<_>>(),
        ),
        _ => {
            eprintln!(
                "usage: meow-checks status [--json] | meow-checks run <verb>... [-- <target>...] | meow-checks evidence [--all] [verb...] | meow-checks state [--purge] | meow-checks tree <commit>"
            );
            USAGE
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn profile_in(case: &str, text: &str) -> std::path::PathBuf {
        let dir = std::env::temp_dir().join(format!("meow-stages-{case}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(dir.join(".meowpaw")).unwrap();
        std::fs::write(dir.join(PROFILE), text).unwrap();
        dir
    }

    fn resolved(report: &Report, stage: &str) -> Option<String> {
        report.verbs.iter().find_map(|(name, entry)| match entry {
            Entry::Resolved { command, .. } if *name == stage => Some(command.clone()),
            _ => None,
        })
    }

    /// TSK-5270, criteria 1 and 2, REQ-4202 and REQ-4204: a stage resolves
    /// from `[stages]`, and from `[verbs]` with the table to use named.
    #[test]
    fn a_stage_resolves_from_either_table() {
        let stages = resolve(&profile_in("stages", "[stages]\ntest = \"run-tests\"\n"));
        assert_eq!(resolved(&stages, "test").as_deref(), Some("run-tests"));
        assert_eq!(stages.profile, ["profile: parsed"]);
        let verbs = resolve(&profile_in("verbs", "[verbs]\ntest = \"run-tests\"\n"));
        assert_eq!(resolved(&verbs, "test").as_deref(), Some("run-tests"));
        assert!(
            verbs.profile.iter().any(|line| line.contains("[stages]")),
            "{:?}",
            verbs.profile
        );
    }

    #[test]
    fn a_command_that_never_started_is_not_an_exit_status() {
        // SPC-1201: an unspawned verb counts neither as a pass nor as a fail.
        let nowhere = std::env::temp_dir().join(format!("meow-no-such-{}", std::process::id()));
        let reason = try_execute(&nowhere, "true").expect_err("a shell started in no directory");
        assert!(reason.starts_with("can't start the shell"), "{reason}");
        assert_eq!(execute(&nowhere, "true").0, 127);
        assert!(
            execute(&nowhere, "true")
                .1
                .starts_with("meow: can't start the shell")
        );
    }

    #[test]
    fn a_command_that_started_keeps_its_exit_status() {
        let here = std::env::temp_dir();
        let failing = if cfg!(windows) { "exit /b 3" } else { "exit 3" };
        assert_eq!(try_execute(&here, failing).map(|(code, _)| code), Ok(3));
    }
}
