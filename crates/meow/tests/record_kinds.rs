// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The kinds a repository declares, the order between kinds and the frozen
//! insight (TSK-4970, TSK-4975, TSK-4960; SPC-1070 "Kinds a repository
//! declares" and "The frozen check").

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
            std::env::temp_dir().join(format!("meow-kinds-{name}-{}-{stamp}", std::process::id()));
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

fn layout() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/lib/layout.toml")
}

fn paw_with(dir: &Path, layout: &Path, args: &[&str]) -> Output {
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

fn paw(dir: &Path, args: &[&str]) -> Output {
    paw_with(dir, &layout(), args)
}

/// Standard output and standard error, in that order.
fn said(output: &Output) -> String {
    format!(
        "{}{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    )
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

fn commit_all(dir: &Path) {
    git(dir, &["init", "-q", "--template="]);
    git(dir, &["add", "-A"]);
    git(
        dir,
        &[
            "-c",
            "user.email=a@b",
            "-c",
            "user.name=n",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "-m",
            "chore: seed",
        ],
    );
}

const NARRATIVE: &str = "[record.kinds.narrative]\nprefix = \"NAR\"\nlifetime = \"record\"\ntemplate = \".meowpaw/templates/narrative.md\"\n";

fn story(id: &str, status: &str, extra: &str) -> String {
    let status = if status.is_empty() {
        String::new()
    } else {
        format!("status: {status}\n")
    };
    format!(
        "---\nid: {id}\nartifact: narrative\n{status}revised: 2026-01-01\n{extra}---\n\n# A story\n"
    )
}

/// A repository declaring `narrative`, with its template and one file.
fn declared(name: &str, profile: &str, story_text: &str) -> Dir {
    let dir = Dir::new(name);
    write(
        &dir.0,
        ".meowpaw/profile.toml",
        &format!("[record]\nroot = \"project\"\n\n{profile}"),
    );
    write(&dir.0, ".meowpaw/templates/narrative.md", "# Template\n");
    write(&dir.0, "project/narrative/NAR-0001-a-story.md", story_text);
    dir
}

fn has_line(text: &str, words: &[&str]) -> bool {
    text.lines().any(|l| words.iter().all(|w| l.contains(w)))
}

/// TSK-4970 criterion 1, REQ-0666, REQ-0670: a declared kind's file is
/// checked as a built-in kind's is.
#[test]
fn a_declared_kinds_file_missing_its_status_is_reported_like_a_built_in_kinds() {
    let dir = declared("status", NARRATIVE, &story("NAR-0001", "", ""));
    let done = paw(&dir.0, &["check"]);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(
        has_line(
            &text,
            &["NAR-0001-a-story.md", "front matter has no status"]
        ),
        "{text}"
    );
}

/// TSK-4970 criterion 1, REQ-0666: a well-formed declared file passes.
#[test]
fn a_well_formed_declared_file_is_not_reported() {
    let dir = declared("clean", NARRATIVE, &story("NAR-0001", "draft", ""));
    let text = said(&paw(&dir.0, &["check"]));
    assert!(!text.contains("NAR-0001"), "{text}");
    assert!(!text.contains("unknown key"), "{text}");
}

/// TSK-4970 criterion 2, REQ-0668: a declaration with no template is a finding
/// naming the kind and the key.
#[test]
fn a_declaration_without_a_template_is_a_finding() {
    let profile = "[record.kinds.narrative]\nprefix = \"NAR\"\nlifetime = \"record\"\n";
    let dir = declared("no-template", profile, &story("NAR-0001", "draft", ""));
    let done = paw(&dir.0, &["check"]);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(has_line(&text, &["narrative", "template"]), "{text}");
}

/// TSK-4970 criterion 2, REQ-0668: a template path that doesn't exist is a
/// finding naming the kind and the file.
#[test]
fn a_template_that_does_not_exist_is_a_finding() {
    let profile = NARRATIVE.replace("narrative.md", "missing.md");
    let dir = declared("bad-template", &profile, &story("NAR-0001", "draft", ""));
    let done = paw(&dir.0, &["check"]);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(
        has_line(&text, &["narrative", ".meowpaw/templates/missing.md"]),
        "{text}"
    );
}

/// TSK-4970 criterion 2, REQ-0668: the prefix and the lifetime are required
/// as well.
#[test]
fn a_declaration_without_a_prefix_or_a_lifetime_is_a_finding() {
    let profile = "[record.kinds.narrative]\ntemplate = \".meowpaw/templates/narrative.md\"\n";
    let dir = declared("bare", profile, &story("NAR-0001", "draft", ""));
    let text = said(&paw(&dir.0, &["check"]));
    assert!(has_line(&text, &["narrative", "prefix"]), "{text}");
    assert!(has_line(&text, &["narrative", "lifetime"]), "{text}");
}

/// TSK-4970 criterion 3, REQ-0670: a key that would turn an obligation off is
/// an unknown key, and the approved file is still frozen.
#[test]
fn a_key_that_would_opt_out_is_unknown_and_the_file_stays_frozen() {
    let profile = format!("{NARRATIVE}frozen = false\n");
    let dir = declared("frozen", &profile, &story("NAR-0001", "approved", ""));
    commit_all(&dir.0);
    let text = said(&paw(&dir.0, &["check"]));
    assert!(
        has_line(&text, &["unknown key", "record.kinds.narrative.frozen"]),
        "{text}"
    );
    write(
        &dir.0,
        "project/narrative/NAR-0001-a-story.md",
        &story("NAR-0001", "approved", "topic: changed\n"),
    );
    let done = paw(&dir.0, &["check", "frozen", "--base", "HEAD"]);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(
        has_line(&text, &["NAR-0001-a-story.md", "approved"]),
        "{text}"
    );
}

/// TSK-4970 criterion 4: `record.kinds` and the keys under it are known.
#[test]
fn the_kinds_table_is_not_an_unknown_key() {
    let profile = format!("{NARRATIVE}outranks = [\"research\"]\n");
    let dir = declared("known", &profile, &story("NAR-0001", "draft", ""));
    let text = said(&paw(&dir.0, &["check"]));
    assert!(!text.contains("unknown key"), "{text}");
}

fn ranked(name: &str, research: &str) -> Dir {
    let profile = format!("{NARRATIVE}outranks = [\"research\"]\n");
    let dir = declared(name, &profile, NARRATIVE_CITING);
    write(&dir.0, "project/research/RES-0001-a-finding.md", research);
    dir
}

const NARRATIVE_CITING: &str = "---\nid: NAR-0001\nartifact: narrative\nstatus: draft\nrevised: 2026-01-01\ntopic: alpha\n---\n\n# A story\n\nSee RES-0001.\n";

fn finding(field: &str, other: &str) -> String {
    format!(
        "---\nid: RES-0001\nartifact: research\nstatus: draft\nrevised: 2026-01-01\n{field}\n---\n\n# A finding\n\nSee {other}.\n"
    )
}

/// TSK-4975 criterion 1, REQ-0667: two artifacts of ranked kinds that cite
/// each other and disagree on a field are reported, both named, with the order,
/// and neither file changes.
#[test]
fn a_conflict_across_a_declared_order_is_reported_and_nothing_is_changed() {
    let research = finding("topic: beta", "NAR-0001");
    let dir = ranked("conflict", &research);
    let done = paw(&dir.0, &["check"]);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(
        has_line(
            &text,
            &[
                "NAR-0001",
                "RES-0001",
                "topic",
                "narrative outranks research"
            ]
        ),
        "{text}"
    );
    assert_eq!(
        std::fs::read_to_string(dir.0.join("project/narrative/NAR-0001-a-story.md")).unwrap(),
        NARRATIVE_CITING
    );
    assert_eq!(
        std::fs::read_to_string(dir.0.join("project/research/RES-0001-a-finding.md")).unwrap(),
        research
    );
}

/// TSK-4975 criterion 2, REQ-0667: agreeing on every field is no conflict.
#[test]
fn a_pair_that_agrees_is_not_a_conflict() {
    let dir = ranked("agree", &finding("topic: alpha", "NAR-0001"));
    let text = said(&paw(&dir.0, &["check"]));
    assert!(!has_line(&text, &["outranks"]), "{text}");
}

/// TSK-4975 criterion 1, REQ-0667: artifacts that don't cite each other are
/// not compared.
#[test]
fn a_pair_that_does_not_cite_each_other_is_not_compared() {
    let dir = ranked("uncited", &finding("topic: beta", "nothing"));
    let text = said(&paw(&dir.0, &["check"]));
    assert!(!has_line(&text, &["outranks"]), "{text}");
}

/// TSK-4975 criterion 3: an `outranks` entry naming no kind is reported.
#[test]
fn an_outranks_entry_naming_no_kind_is_reported() {
    let profile = format!("{NARRATIVE}outranks = [\"dream\"]\n");
    let dir = declared("unknown-kind", &profile, &story("NAR-0001", "draft", ""));
    let done = paw(&dir.0, &["check"]);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(has_line(&text, &["narrative", "dream"]), "{text}");
}

fn insight(body: &str) -> String {
    format!(
        "---\nid: INS-0001\nartifact: insight\nstatus: approved\nrevised: 2026-01-01\n---\n\n# A claim\n\n## Evidence\n\n{body}\n"
    )
}

/// TSK-4960 criterion 1, REQ-2662: an approved insight changed after the base
/// revision is reported, and the same fixture passes once the layout leaves
/// the insight out, so the test can fail.
#[test]
fn an_approved_insight_changed_since_the_base_is_reported() {
    let dir = Dir::new("insight");
    write(
        &dir.0,
        ".meowpaw/profile.toml",
        "[record]\nroot = \"project\"\n",
    );
    write(
        &dir.0,
        "project/insights/INS-0001-a-claim.md",
        &insight("Measured."),
    );
    commit_all(&dir.0);
    write(
        &dir.0,
        "project/insights/INS-0001-a-claim.md",
        &insight("Edited."),
    );
    let done = paw(&dir.0, &["check", "frozen", "--base", "HEAD"]);
    let text = said(&done);
    assert_eq!(done.status.code(), Some(1), "{text}");
    assert!(
        has_line(&text, &["INS-0001-a-claim.md", "changed since"]),
        "{text}"
    );

    let without: String = std::fs::read_to_string(layout())
        .unwrap()
        .split("[[kind]]")
        .filter(|kind| !kind.contains("name = \"insight\""))
        .collect::<Vec<_>>()
        .join("[[kind]]");
    let path = dir.0.join("layout-without-insight.toml");
    std::fs::write(&path, without).unwrap();
    let done = paw_with(&dir.0, &path, &["check", "frozen", "--base", "HEAD"]);
    assert_eq!(done.status.code(), Some(0), "{}", said(&done));
}
