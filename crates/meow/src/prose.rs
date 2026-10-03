// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Block a publish whose text breaks one of three exact rules, or one of three
//! judged rules that two judgements agree on.
//!
//! SPC-1010 states the behaviour, and ADR-1600 and ADR-2390 decide it. The hook
//! passes the tool call as JSON on standard input. `check` finds each `git
//! commit` and `gh` command that publishes text, reads the text from its
//! arguments and from the heredoc it reads as standard input, and blocks by
//! exiting 2 with one line per finding on standard error, `P1 | "span" | fix`.
//! Every span is a slice of the command itself, so it occurs there verbatim
//! (REQ-3183). Where no exact rule fires, a judge reads the text twice, and a
//! judged finding blocks only where both judgements report it (REQ-3744).

use regex::Regex;
use std::io::{Read, Write};
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

const BLOCK: u8 = 2;
const ALLOW: u8 = 0;

/// The judge's instructions and the shape its answer must take, in the unit's
/// `fragments/`, where SPC-1030 holds the prompt.
const JUDGE_PROMPT: &str = "judge.md";
const JUDGE_SCHEMA: &str = "judge.schema.json";
/// The rules a judge may report, a closed list (REQ-3742).
const JUDGED: [&str; 3] = ["J1", "J2", "J3"];
/// A judge with no tool, plugin, hook or project instruction loaded (REQ-3750),
/// followed by the schema.
const JUDGE_ARGS: [&str; 12] = [
    "-p",
    "--safe-mode",
    "--tools",
    "",
    "--no-session-persistence",
    "--max-turns",
    "1",
    "--model",
    "sonnet",
    "--output-format",
    "json",
    "--json-schema",
];
/// Under the hook's 120-second timeout, so the gate reports a slow judge
/// before the platform kills the hook.
const JUDGE_LIMIT: Duration = Duration::from_secs(45);

/// The closed list P1 holds, as ADR-1600 states it.
pub const IDIOMS: [&str; 15] = [
    "low-hanging fruit",
    "under the hood",
    "silver bullet",
    "move the needle",
    "boil the ocean",
    "circle back",
    "deep dive",
    "game changer",
    "at the end of the day",
    "out of the box",
    "on the same page",
    "ballpark figure",
    "in the weeds",
    "rule of thumb",
    "the elephant in the room",
];

const FIX_P1: &str = "say literally what the idiom stands for";
const FIX_P2: &str = "write the point as a sentence, or make the line a real heading";
const FIX_P3: &str =
    "give the text inline, as -m \"...\" or --body \"...\", or in a heredoc read with -F -";

/// One piece of a shell word: its characters as the command holds them, and
/// whether the shell expands a substitution inside it.
#[derive(Debug, Clone)]
struct Piece {
    raw: String,
    expands: bool,
}

#[derive(Debug, Clone, Default)]
struct Word {
    pieces: Vec<Piece>,
}

impl Word {
    fn text(&self) -> String {
        self.pieces.iter().map(|piece| piece.raw.as_str()).collect()
    }
}

/// One simple command: its words, the text it reads on standard input from a
/// heredoc or a here-string, and the file it reads there with `<`.
#[derive(Debug, Default)]
struct Simple {
    words: Vec<Word>,
    input: Vec<Piece>,
    input_file: Option<String>,
}

/// A finding: the rule, the span as the command holds it, and the fix.
#[derive(Debug, PartialEq, Eq)]
pub struct Finding {
    pub rule: &'static str,
    pub span: String,
    pub fix: &'static str,
}

pub fn main(args: &[String]) -> u8 {
    match args.first().map(String::as_str) {
        Some("check") => {
            let mut input = String::new();
            let _ = std::io::stdin().read_to_string(&mut input);
            let event: serde_json::Value =
                serde_json::from_str(&input).unwrap_or(serde_json::Value::Null);
            let Some(command) = event
                .pointer("/tool_input/command")
                .and_then(|c| c.as_str())
            else {
                return ALLOW;
            };
            let found = findings(command);
            if !found.is_empty() {
                for finding in &found {
                    eprintln!("{} | \"{}\" | {}", finding.rule, finding.span, finding.fix);
                }
                return BLOCK;
            }
            let text = published_text(command);
            if text.trim().is_empty() {
                return ALLOW;
            }
            match judged(command, &text) {
                Ok(agreed) if agreed.is_empty() => ALLOW,
                Ok(agreed) => {
                    for (rule, span, fix) in &agreed {
                        eprintln!("{rule} | \"{span}\" | {fix}");
                    }
                    BLOCK
                }
                Err(cause) => {
                    let message =
                        format!("meow-prose-gate: the judged rules were not checked: {cause}");
                    println!("{}", serde_json::json!({ "systemMessage": message }));
                    ALLOW
                }
            }
        }
        _ => {
            eprintln!("usage: meow-prose-gate check, with the hook's JSON on standard input");
            64
        }
    }
}

