// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-author check` fails a tool an agent or a skill grants that no step
//! is named for in its unit's README (TSK-4920, REQ-1430, REQ-1432, SPC-1030
//! "What a unit declares").

#![cfg(feature = "author")]

use std::path::{Path, PathBuf};
use std::process::{Command, Output};

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
            "meow-tools-{name}-{}-{stamp}-{count}",
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

fn write(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

const AGENT: &str = "---\nname: reader\ndescription: Reads a file and reports what it holds, when a person asks for a summary.\nmaxTurns: 4\ntools: [Read, Grep]\nmodel: sonnet\neffort: low\nomitClaudeMd: true\nskills: []\n---\n\n<role>\nYou read one file and report what it holds.\n</role>\n\n<steps name=\"read\">\n1. Read the file named, and stop once you have reported.\n</steps>\n\n<rules name=\"outcome\">\n- O1. Write `outcome:` and one of DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT or BLOCKED.\n</rules>\n";

fn skill(allowed: &str) -> String {
    format!(
        "---\nname: act\ndescription: Acts on a request, when a person asks for it by name.\nallowed-tools: {allowed}\n---\n\n<role>\nYou act on one request.\n</role>\n\n<steps name=\"act\">\n1. Do the work, and stop at the report.\n</steps>\n"
    )
}

/// A repository with one unit `u`, its README's text and its files.
fn unit(readme: &str, files: &[(&str, String)]) -> Dir {
    let dir = Dir::new("u");
    let status = Command::new("git")
        .args(["init", "-q", "--template="])
        .current_dir(&dir.0)
        .status()
        .unwrap();
    assert!(status.success());
    let root = dir.0.join("plugins/u");
    write(&root.join("README.md"), readme);
    for (name, text) in files {
        write(&root.join(name), text);
    }
    dir
}

fn check(dir: &Path) -> Output {
    Command::new(env!("CARGO_BIN_EXE_meow"))
        .args(["author", "check", "plugins/u"])
        .current_dir(dir)
        .output()
        .unwrap()
}

fn said(output: &Output) -> String {
    String::from_utf8_lossy(&output.stdout).to_string()
}

/// REQ-1432: an agent's tool with no step beside it in the README fails,
/// naming the unit, the tool and the agent.
#[test]
fn a_tool_with_no_step_fails_naming_the_unit_the_tool_and_the_agent() {
    let dir = unit(
        "# u\n\n## Tools\n\n- `Read`: the reader opens the one file it was asked about.\n",
        &[("agents/reader.md", AGENT.to_string())],
    );
    let done = check(&dir.0);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(
        text.contains("plugins/u/agents/reader.md")
            && text.contains("`Grep`")
            && text.contains("plugins/u/README.md"),
        "{text}"
    );
    assert!(!text.contains("grants `Read`"), "{text}");
}

/// REQ-1430, REQ-1432: a skill's `allowed-tools` is held to the same rule.
#[test]
fn a_skill_tool_with_no_step_fails_naming_the_skill() {
    let dir = unit(
        "# u\n\nNothing about tools here.\n",
        &[("skills/act/SKILL.md", skill("Bash"))],
    );
    let done = check(&dir.0);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(
        text.contains("plugins/u/skills/act/SKILL.md") && text.contains("`Bash`"),
        "{text}"
    );
}

/// REQ-1430: each tool named beside a step passes, for an agent and a skill.
#[test]
fn each_tool_named_beside_a_step_passes() {
    let dir = unit(
        "# u\n\n## Tools\n\n- `Read`: the reader opens the one file it was asked about.\n- `Grep`: the reader finds the line a question names.\n- `Bash`: the act step runs the one command the request names.\n",
        &[
            ("agents/reader.md", AGENT.to_string()),
            ("skills/act/SKILL.md", skill("Bash")),
        ],
    );
    let done = check(&dir.0);
    assert_eq!(done.status.code(), Some(0), "{}", said(&done));
}

/// The string form of `tools`, and a pattern a skill grants, are read as the
/// tools they name (SPC-1030: a list or a comma-separated string).
#[test]
fn the_string_form_and_a_granted_pattern_name_their_tools() {
    let agent = AGENT.replace("tools: [Read, Grep]", "tools: Read, Grep");
    let dir = unit(
        "# u\n\n## Tools\n\n- `Read`: the reader opens the one file it was asked about.\n- `Grep`: the reader finds a line.\n- `Bash`: the act step runs one command.\n",
        &[
            ("agents/reader.md", agent),
            (
                "skills/act/SKILL.md",
                skill("Read, Bash(git status:*), Grep"),
            ),
        ],
    );
    let done = check(&dir.0);
    assert_eq!(done.status.code(), Some(0), "{}", said(&done));
    // A tool the pattern grants is named by its bare name, and one with none fails.
    let missing = unit(
        "# u\n\n## Tools\n\n- `Read`: opens a file.\n",
        &[("skills/act/SKILL.md", skill("Read, Bash(git status:*)"))],
    );
    let done = check(&missing.0);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(text.contains("grants `Bash`"), "{text}");
    assert!(!text.contains("status:*"), "{text}");
}

/// An item inside a fenced block under `## Tools` is an example, not a step.
#[test]
fn an_item_inside_a_fence_names_no_step() {
    let dir = unit(
        "# u\n\n## Tools\n\n```text\n- `Read`: an example.\n- `Grep`: an example.\n```\n",
        &[("agents/reader.md", AGENT.to_string())],
    );
    let done = check(&dir.0);
    assert_eq!(done.status.code(), Some(1), "{}", said(&done));
}

/// A line that names the tool and no step is not a step.
#[test]
fn a_tool_named_with_no_step_text_fails() {
    let dir = unit(
        "# u\n\n## Tools\n\n- `Read`:\n- `Grep`:\n",
        &[("agents/reader.md", AGENT.to_string())],
    );
    let done = check(&dir.0);
    assert_eq!(done.status.code(), Some(1), "{}", said(&done));
}

/// REQ-1430: this repository's units each name the step for each tool they
/// grant.
#[test]
fn this_repositorys_units_name_a_step_for_each_tool() {
    let repository = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let done = Command::new(env!("CARGO_BIN_EXE_meow"))
        .args(["author", "check"])
        .current_dir(&repository)
        .output()
        .unwrap();
    assert_eq!(done.status.code(), Some(0), "{}", said(&done));
}
