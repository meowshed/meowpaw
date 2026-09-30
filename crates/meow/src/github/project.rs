// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Project an approved epic's tasks onto GitHub issues (ADR-1310).
//!
//! SPC-1080 states the behaviour. The record owns each issue's title and
//! body, and the mapping lives on the task: `issue:` names the issue and
//! `projected:` the fingerprint of what was written, so a replay finds nothing
//! to do and the mapping survives losing the tracker. The fingerprint is the
//! first twelve hex digits of the SHA-256 of the title, a newline and the body,
//! which `shasum -a 256` reproduces by hand. Every call goes through the
//! request layer, and a throttle stops the run where it is met (ADR-1810).
//! The issues a run created are read back in one listing after its last
//! create, and a run that stops before it has projected every task says
//! which tasks it projected, which it created and couldn't read back, and which it left
//! (REQ-2572).

use super::name_repository;
use super::request::{Failure, Layer};
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
    // A task realising a decision with no epic sits under nothing (REQ-3630).
    let mut body = if epic.field("artifact") == "adr" {
        format!(
            "{id}, which realises {}.\n\nCloses {}.",
            epic.field("id"),
            closes.join(", ")
        )
    } else {
        format!(
            "{id} of {}, which realises {}.\n\nCloses {}.",
            epic.field("id"),
            epic.field("realises"),
            closes.join(", ")
        )
    };
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
fn tracked(layer: &mut Layer, repository: &str, issue: &str) -> Result<(String, bool), Failure> {
    let read = layer.get_mapped(&format!("repos/{repository}/issues/{issue}"))?;
    let lacks = || Failure::Failed("the issue lacks the field `title`".to_string());
    let title = read
        .get("title")
        .and_then(Value::as_str)
        .ok_or_else(lacks)?;
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

/// Prints why a call gave nothing, after `context`, with a refusal's line on a
/// line of its own so that it reads as GitHub's answer and not as the task's.
fn report(context: &str, failure: &Failure) {
    match failure {
        Failure::Refused(line) => {
            println!("{line}");
            println!("{context}");
        }
        other => println!("{context}: {other}"),
    }
}

/// Prints the `throttled:` line and says the run sends nothing after it.
fn throttled(line: &str) {
    println!("{line}");
    println!("meow-github project: stopped at the throttle above, sending nothing more");
}

/// An issue this run created, until the listing reads it back.
struct Created {
    id: String,
    number: u64,
    title: String,
    body: String,
    print: String,
}

/// What the run did with each task it can name, for the `partial:` line.
#[derive(Default)]
struct Outcome {
    /// The tasks whose issue was updated, found unchanged, or created and read
    /// back matching the record.
    projected: Vec<String>,
    /// The tasks whose issue was created and not read back, each with why.
    unread: Vec<String>,
    /// Whether the run stopped before it visited every task.
    stopped: bool,
    /// Whether it stopped at a throttle or a ceiling, after which it sends
    /// nothing more, the listing included.
    throttled: bool,
}

impl Outcome {
    /// Puts a created issue's task under `projected`, as read back as written.
    fn read_back(&mut self, c: Created) {
        println!(
            "{}: projected to issue #{} at {}, read back",
            c.id, c.number, c.print
        );
        self.projected.push(c.id);
    }

    /// Puts each created issue's task under `created, not read back`, with why.
    fn leave(&mut self, created: &[Created], why: &str) {
        for c in created {
            self.unread
                .push(format!("{} (issue #{}, {why})", c.id, c.number));
        }
    }

    /// The `partial:` line: every task of `tasks` under one of three groups.
    fn partial(&self, tasks: &[Record]) -> String {
        let left: Vec<String> = tasks
            .iter()
            .map(|t| t.field("id"))
            .filter(|id| {
                !self.projected.contains(id)
                    && !self.unread.iter().any(|u| u.split(' ').next() == Some(id))
            })
            .collect();
        let group = |items: &[String]| {
            if items.is_empty() {
                "none".to_string()
            } else {
                items.join(", ")
            }
        };
        format!(
            "partial: projected {}; created, not read back {}; not projected {}",
            group(&self.projected),
            group(&self.unread),
            group(&left)
        )
    }
}

/// Every issue GitHub lists as written since the run began, by number, read
/// in one uncached listing, every page of it.
fn read_back(layer: &mut Layer, repository: &str) -> Result<Vec<Value>, Failure> {
    let Some(began) = layer.began() else {
        return Err(Failure::Failed(
            "no response stated a `Date` to list from".to_string(),
        ));
    };
    let mut next = Some(format!(
        "repos/{repository}/issues?state=all&since={began}&per_page=100"
    ));
    let mut issues = Vec::new();
    while let Some(page) = next {
        let (body, following) = layer.page(&page, false)?;
        match body {
            Value::Array(page) => issues.extend(page),
            _ => return Err(Failure::Failed("a page isn't a list".to_string())),
        }
        next = following;
    }
    Ok(issues)
}

/// Reads the created issues back and sorts each task into `outcome`. The
/// listing runs after a failed write or a refusal, and not after a throttle
/// or a ceiling, because a request sent while throttled risks the integration.
fn settle(layer: &mut Layer, repository: &str, created: Vec<Created>, outcome: &mut Outcome) {
    if created.is_empty() {
        return;
    }
    if outcome.throttled {
        return outcome.leave(&created, "no listing ran");
    }
    let listed = match read_back(layer, repository) {
        Ok(listed) => listed,
        Err(Failure::Throttled(line)) => {
            throttled(&line);
            outcome.throttled = true;
            outcome.stopped = true;
            return outcome.leave(&created, "the listing was throttled");
        }
        Err(e) => {
            report(
                "meow-github project: the created issues couldn't be read back",
                &e,
            );
            return outcome.leave(&created, "the listing couldn't be read");
        }
    };
    let text = |issue: &Value, name: &str| {
        issue
            .get(name)
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string()
    };
    let written = |issue: &Value, c: &Created| {
        same(&text(issue, "title"), &c.title) && same(&text(issue, "body"), &c.body)
    };
    let mut missing = Vec::new();
    for c in created {
        let found = listed
            .iter()
            .find(|i| i.get("number").and_then(Value::as_u64) == Some(c.number));
        match found {
            Some(issue) if written(issue, &c) => outcome.read_back(c),
            Some(_) => outcome.leave(&[c], "reads differently from what was written"),
            None => missing.push(c),
        }
    }
    // The listing can lag a create by seconds, so an issue it left out is read
    // by its number before it is reported (ADR-2340).
    let mut missing = missing.into_iter();
    while let Some(c) = missing.next() {
        let endpoint = format!("repos/{repository}/issues/{}", c.number);
        match layer.get_mapped(&endpoint) {
            Ok(issue) if written(&issue, &c) => outcome.read_back(c),
            Ok(_) => outcome.leave(&[c], "reads differently from what was written"),
            Err(Failure::Throttled(line)) => {
                throttled(&line);
                outcome.throttled = true;
                outcome.stopped = true;
                let left: Vec<Created> = std::iter::once(c).chain(missing).collect();
                return outcome.leave(&left, "no read ran");
            }
            Err(e) => {
                report(
                    &format!("{}: issue #{} couldn't be read back", c.id, c.number),
                    &e,
                );
                outcome.leave(&[c], "couldn't be read");
            }
        }
    }
}

pub fn run(layer: &mut Layer, epic_id: &str, repository: Option<&str>, check: bool) -> u8 {
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
    // A decision groups the tasks that realise it with no epic (REQ-3630).
    let direct = epic_id.starts_with("ADR-");
    let dir = if direct { "adrs" } else { "epics" };
    let Some(epic) = records(&base.join(dir), &format!("{epic_id}-"))
        .into_iter()
        .next()
    else {
        let kind = if direct { "decision" } else { "epic" };
        println!(
            "meow-github project: {epic_id} resolves to no {kind} under {}",
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
    let tasks: Vec<Record> = records(&base.join("tasks"), "TSK-")
        .into_iter()
        .filter(|t| {
            if direct {
                t.field("realises") == epic_id
                    && t.field("epic").is_empty()
                    && t.field("bug").is_empty()
                    && !matches!(
                        t.field("status").as_str(),
                        "withdrawn" | "rejected" | "superseded"
                    )
            } else {
                t.field("epic") == epic_id
            }
        })
        .collect();
    // With no epic to mark it, a task is done once its Evidence is written.
    let done: Vec<String> = if direct {
        tasks
            .iter()
            .filter(|t| {
                let evidence = t.section("Evidence");
                !evidence.is_empty() && !evidence.starts_with("Not yet")
            })
            .map(|t| t.field("id"))
            .collect()
    } else {
        done_in(&epic)
    };
    let mut outcome = Outcome::default();
    // A run that can't name its repository visits no task, so it is partial too.
    let repository = match name_repository(layer, repository) {
        Ok(name) => name,
        Err(e) => {
            match e {
                Failure::Throttled(line) => throttled(&line),
                e => report("meow-github project: nothing projected", &e),
            }
            if !tasks.is_empty() {
                println!("{}", outcome.partial(&tasks));
            }
            return UNREAD;
        }
    };
    let mut worst = CLEAN;
    let mut created: Vec<Created> = Vec::new();
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
            let (on_tracker, closed) = match tracked(layer, &repository, &issue) {
                Ok(state) => state,
                Err(Failure::Throttled(line)) => {
                    throttled(&line);
                    (outcome.stopped, outcome.throttled) = (true, true);
                    break;
                }
                Err(e) => {
                    report(&format!("{id}: issue #{issue} couldn't be read"), &e);
                    worst = worst.max(UNREAD);
                    continue;
                }
            };
            if closed && !done.contains(&id) {
                if direct {
                    println!(
                        "{id}: issue #{issue} is closed on GitHub while the task's Evidence isn't written; the record decides when a task is done, so this is reported, not reconciled"
                    );
                } else {
                    println!(
                        "{id}: issue #{issue} is closed on GitHub while {epic_id} leaves the task unmarked; the epic decides what the tasks are, so this is reported, not reconciled"
                    );
                }
                worst = worst.max(FOUND);
            }
            if on_tracker != projected {
                println!(
                    "{id}: issue #{issue} was edited on GitHub since it was projected at {projected}; the record owns its title and body, and it is left as it is"
                );
                worst = worst.max(FOUND);
            } else if projected == print {
                println!("{id}: unchanged, issue #{issue} at {print}");
                outcome.projected.push(id);
            } else if check {
                println!(
                    "{id}: changed since it was projected at {projected}; issue #{issue} would be updated to {print}"
                );
            } else {
                let full = format!("{body}\n\n{}", marker(&id, &print));
                let endpoint = format!("repos/{repository}/issues/{issue}");
                match layer.write("PATCH", &endpoint, &[("title", &title), ("body", &full)]) {
                    Ok(_) => match issue
                        .parse::<u64>()
                        .ok()
                        .map(|n| record_mapping(task, n, &print))
                    {
                        Some(Ok(())) => {
                            println!(
                                "{id}: changed since {projected}, issue #{issue} updated to {print}"
                            );
                            outcome.projected.push(id);
                        }
                        _ => {
                            println!(
                                "{id}: issue #{issue} updated, and the mapping couldn't be written to {}",
                                task.path.display()
                            );
                            // The issue was updated, which is what projected means.
                            outcome.projected.push(id);
                            worst = worst.max(FOUND);
                        }
                    },
                    Err(Failure::Throttled(line)) => {
                        throttled(&line);
                        (outcome.stopped, outcome.throttled) = (true, true);
                        break;
                    }
                    Err(e) => {
                        report(&format!("{id}: issue #{issue} not updated: {endpoint}"), &e);
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
        let answer = match layer.write("POST", &endpoint, &[("title", &title), ("body", &full)]) {
            Ok(answer) => answer,
            Err(Failure::Throttled(line)) => {
                throttled(&line);
                (outcome.stopped, outcome.throttled) = (true, true);
                break;
            }
            Err(e) => {
                report(&format!("{id}: not projected: {endpoint}"), &e);
                outcome.stopped = true;
                break;
            }
        };
        let Some(number) = answer.get("number").and_then(Value::as_u64) else {
            println!("{id}: GitHub's reply to {endpoint} lacks the field `number`");
            outcome.stopped = true;
            break;
        };
        if let Err(e) = record_mapping(task, number, &print) {
            println!(
                "{id}: issue #{number} created, and the mapping couldn't be written to {}: {e}",
                task.path.display()
            );
            outcome
                .unread
                .push(format!("{id} (issue #{number}, the task doesn't name it)"));
            outcome.stopped = true;
            break;
        }
        println!("{id}: created issue #{number}");
        created.push(Created {
            id,
            number,
            title,
            body: full,
            print,
        });
    }
    settle(layer, &repository, created, &mut outcome);
    if tasks.is_empty() {
        println!("meow-github project: {epic_id} has no tasks");
    }
    if outcome.stopped || !outcome.unread.is_empty() {
        println!("{}", outcome.partial(&tasks));
        return UNREAD;
    }
    worst
}
