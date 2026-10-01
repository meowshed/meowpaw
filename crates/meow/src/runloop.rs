// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Repeat one prompt in fresh `claude -p` calls until the named verbs pass or
//! the ceiling ends the run.
//!
//! SPC-1201 states the behaviour. `start` refuses to begin without a
//! condition, a ceiling and a budget (REQ-0872), keeps a run's files under the
//! state directory and never in the work tree, and holds the ceiling in this
//! process, so nothing a call prints or writes extends it. The runner decides
//! the condition from each verb's exit status and reads nothing the model
//! printed. Every call gets the prompt's bytes as they were at start and one
//! fixed preamble, in a new session (REQ-0880), and what an iteration leaves
//! for the next goes in the run's progress file (REQ-0882). Before each call
//! the runner checks that the spend so far and one more call as large as the
//! largest so far fit the budget (REQ-0878), and a call whose cost it can't
//! read ends the run, because a spend that can't be summed bounds nothing.

use crate::profile;
use crate::verbs::{self, ledger};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::fs::{File, OpenOptions, TryLockError};
use std::io::{Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::{SystemTime, UNIX_EPOCH};

const FINISHED: u8 = 0;
const ENDED: u8 = 1;
const USAGE: u8 = 2;
const UNRESOLVED: u8 = 3;

/// The one permission mode RES-0300 saw run a call.
const MODE: &str = "dontAsk";
/// What a sum of costs may pass the budget by and still count as within it:
/// a billionth of a dollar, which covers the error of adding decimal costs in
/// binary floating point and is far below any cost a call reports.
const SLACK: f64 = 1e-9;
/// How many of a work tree's runs are kept, the new one among them (ADR-2010).
const KEPT: usize = 20;
const VALUED: [&str; 7] = [
    "--prompt",
    "--until",
    "--iterations",
    "--budget-usd",
    "--permission-mode",
    "--allowed-tools",
    "--plugin-dir",
];

/// What the person typed, read once and held for the whole run.
struct Terms {
    prompt: Vec<u8>,
    verbs: Vec<String>,
    iterations: i64,
    budget_usd: f64,
    allowed: Vec<String>,
    plugin_dirs: Vec<String>,
}

/// The terms the command line states, or every usage error in it, so one
/// attempt names every flag to fix.
fn terms(args: &[String]) -> Result<Terms, Vec<String>> {
    let mut errors = Vec::new();
    let mut single: Vec<(&str, &str)> = Vec::new();
    let (mut allowed, mut plugin_dirs) = (Vec::new(), Vec::new());
    let mut rest = args.iter();
    while let Some(flag) = rest.next() {
        if !VALUED.contains(&flag.as_str()) {
            errors.push(format!("{flag} is not a term of start"));
            continue;
        }
        let Some(value) = rest.next() else {
            errors.push(format!("{flag} needs a value"));
            continue;
        };
        match flag.as_str() {
            "--allowed-tools" => allowed.push(value.clone()),
            "--plugin-dir" => plugin_dirs.push(value.clone()),
            _ => single.push((flag, value)),
        }
    }
    let mut stated = |flag: &str| {
        let found = single.iter().rev().find(|(name, _)| *name == flag);
        if found.is_none() {
            errors.push(format!("{flag} is required"));
        }
        found.map(|(_, value)| *value)
    };
    let (prompt, until, iterations, budget, mode) = (
        stated("--prompt"),
        stated("--until"),
        stated("--iterations"),
        stated("--budget-usd"),
        stated("--permission-mode"),
    );

    let prompt = prompt.and_then(|file| {
        std::fs::read(file)
            .map_err(|_| errors.push(format!("--prompt {file} can't be read")))
            .ok()
    });
    let mut named: Vec<String> = Vec::new();
    match until.map(|value| (value, value.strip_prefix("verbs="))) {
        None => {}
        Some((value, None)) => errors.push(format!("--until {value} is not a condition kind")),
        Some((_, Some(list))) => {
            for name in list.split(',').filter(|name| !name.is_empty()) {
                if !verbs::VERBS.contains(&name) {
                    errors.push(format!("{name} is not a verb"));
                } else if !named.iter().any(|seen| seen == name) {
                    named.push(name.to_string());
                }
            }
            if list.split(',').all(str::is_empty) {
                errors.push("--until names no verb".to_string());
            }
        }
    }
    let ceiling = iterations.and_then(|value| {
        // `run.toml` holds the ceiling as a TOML integer, which is signed.
        let digits = !value.is_empty() && value.bytes().all(|b| b.is_ascii_digit());
        match value.parse::<i64>() {
            Ok(ceiling) if digits && ceiling >= 1 => Some(ceiling),
            Err(_) if digits => {
                errors.push(format!("--iterations {value} is above {}", i64::MAX));
                None
            }
            _ => {
                errors.push(format!("--iterations {value} is not at least 1"));
                None
            }
        }
    });
    let budget_usd = budget.and_then(|value| {
        // Only the one form every reader of a budget agrees on is accepted:
        // digits, with one optional point.
        let (whole, fraction) = value.split_once('.').unwrap_or((value, "0"));
        let decimal = [whole, fraction]
            .iter()
            .all(|part| !part.is_empty() && part.bytes().all(|b| b.is_ascii_digit()));
        let zero = value.bytes().all(|b| b == b'0' || b == b'.');
        let amount = value
            .parse::<f64>()
            .ok()
            .filter(|n| n.is_finite() && *n > 0.0);
        let refused = match amount {
            _ if !decimal => "is not a decimal number",
            _ if zero => "is not above 0",
            // The digits state a number above 0 that the parse lost.
            None => "is too large or too small to hold",
            Some(amount) => return Some(amount),
        };
        errors.push(format!("--budget-usd {value} {refused}"));
        None
    });
    if let Some(value) = mode.filter(|value| *value != MODE) {
        errors.push(format!("--permission-mode {value} is refused"));
    }

    match (prompt, ceiling, budget_usd) {
        (Some(prompt), Some(iterations), Some(budget_usd)) if errors.is_empty() => Ok(Terms {
            prompt,
            verbs: named,
            iterations,
            budget_usd,
            allowed,
            plugin_dirs,
        }),
        _ => Err(errors),
    }
}

fn in_work_tree() -> bool {
    profile::reading_git()
        .args(["rev-parse", "--is-inside-work-tree"])
        .output()
        .is_ok_and(|o| o.status.success() && String::from_utf8_lossy(&o.stdout).trim() == "true")
}

#[cfg(unix)]
fn runnable(candidate: &Path) -> bool {
    use std::os::unix::fs::PermissionsExt;
    std::fs::metadata(candidate).is_ok_and(|m| m.is_file() && m.permissions().mode() & 0o111 != 0)
}

#[cfg(not(unix))]
fn runnable(candidate: &Path) -> bool {
    candidate.is_file()
}

/// The first `claude` on the path that can be run, which every call of the
/// run then starts, as an absolute path because a call starts in the work
/// tree's root and not where the path was read.
fn claude() -> Option<PathBuf> {
    let names: &[&str] = if cfg!(windows) {
        &["claude.exe", "claude.cmd"]
    } else {
        &["claude"]
    };
    let path = std::env::var_os("PATH")?;
    std::env::split_paths(&path)
        .flat_map(|dir| names.iter().map(move |name| dir.join(name)))
        .find(|candidate| runnable(candidate))
        .and_then(|candidate| std::path::absolute(candidate).ok())
}

/// Takes the work tree's lock, or says why it can't. The operating system
/// holds the lock on the open file, so it ends with this process however the
/// process ends, and a killed run leaves none behind.
fn lock(runs: &Path) -> Result<File, String> {
    let path = runs.join("lock");
    let (new_dir, new_file) = (!runs.exists(), !path.exists());
    // A refused start leaves nothing behind, so what this attempt created goes
    // again. `remove_dir` takes only an empty directory, so nothing else does.
    let cant = |error: std::io::Error| {
        if new_file {
            let _ = std::fs::remove_file(&path);
        }
        if new_dir {
            let _ = std::fs::remove_dir(runs);
            let _ = runs.parent().map(std::fs::remove_dir);
        }
        format!("can't take the lock {}: {error}", path.display())
    };
    std::fs::create_dir_all(runs).map_err(cant)?;
    let file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)
        .map_err(cant)?;
    match file.try_lock() {
        Ok(()) => Ok(file),
        Err(TryLockError::WouldBlock) => Err("a run already holds this work tree".to_string()),
        Err(TryLockError::Error(error)) => Err(cant(error)),
    }
}

