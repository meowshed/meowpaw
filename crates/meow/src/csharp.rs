// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-csharp`: where a work tree holds a .NET solution or project, the SDK
//! it pins, the `[stages]` table its configuration binds, and the settings
//! that decide whether its lint means anything (SPC-1360).
//!
//! It reads the files git tracks and the SDK directories under the `dotnet`
//! root, and starts no .NET tool (SPC-1190).

use crate::detect::{self, Marker};
use crate::pack::{self, Binding, Candidate, Pin};
use crate::profile::{self, Profile};
use std::collections::BTreeSet;
use std::path::PathBuf;

const UNIT: &str = "meow-csharp";
const UNRESOLVED: u8 = 3;
const FOUND: u8 = 1;
const NOT_DETECTED: &str = "unresolved: not a C# repository";
const SOLUTIONS: [&str; 2] = [".slnx", ".sln"];
const TEST_PACKAGES: [&str; 5] = [
    "Microsoft.NET.Test.Sdk",
    "xunit",
    "NUnit",
    "MSTest",
    "<IsTestProject>true",
];
/// What `check` reads, named in its clean report (REQ-2432).
const SETTINGS: [&str; 3] = ["Nullable", "TreatWarningsAsErrors", "AnalysisLevel"];

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 3] = [
    crate::help::Entry {
        name: "status",
        determines: "where this repository holds a .NET solution or project, and the SDK, target, runner, formatter and analysis level each uses",
        by_hand: "list the tracked .sln, .slnx, .slnf and .csproj files, then read global.json, Directory.Build.props and .csharpierrc beside them",
        lines: "meow-csharp profile: unknown key: unresolved: scope: marker: sdk: test formatter: analysis target:",
        json: "",
    },
    crate::help::Entry {
        name: "bind",
        determines: "the `[stages]` lines that bind each stage to the dotnet command the repository's configuration names",
        by_hand: "restore explicitly, pass --no-restore and one --artifacts-path outside the tree to each dotnet command, and bind lint only where TreatWarningsAsErrors is set",
        lines: "meow-csharp unresolved: # [stages] format lint check test build",
        json: "",
    },
    crate::help::Entry {
        name: "check",
        determines: "whether Nullable, TreatWarningsAsErrors and AnalysisLevel are set where the compiler reads them",
        by_hand: "read Directory.Build.props and each project file for the three settings",
        lines: "meow-csharp profile: unknown key: unresolved: <path> no",
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
            eprintln!("usage: {UNIT} status | bind | check");
            2
        }
    }
}

fn file_name(path: &str) -> &str {
    path.rsplit('/').next().unwrap_or(path)
}

fn is_solution(name: &str) -> bool {
    SOLUTIONS.iter().any(|ext| name.ends_with(ext)) || name.ends_with(".slnf")
}

/// Whether `directory` lies inside `other`, or is it.
fn within(directory: &str, other: &str) -> bool {
    other == "." || directory == other || directory.starts_with(&format!("{other}/"))
}

/// Each tracked solution, and each tracked project under no directory holding
/// a solution, which that solution covers (REQ-2340, REQ-3048). It reads
/// paths alone, so no tool starts.
pub(crate) fn markers(tracked: &BTreeSet<String>) -> Vec<Marker> {
    let solutions: Vec<String> = tracked
        .iter()
        .filter(|path| is_solution(file_name(path)))
        .map(|path| detect::directory_of(path))
        .collect();
    tracked
        .iter()
        .filter(|path| {
            let name = file_name(path);
            is_solution(name)
                || (name.ends_with(".csproj")
                    && !solutions
                        .iter()
                        .any(|s| within(&detect::directory_of(path), s)))
        })
        .map(|path| Marker {
            file: path.clone(),
            directory: detect::directory_of(path),
        })
        .collect()
}

/// The work tree: its root, the files git tracks and the profile.
struct Tree {
    root: PathBuf,
    tracked: BTreeSet<String>,
    profile: Profile,
}

impl Tree {
    fn read() -> Tree {
        let root = profile::repository_root();
        let root = std::fs::canonicalize(&root).unwrap_or(root);
        let tracked = detect::tracked(&root);
        let profile = profile::read(&root);
        Tree {
            root,
            tracked,
            profile,
        }
    }

    fn text(&self, path: &str) -> Option<String> {
        std::fs::read_to_string(self.root.join(path)).ok()
    }

