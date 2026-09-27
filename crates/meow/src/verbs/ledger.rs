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
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

/// A tree id, or `none` where the directory isn't a git work tree.
pub const UNBOUND: &str = "none";

/// The record's default root, a copy of `meow-flow`'s, since neither unit may
/// depend on the other; change both together (ADR-1550).
const RECORD_ROOT: &str = "project";

/// Where kept evidence lives in the repository: `evidence_dir` under `[verbs]`,
/// or `evidence` under the record's root (ADR-1550).
pub fn evidence_dir(root: &Path) -> String {
    let table = match profile::read(root) {
        profile::Profile::Parsed(table) => table,
        _ => toml::Table::new(),
    };
    let text = |section: &str, key: &str| table.get(section).and_then(|v| v.get(key)).and_then(|v| v.as_str()).map(|d| d.trim_end_matches('/').to_string());
    text("verbs", "evidence_dir").unwrap_or_else(|| format!("{}/evidence", text("record", "root").unwrap_or_else(|| RECORD_ROOT.to_string())))
}

/// Whether git ignores a kept file: `Ok(None)` when it doesn't, `Ok(Some(rule))`
/// when it does, and `Err` when git can't answer (ADR-1550).
pub fn ignored_by(root: &Path, path: &Path) -> std::result::Result<Option<String>, String> {
    // git takes `-z` here only with the path on standard input, NUL-terminated,
    // so a path it would escape is read as it is (REQ-2522).
    let mut child = profile::reading_git()
        .current_dir(root)
        .args(["check-ignore", "-v", "-z", "--stdin"])
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .map_err(|e| e.to_string())?;
    if let Some(mut input) = child.stdin.take() {
        let mut bytes = path.as_os_str().to_string_lossy().into_owned().into_bytes();
        bytes.push(0);
        input.write_all(&bytes).map_err(|e| e.to_string())?;
    }
    let done = child.wait_with_output().map_err(|e| e.to_string())?;
    match done.status.code() {
        Some(0) => {
            // The fields are the source, the line number, the pattern and the path.
            let text = String::from_utf8_lossy(&done.stdout);
            let fields: Vec<&str> = text.split('\0').collect();
            let rule = match (fields.first(), fields.get(1)) {
                (Some(source), Some(line)) => format!("{source}:{line}"),
                _ => String::new(),
            };
            Ok(Some(rule))
        }
        Some(1) => Ok(None),
        _ => Err(String::from_utf8_lossy(&done.stderr).trim().to_string()),
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
    // An edit inside a submodule changes nothing in the parent's tree, so a
    // dirty submodule binds no result at all (ADR-1560).
    if dirty_submodule(root).is_some() {
        return UNBOUND.to_string();
    }
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

/// The first submodule with uncommitted changes, untracked files included and
/// ignored ones left out, as the parent counts them (ADR-1560).
pub fn dirty_submodule(root: &Path) -> Option<String> {
    if !root.join(".gitmodules").is_file() {
        return None;
    }
    let done = profile::reading_git()
        .current_dir(root)
        .args(["submodule", "foreach", "--quiet", "--recursive", "test -z \"$(git status --porcelain)\" || echo \"$displaypath\""])
        .output()
        .ok()?;
    String::from_utf8_lossy(&done.stdout).lines().next().map(str::to_string)
}

/// A kept file's header fields, as `keep` wrote them.
pub fn header_of(path: &Path) -> Option<Value> {
    let text = std::fs::read_to_string(path).ok()?;
    let mut lines = text.lines();
    if lines.next()? != "meow-verbs evidence 1" {
        return None;
    }
    let mut fields = serde_json::Map::new();
    for line in lines.take_while(|l| !l.is_empty()) {
        if let Some((key, value)) = line.split_once(": ") {
            fields.insert(key.to_string(), Value::from(value));
        }
    }
    Some(Value::Object(fields))
}

/// The kept files this work adds against the branch's base on the trunk, or
/// every kept file with the reason it couldn't tell (REQ-0456).
pub fn kept_by_this_work(root: &Path) -> (Vec<PathBuf>, Option<String>) {
    let dir = evidence_dir(root);
    let all = || {
        let mut found: Vec<PathBuf> = std::fs::read_dir(root.join(&dir)).map(|e| e.flatten().map(|e| e.path()).filter(|p| p.extension().is_some_and(|x| x == "txt")).collect()).unwrap_or_default();
        found.sort();
        found
    };
    let trunk = match profile::read(root) {
        profile::Profile::Parsed(table) => table.get("git").and_then(|g| g.get("trunk")).and_then(|t| t.as_str()).map(str::to_string),
        _ => None,
    };
    let Some(trunk) = trunk else { return (all(), Some("no trunk is declared under [git]".into())) };
    let git = |args: &[&str]| profile::reading_git().current_dir(root).args(args).output().ok().filter(|o| o.status.success()).map(|o| String::from_utf8_lossy(&o.stdout).to_string());
    let Some(base) = git(&["merge-base", "HEAD", &trunk]).map(|b| b.trim().to_string()) else {
        return (all(), Some(format!("the branch has no base on {trunk}")));
    };
    // NUL-separated, so a path git would escape reads as it is (REQ-2522).
    let split = |text: String| text.split('\0').filter(|n| !n.is_empty()).map(str::to_string).collect::<Vec<_>>();
    let mut names: Vec<String> = split(git(&["diff", "-z", "--name-only", "--diff-filter=A", &base, "--", &dir]).unwrap_or_default());
    names.extend(split(git(&["ls-files", "-z", "--others", "--exclude-standard", "--", &dir]).unwrap_or_default()));
    names.sort();
    names.dedup();
    (names.into_iter().filter(|n| n.ends_with(".txt")).map(|n| root.join(n)).collect(), None)
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
    let path = dir.join(format!("{id}.txt"));
    let partial = dir.join(format!(".{id}.txt.partial"));
    std::fs::write(&partial, format!("{header}{output}")).map_err(|e| format!("can't write {}: {e}", partial.display()))?;
    std::fs::rename(&partial, &path).map_err(|e| format!("can't move {} into place: {e}", path.display()))?;
    Ok(path)
}

/// The directory holding every work tree's ledger: `$XDG_STATE_HOME` where it
/// is set, and otherwise `%LOCALAPPDATA%` on Windows and `~/.local/state`
/// elsewhere.
fn state_dir() -> Option<PathBuf> {
    let set = |name: &str| std::env::var_os(name).filter(|v| !v.is_empty()).map(PathBuf::from);
    if state_off() {
        return None;
    }
    // `MEOWPAW_STATE_DIR` moves the whole state directory (REQ-2960).
    if let Some(moved) = set("MEOWPAW_STATE_DIR") {
        return Some(moved.join("evidence"));
    }
    let base = set("XDG_STATE_HOME").or_else(|| {
        if cfg!(windows) {
            set("LOCALAPPDATA")
        } else {
            set("HOME").map(|home| home.join(".local").join("state"))
        }
    })?;
    Some(base.join("meowpaw").join("evidence"))
}

/// Whether `MEOWPAW_STATE=off` forbids every write outside the repository (REQ-2960).
pub fn state_off() -> bool {
    std::env::var("MEOWPAW_STATE").is_ok_and(|v| v == "off")
}

/// Why nothing can be recorded, where nothing can.
pub fn no_state_reason() -> &'static str {
    if state_off() {
        "state writing is off (MEOWPAW_STATE=off)"
    } else {
        "no state directory: set XDG_STATE_HOME, MEOWPAW_STATE_DIR or HOME"
    }
}

/// The repository's identity, the hash of its first commit, which every clone
/// and work tree of it shares (REQ-0752).
pub fn repository_identity(root: &Path) -> Option<String> {
    let done = profile::reading_git().current_dir(root).args(["rev-list", "--max-parents=0", "HEAD"]).output().ok()?;
    let text = String::from_utf8_lossy(&done.stdout);
    text.lines().next().filter(|_| done.status.success()).map(str::to_string)
}

/// The runtime directory a lock lives in: user-owned, and cleaned by the system
/// (REQ-2958).
fn runtime_dir() -> PathBuf {
    std::env::var_os("XDG_RUNTIME_DIR").filter(|v| !v.is_empty()).map(PathBuf::from).unwrap_or_else(std::env::temp_dir)
}

/// How old a lock may be before it is taken as a dead process's: a rewrite of
/// one file takes well under this (ADR-1530).
const STALE_LOCK: std::time::Duration = std::time::Duration::from_secs(60);

/// A held lock on one work tree's ledger, released when dropped (REQ-2967).
pub struct Lock(PathBuf);

impl Drop for Lock {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.0);
    }
}

