// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `paw brief <task>` prints the brief a delegated agent gets, built from the
//! task, its epic or decision and the requirements it closes, and never from a
//! conversation (TSK-4945, TSK-5175, SPC-1090 "Delegated work").

#![cfg(feature = "record")]

use std::path::{Path, PathBuf};
use std::process::{Command, Output};

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path =
            std::env::temp_dir().join(format!("meow-brief-{name}-{}-{stamp}", std::process::id()));
        std::fs::create_dir_all(&path).unwrap();
        Dir(path)
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn write(root: &Path, name: &str, text: &str) {
    let path = root.join(name);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// The first requirement's body: a statement over two lines, a reason in a
/// second paragraph, and a trailing space a summary would drop.
const FIRST: &str = "The harness MUST copy a constraint as it stands, \nwith every clause kept.\n\nA summary drops the clause the work turns on.";
const SECOND: &str = "The harness MUST NOT write to a file it was asked to read.";
const CRITERIA: &str = "1. Given a fixture, when it runs, then it prints\n   `exactly this` and nothing else (REQ-0001).";
const LEFT_ALONE: &str = "The other subcommands, which stay as they are.";
const TO_DO: &str = "Add the subcommand to the `record` feature.";
const DECISION: &str = "The record decides what a brief says, and nothing else does.";

fn requirement(id: &str, body: &str) -> String {
    format!(
        "---\nid: {id}\nartifact: requirement\ntopic: a\nclass: functional\nstatus: approved\nrevised: 2026-01-01\nverification: static\n---\n\n# {id}\n\n{body}\n"
    )
}

fn task(id: &str, authority: &str) -> String {
    format!(
        "---\nid: {id}\nartifact: task\nstatus: approved\nrevised: 2026-01-01\n{authority}\ncloses: [REQ-0001, REQ-0002]\n---\n\n<!-- A comment no agent needs. -->\n\n# Build the thing\n\nThe opening says what the task is for.\n\n## Acceptance criteria\n\n{CRITERIA}\n\n## What to do\n\n{TO_DO}\n\n## Depends on\n\nNothing.\n\n## Evidence\n\nNot yet.\n\n## Left alone\n\n{LEFT_ALONE}\n"
    )
}

/// A record holding an approved decision, an epic realising it with one task
/// closing two requirements, and a second task realising the decision itself.
fn fixture(name: &str) -> Dir {
    let dir = Dir::new(name);
    let root = dir.0.join("project");
    write(
        &dir.0,
        ".meowpaw/profile.toml",
        "[record]\nroot = \"project\"\n",
    );
    write(
        &root,
        "requirements/REQ-0001-copy.md",
        &requirement("REQ-0001", FIRST),
    );
    write(
        &root,
        "requirements/REQ-0002-read.md",
        &requirement("REQ-0002", SECOND),
    );
    write(
        &root,
        "specs/SPC-0001-a-part.md",
        "---\nid: SPC-0001\nartifact: spec\nstatus: live\nrevised: 2026-01-01\nstates: [REQ-0001, REQ-0002]\n---\n\n# A part\n",
    );
    write(
        &root,
        "adrs/ADR-0001-a-choice.md",
        &format!(
            "---\nid: ADR-0001\nartifact: adr\nstatus: approved\nrevised: 2026-01-01\naddresses: [REQ-0001, REQ-0002]\n---\n\n# 0001. A choice\n\n## Decision\n\n{DECISION}\n\n## Why\n\nBecause.\n"
        ),
    );
    write(
        &root,
        "epics/EPC-0001-a-plan.md",
        "---\nid: EPC-0001\nartifact: epic\nstatus: approved\nrevised: 2026-01-01\nrealises: ADR-0001\n---\n\n# A plan\n\nThe epic's opening.\n\n## Tasks\n\n- [ ] T-001 TSK-0001 build the thing, in the `record` feature\n      closes: REQ-0001, REQ-0002\n",
    );
    write(
        &root,
        "tasks/TSK-0001-build.md",
        &task("TSK-0001", "epic: EPC-0001"),
    );
    write(
        &root,
        "tasks/TSK-0002-direct.md",
        &task("TSK-0002", "realises: ADR-0001"),
    );
    dir
}

fn paw(dir: &Path, args: &[&str]) -> Output {
    let layout =
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/lib/layout.toml");
    Command::new(env!("CARGO_BIN_EXE_paw"))
        .arg("record")
        .args(args)
        .current_dir(dir)
        .env("MEOW_LAYOUT", layout)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap()
}

fn stdout(output: &Output) -> String {
    String::from_utf8_lossy(&output.stdout).into_owned()
}

/// The text under the brief's `# <name>` heading, up to the next one.
fn part<'a>(brief: &'a str, name: &str) -> &'a str {
    let heading = format!("\n# {name}\n");
    let start = brief
        .find(&heading)
        .unwrap_or_else(|| panic!("the brief has no `# {name}` heading:\n{brief}"))
        + heading.len();
    let rest = &brief[start..];
    let end = rest.find("\n# ").unwrap_or(rest.len());
    &rest[..end]
}

