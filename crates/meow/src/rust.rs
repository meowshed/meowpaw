// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-rust`: whether a work tree holds Rust, what its manifests and
//! toolchain file say, the `[stages]` table that configuration binds, the
//! settings behind the stages that are missing, and whether the pinned
//! toolchain is the one installed (SPC-1310).
//!
//! `status`, `bind` and `check` read the files git tracks, run git alone and
//! write nothing (SPC-1190). `toolchain` runs `rustc --version`, which is the
//! one tool it starts.

use crate::detect::{self, Marker};
use crate::pack::{self, Binding, Candidate, Clean, Pin};
use crate::profile::{self, Profile};
use std::collections::BTreeSet;
use std::path::PathBuf;

const UNRESOLVED: u8 = 3;
const FOUND: u8 = 1;
const USAGE: &str = "usage: meow-rust status | bind | check | toolchain";

/// The groups clippy turns on when nothing configures it, and the ones it
/// leaves off (RES-0361).
const DEFAULT_GROUPS: [&str; 5] = ["correctness", "suspicious", "style", "complexity", "perf"];
const OPT_IN_GROUPS: [&str; 4] = ["pedantic", "restriction", "nursery", "cargo"];

/// What cargo's default test command checks.
const DEFAULT_CHECKS: [&str; 3] = ["unit tests", "integration tests", "documentation examples"];

/// What `check` checks, named in its clean report (REQ-2432).
const CHECKS: [&str; 3] = [
    "the editions the manifests declare",
    "the workspace's lint inheritance",
    "the build output's ignore file",
];

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 4] = [
    crate::help::Entry {
        name: "status",
        determines: "how Rust is configured in this repository",
        by_hand: "list the tracked `Cargo.toml` files and read each one's edition, lint tables and workspace",
        lines: "meow-rust profile: unknown unresolved: workspace: scope: marker: edition: lockfile: toolchain: clippy nextest:",
        json: "",
    },
    crate::help::Entry {
        name: "bind",
        determines: "the `[stages]` lines that bind each stage to the cargo command the manifests call for",
        by_hand: "read the top manifest for a workspace, features and a library, and write each stage's cargo command",
        lines: "meow-rust profile: unknown unresolved: # [stages] format lint check test build",
        json: "",
    },
    crate::help::Entry {
        name: "check",
        determines: "whether the manifests leave an edition, a lint inheritance or an ignore file unsaid",
        by_hand: "read each manifest's package table and lints, and the ignore files beside the top manifest",
        lines: "meow-rust profile: unknown unresolved: <path> target no clippy",
        json: "",
    },
    crate::help::Entry {
        name: "toolchain",
        determines: "whether the toolchain the repository pins is the one installed",
        by_hand: "read the `channel` of the toolchain file and compare it with the output of `rustc --version`",
        lines: "meow-rust profile: unknown unresolved: toolchain: tool",
        json: "",
    },
];

pub fn main(args: &[String]) -> u8 {
    if let Some(code) = crate::help::answer("meow-rust", &HELP, args) {
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
        ["toolchain"] => toolchain(),
        _ => {
            eprintln!("{USAGE}");
            2
        }
    }
}

/// The work tree as the program reads it: its root, what git tracks and the profile.
struct Repo {
    root: PathBuf,
    tracked: BTreeSet<String>,
    profile: toml::Table,
}

impl Repo {
    /// The repository, or the reason it can't be read. `say` gets the
    /// profile's state and its unknown keys (SPC-1080).
    fn read(say: fn(&str)) -> Result<Repo, String> {
        let root = profile::repository_root();
        let root = std::fs::canonicalize(&root).unwrap_or(root);
        let tracked = detect::tracked(&root);
        if markers(&tracked).is_empty() {
            return Err("not a Rust repository".into());
        }
        let read = profile::read(&root);
        for line in profile::report(&read) {
            say(&line);
        }
        let profile = match read {
            Profile::Absent => return Err(format!("no profile at {}", profile::PROFILE)),
            Profile::Unparseable(message) => {
                return Err(format!("the profile doesn't parse: {message}"));
            }
            Profile::Parsed(table, _) => table,
        };
        Ok(Repo {
            root,
            tracked,
            profile,
        })
    }