fn lock_path(root: &Path) -> Option<PathBuf> {
    let (ledger, _) = ledger_of(root)?;
    let key = ledger.file_stem()?.to_string_lossy().to_string();
    Some(runtime_dir().join(format!("meowpaw-{key}.lock")))
}

/// Takes the ledger's lock, replacing one older than a minute; waits for it
/// when `wait` is set, and otherwise gives up at once.
pub fn lock(root: &Path, wait: bool) -> Option<Lock> {
    let path = lock_path(root)?;
    let started = SystemTime::now();
    loop {
        match std::fs::OpenOptions::new().write(true).create_new(true).open(&path) {
            Ok(mut file) => {
                let _ = write!(file, "{}", std::process::id());
                return Some(Lock(path));
            }
            Err(_) => {
                let age = std::fs::metadata(&path).and_then(|m| m.modified()).ok().and_then(|t| t.elapsed().ok());
                if age.is_some_and(|a| a > STALE_LOCK) {
                    let _ = std::fs::remove_file(&path);
                    continue;
                }
                let waited = started.elapsed().unwrap_or_default();
                if !wait || waited > STALE_LOCK + std::time::Duration::from_secs(5) {
                    return None;
                }
                std::thread::sleep(std::time::Duration::from_millis(50));
            }
        }
    }
}

