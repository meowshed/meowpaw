// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-godot`: where a work tree holds a Godot project, which engine version
//! it was saved by, the `[stages]` table its configuration binds, and the
//! generated files it commits or ignores wrongly (SPC-1380).
//!
//! It reads the files git tracks, runs git alone and starts no Godot tool
//! (SPC-1190).

use crate::detect::{self, Marker};
use crate::pack::{self, Binding, Candidate, STAGES};
use crate::perdir::{self, FOUND, Tree, UNRESOLVED, in_dir, join, sh};
use std::collections::BTreeSet;

const LANGUAGE: &str = "Godot and GDScript";
const UNIT: &str = "meow-godot";
const USAGE: &str = "usage: meow-godot status | bind | check";

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 3] = [
    crate::help::Entry {
        name: "status",
        determines: "where this repository holds a Godot project, which engine version it names, and the tools it configures",
        by_hand: "list the tracked project.godot files, then read config/features in each and the gdformatrc, gdlintrc, .gutconfig.json and export_presets.cfg beside it",
        lines: "meow-godot profile: profile error: unknown key: scope: marker: engine: tool: commit: ignore: unresolved:",
        json: "",
    },
    crate::help::Entry {
        name: "bind",
        determines: "the `[stages]` lines that bind each stage to the Godot tool the repository configures",
        by_hand: "match gdformatrc, gdlintrc, .gutconfig.json and export_presets.cfg with the tool that reads each, once the engine version is known",
        lines: "meow-godot profile: profile error: unknown key: # [stages] format lint check test build unresolved:",
        json: "",
    },
    crate::help::Entry {
        name: "check",
        determines: "whether the engine's cache and identifier files are ignored and committed as they should be, and whether a stage exports without importing",
        by_hand: "read .gitignore against .godot/, *.import and *.uid, and each stage command for --export-release without --import",
        lines: "meow-godot profile: profile error: unknown key: <path> format lint check test build no unresolved:",
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

/// Each tracked `project.godot` (REQ-2346, REQ-3048).
pub(crate) fn markers(tracked: &BTreeSet<String>) -> Vec<Marker> {
    detect::by_name(tracked, &["project.godot"])
}

/// One Godot project: its directory, its project file and the engine version
/// the file names.
struct Project {
    dir: String,
    file: String,
    version: Option<(u32, u32)>,
}

impl Project {
    fn at_least(&self, major: u32, minor: u32) -> bool {
        self.version.is_some_and(|v| v >= (major, minor))
    }

    fn named(&self) -> String {
        match self.version {
            Some((major, minor)) => format!("{major}.{minor}"),
            None => "an unknown version".into(),
        }
    }

    /// Why no stage can bind, where the engine version isn't known (REQ-2446).
    fn not_detected(&self) -> String {
        format!(
            "Godot engine version not detected: {} names none in config/features",
            self.file
        )
    }
}

/// The engine's major and minor version, from the first entry of
/// `config/features`; `config_version` names the file's format and is never
/// read as the engine's (RES-0360).
fn engine(text: &str) -> Option<(u32, u32)> {
    let line = text
        .lines()
        .find_map(|l| l.trim().strip_prefix("config/features="))?;
    let first = line.split('"').nth(1)?;
    let mut parts = first.split('.');
    let major = parts.next()?.parse().ok()?;
    let minor = parts.next()?.parse().ok()?;
    Some((major, minor))
}

fn projects(tree: &Tree) -> Vec<Project> {
    markers(&tree.tracked)
        .into_iter()
        .map(|marker| Project {
            version: tree.text(&marker.file).as_deref().and_then(engine),
            dir: marker.directory,
            file: marker.file,
        })
        .collect()
}

/// The presets of `export_presets.cfg` that name an export path, as
/// `(name, export_path)`.
fn presets(text: &str) -> Vec<(String, String)> {
    let quoted = |value: &str| value.trim().trim_matches('"').to_string();
    let mut found: Vec<(String, String)> = Vec::new();
    let mut current: Option<(String, String)> = None;
    for line in text.lines().map(str::trim) {
        if line.starts_with('[') && line.ends_with(']') {
            found.extend(current.take());
            let inner = &line[1..line.len() - 1];
            if inner
                .strip_prefix("preset.")
                .is_some_and(|rest| !rest.is_empty() && !rest.contains('.'))
            {
                current = Some((String::new(), String::new()));
            }
        } else if let Some(entry) = current.as_mut() {
            if let Some(value) = line.strip_prefix("name=") {
                entry.0 = quoted(value);
            } else if let Some(value) = line.strip_prefix("export_path=") {
                entry.1 = quoted(value);
            }
        }
    }
    found.extend(current);
    found
        .into_iter()
        .filter(|(name, path)| !name.is_empty() && !path.is_empty())
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
        println!("marker: {}", project.file);
        match project.version {
            Some(_) => println!("engine: Godot {}, from {}", project.named(), project.file),
            None => {
                println!("unresolved: {}", project.not_detected());
                code = UNRESOLVED;
            }
        }
        for name in tree.names_in(&project.dir) {
            let tool = match name {
                "gdformatrc" => "gdformat",
                "gdlintrc" | ".gdlintrc" => "gdlint",
                ".gutconfig.json" => "GUT",
                "export_presets.cfg" => "the export presets",
                _ => continue,
            };
            println!("tool: {}: {tool}", join(&project.dir, name));
        }
        if project.at_least(4, 4) {
            println!("commit: *.import and *.uid, which are project state");
        } else {
            println!("commit: *.import, which are project state");
        }
        println!("ignore: .godot/, which is the engine's cache");
    }
    code
}

/// The five stages for one project, in the order `bind` prints them.
fn bindings(tree: &Tree, project: &Project) -> Vec<Binding> {
    if project.version.is_none() {
        return pack::waiting(&project.not_detected());
    }
    let dir = project.dir.as_str();
    let has = |name: &str| tree.tracked.contains(&join(dir, name));
    let configured = |names: &[&str]| -> Vec<String> {
        names
            .iter()
            .filter(|n| has(n))
            .map(|n| join(dir, n))
            .collect()
    };
    let out = perdir::out_dir(UNIT, dir);
    let path = sh(dir);
    let import = format!("godot --headless --path {path} --import");
    let format = pack::choose(
        "format",
        &[Candidate::new(
            "gdformat",
            &in_dir(dir, "gdformat --check ."),
            configured(&["gdformatrc"]),
        )],
        "gdformatrc",
    );
    let lint = pack::choose(
        "lint",
        &[Candidate::new(
            "gdlint",
            &in_dir(dir, "gdlint ."),
            configured(&["gdlintrc", ".gdlintrc"]),
        )],
        "gdlintrc and .gdlintrc",
    );
    let check = Binding::unbound(
        "check",
        "godot --check-only parses the one script --script names, so no command checks the project",
    );
    let godot4 = "the pack binds Godot 4's command line alone";
    let test = if !project.at_least(4, 0) {
        Binding::unresolved(
            "test",
            &format!(
                "{godot4}, and {} names Godot {}",
                project.file,
                project.named()
            ),
        )
    } else if has(".gutconfig.json") && !has("addons/gut/gut_cmdln.gd") {
        Binding::unbound(
            "test",
            ".gutconfig.json is committed, and addons/gut/gut_cmdln.gd isn't",
        )
    } else {
        pack::choose(
            "test",
            &[Candidate::new(
                "GUT",
                &format!(
                    "mkdir -p \"{out}\" && godot --headless --path {path} -s addons/gut/gut_cmdln.gd -gexit -gjunit_xml_file=\"{out}/junit.xml\""
                ),
                configured(&[".gutconfig.json"]),
            )],
            ".gutconfig.json",
        )
        .after(&import)
        .note("evidence: JUnit XML at the path -gjunit_xml_file names, outside the working tree")
    };
    let build = if !project.at_least(4, 0) {
        Binding::unresolved(
            "build",
            &format!(
                "{godot4}, and {} names Godot {}",
                project.file,
                project.named()
            ),
        )
    } else if !project.at_least(4, 1) {
        Binding::unbound(
            "build",
            &format!(
                "Godot {} may store credentials in export_presets.cfg, so the pack doesn't read it",
                project.named()
            ),
        )
    } else {
        build_binding(tree, dir, &out, &path, &import)
    };
    vec![format, lint, check, test, build]
}

/// `build`, from the first preset of `export_presets.cfg` that names an
/// export path.
fn build_binding(tree: &Tree, dir: &str, out: &str, path: &str, import: &str) -> Binding {
    let file = join(dir, "export_presets.cfg");
    let Some(text) = tree.text(&file) else {
        return Binding::unbound("build", "looked for export_presets.cfg");
    };
    let all = presets(&text);
    let Some((name, export)) = all.first() else {
        return Binding::unbound(
            "build",
            "export_presets.cfg names no preset with an export_path",
        );
    };
    let target = export.rsplit('/').next().unwrap_or("");
    if target.is_empty() {
        return Binding::unbound("build", "the first preset's export_path names no file");
    }
    let mut binding = pack::choose(
        "build",
        &[Candidate::new(
            "godot",
            &format!(
                "mkdir -p \"{out}\" && godot --headless --path {path} --export-release {} \"{out}/{target}\"",
                sh(name)
            ),
            vec![file],
        )],
        "export_presets.cfg",
    )
    .after(import);
    for (other, _) in &all[1..] {
        binding = binding.note(&format!(
            "export_presets.cfg also defines {other}; build exports the first preset with an export_path"
        ));
    }
    binding
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
        .map(|p| (p.dir.clone(), bindings(&tree, p), p.version.is_some()))
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
    for project in projects(&tree) {
        let dir = project.dir.as_str();
        if !tree.ignored(&join(dir, ".godot/probe")) {
            findings.push(format!("{dir}: .godot/ isn't ignored"));
        }
        if let Some(file) = tree.under(&join(dir, ".godot/")).first() {
            findings.push(format!("{dir}: .godot/ is tracked: {file}"));
        }
        if tree.ignored(&join(dir, "probe.import")) {
            findings.push(format!("{dir}: *.import files are ignored"));
        }
        if project.at_least(4, 4) && tree.ignored(&join(dir, "probe.uid")) {
            findings.push(format!("{dir}: *.uid files are ignored"));
        }
        match project.version {
            None => unresolved.push(project.not_detected()),
            Some(_) if !project.at_least(4, 1) => {
                if tree.tracked.contains(&join(dir, "export_presets.cfg")) {
                    findings.push(format!(
                        "{dir}: export_presets.cfg is tracked, and Godot {} may store credentials",
                        project.named()
                    ));
                }
            }
            Some(_) => {}
        }
    }
    for (stage, command) in tree.commands() {
        if command.contains("--export-release") && !command.contains("--import") {
            findings.push(format!(
                "{stage} exports with --export-release and imports nothing first"
            ));
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
            "the cache and identifier files",
            "an import before each export",
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