    fn json(&self, path: &str) -> Option<serde_json::Value> {
        serde_json::from_str(&pack::plain_json(&self.text(path)?)).ok()
    }

    fn declared(&self, stage: &str) -> bool {
        let Profile::Parsed(table, _) = &self.profile else {
            return false;
        };
        profile::stages(table)
            .and_then(toml::Value::as_table)
            .is_some_and(|stages| stages.contains_key(stage))
    }

    /// A directory outside the working tree for a stage's output, written as
    /// the shell expands it, one per repository and directory (REQ-2442).
    fn outside(&self, directory: &str) -> String {
        let repository = self
            .root
            .file_name()
            .map(|n| slug(&n.to_string_lossy()))
            .unwrap_or_else(|| "repository".to_string());
        let place = if directory == "." {
            "root".to_string()
        } else {
            slug(directory)
        };
        format!("\"${{TMPDIR:-/tmp}}/{UNIT}/{repository}/{place}\"")
    }
}

fn slug(text: &str) -> String {
    text.chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '.' || c == '_' {
                c
            } else {
                '-'
            }
        })
        .collect()
}

/// One directory a marker activates, as the pack read it.
struct Site {
    directory: String,
    /// What `status` prints for the directory.
    report: Vec<String>,
    /// A pinned SDK that isn't installed, which stops the stages from running
    /// as bound (REQ-2428).
    blocked: Option<String>,
    stages: Vec<Binding>,
    findings: Vec<String>,
}

/// The directory's one solution, then its one filter, then its one project,
/// or both names where a level holds two.
fn target(names: &[&str]) -> Result<String, String> {
    let levels: [&dyn Fn(&str) -> bool; 3] = [
        &|n| SOLUTIONS.iter().any(|ext| n.ends_with(ext)),
        &|n| n.ends_with(".slnf"),
        &|n| n.ends_with(".csproj"),
    ];
    for level in levels {
        let found: Vec<&str> = names.iter().copied().filter(|n| level(n)).collect();
        match found.as_slice() {
            [] => continue,
            [one] => return Ok(one.to_string()),
            several => return Err(several.join(" and ")),
        }
    }
    Err("no solution or project".into())
}

/// An SDK version as (major, minor, feature band, patch).
fn sdk_version(text: &str) -> Option<(u32, u32, u32, u32)> {
    let text = text.split('-').next()?;
    let mut parts = text.split('.');
    let major = parts.next()?.parse().ok()?;
    let minor = parts.next()?.parse().ok()?;
    let third: u32 = parts.next()?.parse().ok()?;
    Some((major, minor, third / 100, third % 100))
}

/// Whether `installed` satisfies the pin under `roll`, as the muxer's
/// matching rules state (RES-0360).
fn satisfies(pin: (u32, u32, u32, u32), roll: &str, installed: (u32, u32, u32, u32)) -> bool {
    let (major, minor, band, _) = pin;
    match roll {
        "disable" => installed == pin,
        "feature" | "latestFeature" => {
            installed.0 == major && installed.1 == minor && installed >= pin
        }
        "minor" | "latestMinor" => installed.0 == major && installed >= pin,
        "major" | "latestMajor" => installed >= pin,
        _ => {
            installed.0 == major && installed.1 == minor && installed.2 == band && installed >= pin
        }
    }
}

/// The SDKs installed under the `dotnet` root: `$DOTNET_ROOT`, or the
/// directory of the `dotnet` on `PATH` with links resolved.
fn installed() -> Vec<String> {
    let root = std::env::var_os("DOTNET_ROOT")
        .map(PathBuf::from)
        .or_else(|| {
            let path = std::env::var_os("PATH")?;
            std::env::split_paths(&path)
                .map(|dir| dir.join("dotnet"))
                .find(|candidate| candidate.is_file())
                .and_then(|found| std::fs::canonicalize(found).ok())
                .and_then(|found| found.parent().map(PathBuf::from))
        });
    let mut versions: Vec<String> = root
        .and_then(|root| std::fs::read_dir(root.join("sdk")).ok())
        .into_iter()
        .flatten()
        .flatten()
        .filter(|entry| entry.path().is_dir())
        .map(|entry| entry.file_name().to_string_lossy().into_owned())
        .filter(|name| sdk_version(name).is_some())
        .collect();
    versions.sort_by_key(|v| sdk_version(v));
    versions
}

