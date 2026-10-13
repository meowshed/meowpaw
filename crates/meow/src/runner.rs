// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! What every runner pack shares: the work tree, a resolved task and its
//! report, and the `status`, `bind` and `check` commands (SPC-1140, SPC-1150).
//!
//! A pack supplies how it detects and lists its runner and what blocks a task;
//! this module decides how that is reported, so the packs can't drift apart on
//! what exit 3 or a blocked task means.

use crate::detect::{self, Marker};
use crate::profile;
use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

pub const UNRESOLVED: u8 = 3;
pub const VERBS: [&str; 5] = ["format", "lint", "check", "test", "build"];

/// A state the program couldn't read past, with what it had printed so far.
pub struct Unresolved {
    pub report: Vec<String>,
    pub reason: String,
}

pub struct Resolved {
    pub report: Vec<String>,
    pub tasks: Vec<Task>,
    pub carried: Vec<String>,
    /// Tasks a committed file declares that the listing leaves out, each with why.
    pub unlisted: Vec<(String, String)>,
}

pub struct Task {
    pub name: String,
    pub origin: &'static str,
    pub source: String,
    pub replaced: Option<String>,
    pub blocks: Vec<String>,
    /// Lines printed under the task after its blocks.
    pub notes: Vec<String>,
    /// Whether the runner may skip it; `None` where the program can't tell.
    pub can_skip: Option<bool>,
}

/// How a pack names and runs its runner.
pub struct Runner {
    pub unit: &'static str,
    /// The words a stage's command starts with to run a task, such as `mise run`.
    pub runs: &'static [&'static str],
    /// The binding for a task, such as `mise run --force test`.
    pub binding: fn(&str) -> String,
    pub skip: &'static str,
    /// What a work tree with no marker is not, such as `a mise repository`.
    pub repository: &'static str,
    /// The pack's markers among the paths git tracks (SPC-1190).
    pub markers: fn(&BTreeSet<String>) -> Vec<Marker>,
}

/// The directory a pack reads, its canonical path and the files git tracks
/// under it, relative to it, with the work tree's own root and files.
pub struct Tree {
    pub root: PathBuf,
    pub tracked: BTreeSet<String>,
    top: PathBuf,
    everything: BTreeSet<String>,
}

impl Tree {
    /// The work tree's root.
    pub fn read() -> Tree {
        Tree::read_in(&profile::repository_root())
    }

    /// One directory of the work tree, which a pack activates for when it
    /// holds a marker (REQ-3048).
    pub fn read_in(directory: &Path) -> Tree {
        let top = profile::repository_root();
        let top = std::fs::canonicalize(&top).unwrap_or(top);
        let root = std::fs::canonicalize(directory).unwrap_or(directory.to_path_buf());
        Tree {
            tracked: detect::tracked(&root),
            everything: detect::tracked(&top),
            root,
            top,
        }
    }

    /// A path relative to the root where it lies inside it.
    pub fn relative(&self, path: &Path) -> Option<String> {
        let path = std::fs::canonicalize(path).unwrap_or_else(|_| path.to_path_buf());
        path.strip_prefix(&self.root)
            .ok()
            .map(|p| p.to_string_lossy().into_owned())
    }

    pub fn display(&self, path: &Path) -> String {
        self.relative(path)
            .unwrap_or_else(|| path.display().to_string())
    }

    /// Where a file a task came from lies: committed, in the work tree only, or outside (REQ-2465).
    pub fn origin(&self, path: &Path) -> &'static str {
        let path = std::fs::canonicalize(path).unwrap_or_else(|_| path.to_path_buf());
        let relative = path
            .strip_prefix(&self.top)
            .ok()
            .map(|p| p.to_string_lossy().into_owned());
        match relative {
            Some(r) if self.everything.contains(&r) => "repository",
            Some(_) => "work tree only",
            None => "outside",
        }
    }
}

pub fn version_of(text: &str) -> Option<Vec<u32>> {
    let token = text
        .split_whitespace()
        .find(|t| t.chars().next().is_some_and(|c| c.is_ascii_digit()))?;
    let token = token.trim_start_matches('v');
    token.split('.').map(|p| p.parse().ok()).collect()
}

pub fn last_lines(text: &str) -> String {
    let lines: Vec<&str> = text
        .lines()
        .map(str::trim)
        .filter(|l| !l.is_empty())
        .collect();
    lines[lines.len().saturating_sub(3)..].join(" / ")
}

fn print_unresolved(Unresolved { report, reason }: Unresolved) -> u8 {
    for line in report {
        println!("{line}");
    }
    println!("unresolved: {reason}");
    UNRESOLVED
}

/// What the runner resolves in each directory holding its marker, each
/// opened by its scope and markers, starting no runner where there is none
/// (REQ-3048). It exits 3 where a directory's listing is unresolved.
pub fn status(runner: &Runner, resolve: impl Fn(&Path) -> Result<Resolved, Unresolved>) -> u8 {
    println!("{} status", runner.unit);
    let top = Tree::read();
    let markers = (runner.markers)(&top.tracked);
    if markers.is_empty() {
        println!("unresolved: not {}", runner.repository);
        return UNRESOLVED;
    }
    let parts = detect::parts(&top.root);
    let mut code = 0;
    for (directory, files) in detect::by_directory(&markers) {
        println!("{}", detect::scope(&parts, &directory));
        for file in files {
            println!("marker: {file}");
        }
        if directory_status(&resolve, &top.root.join(&directory)) != 0 {
            code = UNRESOLVED;
        }
    }
    code
}

