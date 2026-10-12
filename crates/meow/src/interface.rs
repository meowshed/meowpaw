// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow interface`: the one public-interface page, generated from the
//! documentation the tool carries, and a crate test holds the committed page
//! to what it generates (REQ-2992, ADR-2490, ADR-2720).

use crate::help::Entry;
use crate::profile::{KEYS, Key};
use crate::record::{Layout, load_layout};
use regex::Regex;
use std::path::Path;

const CLEAN: u8 = 0;
const FOUND: u8 = 1;
const UNCHECKED: u8 = 3;

/// The core unit's version, from the manifest beside the binary, which the
/// page's `describes` stamp carries. Empty where the checkout has none, and
/// the documentation check then reads the stamp against the tree's manifest.
fn core_version() -> String {
    let exe = match std::env::current_exe() {
        Ok(exe) => exe,
        Err(_) => return String::new(),
    };
    let unit = exe.parent().and_then(Path::parent).and_then(Path::parent);
    let manifest = unit
        .map(|u| u.join(".claude-plugin").join("plugin.json"))
        .unwrap_or_default();
    std::fs::read_to_string(manifest)
        .ok()
        .and_then(|t| serde_json::from_str::<serde_json::Value>(&t).ok())
        .and_then(|v| {
            v.get("version")
                .and_then(|v| v.as_str().map(str::to_string))
        })
        .unwrap_or_default()
}

