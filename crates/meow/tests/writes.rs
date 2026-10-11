// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The crate writes only the run state, the record and the repository
//! (TSK-4930, REQ-1429, SPC-1080 "What the harness writes and reads").

#![cfg(all(
    feature = "verbs",
    feature = "record",
    feature = "loop",
    feature = "scm",
    feature = "git",
    feature = "licence",
    feature = "unattended"
))]

use std::collections::BTreeMap;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        static COUNT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
        let count = COUNT.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "meow-writes-{name}-{}-{stamp}-{count}",
            std::process::id()
        ));
        std::fs::create_dir_all(&path).unwrap();
        Dir(path)
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

/// Every file under `dir` with its bytes.
fn snapshot(dir: &Path) -> BTreeMap<PathBuf, Vec<u8>> {
    fn walk(dir: &Path, out: &mut BTreeMap<PathBuf, Vec<u8>>) {
        let Ok(entries) = std::fs::read_dir(dir) else {
            return;
        };
        for entry in entries.flatten() {
            let path = entry.path();
            if path.file_name().is_some_and(|n| n == ".git") {
                continue;
            }
            if path.is_dir() {
                walk(&path, out);
            } else {
                out.insert(path.clone(), std::fs::read(&path).unwrap_or_default());
            }
        }
    }
    let mut out = BTreeMap::new();
    walk(dir, &mut out);
    out
}

/// What changed between two snapshots, by path.
fn changed(
    before: &BTreeMap<PathBuf, Vec<u8>>,
    after: &BTreeMap<PathBuf, Vec<u8>>,
) -> Vec<PathBuf> {
    after
        .iter()
        .filter(|(path, bytes)| before.get(*path) != Some(*bytes))
        .map(|(path, _)| path.clone())
        .collect()
}

/// REQ-1429: the check can fail: a file created in the home directory shows.
#[test]
fn the_comparison_finds_a_write_to_the_home_directory() {
    let home = Dir::new("home");
    let before = snapshot(&home.0);
    std::fs::write(home.0.join(".stray"), "x").unwrap();
    let after = snapshot(&home.0);
    assert_eq!(changed(&before, &after), vec![home.0.join(".stray")]);
}

/// REQ-1429: each subcommand run on a fixture leaves the home and temporary
/// directories as they were, and writes only the state directory and the
/// repository.
#[test]
fn no_subcommand_writes_outside_the_state_the_repository_and_the_record() {
    let repo = Dir::new("repo");
    let home = Dir::new("home");
    let tmp = Dir::new("tmp");
    let state = Dir::new("state");
    let run = |args: &[&str], input: &str| {
        let mut child = Command::new(env!("CARGO_BIN_EXE_meow"))
            .args(args)
            .current_dir(&repo.0)
            .env("HOME", &home.0)
            .env("TMPDIR", &tmp.0)
            .env("XDG_STATE_HOME", &state.0)
            .env("XDG_RUNTIME_DIR", &state.0)
            .env("XDG_CONFIG_HOME", home.0.join(".config"))
            .env("XDG_CACHE_HOME", home.0.join(".cache"))
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        child
            .stdin
            .take()
            .unwrap()
            .write_all(input.as_bytes())
            .unwrap();
        child.wait_with_output().unwrap()
    };
    let git = Command::new("git")
        .args(["init", "-q", "--template="])
        .current_dir(&repo.0)
        .status()
        .unwrap();
    assert!(git.success());
    std::fs::create_dir_all(repo.0.join(".meowpaw")).unwrap();
    std::fs::write(
        repo.0.join(".meowpaw/profile.toml"),
        "[stages]\nlint = \"true\"\n\n[git]\ntrunk = \"main\"\n\n[commits]\nsubject_limit = 72\ntrailers = [\"Signed-off-by\"]\n\n[commits.types]\nfeat = \"minor\"\n\n[unattended]\npermission_mode = \"dontAsk\"\ngates = [\"research\"]\nrelease = false\namend_approved = false\n",
    )
    .unwrap();
    let home_before = snapshot(&home.0);
    let tmp_before = snapshot(&tmp.0);
    let repo_before = snapshot(&repo.0);
    let cwd = serde_json::to_string(&repo.0.display().to_string()).unwrap();
    let event = format!(
        "{{\"hook_event_name\":\"PreToolUse\",\"session_id\":\"s\",\"cwd\":{cwd},\"tool_name\":\"Bash\",\"tool_input\":{{\"command\":\"echo x\"}}}}"
    );
    let calls: Vec<(Vec<&str>, &str)> = vec![
        (vec!["verbs", "status"], ""),
        (vec!["verbs", "run", "lint"], ""),
        (vec!["verbs", "evidence"], ""),
        (vec!["verbs", "state"], ""),
        (vec!["verbs", "revision"], "{}"),
        (vec!["verbs", "tree", "HEAD"], ""),
        (vec!["scm", "convention"], ""),
        (
            vec!["scm", "check-message"],
            "feat: a thing\n\nSigned-off-by: A <a@b>\n",
        ),
        (vec!["git", "commit-guard"], event.as_str()),
        (vec!["git", "push-guard"], event.as_str()),
        (vec!["licence", "check"], ""),
        (vec!["unattended", "plan"], ""),
        (vec!["loop", "guard"], event.as_str()),
        (vec!["loop", "stop"], ""),
        (vec!["loop", "purge"], ""),
        (vec!["record", "status"], ""),
        (vec!["record", "count"], ""),
    ];
    for (args, input) in calls {
        let done = run(&args, input);
        let code = done.status.code();
        // A call that reached its work exits 0, 1 or 3, and never by a signal or a usage error.
        assert!(
            matches!(code, Some(0 | 1 | 3)),
            "meow {} ended with {code:?}: {}",
            args.join(" "),
            String::from_utf8_lossy(&done.stderr)
        );
    }
    assert_eq!(
        changed(&home_before, &snapshot(&home.0)),
        Vec::<PathBuf>::new(),
        "a subcommand wrote into the home directory"
    );
    assert_eq!(
        changed(&tmp_before, &snapshot(&tmp.0)),
        Vec::<PathBuf>::new(),
        "a subcommand wrote into the temporary directory"
    );
    // Every file under the state directory is under `meowpaw/` or a lock named for it.
    for path in snapshot(&state.0).keys() {
        let relative = path
            .strip_prefix(&state.0)
            .unwrap()
            .to_string_lossy()
            .to_string();
        assert!(
            relative.starts_with("meowpaw"),
            "a subcommand wrote {relative} under the state directory, outside meowpaw/"
        );
    }
    let repo_changed = changed(&repo_before, &snapshot(&repo.0));
    assert_eq!(
        repo_changed,
        Vec::<PathBuf>::new(),
        "a read-only subcommand changed the repository"
    );
}