    fn declared(&self, stage: &str) -> bool {
        profile::stages(&self.profile)
            .and_then(toml::Value::as_table)
            .is_some_and(|stages| stages.contains_key(stage))
    }
}

/// Each tracked `Cargo.toml`, wherever it lies (REQ-2332, REQ-0133).
pub(crate) fn markers(tracked: &BTreeSet<String>) -> Vec<Marker> {
    detect::by_name(tracked, &["Cargo.toml"])
}

/// A tracked manifest, parsed.
struct Manifest {
    file: String,
    directory: String,
    table: toml::Table,
}

/// Every tracked manifest, or the first that can't be read.
fn manifests(repo: &Repo) -> Result<Vec<Manifest>, String> {
    let mut found = Vec::new();
    for marker in markers(&repo.tracked) {
        let text = std::fs::read_to_string(repo.root.join(&marker.file))
            .map_err(|error| format!("{} can't be read: {error}", marker.file))?;
        let table = text.parse::<toml::Table>().map_err(|error| {
            format!(
                "{} doesn't parse as TOML: {}",
                marker.file,
                error.message().replace('\n', " ")
            )
        })?;
        found.push(Manifest {
            file: marker.file,
            directory: marker.directory,
            table,
        });
    }
    Ok(found)
}

fn in_dir(directory: &str, name: &str) -> String {
    if directory == "." {
        name.to_string()
    } else {
        format!("{directory}/{name}")
    }
}

fn within(directory: &str, ancestor: &str) -> bool {
    ancestor == "." || directory == ancestor || directory.starts_with(&format!("{ancestor}/"))
}

fn table_of<'a>(table: &'a toml::Table, key: &str) -> Option<&'a toml::Table> {
    table.get(key).and_then(toml::Value::as_table)
}

/// The manifests no other manifest sits above.
fn tops(manifests: &[Manifest]) -> Vec<&Manifest> {
    manifests
        .iter()
        .filter(|m| {
            !manifests
                .iter()
                .any(|n| n.directory != m.directory && within(&m.directory, &n.directory))
        })
        .collect()
}

/// The one workspace `bind` binds: the top manifest and every manifest below it.
struct Workspace<'a> {
    top: &'a Manifest,
    members: Vec<&'a Manifest>,
}

/// The workspace, or why several top manifests have none.
fn workspace(manifests: &[Manifest]) -> Result<Workspace<'_>, String> {
    let tops = tops(manifests);
    match tops.as_slice() {
        [top] => Ok(Workspace {
            top,
            members: manifests
                .iter()
                .filter(|m| within(&m.directory, &top.directory))
                .collect(),
        }),
        several => Err(format!(
            "several Cargo manifests outside one workspace: {}",
            several
                .iter()
                .map(|m| m.file.as_str())
                .collect::<Vec<_>>()
                .join(", ")
        )),
    }
}

impl Workspace<'_> {
    fn declares_workspace(&self) -> bool {
        table_of(&self.top.table, "workspace").is_some()
    }

    fn has_features(&self) -> bool {
        self.members
            .iter()
            .any(|m| table_of(&m.table, "features").is_some_and(|f| !f.is_empty()))
    }

    fn has_library(&self, repo: &Repo) -> bool {
        self.members.iter().any(|m| {
            m.table.contains_key("lib")
                || repo.tracked.contains(&in_dir(&m.directory, "src/lib.rs"))
        })
    }

    /// The words every cargo command but `fmt` takes: the manifest, the
    /// workspace and, where a manifest declares features, all of them.
    fn scope(&self) -> String {
        let mut words = String::new();
        if self.top.directory != "." {
            words.push_str(&format!(" --manifest-path {}", self.top.file));
        }
        if self.declares_workspace() {
            words.push_str(" --workspace");
        }
        if self.has_features() {
            words.push_str(" --all-features");
        }
        words
    }

    fn format_command(&self) -> String {
        let manifest = if self.top.directory == "." {
            String::new()
        } else {
            format!(" --manifest-path {}", self.top.file)
        };
        let all = if self.declares_workspace() {
            " --all"
        } else {
            ""
        };
        format!("cargo fmt{manifest}{all} --check")
    }
}