/// Every finding in the text a shell command publishes, each once.
pub fn findings(command: &str) -> Vec<Finding> {
    let mut found: Vec<Finding> = Vec::new();
    for simple in parse(command) {
        let Some(published) = publishing(&simple) else {
            continue;
        };
        for piece in &published.texts {
            rule_p1(&piece.raw, &mut found);
            rule_p2(&piece.raw, &mut found);
            if piece.expands {
                substitutions(&piece.raw, &mut found);
            }
        }
        for path in published.paths {
            found.push(Finding {
                rule: "P3",
                span: path,
                fix: FIX_P3,
            });
        }
    }
    let mut unique: Vec<Finding> = Vec::new();
    for finding in found {
        // A span the command doesn't hold is never reported (REQ-3183).
        if command.contains(&finding.span) && !unique.contains(&finding) {
            unique.push(finding);
        }
    }
    unique
}

/// The text a shell command publishes, each piece as the command holds it, one
/// blank line between pieces.
fn published_text(command: &str) -> String {
    let mut pieces: Vec<String> = Vec::new();
    for simple in parse(command) {
        if let Some(published) = publishing(&simple) {
            pieces.extend(published.texts.into_iter().map(|piece| piece.raw));
        }
    }
    pieces.join("\n\n")
}

/// Each finding both judgements report on a span the text and the command
/// hold, as rule, span and the first judgement's fix (REQ-3744, REQ-3746), or
/// why the text couldn't be judged (REQ-3748).
fn judged(command: &str, text: &str) -> Result<Vec<(String, String, String)>, String> {
    let program = std::env::var("MEOW_PROSE_GATE_JUDGE").unwrap_or_else(|_| "claude".into());
    let prompt = format!(
        "{}\n<input>\n{}\n</input>\n",
        fragment(JUDGE_PROMPT)?,
        text.replace("</input>", "&lt;/input>")
    );
    let schema = fragment(JUDGE_SCHEMA)?;
    let calls: Vec<_> = ["1", "2"]
        .into_iter()
        .map(|call| {
            let (program, prompt, schema) = (program.clone(), prompt.clone(), schema.clone());
            std::thread::spawn(move || judgement(&program, call, &prompt, &schema))
        })
        .collect();
    // Wait for both calls, each bounded by JUDGE_LIMIT, before reading either
    // result, so one call's failure never returns while the other still runs.
    let results: Vec<_> = calls
        .into_iter()
        .map(|call| {
            call.join()
                .unwrap_or_else(|_| Err("the judge's call panicked".into()))
        })
        .collect();
    let mut answers = Vec::new();
    for result in results {
        answers.push(result?);
    }
    let mut agreed: Vec<(String, String, String)> = Vec::new();
    for (rule, span, fix) in &answers[0] {
        let both = answers[1].iter().any(|(r, s, _)| r == rule && s == span);
        let held = in_prose(text, rule, span) && command.contains(span.as_str());
        if both && held && !agreed.iter().any(|(r, s, _)| r == rule && s == span) {
            agreed.push((rule.clone(), span.clone(), fix.clone()));
        }
    }
    Ok(agreed)
}

/// Whether the span occurs at least once outside fenced code, code spans and
/// URLs, which name things and break no judged rule (REQ-3746). J1 and J2 also
/// skip a token holding a path, a file name or an `_`, as P1 does, and J3
/// doesn't, because `__Why.__` is bold.
fn in_prose(text: &str, rule: &str, span: &str) -> bool {
    let masked = mask(text, rule != "J3");
    text.match_indices(span)
        .any(|(at, _)| masked.get(at..at + span.len()) == Some(span))
}

/// A file in the unit's `fragments/`. The binary sits in the unit at
/// `bin/<target>/meow`, so the unit is three directories above it.
fn fragment(name: &str) -> Result<String, String> {
    let exe = std::env::current_exe()
        .and_then(std::fs::canonicalize)
        .map_err(|error| format!("the gate could not find its own unit: {error}"))?;
    let path = exe
        .ancestors()
        .nth(3)
        .map(|unit| unit.join("fragments").join(name))
        .ok_or_else(|| {
            format!(
                "the gate could not find its own unit from {}",
                exe.display()
            )
        })?;
    std::fs::read_to_string(&path)
        .map_err(|error| format!("the judge's {} could not be read: {error}", path.display()))
}