fn directory_status(
    resolve: &impl Fn(&Path) -> Result<Resolved, Unresolved>,
    directory: &Path,
) -> u8 {
    let resolved = match resolve(directory) {
        Ok(resolved) => resolved,
        Err(unresolved) => return print_unresolved(unresolved),
    };
    for line in &resolved.report {
        println!("{line}");
    }
    println!(
        "tasks resolved in this work tree, which may differ from what the repository declares:"
    );
    for task in &resolved.tasks {
        println!("  {}: {} {}", task.name, task.origin, task.source);
        if let Some(replaced) = &task.replaced {
            println!("    {replaced}");
        }
        if !task.blocks.is_empty() {
            println!("    blocked: {}", task.blocks.join(", "));
        }
        for note in &task.notes {
            println!("    {note}");
        }
    }
    for line in &resolved.carried {
        println!("{line}");
    }
    0
}

/// A `[stages]` table binding each stage to the task of exactly its name, never
/// a near one and never by what a task runs (REQ-2474, REQ-2492). It prints
/// and never writes, because the profile is the repository's (ADR-1070).
pub fn bind(runner: &Runner, resolve: impl Fn(&Path) -> Result<Resolved, Unresolved>) -> u8 {
    let resolved = match resolve(&profile::repository_root()) {
        Ok(resolved) => resolved,
        Err(Unresolved { reason, .. }) => {
            println!("{} bind", runner.unit);
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    println!(
        "# {} bind: paste what follows into .meowpaw/profile.toml",
        runner.unit
    );
    println!("[stages]");
    for verb in VERBS {
        match resolved.tasks.iter().find(|t| t.name == verb) {
            None => match resolved.unlisted.iter().find(|(name, _)| name == verb) {
                Some((_, why)) => println!("# {verb}: task {verb} is {why}"),
                None => println!("# {verb}: no task named {verb}"),
            },
            Some(task) if !task.blocks.is_empty() => println!(
                "# {verb}: task {verb} is blocked: {}",
                task.blocks.join(", ")
            ),
            // Forced, so a task the runner would skip runs, and a pass is never a skip (REQ-2468).
            Some(task) => println!("{verb} = \"{}\"", (runner.binding)(&task.name)),
        }
    }
    0
}

/// Every task a stage's command runs through the runner, with whether it forces the run.
pub fn bound_tasks(command: &str, runs: &[&str]) -> Vec<(String, bool)> {
    let mut found = Vec::new();
    for part in command
        .split("&&")
        .flat_map(|p| p.split("||"))
        .flat_map(|p| p.split(';'))
    {
        let words: Vec<&str> = part.split_whitespace().collect();
        if words.len() < runs.len() || words[..runs.len()] != *runs {
            continue;
        }
        let rest = &words[runs.len()..];
        let flags: Vec<&str> = rest
            .iter()
            .take_while(|w| w.starts_with('-'))
            .copied()
            .collect();
        if let Some(name) = rest.iter().find(|w| !w.starts_with('-')) {
            found.push((
                name.to_string(),
                flags.iter().any(|f| *f == "--force" || *f == "-f"),
            ));
        }
    }
    found
}

/// What stops each task a profile's stage runs from being run unattended.
/// `early` holds findings a pack makes before listing, which a listing it
/// can't run would otherwise hide.
pub fn check(
    runner: &Runner,
    early: Vec<String>,
    resolve: impl Fn(&Path) -> Result<Resolved, Unresolved>,
) -> u8 {
    println!("{} check", runner.unit);
    let root = profile::repository_root();
    let read = profile::read(&root);
    for line in profile::report(&read) {
        println!("{line}");
    }
    let verbs = match read {
        profile::Profile::Absent => {
            println!("unresolved: no profile at {}", profile::PROFILE);
            return UNRESOLVED;
        }
        profile::Profile::Unparseable(message) => {
            println!("unresolved: the profile doesn't parse: {message}");
            return UNRESOLVED;
        }
        profile::Profile::Parsed(table, _) => profile::stages(&table)
            .and_then(toml::Value::as_table)
            .cloned()
            .unwrap_or_default(),
    };
    for finding in &early {
        println!("  {finding}");
    }
    if !early.is_empty() {
        println!(
            "{} findings before listing; nothing was listed",
            early.len()
        );
        return 1;
    }
    let mut bound = Vec::new();
    for (verb, value) in &verbs {
        let command = match value {
            toml::Value::String(c) => Some(c.as_str()),
            toml::Value::Table(t) => t.get("command").and_then(toml::Value::as_str),
            _ => None,
        };
        for (task, forced) in command
            .map(|c| bound_tasks(c, runner.runs))
            .unwrap_or_default()
        {
            bound.push((verb.clone(), task, forced));
        }
    }
    if bound.is_empty() {
        println!(
            "nothing to check: no stage runs a task through {}",
            runner.runs.join(" ")
        );
        return 0;
    }
    let resolved = match resolve(&root) {
        Ok(resolved) => resolved,
        Err(Unresolved { reason, .. }) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let mut findings = 0;
    let checked = bound.len();
    for (verb, name, forced) in bound {
        let Some(task) = resolved.tasks.iter().find(|t| t.name == name) else {
            match resolved.unlisted.iter().find(|(n, _)| *n == name) {
                Some((_, why)) => println!("  {verb}: task {name} is {why}"),
                None => println!("  {verb}: no task named {name}"),
            }
            findings += 1;
            continue;
        };
        if !task.blocks.is_empty() {
            println!(
                "  {verb}: task {name} is blocked: {}",
                task.blocks.join(", ")
            );
            findings += 1;
        }
        if !forced && task.can_skip != Some(false) {
            println!(
                "  {verb}: task {name} can skip {} and runs without --force",
                runner.skip
            );
            findings += 1;
        }
    }
    println!("{findings} findings in {checked} task runs the profile's stages name");
    if findings > 0 { 1 } else { 0 }
}
