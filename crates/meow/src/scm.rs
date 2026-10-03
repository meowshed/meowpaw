// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Check a commit message against the convention the repository declares.
//!
//! SPC-1050 states the behaviour. The convention sits under `[commits]` in the
//! profile (REQ-1290): the types with their release meaning (REQ-1318), the
//! subject limit (REQ-1302) and the trailers every message carries (REQ-1308,
//! REQ-1310). The attribution check runs whatever the profile says, because
//! the ban admits no exception (REQ-1294, REQ-1295). A message is never
//! reported as meeting a convention nobody declared (REQ-1314). The first
//! sign-off names the author (REQ-2206), a trailer naming a person needs them
//! under `may_name` (REQ-2208), and a break says what breaks (REQ-2212).

use crate::profile::{self, PROFILE, Profile};
use regex::Regex;
use std::io::Read;
use std::path::Path;

const DEFAULT_LIMIT: i64 = 72;
const MEANINGS: [&str; 4] = ["major", "minor", "patch", "none"];
const KEYS: [&str; 4] = ["types", "subject_limit", "trailers", "may_name"];
const MET: u8 = 0;
const VIOLATED: u8 = 1;
const USAGE: u8 = 2;
const UNDECLARED: u8 = 3;

// A trailer whose value is `Name <address>` names a person (REQ-2208).
const PERSON: &str =
    r"^(?P<key>[A-Za-z][A-Za-z0-9-]*): (?P<value>[^<>]*\S\s*<[^<>\s@]+@[^<>\s]+>)\s*$";
// Two of the three trailers that record where something came from; the third,
// the author's own sign-off, is the first one, which `sign_off` compares.
const PROVENANCE: [&str; 2] = ["fixes", "cherry-picked-from"];
const BREAKING: &str = r"^BREAKING[ -]CHANGE: \S";

const SUBJECT: &str =
    r"^(?P<type>[a-z][a-z0-9-]*)(?:\((?P<scope>[^()\s]+)\))?(?P<bang>!)?: (?P<text>\S.*)$";
// The pattern, never a bare name: a path such as plugins/meow-core/ or the
// product a harness targets is not attribution.
const ATTRIBUTION: &str = concat!(
    r"(?i)co-authored-by:.*\b(claude|anthropic|copilot|openai|chatgpt|gpt-?\d|gemini|codex|cursor|devin|aider)\b",
    r"|generated (with|by) \[?(claude|copilot|chatgpt|gemini|cursor|codex|an? ai)",
    r"|noreply@(anthropic|openai)\.com",
);

struct Convention {
    state: &'static str,
    detail: String,
    types: Vec<(String, String)>,
    limit: i64,
    trailers: Vec<String>,
    may_name: Vec<String>,
    ignored: Vec<String>,
    malformed: Vec<String>,
}

fn convention(root: &Path) -> Convention {
    let mut found = Convention {
        state: "declared",
        detail: String::new(),
        types: Vec::new(),
        limit: DEFAULT_LIMIT,
        trailers: Vec::new(),
        may_name: Vec::new(),
        ignored: Vec::new(),
        malformed: Vec::new(),
    };
    let data = match profile::read(root) {
        Profile::Absent => {
            found.state = "undeclared";
            found.detail = format!("{PROFILE} doesn't exist");
            return found;
        }
        Profile::Unparseable(error) => {
            found.state = "unparseable";
            found.detail = error;
            return found;
        }
        Profile::Parsed(data) => data,
    };
    let table = match data.get("commits") {
        Some(toml::Value::Table(table)) => table,
        _ => {
            found.state = "undeclared";
            found.detail = "the profile has no [commits] table".to_string();
            return found;
        }
    };

    found.ignored = table
        .keys()
        .filter(|key| !KEYS.contains(&key.as_str()))
        .map(|key| format!("commits.{key}"))
        .collect();
    match table.get("types") {
        None => {}
        Some(toml::Value::Table(types)) => {
            for (name, meaning) in types {
                match meaning {
                    toml::Value::String(meaning) if MEANINGS.contains(&meaning.as_str()) => {
                        found.types.push((name.clone(), meaning.clone()));
                    }
                    toml::Value::String(meaning) => found.malformed.push(format!(
                        "type `{name}` means '{meaning}', not one of {}",
                        MEANINGS.join(", ")
                    )),
                    other => found.malformed.push(format!(
                        "type `{name}` means {other}, not one of {}",
                        MEANINGS.join(", ")
                    )),
                }
            }
        }
        Some(_) => found.malformed.push("`types` isn't a table".to_string()),
    }
    match table.get("subject_limit") {
        None => {}
        Some(toml::Value::Integer(limit)) if *limit > 0 => found.limit = *limit,
        Some(_) => found
            .malformed
            .push("`subject_limit` isn't a positive whole number".to_string()),
    }
    match table.get("trailers") {
        None => {}
        Some(toml::Value::Array(items)) if items.iter().all(|item| item.is_str()) => {
            found.trailers = items
                .iter()
                .filter_map(|item| item.as_str().map(str::to_string))
                .collect();
        }
        Some(_) => found
            .malformed
            .push("`trailers` isn't a list of names".to_string()),
    }
    match table.get("may_name") {
        None => {}
        Some(toml::Value::Array(items)) if items.iter().all(|item| item.is_str()) => {
            found.may_name = items
                .iter()
                .filter_map(|item| item.as_str().map(|name| name.trim().to_string()))
                .collect();
        }
        Some(_) => found
            .malformed
            .push("`may_name` isn't a list of people".to_string()),
    }
    found
}

