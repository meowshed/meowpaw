// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-gotask`: what Task resolves in a work tree, and the verbs bound to
//! its tasks (SPC-1150).
//!
//! Task's listing carries a name and a file and nothing that changes what a
//! pass means, so every block is read from the Taskfile itself (RES-0127). The
//! listing runs with `TASK_TEMP_DIR` outside the repository, because a listing
//! that writes its checksums there makes the next run skip a task that never
//! ran.

use crate::runner::{self, Resolved, Runner, Task, Tree, Unresolved, last_lines, version_of};
use regex::Regex;
use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};
use yaml_rust2::{Yaml, YamlLoader};

/// The Task the pack was tested on: a flag rejected below it is the
/// environment's, and at or above it the pack's.
const TESTED: [u32; 3] = [3, 53, 1];
/// Task's own order of preference among the names it accepts (RES-0123).
const TASKFILES: [&str; 8] = [
    "Taskfile.yml",
    "taskfile.yml",
    "Taskfile.yaml",
    "taskfile.yaml",
    "Taskfile.dist.yml",
    "taskfile.dist.yml",
    "Taskfile.dist.yaml",
    "taskfile.dist.yaml",
];
const RUNNER: Runner = Runner {
    unit: "meow-gotask",
    runs: &["task"],
    binding,
    skip: "as up to date",
};

fn binding(task: &str) -> String {
    format!("task --force {task}")
}

pub fn main(args: &[String]) -> u8 {
    match args
        .iter()
        .map(String::as_str)
        .collect::<Vec<_>>()
        .as_slice()
    {
        ["status"] => runner::status(&RUNNER, resolve),
        ["bind"] => runner::bind(&RUNNER, resolve),
        ["check"] => runner::check(&RUNNER, remote_findings(), resolve),
        _ => {
            eprintln!("usage: meow-gotask status | bind | check");
            2
        }
    }
}

/// Each Taskfile read from the root through local includes, parsed, by path.
struct Taskfiles {
    parsed: BTreeMap<PathBuf, Yaml>,
    /// Each local Taskfile with the namespace its tasks list under.
    namespaces: Vec<(PathBuf, String)>,
    remote: Vec<String>,
}

fn root_taskfile(root: &Path) -> Option<PathBuf> {
    TASKFILES
        .iter()
        .map(|name| root.join(name))
        .find(|p| p.is_file())
}

fn taskfile_in(path: &Path) -> Option<PathBuf> {
    if path.is_dir() {
        TASKFILES
            .iter()
            .map(|name| path.join(name))
            .find(|p| p.is_file())
    } else {
        path.is_file().then(|| path.to_path_buf())
    }
}

fn is_remote(source: &str) -> bool {
    source.contains("://") || source.starts_with("git::")
}

/// Every Taskfile the root reaches through local includes, and each remote
/// include among them, read before anything is listed (REQ-2486).
fn read_taskfiles(tree: &Tree, root_file: &Path) -> Result<Taskfiles, String> {
    let mut found = Taskfiles {
        parsed: BTreeMap::new(),
        namespaces: Vec::new(),
        remote: Vec::new(),
    };
    let mut pending = vec![(root_file.to_path_buf(), String::new())];
    let mut seen = BTreeSet::new();
    while let Some((file, namespace)) = pending.pop() {
        let file = std::fs::canonicalize(&file).unwrap_or(file);
        if !seen.insert(file.clone()) {
            continue;
        }
        let shown = tree.display(&file);
        let text =
            std::fs::read_to_string(&file).map_err(|e| format!("{shown} can't be read: {e}"))?;
        let doc = YamlLoader::load_from_str(&text)
            .map_err(|e| format!("{shown} doesn't parse: {e}"))?
            .into_iter()
            .next()
            .unwrap_or(Yaml::Null);
        if let Some(includes) = doc["includes"].as_hash() {
            for (name, include) in includes {
                let name = name.as_str().unwrap_or_default();
                let source = include
                    .as_str()
                    .or_else(|| include["taskfile"].as_str())
                    .unwrap_or_default();
                if is_remote(source) {
                    found
                        .remote
                        .push(format!("remote include {name}: {source} ({shown})"));
                } else if let Some(next) =
                    taskfile_in(&file.parent().unwrap_or(Path::new(".")).join(source))
                {
                    let flatten = include["flatten"].as_bool() == Some(true);
                    let inner = if flatten {
                        namespace.clone()
                    } else {
                        format!("{namespace}{name}:")
                    };
                    pending.push((next, inner));
                }
            }
        }
        found.namespaces.push((file.clone(), namespace));
        found.parsed.insert(file, doc);
    }
    found.remote.sort();
    Ok(found)
}

