// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The `PreToolUse` hook that asks before a Bash command's `gh` changes how a
//! repository is governed (ADR-1810, REQ-2576). SPC-1080 states the kinds of
//! command it asks about.
//!
//! The guard reads the hook's input on standard input, splits the command into
//! parts at `&&`, `||`, `;`, `|`, `&` and each new line, and reads a part only
//! where its first word, after any variable assignments and a leading `env`,
//! is `gh`. It answers `ask` with a reason naming the method and the endpoint,
//! never the command, because a command can carry a token. For anything else
//! it prints nothing and exits 0, so the platform's own rules decide.

use super::request::governance;
use serde_json::{Value, json};
use std::io::Read;

/// The flags of `gh api` that take a value, so the value isn't read as the
/// endpoint.
const VALUED: [&str; 16] = [
    "-X",
    "--method",
    "-f",
    "-F",
    "--field",
    "--raw-field",
    "-H",
    "--header",
    "--input",
    "-q",
    "--jq",
    "-t",
    "--template",
    "--cache",
    "-p",
    "--preview",
];

pub fn main() -> u8 {
    let mut text = String::new();
    let _ = std::io::stdin().read_to_string(&mut text);
    let event: Value = serde_json::from_str(&text).unwrap_or(Value::Null);
    let Some(command) = event.pointer("/tool_input/command").and_then(Value::as_str) else {
        return 0;
    };
    let asked: Vec<String> = parts(command)
        .iter()
        .filter_map(|part| governs(part))
        .collect();
    if !asked.is_empty() {
        let reason = format!(
            "meow-github: {} changes how the repository is governed, which a person approves (REQ-2576)",
            asked.join(" and ")
        );
        let answer = json!({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": reason,
            }
        });
        println!("{answer}");
    }
    0
}

/// The command's words, grouped into the parts its separators divide it into.
/// Quotes group words and are dropped, and a backslash outside single quotes
/// keeps the next character as it is.
fn parts(command: &str) -> Vec<Vec<String>> {
    let mut parts = vec![Vec::new()];
    let mut word = String::new();
    let mut quoted = false;
    let (mut single, mut double) = (false, false);
    let mut chars = command.chars().peekable();
    let end_word = |word: &mut String, quoted: &mut bool, parts: &mut Vec<Vec<String>>| {
        if (!word.is_empty() || *quoted)
            && let Some(part) = parts.last_mut()
        {
            part.push(std::mem::take(word));
        }
        *quoted = false;
    };
    while let Some(c) = chars.next() {
        match c {
            '\'' if !double => {
                single = !single;
                quoted = true;
            }
            '"' if !single => {
                double = !double;
                quoted = true;
            }
            '\\' if !single => {
                if let Some(next) = chars.next() {
                    word.push(next);
                }
            }
            c if single || double => word.push(c),
            c if c.is_whitespace() && c != '\n' => end_word(&mut word, &mut quoted, &mut parts),
            ';' | '|' | '&' | '\n' => {
                end_word(&mut word, &mut quoted, &mut parts);
                if parts.last().is_some_and(|part| !part.is_empty()) {
                    parts.push(Vec::new());
                }
            }
            c => word.push(c),
        }
    }
    end_word(&mut word, &mut quoted, &mut parts);
    parts.retain(|part| !part.is_empty());
    parts
}

fn assignment(word: &str) -> bool {
    word.split_once('=').is_some_and(|(name, _)| {
        !name.is_empty()
            && name
                .chars()
                .next()
                .is_some_and(|c| c.is_ascii_alphabetic() || c == '_')
            && name.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
    })
}

/// What a part changes, as the method and the endpoint, where it runs `gh` to
/// change governance; `None` otherwise.
fn governs(part: &[String]) -> Option<String> {
    let mut words = part.iter().map(String::as_str).peekable();
    while words.peek().is_some_and(|w| assignment(w)) {
        words.next();
    }
    if words.peek() == Some(&"env") {
        words.next();
        while words
            .peek()
            .is_some_and(|w| assignment(w) || w.starts_with('-'))
        {
            words.next();
        }
    }
    if words.next() != Some("gh") {
        return None;
    }
    let rest: Vec<&str> = words.collect();
    match rest.as_slice() {
        ["api", args @ ..] => api(args),
        [
            "repo",
            action @ ("edit" | "rename" | "archive" | "delete"),
            ..,
        ]
        | ["workflow", action @ ("enable" | "disable"), ..] => {
            Some(format!("gh {} {action}", rest[0]))
        }
        [
            noun @ ("secret" | "variable"),
            action @ ("set" | "delete"),
            ..,
        ] => Some(format!("gh {noun} {action}")),
        _ => None,
    }
}

/// What a `gh api` call changes, where it changes governance.
fn api(args: &[&str]) -> Option<String> {
    let (mut method, mut endpoint, mut body) = (None, None, false);
    let mut query: Vec<String> = Vec::new();
    let mut i = 0;
    while i < args.len() {
        let arg = args[i];
        let (flag, inline) = match arg.split_once('=') {
            Some((flag, value)) if arg.starts_with("--") => (flag, Some(value)),
            _ => (arg, None),
        };
        if VALUED.contains(&flag) {
            let value = match inline {
                Some(value) => value,
                None => {
                    i += 1;
                    args.get(i).copied().unwrap_or("")
                }
            };
            match flag {
                "-X" | "--method" => method = Some(value.to_ascii_uppercase()),
                "-f" | "-F" | "--field" | "--raw-field" => {
                    body = true;
                    if let Some(("query", text)) = value.split_once('=') {
                        query.push(text.to_string());
                    }
                }
                "--input" => {
                    body = true;
                    query.push("@input".to_string());
                }
                _ => {}
            }
        } else if let Some(rest) = arg.strip_prefix("-X").filter(|r| !r.is_empty()) {
            method = Some(rest.to_ascii_uppercase());
        } else if !arg.starts_with('-') && endpoint.is_none() {
            endpoint = Some(arg);
        }
        i += 1;
    }
    let endpoint = endpoint?;
    let method = method.unwrap_or_else(|| if body { "POST" } else { "GET" }.to_string());
    if endpoint == "graphql" {
        // A query from a file or from standard input can't be read here, so it
        // is asked about as a mutation would be.
        let mutates = query
            .iter()
            .any(|q| q.contains("mutation") || q.starts_with('@'));
        return mutates.then(|| format!("gh api {method} graphql"));
    }
    (method != "GET" && governance(endpoint)).then(|| format!("gh api {method} {endpoint}"))
}

#[cfg(test)]
mod tests {
    use super::{governs, parts};

    #[test]
    fn a_part_is_read_after_its_assignments() {
        let found: Vec<Option<String>> =
            parts("A=1 B=2 gh api -XPUT repos/o/r/hooks/1; ls | gh repo rename x")
                .iter()
                .map(|part| governs(part))
                .collect();
        assert_eq!(
            found,
            vec![
                Some("gh api PUT repos/o/r/hooks/1".to_string()),
                None,
                Some("gh repo rename".to_string())
            ]
        );
    }
}
