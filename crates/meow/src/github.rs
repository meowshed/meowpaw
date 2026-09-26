// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Read a GitHub repository's history, and write nothing (ADR-1290).
//!
//! SPC-1080 states the behaviour. `history` reads four listings through
//! `gh api`, the interface beneath GitHub's own client, every page of each and
//! through its cache, and prints one JSON document. It takes each field by
//! name, so a field the forge stops sending fails by that name, and a listing
//! it can't read leaves the history unread rather than printed in part.

use serde_json::{json, Value};
use std::process::{Command, Stdio};

const USAGE: u8 = 2;
const UNREAD: u8 = 3;
const LISTINGS: [(&str, &str); 4] = [
    ("issues and pull requests", "issues?state=all&per_page=100"),
    ("pull requests", "pulls?state=all&per_page=100"),
    ("conversation comments", "issues/comments?per_page=100"),
    ("review comments", "pulls/comments?per_page=100"),
];

pub fn main(args: &[String]) -> u8 {
    match args {
        [command] if command == "history" => history(None),
        [command, repository] if command == "history" => history(Some(repository.as_str())),
        _ => {
            eprintln!("usage: meow-github history [<owner>/<name>]");
            USAGE
        }
    }
}

fn gh(args: &[&str]) -> Result<Value, String> {
    let out = Command::new("gh")
        .args(args)
        .env("GH_PROMPT_DISABLED", "1")
        .stdin(Stdio::null())
        .output()
        .map_err(|e| format!("gh couldn't run ({e}); install GitHub's client, gh, and sign in with `gh auth login`"))?;
    if !out.status.success() {
        let said = String::from_utf8_lossy(&out.stderr).trim().to_string();
        return Err(if said.is_empty() { format!("gh exited with {}", out.status) } else { said });
    }
    serde_json::from_slice(&out.stdout).map_err(|e| format!("gh printed no JSON ({e})"))
}

/// A field of a response, by name, so that one the forge stopped sending fails
/// by that name rather than reading as empty (REQ-2556).
fn field<'a>(item: &'a Value, name: &str, listing: &str) -> Result<&'a Value, String> {
    item.get(name).ok_or_else(|| format!("a response in the {listing} listing lacks the field `{name}`"))
}

fn text(item: &Value, name: &str, listing: &str) -> Result<Value, String> {
    let value = field(item, name, listing)?;
    Ok(if value.is_null() { Value::Null } else { Value::String(value.as_str().unwrap_or_default().to_string()) })
}

fn author(item: &Value, listing: &str) -> Result<Value, String> {
    Ok(field(item, "user", listing)?.get("login").cloned().unwrap_or(Value::Null))
}

/// The number at the end of an issue's or a pull request's address.
fn number_in(item: &Value, name: &str, listing: &str) -> Result<u64, String> {
    let address = field(item, name, listing)?.as_str().unwrap_or_default();
    address.rsplit('/').next().and_then(|n| n.parse().ok()).ok_or_else(|| format!("the {listing} listing gave `{name}` with no number"))
}

/// Every item of a listing, every page of it read (REQ-2560), through the
/// client's cache (REQ-2564).
fn listing(repository: &str, name: &str, path: &str) -> Result<Vec<Value>, String> {
    let endpoint = format!("repos/{repository}/{path}");
    let pages = gh(&["api", &endpoint, "--paginate", "--slurp", "--cache", "1h"]).map_err(|e| format!("{name}, {endpoint}: {e}"))?;
    let Value::Array(pages) = pages else { return Err(format!("{name}, {endpoint}: the pages aren't a list")) };
    let mut items = Vec::new();
    for page in pages {
        match page {
            Value::Array(page) => items.extend(page),
            _ => return Err(format!("{name}, {endpoint}: a page isn't a list")),
        }
    }
    Ok(items)
}

fn history(repository: Option<&str>) -> u8 {
    let repository = match repository {
        Some(name) => name.to_string(),
        None => match gh(&["repo", "view", "--json", "nameWithOwner"]) {
            Ok(view) => view.get("nameWithOwner").and_then(Value::as_str).unwrap_or_default().to_string(),
            Err(e) => {
                println!("meow-github history: unread: couldn't name this directory's repository: {e}; name it as <owner>/<name>");
                return UNREAD;
            }
        },
    };
    match read(&repository) {
        Ok(document) => {
            println!("{}", serde_json::to_string_pretty(&document).unwrap_or_default());
            0
        }
        Err((read, e)) => {
            println!("meow-github history: unread: {e}");
            let read = if read.is_empty() { "nothing".to_string() } else { read.join(", ") };
            println!("read before it stopped: {read}; no document is printed, because a part of the history reads as the whole of it");
            UNREAD
        }
    }
}

fn read(repository: &str) -> Result<Value, (Vec<&'static str>, String)> {
    let mut read = Vec::new();
    let mut lists = Vec::new();
    for (name, path) in LISTINGS {
        let items = listing(repository, name, path).map_err(|e| (read.clone(), e))?;
        read.push(name);
        lists.push(items);
    }
    let failed = |e: String| (read.clone(), e);
    let (issue_listing, pull_listing) = (LISTINGS[0].0, LISTINGS[1].0);
    let mut merged = std::collections::BTreeMap::new();
    for pull in &lists[1] {
        let number = field(pull, "number", pull_listing).map_err(failed)?.as_u64().unwrap_or_default();
        merged.insert(number, !field(pull, "merged_at", pull_listing).map_err(failed)?.is_null());
    }
    let mut issues = Vec::new();
    for item in &lists[0] {
        let number = field(item, "number", issue_listing).map_err(failed)?.as_u64().unwrap_or_default();
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
    Ok(json!({"repository": repository, "issues": issues, "comments": comments, "review_comments": reviews}))
}
