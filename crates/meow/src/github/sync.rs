// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Synchronise an authorising record's tasks with their issues (ADR-2890).
//!
//! SPC-1080 states the behaviour. The mapping on a task carries two
//! fingerprints taken at the last synchronisation: `projected:` for the record
//! side and `tracked:` for the tracker side. A side that changed since is told
//! by its fingerprint and not by a clock, because GitHub keeps one time for a
//! whole issue (RES-0349). The side that changed is applied to the other, the
//! record's text is applied where both changed, and an approved record is never
//! reworded from the tracker: the difference is reported. An issue closed on the
//! tracker marks a task done in its epic or defect where the task's Evidence is
//! written, and is reported where it isn't.

use super::name_repository;
use super::project::{
    CLEAN, FOUND, Record, Tracker, UNREAD, done_in, fingerprint, halt, marker, projection,
    read_tracker, record_mapping, records, report, same, tracker_fingerprint,
};
use super::request::{Failure, Layer};
use crate::profile::{self, Profile};

/// The task's title line, `# <title>`, replaced by `title`.
fn write_title(task: &Record, title: &str) -> std::io::Result<()> {
    let mut done = false;
    let mut out: Vec<String> = Vec::new();
    for line in task.text.lines() {
        if !done && line.starts_with("# ") {
            out.push(format!("# {title}"));
            done = true;
        } else {
            out.push(line.to_string());
        }
    }
    let mut text = out.join("\n");
    if task.text.ends_with('\n') {
        text.push('\n');
    }
    std::fs::write(&task.path, text)
}

/// `- [ ] ... TSK-n` marked `- [x]` in the authorising record, where the line
/// is there and open.
fn mark_done(authoriser: &Record, id: &str) -> std::io::Result<bool> {
    let text = std::fs::read_to_string(&authoriser.path)?;
    let mut changed = false;
    let lines: Vec<String> = text
        .lines()
        .map(|line| {
            let named = line.split_whitespace().any(|word| word == id);
            match line.strip_prefix("- [ ] ") {
                Some(rest) if named && !changed => {
                    changed = true;
                    format!("- [x] {rest}")
                }
                _ => line.to_string(),
            }
        })
        .collect();
    if !changed {
        return Ok(false);
    }
    let mut out = lines.join("\n");
    if text.ends_with('\n') {
        out.push('\n');
    }
    std::fs::write(&authoriser.path, out)?;
    Ok(true)
}

/// A task's Evidence once it is written, which is what makes it done where no
/// epic marks it.
fn evidence_written(task: &Record) -> bool {
    let evidence = task.section("Evidence");
    !evidence.is_empty() && !evidence.starts_with("Not yet")
}