/// The writes the crate's source makes, by file and how many of each kind of
/// call, each with where it writes. A new call fails this test, so a person
/// reads where it writes before it is added (REQ-1429).
const WRITES: [(&str, usize, &str); 11] = [
    (
        "github/project.rs",
        1,
        "the task record the projection marks, under the record root",
    ),
    (
        "github/request.rs",
        1,
        "the rate limit's wait file, under the run state",
    ),
    (
        "github/sync.rs",
        2,
        "the task and its authority's record, under the record root",
    ),
    (
        "gotask.rs",
        2,
        "a scratch directory its own test helper makes and removes",
    ),
    (
        "record.rs",
        7,
        "the record's files through a temporary file beside each, and the onboarding removal under the repository",
    ),
    (
        "runloop.rs",
        11,
        "a run's own files under the run state, and its lock",
    ),
    (
        "verbs.rs",
        6,
        "the personal profile and the exclude file of the repository, written through a temporary file",
    ),
    (
        "verbs/ledger.rs",
        16,
        "the ledger, its outputs, the counter and the lock under the run state, and a temporary index in the temporary directory",
    ),
    ("scm.rs", 0, "writes nothing"),
    ("licence.rs", 0, "writes nothing"),
    ("author.rs", 0, "writes nothing"),
];

/// REQ-1429: each call in the crate's source that writes a file is one the
/// table above knows, by file.
#[test]
fn each_write_in_the_source_is_one_the_table_names() {
    let src = Path::new(env!("CARGO_MANIFEST_DIR")).join("src");
    let patterns = [
        "fs::write(",
        "File::create(",
        "OpenOptions::new(",
        "create_dir_all(",
        "fs::rename(",
        "fs::copy(",
        "remove_file(",
        "remove_dir_all(",
        "File::options",
        "set_permissions(",
        "create_dir(",
        "remove_dir(",
        "hard_link(",
        "symlink(",
        "File::create_new(",
        "set_len(",
    ];
    fn files(dir: &Path, out: &mut Vec<PathBuf>) {
        for entry in std::fs::read_dir(dir).unwrap().flatten() {
            let path = entry.path();
            if path.is_dir() {
                files(&path, out);
            } else if path.extension().is_some_and(|e| e == "rs") {
                out.push(path);
            }
        }
    }
    let mut found = Vec::new();
    files(&src, &mut found);
    let table: BTreeMap<&str, usize> = WRITES.iter().map(|(f, n, _)| (*f, *n)).collect();
    for path in found {
        let relative = path
            .strip_prefix(&src)
            .unwrap()
            .to_string_lossy()
            .to_string();
        let text = std::fs::read_to_string(&path).unwrap();
        // The test module starts at `#[cfg(test)]` followed by `mod tests`; an earlier
        // `#[cfg(test)]` on a helper doesn't end the production code.
        let body = text.split("#[cfg(test)]\nmod tests").next().unwrap();
        let count: usize = patterns.iter().map(|p| body.matches(p).count()).sum();
        let expected = table.get(relative.as_str()).copied().unwrap_or(0);
        assert_eq!(
            count, expected,
            "{relative} makes {count} write calls and the table names {expected}: say where each writes in WRITES"
        );
    }
}
