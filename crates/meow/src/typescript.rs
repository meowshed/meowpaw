// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-typescript`: which packages a work tree holds, the package manager
//! each declares, the `[stages]` table the configuration each committed binds,
//! and the settings behind those stages that are missing or have no effect
//! (SPC-1320).
//!
//! `status`, `bind` and `check` read the files git tracks and run git alone,
//! so none of them starts Node, a package manager or a tool it names
//! (SPC-1190, REQ-0133).

use crate::detect::{self, Marker};
use crate::pack::{self, Binding, Candidate, Environment, State};
use crate::profile::{self, Profile};
use crate::tree::{self, Tree, commands, file_name, program};
use serde_json::Value;
use std::collections::BTreeSet;

const UNRESOLVED: u8 = 3;
const FOUND: u8 = 1;
const USAGE: &str = "usage: meow-typescript status | bind [<directory>] | check [<directory>]";
const NOT_DETECTED: &str = "not a TypeScript and JavaScript repository";

/// The lockfile each package manager writes, and the manager it names.
const LOCKFILES: [(&str, &str); 5] = [
    ("package-lock.json", "npm"),
    ("pnpm-lock.yaml", "pnpm"),
    ("yarn.lock", "yarn"),
    ("bun.lock", "bun"),
    ("bun.lockb", "bun"),
];
const ORCHESTRATORS: [(&str, &str); 2] = [("turbo.json", "turbo"), ("nx.json", "nx")];
const MISE_CONFIGURATION: [&str; 2] = ["mise.toml", ".mise.toml"];
const TASKFILES: [&str; 2] = ["Taskfile.yml", "Taskfile.yaml"];
/// The tools whose bare name a stage must not run, by the manager's rule.
const WATCHED: [&str; 7] = [
    "prettier", "eslint", "oxlint", "biome", "tsc", "vitest", "jest",
];
const OXLINT_FILES: [&str; 4] = [
    ".oxlintrc.json",
    ".oxlintrc.jsonc",
    "oxlint.config.ts",
    "oxlint.config.mts",
];

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 3] = [
    crate::help::Entry {
        name: "status",
        determines: "which packages this repository holds, the package manager each declares and the tools each configured",
        by_hand: "list the tracked package.json files and the lockfile, config and pin files beside each",
        lines: "meow-typescript profile: unknown unresolved: scope: marker: package pinned: configured:",
        json: "",
    },
    crate::help::Entry {
        name: "bind",
        determines: "the `[stages]` lines that bind each stage to a tool the package configured, run through its package manager",
        by_hand: "read the package manager's lockfile, then match each configuration file with the tool that reads it",
        lines: "meow-typescript profile: unknown unresolved: # [stages] format lint check test build",
        json: "",
    },
    crate::help::Entry {
        name: "check",
        determines: "whether the stages run their tools through the package manager and set what the tools need",
        by_hand: "read each stage's command against the lockfiles, the ESLint, oxlint and tsconfig settings",
        lines: "meow-typescript profile: unknown unresolved: format lint check test build eslint oxlint tsc <path> no",
        json: "",
    },
];

pub fn main(args: &[String]) -> u8 {
    if let Some(code) = crate::help::answer("meow-typescript", &HELP, args) {
        return code;
    }
    match args
        .iter()
        .map(String::as_str)
        .collect::<Vec<_>>()
        .as_slice()
    {
        ["status"] => status(),
        ["bind"] => bind(None),
        ["bind", directory] => bind(Some(directory)),
        ["check"] => check(None),
        ["check", directory] => check(Some(directory)),
        _ => {
            eprintln!("{USAGE}");
            2
        }
    }
}

/// Each tracked `package.json` outside `node_modules` marks its directory
/// (REQ-2338, REQ-3048). It reads paths alone, so no tool starts.
pub(crate) fn markers(tracked: &BTreeSet<String>) -> Vec<Marker> {
    detect::by_name(tracked, &["package.json"])
        .into_iter()
        .filter(|marker| !marker.file.contains("node_modules/"))
        .collect()
}