/// Removes the oldest runs so that `KEPT` remain, counting the new one, which
/// is never among those removed, and prints each one removed. A run's id sorts
/// by when it started.
fn remove_old_runs(runs: &Path, new: &Path) {
    let mut ids: Vec<String> = std::fs::read_dir(runs)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|entry| entry.path().is_dir() && entry.path() != new)
        .map(|entry| entry.file_name().to_string_lossy().into_owned())
        .collect();
    ids.sort();
    let surplus = (ids.len() + 1).saturating_sub(KEPT);
    for id in &ids[..surplus] {
        match std::fs::remove_dir_all(runs.join(id)) {
            Ok(()) => println!("removed {id}"),
            Err(error) => println!("can't remove {id}: {error}"),
        }
    }
}

/// Creates the run's directory, named by the time in nanoseconds so that the
/// ids of a work tree's runs sort oldest first.
fn new_run_dir(runs: &Path) -> std::io::Result<PathBuf> {
    let mut nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    loop {
        let dir = runs.join(format!("{nanos:020}"));
        match std::fs::create_dir(&dir) {
            Ok(()) => return Ok(dir),
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => nanos += 1,
            Err(error) => return Err(error),
        }
    }
}

fn sha256(bytes: &[u8]) -> String {
    Sha256::digest(bytes)
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect()
}

