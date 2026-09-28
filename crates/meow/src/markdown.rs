// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-markdown`: whether a work tree holds a Markdown corpus, what it
//! configured, and the `[verbs]` table that configuration binds (SPC-1195).
//!
//! The program reads the files git tracks, runs git alone and writes nothing
//! (SPC-1190), so detection and binding start none of the tools they name.

use crate::profile::{self, Profile};
use std::collections::BTreeSet;
use std::path::PathBuf;

const UNRESOLVED: u8 = 3;
const USAGE: &str = "usage: meow-markdown status | bind";
const KNOWN_TARGETS: [&str; 7] = [
    "github",
    "gitlab",
    "mkdocs",
    "docusaurus",
    "hugo",
    "mdbook",
    "obsidian",
];
const SITE_GENERATORS: [(&str, &str); 3] = [
    ("mkdocs.yml", "MkDocs"),
    ("book.toml", "mdBook"),
    ("hugo.toml", "Hugo"),
];
const MISE_CONFIGURATION: [&str; 6] = [
    "mise.toml",
    ".mise.toml",
    "mise/config.toml",
    ".mise/config.toml",
    ".config/mise/config.toml",
    ".config/mise.toml",
];
const TASKFILES: [&str; 8] = [
    "Taskfile.yml",
    "taskfile.yml",
    "Taskfile.yaml",
    "taskfile.yaml",
    "Taskfile.dist.yml",
    "taskfile.dist.yml",
    "Taskfile.dist.yaml",
    "taskfile.dist.yaml",
];

pub fn main(args: &[String]) -> u8 {
    match args
        .iter()
        .map(String::as_str)
        .collect::<Vec<_>>()
        .as_slice()
    {
        ["status"] => status(),
        ["bind"] => bind(),
        _ => {
            eprintln!("{USAGE}");
            2
        }
    }
}

/// The work tree as the program reads it: its root, what git tracks and the profile.
struct Corpus {
    root: PathBuf,
    tracked: BTreeSet<String>,
    profile: toml::Table,
}

impl Corpus {
    /// The corpus, or the reason it can't be read, in the order SPC-1195 lists them.
    fn read() -> Result<Corpus, String> {
        let root = profile::repository_root();
        let root = std::fs::canonicalize(&root).unwrap_or(root);
        let mut tracked = BTreeSet::new();
        if let Ok(done) = profile::reading_git()
            .args(["ls-files", "-z"])
            .current_dir(&root)
            .output()
        {
            for path in done.stdout.split(|b| *b == 0).filter(|p| !p.is_empty()) {
                tracked.insert(String::from_utf8_lossy(path).into_owned());
            }
        }
        if !detected(&tracked) {
            return Err("not a Markdown repository".into());
        }
        let profile = match profile::read(&root) {
            Profile::Absent => return Err(format!("no profile at {}", profile::PROFILE)),
            Profile::Unparseable(message) => {
                return Err(format!("the profile doesn't parse: {message}"));
            }
            Profile::Parsed(table) => table,
        };
        Ok(Corpus {
            root,
            tracked,
            profile,
        })
    }

    /// Tracked files whose name, wherever they lie, satisfies `test`.
    fn named(&self, test: impl Fn(&str) -> bool) -> Vec<&str> {
        self.tracked
            .iter()
            .map(String::as_str)
            .filter(|path| test(file_name(path)))
            .collect()
    }

    /// Tracked files at the root whose name satisfies `test`.
    fn at_root(&self, test: impl Fn(&str) -> bool) -> Vec<&str> {
        self.tracked
            .iter()
            .map(String::as_str)
            .filter(|path| !path.contains('/') && test(path))
            .collect()
    }