/// One run of the judge, read as the findings its answer holds. Everything,
/// writing the prompt included, happens before one deadline, and on the
/// deadline the judge's whole process group is killed, so a child it left
/// holding its output can't keep the gate waiting.
fn judgement(
    program: &str,
    call: &str,
    prompt: &str,
    schema: &str,
) -> Result<Vec<(String, String, String)>, String> {
    let deadline = Instant::now() + JUDGE_LIMIT;
    let mut command = Command::new(program);
    command
        .args(JUDGE_ARGS)
        .arg(schema)
        .env("MEOW_PROSE_GATE_CALL", call)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    #[cfg(unix)]
    std::os::unix::process::CommandExt::process_group(&mut command, 0);
    let mut child = command
        .spawn()
        .map_err(|error| format!("the judge could not be started: {program}: {error}"))?;
    if let Some(mut input) = child.stdin.take() {
        let prompt = prompt.to_string();
        std::thread::spawn(move || {
            let _ = input.write_all(prompt.as_bytes());
        });
    }
    let stdout = drain(child.stdout.take());
    let stderr = drain(child.stderr.take());
    let late = |child: &mut std::process::Child| {
        stop(child);
        format!("the judge ran past {} seconds", JUDGE_LIMIT.as_secs())
    };
    let left = || deadline.saturating_duration_since(Instant::now());
    let Ok(out) = stdout.recv_timeout(left()) else {
        return Err(late(&mut child));
    };
    let Ok(err) = stderr.recv_timeout(left()) else {
        return Err(late(&mut child));
    };
    let status = loop {
        match child.try_wait() {
            Ok(Some(status)) => break status,
            Ok(None) if left().is_zero() => return Err(late(&mut child)),
            Ok(None) => std::thread::sleep(Duration::from_millis(20)),
            Err(error) => return Err(format!("the judge could not be waited for: {error}")),
        }
    };
    if !status.success() {
        let cause = match status.code() {
            Some(code) => format!("the judge exited {code}"),
            None => "the judge was stopped by a signal".into(),
        };
        return Err(
            match err.lines().rev().find(|line| !line.trim().is_empty()) {
                Some(line) => format!("{cause}: {}", line.trim()),
                None => cause,
            },
        );
    }
    answer(&out).ok_or_else(|| "the judge answered outside the schema".into())
}

/// A pipe read to its end on a thread of its own, its text sent once it closes.
fn drain(pipe: Option<impl Read + Send + 'static>) -> std::sync::mpsc::Receiver<String> {
    let (send, receive) = std::sync::mpsc::channel();
    std::thread::spawn(move || {
        let mut text = String::new();
        if let Some(mut pipe) = pipe {
            let _ = pipe.read_to_string(&mut text);
        }
        let _ = send.send(text);
    });
    receive
}

/// Kill the judge and every process in its group, which closes the pipes a
/// child of it still holds.
fn stop(child: &mut std::process::Child) {
    #[cfg(unix)]
    let _ = Command::new("kill")
        .args(["-KILL", &format!("-{}", child.id())])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    let _ = child.kill();
    let _ = child.wait();
}

/// The findings in a reply from `claude -p --output-format json`, or None where
/// the reply doesn't match the schema the unit ships.
fn answer(out: &str) -> Option<Vec<(String, String, String)>> {
    let reply: serde_json::Value = serde_json::from_str(out.trim()).ok()?;
    let structured = match reply.get("structured_output") {
        Some(value) => value.clone(),
        None => serde_json::from_str(reply.get("result")?.as_str()?).ok()?,
    };
    let object = structured.as_object()?;
    if object.len() != 1 {
        return None;
    }
    let mut found = Vec::new();
    for item in object.get("findings")?.as_array()? {
        let item = item.as_object()?;
        if item.len() != 3 {
            return None;
        }
        let field = |key: &str| item.get(key)?.as_str().map(str::to_string);
        let (rule, span, fix) = (field("rule")?, field("span")?, field("fix")?);
        if !JUDGED.contains(&rule.as_str()) || span.is_empty() || fix.is_empty() {
            return None;
        }
        found.push((rule, span, fix));
    }
    Some(found)
}

struct Published {
    texts: Vec<Piece>,
    paths: Vec<String>,
}

