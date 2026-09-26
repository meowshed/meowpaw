// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Check a commit message against the convention the repository declares.
//!
//! SPC-1050 states the behaviour. The convention sits under `[commits]` in the
//! profile (REQ-1290): the types with their release meaning (REQ-1318), the
//! subject limit (REQ-1302) and the trailers every message carries (REQ-1308,
//! REQ-1310). The attribution check runs whatever the profile says, because
//! the ban admits no exception (REQ-1294, REQ-1295). A message is never
//! reported as meeting a convention nobody declared (REQ-1314).

use crate::profile::{self, Profile, PROFILE};
use regex::Regex;
use std::io::Read;
use std::path::Path;

const DEFAULT_LIMIT: i64 = 72;
const MEANINGS: [&str; 4] = ["major", "minor", "patch", "none"];
const KEYS: [&str; 3] = ["types", "subject_limit", "trailers"];
const MET: u8 = 0;
const VIOLATED: u8 = 1;
const USAGE: u8 = 2;
const UNDECLARED: u8 = 3;

const SUBJECT: &str = r"^(?P<type>[a-z][a-z0-9-]*)(?:\((?P<scope>[^()\s]+)\))?(?P<bang>!)?: (?P<text>\S.*)$";
// The pattern, never a bare name: a path such as plugins/meow-core/ or the
// product a harness targets is not attribution.
const ATTRIBUTION: &str = concat!(
    r"(?i)co-authored-by:.*\b(claude|anthropic|copilot|openai|chatgpt|gpt-?\d|gemini|codex|cursor|devin|aider)\b",
    r"|generated (with|by) \[?(claude|copilot|chatgpt|gemini|cursor|codex|an? ai)",
    r"|noreply@(anthropic|openai)\.com",
);

struct Convention {
    state: &'static str,
    detail: String,
    types: Vec<(String, String)>,
    limit: i64,
    trailers: Vec<String>,
    ignored: Vec<String>,
    malformed: Vec<String>,
}

fn convention(root: &Path) -> Convention {
    let mut found = Convention {
        state: "declared",
        detail: String::new(),
        types: Vec::new(),
        limit: DEFAULT_LIMIT,
        trailers: Vec::new(),
        ignored: Vec::new(),
        malformed: Vec::new(),
    };
    let data = match profile::read(root) {
        Profile::Absent => {
            found.state = "undeclared";
            found.detail = format!("{PROFILE} doesn't exist");
            return found;
        }
        Profile::Unparseable(error) => {
            found.state = "unparseable";
            found.detail = error;
            return found;
        }
        Profile::Parsed(data) => data,
    };
    let table = match data.get("commits") {
        Some(toml::Value::Table(table)) => table,
        _ => {
            found.state = "undeclared";
            found.detail = "the profile has no [commits] table".to_string();
            return found;
        }
    };

    found.ignored = table.keys().filter(|key| !KEYS.contains(&key.as_str())).map(|key| format!("commits.{key}")).collect();
    match table.get("types") {
        None => {}
        Some(toml::Value::Table(types)) => {
            for (name, meaning) in types {
                match meaning {
                    toml::Value::String(meaning) if MEANINGS.contains(&meaning.as_str()) => {
                        found.types.push((name.clone(), meaning.clone()));
                    }
                    toml::Value::String(meaning) => found.malformed.push(format!(
                        "type `{name}` means '{meaning}', not one of {}",
                        MEANINGS.join(", ")
                    )),
                    other => found.malformed.push(format!(
                        "type `{name}` means {other}, not one of {}",
                        MEANINGS.join(", ")
                    )),
                }
            }
        }
        Some(_) => found.malformed.push("`types` isn't a table".to_string()),
    }
    match table.get("subject_limit") {
        None => {}
        Some(toml::Value::Integer(limit)) if *limit > 0 => found.limit = *limit,
        Some(_) => found.malformed.push("`subject_limit` isn't a positive whole number".to_string()),
    }
    match table.get("trailers") {
        None => {}
        Some(toml::Value::Array(items)) if items.iter().all(|item| item.is_str()) => {
            found.trailers = items.iter().filter_map(|item| item.as_str().map(str::to_string)).collect();
        }
        Some(_) => found.malformed.push("`trailers` isn't a list of names".to_string()),
    }
    found
}

fn report_convention(root: &Path) -> u8 {
    let found = convention(root);
    if found.state != "declared" {
        println!("meow-scm convention: {} ({})", found.state, found.detail);
        return UNDECLARED;
    }
    println!("meow-scm convention, from {PROFILE}\n");
    for (name, meaning) in &found.types {
        println!("type {name:<10} release: {meaning}");
    }
    println!("subject limit  {} characters", found.limit);
    let trailers = if found.trailers.is_empty() { "none declared".to_string() } else { found.trailers.join(", ") };
    println!("trailers       {trailers}");
    for problem in &found.malformed {
        println!("malformed      {problem}");
    }
    if !found.ignored.is_empty() {
        println!("\nNot read by meow-scm: {}", found.ignored.join(", "));
    }
    MET
}