/// The level a lint table gives a lint: a string, or a table's `level`.
fn level(value: &toml::Value) -> Option<&str> {
    value
        .as_str()
        .or_else(|| value.get("level").and_then(toml::Value::as_str))
}

/// The clippy groups a run of the top manifest's `lint` stage enables: the
/// five clippy turns on by default, less each the manifest sets to `allow`,
/// plus each other group it raises (REQ-2432, RES-0361).
fn clippy_groups(top: &Manifest) -> Vec<String> {
    let inherited = table_of(&top.table, "workspace")
        .and_then(|w| table_of(w, "lints"))
        .and_then(|l| table_of(l, "clippy"));
    let own = table_of(&top.table, "lints").and_then(|l| table_of(l, "clippy"));
    let set = |group: &str| {
        own.and_then(|t| t.get(group))
            .or_else(|| inherited.and_then(|t| t.get(group)))
            .and_then(level)
    };
    let mut groups: Vec<String> = DEFAULT_GROUPS
        .iter()
        .filter(|group| set(group) != Some("allow"))
        .map(|group| group.to_string())
        .collect();
    groups.extend(
        OPT_IN_GROUPS
            .iter()
            .filter(|group| matches!(set(group), Some("warn" | "deny" | "forbid")))
            .map(|group| group.to_string()),
    );
    groups
}

/// The toolchain file nearest `directory`, with its channel: `rust-toolchain`
/// before `rust-toolchain.toml` in one directory, and the nearer directory
/// first (RES-0361).
fn pinned(repo: &Repo, directory: &str) -> Option<(String, Option<String>)> {
    let mut dir = directory.to_string();
    loop {
        for name in ["rust-toolchain", "rust-toolchain.toml"] {
            let file = in_dir(&dir, name);
            if repo.tracked.contains(&file) {
                let text = std::fs::read_to_string(repo.root.join(&file)).unwrap_or_default();
                return Some((file, channel(&text)));
            }
        }
        if dir == "." {
            return None;
        }
        dir = match dir.rsplit_once('/') {
            Some((parent, _)) => parent.to_string(),
            None => ".".to_string(),
        };
    }
}

/// The `channel` of a toolchain file: the key of its `[toolchain]` table, or
/// the first line of a file that isn't TOML.
fn channel(text: &str) -> Option<String> {
    match text.parse::<toml::Table>() {
        Ok(table) => table_of(&table, "toolchain")
            .and_then(|t| t.get("channel"))
            .and_then(toml::Value::as_str)
            .map(str::to_string),
        Err(_) => text
            .lines()
            .map(str::trim)
            .find(|line| !line.is_empty())
            .map(str::to_string),
    }
}

/// A channel that names a version, `1.99` or `1.99.0`, and no other channel.
fn version_of(channel: &str) -> Option<usize> {
    let parts: Vec<&str> = channel.split('.').collect();
    let numeric = parts
        .iter()
        .all(|p| !p.is_empty() && p.chars().all(|c| c.is_ascii_digit()));
    (numeric && (parts.len() == 2 || parts.len() == 3)).then_some(parts.len())
}