/// The texts and the paths a `git commit` or a `gh` command publishes, or
/// nothing for any other command.
fn publishing(simple: &Simple) -> Option<Published> {
    let words: Vec<String> = simple.words.iter().map(Word::text).collect();
    let start = words
        .iter()
        .position(|word| word == "git" || word == "gh")?;
    let (text_flags, path_flags, arg_flags): (&[&str], &[&str], &[&str]) = if words[start] == "git"
    {
        let mut at = start + 1;
        while at < words.len() && words[at].starts_with('-') {
            at += if matches!(
                words[at].as_str(),
                "-C" | "-c" | "--git-dir" | "--work-tree" | "--namespace"
            ) {
                2
            } else {
                1
            };
        }
        if words.get(at).map(String::as_str) != Some("commit") {
            return None;
        }
        (
            &["-m", "--message"],
            &["-F", "--file"],
            &[
                "-C",
                "-c",
                "-t",
                "--reuse-message",
                "--reedit-message",
                "--template",
                "--author",
                "--date",
                "--cleanup",
                "--fixup",
                "--squash",
                "--trailer",
                "--pathspec-from-file",
            ],
        )
    } else {
        // `-R` and `--repo` name another repository and may come first.
        let mut at = start + 1;
        while let Some(word) = words.get(at) {
            if word == "-R" || word == "--repo" {
                at += 2;
            } else if word.starts_with("--repo=") || (word.starts_with("-R") && word.len() > 2) {
                at += 1;
            } else {
                break;
            }
        }
        let group = words.get(at).map(String::as_str);
        let action = words.get(at + 1).map(String::as_str);
        let publishes = matches!(group, Some("pr" | "issue" | "release"))
            && matches!(action, Some("create" | "edit" | "comment" | "review"));
        if !publishes {
            return None;
        }
        (
            &["-t", "--title", "-b", "--body", "-n", "--notes"],
            &["-F", "--body-file", "--notes-file"],
            &[],
        )
    };
    let mut texts = Vec::new();
    let mut paths = Vec::new();
    let mut reads_input = false;
    let mut index = start + 1;
    let take = |value: &Word,
                is_path: bool,
                texts: &mut Vec<Piece>,
                paths: &mut Vec<String>,
                reads_input: &mut bool| {
        if is_path {
            let path = value.text();
            if matches!(path.as_str(), "-" | "/dev/stdin" | "/dev/fd/0") {
                *reads_input = true;
            } else {
                paths.push(path);
            }
        } else {
            texts.extend(value.pieces.iter().cloned());
        }
    };
    while index < simple.words.len() {
        let word = &words[index];
        if word == "--" {
            break;
        }
        let next = simple.words.get(index + 1);
        if text_flags.contains(&word.as_str()) || path_flags.contains(&word.as_str()) {
            if let Some(value) = next {
                take(
                    value,
                    path_flags.contains(&word.as_str()),
                    &mut texts,
                    &mut paths,
                    &mut reads_input,
                );
            }
            index += 2;
            continue;
        }
        if arg_flags.contains(&word.as_str()) {
            index += 2;
            continue;
        }
        if let Some((flag, value)) = word
            .split_once('=')
            .filter(|(flag, _)| flag.starts_with("--"))
        {
            let is_text = text_flags.contains(&flag);
            if is_text || path_flags.contains(&flag) {
                let mut rest = simple.words[index].clone();
                strip_prefix(&mut rest, flag.len() + 1);
                debug_assert_eq!(rest.text(), value);
                take(&rest, !is_text, &mut texts, &mut paths, &mut reads_input);
            }
            index += 1;
            continue;
        }
        if word.len() > 2 && word.starts_with('-') && !word.starts_with("--") {
            // A cluster of short options, such as `-am`, where the last one
            // that takes a value takes the rest of the word or the next word.
            let letters: Vec<char> = word[1..].chars().collect();
            let mut consumed_next = false;
            for (at, letter) in letters.iter().enumerate() {
                let flag = format!("-{letter}");
                let is_text = text_flags.contains(&flag.as_str());
                let is_path = path_flags.contains(&flag.as_str());
                let is_arg = arg_flags.contains(&flag.as_str());
                if !(is_text || is_path || is_arg) {
                    continue;
                }
                if at + 1 < letters.len() {
                    if is_text || is_path {
                        let mut rest = simple.words[index].clone();
                        strip_prefix(&mut rest, 2 + at);
                        take(&rest, is_path, &mut texts, &mut paths, &mut reads_input);
                    }
                } else if let Some(value) = next {
                    if is_text || is_path {
                        take(value, is_path, &mut texts, &mut paths, &mut reads_input);
                    }
                    consumed_next = true;
                }
                break;
            }
            index += if consumed_next { 2 } else { 1 };
            continue;
        }
        index += 1;
    }
    if reads_input {
        texts.extend(simple.input.iter().cloned());
        if let Some(file) = &simple.input_file {
            paths.push(file.clone());
        }
    }
    Some(Published { texts, paths })
}