/// The terms as `run.toml` holds them, before the run has an ending.
fn run_table(root: &Path, terms: &Terms, commands: &[(String, String)]) -> toml::Table {
    let strings = |items: &[String]| {
        toml::Value::Array(items.iter().cloned().map(toml::Value::String).collect())
    };
    let mut table = toml::Table::new();
    table.insert("prompt_sha256".into(), sha256(&terms.prompt).into());
    let settings = match std::fs::read(root.join(".claude").join("settings.json")) {
        Ok(bytes) => sha256(&bytes),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => "absent".to_string(),
        Err(error) => format!("unreadable: {error}"),
    };
    table.insert("settings_sha256".into(), settings.into());
    table.insert("iterations".into(), terms.iterations.into());
    table.insert("budget_usd".into(), terms.budget_usd.into());
    table.insert("permission_mode".into(), MODE.into());
    table.insert("allowed_tools".into(), strings(&terms.allowed));
    table.insert("plugin_dirs".into(), strings(&terms.plugin_dirs));
    let who = ["USER", "USERNAME"]
        .iter()
        .find_map(|name| std::env::var(name).ok().filter(|v| !v.is_empty()));
    table.insert(
        "started_by".into(),
        who.unwrap_or_else(|| "unknown".into()).into(),
    );
    table.insert("started".into(), ledger::now().into());
    if let Some(identity) = ledger::repository_identity(root) {
        table.insert("repository".into(), identity.into());
    }
    let mut resolved = toml::Table::new();
    for (verb, command) in commands {
        resolved.insert(verb.clone(), command.clone().into());
    }
    let mut until = toml::Table::new();
    until.insert("verbs".into(), resolved.into());
    table.insert("until".into(), until.into());
    table
}

fn write(path: &Path, bytes: &[u8]) -> Result<(), String> {
    std::fs::write(path, bytes).map_err(|error| format!("can't write {}: {error}", path.display()))
}

/// One evaluation of the condition: it holds only when every named verb's
/// command exits 0 and the tree is identified and the same after the verbs as
/// before them. Where the verbs changed the tree, they run once more and that
/// second result stands, so a verb that settles after one pass can finish the
/// run and one that changes the tree on every pass never does.
fn evaluate(root: &Path, held: &[(String, String)]) -> Result<bool, String> {
    for _ in 0..2 {
        let mut passed = true;
        let mut ends: Option<(String, String)> = None;
        // Each verb runs the command it resolved to at start, so a call that
        // rewrites the profile changes no condition (REQ-0874).
        for (verb, command) in held {
            let ran = verbs::run_recorded(root, verb, command)
                .map_err(|reason| format!("verb {verb} didn't run: {reason}"))?;
            match ran.status {
                0 => println!("{verb}: passed"),
                status => println!("{verb}: failed, exit status {status}"),
            }
            if let Err(reason) = &ran.recorded {
                println!("not recorded: {verb} ({reason})");
            }
            passed &= ran.status == 0;
            ends = Some(match ends {
                Some((before, _)) => (before, ran.after),
                None => (ran.before, ran.after),
            });
        }
        let Some((before, after)) = ends else {
            return Ok(false);
        };
        if before == ledger::UNBOUND || after == ledger::UNBOUND {
            return Ok(false);
        }
        if before == after {
            return Ok(passed);
        }
    }
    Ok(false)
}

/// What one call left: its exit status, or none where a signal ended it, and
/// the JSON result it printed, where it printed one.
struct Called {
    status: Option<i32>,
    result: Option<Value>,
}

/// What every call of a run is given beside the terms, fixed at start.
struct Context {
    /// The run's `progress` directory, as an absolute path with every link
    /// and `..` resolved, because a permission rule names the file as the
    /// platform finds it.
    progress: PathBuf,
    preamble: String,
    /// `meow-loop`'s own directory, which every call names first with
    /// `--plugin-dir`, so the unit's hook loads in every call.
    unit: PathBuf,
    /// Each named verb with the command it resolved to at start.
    held: Vec<(String, String)>,
    /// The files whose change ends the run `tampered`: the run's `run.toml`
    /// and `prompt.md`, and the work tree's `.claude/settings.json`.
    watched: [PathBuf; 3],
}

impl Context {
    fn new(
        dir: &Path,
        root: &Path,
        terms: &Terms,
        unit: PathBuf,
        held: Vec<(String, String)>,
    ) -> Result<Self, String> {
        let progress = dir.join("progress");
        let progress = progress
            .canonicalize()
            .map_err(|error| format!("can't resolve {}: {error}", progress.display()))?;
        let preamble = preamble(&progress.join("progress.md"), &terms.verbs);
        let watched = [
            dir.join("run.toml"),
            dir.join("prompt.md"),
            root.join(".claude").join("settings.json"),
        ];
        Ok(Context {
            progress,
            preamble,
            unit,
            held,
            watched,
        })
    }

