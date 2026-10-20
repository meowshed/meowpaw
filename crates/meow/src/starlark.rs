// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-starlark`: where a work tree holds a Bazel or Buck workspace, which
//! build system evaluates its Starlark, the `[stages]` table its configuration
//! binds, and the stage commands that write into the tree or pass whatever
//! they find (SPC-1385).
//!
//! It reads the files git tracks, runs git alone and starts no Bazel, Buck or
//! buildifier process (SPC-1190).

use crate::detect::{self, Marker};
use crate::pack::{self, Binding, Candidate, Host, STAGES};
use crate::perdir::{self, FOUND, Tree, UNRESOLVED, in_dir, join, runs, words};
use std::collections::BTreeSet;

const LANGUAGE: &str = "Starlark";
const UNIT: &str = "meow-starlark";
const USAGE: &str = "usage: meow-starlark status | bind | check";
const BAZEL: [&str; 4] = ["MODULE.bazel", "REPO.bazel", "WORKSPACE", "WORKSPACE.bazel"];
const BUCK: &str = ".buckconfig";

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 3] = [
    crate::help::Entry {
        name: "status",
        determines: "where this repository holds a Bazel or Buck workspace, which build system evaluates it, and the tools it configures",
        by_hand: "list the tracked MODULE.bazel, REPO.bazel, WORKSPACE, WORKSPACE.bazel and .buckconfig files, then read the .buildifier.json beside each",
        lines: "meow-starlark profile: profile error: unknown key: scope: marker: build tool: commit: ignore: unresolved:",
        json: "",
    },
    crate::help::Entry {
        name: "bind",
        determines: "the `[stages]` lines that bind each stage to the Starlark tool the repository configures",
        by_hand: "match .buildifier.json and the workspace marker with buildifier and bazel, once the build system is known",
        lines: "meow-starlark profile: profile error: unknown key: # [stages] format lint check test build unresolved:",
        json: "",
    },
    crate::help::Entry {
        name: "check",
        determines: "whether a stage's command passes whatever it finds, rewrites files, or leaves Bazel's symlinks and Buck's output in the tree",
        by_hand: "read each stage command for buildifier with --format or without --mode=check and for bazel without --symlink_prefix=/, then .gitignore against bazel-* and buck-out/",
        lines: "meow-starlark profile: profile error: unknown key: <path> format lint check test build no unresolved:",
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

/// Each tracked Bazel boundary file or `.buckconfig` (REQ-2348, REQ-3048).
pub(crate) fn markers(tracked: &BTreeSet<String>) -> Vec<Marker> {
    let mut names = BAZEL.to_vec();
    names.push(BUCK);
    detect::by_name(tracked, &names)
}

/// One workspace: its directory, its markers and the build system they name.
struct Workspace {
    dir: String,
    markers: Vec<String>,
    system: Result<&'static str, String>,
}

impl Workspace {
    fn is_bazel(&self) -> bool {
        self.system == Ok("Bazel")
    }

    fn is_buck(&self) -> bool {
        self.system == Ok("Buck")
    }
}

fn workspaces(tree: &Tree) -> Vec<Workspace> {
    let found = markers(&tree.tracked);
    detect::by_directory(&found)
        .into_iter()
        .map(|(dir, files)| {
            let of = |wanted: &dyn Fn(&str) -> bool| -> Vec<String> {
                files
                    .iter()
                    .filter(|f| wanted(f.rsplit('/').next().unwrap_or(f)))
                    .cloned()
                    .collect()
            };
            let hosts = [
                Host {
                    name: "Bazel".into(),
                    markers: of(&|n| BAZEL.contains(&n)),
                },
                Host {
                    name: "Buck".into(),
                    markers: of(&|n| n == BUCK),
                },
            ];
            let system =
                pack::host(&hosts).map(|h| if h.name == "Bazel" { "Bazel" } else { "Buck" });
            Workspace {
                dir,
                markers: files,
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
    for workspace in workspaces(&tree) {
        println!("{}", detect::scope(&parts, &workspace.dir));
        for marker in &workspace.markers {
            println!("marker: {marker}");
        }
        match &workspace.system {
            Ok(system) => println!("build system: {system}, from {}", workspace.markers[0]),
            Err(reason) => {
                println!("unresolved: {reason}");
                code = UNRESOLVED;
            }
        }
        let config = join(&workspace.dir, ".buildifier.json");
        if tree.tracked.contains(&config) {
            println!("build tool: {config}: buildifier");
        }
    }
    println!("commit: the workspace markers and .buildifier.json, which are project state");
    println!(
        "ignore: bazel-*, which are Bazel's convenience symlinks, and buck-out/, which is Buck's output"
    );
    code
}

/// Whether `.buildifier.json` in the workspace asks for lint warnings.
fn lint_asked(tree: &Tree, config: &str) -> bool {
    tree.text(config)
        .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok())
        .and_then(|json| json.get("lint")?.as_str().map(|s| s == "warn"))
        == Some(true)
}

/// The five stages for one workspace, in the order `bind` prints them.
fn bindings(tree: &Tree, workspace: &Workspace) -> Vec<Binding> {
    if let Err(reason) = &workspace.system {
        return pack::waiting(reason);
    }
    let dir = workspace.dir.as_str();
    let config = join(dir, ".buildifier.json");
    let configured = tree.tracked.contains(&config);
    let candidate =
        |command: &str, by: Vec<String>| Candidate::new("buildifier", &in_dir(dir, command), by);
    let exit = "evidence: captured output; exit 4 means a file needs reformatting or a lint warning was found";
    let format = pack::choose(
        "format",
        &[candidate(
            "buildifier --mode=check -r .",
            if configured {
                vec![config.clone()]
            } else {
                vec![]
            },
        )],
        ".buildifier.json",
    )
    .note(exit);
    let lint = pack::choose(
        "lint",
        &[candidate(
            "buildifier --mode=check --lint=warn -r .",
            if lint_asked(tree, &config) {
                vec![config.clone()]
            } else {
                vec![]
            },
        )],
        ".buildifier.json with \"lint\": \"warn\"",
    )
    .note(exit);
    let check = Binding::unresolved("check", "Starlark has no static types");
    let (test, build) = if workspace.is_bazel() {
        let out = perdir::out_dir(UNIT, dir);
        let marker = vec![workspace.markers[0].clone()];
        let test = pack::choose(
            "test",
            &[Candidate::new(
                "bazel",
                &in_dir(
                    dir,
                    &format!(
                        "mkdir -p \"{out}\" && bazel test --symlink_prefix=/ --build_event_json_file=\"{out}/bep.json\" //..."
                    ),
                ),
                marker.clone(),
            )],
            "a Bazel workspace file",
        )
        .note("evidence: the build event protocol as JSON at bep.json; a workspace with no test target makes bazel test exit 4");
        let build = pack::choose(
            "build",
            &[Candidate::new(
                "bazel",
                &in_dir(dir, "bazel build --symlink_prefix=/ //..."),
                marker,
            )],
            "a Bazel workspace file",
        );
        (test, build)
    } else {
        let why = "Buck2 writes buck-out at the project's root and documents no flag that moves it";
        (
            Binding::unbound("test", why),
            Binding::unbound("build", why),
        )
    };
    vec![format, lint, check, test, build]
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
    let found: Vec<(String, Vec<Binding>, bool)> = workspaces(&tree)
        .iter()
        .map(|w| (w.dir.clone(), bindings(&tree, w), w.system.is_ok()))
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

fn has_word(command: &str, wanted: &[&str]) -> bool {
    words(command).iter().any(|w| wanted.contains(w))
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
    let mut bazel_in_tree = false;
    for (stage, command) in tree.commands() {
        if runs(&command, "buildifier") {
            if words(&command)
                .iter()
                .any(|w| w.starts_with("--format") || w.starts_with("-format"))
            {
                findings.push(format!(
                    "{stage} runs buildifier with --format; its exit status is 0 whatever it finds"
                ));
            }
            if !has_word(&command, &["--mode=check", "-mode=check"]) {
                findings.push(format!(
                    "{stage} runs buildifier without --mode=check, which rewrites the files"
                ));
            }
        }
        if runs(&command, "bazel")
            && has_word(&command, &["build", "test"])
            && !has_word(&command, &["--symlink_prefix=/"])
        {
            bazel_in_tree = true;
            findings.push(format!("{stage} runs bazel without --symlink_prefix=/"));
        }
    }
    for workspace in workspaces(&tree) {
        let dir = workspace.dir.as_str();
        match &workspace.system {
            Err(reason) => unresolved.push(reason.clone()),
            Ok(_) if workspace.is_buck() => {
                if !tree.ignored(&join(dir, "buck-out/probe")) {
                    findings.push(format!("{dir}: buck-out/ isn't ignored"));
                }
            }
            Ok(_) => {
                if bazel_in_tree && !tree.ignored(&join(dir, "bazel-out")) {
                    findings.push(format!("{dir}: bazel-* symlinks aren't ignored"));
                }
            }
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
        groups: [
            "buildifier's mode and exit status",
            "Bazel's symlinks",
            "Buck's output directory",
        ]
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