/// How long a record is kept: one older names a tree the work has long left
/// (REQ-2962).
const RETENTION_DAYS: u64 = 30;

/// Rewrites a ledger through a temporary file renamed into place (REQ-2966).
fn rewrite(ledger: &Path, lines: &[String]) -> std::io::Result<()> {
    let partial = ledger.with_extension("jsonl.partial");
    let mut text = lines.join("\n");
    if !text.is_empty() {
        text.push('\n');
    }
    std::fs::write(&partial, text)?;
    std::fs::rename(&partial, ledger)
}

/// Drops every record older than 30 days and its output file, where the lock
/// can be taken at once; a held lock skips the prune for the next run.
pub fn prune(root: &Path) -> usize {
    let Some((ledger, outputs)) = ledger_of(root) else { return 0 };
    let Ok(text) = std::fs::read_to_string(&ledger) else { return 0 };
    let cutoff = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0).saturating_sub(RETENTION_DAYS * 86_400);
    let old = |line: &str| {
        serde_json::from_str::<Value>(line).ok().and_then(|v| v.get("time").and_then(Value::as_str).and_then(seconds_of)).is_some_and(|t| t < cutoff)
    };
    if !text.lines().any(old) {
        return 0;
    }
    let Some(_held) = lock(root, false) else { return 0 };
    let Ok(text) = std::fs::read_to_string(&ledger) else { return 0 };
    let (dropped, kept): (Vec<&str>, Vec<&str>) = text.lines().partition(|l| old(l));
    for line in &dropped {
        if let Some(id) = serde_json::from_str::<Value>(line).ok().and_then(|v| v.get("record").and_then(Value::as_str).map(str::to_string)) {
            let _ = std::fs::remove_file(outputs.join(format!("{id}.log")));
        }
    }
    let kept: Vec<String> = kept.iter().map(|l| l.to_string()).collect();
    if rewrite(&ledger, &kept).is_ok() { dropped.len() } else { 0 }
}

/// Drops every record in a work tree's ledger, and their output files.
pub fn purge(root: &Path) -> std::result::Result<usize, String> {
    let (ledger, outputs) = ledger_of(root).ok_or(no_state_reason())?;
    let _held = lock(root, true).ok_or("the ledger's lock is held and fresh; try again in a minute")?;
    let count = std::fs::read_to_string(&ledger).map(|t| t.lines().count()).unwrap_or(0);
    let _ = std::fs::remove_dir_all(&outputs);
    rewrite(&ledger, &[]).map_err(|e| e.to_string())?;
    Ok(count)
}

