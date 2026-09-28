// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-author check`: the harness's own kind of material holds the form
//! SPC-1030 states, in this repository's units or in any directory a
//! repository points it at (ADR-1450).

use crate::profile;
use regex::Regex;
use std::path::{Path, PathBuf};

const CLEAN: u8 = 0;
const FOUND: u8 = 1;
const USAGE: u8 = 2;
const UNCHECKED: u8 = 3;

const VOCABULARY: [&str; 5] = ["role", "rules", "steps", "example", "input"];
const QUOTED: [&str; 2] = ["example", "input"];
/// Where a unit keeps its prompts, relative to the unit.
const PROMPT_DIRS: [&str; 4] = ["skills", "agents", "output-styles", "fragments"];
/// Material that isn't shipped behaviour: measurement cases and fixtures.
const SKIPPED: [&str; 3] = ["evals", "tests", "__pycache__"];

pub fn main(args: &[String]) -> u8 {
    match args.split_first() {
        Some((command, paths)) if command == "check" => check(paths),
        Some((command, rest)) if command == "cost" => cost(rest),
        _ => {
            eprintln!("usage: meow-author check [path...] | meow-author cost");
            USAGE
        }
    }
}

fn check(paths: &[String]) -> u8 {
    let root = profile::repository_root();
    let units: Vec<PathBuf> = if paths.is_empty() {
        let plugins = root.join("plugins");
        let mut found: Vec<PathBuf> = std::fs::read_dir(&plugins)
            .map(|entries| {
                entries
                    .flatten()
                    .map(|e| e.path())
                    .filter(|p| p.is_dir())
                    .collect()
            })
            .unwrap_or_default();
        found.sort();
        found
    } else {
        paths.iter().map(PathBuf::from).collect()
    };
    let mut failures = Vec::new();
    let mut files = 0;
    for unit in &units {
        if !unit.is_dir() {
            failures.push(format!("{}: is not a directory", unit.display()));
            continue;
        }
        if unit.join("commands").is_dir() {
            failures.push(format!(
                "{}: ships a commands/ directory, where a command is a skill only a person invokes",
                shown(&root, &unit.join("commands"))
            ));
        }
        for path in prompt_files(unit) {
            files += 1;
            let text = std::fs::read_to_string(&path).unwrap_or_default();
            let where_ = shown(&root, &path);
            failures.extend(vocabulary(&text, &where_));
            failures.extend(unanchored_paths(&text, &where_));
            let is_core = path.file_name().is_some_and(|n| n == "SKILL.md");
            let is_agent = path
                .parent()
                .and_then(|p| p.file_name())
                .is_some_and(|n| n == "agents");
            if is_core || is_agent {
                if field(&text, "description").is_empty() {
                    failures.push(format!("{where_}: has no description in its front matter"));
                }
                if has_steps(&text) && !stops(&text) {
                    failures.push(format!(
                        "{where_}: has a procedure and no step naming where it stops"
                    ));
                }
            }
            if is_core {
                failures.extend(unnamed_files(&root, &path, &text));
            }
        }
        for (where_, prompt) in hook_prompts(&root, unit) {
            files += 1;
            failures.extend(vocabulary(&prompt, &where_));
        }
    }
    if files == 0 && failures.is_empty() {
        println!(
            "meow-author check: unchecked: no skill, agent, output style or prompt hook was found"
        );
        return UNCHECKED;
    }
    for failure in &failures {
        println!("{failure}");
    }
    println!(
        "{files} files, {} authoring failure{}",
        failures.len(),
        if failures.len() == 1 { "" } else { "s" }
    );
    if failures.is_empty() { CLEAN } else { FOUND }
}

fn shown(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .display()
        .to_string()
}

/// Every prompt file a unit ships, outside measurement cases and fixtures.
fn prompt_files(unit: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    for dir in PROMPT_DIRS {
        walk(&unit.join(dir), &mut out);
    }
    out.retain(|p| p.extension().is_some_and(|e| e == "md"));
    out.sort();
    out
}

fn walk(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        let name = entry.file_name().to_string_lossy().to_string();
        if SKIPPED.contains(&name.as_str()) {
            continue;
        }
        if path.is_dir() {
            walk(&path, out);
        } else {
            out.push(path);
        }
    }
}

