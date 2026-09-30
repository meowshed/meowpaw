// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The one tool every unit's program is a subcommand of (ADR-1110).
//!
//! Each subcommand sits behind the feature of the unit that ships it, so a
//! unit's binary carries its own code and nothing of another unit's
//! (REQ-0076). SPC-1080 states the crate; each subcommand's behaviour is its
//! unit's specification.

#[cfg(feature = "author")]
mod author;
#[cfg(feature = "git")]
mod git;
#[cfg(feature = "github")]
mod github;
#[cfg(feature = "gotask")]
mod gotask;
#[cfg(feature = "licence")]
mod licence;
#[cfg(feature = "markdown")]
mod markdown;
#[cfg(feature = "mise")]
mod mise;
mod profile;
#[cfg(feature = "prose")]
mod prose;
#[cfg(feature = "record")]
mod record;
#[cfg(feature = "loop")]
mod runloop;
#[cfg(any(feature = "mise", feature = "gotask"))]
mod runner;
#[cfg(feature = "scm")]
mod scm;
#[cfg(feature = "unattended")]
mod unattended;
#[cfg(any(feature = "verbs", feature = "loop"))]
#[cfg_attr(not(feature = "verbs"), allow(dead_code))]
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
        #[cfg(feature = "scm")]
        "scm" => scm::main(rest),
        #[cfg(feature = "git")]
        "git" => git::main(rest),
        #[cfg(feature = "record")]
        "record" => record::main(rest),
        #[cfg(feature = "github")]
        "github" => github::main(rest),
        #[cfg(feature = "licence")]
        "licence" => licence::main(rest),
        #[cfg(feature = "author")]
        "author" => author::main(rest),
        #[cfg(feature = "mise")]
        "mise" => mise::main(rest),
        #[cfg(feature = "gotask")]
        "gotask" => gotask::main(rest),
        #[cfg(feature = "prose")]
        "prose" => prose::main(rest),
        #[cfg(feature = "markdown")]
        "markdown" => markdown::main(rest),
        #[cfg(feature = "unattended")]
        "unattended" => unattended::main(rest),
        #[cfg(feature = "loop")]
        "loop" => runloop::main(rest),
        _ => {
            eprintln!(
                "usage: meow <subcommand> ..., where this build carries: {}",
                carried().join(", ")
            );
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
    if cfg!(feature = "github") {
        names.push("github");
    }
    if cfg!(feature = "licence") {
        names.push("licence");
    }
    if cfg!(feature = "author") {
        names.push("author");
    }
    if cfg!(feature = "mise") {
        names.push("mise");
    }
    if cfg!(feature = "gotask") {
        names.push("gotask");
    }
    if cfg!(feature = "prose") {
        names.push("prose");
    }
    if cfg!(feature = "markdown") {
        names.push("markdown");
    }
    if cfg!(feature = "unattended") {
        names.push("unattended");
    }
    if cfg!(feature = "loop") {
        names.push("loop");
    }
    names
}