/// The value of an MSBuild element `<name>value</name>`, trimmed.
fn element(text: &str, name: &str) -> Option<String> {
    let open = format!("<{name}>");
    let start = text.find(&open)? + open.len();
    let end = text[start..].find("</")? + start;
    Some(text[start..end].trim().to_string())
}

/// The MSBuild files whose properties apply in `directory`: each
/// `Directory.Build.props` from it up to the root, then every project under it.
fn msbuild_texts(tree: &Tree, directory: &str) -> Vec<String> {
    let mut texts: Vec<String> = detect::ancestors(directory)
        .iter()
        .map(|d| detect::join(d, "Directory.Build.props"))
        .filter(|path| tree.tracked.contains(path))
        .filter_map(|path| tree.text(&path))
        .collect();
    texts.extend(
        detect::under(&tree.tracked, directory)
            .into_iter()
            .filter(|path| path.ends_with(".csproj"))
            .filter_map(|path| tree.text(path)),
    );
    texts
}

fn property(texts: &[String], name: &str) -> Option<String> {
    texts.iter().find_map(|text| element(text, name))
}

/// The CSharpier configuration the directory, a directory under it or one
/// above it commits.
fn csharpier(tree: &Tree, directory: &str) -> Option<String> {
    let configured = |path: &str| {
        let name = file_name(path);
        name.starts_with(".csharpierrc")
            || name == "csharpier.yaml"
            || (path.ends_with(".config/dotnet-tools.json")
                && tree.text(path).is_some_and(|t| t.contains("csharpier")))
    };
    let above = detect::ancestors(directory);
    detect::under(&tree.tracked, directory)
        .into_iter()
        .find(|path| configured(path))
        .or_else(|| {
            tree.tracked.iter().map(String::as_str).find(|path| {
                above.iter().skip(1).any(|up| {
                    detect::directory_of(path) == *up
                        || *path == detect::join(up, ".config/dotnet-tools.json")
                }) && configured(path)
            })
        })
        .map(str::to_string)
}