fn report_convention(root: &Path) -> u8 {
    let found = convention(root);
    if found.state != "declared" {
        println!("meow-scm convention: {} ({})", found.state, found.detail);
        return UNDECLARED;
    }
    println!("meow-scm convention, from {PROFILE}\n");
    for (name, meaning) in &found.types {
        println!("type {name:<10} release: {meaning}");
    }
    println!("subject limit  {} characters", found.limit);
    let trailers = if found.trailers.is_empty() {
        "none declared".to_string()
    } else {
        found.trailers.join(", ")
    };
    println!("trailers       {trailers}");
    let named = if found.may_name.is_empty() {
        "nobody listed".to_string()
    } else {
        found.may_name.join(", ")
    };
    println!("may name       {named}");
    for problem in &found.malformed {
        println!("malformed      {problem}");
    }
    if !found.ignored.is_empty() {
        println!("\nNot read by meow-scm: {}", found.ignored.join(", "));
    }
    MET
}

/// Every violation, as (line number, rule, detail), with no author known.
#[cfg(test)]
fn problems(message: &str, found: &Convention) -> Vec<(usize, String, String)> {
    problems_by(message, found, None)
}

/// Every violation, where a sign-off naming `author` names nobody new.
fn problems_by(
    message: &str,
    found: &Convention,
    author: Option<&str>,
) -> Vec<(usize, String, String)> {
    let mut lines: Vec<&str> = message
        .lines()
        .filter(|line| !line.starts_with('#'))
        .collect();
    while lines.last().is_some_and(|line| line.trim().is_empty()) {
        lines.pop();
    }
    if lines.is_empty() || lines[0].trim().is_empty() {
        return vec![(
            1,
            "empty message".into(),
            "the message has no subject".into(),
        )];
    }

    let attribution = Regex::new(ATTRIBUTION).expect("the attribution pattern compiles");
    let mut found_problems = Vec::new();
    for (index, line) in lines.iter().enumerate() {
        if attribution.is_match(line) {
            found_problems.push((
                index + 1,
                "attribution".into(),
                format!("\"{}\" credits a tool, an agent or a vendor", line.trim()),
            ));
        }
    }
    if found.state != "declared" {
        return found_problems;
    }

    let subject = lines[0];
    match Regex::new(SUBJECT)
        .expect("the subject pattern compiles")
        .captures(subject)
    {
        None => found_problems.push((
            1,
            "subject form".into(),
            "the subject isn't `type(scope)!: description`".into(),
        )),
        Some(parts) => {
            let kind = &parts["type"];
            let major = found
                .types
                .iter()
                .any(|(name, meaning)| name == kind && meaning == "major");
            let said = Regex::new(BREAKING).expect("the breaking pattern compiles");
            if (parts.name("bang").is_some() || major)
                && !lines[1..].iter().any(|line| said.is_match(line))
            {
                found_problems.push((
                    1,
                    "breaking mark".into(),
                    "the change breaks an interface and no `BREAKING CHANGE:` trailer says what breaks".into(),
                ));
            }
            if !found.types.is_empty() && !found.types.iter().any(|(name, _)| name == kind) {
                let declared: Vec<&str> =
                    found.types.iter().map(|(name, _)| name.as_str()).collect();
                found_problems.push((
                    1,
                    "declared type".into(),
                    format!("`{kind}` isn't a declared type ({})", declared.join(", ")),
                ));
            }
        }
    }
    let length = subject.chars().count() as i64;
    if length > found.limit {
        found_problems.push((
            1,
            "subject length".into(),
            format!("{length} characters, over the limit of {}", found.limit),
        ));
    }
    if subject.trim_end().ends_with('.') {
        found_problems.push((
            1,
            "subject ending".into(),
            "the subject ends in a full stop".into(),
        ));
    }
    if lines.len() > 1 && !lines[1].trim().is_empty() {
        found_problems.push((
            2,
            "blank line".into(),
            "the body follows the subject with no empty line between them".into(),
        ));
    }
    for trailer in &found.trailers {
        let pattern = Regex::new(&format!(r"^{}: \S", regex::escape(trailer)))
            .expect("a trailer pattern compiles");
        if !lines[1..].iter().any(|line| pattern.is_match(line)) {
            found_problems.push((
                lines.len(),
                "trailer".into(),
                format!("the `{trailer}` trailer is missing"),
            ));
        }
    }
    let person = Regex::new(PERSON).expect("the person pattern compiles");
    let mut first_sign_off = true;
    // Git reads trailers from the last paragraph alone, so a body line names nobody.
    let block = lines
        .iter()
        .rposition(|line| line.trim().is_empty())
        .map_or(lines.len(), |blank| blank + 1);
    for (index, line) in lines.iter().enumerate().skip(block) {
        let Some(parts) = person.captures(line) else {
            continue;
        };
        let key = parts["key"].to_ascii_lowercase();
        if PROVENANCE.contains(&key.as_str()) {
            continue;
        }
        let named = parts["value"].trim();
        // The first sign-off is the author's own, which `sign_off` holds.
        if key == "signed-off-by" && (std::mem::take(&mut first_sign_off) || author == Some(named))
        {
            continue;
        }
        if !found.may_name.iter().any(|listed| listed == named) {
            found_problems.push((
                index + 1,
                "named person".into(),
                format!(
                    "`{}` names {named}, whom [commits] may_name doesn't list; a trailer naming a person needs their agreement",
                    &parts["key"]
                ),
            ));
        }
    }
    found_problems
}

