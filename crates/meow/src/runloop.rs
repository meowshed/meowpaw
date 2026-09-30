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
//! for the next goes in the run's progress file (REQ-0882).

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
    /// The budget as typed, which is what each call's cap is passed as.
    budget: String,
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
        // Every call gets the budget as typed, so only the one form every
        // reader of it agrees on is accepted: digits, with one optional point.
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

    match (prompt, ceiling, budget, budget_usd) {
        (Some(prompt), Some(iterations), Some(budget), Some(budget_usd)) if errors.is_empty() => {
            Ok(Terms {
                prompt,
                verbs: named,
                iterations,
                budget: budget.to_string(),
                budget_usd,
                allowed,
                plugin_dirs,
            })
        }
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
fn evaluate(root: &Path, named: &[String]) -> Result<bool, String> {
    for _ in 0..2 {
        let mut passed = true;
        let mut ends: Option<(String, String)> = None;
        for verb in named {
            let command = verbs::command_of(root, verb)
                .map_err(|_| format!("verb {verb} resolves to no command"))?;
            let ran = verbs::run_recorded(root, verb, &command)
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
}

impl Context {
    fn new(dir: &Path, terms: &Terms) -> Result<Self, String> {
        let progress = dir.join("progress");
        let progress = progress
            .canonicalize()
            .map_err(|error| format!("can't resolve {}: {error}", progress.display()))?;
        let preamble = preamble(&progress.join("progress.md"), &terms.verbs);
        Ok(Context { progress, preamble })
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

fn call(claude: &Path, root: &Path, terms: &Terms, context: &Context) -> Result<Called, String> {
    let mut command = Command::new(claude);
    command.current_dir(root).args([
        "-p",
        "--output-format",
        "json",
        "--no-session-persistence",
        "--setting-sources",
        "project",
    ]);
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
    // The whole budget, because the runner keeps no spend yet: until it does,
    // this is only the platform's cap on one call.
    command.args([
        "--max-budget-usd",
        &terms.budget,
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
    if evaluate(root, &terms.verbs)? {
        return Ok("finished");
    }
    for iteration in 1..=terms.iterations {
        // Read after the last evaluation, so a verb that writes to the tree
        // never counts as a change this call made.
        let before = ledger::tree_id(root);
        let called = call(claude, root, terms, context)?;
        let after = ledger::tree_id(root);
        let result = called.result.as_ref();
        let mut line = json!({
            "iteration": iteration,
            "tree_before": before,
            "tree_after": after,
            "total_cost_usd": result
                .and_then(|r| r.get("total_cost_usd"))
                .filter(|cost| cost.is_number()),
            "permission_denials": result
                .and_then(|r| r.get("permission_denials"))
                .and_then(Value::as_array)
                .map(Vec::len),
            "exit_status": called.status,
            "condition": null,
        });
        let logged = log_line(log, None, &line)?;
        // An unchanged tree would repeat the last result.
        let held = if after != before || after == ledger::UNBOUND {
            let held = evaluate(root, &terms.verbs)?;
            line["condition"] = json!(held);
            log_line(log, Some(&logged), &line)?;
            Some(held)
        } else {
            None
        };
        let shown = match called.status {
            Some(status) => format!("exit status {status}"),
            None => "ended by a signal".to_string(),
        };
        match held {
            Some(true) => {
                println!("iteration {iteration}: {shown}, the condition holds");
                return Ok("finished");
            }
            Some(false) => println!("iteration {iteration}: {shown}, the condition doesn't hold"),
            None => println!("iteration {iteration}: {shown}, the tree didn't change"),
        }
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
        .and_then(|()| write(&log, b""));
    if let Err(reason) = written {
        let _ = std::fs::remove_dir_all(&dir);
        return refuse(&reason);
    }
    // Old runs go only once the new one is whole, so a refused start removes none.
    remove_old_runs(&runs, &dir);
    println!("run {}", dir.display());

    let ending = match Context::new(&dir, &terms)
        .and_then(|context| run(&root, &terms, &context, &claude, &log))
    {
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

pub fn main(args: &[String]) -> u8 {
    match args.split_first() {
        Some((command, rest)) if command == "start" => start(rest),
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

    #[test]
    fn every_missing_term_is_named_in_one_attempt() {
        // REQ-0872: no run starts without a condition, a ceiling and a budget.
        let found = errors(&[]);
        for flag in [
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
        assert_eq!(found.len(), 5);
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
