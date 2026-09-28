// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Project an approved epic's tasks onto GitHub issues (ADR-1310).
//!
//! SPC-1080 states the behaviour. The record owns each issue's title and
//! body, and the mapping lives on the task: `issue:` names the issue and
//! `projected:` the fingerprint of what was written, so a replay finds nothing
//! to do and the mapping survives losing the tracker. The fingerprint is the
//! first twelve hex digits of the SHA-256 of the title, a newline and the body,
//! which `shasum -a 256` reproduces by hand.

use super::{gh, name_repository};
use crate::profile::{self, Profile};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

const CLEAN: u8 = 0;
const FOUND: u8 = 1;
const UNREAD: u8 = 3;

struct Record {
    path: PathBuf,
    text: String,
}

impl Record {
    fn field(&self, key: &str) -> String {
        front_matter(&self.text)
            .iter()
            .find(|l| l.starts_with(&format!("{key}:")))
            .map(|l| {
                l[key.len() + 1..]
                    .split('#')
                    .next()
                    .unwrap_or("")
                    .trim()
                    .to_string()
            })
            .unwrap_or_default()
    }

    fn title(&self) -> String {
        self.text
            .lines()
            .find(|l| l.starts_with("# "))
            .map(|l| l[2..].trim().to_string())
            .unwrap_or_default()
    }

    /// The requirement identifiers in `closes`, which may run over several lines.
    fn closes(&self) -> Vec<String> {
        let mut out = Vec::new();
        let mut inside = false;
        for line in front_matter(&self.text) {
            if line.starts_with("closes:") {
                inside = true;
            } else if !line.starts_with(' ') && !line.starts_with(']') && line.contains(':') {
                inside = false;
            }
            if inside {
                for word in line.split(|c: char| !(c.is_ascii_alphanumeric() || c == '-')) {
                    if word.len() == 8 && word.starts_with("REQ-") {
                        out.push(word.to_string());
                    }
                }
            }
        }
        out
    }

    fn section(&self, name: &str) -> String {
        let mut out = Vec::new();
        let mut inside = false;
        for line in self.text.lines() {
            if let Some(heading) = line.strip_prefix("## ") {
                inside = heading.trim() == name;
                continue;
            }
            if inside && !line.trim().is_empty() {
                out.push(line.trim());
            }
        }
        out.join(" ")
    }
}

fn front_matter(text: &str) -> Vec<&str> {
    let mut lines = text.lines();
    if lines.next() != Some("---") {
        return Vec::new();
    }
    lines.take_while(|l| *l != "---").collect()
}

fn records(dir: &Path, prefix: &str) -> Vec<Record> {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return Vec::new();
    };
    let mut out: Vec<Record> = entries
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|p| {
            p.file_name()
                .and_then(|n| n.to_str())
                .is_some_and(|n| n.starts_with(prefix) && n.ends_with(".md"))
        })
        .filter_map(|path| {
            std::fs::read_to_string(&path)
                .ok()
                .map(|text| Record { path, text })
        })
        .collect();
    out.sort_by(|a, b| a.path.cmp(&b.path));
    out
}

pub fn fingerprint(title: &str, body: &str) -> String {
    let digest = Sha256::digest(format!("{title}\n{body}").as_bytes());
    digest.iter().take(6).map(|b| format!("{b:02x}")).collect()
}

/// What the record says the task's issue holds: its title, and its body
/// without the marker, which names the fingerprint and so can't be part of it.
fn projection(task: &Record, epic: &Record) -> (String, String) {
    let id = task.field("id");
    let title = format!("{id}: {}", task.title());
    let closes = task.closes();
    let mut body = format!(
        "{id} of {}, which realises {}.\n\nCloses {}.",
        epic.field("id"),
        epic.field("realises"),
        closes.join(", ")
    );
    let depends = task.section("Depends on");
    if !depends.is_empty() {
        body.push_str(&format!("\n\nDepends on: {depends}"));
    }
    (title, body)
}

fn marker(id: &str, fingerprint: &str) -> String {
    format!("<!-- meow-github: projected from {id} at {fingerprint} -->")
}

