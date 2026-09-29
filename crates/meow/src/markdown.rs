// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-markdown`: whether a work tree holds a Markdown corpus, what it
//! configured, the `[verbs]` table that configuration binds, and the settings
//! behind its verbs that are missing or have no effect (SPC-1195).
//!
//! `status`, `bind` and `check` read the files git tracks, run git alone and
//! write nothing (SPC-1190), so detection and binding start none of the tools
//! they name. `links` runs lychee and classifies each result from its JSON.

use crate::profile::{self, Profile};
use std::collections::BTreeSet;
use std::path::PathBuf;
use yaml_rust2::{Yaml, YamlLoader};

const UNRESOLVED: u8 = 3;
const FOUND: u8 = 1;
const USAGE: &str = "usage: meow-markdown status | bind | check | links [<input>...]";
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
        ["check"] => check(),
        ["links", inputs @ ..] => links(inputs),
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

    /// Each `.markdownlintrc`, which markdownlint-cli alone reads, and only
    /// in the directory it runs from (RES-0295).
    fn markdownlintrc(&self) -> Vec<&str> {
        self.named(|n| n == ".markdownlintrc")
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
    configurations.extend(corpus.markdownlintrc());
    configurations.sort_by_key(|path| (path.rsplit_once('/').map_or("", |(dir, _)| dir), *path));
    if configurations.is_empty() {
        println!("markdownlint configuration: none tracked");
    } else {
        println!("markdownlint configuration, by directory:");
        for path in configurations {
            let readers = if file_name(path).starts_with(".markdownlint-cli2.") {
                "markdownlint-cli2 alone"
            } else if file_name(path) == ".markdownlintrc" {
                "markdownlint-cli alone, run in its directory"
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
        } else if !corpus.at_root(|n| n == ".markdownlintrc").is_empty() {
            println!("lint = \"markdownlint '**/*.md'\"");
            println!("# meow-markdown check runs the settings checks; this lint command doesn't");
        } else if others.is_empty() {
            println!("lint = \"meow-markdown check\"");
        } else {
            println!(
                "# lint: unbound, looked for .markdownlint-cli2.*, .markdownlint.* and .markdownlintrc, and found only a linter this pack binds no command for"
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

/// The findings in the settings behind the verbs: a missing render target
/// (REQ-2452), a markdownlint configuration the `lint` verb lacks, ignores or
/// never applies (REQ-2434), and a link check that leaves its network
/// behaviour undeclared (REQ-2454). It reads the profile and the tracked
/// files, and exits 1 on any finding.
fn check() -> u8 {
    println!("meow-markdown check");
    let corpus = match Corpus::read() {
        Ok(corpus) => corpus,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let findings = findings(&corpus);
    if findings.is_empty() {
        println!("no findings");
        return 0;
    }
    for finding in &findings {
        println!("{finding}");
    }
    FOUND
}

fn findings(corpus: &Corpus) -> Vec<String> {
    let mut found = Vec::new();
    let target = corpus
        .profile
        .get("markdown")
        .and_then(|m| m.get("target"))
        .and_then(toml::Value::as_str)
        .unwrap_or("");
    if target.trim().is_empty() {
        found.push("no render target: declare [markdown] target".to_string());
    }
    let lint = corpus
        .profile
        .get("verbs")
        .and_then(|v| v.get("lint"))
        .and_then(toml::Value::as_str)
        .unwrap_or("");
    let programs = programs(lint);
    let configurations = corpus.markdownlint();
    if programs.contains(&"markdownlint-cli2") && configurations.is_empty() {
        found.push("markdownlint-cli2 runs its defaults: no configuration file".to_string());
    }
    if programs.contains(&"markdownlint") {
        for file in configurations.iter().filter(|p| is_cli2(p)) {
            found.push(format!("markdownlint ignores {file}"));
        }
    }
    for dir in configurations
        .iter()
        .map(|p| directory(p))
        .collect::<BTreeSet<_>>()
    {
        let here: Vec<&str> = configurations
            .iter()
            .copied()
            .filter(|p| directory(p) == dir)
            .collect();
        let applied = here.iter().find(|p| !is_cli2(p));
        let overridden = here
            .iter()
            .find(|p| is_cli2(p) && cli2_sets_rules(&corpus.root.join(p)));
        if let (Some(a), Some(b)) = (applied, overridden) {
            found.push(format!(
                "{}: {a} and {b} both configure rules; markdownlint-cli2 applies {a}",
                if dir.is_empty() { "." } else { dir }
            ));
        }
    }
    for finding in link_settings(corpus) {
        if !found.contains(&finding) {
            found.push(finding);
        }
    }
    found
}

/// The settings a link check must declare, by their names in `lychee.toml`.
const LINK_SETTINGS: [&str; 3] = ["offline", "max_retries", "cache"];

/// The findings for each verb that runs `lychee` or `meow-markdown links`:
/// a setting neither its settings file nor its flags declare, a settings file
/// that doesn't parse, and a cache the repository's ignore files leave
/// unignored (REQ-2454).
fn link_settings(corpus: &Corpus) -> Vec<String> {
    let mut found = Vec::new();
    let Some(verbs) = corpus.profile.get("verbs").and_then(toml::Value::as_table) else {
        return found;
    };
    for command in verbs.values().filter_map(toml::Value::as_str) {
        let words = words(command);
        let direct = words.iter().any(|w| file_name(w) == "lychee");
        let links = words
            .windows(2)
            .any(|pair| file_name(pair[0]) == "meow-markdown" && pair[1] == "links");
        if !direct && !links {
            continue;
        }
        let flags = if direct {
            LinkFlags::read(&words)
        } else {
            LinkFlags::default()
        };
        let file = flags.config.clone().unwrap_or_else(|| "lychee.toml".into());
        let mut settings = toml::Table::new();
        if let Ok(text) = std::fs::read_to_string(corpus.root.join(&file)) {
            match text.parse::<toml::Table>() {
                Ok(table) => settings = table,
                Err(error) => {
                    let message = error.message().replace('\n', " ");
                    found.push(format!("{file} doesn't parse as TOML: {message}"));
                    continue;
                }
            }
        }
        for setting in LINK_SETTINGS {
            let flagged = match setting {
                "offline" => flags.offline,
                "max_retries" => flags.max_retries,
                _ => flags.cache.is_some(),
            };
            if !flagged && !settings.contains_key(setting) {
                found.push(format!("link check declares no {setting}"));
            }
        }
        let cached = flags
            .cache
            .unwrap_or_else(|| settings.get("cache").and_then(toml::Value::as_bool) == Some(true));
        if cached && !ignored(&corpus.root, ".lycheecache") {
            found.push(".lycheecache isn't ignored".to_string());
        }
    }
    found
}

/// What a `lychee` command's own flags declare (RES-0294): `--offline`,
/// `--max-retries` and `--cache`, the last two with an optional value, and
/// the settings file `--config` names.
#[derive(Default)]
struct LinkFlags {
    offline: bool,
    max_retries: bool,
    /// Whether the flags turn the cache on, where they set it at all.
    cache: Option<bool>,
    config: Option<String>,
}

impl LinkFlags {
    fn read(words: &[&str]) -> LinkFlags {
        let mut flags = LinkFlags::default();
        for (i, word) in words.iter().enumerate() {
            let (name, value) = match word.split_once('=') {
                Some((name, value)) => (name, Some(value)),
                None => (*word, None),
            };
            match name {
                "--offline" => flags.offline = true,
                "--max-retries" => flags.max_retries = true,
                "--cache" => flags.cache = Some(value != Some("false")),
                "--config" | "-c" => {
                    flags.config = value
                        .map(str::to_string)
                        .or_else(|| words.get(i + 1).map(|w| w.to_string()));
                }
                _ => {}
            }
        }
        flags
    }
}

/// Whether an ignore file the repository holds ignores `path`. A global
/// excludes file and `.git/info/exclude` protect one clone only, so they
/// don't count.
fn ignored(root: &std::path::Path, path: &str) -> bool {
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

/// The maps `links` reads from lychee's JSON, and the ones it knows and passes
/// over: a success, a redirect that resolved, and a suggestion for an address
/// already in `error_map` (RES-0294).
const READ_MAPS: [&str; 3] = ["error_map", "timeout_map", "excluded_map"];
const KNOWN_MAPS: [&str; 6] = [
    "success_map",
    "error_map",
    "timeout_map",
    "suggestion_map",
    "redirect_map",
    "excluded_map",
];

/// How `links` classifies one result (SPC-1195).
#[derive(Clone, Copy, PartialEq)]
enum Class {
    Finding,
    Unreachable,
    Unresolved,
    Skipped,
}

impl Class {
    fn label(self) -> &'static str {
        match self {
            Class::Finding => "finding",
            Class::Unreachable => "unreachable",
            Class::Unresolved => "unresolved",
            Class::Skipped => "skipped",
        }
    }
}

/// Runs lychee from the root and classifies each result from its JSON, never
/// from its exit status, because lychee exits 2 for a timeout as for a broken
/// link (RES-0294, REQ-2438). It exits 1 on any finding, 3 where none is and
/// anything is unreachable, unresolved, absent or broken, and 0 otherwise.
fn links(inputs: &[&str]) -> u8 {
    println!("meow-markdown links");
    let corpus = match Corpus::read() {
        Ok(corpus) => corpus,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let inputs: Vec<&str> = if inputs.is_empty() {
        vec!["**/*.md"]
    } else {
        inputs.to_vec()
    };
    let ran = std::process::Command::new("lychee")
        .args(["--format", "json", "--no-progress", "--"])
        .args(&inputs)
        .current_dir(&corpus.root)
        .stdin(std::process::Stdio::null())
        .output();
    let done = match ran {
        Ok(done) => done,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            println!("tool absent: lychee");
            return UNRESOLVED;
        }
        Err(error) => {
            println!("tool broken: lychee didn't start: {error}");
            return UNRESOLVED;
        }
    };
    if !matches!(done.status.code(), Some(0 | 2)) {
        let said = String::from_utf8_lossy(&done.stderr);
        let said = said
            .lines()
            .find(|l| !l.trim().is_empty())
            .unwrap_or("")
            .trim();
        let status = done
            .status
            .code()
            .map_or("no exit status".to_string(), |code| {
                format!("exit status {code}")
            });
        println!("tool broken: lychee ended with {status}, checking nothing: {said}");
        return UNRESOLVED;
    }
    let results = match classify(&done.stdout, &corpus.root) {
        Ok(results) => results,
        Err(reason) => {
            println!("tool broken: lychee printed {reason}");
            return UNRESOLVED;
        }
    };
    for (class, heading) in [
        (Class::Finding, "findings"),
        (Class::Unreachable, "unreachable, so not checked"),
        (Class::Unresolved, "unresolved, matching no class"),
    ] {
        let lines: Vec<&String> = results
            .iter()
            .filter(|(c, _)| *c == class)
            .map(|(_, line)| line)
            .collect();
        if !lines.is_empty() {
            println!("{heading}:");
            for line in lines {
                println!("  {line}");
            }
        }
    }
    let skipped: Vec<&String> = results
        .iter()
        .filter(|(c, _)| *c == Class::Skipped)
        .map(|(_, line)| line)
        .collect();
    if !skipped.is_empty() {
        println!("skipped, never checked: {}", skipped.len());
        for line in skipped {
            println!("  {line}");
        }
    }
    let any = |class| results.iter().any(|(c, _)| *c == class);
    if any(Class::Finding) {
        FOUND
    } else if any(Class::Unreachable) || any(Class::Unresolved) {
        UNRESOLVED
    } else {
        println!("every checked link resolved");
        0
    }
}

/// Each result in lychee's JSON with its class and the line that reports it,
/// or what made the output unreadable.
fn classify(stdout: &[u8], root: &std::path::Path) -> Result<Vec<(Class, String)>, String> {
    let json: serde_json::Value =
        serde_json::from_slice(stdout).map_err(|_| "output that isn't JSON".to_string())?;
    let Some(report) = json.as_object() else {
        return Err("JSON that isn't an object".into());
    };
    for key in report.keys().filter(|k| k.ends_with("_map")) {
        if !KNOWN_MAPS.contains(&key.as_str()) {
            return Err(format!("{key}, a map links doesn't know"));
        }
    }
    let mut results = Vec::new();
    for map in READ_MAPS {
        let Some(sources) = report.get(map).and_then(serde_json::Value::as_object) else {
            return Err(format!("no {map}"));
        };
        for (source, entries) in sources {
            let source = shown(source, root);
            for entry in entries.as_array().into_iter().flatten() {
                let url = entry["url"].as_str().unwrap_or("");
                let status = &entry["status"];
                let text = status["text"].as_str().unwrap_or("");
                let class = match map {
                    "timeout_map" => Class::Unreachable,
                    "excluded_map" => Class::Skipped,
                    _ => error_class(url, status),
                };
                let at = entry["span"]["line"]
                    .as_u64()
                    .map_or(String::new(), |line| format!(":{line}"));
                results.push((
                    class,
                    format!("{}: {source}{at}: {url}: {text}", class.label()),
                ));
            }
        }
    }
    Ok(results)
}

/// The class of an entry in `error_map`, from its address and its status.
fn error_class(url: &str, status: &serde_json::Value) -> Class {
    match status["code"].as_u64() {
        Some(500..=599 | 429 | 408 | 401 | 403) => Class::Unreachable,
        Some(400..=499) => Class::Finding,
        Some(_) => Class::Unresolved,
        None if url.starts_with("file://")
            && status["text"]
                .as_str()
                .is_some_and(|t| t.starts_with("File not found")) =>
        {
            Class::Finding
        }
        None if url.starts_with("http://") || url.starts_with("https://") => Class::Unreachable,
        None => Class::Unresolved,
    }
}

/// An input as lychee named it, relative to the root where it lies inside.
fn shown(source: &str, root: &std::path::Path) -> String {
    std::path::Path::new(source)
        .strip_prefix(root)
        .map_or(source.to_string(), |p| p.to_string_lossy().into_owned())
}

/// The directory a tracked path lies in, empty at the root.
fn directory(path: &str) -> &str {
    path.rsplit_once('/').map_or("", |(dir, _)| dir)
}

fn is_cli2(path: &str) -> bool {
    file_name(path).starts_with(".markdownlint-cli2.")
}

/// The name of each program a shell command runs or passes as a word, by its
/// last path component, so `npx markdownlint-cli2` and a path both count.
fn programs(command: &str) -> Vec<&str> {
    words(command).into_iter().map(file_name).collect()
}

/// A shell command's words, split at white space and the shell's `;`, `&`,
/// `|`, `(` and `)`, with their quotes removed.
fn words(command: &str) -> Vec<&str> {
    command
        .split(|c: char| c.is_whitespace() || ";&|()".contains(c))
        .map(|word| word.trim_matches(['\'', '"']))
        .filter(|word| !word.is_empty())
        .collect()
}

/// Whether a `.markdownlint-cli2.*` file's `config` key sets any rule. A
/// JavaScript file is code the program doesn't run, so it counts as setting
/// rules where its text names `config`. A file that can't be read or parsed
/// counts as setting none, since markdownlint-cli2 then fails on it itself.
fn cli2_sets_rules(path: &std::path::Path) -> bool {
    let Ok(text) = std::fs::read_to_string(path) else {
        return false;
    };
    let name = path.to_string_lossy();
    if name.ends_with(".cjs") || name.ends_with(".mjs") {
        return text.contains("config");
    }
    if name.ends_with(".yaml") || name.ends_with(".yml") {
        return YamlLoader::load_from_str(&text)
            .ok()
            .and_then(|docs| docs.into_iter().next())
            .is_some_and(|doc| match &doc["config"] {
                Yaml::Hash(rules) => !rules.is_empty(),
                Yaml::BadValue | Yaml::Null => false,
                _ => true,
            });
    }
    serde_json::from_str::<serde_json::Value>(&plain_json(&text))
        .ok()
        .and_then(|json| json.get("config").cloned())
        .is_some_and(|config| match config {
            serde_json::Value::Object(rules) => !rules.is_empty(),
            serde_json::Value::Null => false,
            _ => true,
        })
}

/// JSONC as JSON: comments and trailing commas outside strings removed.
fn plain_json(text: &str) -> String {
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

    fn tracked(paths: &[&str]) -> BTreeSet<String> {
        paths.iter().map(|p| p.to_string()).collect()
    }

    #[test]
    fn two_markdown_files_are_a_corpus_and_one_is_not() {
        assert!(detected(&tracked(&["README.md", "docs/a.md"])));
        assert!(!detected(&tracked(&["README.md", "main.c"])));
    }

    #[test]
    fn a_command_names_its_programs_by_their_last_component() {
        assert_eq!(
            programs("npx markdownlint-cli2 '**/*.md' && node_modules/.bin/markdownlint x"),
            ["npx", "markdownlint-cli2", "*.md", "markdownlint", "x"]
        );
    }

    #[test]
    fn jsonc_loses_its_comments_and_trailing_commas() {
        let text = "{ // a comment\n \"config\": { \"MD013\": false, }, /* \"x\": 1 */ \"url\": \"a//b\", }";
        let json: serde_json::Value = serde_json::from_str(&plain_json(text)).unwrap();
        assert_eq!(json["config"]["MD013"], false);
        assert_eq!(json["url"], "a//b");
    }

    #[test]
    fn a_nested_markdownlint_file_makes_a_corpus() {
        assert!(detected(&tracked(&[
            "README.md",
            "docs/.markdownlint.jsonc"
        ])));
    }
}