    /// The sha256 of each watched file, or `absent` where it doesn't exist and
    /// `unreadable` where it can't be read, which a later read can't match
    /// unless it fails the same way.
    fn seal(&self) -> Vec<String> {
        self.watched
            .iter()
            .map(|path| match std::fs::read(path) {
                Ok(bytes) => sha256(&bytes),
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => "absent".to_string(),
                Err(error) => format!("unreadable: {error}"),
            })
            .collect()
    }

    /// The watched files whose sha256 differs from `sealed`.
    fn tampered(&self, sealed: &[String]) -> Vec<String> {
        self.seal()
            .iter()
            .zip(sealed)
            .zip(&self.watched)
            .filter(|((now, then), _)| now != then)
            .map(|(_, path)| path.display().to_string())
            .collect()
    }
}

/// The preamble every call of a run carries. It holds no iteration number and
/// no spend, so its bytes are the same on every call (REQ-0880).
fn preamble(progress: &Path, verbs: &[String]) -> String {
    format!(
        "<role>
This session is one iteration of a run that `meow-loop` repeats. Each
iteration is a new session given this same prompt, so nothing an earlier
iteration said is in this conversation.
</role>

<rules name=\"the run\">
- L1. Read `{file}` before you start, because it is the only place an earlier
  iteration could leave what it did, what is left and what failed.
- L2. Before you stop, bring that file up to date with what is done, what is
  left and what failed, keeping what it already holds that is still true,
  because this conversation ends with the session and the file carries over.
- L3. Work until the condition `verbs={verbs}` holds, and never report it as
  held, because the runner runs those verification verbs itself after this
  session and decides from their exit status whether the run is finished.
- L4. Never try to extend the run, because the runner holds its bounds in its
  own process and nothing this session writes or prints changes them.
</rules>
",
        file = progress.display(),
        verbs = verbs.join(","),
    )
}

/// An amount to six decimal places, without the zeros that end it, so a sum
/// such as 0.8999999999999999 reads as 0.9.
fn dollars(amount: f64) -> String {
    let text = format!("{amount:.6}");
    text.trim_end_matches('0').trim_end_matches('.').to_string()
}

/// The cap one call gets for `left`, the budget less the spend so far: six
/// decimal places, or every digit where six would round it to nothing, and
/// never below 0.
fn cap(left: f64) -> String {
    if left >= 0.000001 {
        dollars(left)
    } else {
        left.max(0.0).to_string()
    }
}

/// Makes one call, capped at `left`, the budget less the spend so far. The cap
/// is the platform's limit on this one call, and the check before the call is
/// what bounds the run.
fn call(
    claude: &Path,
    root: &Path,
    terms: &Terms,
    context: &Context,
    left: f64,
) -> Result<Called, String> {
    let mut command = Command::new(claude);
    command.current_dir(root).args([
        "-p",
        "--output-format",
        "json",
        "--no-session-persistence",
        "--setting-sources",
        "project",
    ]);
    command.arg("--plugin-dir").arg(&context.unit);
    for dir in &terms.plugin_dirs {
        command.args(["--plugin-dir", dir]);
    }
    command.args(["--permission-mode", MODE]);
    for rule in &terms.allowed {
        command.args(["--allowedTools", rule]);
    }
    // The run's id is fixed only at start, so no rule the person types can
    // name the progress file. A rule writes an absolute path after one more
    // slash.
    let file = context.progress.join("progress.md");
    for tool in ["Edit", "Write"] {
        command.args(["--allowedTools", &format!("{tool}(/{})", file.display())]);
    }
    command.args(["--permission-prompts", "none", "--add-dir"]);
    command.arg(&context.progress);
    command.args([
        "--max-budget-usd",
        &cap(left),
        // A call can't start a nested run by either name (REQ-0894).
        "--disallowedTools",
        "Bash(meow-loop *)",
        "Bash(meow loop *)",
        "--append-system-prompt",
        &context.preamble,
    ]);
    let mut child = command
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .map_err(|error| format!("claude can't be started: {error}"))?;
    let stdin = child.stdin.take();
    // The prompt is written from another thread, so a call that prints before
    // it has read its whole input can't stall both ends of the pipes.
    let output = std::thread::scope(|scope| {
        scope.spawn(|| {
            if let Some(mut stdin) = stdin {
                let _ = stdin.write_all(&terms.prompt);
            }
        });
        child.wait_with_output()
    })
    .map_err(|error| format!("claude can't be waited for: {error}"))?;
    let text = String::from_utf8_lossy(&output.stdout);
    let result = serde_json::from_str::<Value>(text.trim())
        .ok()
        .or_else(|| {
            text.lines()
                .rev()
                .find(|line| !line.trim().is_empty())
                .and_then(|line| serde_json::from_str(line.trim()).ok())
        })
        .filter(Value::is_object);
    let status = output.status.code();
    // A file the system can't run is handed to the shell, which reports it
    // with one of these two statuses, and no call was made.
    if result.is_none() && matches!(status, Some(126 | 127)) {
        return Err(format!(
            "claude can't be started: {} exited {} and printed no result",
            claude.display(),
            status.unwrap_or_default()
        ));
    }
    Ok(Called { status, result })
}

