// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-mise`: what mise resolves in a work tree (SPC-1140).
//!
//! The program asks mise and reads the repository's committed files, and it
//! runs no task, grants no trust and writes nothing (REQ-2466, REQ-2504).
//! Every state that would otherwise read as "no tasks" is reported as itself
//! and exits 3, because an empty list nobody could read is not a list.

use crate::profile;
use regex::Regex;
use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

const UNRESOLVED: u8 = 3;
/// The mise the pack was tested on: a flag rejected below it is the
/// environment's, and at or above it the pack's (REQ-2496).
const TESTED: [u32; 3] = [2026, 9, 11];
const TASK_DIRECTORIES: [&str; 5] = ["mise-tasks/", ".mise-tasks/", "mise/tasks/", ".mise/tasks/", ".config/mise/tasks/"];
const CONFIGURATION: [&str; 6] = ["mise.toml", ".mise.toml", "mise/config.toml", ".mise/config.toml", ".config/mise/config.toml", ".config/mise.toml"];
const CONF_D: [&str; 3] = ["mise/conf.d/", ".mise/conf.d/", ".config/mise/conf.d/"];

pub fn main(args: &[String]) -> u8 {
    match args.iter().map(String::as_str).collect::<Vec<_>>().as_slice() {
        ["status"] => status(),
        _ => {
            eprintln!("usage: meow-mise status");
            2
        }
    }
}

fn status() -> u8 {
    println!("meow-mise status");
    match resolve() {
        Ok(resolved) => {
            print_resolved(&resolved);
            0
        }
        Err(Unresolved { report, reason }) => {
            for line in report {
                println!("{line}");
            }
            println!("unresolved: {reason}");
            UNRESOLVED
        }
    }
}

/// A state the program couldn't read past, with what it had printed so far.
struct Unresolved {
    report: Vec<String>,
    reason: String,
}

struct Resolved {
    report: Vec<String>,
    tasks: Vec<Task>,
    carried: Vec<String>,
}

pub struct Task {
    pub name: String,
    pub origin: &'static str,
    pub source: String,
    pub replaced: Option<String>,
    pub blocks: Vec<String>,
    pub can_skip: Option<bool>,
    pub confirm_unknown: bool,
}

/// The work tree: its canonical root and the files git tracks in it.
struct Tree {
    root: PathBuf,
    tracked: BTreeSet<String>,
}

impl Tree {
    fn read() -> Tree {
        let root = profile::repository_root();
        let root = std::fs::canonicalize(&root).unwrap_or(root);
        let mut tracked = BTreeSet::new();
        if let Ok(done) = profile::reading_git().args(["ls-files", "-z"]).current_dir(&root).output() {
            for path in done.stdout.split(|b| *b == 0).filter(|p| !p.is_empty()) {
                tracked.insert(String::from_utf8_lossy(path).into_owned());
            }
        }
        Tree { root, tracked }
    }

    /// A path relative to the root where it lies inside it.
    fn relative(&self, path: &Path) -> Option<String> {
        let path = std::fs::canonicalize(path).unwrap_or_else(|_| path.to_path_buf());
        path.strip_prefix(&self.root).ok().map(|p| p.to_string_lossy().into_owned())
    }

    fn display(&self, path: &Path) -> String {
        self.relative(path).unwrap_or_else(|| path.display().to_string())
    }

    fn committed_configuration(&self) -> Vec<&String> {
        self.tracked.iter().filter(|p| is_configuration(p)).collect()
    }
}

fn is_configuration(path: &str) -> bool {
    let environment = Regex::new(r"^\.?mise\.[^/]+\.toml$").expect("environment pattern");
    CONFIGURATION.contains(&path)
        || environment.is_match(path)
        || CONF_D.iter().any(|d| path.starts_with(d) && path.ends_with(".toml") && !path[d.len()..].contains('/'))
}

