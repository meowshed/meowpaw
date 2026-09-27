// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-licence check`: every file a repository tracks is covered by a
//! licensing declaration, as SPC-1120 states it (ADR-1400).
//!
//! A file is covered by a header in its first lines, by a `.license` file
//! beside it, or by an annotation in `REUSE.toml`. The check reports licensing
//! alone, and never who wrote a file or where anything was built (REQ-3064).

use crate::profile::{self, Profile};
use regex::Regex;
use std::collections::BTreeSet;
use std::path::Path;

const CLEAN: u8 = 0;
const FOUND: u8 = 1;
const USAGE: u8 = 2;
const UNCHECKED: u8 = 3;

/// How far into a file a header is looked for.
const HEADER_LINES: usize = 20;
const COPYRIGHT: &str = "SPDX-FileCopyrightText:";
const IDENTIFIER: &str = "SPDX-License-Identifier:";

pub fn main(args: &[String]) -> u8 {
    match args {
        [command] if command == "check" => check(&profile::repository_root()),
        _ => {
            eprintln!("usage: meow-licence check");
            USAGE
        }
    }
}

/// One `[[annotations]]` table: the globs it covers and what it declares.
struct Annotation {
    paths: Vec<Regex>,
    copyright: bool,
    identifiers: Vec<String>,
}

/// What a file's first lines, or its `.license` file, declare.
#[derive(Default)]
struct Header {
    copyright: bool,
    identifiers: Vec<String>,
}

fn check(root: &Path) -> u8 {
    let Some(files) = tracked(root) else {
        println!("meow-licence check: unchecked: the tracked files can't be listed");
        return UNCHECKED;
    };
    let mut out = Vec::new();
    let annotations = match annotations(root) {
        Ok(found) => found,
        Err(reason) => {
            println!("meow-licence check: unchecked: REUSE.toml can't be read ({reason})");
            return UNCHECKED;
        }
    };
    for annotation in &annotations {
        if annotation.copyright != !annotation.identifiers.is_empty() {
            out.push(half("REUSE.toml: an annotation", annotation.copyright));
        }
    }
    let declared = declared_header(root, &mut out);
    let mut in_use: BTreeSet<String> = annotations.iter().flat_map(|a| a.identifiers.clone()).collect();
    let mut headed = false;
    for file in &files {
        // A licence text, the bulk declaration and a `.license` file are what
        // declares licensing, and need no declaration of their own.
        if is_licence_text(file) || file == "REUSE.toml" || file.ends_with(".license") {
            continue;
        }
        let covering = annotations.iter().find(|a| a.paths.iter().any(|glob| glob.is_match(file)));
        let header = header(root, file);
        headed |= header.copyright || !header.identifiers.is_empty();
        in_use.extend(header.identifiers.iter().cloned());
        let complete = header.copyright && !header.identifiers.is_empty();
        let covered = covering.is_some_and(|a| a.copyright && !a.identifiers.is_empty());
        if complete || covered {
            continue;
        }
        if header.copyright || !header.identifiers.is_empty() {
            out.push(half(&format!("{file}: the header"), header.copyright));
        } else if covering.is_none() {
            out.push(format!("{file}: no licensing declaration covers it"));
        }
    }
    if annotations.is_empty() && !declared && !headed {
        println!("meow-licence check: licensing is undeclared: no REUSE.toml, no [licence], and no header");
        return UNCHECKED;
    }
    out.extend(licence_texts(root, &in_use));
    for finding in &out {
        println!("{finding}");
    }
    let plural = if out.len() == 1 { "" } else { "s" };
    println!("{} files, {} licensing finding{plural}", files.len(), out.len());
    if out.is_empty() { CLEAN } else { FOUND }
}

/// A declaration naming one half of a licensing statement and not the other
/// (REQ-1022).
fn half(what: &str, has_copyright: bool) -> String {
    if has_copyright {
        format!("{what} names a copyright and no licence identifier")
    } else {
        format!("{what} names a licence and no copyright")
    }
}

/// The files the repository's version control tracks, relative to its root.
fn tracked(root: &Path) -> Option<Vec<String>> {
    let done = profile::reading_git().current_dir(root).args(["ls-files", "-z"]).output().ok()?;
    if !done.status.success() {
        return None;
    }
    let text = String::from_utf8_lossy(&done.stdout);
    Some(text.split('\0').filter(|name| !name.is_empty()).map(str::to_string).collect())
}

/// A licence text is the licence itself, and needs no declaration.
fn is_licence_text(file: &str) -> bool {
    if file.starts_with("LICENSES/") {
        return true;
    }
    let name = file.rsplit('/').next().unwrap_or(file);
    let (stem, extension) = match name.split_once('.') {
        Some((stem, extension)) => (stem, extension.to_ascii_lowercase()),
        None => (name, String::new()),
    };
    // A text's extension, if it has one, names a text format: a source file
    // called licence.rs is code about licences, not a licence.
    let textual = ["", "txt", "md", "rst", "html"].contains(&extension.as_str());
    let stem = stem.to_ascii_uppercase();
    textual && ["LICENSE", "LICENCE", "COPYING"].iter().any(|text| stem == *text || stem.starts_with(&format!("{text}-")))
}