/// Where a line of the log starts, and how many bytes it holds before its end.
struct Logged {
    start: u64,
    length: usize,
}

/// Writes one line of the log: at its end, or over the line `over` names. A
/// call's line is written before the condition is evaluated, so a run stopped
/// during the verbs still shows the call, and written again in place once the
/// result is known. The log is never cut back, so at every moment it holds
/// the line in one form or the other, and a shorter line is padded with spaces
/// to cover the one it replaces.
fn log_line(log: &Path, over: Option<&Logged>, line: &Value) -> Result<Logged, String> {
    let mut text = line.to_string();
    let length = text.len().max(over.map_or(0, |old| old.length));
    text.push_str(&" ".repeat(length - text.len()));
    text.push('\n');
    let put = || {
        let mut file = OpenOptions::new().write(true).open(log)?;
        let start = file.seek(match over {
            Some(old) => SeekFrom::Start(old.start),
            None => SeekFrom::End(0),
        })?;
        file.write_all(text.as_bytes())?;
        Ok(Logged { start, length })
    };
    put().map_err(|error: std::io::Error| format!("can't write {}: {error}", log.display()))
}

/// Runs the loop to its ending, or to the state it can't read past.
fn run(
    root: &Path,
    terms: &Terms,
    context: &Context,
    claude: &Path,
    log: &Path,
) -> Result<&'static str, String> {
    let sealed = context.seal();
    // A changed term is reported as that, whichever bound the run also
    // reached, so this check comes first before a call and after it.
    let tampered = || {
        let changed = context.tampered(&sealed);
        (!changed.is_empty()).then(|| {
            println!("the run's terms changed: {}", changed.join(", "));
            "tampered"
        })
    };
    if evaluate(root, &context.held)? {
        // The verbs may themselves have changed a watched file.
        if let Some(ending) = tampered() {
            return Ok(ending);
        }
        return Ok("finished");
    }
    let (mut spend, mut largest) = (0.0_f64, 0.0_f64);
    let progress = context.progress.join("progress.md");
    // A progress file the runner can't read counts as changed, as an
    // unidentified tree does, so neither can end a run `idle`. An absent file
    // is a state of its own, so a call that removes it can't keep a run busy.
    let digest = || match std::fs::read(&progress) {
        Ok(bytes) => Some(sha256(&bytes)),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Some("absent".to_string()),
        Err(_) => None,
    };
    let mut idle_before = false;
    for iteration in 1..=terms.iterations {
        if let Some(ending) = tampered() {
            return Ok(ending);
        }
        // The next call may cost as much as the largest so far, so the run
        // ends before a call that could pass the budget, not after it.
        if spend + largest > terms.budget_usd + SLACK {
            println!(
                "the next call could pass the budget: {} spent, {} the largest call, {} the budget",
                dollars(spend),
                dollars(largest),
                dollars(terms.budget_usd)
            );
            return Ok("budget");
        }
        // Read after the last evaluation, so a verb that writes to the tree
        // never counts as a change this call made.
        let before = ledger::tree_id(root);
        let progress_before = digest();
        let called = call(claude, root, terms, context, terms.budget_usd - spend)?;
        let after = ledger::tree_id(root);
        let progress_after = digest();
        let progress_changed = progress_before.is_none() || progress_before != progress_after;
        let unidentified = before == ledger::UNBOUND || after == ledger::UNBOUND;
        // An iteration changes nothing when both the tree and the progress
        // file are as they were (REQ-0886).
        let idle = !unidentified && before == after && !progress_changed;
        let result = called.result.as_ref();
        // A cost that isn't a number of dollars at or above 0 can't be summed.
        let cost = result
            .and_then(|r| r.get("total_cost_usd"))
            .and_then(Value::as_f64)
            .filter(|cost| cost.is_finite() && *cost >= 0.0);
        let mut line = json!({
            "iteration": iteration,
            "tree_before": before,
            "tree_after": after,
            "total_cost_usd": result
                .and_then(|r| r.get("total_cost_usd"))
                .filter(|cost| cost.is_number()),
            "sum_usd": cost.map(|cost| spend + cost),
            "permission_denials": result
                .and_then(|r| r.get("permission_denials"))
                .and_then(Value::as_array)
                .map(Vec::len),
            "exit_status": called.status,
            "progress_changed": progress_changed,
            "unidentified": unidentified,
            "condition": null,
        });
        let logged = log_line(log, None, &line)?;
        if let Some(ending) = tampered() {
            return Ok(ending);
        }
        let shown = match called.status {
            Some(status) => format!("exit status {status}"),
            None => "ended by a signal".to_string(),
        };
        // A broken bound is reported before a success, so both endings come
        // before the condition is evaluated.
        let Some(cost) = cost else {
            println!(
                "iteration {iteration}: {shown}, the call reported no cost the runner can sum"
            );
            return Ok("unmetered");
        };
        spend += cost;
        largest = largest.max(cost);
        let subtype = result
            .and_then(|r| r.get("subtype"))
            .and_then(Value::as_str);
        if subtype == Some("error_max_budget_usd") {
            println!("iteration {iteration}: {shown}, the call reached its own cap");
            return Ok("budget");
        }
        // An unchanged tree would repeat the last result.
        let held = if after != before || after == ledger::UNBOUND {
            let held = evaluate(root, &context.held)?;
            line["condition"] = json!(held);
            log_line(log, Some(&logged), &line)?;
            Some(held)
        } else {
            None
        };
        match held {
            Some(true) => {
                // The verbs may themselves have changed a watched file, and
                // a changed term is reported before a success.
                if let Some(ending) = tampered() {
                    return Ok(ending);
                }
                println!("iteration {iteration}: {shown}, the condition holds");
                return Ok("finished");
            }
            Some(false) => println!("iteration {iteration}: {shown}, the condition doesn't hold"),
            None => println!("iteration {iteration}: {shown}, the tree didn't change"),
        }
        if idle && idle_before {
            println!("two iterations in a row changed neither the tree nor the progress file");
            return Ok("idle");
        }
        idle_before = idle;
    }
    if let Some(ending) = tampered() {
        return Ok(ending);
    }
    Ok("ceiling")
}