/// The commit's author as git will record it, without the time git appends.
fn author(root: &Path) -> Option<String> {
    let out = crate::profile::reading_git()
        .args(["var", "GIT_AUTHOR_IDENT"])
        .current_dir(root)
        .env("GIT_TERMINAL_PROMPT", "0")
        .stdin(std::process::Stdio::null())
        .output()
        .ok()?;
    if !out.status.success() {
        return None;
    }
    let ident = String::from_utf8_lossy(&out.stdout).trim().to_string();
    let end = ident.rfind('>')?;
    Some(ident[..=end].to_string())
}

/// The person a `Signed-off-by` line names, whatever the key's case, as git reads it.
fn signed_by(line: &str) -> Option<&str> {
    let (key, value) = line.split_once(": ")?;
    key.eq_ignore_ascii_case("Signed-off-by")
        .then_some(value.trim())
}

/// The sign-off chain records the route a change took, so its first entry
/// names the author and each later one someone it passed through (REQ-1312,
/// REQ-2206).
fn sign_off(message: &str, author: &str) -> Vec<(usize, String, String)> {
    message
        .lines()
        .enumerate()
        .filter_map(|(i, line)| signed_by(line).map(|v| (i + 1, v)))
        .take(1)
        .filter(|(_, named)| *named != author)
        .map(|(number, named)| {
            (number, "sign-off route".to_string(), format!("the first sign-off names {named}, and the commit's author is {author}; the chain starts with the author's own statement"))
        })
        .collect()
}

fn check_message(root: &Path, source: Option<&str>) -> u8 {
    let message = match source {
        None => {
            let mut text = String::new();
            let _ = std::io::stdin().read_to_string(&mut text);
            text
        }
        Some(path) => match std::fs::read(path) {
            Ok(bytes) => String::from_utf8_lossy(&bytes).into_owned(),
            Err(error) => {
                eprintln!("meow-scm check-message: can't read {path}: {error}");
                return USAGE;
            }
        },
    };
    let found = convention(root);
    let signed = found.state == "declared" && message.lines().any(|line| signed_by(line).is_some());
    let author = if signed { author(root) } else { None };
    let mut listed = problems_by(&message, &found, author.as_deref());
    let mut notes = Vec::new();
    if signed {
        match &author {
            Some(author) => listed.extend(sign_off(&message, author)),
            None => notes.push(
                "sign-off route: not compared with the author, because git reports no author identity"
                    .to_string(),
            ),
        }
    }
    for note in &notes {
        println!("{note}");
    }
    listed.sort();
    for (number, rule, detail) in &listed {
        println!("line {number}: {rule}: {detail}");
    }
    if found.state == "declared" {
        for problem in &found.malformed {
            println!("convention: malformed: {problem}");
        }
    }
    if !listed.is_empty() {
        let plural = if listed.len() != 1 { "s" } else { "" };
        println!(
            "meow-scm check-message: {} problem{plural}; don't use this message until they are fixed",
            listed.len()
        );
        return VIOLATED;
    }
    if found.state != "declared" {
        println!(
            "meow-scm check-message: convention {} ({}); only the attribution check ran, and it found nothing",
            found.state, found.detail
        );
        return UNDECLARED;
    }
    println!("meow-scm check-message: the message meets the declared convention");
    MET
}

