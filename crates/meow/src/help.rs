// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The help every subcommand outside `paw` carries: what it determines, what a
//! person reads to reach the same answer by hand, and the first word of each
//! kind of line it prints (SPC-1080, REQ-1176, REQ-1184).
//!
//! A unit's `main` calls [`answer`] before it dispatches, so `--help` is the
//! same everywhere and a subcommand's entry sits beside its table.

/// One subcommand's help.
pub struct Entry {
    pub name: &'static str,
    pub determines: &'static str,
    pub by_hand: &'static str,
    /// Whitespace-separated first words, as printed. A word in angle brackets
    /// stands for a kind of word: `<id>` an identifier, `<count>` a number,
    /// `<path>` a path, `<hash>` a hexadecimal hash, `<json>` a line that is a
    /// JSON object whose keys `json` names, and `<text>` free text, which is
    /// stated only where the subcommand echoes a word it didn't write, such as
    /// a task's name.
    pub lines: &'static str,
    /// The top-level keys of a JSON answer, or empty where the answer is lines.
    /// A test holds each JSON object the subcommand prints to these keys.
    pub json: &'static str,
}

/// Prints the help `args` ask for and returns the exit status, or returns
/// `None` where `args` ask for none. `<binary> --help` lists each subcommand,
/// and `<binary> <name> --help` prints one's help. `--help` is the first
/// argument after the name and nowhere else, so a target or a command that
/// is the word `--help` still reaches the subcommand.
pub fn answer(binary: &str, entries: &[Entry], args: &[String]) -> Option<u8> {
    let (first, rest) = args.split_first()?;
    if first == "--help" {
        for entry in entries {
            println!("{binary} {}: {}", entry.name, entry.determines);
        }
        return Some(0);
    }
    if rest.first().map(String::as_str) != Some("--help") {
        return None;
    }
    let entry = entries.iter().find(|entry| entry.name == first)?;
    println!("{binary} {}: {}", entry.name, entry.determines);
    println!("by hand: {}", entry.by_hand);
    println!("lines: {}", entry.lines);
    if !entry.json.is_empty() {
        println!("json: {}", entry.json);
    }
    Some(0)
}
