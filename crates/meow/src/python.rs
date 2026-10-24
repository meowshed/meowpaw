// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-python`: which projects a work tree holds, the environment tool each
//! declares, the `[stages]` table the configuration each committed binds, and
//! the settings behind those stages that are missing, have no effect or let a
//! tool write into the working tree (SPC-1330).
//!
//! `status`, `bind` and `check` read the files git tracks and run git alone,
//! so none of them starts Python, an environment tool or a tool it names
//! (SPC-1190, REQ-0133).

use crate::detect::{self, Marker};
use crate::pack::{self, Binding, Candidate, Environment, State};
use crate::profile::{self, Profile};
use crate::tree::{self, Tree, commands, file_name, program};
use std::collections::BTreeSet;

const UNRESOLVED: u8 = 3;
const FOUND: u8 = 1;
const USAGE: &str = "usage: meow-python status | bind [<directory>] | check [<directory>]";
const NOT_DETECTED: &str = "not a Python repository";

/// Each environment tool, the lockfile it writes and the table it owns in
/// `pyproject.toml` (RES-0363).
const ENVIRONMENTS: [(&str, &str, &str); 3] = [
    ("uv", "uv.lock", "uv"),
    ("poetry", "poetry.lock", "poetry"),
    ("pdm", "pdm.lock", "pdm"),
];
const OLDER_LAYOUT: [&str; 3] = ["setup.py", "setup.cfg", "requirements.txt"];
const MISE_CONFIGURATION: [&str; 2] = ["mise.toml", ".mise.toml"];
const TASKFILES: [&str; 2] = ["Taskfile.yml", "Taskfile.yaml"];
/// The tools whose bare name a stage must not run, by the environment's rule.
const WATCHED: [&str; 6] = ["ruff", "mypy", "pyright", "pyrefly", "ty", "pytest"];
/// Where Ruff's cache goes: outside the tree (REQ-2442).
const RUFF_CACHE: &str = "--cache-dir \"${TMPDIR:-/tmp}/ruff-cache\"";

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 3] = [
    crate::help::Entry {
        name: "status",
        determines: "which projects this repository holds, the environment tool each declares and the tools each configured",
        by_hand: "list the tracked pyproject.toml files and the lockfile, config and pin files beside each",
        lines: "meow-python profile: unknown unresolved: scope: marker: older environment: pinned: configured:",
        json: "",
    },
    crate::help::Entry {
        name: "bind",
        determines: "the `[stages]` lines that bind each stage to a tool the project configured, run through its environment tool",
        by_hand: "read the environment tool's lockfile, then match each configuration file with the tool that reads it",
        lines: "meow-python profile: unknown unresolved: # [stages] format lint check test build",
        json: "",
    },
    crate::help::Entry {
        name: "check",
        determines: "whether the stages run their tools through the environment, apply no fix and keep each tool's cache out of the tree",
        by_hand: "read each stage's command against the lockfiles, the tools' flags and the files each tool reads",
        lines: "meow-python profile: unknown unresolved: format lint check test build ruff mypy pytest <path> no",
        json: "",
    },
];

pub fn main(args: &[String]) -> u8 {
    if let Some(code) = crate::help::answer("meow-python", &HELP, args) {
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

/// Each tracked `pyproject.toml` marks its directory (REQ-2336, REQ-3048). A
/// `setup.py` or a `requirements.txt` alone marks nothing, because it
/// predates the convention (RES-0103). It reads paths alone, so no tool
/// starts.
pub(crate) fn markers(tracked: &BTreeSet<String>) -> Vec<Marker> {
    detect::by_name(tracked, &["pyproject.toml"])
        .into_iter()
        .filter(|marker| !marker.file.contains(".venv/"))
        .collect()
}

/// The directory a command acts on, or why it can't.
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
        "{directory} holds no pyproject.toml; one is in {}",
        elsewhere.join(", ")
    ))
}

/// The project's `pyproject.toml`.
fn pyproject(tree: &Tree, directory: &str) -> Result<toml::Table, String> {
    let Some(path) = tree.here(directory, "pyproject.toml") else {
        return Ok(toml::Table::new());
    };
    let text = tree
        .text(&path)
        .ok_or_else(|| format!("{path} can't be read"))?;
    text.parse::<toml::Table>().map_err(|error| {
        format!(
            "{path} doesn't parse as TOML: {}",
            error.message().replace('\n', " ")
        )
    })
}

