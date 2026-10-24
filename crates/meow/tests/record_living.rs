// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The rules `paw check` holds living documents and withdrawals to, and how a
//! task's state is read from the task (TSK-4750 and SPC-1230, TSK-4770 and
//! SPC-1070 "The layout", TSK-4780 and SPC-1090 "The gate").

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
            std::env::temp_dir().join(format!("meow-living-{name}-{}-{stamp}", std::process::id()));
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

/// A repository with an empty record under `project/` and the given files.
fn repo(name: &str, files: &[(&str, &str)]) -> Dir {
    let dir = Dir::new(name);
    write(
        &dir.0,
        ".meowpaw/profile.toml",
        "[record]\nroot = \"project\"\n",
    );
    for (path, text) in files {
        write(&dir.0.join("project"), path, text);
    }
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

/// What `paw check` printed, and whether it reported anything.
fn check(dir: &Path) -> (String, Option<i32>) {
    let output = paw(dir, &["check"]);
    (stdout(&output), output.status.code())
}

fn vision(body: &str) -> String {
    format!("---\nid: vision\nartifact: vision\nstatus: live\nrevised: 2026-01-01\n---\n\n{body}")
}

const SECTIONS: [&str; 4] = [
    "Who it is for",
    "Quality goals",
    "What it will not do",
    "Risks",
];

fn full_vision(extra: &str) -> String {
    let mut body = String::from("# V\n\n");
    for section in SECTIONS {
        body.push_str(&format!("## {section}\n\nText.\n\n"));
    }
    body.push_str(extra);
    vision(&body)
}

/// Criterion 1 of TSK-4750 (REQ-0616, REQ-0618, REQ-0620): each required
/// section is reported when missing, naming the section.
#[test]
fn a_vision_missing_a_section_is_reported_naming_it() {
    for missing in SECTIONS {
        let mut body = String::from("# V\n\n");
        for section in SECTIONS.iter().filter(|s| **s != missing) {
            body.push_str(&format!("## {section}\n\nText.\n\n"));
        }
        let dir = repo("section", &[("vision.md", &vision(&body))]);
        let (out, _) = check(&dir.0);
        assert!(
            out.contains(&format!(
                "project/vision.md: has no {missing} section, which a vision carries"
            )),
            "{missing}: {out}"
        );
    }
    let dir = repo("whole", &[("vision.md", &full_vision(""))]);
    assert!(!check(&dir.0).0.contains("project/vision.md"));
}

/// Criterion 2 of TSK-4750 (REQ-2856): a date in the body is reported, each
/// form with its line, and the front matter's `revised` passes.
#[test]
fn a_vision_carrying_a_date_is_reported_with_its_line() {
    let extra = "On 2027-01-01 it ships.\nIn March 2027 it grows.\nBy Q3 2027 it ends.\n";
    let dir = repo("date", &[("vision.md", &full_vision(extra))]);
    let (out, _) = check(&dir.0);
    let first = 26; // the first line after the four sections
    for (i, form) in ["2027-01-01", "March 2027", "Q3 2027"].iter().enumerate() {
        let line = format!("project/vision.md:{}: carries the date {form}", first + i);
        assert!(out.contains(&line), "{line}\n{out}");
    }
    let dir = repo("revised", &[("vision.md", &full_vision(""))]);
    assert!(!check(&dir.0).0.contains("carries the date"));
}

/// Criterion 3 of TSK-4750 (REQ-2857): a requirement stated as an obligation.
#[test]
fn a_vision_stating_a_requirement_is_reported() {
    let dir = repo(
        "obligation",
        &[(
            "vision.md",
            &full_vision("The harness MUST log every run (REQ-0010).\n"),
        )],
    );
    let (out, _) = check(&dir.0);
    assert!(
        out.contains("states REQ-0010 as an obligation, and a vision restates no requirement"),
        "{out}"
    );
    let dir = repo(
        "cited",
        &[(
            "vision.md",
            &full_vision("Logging is described in REQ-0010.\n"),
        )],
    );
    assert!(!check(&dir.0).0.contains("as an obligation"));
}

/// Criterion 4 of TSK-4750 (REQ-0611): 2,001 words are reported with the
/// count, 2,000 are not, and fenced code is not counted.
#[test]
fn a_vision_over_two_thousand_words_is_reported_with_its_count() {
    let make = |words: usize, fenced: usize| {
        let head = full_vision("");
        let body = head.split_once("\n---\n\n").unwrap().1.to_string();
        let have = body.split_whitespace().count();
        let mut text = vision(&body);
        text.push_str(&"word ".repeat(words - have));
        if fenced > 0 {
            text.push_str(&format!("\n```text\n{}\n```\n", "code ".repeat(fenced)));
        }
        text
    };
    let dir = repo("long", &[("vision.md", &make(2001, 0))]);
    let (out, _) = check(&dir.0);
    assert!(
        out.contains("runs to 2001 words, over the 2000 a vision runs to"),
        "{out}"
    );
    let dir = repo("exact", &[("vision.md", &make(2000, 500))]);
    assert!(!check(&dir.0).0.contains("words, over"));
}

/// Criterion 5 of TSK-4750 (REQ-0614): a second vision under any directory.
#[test]
fn a_second_vision_is_reported_naming_both_files() {
    let dir = repo(
        "twice",
        &[
            ("vision.md", &full_vision("")),
            ("notes/vision.md", &full_vision("")),
        ],
    );
    let (out, _) = check(&dir.0);
    assert!(
        out.contains("vision is also allocated to project/vision.md")
            || out.contains("vision is also allocated to project/notes/vision.md"),
        "{out}"
    );
}

fn requirement(status: &str, body: &str) -> String {
    format!(
        "---\nid: REQ-0001\nartifact: requirement\ntopic: a\nclass: functional\nstatus: {status}\nrevised: 2026-01-01\nverification: static\n---\n\n# REQ-0001\n\n{body}\n"
    )
}

/// Criterion 1 of TSK-4770 (REQ-0610): a requirement stores no `live`, and an
/// index file in a kind's directory may.
#[test]
fn a_live_requirement_fails_and_a_live_index_passes() {
    let dir = repo(
        "live",
        &[
            (
                "requirements/REQ-0001-a.md",
                &requirement("live", "The harness MUST work."),
            ),
            (
                "requirements/README.md",
                "---\nid: index\nartifact: index\nstatus: live\nrevised: 2026-01-01\n---\n\n# Index\n",
            ),
        ],
    );
    let (out, code) = check(&dir.0);
    assert!(
        out.contains("project/requirements/REQ-0001-a.md:")
            && out.contains("status live is not one a requirement stores"),
        "{out}"
    );
    assert_eq!(code, Some(1));
    assert_eq!(out.matches("is not one a").count(), 1, "{out}");
}

fn spec(body: &str) -> String {
    format!(
        "---\nid: SPC-0001\nartifact: spec\nstatus: live\nrevised: 2026-01-01\nstates: [REQ-0001]\n---\n\n# A part\n\n## Scope\n\nText.\n\n## Boundary\n\nText.\n\n## Behaviour\n\n{body}\n\n## Failure paths\n\nText.\n"
    )
}

/// Criterion 2 of TSK-4770 (REQ-0612, REQ-0632): struck text, a tombstone
/// heading and a sentence naming an earlier version, each with its line.
#[test]
fn a_specification_carrying_history_fails_naming_the_line() {
    // Line 21 is the first line under Behaviour.
    let cases = [
        ("~~Old rule.~~", "carries struck text"),
        (
            "### Withdrawn requirements",
            "carries the heading Withdrawn requirements",
        ),
        (
            "This previously read the profile twice.",
            "says \"previously\"",
        ),
    ];
    for (body, message) in cases {
        let dir = repo("history", &[("specs/SPC-0001-a.md", &spec(body))]);
        let (out, _) = check(&dir.0);
        let expected = format!("project/specs/SPC-0001-a.md:21: {message}");
        assert!(out.contains(&expected), "{expected}\n{out}");
    }
    let dir = repo(
        "present",
        &[("specs/SPC-0001-a.md", &spec("It reads the profile once."))],
    );
    let (out, _) = check(&dir.0);
    assert!(!out.contains("SPC-0001-a.md:21"), "{out}");
}

fn withdrawn(first: &str) -> String {
    requirement("withdrawn", first)
}

/// Criterion 3 of TSK-4770 (REQ-0628): a withdrawal opens with a line naming
/// the record that withdrew it.
#[test]
fn a_withdrawal_naming_nothing_fails() {
    let dir = repo(
        "withdrawn",
        &[(
            "requirements/REQ-0001-a.md",
            &withdrawn("No longer needed."),
        )],
    );
    let (out, _) = check(&dir.0);
    assert!(
        out.contains("project/requirements/REQ-0001-a.md:13: is withdrawn and its first line names no record that withdrew it"),
        "{out}"
    );
    let dir = repo(
        "named",
        &[(
            "requirements/REQ-0001-a.md",
            &withdrawn("**Withdrawn by ADR-1800. Replaced by REQ-3320.**"),
        )],
    );
    assert!(!check(&dir.0).0.contains("first line names no record"));
}

fn epic(status: &str, entry: &str) -> String {
    format!(
        "---\nid: EPC-0001\nartifact: epic\nstatus: {status}\nrevised: 2026-01-01\nrealises: ADR-0001\n---\n\n# A plan\n\n## Acceptance criteria\n\nText.\n\n## Tasks\n\n{entry}\n      closes: REQ-0001\n\n## Coverage\n\nText.\n\n## Not covered\n\nText.\n"
    )
}

/// Criterion 1 of TSK-4780 (REQ-2897): a draft epic carries no mark per task,
/// and an approved one may.
#[test]
fn a_draft_epic_with_a_status_per_task_fails() {
    let marked = "- [ ] T-001 TSK-0001 build it";
    let dir = repo(
        "draft-marked",
        &[("epics/EPC-0001-a.md", &epic("draft", marked))],
    );
    let (out, _) = check(&dir.0);
    assert!(
        out.contains("project/epics/EPC-0001-a.md:17: marks a task with a checkbox, where an epic carries no status per task"),
        "{out}"
    );
    let dir = repo(
        "draft-plain",
        &[(
            "epics/EPC-0001-a.md",
            &epic("draft", "- T-001 TSK-0001 build it"),
        )],
    );
    assert!(!check(&dir.0).0.contains("carries no status per task"));
    let dir = repo(
        "approved-marked",
        &[("epics/EPC-0001-a.md", &epic("approved", marked))],
    );
    assert!(!check(&dir.0).0.contains("carries no status per task"));
}

fn task(id: &str, status: &str, evidence: &str, depends: &str) -> String {
    format!(
        "---\nid: {id}\nartifact: task\nstatus: {status}\nrevised: 2026-01-01\nepic: EPC-0001\ncloses: [REQ-0001]\n---\n\n# A task\n\n## What to do\n\nText.\n\n## Depends on\n\n{depends}\n\n## Evidence\n\n{evidence}\n\n## Left alone\n\nText.\n"
    )
}

fn record_with(entry_one: &str, first: &str, epic_status: &str) -> Dir {
    let entries = format!("{entry_one}\n      closes: REQ-0001\n- T-002 TSK-0002 second");
    repo(
        "derive",
        &[
            (
                "requirements/REQ-0001-a.md",
                &requirement("approved", "The harness MUST work."),
            ),
            (
                "adrs/ADR-0001-a.md",
                "---\nid: ADR-0001\nartifact: adr\nstatus: approved\nrevised: 2026-01-01\naddresses: [REQ-0001]\n---\n\n# 1. A\n\n## Decision\n\nText.\n",
            ),
            ("epics/EPC-0001-a.md", &epic(epic_status, &entries)),
            ("tasks/TSK-0001-a.md", first),
            (
                "tasks/TSK-0002-b.md",
                &task("TSK-0002", "approved", "Not yet.", "- TSK-0001 (blocking)"),
            ),
        ],
    )
}

fn ready(dir: &Path) -> Option<i32> {
    paw(dir, &["ready", "implement", "TSK-0002"]).status.code()
}

/// Criterion 2 of TSK-4780: an unmarked entry reads as done once the task's
/// Evidence is written, and as dropped once the task is withdrawn.
#[test]
fn an_unmarked_task_is_done_from_its_evidence_and_dropped_from_its_status() {
    let entry = "- T-001 TSK-0001 first";
    let written = task("TSK-0001", "approved", "Tests close it.", "Nothing.");
    assert_eq!(ready(&record_with(entry, &written, "approved").0), Some(0));
    let open = task("TSK-0001", "approved", "Not yet.", "Nothing.");
    assert_eq!(ready(&record_with(entry, &open, "approved").0), Some(1));
    let dropped = task("TSK-0001", "withdrawn", "Not yet.", "Nothing.");
    assert_eq!(ready(&record_with(entry, &dropped, "approved").0), Some(0));
}

/// Criterion 3 of TSK-4780: in an approved epic with marks, `[x]` and `[~]`
/// still decide, whatever the Evidence says.
#[test]
fn a_marked_task_keeps_the_state_its_mark_gives() {
    let open = task("TSK-0001", "approved", "Not yet.", "Nothing.");
    assert_eq!(
        ready(&record_with("- [x] T-001 TSK-0001 first", &open, "approved").0),
        Some(0)
    );
    assert_eq!(
        ready(&record_with("- [~] T-001 TSK-0001 first", &open, "approved").0),
        Some(0)
    );
    assert_eq!(
        ready(&record_with("- [ ] T-001 TSK-0001 first", &open, "approved").0),
        Some(1)
    );
}
