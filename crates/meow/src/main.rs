// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The one tool every unit's program is a subcommand of (ADR-1110).
//!
//! Each subcommand sits behind the feature of the unit that ships it, so a
//! unit's binary carries its own code and nothing of another unit's
//! (REQ-0076). SPC-1080 states the crate; each subcommand's behaviour is its
//! unit's specification.

mod profile;
#[cfg(feature = "verbs")]
mod verbs;

use std::process::ExitCode;

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let (command, rest) = match args.split_first() {
        Some((command, rest)) => (command.as_str(), rest),
        None => ("", &[][..]),
    };
    let code = match command {
        #[cfg(feature = "verbs")]
        "verbs" => verbs::main(rest),
        _ => {
            eprintln!("usage: meow <subcommand> ..., where this build carries: {}", carried().join(", "));
            2
        }
    };
    ExitCode::from(code)
}

/// The subcommands this binary was built with.
fn carried() -> Vec<&'static str> {
    let mut names = Vec::new();
    if cfg!(feature = "verbs") {
        names.push("verbs");
    }
    if cfg!(feature = "scm") {
        names.push("scm");
    }
    if cfg!(feature = "git") {
        names.push("git");
    }
    if cfg!(feature = "record") {
        names.push("record");
    }
    names
}