/// Remote includes as `check` findings, which it reports whether or not a
/// verb runs a task from one (REQ-2487).
fn remote_findings() -> Vec<String> {
    let tree = Tree::read();
    let Some(file) = root_taskfile(&tree.root) else {
        return Vec::new();
    };
    read_taskfiles(&tree, &file)
        .map(|found| found.remote)
        .unwrap_or_default()
}

fn task_command(root: &Path, args: &[&str], temporary: Option<&Path>) -> std::io::Result<Output> {
    let mut command = Command::new("task");
    command.args(args).current_dir(root).stdin(Stdio::null());
    if let Some(directory) = temporary {
        command.env("TASK_TEMP_DIR", directory);
    }
    command.output()
}

/// A directory of the program's own outside the repository, removed on drop.
struct Temporary(PathBuf);

impl Temporary {
    fn new() -> std::io::Result<Temporary> {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0);
        let path = std::env::temp_dir().join(format!("meow-gotask-{}-{stamp}", std::process::id()));
        std::fs::create_dir_all(&path)?;
        Ok(Temporary(path))
    }
}

impl Drop for Temporary {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn resolve() -> Result<Resolved, Unresolved> {
    let tree = Tree::read();
    let mut report = Vec::new();
    let unresolved = |report: &Vec<String>, reason: String| Unresolved {
        report: report.clone(),
        reason,
    };
    let Some(root_file) = root_taskfile(&tree.root) else {
        return Err(unresolved(&report, "not a Task repository".into()));
    };
    let version = match task_command(&tree.root, &["--version"], None) {
        Ok(done) => String::from_utf8_lossy(&done.stdout)
            .lines()
            .next()
            .unwrap_or("")
            .trim()
            .to_string(),
        Err(_) => return Err(unresolved(&report, "task not found".into())),
    };
    report.push(format!("task: {version}"));
    let taskfiles =
        read_taskfiles(&tree, &root_file).map_err(|reason| unresolved(&report, reason))?;
    if !taskfiles.remote.is_empty() {
        report.extend(taskfiles.remote.iter().cloned());
        return Err(unresolved(&report, "remote include".into()));
    }
    let temporary = Temporary::new().map_err(|e| {
        unresolved(
            &report,
            format!("no temporary directory for the listing: {e}"),
        )
    })?;
    let listing = task_command(&tree.root, &["--list-all", "--json"], Some(&temporary.0))
        .map_err(|e| unresolved(&report, format!("task failed: {e}")))?;
    if !listing.status.success() {
        let stderr = String::from_utf8_lossy(&listing.stderr).into_owned();
        return Err(unresolved(
            &report,
            listing_failure(&stderr, &version, listing.status.code()),
        ));
    }
    let stdout = String::from_utf8_lossy(&listing.stdout).into_owned();
    let Some(entries) = recognised(&stdout) else {
        let shown: String = stdout.trim().chars().take(200).collect();
        return Err(unresolved(&report, format!("unrecognised shape: {shown}")));
    };
    report.push(
        "listing ran task over the Taskfile, with its temporary directory outside the repository"
            .into(),
    );
    let listed: BTreeMap<String, PathBuf> = entries
        .iter()
        .map(|e| {
            (
                e["name"].as_str().unwrap_or_default().to_string(),
                PathBuf::from(e["location"]["taskfile"].as_str().unwrap_or_default()),
            )
        })
        .collect();
    let mut known = Definitions {
        parsed: taskfiles.parsed.clone(),
        listed,
    };
    let tasks = entries
        .iter()
        .map(|entry| task(&tree, &mut known, entry))
        .collect();
    let unlisted = internal_tasks(&taskfiles);
    let carried = secret_variables(&tree, &taskfiles);
    Ok(Resolved {
        report,
        tasks,
        carried,
        unlisted,
    })
}

/// A listing's failure, named for what it is and never read as an empty list.
fn listing_failure(stderr: &str, version: &str, code: Option<i32>) -> String {
    if matches!(code, Some(104) | Some(106)) {
        // Neither says the person didn't trust it: the listing reads no trust or cache (RES-0127).
        return "a remote Taskfile this listing can't see, since it reads no trust or cache".into();
    }
    let flag =
        Regex::new(r"unknown (?:shorthand )?flag: '?(-{1,2}[A-Za-z0-9-]+)").expect("flag pattern");
    if let Some(found) = flag.captures(stderr) {
        let flag = &found[1];
        let number = version.split_whitespace().last().unwrap_or("unknown");
        return match version_of(version) {
            Some(v) if v < TESTED.to_vec() => format!("environment: task {number} predates {flag}"),
            _ => format!("meow-gotask defect: {flag}"),
        };
    }
    let status = code.map_or("a signal".to_string(), |c| c.to_string());
    format!(
        "task failed with exit status {status}: {}",
        last_lines(stderr)
    )
}

/// The listing's tasks, where it is an object whose `tasks` each name a task
/// and the Taskfile declaring it; anything else is another shape (REQ-2462).
fn recognised(stdout: &str) -> Option<Vec<serde_json::Map<String, Value>>> {
    let Ok(Value::Object(mut listing)) = serde_json::from_str::<Value>(stdout) else {
        return None;
    };
    let Some(Value::Array(items)) = listing.remove("tasks") else {
        return None;
    };
    items
        .into_iter()
        .map(|item| match item {
            Value::Object(o)
                if o.get("name").is_some_and(Value::is_string)
                    && o.get("location")
                        .and_then(|l| l.get("taskfile"))
                        .is_some_and(Value::is_string) =>
            {
                Some(o)
            }
            _ => None,
        })
        .collect()
}

/// Task definitions, found through the listing and parsed on first use.
struct Definitions {
    parsed: BTreeMap<PathBuf, Yaml>,
    listed: BTreeMap<String, PathBuf>,
}

impl Definitions {
    /// The definition of a listed task, and the key it sits under in its file:
    /// the listed name, then with each leading namespace removed in turn.
    fn definition(&mut self, name: &str) -> Option<(Yaml, Yaml)> {
        let file = self.listed.get(name)?.clone();
        let file = std::fs::canonicalize(&file).unwrap_or(file);
        if !self.parsed.contains_key(&file) {
            let text = std::fs::read_to_string(&file).ok()?;
            let doc = YamlLoader::load_from_str(&text).ok()?.into_iter().next()?;
            self.parsed.insert(file.clone(), doc);
        }
        let doc = &self.parsed[&file];
        let mut key = name;
        loop {
            let found = &doc["tasks"][key];
            if !found.is_badvalue() {
                return Some((found.clone(), doc.clone()));
            }
            key = key.split_once(':')?.1;
        }
    }

