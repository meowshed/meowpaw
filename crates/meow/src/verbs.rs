// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Resolve the five stages from the repository's profile, report them, and run them.
//!
//! SPC-1040 states the behaviour. A stage resolves only from the command the
//! repository declares under `[stages]` (REQ-0134), and a stage that resolves to
//! nothing is reported as unresolved and of which kind, never as passed
//! (REQ-0136, REQ-0154). `status` runs nothing (REQ-0150). `run` records each
//! stage's exact command, exit status and whole output (REQ-0144, REQ-0156), and
//! leads a failed stage with its last lines (REQ-0135). Each result goes into a
//! ledger bound to the tree it ran on, which `evidence` reads back (ADR-1480).

pub(crate) mod ledger;

use crate::profile::{self, PERSONAL, PROFILE, Personal, Profile};
use serde_json::{Map, Value, json};
use std::io::Read;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Instant;

pub(crate) const VERBS: [&str; 5] = ["format", "lint", "check", "test", "build"];
/// The outcomes a stage's run records, as SPC-1040 states them: passed and
/// failed from the exit status, interrupted from a signal, and unresolved
/// where the profile declares no command.
pub(crate) const OUTCOMES: [&str; 4] = ["passed", "failed", "unresolved", "interrupted"];
const TAIL: usize = 20;
const PASSED: u8 = 0;
const FAILED: u8 = 1;
const USAGE: u8 = 2;
const UNRESOLVED: u8 = 3;
/// A run cut short, which a new run can fix (ADR-1530).
const INTERRUPTED: u8 = 4;
const SIGINT: i32 = 2;
const SIGTERM: i32 = 15;

/// Where a stage's subset form puts the part of the work (ADR-1520).
const TARGETS: &str = "{targets}";