/// A static read for the markers, so a tree without one starts no mise (REQ-2472).
fn detected(root: &Path) -> bool {
    let environment = Regex::new(r"^\.?mise\.[^/]+\.toml$").expect("environment pattern");
    CONFIGURATION.iter().any(|p| root.join(p).is_file())
        || TASK_DIRECTORIES.iter().any(|d| root.join(d).is_dir())
        || CONF_D.iter().any(|d| root.join(d).is_dir())
        || std::fs::read_dir(root)
            .map(|entries| entries.flatten().any(|e| environment.is_match(&e.file_name().to_string_lossy())))
            .unwrap_or(false)
}

fn mise(root: &Path, args: &[&str]) -> std::io::Result<Output> {
    Command::new("mise").args(args).current_dir(root).stdin(Stdio::null()).output()
}

fn version_of(text: &str) -> Option<[u32; 3]> {
    let token = text.split_whitespace().next()?;
    let parts: Vec<u32> = token.split('.').map(|p| p.parse().ok()).collect::<Option<_>>()?;
    (parts.len() == 3).then(|| [parts[0], parts[1], parts[2]])
}

fn last_lines(text: &str) -> String {
    let lines: Vec<&str> = text.lines().map(str::trim).filter(|l| !l.is_empty()).collect();
    lines[lines.len().saturating_sub(3)..].join(" / ")
}

fn resolve() -> Result<Resolved, Unresolved> {
    let tree = Tree::read();
    let mut report = Vec::new();
    let unresolved = |report: &Vec<String>, reason: String| Unresolved { report: report.clone(), reason };
    if !detected(&tree.root) {
        return Err(unresolved(&report, "not a mise repository".into()));
    }
    let version = match mise(&tree.root, &["--version"]) {
        Ok(done) => String::from_utf8_lossy(&done.stdout).lines().next().unwrap_or("").trim().to_string(),
        Err(_) => return Err(unresolved(&report, "mise not found".into())),
    };
    report.push(format!("mise: {version}"));
    if let Ok(done) = mise(&tree.root, &["trust", "--show"]) {
        report.push("trust:".into());
        for line in String::from_utf8_lossy(&done.stdout).lines().filter(|l| !l.trim().is_empty()) {
            report.push(format!("  {}", line.trim()));
        }
    }
    let listing = mise(&tree.root, &["tasks", "ls", "--json", "--hidden"]).map_err(|e| unresolved(&report, format!("mise failed: {e}")))?;
    let stderr = String::from_utf8_lossy(&listing.stderr).into_owned();
    if !listing.status.success() {
        return Err(unresolved(&report, listing_failure(&stderr, &version, listing.status.code())));
    }
    let stdout = String::from_utf8_lossy(&listing.stdout).into_owned();
    let Some(entries) = recognised(&stdout) else {
        let shown: String = stdout.trim().chars().take(200).collect();
        return Err(unresolved(&report, format!("unrecognised shape: {shown}")));
    };
    let exec: Vec<&String> = tree
        .committed_configuration()
        .into_iter()
        .filter(|p| std::fs::read_to_string(tree.root.join(p)).is_ok_and(|t| t.contains("exec(")))
        .collect();
    report.push(if exec.is_empty() {
        "listing ran mise over the configuration; no committed configuration file calls exec".into()
    } else {
        let names: Vec<&str> = exec.iter().map(|s| s.as_str()).collect();
        format!("listing ran mise over the configuration; templates calling exec, evaluated by the listing: {}", names.join(", "))
    });
    let declared = declared_by_commits(&tree);
    let tasks = entries.iter().map(|entry| task(&tree, &declared, entry)).collect();
    let mut carried = pinned_tools(&tree);
    carried.extend(environment_files(&tree));
    carried.extend(idiomatic_files(&tree));
    Ok(Resolved { report, tasks, carried })
}