/// What one subcommand's page entry carries: its name, what it determines,
/// and what a person reads in its place.
type Subcommand = (&'static str, &'static str, &'static str);

/// Every unit's program with its subcommand table, so the page names each
/// subcommand of the tool from the documentation that unit carries.
fn tables() -> Vec<(&'static str, Vec<Subcommand>)> {
    // The pushes are gated per feature, so a literal doesn't serve.
    #[allow(clippy::vec_init_then_push)]
    let mut out: Vec<(&'static str, Vec<Subcommand>)> = Vec::new();
    #[cfg(feature = "author")]
    out.push(("meow-author", entries(&crate::author::HELP)));
    #[cfg(feature = "verbs")]
    out.push(("meow-checks", entries(&crate::verbs::HELP)));
    #[cfg(feature = "github")]
    out.push(("meow-github", entries(&crate::github::HELP)));
    #[cfg(feature = "git")]
    out.push(("meow-git", entries(&crate::git::HELP)));
    #[cfg(feature = "record")]
    out.push((
        "meow-flow",
        crate::record::COMMANDS
            .iter()
            .map(|c| (c.name, c.determines, c.by_hand))
            .collect(),
    ));
    #[cfg(feature = "licence")]
    out.push(("meow-licence", entries(&crate::licence::HELP)));
    #[cfg(feature = "loop")]
    out.push(("meow-loop", entries(&crate::runloop::HELP)));
    #[cfg(feature = "markdown")]
    out.push(("meow-markdown", entries(&crate::markdown::HELP)));
    #[cfg(feature = "mise")]
    out.push(("meow-mise", entries(&crate::mise::HELP)));
    #[cfg(feature = "gotask")]
    out.push(("meow-gotask", entries(&crate::gotask::HELP)));
    #[cfg(feature = "prose")]
    out.push(("meow-prose", entries(&crate::prose::HELP)));
    #[cfg(feature = "scm")]
    out.push(("meow-scm", entries(&crate::scm::HELP)));
    #[cfg(feature = "unattended")]
    out.push(("meow-unattended", entries(&crate::unattended::HELP)));
    out
}

fn entries(table: &[Entry]) -> Vec<Subcommand> {
    table
        .iter()
        .map(|e| (e.name, e.determines, e.by_hand))
        .collect()
}

pub fn main(args: &[String]) -> u8 {
    if !args.is_empty() {
        eprintln!("usage: meow interface");
        return 2;
    }
    let layout = match load_layout() {
        Ok(layout) => layout,
        Err(error) => {
            eprintln!("meow interface: {error}");
            return UNCHECKED;
        }
    };
    match page(&layout, tables(), KEYS, &core_version()) {
        Ok(text) => {
            print!("{text}");
            CLEAN
        }
        Err(failures) => {
            for failure in &failures {
                eprintln!("{failure}");
            }
            FOUND
        }
    }
}

/// The page, from the layout the record ships, each unit's subcommand
/// documentation and the table of profile keys. An item with no
/// documentation comment is an error naming it, because a page generated
/// from nothing states nothing (REQ-2992).
pub(crate) fn page(
    layout: &Layout,
    tables: Vec<(&'static str, Vec<Subcommand>)>,
    keys: &[Key],
    version: &str,
) -> Result<String, Vec<String>> {
    let mut failures = Vec::new();
    // A documentation page states no requirement identifier (SPC-1110): the
    // reasons the tool carries name their records, and the page strips the
    // parenthetical that holds them.
    let citation = Regex::new(r"\s*\((?:and )?(?:REQ|ADR|SPC|EPC|TSK|BUG|RES)-\d+[a-z]?(?:, (?:(?:and )?(?:REQ|ADR|SPC|EPC|TSK|BUG|RES)-\d+[a-z]?|\d+))*\)")
        .expect("citation pattern");
    let plain = |text: &str| citation.replace_all(text, "").into_owned();
    let mut out = format!(
        "---
reader: someone changing the harness or writing against it
answers: what the harness's public interface is, and what a change to it breaks
kind: reference
describes: [meow-core@{version}]
---

# The public interface

Generated by `paw interface` from the documentation the tool carries. Edit the
tool's documentation, never this page: a change that removes or renames an
entry here is a change to the interface, and its commit is marked breaking.

## The stages and their outcomes

The five stages a repository declares, and the outcome each run records:

| Stage    | Outcomes                                          |
| -------- | ------------------------------------------------- |
",
    );
    for verb in crate::verbs::VERBS {
        out.push_str(&format!(
            "| `{verb}` | {} |\n",
            crate::verbs::OUTCOMES.join(", ")
        ));
    }
    out.push_str(
        "\nA stage's run records one of the four outcomes: `passed` and `failed`\n\
         from the command's exit status, `interrupted` from a signal, which says\n\
         the run stopped and nothing about the work, and `unresolved` where the\n\
         profile declares no command, which is never a pass.\n\n\
         ## The artifact kinds and their front matter\n\n",
    );
    for kind in &layout.kinds {
        let place = kind
            .dir
            .as_ref()
            .or(kind.file.as_ref())
            .map(|d| format!("`{d}/`"))
            .unwrap_or_else(|| "at the record's root".to_string());
        let prefix = kind
            .prefix
            .as_ref()
            .map(|p| format!("`{p}-NNNN`, "))
            .unwrap_or_default();
        out.push_str(&format!(
            "- **{}** — {}{}: {}\n",
            kind.name,
            place,
            prefix,
            kind.fields.join(", ")
        ));
        if !kind.statuses.is_empty() {
            out.push_str(&format!("  statuses: {}\n", kind.statuses.join(", ")));
        }
        if !kind.sections.is_empty() {
            out.push_str(&format!("  sections: {}\n", kind.sections.join(", ")));
        }
    }
    out.push_str(&format!(
        "\n## The record's paths and identifier formats\n\n\
         Every artifact carries `{}` in its front matter. The relations, whose\n\
         values are bare identifiers: {}.\n\
         An identifier is its kind's prefix, a dash and four digits, allocated\n\
         once, never reused and never renumbered. The index of a kind is its\n\
         `{}`.\n\n\
         ## The profile's keys\n\n\
         Each key the profile may carry, with the reason the key exists:\n\n",
        layout.fields.join(", "),
        layout.relations.join(", "),
        layout.index_name,
    ));
    for key in keys {
        if key.reason.trim().is_empty() {
            failures.push(format!(
                "the profile key {} carries no documentation comment, where the page states its reason",
                key.path
            ));
        }
        out.push_str(&format!("- `{}` — {}\n", key.path, plain(key.reason)));
    }
    out.push_str(
        "\n## The subcommands\n\n\
         Every subcommand of the tool, each with what it determines and what a\n\
         person reads in its place:\n",
    );
    for (unit, entries) in tables {
        out.push_str(&format!("\n### {unit}\n\n"));
        for (name, determines, by_hand) in entries {
            if determines.trim().is_empty() {
                failures.push(format!(
                    "the subcommand {unit} {name} carries no documentation comment"
                ));
            }
            out.push_str(&format!("- `{name}` — {}\n", plain(determines)));
            if !by_hand.trim().is_empty() {
                out.push_str(&format!("  By hand: {}\n", plain(by_hand)));
            }
        }
    }
    out.push_str(&format!(
        "\n## The form of a piece of evidence\n\n{}\n",
        crate::verbs::ledger::EVIDENCE
    ));
    if failures.is_empty() {
        Ok(out)
    } else {
        Err(failures)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn layout() -> Layout {
        // The layout the record ships, named where the binary's own copy
        // doesn't exist, as the record's tests do.
        unsafe {
            std::env::set_var(
                "MEOW_LAYOUT",
                concat!(
                    env!("CARGO_MANIFEST_DIR"),
                    "/../../plugins/meow-flow/lib/layout.toml"
                ),
            );
        }
        load_layout().unwrap()
    }

    #[test]
    fn the_committed_page_is_current() {
        // TSK-4940 criterion 1, REQ-2992: the page regenerates byte for byte,
        // and names each of the six parts.
        // The version the repository's own manifest stamps, which the
        // committed page's `describes` carries.
        let manifest = std::fs::read_to_string(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../plugins/meow-core/.claude-plugin/plugin.json"
        ))
        .unwrap();
        let version = serde_json::from_str::<serde_json::Value>(&manifest).unwrap()["version"]
            .as_str()
            .unwrap()
            .to_string();
        let page =
            page(&layout(), tables(), KEYS, &version).expect("every item carries its comment");
        let committed = std::fs::read_to_string(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../docs/interface.md"
        ))
        .unwrap();
        assert_eq!(page, committed);
        for part in [
            "stages",
            "artifact kinds",
            "paths and identifier formats",
            "profile's keys",
            "subcommands",
            "piece of evidence",
        ] {
            assert!(
                page.to_lowercase().contains(&part.to_lowercase()),
                "the page names no part {part}"
            );
        }
    }

    #[test]
    fn a_key_without_a_comment_fails_the_page() {
        // TSK-4940 criterion 3, REQ-2992: a profile key with no documentation
        // comment fails the page, naming the key.
        let keys = [Key {
            path: "stages.test",
            reason: "",
        }];
        let failures = page(&layout(), tables(), &keys, "0.10.0").unwrap_err();
        assert!(
            failures.iter().any(|f| f.contains("stages.test")),
            "the keyless comment went unnamed: {failures:?}"
        );
    }
}