/// Drop the first `count` characters of a word, as `--body=` or `-m` in `-mtext`.
fn strip_prefix(word: &mut Word, mut count: usize) {
    while count > 0 && !word.pieces.is_empty() {
        let first = &mut word.pieces[0];
        let length = first.raw.chars().count();
        if length <= count {
            count -= length;
            word.pieces.remove(0);
        } else {
            first.raw = first.raw.chars().skip(count).collect();
            count = 0;
        }
    }
}

/// P1: an idiom from the closed list, as whole words, in any case, with any
/// run of spaces, line breaks or hyphens between its words.
fn rule_p1(text: &str, found: &mut Vec<Finding>) {
    let masked = mask(text, true);
    for idiom in IDIOMS {
        let words: Vec<String> = idiom.split([' ', '-']).map(regex::escape).collect();
        let pattern = Regex::new(&format!(r"(?i)\b{}\b", words.join(r"[\s-]+")))
            .expect("an idiom's pattern compiles");
        for hit in pattern.find_iter(&masked) {
            found.push(Finding {
                rule: "P1",
                span: text[hit.range()].to_string(),
                fix: FIX_P1,
            });
        }
    }
}

/// P2: a line holding only bold text, with an optional colon or full stop.
fn rule_p2(text: &str, found: &mut Vec<Finding>) {
    let masked = mask(text, false);
    let bold = Regex::new(r"^[ \t]*(\*\*[^*\n]*[^*\s]\*\*|__[^_\n]*[^_\s]__)[ \t]*[:.]?[ \t]*$")
        .expect("P2 compiles");
    let mut offset = 0;
    for line in masked.split('\n') {
        if let Some(hit) = bold.find(line) {
            let span = text[offset + hit.start()..offset + hit.end()].trim();
            let inner = &span.trim_end_matches([':', '.', ' ', '\t'])[2..];
            if !inner.trim_start().is_empty() && !inner.starts_with(char::is_whitespace) {
                found.push(Finding {
                    rule: "P2",
                    span: span.to_string(),
                    fix: FIX_P2,
                });
            }
        }
        offset += line.len() + 1;
    }
}

/// P3 inside a text: `$(cat path)`, `$(< path)` or `` `cat path` ``, where the
/// shell would read the text from a file the hook can't see.
fn substitutions(text: &str, found: &mut Vec<Finding>) {
    let pattern = Regex::new(r"\$\(\s*(?:cat\s+(?:-\S+\s+)*|<\s*)([^\s()<>;&|`]+)\s*\)|(?:^|[^\\])`\s*cat\s+([^\s`<]+)\s*`")
        .expect("P3 compiles");
    for hit in pattern.captures_iter(text) {
        if let Some(path) = hit.get(1).or_else(|| hit.get(2)) {
            found.push(Finding {
                rule: "P3",
                span: path.as_str().to_string(),
                fix: FIX_P3,
            });
        }
    }
}

/// The text with the regions no rule reads blanked out, character for
/// character so offsets still match: fenced code, code spans and URLs, and for
/// P1 also any token that holds a path or a file name.
fn mask(text: &str, tokens: bool) -> String {
    let mut out = String::with_capacity(text.len());
    let mut fenced = false;
    for (index, line) in text.split('\n').enumerate() {
        if index > 0 {
            out.push('\n');
        }
        let trimmed = line.trim_start().trim_start_matches('\\');
        if trimmed.starts_with("```") || trimmed.starts_with("~~~") {
            fenced = !fenced;
            out.push_str(&blank(line));
            continue;
        }
        if fenced {
            out.push_str(&blank(line));
        } else {
            out.push_str(line);
        }
    }
    let mut spans: Vec<(usize, usize)> = Vec::new();
    let code = Regex::new(r"\\?`[^`\n]*\\?`").expect("code spans compile");
    let url = Regex::new(r"\b[a-z][a-z0-9+.-]*://\S+").expect("URLs compile");
    spans.extend(code.find_iter(&out).map(|m| (m.start(), m.end())));
    spans.extend(url.find_iter(&out).map(|m| (m.start(), m.end())));
    if tokens {
        let token = Regex::new(
            r"[^\s`]*[/\\][^\s`]*|[^\s`]+\.[A-Za-z][A-Za-z0-9]*\b[^\s`]*|[^\s`]*_[^\s`]*",
        )
        .expect("tokens compile");
        spans.extend(token.find_iter(&out).map(|m| (m.start(), m.end())));
    }
    let mut bytes = out.into_bytes();
    for (start, end) in spans {
        for byte in &mut bytes[start..end] {
            if *byte != b'\n' && byte.is_ascii() {
                *byte = b' ';
            }
        }
    }
    String::from_utf8(bytes).unwrap_or_default()
}

