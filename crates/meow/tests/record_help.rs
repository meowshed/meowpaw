// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Every `paw` subcommand's help names what a person reads in its place and
//! the first word of each kind of line it prints, and each subcommand's output
//! on a fixture record holds to that (TSK-4330, SPC-1080 "Each subcommand makes
//! one determination").

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
            std::env::temp_dir().join(format!("meow-help-{name}-{}-{stamp}", std::process::id()));
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

fn record(kind: &str, id: &str, fields: &[(&str, &str)], sections: &[&str], body: &str) -> String {
    let mut status = "approved";
    let mut out = String::new();
    let mut rest = String::new();
    for (key, value) in fields {
        if *key == "status" {
            status = value;
        } else {
            rest.push_str(&format!("{key}: {value}\n"));
        }
    }
    out.push_str(&format!(
        "---\nid: {id}\nartifact: {kind}\nstatus: {status}\nrevised: 2026-01-01\n{rest}---\n\n# {id}\n\n"
    ));
    for section in sections {
        out.push_str(&format!("## {section}\n\nText.\n\n"));
    }
    out.push_str(body);
    out
}

fn index(names: &[&str]) -> String {
    let mut out =
        "---\nid: index\nartifact: index\nstatus: live\nrevised: 2026-01-01\n---\n\n# Index\n\n"
            .to_string();
    for name in names {
        out.push_str(&format!("- {name}\n"));
    }
    out
}

/// A small record every check passes, in a git repository of its own.
fn fixture(name: &str) -> Dir {
    let dir = Dir::new(name);
    let root = dir.0.join("project");
    let done = Command::new("git")
        .args(["init", "-q"])
        .current_dir(&dir.0)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap();
    assert!(done.status.success(), "git init failed: {done:?}");
    write(
        &dir.0,
        ".meowpaw/profile.toml",
        "[record]\nroot = \"project\"\n",
    );
    write(
        &root,
        "vision.md",
        "---\nid: vision\nartifact: vision\nstatus: live\nrevised: 2026-01-01\n---\n\n# Vision\n",
    );
    write(
        &root,
        "README.md",
        &index(&["SPC-0001", "EPC-0001", "BUG-0001"]),
    );
    write(
        &root,
        "specs/SPC-0001-a-part.md",
        &record(
            "spec",
            "SPC-0001",
            &[("status", "live"), ("states", "[REQ-0001]")],
            &["Scope", "Boundary", "Behaviour", "Failure paths"],
            "",
        ),
    );
    write(
        &root,
        "research/RES-0001-synthesis.md",
        &record(
            "research",
            "RES-0001",
            &[],
            &["Summary", "Conclusions", "Sources"],
            "\nIt indexes RES-0002.\n",
        ),
    );
    write(
        &root,
        "research/RES-0002-a-finding.md",
        &record(
            "research",
            "RES-0002",
            &[("elaborates", "RES-0001")],
            &["Summary", "Method", "Conclusions", "Sources"],
            "",
        ),
    );
    write(&root, "requirements/README.md", &index(&["REQ-0001"]));
    write(
        &root,
        "requirements/REQ-0001-an-obligation.md",
        &record(
            "requirement",
            "REQ-0001",
            &[
                ("topic", "a"),
                ("class", "functional"),
                ("verification", "static"),
                ("elaborates", "RES-0002"),
            ],
            &[],
            "",
        ),
    );
    write(&root, "adrs/README.md", &index(&["ADR-0001"]));
    let decision = record(
        "adr",
        "ADR-0001",
        &[("addresses", "[REQ-0001]")],
        &[
            "Decision",
            "Why",
            "Alternatives",
            "What it costs",
            "What would reverse it",
            "Consequences",
        ],
        "",
    )
    .replace(
        "## Alternatives\n\nText.",
        "## Alternatives\n\n| Option | Why it lost |\n| ------ | ----------- |\n| Nothing | It costs more |",
    );
    write(&root, "adrs/ADR-0001-a-choice.md", &decision);
    write(
        &root,
        "epics/EPC-0001-a-plan.md",
        &record(
            "epic",
            "EPC-0001",
            &[("realises", "ADR-0001")],
            &["Acceptance criteria", "Tasks", "Coverage", "Not covered"],
            "",
        ),
    );
    write(
        &root,
        "tasks/TSK-0001-a-task.md",
        &record(
            "task",
            "TSK-0001",
            &[
                ("epic", "EPC-0001"),
                ("closes", "\n  [\n    REQ-0001,\n  ]"),
            ],
            &["What to do", "Depends on", "Evidence", "Left alone"],
            "\nSee [the plan](../epics/EPC-0001-a-plan.md).\n",
        ),
    );
    write(
        &root,
        "bugs/BUG-0001-a-defect.md",
        &record(
            "bug",
            "BUG-0001",
            &[
                ("violates", "REQ-0001"),
                ("severity", "minor"),
                ("found", "2026-01-01"),
            ],
            &[
                "Reproduction",
                "What the system does",
                "What it should do, and why",
                "Triage",
                "Closed by",
            ],
            "",
        ),
    );
    dir
}

