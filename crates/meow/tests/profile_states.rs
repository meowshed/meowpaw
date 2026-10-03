// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The profile's three states and its unknown keys, as `meow-checks` prints
//! them from a fixture repository (TSK-4300, SPC-1080 "The profile").

#![cfg(feature = "verbs")]

use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

const VERBS: [&str; 5] = ["format", "lint", "check", "test", "build"];

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "meow-profile-{name}-{}-{stamp}",
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

fn write_profile(dir: &Path, text: &str) {
    std::fs::create_dir_all(dir.join(".meowpaw")).unwrap();
    std::fs::write(dir.join(".meowpaw/profile.toml"), text).unwrap();
}

/// A git repository at `dir`, so the root is the top of a working tree.
fn init(dir: &Path) {
    let done = Command::new("git")
        .args(["init", "-q"])
        .current_dir(dir)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap();
    assert!(done.status.success(), "git init failed: {done:?}");
}

/// `meow <args>` in `dir`, given `input` on standard input, with a state
/// directory of the fixture's own.
fn meow(dir: &Path, state: &Path, args: &[&str], input: &str) -> Output {
    let mut child = Command::new(env!("CARGO_BIN_EXE_meow"))
        .args(args)
        .current_dir(dir)
        .env("XDG_STATE_HOME", state)
        .env("XDG_RUNTIME_DIR", state)
        .env("MEOWPAW_STATE_DIR", state)
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
}

/// `meow verbs <args>` in `dir`, and what it printed on standard output.
fn checks(dir: &Path, state: &Path, args: &[&str]) -> (Output, String) {
    let done = meow(dir, state, &[&["verbs"], args].concat(), "");
    let stdout = String::from_utf8_lossy(&done.stdout).into_owned();
    (done, stdout)
}

fn lines(stdout: &str) -> Vec<&str> {
    stdout.lines().map(str::trim_end).collect()
}

#[test]
fn a_profile_above_the_root_is_absent() {
    // TSK-4300 criterion 1, REQ-2940: no profile is read from above the root.
    let parent = Dir::new("above");
    let state = Dir::new("above-state");
    write_profile(&parent.0, "[verbs]\ntest = \"true\"\n");
    let root = parent.0.join("repository");
    std::fs::create_dir_all(&root).unwrap();
    init(&root);
    let (done, stdout) = checks(&root, &state.0, &["status"]);
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert!(
        lines(&stdout).contains(&"profile: absent"),
        "no `profile: absent` line in:\n{stdout}"
    );
    for verb in VERBS {
        let line = lines(&stdout)
            .into_iter()
            .find(|line| line.starts_with(&format!("{verb} ")))
            .unwrap_or_else(|| panic!("no line for {verb} in:\n{stdout}"));
        assert!(
            line.contains("unresolved  no profile:"),
            "{verb} isn't unresolved as `no profile`: {line}"
        );
    }
}

#[test]
fn an_unparseable_profile_names_the_parser_message_and_line_and_runs_nothing() {
    // TSK-4300 criterion 2, REQ-2948: a broken profile is told apart from an
    // absent one, every verb stays unresolved and nothing falls back.
    let root = Dir::new("broken");
    let state = Dir::new("broken-state");
    init(&root.0);
    let text = "[verbs]\ntest = \"touch ran\"\n[verbs\n";
    write_profile(&root.0, text);
    let message = text
        .parse::<toml::Table>()
        .expect_err("the fixture doesn't parse")
        .message()
        .to_string();
    let joined = message
        .lines()
        .map(str::trim)
        .filter(|line| !line.is_empty())
        .collect::<Vec<_>>()
        .join("; ");
    assert!(!joined.is_empty(), "the parser gave no message");
    let expected = format!("profile error: line 3: {joined}");

    let (status, status_out) = checks(&root.0, &state.0, &["status"]);
    let (run, run_out) = checks(&root.0, &state.0, &["run", "test"]);
    for (name, stdout) in [("status", &status_out), ("run test", &run_out)] {
        let found = lines(stdout);
        assert!(
            found.contains(&"profile: unparseable"),
            "{name} prints no `profile: unparseable` line:\n{stdout}"
        );
        assert!(
            found.contains(&expected.as_str()),
            "{name} prints no {expected:?} line:\n{stdout}"
        );
    }
    assert_eq!(status.status.code(), Some(0), "{status_out}");
    for verb in VERBS {
        let line = lines(&status_out)
            .into_iter()
            .find(|line| line.starts_with(&format!("{verb} ")))
            .unwrap_or_else(|| panic!("no line for {verb} in:\n{status_out}"));
        assert!(
            line.contains("unresolved  profile unparseable:"),
            "{verb} isn't unresolved as `profile unparseable`: {line}"
        );
    }
    assert!(
        run_out.contains("== test: unresolved (profile unparseable:"),
        "{run_out}"
    );
    assert_eq!(run.status.code(), Some(3), "{run_out}");
    assert!(
        !root.0.join("ran").exists(),
        "a command ran from a profile that doesn't parse"
    );
}

