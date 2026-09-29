// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-unattended plan`: the posture an unattended run declares, and the
//! snapshot that holds its authority (SPC-1200).
//!
//! The run's posture comes from the `[unattended]` table and never from a
//! session's default (REQ-2388), so a table that is missing or wrong is
//! unresolved and nothing is written. `plan` starts nothing (ADR-2000).

use crate::profile::{self, Profile};
use serde_json::{Map, Value, json};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

const MODES: [&str; 5] = ["manual", "plan", "dontAsk", "acceptEdits", "auto"];
const GATES: [&str; 7] = [
    "research",
    "requirements",
    "design",
    "epic",
    "verify",
    "review",
    "merge",
];
const REQUIRED: [&str; 4] = ["permission_mode", "budget_usd", "gates", "units"];
const NO_TABLE: &str = "unresolved: no [unattended] table in .meowpaw/profile.toml";
const SKIP: [&str; 5] = ["node_modules", "target", "templates", "_archive", "evals"];

const LIMITS: &str = "\
The deny rules have four limits:
- A Bash deny rule stops only the forms it matches, so `git -C . push origin main`
  isn't denied, and neither is `git push origin` or `git push --force-with-lease`
  while the trunk is checked out.
- An Edit deny rule reaches the file tools and the file commands Claude Code
  recognises, and not a script that opens the file itself.
- A merge through the code host's interface isn't denied.
- A new record whose front matter supersedes or withdraws an approved one retires
  it without editing its file, so no deny rule stops it.";

/// The table as `plan` resolved it, with each default filled in.
struct Authority {
    mode: String,
    budget: toml::Value,
    gates: Vec<String>,
    units: Vec<Unit>,
    merge_protected: bool,
    amend_approved: bool,
}

/// A declared unit, with the name and version its `plugin.json` holds.
struct Unit {
    entry: String,
    name: String,
    version: String,
}

pub fn main(args: &[String]) -> u8 {
    let args: Vec<&str> = args.iter().map(String::as_str).collect();
    match args.as_slice() {
        ["plan"] => plan(&root()),
        ["plan", "--purge"] => purge(&root()),
        _ => {
            eprintln!("usage: meow-unattended plan [--purge]");
            2
        }
    }
}

fn root() -> PathBuf {
    let root = profile::repository_root();
    std::fs::canonicalize(&root).unwrap_or(root)
}

