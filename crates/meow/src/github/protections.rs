// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Report which of six protections are in force on the declared trunk, and
//! write nothing (ADR-2520, REQ-2194). SPC-1080 states the behaviour under
//! "Reporting the trunk's protections".
//!
//! The report reads the branch's classic protection and the rules in force on
//! the branch, both through the request layer. A protection either one sets
//! is in force. A protection neither read shows in force is absent only where
//! both reads answered, and unread otherwise, because a read that failed
//! can't show a protection is missing.

use super::request::{Failure, Layer};
use crate::profile::{self, Profile};
use serde_json::Value;

const UNREAD: u8 = 3;

/// The six protections, in the order the report prints them, which is the
/// order of value RES-0066 gave them.
const NAMES: [&str; 6] = [
    "force pushes blocked",
    "deletion blocked",
    "required reviews",
    "required checks",
    "signed commits",
    "linear history",
];

/// The rule type a ruleset uses for each protection, in the order of `NAMES`.
const RULES: [&str; 6] = [
    "non_fast_forward",
    "deletion",
    "pull_request",
    "required_status_checks",
    "required_signatures",
    "required_linear_history",
];

/// What one read showed: each protection in force or not, or `None` where
/// the read gave no answer.
type Shown = Option<[bool; 6]>;

pub fn run(layer: &mut Layer, repository: Option<&str>) -> u8 {
    let read = profile::read(&profile::repository_root());
    for line in profile::report(&read) {
        println!("meow-github protections: {line}");
    }
    let trunk = match &read {
        Profile::Parsed(table, _) => table
            .get("git")
            .and_then(|git| git.get("trunk"))
            .and_then(|trunk| trunk.as_str())
            .map(str::to_string),
        _ => None,
    };
    let Some(trunk) = trunk.filter(|t| !t.is_empty()) else {
        println!(
            "meow-github protections: no trunk declared under [git] in {}, so no protection is read; declare `[git] trunk`",
            profile::PROFILE
        );
        return UNREAD;
    };
    let repository = match super::name_repository(layer, repository) {
        Ok(name) => name,
        Err(failure) => {
            report(Err(failure), &mut false);
            return UNREAD;
        }
    };
    let mut stopped = false;
    let classic = report(
        classic(
            layer,
            &format!("repos/{repository}/branches/{trunk}/protection"),
        ),
        &mut stopped,
    );
    let rules = if stopped {
        None
    } else {
        report(
            rules(
                layer,
                &format!("repos/{repository}/rules/branches/{trunk}?per_page=100"),
            ),
            &mut stopped,
        )
    };
    let mut code = 0;
    for (i, name) in NAMES.iter().enumerate() {
        let shown = |read: Shown| read.map(|r| r[i]);
        let state = match (shown(classic), shown(rules)) {
            (Some(true), _) | (_, Some(true)) => "in force",
            (Some(false), Some(false)) => "absent",
            _ => {
                code = UNREAD;
                "unread"
            }
        };
        println!("{name}: {state}");
    }
    code
}

/// What a read showed, printing its failure as the layer reports it, and
/// noting a throttle or a rejected credential, after which nothing more is
/// sent.
fn report(read: Result<[bool; 6], Failure>, stopped: &mut bool) -> Shown {
    match read {
        Ok(shown) => Some(shown),
        Err(failure) => {
            match &failure {
                Failure::Throttled(_) | Failure::Rejected(_) => *stopped = true,
                Failure::Refused(_) | Failure::Failed(_) => {}
            }
            match failure {
                Failure::Failed(e) => println!("meow-github protections: unread: {e}"),
                other => println!("{other}"),
            }
            None
        }
    }
}

/// The classic protection at `endpoint`, where a 404 says the branch has
/// none, so every classic protection is absent.
fn classic(layer: &mut Layer, endpoint: &str) -> Result<[bool; 6], Failure> {
    let Some(protection) = layer.get_unless_missing(endpoint)? else {
        return Ok([false; 6]);
    };
    // A setting GitHub always sends fails by its name where it stops sending
    // it, rather than reading as absent (REQ-2556).
    let enabled = |name: &str| {
        protection
            .get(name)
            .map(|setting| setting.get("enabled").and_then(Value::as_bool) == Some(true))
            .ok_or_else(|| {
                Failure::Failed(format!(
                    "GET {endpoint}: the protection lacks the field `{name}`"
                ))
            })
    };
    let set = |name: &str| protection.get(name).is_some_and(|v| !v.is_null());
    Ok([
        !enabled("allow_force_pushes")?,
        !enabled("allow_deletions")?,
        set("required_pull_request_reviews"),
        set("required_status_checks"),
        enabled("required_signatures")?,
        enabled("required_linear_history")?,
    ])
}

/// The rules in force on the branch, every page of them.
fn rules(layer: &mut Layer, endpoint: &str) -> Result<[bool; 6], Failure> {
    let mut shown = [false; 6];
    let mut next = Some(endpoint.to_string());
    while let Some(page) = next {
        let (body, following) = layer.page(&page, false)?;
        let Value::Array(rules) = body else {
            return Err(Failure::Failed(format!(
                "GET {page}: the rules aren't a list"
            )));
        };
        for rule in rules {
            let kind = rule.get("type").and_then(Value::as_str).unwrap_or_default();
            if let Some(i) = RULES.iter().position(|r| *r == kind) {
                shown[i] = true;
            }
        }
        next = following;
    }
    Ok(shown)
}