fn start(args: &[String]) -> u8 {
    let terms = match terms(args) {
        Ok(terms) => terms,
        Err(errors) => {
            for error in errors {
                eprintln!("usage: {error}");
            }
            return USAGE;
        }
    };
    // A session inside Claude Code sets `CLAUDECODE`, so a run started from
    // one was started by the model, and only a person starts a run
    // (REQ-0894). Nothing is written before this refusal.
    if std::env::var_os("CLAUDECODE").is_some() {
        println!("unresolved: a run starts from a terminal outside Claude Code");
        return UNRESOLVED;
    }
    let refuse = |what: &str| {
        println!("unresolved: {what}");
        UNRESOLVED
    };
    if !in_work_tree() {
        return refuse("not a git work tree");
    }
    let root = profile::repository_root();
    if ledger::state_off() {
        return refuse("state writing is off, and a run needs state");
    }
    let Some(runs) = ledger::runs_dir(&root) else {
        return refuse(ledger::no_state_reason());
    };
    let Some(claude) = claude() else {
        return refuse("claude is not on the path");
    };
    let Some(unit) = own_unit() else {
        return refuse("meow-loop's own directory can't be found from its program's path");
    };
    let mut commands = Vec::new();
    let mut unresolved = false;
    for verb in &terms.verbs {
        match verbs::command_of(&root, verb) {
            Ok(command) => commands.push((verb.clone(), command)),
            Err(_) => {
                unresolved = true;
                refuse(&format!("verb {verb} resolves to no command"));
            }
        }
    }
    if unresolved {
        return UNRESOLVED;
    }
    let _held = match lock(&runs) {
        Ok(file) => file,
        Err(reason) => return refuse(&reason),
    };

    let dir = match new_run_dir(&runs) {
        Ok(dir) => dir,
        Err(error) => {
            return refuse(&format!(
                "can't create a run in {}: {error}",
                runs.display()
            ));
        }
    };
    let mut table = run_table(&root, &terms, &commands);
    let (terms_file, log) = (dir.join("run.toml"), dir.join("log.jsonl"));
    let written = write(&terms_file, table.to_string().as_bytes())
        .and_then(|()| write(&dir.join("prompt.md"), &terms.prompt))
        .and_then(|()| {
            std::fs::create_dir(dir.join("progress"))
                .map_err(|error| format!("can't create {}/progress: {error}", dir.display()))
        })
        .and_then(|()| write(&dir.join("progress").join("progress.md"), b""))
        .and_then(|()| write(&log, b""))
        .and_then(|()| Context::new(&dir, &root, &terms, unit, commands.clone()));
    let context = match written {
        Ok(context) => context,
        Err(reason) => {
            let _ = std::fs::remove_dir_all(&dir);
            return refuse(&reason);
        }
    };
    // Old runs go only once the new one is whole, so a refused start removes none.
    remove_old_runs(&runs, &dir);
    println!("run {}", dir.display());

    let ending = match run(&root, &terms, &context, &claude, &log) {
        Ok(ending) => ending,
        Err(reason) => return refuse(&reason),
    };
    table.insert("ending".into(), ending.into());
    if let Err(reason) = write(&terms_file, table.to_string().as_bytes()) {
        return refuse(&reason);
    }
    println!("{ending}");
    if ending == "finished" {
        FINISHED
    } else {
        ENDED
    }
}