fn reload(task: &Record) -> Record {
    Record {
        path: task.path.clone(),
        text: std::fs::read_to_string(&task.path).unwrap_or_default(),
    }
}

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
    let direct = target_id.starts_with("ADR-");
    let defect = target_id.starts_with("BUG-");
    let dir = if direct {
        "adrs"
    } else if defect {
        "bugs"
    } else {
        "epics"
    };
    let Some(authoriser) = records(&base.join(dir), &format!("{target_id}-"))
        .into_iter()
        .next()
    else {
        println!(
            "meow-github sync: {target_id} resolves to no record under {}",
            base.display()
        );
        return FOUND;
    };
    if !matches!(authoriser.field("status").as_str(), "approved" | "done") {
        println!(
            "meow-github sync: {target_id} is {}, and its tasks are synchronised only once it is approved",
            authoriser.field("status")
        );
        return FOUND;
    }
    let skipped = |t: &Record| {
        matches!(
            t.field("status").as_str(),
            "withdrawn" | "rejected" | "superseded"
        )
    };
    let tasks: Vec<Record> = records(&base.join("tasks"), "TSK-")
        .into_iter()
        .filter(|t| {
            if direct {
                t.field("realises") == target_id
                    && t.field("epic").is_empty()
                    && t.field("bug").is_empty()
                    && !skipped(t)
            } else if defect {
                t.field("bug") == target_id && !skipped(t)
            } else {
                t.field("epic") == target_id
            }
        })
        .collect();
    let marked: Vec<String> = if direct {
        Vec::new()
    } else {
        done_in(&authoriser)
    };
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
        let (title, body) = projection(task, &authoriser);
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
        let draft = task.field("status") == "draft";
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
            let remote_title = remote
                .title
                .strip_prefix(&format!("{id}: "))
                .unwrap_or(&remote.title)
                .to_string();
            if !draft {
                println!(
                    "{id}: issue #{issue} was edited on GitHub since the last synchronisation; {id} is {}, and an approved record's wording is never written from the tracker, so the difference is reported",
                    task.field("status")
                );
                worst = worst.max(FOUND);
            } else if check {
                println!(
                    "{id}: issue #{issue} changed on GitHub only; the title would be written into {} (would)",
                    task.path.display()
                );
            } else {
                match write_title(task, &remote_title) {
                    Ok(()) => {
                        let fresh = reload(task);
                        let (new_title, new_body) = projection(&fresh, &authoriser);
                        let new_print = fingerprint(&new_title, &new_body);
                        println!(
                            "{id}: issue #{issue} changed on GitHub only; the title was written into {}",
                            task.path.display()
                        );
                        // The body is derived from the task's closes and depends, so
                        // a body edited on the tracker can't be written into the
                        // record, and the record's body goes back to the issue.
                        let mut fp = tracked_now(&remote.title, &remote.body);
                        if !same(&remote.body, &new_body) {
                            let again = format!("{new_body}\n\n{}", marker(&id, &new_print));
                            match layer.update_issue(
                                &repository,
                                &issue,
                                &[("title", &new_title), ("body", &again)],
                            ) {
                                Ok(_) => {
                                    println!(
                                        "{id}: the body is derived from closes and depends, so the record's body is written to issue #{issue}"
                                    );
                                    fp = tracked_now(&new_title, &new_body);
                                }
                                Err(e) => {
                                    report(&format!("{id}: issue #{issue} body not updated"), &e);
                                    worst = worst.max(UNREAD);
                                }
                            }
                        }
                        let _ = record_mapping(&fresh, number, &new_print, &fp);
                    }
                    Err(e) => {
                        println!(
                            "{id}: issue #{issue} changed on GitHub, and the title couldn't be written to {}: {e}",
                            task.path.display()
                        );
                        worst = worst.max(FOUND);
                    }
                }
            }
        } else {
            println!("{id}: unchanged, issue #{issue} at {print}");
            if stored.is_empty() && !check {
                let _ = record_mapping(task, number, &print, &remote.fingerprint());
            }
        }

        // The issue's state is the tracker's, and a closed issue marks a task
        // done where the Evidence is written (REQ-1355, REQ-4700).
        let done = if direct {
            evidence_written(task)
        } else {
            marked.contains(&id)
        };
        if remote.closed && !done {
            if evidence_written(task) && !direct {
                if check {
                    println!(
                        "{id}: issue #{issue} is closed on GitHub; {target_id} would mark the task done (would)"
                    );
                } else {
                    match mark_done(&authoriser, &id) {
                        Ok(true) => println!(
                            "{id}: issue #{issue} is closed on GitHub, and {target_id} now marks the task done"
                        ),
                        Ok(false) => println!(
                            "{id}: issue #{issue} is closed on GitHub, and {target_id} has no open line for it"
                        ),
                        Err(e) => {
                            println!("{id}: the mark couldn't be written to {target_id}: {e}");
                            worst = worst.max(FOUND);
                        }
                    }
                }
            } else {
                println!(
                    "{id}: issue #{issue} is closed on GitHub while its Evidence isn't written; the record decides when a task is done, so this is reported, not reconciled"
                );
                worst = worst.max(FOUND);
            }
        }
    }
    if tasks.is_empty() {
        println!("meow-github sync: {target_id} has no tasks");
    }
    worst
}
