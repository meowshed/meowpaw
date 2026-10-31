// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Read a GitHub repository's history, and write nothing (ADR-1290).
//!
//! SPC-1080 states the behaviour. `history` reads four listings through the
//! request layer (ADR-1810), every page of each and through `gh`'s cache, and
//! prints one JSON document. It takes each field by
//! name, so a field the code host stops sending fails by that name, and a listing
//! it can't read leaves the history unread rather than printed in part.

use request::{Failure, Layer, credential};
use serde_json::{Value, json};

mod guard;
mod project;
mod protections;
mod request;
mod sync;
mod upgrade;

const USAGE: u8 = 2;
const UNREAD: u8 = 3;
const LISTINGS: [(&str, &str); 4] = [
    ("issues and pull requests", "issues?state=all&per_page=100"),
    ("pull requests", "pulls?state=all&per_page=100"),
    ("conversation comments", "issues/comments?per_page=100"),
    ("review comments", "pulls/comments?per_page=100"),
];

const USAGE_LINE: &str = "usage: meow-github history [--wait] [<owner>/<name>] | project <decision|defect> [--check] [--wait] [<owner>/<name>] | sync <decision|defect> [--check] [--wait] [<owner>/<name>] | upgrade [--check] [--wait] [<owner>/<name>] | protections [--wait] [<owner>/<name>] | governance-guard | irreversible-guard";

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 7] = [
    crate::help::Entry {
        name: "history",
        determines: "the issues, pull requests and comments of one repository on the code host, read back",
        by_hand: "list the repository's issues, pull requests, conversation comments and review comments on the code host, with the `gh` tool or its web page",
        lines: "credential: meow-github primary secondary content spacing: read",
        json: "repository issues comments review_comments credential budget",
    },
    crate::help::Entry {
        name: "project",
        determines: "where a decision or defect stands as an issue, and creates the issue where it is missing",
        by_hand: "read the record's `issue:` and the tracker's issue it names, and create the issue where it lacks one",
        lines: "credential: meow-github primary secondary content spacing: partial: <id>",
        json: "",
    },
    crate::help::Entry {
        name: "sync",
        determines: "what changed on the tracker since the last projection, written back into the record",
        by_hand: "compare the issue's title, state and body with its record, and copy a change to the record",
        lines: "credential: meow-github primary secondary content spacing: partial: <id>",
        json: "",
    },
    crate::help::Entry {
        name: "upgrade",
        determines: "what retires the issues of archived tasks after the record's upgrade merged, and with no `--check` retires them",
        by_hand: "for each file under `archive/tasks`, close its open issue as completed where it is done, as not planned where it is dropped or carries `folded-into:`, naming the record that carries the work, and leave any other open",
        lines: "credential: meow-github primary secondary content spacing: pull <id>",
        json: "",
    },
    crate::help::Entry {
        name: "protections",
        determines: "which of six protections are in force on the declared trunk, read and never changed",
        by_hand: "read `gh api repos/{owner}/{repo}/branches/{trunk}/protection` and `gh api repos/{owner}/{repo}/rules/branches/{trunk}`, and look in each for blocked force pushes, blocked deletion, required reviews, required checks, signed commits and linear history",
        lines: "credential: meow-github force deletion required signed linear refused: throttled: unauthenticated: primary secondary content spacing:",
        json: "",
    },
    crate::help::Entry {
        name: "governance-guard",
        determines: "whether a tool call would change the repository's governance on the code host",
        by_hand: "read the command a hook is about to run for a call that edits branch protection, rulesets or secrets",
        lines: "<json>",
        json: "hookSpecificOutput",
    },
    crate::help::Entry {
        name: "irreversible-guard",
        determines: "whether a tool call merges, releases or writes an issue or a pull request from a session a person attends, which the person confirms for that one call",
        by_hand: "read the command a hook is about to run for `gh pr merge`, `gh release`, an issue or pull request write, a `gh api` write or `meow-github project` without `--check`, and the session's permission mode for `dontAsk`",
        lines: "<json>",
        json: "hookSpecificOutput",
    },
];