/// `meow record <args>` in `dir`, against this repository's own layout.
fn paw(dir: &Path, args: &[&str]) -> Output {
    let layout = layout_path();
    Command::new(env!("CARGO_BIN_EXE_meow"))
        .arg("record")
        .args(args)
        .current_dir(dir)
        .env("MEOW_LAYOUT", layout)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap()
}

fn lines(output: &Output) -> Vec<String> {
    String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(str::to_string)
        .collect()
}

/// The subcommands, as `paw --help` lists them, one a line opening `paw`.
fn subcommands(dir: &Path) -> Vec<String> {
    let listed = paw(dir, &["--help"]);
    assert!(listed.status.success(), "paw --help failed: {listed:?}");
    lines(&listed)
        .iter()
        .filter_map(|line| line.strip_prefix("paw "))
        .filter_map(|line| line.split(':').next())
        .map(str::to_string)
        .collect()
}

/// The value of the help line that opens `key:`, if the help has one.
fn help_value(dir: &Path, verb: &str, key: &str) -> Option<String> {
    let help = paw(dir, &[verb, "--help"]);
    assert!(help.status.success(), "paw {verb} --help failed: {help:?}");
    lines(&help)
        .iter()
        .find_map(|line| line.strip_prefix(&format!("{key}: ")).map(str::to_string))
}

/// The layout's kind names and relation keys, which `<kind>` and `<relation>`
/// stand for.
fn vocabulary() -> (Vec<String>, Vec<String>) {
    let text = std::fs::read_to_string(layout_path()).unwrap();
    let table: toml::Table = text.parse().unwrap();
    let relations = table
        .get("relations")
        .and_then(|v| v.as_array())
        .into_iter()
        .flatten()
        .filter_map(|v| v.as_str().map(str::to_string))
        .collect();
    let kinds = table
        .get("kind")
        .and_then(|v| v.as_array())
        .into_iter()
        .flatten()
        .filter_map(|k| k.get("name").and_then(|n| n.as_str()).map(str::to_string))
        .collect();
    (kinds, relations)
}

fn layout_path() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/lib/layout.toml")
}

/// Whether `word`, the first word of an output line, is one the help states:
/// a literal as printed, or a placeholder the help names in angle brackets.
fn stated(word: &str, kinds: &[&str]) -> bool {
    let bare = word.trim_end_matches([',', ':']);
    kinds.iter().any(|kind| match *kind {
        "<id>" => {
            let (prefix, number) = bare.split_once('-').unwrap_or(("", ""));
            !prefix.is_empty()
                && prefix.chars().all(|c| c.is_ascii_uppercase())
                && !number.is_empty()
                && number.chars().all(|c| c.is_ascii_digit())
        }
        "<count>" => !bare.is_empty() && bare.chars().all(|c| c.is_ascii_digit()),
        "<path>" => bare.contains('/'),
        "<kind>:" => word.ends_with(':') && vocabulary().0.iter().any(|k| k == bare),
        "<relation>:" => word.ends_with(':') && vocabulary().1.iter().any(|k| k == bare),
        // Free text, accepted only in the first block of lines `held` allows.
        "<text>" => false,
        placeholder if placeholder.starts_with('<') => {
            panic!("the help states a placeholder this test can't check: {placeholder}")
        }
        literal => literal == word,
    })
}

