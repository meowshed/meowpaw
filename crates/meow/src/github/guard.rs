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

use super::request::{governance, path_of};
use serde_json::{Value, json};
use std::io::Read;

/// The long flags of `gh api` that take a value, as `gh api --help` lists
/// them in `gh` 2.101.0, so a value isn't read as the endpoint.
const VALUED: [&str; 10] = [
    "--cache",
    "--field",
    "--header",
    "--hostname",
    "--input",
    "--jq",
    "--method",
    "--preview",
    "--raw-field",
    "--template",
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
            // A backslash before a new line continues the line, as the shell
            // reads it, so both go.
            '\\' if !single => match chars.next() {
                Some('\n') if !double => {}
                Some(next) => word.push(next),
                None => {}
            },
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

/// The shell words that can stand before a command and run it.
const LEADS: [&str; 10] = [
    "then", "do", "else", "elif", "if", "while", "until", "time", "!", "exec",
];

/// What a part changes, as the method and the endpoint, where it runs `gh` to
/// change governance; `None` otherwise.
fn governs(part: &[String]) -> Option<String> {
    let mut words = part.iter().map(String::as_str).peekable();
    loop {
        match words.peek() {
            Some(w) if assignment(w) || LEADS.contains(w) || *w == "command" => {
                words.next();
            }
            Some(&"env") => {
                words.next();
                while words
                    .peek()
                    .is_some_and(|w| assignment(w) || w.starts_with('-'))
                {
                    words.next();
                }
            }
            _ => break,
        }
    }
    if !words
        .next()
        .is_some_and(|w| w == "gh" || w.ends_with("/gh"))
    {
        return None;
    }
    let rest: Vec<&str> = words.collect();
    match rest.as_slice() {
        ["api", args @ ..] => api(args),
        [
            "repo",
            action @ ("edit" | "rename" | "archive" | "unarchive" | "delete"),
            ..,
        ]
        | ["workflow", action @ ("enable" | "disable"), ..] => {
            Some(format!("gh {} {action}", rest[0]))
        }
        [
            noun @ ("secret" | "variable"),
            action @ ("set" | "delete" | "remove"),
            ..,
        ] => Some(format!("gh {noun} {action}")),
        _ => None,
    }
}

/// The short flags of `gh api` that take a value, written alone or joined to
/// their value or to other short flags, as in `-iXPUT`.
const SHORT_VALUED: [char; 7] = ['X', 'f', 'F', 'H', 'q', 't', 'p'];

/// The HTTP methods a reason may name; anything else is named as a method
/// other than `GET`, so no word of the command reaches the reason.
const METHODS: [&str; 7] = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"];

/// What a `gh api` call changes, where it changes governance.
fn api(args: &[&str]) -> Option<String> {
    let (mut method, mut endpoint, mut body) = (None, None, false);
    let mut query: Vec<String> = Vec::new();
    let mut take = |flag: &str, value: &str, method: &mut Option<String>| match flag {
        "-X" | "--method" => *method = Some(value.to_ascii_uppercase()),
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
    };
    let mut i = 0;
    while i < args.len() {
        let arg = args[i];
        if [">", ">>", "<", "2>", "2>>", "&>"].contains(&arg) {
            i += 2;
            continue;
        }
        if arg.starts_with(['<', '>'])
            || (arg.starts_with(|c: char| c.is_ascii_digit()) && arg.contains('>'))
        {
            i += 1;
            continue;
        }
        if let Some(long) = arg.strip_prefix("--") {
            let (name, inline) = match long.split_once('=') {
                Some((name, value)) => (name, Some(value)),
                None => (long, None),
            };
            let flag = format!("--{name}");
            if VALUED.contains(&flag.as_str()) {
                let value = match inline {
                    Some(value) => value,
                    None => {
                        i += 1;
                        args.get(i).copied().unwrap_or("")
                    }
                };
                take(&flag, value, &mut method);
            }
        } else if let Some(cluster) = arg.strip_prefix('-').filter(|c| !c.is_empty()) {
            for (at, c) in cluster.char_indices() {
                if SHORT_VALUED.contains(&c) {
                    let joined = &cluster[at + c.len_utf8()..];
                    let value = if joined.is_empty() {
                        i += 1;
                        args.get(i).copied().unwrap_or("")
                    } else {
                        joined
                    };
                    take(&format!("-{c}"), value, &mut method);
                    break;
                }
            }
        } else if endpoint.is_none() {
            endpoint = Some(arg);
        }
        i += 1;
    }
    let path = path_of(endpoint?);
    let method = method.unwrap_or_else(|| if body { "POST" } else { "GET" }.to_string());
    let shown = if METHODS.contains(&method.as_str()) {
        method.clone()
    } else {
        "a method other than GET".to_string()
    };
    if path == "graphql" || path == "api/graphql" {
        // A query from a file, from standard input or from the shell can't be
        // read here, so it is asked about as a mutation would be.
        let mutates = query.iter().any(|q| {
            q.contains("mutation") || q.starts_with('@') || q.contains('$') || q.contains('`')
        });
        return mutates.then(|| format!("gh api {shown} graphql"));
    }
    (method != "GET" && governance(path)).then(|| format!("gh api {shown} {path}"))
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