fn blank(line: &str) -> String {
    line.chars()
        .map(|c| if c.is_ascii() { ' ' } else { c })
        .collect()
}

/// Split a shell command into simple commands, keeping each word's characters
/// as the command holds them and noting which pieces the shell expands.
fn parse(command: &str) -> Vec<Simple> {
    let chars: Vec<char> = command.chars().collect();
    let mut commands: Vec<Simple> = Vec::new();
    let mut current = Simple::default();
    let mut word: Option<Word> = None;
    // Each heredoc waiting for its body, with the command it belongs to once
    // that command has ended before the line does, as in `<<EOF && echo`.
    let mut pending: Vec<(String, bool, bool, Option<usize>)> = Vec::new();
    let mut redirect: Option<char> = None;
    let mut index = 0;

    fn push_piece(word: &mut Option<Word>, raw: String, expands: bool) {
        word.get_or_insert_with(Word::default)
            .pieces
            .push(Piece { raw, expands });
    }

    macro_rules! end_word {
        () => {
            if let Some(done) = word.take() {
                match redirect.take() {
                    Some('<') => current.input_file = Some(done.text()),
                    Some('s') => current.input.extend(done.pieces),
                    Some(_) => {}
                    None => current.words.push(done),
                }
            }
        };
    }
    macro_rules! end_command {
        () => {
            end_word!();
            let done = std::mem::take(&mut current);
            let owner = commands.len();
            let mut kept = false;
            for waiting in pending.iter_mut().filter(|waiting| waiting.3.is_none()) {
                waiting.3 = Some(owner);
                kept = true;
            }
            if kept || !done.words.is_empty() || !done.input.is_empty() {
                commands.push(done);
            }
        };
    }

    while index < chars.len() {
        let c = chars[index];
        match c {
            ' ' | '\t' => {
                end_word!();
                index += 1;
            }
            '\n' => {
                end_word!();
                index += 1;
                end_command!();
                for (delimiter, strip, expands, owner) in std::mem::take(&mut pending) {
                    let (body, next) = heredoc(&chars, index, &delimiter, strip);
                    if let Some(owner) = owner.and_then(|owner| commands.get_mut(owner)) {
                        owner.input.push(Piece { raw: body, expands });
                    }
                    index = next;
                }
            }
            ';' | '&' | '|' | '(' | ')' => {
                end_command!();
                index += 1;
            }
            '#' if word.is_none() => {
                while index < chars.len() && chars[index] != '\n' {
                    index += 1;
                }
            }
            '\'' => {
                let end = find(&chars, index + 1, '\'');
                push_piece(&mut word, chars[index + 1..end].iter().collect(), false);
                index = end + 1;
            }
            '"' => {
                let end = double_quoted(&chars, index + 1);
                push_piece(&mut word, chars[index + 1..end].iter().collect(), true);
                index = end + 1;
            }
            '\\' => {
                if index + 1 < chars.len() {
                    push_piece(&mut word, chars[index + 1].to_string(), false);
                }
                index += 2;
            }
            '$' if chars.get(index + 1) == Some(&'(') => {
                let end = substitution(&chars, index + 2);
                push_piece(
                    &mut word,
                    chars[index..end.min(chars.len())].iter().collect(),
                    true,
                );
                index = end;
            }
            '`' => {
                let end = find(&chars, index + 1, '`');
                push_piece(
                    &mut word,
                    chars[index..(end + 1).min(chars.len())].iter().collect(),
                    true,
                );
                index = end + 1;
            }
            '<' if chars.get(index + 1) == Some(&'<') && chars.get(index + 2) == Some(&'<') => {
                end_word!();
                redirect = Some('s');
                index += 3;
                while index < chars.len() && matches!(chars[index], ' ' | '\t') {
                    index += 1;
                }
            }
            '<' if chars.get(index + 1) == Some(&'<') => {
                end_word!();
                index += 2;
                let strip = chars.get(index) == Some(&'-');
                if strip {
                    index += 1;
                }
                while index < chars.len() && matches!(chars[index], ' ' | '\t') {
                    index += 1;
                }
                let (delimiter, quoted, next) = delimiter_word(&chars, index);
                pending.push((delimiter, strip, !quoted, None));
                index = next;
            }
            '<' => {
                end_word!();
                redirect = Some('<');
                index += 1;
                while index < chars.len() && matches!(chars[index], ' ' | '\t') {
                    index += 1;
                }
            }
            '>' => {
                let digits = word
                    .as_ref()
                    .map(|w| w.text().chars().all(|d| d.is_ascii_digit()))
                    .unwrap_or(false);
                if digits {
                    word = None;
                } else {
                    end_word!();
                }
                index += 1;
                while index < chars.len() && matches!(chars[index], '>' | '&' | '|') {
                    index += 1;
                }
                while index < chars.len() && matches!(chars[index], ' ' | '\t') {
                    index += 1;
                }
                redirect = Some('>');
            }
            _ => {
                let start = index;
                while index < chars.len() && !" \t\n;&|()'\"\\$`<>#".contains(chars[index]) {
                    index += 1;
                }
                if index == start {
                    index += 1;
                }
                push_piece(&mut word, chars[start..index].iter().collect(), true);
            }
        }
    }
    end_command!();
    commands
}