fn plan(root: &Path) -> u8 {
    let data = match profile::read(root) {
        Profile::Parsed(data) => data,
        Profile::Absent => return unresolved(&[NO_TABLE.to_string()]),
        Profile::Unparseable(reason) => {
            return unresolved(&[format!("unresolved: the profile doesn't parse: {reason}")]);
        }
    };
    let Some(table) = data.get("unattended").and_then(toml::Value::as_table) else {
        return unresolved(&[NO_TABLE.to_string()]);
    };
    let trunk = data
        .get("git")
        .and_then(|git| git.get("trunk"))
        .and_then(toml::Value::as_str)
        .map(str::to_string);
    let env = env_refusals(root);
    let authority = match resolve(table, trunk.is_some(), root) {
        Ok(authority) if env.is_empty() => authority,
        Ok(_) => return unresolved(&env),
        Err(mut refusals) => {
            refusals.extend(env);
            return unresolved(&refusals);
        }
    };
    let record = data
        .get("record")
        .and_then(toml::Value::as_table)
        .map(|record| {
            root.join(
                record
                    .get("root")
                    .and_then(toml::Value::as_str)
                    .unwrap_or("project"),
            )
        });

    // The folder is made before the rule naming it is written, so the rule
    // names it as the file system resolves it, through any symbolic link.
    let folder = match folder(root).map(|folder| made(&folder)) {
        Some(Ok(folder)) => Some(folder),
        Some(Err(reason)) => {
            return unresolved(&[format!("unresolved: snapshot not written: {reason}")]);
        }
        None => None,
    };
    let tree = slashed(root);
    let mut deny = vec![
        format!("Edit(/{tree}/.meowpaw/**)"),
        format!("Edit(/{tree}/.claude/**)"),
    ];
    if let Some(protected) = folder.clone().or_else(|| location(root)) {
        deny.push(format!("Edit(/{}/**)", slashed(&protected)));
    }
    if !authority.merge_protected {
        let trunk = trunk.as_deref().unwrap_or_default();
        deny.push(format!("Bash(git push *{trunk}*)"));
        deny.push("Bash(git push)".to_string());
        deny.push("Bash(git push *HEAD*)".to_string());
    }
    if !authority.amend_approved
        && let Some(record) = &record
    {
        for path in approved(record) {
            deny.push(format!("Edit(/{})", slashed(&path)));
        }
    }

    let content = snapshot(&authority, &deny);
    let kept = match &folder {
        Some(folder) => match keep(folder, &content) {
            Ok(path) => Some(path),
            Err(reason) => {
                return unresolved(&[format!("unresolved: snapshot not written: {reason}")]);
            }
        },
        None if state_off() => None,
        None => {
            return unresolved(&[format!(
                "unresolved: snapshot not written: {}",
                no_state_reason()
            )]);
        }
    };

    println!("{}", table_text(&authority));
    if authority.units.is_empty() {
        println!("units: none declared");
    } else {
        println!("units, each with the name and version its plugin.json holds:");
        for unit in &authority.units {
            println!("  {}  {} {}", unit.entry, unit.name, unit.version);
        }
    }
    println!();
    println!("The command that would start the run, one argument a line:");
    println!();
    let settings = kept.as_ref().map_or_else(
        || "<the snapshot below>".to_string(),
        |path| quoted(&path.to_string_lossy()),
    );
    let mut line: Vec<String> = vec!["claude".into(), "-p".into(), "--bare".into()];
    for unit in &authority.units {
        line.push(format!("--plugin-dir {}", quoted(&unit.entry)));
    }
    line.push(format!("--permission-mode {}", authority.mode));
    line.push("--permission-prompts none".into());
    line.push("--disallowed-tools AskUserQuestion".into());
    line.push("--output-format stream-json".into());
    line.push("--verbose".into());
    line.push(format!("--max-budget-usd {}", authority.budget));
    line.push(format!("--settings {settings}"));
    let last = line.len() - 1;
    for (n, argument) in line.iter().enumerate() {
        let indent = if n == 0 { "" } else { "  " };
        let tail = if n == last { "" } else { " \\" };
        println!("  {indent}{argument}{tail}");
    }
    println!();
    match &kept {
        Some(path) => println!("snapshot: {}", path.display()),
        None => {
            println!(
                "no snapshot kept, since state writing is off (MEOWPAW_STATE=off); its content:"
            );
            println!("{content}");
        }
    }
    println!();
    println!("deny rules:");
    for rule in &deny {
        println!("  {rule}");
    }
    if record.is_none() && !authority.amend_approved {
        println!("no record to protect: the profile declares no [record]");
    }
    println!();
    println!(
        "A requirement or decision approved after this plan isn't protected until plan runs again."
    );
    println!();
    println!("{LIMITS}");
    println!();
    println!("The command needs ANTHROPIC_API_KEY in its environment.");
    0
}

fn unresolved(refusals: &[String]) -> u8 {
    for refusal in refusals {
        println!("{refusal}");
    }
    3
}