enum Entry {
    Resolved {
        command: String,
        subset: Option<String>,
        /// The file the declaration came from.
        source: &'static str,
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

/// What a report or a run covers: one part the root profile declares, or the
/// whole repository (REQ-3042, REQ-3043).
pub(crate) struct Scope {
    part: Option<profile::Part>,
    /// Where the scope's commands run: the part's directory, or the root.
    directory: PathBuf,
}

impl Scope {
    pub(crate) fn repository(root: &Path) -> Scope {
        Scope {
            part: None,
            directory: root.to_path_buf(),
        }
    }

    fn of(root: &Path, part: profile::Part) -> Scope {
        Scope {
            directory: root.join(&part.directory),
            part: Some(part),
        }
    }

    /// The line every report prints, naming what it ran for.
    fn line(&self) -> String {
        match &self.part {
            Some(part) => format!("scope: {} {}", part.name, part.directory),
            None => "scope: repository".to_string(),
        }
    }

    /// The name a ledger record keeps, which `evidence` reads back.
    fn label(&self) -> &str {
        self.part.as_ref().map_or("repository", |p| p.name.as_str())
    }
}

/// The parts the root profile declares, or none where it declares none or
/// doesn't parse.
fn declared_parts(root: &Path) -> Vec<profile::Part> {
    match profile::read(root) {
        Profile::Parsed(table, _) => profile::parts(&table).0,
        _ => Vec::new(),
    }
}

/// The scope `--part <name>` names, and the arguments without it. With no
/// `--part`, it is the part whose directory holds the current directory, and
/// the repository where none does. Arguments after `--` are targets and stay.
fn scope_of(root: &Path, command: &str, args: &[String]) -> Result<(Scope, Vec<String>), u8> {
    let end = args.iter().position(|a| a == "--").unwrap_or(args.len());
    let mut rest = Vec::new();
    let mut named = None;
    let mut i = 0;
    while i < args.len() {
        if i < end && args[i] == "--part" {
            let Some(name) = args.get(i + 1).filter(|_| i + 1 < end) else {
                eprintln!("meow-checks {command}: --part names no part; write --part <name>");
                return Err(USAGE);
            };
            named = Some(name.clone());
            i += 2;
            continue;
        }
        rest.push(args[i].clone());
        i += 1;
    }
    let parts = declared_parts(root);
    if let Some(name) = named {
        return match parts.iter().find(|part| part.name == name) {
            Some(part) => Ok((Scope::of(root, part.clone()), rest)),
            None => {
                let names: Vec<&str> = parts.iter().map(|p| p.name.as_str()).collect();
                let declared = if names.is_empty() {
                    "the profile declares no [parts]".to_string()
                } else {
                    format!("the profile declares: {}", names.join(", "))
                };
                eprintln!(
                    "meow-checks {command}: --part {name} names no declared part, so nothing ran; {declared}"
                );
                Err(USAGE)
            }
        };
    }
    let here = std::env::current_dir()
        .ok()
        .and_then(|d| std::fs::canonicalize(d).ok());
    let top = std::fs::canonicalize(root).unwrap_or_else(|_| root.to_path_buf());
    let inside = here
        .as_deref()
        .and_then(|here| here.strip_prefix(&top).ok())
        .map(Path::to_path_buf);
    let holding = inside.and_then(|relative| {
        parts
            .into_iter()
            .filter(|part| relative.starts_with(&part.directory))
            .max_by_key(|part| part.directory.len())
    });
    Ok((
        holding.map_or_else(|| Scope::repository(root), |part| Scope::of(root, part)),
        rest,
    ))
}

fn resolve(root: &Path, scope: &Scope) -> Report {
    let mut report = resolve_shared(root, scope);
    // The personal profile sits beside the shared profile the stages came from.
    let personal = match &scope.part {
        Some(part) if profile::part_profile(root, part).is_file() => scope.directory.clone(),
        _ => root.to_path_buf(),
    };
    apply_personal(root, &personal, &mut report);
    report
}

/// The word a command starts with, with its quotes taken off.
fn first_word(command: &str) -> &str {
    let command = command.trim_start();
    match command.chars().next() {
        Some(quote @ ('"' | '\'')) => {
            let rest = &command[1..];
            rest.split(quote).next().unwrap_or(rest)
        }
        _ => command.split_whitespace().next().unwrap_or(""),
    }
}

/// Where `path` points once its `.` and `..` components are applied, or
/// `None` where a relative path climbs above its starting point.
fn lexical(path: &Path) -> Option<std::path::PathBuf> {
    use std::path::Component;
    let mut out = std::path::PathBuf::new();
    let mut depth = 0usize;
    for part in path.components() {
        match part {
            Component::CurDir => {}
            Component::ParentDir => {
                if depth == 0 && !path.is_absolute() {
                    return None;
                }
                out.pop();
                depth = depth.saturating_sub(1);
            }
            Component::Normal(name) => {
                out.push(name);
                depth += 1;
            }
            other => out.push(other.as_os_str()),
        }
    }
    Some(out)
}

/// The first word of a command, where it names a place on this machine and not
/// a tool the toolchain provides: it starts with `~` or `$HOME`, or is a path
/// that resolves outside the repository, however it is quoted or written with
/// `..` (REQ-2946).
fn machine_path<'a>(root: &Path, command: &'a str) -> Option<&'a str> {
    let word = first_word(command);
    if word.starts_with('~') || word.starts_with("$HOME") || word.starts_with("${HOME}") {
        return Some(word);
    }
    let path = Path::new(word);
    let outside = if path.is_absolute() {
        lexical(path).is_none_or(|resolved| !resolved.starts_with(root))
    } else {
        word.contains('/') && lexical(path).is_none()
    };
    outside.then_some(word)
}