/// Seconds since the epoch of an ISO 8601 time this module wrote.
fn seconds_of(time: &str) -> Option<u64> {
    let (date, clock) = time.trim_end_matches('Z').split_once('T')?;
    let mut d = date.split('-').map(|p| p.parse::<i64>().ok());
    let (y, m, day) = (d.next()??, d.next()??, d.next()??);
    let mut c = clock.split(':').map(|p| p.parse::<u64>().ok());
    let (h, mi, se) = (c.next()??, c.next()??, c.next()??);
    // Howard Hinnant's days-from-civil, the inverse of `now`.
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let yoe = y - era * 400;
    let mp = (m + 9) % 12;
    let doy = (153 * mp + 2) / 5 + day - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    let days = era * 146_097 + doe - 719_468;
    Some(days as u64 * 86_400 + h * 3_600 + mi * 60 + se)
}

/// The facts about a work tree's ledger a person reads (REQ-0756).
pub fn facts(root: &Path) -> Vec<String> {
    let Some((ledger, _)) = ledger_of(root) else { return vec![no_state_reason().to_string()] };
    let records = records(root);
    let times: Vec<String> = records.iter().filter_map(|r| r.get("time").and_then(Value::as_str).map(str::to_string)).collect();
    vec![
        format!("ledger: {}", ledger.display()),
        format!("records: {}", records.len()),
        format!("oldest: {}", times.iter().min().cloned().unwrap_or_else(|| "none".into())),
        format!("newest: {}", times.iter().max().cloned().unwrap_or_else(|| "none".into())),
        format!("evidence directory: {}", evidence_dir(root)),
        format!("lock: {}", lock_path(root).map(|p| p.display().to_string()).unwrap_or_default()),
    ]
}

/// Every other work tree's records that name this repository, by the path
/// each names (REQ-2970).
pub fn other_work_trees(root: &Path) -> Vec<(String, Vec<Value>)> {
    let (Some(identity), Some((mine, _)), Some(dir)) = (repository_identity(root), ledger_of(root), state_dir()) else { return Vec::new() };
    let mut out = Vec::new();
    let Ok(entries) = std::fs::read_dir(&dir) else { return out };
    let mut paths: Vec<PathBuf> = entries.flatten().map(|e| e.path()).filter(|p| p.extension().is_some_and(|e| e == "jsonl") && *p != mine).collect();
    paths.sort();
    for path in paths {
        let Ok(text) = std::fs::read_to_string(&path) else { continue };
        let found: Vec<Value> = text.lines().filter_map(|l| serde_json::from_str::<Value>(l).ok()).filter(|v| v.get("repository").and_then(Value::as_str) == Some(identity.as_str())).collect();
        if let Some(tree) = found.iter().rev().find_map(|v| v.get("work_tree").and_then(Value::as_str).map(str::to_string)) {
            out.push((tree, found));
        }
    }
    out
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
pub fn record(root: &Path, result: &Result, started: Option<&str>) -> std::result::Result<String, String> {
    let (ledger, outputs) = ledger_of(root).ok_or(no_state_reason())?;
    let time = now();
    let id = started.map(str::to_string).unwrap_or_else(|| new_id(result.verb));
    let line = json!({
        "record": id,
        "phase": "ended",
        "verb": result.verb,
        "command": result.command,
        "outcome": result.outcome,
        "status": result.status,
        "time": time,
        "tree_before": result.before,
        "tree": result.after,
        "targets": result.targets,
        "repository": repository_identity(root),
        "work_tree": std::fs::canonicalize(root).unwrap_or_else(|_| root.to_path_buf()).display().to_string(),
    });
    std::fs::create_dir_all(&outputs).map_err(|e| format!("can't create {}: {e}", outputs.display()))?;
    std::fs::write(outputs.join(format!("{id}.log")), result.output)
        .map_err(|e| format!("can't write the output: {e}"))?;
    append(root, &ledger, &line)?;
    Ok(id)
}

fn new_id(verb: &str) -> String {
    let nanos = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_nanos()).unwrap_or(0);
    let seed = format!("{verb}\n{nanos}\n{}", std::process::id());
    hex(&Sha256::digest(seed.as_bytes()))[..12].to_string()
}