/// The package manager a package runs its tools through, and the file that
/// declares it.
struct Manager {
    name: &'static str,
    declared_by: String,
    /// The `name@version` the `packageManager` field pins, where it does.
    pinned: Option<(String, String)>,
}

impl Manager {
    fn environment(&self) -> Environment {
        Environment {
            name: self.name.to_string(),
            declared_by: self.declared_by.clone(),
            prefix: prefix(self.name).to_string(),
        }
    }
}

/// The words that run an installed tool through a manager (RES-0362).
fn prefix(manager: &str) -> &'static str {
    match manager {
        "npm" => "npm exec --",
        "pnpm" => "pnpm exec",
        "yarn" => "yarn run",
        _ => "bun x",
    }
}

fn manager_name(name: &str) -> Option<&'static str> {
    ["npm", "pnpm", "yarn", "bun"]
        .into_iter()
        .find(|known| *known == name)
}

fn json(tree: &Tree, path: &str) -> Result<Value, String> {
    let text = tree
        .text(path)
        .ok_or_else(|| format!("{path} can't be read"))?;
    serde_json::from_str(&text).map_err(|error| format!("{path} doesn't parse as JSON: {error}"))
}

/// The lockfiles of the nearest directory, from `directory` upwards, that
/// holds any.
fn lockfiles(tree: &Tree, directory: &str) -> Vec<String> {
    for here in tree::ancestors(directory) {
        let found: Vec<String> = LOCKFILES
            .iter()
            .filter_map(|(name, _)| tree.here(&here, name))
            .collect();
        if !found.is_empty() {
            return found;
        }
    }
    Vec::new()
}

fn locks(file: &str) -> &'static str {
    LOCKFILES
        .iter()
        .find(|(name, _)| *name == file_name(file))
        .map_or("", |(_, manager)| manager)
}

/// The manager the package in `directory` declares, from what the repository
/// commits and never from what is installed (REQ-2426, SPC-1320).
fn manager(tree: &Tree, directory: &str) -> Result<Manager, String> {
    let mut field: Option<(String, String)> = None;
    for here in tree::ancestors(directory) {
        let Some(path) = tree.here(&here, "package.json") else {
            continue;
        };
        let own = json(tree, &path);
        if here == directory {
            own.as_ref().map_err(Clone::clone)?;
        }
        if let Some(text) = own.ok().and_then(|v| {
            v.get("packageManager")
                .and_then(Value::as_str)
                .map(str::to_string)
        }) {
            field = Some((path, text));
            break;
        }
    }
    let locked = lockfiles(tree, directory);
    match field {
        Some((path, text)) => {
            let (name, version) = text.split_once('@').unwrap_or((&text, ""));
            let Some(known) = manager_name(name) else {
                return Err(format!(
                    "packageManager names {name}, which this pack doesn't know"
                ));
            };
            if let Some(other) = locked
                .iter()
                .find(|file| locks(file) != known)
                .filter(|_| !locked.iter().any(|file| locks(file) == known))
            {
                return Err(format!(
                    "{path} declares {known}, and {other} locks {}",
                    locks(other)
                ));
            }
            Ok(Manager {
                name: known,
                declared_by: path,
                pinned: Some((
                    known.to_string(),
                    version.split('+').next().unwrap_or("").to_string(),
                )),
            })
        }
        None => match locked.as_slice() {
            [] => {
                Err("no package manager declared: commit a lockfile or set packageManager".into())
            }
            [one] => Ok(Manager {
                name: locks_name(one),
                declared_by: one.clone(),
                pinned: None,
            }),
            several => Err(format!(
                "{} both lock this package; declare packageManager",
                join_and(several)
            )),
        },
    }
}

fn locks_name(file: &str) -> &'static str {
    manager_name(locks(file)).unwrap_or("npm")
}