fn find(chars: &[char], from: usize, wanted: char) -> usize {
    let mut index = from;
    while index < chars.len() && chars[index] != wanted {
        index += 1;
    }
    index
}

/// The index of the quote that closes a double-quoted string opened before
/// `from`, stepping over escapes and substitutions.
fn double_quoted(chars: &[char], from: usize) -> usize {
    let mut index = from;
    while index < chars.len() {
        match chars[index] {
            '\\' => index += 2,
            '"' => return index,
            '$' if chars.get(index + 1) == Some(&'(') => index = substitution(chars, index + 2),
            '`' => index = find(chars, index + 1, '`') + 1,
            _ => index += 1,
        }
    }
    chars.len()
}

/// The index just past the `)` that closes a `$(` opened before `from`,
/// stepping over quotes, nested substitutions and heredoc bodies.
fn substitution(chars: &[char], from: usize) -> usize {
    let mut index = from;
    let mut depth = 1;
    let mut pending: Vec<(String, bool)> = Vec::new();
    while index < chars.len() {
        match chars[index] {
            '\\' => index += 2,
            '\'' => index = find(chars, index + 1, '\'') + 1,
            '"' => index = double_quoted(chars, index + 1) + 1,
            '(' => {
                depth += 1;
                index += 1;
            }
            ')' => {
                depth -= 1;
                index += 1;
                if depth == 0 {
                    return index;
                }
            }
            '<' if chars.get(index + 1) == Some(&'<') && chars.get(index + 2) != Some(&'<') => {
                index += 2;
                let strip = chars.get(index) == Some(&'-');
                if strip {
                    index += 1;
                }
                while index < chars.len() && matches!(chars[index], ' ' | '\t') {
                    index += 1;
                }
                let (delimiter, _, next) = delimiter_word(chars, index);
                pending.push((delimiter, strip));
                index = next;
            }
            '\n' => {
                index += 1;
                for (delimiter, strip) in std::mem::take(&mut pending) {
                    index = heredoc(chars, index, &delimiter, strip).1;
                }
            }
            _ => index += 1,
        }
    }
    chars.len()
}

/// A heredoc's delimiter, whether it was quoted, and the index after it.
fn delimiter_word(chars: &[char], from: usize) -> (String, bool, usize) {
    let mut index = from;
    let mut delimiter = String::new();
    let mut quoted = false;
    while index < chars.len() && !" \t\n;&|()<>".contains(chars[index]) {
        match chars[index] {
            '\'' | '"' => {
                let quote = chars[index];
                quoted = true;
                let end = find(chars, index + 1, quote);
                delimiter.extend(&chars[index + 1..end.min(chars.len())]);
                index = end + 1;
            }
            '\\' => {
                quoted = true;
                if let Some(next) = chars.get(index + 1) {
                    delimiter.push(*next);
                }
                index += 2;
            }
            other => {
                delimiter.push(other);
                index += 1;
            }
        }
    }
    (delimiter, quoted, index.min(chars.len()))
}