/// The table's keys, checked, or every refusal found in it.
fn resolve(table: &toml::Table, has_trunk: bool, root: &Path) -> Result<Authority, Vec<String>> {
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
    let budget = table.get("budget_usd").cloned();
    if let Some(value) = &budget {
        let positive = match value {
            toml::Value::Integer(n) => *n > 0,
            toml::Value::Float(n) => n.is_finite() && *n > 0.0,
            _ => false,
        };
        if !positive {
            refusals.push(format!(
                "unresolved: [unattended] budget_usd {} is not a positive number",
                shown(value)
            ));
        }
    }
    let gates = strings(table, "gates", &mut refusals);
    for gate in &gates {
        if !GATES.contains(&gate.as_str()) {
            refusals.push(format!(
                "unresolved: [unattended] gates names {gate}, which is not a gate"
            ));
        }
    }
    let units: Vec<Unit> = strings(table, "units", &mut refusals)
        .into_iter()
        .filter_map(|entry| unit(root, entry, &mut refusals))
        .collect();
    let merge_protected = flag(table, "merge_protected", &mut refusals);
    let amend_approved = flag(table, "amend_approved", &mut refusals);
    if merge_protected && table.contains_key("gates") && !gates.iter().any(|g| g == "merge") {
        refusals.push("unresolved: merge_protected is true and gates lacks merge".to_string());
    }
    if !merge_protected && !has_trunk {
        refusals.push(
            "unresolved: [git] trunk is not declared, so the push rules have no trunk to protect"
                .to_string(),
        );
    }
    match budget {
        Some(budget) if refusals.is_empty() => Ok(Authority {
            mode,
            budget,
            gates,
            units,
            merge_protected,
            amend_approved,
        }),
        _ => Err(refusals),
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

/// A `units` entry, loaded by name: a URL, and a directory that holds no
/// `.claude-plugin/plugin.json` of its own, such as a folder of units whose
/// children would load by discovery, are refused (REQ-2392).
fn unit(root: &Path, entry: String, refusals: &mut Vec<String>) -> Option<Unit> {
    if entry.contains("://") {
        refusals.push(format!(
            "unresolved: unit {entry} is a URL, and a unit loads from a directory"
        ));
        return None;
    }
    let manifest = root.join(&entry).join(".claude-plugin").join("plugin.json");
    let Ok(text) = std::fs::read_to_string(&manifest) else {
        refusals.push(format!(
            "unresolved: unit {entry} is not a unit's own directory"
        ));
        return None;
    };
    let fields = serde_json::from_str::<Value>(&text).ok().and_then(|json| {
        let field = |key: &str| json.get(key)?.as_str().map(str::to_string);
        Some((field("name")?, field("version")?))
    });
    let Some((name, version)) = fields else {
        refusals.push(format!(
            "unresolved: unit {entry} has a plugin.json that states no name and version"
        ));
        return None;
    };
    Some(Unit {
        entry,
        name,
        version,
    })
}

/// Each repository settings file whose `env` block would reach the run
/// (REQ-2392), naming the keys it sets.
fn env_refusals(root: &Path) -> Vec<String> {
    let mut refusals = Vec::new();
    for name in [".claude/settings.json", ".claude/settings.local.json"] {
        let Ok(text) = std::fs::read_to_string(root.join(name)) else {
            continue;
        };
        let Ok(json) = serde_json::from_str::<Value>(&text) else {
            continue;
        };
        if let Some(env) = json.get("env").and_then(Value::as_object)
            && !env.is_empty()
        {
            let keys: Vec<&str> = env.keys().map(String::as_str).collect();
            refusals.push(format!("unresolved: {name} sets env {}", keys.join(", ")));
        }
    }
    refusals
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

fn table_text(authority: &Authority) -> String {
    let entries: Vec<String> = authority.units.iter().map(|u| u.entry.clone()).collect();
    let list = |items: &[String]| {
        let quoted: Vec<String> = items.iter().map(|i| format!("{i:?}")).collect();
        format!("[{}]", quoted.join(", "))
    };
    format!(
        "[unattended]\npermission_mode = {:?}\nbudget_usd = {}\ngates = {}\nunits = {}\nmerge_protected = {}\namend_approved = {}\n",
        authority.mode,
        authority.budget,
        list(&authority.gates),
        list(&entries),
        authority.merge_protected,
        authority.amend_approved
    )
}

/// The snapshot's content: the resolved table and the deny rules, as JSON.
/// It holds no credential and no `apiKeyHelper`.
fn snapshot(authority: &Authority, deny: &[String]) -> String {
    let budget = match &authority.budget {
        toml::Value::Integer(n) => json!(n),
        toml::Value::Float(n) => json!(n),
        other => json!(other.to_string()),
    };
    let mut table = Map::new();
    table.insert("permission_mode".into(), json!(authority.mode));
    table.insert("budget_usd".into(), budget);
    table.insert("gates".into(), json!(authority.gates));
    let entries: Vec<&str> = authority.units.iter().map(|u| u.entry.as_str()).collect();
    table.insert("units".into(), json!(entries));
    table.insert("merge_protected".into(), json!(authority.merge_protected));
    table.insert("amend_approved".into(), json!(authority.amend_approved));
    let units: Vec<Value> = authority
        .units
        .iter()
        .map(|u| json!({ "path": u.entry, "name": u.name, "version": u.version }))
        .collect();
    let content = json!({
        "meowpaw": { "unattended": Value::Object(table), "units": units },
        "permissions": { "deny": deny },
    });
    let mut text = serde_json::to_string_pretty(&content).unwrap_or_default();
    text.push('\n');
    text
}

/// Writes the snapshot through a temporary file renamed into place, named for
/// the SHA-256 of its content.
fn keep(folder: &Path, content: &str) -> Result<PathBuf, String> {
    let hash = hex(&Sha256::digest(content.as_bytes()));
    let path = folder.join(format!("{hash}.json"));
    let partial = folder.join(format!(".{hash}.json.partial"));
    std::fs::write(&partial, content)
        .map_err(|e| format!("can't write {}: {e}", partial.display()))?;
    std::fs::rename(&partial, &path)
        .map_err(|e| format!("can't move {} into place: {e}", path.display()))?;
    Ok(path)
}

fn purge(root: &Path) -> u8 {
    let Some(folder) = folder(root) else {
        return unresolved(&[format!(
            "unresolved: snapshots not purged: {}",
            no_state_reason()
        )]);
    };
    let mut removed = 0;
    if let Ok(entries) = std::fs::read_dir(&folder) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().is_some_and(|e| e == "json") {
                if let Err(error) = std::fs::remove_file(&path) {
                    return unresolved(&[format!(
                        "unresolved: snapshots not purged: can't remove {}: {error}",
                        path.display()
                    )]);
                }
                removed += 1;
            }
        }
    }
    let _ = std::fs::remove_dir(&folder);
    println!("purged {removed} snapshots of {}", root.display());
    0
}

/// The folder, created where it is missing, with every symbolic link resolved.
fn made(folder: &Path) -> Result<PathBuf, String> {
    std::fs::create_dir_all(folder)
        .and_then(|()| std::fs::canonicalize(folder))
        .map_err(|e| format!("can't create {}: {e}", folder.display()))
}

/// The folder the work tree's snapshots are kept in, or none where state
/// writing is off or there is no state directory.
fn folder(root: &Path) -> Option<PathBuf> {
    if state_off() { None } else { location(root) }
}

/// Where the work tree's snapshots belong, found as the evidence ledger finds
/// its state directory and keys a work tree (SPC-1040), whether or not state
/// writing is on, so a printed snapshot still denies the folder.
fn location(root: &Path) -> Option<PathBuf> {
    let set = |name: &str| {
        std::env::var_os(name)
            .filter(|v| !v.is_empty())
            .map(PathBuf::from)
    };
    let dir = if let Some(moved) = set("MEOWPAW_STATE_DIR") {
        moved.join("unattended")
    } else {
        let base = set("XDG_STATE_HOME").or_else(|| {
            if cfg!(windows) {
                set("LOCALAPPDATA")
            } else {
                set("HOME").map(|home| home.join(".local").join("state"))
            }
        })?;
        base.join("meowpaw").join("unattended")
    };
    let key = hex(&Sha256::digest(root.to_string_lossy().as_bytes()))[..16].to_string();
    Some(dir.join(key))
}

fn state_off() -> bool {
    std::env::var("MEOWPAW_STATE").is_ok_and(|v| v == "off")
}

fn no_state_reason() -> &'static str {
    if state_off() {
        "state writing is off (MEOWPAW_STATE=off)"
    } else {
        "no state directory: set XDG_STATE_HOME, MEOWPAW_STATE_DIR or HOME"
    }
}