pub fn main(args: &[String]) -> u8 {
    if let Some(code) = crate::help::answer("meow-github", &HELP, args) {
        return code;
    }
    let Some((command, rest)) = args.split_first() else {
        eprintln!("{USAGE_LINE}");
        return USAGE;
    };
    if command == "governance-guard" && rest.is_empty() {
        return guard::main();
    }
    if command == "irreversible-guard" && rest.is_empty() {
        return guard::irreversible_main();
    }
    let flag = |name: &str| rest.iter().any(|a| a == name);
    let (check, wait) = (flag("--check"), flag("--wait"));
    let words: Vec<&str> = rest
        .iter()
        .map(String::as_str)
        .filter(|a| *a != "--check" && *a != "--wait")
        .collect();
    let mut layer = Layer::new(wait);
    match (command.as_str(), words.as_slice(), check) {
        ("history", [], false) => history(&mut layer, None),
        ("history", [repository], false) => history(&mut layer, Some(repository)),
        ("project", [record], _) => project(&mut layer, record, None, check),
        ("project", [record, repository], _) => {
            project(&mut layer, record, Some(repository), check)
        }
        ("sync", [record], _) => synchronise(&mut layer, record, None, check),
        ("sync", [record, repository], _) => {
            synchronise(&mut layer, record, Some(repository), check)
        }
        ("upgrade", [], _) => retire(&mut layer, None, check),
        ("upgrade", [repository], _) => retire(&mut layer, Some(repository), check),
        ("protections", [], false) => protect(&mut layer, None),
        ("protections", [repository], false) => protect(&mut layer, Some(repository)),
        _ => {
            eprintln!("{USAGE_LINE}");
            USAGE
        }
    }
}

/// Projects a decision or defect, with the credential's form as the report's first line and
/// the budget as its last lines (REQ-2568, REQ-2582).
fn project(layer: &mut Layer, record: &str, repository: Option<&str>, check: bool) -> u8 {
    println!("credential: {}", credential());
    let code = project::run(layer, record, repository, check);
    for line in layer.budget() {
        println!("{line}");
    }
    code
}

/// Synchronises a decision or defect with its issue, with the
/// credential's form as the report's first line and the budget as its last
/// lines, as `project` does (ADR-2890).
fn synchronise(layer: &mut Layer, record: &str, repository: Option<&str>, check: bool) -> u8 {
    println!("credential: {}", credential());
    let code = sync::run(layer, record, repository, check);
    for line in layer.budget() {
        println!("{line}");
    }
    code
}

/// Retires the issues of archived tasks, with the credential's form as the
/// report's first line and the budget as its last lines, as `project` does
/// (ADR-3090).
fn retire(layer: &mut Layer, repository: Option<&str>, check: bool) -> u8 {
    println!("credential: {}", credential());
    let code = upgrade::run(layer, repository, check);
    for line in layer.budget() {
        println!("{line}");
    }
    code
}

/// Reports the trunk's protections, with the credential's form as the
/// report's first line and the budget as its last lines, as `project` does
/// (REQ-2194).
fn protect(layer: &mut Layer, repository: Option<&str>) -> u8 {
    println!("credential: {}", credential());
    let code = protections::run(layer, repository);
    for line in layer.budget() {
        println!("{line}");
    }
    code
}

/// The repository named, or else the one this directory's clone belongs to,
/// read as `repos/{owner}/{repo}` through the layer.
fn name_repository(layer: &mut Layer, repository: Option<&str>) -> Result<String, Failure> {
    match repository {
        Some(name) => Ok(name.to_string()),
        None => match layer.get("repos/{owner}/{repo}", false) {
            Ok(view) => Ok(view
                .get("full_name")
                .and_then(Value::as_str)
                .unwrap_or_default()
                .to_string()),
            Err(Failure::Failed(e)) => Err(Failure::Failed(format!(
                "couldn't name this directory's repository: {e}; name it as <owner>/<name>"
            ))),
            Err(other) => Err(other),
        },
    }
}

/// A field of a response, by name, so that one the code host stopped sending fails
/// by that name rather than reading as empty (REQ-2556).
fn field<'a>(item: &'a Value, name: &str, listing: &str) -> Result<&'a Value, String> {
    item.get(name)
        .ok_or_else(|| format!("a response in the {listing} listing lacks the field `{name}`"))
}

fn text(item: &Value, name: &str, listing: &str) -> Result<Value, String> {
    let value = field(item, name, listing)?;
    Ok(if value.is_null() {
        Value::Null
    } else {
        Value::String(value.as_str().unwrap_or_default().to_string())
    })
}

fn author(item: &Value, listing: &str) -> Result<Value, String> {
    Ok(field(item, "user", listing)?
        .get("login")
        .cloned()
        .unwrap_or(Value::Null))
}

/// The number at the end of an issue's or a pull request's address.
fn number_in(item: &Value, name: &str, listing: &str) -> Result<u64, String> {
    let address = field(item, name, listing)?.as_str().unwrap_or_default();
    address
        .rsplit('/')
        .next()
        .and_then(|n| n.parse().ok())
        .ok_or_else(|| format!("the {listing} listing gave `{name}` with no number"))
}