    fn prettier(&self) -> Vec<&str> {
        let mut found =
            self.named(|n| n.starts_with(".prettierrc") || n.starts_with("prettier.config."));
        let keyed = self.tracked.contains("package.json")
            && std::fs::read_to_string(self.root.join("package.json"))
                .ok()
                .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok())
                .is_some_and(|json| json.get("prettier").is_some());
        if keyed {
            found.push("package.json");
        }
        found
    }

    fn mdformat(&self) -> Vec<&str> {
        self.at_root(|n| n == ".mdformat.toml")
    }

    fn markdownlint(&self) -> Vec<&str> {
        self.named(|n| n.starts_with(".markdownlint-cli2.") || n.starts_with(".markdownlint."))
    }

    fn remark(&self) -> Vec<&str> {
        self.named(|n| n.starts_with(".remarkrc"))
    }

    fn textlint(&self) -> Vec<&str> {
        self.named(|n| n.starts_with(".textlintrc"))
    }

    fn lychee(&self) -> Option<&str> {
        self.at_root(|n| n == "lychee.toml").into_iter().next()
    }

    /// Each site generator's configuration at the root, with the generator's name.
    fn sites(&self) -> Vec<(&str, &'static str)> {
        let mut found: Vec<(&str, &'static str)> = SITE_GENERATORS
            .iter()
            .filter(|(file, _)| self.tracked.contains(*file))
            .map(|(file, name)| (*file, *name))
            .collect();
        found.extend(
            self.at_root(|n| n.starts_with("docusaurus.config."))
                .into_iter()
                .map(|file| (file, "Docusaurus")),
        );
        found
    }

    /// Each runner's configuration, with the pack that reads its tasks.
    fn runners(&self) -> Vec<(&str, &'static str, &'static str)> {
        let mut found = Vec::new();
        for file in MISE_CONFIGURATION {
            if let Some(path) = self.tracked.get(file) {
                found.push((path.as_str(), "mise", "meow-mise"));
            }
        }
        for file in TASKFILES {
            if let Some(path) = self.tracked.get(file) {
                found.push((path.as_str(), "Task", "meow-gotask"));
            }
        }
        found
    }

    fn declared(&self, verb: &str) -> bool {
        self.profile
            .get("verbs")
            .and_then(toml::Value::as_table)
            .is_some_and(|verbs| verbs.contains_key(verb))
    }
}

fn file_name(path: &str) -> &str {
    path.rsplit('/').next().unwrap_or(path)
}

/// Two tracked `*.md` files, or any `.markdownlint*` file (REQ-2352): a lone
/// README is no corpus, and a markdownlint file says the repository lints one.
fn detected(tracked: &BTreeSet<String>) -> bool {
    let markdown = tracked.iter().filter(|p| p.ends_with(".md")).count();
    markdown >= 2
        || tracked
            .iter()
            .any(|p| file_name(p).starts_with(".markdownlint"))
}