/// Writes `issue:` and `projected:` into the task's front matter.
fn record_mapping(task: &Record, number: u64, fingerprint: &str) -> std::io::Result<()> {
    let mut out = Vec::new();
    let mut in_front = false;
    let mut fences = 0;
    for line in task.text.lines() {
        if line == "---" {
            fences += 1;
            in_front = fences == 1;
            // A task written without the optional fields gets them here, or a
            // replay finds no mapping and opens a second issue (BUG-1210).
            if fences == 2 && !out.iter().any(|l: &String| l.starts_with("issue:")) {
                out.push(format!("issue: {number}"));
            }
            if fences == 2 && !out.iter().any(|l: &String| l.starts_with("projected:")) {
                out.push(format!("projected: {fingerprint}"));
            }
        } else if in_front && line.starts_with("issue:") {
            out.push(format!("issue: {number}"));
            continue;
        } else if in_front && line.starts_with("projected:") {
            out.push(format!("projected: {fingerprint}"));
            continue;
        }
        out.push(line.to_string());
    }
    let mut text = out.join("\n");
    if task.text.ends_with('\n') {
        text.push('\n');
    }
    std::fs::write(&task.path, text)
}

fn same(a: &str, b: &str) -> bool {
    a.replace("\r\n", "\n").trim_end() == b.replace("\r\n", "\n").trim_end()
}

/// What the tracker holds now, as the fingerprint its title and body carry
/// without the marker, and whether the issue is closed.
fn tracked(repository: &str, issue: &str) -> Result<(String, bool), String> {
    let read = gh(&["api", &format!("repos/{repository}/issues/{issue}")])?;
    let title = read
        .get("title")
        .and_then(Value::as_str)
        .ok_or("the issue lacks the field `title`")?;
    let body = read
        .get("body")
        .and_then(Value::as_str)
        .unwrap_or("")
        .replace("\r\n", "\n");
    let body = body
        .rsplit_once("\n\n<!-- meow-github:")
        .map(|(b, _)| b.to_string())
        .unwrap_or(body);
    let closed = read.get("state").and_then(Value::as_str) == Some("closed");
    Ok((fingerprint(title, &body), closed))
}

/// The tasks the epic marks done.
fn done_in(epic: &Record) -> Vec<String> {
    epic.text
        .lines()
        .filter_map(|l| l.strip_prefix("- [x] "))
        .filter_map(|l| l.split_whitespace().nth(1).map(str::to_string))
        .collect()
}