/// Each requirement and decision under the record whose front matter says
/// `status: approved`.
fn approved(record: &Path) -> Vec<PathBuf> {
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
            matches!(field("artifact"), Some("requirement" | "adr"))
                && field("status") == Some("approved")
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

/// The top-level `key: value` pairs of a file's YAML front matter.
fn front_matter(text: &str) -> Vec<(String, String)> {
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

/// A path with forward slashes, so a deny rule reads the same on every system.
fn slashed(path: &Path) -> String {
    path.to_string_lossy().replace('\\', "/")
}

/// An argument quoted for a POSIX shell where it holds anything but safe
/// characters.
fn quoted(text: &str) -> String {
    let safe = !text.is_empty()
        && text
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || "-_./+=:@%,".contains(c));
    if safe {
        text.to_string()
    } else {
        format!("'{}'", text.replace('\'', r"'\''"))
    }
}

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn table(text: &str) -> toml::Table {
        text.parse().unwrap()
    }

    #[test]
    fn every_refusal_is_reported_in_one_run() {
        let refused = resolve(
            &table("permission_mode = \"bypassPermissions\"\nbudget_usd = -1\n"),
            true,
            Path::new("/nonexistent"),
        )
        .err()
        .unwrap();
        assert_eq!(refused.len(), 4, "{refused:?}");
    }

    #[test]
    fn a_string_budget_is_refused() {
        let refused = resolve(
            &table("permission_mode = \"auto\"\nbudget_usd = \"5\"\ngates = []\nunits = []\n"),
            true,
            Path::new("/nonexistent"),
        )
        .err()
        .unwrap();
        assert_eq!(
            refused,
            ["unresolved: [unattended] budget_usd 5 is not a positive number"]
        );
    }

    #[test]
    fn front_matter_reads_top_level_keys() {
        let fields = front_matter("---\nid: X\nstatus: approved\n---\n\n# X\n");
        assert_eq!(fields[1], ("status".to_string(), "approved".to_string()));
    }

    #[test]
    fn a_path_with_a_space_is_quoted() {
        assert_eq!(quoted("a b"), "'a b'");
        assert_eq!(quoted("units/alpha"), "units/alpha");
    }
}