/// Runs `args` and holds every line it printed to the first words `verb`'s
/// help states, and returns the lines.
fn held(dir: &Path, verb: &str, args: &[&str]) -> Vec<String> {
    let kinds = help_value(dir, verb, "lines")
        .unwrap_or_else(|| panic!("paw {verb} --help states no `lines:` line"));
    let kinds: Vec<&str> = kinds.split_whitespace().collect();
    let output = paw(dir, args);
    let printed = lines(&output);
    assert!(
        !printed.is_empty(),
        "paw {} printed nothing: {output:?}",
        args.join(" ")
    );
    let free_first_block = kinds.contains(&"<text>");
    let mut in_first_block = true;
    for (number, line) in printed.iter().enumerate() {
        let Some(word) = line.split_whitespace().next() else {
            in_first_block = false;
            continue;
        };
        // `<text>` covers the paragraph under a heading, and not the heading.
        if free_first_block && in_first_block && number > 0 {
            continue;
        }
        assert!(
            stated(word, &kinds),
            "paw {}: the line {line:?} opens with {word:?}, which the help doesn't state ({kinds:?})",
            args.join(" ")
        );
    }
    printed
}

/// REQ-1176: every subcommand's help says what a person reads in its place.
#[test]
fn every_subcommand_names_what_a_person_reads_in_its_place() {
    let dir = fixture("by-hand");
    let verbs = subcommands(&dir.0);
    for expected in [
        "check",
        "status",
        "ready",
        "template",
        "show",
        "index",
        "new",
        "find",
        "count",
        "approve",
        "withdraw",
        "done",
        "onboarding",
    ] {
        assert!(
            verbs.iter().any(|v| v == expected),
            "paw --help lists no {expected}: {verbs:?}"
        );
    }
    for verb in &verbs {
        let by_hand = help_value(&dir.0, verb, "by hand")
            .unwrap_or_else(|| panic!("paw {verb} --help has no `by hand:` line"));
        assert!(
            by_hand.split_whitespace().count() >= 4,
            "paw {verb}: the `by hand:` line names too little to follow: {by_hand:?}"
        );
        let kinds = help_value(&dir.0, verb, "lines")
            .unwrap_or_else(|| panic!("paw {verb} --help has no `lines:` line"));
        assert!(
            !kinds.trim().is_empty(),
            "paw {verb}: the `lines:` line states no first word"
        );
    }
}

/// REQ-1184: each line the read-only subcommands print opens with a first
/// word the subcommand's help states.
#[test]
fn read_only_output_opens_with_stated_first_words() {
    let dir = fixture("read-only");
    let d = &dir.0;
    let printed = held(d, "check", &["check"]);
    assert!(
        printed.iter().any(|l| l.starts_with("coverage: ")),
        "check printed no coverage line: {printed:?}"
    );
    held(d, "check", &["check", "coverage"]);
    held(d, "check", &["check", "frozen"]);
    let printed = held(d, "status", &["status"]);
    assert!(printed.iter().any(|l| l == "Decisions"), "{printed:?}");
    held(d, "count", &["count"]);
    let hit = held(d, "find", &["find", "REQ-0001"]);
    assert!(
        hit.iter().any(|l| l.starts_with("artifacts matched:")),
        "{hit:?}"
    );
    held(d, "find", &["find", "zzzzqq"]);
    held(d, "show", &["show", "REQ-0001"]);
    held(d, "show", &["show", "TSK-0001"]);
    held(d, "show", &["show", "TSK-9999"]);
    held(d, "ready", &["ready", "implement", "TSK-0001"]);
    held(d, "ready", &["ready", "implement", "TSK-9999"]);
    held(d, "ready", &["ready", "research"]);
    held(d, "template", &["template", "task"]);
    held(d, "new", &["new", "task"]);
    held(d, "index", &["index", "requirement"]);
    held(d, "index", &["index", "task"]);
    held(d, "find", &["find", "vision"]);
    held(d, "show", &["show", "vision"]);
}