fn join_and(items: &[String]) -> String {
    match items.split_last() {
        Some((last, [])) => last.clone(),
        Some((last, rest)) => format!("{} and {last}", rest.join(", ")),
        None => String::new(),
    }
}

/// The directory a command acts on, or why it can't: the argument, or the
/// root, and a `package.json` must be tracked in it.
fn target(tree: &Tree, argument: Option<&str>) -> Result<String, String> {
    let all = markers(&tree.tracked);
    if all.is_empty() {
        return Err(NOT_DETECTED.to_string());
    }
    let directory = argument.map_or_else(|| ".".to_string(), tree::directory_argument);
    if all.iter().any(|marker| marker.directory == directory) {
        return Ok(directory);
    }
    let elsewhere: Vec<&str> = all.iter().map(|m| m.directory.as_str()).collect();
    Err(format!(
        "{directory} holds no package.json; one is in {}",
        elsewhere.join(", ")
    ))
}

fn status() -> u8 {
    println!("meow-typescript status");
    let tree = Tree::read();
    let found = markers(&tree.tracked);
    if found.is_empty() {
        println!("unresolved: {NOT_DETECTED}");
        return UNRESOLVED;
    }
    for line in profile::report(&profile::read(&tree.root)) {
        println!("{line}");
    }
    let mut broken = false;
    for (directory, files) in detect::by_directory(&found) {
        println!("{}", detect::scope(&tree.parts, &directory));
        for file in &files {
            println!("marker: {file}");
        }
        let package = tree.here(&directory, "package.json");
        if let Some(Err(reason)) = package.as_ref().map(|path| json(&tree, path)) {
            println!("unresolved: {reason}");
            broken = true;
            continue;
        }
        match manager(&tree, &directory) {
            Ok(found) => {
                println!(
                    "package manager: {}, declared by {}",
                    found.name, found.declared_by
                );
                if let Some((name, version)) = &found.pinned {
                    println!("pinned: {name} {version} in {}", found.declared_by);
                }
            }
            Err(reason) => println!("package manager: unresolved, {reason}"),
        }
        for pin in [".nvmrc", ".node-version"] {
            if let Some(path) = tree.here(&directory, pin) {
                let version = tree.text(&path).unwrap_or_default();
                println!("pinned: node {} in {path}", version.trim());
            }
        }
        for (file, tool) in configured(&tree, &directory) {
            println!("configured: {file}: {tool}");
        }
    }
    if broken { UNRESOLVED } else { 0 }
}

/// Each configuration the package's directory or one above it holds, with the
/// tool that reads it.
fn configured(tree: &Tree, directory: &str) -> Vec<(String, String)> {
    let mut found = Vec::new();
    let mut add = |files: Vec<String>, tool: &str| {
        found.extend(files.into_iter().map(|file| (file, tool.to_string())));
    };
    add(files_prettier(tree, directory), "Prettier");
    add(files_biome(tree, directory), "Biome");
    add(files_oxlint(tree, directory), "oxlint");
    add(files_eslint(tree, directory), "ESLint");
    add(
        files_eslintrc(tree, directory),
        "ESLint 9, which ESLint 10 no longer reads",
    );
    add(
        tree.here(directory, "tsconfig.json").into_iter().collect(),
        "the TypeScript compiler",
    );
    add(files_vitest(tree, directory), "Vitest");
    add(files_jest(tree, directory), "Jest");
    for (file, tool) in ORCHESTRATORS {
        add(tree.here(".", file).into_iter().collect(), tool);
    }
    found
}

fn files_prettier(tree: &Tree, directory: &str) -> Vec<String> {
    tree.find(directory, |n| {
        n.starts_with(".prettierrc") || n.starts_with("prettier.config.")
    })
}

fn files_biome(tree: &Tree, directory: &str) -> Vec<String> {
    tree.find(directory, |n| matches!(n, "biome.json" | "biome.jsonc"))
}

fn files_oxlint(tree: &Tree, directory: &str) -> Vec<String> {
    tree.find(directory, |n| OXLINT_FILES.contains(&n))
}