/// Whether the table holds `tool.<name>`, or `tool.<name>.<inner>`.
fn has_tool(table: &toml::Table, path: &[&str]) -> bool {
    let mut here = table.get("tool");
    for key in path {
        here = here.and_then(|v| v.get(key));
    }
    here.is_some()
}

/// Each environment tool the project declares, with the file that declares
/// it, in the order of those files.
fn environments(tree: &Tree, directory: &str, table: &toml::Table) -> Vec<(&'static str, String)> {
    let mut found: Vec<(&'static str, String)> = ENVIRONMENTS
        .iter()
        .filter_map(|(name, lock, key)| {
            tree.here(directory, lock)
                .or_else(|| {
                    has_tool(table, &[key])
                        .then(|| tree.here(directory, "pyproject.toml"))
                        .flatten()
                })
                .map(|file| (*name, file))
        })
        .collect();
    found.sort_by(|a, b| a.1.cmp(&b.1));
    found
}

/// The environment the project declares, none, or why it is unresolved
/// (REQ-2426).
fn environment(
    tree: &Tree,
    directory: &str,
    table: &toml::Table,
) -> Result<Option<(&'static str, String)>, String> {
    let found = environments(tree, directory, table);
    match found.as_slice() {
        [] => Ok(None),
        [one] => Ok(Some(one.clone())),
        several => Err(format!(
            "{} both declare an environment",
            several
                .iter()
                .map(|(_, file)| file.as_str())
                .collect::<Vec<_>>()
                .join(" and ")
        )),
    }
}

/// The words that run an installed tool through an environment tool.
fn prefix(name: &str) -> String {
    format!("{name} run")
}

/// The files that configure each tool the pack binds, in the order the tool
/// reads them, so the first is the one that applies.
#[derive(Default)]
struct Configs {
    ruff: Vec<String>,
    mypy: Vec<String>,
    pyright: Vec<String>,
    pyrefly: Vec<String>,
    ty: Vec<String>,
    pytest: Vec<String>,
}

fn configs(tree: &Tree, directory: &str, table: &toml::Table) -> Configs {
    let project = tree.here(directory, "pyproject.toml");
    let mut found = Configs::default();
    // Each list takes its files in the order the tool reads them.
    let order = |list: &mut Vec<String>, names: &[&str], keys: &[&[&str]], after: &[&str]| {
        let mut files: Vec<String> = Vec::new();
        for name in names {
            files.extend(tree.here(directory, name));
        }
        if keys.iter().any(|key| has_tool(table, key)) {
            files.extend(project.clone());
        }
        for name in after {
            files.extend(tree.here(directory, name));
        }
        *list = files;
    };
    order(
        &mut found.ruff,
        &[".ruff.toml", "ruff.toml"],
        &[&["ruff"]],
        &[],
    );
    let setup = |name: &str, section: &str| {
        tree.here(directory, name)
            .filter(|path| tree.text(path).is_some_and(|text| text.contains(section)))
    };
    order(
        &mut found.mypy,
        &["mypy.ini", ".mypy.ini"],
        &[&["mypy"]],
        &[],
    );
    found.mypy.extend(setup("setup.cfg", "[mypy]"));
    order(
        &mut found.pyright,
        &["pyrightconfig.json"],
        &[&["pyright"]],
        &[],
    );
    order(&mut found.pyrefly, &["pyrefly.toml"], &[&["pyrefly"]], &[]);
    order(&mut found.ty, &["ty.toml"], &[&["ty"]], &[]);
    order(
        &mut found.pytest,
        &["pytest.toml", ".pytest.toml", "pytest.ini", ".pytest.ini"],
        &[&["pytest"], &["pytest", "ini_options"]],
        &[],
    );
    found.pytest.extend(setup("tox.ini", "[pytest]"));
    found.pytest.extend(setup("setup.cfg", "[tool:pytest]"));
    found
}

/// The text of `addopts` in the pytest configuration that applies.
fn addopts(tree: &Tree, table: &toml::Table, applied: Option<&String>) -> String {
    let Some(file) = applied else {
        return String::new();
    };
    if file_name(file) == "pyproject.toml" {
        let tool = table.get("tool").and_then(|t| t.get("pytest"));
        return [
            tool.and_then(|t| t.get("addopts")),
            tool.and_then(|t| t.get("ini_options"))
                .and_then(|t| t.get("addopts")),
        ]
        .into_iter()
        .flatten()
        .map(|v| v.to_string())
        .collect::<Vec<_>>()
        .join(" ");
    }
    tree.text(file).unwrap_or_default()
}

fn status() -> u8 {
    println!("meow-python status");
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
        for name in OLDER_LAYOUT {
            if let Some(path) = tree.here(&directory, name) {
                println!("older layout: {path}");
            }
        }
        let table = match pyproject(&tree, &directory) {
            Ok(table) => table,
            Err(reason) => {
                println!("unresolved: {reason}");
                broken = true;
                continue;
            }
        };
        match environment(&tree, &directory, &table) {
            Ok(Some((name, file))) => println!("environment: {name}, declared by {file}"),
            Ok(None) => println!("environment: none declared"),
            Err(reason) => println!("environment: unresolved, {reason}"),
        }
        if let Some(path) = tree.here(&directory, ".python-version") {
            let version = tree.text(&path).unwrap_or_default();
            println!("pinned: python {} in {path}", version.trim());
        }
        let found = configs(&tree, &directory, &table);
        for (files, tool) in [
            (&found.ruff, "Ruff"),
            (&found.mypy, "mypy"),
            (&found.pyright, "pyright"),
            (&found.pyrefly, "pyrefly"),
            (&found.ty, "ty"),
            (&found.pytest, "pytest"),
        ] {
            for file in files {
                println!("configured: {file}: {tool}");
            }
        }
        for (name, tool) in [("noxfile.py", "nox"), ("tox.ini", "tox")] {
            if let Some(path) = tree.here(&directory, name) {
                println!("configured: {path}: {tool}");
            }
        }
    }
    if broken { UNRESOLVED } else { 0 }
}

