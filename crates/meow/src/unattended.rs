// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-unattended plan`: the posture an unattended run declares and the deny
//! rules it yields (SPC-1200).
//!
//! The posture comes from the `[unattended]` table and never from a session's
//! default (REQ-2388), so a table that is missing or wrong is unresolved. The
//! `loop` feature compiles this module in too, so the start hook and the
//! guard read the posture without running another unit's program. `plan`
//! writes nothing and starts nothing.

use crate::profile::{self, Profile};
use std::path::{Path, PathBuf};

const MODES: [&str; 3] = ["dontAsk", "acceptEdits", "auto"];
const GATES: [&str; 8] = [
    "research",
    "requirements",
    "design",
    "spec",
    "epic",
    "implement",
    "review",
    "merge",
];
const REQUIRED: [&str; 3] = ["permission_mode", "gates", "release"];
const NO_TABLE: &str = "unresolved: no [unattended] table in .meowpaw/profile.toml";
const SKIP: [&str; 5] = ["node_modules", "target", "templates", "_archive", "evals"];

const LIMITS: &str = "\
The deny rules have three limits:
- A Bash deny matches the command's text, so a push hidden in a script isn't
  denied, and neither is a push to a branch that is the trunk under another name.
- A merge through the code host's interface needs no push, so no deny rule stops
  it. The checks the run makes before a merge hold it, and the deny rules are a
  second line.
- A new record whose front matter supersedes or withdraws an approved one retires
  it without editing its file, so no deny rule stops it.";

/// The table as it resolved, with each default filled in.
#[cfg_attr(not(feature = "loop"), allow(dead_code))]
pub(crate) struct Posture {
    pub mode: String,
    pub gates: Vec<String>,
    /// The release command, or none where the table says `false`.
    pub release: Option<String>,
    pub amend_approved: bool,
    pub trunk: String,
}

#[cfg_attr(not(feature = "unattended"), allow(dead_code))]
pub fn main(args: &[String]) -> u8 {
    let args: Vec<&str> = args.iter().map(String::as_str).collect();
    match args.as_slice() {
        ["plan"] => plan(&root()),
        _ => {
            eprintln!("usage: meow-unattended plan");
            2
        }
    }
}

fn root() -> PathBuf {
    let root = profile::repository_root();
    std::fs::canonicalize(&root).unwrap_or(root)
}

/// The posture the repository at `root` declares, or each refusal found in it.
#[cfg_attr(not(feature = "loop"), allow(dead_code))]
pub(crate) fn posture(root: &Path) -> Result<Posture, Vec<String>> {
    from_profile(profile::read(root))
}

fn from_profile(read: Profile) -> Result<Posture, Vec<String>> {
    let data = match read {
        Profile::Parsed(data, _) => data,
        Profile::Absent => return Err(vec![NO_TABLE.to_string()]),
        Profile::Unparseable(reason) => {
            return Err(vec![format!(
                "unresolved: the profile doesn't parse: {reason}"
            )]);
        }
    };
    let Some(table) = data.get("unattended").and_then(toml::Value::as_table) else {
        return Err(vec![NO_TABLE.to_string()]);
    };
    let trunk = data
        .get("git")
        .and_then(|git| git.get("trunk"))
        .and_then(toml::Value::as_str)
        .map(str::to_string);
    resolve(table, trunk)
}

fn plan(root: &Path) -> u8 {
    let read = profile::read(root);
    for line in profile::report(&read) {
        println!("{line}");
    }
    let record_root = match &read {
        Profile::Parsed(data, _) => root.join(
            data.get("record")
                .and_then(toml::Value::as_table)
                .and_then(|r| r.get("root"))
                .and_then(toml::Value::as_str)
                .unwrap_or("project"),
        ),
        _ => root.join("project"),
    };
    let posture = match from_profile(read) {
        Ok(posture) => posture,
        Err(refusals) => return unresolved(&refusals),
    };
    println!("{}", table_text(&posture));
    match &posture.release {
        Some(command) => {
            println!("the run runs `{command}` once, after a merge, from the repository's root")
        }
        None => println!("the run releases nothing"),
    }
    println!();
    println!("deny rules:");
    println!("  Edit or Write of .meowpaw/** and .claude/** in the work tree");
    println!(
        "  Bash git push naming {}, HEAD or no branch, so the run lands work through a pull request",
        posture.trunk
    );
    if posture.amend_approved {
        println!("  none for an approved record: amend_approved is true");
    } else {
        println!(
            "  Edit or Write of an approved requirement or decision ({} files now), so the run amends one by writing a new record",
            approved(&record_root).len()
        );
    }
    println!();
    println!("A requirement or decision approved after this plan is protected as soon as it is.");
    println!();
    println!("{LIMITS}");
    0
}