fn site(tree: &Tree, directory: &str) -> Site {
    let mut site = Site {
        directory: directory.to_string(),
        report: Vec::new(),
        blocked: None,
        stages: Vec::new(),
        findings: Vec::new(),
    };
    let names = detect::names_in(&tree.tracked, directory);
    let out = tree.outside(directory);
    let artifacts = format!("--artifacts-path {out}");

    let global = detect::nearest(&tree.tracked, directory, "global.json");
    let settings = global.as_deref().and_then(|p| tree.json(p));
    let setting = |pointer: &str| {
        settings
            .as_ref()
            .and_then(|g| g.pointer(pointer))
            .and_then(serde_json::Value::as_str)
    };
    let runner = setting("/test/runner").unwrap_or("VSTest");
    match (setting("/sdk/version"), global.as_deref()) {
        (Some(pinned), Some(file)) => {
            let roll = setting("/sdk/rollForward").unwrap_or("patch");
            let installed = installed();
            let listed = if installed.is_empty() {
                "none found".to_string()
            } else {
                installed.join(", ")
            };
            site.report.push(format!(
                "sdk: {pinned} pinned in {file}, rollForward {roll}, installed: {listed}"
            ));
            let met = sdk_version(pinned).is_some_and(|pin| {
                installed
                    .iter()
                    .filter_map(|v| sdk_version(v))
                    .any(|v| satisfies(pin, roll, v))
            });
            if !met {
                let pin = Pin {
                    tool: "dotnet".into(),
                    pinned: pinned.into(),
                    declared_by: file.into(),
                };
                let have = (!installed.is_empty()).then(|| installed.join(", "));
                site.blocked = Some(match pin.against(have.as_deref()) {
                    Ok(line) | Err(line) => line,
                });
            }
        }
        _ => site
            .report
            .push("sdk: not pinned, dotnet runs the newest SDK installed".into()),
    }
    site.report.push(format!("test runner: {runner}"));

    let texts = msbuild_texts(tree, directory);
    let level = property(&texts, "AnalysisLevel");
    let strict = property(&texts, "TreatWarningsAsErrors").is_some_and(|v| v == "true");
    let nullable = property(&texts, "Nullable").is_some_and(|v| v == "enable");
    let formatter = csharpier(tree, directory);
    site.report.push(match &formatter {
        Some(file) => format!("formatter: CSharpier, configured in {file}"),
        None => "formatter: none configured".into(),
    });
    site.report.push(match &level {
        Some(level) => format!("analysis level: {level}"),
        None => "analysis level: not set, the SDK's default applies".into(),
    });
    if !nullable {
        site.findings.push("Nullable isn't enabled".into());
    }
    if !strict {
        site.findings.push("TreatWarningsAsErrors isn't set".into());
    }
    if level.is_none() {
        site.findings
            .push("AnalysisLevel isn't set, the SDK's default applies".into());
    }
    let tests = detect::under(&tree.tracked, directory)
        .into_iter()
        .filter(|path| path.ends_with(".csproj"))
        .filter_map(|path| tree.text(path))
        .any(|text| TEST_PACKAGES.iter().any(|p| text.contains(p)));

    let format = pack::choose(
        "format",
        &[Candidate::new(
            "csharpier",
            "dotnet csharpier check .",
            formatter.into_iter().collect(),
        )],
        ".csharpierrc*, csharpier.yaml and csharpier in .config/dotnet-tools.json; dotnet format restores into obj/ beside each project and takes no --artifacts-path, so this pack binds it nowhere",
    );
    let target = match target(&names) {
        Ok(target) => target,
        Err(both) => {
            site.report
                .push(format!("target: none, {both} both qualify"));
            let why =
                format!("{both} both qualify, and the pack never picks one; declare the stage");
            site.stages = vec![format];
            for stage in &pack::STAGES[1..] {
                site.stages.push(Binding::unbound(stage, &why));
            }
            return site;
        }
    };
    site.report.push(format!("target: {target}"));
    let restore = format!("dotnet restore {target} {artifacts}");
    let compile = format!("dotnet build {target} --no-restore {artifacts}");
    let lint = if strict {
        Binding::bound("lint", "dotnet", &compile).after(&restore)
    } else {
        Binding::unbound(
            "lint",
            "TreatWarningsAsErrors isn't set, so the compiler fails on no analyser finding, and this pack turns on no strictness the repository didn't ask for",
        )
    };
    let check = Binding::bound("check", "dotnet", &compile)
        .after(&restore)
        .note(&match &level {
            Some(level) => format!("lint and check run at AnalysisLevel {level}"),
            None => "lint and check run at the SDK's default AnalysisLevel".into(),
        });
    let results = format!("--results-directory {}/test\"", out.trim_end_matches('"'));
    let test = if !tests {
        Binding::unbound(
            "test",
            "looked for a project referencing Microsoft.NET.Test.Sdk, xunit, NUnit or MSTest, or setting IsTestProject",
        )
    } else if runner == "Microsoft.Testing.Platform" {
        let kind = if target.ends_with(".csproj") {
            "--project"
        } else {
            "--solution"
        };
        Binding::bound(
            "test",
            "dotnet",
            &format!("dotnet test {kind} {target} --no-restore {artifacts} {results} -- --report-trx"),
        )
        .after(&restore)
        .note("test under Microsoft.Testing.Platform takes --artifacts-path from .NET 11, and --report-trx needs Microsoft.Testing.Extensions.TrxReport")
    } else {
        Binding::bound(
            "test",
            "dotnet",
            &format!("dotnet test {target} --no-restore {artifacts} --logger trx {results}"),
        )
        .after(&restore)
    };
    let build = Binding::bound(
        "build",
        "dotnet",
        &format!("dotnet build {target} --no-restore -c Release {artifacts}"),
    )
    .after(&restore);
    site.stages = vec![format, lint, check, test, build];
    site
}

/// Each directory a marker activates, with the marker files found there.
fn sites(tree: &Tree) -> Vec<(Site, Vec<String>)> {
    detect::by_directory(&markers(&tree.tracked))
        .into_iter()
        .map(|(directory, files)| (site(tree, &directory), files))
        .collect()
}

fn status() -> u8 {
    println!("{UNIT} status");
    let tree = Tree::read();
    let sites = sites(&tree);
    if sites.is_empty() {
        println!("{NOT_DETECTED}");
        return UNRESOLVED;
    }
    for line in profile::report(&tree.profile) {
        println!("{line}");
    }
    let parts = detect::parts(&tree.root);
    let mut code = 0;
    for (site, files) in &sites {
        println!("{}", detect::scope(&parts, &site.directory));
        for file in files {
            println!("marker: {file}");
        }
        for line in &site.report {
            println!("{line}");
        }
        if let Some(reason) = &site.blocked {
            println!("unresolved: {reason}");
            code = UNRESOLVED;
        }
    }
    code
}

