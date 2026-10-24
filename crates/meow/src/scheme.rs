// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-scheme`: where a work tree holds a Scheme project, which
//! implementation runs it, the `[stages]` table its configuration binds, and
//! the stage commands that write bytecode into the tree (SPC-1390).
//!
//! It reads the files git tracks, runs git alone and starts no Scheme
//! implementation (SPC-1190).

use crate::detect::{self, Marker};
use crate::pack::{self, Binding, Candidate, Host, STAGES};
use crate::perdir::{self, FOUND, Tree, UNRESOLVED, in_dir, join, runs, words};
use std::collections::BTreeSet;

const LANGUAGE: &str = "Scheme";
const UNIT: &str = "meow-scheme";
const USAGE: &str = "usage: meow-scheme status | bind | check";

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 3] = [
    crate::help::Entry {
        name: "status",
        determines: "where this repository holds a Scheme project, which implementation runs it, and how its tests are discovered",
        by_hand: "list the tracked info.rkt, .egg and guix.scm files, then read info.rkt for test-omit-paths and test-include-paths",
        lines: "meow-scheme profile: profile error: unknown key: scope: marker: implementation: test commit: ignore: unresolved:",
        json: "",
    },
    crate::help::Entry {
        name: "bind",
        determines: "the `[stages]` lines that bind each stage to the Scheme tool the repository configures",
        by_hand: "identify the implementation from its manifest, then write its test command; Racket binds raco test and nothing else",
        lines: "meow-scheme profile: profile error: unknown key: # [stages] format lint check test build unresolved:",
        json: "",
    },
    crate::help::Entry {
        name: "check",
        determines: "whether a stage's command writes bytecode into the tree, and whether compiled/ is ignored and untracked",
        by_hand: "read each stage command for raco make or --make, then .gitignore and the tracked files against compiled/",
        lines: "meow-scheme profile: profile error: unknown key: <path> format lint check test build no unresolved:",
        json: "",
    },
];

pub fn main(args: &[String]) -> u8 {
    if let Some(code) = crate::help::answer(UNIT, &HELP, args) {
        return code;
    }
    match args
        .iter()
        .map(String::as_str)
        .collect::<Vec<_>>()
        .as_slice()
    {
        ["status"] => status(),
        ["bind"] => bind(),
        ["check"] => check(),
        _ => {
            eprintln!("{USAGE}");
            2
        }
    }
}

/// The implementation a manifest file names, or none for a file that names no
/// implementation (REQ-2446).
fn implementation(file_name: &str) -> Option<&'static str> {
    match file_name {
        "info.rkt" => Some("Racket"),
        "guix.scm" => Some("Guile"),
        name if name.ends_with(".egg") => Some("CHICKEN"),
        _ => None,
    }
}

/// Each tracked manifest: `info.rkt`, a `.egg` file or `guix.scm` (REQ-2350,
/// REQ-3048).
pub(crate) fn markers(tracked: &BTreeSet<String>) -> Vec<Marker> {
    tracked
        .iter()
        .filter(|path| implementation(path.rsplit('/').next().unwrap_or(path)).is_some())
        .map(|path| Marker {
            file: path.clone(),
            directory: detect::directory_of(path),
        })
        .collect()
}

/// One project: its directory, its manifests and the implementation they name.
struct Project {
    dir: String,
    manifests: Vec<String>,
    system: Result<&'static str, String>,
}

impl Project {
    fn is_racket(&self) -> bool {
        self.system == Ok("Racket")
    }
}

fn projects(tree: &Tree) -> Vec<Project> {
    detect::by_directory(&markers(&tree.tracked))
        .into_iter()
        .map(|(dir, files)| {
            let hosts: Vec<Host> = ["Racket", "CHICKEN", "Guile"]
                .iter()
                .map(|name| Host {
                    name: name.to_string(),
                    markers: files
                        .iter()
                        .filter(|f| implementation(f.rsplit('/').next().unwrap_or(f)) == Some(name))
                        .cloned()
                        .collect(),
                })
                .collect();
            let system = pack::host(&hosts).map(|host| match host.name.as_str() {
                "Racket" => "Racket",
                "CHICKEN" => "CHICKEN",
                _ => "Guile",
            });
            Project {
                dir,
                manifests: files,
                system,
            }
        })
        .collect()
}

fn read(say: fn(&str)) -> Result<Tree, String> {
    Tree::read(LANGUAGE, markers, say)
}