/// Lets the personal profile's stages replace the shared ones on this machine
/// (REQ-2944). A personal profile that doesn't parse replaces nothing, and an
/// unparseable shared profile resolves nothing for it to replace (REQ-2948).
fn apply_personal(root: &Path, beside: &Path, report: &mut Report) {
    if report.state == "unparseable" {
        return;
    }
    match profile::read_personal(beside) {
        Personal::Absent => {}
        Personal::Unparseable(error) => {
            report
                .profile
                .push("personal profile: unparseable".to_string());
            report
                .profile
                .push(format!("personal profile error: {error}"));
        }
        Personal::Parsed(table, unknown) => {
            for key in unknown {
                report
                    .profile
                    .push(format!("unknown key: {key} (in {PERSONAL})"));
                report.unknown.push(format!("{key} (in {PERSONAL})"));
            }
            let empty = toml::Table::new();
            let declared = match profile::stages(&table) {
                None => &empty,
                Some(toml::Value::Table(declared)) => declared,
                Some(_) => {
                    report.profile.push(format!(
                        "personal profile: the stages declaration in {PERSONAL} isn't a table"
                    ));
                    return;
                }
            };
            for (verb, entry) in report.verbs.iter_mut() {
                let Some(value) = declared.get(*verb) else {
                    continue;
                };
                let personal = match value {
                    toml::Value::String(command) if !command.trim().is_empty() => Entry::Resolved {
                        command: command.clone(),
                        subset: None,
                        source: PERSONAL,
                    },
                    toml::Value::Table(inner) => match from_table(inner) {
                        Entry::Resolved {
                            command, subset, ..
                        } => Entry::Resolved {
                            command,
                            subset,
                            source: PERSONAL,
                        },
                        other => other,
                    },
                    _ => Entry::Unresolved {
                        kind: "malformed declaration",
                        detail: format!(
                            "the value in {PERSONAL} isn't one command; write one command as a string under [stages]"
                        ),
                    },
                };
                *entry = match personal {
                    Entry::Resolved { command, .. } if machine_path(root, &command).is_some() => {
                        let word = machine_path(root, &command).unwrap_or_default();
                        Entry::Unresolved {
                            kind: "machine path",
                            detail: format!(
                                "{PERSONAL} runs {word}, a path on this machine; name the tool through the project's toolchain declaration"
                            ),
                        }
                    }
                    other => other,
                };
            }
        }
    }
}