/// A `[stages]` table bound from what the repository committed, never from
/// what is installed, and printed, never written (ADR-1900).
fn bind() -> u8 {
    let tree = Tree::read();
    let sites = sites(&tree);
    if sites.is_empty() {
        println!("{UNIT} bind");
        println!("{NOT_DETECTED}");
        return UNRESOLVED;
    }
    // What `bind` prints is pasted into the profile, so the state goes to
    // standard error.
    for line in profile::report(&tree.profile) {
        eprintln!("{line}");
    }
    println!("# {UNIT} bind: paste what follows into .meowpaw/profile.toml");
    let mut code = 0;
    for (site, _) in &sites {
        if let Some(reason) = &site.blocked {
            println!("# unresolved: {reason} in {}", site.directory);
            code = UNRESOLVED;
        }
    }
    println!("[stages]");
    let stages: Vec<(String, Vec<Binding>)> = sites
        .into_iter()
        .map(|(site, _)| (site.directory, site.stages))
        .collect();
    for binding in pack::across(&stages) {
        if !tree.declared(&binding.stage) {
            binding.lines().iter().for_each(|line| println!("{line}"));
        }
    }
    code
}

/// The settings that decide whether the lint stage means anything, read
/// where the compiler reads them (REQ-2444). It exits 1 on any finding.
fn check() -> u8 {
    println!("{UNIT} check");
    let tree = Tree::read();
    let sites = sites(&tree);
    if sites.is_empty() {
        println!("{NOT_DETECTED}");
        return UNRESOLVED;
    }
    for line in profile::report(&tree.profile) {
        println!("{line}");
    }
    match &tree.profile {
        Profile::Absent => {
            println!("unresolved: no profile at {}", profile::PROFILE);
            return UNRESOLVED;
        }
        Profile::Unparseable(message) => {
            println!("unresolved: the profile doesn't parse: {message}");
            return UNRESOLVED;
        }
        Profile::Parsed(..) => {}
    }
    let mut found = false;
    let mut unresolved = false;
    for (site, _) in &sites {
        if let Some(reason) = &site.blocked {
            println!("unresolved: {reason} in {}", site.directory);
            unresolved = true;
        }
        for finding in &site.findings {
            println!("{}: {finding}", site.directory);
            found = true;
        }
    }
    if found {
        return FOUND;
    }
    if unresolved {
        return UNRESOLVED;
    }
    let clean = pack::Clean {
        said: "no findings".into(),
        groups: SETTINGS.iter().map(|s| s.to_string()).collect(),
        hides_below_a_level: false,
        level: None,
    };
    match clean.line() {
        Ok(line) => println!("{line}"),
        Err(reason) => println!("unresolved: {reason}"),
    }
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tracked(paths: &[&str]) -> BTreeSet<String> {
        paths.iter().map(|p| p.to_string()).collect()
    }

    /// REQ-2340, REQ-3048: a solution at the root covers every project, and a
    /// project under no directory holding a solution activates its own.
    #[test]
    fn a_project_under_a_solution_is_no_marker_of_its_own() {
        let found = markers(&tracked(&[
            "Shop.slnx",
            "src/Shop/Shop.csproj",
            "tools/Tool/Tool.csproj",
        ]));
        let files: Vec<&str> = found.iter().map(|m| m.file.as_str()).collect();
        assert_eq!(files, ["Shop.slnx"]);
        let apart = markers(&tracked(&["shop/Shop.sln", "tools/Tool/Tool.csproj"]));
        let directories: Vec<&str> = apart.iter().map(|m| m.directory.as_str()).collect();
        assert_eq!(directories, ["shop", "tools/Tool"]);
    }

    /// REQ-2428: the pin is met as the muxer's `rollForward` policy says.
    #[test]
    fn a_pin_is_met_as_its_roll_forward_policy_says() {
        let pin = sdk_version("8.0.100").unwrap();
        let v = |text| sdk_version(text).unwrap();
        assert!(satisfies(pin, "patch", v("8.0.105")));
        assert!(!satisfies(pin, "patch", v("8.0.200")));
        assert!(satisfies(pin, "latestFeature", v("8.0.200")));
        assert!(!satisfies(pin, "latestMinor", v("9.0.100")));
        assert!(satisfies(pin, "latestMajor", v("9.0.100")));
        assert!(!satisfies(pin, "disable", v("8.0.105")));
    }
}