fn unresolved(refusals: &[String]) -> u8 {
    for refusal in refusals {
        println!("{refusal}");
    }
    3
}

/// The table's keys, checked, or every refusal found in it.
fn resolve(table: &toml::Table, trunk: Option<String>) -> Result<Posture, Vec<String>> {
    let mut refusals = Vec::new();
    for key in REQUIRED {
        if !table.contains_key(key) {
            refusals.push(format!("unresolved: [unattended] {key} is not declared"));
        }
    }
    let mode = match table.get("permission_mode") {
        Some(toml::Value::String(mode)) if MODES.contains(&mode.as_str()) => mode.clone(),
        Some(value) => {
            refusals.push(format!(
                "unresolved: [unattended] permission_mode {} is refused",
                shown(value)
            ));
            String::new()
        }
        None => String::new(),
    };
    let gates = strings(table, "gates", &mut refusals);
    for gate in &gates {
        if !GATES.contains(&gate.as_str()) {
            refusals.push(format!(
                "unresolved: [unattended] gates names {gate}, which is not a gate"
            ));
        }
    }
    let release = match table.get("release") {
        None | Some(toml::Value::Boolean(false)) => None,
        Some(toml::Value::String(command)) if !command.trim().is_empty() => Some(command.clone()),
        Some(value) => {
            refusals.push(format!(
                "unresolved: [unattended] release {} is not a command or false",
                shown(value)
            ));
            None
        }
    };
    let amend_approved = flag(table, "amend_approved", &mut refusals);
    if trunk.is_none() {
        refusals
            .push("unresolved: [git] trunk is not declared, so the push rule has no trunk".into());
    }
    if refusals.is_empty() {
        Ok(Posture {
            mode,
            gates,
            release,
            amend_approved,
            trunk: trunk.unwrap_or_default(),
        })
    } else {
        Err(refusals)
    }
}

fn strings(table: &toml::Table, key: &str, refusals: &mut Vec<String>) -> Vec<String> {
    let Some(value) = table.get(key) else {
        return Vec::new();
    };
    let list: Option<Vec<String>> = value.as_array().and_then(|items| {
        items
            .iter()
            .map(|item| item.as_str().map(str::to_string))
            .collect()
    });
    list.unwrap_or_else(|| {
        refusals.push(format!(
            "unresolved: [unattended] {key} {} is not a list of strings",
            shown(value)
        ));
        Vec::new()
    })
}

fn flag(table: &toml::Table, key: &str, refusals: &mut Vec<String>) -> bool {
    match table.get(key) {
        None => false,
        Some(toml::Value::Boolean(value)) => *value,
        Some(value) => {
            refusals.push(format!(
                "unresolved: [unattended] {key} {} is not true or false",
                shown(value)
            ));
            false
        }
    }
}

/// A value as the profile wrote it, a string without its quotes.
fn shown(value: &toml::Value) -> String {
    match value {
        toml::Value::String(text) => text.clone(),
        other => other.to_string(),
    }
}

fn table_text(posture: &Posture) -> String {
    let gates: Vec<String> = posture.gates.iter().map(|g| format!("{g:?}")).collect();
    let release = match &posture.release {
        Some(command) => format!("{command:?}"),
        None => "false".to_string(),
    };
    format!(
        "[unattended]\npermission_mode = {:?}\ngates = [{}]\nrelease = {release}\namend_approved = {}\n",
        posture.mode,
        gates.join(", "),
        posture.amend_approved
    )
}

/// Whether a command's text is a `git push` the posture forbids: one that
/// names the trunk or `HEAD`, pushes every branch, or names no branch, so a
/// run lands work only through a pull request (REQ-3718). It reads the text
/// and not what it expands to.
#[cfg_attr(not(feature = "loop"), allow(dead_code))]
pub(crate) fn push_denied(command: &str, trunk: &str) -> bool {
    let words: Vec<&str> = command
        .split(|c: char| c.is_whitespace() || "'\"`;|()&".contains(c))
        .filter(|w| !w.is_empty())
        .collect();
    let mut denied = false;
    for (i, word) in words.iter().enumerate() {
        if !(word.ends_with("git") || word.ends_with("git.exe")) {
            continue;
        }
        let Some(offset) = words[i + 1..].iter().take(5).position(|w| *w == "push") else {
            continue;
        };
        let after = &words[i + 1 + offset + 1..];
        if after.iter().any(|w| *w == "--all" || *w == "--mirror") {
            denied = true;
        }
        let arguments: Vec<&str> = after
            .iter()
            .copied()
            .take_while(|w| !w.ends_with("git") && *w != "git.exe")
            .filter(|w| !w.starts_with('-'))
            .collect();
        if arguments.len() < 2 {
            denied = true;
        }
        for argument in &arguments {
            let argument = argument.trim_start_matches('+');
            let destination = argument.rsplit(':').next().unwrap_or(argument);
            if destination == trunk
                || destination == "HEAD"
                || destination.ends_with(&format!("refs/heads/{trunk}"))
                || argument.starts_with("HEAD:")
            {
                denied = true;
            }
        }
    }
    denied
}