/// What `bind` prints for the project in `argument`'s directory.
fn bind(argument: Option<&str>) -> u8 {
    let tree = Tree::read();
    let directory = match target(&tree, argument) {
        Ok(directory) => directory,
        Err(reason) => {
            println!("meow-python bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let project = match pyproject(&tree, &directory) {
        Ok(table) => table,
        Err(reason) => {
            println!("meow-python bind");
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    // What `bind` prints is pasted into the profile, so the state goes to
    // standard error.
    let read = tree.profile(&directory);
    for line in profile::report(&read) {
        eprintln!("{line}");
    }
    let table = match read {
        Profile::Unparseable(message) => {
            println!("meow-python bind");
            println!("unresolved: the profile doesn't parse: {message}");
            return UNRESOLVED;
        }
        Profile::Absent => toml::Table::new(),
        Profile::Parsed(table, _) => table,
    };
    let declared: BTreeSet<&str> = tree::declared(&table).iter().map(|(s, _)| *s).collect();
    let bindings = match environment(&tree, &directory, &project) {
        Ok(env) => bindings(&tree, &directory, &project, env.as_ref()),
        Err(reason) => pack::waiting(&reason),
    };
    println!(
        "# meow-python bind {directory}: paste what follows into {}",
        tree.profile_path(&directory)
    );
    println!("[stages]");
    let uses_uv = matches!(
        environment(&tree, &directory, &project),
        Ok(Some(("uv", _)))
    );
    if uses_uv && bindings.iter().any(|b| b.command().is_some()) {
        println!(
            "# uv run brings the project environment up to date before it runs, so a stage may write into .venv, which a repository ignores"
        );
    }
    for binding in &bindings {
        if !declared.contains(binding.stage.as_str()) {
            binding.lines().iter().for_each(|line| println!("{line}"));
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

/// The five stages bound from what the project configured, each tool run
/// through its environment tool.
fn bindings(
    tree: &Tree,
    directory: &str,
    table: &toml::Table,
    env: Option<&(&'static str, String)>,
) -> Vec<Binding> {
    let found = configs(tree, directory, table);
    let first = |files: &Vec<String>| files.first().cloned().into_iter().collect::<Vec<_>>();
    let format = pack::choose(
        "format",
        &[Candidate::new(
            "ruff",
            &format!("ruff format --check {RUFF_CACHE} ."),
            first(&found.ruff),
        )],
        ".ruff.toml, ruff.toml and a [tool.ruff] table in pyproject.toml",
    );
    let lint = pack::choose(
        "lint",
        &[Candidate::new(
            "ruff",
            &format!("ruff check {RUFF_CACHE} ."),
            first(&found.ruff),
        )],
        ".ruff.toml, ruff.toml and a [tool.ruff] table in pyproject.toml",
    )
    .note("ruff's security rules (the S group) run only where the configuration selects them");
    let check = pack::choose(
        "check",
        &[
            Candidate::new("mypy", "mypy --cache-dir=/dev/null", first(&found.mypy)),
            Candidate::new("pyright", "pyright", first(&found.pyright)),
            Candidate::new("pyrefly", "pyrefly check", first(&found.pyrefly)),
            Candidate::new("ty", "ty check", first(&found.ty)),
        ],
        "mypy.ini, .mypy.ini, pyrightconfig.json, pyrefly.toml, ty.toml and the tool tables of pyproject.toml",
    );
    let mut test = pack::choose(
        "test",
        &[Candidate::new(
            "pytest",
            "python -B -m pytest -p no:cacheprovider",
            first(&found.pytest),
        )],
        "pytest.toml, .pytest.toml, pytest.ini, .pytest.ini, a pytest table in pyproject.toml, and pytest sections in tox.ini and setup.cfg",
    );
    let options = addopts(tree, table, found.pytest.first());
    if test.command().is_some()
        && !options.contains("--doctest-modules")
        && !options.contains("--doctest-glob")
    {
        test = test.note(
            "the test stage doesn't run the examples in your documentation; add --doctest-modules to addopts if your docstrings hold examples",
        );
    }
    let backend = table
        .get("build-system")
        .and_then(|b| b.get("build-backend"))
        .and_then(toml::Value::as_str);
    let build = Binding::unbound(
        "build",
        &match backend {
            Some(backend) => {
                format!(
                    "pyproject.toml names the build backend {backend}, and this pack binds no build"
                )
            }
            None => "pyproject.toml declares no build backend, and this pack binds no build".into(),
        },
    );
    [format, lint, check, test]
        .into_iter()
        .map(|binding| match env {
            Some((name, file)) => binding.through(&Environment {
                name: name.to_string(),
                declared_by: file.clone(),
                prefix: prefix(name),
            }),
            None => match &binding.state {
                State::Bound { tool, .. } => {
                    let note = format!(
                        "no environment declared: the interpreter that runs {tool} is whatever the shell finds"
                    );
                    binding.note(&note)
                }
                _ => binding,
            },
        })
        .chain(std::iter::once(build))
        .collect()
}

/// A tool a stage's command runs.
struct Run {
    /// The tool, where the command names one.
    tool: Option<String>,
    /// The tool is run by its bare name, outside any environment tool.
    bare: bool,
    words: Vec<String>,
}

/// The tool a word names, or the module `python -m` runs.
fn tool_of(words: &[&str]) -> Option<String> {
    let word = words.iter().find(|w| !w.starts_with('-'))?;
    if matches!(program(word), "python" | "python3") {
        return module(words);
    }
    Some(program(word).to_string())
}

/// The word after `-m` in a `python` command.
fn module(words: &[&str]) -> Option<String> {
    let at = words.iter().position(|w| *w == "-m")?;
    words.get(at + 1).map(|w| program(w).to_string())
}

/// Each simple command of `command`, as the tool it runs. A word after an
/// environment tool's `run` runs that tool through it, and so does the module
/// after `python -m` (SPC-1330).
fn runs(command: &str) -> Vec<Run> {
    commands(command)
        .into_iter()
        .filter_map(|words| {
            let owned: Vec<String> = words.iter().map(|w| w.to_string()).collect();
            let start = words
                .iter()
                .position(|w| !(w.contains('=') && !w.starts_with('-')))?;
            let rest = &words[start..];
            let first = program(rest[0]);
            Some(if matches!(first, "uv" | "poetry" | "pdm") {
                let tool = (rest.get(1) == Some(&"run"))
                    .then(|| tool_of(&rest[2..]))
                    .flatten();
                Run {
                    tool,
                    bare: false,
                    words: owned,
                }
            } else if matches!(first, "python" | "python3") {
                Run {
                    tool: module(rest),
                    bare: true,
                    words: owned,
                }
            } else {
                Run {
                    tool: Some(first.to_string()),
                    bare: !rest[0].contains('/'),
                    words: owned,
                }
            })
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

/// What `check` reports for the project in `argument`'s directory.
fn check(argument: Option<&str>) -> u8 {
    println!("meow-python check");
    let tree = Tree::read();
    let directory = match target(&tree, argument) {
        Ok(directory) => directory,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
    let project = match pyproject(&tree, &directory) {
        Ok(table) => table,
        Err(reason) => {
            println!("unresolved: {reason}");
            return UNRESOLVED;
        }
    };
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
    let found = findings(&tree, &directory, &project, &table);
    if found.is_empty() {
        let clean = pack::Clean {
            said: "no findings".into(),
            groups: [
                "the environment",
                "the fixes",
                "the caches",
                "the configuration files",
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
    FOUND
}

/// The findings in the stages and the files behind them (REQ-2426, REQ-2434,
/// REQ-2442).
fn findings(
    tree: &Tree,
    directory: &str,
    project: &toml::Table,
    table: &toml::Table,
) -> Vec<String> {
    let mut found: Vec<String> = Vec::new();
    let mut push = |line: String| {
        if !found.contains(&line) {
            found.push(line);
        }
    };
    let environment = match environment(tree, directory, project) {
        Ok(env) => env,
        Err(reason) => {
            push(reason);
            None
        }
    };
    let in_tree = |cache: &str| {
        let path = if directory == "." {
            format!("{cache}/x")
        } else {
            format!("{directory}/{cache}/x")
        };
        !tree::ignored(&tree.root, &path)
    };
    for (stage, command) in tree::declared(table) {
        for run in runs(&command) {
            if let Some((name, _)) = &environment
                && run.bare
                && let Some(tool) = run.tool.as_deref().filter(|t| WATCHED.contains(t))
            {
                push(format!(
                    "{stage} runs {tool} outside {name}: write {} {tool}",
                    prefix(name)
                ));
            }
            if names(&run, "ruff") {
                let fixing = matches!(stage, "format" | "lint");
                if has_flag(&run, "--unsafe-fixes") {
                    push("ruff would apply unsafe fixes: remove --unsafe-fixes".into());
                }
                if fixing && has_flag(&run, "--fix") {
                    push("ruff applies fixes in a check: remove --fix".into());
                }
                if run.words.iter().any(|w| w == "format")
                    && !has_flag(&run, "--check")
                    && !has_flag(&run, "--diff")
                {
                    push("ruff format rewrites the tree: pass --check".into());
                }
                let moved = has_flag(&run, "--cache-dir")
                    || run.words.iter().any(|w| w.starts_with("RUFF_CACHE_DIR="));
                if !moved && in_tree(".ruff_cache") {
                    push("ruff writes .ruff_cache into the tree: pass --cache-dir".into());
                }
            }
            if names(&run, "mypy") && !has_flag(&run, "--cache-dir") && in_tree(".mypy_cache") {
                push("mypy writes .mypy_cache into the tree: pass --cache-dir=/dev/null".into());
            }
            if names(&run, "pytest")
                && !run.words.iter().any(|w| w.contains("no:cacheprovider"))
                && !has_flag(&run, "--cache-dir")
                && in_tree(".pytest_cache")
            {
                push("pytest writes .pytest_cache into the tree: pass -p no:cacheprovider".into());
            }
        }
    }
    let configured = configs(tree, directory, project);
    for (files, tool) in [
        (&configured.ruff, "ruff"),
        (&configured.mypy, "mypy"),
        (&configured.ty, "ty"),
        (&configured.pytest, "pytest"),
    ] {
        if let Some((winner, losers)) = files.split_first() {
            for loser in losers {
                push(format!(
                    "{loser} configures {tool} and {winner} does too: {tool} reads {winner} alone"
                ));
            }
        }
    }
    found
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_setup_file_alone_is_not_a_project() {
        let tracked: BTreeSet<String> = [
            "setup.py",
            "requirements.txt",
            "a/pyproject.toml",
            ".venv/x/pyproject.toml",
        ]
        .iter()
        .map(|p| p.to_string())
        .collect();
        let dirs: Vec<String> = markers(&tracked).into_iter().map(|m| m.directory).collect();
        assert_eq!(dirs, ["a"]);
    }

    #[test]
    fn the_module_after_python_dash_m_is_the_tool_it_runs() {
        let tools = |command: &str| -> Vec<(Option<String>, bool)> {
            runs(command)
                .into_iter()
                .map(|r| (r.tool, r.bare))
                .collect()
        };
        assert_eq!(
            tools("python -B -m pytest -p no:cacheprovider"),
            [(Some("pytest".into()), true)]
        );
        assert_eq!(
            tools("uv run python -m mypy . && RUFF_CACHE_DIR=/t ruff check ."),
            [(Some("mypy".into()), false), (Some("ruff".into()), true)]
        );
        assert_eq!(
            tools("poetry run ruff check ."),
            [(Some("ruff".into()), false)]
        );
        assert_eq!(tools(".venv/bin/pytest"), [(Some("pytest".into()), false)]);
    }
}