/// A listing's failure, named for what it is and never read as an empty list.
fn listing_failure(stderr: &str, version: &str, code: Option<i32>) -> String {
    if let Some(at) = stderr.find("Config files in ") {
        let rest = &stderr[at + "Config files in ".len()..];
        if let Some(end) = rest.find(" are not trusted") {
            let file = PathBuf::from(&rest[..end]);
            let directory = file.parent().map(Path::to_path_buf).unwrap_or(file);
            let directory = std::fs::canonicalize(&directory).unwrap_or(directory);
            let shown = directory.display();
            return format!("untrusted {shown}; a person runs mise trust {shown} after reading it");
        }
    }
    if stderr.contains("not trusted") {
        return format!("untrusted: {}", last_lines(stderr));
    }
    let flag = Regex::new(r"unexpected argument '([^']+)'").expect("flag pattern");
    if let Some(found) = flag.captures(stderr) {
        let flag = &found[1];
        let number = version.split_whitespace().next().unwrap_or("unknown");
        return match version_of(version) {
            Some(v) if v < TESTED => format!("environment: mise {number} predates {flag}"),
            _ => format!("meow-mise defect: {flag}"),
        };
    }
    let status = code.map_or("a signal".to_string(), |c| c.to_string());
    format!("mise failed with exit status {status}: {}", last_lines(stderr))
}

/// The listing's entries, where it is an array of objects each naming a task
/// and its source; anything else is another shape (REQ-2462).
fn recognised(stdout: &str) -> Option<Vec<serde_json::Map<String, Value>>> {
    let Ok(Value::Array(items)) = serde_json::from_str::<Value>(stdout) else { return None };
    items
        .into_iter()
        .map(|item| match item {
            Value::Object(o) if o.get("name").is_some_and(Value::is_string) && o.get("source").is_some_and(Value::is_string) => Some(o),
            _ => None,
        })
        .collect()
}

/// Each task a committed file declares, with the files declaring it.
fn declared_by_commits(tree: &Tree) -> BTreeMap<String, Vec<String>> {
    let mut declared: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for file in tree.committed_configuration() {
        let Ok(text) = std::fs::read_to_string(tree.root.join(file)) else { continue };
        let Ok(table) = text.parse::<toml::Table>() else { continue };
        if let Some(toml::Value::Table(tasks)) = table.get("tasks") {
            for name in tasks.keys() {
                declared.entry(name.clone()).or_default().push(file.clone());
            }
        }
    }
    for file in &tree.tracked {
        if let Some(directory) = TASK_DIRECTORIES.iter().find(|d| file.starts_with(*d)) {
            let name = file[directory.len()..].replace('/', ":");
            declared.entry(name).or_default().push(file.clone());
        }
    }
    declared
}

fn task(tree: &Tree, declared: &BTreeMap<String, Vec<String>>, entry: &serde_json::Map<String, Value>) -> Task {
    let name = entry["name"].as_str().unwrap_or_default().to_string();
    let source_path = PathBuf::from(entry["source"].as_str().unwrap_or_default());
    let relative = tree.relative(&source_path);
    let origin = match &relative {
        Some(r) if tree.tracked.contains(r) => "repository",
        Some(_) => "work tree only",
        None => "outside",
    };
    let source = tree.display(&source_path);
    let replaced = declared
        .get(&name)
        .filter(|files| !relative.as_ref().is_some_and(|r| files.contains(r)))
        .map(|files| format!("replaced by {source}; {} declares it", files.join(", ")));
    let mut blocks = Vec::new();
    match entry.get("hide").and_then(Value::as_bool) {
        Some(true) => blocks.push("hidden".to_string()),
        Some(false) => {}
        None => blocks.push("unknown hide".to_string()),
    }
    let committed = origin == "repository" && replaced.is_none();
    let mut confirm_unknown = false;
    if committed {
        if asks_for_a_person(tree, relative.as_deref().unwrap_or_default(), &name) {
            blocks.push("asks for a person".to_string());
        }
    } else {
        confirm_unknown = true;
    }
    match required_arguments(tree, entry, &name) {
        Some(needed) if needed.is_empty() => {}
        Some(needed) => blocks.push(format!("needs {}", needed.join(" "))),
        None => blocks.push("unknown arguments".to_string()),
    }
    if !committed {
        blocks.push("not committed".to_string());
    }
    let listed = |field: &str| entry.get(field).and_then(Value::as_array).map(|a| !a.is_empty());
    let can_skip = match (listed("sources"), listed("outputs")) {
        (Some(s), Some(o)) => Some(s && o),
        _ => None,
    };
    Task { name, origin, source, replaced, blocks, can_skip, confirm_unknown }
}