fn files_eslint(tree: &Tree, directory: &str) -> Vec<String> {
    tree.find(directory, |n| {
        n.strip_prefix("eslint.config.")
            .is_some_and(|ext| matches!(ext, "js" | "mjs" | "cjs" | "ts" | "mts" | "cts"))
    })
}

fn files_eslintrc(tree: &Tree, directory: &str) -> Vec<String> {
    tree.find(directory, |n| n.starts_with(".eslintrc"))
}

fn files_vitest(tree: &Tree, directory: &str) -> Vec<String> {
    tree.find(directory, |n| n.starts_with("vitest.config."))
}

fn files_jest(tree: &Tree, directory: &str) -> Vec<String> {
    tree.find(directory, |n| n.starts_with("jest.config."))
}

/// A key of the package's `dependencies` or `devDependencies`.
fn depends_on(package: &Value, name: &str) -> bool {
    ["dependencies", "devDependencies"]
        .iter()
        .any(|table| package.get(table).is_some_and(|t| t.get(name).is_some()))
}

fn script<'a>(package: &'a Value, name: &str) -> Option<&'a str> {
    package.get("scripts")?.get(name)?.as_str()
}

/// What `bind` prints for the package in `argument`'s directory.
fn bind(argument: Option<&str>) -> u8 {
    let tree = Tree::read();
    let directory = match target(&tree, argument) {
        Ok(directory) => directory,
        Err(reason) => {
            println!("meow-typescript bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let package = match tree
        .here(&directory, "package.json")
        .map(|path| json(&tree, &path))
    {
        Some(Ok(package)) => package,
        Some(Err(reason)) => {
            println!("meow-typescript bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
        None => Value::Null,
    };
    // What `bind` prints is pasted into the profile, so the state goes to
    // standard error.
    let read = tree.profile(&directory);
    for line in profile::report(&read) {
        eprintln!("{line}");
    }
    let table = match read {
        Profile::Unparseable(message) => {
            println!("meow-typescript bind");
            println!("unresolved: the profile doesn't parse: {message}");
            return UNRESOLVED;
        }
        Profile::Absent => toml::Table::new(),
        Profile::Parsed(table, _) => table,
    };
    let declared: BTreeSet<&str> = tree::declared(&table).iter().map(|(s, _)| *s).collect();
    let manager = manager(&tree, &directory);
    let bindings = match &manager {
        Ok(found) => bindings(&tree, &directory, &package, found),
        Err(reason) => pack::waiting(reason),
    };
    println!(
        "# meow-typescript bind {directory}: paste what follows into {}",
        tree.profile_path(&directory)
    );
    println!("[stages]");
    if let Ok(found) = &manager
        && matches!(found.name, "npm" | "bun")
    {
        println!(
            "# {} fetches a tool the project never installed, so a tool missing from its dependencies runs a version nobody pinned",
            found.name
        );
    }
    for binding in &bindings {
        if !declared.contains(binding.stage.as_str()) {
            binding.lines().iter().for_each(|line| println!("{line}"));
        }
    }
    for (file, tool) in ORCHESTRATORS {
        if let Some(path) = tree.here(".", file) {
            println!(
                "# build: {path} configures {tool}, which runs a task across the workspace's packages; this pack binds none"
            );
        }
    }
    for (files, runner, unit) in [
        (&MISE_CONFIGURATION[..], "mise", "meow-mise"),
        (&TASKFILES[..], "Task", "meow-gotask"),
    ] {
        for file in files {
            if let Some(path) = tree.here(".", file) {
                println!(
                    "# {path} configures {runner}; to bind a stage to its tasks, run {unit} bind, since this pack doesn't read them"
                );
            }
        }
    }
    0
}

/// The five stages bound from what the package configured, each tool run
/// through its manager.
fn bindings(tree: &Tree, directory: &str, package: &Value, manager: &Manager) -> Vec<Binding> {
    let environment = manager.environment();
    let owned = |files: Vec<String>| files;
    let mut prettier = owned(files_prettier(tree, directory));
    if package.get("prettier").is_some() || depends_on(package, "prettier") {
        prettier.push("package.json".to_string());
    }
    let biome = files_biome(tree, directory);
    let oxlint = files_oxlint(tree, directory);
    let eslint = files_eslint(tree, directory);
    let eslintrc = files_eslintrc(tree, directory);

    let mut format = pack::choose(
        "format",
        &[Candidate::new("prettier", "prettier --check .", prettier)],
        "a .prettierrc*, a prettier.config.* or a prettier key or dependency in package.json",
    );
    if matches!(format.state, State::Unbound(_))
        && let Some(file) = biome.first()
    {
        format = Binding::unbound(
            "format",
            &format!("{file} configures Biome, whose biome ci in lint checks the formatting"),
        );
    }

    let both = !oxlint.is_empty() && !eslint.is_empty();
    let together: Vec<String> = oxlint.iter().chain(eslint.iter()).cloned().collect();
    let alone = |files: &Vec<String>| if both { Vec::new() } else { files.clone() };
    let mut lint = pack::choose(
        "lint",
        &[
            Candidate::new("biome", "biome ci --error-on-warnings .", biome.clone()),
            Candidate::new(
                "oxlint and eslint",
                "oxlint --deny-warnings && eslint --max-warnings 0 .",
                if both { together } else { Vec::new() },
            ),
            Candidate::new("oxlint", "oxlint --deny-warnings", alone(&oxlint)),
            Candidate::new("eslint", "eslint --max-warnings 0 .", alone(&eslint)),
        ],
        "biome.json, an oxlint configuration and an eslint.config.* file",
    );
    if let Some(rc) = eslintrc.first() {
        lint = lint.note(&format!(
            "{rc} configures ESLint 9 alone; ESLint 10 doesn't read it, so it binds nothing"
        ));
    }

    let check = pack::choose(
        "check",
        &[Candidate::new(
            "tsc",
            "tsc --noEmit",
            tree.here(directory, "tsconfig.json").into_iter().collect(),
        )],
        "a tsconfig.json beside package.json",
    );

    let mut vitest = files_vitest(tree, directory);
    if depends_on(package, "vitest") {
        vitest.push("package.json".to_string());
    }
    let mut jest = files_jest(tree, directory);
    if package.get("jest").is_some() || depends_on(package, "jest") {
        jest.push("package.json".to_string());
    }
    let node = script(package, "test")
        .filter(|text| text.contains("node --test"))
        .map(|_| vec!["package.json".to_string()])
        .unwrap_or_default();
    let mut test = pack::choose(
        "test",
        &[
            Candidate::new("vitest", "vitest run", vitest),
            Candidate::new("jest", "jest", jest),
            Candidate::new("node", "node --test", node),
        ],
        "a vitest.config.* file or dependency, a jest.config.* file, key or dependency, and a test script that runs node --test",
    );

    format = format.through(&environment);
    lint = lint.through(&environment);
    let check = check.through(&environment);
    if !matches!(&test.state, State::Bound { tool, .. } if tool == "node") {
        test = test.through(&environment);
    }
    let build = match script(package, "build") {
        Some(_) => Binding::bound(
            "build",
            manager.name,
            &format!("{} run build", manager.name),
        ),
        None => Binding::unbound("build", "looked for a build script in package.json"),
    };
    vec![format, lint, check, test, build]
}

/// A tool a stage's command runs.
struct Run {
    /// The tool, where the command names one.
    tool: Option<String>,
    /// The manager the command goes through, where it names one: `npm` for
    /// both `npm` and `npx`.
    runner: Option<&'static str>,
    /// The tool is run by its bare name, outside any manager.
    bare: bool,
    words: Vec<String>,
}

/// Each simple command of `command`, as the tool it runs and the manager it
/// goes through. A word after a manager's `exec`, `run` or `x`, or after
/// `npx` or `bunx`, runs that tool through the manager (SPC-1320).
fn runs(command: &str) -> Vec<Run> {
    commands(command)
        .into_iter()
        .map(|words| {
            let first = program(words[0]);
            let owned: Vec<String> = words.iter().map(|w| w.to_string()).collect();
            let after = |from: &[&str]| {
                from.iter()
                    .find(|w| **w != "--" && !w.starts_with('-'))
                    .map(|w| program(w).to_string())
            };
            match first {
                "npm" | "pnpm" | "yarn" | "bun" => {
                    let verb = match first {
                        "npm" | "pnpm" => "exec",
                        "yarn" => "run",
                        _ => "x",
                    };
                    let tool = (words.get(1) == Some(&verb))
                        .then(|| after(&words[2..]))
                        .flatten();
                    Run {
                        tool,
                        runner: manager_name(first),
                        bare: false,
                        words: owned,
                    }
                }
                "npx" | "bunx" => Run {
                    tool: after(&words[1..]),
                    runner: manager_name(if first == "npx" { "npm" } else { "bun" }),
                    bare: false,
                    words: owned,
                },
                _ => Run {
                    tool: Some(first.to_string()),
                    runner: None,
                    bare: !words[0].contains('/'),
                    words: owned,
                },
            }
        })
        .collect()
}

fn names(run: &Run, tool: &str) -> bool {
    run.tool.as_deref() == Some(tool)
}

fn has_flag(run: &Run, flag: &str) -> bool {
    run.words
        .iter()
        .any(|w| w == flag || w.starts_with(&format!("{flag}=")))
}

/// Whether the package's `tsconfig.json` sets `noEmit`.
fn tsconfig_sets_no_emit(tree: &Tree, directory: &str) -> bool {
    tree.here(directory, "tsconfig.json")
        .and_then(|path| tree.text(&path))
        .and_then(|text| serde_json::from_str::<Value>(&tree::plain_json(&text)).ok())
        .is_some_and(|v| v["compilerOptions"]["noEmit"] == Value::Bool(true))
}

/// What `check` reports for the package in `argument`'s directory.
fn check(argument: Option<&str>) -> u8 {
    println!("meow-typescript check");
    let tree = Tree::read();
    let directory = match target(&tree, argument) {
        Ok(directory) => directory,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    if let Some(Err(reason)) = tree
        .here(&directory, "package.json")
        .map(|path| json(&tree, &path))
    {
        println!("unresolved: {reason}");
        return UNRESOLVED;
    }
    let read = tree.profile(&directory);
    for line in profile::report(&read) {
        println!("{line}");
    }
    let table = match read {
        Profile::Absent => {
            println!(
                "unresolved: no profile at {}",
                tree.profile_path(&directory)
            );
            return UNRESOLVED;
        }
        Profile::Unparseable(message) => {
            println!("unresolved: the profile doesn't parse: {message}");
            return UNRESOLVED;
        }
        Profile::Parsed(table, _) => table,
    };
    let (found, unresolved) = findings(&tree, &directory, &table);
    if found.is_empty() && unresolved.is_empty() {
        let clean = pack::Clean {
            said: "no findings".into(),
            groups: [
                "the package manager",
                "the linter's settings",
                "the compiler's output",
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
        return 0;
    }
    found.iter().for_each(|line| println!("{line}"));
    unresolved
        .iter()
        .for_each(|reason| println!("unresolved: {reason}"));
    if found.is_empty() { UNRESOLVED } else { FOUND }
}

/// The findings in the settings behind the stages (REQ-2426, REQ-2434,
/// REQ-2442), and the reasons the package manager is unresolved.
fn findings(tree: &Tree, directory: &str, table: &toml::Table) -> (Vec<String>, Vec<String>) {
    let mut found: Vec<String> = Vec::new();
    let mut unresolved = Vec::new();
    let mut push = |line: String| {
        if !found.contains(&line) {
            found.push(line);
        }
    };
    let locked = lockfiles(tree, directory);
    if locked.len() > 1 {
        push(format!("{} both lock this package", join_and(&locked)));
    }
    let manager = match manager(tree, directory) {
        Ok(manager) => Some(manager),
        Err(reason) => {
            if locked.len() < 2 {
                unresolved.push(reason);
            }
            None
        }
    };
    let stages = tree::declared(table);
    let ran: Vec<(&str, Vec<Run>)> = stages
        .iter()
        .map(|(stage, command)| (*stage, runs(command)))
        .collect();
    for (stage, runs) in &ran {
        for run in runs {
            if let Some(manager) = &manager {
                if run.bare
                    && let Some(tool) = run.tool.as_deref().filter(|t| WATCHED.contains(t))
                {
                    push(format!(
                        "{stage} runs {tool} outside {}: write {} {tool}",
                        manager.name,
                        prefix(manager.name)
                    ));
                }
                if let Some(runner) = run.runner.filter(|r| *r != manager.name) {
                    push(format!(
                        "{stage} runs {runner}, and {} declares {}",
                        manager.declared_by, manager.name
                    ));
                }
            }
            if names(run, "tsgo") {
                push(format!(
                    "{stage} runs tsgo, the TypeScript 7 preview; the compiler is tsc"
                ));
            }
            if names(run, "oxlint")
                && !has_flag(run, "--deny-warnings")
                && !has_flag(run, "--max-warnings")
            {
                push("oxlint exits 0 on warnings: pass --deny-warnings".into());
            }
            if names(run, "eslint") && !has_flag(run, "--max-warnings") {
                push("eslint exits 0 on warnings: pass --max-warnings 0".into());
            }
            if names(run, "tsc")
                && matches!(*stage, "format" | "lint" | "check" | "test")
                && !has_flag(run, "--noEmit")
                && !tsconfig_sets_no_emit(tree, directory)
            {
                push("tsc writes JavaScript into the tree: pass --noEmit".into());
            }
        }
    }
    if ran
        .iter()
        .any(|(_, runs)| runs.iter().any(|r| names(r, "eslint")))
    {
        let rc = files_eslintrc(tree, directory);
        let flat = files_eslint(tree, directory);
        for file in &rc {
            match flat.first() {
                None => push(format!(
                    "eslint reads no configuration: ESLint 10 ignores {file}"
                )),
                Some(config) => push(format!(
                    "eslint ignores {file}: ESLint 10 reads {} alone",
                    file_name(config)
                )),
            }
        }
    }
    (found, unresolved)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_marker_inside_node_modules_is_not_a_package() {
        let tracked: BTreeSet<String> = [
            "package.json",
            "node_modules/x/package.json",
            "web/package.json",
        ]
        .iter()
        .map(|p| p.to_string())
        .collect();
        let dirs: Vec<String> = markers(&tracked).into_iter().map(|m| m.directory).collect();
        assert_eq!(dirs, [".", "web"]);
    }

    #[test]
    fn a_word_after_a_managers_verb_is_the_tool_it_runs() {
        let tools = |command: &str| -> Vec<(Option<String>, Option<&'static str>, bool)> {
            runs(command)
                .into_iter()
                .map(|r| (r.tool, r.runner, r.bare))
                .collect()
        };
        assert_eq!(
            tools("npm exec -- eslint ."),
            [(Some("eslint".into()), Some("npm"), false)]
        );
        assert_eq!(
            tools("npx vitest@5 run && eslint ."),
            [
                (Some("vitest".into()), Some("npm"), false),
                (Some("eslint".into()), None, true)
            ]
        );
        // A script and a binary read alike after `yarn run`, and a script
        // name is no watched tool.
        assert_eq!(
            tools("yarn run build"),
            [(Some("build".into()), Some("yarn"), false)]
        );
        assert_eq!(tools("npm run build"), [(None, Some("npm"), false)]);
        assert_eq!(
            tools("./node_modules/.bin/eslint ."),
            [(Some("eslint".into()), None, false)]
        );
    }
}
