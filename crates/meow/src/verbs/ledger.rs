// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The ledger of recorded verb results, outside the repository, each bound to
//! the tree it ran on (ADR-1480).
//!
//! A tree id is git's hash of the working state as a tree object, untracked
//! files included and ignored ones left out, built through a temporary index
//! so the repository's own index is untouched. It equals the tree of a commit
//! that adds every file it counted, which is what lets a reviewer compare a
//! result with a commit.

use crate::profile;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

/// A tree id, or `none` where the directory isn't a git work tree.
pub const UNBOUND: &str = "none";

/// Where kept evidence lives in the repository: `evidence_dir` under `[verbs]`,
/// or `.meowpaw/evidence` (ADR-1530).
pub fn evidence_dir(root: &Path) -> String {
    match profile::read(root) {
        profile::Profile::Parsed(table) => table
            .get("verbs")
            .and_then(|v| v.get("evidence_dir"))
            .and_then(|v| v.as_str())
            .map(|d| d.trim_end_matches('/').to_string())
            .unwrap_or_else(|| ".meowpaw/evidence".to_string()),
        _ => ".meowpaw/evidence".to_string(),
    }
}

fn temporary_index() -> PathBuf {
    let nanos = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_nanos()).unwrap_or(0);
    std::env::temp_dir().join(format!("meow-index-{}-{nanos}", std::process::id()))
}

/// The tree id of the working state, leaving the evidence directory out,
/// because the evidence describes the work and isn't part of it (ADR-1530);
/// or `none` outside a git work tree.
pub fn tree_id(root: &Path) -> String {
    let git = |args: &[&str]| profile::reading_git().current_dir(root).args(args).output().ok();
    let inside = git(&["rev-parse", "--is-inside-work-tree"])
        .is_some_and(|o| o.status.success() && String::from_utf8_lossy(&o.stdout).trim() == "true");
    if !inside {
        return UNBOUND.to_string();
    }
    let Some(index) = git(&["rev-parse", "--path-format=absolute", "--git-path", "index"])
        .filter(|o| o.status.success())
        .map(|o| PathBuf::from(String::from_utf8_lossy(&o.stdout).trim()))
    else {
        return UNBOUND.to_string();
    };
    let temporary = temporary_index();
    if index.is_file() && std::fs::copy(&index, &temporary).is_err() {
        return UNBOUND.to_string();
    }
    let with_index = |args: &[&str]| {
        profile::reading_git().current_dir(root).env("GIT_INDEX_FILE", &temporary).args(args).output().ok()
    };
    let excluded = format!(":(exclude){}", evidence_dir(root));
    let added = with_index(&["add", "--all", "--", ".", &excluded]).is_some_and(|o| o.status.success())
        && with_index(&["rm", "-r", "--cached", "-q", "--ignore-unmatch", "--", &evidence_dir(root)])
            .is_some_and(|o| o.status.success());
    let written = with_index(&["write-tree"]).filter(|o| added && o.status.success());
    let _ = std::fs::remove_file(&temporary);
    match written {
        Some(done) => String::from_utf8_lossy(&done.stdout).trim().to_string(),
        None => UNBOUND.to_string(),
    }
}

/// A commit's tree id with the evidence directory left out, the id a kept
/// record names for the work that commit holds (ADR-1530).
pub fn tree_of_commit(root: &Path, commit: &str) -> std::result::Result<String, String> {
    let temporary = temporary_index();
    let git = |args: &[&str]| profile::reading_git().current_dir(root).env("GIT_INDEX_FILE", &temporary).args(args).output();
    let read = git(&["read-tree", commit]).map_err(|e| e.to_string())?;
    if !read.status.success() {
        let _ = std::fs::remove_file(&temporary);
        return Err(format!("{commit} is not a commit here: {}", String::from_utf8_lossy(&read.stderr).trim()));
    }
    let dir = evidence_dir(root);
    let removed = git(&["rm", "-r", "--cached", "-q", "--ignore-unmatch", "--", &dir]).map(|o| o.status.success()).unwrap_or(false);
    let written = git(&["write-tree"]).ok().filter(|o| removed && o.status.success());
    let _ = std::fs::remove_file(&temporary);
    written.map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string()).ok_or_else(|| "git couldn't write the tree".to_string())
}

/// A record's whole output, from beside the ledger.
pub fn output_of(root: &Path, record: &str) -> Option<String> {
    let (_, outputs) = ledger_of(root)?;
    std::fs::read_to_string(outputs.join(format!("{record}.log"))).ok()
}