/// REQ-1184: a finding's line, a draft's waiting line and a refused change
/// each open with a first word the help states.
#[test]
fn findings_drafts_and_refusals_open_with_stated_first_words() {
    let dir = fixture("planted");
    let d = &dir.0;
    write(
        &d.join("project"),
        "research/RES-0003-broken.md",
        "No front matter.\n",
    );
    let found = paw(d, &["check"]);
    assert_eq!(found.status.code(), Some(1), "{found:?}");
    let printed = held(d, "check", &["check"]);
    assert!(
        printed
            .iter()
            .any(|l| l.starts_with("project/research/RES-0003-broken.md")),
        "check named no finding for the planted file: {printed:?}"
    );
    std::fs::remove_file(d.join("project/research/RES-0003-broken.md")).unwrap();

    let decision = d.join("project/adrs/ADR-0001-a-choice.md");
    let text = std::fs::read_to_string(&decision).unwrap();
    std::fs::write(&decision, text.replace("status: approved", "status: draft")).unwrap();
    let printed = held(d, "status", &["status", "--waiting"]);
    assert!(
        printed
            .first()
            .is_some_and(|l| l.starts_with("Waiting for approval")),
        "status --waiting named no draft: {printed:?}"
    );
    held(d, "approve", &["approve", "ADR-0001"]);
    held(d, "approve", &["approve", "ADR-9999"]);
    held(
        d,
        "withdraw",
        &[
            "withdraw",
            "REQ-9999",
            "--by",
            "ADR-0001",
            "--replaced-by",
            "REQ-0001",
        ],
    );
    held(d, "done", &["done", "TSK-9999", "--pr", "1"]);
    held(d, "onboarding", &["onboarding", "remove"]);
}

/// REQ-1170: `paw` is the launcher for the shipped binary, and no other helper
/// sits beside it.
#[test]
fn the_unit_ships_the_launcher_and_no_other_helper() {
    let bin = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/bin");
    let mut files: Vec<String> = std::fs::read_dir(&bin)
        .unwrap()
        .map(|entry| entry.unwrap())
        .filter(|entry| entry.file_type().unwrap().is_file())
        .map(|entry| entry.file_name().to_string_lossy().into_owned())
        .collect();
    files.sort();
    assert_eq!(files, ["paw"], "files beside the launcher: {files:?}");
    let launcher = std::fs::read_to_string(bin.join("paw")).unwrap();
    assert!(
        launcher.contains("meow$exe"),
        "paw doesn't run the shipped meow binary"
    );
}

/// REQ-1184: the lines a change writes open with a stated first word.
#[test]
fn successful_changes_open_with_stated_first_words() {
    let dir = fixture("changes");
    let d = &dir.0;
    write(
        &d.join("project"),
        "requirements/REQ-0002-a-replacement.md",
        &record(
            "requirement",
            "REQ-0002",
            &[
                ("topic", "a"),
                ("class", "functional"),
                ("verification", "static"),
                ("elaborates", "RES-0002"),
            ],
            &[],
            "",
        ),
    );
    let epic = d.join("project/epics/EPC-0001-a-plan.md");
    let text = std::fs::read_to_string(&epic).unwrap();
    std::fs::write(
        &epic,
        format!("{text}\n- [ ] T-001 TSK-0001 a task\n      closes: REQ-0001\n"),
    )
    .unwrap();
    let done = held(d, "done", &["done", "TSK-0001", "--pr", "7"]);
    assert!(
        done.iter().any(|l| l.contains("is done in pull request 7")),
        "{done:?}"
    );
    let withdrawn = held(
        d,
        "withdraw",
        &[
            "withdraw",
            "REQ-0001",
            "--by",
            "ADR-0001",
            "--replaced-by",
            "REQ-0002",
        ],
    );
    assert!(
        withdrawn.iter().any(|l| l.contains("is withdrawn")),
        "{withdrawn:?}"
    );
}

/// REQ-1184: an index's amendment line opens with a stated first word.
#[test]
fn an_index_with_an_amendment_opens_with_stated_first_words() {
    let dir = fixture("amended");
    let d = &dir.0;
    let path = d.join("project/requirements/REQ-0001-an-obligation.md");
    let text = std::fs::read_to_string(&path).unwrap();
    std::fs::write(&path, format!("{text}\n**Amended by ADR-0001.**\n")).unwrap();
    let printed = held(d, "index", &["index", "requirement"]);
    assert!(
        printed.iter().any(|l| l.starts_with("Amended:")),
        "index printed no amendment line: {printed:?}"
    );
}