pub fn main(args: &[String]) -> u8 {
    let root = profile::repository_root();
    let args: Vec<&str> = args.iter().map(String::as_str).collect();
    match args.as_slice() {
        ["convention"] => report_convention(&root),
        ["check-message"] => check_message(&root, None),
        ["check-message", path] => check_message(&root, Some(path)),
        _ => {
            eprintln!("usage: meow-scm convention | meow-scm check-message [FILE]");
            USAGE
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_path_or_a_product_name_is_not_attribution() {
        let attribution = Regex::new(ATTRIBUTION).unwrap();
        assert!(
            !attribution.is_match("fix: route the shape in plugins/meow-core/ for Claude Code")
        );
        assert!(attribution.is_match(&format!("Co-Authored-{}", "By: Claude <x@example.org>")));
    }

    const AUTHOR: &str = "A Person <a@example.org>";
    const ADA: &str = "Ada Lovelace <ada@example.org>";

    /// The convention a profile with `extra` under `[commits]` declares.
    fn declared(extra: &str) -> Convention {
        static NEXT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
        let n = NEXT.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        let dir = std::env::temp_dir().join(format!("meow-scm-test-{}-{n}", std::process::id()));
        std::fs::create_dir_all(dir.join(".meowpaw")).unwrap();
        std::fs::write(
            dir.join(PROFILE),
            format!("[commits]\ntrailers = [\"Signed-off-by\"]\n{extra}\n[commits.types]\nfeat = \"minor\"\nfix = \"patch\"\nbreak = \"major\"\n"),
        )
        .unwrap();
        let found = convention(&dir);
        std::fs::remove_dir_all(&dir).unwrap();
        assert_eq!(found.state, "declared", "{}", found.detail);
        found
    }

    fn rules(message: &str, found: &Convention) -> Vec<String> {
        problems(message, found)
            .into_iter()
            .map(|(_, rule, _)| rule)
            .collect()
    }

    #[test]
    fn the_first_sign_off_names_the_author() {
        // REQ-2206: the first entry names the author, and later entries are the route.
        let other = format!("fix: a change\n\nSigned-off-by: {ADA}\nSigned-off-by: {AUTHOR}\n");
        let found = sign_off(&other, AUTHOR);
        assert_eq!(found.len(), 1, "{found:?}");
        assert_eq!(found[0].0, 3);
        assert_eq!(found[0].1, "sign-off route");
        let route = format!("fix: a change\n\nSigned-off-by: {AUTHOR}\nSigned-off-by: {ADA}\n");
        assert_eq!(sign_off(&route, AUTHOR), Vec::new());
    }

    #[test]
    fn a_trailer_naming_a_person_needs_them_listed() {
        // REQ-2208: a trailer naming a person passes only where may_name lists them.
        let message = format!("fix: a change\n\nCo-authored-by: {ADA}\nSigned-off-by: {AUTHOR}\n");
        let unlisted = problems(&message, &declared(""));
        let named: Vec<_> = unlisted
            .iter()
            .filter(|(_, rule, _)| rule == "named person")
            .collect();
        assert_eq!(named.len(), 1, "{unlisted:?}");
        assert_eq!(named[0].0, 3);
        assert!(named[0].2.contains("Co-authored-by"), "{}", named[0].2);
        assert!(named[0].2.contains(ADA), "{}", named[0].2);
        let listed = declared(&format!("may_name = [\"{ADA}\"]"));
        assert_eq!(rules(&message, &listed), Vec::<String>::new());
    }

    #[test]
    fn a_later_sign_off_names_a_person() {
        // REQ-2208: only the author's own sign-off records provenance.
        let message = format!("fix: a change\n\nSigned-off-by: {AUTHOR}\nSigned-off-by: {ADA}\n");
        assert_eq!(rules(&message, &declared("")), vec!["named person"]);
    }

    #[test]
    fn the_provenance_trailers_need_no_list() {
        // REQ-2208: Fixes and Cherry-picked-from record where something came from.
        // Each carries a person's form here, so the exemption, not the form, passes
        // it, and the unlisted reviewer beside them shows the rule is running.
        let message = format!(
            "fix: a change\n\nFixes: {ADA}\nCherry-picked-from: {ADA}\nReviewed-by: {ADA}\nSigned-off-by: {AUTHOR}\n"
        );
        let listed = problems(&message, &declared(""));
        let lines: Vec<usize> = listed.iter().map(|(line, _, _)| *line).collect();
        assert_eq!(
            rules(&message, &declared("")),
            vec!["named person"],
            "{listed:?}"
        );
        assert_eq!(lines, vec![5], "{listed:?}");
    }

    #[test]
    fn a_lower_case_sign_off_is_still_a_sign_off() {
        // REQ-2206: git reads a trailer's key in any case, so the chain does too.
        let message = format!("fix: a change\n\nsigned-off-by: {ADA}\nSigned-off-by: {AUTHOR}\n");
        let found = sign_off(&message, AUTHOR);
        assert_eq!(found.len(), 1, "{found:?}");
        assert_eq!((found[0].0, found[0].1.as_str()), (3, "sign-off route"));
    }

    #[test]
    fn a_sign_off_in_the_body_is_not_the_first() {
        // REQ-2206: git reads the chain from the trailer block, so a body line starts nothing.
        let message = format!(
            "fix: a change\n\nSigned-off-by: {AUTHOR}\n\nSigned-off-by: {ADA}\nSigned-off-by: {AUTHOR}\n"
        );
        let found = sign_off(&message, AUTHOR);
        assert_eq!(found.len(), 1, "{found:?}");
        assert_eq!((found[0].0, found[0].1.as_str()), (5, "sign-off route"));
        let squashed =
            format!("fix: a change\n\nSigned-off-by: {ADA}\n\nSigned-off-by: {AUTHOR}\n");
        assert_eq!(sign_off(&squashed, AUTHOR), Vec::new());
    }

    #[test]
    fn a_body_line_names_nobody() {
        // REQ-2208: only the trailer block names a person, and only with an address.
        let message = format!(
            "fix: a change\n\nUsage: meow-scm check-message <file>\nAsked: Ada Lovelace <ada@example.org>\n\nSee: the guide <https://example.org>\nSigned-off-by: {AUTHOR}\n"
        );
        assert_eq!(rules(&message, &declared("")), Vec::<String>::new());
    }

    #[test]
    fn a_malformed_list_names_nobody() {
        // REQ-2208: a list that isn't one can't say who agreed.
        let found = declared("may_name = \"Ada Lovelace <ada@example.org>\"");
        assert!(
            found.malformed.iter().any(|m| m.contains("may_name")),
            "{:?}",
            found.malformed
        );
        let message = format!("fix: a change\n\nReviewed-by: {ADA}\nSigned-off-by: {AUTHOR}\n");
        assert_eq!(rules(&message, &found), vec!["named person"]);
    }

    #[test]
    fn a_break_says_what_breaks() {
        // REQ-2212: a `!` or a type meaning major needs a BREAKING CHANGE trailer.
        let found = declared("");
        for subject in ["feat!: drop the old flag", "break: drop the old flag"] {
            let bare = format!("{subject}\n\nSigned-off-by: {AUTHOR}\n");
            let listed = problems(&bare, &found);
            let marks: Vec<_> = listed
                .iter()
                .filter(|(_, rule, _)| rule == "breaking mark")
                .collect();
            assert_eq!(marks.len(), 1, "{subject}: {listed:?}");
            assert_eq!(marks[0].0, 1);
            let said = format!(
                "{subject}\n\nBREAKING CHANGE: the --old flag is gone.\nSigned-off-by: {AUTHOR}\n"
            );
            assert_eq!(rules(&said, &found), Vec::<String>::new(), "{subject}");
        }
        let minor = format!("feat: add a flag\n\nSigned-off-by: {AUTHOR}\n");
        assert_eq!(rules(&minor, &found), Vec::<String>::new());
    }

    #[test]
    fn may_name_is_a_key_the_unit_reads() {
        // TSK-4650 criterion 5: a profile declaring may_name isn't told the key is unknown.
        let found = declared(&format!("may_name = [\"{ADA}\"]"));
        assert!(
            !found.ignored.iter().any(|key| key == "commits.may_name"),
            "{:?}",
            found.ignored
        );
    }
}