/// A heredoc's body starting at `from`, and the index after its closing line.
fn heredoc(chars: &[char], from: usize, delimiter: &str, strip: bool) -> (String, usize) {
    let mut index = from;
    let mut body = String::new();
    while index < chars.len() {
        let end = find(chars, index, '\n');
        let line: String = chars[index..end].iter().collect();
        let bare = if strip {
            line.trim_start_matches('\t')
        } else {
            line.as_str()
        };
        if bare == delimiter {
            return (body, (end + 1).min(chars.len()));
        }
        body.push_str(&line);
        body.push('\n');
        index = end + 1;
    }
    (body, chars.len())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rules(command: &str) -> Vec<(&'static str, String)> {
        findings(command)
            .into_iter()
            .map(|f| (f.rule, f.span))
            .collect()
    }

    #[test]
    fn an_idiom_in_a_message_is_quoted_as_written() {
        assert_eq!(
            rules("git commit -m \"The Low-Hanging  fruit here\""),
            vec![("P1", "Low-Hanging  fruit".to_string())]
        );
    }

    #[test]
    fn an_idiom_in_a_path_or_code_passes() {
        assert!(
            rules("git commit -m \"see plugins/deep-dive/ and `deep dive` and rule-of-thumb.md\"")
                .is_empty()
        );
    }

    #[test]
    fn an_idiom_inside_longer_words_is_no_finding() {
        assert!(
            rules("git commit -m \"Route the circle backend\" -m \"a deep diver\" -m \"undercircle back\"")
                .is_empty()
        );
    }

    #[test]
    fn a_clustered_message_flag_is_read() {
        assert_eq!(
            rules("git commit -am \"a silver bullet\""),
            vec![("P1", "silver bullet".to_string())]
        );
    }

    #[test]
    fn no_verify_is_not_a_notes_flag_for_git() {
        assert!(rules("git commit -n -m \"Cache pages\"").is_empty());
    }

    #[test]
    fn a_heredoc_another_command_reads_is_not_published() {
        assert!(
            rules("cat > notes.md <<'EOF'\n**Why.**\nEOF\ngit commit -m \"Cache pages\"")
                .is_empty()
        );
    }

    #[test]
    fn a_heredoc_the_commit_reads_is_published() {
        assert_eq!(
            rules("git commit -F - <<'EOF'\nCache\n\n**Why.**\nEOF"),
            vec![("P2", "**Why.**".to_string())]
        );
    }

    #[test]
    fn a_heredoc_belongs_to_its_command_when_another_follows() {
        assert_eq!(
            rules("git commit -F - <<'EOF' && git push\nsilver bullet\nEOF"),
            vec![("P1", "silver bullet".to_string())]
        );
    }

    #[test]
    fn a_file_on_standard_input_hides_the_text() {
        assert_eq!(
            rules("git commit -F - < notes.txt"),
            vec![("P3", "notes.txt".to_string())]
        );
    }

    #[test]
    fn a_single_quoted_substitution_is_literal() {
        assert!(rules("gh pr comment 5 --body 'Run $(cat notes.md) to see it'").is_empty());
    }

    #[test]
    fn a_long_flag_with_equals_is_read() {
        assert_eq!(
            rules("gh issue create --title x --body-file=body.md"),
            vec![("P3", "body.md".to_string())]
        );
    }

    #[test]
    fn an_answer_is_read_from_the_structured_output_or_the_result() {
        let finding =
            r#"{"findings": [{"rule": "J2", "span": "CI", "fix": "say continuous integration"}]}"#;
        let wanted = vec![(
            "J2".into(),
            "CI".into(),
            "say continuous integration".into(),
        )];
        assert_eq!(
            answer(&format!(r#"{{"structured_output": {finding}}}"#)),
            Some(wanted.clone())
        );
        let quoted = serde_json::to_string(finding).unwrap();
        assert_eq!(answer(&format!(r#"{{"result": {quoted}}}"#)), Some(wanted));
    }

    #[test]
    fn an_answer_outside_the_schema_is_refused() {
        for reply in [
            "not json",
            r#"{"structured_output": {"findings": [{"rule": "J4", "span": "x", "fix": "y"}]}}"#,
            r#"{"structured_output": {"findings": [{"rule": "J1", "span": "", "fix": "y"}]}}"#,
            r#"{"structured_output": {"findings": [{"rule": "J1", "span": "x"}]}}"#,
            r#"{"structured_output": {"findings": [], "verdict": "ok"}}"#,
            r#"{"structured_output": {}}"#,
        ] {
            assert_eq!(answer(reply), None, "{reply}");
        }
    }

    #[test]
    fn the_published_text_leaves_out_what_no_command_publishes() {
        assert_eq!(
            published_text("echo \"a\" && git commit -m \"Cache pages\" -m \"Skip the template\""),
            "Cache pages\n\nSkip the template"
        );
        assert_eq!(published_text("git push"), "");
    }

    #[test]
    fn a_list_of_bold_words_is_not_a_bold_line() {
        assert!(rules("gh pr create --body \"**a** and **b**\"").is_empty());
    }
}