/// Whether the task's committed definition sets `confirm`, which mise's
/// listing leaves out (RES-0126).
fn asks_for_a_person(tree: &Tree, file: &str, name: &str) -> bool {
    let Ok(text) = std::fs::read_to_string(tree.root.join(file)) else { return false };
    if is_configuration(file) {
        let Ok(table) = text.parse::<toml::Table>() else { return false };
        return table.get("tasks").and_then(|t| t.get(name)).and_then(toml::Value::as_table).is_some_and(|t| t.contains_key("confirm"));
    }
    let header = Regex::new(r"^\s*(?:#|//)\s*(?:\[MISE\]|MISE)\s+confirm\s*=").expect("confirm pattern");
    text.lines().any(|line| header.is_match(line))
}

/// The task's required arguments and flags, read from `mise tasks info`,
/// never found by running it (REQ-2476); `None` where they can't be read.
fn required_arguments(tree: &Tree, entry: &serde_json::Map<String, Value>, name: &str) -> Option<Vec<String>> {
    let usage = entry.get("usage").and_then(Value::as_str);
    let args = entry.get("args").and_then(Value::as_array);
    if usage == Some("") && args.is_some_and(|a| a.is_empty()) {
        return Some(Vec::new());
    }
    let done = mise(&tree.root, &["tasks", "info", name, "--json"]).ok().filter(|d| d.status.success())?;
    let info: Value = serde_json::from_slice(&done.stdout).ok()?;
    let command = info.get("usage_spec")?.get("cmd")?;
    let mut needed = Vec::new();
    for (field, fallback) in [("args", true), ("flags", false)] {
        for item in command.get(field).and_then(Value::as_array).into_iter().flatten() {
            if item.get("required").and_then(Value::as_bool) == Some(true) {
                let shown = item.get("usage").and_then(Value::as_str).map(str::to_string);
                let named = item.get("name").and_then(Value::as_str).map(|n| if fallback { format!("<{n}>") } else { format!("--{n}") });
                needed.push(shown.or(named)?);
            }
        }
    }
    Some(needed)
}

/// The committed configuration files, each parsed, in the order git lists them.
fn committed_tables(tree: &Tree) -> Vec<(&String, toml::Table)> {
    tree.committed_configuration()
        .into_iter()
        .filter_map(|file| std::fs::read_to_string(tree.root.join(file)).ok()?.parse::<toml::Table>().ok().map(|t| (file, t)))
        .collect()
}

/// The toolchain each committed file pins, and whether a lock records it (REQ-2482).
fn pinned_tools(tree: &Tree) -> Vec<String> {
    let mut lines = vec!["tools pinned by committed files:".to_string()];
    for (file, table) in committed_tables(tree) {
        let Some(toml::Value::Table(tools)) = table.get("tools") else { continue };
        for (tool, request) in tools {
            let version = match request {
                toml::Value::String(v) => v.clone(),
                toml::Value::Table(t) => t.get("version").and_then(toml::Value::as_str).unwrap_or("unstated").to_string(),
                toml::Value::Array(a) => a.iter().filter_map(toml::Value::as_str).collect::<Vec<_>>().join(", "),
                other => other.to_string(),
            };
            lines.push(format!("  {tool} = {version} ({file})"));
        }
    }
    let lock = if tree.tracked.contains("mise.lock") {
        "committed"
    } else if tree.root.join("mise.lock").is_file() {
        "present and not committed"
    } else {
        "not committed"
    };
    lines.push(format!("  mise.lock: {lock}"));
    lines
}