/// `meow-loop`'s own directory: the program sits at
/// `<unit>/bin/<target>/meow`, so the unit is three levels up from it, and
/// it is the unit only where its manifest names `meow-loop`, because a call
/// that names another directory loads no hook.
fn own_unit() -> Option<PathBuf> {
    let program = std::env::current_exe().ok()?.canonicalize().ok()?;
    let unit = program.parent()?.parent()?.parent()?.to_path_buf();
    let manifest = std::fs::read_to_string(unit.join(".claude-plugin").join("plugin.json")).ok()?;
    let manifest: Value = serde_json::from_str(&manifest).ok()?;
    (manifest.get("name").and_then(Value::as_str) == Some("meow-loop")).then_some(unit)
}

/// `path` as an absolute path with every link and `..` resolved, where it
/// exists, and its missing tail joined to the resolved part lexically, so a
/// file about to be written is resolved as well as one that exists.
fn resolved(path: &Path) -> PathBuf {
    let absolute = std::path::absolute(path).unwrap_or_else(|_| path.to_path_buf());
    let mut existing = absolute.as_path();
    let mut tail = Vec::new();
    // Walk up past every component that doesn't exist, `..` included, so a
    // path through a missing directory is resolved like any other.
    while !existing.exists() {
        match (existing.parent(), existing.components().next_back()) {
            (Some(parent), Some(last)) => {
                tail.push(last.as_os_str().to_os_string());
                existing = parent;
            }
            _ => break,
        }
    }
    let mut out = existing
        .canonicalize()
        .unwrap_or_else(|_| existing.to_path_buf());
    for name in tail.iter().rev() {
        match name.to_str() {
            Some("..") => {
                out.pop();
            }
            Some(".") => {}
            _ => out.push(name),
        }
    }
    out
}

/// The `PreToolUse` hook on Bash, Edit and Write: it denies a Bash command
/// that starts a run (REQ-0894), and a write of any path under
/// the runs directory other than a run's `progress/progress.md`, because a
/// run's files hold its terms and only the runner writes them (REQ-0874). The
/// hash check decides whether the terms changed, whether or not this ran.
fn guard() -> u8 {
    let mut text = String::new();
    let _ = std::io::Read::read_to_string(&mut std::io::stdin(), &mut text);
    let event: Value = serde_json::from_str(&text).unwrap_or(Value::Null);
    if let Some(command) = event.pointer("/tool_input/command").and_then(Value::as_str) {
        if starts_a_run(command) {
            deny(
                "meow-loop: a run starts from a terminal outside Claude Code, which only a person opens, so a Bash command that runs `meow-loop start` is denied (REQ-0894)",
            );
        }
        return FINISHED;
    }
    let Some(path) = event
        .pointer("/tool_input/file_path")
        .and_then(Value::as_str)
    else {
        return FINISHED;
    };
    let Some(runs) = ledger::runs_root() else {
        return FINISHED;
    };
    let runs = resolved(&runs);
    let target = resolved(Path::new(path));
    let Ok(inside) = target.strip_prefix(&runs) else {
        return FINISHED;
    };
    let names: Vec<_> = inside.iter().collect();
    if let [_, _, progress, file] = names.as_slice()
        && *progress == "progress"
        && *file == "progress.md"
    {
        return FINISHED;
    }
    let tool = event
        .get("tool_name")
        .and_then(Value::as_str)
        .unwrap_or("A write");
    deny(&format!(
        "meow-loop: {tool} of {} under the runs directory is denied, because a run's files hold its terms and only the runner writes them; a call writes only its progress/progress.md (REQ-0874)",
        inside.display()
    ));
    FINISHED
}

/// Answers the hook with `deny` and `reason`.
fn deny(reason: &str) {
    let answer = json!({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    });
    println!("{answer}");
}

/// Whether a command's text starts a run: a word ending in `meow-loop`
/// followed by `start`, or a word ending in `meow` followed by `loop start`.
/// It reads the text and not what the text expands to, so it catches a
/// path-qualified runner and one inside `bash -c`, and misses a name hidden
/// in a script, a variable or a command substitution, or split by quotes or
/// a backslash (SPC-1201). A redirect is dropped wherever it stands, because the shell
/// passes the words around it on as they are.
fn starts_a_run(command: &str) -> bool {
    let raw = command
        .split(|c: char| c.is_whitespace() || "'\"`;|()\\".contains(c))
        .filter(|w| !w.is_empty());
    let mut words: Vec<&str> = Vec::new();
    let mut target = false;
    for word in raw {
        // A runner's name is never taken as a redirect's target, because
        // a `>` the split separated from what follows it, as in `'>'; x`,
        // isn't one.
        if std::mem::take(&mut target) && !word.ends_with("meow-loop") && !word.ends_with("meow") {
            continue;
        }
        match word.find(['<', '>']) {
            Some(at) => {
                let (before, redirect) = word.split_at(at);
                let before = before.trim_matches('&');
                // A descriptor, by number or by name as in `{fd}>`, belongs
                // to the redirect.
                let descriptor = before.bytes().all(|b| b.is_ascii_digit())
                    || (before.starts_with('{') && before.ends_with('}'));
                if !before.is_empty() && !descriptor {
                    words.push(before);
                }
                // A redirect with nothing after its operator takes the next
                // word as its target, as in `> out.log`; `2>&1` takes none.
                target = redirect.trim_start_matches(['<', '>', '&']).is_empty();
            }
            None => words.extend(word.split('&').filter(|w| !w.is_empty())),
        }
    }
    words
        .windows(2)
        .any(|pair| pair[0].ends_with("meow-loop") && pair[1] == "start")
        || words
            .windows(3)
            .any(|three| three[0].ends_with("meow") && three[1] == "loop" && three[2] == "start")
}