fn resolve_shared(root: &Path, scope: &Scope) -> Report {
    let (read, path) = match &scope.part {
        Some(part) if profile::part_profile(root, part).is_file() => (
            profile::read_part(root, part),
            profile::part_profile(root, part),
        ),
        Some(part) => (profile::read_part(root, part), root.join(PROFILE)),
        None => (profile::read(root), root.join(PROFILE)),
    };
    let path = path.display().to_string();
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
    let mut lines = profile::report(&read);
    if let Profile::Parsed(table, _) = &read {
        lines.extend(profile::parts(table).1);
    }
    match read {
        Profile::Absent => Report {
            path,
            state: "absent",
            error: None,
            verbs: every(
                "no profile",
                format!("{PROFILE} doesn't exist; write it, declaring each stage under [stages]"),
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
            let declared = match profile::stages(&data) {
                None => &empty,
                Some(toml::Value::Table(table)) => table,
                Some(_) => {
                    return Report {
                        path,
                        state: "parsed",
                        error: None,
                        verbs: every(
                            "malformed declaration",
                            "the stages declaration isn't a table".to_string(),
                        ),
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
                            detail: "the profile doesn't name it; declare it under [stages] in .meowpaw/profile.toml".into(),
                        },
                        Some(toml::Value::String(command)) if !command.trim().is_empty() => {
                            Entry::Resolved { command: command.clone(), subset: None, source: PROFILE }
                        }
                        Some(toml::Value::Table(table)) => from_table(table),
                        Some(_) => Entry::Unresolved {
                            kind: "malformed declaration",
                            detail: "the value isn't one command; write one command as a string under [stages]".into(),
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

/// The command a stage resolves to, or why it resolves to none, for a runner
/// that holds the command itself (SPC-1201).
#[cfg(feature = "loop")]
pub(crate) fn command_of(root: &Path, verb: &str) -> std::result::Result<String, String> {
    match resolve(root, &Scope::repository(root))
        .verbs
        .into_iter()
        .find(|(name, _)| *name == verb)
    {
        Some((_, Entry::Resolved { command, .. })) => Ok(command),
        Some((_, Entry::Unresolved { kind, detail })) => Err(format!("{kind}: {detail}")),
        None => Err(format!("{verb} is not a stage")),
    }
}

/// A stage declared as a table: `command` for the whole work, and an optional
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
        source: PROFILE,
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

fn status(root: &Path, scope: &Scope, as_json: bool) -> u8 {
    let report = resolve(root, scope);
    if as_json {
        let mut verbs = Map::new();
        for (verb, entry) in &report.verbs {
            let value = match entry {
                Entry::Resolved {
                    command,
                    subset,
                    source,
                } => {
                    json!({"state": "resolved", "command": command, "subset": subset, "source": source})
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
        let directory = scope.part.as_ref().map(|part| part.directory.as_str());
        let part = scope.part.as_ref().map(|part| part.name.as_str());
        let out = json!({
            "profile": profile,
            "profile_state": report.state,
            "scope": {"part": part, "directory": directory},
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
    println!("{}", scope.line());
    println!();
    for (verb, entry) in &report.verbs {
        match entry {
            Entry::Resolved {
                command,
                subset,
                source,
            } => {
                println!("{verb:<10} resolved    {command}   (from {source})");
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

/// What one recorded run of a stage's command left behind.
#[cfg(feature = "loop")]
pub(crate) struct Ran {
    pub status: i32,
    /// The tree id before the command ran and after it.
    pub before: String,
    pub after: String,
    /// The ledger record's identifier, or why nothing was recorded.
    pub recorded: std::result::Result<String, String>,
}

/// Runs a stage's whole command and records the result in the ledger with the
/// tree before and after it, as `run` does, for a runner that decides from the
/// exit status itself (SPC-1201). A command that never started is an error and
/// is recorded as unresolved, because an unresolved stage is never a pass.
#[cfg(feature = "loop")]
pub(crate) fn run_recorded(
    root: &Path,
    verb: &str,
    command: &str,
) -> std::result::Result<Ran, String> {
    let before = ledger::tree_id(root);
    let started = ledger::start(root, verb, command, None, &before, "repository");
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
            scope: "repository",
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

fn run(root: &Path, scope: &Scope, args: &[String]) -> u8 {
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
            "meow-checks run: name the stages to run, from: {}",
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
            "meow-checks run: {} isn't a stage; the five are {}",
            unknown.join(", "),
            VERBS.join(" ")
        );
        return USAGE;
    }

    let report = resolve(root, scope);
    for line in &report.profile {
        println!("{line}");
    }
    println!("{}", scope.line());
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
            .expect("a known stage")
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
                        scope: scope.label(),
                    },
                    None,
                );
                continue;
            }
            Entry::Resolved {
                command, subset, ..
            } => match (targets, subset) {
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
                        "the profile declares no `subset` for {name}; declare one under [stages.{name}] with {TARGETS}, or run the whole stage"
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
                            scope: scope.label(),
                        },
                        None,
                    );
                    continue;
                }
            },
        };
        let command = &command;
        let before = ledger::tree_id(root);
        let record = ledger::start(root, name, command, targets, &before, scope.label());
        let started = Instant::now();
        let (code, output) = execute(&scope.directory, command);
        let after = ledger::tree_id(root);
        // A stage ended by an interrupt or a termination signal says the run
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
                scope: scope.label(),
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

/// Whether each stage's latest recorded result holds for the tree as it is
/// now: 0 when every one passed on it, 1 when one failed, went stale or
/// changed during its run, and 3 when one has no record, was unresolved or is
/// bound to no tree (REQ-0146, REQ-0148).
fn evidence(root: &Path, scope: &Scope, args: &[String]) -> u8 {
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
            "meow-checks evidence: {} isn't a stage; the five are {}",
            unknown.join(", "),
            VERBS.join(" ")
        );
        return USAGE;
    }
    println!("{}", scope.line());
    // A record from before scopes were kept covered the repository.
    let records: Vec<Value> = ledger::records(root)
        .into_iter()
        .filter(|r| {
            r.get("scope")
                .and_then(Value::as_str)
                .unwrap_or("repository")
                == scope.label()
        })
        .collect();
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
        println!(
            "no stage has a record for this work tree; run one with `meow-checks run <stage>`"
        );
        return UNRESOLVED;
    }
    let now = ledger::tree_id(root);
    let (mut failed, mut unresolved, mut interrupted) = (false, false, false);
    for verb in &wanted {
        // A subset record never stands for the whole stage (ADR-1520); a record
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
            let counted = match latest.get("revision").and_then(Value::as_u64) {
                Some(then) => format!(", revision {then}, now {}", ledger::revision(root)),
                None => String::new(),
            };
            println!("{head}, current at tree {}{counted}", ledger::short(&tree));
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

/// Adds one to the work tree's revision counter for a tool use that ended,
/// failed or not. It reads its input to the end and keeps none of it, prints
/// nothing, and writes nothing where state writing is off (REQ-2724,
/// REQ-2728).
fn revision(root: &Path) -> u8 {
    use std::io::Read;
    let mut sink = Vec::new();
    let _ = std::io::stdin().read_to_end(&mut sink);
    match ledger::advance(root) {
        Ok(_) => PASSED,
        Err(_) if ledger::state_off() => PASSED,
        Err(reason) => {
            eprintln!("meow-checks revision: {reason}");
            FAILED
        }
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
            println!("revision: {}", ledger::revision(root));
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

/// Where git keeps the exclude file of the working tree at `root`, or why
/// there is no working tree there (REQ-2944).
fn exclude_file(root: &Path) -> std::result::Result<std::path::PathBuf, String> {
    let done = profile::reading_git()
        .args(["rev-parse", "--git-path", "info/exclude"])
        .current_dir(root)
        .output()
        .map_err(|error| format!("can't start git: {error}"))?;
    let text = String::from_utf8_lossy(&done.stdout).trim().to_string();
    if !done.status.success() || text.is_empty() {
        return Err(format!(
            "{} isn't inside a git working tree, so there is nowhere to exclude the personal profile",
            root.display()
        ));
    }
    let path = std::path::PathBuf::from(text);
    Ok(if path.is_absolute() {
        path
    } else {
        root.join(path)
    })
}

/// Writes one stage into the personal profile and excludes the file from the
/// working tree, in that order of safety: the exclusion first, so the file is
/// never seen untracked (REQ-2944). It writes nothing else.
fn local(root: &Path, args: &[&str]) -> u8 {
    let [verb, command] = args else {
        eprintln!("usage: meow-checks local <stage> <command>");
        return USAGE;
    };
    if !VERBS.contains(verb) {
        eprintln!(
            "meow-checks local: {verb} isn't a stage; the five are {}",
            VERBS.join(" ")
        );
        return USAGE;
    }
    if command.trim().is_empty() {
        eprintln!("meow-checks local: the command is empty; name the command {verb} runs");
        return USAGE;
    }
    if let Some(word) = machine_path(root, command) {
        eprintln!(
            "meow-checks local: {word} is a path on this machine, and nothing was written; name the tool through the project's toolchain declaration"
        );
        return FAILED;
    }
    let exclude = match exclude_file(root) {
        Ok(path) => path,
        Err(reason) => {
            eprintln!("meow-checks local: {reason}; run it inside the repository");
            return FAILED;
        }
    };
    let file = root.join(PERSONAL);
    if std::fs::symlink_metadata(&file).is_ok_and(|meta| meta.file_type().is_symlink()) {
        eprintln!(
            "meow-checks local: {PERSONAL} is a symbolic link, and writing through it would change a file outside what this command names; replace it with a regular file"
        );
        return FAILED;
    }
    let tracked = profile::reading_git()
        .args(["ls-files", "--error-unmatch", "--", PERSONAL])
        .current_dir(root)
        .output()
        .is_ok_and(|done| done.status.success());
    if tracked {
        eprintln!(
            "meow-checks local: {PERSONAL} is tracked by git, so excluding it would hide nothing and it would stay in the repository; run `git rm --cached {PERSONAL}` and run this again"
        );
        return FAILED;
    }
    let mut table = match std::fs::read_to_string(&file) {
        Err(_) => toml::Table::new(),
        Ok(text) => match text.parse::<toml::Table>() {
            Ok(table) => table,
            Err(error) => {
                eprintln!(
                    "meow-checks local: {PERSONAL} doesn't parse ({}); fix or remove it, and nothing was written",
                    error.message().trim()
                );
                return FAILED;
            }
        },
    };
    let name = if table.contains_key("stages") || !table.contains_key("verbs") {
        "stages"
    } else {
        "verbs"
    };
    let stages = table
        .entry(name.to_string())
        .or_insert_with(|| toml::Value::Table(toml::Table::new()));
    let toml::Value::Table(stages) = stages else {
        eprintln!(
            "meow-checks local: [{name}] in {PERSONAL} isn't a table; fix it, and nothing was written"
        );
        return FAILED;
    };
    stages.insert(verb.to_string(), toml::Value::String(command.to_string()));
    let body = match toml::to_string(&table) {
        Ok(body) => body,
        Err(error) => {
            eprintln!("meow-checks local: can't write {PERSONAL}: {error}");
            return FAILED;
        }
    };
    let line = format!("/{PERSONAL}");
    let kept = std::fs::read_to_string(&exclude).unwrap_or_default();
    let write = || -> std::io::Result<()> {
        if !kept.lines().any(|l| l.trim() == line) {
            if let Some(parent) = exclude.parent() {
                std::fs::create_dir_all(parent)?;
            }
            let mut text = kept.clone();
            if !text.is_empty() && !text.ends_with('\n') {
                text.push('\n');
            }
            text.push_str(&line);
            text.push('\n');
            std::fs::write(&exclude, text)?;
        }
        if let Some(parent) = file.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let temporary = file.with_extension("toml.tmp");
        std::fs::write(&temporary, &body)?;
        std::fs::rename(&temporary, &file).inspect_err(|_| {
            let _ = std::fs::remove_file(&temporary);
        })
    };
    match write() {
        Ok(()) => {
            println!("{PERSONAL}: {verb} = {command}");
            println!("excluded through {}", exclude.display());
            PASSED
        }
        Err(error) => {
            eprintln!("meow-checks local: {error}");
            FAILED
        }
    }
}

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 7] = [
    crate::help::Entry {
        name: "status",
        determines: "how each of the five stages resolves from the profile, and from where",
        by_hand: "read the `[stages]` table of `.meowpaw/profile.toml`, then `.meowpaw/profile.local.toml` for a command it overrides",
        lines: "meow-checks profile: unknown personal scope: format lint check test build subset notice:",
        json: "profile profile_state scope error notices unknown verbs",
    },
    crate::help::Entry {
        name: "run",
        determines: "the result of each stage the profile binds, run in order, and records it",
        by_hand: "run each stage's command from the profile's `[stages]` table from the repository's root and read its exit status",
        lines: "profile: unknown personal scope: == -- passed, failed, interrupted summary: recorded: notice: pruned not",
        json: "",
    },
    crate::help::Entry {
        name: "evidence",
        determines: "whether each stage has a record of a whole run that is current at this tree",
        by_hand: "read the ledger file `meow-checks state` names, where each line is one record with its stage, its result and the tree it ran at, and compare that tree with `meow-checks tree HEAD`",
        lines: "scope: format: lint: check: test: build: no ==",
        json: "",
    },
    crate::help::Entry {
        name: "state",
        determines: "where the evidence ledger is and what it holds",
        by_hand: "read the ledger file `meow-checks state` names, which holds one JSON record on each line, and count them",
        lines: "ledger: records: oldest: newest: lock: revision: purged state no",
        json: "",
    },
    crate::help::Entry {
        name: "revision",
        determines: "that a tool use ended, by adding one to the work tree's revision counter",
        by_hand: "add one to the number in the counter file beside the ledger `meow-checks state` names, and write nothing the hook read",
        lines: "meow-checks",
        json: "",
    },
    crate::help::Entry {
        name: "tree",
        determines: "the tree a commit names",
        by_hand: "run `git rev-parse <commit>^{tree}`",
        lines: "<hash>",
        json: "",
    },
    crate::help::Entry {
        name: "local",
        determines: "that the command of a stage is written to the personal profile and excluded from version control",
        by_hand: "write the command under `[stages]` in `.meowpaw/profile.local.toml` and add the file to `.git/info/exclude`",
        lines: ".meowpaw/profile.local.toml: excluded",
        json: "",
    },
];

pub fn main(args: &[String]) -> u8 {
    if let Some(code) = crate::help::answer("meow-checks", &HELP, args) {
        return code;
    }
    let root = profile::repository_root();
    // `status`, `run` and `evidence` take `--part <name>` (REQ-3042).
    let scoped = matches!(
        args.first().map(String::as_str),
        Some("status" | "run" | "evidence")
    );
    let (scope, args) = if scoped {
        match scope_of(&root, &args[0], &args[1..]) {
            Ok((scope, rest)) => (scope, [&args[..1], &rest[..]].concat()),
            Err(code) => return code,
        }
    } else {
        (Scope::repository(&root), args.to_vec())
    };
    let args: Vec<&str> = args.iter().map(String::as_str).collect();
    match args.as_slice() {
        ["status"] => status(&root, &scope, false),
        ["status", "--json"] => status(&root, &scope, true),
        ["run", rest @ ..] => run(
            &root,
            &scope,
            &rest.iter().map(|s| s.to_string()).collect::<Vec<_>>(),
        ),
        ["revision"] => revision(&root),
        ["state", rest @ ..] => state(&root, rest),
        ["local", rest @ ..] => local(&root, rest),
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
            &scope,
            &rest.iter().map(|s| s.to_string()).collect::<Vec<_>>(),
        ),
        _ => {
            eprintln!(
                "usage: meow-checks status [--json] [--part <name>] | meow-checks run <stage>... [--part <name>] [-- <target>...] | meow-checks evidence [--all] [--part <name>] [verb...] | meow-checks state [--purge] | meow-checks tree <commit> | meow-checks local <stage> <command>"
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
        let resolve = |dir: std::path::PathBuf| super::resolve(&dir, &Scope::repository(&dir));
        let stages = resolve(profile_in("stages", "[stages]\ntest = \"run-tests\"\n"));
        assert_eq!(resolved(&stages, "test").as_deref(), Some("run-tests"));
        assert_eq!(stages.profile, ["profile: parsed"]);
        let verbs = resolve(profile_in("verbs", "[verbs]\ntest = \"run-tests\"\n"));
        assert_eq!(resolved(&verbs, "test").as_deref(), Some("run-tests"));
        assert!(
            verbs.profile.iter().any(|line| line.contains("[stages]")),
            "{:?}",
            verbs.profile
        );
    }

    #[test]
    fn a_command_that_never_started_is_not_an_exit_status() {
        // SPC-1201: an unspawned stage counts neither as a pass nor as a fail.
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