/// TSK-4945 criterion 1, REQ-0810, REQ-0812, REQ-0814: the brief states what
/// to build, the constraints, the interfaces and what to report back, each
/// under its own heading, and copies each constraint byte for byte from the
/// record.
#[test]
fn a_brief_states_four_parts_and_copies_each_constraint_byte_for_byte() {
    let dir = fixture("parts");
    let done = paw(&dir.0, &["brief", "TSK-0001"]);
    assert_eq!(done.status.code(), Some(0), "{done:?}");
    let brief = stdout(&done);
    let build = part(&brief, "What to build");
    assert!(
        build.contains("The opening says what the task is for."),
        "{build}"
    );
    assert!(build.contains(TO_DO), "{build}");
    let constraints = part(&brief, "Constraints");
    for copied in [FIRST, SECOND, CRITERIA, LEFT_ALONE] {
        assert!(
            constraints.contains(copied),
            "the constraints don't hold {copied:?} byte for byte:\n{constraints}"
        );
    }
    let interfaces = part(&brief, "Interfaces");
    assert!(
        interfaces.contains("- [ ] T-001 TSK-0001 build the thing, in the `record` feature"),
        "{interfaces}"
    );
    assert!(interfaces.contains("SPC-0001"), "{interfaces}");
    let report = part(&brief, "Report back");
    for outcome in ["DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED"] {
        assert!(report.contains(outcome), "{report}");
    }
    // REQ-0810: the brief carries what the record says and nothing a
    // conversation could add, so it is the same on every run.
    assert_eq!(stdout(&paw(&dir.0, &["brief", "TSK-0001"])), brief);
    assert!(!brief.contains("A comment no agent needs."), "{brief}");
}

/// TSK-4945 criterion 2: a task realising a decision has the decision read in
/// the epic's place.
#[test]
fn a_task_realising_a_decision_reads_the_decision_in_the_epics_place() {
    let dir = fixture("decision");
    let done = paw(&dir.0, &["brief", "TSK-0002"]);
    assert_eq!(done.status.code(), Some(0), "{done:?}");
    let brief = stdout(&done);
    assert!(part(&brief, "What to build").contains(DECISION), "{brief}");
    assert!(!brief.contains("The epic's opening."), "{brief}");
    assert!(
        brief.lines().nth(1).is_some_and(|l| l.contains("ADR-0001")),
        "{brief}"
    );
}

/// TSK-4945 criterion 3, TSK-5175, REQ-1764: the first line names the agent
/// definition the brief is written for, the one `--agent` gives or the one the
/// implement step dispatches without it, and names no model or vendor.
#[test]
fn the_first_line_names_the_agent_the_brief_is_written_for() {
    let dir = fixture("agent");
    let named = paw(
        &dir.0,
        &["brief", "TSK-0001", "--agent", "meow-flow:router"],
    );
    assert_eq!(named.status.code(), Some(0), "{named:?}");
    assert_eq!(
        stdout(&named).lines().next(),
        Some("agent: meow-flow:router")
    );
    let default = paw(&dir.0, &["brief", "TSK-0001"]);
    assert_eq!(
        stdout(&default).lines().next(),
        Some("agent: general-purpose")
    );
    let help = stdout(&paw(&dir.0, &["brief", "--help"]));
    assert!(
        help.contains("general-purpose"),
        "the help states no default: {help}"
    );
    for text in [stdout(&named), stdout(&default)] {
        let lower = text.to_lowercase();
        for word in [
            "claude",
            "anthropic",
            "opus",
            "sonnet",
            "haiku",
            "co-authored-by",
        ] {
            assert!(!lower.contains(word), "the brief names {word}:\n{text}");
        }
    }
}

/// TSK-4945 criterion 4: an identifier that resolves to no task exits 1,
/// naming it, and prints no brief.
#[test]
fn an_unresolved_task_exits_1_and_prints_no_brief() {
    let dir = fixture("unresolved");
    for id in ["TSK-9999", "REQ-0001"] {
        let done = paw(&dir.0, &["brief", id]);
        assert_eq!(done.status.code(), Some(1), "{done:?}");
        let out = stdout(&done);
        assert!(out.contains(id), "{out}");
        assert!(!out.contains("# What to build"), "{out}");
        assert!(!out.starts_with("agent:"), "{out}");
    }
    let usage = paw(&dir.0, &["brief"]);
    assert_eq!(usage.status.code(), Some(2), "{usage:?}");
}

/// TSK-5175, REQ-1764, REQ-1294, ADR-2730: the brief tells the delegated
/// agent that its pull request names the task and the command that prints the
/// brief, and names no agent, model or vendor.
#[test]
fn the_brief_asks_the_pull_request_for_the_task_and_the_brief_command() {
    let dir = fixture("pull-request");
    let brief = stdout(&paw(
        &dir.0,
        &["brief", "TSK-0001", "--agent", "meow-flow:researcher"],
    ));
    let report = part(&brief, "Report back")
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ");
    assert!(
        report.contains("pull request carrying this work names the task, TSK-0001, and the command that prints this brief, `paw brief TSK-0001`"),
        "{report}"
    );
    assert!(
        report.contains("names no agent, model or vendor"),
        "{report}"
    );
    assert_eq!(brief.lines().next(), Some("agent: meow-flow:researcher"));
}