fn status() -> u8 {
    println!("meow-rust status");
    let repo = match Repo::read(|line| println!("{line}")) {
        Ok(repo) => repo,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let manifests = match manifests(&repo) {
        Ok(manifests) => manifests,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let parts = detect::parts(&repo.root);
    for (directory, files) in detect::by_directory(&markers(&repo.tracked)) {
        println!("{}", detect::scope(&parts, &directory));
        for file in files {
            println!("marker: {file}");
            let Some(manifest) = manifests.iter().find(|m| m.file == file) else {
                continue;
            };
            if let Some(package) = table_of(&manifest.table, "package") {
                match package.get("edition") {
                    Some(edition) => println!(
                        "edition: {}",
                        edition.as_str().unwrap_or("inherited from the workspace")
                    ),
                    None => {
                        println!("edition: none declared, so cargo compiles it as the 2015 edition")
                    }
                }
            }
            if table_of(&manifest.table, "workspace").is_some() {
                println!("workspace: {file} declares one");
            }
        }
    }
    match detect::by_name(&repo.tracked, &["Cargo.lock"]).first() {
        Some(lock) => println!("lockfile: {} tracked", lock.file),
        None => println!("lockfile: none tracked"),
    }
    match workspace(&manifests) {
        Ok(ws) => {
            match pinned(&repo, &ws.top.directory) {
                Some((file, Some(channel))) => println!("toolchain: {file} pins {channel}"),
                Some((file, None)) => println!("toolchain: {file} pins no channel"),
                None => println!("toolchain: nothing pinned"),
            }
            println!("clippy groups: {}", clippy_groups(ws.top).join(", "));
            let nextest = in_dir(&ws.top.directory, ".config/nextest.toml");
            if repo.tracked.contains(&nextest) {
                println!("nextest: {nextest}");
            }
        }
        Err(reason) => println!("workspace: {reason}"),
    }
    0
}

/// Every stage's binding, in the order `bind` prints them (SPC-1310).
fn bindings(repo: &Repo, ws: &Workspace<'_>) -> Vec<Binding> {
    let scope = ws.scope();
    let groups = clippy_groups(ws.top);
    let format = Binding::bound("format", "rustfmt", &ws.format_command());
    let lint = Binding::bound(
        "lint",
        "clippy",
        &format!("cargo clippy{scope} --all-targets -- -D warnings"),
    )
    .note(&format!("clippy groups run: {}", groups.join(", ")));
    let check = Binding::bound(
        "check",
        "cargo",
        &format!("cargo check{scope} --all-targets"),
    );
    let nextest_file = in_dir(&ws.top.directory, ".config/nextest.toml");
    let nextest = repo.tracked.contains(&nextest_file);
    // cargo-nextest runs no doctests, so with a library it is followed by
    // `cargo test --doc`; without one there are no doctests to run (RES-0361).
    let nextest_command = if ws.has_library(repo) {
        format!("cargo nextest run{scope} && cargo test --doc{scope}")
    } else {
        format!("cargo nextest run{scope}")
    };
    let candidates = [
        Candidate::new(
            "cargo-nextest",
            &nextest_command,
            if nextest { vec![nextest_file] } else { vec![] },
        )
        .covering(&DEFAULT_CHECKS),
        Candidate::new(
            "cargo",
            &format!("cargo test{scope}"),
            if nextest {
                vec![]
            } else {
                vec![ws.top.file.clone()]
            },
        )
        .covering(&DEFAULT_CHECKS),
    ];
    let test = pack::choose("test", &candidates, "Cargo.toml")
        .short_of("cargo test", &DEFAULT_CHECKS)
        .requiring("documentation examples");
    let build = Binding::bound("build", "cargo", &format!("cargo build{scope}"));
    vec![format, lint, check, test, build]
}

/// The runners whose configuration sits at the root, with the pack that reads
/// their tasks.
fn runners(repo: &Repo) -> Vec<(&'static str, &'static str, &'static str)> {
    [
        ("mise.toml", "mise", "meow-mise"),
        (".mise.toml", "mise", "meow-mise"),
        ("Taskfile.yml", "Task", "meow-gotask"),
        ("Taskfile.yaml", "Task", "meow-gotask"),
    ]
    .into_iter()
    .filter(|(file, _, _)| repo.tracked.contains(*file))
    .collect()
}

/// A `[stages]` table bound from what the repository committed, never from
/// what is installed, and printed, never written. It exits 0 once the table is
/// printed, because a stage printed with its reason is settled.
fn bind() -> u8 {
    // What `bind` prints is pasted into the profile, so the state goes to
    // standard error.
    let repo = match Repo::read(|line| eprintln!("{line}")) {
        Ok(repo) => repo,
        Err(reason) => {
            println!("meow-rust bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let manifests = match manifests(&repo) {
        Ok(manifests) => manifests,
        Err(reason) => {
            println!("meow-rust bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    println!("# meow-rust bind: paste what follows into .meowpaw/profile.toml");
    println!("[stages]");
    let mut notes = Vec::new();
    let table = match workspace(&manifests) {
        Ok(ws) => {
            if let Some((file, Some(channel))) = pinned(&repo, &ws.top.directory)
                && version_of(&channel).is_some()
            {
                notes.push(format!(
                    "{file} pins {channel}; rustup runs each stage under it, and meow-rust toolchain compares it with the installed one"
                ));
            }
            bindings(&repo, &ws)
        }
        Err(reason) => pack::waiting(&reason),
    };
    for binding in table {
        if !repo.declared(&binding.stage) {
            binding.lines().iter().for_each(|line| println!("{line}"));
        }
    }
    for note in notes {
        println!("# {note}");
    }
    for (file, runner, pack) in runners(&repo) {
        println!(
            "# {file} configures {runner}; to bind a stage to its tasks, run {pack} bind, since this pack doesn't read them"
        );
    }
    0
}

/// Whether an ignore file the repository tracks ignores `path`. A global
/// excludes file and `.git/info/exclude` protect one clone only, so they
/// don't count.
fn ignored(repo: &Repo, path: &str) -> bool {
    let Ok(done) = profile::reading_git()
        .args(["check-ignore", "--verbose", "--", path])
        .current_dir(&repo.root)
        .output()
    else {
        return false;
    };
    String::from_utf8_lossy(&done.stdout).lines().any(|line| {
        let mut parts = line.splitn(3, ':');
        let (Some(source), Some(_), Some(rest)) = (parts.next(), parts.next(), parts.next()) else {
            return false;
        };
        let pattern = rest.split('\t').next().unwrap_or("");
        repo.tracked.contains(source) && !pattern.starts_with('!')
    })
}

/// The findings in the settings behind the stages (REQ-2434, REQ-2442).
fn findings(repo: &Repo, manifests: &[Manifest]) -> Vec<String> {
    let mut found = Vec::new();
    for manifest in manifests {
        if table_of(&manifest.table, "package").is_some_and(|p| !p.contains_key("edition")) {
            found.push(format!(
                "{}: no edition, so cargo compiles it as the 2015 edition",
                manifest.file
            ));
        }
    }
    if let Ok(ws) = workspace(manifests)
        && table_of(&ws.top.table, "workspace")
            .and_then(|w| table_of(w, "lints"))
            .is_some()
    {
        for member in &ws.members {
            let inherits = table_of(&member.table, "lints")
                .and_then(|l| l.get("workspace"))
                .and_then(toml::Value::as_bool)
                == Some(true);
            if table_of(&member.table, "package").is_some() && !inherits {
                found.push(format!(
                    "{} doesn't inherit the workspace's lints: set workspace = true under [lints]",
                    member.file
                ));
            }
        }
    }
    for top in tops(manifests) {
        let output = in_dir(&top.directory, "target");
        if !ignored(repo, &format!("{output}/.probe")) {
            found.push(format!(
                "{output} isn't ignored, and cargo writes its build output there"
            ));
        }
    }
    found
}

/// Exits 1 on any finding, and prints the groups a clean report covers.
fn check() -> u8 {
    println!("meow-rust check");
    let repo = match Repo::read(|line| println!("{line}")) {
        Ok(repo) => repo,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let manifests = match manifests(&repo) {
        Ok(manifests) => manifests,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let found = findings(&repo, &manifests);
    if !found.is_empty() {
        for finding in &found {
            println!("{finding}");
        }
        return FOUND;
    }
    let clean = Clean {
        said: "no findings".into(),
        groups: CHECKS.iter().map(|c| c.to_string()).collect(),
        hides_below_a_level: false,
        level: None,
    };
    match clean.line() {
        Ok(line) => println!("{line}"),
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    }
    if let Ok(ws) = workspace(&manifests) {
        println!("clippy groups: {}", clippy_groups(ws.top).join(", "));
    }
    0
}

/// Compares the pinned toolchain with the installed one (REQ-2428).
fn toolchain() -> u8 {
    println!("meow-rust toolchain");
    let repo = match Repo::read(|line| println!("{line}")) {
        Ok(repo) => repo,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let manifests = match manifests(&repo) {
        Ok(manifests) => manifests,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let ws = match workspace(&manifests) {
        Ok(ws) => ws,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let (file, channel) = match pinned(&repo, &ws.top.directory) {
        Some(found) => found,
        None => {
            println!("toolchain: nothing pinned");
            return 0;
        }
    };
    let Some(channel) = channel else {
        println!("toolchain: {file} pins no channel");
        return 0;
    };
    let Some(precision) = version_of(&channel) else {
        println!("toolchain: {file} pins the {channel} channel, no version");
        return 0;
    };
    let pin = Pin {
        tool: "rust".into(),
        pinned: channel,
        declared_by: file,
    };
    let done = std::process::Command::new("rustc")
        .arg("--version")
        .current_dir(repo.root.join(&ws.top.directory))
        .stdin(std::process::Stdio::null())
        .output();
    let done = match done {
        Ok(done) => done,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            println!("tool absent: rustc");
            return UNRESOLVED;
        }
        Err(error) => {
            println!("tool broken: rustc didn't start: {error}");
            return UNRESOLVED;
        }
    };
    if !done.status.success() {
        let said = String::from_utf8_lossy(&done.stderr);
        let said = said.lines().next().unwrap_or("").trim();
        let reason = pin.against(None).unwrap_err();
        println!("unresolved: {reason}: {said}");
        return UNRESOLVED;
    }
    let stdout = String::from_utf8_lossy(&done.stdout);
    let first = stdout.lines().next().unwrap_or("").trim();
    let mut words = first.split_whitespace();
    let version = match (words.next(), words.next()) {
        (Some("rustc"), Some(version)) => version,
        _ => {
            println!("tool broken: rustc printed {first}");
            return UNRESOLVED;
        }
    };
    let installed = version
        .split('.')
        .take(precision)
        .collect::<Vec<_>>()
        .join(".");
    match pin.against(Some(&installed)) {
        Ok(line) => {
            println!("{line}");
            0
        }
        Err(reason) => {
            println!("unresolved: {reason}");
            UNRESOLVED
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_channel_names_a_version_by_its_numbers_alone() {
        assert_eq!(version_of("1.99"), Some(2));
        assert_eq!(version_of("1.99.0"), Some(3));
        assert_eq!(version_of("stable"), None);
        assert_eq!(version_of("nightly-2026-09-01"), None);
        assert_eq!(version_of("1.99.0-beta.1"), None);
    }

    #[test]
    fn a_plain_toolchain_file_is_its_first_line() {
        assert_eq!(channel("1.99.0\n").as_deref(), Some("1.99.0"));
        assert_eq!(
            channel("[toolchain]\nchannel = \"stable\"\n").as_deref(),
            Some("stable")
        );
        assert_eq!(channel("[toolchain]\nprofile = \"minimal\"\n"), None);
    }
}