/// Each requirement and decision under the record whose front matter says
/// `status: approved`.
pub(crate) fn approved(record: &Path) -> Vec<PathBuf> {
    let mut files = Vec::new();
    markdown_under(record, &mut files);
    files
        .into_iter()
        .filter(|path| {
            let text = std::fs::read_to_string(path).unwrap_or_default();
            let fields = front_matter(&text);
            let field = |key: &str| {
                fields
                    .iter()
                    .find(|(k, _)| k == key)
                    .map(|(_, v)| v.as_str())
            };
            matches!(field("artifact").map(bare), Some("requirement" | "adr"))
                && field("status").map(bare) == Some("approved")
        })
        .collect()
}

fn markdown_under(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    let mut paths: Vec<PathBuf> = entries.flatten().map(|e| e.path()).collect();
    paths.sort();
    for path in paths {
        let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        if path.is_dir() {
            if !name.starts_with('.') && !SKIP.contains(&name) {
                markdown_under(&path, out);
            }
        } else if name.ends_with(".md") {
            out.push(path);
        }
    }
}

/// The top-level `key: value` pairs of a file's YAML front matter, with LF or
/// CRLF line endings.
fn front_matter(text: &str) -> Vec<(String, String)> {
    let text = text.replace("\r\n", "\n");
    let Some(rest) = text.strip_prefix("---\n") else {
        return Vec::new();
    };
    let end = rest.find("\n---").unwrap_or(0);
    rest[..end]
        .lines()
        .filter(|line| !line.starts_with([' ', '\t']))
        .filter_map(|line| line.split_once(':'))
        .map(|(k, v)| (k.trim().to_string(), v.trim().to_string()))
        .collect()
}

/// A value without its trailing comment and its quotes, as `paw check` reads
/// it, so the two agree on which records are approved.
fn bare(value: &str) -> &str {
    let value = value.split(" #").next().unwrap_or(value).trim();
    value.trim_matches('"').trim_matches('\'')
}

#[cfg(test)]
mod tests {
    use super::*;

    fn table(text: &str) -> toml::Table {
        text.parse().unwrap()
    }

    #[test]
    fn every_refusal_is_reported_in_one_run() {
        let refusals = resolve(
            &table("permission_mode = \"manual\"\ngates = [\"verify\"]\n"),
            None,
        )
        .err()
        .unwrap();
        assert!(
            refusals
                .iter()
                .any(|r| r.contains("permission_mode manual is refused"))
        );
        assert!(refusals.iter().any(|r| r.contains("gates names verify")));
        assert!(
            refusals
                .iter()
                .any(|r| r.contains("release is not declared"))
        );
        assert!(
            refusals
                .iter()
                .any(|r| r.contains("[git] trunk is not declared"))
        );
    }

    #[test]
    fn a_release_of_false_resolves_to_none() {
        let posture = resolve(
            &table("permission_mode = \"dontAsk\"\ngates = []\nrelease = false\n"),
            Some("main".into()),
        )
        .ok()
        .unwrap();
        assert!(posture.release.is_none());
        assert!(!posture.amend_approved);
    }

    #[test]
    fn a_push_is_denied_unless_it_names_a_branch_that_is_not_the_trunk() {
        assert!(push_denied("git push", "main"));
        assert!(push_denied("git push origin", "main"));
        assert!(push_denied("git push origin main", "main"));
        assert!(push_denied("git push origin HEAD", "main"));
        assert!(push_denied("git push origin feat/x:main", "main"));
        assert!(push_denied("git push --all origin", "main"));
        assert!(!push_denied("git push origin feat/x", "main"));
        assert!(!push_denied("git push -u origin feat/x", "main"));
        assert!(!push_denied("git status", "main"));
    }

    #[test]
    fn front_matter_reads_top_level_keys() {
        let fields = front_matter("---\nid: REQ-1\nstatus: approved # frozen\n---\n\n# T\n");
        assert_eq!(bare(&fields[1].1), "approved");
    }
}
