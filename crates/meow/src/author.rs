// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-author check`: the harness's own kind of material holds the form
//! SPC-1030 states, in this repository's units or in any directory a
//! repository points it at (ADR-1450).

use crate::profile;
use regex::Regex;
use std::path::{Path, PathBuf};
use yaml_rust2::{Yaml, YamlLoader};

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
/// The model aliases the platform documents (SPC-1030, RES-0284).
const MODEL_ALIASES: [&str; 4] = ["sonnet", "opus", "haiku", "fable"];
const EFFORTS: [&str; 5] = ["low", "medium", "high", "xhigh", "max"];
/// The tools that dispatch another agent, `Task` being the older name.
const DISPATCHING: [&str; 2] = ["Agent", "Task"];
/// The four outcomes an agent a unit ships reports (SPC-1030 "What an agent
/// reports", REQ-0816).
const OUTCOMES: [&str; 4] = ["DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED"];

/// What the subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 1] = [crate::help::Entry {
    name: "check",
    determines: "whether each skill, agent, output style and prompt hook follows the authoring rules",
    by_hand: "read each file against the rules of the `write` skill of `meow-author`, and each `hooks/hooks.json` against the answer, network and launcher rules of SPC-1240",
    lines: "meow-author <path> <count>",
    json: "",
}];

