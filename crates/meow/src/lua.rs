// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-lua`: where a work tree holds Lua or a Neovim plugin, which host
//! evaluates it, the `[stages]` table its configuration binds, and what a
//! plugin lacks (SPC-1370).
//!
//! It reads the files git tracks and starts no Lua tool (SPC-1190).

use crate::detect::{self, Marker};
use crate::pack::{self, Binding, Candidate, Host};
use crate::profile::{self, Profile};
use std::collections::BTreeSet;
use std::path::PathBuf;

const UNIT: &str = "meow-lua";
const UNRESOLVED: u8 = 3;
const FOUND: u8 = 1;
const NOT_DETECTED: &str = "unresolved: not a Lua and Neovim plugins repository";
const RUNTIMES: [&str; 5] = ["Lua 5.1", "Lua 5.2", "Lua 5.3", "Lua 5.4", "LuaJIT"];
/// What `check` reads in a Neovim plugin, named in its clean report
/// (REQ-2432).
const CHECKS: [&str; 2] = ["the plugin's .luarc.json", "the plugin's doc/"];

/// What each subcommand determines, what a person reads in its place, and its
/// kinds of line (SPC-1080).
pub(crate) const HELP: [crate::help::Entry; 3] = [
    crate::help::Entry {
        name: "status",
        determines: "where this repository holds Lua or a Neovim plugin, which host evaluates it, and the tools it configures",
        by_hand: "list the tracked rockspecs, .luarc.json files and lua/ beside plugin/ directories, then read runtime.version and the stylua, selene, luacheck and busted files",
        lines: "meow-lua profile: unknown key: unresolved: scope: marker: host: runtime formatter: linter:",
        json: "",
    },
    crate::help::Entry {
        name: "bind",
        determines: "the `[stages]` lines that bind each stage to the Lua tool the repository configures",
        by_hand: "match stylua.toml, selene.toml, .luacheckrc, .busted and the rockspec with the tool that reads each, once the runtime is known",
        lines: "meow-lua unresolved: # [stages] format lint check test build",
        json: "",
    },
    crate::help::Entry {
        name: "check",
        determines: "whether a Neovim plugin declares its runtime and documents itself for :help",
        by_hand: "look for .luarc.json and doc/ beside the plugin's lua/ and plugin/",
        lines: "meow-lua profile: unknown key: unresolved: <path> no",
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

/// Whether git tracks files under both `lua/` and `plugin/` of `directory`,
/// which lays out a Neovim plugin (REQ-2344).
fn laid_out_for_neovim(tracked: &BTreeSet<String>, directory: &str) -> bool {
    let has = |sub: &str| {
        let prefix = detect::join(directory, &format!("{sub}/"));
        tracked.iter().any(|p| p.starts_with(&prefix))
    };
    has("lua") && has("plugin")
}

/// The marker naming a Neovim plugin's layout in `directory`.
fn layout(directory: &str) -> String {
    format!(
        "{}, {}",
        detect::join(directory, "lua/"),
        detect::join(directory, "plugin/")
    )
}

/// Each tracked rockspec and `.luarc.json` (REQ-2342), and each directory
/// laid out as a Neovim plugin (REQ-2344, REQ-3048). It reads paths alone,
/// so no tool starts.
pub(crate) fn markers(tracked: &BTreeSet<String>) -> Vec<Marker> {
    let mut found: Vec<Marker> = tracked
        .iter()
        .filter(|path| {
            let name = file_name(path);
            name.ends_with(".rockspec") || name == ".luarc.json"
        })
        .map(|path| Marker {
            file: path.clone(),
            directory: detect::directory_of(path),
        })
        .collect();
    let mut plugins = BTreeSet::new();
    for path in tracked {
        let parts: Vec<&str> = path.split('/').collect();
        for (at, part) in parts.iter().enumerate() {
            if *part != "plugin" || at + 1 >= parts.len() {
                continue;
            }
            let directory = if at == 0 {
                ".".to_string()
            } else {
                parts[..at].join("/")
            };
            if laid_out_for_neovim(tracked, &directory) {
                plugins.insert(directory);
            }
        }
    }
    found.extend(plugins.into_iter().map(|directory| Marker {
        file: layout(&directory),
        directory,
    }));
    found
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

    fn table(&self) -> Option<&toml::Table> {
        match &self.profile {
            Profile::Parsed(table, _) => Some(table),
            _ => None,
        }
    }

    fn declared(&self, stage: &str) -> bool {
        self.table()
            .and_then(profile::stages)
            .and_then(toml::Value::as_table)
            .is_some_and(|stages| stages.contains_key(stage))
    }

    /// `[lua] runtime` in the profile.
    fn runtime(&self) -> Option<String> {
        self.table()?
            .get("lua")?
            .get("runtime")?
            .as_str()
            .filter(|v| !v.is_empty())
            .map(str::to_string)
    }

    /// The runtime a `.luarc.json` names, in the dotted or the nested form.
    fn luarc_runtime(&self, path: &str) -> Option<String> {
        let text = std::fs::read_to_string(self.root.join(path)).ok()?;
        let json: serde_json::Value = serde_json::from_str(&pack::plain_json(&text)).ok()?;
        json.get("runtime.version")
            .or_else(|| json.pointer("/runtime/version"))
            .and_then(serde_json::Value::as_str)
            .map(str::to_string)
    }
}

/// One directory a marker activates, as the pack read it.
struct Site {
    directory: String,
    report: Vec<String>,
    /// Why no host is known, which leaves every stage unresolved (REQ-2446).
    host: Option<String>,
    stages: Vec<Binding>,
    findings: Vec<String>,
}

fn site(tree: &Tree, directory: &str) -> Site {
    let tracked = &tree.tracked;
    let names = detect::names_in(tracked, directory);
    let neovim = laid_out_for_neovim(tracked, directory);
    let luarc = detect::join(directory, ".luarc.json");
    let declared = tracked
        .contains(&luarc)
        .then(|| tree.luarc_runtime(&luarc))
        .flatten();
    let mut site = Site {
        directory: directory.to_string(),
        report: Vec::new(),
        host: None,
        stages: Vec::new(),
        findings: Vec::new(),
    };
    // The host, in the order SPC-1370 states: the plugin layout, then
    // `.luarc.json`, then the profile.
    let source = if neovim {
        Some("Neovim, from lua/ beside plugin/".to_string())
    } else if let Some(runtime) = &declared {
        Some(format!("{runtime}, from {luarc}"))
    } else {
        tree.runtime()
            .map(|runtime| format!("{runtime}, from [lua] runtime"))
    };
    let hosts = [Host {
        name: "Lua runtime".into(),
        markers: source.clone().into_iter().collect(),
    }];
    match pack::host(&hosts) {
        Ok(_) => site
            .report
            .push(format!("host: {}", source.unwrap_or_default())),
        Err(reason) => {
            site.host = Some(format!(
                "{reason}: set runtime.version in .luarc.json or declare [lua] runtime"
            ))
        }
    }
    if let Some(runtime) = &declared
        && !RUNTIMES.contains(&runtime.as_str())
    {
        site.report
            .push(format!("runtime {runtime} is not one LuaLS names"));
    }
    if neovim {
        if !tracked.contains(&luarc) {
            site.findings.push(
                "no .luarc.json, so lua-language-server checks a Lua with no editor runtime declared"
                    .into(),
            );
        }
        let doc = detect::join(directory, "doc/");
        if !tracked.iter().any(|p| p.starts_with(&doc)) {
            site.findings
                .push("no doc/, so :help has nothing for the plugin's users".into());
        }
    }

    let stylua = detect::nearest(tracked, directory, "stylua.toml")
        .or_else(|| detect::nearest(tracked, directory, ".stylua.toml"));
    let selene = names
        .contains(&"selene.toml")
        .then(|| detect::join(directory, "selene.toml"));
    let luacheck = detect::nearest(tracked, directory, ".luacheckrc");
    let rockspecs: Vec<&str> = names
        .iter()
        .copied()
        .filter(|n| n.ends_with(".rockspec"))
        .collect();
    site.report.push(match &stylua {
        Some(file) => format!("formatter: stylua, configured in {file}"),
        None => "formatter: none configured".into(),
    });
    let linters: Vec<&str> = [("selene", &selene), ("luacheck", &luacheck)]
        .iter()
        .filter(|(_, file)| file.is_some())
        .map(|(name, _)| *name)
        .collect();
    site.report.push(if linters.is_empty() {
        "linter: none configured".into()
    } else {
        format!("linter: {}", linters.join(" and "))
    });
    if let Some(reason) = &site.host {
        site.stages = pack::waiting(reason);
        return site;
    }

    let format = pack::choose(
        "format",
        &[Candidate::new(
            "stylua",
            "stylua --check .",
            stylua.into_iter().collect(),
        )],
        "stylua.toml and .stylua.toml",
    );
    // selene and luacheck check different sets, so both run where both are
    // configured, and neither stands in for the other (REQ-2420).
    let lint = if selene.is_some() && luacheck.is_some() {
        Binding::bound("lint", "selene", "selene . && luacheck .").note(
            "lint runs selene and luacheck, both configured, because they check different sets",
        )
    } else {
        pack::choose(
            "lint",
            &[
                Candidate::new("selene", "selene .", selene.into_iter().collect()),
                Candidate::new("luacheck", "luacheck .", luacheck.into_iter().collect()),
            ],
            "selene.toml and .luacheckrc",
        )
    };
    let check = Binding::unbound(
        "check",
        "lua-language-server --check writes its findings to a log file, so a stage reading its exit status hasn't read them; declare a command that reads the report, such as llscheck",
    );
    let test = if neovim {
        Binding::unbound(
            "test",
            "a Neovim plugin's tests run inside nvim --headless, and the harness, plenary or mini.test, is the repository's to declare",
        )
    } else {
        let busted = names
            .contains(&".busted")
            .then(|| detect::join(directory, ".busted"));
        pack::choose(
            "test",
            &[Candidate::new(
                "busted",
                "busted",
                busted.into_iter().collect(),
            )],
            ".busted",
        )
    };
    let build = match rockspecs.as_slice() {
        [] if neovim => Binding::unresolved(
            "build",
            "a Neovim plugin is loaded from its source and has no build without a rockspec",
        ),
        [] => Binding::unresolved("build", "Lua has no build without a rockspec"),
        [one] => Binding::bound("build", "luarocks", &format!("luarocks make {one}")),
        several => Binding::unbound(
            "build",
            &format!(
                "{} each qualify, and the pack never picks one",
                several.join(" and ")
            ),
        ),
    };
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
        if let Some(reason) = &site.host {
            println!("unresolved: {reason}");
            code = UNRESOLVED;
        }
    }
    code
}

/// A `[stages]` table bound from what the repository committed, never from
/// what is installed, and printed, never written (ADR-1900). Every stage of a
/// directory whose host isn't known is unresolved, and it exits 3.
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
    let code = if sites.iter().any(|(site, _)| site.host.is_some()) {
        UNRESOLVED
    } else {
        0
    };
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

/// What a Neovim plugin lacks: a declared runtime and a help file
/// (RES-0107). It exits 1 on any finding.
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
        if let Some(reason) = &site.host {
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
        groups: CHECKS.iter().map(|c| c.to_string()).collect(),
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

    /// REQ-2342, REQ-2344, REQ-3048: a rockspec and a `.luarc.json` mark
    /// their directories, `lua/` beside `plugin/` marks a plugin, and a lone
    /// `lua/` marks nothing.
    #[test]
    fn each_marker_names_its_directory() {
        let found = markers(&tracked(&[
            "rocks/shop-1.0-1.rockspec",
            "nvim/lua/shop/init.lua",
            "nvim/plugin/shop.lua",
            "lua/alone.lua",
        ]));
        let pairs: Vec<(&str, &str)> = found
            .iter()
            .map(|m| (m.directory.as_str(), m.file.as_str()))
            .collect();
        assert_eq!(
            pairs,
            [
                ("rocks", "rocks/shop-1.0-1.rockspec"),
                ("nvim", "nvim/lua/, nvim/plugin/"),
            ]
        );
    }
}
