// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! What the language packs that read a work tree's tracked files share
//! (SPC-1320, SPC-1330): the files git tracks, the parts the profile
//! declares, the profile that governs a directory, a configuration file found
//! in a directory or above it, and the words of a stage's shell command.
//!
//! Everything here reads paths and the profile, so no tool starts (SPC-1190).

#![allow(dead_code)]

use crate::detect;
use crate::profile::{self, Part, Profile};
use std::collections::BTreeSet;
use std::path::PathBuf;

pub(crate) use crate::pack::STAGES;

/// The work tree as a pack reads it.
pub(crate) struct Tree {
    pub root: PathBuf,
    pub tracked: BTreeSet<String>,
    pub parts: Vec<Part>,
}

impl Tree {
    pub(crate) fn read() -> Tree {
        let root = profile::repository_root();
        let root = std::fs::canonicalize(&root).unwrap_or(root);
        Tree {
            tracked: detect::tracked(&root),
            parts: detect::parts(&root),
            root,
        }
    }

    /// The declared part with the longest directory holding `directory`.
    pub(crate) fn holding(&self, directory: &str) -> Option<&Part> {
        self.parts
            .iter()
            .filter(|part| directory != "." && covers(directory, &part.directory))
            .max_by_key(|part| part.directory.len())
    }

    /// The profile that governs `directory`: its part's, read over the
    /// root's, or the root's where no part holds it (SPC-1040).
    pub(crate) fn profile(&self, directory: &str) -> Profile {
        match self.holding(directory) {
            Some(part) => profile::read_part(&self.root, part),
            None => profile::read(&self.root),
        }
    }

    /// Where that profile is, relative to the root.
    pub(crate) fn profile_path(&self, directory: &str) -> String {
        match self.holding(directory) {
            Some(part) => format!("{}/{}", part.directory, profile::PROFILE),
            None => profile::PROFILE.to_string(),
        }
    }

    /// Each tracked file whose name satisfies `test`, in `directory` or above
    /// it, up to the root: the places a tool searches for its configuration.
    pub(crate) fn find(&self, directory: &str, test: impl Fn(&str) -> bool) -> Vec<String> {
        self.tracked
            .iter()
            .filter(|path| {
                !path.contains("node_modules/")
                    && covers(directory, &detect::directory_of(path))
                    && test(file_name(path))
            })
            .cloned()
            .collect()
    }

    /// The tracked file `name` in `directory` itself, as a path from the root.
    pub(crate) fn here(&self, directory: &str, name: &str) -> Option<String> {
        let path = if directory == "." {
            name.to_string()
        } else {
            format!("{directory}/{name}")
        };
        self.tracked.contains(&path).then_some(path)
    }

    /// A tracked file's text.
    pub(crate) fn text(&self, path: &str) -> Option<String> {
        std::fs::read_to_string(self.root.join(path)).ok()
    }
}

/// Whether `of` is `directory` or a directory above it.
fn covers(directory: &str, of: &str) -> bool {
    of == "."
        || directory == of
        || directory
            .strip_prefix(of)
            .is_some_and(|rest| rest.starts_with('/'))
}

/// `directory`, then each directory above it, ending at the root.
pub(crate) fn ancestors(directory: &str) -> Vec<String> {
    let mut found = Vec::new();
    let mut here = directory.to_string();
    while here != "." {
        found.push(here.clone());
        here = detect::directory_of(&here);
    }
    found.push(".".to_string());
    found
}

/// A directory as an argument gives it, without `./` or a trailing `/`.
pub(crate) fn directory_argument(text: &str) -> String {
    let trimmed = text.trim().trim_end_matches('/');
    let trimmed = trimmed.strip_prefix("./").unwrap_or(trimmed);
    if trimmed.is_empty() {
        ".".to_string()
    } else {
        trimmed.to_string()
    }
}

pub(crate) fn file_name(path: &str) -> &str {
    path.rsplit('/').next().unwrap_or(path)
}

/// A word as the program it names: its last path component without an
/// `@<version>` suffix, so `npx eslint@10.12.0` runs ESLint.
pub(crate) fn program(word: &str) -> &str {
    let name = file_name(word);
    match name.split_once('@') {
        Some((bare, _)) if !bare.is_empty() => bare,
        _ => name,
    }
}