pub fn main(args: &[String]) -> u8 {
    if let Some(code) = crate::help::answer("meow-author", &HELP, args) {
        return code;
    }
    match args.split_first() {
        Some((command, paths)) if command == "check" => check(paths),
        _ => {
            eprintln!("usage: meow-author check [path...]");
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
        let shipped = ships(unit);
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
                failures.extend(description_leads(&text, &where_));
                if has_steps(&text) && !stops(&text) {
                    failures.push(format!(
                        "{where_}: has a procedure and no step naming where it stops"
                    ));
                }
            }
            if is_agent {
                failures.extend(agent_fields(&text, &where_, shipped));
            }
            if is_agent && shipped {
                failures.extend(missing_outcomes(&text, &where_));
            }
            if is_core {
                failures.extend(unnamed_files(&root, &path, &text));
            }
        }
        for (where_, prompt) in hook_prompts(&root, unit) {
            files += 1;
            failures.extend(vocabulary(&prompt, &where_));
        }
        if shipped {
            failures.extend(manifest_rules(&root, unit));
            failures.extend(tool_steps(&root, unit));
            for (path, size) in permanent(&unit_root(unit)) {
                if path.extension().is_some_and(|e| e == "md")
                    && !path.to_string_lossy().contains("output-styles")
                    && size > CAP
                {
                    failures.push(format!(
                        "{}: description is {size} characters, over the cap of {CAP}",
                        shown(&root, &path)
                    ));
                }
            }
        }
        let (hooks, broken) = hook_rules(&root, unit);
        files += hooks;
        failures.extend(broken);
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

/// The directory a check on a unit's own file reads the unit from: the nearest
/// ancestor that carries a plugin manifest, or the path itself where it is
/// already a directory of one.
fn unit_root(unit: &Path) -> PathBuf {
    let mut dir = unit.to_path_buf();
    if dir.is_file() {
        dir = dir.parent().map(|p| p.to_path_buf()).unwrap_or(dir);
    }
    let mut walk = dir.clone();
    loop {
        if walk.join(".claude-plugin").join("plugin.json").is_file()
            || walk
                .parent()
                .and_then(|p| p.file_name())
                .is_some_and(|n| n == "plugins")
        {
            return walk;
        }
        match walk.parent() {
            Some(parent) => walk = parent.to_path_buf(),
            None => return dir,
        }
    }
}

/// Whether a directory is a unit the harness ships, rather than a
/// repository's own material such as `.claude/`: it sits in a `plugins/`
/// directory or carries a plugin manifest.
fn ships(unit: &Path) -> bool {
    let absolute = unit.canonicalize().unwrap_or_else(|_| unit.to_path_buf());
    absolute
        .parent()
        .and_then(|p| p.file_name())
        .is_some_and(|n| n == "plugins")
        || unit.join(".claude-plugin").join("plugin.json").is_file()
}

/// Each defect in the six fields an agent declares, as SPC-1030 states them
/// under "What an agent declares" (REQ-2974, REQ-2982, REQ-2984, REQ-2988,
/// REQ-3270). Front matter that doesn't parse is the only failure reported,
/// because no field can be read from it.
fn agent_fields(text: &str, where_: &str, shipped: bool) -> Vec<String> {
    let Some(front) = front_matter(text) else {
        return Vec::new();
    };
    let map = match YamlLoader::load_from_str(front) {
        Ok(docs) => match docs.into_iter().next() {
            Some(Yaml::Hash(map)) => map,
            Some(Yaml::Null) | None => Default::default(),
            Some(_) => {
                return vec![format!(
                    "{where_}: its front matter doesn't parse: it isn't a mapping of fields"
                )];
            }
        },
        Err(error) => {
            return vec![format!("{where_}: its front matter doesn't parse: {error}")];
        }
    };
    let get = |key: &str| map.get(&Yaml::String(key.to_string()));
    let mut out = Vec::new();
    let mut fail = |field: &str, why: &str| out.push(format!("{where_}: {field} {why}"));
    match get("maxTurns") {
        None => fail(
            "maxTurns",
            "is missing, where a positive integer caps the agent's turns",
        ),
        Some(Yaml::Integer(n)) if *n > 0 => {}
        Some(_) => fail("maxTurns", "is not a positive integer"),
    }
    match get("tools") {
        None => fail(
            "tools",
            "is missing, where a written list names every tool the agent holds",
        ),
        Some(value) => match tool_names(value) {
            None => fail(
                "tools",
                "is not a list or a comma-separated string of tool names",
            ),
            Some(names) if shipped => {
                if names.iter().any(|n| {
                    n == "*"
                        || DISPATCHING
                            .iter()
                            .any(|d| n == d || n.starts_with(&format!("{d}(")))
                }) {
                    fail(
                        "tools",
                        "holds *, Agent or Task, where an agent a unit ships dispatches no other agent",
                    );
                }
            }
            Some(_) => {}
        },
    }
    match get("model") {
        None => fail(
            "model",
            "is missing, where sonnet, opus, haiku, fable or a claude- identifier belongs",
        ),
        Some(Yaml::String(m)) if MODEL_ALIASES.contains(&m.as_str()) || m.contains("claude-") => {}
        Some(Yaml::String(m)) if m == "inherit" => fail(
            "model",
            "is inherit, which leaves the cost to whichever session dispatches the agent",
        ),
        Some(_) => fail(
            "model",
            "is not sonnet, opus, haiku, fable or an identifier containing claude-",
        ),
    }
    match get("effort") {
        None => fail(
            "effort",
            "is missing, where low, medium, high, xhigh or max belongs",
        ),
        Some(Yaml::String(e)) if EFFORTS.contains(&e.as_str()) => {}
        Some(_) => fail("effort", "is not low, medium, high, xhigh or max"),
    }
    match get("omitClaudeMd") {
        None => fail(
            "omitClaudeMd",
            "is missing, where true or false is written out",
        ),
        Some(Yaml::Boolean(_)) => {}
        Some(_) => fail("omitClaudeMd", "is not true or false"),
    }
    match get("skills") {
        None => fail(
            "skills",
            "is missing, where a list of the skills the agent preloads belongs, empty included",
        ),
        Some(Yaml::Array(items)) if items.iter().all(|i| matches!(i, Yaml::String(_))) => {}
        Some(_) => fail("skills", "is not a list of skill names"),
    }
    out
}

/// One failure for each of the four outcomes an agent's body doesn't name,
/// each read as a whole word, so `DONE_WITH_CONCERNS` doesn't name `DONE`
/// (SPC-1030 "The check", REQ-0816). Only an agent a unit ships is read,
/// because a repository's own agent follows no outcome rule.
fn missing_outcomes(text: &str, where_: &str) -> Vec<String> {
    let (body, _) = body(text);
    OUTCOMES
        .iter()
        .filter(|word| {
            let whole = Regex::new(&format!(r"(^|[^A-Za-z_]){word}($|[^A-Za-z_])"))
                .expect("outcome pattern");
            !whole.is_match(body)
        })
        .map(|word| {
            format!(
                "{where_}: its body doesn't name the outcome {word}, where an agent a unit ships names all four it may report"
            )
        })
        .collect()
}

/// The tool names a `tools` value holds, read as a YAML list or as a
/// comma-separated string, or nothing where it is neither.
fn tool_names(value: &Yaml) -> Option<Vec<String>> {
    match value {
        Yaml::Array(items) => items
            .iter()
            .map(|i| i.as_str().map(|s| s.trim().to_string()))
            .collect(),
        Yaml::String(s) => Some(
            s.split(',')
                .map(|n| n.trim().to_string())
                .filter(|n| !n.is_empty())
                .collect(),
        ),
        _ => None,
    }
}

/// The text between a file's opening and closing `---` lines.
fn front_matter(text: &str) -> Option<&str> {
    let rest = text.strip_prefix("---\n")?;
    let end = rest.find("\n---\n")?;
    Some(&rest[..end])
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

/// The tools a comma-separated string names, split at the commas outside
/// parentheses, so `Bash(git status:*)` stays one entry.
fn split_tools(list: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut current = String::new();
    let mut depth = 0usize;
    for c in list.chars() {
        match c {
            '(' => {
                depth += 1;
                current.push(c);
            }
            ')' => {
                depth = depth.saturating_sub(1);
                current.push(c);
            }
            ',' if depth == 0 => out.push(std::mem::take(&mut current)),
            c => current.push(c),
        }
    }
    out.push(current);
    out.into_iter()
        .map(|t| t.trim().to_string())
        .filter(|t| !t.is_empty())
        .collect()
}

/// Each tool an agent's `tools` or a skill's `allowed-tools` grants, which the
/// unit's README names no step for under `## Tools`, naming the file, the tool
/// and the README (REQ-1430, REQ-1432, SPC-1030 "What a unit declares").
///
/// The README names a step in a list item, `` - `Tool`: what the step does ``,
/// and a tool with no text after its colon names none.
fn tool_steps(root: &Path, unit: &Path) -> Vec<String> {
    let readme = std::fs::read_to_string(unit.join("README.md")).unwrap_or_default();
    let mut named = std::collections::BTreeSet::new();
    let mut inside = false;
    let mut fenced = false;
    for line in readme.lines() {
        if line.trim_start().starts_with("```") || line.trim_start().starts_with("~~~") {
            fenced = !fenced;
        }
        if !fenced && line.starts_with("## ") {
            inside = line.trim() == "## Tools";
            continue;
        }
        if inside
            && !fenced
            && let Some(item) = line.strip_prefix("- `")
            && let Some((tool, rest)) = item.split_once("`:")
            && !rest.trim().is_empty()
        {
            named.insert(tool.trim().to_string());
        }
    }
    let mut files = Vec::new();
    walk(&unit.join("agents"), &mut files);
    walk(&unit.join("skills"), &mut files);
    files.retain(|p| p.extension().is_some_and(|e| e == "md"));
    files.sort();
    let mut out = Vec::new();
    for path in files {
        let is_skill = path.file_name().is_some_and(|n| n == "SKILL.md");
        let is_agent = path
            .parent()
            .and_then(|p| p.file_name())
            .is_some_and(|n| n == "agents");
        if !is_skill && !is_agent {
            continue;
        }
        let text = std::fs::read_to_string(&path).unwrap_or_default();
        let Some(front) = front_matter(&text) else {
            continue;
        };
        let Ok(docs) = YamlLoader::load_from_str(front) else {
            continue;
        };
        let Some(Yaml::Hash(map)) = docs.into_iter().next() else {
            continue;
        };
        let key = if is_agent { "tools" } else { "allowed-tools" };
        let granted: Vec<String> = match map.get(&Yaml::String(key.to_string())) {
            Some(Yaml::Array(items)) => items
                .iter()
                .filter_map(|i| i.as_str().map(str::to_string))
                .collect(),
            Some(Yaml::String(list)) => split_tools(list),
            _ => Vec::new(),
        };
        for tool in granted {
            // `Bash(git status:*)` grants the tool `Bash` for a pattern.
            let name = tool.split('(').next().unwrap_or("").trim().to_string();
            if name.is_empty() || named.contains(&name) {
                continue;
            }
            out.push(format!(
                "{}: grants `{name}`, and {} names no step for it under `## Tools`",
                shown(root, &path),
                shown(root, &unit.join("README.md"))
            ));
        }
    }
    out
}

/// The longest timeout, in seconds, a prose gate hook may wait on its judge
/// under ADR-2390's bound.
const JUDGE_BOUND: f64 = 120.0;

/// Events whose hook can't stop a call or the turn, and so are free of the
/// launcher rule: one that runs when a session opens or closes, and one that
/// runs after a tool already ran (REQ-2716). Every other event, a new one
/// included, is held to the rule, because an unlisted event that can stop the
/// turn must not slip through.
const HARMLESS_EVENTS: [&str; 4] = [
    "SessionStart",
    "SessionEnd",
    "PostToolUse",
    "PostToolUseFailure",
];

/// The tokens of a command, with a double-quoted run kept as one token and its
/// quotes dropped, so a path with a space stays whole.
fn command_tokens(command: &str) -> Vec<String> {
    let mut tokens = Vec::new();
    let mut current = String::new();
    let mut quoted = false;
    let mut started = false;
    for c in command.chars() {
        match c {
            '"' => {
                quoted = !quoted;
                started = true;
            }
            c if c.is_whitespace() && !quoted => {
                if started {
                    tokens.push(std::mem::take(&mut current));
                    started = false;
                }
            }
            c => {
                current.push(c);
                started = true;
            }
        }
    }
    if started {
        tokens.push(current);
    }
    tokens
}

/// The command hooks of a unit held to the rules SPC-1240 states under "The
/// check" (REQ-2716, REQ-2718, REQ-2720, REQ-2726, REQ-2727): no `allow`
/// decision, no `updatedInput`, no network command, a hook that can stop a call
/// that is the unit's launcher with one subcommand, and a sentence for it under
/// the README's `## Hooks`. It returns how many hooks it read and each failure.
///
/// The prose gate's `check` is excused from one network word, `claude -p`, the
/// judge's call, on `PreToolUse`, named here by unit and subcommand so no other
/// hook inherits it, and only while its hook's timeout is at most
/// `JUDGE_BOUND` seconds (ADR-2700).
fn hook_rules(root: &Path, unit: &Path) -> (usize, Vec<String>) {
    let path = unit.join("hooks").join("hooks.json");
    let Ok(text) = std::fs::read_to_string(&path) else {
        return (0, Vec::new());
    };
    let where_file = shown(root, &path);
    let config = match serde_json::from_str::<serde_json::Value>(&text) {
        Ok(config) => config,
        Err(error) => {
            return (
                1,
                vec![format!(
                    "{where_file}: doesn't parse, so no hook in it was read: {error}"
                )],
            );
        }
    };
    let unit_name = unit
        .canonicalize()
        .unwrap_or_else(|_| unit.to_path_buf())
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_default();
    let readme = std::fs::read_to_string(unit.join("README.md")).unwrap_or_default();
    let section = hooks_section(&readme);
    let allow = Regex::new(
        r#"(?is)permissionDecision["']?\s*[:=]\s*\\?["']?(?:allow|approve)\b|behavior["']?\s*[:=]\s*\\?["']?allow\b|"decision"\s*:\s*"approve""#,
    )
    .expect("allow pattern");
    let network = Regex::new(
        r#"(?i)(?:^|[\s;&|(`'"=])(?:(?:curl|wget|ssh|scp|sftp|rsync|ncat|nc|telnet)\b|gh\s+\S|git\s+(?:fetch|pull|clone|ls-remote|push|remote\s+update|submodule\s+update)\b|claude\s+(?:-\S+\s+)*(?:-p|--print)\b)"#,
    )
    .expect("network pattern");
    let judge = Regex::new(r"(?i)^claude\s+(?:-\S+\s+)*(?:-p|--print)$").expect("judge pattern");
    let launcher =
        Regex::new(r"^\$\{CLAUDE_PLUGIN_ROOT\}/bin/([A-Za-z0-9._-]+)$").expect("launcher pattern");
    let mut count = 0;
    let mut out = Vec::new();
    let Some(events) = config.get("hooks").and_then(|h| h.as_object()) else {
        return (
            1,
            vec![format!(
                "{where_file}: has no `hooks` table, so no hook in it was read"
            )],
        );
    };
    for (event, groups) in events {
        for group in groups.as_array().into_iter().flatten() {
            for hook in group
                .get("hooks")
                .and_then(|h| h.as_array())
                .into_iter()
                .flatten()
            {
                let kind = hook
                    .get("type")
                    .and_then(|t| t.as_str())
                    .unwrap_or("command");
                let where_ = format!("{where_file} ({event})");
                if kind == "prompt" {
                    continue;
                }
                count += 1;
                if kind != "command" {
                    out.push(format!(
                        "{where_}: a `{kind}` hook can't be read by this check, and a hook that isn't a command reaches somewhere nobody can see (REQ-2727)"
                    ));
                    continue;
                }
                let command = hook
                    .get("command")
                    .and_then(|c| c.as_str())
                    .unwrap_or_default();
                let tokens = command_tokens(command);
                let mut haystack = command.to_string();
                for token in &tokens {
                    if token.contains("${CLAUDE_PLUGIN_ROOT}") {
                        let file = PathBuf::from(
                            token.replace("${CLAUDE_PLUGIN_ROOT}", &unit.display().to_string()),
                        );
                        if let Ok(bytes) = std::fs::read(&file)
                            && let Ok(script) = String::from_utf8(bytes)
                        {
                            haystack.push('\n');
                            haystack.push_str(&script);
                        }
                    }
                }
                // The launcher with one subcommand, and any flags it takes.
                let shaped = tokens
                    .first()
                    .and_then(|t| launcher.captures(t))
                    .filter(|_| {
                        tokens.len() >= 2
                            && tokens[1..2].iter().all(|w| !w.starts_with('-'))
                            && tokens[2..].iter().all(|w| w.starts_with('-'))
                            && !command.contains(['|', ';', '&', '<', '>', '`'])
                    });
                let name = match &shaped {
                    Some(_) => tokens[1].clone(),
                    None => tokens
                        .iter()
                        .find(|t| t.contains("${CLAUDE_PLUGIN_ROOT}"))
                        .and_then(|t| Path::new(t).file_name())
                        .map(|n| n.to_string_lossy().to_string())
                        .or_else(|| tokens.first().cloned())
                        .unwrap_or_default(),
                };
                let judge_call = unit_name == "meow-prose-gate"
                    && event == "PreToolUse"
                    && shaped.is_some()
                    && tokens.get(1).is_some_and(|w| w == "check");
                if allow.is_match(&haystack) {
                    out.push(format!(
                        "{where_}: `{name}` answers `allow`, which skips the permission flow the repository owns (REQ-2720)"
                    ));
                }
                if haystack.contains("updatedInput") {
                    out.push(format!(
                        "{where_}: `{name}` returns an `updatedInput`, where it denies with the reason and lets the model redo the call (REQ-2718)"
                    ));
                }
                // The judge waits inside the hook's timeout, which ADR-2390
                // bounds at 120 seconds, so an unbounded gate loses the
                // exception (ADR-2700).
                let bounded = hook
                    .get("timeout")
                    .and_then(|t| t.as_f64())
                    .is_some_and(|t| t > 0.0 && t <= JUDGE_BOUND);
                for found in network.find_iter(&haystack) {
                    if judge_call && judge.is_match(found.as_str().trim()) {
                        if bounded {
                            continue;
                        }
                        out.push(format!(
                            "{where_}: `{name}` waits on the judge `{}` without a timeout of at most {JUDGE_BOUND} seconds, the bound ADR-2390 sets (REQ-2716, REQ-2727)",
                            found.as_str().trim()
                        ));
                        break;
                    }
                    out.push(format!(
                        "{where_}: `{name}` names the network command `{}`, and no hook reaches the network (REQ-2727)",
                        found.as_str().trim()
                    ));
                    break;
                }
                if !HARMLESS_EVENTS.contains(&event.as_str()) {
                    let ours = shaped
                        .as_ref()
                        .is_some_and(|found| unit.join("bin").join(&found[1]).is_file());
                    if !ours {
                        out.push(format!(
                            "{where_}: a hook that can stop a call or the turn runs the unit's launcher with one subcommand, and `{command}` isn't that (REQ-2716)"
                        ));
                    }
                }
                if !section.split('`').skip(1).step_by(2).any(|span| {
                    span.trim() == name || span.split_whitespace().any(|word| word == name)
                }) {
                    out.push(format!(
                        "{where_}: `{name}` has no sentence under `## Hooks` in {} (REQ-2726)",
                        shown(root, &unit.join("README.md"))
                    ));
                }
            }
        }
    }
    (count, out)
}

/// The text under a README's `## Hooks` heading, up to the next heading of its
/// level, or none where it has no such heading.
fn hooks_section(readme: &str) -> String {
    let mut inside = false;
    let mut out = String::new();
    let mut fenced = false;
    for line in readme.lines() {
        if line.trim_start().starts_with("```") {
            fenced = !fenced;
        }
        if !fenced && line.starts_with("## ") {
            inside = line.trim() == "## Hooks";
            continue;
        }
        if inside {
            out.push_str(line);
            out.push('\n');
        }
    }
    out
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
    if let Some(rest) = text.strip_prefix("---\n")
        && let Some(end) = rest.find("\n---\n")
    {
        let cut = 4 + end + 5;
        return (&text[cut..], text[..cut].matches('\n').count());
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

/// The defect in a description that leads with none of the words its
/// `when_to_use` names (REQ-3050): a request reaches a unit through those
/// words. `when_to_use` names a word by writing it in code font, and a word
/// matches when a word of the description's first sentence starts with it, so
/// `commit` is met by `commits`. A unit with no `when_to_use`, or none in code
/// font, has no word to read, so the rule passes it.
fn description_leads(text: &str, where_: &str) -> Vec<String> {
    let when = field(text, "when_to_use");
    let named = Regex::new(r"`([A-Za-z][A-Za-z-]*)`").expect("code font pattern");
    let mut words: Vec<String> = Vec::new();
    for capture in named.captures_iter(&when) {
        let word = capture[1].to_lowercase();
        if !words.contains(&word) {
            words.push(word);
        }
    }
    let description = field(text, "description");
    let description = description.trim_matches(|c| c == '"' || c == '\'');
    if words.is_empty() || description.is_empty() {
        return Vec::new();
    }
    let first = Regex::new(r"[.!?](\s|$)")
        .expect("sentence end pattern")
        .find(description)
        .map_or(description, |end| &description[..end.start()])
        .to_lowercase();
    let carried = Regex::new(r"[a-z][a-z-]*")
        .expect("word pattern")
        .find_iter(&first)
        .any(|w| {
            words
                .iter()
                .any(|word| w.as_str().starts_with(word.as_str()))
        });
    if carried {
        return Vec::new();
    }
    vec![format!(
        "{where_}: description's first sentence carries none of the words when_to_use names: {}",
        words.join(", ")
    )]
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

/// The four layers a unit ships in, as SPC-1080 states them under "Each unit
/// is a plugin".
const LAYERS: [&str; 4] = ["kernel", "method", "practice", "pack"];

/// Each defect in a unit's manifest, as SPC-1080 states under "Each unit is a
/// plugin" (REQ-1482, REQ-2990, REQ-2998, REQ-3006): a version in the plugin
/// manifest, a requires.toml naming `layer` and `units`, a `kernel` range in a
/// pack, and, for each unit `units` names, a README that says the platform
/// enables it and keeps it enabled while this unit is on.
fn manifest_rules(root: &Path, unit: &Path) -> Vec<String> {
    let name = shown(root, unit);
    let mut out = Vec::new();
    let plugin = unit.join(".claude-plugin").join("plugin.json");
    let version = std::fs::read_to_string(&plugin)
        .ok()
        .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok())
        .and_then(|value| {
            value
                .get("version")
                .and_then(|v| v.as_str())
                .map(str::to_string)
        });
    match version {
        Some(v) if !v.is_empty() => {}
        _ => out.push(format!(
            "{}: has no version, where every unit the harness ships carries one (REQ-2990)",
            shown(root, &plugin)
        )),
    }
    let requires = unit.join("requires.toml");
    let text = match std::fs::read_to_string(&requires) {
        Ok(text) => text,
        Err(_) => {
            out.push(format!(
                "{name}: has no {}, which states its platform version, layer, units and kernel range (REQ-1482)",
                shown(root, &requires)
            ));
            return out;
        }
    };
    let where_ = shown(root, &requires);
    let table = match text.parse::<toml::Table>() {
        Ok(table) => table,
        Err(error) => {
            out.push(format!("{where_}: doesn't parse: {error}"));
            return out;
        }
    };
    let layer = match table.get("layer") {
        Some(toml::Value::String(layer)) if LAYERS.contains(&layer.as_str()) => {
            Some(layer.as_str())
        }
        Some(toml::Value::String(layer)) => {
            out.push(format!(
                "{where_}: layer is `{layer}`, where the unit states kernel, method, practice or pack"
            ));
            None
        }
        Some(_) => {
            out.push(format!(
                "{where_}: layer is not a string naming kernel, method, practice or pack"
            ));
            None
        }
        None => {
            out.push(format!(
                "{where_}: has no layer, where the unit states kernel, method, practice or pack"
            ));
            None
        }
    };
    let units: Option<Vec<String>> = match table.get("units") {
        Some(toml::Value::Array(items)) => items
            .iter()
            .map(|item| item.as_str().map(str::to_string))
            .collect(),
        Some(_) => {
            out.push(format!(
                "{where_}: units is not a list of unit names, empty where the unit needs none"
            ));
            None
        }
        None => {
            out.push(format!(
                "{where_}: has no units, where the unit states the units it needs, empty where it needs none (REQ-1482)"
            ));
            None
        }
    };
    if layer == Some("pack") && table.get("kernel").is_none() {
        out.push(format!(
            "{where_}: has no kernel, where a pack states the range of meow-core versions it works with (REQ-2998)"
        ));
    }
    let readme = unit.join("README.md");
    let read = std::fs::read_to_string(&readme).unwrap_or_default();
    for required in units.into_iter().flatten() {
        let says = read.contains(&required) && read.contains("enabled");
        if !says {
            out.push(format!(
                "{}: requires {required} and doesn't say the platform enables it and keeps it enabled while this unit is on (REQ-3006)",
                shown(root, &readme)
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

    /// An agent declaring the six fields SPC-1030 states, with `role` as its
    /// body, so the outcome rule is the only one it can fail.
    fn outcome_agent(role: &str) -> String {
        format!(
            "---\nname: reviewer\ndescription: Reviews the demo and reports findings, editing nothing.\n\
             tools: [Read, Grep, Glob]\nmaxTurns: 30\nmodel: opus\neffort: high\n\
             omitClaudeMd: false\nskills: []\n---\n\n<role>\n{role}\n</role>\n"
        )
    }

    /// `meow-author check`'s exit status over one agent written at
    /// `agents/reviewer.md` inside `unit`, which sits in a scratch directory.
    fn check_agent(case: &str, unit: &str, role: &str) -> u8 {
        let dir = std::env::temp_dir().join(format!("meow-author-{case}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        let agents = dir.join(unit).join("agents");
        std::fs::create_dir_all(&agents).unwrap();
        std::fs::write(agents.join("reviewer.md"), outcome_agent(role)).unwrap();
        std::fs::create_dir_all(dir.join(unit).join(".claude-plugin")).unwrap();
        // A unit under `plugins/` carries the manifest files the manifest
        // rules read; a repository's own `.claude/` carries none, because it
        // ships no plugin.
        if unit.ends_with("plugins/meow-demo") {
            std::fs::write(
                dir.join(unit).join(".claude-plugin").join("plugin.json"),
                "{\"name\":\"meow-demo\",\"version\":\"0.1.0\"}",
            )
            .unwrap();
            std::fs::write(dir.join(unit).join("requires.toml"), MANIFEST_REQUIRES).unwrap();
        }
        std::fs::write(
            dir.join(unit).join("README.md"),
            "# demo\n\n## Tools\n\n- `Read`: the review reads the file.\n- `Grep`: the review finds a line.\n- `Glob`: the review lists paths.\n",
        )
        .unwrap();
        let status = check(&[dir.join(unit).display().to_string()]);
        let _ = std::fs::remove_dir_all(&dir);
        status
    }

    const ALL_FOUR: &str = "You review the demo and end with outcome: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT or BLOCKED.";

    /// The requires.toml a complete fixture unit carries.
    const MANIFEST_REQUIRES: &str = "claude_code = \"2.0.0\"\nlayer = \"practice\"\nunits = []\n";

    /// A fixture unit carrying the manifest files the manifest rules read: a
    /// version in its plugin manifest, a requires.toml and a README. Each file
    /// named is replaced; each left alone keeps its default.
    fn manifest_check(
        case: &str,
        plugin: Option<&str>,
        requires: Option<&str>,
        readme: Option<&str>,
    ) -> u8 {
        let root = std::env::temp_dir().join(format!(
            "meow-author-manifest-{case}-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&root);
        let unit = root.join("plugins").join("meow-demo");
        std::fs::create_dir_all(unit.join(".claude-plugin")).unwrap();
        std::fs::write(
            unit.join(".claude-plugin").join("plugin.json"),
            plugin.unwrap_or("{\"name\":\"meow-demo\",\"version\":\"0.1.0\"}"),
        )
        .unwrap();
        if let Some(requires) = requires {
            std::fs::write(unit.join("requires.toml"), requires).unwrap();
        }
        std::fs::write(unit.join("README.md"), readme.unwrap_or("# meow-demo\n")).unwrap();
        // A skill, so the check reads prompt material and reports a pass as
        // clean instead of unresolved (unresolved is never a pass).
        let skill = unit.join("skills").join("demo");
        std::fs::create_dir_all(&skill).unwrap();
        std::fs::write(
            skill.join("SKILL.md"),
            "---\nname: demo\ndescription: The demo skill. It MUST be loaded before a demo is run.\n---\n\n<role>\nYou run the demo.\n</role>\n\n<steps name=\"demo\">\n1. Run the demo, report what it printed, and stop.\n</steps>\n",
        )
        .unwrap();
        let status = check(&[unit.display().to_string()]);
        let _ = std::fs::remove_dir_all(&root);
        status
    }

    #[test]
    fn a_unit_without_requires_toml_fails() {
        // TSK-4390 criterion 1, REQ-1482: a unit with no requires.toml fails.
        assert_eq!(manifest_check("norequires", None, None, None), FOUND);
    }

    #[test]
    fn a_unit_without_a_version_fails() {
        // TSK-4390 criterion 2, REQ-2990: a plugin manifest with no version
        // fails.
        assert_eq!(
            manifest_check(
                "noversion",
                Some("{\"name\":\"meow-demo\"}"),
                Some(MANIFEST_REQUIRES),
                None
            ),
            FOUND
        );
    }

    #[test]
    fn a_pack_without_a_kernel_range_fails() {
        // TSK-4390 criterion 3, REQ-2998: a pack with no kernel fails.
        assert_eq!(
            manifest_check(
                "nokernel",
                None,
                Some("claude_code = \"2.0.0\"\nlayer = \"pack\"\nunits = []\n"),
                None
            ),
            FOUND
        );
    }

    #[test]
    fn a_unit_without_a_layer_or_units_fails() {
        // SPC-1080 "Each unit is a plugin": the check fails a unit with no
        // layer or no units, a pack with no kernel range included.
        assert_eq!(
            manifest_check(
                "nolayer",
                None,
                Some("claude_code = \"2.0.0\"\nunits = []\n"),
                None
            ),
            FOUND
        );
        assert_eq!(
            manifest_check(
                "nounits",
                None,
                Some("claude_code = \"2.0.0\"\nlayer = \"practice\"\n"),
                None
            ),
            FOUND
        );
    }

    #[test]
    fn a_unit_requiring_another_says_the_platform_enables_it() {
        // TSK-4390 criterion 5, REQ-3006: a README that doesn't state the
        // enabling fails, and one that does passes.
        assert_eq!(
            manifest_check(
                "requiressilent",
                None,
                Some("claude_code = \"2.0.0\"\nlayer = \"practice\"\nunits = [\"meow-scm\"]\n"),
                Some("# meow-demo\n"),
            ),
            FOUND
        );
        assert_eq!(
            manifest_check(
                "requiresstated",
                None,
                Some("claude_code = \"2.0.0\"\nlayer = \"practice\"\nunits = [\"meow-scm\"]\n"),
                Some(
                    "# meow-demo\n\nInstalling this unit enables `meow-scm`, and the platform keeps `meow-scm` enabled while this unit is on.\n"
                ),
            ),
            CLEAN
        );
    }

    #[test]
    fn a_unit_with_a_complete_manifest_passes() {
        // TSK-4390 criteria 1 to 3: a unit carrying every key the rules read
        // passes.
        assert_eq!(
            manifest_check("complete", None, Some(MANIFEST_REQUIRES), None),
            CLEAN
        );
    }

    #[test]
    fn a_unit_agent_naming_no_outcome_fails() {
        // TSK-2702 criterion 1, REQ-0816: a unit's agent naming none of the
        // four outcomes fails (SPC-1030 "The check").
        assert_eq!(
            check_agent("none", "plugins/meow-demo", "You review the demo."),
            FOUND
        );
    }

    #[test]
    fn a_unit_agent_missing_only_blocked_fails() {
        // TSK-2702 criterion 1, REQ-0816: a unit's agent naming three of the
        // four outcomes, all but BLOCKED, fails.
        assert_eq!(
            check_agent(
                "three",
                "plugins/meow-demo",
                "You review the demo and end with outcome: DONE, DONE_WITH_CONCERNS or NEEDS_CONTEXT."
            ),
            FOUND
        );
    }

    #[test]
    fn a_unit_agent_naming_all_four_passes() {
        // TSK-2702 criterion 1, REQ-0816: a unit's agent naming all four
        // outcomes passes.
        assert_eq!(check_agent("four", "plugins/meow-demo", ALL_FOUR), CLEAN);
    }

    #[test]
    fn a_repository_agent_naming_no_outcome_passes() {
        // TSK-2702 criterion 1, REQ-0816: a repository's own agent under
        // `.claude/agents/` isn't read for the outcome rule.
        assert_eq!(check_agent("own", ".claude", "You review the demo."), CLEAN);
    }
}