fn annotations(root: &Path) -> Result<Vec<Annotation>, String> {
    let path = root.join("REUSE.toml");
    if !path.is_file() {
        return Ok(Vec::new());
    }
    let text = std::fs::read_to_string(&path).map_err(|e| e.to_string())?;
    let table: toml::Table = text.parse().map_err(|e: toml::de::Error| e.message().to_string())?;
    let mut out = Vec::new();
    for entry in table.get("annotations").and_then(|v| v.as_array()).into_iter().flatten() {
        let Some(entry) = entry.as_table() else { continue };
        let paths = match entry.get("path") {
            Some(toml::Value::String(one)) => vec![one.clone()],
            Some(toml::Value::Array(many)) => many.iter().filter_map(|v| v.as_str().map(str::to_string)).collect(),
            _ => Vec::new(),
        };
        let copyright = entry.get("SPDX-FileCopyrightText").is_some_and(|v| !is_empty(v));
        let identifiers = match entry.get("SPDX-License-Identifier") {
            Some(toml::Value::String(expression)) => identifiers_in(expression),
            _ => Vec::new(),
        };
        out.push(Annotation { paths: paths.iter().map(|glob| glob_regex(glob)).collect(), copyright, identifiers });
    }
    Ok(out)
}

fn is_empty(value: &toml::Value) -> bool {
    match value {
        toml::Value::String(text) => text.trim().is_empty(),
        toml::Value::Array(items) => items.is_empty(),
        _ => false,
    }
}

/// A REUSE glob as a pattern: `**` crosses directories, `*` stays in one.
fn glob_regex(glob: &str) -> Regex {
    let mut pattern = String::from("^");
    let mut chars = glob.chars().peekable();
    while let Some(c) = chars.next() {
        match c {
            '*' if chars.peek() == Some(&'*') => {
                chars.next();
                pattern.push_str(".*");
            }
            '*' => pattern.push_str("[^/]*"),
            '?' => pattern.push_str("[^/]"),
            other => pattern.push_str(&regex::escape(&other.to_string())),
        }
    }
    pattern.push('$');
    Regex::new(&pattern).unwrap_or_else(|_| Regex::new("$^").expect("a pattern matching nothing"))
}

/// The licence identifiers in an SPDX expression, such as `MIT OR Apache-2.0`.
fn identifiers_in(expression: &str) -> Vec<String> {
    expression
        .split(|c: char| c.is_whitespace() || c == '(' || c == ')')
        .filter(|word| !word.is_empty() && !["AND", "OR", "WITH"].contains(word))
        .map(str::to_string)
        .collect()
}

/// What a file declares in its first lines, or in the `.license` file beside it.
fn header(root: &Path, file: &str) -> Header {
    let mut found = read_header(&root.join(format!("{file}.license")));
    if !found.copyright && found.identifiers.is_empty() {
        found = read_header(&root.join(file));
    }
    found
}

fn read_header(path: &Path) -> Header {
    let Ok(bytes) = std::fs::read(path) else { return Header::default() };
    let text = String::from_utf8_lossy(&bytes);
    let mut found = Header::default();
    for line in text.lines().take(HEADER_LINES) {
        if line.contains(COPYRIGHT) {
            found.copyright = true;
        }
        if let Some((_, expression)) = line.split_once(IDENTIFIER) {
            let expression = expression.trim().trim_end_matches(|c: char| "*/->#;".contains(c)).trim();
            found.identifiers.extend(identifiers_in(expression));
        }
    }
    found
}

/// Whether the profile declares a header, and a finding where the declared
/// header states half of what a licensing declaration must (REQ-1022).
fn declared_header(root: &Path, out: &mut Vec<String>) -> bool {
    let Profile::Parsed(table) = profile::read(root) else { return false };
    let Some(lines) = table.get("licence").and_then(|t| t.get("header")).and_then(|h| h.as_array()) else {
        return false;
    };
    let lines: Vec<&str> = lines.iter().filter_map(|l| l.as_str()).collect();
    let copyright = lines.iter().any(|l| l.contains(COPYRIGHT));
    let identifier = lines.iter().any(|l| l.contains(IDENTIFIER));
    if copyright != identifier {
        out.push(half(".meowpaw/profile.toml: the declared header", copyright));
    }
    true
}

/// Each licence text no declaration uses, and each identifier in use with no
/// text, where the repository keeps `LICENSES/` (REQ-3062).
fn licence_texts(root: &Path, in_use: &BTreeSet<String>) -> Vec<String> {
    let directory = root.join("LICENSES");
    let Ok(entries) = std::fs::read_dir(&directory) else { return Vec::new() };
    let mut texts = BTreeSet::new();
    for entry in entries.flatten() {
        let name = entry.file_name().to_string_lossy().to_string();
        if let Some(id) = name.rsplit_once('.').map(|(stem, _)| stem.to_string()) {
            texts.insert(id);
        }
    }
    let mut out = Vec::new();
    for id in texts.difference(in_use) {
        out.push(format!("LICENSES/{id}.txt: no declaration uses {id}"));
    }
    for id in in_use.difference(&texts) {
        out.push(format!("LICENSES/: {id} is in use and has no text"));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_double_star_crosses_directories_and_a_single_one_does_not() {
        assert!(glob_regex("project/**").is_match("project/adrs/ADR-1000.md"));
        assert!(glob_regex("docs/*.md").is_match("docs/README.md"));
        assert!(!glob_regex("docs/*.md").is_match("docs/sub/page.md"));
    }

    #[test]
    fn an_expression_yields_its_identifiers() {
        assert_eq!(identifiers_in("(MIT OR Apache-2.0) WITH LLVM-exception"), ["MIT", "Apache-2.0", "LLVM-exception"]);
    }

    #[test]
    fn a_licence_text_needs_no_declaration() {
        assert!(is_licence_text("LICENSE"));
        assert!(is_licence_text("LICENSES/MIT.txt"));
        assert!(is_licence_text("COPYING.md"));
        assert!(!is_licence_text("src/licence.rs"));
    }
}