fn status() -> u8 {
    println!("meow-markdown status");
    let corpus = match Corpus::read() {
        Ok(corpus) => corpus,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let count = corpus.tracked.iter().filter(|p| p.ends_with(".md")).count();
    println!("markdown files: {count} tracked");
    let target = corpus
        .profile
        .get("markdown")
        .and_then(|m| m.get("target"))
        .and_then(toml::Value::as_str)
        .filter(|t| !t.is_empty());
    match target {
        Some(t) if KNOWN_TARGETS.contains(&t) => println!("render target: {t}, known to the skill"),
        Some(t) => println!("render target: {t}, declared and unknown to the skill"),
        None => println!("render target: not declared in [markdown] target"),
    }
    let mut configurations = corpus.markdownlint();
    configurations.sort_by_key(|path| (path.rsplit_once('/').map_or("", |(dir, _)| dir), *path));
    if configurations.is_empty() {
        println!("markdownlint configuration: none tracked");
    } else {
        println!("markdownlint configuration, by directory:");
        for path in configurations {
            let readers = if file_name(path).starts_with(".markdownlint-cli2.") {
                "markdownlint-cli2 alone"
            } else {
                "markdownlint-cli2 and markdownlint-cli"
            };
            println!("  {path}: read by {readers}");
        }
    }
    let mut tools = Vec::new();
    for (files, tool) in [
        (corpus.prettier(), "prettier"),
        (corpus.mdformat(), "mdformat"),
        (corpus.remark(), "remark-lint"),
        (corpus.textlint(), "textlint"),
    ] {
        tools.extend(files.into_iter().map(|file| format!("  {file}: {tool}")));
    }
    if let Some(file) = corpus.lychee() {
        tools.push(format!("  {file}: lychee"));
    }
    for (file, name) in corpus.sites() {
        tools.push(format!("  {file}: {name}, a site generator"));
    }
    if tools.is_empty() {
        println!("other tools configured: none recognised");
    } else {
        println!("other tools configured:");
        for line in tools {
            println!("{line}");
        }
    }
    if let Some(file) = corpus.lychee() {
        let cached = std::fs::read_to_string(corpus.root.join(file))
            .ok()
            .and_then(|text| text.parse::<toml::Table>().ok())
            .and_then(|table| table.get("cache").and_then(toml::Value::as_bool))
            == Some(true);
        if cached {
            println!("lychee writes .lycheecache at the root, since {file} sets cache = true");
        }
    }
    0
}

/// A `[verbs]` table bound from what the repository committed, never from
/// what is installed, and printed, never written (ADR-1900). It exits 0 once
/// the table is printed, because a verb printed with its reason is settled.
fn bind() -> u8 {
    let corpus = match Corpus::read() {
        Ok(corpus) => corpus,
        Err(reason) => {
            println!("meow-markdown bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    println!("# meow-markdown bind: paste what follows into .meowpaw/profile.toml");
    println!("[verbs]");
    if !corpus.declared("format") {
        if !corpus.prettier().is_empty() {
            println!("format = \"prettier --check '**/*.md'\"");
        } else if !corpus.mdformat().is_empty() {
            println!("format = \"mdformat --check .\"");
        } else {
            println!(
                "# format: unbound, looked for .prettierrc*, prettier.config.*, a prettier key in package.json and .mdformat.toml"
            );
        }
    }
    let others: Vec<(&str, &str)> = corpus
        .remark()
        .into_iter()
        .map(|file| (file, "remark-lint"))
        .chain(corpus.textlint().into_iter().map(|file| (file, "textlint")))
        .collect();
    if !corpus.declared("lint") {
        if !corpus.markdownlint().is_empty() {
            println!("lint = \"markdownlint-cli2 '**/*.md'\"");
            println!("# meow-markdown check runs the settings checks; this lint command doesn't");
        } else if others.is_empty() {
            println!("lint = \"meow-markdown check\"");
        } else {
            println!(
                "# lint: unbound, looked for .markdownlint-cli2.* and .markdownlint.*, and found only a linter this pack binds no command for"
            );
        }
    }
    for (file, linter) in &others {
        println!("# {file} configures {linter}, which this pack binds no command for");
    }
    if !corpus.declared("check") {
        println!("# check: unresolved, Markdown has no types");
    }
    if !corpus.declared("test") {
        match corpus.lychee() {
            Some(_) => println!("test = \"meow-markdown links\""),
            None => println!("# test: unbound, looked for lychee.toml"),
        }
    }
    if !corpus.declared("build") {
        match corpus.sites().first() {
            Some((file, _)) => println!("# build: unbound, {file} configures a site build"),
            None => println!(
                "# build: unbound, looked for mkdocs.yml, book.toml, hugo.toml and docusaurus.config.*"
            ),
        }
    }
    for (file, runner, pack) in corpus.runners() {
        println!(
            "# {file} configures {runner}; to bind a verb to its tasks, run {pack} bind, since this pack doesn't read them"
        );
    }
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tracked(paths: &[&str]) -> BTreeSet<String> {
        paths.iter().map(|p| p.to_string()).collect()
    }

    #[test]
    fn two_markdown_files_are_a_corpus_and_one_is_not() {
        assert!(detected(&tracked(&["README.md", "docs/a.md"])));
        assert!(!detected(&tracked(&["README.md", "main.c"])));
    }

    #[test]
    fn a_nested_markdownlint_file_makes_a_corpus() {
        assert!(detected(&tracked(&[
            "README.md",
            "docs/.markdownlint.jsonc"
        ])));
    }
}