/// The files mise loads configuration and environment from, by path only,
/// since what they hold stays unread (REQ-2490).
fn environment_files(tree: &Tree) -> Vec<String> {
    let mut lines = vec!["configuration and environment loaded from:".to_string()];
    match mise(&tree.root, &["config", "ls", "--json"]).ok().filter(|d| d.status.success()) {
        Some(done) => match serde_json::from_slice::<Value>(&done.stdout) {
            Ok(Value::Array(files)) => {
                for path in files.iter().filter_map(|f| f.get("path").and_then(Value::as_str)) {
                    lines.push(format!("  {}", tree.display(Path::new(path))));
                }
            }
            _ => lines.push("  unknown: mise config ls printed a shape this program can't read".into()),
        },
        None => lines.push("  unknown: mise config ls failed".into()),
    }
    for (file, table) in committed_tables(tree) {
        let Some(directives) = table.get("env").and_then(|e| e.get("_")).and_then(toml::Value::as_table) else { continue };
        for key in ["file", "source"] {
            let values = match directives.get(key) {
                Some(toml::Value::Array(items)) => items.clone(),
                Some(one) => vec![one.clone()],
                None => Vec::new(),
            };
            for value in values {
                let path = match &value {
                    toml::Value::String(p) => Some(p.clone()),
                    toml::Value::Table(t) => t.get("path").and_then(toml::Value::as_str).map(str::to_string),
                    _ => None,
                };
                lines.push(format!("  {} (_.{key} in {file})", path.unwrap_or_else(|| "a path this program can't read".into())));
            }
        }
    }
    lines
}

/// Each idiomatic version file at the root, which mise reads only for a tool
/// its setting names (REQ-2506).
fn idiomatic_files(tree: &Tree) -> Vec<String> {
    const FILES: [(&str, &str); 7] = [
        (".python-version", "python"),
        (".node-version", "node"),
        (".nvmrc", "node"),
        (".ruby-version", "ruby"),
        (".go-version", "go"),
        (".java-version", "java"),
        (".terraform-version", "terraform"),
    ];
    let present: Vec<&(&str, &str)> = FILES.iter().filter(|(file, _)| tree.root.join(file).is_file()).collect();
    if present.is_empty() {
        return Vec::new();
    }
    let enabled: Option<Vec<String>> = mise(&tree.root, &["settings", "get", "idiomatic_version_file_enable_tools"])
        .ok()
        .filter(|d| d.status.success())
        .and_then(|d| serde_json::from_slice(&d.stdout).ok());
    let mut lines = vec!["idiomatic version files:".to_string()];
    for (file, tool) in present {
        let state = match &enabled {
            Some(tools) if tools.iter().any(|t| t == tool) => "read by mise".to_string(),
            Some(_) => format!("possibly inert, since idiomatic_version_file_enable_tools doesn't name {tool}"),
            None => format!("possibly inert, since mise didn't say whether it reads {tool}'s file"),
        };
        lines.push(format!("  {file}: {state}"));
    }
    lines
}

fn print_resolved(resolved: &Resolved) {
    for line in &resolved.report {
        println!("{line}");
    }
    println!("tasks resolved in this work tree, which may differ from what the repository declares:");
    for task in &resolved.tasks {
        println!("  {}: {} {}", task.name, task.origin, task.source);
        if let Some(replaced) = &task.replaced {
            println!("    {replaced}");
        }
        if !task.blocks.is_empty() {
            println!("    blocked: {}", task.blocks.join(", "));
        }
        if task.confirm_unknown {
            println!("    confirm unknown: its definition isn't in a committed file");
        }
        match task.can_skip {
            Some(true) => println!("    can skip as fresh: freshness decided by mise, by a method it doesn't report"),
            Some(false) => {}
            None => println!("    can skip as fresh: unknown, since the listing doesn't say"),
        }
    }
    for line in &resolved.carried {
        println!("{line}");
    }
}
