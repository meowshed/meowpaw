// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Synchronise a decision or defect with its issue (ADR-2890, ADR-3090).
//!
//! SPC-1080 states the behaviour. The mapping on a record carries two
//! fingerprints taken at the last synchronisation: `projected:` for the record
//! side and `tracked:` for the tracker side. A side that changed since is told
//! by its fingerprint and not by a clock, because GitHub keeps one time for a
//! whole issue (RES-0349). The side that changed is applied to the other, the
//! record's text is applied where both changed, and an approved record is never
//! reworded from the tracker: the difference is reported. An issue closed on the
//! tracker while its record isn't done is reported, because the record decides.

use super::name_repository;
use super::project::{
    CLEAN, FOUND, Tracker, UNREAD, fingerprint, halt, marker, projection, read_tracker,
    record_mapping, records, report, tracker_fingerprint,
};
use super::request::{Failure, Layer};
use crate::profile::{self, Profile};

fn stopped(failure: &Failure) {
    halt(failure);
}

pub fn run(layer: &mut Layer, target_id: &str, repository: Option<&str>, check: bool) -> u8 {
    let root = profile::repository_root();
    let read = profile::read(&root);
    for line in profile::report(&read) {
        println!("meow-github sync: {line}");
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
            "meow-github sync: {} declares no GitHub tracker, so nothing is synchronised; declare `[tracker] kind = \"github\"`",
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
    let dir = if target_id.starts_with("ADR-") {
        "adrs"
    } else if target_id.starts_with("BUG-") {
        "bugs"
    } else {
        println!(
            "meow-github sync: {target_id} is no decision or defect, and only those map to an issue"
        );
        return FOUND;
    };
    let tasks = records(&base.join(dir), &format!("{target_id}-"));
    let Some(authoriser) = tasks.first() else {
        println!(
            "meow-github sync: {target_id} resolves to no record under {}",
            base.display()
        );
        return FOUND;
    };
    if !matches!(authoriser.field("status").as_str(), "approved" | "done") {
        println!(
            "meow-github sync: {target_id} is {}, and it is synchronised only once it is approved",
            authoriser.field("status")
        );
        return FOUND;
    }
    let repository = match name_repository(layer, repository) {
        Ok(name) => name,
        Err(e) => {
            match e {
                stop @ (Failure::Throttled(_) | Failure::Rejected(_)) => stopped(&stop),
                e => report("meow-github sync: nothing synchronised", &e),
            }
            return UNREAD;
        }
    };
    let mut worst = CLEAN;
    for task in &tasks {
        let id = task.field("id");
        let issue = task.field("issue");
        let projected = task.field("projected");
        if issue.is_empty() || projected.is_empty() {
            println!("{id}: not projected yet, so nothing to synchronise; run `project` first");
            continue;
        }
        let Ok(number) = issue.parse::<u64>() else {
            println!("{id}: issue `{issue}` is not a number; left as it is");
            worst = worst.max(FOUND);
            continue;
        };
        let remote: Tracker = match read_tracker(layer, &repository, &issue) {
            Ok(remote) => remote,
            Err(stop @ (Failure::Throttled(_) | Failure::Rejected(_))) => {
                stopped(&stop);
                return UNREAD;
            }
            Err(e) => {
                report(&format!("{id}: issue #{issue} couldn't be read"), &e);
                worst = worst.max(UNREAD);
                continue;
            }
        };
        let (title, body) = projection(task);
        let print = fingerprint(&title, &body);
        let stored = task.field("tracked");
        let record_changed = print != projected;
        // An older mapping has the record side only, so the tracker side is
        // judged by its title and body against `projected` (REQ-4704).
        let tracker_changed = if stored.is_empty() {
            remote.text_fingerprint() != projected
        } else {
            let open = tracker_fingerprint(&remote.title, &remote.body, false);
            let closed = tracker_fingerprint(&remote.title, &remote.body, true);
            stored != open && stored != closed
        };
        let full = format!("{body}\n\n{}", marker(&id, &print));
        let tracked_now = |t: &str, b: &str| tracker_fingerprint(t, b, remote.closed);

        if record_changed {
            // The record's text goes to the issue, alone or in a conflict.
            let what = if tracker_changed {
                format!(
                    "{id}: both sides changed since the last synchronisation; the record's text is written to issue #{issue}, which wins a conflict"
                )
            } else {
                format!("{id}: changed in the record only; issue #{issue} is updated to {print}")
            };
            if check {
                println!("{what} (would)");
            } else {
                match layer.update_issue(&repository, &issue, &[("title", &title), ("body", &full)])
                {
                    Ok(_) => {
                        println!("{what}");
                        let _ = record_mapping(task, number, &print, &tracked_now(&title, &body));
                    }
                    Err(stop @ (Failure::Throttled(_) | Failure::Rejected(_))) => {
                        stopped(&stop);
                        return UNREAD;
                    }
                    Err(e) => {
                        report(&format!("{id}: issue #{issue} not updated"), &e);
                        worst = worst.max(UNREAD);
                    }
                }
            }
        } else if tracker_changed {
            println!(
                "{id}: issue #{issue} was edited on GitHub since the last synchronisation; {id} is {}, and an approved record's wording is never written from the tracker, so the difference is reported",
                task.field("status")
            );
            worst = worst.max(FOUND);
        } else {
            println!("{id}: unchanged, issue #{issue} at {print}");
            if stored.is_empty() && !check {
                let _ = record_mapping(task, number, &print, &remote.fingerprint());
            }
        }

        // The issue's state is the tracker's, and the record decides when its
        // work is done (REQ-3678).
        if remote.closed && task.field("status") != "done" {
            println!(
                "{id}: issue #{issue} is closed on GitHub while {id} isn't done; the record decides when it is done, so this is reported, not reconciled"
            );
            worst = worst.max(FOUND);
        }
    }
    worst
}