pub fn run(epic_id: &str, repository: Option<&str>, check: bool) -> u8 {
    let root = profile::repository_root();
    let table = match profile::read(&root) {
        Profile::Parsed(table) => table,
        _ => toml::Table::new(),
    };
    // A repository declares its tracker, and one that declares none is fully
    // served by the method without it (REQ-1351, REQ-1380).
    let tracker = table
        .get("tracker")
        .and_then(|t| t.get("kind"))
        .and_then(|k| k.as_str())
        .unwrap_or("");
    if tracker != "github" {
        let declared = if tracker.is_empty() {
            "declares no tracker".to_string()
        } else {
            format!("declares the tracker {tracker}")
        };
        println!(
            "meow-github project: {} {declared}, so nothing is projected; declare `[tracker] kind = \"github\"` to project onto GitHub",
            profile::PROFILE
        );
        return UNREAD;
    }
    let record_root = table
        .get("record")
        .and_then(|r| r.get("root"))
        .and_then(|r| r.as_str())
        .unwrap_or("project")
        .to_string();
    let base = root.join(record_root);
    let Some(epic) = records(&base.join("epics"), &format!("{epic_id}-"))
        .into_iter()
        .next()
    else {
        println!(
            "meow-github project: {epic_id} resolves to no epic under {}",
            base.display()
        );
        return FOUND;
    };
    if epic.field("status") != "approved" {
        println!(
            "meow-github project: {epic_id} is {}, and its tasks are projected only once it is approved",
            epic.field("status")
        );
        return FOUND;
    }
    let repository = match name_repository(repository) {
        Ok(name) => name,
        Err(e) => {
            println!("meow-github project: nothing projected: {e}");
            return UNREAD;
        }
    };
    let tasks: Vec<Record> = records(&base.join("tasks"), "TSK-")
        .into_iter()
        .filter(|t| t.field("epic") == epic_id)
        .collect();
    let done = done_in(&epic);
    let mut worst = CLEAN;
    for task in &tasks {
        let id = task.field("id");
        let (title, body) = projection(task, &epic);
        let print = fingerprint(&title, &body);
        let issue = task.field("issue");
        if !issue.is_empty() {
            let projected = task.field("projected");
            if projected.is_empty() {
                println!(
                    "{id}: mapped to issue #{issue} by hand, with no fingerprint; left as it is"
                );
                continue;
            }
            // Computed from the two fingerprints each run, never stored (REQ-1388).
            let (on_tracker, closed) = match tracked(&repository, &issue) {
                Ok(state) => state,
                Err(e) => {
                    println!("{id}: issue #{issue} couldn't be read: {e}");
                    worst = worst.max(UNREAD);
                    continue;
                }
            };
            if closed && !done.contains(&id) {
                println!(
                    "{id}: issue #{issue} is closed on GitHub while {epic_id} leaves the task unmarked; the epic decides what the tasks are, so this is reported, not reconciled"
                );
                worst = worst.max(FOUND);
            }
            if on_tracker != projected {
                println!(
                    "{id}: issue #{issue} was edited on GitHub since it was projected at {projected}; the record owns its title and body, and it is left as it is"
                );
                worst = worst.max(FOUND);
            } else if projected == print {
                println!("{id}: unchanged, issue #{issue} at {print}");
            } else if check {
                println!(
                    "{id}: changed since it was projected at {projected}; issue #{issue} would be updated to {print}"
                );
            } else {
                let full = format!("{body}\n\n{}", marker(&id, &print));
                let endpoint = format!("repos/{repository}/issues/{issue}");
                match gh(&[
                    "api",
                    &endpoint,
                    "-X",
                    "PATCH",
                    "-f",
                    &format!("title={title}"),
                    "-f",
                    &format!("body={full}"),
                ]) {
                    Ok(_) => match issue
                        .parse::<u64>()
                        .ok()
                        .map(|n| record_mapping(task, n, &print))
                    {
                        Some(Ok(())) => println!(
                            "{id}: changed since {projected}, issue #{issue} updated to {print}"
                        ),
                        _ => {
                            println!(
                                "{id}: issue #{issue} updated, and the mapping couldn't be written to {}",
                                task.path.display()
                            );
                            worst = worst.max(FOUND);
                        }
                    },
                    Err(e) => {
                        println!("{id}: issue #{issue} not updated: {endpoint}: {e}");
                        worst = worst.max(UNREAD);
                    }
                }
            }
            continue;
        }
        if check {
            println!("{id}: not projected yet");
            continue;
        }
        let full = format!("{body}\n\n{}", marker(&id, &print));
        let endpoint = format!("repos/{repository}/issues");
        let created = match gh(&[
            "api",
            &endpoint,
            "-X",
            "POST",
            "-f",
            &format!("title={title}"),
            "-f",
            &format!("body={full}"),
        ]) {
            Ok(created) => created,
            Err(e) => {
                println!("{id}: not projected: {endpoint}: {e}");
                println!(
                    "meow-github project: stopped part way; the tasks above it were projected"
                );
                return UNREAD;
            }
        };
        let Some(number) = created.get("number").and_then(Value::as_u64) else {
            println!("{id}: GitHub's reply to {endpoint} lacks the field `number`");
            return UNREAD;
        };
        if let Err(e) = record_mapping(task, number, &print) {
            println!(
                "{id}: issue #{number} created, and the mapping couldn't be written to {}: {e}",
                task.path.display()
            );
            return FOUND;
        }
        match gh(&["api", &format!("{endpoint}/{number}")]) {
            Ok(read)
                if same(
                    read.get("title").and_then(Value::as_str).unwrap_or(""),
                    &title,
                ) && same(
                    read.get("body").and_then(Value::as_str).unwrap_or(""),
                    &full,
                ) =>
            {
                println!("{id}: projected to issue #{number} at {print}, read back");
            }
            Ok(_) => {
                println!(
                    "{id}: projected to issue #{number}, and it reads back differently from what was written"
                );
                worst = worst.max(FOUND);
            }
            Err(e) => {
                println!("{id}: projected to issue #{number}, and it couldn't be read back: {e}");
                worst = worst.max(UNREAD);
            }
        }
    }
    if tasks.is_empty() {
        println!("meow-github project: {epic_id} has no tasks");
    }
    worst
}
