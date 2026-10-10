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
    /// `<path>` a path, `<text>` free text, which a test accepts only where the
    /// subcommand echoes text it didn't write.
    pub lines: &'static str,
    /// The top-level keys of a JSON answer, or empty where the answer is lines.
    pub json: &'static str,
}

/// Prints the help `args` ask for and returns the exit status, or returns
/// `None` where `args` ask for none. `meow <unit> --help` lists each
/// subcommand, and `meow <unit> <name> --help` prints one's help.
pub fn answer(unit: &str, entries: &[Entry], args: &[String]) -> Option<u8> {
    let (first, rest) = args.split_first()?;
    if first == "--help" {
        for entry in entries {
            println!("meow {unit} {}: {}", entry.name, entry.determines);
        }
        return Some(0);
    }
    if !rest.iter().any(|arg| arg == "--help") {
        return None;
    }
    let entry = entries.iter().find(|entry| entry.name == first)?;
    println!("meow {unit} {}: {}", entry.name, entry.determines);
    println!("by hand: {}", entry.by_hand);
    println!("lines: {}", entry.lines);
    if !entry.json.is_empty() {
        println!("json: {}", entry.json);
    }
    Some(0)
}