/// Each prompt hook's text, from the unit's `hooks/hooks.json`.
fn hook_prompts(root: &Path, unit: &Path) -> Vec<(String, String)> {
    let path = unit.join("hooks").join("hooks.json");
    let Ok(text) = std::fs::read_to_string(&path) else {
        return Vec::new();
    };
    let Ok(config) = serde_json::from_str::<serde_json::Value>(&text) else {
        return Vec::new();
    };
    let mut out = Vec::new();
    if let Some(events) = config.get("hooks").and_then(|h| h.as_object()) {
        for (event, groups) in events {
            for group in groups.as_array().into_iter().flatten() {
                for hook in group
                    .get("hooks")
                    .and_then(|h| h.as_array())
                    .into_iter()
                    .flatten()
                {
                    if hook.get("type").and_then(|t| t.as_str()) == Some("prompt") {
                        let prompt = hook
                            .get("prompt")
                            .and_then(|p| p.as_str())
                            .unwrap_or_default();
                        out.push((
                            format!("{} ({event})", shown(root, &path)),
                            prompt.to_string(),
                        ));
                    }
                }
            }
        }
    }
    out
}

/// The text after the front matter, and how many lines the front matter took.
fn body(text: &str) -> (&str, usize) {
    if let Some(rest) = text.strip_prefix("---\n") {
        if let Some(end) = rest.find("\n---\n") {
            let cut = 4 + end + 5;
            return (&text[cut..], text[..cut].matches('\n').count());
        }
    }
    (text, 0)
}

fn field(text: &str, key: &str) -> String {
    let Some(rest) = text.strip_prefix("---\n") else {
        return String::new();
    };
    let Some(end) = rest.find("\n---\n") else {
        return String::new();
    };
    rest[..end]
        .lines()
        .find_map(|line| line.strip_prefix(&format!("{key}:")))
        .map(|v| v.trim().to_string())
        .unwrap_or_default()
}

/// Each defect in one prompt's form, as SPC-1030 states it (REQ-1112, REQ-1120).
fn vocabulary(text: &str, where_: &str) -> Vec<String> {
    let tag = Regex::new(r"<(/?)([A-Za-z_][\w-]*)(?:\s[^<>]*)?>").expect("tag pattern");
    let heading = Regex::new(r"^#{1,6}\s").expect("heading pattern");
    let fence = Regex::new(r"^\s*(```|~~~)").expect("fence pattern");
    let code_span = Regex::new(r"`[^`]*`").expect("code span pattern");
    let opens = Regex::new(r"^<(/?)([A-Za-z_][\w-]*)(?:\s[^<>]*)?>").expect("opening tag pattern");
    let (content, offset) = body(text);
    let mut found: Vec<String> = Vec::new();
    let mut stack: Vec<String> = Vec::new();
    let mut fenced = false;
    for (i, line) in content.lines().enumerate() {
        let number = offset + i + 1;
        if fence.is_match(line) {
            fenced = !fenced;
            continue;
        }
        if fenced {
            continue;
        }
        let quoted = stack.iter().any(|t| QUOTED.contains(&t.as_str()));
        let bare = code_span.replace_all(line, "");
        if !quoted && heading.is_match(line) {
            found.push(format!(
                "{where_}:{number}: a Markdown heading, where the prompt uses tags"
            ));
        }
        let outside = stack.is_empty() && !line.trim().is_empty();
        for c in tag.captures_iter(&bare) {
            let closing = &c[1] == "/";
            let name = c[2].to_string();
            if !VOCABULARY.contains(&name.as_str()) {
                let message =
                    format!("{where_}:{number}: <{name}> is not in the vocabulary SPC-1030 states");
                if !quoted && !found.contains(&message) {
                    found.push(message);
                }
                continue;
            }
            if closing {
                if stack.contains(&name) {
                    while let Some(top) = stack.pop() {
                        if top == name {
                            break;
                        }
                    }
                }
            } else {
                if let Some(top) = stack.last() {
                    found.push(format!("{where_}:{number}: <{name}> opens inside <{top}>, where tags are top-level only"));
                }
                stack.push(name);
            }
        }
        if outside && !opens.is_match(line.trim()) {
            found.push(format!("{where_}:{number}: text outside every tag"));
        }
    }
    if let Some(top) = stack.last() {
        found.push(format!("{where_}: <{top}> is never closed"));
    }
    found
}