    /// The name a dependency lists under: the calling task's namespace first,
    /// then as written.
    fn dependency(&self, caller: &str, dependency: &str) -> Option<String> {
        let namespace = caller
            .rsplit_once(':')
            .map(|(n, _)| format!("{n}:"))
            .unwrap_or_default();
        [format!("{namespace}{dependency}"), dependency.to_string()]
            .into_iter()
            .find(|n| self.listed.contains_key(n))
    }
}

/// What a definition itself sets that stops a verb running it unattended.
fn own_blocks(definition: &Yaml) -> Vec<String> {
    let mut blocks = Vec::new();
    if !definition["prompt"].is_badvalue() {
        blocks.push("asks for a person".to_string());
    }
    let variables: Vec<String> = definition["requires"]["vars"]
        .as_vec()
        .map(|vars| {
            vars.iter()
                .filter_map(|v| {
                    v.as_str()
                        .or_else(|| v["name"].as_str())
                        .map(str::to_string)
                })
                .collect()
        })
        .unwrap_or_default();
    if !variables.is_empty() {
        blocks.push(format!("needs variables {}", variables.join(" ")));
    }
    let ignores = definition["ignore_error"].as_bool() == Some(true)
        || definition["cmds"].as_vec().is_some_and(|cmds| {
            cmds.iter()
                .any(|c| c["ignore_error"].as_bool() == Some(true))
        });
    if ignores {
        blocks.push("ignores errors".to_string());
    }
    if let Some(condition) = scalar(&definition["if"]) {
        blocks.push(format!("runs only if {condition}"));
    }
    if let Some(platforms) = definition["platforms"].as_vec() {
        let names: Vec<String> = platforms.iter().filter_map(scalar).collect();
        blocks.push(format!("runs only on {}", names.join(", ")));
    }
    blocks
}

fn scalar(value: &Yaml) -> Option<String> {
    match value {
        Yaml::String(s) | Yaml::Real(s) => Some(s.clone()),
        Yaml::Boolean(b) => Some(b.to_string()),
        Yaml::Integer(i) => Some(i.to_string()),
        _ => None,
    }
}

/// The tasks a definition runs: its `deps` and each `task:` its `cmds` call.
fn called(definition: &Yaml) -> Vec<String> {
    let mut names = Vec::new();
    for dep in definition["deps"].as_vec().into_iter().flatten() {
        if let Some(name) = dep.as_str().or_else(|| dep["task"].as_str()) {
            names.push(name.to_string());
        }
    }
    for cmd in definition["cmds"].as_vec().into_iter().flatten() {
        if let Some(name) = cmd["task"].as_str() {
            names.push(name.to_string());
        }
    }
    names
}

/// A task's own blocks and those it takes on through what it calls, each of
/// the latter naming the task it came through (REQ-2480).
fn blocks_through(
    known: &mut Definitions,
    name: &str,
    seen: &mut BTreeSet<String>,
) -> Option<Vec<String>> {
    if !seen.insert(name.to_string()) {
        return Some(Vec::new());
    }
    let (definition, _) = known.definition(name)?;
    let mut blocks = own_blocks(&definition);
    for callee in called(&definition) {
        let Some(listed) = known.dependency(name, &callee) else {
            continue;
        };
        for block in blocks_through(known, &listed, seen)
            .unwrap_or_else(|| vec!["unknown definition".into()])
        {
            let block = if block.contains(", through ") {
                block
            } else {
                format!("{block}, through {callee}")
            };
            if !blocks.contains(&block) {
                blocks.push(block);
            }
        }
    }
    Some(blocks)
}

fn task(tree: &Tree, known: &mut Definitions, entry: &serde_json::Map<String, Value>) -> Task {
    let name = entry["name"].as_str().unwrap_or_default().to_string();
    let source_path = PathBuf::from(entry["location"]["taskfile"].as_str().unwrap_or_default());
    let relative = tree.relative(&source_path);
    let origin = tree.origin(relative.as_deref());
    let source = tree.display(&source_path);
    let mut notes = Vec::new();
    let (mut blocks, can_skip) = match (
        blocks_through(known, &name, &mut BTreeSet::new()),
        known.definition(&name),
    ) {
        (Some(blocks), Some((definition, doc))) => {
            if blocks.iter().any(|b| b.starts_with("ignores errors")) {
                notes.push("a verb bound to it can't report the failure it ignores".to_string());
            }
            let method = scalar(&definition["method"])
                .or_else(|| scalar(&doc["method"]))
                .unwrap_or_else(|| "checksum".into());
            let skip = if !definition["status"].is_badvalue() {
                Some("decided by its status commands".to_string())
            } else if !definition["sources"].is_badvalue() && method != "none" {
                Some(format!("decided by the {method} of its sources"))
            } else {
                None
            };
            if let Some(skip) = &skip {
                notes.push(format!("can skip as up to date: {skip}"));
            }
            (blocks, Some(skip.is_some()))
        }
        _ => (vec!["unknown definition".to_string()], None),
    };
    if origin != "repository" {
        blocks.push("not committed".to_string());
    }
    Task {
        name,
        origin,
        source,
        replaced: None,
        blocks,
        notes,
        can_skip,
    }
}

/// Tasks a Taskfile declares internal, which the listing leaves out, so a verb
/// naming one reads as internal and never as missing.
fn internal_tasks(taskfiles: &Taskfiles) -> Vec<(String, String)> {
    let mut internal = Vec::new();
    for (file, namespace) in &taskfiles.namespaces {
        let Some(tasks) = taskfiles
            .parsed
            .get(file)
            .and_then(|doc| doc["tasks"].as_hash())
        else {
            continue;
        };
        for (name, definition) in tasks {
            if definition["internal"].as_bool() == Some(true) {
                internal.push((
                    format!("{namespace}{}", name.as_str().unwrap_or_default()),
                    "internal".to_string(),
                ));
            }
        }
    }
    internal
}

/// Each variable a Taskfile marks secret, named and never shown, because
/// Task masks it only where it echoes a command (REQ-2510).
fn secret_variables(tree: &Tree, taskfiles: &Taskfiles) -> Vec<String> {
    let mut lines = Vec::new();
    for (file, doc) in &taskfiles.parsed {
        let shown = tree.display(file);
        let mut scopes = vec![&doc["vars"]];
        if let Some(tasks) = doc["tasks"].as_hash() {
            scopes.extend(tasks.values().map(|t| &t["vars"]));
        }
        for vars in scopes.into_iter().filter_map(Yaml::as_hash) {
            for (name, value) in vars {
                if value["secret"].as_bool() == Some(true) {
                    lines.push(format!(
                        "  {} ({shown}): masked in Task's output, not protected",
                        name.as_str().unwrap_or_default()
                    ));
                }
            }
        }
    }
    if lines.is_empty() {
        return lines;
    }
    lines.insert(0, "secret variables:".to_string());
    lines
}