/// Every item of a listing, every page of it read by following its `Link`
/// header (REQ-2560), through the client's cache (REQ-2564).
fn listing(
    layer: &mut Layer,
    repository: &str,
    name: &str,
    path: &str,
) -> Result<Vec<Value>, String> {
    let endpoint = format!("repos/{repository}/{path}");
    let mut items = Vec::new();
    let mut next = Some(endpoint.clone());
    while let Some(page) = next {
        let (body, following) = layer.page(&page, true).map_err(|e| match e {
            Failure::Throttled(line) => line,
            Failure::Refused(line) | Failure::Rejected(line) => format!("{name}: {line}"),
            Failure::Failed(e) => format!("{name}, {endpoint}: {e}"),
        })?;
        match body {
            Value::Array(page) => items.extend(page),
            _ => return Err(format!("{name}, {endpoint}: a page isn't a list")),
        }
        next = following;
    }
    Ok(items)
}

fn history(layer: &mut Layer, repository: Option<&str>) -> u8 {
    let unread = |layer: &Layer, lines: &[String]| {
        println!("credential: {}", credential());
        for line in lines {
            println!("{line}");
        }
        for line in layer.budget() {
            println!("{line}");
        }
        UNREAD
    };
    let repository = match name_repository(layer, repository) {
        Ok(name) => name,
        Err(e) => return unread(layer, &[format!("meow-github history: unread: {e}")]),
    };
    match read(layer, &repository) {
        Ok(mut document) => {
            document["credential"] = json!(credential());
            document["budget"] = json!(layer.budget());
            println!(
                "{}",
                serde_json::to_string_pretty(&document).unwrap_or_default()
            );
            0
        }
        Err((read, e)) => {
            let read = if read.is_empty() {
                "nothing".to_string()
            } else {
                read.join(", ")
            };
            unread(
                layer,
                &[
                    format!("meow-github history: unread: {e}"),
                    format!(
                        "read before it stopped: {read}; no document is printed, because a part of the history reads as the whole of it"
                    ),
                ],
            )
        }
    }
}

fn read(layer: &mut Layer, repository: &str) -> Result<Value, (Vec<&'static str>, String)> {
    let mut read = Vec::new();
    let mut lists = Vec::new();
    for (name, path) in LISTINGS {
        let items = listing(layer, repository, name, path).map_err(|e| (read.clone(), e))?;
        read.push(name);
        lists.push(items);
    }
    let failed = |e: String| (read.clone(), e);
    let (issue_listing, pull_listing) = (LISTINGS[0].0, LISTINGS[1].0);
    let mut merged = std::collections::BTreeMap::new();
    for pull in &lists[1] {
        let number = field(pull, "number", pull_listing)
            .map_err(failed)?
            .as_u64()
            .unwrap_or_default();
        merged.insert(
            number,
            !field(pull, "merged_at", pull_listing)
                .map_err(failed)?
                .is_null(),
        );
    }
    let mut issues = Vec::new();
    for item in &lists[0] {
        let number = field(item, "number", issue_listing)
            .map_err(failed)?
            .as_u64()
            .unwrap_or_default();
        let pull = item.get("pull_request").is_some();
        let labels: Vec<Value> = field(item, "labels", issue_listing)
            .map_err(failed)?
            .as_array()
            .map(|a| a.iter().filter_map(|l| l.get("name").cloned()).collect())
            .unwrap_or_default();
        issues.push(json!({
            "number": number,
            "kind": if pull { "pull request" } else { "issue" },
            "title": text(item, "title", issue_listing).map_err(failed)?,
            "body": text(item, "body", issue_listing).map_err(failed)?,
            "state": text(item, "state", issue_listing).map_err(failed)?,
            "merged": if pull { merged.get(&number).copied().map(Value::Bool).unwrap_or(Value::Null) } else { Value::Null },
            "author": author(item, issue_listing).map_err(failed)?,
            "url": text(item, "html_url", issue_listing).map_err(failed)?,
            "labels": labels,
        }));
    }
    let mut comments = Vec::new();
    let listing_name = LISTINGS[2].0;
    for item in &lists[2] {
        comments.push(json!({
            "on": number_in(item, "issue_url", listing_name).map_err(failed)?,
            "author": author(item, listing_name).map_err(failed)?,
            "body": text(item, "body", listing_name).map_err(failed)?,
            "url": text(item, "html_url", listing_name).map_err(failed)?,
        }));
    }
    let mut reviews = Vec::new();
    let listing_name = LISTINGS[3].0;
    for item in &lists[3] {
        reviews.push(json!({
            "on": number_in(item, "pull_request_url", listing_name).map_err(failed)?,
            "path": text(item, "path", listing_name).map_err(failed)?,
            "author": author(item, listing_name).map_err(failed)?,
            "body": text(item, "body", listing_name).map_err(failed)?,
            "url": text(item, "html_url", listing_name).map_err(failed)?,
        }));
    }
    Ok(
        json!({"repository": repository, "issues": issues, "comments": comments, "review_comments": reviews}),
    )
}