/// Copies one current record, with its whole output, into the repository's
/// evidence directory, written through a temporary file renamed into place
/// (REQ-2956, REQ-2964, REQ-2966).
pub fn keep(root: &Path, record: &Value) -> std::result::Result<PathBuf, String> {
    let text = |key: &str| record.get(key).and_then(Value::as_str).unwrap_or("").to_string();
    let id = text("record");
    let output = output_of(root, &id).ok_or_else(|| format!("the output of record {id} is gone from the ledger"))?;
    let targets: Vec<&str> = record.get("targets").and_then(Value::as_array).into_iter().flatten().filter_map(Value::as_str).collect();
    let status = record.get("status").and_then(Value::as_i64).map(|s| s.to_string()).unwrap_or_else(|| "none".into());
    let header = format!(
        "meow-verbs evidence 1\nrecord: {id}\nverb: {}\ncommand: {}\ntargets: {}\noutcome: {}\nexit status: {status}\ntree: {}\ntime: {}\n\n",
        text("verb"), text("command"), if targets.is_empty() { "none".to_string() } else { targets.join(" ") },
        text("outcome"), text("tree"), text("time"),
    );
    let dir = root.join(evidence_dir(root));
    std::fs::create_dir_all(&dir).map_err(|e| format!("can't create {}: {e}", dir.display()))?;
    let path = dir.join(format!("{id}.log"));
    let partial = dir.join(format!(".{id}.log.partial"));
    std::fs::write(&partial, format!("{header}{output}")).map_err(|e| format!("can't write {}: {e}", partial.display()))?;
    std::fs::rename(&partial, &path).map_err(|e| format!("can't move {} into place: {e}", path.display()))?;
    Ok(path)
}

/// The directory holding every work tree's ledger: `$XDG_STATE_HOME` where it
/// is set, and otherwise `%LOCALAPPDATA%` on Windows and `~/.local/state`
/// elsewhere.
fn state_dir() -> Option<PathBuf> {
    let set = |name: &str| std::env::var_os(name).filter(|v| !v.is_empty()).map(PathBuf::from);
    let base = set("XDG_STATE_HOME").or_else(|| {
        if cfg!(windows) {
            set("LOCALAPPDATA")
        } else {
            set("HOME").map(|home| home.join(".local").join("state"))
        }
    })?;
    Some(base.join("meowpaw").join("evidence"))
}

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

/// The ledger file for a work tree, keyed by a hash of its absolute path, so
/// two work trees of one repository keep separate ledgers.
fn ledger_of(root: &Path) -> Option<(PathBuf, PathBuf)> {
    let absolute = std::fs::canonicalize(root).unwrap_or_else(|_| root.to_path_buf());
    let key = hex(&Sha256::digest(absolute.to_string_lossy().as_bytes()))[..16].to_string();
    let dir = state_dir()?;
    Some((dir.join(format!("{key}.jsonl")), dir.join(key)))
}

/// Now, as an ISO 8601 time in UTC.
fn now() -> String {
    let secs = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0);
    // Howard Hinnant's civil-from-days, so the time needs no calendar crate.
    let z = (secs / 86_400) as i64 + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1_460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let day = doy - (153 * mp + 2) / 5 + 1;
    let month = if mp < 10 { mp + 3 } else { mp - 9 };
    let year = yoe + era * 400 + i64::from(month <= 2);
    let rest = secs % 86_400;
    format!("{year:04}-{month:02}-{day:02}T{:02}:{:02}:{:02}Z", rest / 3_600, rest % 3_600 / 60, rest % 60)
}

/// One verb's result, as `run` hands it over.
pub struct Result<'a> {
    pub verb: &'a str,
    pub command: Option<&'a str>,
    pub outcome: &'a str,
    pub status: Option<i32>,
    pub before: &'a str,
    pub after: &'a str,
    pub output: &'a str,
    /// The part of the work a subset run covered, or `None` for the whole.
    pub targets: Option<&'a [String]>,
}

/// Appends one record, and its whole output beside the ledger, returning the
/// record's identifier or why it couldn't be written.
pub fn record(root: &Path, result: &Result) -> std::result::Result<String, String> {
    let (ledger, outputs) = ledger_of(root).ok_or("no state directory: set XDG_STATE_HOME or HOME")?;
    let time = now();
    let nanos = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_nanos()).unwrap_or(0);
    let seed = format!("{}\n{}\n{}\n{time}\n{nanos}\n{}", result.verb, result.outcome, result.after, std::process::id());
    let id = hex(&Sha256::digest(seed.as_bytes()))[..12].to_string();
    let line = json!({
        "record": id,
        "verb": result.verb,
        "command": result.command,
        "outcome": result.outcome,
        "status": result.status,
        "time": time,
        "tree_before": result.before,
        "tree": result.after,
        "targets": result.targets,
    });
    std::fs::create_dir_all(&outputs).map_err(|e| format!("can't create {}: {e}", outputs.display()))?;
    std::fs::write(outputs.join(format!("{id}.log")), result.output)
        .map_err(|e| format!("can't write the output: {e}"))?;
    let mut file = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&ledger)
        .map_err(|e| format!("can't open {}: {e}", ledger.display()))?;
    // One write per line, so two sessions appending at once keep lines whole.
    file.write_all(format!("{line}\n").as_bytes()).map_err(|e| format!("can't append: {e}"))?;
    Ok(id)
}

/// Every record in a work tree's ledger, oldest first; a line that doesn't
/// parse is skipped.
pub fn records(root: &Path) -> Vec<Value> {
    let Some((ledger, _)) = ledger_of(root) else { return Vec::new() };
    let Ok(text) = std::fs::read_to_string(ledger) else { return Vec::new() };
    text.lines().filter_map(|line| serde_json::from_str(line).ok()).collect()
}

/// The first twelve characters of a tree id, which is how it is shown.
pub fn short(tree: &str) -> &str {
    &tree[..tree.len().min(12)]
}