/// Every violation, as (line number, rule, detail).
fn problems(message: &str, found: &Convention) -> Vec<(usize, String, String)> {
    let mut lines: Vec<&str> = message.lines().filter(|line| !line.starts_with('#')).collect();
    while lines.last().is_some_and(|line| line.trim().is_empty()) {
        lines.pop();
    }
    if lines.is_empty() || lines[0].trim().is_empty() {
        return vec![(1, "empty message".into(), "the message has no subject".into())];
    }

    let attribution = Regex::new(ATTRIBUTION).expect("the attribution pattern compiles");
    let mut found_problems = Vec::new();
    for (index, line) in lines.iter().enumerate() {
        if attribution.is_match(line) {
            found_problems.push((
                index + 1,
                "attribution".into(),
                format!("\"{}\" credits a tool, an agent or a vendor", line.trim()),
            ));
        }
    }
    if found.state != "declared" {
        return found_problems;
    }

    let subject = lines[0];
    match Regex::new(SUBJECT).expect("the subject pattern compiles").captures(subject) {
        None => found_problems.push((1, "subject form".into(), "the subject isn't `type(scope)!: description`".into())),
        Some(parts) => {
            let kind = &parts["type"];
            if !found.types.is_empty() && !found.types.iter().any(|(name, _)| name == kind) {
                let declared: Vec<&str> = found.types.iter().map(|(name, _)| name.as_str()).collect();
                found_problems.push((
                    1,
                    "declared type".into(),
                    format!("`{kind}` isn't a declared type ({})", declared.join(", ")),
                ));
            }
        }
    }
    let length = subject.chars().count() as i64;
    if length > found.limit {
        found_problems.push((
            1,
            "subject length".into(),
            format!("{length} characters, over the limit of {}", found.limit),
        ));
    }
    if subject.trim_end().ends_with('.') {
        found_problems.push((1, "subject ending".into(), "the subject ends in a full stop".into()));
    }
    if lines.len() > 1 && !lines[1].trim().is_empty() {
        found_problems.push((
            2,
            "blank line".into(),
            "the body follows the subject with no empty line between them".into(),
        ));
    }
    for trailer in &found.trailers {
        let pattern = Regex::new(&format!(r"^{}: \S", regex::escape(trailer))).expect("a trailer pattern compiles");
        if !lines[1..].iter().any(|line| pattern.is_match(line)) {
            found_problems.push((lines.len(), "trailer".into(), format!("the `{trailer}` trailer is missing")));
        }
    }
    found_problems
}

fn check_message(root: &Path, source: Option<&str>) -> u8 {
    let message = match source {
        None => {
            let mut text = String::new();
            let _ = std::io::stdin().read_to_string(&mut text);
            text
        }
        Some(path) => match std::fs::read(path) {
            Ok(bytes) => String::from_utf8_lossy(&bytes).into_owned(),
            Err(error) => {
                eprintln!("meow-scm check-message: can't read {path}: {error}");
                return USAGE;
            }
        },
    };
    let found = convention(root);
    let mut listed = problems(&message, &found);
    listed.sort();
    for (number, rule, detail) in &listed {
        println!("line {number}: {rule}: {detail}");
    }
    if found.state == "declared" {
        for problem in &found.malformed {
            println!("convention: malformed: {problem}");
        }
    }
    if !listed.is_empty() {
        let plural = if listed.len() != 1 { "s" } else { "" };
        println!(
            "meow-scm check-message: {} problem{plural}; don't use this message until they are fixed",
            listed.len()
        );
        return VIOLATED;
    }
    if found.state != "declared" {
        println!(
            "meow-scm check-message: convention {} ({}); only the attribution check ran, and it found nothing",
            found.state, found.detail
        );
        return UNDECLARED;
    }
    println!("meow-scm check-message: the message meets the declared convention");
    MET
}

pub fn main(args: &[String]) -> u8 {
    let root = profile::repository_root();
    let args: Vec<&str> = args.iter().map(String::as_str).collect();
    match args.as_slice() {
        ["convention"] => report_convention(&root),
        ["check-message"] => check_message(&root, None),
        ["check-message", path] => check_message(&root, Some(path)),
        _ => {
            eprintln!("usage: meow-scm convention | meow-scm check-message [FILE]");
            USAGE
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_path_or_a_product_name_is_not_attribution() {
        let attribution = Regex::new(ATTRIBUTION).unwrap();
        assert!(!attribution.is_match("fix: route the shape in plugins/meow-core/ for Claude Code"));
        assert!(attribution.is_match(&format!("Co-Authored-{}", "By: Claude <x@example.org>")));
    }
}
