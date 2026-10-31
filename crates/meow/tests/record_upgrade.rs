// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The record's unit of work and the upgrade to it (ADR-3090; SPC-1070
//! "The upgrade").

#![cfg(feature = "record")]

use std::path::{Path, PathBuf};
use std::process::{Command, Output};

struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "meow-upgrade-{name}-{}-{stamp}",
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

fn write(root: &Path, name: &str, text: &str) {
    let path = root.join(name);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn read(root: &Path, name: &str) -> String {
    std::fs::read_to_string(root.join(name)).unwrap()
}

fn paw(dir: &Path, args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_paw"))
        .arg("record")
        .args(args)
        .current_dir(dir)
        .env(
            "MEOW_LAYOUT",
            Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/lib/layout.toml"),
        )
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap()
}

fn said(output: &Output) -> String {
    format!(
        "{}{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    )
}

fn decision(id: &str, status: &str) -> String {
    format!(
        "---\nid: {id}\nartifact: adr\nstatus: {status}\nrevised: 2026-01-01\naddresses: []\nsupersedes: []\n---\n\n# {id}\n\n## Decision\n\nDecided.\n"
    )
}

fn task(id: &str, status: &str, authority: &str, evidence: &str) -> String {
    format!(
        "---\nid: {id}\nartifact: task\nstatus: {status}\nrevised: 2026-01-01\n{authority}\ncloses: []\nissue: 7\n---\n\n# Work {id}\n\n## What to do\n\nDo it.\n\n## Depends on\n\nNothing.\n\n## Evidence\n\n{evidence}\n\n## Left alone\n\nNothing.\n"
    )
}

fn epic(id: &str, realises: &str, entries: &str) -> String {
    format!(
        "---\nid: {id}\nartifact: epic\nstatus: approved\nrevised: 2026-01-01\nrealises: {realises}\n---\n\n# {id}\n\n## Tasks\n\n{entries}\n"
    )
}

fn defect(id: &str, tasks: &str, closed_by: &str) -> String {
    format!(
        "---\nid: {id}\nartifact: bug\nstatus: approved\nseverity: minor\nfound: 2026-01-01\nrevised: 2026-01-01\n---\n\n# {id}\n\n## Closed by\n\n{closed_by}\n\n## Tasks\n\n{tasks}\n"
    )
}

/// A record in the old form: finished work, open work under a live decision
/// and a live defect, and an open task under a decision that is already done.
fn old_form(root: &Path) {
    write(
        root,
        ".meowpaw/profile.toml",
        "[record]\nroot = \"project\"\n\n# The gates a run decides.\n[unattended]\ngates = [\"design\", \"spec\", \"epic\", \"implement\"]\n",
    );
    write(
        root,
        "project/adrs/ADR-0001-open.md",
        &decision("ADR-0001", "approved"),
    );
    write(
        root,
        "project/adrs/ADR-0002-gone.md",
        &decision("ADR-0002", "done"),
    );
    write(
        root,
        "project/adrs/ADR-0003-finished.md",
        &decision("ADR-0003", "approved"),
    );
    write(
        root,
        "project/epics/EPC-0001-open.md",
        &epic(
            "EPC-0001",
            "ADR-0001",
            "- T-001 TSK-0001 done\n- T-002 TSK-0002 open",
        ),
    );
    write(
        root,
        "project/epics/EPC-0002-finished.md",
        &epic("EPC-0002", "ADR-0003", "- [x] T-001 TSK-0006 done"),
    );
    write(
        root,
        "project/tasks/TSK-0001-a.md",
        &task("TSK-0001", "done", "epic: EPC-0001", "Pull request 1."),
    );
    write(
        root,
        "project/tasks/TSK-0002-b.md",
        &task("TSK-0002", "approved", "epic: EPC-0001", "Not yet."),
    );
    write(
        root,
        "project/tasks/TSK-0003-c.md",
        &task("TSK-0003", "approved", "realises: ADR-0002", "Not yet."),
    );
    write(
        root,
        "project/tasks/TSK-0004-d.md",
        &task("TSK-0004", "done", "bug: BUG-0001", "Pull request 2."),
    );
    write(
        root,
        "project/tasks/TSK-0005-e.md",
        &task("TSK-0005", "approved", "bug: BUG-0002", "Not yet."),
    );
    write(
        root,
        "project/tasks/TSK-0006-f.md",
        &task("TSK-0006", "done", "epic: EPC-0002", "Pull request 3."),
    );
    write(
        root,
        "project/bugs/BUG-0001-closed.md",
        &defect("BUG-0001", "- [x] T-001 TSK-0004", "A regression test."),
    );
    write(
        root,
        "project/bugs/BUG-0002-open.md",
        &defect("BUG-0002", "- [ ] T-001 TSK-0005", "Not closed."),
    );
    write(
        root,
        "project/bugs/BUG-0003-recorded.md",
        &defect("BUG-0003", "", "The change that recorded it."),
    );
    // A task its defect still lists as open, and which was withdrawn.
    write(
        root,
        "project/tasks/TSK-0007-g.md",
        &task("TSK-0007", "withdrawn", "bug: BUG-0002", "Not yet."),
    );
    // A decision whose epic lists no tasks, because other work closed all of
    // what it addresses and the epic says so (BUG-1250).
    write(
        root,
        "project/requirements/REQ-0002-b.md",
        "---\nid: REQ-0002\nartifact: requirement\ntopic: t\nclass: functional\nstatus: approved\nrevised: 2026-01-01\nverification: static\n---\n\n# REQ-0002\n\nThe thing MUST hold.\n",
    );
    write(
        root,
        "project/adrs/ADR-0004-elsewhere.md",
        &decision("ADR-0004", "approved").replace("addresses: []", "addresses: [REQ-0002]"),
    );
    write(
        root,
        "project/epics/EPC-0003-elsewhere.md",
        &format!(
            "{}\n## Not covered\n\n- REQ-0002 was closed before this decision.\n",
            epic("EPC-0003", "ADR-0004", "None.")
        ),
    );
}

#[test]
fn a_preview_says_what_moves_and_writes_nothing() {
    let dir = Dir::new("preview");
    old_form(&dir.0);
    let output = paw(&dir.0, &["upgrade"]);
    let text = said(&output);
    assert!(output.status.success(), "{text}");
    assert!(text.contains("would archive 7 tasks and 3 epics"), "{text}");
    assert!(text.contains("TSK-0002 into ADR-0001"), "{text}");
    assert!(dir.0.join("project/tasks/TSK-0001-a.md").exists());
    assert!(!dir.0.join("project/archive").exists());
    assert!(read(&dir.0, ".meowpaw/profile.toml").contains("\"epic\""));
}

#[test]
fn the_write_archives_each_file_and_keeps_a_finished_one_as_it_was() {
    let dir = Dir::new("archive");
    old_form(&dir.0);
    let before = read(&dir.0, "project/tasks/TSK-0001-a.md");
    let output = paw(&dir.0, &["upgrade", "--write"]);
    assert!(output.status.success(), "{}", said(&output));
    assert!(!dir.0.join("project/tasks").exists());
    assert!(!dir.0.join("project/epics").exists());
    assert_eq!(read(&dir.0, "project/archive/tasks/TSK-0001-a.md"), before);
    assert!(
        dir.0
            .join("project/archive/epics/EPC-0001-open.md")
            .exists()
    );
}

#[test]
fn open_work_becomes_a_step_of_its_live_authority() {
    let dir = Dir::new("fold");
    old_form(&dir.0);
    paw(&dir.0, &["upgrade", "--write"]);
    let adr = read(&dir.0, "project/adrs/ADR-0001-open.md");
    assert!(adr.contains("## Plan"), "{adr}");
    assert!(adr.contains("1. Work TSK-0002"), "{adr}");
    assert!(adr.contains("archive/tasks/TSK-0002-b.md"), "{adr}");
    assert!(
        !adr.contains("TSK-0001"),
        "a finished task is no step: {adr}"
    );
    let bug = read(&dir.0, "project/bugs/BUG-0002-open.md");
    assert!(bug.contains("1. Work TSK-0005"), "{bug}");
    assert!(bug.contains("status: approved"), "{bug}");
    assert!(read(&dir.0, "project/archive/tasks/TSK-0002-b.md").contains("folded-into: ADR-0001"));
    assert!(read(&dir.0, "project/archive/tasks/TSK-0005-e.md").contains("folded-into: BUG-0002"));
}

#[test]
fn an_open_task_with_no_live_authority_is_reported_and_placed_nowhere() {
    let dir = Dir::new("orphan");
    old_form(&dir.0);
    let text = said(&paw(&dir.0, &["upgrade", "--write"]));
    assert!(text.contains("TSK-0003 needs a decision"), "{text}");
    assert!(!read(&dir.0, "project/archive/tasks/TSK-0003-c.md").contains("folded-into"));
    assert!(!read(&dir.0, "project/adrs/ADR-0002-gone.md").contains("## Plan"));
}

#[test]
fn a_withdrawn_task_is_neither_folded_nor_reported_whatever_its_list_says() {
    let dir = Dir::new("withdrawn");
    old_form(&dir.0);
    let text = said(&paw(&dir.0, &["upgrade", "--write"]));
    assert!(!text.contains("TSK-0007"), "{text}");
    assert!(!read(&dir.0, "project/bugs/BUG-0002-open.md").contains("2. "));
}

#[test]
fn a_decision_whose_work_landed_elsewhere_stores_done() {
    let dir = Dir::new("elsewhere");
    old_form(&dir.0);
    paw(&dir.0, &["upgrade", "--write"]);
    assert!(read(&dir.0, "project/adrs/ADR-0004-elsewhere.md").contains("status: done"));
}

#[test]
fn finished_records_store_done_and_open_ones_do_not() {
    let dir = Dir::new("done");
    old_form(&dir.0);
    paw(&dir.0, &["upgrade", "--write"]);
    assert!(read(&dir.0, "project/adrs/ADR-0003-finished.md").contains("status: done"));
    assert!(read(&dir.0, "project/adrs/ADR-0001-open.md").contains("status: approved"));
    assert!(read(&dir.0, "project/bugs/BUG-0001-closed.md").contains("status: done"));
    assert!(read(&dir.0, "project/bugs/BUG-0003-recorded.md").contains("status: done"));
}

#[test]
fn the_retired_step_leaves_the_profile_and_its_comment_stays() {
    let dir = Dir::new("profile");
    old_form(&dir.0);
    paw(&dir.0, &["upgrade", "--write"]);
    let profile = read(&dir.0, ".meowpaw/profile.toml");
    assert!(
        profile.contains("gates = [\"design\", \"spec\", \"implement\"]"),
        "{profile}"
    );
    assert!(profile.contains("# The gates a run decides."), "{profile}");
}

#[test]
fn a_second_run_changes_nothing_and_says_so() {
    let dir = Dir::new("again");
    old_form(&dir.0);
    paw(&dir.0, &["upgrade", "--write"]);
    let adr = read(&dir.0, "project/adrs/ADR-0001-open.md");
    let output = paw(&dir.0, &["upgrade", "--write"]);
    let text = said(&output);
    assert!(output.status.success(), "{text}");
    assert!(text.contains("nothing to upgrade"), "{text}");
    assert_eq!(read(&dir.0, "project/adrs/ADR-0001-open.md"), adr);
}

#[test]
fn every_check_of_a_record_in_the_old_form_names_the_upgrade() {
    let dir = Dir::new("old");
    old_form(&dir.0);
    let output = paw(&dir.0, &["check"]);
    let text = said(&output);
    assert_eq!(output.status.code(), Some(1), "{text}");
    assert!(text.contains("run paw upgrade"), "{text}");
    assert_eq!(text.matches("run paw upgrade").count(), 1, "{text}");
}

#[test]
fn a_retired_kind_is_refused_and_an_archived_record_still_resolves() {
    let dir = Dir::new("retired");
    old_form(&dir.0);
    paw(&dir.0, &["upgrade", "--write"]);
    for kind in ["task", "epic"] {
        let output = paw(&dir.0, &["new", kind]);
        assert_eq!(output.status.code(), Some(1), "{}", said(&output));
        assert!(said(&output).contains("retired"), "{}", said(&output));
    }
    let output = paw(&dir.0, &["show", "TSK-0001"]);
    assert!(output.status.success(), "{}", said(&output));
    assert!(said(&output).contains("Work TSK-0001"), "{}", said(&output));
}

fn requirement(id: &str) -> String {
    format!(
        "---\nid: {id}\nartifact: requirement\ntopic: t\nclass: functional\nstatus: approved\nrevised: 2026-01-01\nverification: static\n---\n\n# {id}\n\nThe thing MUST hold.\n"
    )
}

fn planned(id: &str, status: &str, plan: &str) -> String {
    format!(
        "---\nid: {id}\nartifact: adr\nstatus: {status}\nrevised: 2026-01-01\naddresses: [REQ-0001]\nsupersedes: []\n---\n\n# {id}\n\n## Decision\n\nDecided.\n{plan}"
    )
}

fn new_form(root: &Path, status: &str, plan: &str) {
    write(
        root,
        ".meowpaw/profile.toml",
        "[record]\nroot = \"project\"\n",
    );
    write(
        root,
        "project/requirements/REQ-0001-a.md",
        &requirement("REQ-0001"),
    );
    write(
        root,
        "project/adrs/ADR-0001-a.md",
        &planned("ADR-0001", status, plan),
    );
}

#[test]
fn a_decision_with_no_plan_is_not_ready_to_implement() {
    let dir = Dir::new("noplan");
    new_form(&dir.0, "approved", "");
    let output = paw(&dir.0, &["ready", "implement", "ADR-0001"]);
    assert_eq!(output.status.code(), Some(1), "{}", said(&output));
    assert!(said(&output).contains("no plan"), "{}", said(&output));
}

#[test]
fn a_decision_with_a_plan_is_next_and_ready() {
    let dir = Dir::new("plan");
    new_form(&dir.0, "approved", "\n## Plan\n\n1. Do it.\n");
    write(
        &dir.0,
        "project/specs/SPC-0001-a.md",
        "---\nid: SPC-0001\nartifact: spec\nstatus: live\nrevised: 2026-01-01\nstates: [REQ-0001]\n---\n\n# A\n",
    );
    let output = paw(&dir.0, &["ready", "implement", "ADR-0001"]);
    assert!(output.status.success(), "{}", said(&output));
    assert!(said(&paw(&dir.0, &["status"])).contains("next: implement ADR-0001"));
}

#[test]
fn done_closes_the_decision_and_its_requirement() {
    let dir = Dir::new("close");
    new_form(&dir.0, "approved", "\n## Plan\n\n1. Do it.\n");
    let output = paw(&dir.0, &["done", "ADR-0001", "--pr", "12"]);
    assert!(output.status.success(), "{}", said(&output));
    let adr = read(&dir.0, "project/adrs/ADR-0001-a.md");
    assert!(adr.contains("status: done"), "{adr}");
    assert!(adr.contains("pr: 12"), "{adr}");
    let shown = said(&paw(&dir.0, &["show", "REQ-0001"]));
    assert!(shown.contains("closed"), "{shown}");
}

#[test]
fn done_closes_a_defect() {
    let dir = Dir::new("closedefect");
    write(
        &dir.0,
        ".meowpaw/profile.toml",
        "[record]\nroot = \"project\"\n",
    );
    write(
        &dir.0,
        "project/bugs/BUG-0001-a.md",
        &defect("BUG-0001", "", "The regression test in tests/a."),
    );
    let output = paw(&dir.0, &["done", "BUG-0001", "--pr", "13"]);
    assert!(output.status.success(), "{}", said(&output));
    assert!(read(&dir.0, "project/bugs/BUG-0001-a.md").contains("status: done"));
}

#[test]
fn a_plan_may_change_until_the_record_is_done() {
    let dir = Dir::new("frozen");
    new_form(&dir.0, "approved", "\n## Plan\n\n1. Do it.\n");
    let git = |args: &[&str]| {
        let done = Command::new("git")
            .args(args)
            .current_dir(&dir.0)
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .output()
            .unwrap();
        assert!(done.status.success(), "{}", said(&done));
    };
    git(&["init", "-q"]);
    git(&["add", "-A"]);
    git(&[
        "-c",
        "user.name=a",
        "-c",
        "user.email=a@b",
        "commit",
        "-qm",
        "a",
    ]);
    write(
        &dir.0,
        "project/adrs/ADR-0001-a.md",
        &planned("ADR-0001", "approved", "\n## Plan\n\n1. Do it better.\n"),
    );
    let output = paw(&dir.0, &["check", "frozen", "--base", "HEAD"]);
    assert!(output.status.success(), "{}", said(&output));
    write(
        &dir.0,
        "project/adrs/ADR-0001-a.md",
        &planned(
            "ADR-0001",
            "approved",
            "\n## Plan\n\n1. Do it.\n\nDecided otherwise.\n",
        )
        .replace("Decided.", "Reworded."),
    );
    let output = paw(&dir.0, &["check", "frozen", "--base", "HEAD"]);
    assert_eq!(output.status.code(), Some(1), "{}", said(&output));
}