/// A path climbing out of the file with `../` and no directory variable in
/// front of it, which works only where the unit happens to be installed
/// (REQ-2688).
fn unanchored_paths(text: &str, where_: &str) -> Vec<String> {
    let token = Regex::new(r#"[^\s`'"()\[\]<>]*\.\./[^\s`'"()\[\]<>]*"#).expect("path pattern");
    let (content, offset) = body(text);
    let mut out = Vec::new();
    for (i, line) in content.lines().enumerate() {
        for m in token.find_iter(line) {
            let path = m.as_str();
            if !path.starts_with("${CLAUDE_SKILL_DIR}")
                && !path.starts_with("${CLAUDE_PLUGIN_ROOT}")
            {
                out.push(format!(
                    "{where_}:{}: {path} climbs out of the file with no directory variable",
                    offset + i + 1
                ));
            }
        }
    }
    out
}

/// Each file in a skill's directory its core never names, by its path, its
/// name or the directory holding it (REQ-1124, REQ-1142).
fn unnamed_files(root: &Path, core: &Path, text: &str) -> Vec<String> {
    let Some(dir) = core.parent() else {
        return Vec::new();
    };
    let mut files = Vec::new();
    walk(dir, &mut files);
    let mut out = Vec::new();
    for file in files {
        if file == core {
            continue;
        }
        let rel = file
            .strip_prefix(dir)
            .unwrap_or(&file)
            .to_string_lossy()
            .replace('\\', "/");
        let name = file
            .file_name()
            .map(|n| n.to_string_lossy().to_string())
            .unwrap_or_default();
        let parent = rel
            .rsplit_once('/')
            .map(|(p, _)| format!("{p}/"))
            .unwrap_or_default();
        let named = text.contains(&rel)
            || text.contains(&name)
            || (!parent.is_empty() && text.contains(&parent));
        if !named {
            out.push(format!(
                "{}: {rel} is never named by the skill's core, so nothing loads it",
                shown(root, core)
            ));
        }
    }
    out
}

fn has_steps(text: &str) -> bool {
    text.contains("<steps")
}

/// Whether a procedure in the file ends at a named stopping point (REQ-1122).
fn stops(text: &str) -> bool {
    let block = Regex::new(r"(?s)<steps[^>]*>(.*?)</steps>").expect("steps pattern");
    let item = Regex::new(r"(?m)^\d+\. ").expect("item pattern");
    let stopping = Regex::new(r"(?i)\b(stop|stops|end|ends|report|finish|return|until)\b")
        .expect("stop pattern");
    block.captures_iter(text).any(|c| {
        let steps = &c[1];
        let last = item
            .find_iter(steps)
            .last()
            .map(|m| &steps[m.start()..])
            .unwrap_or(steps);
        stopping.is_match(last)
    })
}

/// The platform's cap on a skill's or agent's description, in characters.
const CAP: usize = 1536;

/// `meow-author cost`: what each unit keeps in context on every turn against
/// its budget, with each skill's use left to the platform's `/skill-doctor`
/// (ADR-1460).
fn cost(args: &[String]) -> u8 {
    if !args.is_empty() {
        eprintln!("usage: meow-author cost");
        return USAGE;
    }
    let root = profile::repository_root();
    let mut units: Vec<PathBuf> = std::fs::read_dir(root.join("plugins"))
        .map(|entries| {
            entries
                .flatten()
                .map(|e| e.path())
                .filter(|p| p.join(".claude-plugin").join("plugin.json").is_file())
                .collect()
        })
        .unwrap_or_default();
    units.sort();
    if units.is_empty() {
        println!("meow-author cost: unchecked: no unit was found under plugins/");
        return UNCHECKED;
    }
    let mut failures = Vec::new();
    for unit in &units {
        let name = unit
            .file_name()
            .map(|n| n.to_string_lossy().to_string())
            .unwrap_or_default();
        let pieces = permanent(unit);
        for (path, size) in &pieces {
            if path.extension().is_some_and(|e| e == "md")
                && !path.to_string_lossy().contains("output-styles")
                && *size > CAP
            {
                failures.push(format!(
                    "{}: description is {size} characters, over the cap of {CAP}",
                    shown(&root, path)
                ));
            }
        }
        let total: usize = pieces.iter().map(|(_, size)| size).sum();
        match ceiling(unit) {
            Some(budget) => {
                println!("{name}: {total} of {budget} characters on every turn");
                if total > budget {
                    failures.push(format!("{name}: loads {total} characters on every turn, {} over its budget of {budget}", total - budget));
                }
            }
            None => {
                println!("{name}: {total} characters on every turn, and no budget");
                failures.push(format!("{name}: states no budget in budget.toml"));
            }
        }
    }
    for failure in &failures {
        println!("{failure}");
    }
    println!(
        "{} units, {} budget failure{}",
        units.len(),
        failures.len(),
        if failures.len() == 1 { "" } else { "s" }
    );
    println!(
        "How often each skill is used: run /skill-doctor in Claude Code, which reports each skill's cost and invocations."
    );
    if failures.is_empty() { CLEAN } else { FOUND }
}

/// Each piece of a unit that loads on every turn, with its characters: the
/// description and `when_to_use` of each skill and agent the model can load,
/// and the whole of each output style.
fn permanent(unit: &Path) -> Vec<(PathBuf, usize)> {
    let mut pieces = Vec::new();
    let mut listed = Vec::new();
    if let Ok(skills) = std::fs::read_dir(unit.join("skills")) {
        for skill in skills.flatten() {
            listed.push(skill.path().join("SKILL.md"));
        }
    }
    let mut agents = Vec::new();
    walk(&unit.join("agents"), &mut agents);
    listed.extend(
        agents
            .into_iter()
            .filter(|p| p.extension().is_some_and(|e| e == "md")),
    );
    listed.sort();
    for path in listed {
        let Ok(text) = std::fs::read_to_string(&path) else {
            continue;
        };
        // A skill only a person can invoke isn't listed to the model.
        if field(&text, "disable-model-invocation") == "true" {
            continue;
        }
        let words: Vec<String> = ["description", "when_to_use"]
            .iter()
            .map(|key| {
                field(&text, key)
                    .trim_matches(|c| c == '"' || c == '\'')
                    .to_string()
            })
            .filter(|v| !v.is_empty())
            .collect();
        pieces.push((path, words.join(" ").chars().count()));
    }
    let mut styles = Vec::new();
    walk(&unit.join("output-styles"), &mut styles);
    styles.sort();
    for path in styles {
        let size = std::fs::read_to_string(&path)
            .map(|t| t.chars().count())
            .unwrap_or(0);
        pieces.push((path, size));
    }
    pieces
}

fn ceiling(unit: &Path) -> Option<usize> {
    let text = std::fs::read_to_string(unit.join("budget.toml")).ok()?;
    let table: toml::Table = text.parse().ok()?;
    table
        .get("permanent_characters")?
        .as_integer()
        .map(|n| n as usize)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_heading_and_an_unknown_tag_are_found() {
        let found = vocabulary(
            "---\nname: x\n---\n\n<role>\nA.\n</role>\n\n## H\n\n<context>\nB.\n</context>\n",
            "x",
        );
        assert!(found.iter().any(|f| f.contains("a Markdown heading")));
        assert!(
            found
                .iter()
                .any(|f| f.contains("<context> is not in the vocabulary"))
        );
    }

    #[test]
    fn a_procedure_names_where_it_stops() {
        assert!(stops("<steps>\n1. Do it.\n2. Report and stop.\n</steps>"));
        assert!(!stops("<steps>\n1. Do it.\n2. Do more.\n</steps>"));
    }

    #[test]
    fn a_variable_anchors_a_climbing_path() {
        assert!(
            unanchored_paths(
                "<steps>\n1. Run `${CLAUDE_SKILL_DIR}/../../bin/x`.\n</steps>",
                "x"
            )
            .is_empty()
        );
        assert_eq!(
            unanchored_paths("<steps>\n1. Run `../../bin/x`.\n</steps>", "x").len(),
            1
        );
    }
}