/// The simple commands of a shell command, split at `&&`, `||`, `;` and `|`,
/// each as its words with their quotes removed.
pub(crate) fn commands(command: &str) -> Vec<Vec<&str>> {
    command
        .split([';', '&', '|', '(', ')'])
        .map(|simple| {
            simple
                .split_whitespace()
                .map(|word| word.trim_matches(['\'', '"']))
                .filter(|word| !word.is_empty())
                .collect::<Vec<_>>()
        })
        .filter(|words| !words.is_empty())
        .collect()
}

/// Each of the five stages the profile declares, with its command.
pub(crate) fn declared(table: &toml::Table) -> Vec<(&'static str, String)> {
    let Some(stages) = profile::stages(table).and_then(toml::Value::as_table) else {
        return Vec::new();
    };
    STAGES
        .iter()
        .filter_map(|stage| {
            stages
                .get(*stage)
                .and_then(toml::Value::as_str)
                .map(|command| (*stage, command.to_string()))
        })
        .collect()
}

/// Whether an ignore file the repository holds ignores `path`. A global
/// excludes file and `.git/info/exclude` protect one clone only, so they
/// don't count.
pub(crate) fn ignored(root: &std::path::Path, path: &str) -> bool {
    let Ok(done) = profile::reading_git()
        .args(["check-ignore", "--verbose", "--", path])
        .current_dir(root)
        .output()
    else {
        return false;
    };
    let text = String::from_utf8_lossy(&done.stdout);
    text.lines().any(|line| {
        let mut parts = line.splitn(3, ':');
        let (Some(source), Some(_), Some(rest)) = (parts.next(), parts.next(), parts.next()) else {
            return false;
        };
        let pattern = rest.split('\t').next().unwrap_or("");
        !source.is_empty()
            && !source.starts_with(".git/")
            && !std::path::Path::new(source).is_absolute()
            && !pattern.starts_with('!')
    })
}

/// JSONC as JSON: comments and trailing commas outside strings removed.
pub(crate) fn plain_json(text: &str) -> String {
    let chars: Vec<char> = text.chars().collect();
    let mut out = String::with_capacity(text.len());
    let mut i = 0;
    let mut in_string = false;
    while i < chars.len() {
        let c = chars[i];
        let next = chars.get(i + 1).copied();
        if in_string {
            out.push(c);
            if c == '\\' {
                if let Some(n) = next {
                    out.push(n);
                    i += 1;
                }
            } else if c == '"' {
                in_string = false;
            }
        } else if c == '"' {
            in_string = true;
            out.push(c);
        } else if c == '/' && next == Some('/') {
            while i < chars.len() && chars[i] != '\n' {
                i += 1;
            }
            continue;
        } else if c == '/' && next == Some('*') {
            i += 2;
            while i < chars.len() && !(chars[i] == '*' && chars.get(i + 1) == Some(&'/')) {
                i += 1;
            }
            i += 2;
            continue;
        } else if c == ',' {
            let rest = chars[i + 1..].iter().find(|c| !c.is_whitespace());
            if !matches!(rest, Some('}') | Some(']')) {
                out.push(c);
            }
        } else {
            out.push(c);
        }
        i += 1;
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_file_is_found_in_its_directory_and_above_and_not_below() {
        let tree = Tree {
            root: PathBuf::from("."),
            tracked: ["a.cfg", "x/a.cfg", "x/y/a.cfg", "z/a.cfg"]
                .iter()
                .map(|p| p.to_string())
                .collect(),
            parts: Vec::new(),
        };
        assert_eq!(tree.find("x", |n| n == "a.cfg"), ["a.cfg", "x/a.cfg"]);
        assert_eq!(tree.find(".", |n| n == "a.cfg"), ["a.cfg"]);
        assert_eq!(ancestors("x/y"), ["x/y", "x", "."]);
    }

    #[test]
    fn a_command_splits_at_the_shells_separators() {
        let found = commands("a -x && b 'c' | d; e");
        assert_eq!(
            found,
            [vec!["a", "-x"], vec!["b", "c"], vec!["d"], vec!["e"]]
        );
        assert_eq!(program("npx"), "npx");
        assert_eq!(program("node_modules/.bin/eslint@10"), "eslint");
    }
}