fn status() -> u8 {
    println!("{UNIT} status");
    let tree = match read(|line| println!("{line}")) {
        Ok(tree) => tree,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let parts = detect::parts(&tree.root);
    let mut code = 0;
    for project in projects(&tree) {
        println!("{}", detect::scope(&parts, &project.dir));
        for manifest in &project.manifests {
            println!("marker: {manifest}");
        }
        match &project.system {
            Ok(system) => println!("implementation: {system}, from {}", project.manifests[0]),
            Err(reason) => {
                println!("unresolved: {reason}");
                code = UNRESOLVED;
            }
        }
        if project.is_racket() {
            let info = join(&project.dir, "info.rkt");
            let text = tree.text(&info).unwrap_or_default();
            let declared: Vec<&str> = ["test-omit-paths", "test-include-paths"]
                .into_iter()
                .filter(|key| text.contains(key))
                .collect();
            if declared.is_empty() {
                println!(
                    "test discovery: {info} declares none, so raco test runs every file under the directory"
                );
            } else {
                println!("test discovery: {info} declares {}", declared.join(" and "));
            }
            println!("commit: {info}, which is project state");
            println!("ignore: compiled/, which is bytecode written beside each source");
        }
    }
    code
}

/// The five stages for one project, in the order `bind` prints them.
fn bindings(project: &Project) -> Vec<Binding> {
    let system = match &project.system {
        Ok(system) => *system,
        Err(reason) => return pack::waiting(reason),
    };
    if !project.is_racket() {
        let why = format!("no command is bound for {system}");
        return STAGES
            .iter()
            .map(|stage| Binding::unbound(stage, &why))
            .collect();
    }
    let compiled = "raco make writes compiled/ beside each source";
    let test = pack::choose(
        "test",
        &[Candidate::new(
            "raco",
            &in_dir(&project.dir, "raco test --table ."),
            project.manifests.clone(),
        )],
        "info.rkt",
    )
    .note("evidence: captured output with the summary table; exit 0 means every test passed, 2 a timeout and 1 another failure");
    vec![
        Binding::unbound(
            "format",
            "raco fmt has no check mode: it prints the formatted program or rewrites the file",
        ),
        Binding::unbound(
            "lint",
            "looked for a linter the repository committed, and Racket's tools name none",
        ),
        Binding::unbound("check", compiled),
        test,
        Binding::unbound("build", compiled),
    ]
}

/// A table bound from what the repository committed, never from what is
/// installed, and printed, never written (SPC-1190).
fn bind() -> u8 {
    let tree = match read(|line| eprintln!("{line}")) {
        Ok(tree) => tree,
        Err(reason) => {
            println!("{UNIT} bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    println!("# {UNIT} bind: paste what follows into .meowpaw/profile.toml");
    println!("[stages]");
    let found: Vec<(String, Vec<Binding>, bool)> = projects(&tree)
        .iter()
        .map(|p| (p.dir.clone(), bindings(p), p.system.is_ok()))
        .collect();
    for (at, stage) in STAGES.iter().enumerate() {
        if tree.declared(stage) {
            continue;
        }
        let per_dir: Vec<(String, Binding)> = found
            .iter()
            .map(|(dir, all, _)| (dir.clone(), all[at].clone()))
            .collect();
        for line in perdir::merge(stage, &per_dir) {
            println!("{line}");
        }
    }
    if found.iter().all(|(_, _, known)| *known) {
        0
    } else {
        UNRESOLVED
    }
}

fn check() -> u8 {
    println!("{UNIT} check");
    let tree = match read(|line| println!("{line}")) {
        Ok(tree) => tree,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    if !tree.has_profile {
        println!("unresolved: no profile at {}", crate::profile::PROFILE);
        return UNRESOLVED;
    }
    let mut findings = Vec::new();
    let mut unresolved = Vec::new();
    for (stage, command) in tree.commands() {
        let w = words(&command);
        let makes = runs(&command, "raco")
            && (w.contains(&"make") || w.contains(&"--make") || w.contains(&"-y"));
        if makes {
            findings.push(format!(
                "{stage} runs raco make or --make, which writes compiled/ into the tree"
            ));
        }
    }
    for project in projects(&tree) {
        let dir = project.dir.as_str();
        match &project.system {
            Err(reason) => unresolved.push(reason.clone()),
            Ok(_) if project.is_racket() => {
                if !tree.ignored(&join(dir, "compiled/probe.zo")) {
                    findings.push(format!("{dir}: compiled/ isn't ignored"));
                }
                if let Some(file) = tree.under(&join(dir, "compiled/")).first() {
                    findings.push(format!("{dir}: compiled/ is tracked: {file}"));
                }
            }
            Ok(_) => {}
        }
    }
    if !findings.is_empty() {
        for finding in findings {
            println!("{finding}");
        }
        return FOUND;
    }
    if !unresolved.is_empty() {
        for reason in unresolved {
            println!("unresolved: {reason}");
        }
        return UNRESOLVED;
    }
    let clean = pack::Clean {
        said: "no findings".into(),
        groups: ["stages that write bytecode", "the compiled/ directory"]
            .iter()
            .map(|g| g.to_string())
            .collect(),
        hides_below_a_level: false,
        level: None,
    };
    match clean.line() {
        Ok(line) => println!("{line}"),
        Err(reason) => println!("unresolved: {reason}"),
    }
    0
}