/// Appends one whole line under the lock, so no line is lost to a prune
/// (REQ-0758), with one write per line so a reader sees it whole or not at all.
fn append(root: &Path, ledger: &Path, line: &Value) -> std::result::Result<(), String> {
    if let Some(dir) = ledger.parent() {
        std::fs::create_dir_all(dir).map_err(|e| format!("can't create {}: {e}", dir.display()))?;
    }
    let _held = lock(root, true).ok_or("the ledger's lock stayed held; the result wasn't recorded")?;
    let mut file = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(ledger)
        .map_err(|e| format!("can't open {}: {e}", ledger.display()))?;
    file.write_all(format!("{line}\n").as_bytes()).map_err(|e| format!("can't append: {e}"))
}

/// When a process started, as the system reports it, so a reused process id
/// isn't read as the same run (REQ-2968).
fn process_start(pid: u32) -> Option<String> {
    let done = Command::new("ps").args(["-o", "lstart=", "-p", &pid.to_string()]).output().ok()?;
    let text = String::from_utf8_lossy(&done.stdout).trim().to_string();
    (done.status.success() && !text.is_empty()).then_some(text)
}

fn host() -> String {
    Command::new("hostname").output().ok().map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string()).unwrap_or_default()
}

/// Records a verb as started before it runs, naming this process, so a run
/// cut short reads as interrupted and never as a result (REQ-2968).
pub fn start(root: &Path, verb: &str, command: &str, targets: Option<&[String]>, before: &str) -> Option<String> {
    let (ledger, _) = ledger_of(root)?;
    let id = new_id(verb);
    let pid = std::process::id();
    let line = json!({
        "record": id,
        "phase": "started",
        "verb": verb,
        "command": command,
        "targets": targets,
        "tree_before": before,
        "time": now(),
        "pid": pid,
        "process_start": process_start(pid),
        "host": host(),
        "repository": repository_identity(root),
        "work_tree": std::fs::canonicalize(root).unwrap_or_else(|_| root.to_path_buf()).display().to_string(),
    });
    append(root, &ledger, &line).ok().map(|_| id)
}

/// Whether the process a started record names still runs this verb.
fn still_running(started: &Value) -> bool {
    let pid = started.get("pid").and_then(Value::as_u64).unwrap_or(0) as u32;
    let same_host = started.get("host").and_then(Value::as_str) == Some(host().as_str());
    let recorded = started.get("process_start").and_then(Value::as_str);
    same_host && pid != 0 && recorded.is_some() && process_start(pid).as_deref() == recorded
}

/// Every record in a work tree's ledger, oldest first; a line that doesn't
/// parse is skipped.
pub fn records(root: &Path) -> Vec<Value> {
    let Some((ledger, _)) = ledger_of(root) else { return Vec::new() };
    let Ok(text) = std::fs::read_to_string(ledger) else { return Vec::new() };
    let lines: Vec<Value> = text.lines().filter_map(|line| serde_json::from_str(line).ok()).collect();
    pair(lines)
}

/// One record per identifier, in the order each reached its last state: an
/// ended line stands for its record, and a start with no end reads as
/// `running` while its process lives and `interrupted` otherwise (REQ-2968).
fn pair(lines: Vec<Value>) -> Vec<Value> {
    let mut out: Vec<Value> = Vec::new();
    for line in lines {
        let id = line.get("record").and_then(Value::as_str).unwrap_or("").to_string();
        if let Some(i) = out.iter().position(|r| r.get("record").and_then(Value::as_str) == Some(id.as_str())) {
            out.remove(i);
        }
        out.push(line);
    }
    for record in &mut out {
        if record.get("phase").and_then(Value::as_str) == Some("started") {
            let outcome = if still_running(record) { "running" } else { "interrupted" };
            record["outcome"] = Value::from(outcome);
            let before = record.get("tree_before").cloned().unwrap_or(Value::Null);
            record["tree"] = before;
        }
    }
    out
}

/// The first twelve characters of a tree id, which is how it is shown.
pub fn short(tree: &str) -> &str {
    &tree[..tree.len().min(12)]
}
