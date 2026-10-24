// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! What the Godot, Starlark and Scheme packs share beyond `pack`: the work tree
//! as a pack reads it, a stage bound once for each directory its marker
//! activates, and the words of a stage's command (SPC-1190, SPC-1380,
//! SPC-1385, SPC-1390).

#![allow(dead_code)]

use crate::detect::{self, Marker};
use crate::pack::{Binding, State};
use crate::profile::{self, Profile};
use std::collections::BTreeSet;
use std::path::PathBuf;

/// The exit status of a report that found nothing and left something
/// unresolved (SPC-1190).
pub(crate) const UNRESOLVED: u8 = 3;
/// The exit status of a report with at least one finding.
pub(crate) const FOUND: u8 = 1;

/// The work tree as the program reads it: its root, what git tracks and the
/// profile.
pub(crate) struct Tree {
    pub root: PathBuf,
    pub tracked: BTreeSet<String>,
    pub profile: toml::Table,
    pub has_profile: bool,
}

impl Tree {
    /// The tree, or why it can't be read: no marker is tracked, or the profile
    /// doesn't parse. `say` gets the profile's state and its unknown keys.
    pub(crate) fn read(
        language: &str,
        markers: fn(&BTreeSet<String>) -> Vec<Marker>,
        say: fn(&str),
    ) -> Result<Tree, String> {
        let root = profile::repository_root();
        let root = std::fs::canonicalize(&root).unwrap_or(root);
        let tracked = detect::tracked(&root);
        if markers(&tracked).is_empty() {
            return Err(format!("not a {language} repository"));
        }
        let read = profile::read(&root);
        for line in profile::report(&read) {
            say(&line);
        }
        let (profile, has_profile) = match read {
            Profile::Absent => (toml::Table::new(), false),
            Profile::Unparseable(message) => {
                return Err(format!("the profile doesn't parse: {message}"));
            }
            Profile::Parsed(table, _) => (table, true),
        };
        Ok(Tree {
            root,
            tracked,
            profile,
            has_profile,
        })
    }

    /// The text of a tracked file, or none where it can't be read.
    pub(crate) fn text(&self, path: &str) -> Option<String> {
        if !self.tracked.contains(path) {
            return None;
        }
        std::fs::read_to_string(self.root.join(path)).ok()
    }

    /// The names of the tracked files directly in `dir`.
    pub(crate) fn names_in(&self, dir: &str) -> Vec<&str> {
        self.tracked
            .iter()
            .filter(|path| detect::directory_of(path) == dir)
            .map(|path| path.rsplit('/').next().unwrap_or(path))
            .collect()
    }

    /// The tracked files under `prefix`.
    pub(crate) fn under(&self, prefix: &str) -> Vec<&str> {
        self.tracked
            .iter()
            .filter(|path| path.starts_with(prefix))
            .map(String::as_str)
            .collect()
    }

    /// Whether an ignore rule git reads covers `path`.
    pub(crate) fn ignored(&self, path: &str) -> bool {
        profile::reading_git()
            .args(["check-ignore", "-q", "--", path])
            .current_dir(&self.root)
            .status()
            .is_ok_and(|status| status.success())
    }

    /// Whether the profile declares `stage`.
    pub(crate) fn declared(&self, stage: &str) -> bool {
        profile::stages(&self.profile)
            .and_then(toml::Value::as_table)
            .is_some_and(|stages| stages.contains_key(stage))
    }

    /// Each stage's command the profile declares as a string.
    pub(crate) fn commands(&self) -> Vec<(String, String)> {
        profile::stages(&self.profile)
            .and_then(toml::Value::as_table)
            .map(|stages| {
                stages
                    .iter()
                    .filter_map(|(stage, value)| Some((stage.clone(), value.as_str()?.to_string())))
                    .collect()
            })
            .unwrap_or_default()
    }
}

/// `dir` joined to `name`, with `.` for the root.
pub(crate) fn join(dir: &str, name: &str) -> String {
    if dir == "." {
        name.to_string()
    } else {
        format!("{dir}/{name}")
    }
}

/// A word the shell passes through unchanged, or quoted where it needs it.
pub(crate) fn sh(word: &str) -> String {
    if !word.is_empty()
        && word
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || "._/-=:@,+".contains(c))
    {
        word.to_string()
    } else {
        format!("'{}'", word.replace('\'', "'\\''"))
    }
}

/// `command` run in `dir`: in a subshell, so that a stage joining several
/// directories' commands stays in the root between them.
pub(crate) fn in_dir(dir: &str, command: &str) -> String {
    if dir == "." {
        command.to_string()
    } else {
        format!("(cd {} && {command})", sh(dir))
    }
}

/// The directory outside the working tree where the commands `bind` prints
/// for `pack` keep their output, as the shell text that names it.
pub(crate) fn out_dir(pack: &str, dir: &str) -> String {
    let name = if dir == "." { "root" } else { dir };
    format!("${{XDG_STATE_HOME:-$HOME/.local/state}}/meowpaw/packs/{pack}/{name}")
}

/// The words of a command, split at white space and the shell's `;`, `&`, `|`,
/// `(` and `)`.
pub(crate) fn words(command: &str) -> Vec<&str> {
    command
        .split(|c: char| c.is_whitespace() || ";&|()".contains(c))
        .filter(|w| !w.is_empty())
        .collect()
}

/// Whether one of the command's words runs `tool`: its last path component.
pub(crate) fn runs(command: &str, tool: &str) -> bool {
    words(command)
        .iter()
        .any(|w| w.rsplit('/').next() == Some(tool))
}

/// The line `bind` prints for `stage`: the one binding where a single
/// directory activates, and otherwise one command joining each directory's
/// bound command, with a comment naming each directory that bound nothing.
pub(crate) fn merge(stage: &str, per_dir: &[(String, Binding)]) -> Vec<String> {
    if let [(_, only)] = per_dir {
        return only.lines();
    }
    let bound: Vec<&Binding> = per_dir
        .iter()
        .map(|(_, binding)| binding)
        .filter(|binding| binding.command().is_some())
        .collect();
    let mut lines = Vec::new();
    if !bound.is_empty() {
        let command: Vec<&str> = bound.iter().filter_map(|b| b.command()).collect();
        let mut joined = Binding::bound(stage, "", &command.join(" && "));
        joined.notes = bound.iter().flat_map(|b| b.notes.clone()).collect();
        lines = joined.lines();
    }
    for (dir, binding) in per_dir {
        match &binding.state {
            State::Bound { .. } => {}
            State::Unbound(reason) => {
                lines.push(format!("# {stage}: unbound, {reason} (in {dir})"))
            }
            State::Unresolved(reason) => {
                lines.push(format!("# {stage}: unresolved, {reason} (in {dir})"))
            }
        }
    }
    lines
}