pub fn main(args: &[String]) -> u8 {
    match args.split_first() {
        Some((command, rest)) if command == "start" => start(rest),
        Some((command, rest)) if command == "guard" && rest.is_empty() => guard(),
        _ => {
            eprintln!(
                "usage: meow-loop start --prompt <file> --until verbs=<verb>[,<verb>...] --iterations <n> --budget-usd <amount> --permission-mode dontAsk [--allowed-tools <rule>]... [--plugin-dir <dir>]..."
            );
            USAGE
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn typed(args: &[&str]) -> Result<Terms, Vec<String>> {
        terms(&args.iter().map(|a| a.to_string()).collect::<Vec<_>>())
    }

    fn errors(args: &[&str]) -> Vec<String> {
        typed(args).err().unwrap_or_default()
    }

    /// TSK-3370: an amount prints without the error of a binary sum, and the
    /// cap a call gets is never rounded down to nothing.
    #[test]
    fn an_amount_reads_as_its_decimal_figure() {
        assert_eq!(dollars(0.3 + 0.3 + 0.3), "0.9");
        assert_eq!(dollars(1.0), "1");
        assert_eq!(dollars(10.0), "10");
        assert_eq!(dollars(0.0), "0");
        assert_eq!(cap(1.0 - 0.3), "0.7");
        assert_eq!(cap(10.0), "10");
        assert_eq!(cap(0.0000004), "0.0000004");
        assert_eq!(cap(-0.0000000001), "0");
    }

    #[test]
    fn every_missing_term_is_named_in_one_attempt() {
        // REQ-0872: no run starts without a condition, a ceiling and a budget.
        let found = errors(&[]);
        for flag in [
            "--step",
            "--prompt",
            "--until",
            "--iterations",
            "--budget-usd",
            "--permission-mode",
        ] {
            assert!(
                found.contains(&format!("{flag} is required")),
                "{flag} in {found:?}"
            );
        }
        assert_eq!(found.len(), 6);
    }

    #[test]
    fn a_condition_names_only_verbs() {
        let rest = [
            "--iterations",
            "1",
            "--budget-usd",
            "1",
            "--permission-mode",
            "dontAsk",
        ];
        let with = |until: &str| errors(&[&["--until", until], &rest[..]].concat());
        assert!(with("verbs=").contains(&"--until names no verb".to_string()));
        assert!(with("verbs=test,deploy").contains(&"deploy is not a verb".to_string()));
        assert!(
            with("phrase=done")
                .contains(&"--until phrase=done is not a condition kind".to_string())
        );
    }

    #[test]
    fn a_bound_that_bounds_nothing_is_refused() {
        let with = |flag: &str, value: &str| errors(&[flag, value]);
        let said = |flag: &str, value: &str, what: &str| {
            let found = with(flag, value);
            assert!(
                found.contains(&format!("{flag} {value} {what}")),
                "{found:?}"
            );
        };
        for value in ["0", "-1", "many", "1.5", "+3", ""] {
            said("--iterations", value, "is not at least 1");
        }
        said(
            "--iterations",
            "9223372036854775808",
            "is above 9223372036854775807",
        );
        for value in ["0", "0.0", "00"] {
            said("--budget-usd", value, "is not above 0");
        }
        for value in [
            "+1e1", "1e1", "-2", "inf", "NaN", "free", "1.", ".5", "1.2.3", "", "+1",
        ] {
            said("--budget-usd", value, "is not a decimal number");
        }
        let (huge, tiny) = ("9".repeat(400), format!("0.{}1", "0".repeat(400)));
        for value in [huge.as_str(), tiny.as_str()] {
            said("--budget-usd", value, "is too large or too small to hold");
        }
        said("--budget-usd", &"0".repeat(400), "is not above 0");
        for value in ["1", "2.50", "0.01"] {
            let found = with("--budget-usd", value);
            assert!(
                found.iter().all(|e| !e.starts_with("--budget-usd")),
                "{found:?}"
            );
        }
        for value in ["acceptEdits", "bypassPermissions", "default"] {
            said("--permission-mode", value, "is refused");
        }
    }
}
