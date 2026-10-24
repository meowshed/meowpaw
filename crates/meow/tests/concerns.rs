// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! A decision's `concerns:` front matter: it passes the front matter check
//! where the decision names one (TSK-5000), and `paw check` reports a concern
//! no specification section frames (TSK-5005, ADR-2630, SPC-1090 "The
//! questions a specification answers").

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
        let path = std::env::temp_dir().join(format!(
            "meow-concerns-{name}-{}-{stamp}",
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

fn out(output: &Output) -> String {
    format!(
        "{}{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    )
}

/// A record holding an approved requirement and a decision addressing it with
/// the front matter lines `extra`, and a specification with the section
/// headings `headings`.
fn fixture(name: &str, status: &str, extra: &str, headings: &str) -> Dir {
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
        "---\nid: REQ-0001\nartifact: requirement\ntopic: a\nclass: functional\nstatus: approved\nrevised: 2026-01-01\nverification: static\nelaborates: []\n---\n\n# REQ-0001\n\nThe harness MUST copy a constraint as it stands.\n",
    );
    write(
        &root,
        "specs/SPC-0001-a-part.md",
        &format!(
            "---\nid: SPC-0001\nartifact: spec\nstatus: live\nrevised: 2026-01-01\nstates: [REQ-0001]\n---\n\n# A part\n\n## Scope\n\nWhat it covers.\n\n{headings}"
        ),
    );
    write(
        &root,
        "adrs/ADR-0001-a-choice.md",
        &format!(
            "---\nid: ADR-0001\nartifact: adr\nstatus: {status}\nrevised: 2026-01-01\naddresses: [REQ-0001]\nsupersedes: []\n{extra}---\n\n# 0001. A choice\n\n## Decision\n\nIt is decided.\n\n## Why\n\nBecause.\n\n## Alternatives\n\n| Option | Better at | Why it lost |\n| --- | --- | --- |\n| Do nothing | Nothing | It fixes nothing |\n\n## What it costs\n\nSomething.\n\n## What would reverse it\n\n- A condition.\n\n## Consequences\n\nSome.\n"
        ),
    );
    dir
}

/// TSK-5000 criterion 2, REQ-2252: a decision with `concerns: [security]`
/// passes the front matter check, and the layout names `concerns` as an
/// optional field of the decision kind.
#[test]
fn a_decision_naming_a_concern_passes_the_front_matter_check() {
    let dir = fixture("front", "approved", "concerns: [security]\n", "");
    let done = paw(&dir.0, &["check", "front-matter"]);
    assert_eq!(done.status.code(), Some(0), "{}", out(&done));
    assert!(!out(&done).contains("concerns"), "{}", out(&done));
}

#[test]
fn the_layout_names_concerns_as_an_optional_field_of_the_decision_kind() {
    let layout = std::fs::read_to_string(
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/lib/layout.toml"),
    )
    .unwrap();
    let table: toml::Table = layout.parse().unwrap();
    let kinds = table["kind"].as_array().unwrap();
    let decision = kinds
        .iter()
        .find(|k| k["name"].as_str() == Some("decision"))
        .unwrap();
    let optional = decision["optional_fields"].as_array().unwrap();
    assert!(optional.iter().any(|v| v.as_str() == Some("concerns")));
    assert!(
        !decision["fields"]
            .as_array()
            .unwrap()
            .iter()
            .any(|v| v.as_str() == Some("concerns")),
        "concerns is optional, so approved decisions with none still pass"
    );
}
