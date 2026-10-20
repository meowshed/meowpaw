// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-go`: whether a work tree holds Go, what its modules and linter
//! configuration say, the `[stages]` table that configuration binds, the
//! settings behind the stages that are the wrong shape, and whether the
//! pinned toolchain is the one installed (SPC-1340).
//!
//! `status`, `bind` and `check` read the files git tracks, run git alone and
//! write nothing (SPC-1190). `toolchain` runs `go version`, which is the one
//! tool it starts.

use crate::detect::{self, Marker};
use crate::pack::{self, Binding, Candidate, Clean, Detector, Pin, Reach, SupplyChain};
use crate::profile::{self, Profile};
use std::collections::BTreeSet;
use std::path::PathBuf;
use yaml_rust2::{Yaml, YamlLoader};

const UNRESOLVED: u8 = 3;
const FOUND: u8 = 1;
const USAGE: &str = "usage: meow-go status | bind | check | toolchain";

/// The names golangci-lint reads its configuration from (RES-0102).
const GOLANGCI: [&str; 4] = [
    ".golangci.yml",
    ".golangci.yaml",
    ".golangci.toml",
    ".golangci.json",
];

/// What golangci-lint v2 merged into `staticcheck` or replaced with
/// `linters.default` (RES-0102).
const REMOVED: [&str; 4] = ["stylecheck", "gosimple", "disable-all", "enable-all"];

/// What `check` checks, named in its clean report (REQ-2432).
const CHECKS: [&str; 2] = [
    "the golangci-lint configuration's shape",
    "the linters it names",
];

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 4] = [
    crate::help::Entry {
        name: "status",
        determines: "how Go is configured in this repository",
        by_hand: "list the tracked `go.mod` files and read each one's go line, toolchain line and tool directives",
        lines: "meow-go profile: unknown unresolved: scope: marker: go: toolchain: workspace: tool: golangci-lint: race",
        json: "",
    },
    crate::help::Entry {
        name: "bind",
        determines: "the `[stages]` lines that bind each stage to the go command the module and its linter configuration call for",
        by_hand: "read the module, the golangci-lint configuration and the profile's go table, and write each stage's go command",
        lines: "meow-go profile: unknown unresolved: # [stages] format lint check test build",
        json: "",
    },
    crate::help::Entry {
        name: "check",
        determines: "whether the golangci-lint configuration is the version 2 shape and which supply-chain check the repository runs",
        by_hand: "read the golangci-lint configuration for its version and the linters it names, and the tool directives for govulncheck",
        lines: "meow-go profile: unknown unresolved: <path> supply no",
        json: "",
    },
    crate::help::Entry {
        name: "toolchain",
        determines: "whether the toolchain the module pins is the one installed",
        by_hand: "read the toolchain line of go.mod and compare it with the output of `go version` run with GOTOOLCHAIN=local",
        lines: "meow-go profile: unknown unresolved: toolchain: tool",
        json: "",
    },
];