#[test]
fn an_unknown_key_is_named_once_and_changes_no_exit_status() {
    // TSK-4300 criterion 3, REQ-2942: an unknown key is ignored and reported.
    let with = Dir::new("tset");
    let without = Dir::new("no-tset");
    let state = Dir::new("tset-state");
    for (dir, text) in [
        (&with, "[verbs]\ntset = \"true\"\ntest = \"true\"\n"),
        (&without, "[verbs]\ntest = \"true\"\n"),
    ] {
        init(&dir.0);
        write_profile(&dir.0, text);
    }
    let (done, stdout) = checks(&with.0, &state.0, &["run", "test"]);
    let (plain, plain_out) = checks(&without.0, &state.0, &["run", "test"]);
    assert!(
        lines(&stdout).contains(&"profile: parsed"),
        "no `profile: parsed` line in:\n{stdout}"
    );
    let named: Vec<&str> = lines(&stdout)
        .into_iter()
        .filter(|line| line.contains("verbs.tset"))
        .collect();
    assert_eq!(
        named,
        ["unknown key: verbs.tset"],
        "verbs.tset isn't named once as unknown in:\n{stdout}"
    );
    assert!(stdout.contains("summary: test passed"), "{stdout}");
    assert_eq!(done.status.code(), Some(0), "{stdout}");
    assert_eq!(done.status.code(), plain.status.code(), "{plain_out}");
    assert!(
        !lines(&plain_out)
            .iter()
            .any(|line| line.starts_with("unknown key:")),
        "a profile of known keys names an unknown one:\n{plain_out}"
    );
}

#[test]
#[cfg(all(
    feature = "scm",
    feature = "git",
    feature = "record",
    feature = "github",
    feature = "licence",
    feature = "markdown",
    feature = "mise",
    feature = "gotask",
    feature = "unattended"
))]
fn every_subcommand_that_reads_the_profile_names_each_unknown_key_once() {
    // TSK-4300 criterion 3, REQ-2942 and SPC-1080: every command that reads
    // the profile names each unknown key, a key in a verb's table included,
    // and exits as it would without the keys. The loop runner stays out,
    // because it refuses before it reads the profile unless `claude` is
    // installed and the binary sits in its unit.
    let with = Dir::new("every");
    let without = Dir::new("every-known");
    let state = Dir::new("every-state");
    for (dir, text) in [
        (
            &with,
            "[verbs]\ntset = \"true\"\n[verbs.test]\ncommand = \"true\"\ncmd = \"x\"\n",
        ),
        (&without, "[verbs.test]\ncommand = \"true\"\n"),
    ] {
        init(&dir.0);
        write_profile(&dir.0, text);
        for name in ["a.md", "b.md"] {
            std::fs::write(dir.0.join(name), "text\n").unwrap();
        }
        let added = Command::new("git")
            .args(["add", "-A"])
            .current_dir(&dir.0)
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .output()
            .unwrap();
        assert!(added.status.success(), "git add failed: {added:?}");
    }
    // A hook reads the session's directory and the shell command as JSON.
    let event = |dir: &Dir, verb: &str| {
        format!(
            "{{\"cwd\": {:?}, \"tool_input\": {{\"command\": \"git {verb}\"}}}}",
            dir.0.display().to_string()
        )
    };
    // Each subcommand, the stream it reports the profile on, and the prefix
    // its other lines carry (SPC-1080).
    let subcommands: [(&[&str], &str, &str); 15] = [
        (&["verbs", "status"], "stdout", ""),
        (&["verbs", "run", "test"], "stdout", ""),
        (&["scm", "convention"], "stdout", ""),
        (&["scm", "check-message"], "stdout", ""),
        (
            &["git", "commit-guard"],
            "stdout",
            "meow-git commit-guard: ",
        ),
        (&["git", "push-guard"], "stdout", "meow-git push-guard: "),
        (&["record", "check"], "stderr", ""),
        (
            &["github", "project", "EPC-0001"],
            "stdout",
            "meow-github project: ",
        ),
        (&["licence", "check"], "stdout", "meow-licence check: "),
        (&["markdown", "status"], "stdout", ""),
        (&["markdown", "check"], "stdout", ""),
        (&["markdown", "bind"], "stderr", ""),
        (&["mise", "check"], "stdout", ""),
        (&["gotask", "check"], "stdout", ""),
        (&["unattended", "plan"], "stdout", ""),
    ];
    for (args, stream, prefix) in subcommands {
        let name = args.join(" ");
        let (given, plain) = match args {
            ["git", "commit-guard"] => (event(&with, "commit"), event(&without, "commit")),
            ["git", "push-guard"] => (event(&with, "push"), event(&without, "push")),
            ["scm", "check-message"] => ("fix: a subject\n".into(), "fix: a subject\n".into()),
            _ => (String::new(), String::new()),
        };
        let done = meow(&with.0, &state.0, args, &given);
        let known = meow(&without.0, &state.0, args, &plain);
        let stdout = String::from_utf8_lossy(&done.stdout).into_owned();
        let stderr = String::from_utf8_lossy(&done.stderr).into_owned();
        let (reported, other) = if stream == "stdout" {
            (&stdout, &stderr)
        } else {
            (&stderr, &stdout)
        };
        for line in [
            "profile: parsed",
            "unknown key: verbs.tset",
            "unknown key: verbs.test.cmd",
        ] {
            let expected = format!("{prefix}{line}");
            let found = reported.lines().filter(|l| *l == expected).count();
            assert_eq!(
                found, 1,
                "{name} doesn't print {expected:?} once on {stream}:\n{reported}"
            );
        }
        for key in ["verbs.tset", "verbs.test.cmd"] {
            let named = reported.lines().filter(|l| l.contains(key)).count();
            assert_eq!(named, 1, "{name} names {key} more than once:\n{reported}");
        }
        assert!(
            !other
                .lines()
                .any(|l| l.contains("profile: ") || l.contains("unknown key:")),
            "{name} reports the profile on the wrong stream as well:\n{other}"
        );
        assert_eq!(
            done.status.code(),
            known.status.code(),
            "{name} exits differently with the unknown keys:\n{stdout}{stderr}"
        );
    }
}
