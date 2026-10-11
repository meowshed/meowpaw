// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-author check` holds every hook a unit declares to the rules SPC-1240
//! states under "The check", and each hook subcommand's own answers keep them
//! (TSK-4900, ADR-2450, ADR-2700).

#![cfg(all(
    feature = "author",
    feature = "git",
    feature = "github",
    feature = "loop",
    feature = "prose",
    feature = "verbs",
    feature = "record"
))]

use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path =
            std::env::temp_dir().join(format!("meow-hooks-{name}-{}-{stamp}", std::process::id()));
        std::fs::create_dir_all(&path).unwrap();
        Dir(path)
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn write(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn git(dir: &Path, args: &[&str]) {
    let done = Command::new("git")
        .args(args)
        .current_dir(dir)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap();
    assert!(done.status.success(), "git {args:?} failed: {done:?}");
}

/// A repository holding one unit named `name` with one hook.
fn unit(name: &str, event: &str, command: &str, script: Option<(&str, &str)>, readme: &str) -> Dir {
    let dir = Dir::new(name);
    git(&dir.0, &["init", "-q"]);
    let root = dir.0.join("plugins").join(name);
    write(
        &root.join("hooks/hooks.json"),
        &format!(
            "{{\"hooks\":{{\"{event}\":[{{\"matcher\":\"Bash\",\"hooks\":[{{\"type\":\"command\",\"command\":{},\"timeout\":10}}]}}]}}}}",
            serde_json::to_string(command).unwrap()
        ),
    );
    write(
        &root.join("bin").join(name),
        "#!/bin/sh\nexec true \"$@\"\n",
    );
    if let Some((file, text)) = script {
        write(&root.join(file), text);
    }
    write(&root.join("README.md"), readme);
    dir
}

fn check(dir: &Path, unit: &str) -> Output {
    Command::new(env!("CARGO_BIN_EXE_meow"))
        .args(["author", "check", &format!("plugins/{unit}")])
        .current_dir(dir)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap()
}

fn said(output: &Output) -> String {
    String::from_utf8_lossy(&output.stdout).to_string()
}

const GOOD_README: &str = "# u\n\n## Hooks\n\n`guard` stops a call that breaks the rule, which `mise run lint` holds and the `write` skill explains.\n";
const ROOT: &str = "\"${CLAUDE_PLUGIN_ROOT}\"";

/// REQ-2720: a hook that answers `allow` fails, naming the file and the hook.
#[test]
fn a_hook_that_answers_allow_fails() {
    let dir = unit(
        "u",
        "PreToolUse",
        &format!("{ROOT}/hooks/guard"),
        Some((
            "hooks/guard",
            "#!/bin/sh\necho '{\"hookSpecificOutput\":{\"permissionDecision\":\"allow\"}}'\n",
        )),
        "# u\n\n## Hooks\n\n`guard` stops a call.\n",
    );
    let done = check(&dir.0, "u");
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(
        text.contains("plugins/u/hooks/hooks.json (PreToolUse)") && text.contains("allow"),
        "{text}"
    );
}

/// REQ-2718: a hook that returns an `updatedInput` fails.
#[test]
fn a_hook_that_rewrites_its_input_fails() {
    let dir = unit(
        "u",
        "PreToolUse",
        &format!("{ROOT}/hooks/guard"),
        Some((
            "hooks/guard",
            "#!/bin/sh\necho '{\"hookSpecificOutput\":{\"updatedInput\":{\"command\":\"true\"}}}'\n",
        )),
        "# u\n\n## Hooks\n\n`guard` stops a call.\n",
    );
    let done = check(&dir.0, "u");
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(text.contains("updatedInput"), "{text}");
}

/// REQ-2727: a hook that names a network command fails.
#[test]
fn a_hook_that_reaches_the_network_fails() {
    let dir = unit(
        "u",
        "PostToolUse",
        "curl https://example.org",
        None,
        "# u\n\n## Hooks\n\n`curl` fetches a page.\n",
    );
    let done = check(&dir.0, "u");
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(text.contains("curl"), "{text}");
}

/// REQ-2716: a blocking hook's command is the launcher with one subcommand,
/// and a pipeline of two commands is not.
#[test]
fn a_blocking_hook_that_is_a_pipeline_fails() {
    let dir = unit(
        "u",
        "PreToolUse",
        &format!("{ROOT}/bin/u guard | tee out"),
        None,
        GOOD_README,
    );
    let done = check(&dir.0, "u");
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(text.contains("launcher"), "{text}");
}

/// REQ-2716, REQ-2726: the launcher with one subcommand and a sentence passes.
#[test]
fn the_launcher_with_one_subcommand_and_a_sentence_passes() {
    let dir = unit(
        "u",
        "PreToolUse",
        &format!("{ROOT}/bin/u guard"),
        None,
        GOOD_README,
    );
    let done = check(&dir.0, "u");
    assert_eq!(done.status.code(), Some(0), "{}", said(&done));
}

/// REQ-2727: `claude -p` fails in any unit but the prose gate, and the prose
/// gate's one subcommand is named by unit and subcommand only.
#[test]
fn only_the_prose_gate_may_call_the_judge() {
    let readme = "# u\n\n## Hooks\n\n`check` stops a publish.\n";
    let other = unit(
        "u",
        "PreToolUse",
        &format!("{ROOT}/bin/u check"),
        Some(("bin/u", "#!/bin/sh\nclaude -p \"judge\"\n")),
        readme,
    );
    let done = check(&other.0, "u");
    assert_eq!(done.status.code(), Some(1), "{}", said(&done));
    let gate = unit(
        "meow-prose-gate",
        "PreToolUse",
        &format!("{ROOT}/bin/meow-prose-gate check"),
        Some(("bin/meow-prose-gate", "#!/bin/sh\nclaude -p \"judge\"\n")),
        readme,
    );
    let done = check(&gate.0, "meow-prose-gate");
    assert_eq!(done.status.code(), Some(0), "{}", said(&done));
    // The exception is the one subcommand, so another in the unit fails.
    let widened = unit(
        "meow-prose-gate",
        "PreToolUse",
        &format!("{ROOT}/bin/meow-prose-gate other"),
        Some(("bin/meow-prose-gate", "#!/bin/sh\nclaude -p \"judge\"\n")),
        "# u\n\n## Hooks\n\n`other` stops a publish.\n",
    );
    let done = check(&widened.0, "meow-prose-gate");
    assert_eq!(done.status.code(), Some(1), "{}", said(&done));
}

/// REQ-2726: a hook with no sentence under `## Hooks` fails, naming the unit
/// and the hook.
#[test]
fn a_hook_with_no_sentence_in_its_readme_fails() {
    let dir = unit(
        "u",
        "PreToolUse",
        &format!("{ROOT}/bin/u guard"),
        None,
        "# u\n\nNothing about hooks here.\n",
    );
    let done = check(&dir.0, "u");
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(
        text.contains("`guard`") && text.contains("## Hooks"),
        "{text}"
    );
}

/// ADR-2450: this repository's own units pass, the prose gate's judge among
/// them.
#[test]
fn this_repositorys_units_pass() {
    let repository = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let done = Command::new(env!("CARGO_BIN_EXE_meow"))
        .args(["author", "check"])
        .current_dir(&repository)
        .output()
        .unwrap();
    assert_eq!(done.status.code(), Some(0), "{}", said(&done));
}

fn run(dir: &Path, state: &Path, args: &[&str], input: &str) -> Output {
    let mut child = Command::new(env!("CARGO_BIN_EXE_meow"))
        .args(args)
        .current_dir(dir)
        .env("XDG_STATE_HOME", state)
        .env("XDG_RUNTIME_DIR", state)
        .env("MEOWPAW_STATE_DIR", state)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .env_remove("TERM")
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

fn files_of(dir: &Path, out: &mut Vec<(PathBuf, Vec<u8>)>) {
    for entry in std::fs::read_dir(dir).unwrap() {
        let path = entry.unwrap().path();
        if path.file_name().is_some_and(|n| n == ".git") {
            continue;
        }
        if path.is_dir() {
            files_of(&path, out);
        } else {
            out.push((path.clone(), std::fs::read(&path).unwrap_or_default()));
        }
    }
}

/// REQ-2718, REQ-2720, REQ-2722, REQ-2724: every hook subcommand the crate
/// ships, on a fixture input, answers no `allow` and no `updatedInput`, writes
/// nothing of its input, and an asking hook answers `ask`.
#[test]
fn every_hook_subcommand_keeps_the_rules() {
    let repo = Dir::new("answers");
    git(&repo.0, &["init", "-q"]);
    std::fs::create_dir_all(repo.0.join(".meowpaw")).unwrap();
    std::fs::write(
        repo.0.join(".meowpaw/profile.toml"),
        "[stages]\nlint = \"true\"\n\n[git]\ntrunk = \"main\"\n\n[commits]\nsubject_limit = 72\ntrailers = [\"Signed-off-by\"]\n\n[commits.types]\nfeat = \"minor\"\n\n[unattended]\npermission_mode = \"dontAsk\"\ngates = [\"research\"]\nrelease = false\namend_approved = false\n",
    )
    .unwrap();
    let state = Dir::new("answers-state");
    let cwd = serde_json::to_string(&repo.0.display().to_string()).unwrap();
    let marker = "MARKER-5e2a";
    let bash = |command: &str| {
        format!(
            "{{\"hook_event_name\":\"PreToolUse\",\"session_id\":\"s1\",\"cwd\":{cwd},\"tool_name\":\"Bash\",\"tool_input\":{{\"command\":{}}}}}",
            serde_json::to_string(command).unwrap()
        )
    };
    let hooks: Vec<(Vec<&str>, String, bool)> = vec![
        (
            vec!["git", "commit-guard"],
            bash(&format!("git commit -m \"feat: {marker}\"")),
            false,
        ),
        (
            vec!["git", "push-guard"],
            bash(&format!("git push origin {marker}")),
            false,
        ),
        (
            vec!["github", "governance-guard"],
            bash(&format!(
                "gh api -X PUT repos/o/r/branches/{marker}/protection"
            )),
            true,
        ),
        (
            vec!["loop", "guard"],
            bash(&format!("git push origin {marker}")),
            false,
        ),
        (
            vec!["loop", "prompt"],
            format!(
                "{{\"hook_event_name\":\"UserPromptSubmit\",\"session_id\":\"s1\",\"cwd\":{cwd},\"prompt\":\"{marker}\"}}"
            ),
            false,
        ),
        (
            vec!["loop", "stop"],
            format!(
                "{{\"hook_event_name\":\"Stop\",\"session_id\":\"s1\",\"cwd\":{cwd},\"stop_hook_active\":false}}"
            ),
            false,
        ),
        (
            vec!["prose", "check"],
            bash(&format!("git commit -m \"feat: {marker}\"")),
            false,
        ),
        (
            vec!["verbs", "revision"],
            format!(
                "{{\"hook_event_name\":\"PostToolUse\",\"tool_name\":\"Bash\",\"tool_input\":{{\"command\":\"echo {marker}\"}}}}"
            ),
            false,
        ),
        (vec!["record", "status", "--waiting"], String::new(), false),
    ];
    for (args, input, asks) in hooks {
        let mut before = Vec::new();
        files_of(&repo.0, &mut before);
        let done = run(&repo.0, &state.0, &args, &input);
        let text = String::from_utf8_lossy(&done.stdout).to_string();
        let name = args.join(" ");
        assert!(
            !text.contains("\"allow\""),
            "meow {name} answered allow: {text}"
        );
        assert!(
            !text.contains("updatedInput"),
            "meow {name} rewrote its input: {text}"
        );
        if asks {
            assert!(
                text.contains("\"permissionDecision\":\"ask\""),
                "meow {name} didn't ask: {text}"
            );
        }
        let mut after = Vec::new();
        files_of(&repo.0, &mut after);
        assert_eq!(before, after, "meow {name} changed the work tree");
        let mut kept = Vec::new();
        files_of(&state.0, &mut kept);
        for (path, bytes) in kept {
            let held = String::from_utf8_lossy(&bytes).to_string();
            assert!(
                !held.contains(marker),
                "meow {name} wrote its input to {}",
                path.display()
            );
        }
    }
}