pub fn main(args: &[String]) -> u8 {
    if let Some(code) = crate::help::answer("meow-go", &HELP, args) {
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
            return Err("not a Go repository".into());
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

    /// The profile's `[go]` table, where it has one.
    fn settings(&self) -> Option<&toml::Table> {
        self.profile.get("go").and_then(toml::Value::as_table)
    }

    fn race_on(&self) -> bool {
        self.settings()
            .and_then(|table| table.get("race"))
            .and_then(toml::Value::as_bool)
            != Some(false)
    }

    /// The nearest tracked file named one of `names`, in `directory` or the
    /// directories above it.
    fn nearest(&self, directory: &str, names: &[&str]) -> Option<String> {
        let mut dir = directory.to_string();
        loop {
            for name in names {
                let file = in_dir(&dir, name);
                if self.tracked.contains(&file) {
                    return Some(file);
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
}

/// Each tracked `go.mod`, wherever it lies (REQ-2334, REQ-0133).
pub(crate) fn markers(tracked: &BTreeSet<String>) -> Vec<Marker> {
    detect::by_name(tracked, &["go.mod"])
}

fn in_dir(directory: &str, name: &str) -> String {
    if directory == "." {
        name.to_string()
    } else {
        format!("{directory}/{name}")
    }
}

/// A tracked `go.mod`, read.
struct Module {
    file: String,
    directory: String,
    go: Option<String>,
    toolchain: Option<String>,
    tools: Vec<String>,
}

/// Every tracked module, or the first that can't be read.
fn modules(repo: &Repo) -> Result<Vec<Module>, String> {
    let mut found = Vec::new();
    for marker in markers(&repo.tracked) {
        let text = std::fs::read_to_string(repo.root.join(&marker.file))
            .map_err(|error| format!("{} can't be read: {error}", marker.file))?;
        let mut module = Module {
            file: marker.file.clone(),
            directory: marker.directory,
            go: None,
            toolchain: None,
            tools: Vec::new(),
        };
        let mut named = false;
        let mut in_tools = false;
        for raw in text.lines() {
            let line = raw.split("//").next().unwrap_or("").trim();
            if line.is_empty() {
                continue;
            }
            if in_tools {
                if line == ")" {
                    in_tools = false;
                } else {
                    module.tools.push(line.to_string());
                }
                continue;
            }
            let mut words = line.split_whitespace();
            match (words.next(), words.next()) {
                (Some("module"), Some(_)) => named = true,
                (Some("go"), Some(version)) => module.go = Some(version.to_string()),
                (Some("toolchain"), Some(name)) => module.toolchain = Some(name.to_string()),
                (Some("tool"), Some("(")) | (Some("tool("), _) => in_tools = true,
                (Some("tool"), Some(package)) => module.tools.push(package.to_string()),
                _ => {}
            }
        }
        if !named {
            return Err(format!(
                "{} doesn't parse: no module directive",
                marker.file
            ));
        }
        found.push(module);
    }
    Ok(found)
}

/// The one module `bind` binds, or why several have none.
fn single(modules: &[Module]) -> Result<&Module, String> {
    match modules {
        [one] => Ok(one),
        several => Err(format!(
            "several Go modules and no single command reaching them: {}",
            several
                .iter()
                .map(|m| m.file.as_str())
                .collect::<Vec<_>>()
                .join(", ")
        )),
    }
}

/// A golangci-lint configuration, as JSON whatever format it was written in.
struct Config {
    file: String,
    value: Result<serde_json::Value, String>,
}

fn config(repo: &Repo, directory: &str) -> Option<Config> {
    let file = repo.nearest(directory, &GOLANGCI)?;
    let text = std::fs::read_to_string(repo.root.join(&file)).unwrap_or_default();
    let value = if file.ends_with(".json") {
        serde_json::from_str(&text).map_err(|error| format!("doesn't parse as JSON: {error}"))
    } else if file.ends_with(".toml") {
        text.parse::<toml::Table>()
            .map_err(|error| {
                format!(
                    "doesn't parse as TOML: {}",
                    error.message().replace('\n', " ")
                )
            })
            .and_then(|table| serde_json::to_value(table).map_err(|error| error.to_string()))
    } else {
        YamlLoader::load_from_str(&text)
            .map_err(|error| format!("doesn't parse as YAML: {error}"))
            .map(|docs| docs.first().map(json).unwrap_or(serde_json::Value::Null))
    };
    Some(Config { file, value })
}

/// A YAML value as JSON.
fn json(yaml: &Yaml) -> serde_json::Value {
    use serde_json::Value;
    match yaml {
        Yaml::Boolean(b) => Value::Bool(*b),
        Yaml::Integer(n) => Value::from(*n),
        Yaml::Real(text) | Yaml::String(text) => Value::String(text.clone()),
        Yaml::Array(items) => Value::Array(items.iter().map(json).collect()),
        Yaml::Hash(map) => Value::Object(
            map.iter()
                .filter_map(|(k, v)| Some((k.as_str()?.to_string(), json(v))))
                .collect(),
        ),
        _ => Value::Null,
    }
}

impl Config {
    fn version(&self) -> Option<String> {
        match self.value.as_ref().ok()?.get("version")? {
            serde_json::Value::String(text) => Some(text.clone()),
            serde_json::Value::Number(number) => Some(number.to_string()),
            _ => None,
        }
    }

    fn has_formatters(&self) -> bool {
        self.value
            .as_ref()
            .ok()
            .and_then(|v| v.get("formatters"))
            .is_some_and(|f| !f.is_null() && f.as_object().is_none_or(|o| !o.is_empty()))
    }

    /// Each merged or removed name the configuration uses: in the linters it
    /// enables or disables, as a key of `linters`, or as a key of its settings.
    fn removed(&self) -> Vec<&'static str> {
        let Some(linters) = self.value.as_ref().ok().and_then(|v| v.get("linters")) else {
            return Vec::new();
        };
        let listed = |key: &str| -> Vec<String> {
            linters
                .get(key)
                .and_then(serde_json::Value::as_array)
                .map(|items| {
                    items
                        .iter()
                        .filter_map(|i| i.as_str().map(str::to_string))
                        .collect()
                })
                .unwrap_or_default()
        };
        let enabled = listed("enable");
        let disabled = listed("disable");
        REMOVED
            .iter()
            .copied()
            .filter(|name| {
                enabled.iter().any(|n| n == name)
                    || disabled.iter().any(|n| n == name)
                    || linters.get(*name).is_some()
                    || linters
                        .get("settings")
                        .is_some_and(|settings| settings.get(*name).is_some())
            })
            .collect()
    }
}

/// A channel or toolchain name's version, `1.26.0` from `go1.26.0`, where it
/// names one.
fn version_of(toolchain: &str) -> Option<&str> {
    let version = toolchain.strip_prefix("go")?;
    let numeric = version
        .split('.')
        .all(|part| !part.is_empty() && part.chars().all(|c| c.is_ascii_digit()));
    (numeric && version.contains('.')).then_some(version)
}

fn status() -> u8 {
    println!("meow-go status");
    let repo = match Repo::read(|line| println!("{line}")) {
        Ok(repo) => repo,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let modules = match modules(&repo) {
        Ok(modules) => modules,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let parts = detect::parts(&repo.root);
    for module in &modules {
        println!("{}", detect::scope(&parts, &module.directory));
        println!("marker: {}", module.file);
        match &module.go {
            Some(version) => println!("go: {version} minimum"),
            None => println!("go: no go line"),
        }
        if let Some(name) = &module.toolchain {
            println!("toolchain: {name} pinned in {}", module.file);
        }
        for tool in &module.tools {
            println!("tool: {tool}");
        }
        match config(&repo, &module.directory) {
            Some(found) => match found.version() {
                Some(version) => println!("golangci-lint: {}, version {version}", found.file),
                None => println!("golangci-lint: {}, declares no version", found.file),
            },
            None => println!("golangci-lint: no configuration tracked"),
        }
    }
    if repo.tracked.contains("go.work") {
        println!("workspace: go.work tracked");
    }
    if repo.race_on() {
        println!("race detector: on");
    } else {
        println!("race detector: off, as [go] race = false records");
    }
    0
}

/// The detector `test` turns on (REQ-2414).
fn race() -> Detector {
    Detector {
        name: "the race detector".into(),
        switch: "-race".into(),
        after: "go test".into(),
        language: "go".into(),
        setting: "race".into(),
    }
}

/// Every stage's binding, in the order `bind` prints them (SPC-1340).
fn bindings(repo: &Repo, module: &Module) -> Vec<Binding> {
    let prefix = if module.directory == "." {
        String::new()
    } else {
        format!("cd {} && ", module.directory)
    };
    let linter = config(repo, &module.directory);
    let format = match linter.as_ref().filter(|c| c.has_formatters()) {
        Some(found) => Binding::unresolved(
            "format",
            &format!(
                "{} configures formatters, and golangci-lint fmt --diff states no exit status to check",
                found.file
            ),
        ),
        None => Binding::bound(
            "format",
            "gofmt",
            &format!("{prefix}test -z \"$(gofmt -l .)\""),
        ),
    };
    let staticcheck = repo
        .nearest(&module.directory, &["staticcheck.conf"])
        .into_iter()
        .collect::<Vec<_>>();
    let candidates = [
        Candidate::new(
            "golangci-lint",
            &format!("{prefix}golangci-lint run"),
            linter.iter().map(|c| c.file.clone()).collect(),
        ),
        Candidate::new(
            "staticcheck",
            &format!("{prefix}staticcheck ./..."),
            staticcheck,
        ),
    ];
    let mut lint = pack::choose(
        "lint",
        &candidates,
        "a .golangci.yml, .golangci.yaml, .golangci.toml or .golangci.json and a staticcheck.conf",
    );
    if lint.command().is_some_and(|c| c.contains("golangci-lint")) {
        lint = lint.note("golangci-lint linters lists the linters this configuration enables");
    }
    let check = Binding::bound("check", "go", &format!("{prefix}go vet ./..."));
    // `go test` runs each documentation example that states its output
    // (RES-0364).
    let test = Binding::bound("test", "go", &format!("{prefix}go test ./..."))
        .covering(&["unit tests", "documentation examples"])
        .requiring("documentation examples")
        .with_detector(&race(), repo.settings());
    let build = Binding::bound("build", "go", &format!("{prefix}go build ./..."));
    vec![format, lint, check, test, build]
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
            println!("meow-go bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let modules = match modules(&repo) {
        Ok(modules) => modules,
        Err(reason) => {
            println!("meow-go bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    println!("# meow-go bind: paste what follows into .meowpaw/profile.toml");
    println!("[stages]");
    let mut notes = Vec::new();
    let table = match single(&modules) {
        Ok(module) => {
            if let Some(name) = &module.toolchain
                && version_of(name).is_some()
            {
                notes.push(format!(
                    "{} pins {name}; the go command runs that toolchain, and meow-go toolchain compares it with the installed one",
                    module.file
                ));
            }
            bindings(&repo, module)
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
    for (file, runner, pack) in [
        ("mise.toml", "mise", "meow-mise"),
        ("Taskfile.yml", "Task", "meow-gotask"),
    ] {
        if repo.tracked.contains(file) {
            println!(
                "# {file} configures {runner}; to bind a stage to its tasks, run {pack} bind, since this pack doesn't read them"
            );
        }
    }
    0
}

/// The supply-chain check the repository declares, as a tool directive or a
/// word of a stage's command (REQ-2436).
fn supply_chain(repo: &Repo, modules: &[Module]) -> Option<SupplyChain> {
    let mut commands: Vec<&str> = Vec::new();
    if let Some(stages) = profile::stages(&repo.profile).and_then(toml::Value::as_table) {
        for value in stages.values() {
            if let Some(command) = value
                .as_str()
                .or_else(|| value.get("command").and_then(toml::Value::as_str))
            {
                commands.push(command);
            }
        }
    }
    let named = commands
        .iter()
        .flat_map(|c| c.split_whitespace())
        .any(|word| {
            word.rsplit('/').next().unwrap_or(word).split('@').next() == Some("govulncheck")
        });
    let declared = modules
        .iter()
        .flat_map(|m| &m.tools)
        .any(|t| t.ends_with("/govulncheck") || t == "govulncheck");
    (named || declared).then(|| SupplyChain {
        tool: "govulncheck".into(),
        transitive: true,
        reach: Reach::Reachability,
    })
}

/// The findings in the golangci-lint configuration (REQ-2434).
fn findings(repo: &Repo, modules: &[Module]) -> Vec<String> {
    let mut found = Vec::new();
    let mut seen = BTreeSet::new();
    for module in modules {
        let Some(linter) = config(repo, &module.directory) else {
            continue;
        };
        if !seen.insert(linter.file.clone()) {
            continue;
        }
        if let Err(reason) = &linter.value {
            found.push(format!("{} {reason}", linter.file));
            continue;
        }
        if linter.version().as_deref() != Some("2") {
            found.push(format!(
                "{}: declares no version \"2\", so it is a v1 configuration",
                linter.file
            ));
        }
        for name in linter.removed() {
            found.push(format!(
                "{} names {name}, which golangci-lint v2 merged or removed",
                linter.file
            ));
        }
    }
    found
}

/// Exits 1 on any finding, and states the supply-chain check's reach.
fn check() -> u8 {
    println!("meow-go check");
    let repo = match Repo::read(|line| println!("{line}")) {
        Ok(repo) => repo,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let modules = match modules(&repo) {
        Ok(modules) => modules,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let found = findings(&repo, &modules);
    let supply = match supply_chain(&repo, &modules) {
        Some(check) => format!("supply chain: {}", check.line()),
        None => "supply chain: none configured".to_string(),
    };
    if !found.is_empty() {
        for finding in &found {
            println!("{finding}");
        }
        println!("{supply}");
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
    println!("{supply}");
    0
}

/// Compares the pinned toolchain with the installed one (REQ-2428).
fn toolchain() -> u8 {
    println!("meow-go toolchain");
    let repo = match Repo::read(|line| println!("{line}")) {
        Ok(repo) => repo,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let modules = match modules(&repo) {
        Ok(modules) => modules,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let module = match single(&modules) {
        Ok(module) => module,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let Some(name) = &module.toolchain else {
        println!("toolchain: nothing pinned");
        return 0;
    };
    let Some(pinned) = version_of(name) else {
        println!(
            "toolchain: {} pins the {name} toolchain, no version",
            module.file
        );
        return 0;
    };
    let pin = Pin {
        tool: "go".into(),
        pinned: pinned.to_string(),
        declared_by: module.file.clone(),
    };
    // GOTOOLCHAIN=local keeps the go command from switching to the pin and
    // reporting it as installed (RES-0364).
    let done = std::process::Command::new("go")
        .arg("version")
        .env("GOTOOLCHAIN", "local")
        .current_dir(repo.root.join(&module.directory))
        .stdin(std::process::Stdio::null())
        .output();
    let done = match done {
        Ok(done) => done,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            println!("tool absent: go");
            return UNRESOLVED;
        }
        Err(error) => {
            println!("tool broken: go didn't start: {error}");
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
    let version = first
        .strip_prefix("go version go")
        .and_then(|rest| rest.split_whitespace().next());
    let Some(version) = version else {
        println!("tool broken: go printed {first}");
        return UNRESOLVED;
    };
    let precision = pinned.split('.').count();
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
    fn a_toolchain_name_gives_its_version_where_it_has_one() {
        assert_eq!(version_of("go1.26.0"), Some("1.26.0"));
        assert_eq!(version_of("go1.21"), Some("1.21"));
        assert_eq!(version_of("default"), None);
        assert_eq!(version_of("local"), None);
        assert_eq!(version_of("go1.21rc1"), None);
    }
}
