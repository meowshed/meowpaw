// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Retire the issues of archived tasks, after the record's upgrade has merged
//! (ADR-3090).
//!
//! SPC-1080 states the behaviour. Each write sets the notice and the state in
//! one call, so an interrupted run leaves no issue half changed and the next
//! run skips what is already closed. An issue no archived task maps is never
//! read.

use super::name_repository;
use super::project::{self, CLEAN, FOUND, Record, UNREAD, halt, read_tracker, records, report};
use super::request::{Failure, Layer};
use crate::profile::{self, Profile};
use serde_json::Value;
use std::collections::BTreeSet;

/// What the record says of one archived task's issue.
#[derive(PartialEq)]
enum Fate {
    /// Close it as completed.
    Completed,
    /// Close it as not planned.
    Dropped,
    /// Close it as not planned, naming the record that carries the work.
    Folded(String),
    /// Leave it open: nothing authorises the work.
    Orphan,
}

fn fate(task: &Record) -> Fate {
    let folded = task.field("folded-into");
    match task.field("status").as_str() {
        _ if !folded.is_empty() => Fate::Folded(folded),
        "done" => Fate::Completed,
        "withdrawn" | "rejected" | "superseded" => Fate::Dropped,
        _ => Fate::Orphan,
    }
}

/// The issue a folded task's record carries, once `project` has run.
fn issue_of(base: &std::path::Path, id: &str) -> String {
    let dir = if id.starts_with("BUG-") {
        "bugs"
    } else {
        "adrs"
    };
    records(&base.join(dir), &format!("{id}-"))
        .first()
        .map(|record| record.field("issue"))
        .unwrap_or_default()
}

/// Reports each open pull request that names a folded task, and changes none,
/// because a branch in flight is somebody's work (ADR-3090).
fn name_open_pulls(layer: &mut Layer, repository: &str, folded: &BTreeSet<String>) {
    let endpoint = format!("repos/{repository}/pulls?state=open&per_page=100");
    let Ok(Value::Array(pulls)) = layer.get(&endpoint, false) else {
        println!("meow-github upgrade: the open pull requests couldn't be read");
        return;
    };
    for pull in pulls {
        let text = ["title", "body"]
            .map(|key| pull.get(key).and_then(Value::as_str).unwrap_or_default())
            .join("\n");
        let number = pull.get("number").and_then(Value::as_u64).unwrap_or(0);
        for id in folded.iter().filter(|id| text.contains(id.as_str())) {
            println!(
                "pull request #{number} names {id}, which is folded; left as it is, and its branch moves its plan to the record by hand"
            );
        }
    }
}

pub fn run(layer: &mut Layer, repository: Option<&str>, check: bool) -> u8 {
    let root = profile::repository_root();
    let read = profile::read(&root);
    for line in profile::report(&read) {
        println!("meow-github upgrade: {line}");
    }
    let table = match read {
        Profile::Parsed(table, _) => table,
        _ => toml::Table::new(),
    };
    let tracker = table
        .get("tracker")
        .and_then(|t| t.get("kind"))
        .and_then(|k| k.as_str())
        .unwrap_or("");
    if tracker != "github" {
        println!(
            "meow-github upgrade: {} declares no GitHub tracker, so nothing is retired; declare `[tracker] kind = \"github\"`",
            profile::PROFILE
        );
        return UNREAD;
    }
    let record_root = table
        .get("record")
        .and_then(|r| r.get("root"))
        .and_then(|r| r.as_str())
        .unwrap_or("project");
    let base = root.join(record_root);
    let tasks = records(&base.join("archive").join("tasks"), "TSK-");
    if tasks.is_empty() {
        println!("meow-github upgrade: no archived task; merge `paw upgrade --write` first");
        return FOUND;
    }
    let repository = match name_repository(layer, repository) {
        Ok(name) => name,
        Err(e) => {
            match e {
                stop @ (Failure::Throttled(_) | Failure::Rejected(_)) => halt(&stop),
                e => report("meow-github upgrade: nothing retired", &e),
            }
            return UNREAD;
        }
    };
    // Each carrier gets its issue first, so that a closing notice can name it.
    let mut worst = CLEAN;
    let carriers: BTreeSet<String> = tasks
        .iter()
        .filter_map(|task| match fate(task) {
            Fate::Folded(carrier) => Some(carrier),
            _ => None,
        })
        .collect();
    for carrier in &carriers {
        worst = worst.max(project::run(layer, carrier, Some(&repository), check));
    }
    let folded: BTreeSet<String> = tasks
        .iter()
        .filter(|task| matches!(fate(task), Fate::Folded(_)))
        .map(|task| task.field("id"))
        .collect();
    name_open_pulls(layer, &repository, &folded);
    let verb = if check { "would close" } else { "closed" };
    for task in &tasks {
        let id = task.field("id");
        let issue = task.field("issue");
        let fate = fate(task);
        if issue.is_empty() {
            if fate == Fate::Orphan {
                println!("{id}: needs a decision, and it maps to no issue");
                worst = worst.max(FOUND);
            }
            continue;
        }
        let remote = match read_tracker(layer, &repository, &issue) {
            Ok(remote) => remote,
            Err(stop @ (Failure::Throttled(_) | Failure::Rejected(_))) => {
                halt(&stop);
                return UNREAD;
            }
            Err(e) => {
                report(&format!("{id}: issue #{issue} couldn't be read"), &e);
                worst = worst.max(UNREAD);
                continue;
            }
        };
        let (reason, notice) = match &fate {
            Fate::Orphan => {
                println!("{id}: issue #{issue} is left as it is, and {id} needs a decision");
                worst = worst.max(FOUND);
                continue;
            }
            Fate::Folded(carrier) if remote.closed => {
                println!("{id}: issue #{issue} is closed, and {carrier} carries the work");
                continue;
            }
            _ if remote.closed => continue,
            Fate::Completed => (
                "completed",
                format!("{id} is done and archived (ADR-3090)."),
            ),
            Fate::Dropped => (
                "not_planned",
                format!("{id} was dropped and is archived (ADR-3090)."),
            ),
            Fate::Folded(carrier) => {
                let successor = issue_of(&base, carrier);
                let named = if successor.is_empty() {
                    carrier.clone()
                } else {
                    format!("{carrier} (#{successor})")
                };
                (
                    "not_planned",
                    format!("{id} is archived, and {named} carries its work (ADR-3090)."),
                )
            }
        };
        if check {
            println!("{id}: {verb} issue #{issue} as {reason}");
            continue;
        }
        let body = format!("{notice}\n\n{}", remote.body);
        let fields = [
            ("body", body.as_str()),
            ("state", "closed"),
            ("state_reason", reason),
        ];
        match layer.update_issue(&repository, &issue, &fields) {
            Ok(_) => println!("{id}: {verb} issue #{issue} as {reason}"),
            Err(stop @ (Failure::Throttled(_) | Failure::Rejected(_))) => {
                halt(&stop);
                return UNREAD;
            }
            Err(e) => {
                report(&format!("{id}: issue #{issue} not closed"), &e);
                worst = worst.max(UNREAD);
            }
        }
    }
    worst
}
