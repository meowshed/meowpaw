// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The shared layer every language pack's program builds on (SPC-1190,
//! ADR-2670). A pack states its ecosystem as data: the tools that can serve
//! each stage, what in the repository configures each one, and what each
//! command checks. The layer holds the rules SPC-1190 states for every pack,
//! so a pack meets them by building its bindings and runs here and not by
//! restating them.
//!
//! What a pack runs: [`choose`] binds a stage to the tool the repository
//! configured and refuses a command that turns on a group nobody asked for,
//! [`Binding::through`] runs it through the declared environment,
//! [`Binding::after`] performs a build's prerequisite, [`Pin::against`]
//! compares a pinned toolchain with the installed one, and [`host`] with
//! [`waiting`] leaves every stage unresolved until the host is known.
//!
//! What a pack reports it didn't check: [`Binding::short_of`] names what a
//! narrower tool stops checking, [`Binding::requiring`] refuses a runner that
//! leaves out what the language runs as tests, [`Binding::with_detector`]
//! turns a defect detector on, [`Clean`] names the rule groups and level of a
//! clean run, and [`SupplyChain`] states a supply-chain check's reach.
//!
//! What a pack never changes: [`apply`] applies no fix its tool marks unsafe
//! and no suggestion during a check, and [`run`] points a tool's output
//! outside the working tree and names any file the run left in it.
//!
//! What a pack keeps: [`run`] collects the result in the ecosystem's
//! machine-readable [`Format`] or says the evidence is captured output, and
//! asks for the files its tool deletes unless asked; and
//! [`states_generated_files`] holds a pack's page to naming the generated
//! files to commit and the ones to ignore.

#![allow(dead_code)]

use std::path::{Path, PathBuf};

/// The five stages a pack binds, in the order `bind` prints them (SPC-1040).
pub(crate) const STAGES: [&str; 5] = ["format", "lint", "check", "test", "build"];

/// One tool that can serve a stage, with what the repository committed that
/// configures it.
#[derive(Clone, Debug)]
pub(crate) struct Candidate {
    pub tool: String,
    pub command: String,
    /// Each tracked file or setting that shows the repository configured this
    /// tool; empty where nothing does.
    pub configured_by: Vec<String>,
    /// Each lint group, strictness setting or analysis level the command turns
    /// on by its own words.
    pub enables: Vec<String>,
    /// Each of those the repository's configuration asks for.
    pub asked: Vec<String>,
    /// What the command checks, in the words the pack's document uses, such
    /// as `documentation examples`.
    pub covers: Vec<String>,
}

impl Candidate {
    pub(crate) fn new(tool: &str, command: &str, configured_by: Vec<String>) -> Candidate {
        Candidate {
            tool: tool.to_string(),
            command: command.to_string(),
            configured_by,
            enables: Vec::new(),
            asked: Vec::new(),
            covers: Vec::new(),
        }
    }

    /// What the command checks.
    pub(crate) fn covering(mut self, what: &[&str]) -> Candidate {
        self.covers = what.iter().map(|w| w.to_string()).collect();
        self
    }

    /// The groups the command turns on by its own words.
    pub(crate) fn enabling(mut self, groups: &[&str]) -> Candidate {
        self.enables = groups.iter().map(|g| g.to_string()).collect();
        self
    }

    /// The groups the repository's configuration asks for.
    pub(crate) fn asking(mut self, groups: &[String]) -> Candidate {
        self.asked = groups.to_vec();
        self
    }
}

/// What a stage resolves to.
#[derive(Clone, Debug, PartialEq)]
pub(crate) enum State {
    Bound {
        tool: String,
        command: String,
    },
    /// Nothing to bind, with what the pack looked for.
    Unbound(String),
    /// The stage can't be bound, with the reason.
    Unresolved(String),
}

/// One stage as `bind` prints it, with the comments printed under it.
#[derive(Clone, Debug)]
pub(crate) struct Binding {
    pub stage: String,
    pub state: State,
    pub notes: Vec<String>,
    /// What the bound command checks.
    pub covers: Vec<String>,
}

impl Binding {
    pub(crate) fn bound(stage: &str, tool: &str, command: &str) -> Binding {
        Binding::of(
            stage,
            State::Bound {
                tool: tool.to_string(),
                command: command.to_string(),
            },
        )
    }

    pub(crate) fn unbound(stage: &str, reason: &str) -> Binding {
        Binding::of(stage, State::Unbound(reason.to_string()))
    }

    pub(crate) fn unresolved(stage: &str, reason: &str) -> Binding {
        Binding::of(stage, State::Unresolved(reason.to_string()))
    }

    fn of(stage: &str, state: State) -> Binding {
        Binding {
            stage: stage.to_string(),
            state,
            notes: Vec::new(),
            covers: Vec::new(),
        }
    }

    /// A comment printed under the stage's line.
    pub(crate) fn note(mut self, note: &str) -> Binding {
        self.notes.push(note.to_string());
        self
    }

    /// What the bound command checks.
    pub(crate) fn covering(mut self, what: &[&str]) -> Binding {
        self.covers = what.iter().map(|w| w.to_string()).collect();
        self
    }

    /// The stage with a comment naming each thing the ecosystem's default
    /// tool, `default`, checks and the bound command doesn't, since nothing
    /// else in the stage checks it (REQ-2410). A binding that runs the rest
    /// covers it all and gets no comment.
    pub(crate) fn short_of(mut self, default: &str, checks: &[&str]) -> Binding {
        let State::Bound { tool, .. } = &self.state else {
            return self;
        };
        let missing: Vec<&str> = checks
            .iter()
            .copied()
            .filter(|what| !self.covers.iter().any(|c| c == what))
            .collect();
        if !missing.is_empty() {
            let note = format!(
                "{tool} doesn't check {}, which {default} does; nothing in this stage checks it now",
                missing.join(", ")
            );
            self.notes.push(note);
        }
        self
    }

    /// The stage refused where the bound command leaves out `what`, which the
    /// language runs as tests, such as its documentation examples, so a runner
    /// that silently skips them never binds (REQ-2412).
    pub(crate) fn requiring(mut self, what: &str) -> Binding {
        if let State::Bound { tool, .. } = &self.state
            && !self.covers.iter().any(|c| c == what)
        {
            self.state = State::Unresolved(format!(
                "{tool} leaves out {what}, which {} must run",
                self.stage
            ));
        }
        self
    }

    /// The stage with the language's defect detector on, or with a comment
    /// naming the profile's setting that turns it off, which is the record
    /// REQ-2414 asks for. `settings` is the profile's table for the language.
    pub(crate) fn with_detector(
        mut self,
        detector: &Detector,
        settings: Option<&toml::Table>,
    ) -> Binding {
        let State::Bound { command, .. } = &mut self.state else {
            return self;
        };
        let off = settings
            .and_then(|table| table.get(&detector.setting))
            .and_then(toml::Value::as_bool)
            == Some(false);
        if off {
            self.notes.push(format!(
                "{} is off, as [{}] {} = false records",
                detector.name, detector.language, detector.setting
            ));
            return self;
        }
        if !command
            .split_whitespace()
            .any(|word| word == detector.switch)
        {
            *command = match command.find(&detector.after) {
                Some(at) => {
                    let end = at + detector.after.len();
                    format!("{} {}{}", &command[..end], detector.switch, &command[end..])
                }
                None => format!("{command} {}", detector.switch),
            };
        }
        self
    }

    /// The bound command, where the stage is bound.
    pub(crate) fn command(&self) -> Option<&str> {
        match &self.state {
            State::Bound { command, .. } => Some(command),
            _ => None,
        }
    }

    /// Each command of the stage run through the environment or package
    /// manager the project declares, never through whatever the shell finds
    /// first (REQ-2426).
    pub(crate) fn through(mut self, environment: &Environment) -> Binding {
        if let State::Bound { command, .. } = &mut self.state {
            *command = command
                .split(" && ")
                .map(|part| {
                    if part.starts_with(&environment.prefix) {
                        part.to_string()
                    } else {
                        format!("{} {part}", environment.prefix)
                    }
                })
                .collect::<Vec<_>>()
                .join(" && ");
        }
        self
    }

    /// The stage with its prerequisite run first, where another form of the
    /// step performs it implicitly (REQ-2448).
    pub(crate) fn after(mut self, prerequisite: &str) -> Binding {
        if let State::Bound { command, .. } = &mut self.state {
            *command = format!("{prerequisite} && {command}");
        }
        self
    }

    /// The lines `bind` prints for the stage: `<stage> = "<command>"`, or a
    /// comment naming why it isn't bound, then each note as a comment.
    pub(crate) fn lines(&self) -> Vec<String> {
        let mut lines = vec![match &self.state {
            State::Bound { command, .. } => format!("{} = {}", self.stage, quoted(command)),
            State::Unbound(reason) => format!("# {}: unbound, {reason}", self.stage),
            State::Unresolved(reason) => format!("# {}: unresolved, {reason}", self.stage),
        }];
        lines.extend(self.notes.iter().map(|note| format!("# {note}")));
        lines
    }
}

/// A TOML basic string holding `text`.
fn quoted(text: &str) -> String {
    format!("\"{}\"", text.replace('\\', "\\\\").replace('"', "\\\""))
}

/// Binds `stage` to the first candidate the repository configured, in the
/// order the pack's document lists them, and never to a tool nothing
/// configures (REQ-2420). Where several are configured, the others are named
/// under the line, so the choice the order made is visible. A candidate whose
/// command turns on a group the repository's configuration doesn't ask for
/// is refused and the stage is unresolved, naming the group (REQ-2422). With
/// none configured, the stage is unbound, naming what the pack looked for.
pub(crate) fn choose(stage: &str, candidates: &[Candidate], looked_for: &str) -> Binding {
    let configured: Vec<&Candidate> = candidates
        .iter()
        .filter(|c| !c.configured_by.is_empty())
        .collect();
    let Some(first) = configured.first() else {
        return Binding::unbound(stage, &format!("looked for {looked_for}"));
    };
    let unasked: Vec<&str> = first
        .enables
        .iter()
        .filter(|group| !first.asked.contains(group))
        .map(String::as_str)
        .collect();
    if !unasked.is_empty() {
        return Binding::unresolved(
            stage,
            &format!(
                "{} would turn on {}, which the repository's configuration doesn't ask for",
                first.tool,
                unasked.join(", ")
            ),
        );
    }
    let mut binding = Binding::bound(stage, &first.tool, &first.command);
    binding.covers = first.covers.clone();
    for other in &configured[1..] {
        binding = binding.note(&format!(
            "{} configures {} too; {stage} runs {}, the first this pack's document lists",
            other.configured_by.join(", "),
            other.tool,
            first.tool
        ));
    }
    binding
}

/// The environment or package manager a project declares, which every tool
/// runs through.
#[derive(Clone, Debug)]
pub(crate) struct Environment {
    /// What the pack calls it, such as a package manager's name.
    pub name: String,
    /// The tracked file or setting that declares it.
    pub declared_by: String,
    /// The words that run a tool through it, put in front of each command.
    pub prefix: String,
}

/// A toolchain version the repository pins.
#[derive(Clone, Debug)]
pub(crate) struct Pin {
    pub tool: String,
    pub pinned: String,
    /// The tracked file that pins it.
    pub declared_by: String,
}

impl Pin {
    /// The line naming the pinned version, or, where the installed one
    /// differs or none is installed, the reason the stages are unresolved,
    /// naming both (REQ-2428). The pack reads the installed version from the
    /// tool in a command that runs it, since `status`, `bind` and `check` run
    /// none.
    pub(crate) fn against(&self, installed: Option<&str>) -> Result<String, String> {
        match installed {
            Some(version) if version == self.pinned => Ok(format!(
                "toolchain: {} {}, pinned in {} and installed",
                self.tool, self.pinned, self.declared_by
            )),
            other => Err(format!(
                "{} {} pinned, {} installed",
                self.tool,
                self.pinned,
                other.unwrap_or("none")
            )),
        }
    }
}

/// A host or implementation that can evaluate the language, with the tracked
/// files that show this repository uses it.
#[derive(Clone, Debug)]
pub(crate) struct Host {
    pub name: String,
    pub markers: Vec<String>,
}

/// The one host the repository shows, or why none is known: `<a> or <b> not
/// detected` where none is, and both named where several are, because a
/// command from the wrong one often succeeds and does something else
/// (REQ-2446).
pub(crate) fn host(hosts: &[Host]) -> Result<&Host, String> {
    let found: Vec<&Host> = hosts.iter().filter(|h| !h.markers.is_empty()).collect();
    let names = |list: &[&Host], joint: &str| {
        list.iter()
            .map(|h| h.name.as_str())
            .collect::<Vec<_>>()
            .join(joint)
    };
    match found.as_slice() {
        [one] => Ok(one),
        [] => Err(format!(
            "{} not detected",
            names(&hosts.iter().collect::<Vec<_>>(), " or ")
        )),
        several => Err(format!(
            "{} are all detected, so which one evaluates the language isn't known",
            names(several, " and ")
        )),
    }
}

/// Every stage unresolved for `reason`, as `bind` prints them while the host
/// isn't known (REQ-2446).
pub(crate) fn waiting(reason: &str) -> Vec<Binding> {
    STAGES
        .iter()
        .map(|stage| Binding::unresolved(stage, reason))
        .collect()
}

/// The detector a language ships for the defect class its programs most often
/// have, such as a race detector, and how `test` turns it on.
#[derive(Clone, Debug)]
pub(crate) struct Detector {
    pub name: String,
    /// The words that turn it on, such as `-race`.
    pub switch: String,
    /// The words of the command the switch follows, such as `go test`; where
    /// the command doesn't hold them, the switch goes at its end.
    pub after: String,
    /// The table the profile names for the language, such as `go`.
    pub language: String,
    /// The key in that table a repository sets to `false` to turn it off.
    pub setting: String,
}

/// A clean report: what the stage said, the rule groups or analyses it ran,
/// and the level it ran at where its tool hides findings below a level by
/// default, because a clean result under a default configuration is a claim
/// about the configuration (REQ-2432, REQ-2444).
#[derive(Clone, Debug)]
pub(crate) struct Clean {
    /// The words the report opens with, such as `no findings`.
    pub said: String,
    pub groups: Vec<String>,
    /// Whether the tool hides findings below a level unless told otherwise.
    pub hides_below_a_level: bool,
    pub level: Option<String>,
}

impl Clean {
    /// The line reporting the clean run, or why the report is incomplete: no
    /// rule group named, or no level named for a tool that hides findings
    /// below one.
    pub(crate) fn line(&self) -> Result<String, String> {
        if self.groups.is_empty() {
            return Err(format!(
                "{}: the report names no rule group it ran",
                self.said
            ));
        }
        let mut line = format!(
            "{}; rule groups enabled: {}",
            self.said,
            self.groups.join(", ")
        );
        match (&self.level, self.hides_below_a_level) {
            (Some(level), _) => line.push_str(&format!("; ran at level {level}")),
            (None, true) => {
                return Err(format!(
                    "{}: the tool hides findings below a level, and the report names none",
                    self.said
                ));
            }
            (None, false) => {}
        }
        Ok(line)
    }
}

/// How far a supply-chain check reaches.
#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) enum Reach {
    /// It reports a vulnerable dependency because the project depends on it.
    Presence,
    /// It reports one only where the code calls what is vulnerable.
    Reachability,
}

/// A supply-chain check, which states whether it covers transitive
/// dependencies and whether it reports presence or reachability, because the
/// two findings are different claims (REQ-2436).
#[derive(Clone, Debug)]
pub(crate) struct SupplyChain {
    pub tool: String,
    pub transitive: bool,
    pub reach: Reach,
}

impl SupplyChain {
    /// The line stating the check's reach.
    pub(crate) fn line(&self) -> String {
        let covers = if self.transitive {
            "direct and transitive dependencies"
        } else {
            "direct dependencies only"
        };
        let reports = match self.reach {
            Reach::Presence => {
                "a vulnerable dependency's presence, whether or not the code calls it"
            }
            Reach::Reachability => {
                "a vulnerable dependency only where the code reaches it, so reachability"
            }
        };
        format!("{}: covers {covers}, and reports {reports}", self.tool)
    }
}

/// Whether the tool producing a fix calls it safe to apply mechanically.
#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) enum Safety {
    Safe,
    Unsafe,
}

/// What a fix is: a repair of a finding, or a suggestion to use a newer
/// language feature, which is a kind of finding of its own (REQ-2440).
#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) enum Kind {
    Repair,
    Modernise,
}

/// One fix a tool proposed: in `path`, at `line`, replace `from` with `to`.
#[derive(Clone, Debug)]
pub(crate) struct Fix {
    pub path: String,
    pub line: usize,
    /// The tool's own words for it.
    pub said: String,
    pub from: String,
    pub to: String,
    pub safety: Safety,
    pub kind: Kind,
}

/// Whether the run checks or was asked to fix.
#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) enum Mode {
    Check,
    Fix,
}

/// Applies the fixes the run may apply, under `root`, and returns a line for
/// each fix. A check applies none and reports each, a suggestion to use a
/// newer feature among them (REQ-2440). A fixing run applies the safe ones
/// and reports each fix its tool marks unsafe as not applied (REQ-2430).
pub(crate) fn apply(root: &Path, fixes: &[Fix], mode: Mode) -> Vec<String> {
    let mut lines = Vec::new();
    for fix in fixes {
        let at = format!("{}:{}: {}", fix.path, fix.line, fix.said);
        let line = match (mode, fix.kind, fix.safety) {
            (Mode::Check, Kind::Modernise, _) => {
                format!("suggestion: {at}; a check applies none")
            }
            (Mode::Check, Kind::Repair, _) => format!("finding: {at}"),
            (Mode::Fix, _, Safety::Unsafe) => format!("unsafe, not applied: {at}"),
            (Mode::Fix, _, Safety::Safe) => {
                let path = root.join(&fix.path);
                match std::fs::read_to_string(&path) {
                    Ok(text) if text.contains(&fix.from) => {
                        match std::fs::write(&path, text.replacen(&fix.from, &fix.to, 1)) {
                            Ok(()) => format!("fixed: {at}"),
                            Err(error) => format!("not applied, {error}: {at}"),
                        }
                    }
                    Ok(_) => format!("not applied, the text changed since the tool read it: {at}"),
                    Err(error) => format!("not applied, {error}: {at}"),
                }
            }
        };
        lines.push(line);
    }
    lines
}

/// How a tool is told where to write.
#[derive(Clone, Debug)]
pub(crate) enum Ask {
    /// A flag followed by the path as the next word, such as `--out <dir>`.
    Flag(String),
    /// A flag joined to the path by `=`, such as `--out=<dir>`.
    Joined(String),
    /// An environment variable holding the path.
    Env(String),
}

/// One run of a stage's tool.
#[derive(Clone, Debug)]
pub(crate) struct Invocation {
    pub stage: String,
    pub program: String,
    pub args: Vec<String>,
    /// How to point the output the tool writes into the working directory by
    /// default somewhere else; `None` where it writes none.
    pub output: Option<Ask>,
    /// The machine-readable format the ecosystem reports the stage in;
    /// `None` where it has none, so the evidence is captured output.
    pub format: Option<Format>,
    /// How to ask the tool for files it deletes unless asked, and what they
    /// are, such as `the test binaries`.
    pub keep: Option<(Ask, String)>,
}

/// Where a run's machine-readable result comes from (REQ-2416).
#[derive(Clone, Debug)]
pub(crate) enum Format {
    /// The tool prints the format on standard output, as the invocation's
    /// own words ask it to; `name` names the format.
    Stdout { name: String },
    /// The tool writes the format to the file `ask` names, which the layer
    /// puts outside the working tree under `file`.
    File {
        name: String,
        ask: Ask,
        file: String,
    },
}

impl Invocation {
    pub(crate) fn new(stage: &str, program: &str, args: &[&str]) -> Invocation {
        Invocation {
            stage: stage.to_string(),
            program: program.to_string(),
            args: args.iter().map(|a| a.to_string()).collect(),
            output: None,
            format: None,
            keep: None,
        }
    }

    /// The tool writes output into the working directory unless told
    /// otherwise, and `ask` tells it.
    pub(crate) fn writing(mut self, ask: Ask) -> Invocation {
        self.output = Some(ask);
        self
    }

    /// The result is collected in `format`.
    pub(crate) fn reporting(mut self, format: Format) -> Invocation {
        self.format = Some(format);
        self
    }

    /// The tool deletes `what` unless `ask` asks it to keep them.
    pub(crate) fn keeping(mut self, ask: Ask, what: &str) -> Invocation {
        self.keep = Some((ask, what.to_string()));
        self
    }
}

/// Whether a pack's document states which of the ecosystem's generated files
/// are project state to commit and which are cache to ignore: a section
/// headed `Generated files` that says what to commit and what to ignore
/// (REQ-2450). It returns what the document lacks.
pub(crate) fn states_generated_files(document: &str) -> Result<(), String> {
    let mut section: Option<(usize, Vec<&str>)> = None;
    let mut fenced = false;
    for line in document.lines() {
        if line.trim_start().starts_with("```") {
            fenced = !fenced;
        }
        let depth = line.chars().take_while(|c| *c == '#').count();
        let heading = !fenced && depth > 0 && line[depth..].starts_with(' ');
        match &mut section {
            Some((level, _)) if heading && depth <= *level => break,
            Some((_, body)) => body.push(line),
            None if heading && line[depth..].trim().eq_ignore_ascii_case("generated files") => {
                section = Some((depth, Vec::new()));
            }
            None => {}
        }
    }
    let Some((_, body)) = section else {
        return Err("no section headed `Generated files`".into());
    };
    let text = body.join("\n").to_lowercase();
    let missing: Vec<&str> = ["commit", "ignore"]
        .into_iter()
        .filter(|word| !text.contains(word))
        .collect();
    if missing.is_empty() {
        Ok(())
    } else {
        Err(format!(
            "the `Generated files` section doesn't say what to {}",
            missing.join(" or ")
        ))
    }
}

/// What a run produced.
#[derive(Debug)]
pub(crate) struct Ran {
    pub status: Option<i32>,
    pub stdout: Vec<u8>,
    pub stderr: Vec<u8>,
    /// Each path `git status --porcelain` shows after the run and didn't
    /// before, which the run left in the working tree (REQ-2442).
    pub left: Vec<String>,
    /// The lines the pack prints about the run: where its output went, where
    /// its evidence is and where its kept files are.
    pub lines: Vec<String>,
    /// The file holding the machine-readable result, where the tool wrote one.
    pub report: Option<PathBuf>,
}

/// The directory outside the working tree where the runs of `pack` in the
/// repository at `root` keep their output: under the harness's state
/// directory, `$MEOWPAW_STATE_DIR`, or `$XDG_STATE_HOME/meowpaw`, or
/// `~/.local/state/meowpaw` (SPC-1080), or why there is none.
pub(crate) fn outside(pack: &str, root: &Path) -> Result<PathBuf, String> {
    let set = |name: &str| {
        std::env::var_os(name)
            .filter(|v| !v.is_empty())
            .map(PathBuf::from)
    };
    if std::env::var("MEOWPAW_STATE").is_ok_and(|v| v == "off") {
        return Err("state writing is off (MEOWPAW_STATE=off)".into());
    }
    let state = set("MEOWPAW_STATE_DIR")
        .or_else(|| set("XDG_STATE_HOME").map(|base| base.join("meowpaw")))
        .or_else(|| {
            if cfg!(windows) {
                set("LOCALAPPDATA").map(|base| base.join("meowpaw"))
            } else {
                set("HOME").map(|home| home.join(".local").join("state").join("meowpaw"))
            }
        })
        .ok_or("no state directory: set XDG_STATE_HOME, MEOWPAW_STATE_DIR or HOME")?;
    // One directory per work tree, so two checkouts never share a tool's output.
    let mut hasher = std::hash::DefaultHasher::new();
    std::hash::Hash::hash(root, &mut hasher);
    let tree = format!("{:016x}", std::hash::Hasher::finish(&hasher));
    Ok(state.join("packs").join(pack).join(tree))
}

/// Runs the invocation from `root` and keeps the working tree as it was:
/// output the tool writes there by default goes to a directory outside it,
/// and each file the run left anyway is named in `left` (REQ-2442). It
/// collects the result in the format the invocation names, or says the
/// evidence is captured output (REQ-2416), and asks for the files the tool
/// deletes unless asked, naming where they are (REQ-2418). It returns
/// `tool absent: <program>` where the program isn't on `PATH`, and
/// `tool broken: <program> ...` where it didn't start.
pub(crate) fn run(pack: &str, root: &Path, invocation: &Invocation) -> Result<Ran, String> {
    let needs = invocation.output.is_some()
        || invocation.keep.is_some()
        || matches!(invocation.format, Some(Format::File { .. }));
    let place = if needs {
        Some(outside(pack, root).map_err(|reason| {
            format!(
                "unresolved: nowhere outside the working tree for {}'s output: {reason}",
                invocation.program
            )
        })?)
    } else {
        None
    };
    run_in(root, invocation, place.as_deref())
}

/// [`run`], with the directory outside the tree given.
pub(crate) fn run_in(
    root: &Path,
    invocation: &Invocation,
    outside: Option<&Path>,
) -> Result<Ran, String> {
    let program = &invocation.program;
    let mut command = std::process::Command::new(program);
    command
        .args(&invocation.args)
        .current_dir(root)
        .stdin(std::process::Stdio::null());
    // Each directory outside the tree the run writes to, made before it runs.
    let place = |name: &str| -> Result<PathBuf, String> {
        let Some(outside) = outside else {
            return Err(format!(
                "unresolved: nowhere outside the working tree for {program}'s {name}"
            ));
        };
        let dir = outside.join(&invocation.stage).join(name);
        std::fs::create_dir_all(&dir)
            .map_err(|error| format!("unresolved: {} can't be made: {error}", dir.display()))?;
        Ok(dir)
    };
    let mut lines = Vec::new();
    if let Some(ask) = &invocation.output {
        let dir = place("output")?;
        point(&mut command, ask, &dir);
        lines.push(format!(
            "output: {program} writes to {}, outside the working tree",
            dir.display()
        ));
    }
    let mut report = None;
    match &invocation.format {
        Some(Format::Stdout { name }) => lines.push(format!(
            "evidence: {name}, read from {program}'s standard output"
        )),
        Some(Format::File { name, ask, file }) => {
            let path = place("report")?.join(file);
            point(&mut command, ask, &path);
            lines.push(format!("evidence: {name} at {}", path.display()));
            report = Some(path);
        }
        None => lines.push(format!(
            "evidence: captured output; {program} has no machine-readable report for {}",
            invocation.stage
        )),
    }
    if let Some((ask, what)) = &invocation.keep {
        let dir = place("kept")?;
        point(&mut command, ask, &dir);
        lines.push(format!("kept: {what} at {}", dir.display()));
    }
    let before = changed(root);
    let done = match command.output() {
        Ok(done) => done,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            return Err(format!("tool absent: {program}"));
        }
        Err(error) => return Err(format!("tool broken: {program} didn't start: {error}")),
    };
    let left = changed(root)
        .into_iter()
        .filter(|entry| !before.contains(entry))
        .map(|entry| entry.get(3..).unwrap_or("").to_string())
        .collect();
    Ok(Ran {
        status: done.status.code(),
        stdout: done.stdout,
        stderr: done.stderr,
        left,
        lines,
        report,
    })
}

/// Tells the command where to write, as `ask` says the tool takes it.
fn point(command: &mut std::process::Command, ask: &Ask, dir: &Path) {
    match ask {
        Ask::Flag(flag) => {
            command.arg(flag).arg(dir);
        }
        Ask::Joined(flag) => {
            command.arg(format!("{flag}={}", dir.display()));
        }
        Ask::Env(name) => {
            command.env(name, dir);
        }
    }
}

/// Each entry `git status --porcelain` prints for the work tree at `root`,
/// untracked files listed one by one, so a file a run adds shows as itself.
fn changed(root: &Path) -> std::collections::BTreeSet<String> {
    crate::profile::reading_git()
        .args(["status", "--porcelain=v1", "-z", "--untracked-files=all"])
        .current_dir(root)
        .output()
        .ok()
        .filter(|done| done.status.success())
        .map(|done| {
            done.stdout
                .split(|b| *b == 0)
                .filter(|entry| !entry.is_empty())
                .map(|entry| String::from_utf8_lossy(entry).into_owned())
                .collect()
        })
        .unwrap_or_default()
}

#[cfg(test)]
mod tests {
    //! Each rule held by a fixture pack: a made-up ecosystem whose tools are
    //! named for what they show, so a test reads as the rule it holds.
    use super::*;

    fn files(paths: &[&str]) -> Vec<String> {
        paths.iter().map(|p| p.to_string()).collect()
    }

    /// The fixture ecosystem's two linters, configured by their own files.
    fn linters(first: &[&str], second: &[&str]) -> Vec<Candidate> {
        vec![
            Candidate::new("lint-one", "lint-one .", files(first)),
            Candidate::new("lint-two", "lint-two --check", files(second)),
        ]
    }

    #[test]
    fn tsk_5120_criterion_1_the_configured_tool_binds_and_none_is_unbound() {
        // TSK-5120 criterion 1, REQ-2420: two tools serve lint; the repository
        // configures the second, so the second binds, and with neither the
        // stage is printed unbound.
        let bound = choose("lint", &linters(&[], &[".lint-two.toml"]), "x");
        assert_eq!(bound.command(), Some("lint-two --check"));
        assert_eq!(bound.lines(), ["lint = \"lint-two --check\""]);
        let neither = choose("lint", &linters(&[], &[]), ".lint-one and .lint-two.toml");
        assert_eq!(
            neither.lines(),
            ["# lint: unbound, looked for .lint-one and .lint-two.toml"]
        );
    }

    #[test]
    fn tsk_5120_criterion_1_a_second_configured_tool_is_named_and_not_run() {
        // TSK-5120 criterion 1, REQ-2420: with both configured, the order the
        // pack's document states binds, and the other is named, not run.
        let both = choose("lint", &linters(&[".lint-one"], &[".lint-two.toml"]), "x");
        assert_eq!(both.command(), Some("lint-one ."));
        assert!(
            both.notes
                .iter()
                .any(|n| n.contains(".lint-two.toml") && n.contains("lint-two")),
            "{:?}",
            both.notes
        );
    }

    #[test]
    fn tsk_5120_criterion_2_a_lint_group_nobody_asked_for_is_refused() {
        // TSK-5120 criterion 2, REQ-2422: a fixture binding that turns on
        // `pedantic`, which the repository's configuration doesn't name, is
        // refused, and the stage is unresolved naming the group.
        let eager = Candidate::new("lint-one", "lint-one -W pedantic", files(&[".lint-one"]))
            .enabling(&["pedantic"])
            .asking(&files(&["correctness"]));
        let refused = choose("lint", std::slice::from_ref(&eager), "x");
        assert!(refused.command().is_none(), "{:?}", refused.state);
        assert!(
            matches!(&refused.state, State::Unresolved(r) if r.contains("pedantic")),
            "{:?}",
            refused.state
        );
        let asked = eager.asking(&files(&["pedantic"]));
        assert_eq!(
            choose("lint", &[asked], "x").command(),
            Some("lint-one -W pedantic")
        );
    }

    #[test]
    fn tsk_5120_criterion_3_each_command_runs_through_the_declared_package_manager() {
        // TSK-5120 criterion 3, REQ-2426: a fixture project declaring the
        // package manager `fixpm` runs every bound command through it.
        let manager = Environment {
            name: "fixpm".into(),
            declared_by: "fixpm.lock".into(),
            prefix: "fixpm exec".into(),
        };
        let bound =
            Binding::bound("test", "fixtest", "fixtest unit && fixtest docs").through(&manager);
        assert_eq!(
            bound.command(),
            Some("fixpm exec fixtest unit && fixpm exec fixtest docs")
        );
        let unbound = Binding::unbound("build", "looked for x").through(&manager);
        assert_eq!(unbound.state, State::Unbound("looked for x".into()));
    }

    #[test]
    fn tsk_5120_criterion_4_a_pinned_version_unlike_the_installed_one_names_both() {
        // TSK-5120 criterion 4, REQ-2428: the pinned and the installed version
        // are both named where they differ, and the stages are unresolved.
        let pin = Pin {
            tool: "fixc".into(),
            pinned: "1.80.0".into(),
            declared_by: "fix-toolchain.toml".into(),
        };
        let differs = pin.against(Some("1.85.0")).unwrap_err();
        assert_eq!(differs, "fixc 1.80.0 pinned, 1.85.0 installed");
        let absent = pin.against(None).unwrap_err();
        assert_eq!(absent, "fixc 1.80.0 pinned, none installed");
        let same = pin.against(Some("1.80.0")).unwrap();
        assert!(same.contains("1.80.0") && same.contains("fix-toolchain.toml"));
    }

    #[test]
    fn tsk_5120_criterion_5_with_no_host_detected_every_stage_waits_on_it() {
        // TSK-5120 criterion 5, REQ-2446: a fixture language two hosts can
        // evaluate, with neither detected, leaves every stage unresolved
        // naming the hosts it waits on.
        let hosts = [
            Host {
                name: "fixhost".into(),
                markers: Vec::new(),
            },
            Host {
                name: "otherhost".into(),
                markers: Vec::new(),
            },
        ];
        let reason = host(&hosts).unwrap_err();
        assert_eq!(reason, "fixhost or otherhost not detected");
        let table = waiting(&reason);
        assert_eq!(
            table.iter().map(|b| b.stage.as_str()).collect::<Vec<_>>(),
            STAGES
        );
        for binding in &table {
            assert_eq!(
                binding.lines(),
                [format!(
                    "# {}: unresolved, fixhost or otherhost not detected",
                    binding.stage
                )]
            );
        }
    }

    #[test]
    fn tsk_5120_criterion_5_one_host_detected_is_the_one_and_two_are_unknown() {
        // TSK-5120 criterion 5, REQ-2446: one detected host applies; two
        // detected leave the host unknown, naming both.
        let one = Host {
            name: "fixhost".into(),
            markers: files(&["fixhost.cfg"]),
        };
        let two = Host {
            name: "otherhost".into(),
            markers: files(&["other.cfg"]),
        };
        let none = Host {
            name: "thirdhost".into(),
            markers: Vec::new(),
        };
        assert_eq!(
            host(&[one.clone(), none]).map(|h| h.name.clone()),
            Ok("fixhost".to_string())
        );
        let both = host(&[one, two]).unwrap_err();
        assert!(
            both.contains("fixhost") && both.contains("otherhost"),
            "{both}"
        );
    }

    #[test]
    fn tsk_5120_criterion_6_the_build_runs_its_prerequisite_first() {
        // TSK-5120 criterion 6, REQ-2448: a fixture build whose prerequisite
        // another form of the step performs implicitly runs it first.
        let build = Binding::bound("build", "fixbuild", "fixbuild --release").after("fixgen");
        assert_eq!(build.command(), Some("fixgen && fixbuild --release"));
    }

    /// The fixture ecosystem's default test runner checks these three.
    const DEFAULT_CHECKS: [&str; 3] = ["unit tests", "integration tests", "documentation examples"];

    #[test]
    fn tsk_5125_criterion_1_a_narrower_tool_names_what_is_no_longer_checked() {
        // TSK-5125 criterion 1, REQ-2410: a fixture runner faster and narrower
        // than the default names what nothing in the stage checks now.
        let narrow = Binding::bound("test", "fastrun", "fastrun")
            .covering(&["unit tests", "integration tests"])
            .short_of("fixtest", &DEFAULT_CHECKS);
        assert!(
            narrow
                .notes
                .iter()
                .any(|n| n.contains("documentation examples") && n.contains("fixtest")),
            "{:?}",
            narrow.notes
        );
        let whole = Binding::bound("test", "fastrun", "fastrun && fixtest --doc")
            .covering(&DEFAULT_CHECKS)
            .short_of("fixtest", &DEFAULT_CHECKS);
        assert!(whole.notes.is_empty(), "{:?}", whole.notes);
    }

    #[test]
    fn tsk_5125_criterion_2_a_runner_leaving_out_documentation_examples_is_refused() {
        // TSK-5125 criterion 2, REQ-2412: the fixture language runs its
        // documentation examples as tests, so `test` runs them, and a runner
        // that leaves them out fails the layer's rule.
        let runs = Binding::bound("test", "fixtest", "fixtest")
            .covering(&DEFAULT_CHECKS)
            .requiring("documentation examples");
        assert_eq!(runs.command(), Some("fixtest"));
        let skips = Binding::bound("test", "fastrun", "fastrun")
            .covering(&["unit tests"])
            .requiring("documentation examples");
        assert!(
            matches!(&skips.state, State::Unresolved(r) if r.contains("documentation examples")),
            "{:?}",
            skips.state
        );
    }

    fn race() -> Detector {
        Detector {
            name: "the race detector".into(),
            switch: "-race".into(),
            after: "fixgo test".into(),
            language: "fixgo".into(),
            setting: "race".into(),
        }
    }

    #[test]
    fn tsk_5125_criterion_3_the_detector_is_on_and_turning_it_off_is_named() {
        // TSK-5125 criterion 3, REQ-2414: `test` turns the fixture language's
        // detector on, and a profile turning it off is named in the report.
        let on = Binding::bound("test", "fixgo", "fixgo test ./...").with_detector(&race(), None);
        assert_eq!(on.command(), Some("fixgo test -race ./..."));
        let settings: toml::Table = "race = false".parse().unwrap();
        let off = Binding::bound("test", "fixgo", "fixgo test ./...")
            .with_detector(&race(), Some(&settings));
        assert_eq!(off.command(), Some("fixgo test ./..."));
        assert!(
            off.notes
                .iter()
                .any(|n| n.contains("the race detector") && n.contains("[fixgo] race = false")),
            "{:?}",
            off.notes
        );
    }

    #[test]
    fn tsk_5125_criterion_4_a_clean_report_names_its_groups_and_its_level() {
        // TSK-5125 criterion 4, REQ-2432, REQ-2444: a clean fixture run names
        // the rule groups enabled and the level it ran at, and a report that
        // omits either fails.
        let clean = Clean {
            said: "lint: no findings".into(),
            groups: vec!["correctness".into(), "suspicious".into()],
            hides_below_a_level: true,
            level: Some("warning".into()),
        };
        let line = clean.line().unwrap();
        assert!(line.starts_with("lint: no findings"), "{line}");
        assert!(line.contains("correctness, suspicious"), "{line}");
        assert!(line.contains("warning"), "{line}");
        let no_groups = Clean {
            groups: Vec::new(),
            ..clean.clone()
        };
        assert!(no_groups.line().is_err());
        let no_level = Clean {
            level: None,
            ..clean.clone()
        };
        assert!(no_level.line().is_err());
        let shows_all = Clean {
            hides_below_a_level: false,
            level: None,
            ..clean
        };
        assert!(shows_all.line().is_ok());
    }

    #[test]
    fn tsk_5125_criterion_5_a_supply_chain_check_states_its_reach() {
        // TSK-5125 criterion 5, REQ-2436: a fixture supply-chain check states
        // whether it covers transitive dependencies and whether it reports
        // presence or reachability.
        let presence = SupplyChain {
            tool: "fixaudit".into(),
            transitive: true,
            reach: Reach::Presence,
        }
        .line();
        assert!(presence.contains("transitive"), "{presence}");
        assert!(presence.contains("presence"), "{presence}");
        let reach = SupplyChain {
            tool: "fixvuln".into(),
            transitive: false,
            reach: Reach::Reachability,
        }
        .line();
        assert!(reach.contains("direct dependencies only"), "{reach}");
        assert!(reach.contains("reachab"), "{reach}");
    }

    /// A scratch directory of its own, removed when the test ends.
    struct Scratch(PathBuf);

    impl Scratch {
        fn new() -> Scratch {
            static NEXT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
            let n = NEXT.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
            let stamp = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos();
            let path =
                std::env::temp_dir().join(format!("meow-pack-{}-{n}-{stamp}", std::process::id()));
            std::fs::create_dir_all(&path).unwrap();
            Scratch(std::fs::canonicalize(&path).unwrap())
        }

        fn write(&self, name: &str, text: &str) -> PathBuf {
            let path = self.0.join(name);
            std::fs::create_dir_all(path.parent().unwrap()).unwrap();
            std::fs::write(&path, text).unwrap();
            path
        }

        fn read(&self, name: &str) -> String {
            std::fs::read_to_string(self.0.join(name)).unwrap()
        }
    }

    impl Drop for Scratch {
        fn drop(&mut self) {
            let _ = std::fs::remove_dir_all(&self.0);
        }
    }

    fn fix(from: &str, to: &str, safety: Safety, kind: Kind) -> Fix {
        Fix {
            path: "src/main.fix".into(),
            line: 1,
            said: format!("replace {from} with {to}"),
            from: from.into(),
            to: to.into(),
            safety,
            kind,
        }
    }

    #[test]
    fn tsk_5130_criterion_1_a_fix_marked_unsafe_is_reported_and_not_applied() {
        // TSK-5130 criterion 1, REQ-2430: the fixture tool marks one of its
        // two fixes unsafe; the fixing run applies the other and reports it.
        let tree = Scratch::new();
        tree.write("src/main.fix", "let a = old_safe;\nlet b = old_unsafe;\n");
        let lines = apply(
            &tree.0,
            &[
                fix("old_safe", "new_safe", Safety::Safe, Kind::Repair),
                fix("old_unsafe", "new_unsafe", Safety::Unsafe, Kind::Repair),
            ],
            Mode::Fix,
        );
        assert_eq!(
            tree.read("src/main.fix"),
            "let a = new_safe;\nlet b = old_unsafe;\n"
        );
        assert!(
            lines
                .iter()
                .any(|l| l.starts_with("unsafe, not applied:") && l.contains("old_unsafe")),
            "{lines:?}"
        );
    }

    #[test]
    fn tsk_5130_criterion_2_a_suggestion_is_reported_and_the_file_unchanged() {
        // TSK-5130 criterion 2, REQ-2440: the fixture tool suggests a newer
        // language feature; a check reports it and leaves the file alone.
        let tree = Scratch::new();
        let text = "for i in range(len(xs)):\n";
        tree.write("src/main.fix", text);
        let lines = apply(
            &tree.0,
            &[fix(
                "for i in range(len(xs))",
                "for i, x in enumerate(xs)",
                Safety::Safe,
                Kind::Modernise,
            )],
            Mode::Check,
        );
        assert_eq!(tree.read("src/main.fix"), text);
        assert!(
            lines.iter().any(|l| l.starts_with("suggestion:")),
            "{lines:?}"
        );
    }

    /// A git work tree in a scratch directory, and a fixture tool beside it
    /// that writes `result.txt` into `$FIX_OUT`, or into `out/` in the working
    /// directory where that is unset.
    #[cfg(unix)]
    fn tree_and_tool() -> (Scratch, Scratch, String) {
        use std::os::unix::fs::PermissionsExt;
        let tree = Scratch::new();
        let done = crate::profile::reading_git()
            .args(["init", "-q"])
            .current_dir(&tree.0)
            .output()
            .unwrap();
        assert!(done.status.success());
        let tools = Scratch::new();
        let tool = tools.write(
            "fixtool",
            "#!/bin/sh\nout=${FIX_OUT:-out}\nmkdir -p \"$out\"\necho checked > \"$out/result.txt\"\n",
        );
        std::fs::set_permissions(&tool, std::fs::Permissions::from_mode(0o755)).unwrap();
        (tree, tools, tool.to_string_lossy().into_owned())
    }

    #[cfg(unix)]
    fn porcelain(root: &Path) -> String {
        let done = crate::profile::reading_git()
            .args(["status", "--porcelain", "--untracked-files=all"])
            .current_dir(root)
            .output()
            .unwrap();
        String::from_utf8_lossy(&done.stdout).into_owned()
    }

    #[cfg(unix)]
    #[test]
    fn tsk_5130_criterion_3_output_goes_outside_and_the_tree_stays_clean() {
        // TSK-5130 criterion 3, REQ-2442: the fixture tool writes into the
        // working directory by default; run through the layer, the tree's
        // `git status --porcelain` is empty and the output sits outside it.
        let (tree, _tools, tool) = tree_and_tool();
        let state = Scratch::new();
        let invocation = Invocation::new("test", &tool, &[]).writing(Ask::Env("FIX_OUT".into()));
        let ran = run_in(&tree.0, &invocation, Some(&state.0)).unwrap();
        assert_eq!(ran.status, Some(0));
        assert_eq!(porcelain(&tree.0), "");
        assert!(ran.left.is_empty(), "{:?}", ran.left);
        let written: Vec<PathBuf> = walk(&state.0);
        assert!(
            written.iter().any(|p| p.ends_with("result.txt")),
            "{written:?}"
        );
        assert!(
            ran.lines.iter().any(|l| l.starts_with("output:")),
            "{:?}",
            ran.lines
        );
    }

    #[cfg(unix)]
    #[test]
    fn tsk_5130_criterion_3_a_file_left_in_the_tree_is_named() {
        // TSK-5130 criterion 3, REQ-2442: where the pack doesn't point the
        // output away, the layer names the file the run left in the tree.
        let (tree, _tools, tool) = tree_and_tool();
        let ran = run_in(&tree.0, &Invocation::new("test", &tool, &[]), None).unwrap();
        assert_eq!(ran.left, ["out/result.txt"]);
    }

    #[test]
    fn tsk_5130_an_absent_tool_is_reported_as_absent() {
        // TSK-5130, SPC-1190's failure paths: a tool not on `PATH` is absent.
        let tree = Scratch::new();
        let absent = run_in(
            &tree.0,
            &Invocation::new("test", "meow-no-such-tool-anywhere", &[]),
            None,
        )
        .unwrap_err();
        assert_eq!(absent, "tool absent: meow-no-such-tool-anywhere");
    }

    /// A fixture tool in its own scratch directory, running `body`.
    #[cfg(unix)]
    fn tool(body: &str) -> (Scratch, String) {
        use std::os::unix::fs::PermissionsExt;
        let tools = Scratch::new();
        let path = tools.write("fixtool", &format!("#!/bin/sh\n{body}"));
        std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o755)).unwrap();
        (tools, path.to_string_lossy().into_owned())
    }

    #[cfg(unix)]
    #[test]
    fn tsk_5135_criterion_1_a_result_is_collected_in_the_ecosystems_format() {
        // TSK-5135 criterion 1, REQ-2416: the fixture ecosystem reports tests
        // as XML to the file `--report` names; the run collects the result
        // there, outside the tree, and the report names the format and path.
        let tree = Scratch::new();
        let state = Scratch::new();
        let (_tools, tool) = tool("[ \"$1\" = --report ] && echo '<suite ok=\"1\"/>' > \"$2\"\n");
        let invocation = Invocation::new("test", &tool, &[]).reporting(Format::File {
            name: "fixture XML".into(),
            ask: Ask::Flag("--report".into()),
            file: "report.xml".into(),
        });
        let ran = run_in(&tree.0, &invocation, Some(&state.0)).unwrap();
        let report = ran.report.clone().expect("no report path");
        assert!(report.starts_with(&state.0), "{report:?}");
        assert_eq!(
            std::fs::read_to_string(&report).unwrap(),
            "<suite ok=\"1\"/>\n"
        );
        assert!(
            ran.lines
                .iter()
                .any(|l| l.starts_with("evidence: fixture XML at")
                    && l.contains(&*report.to_string_lossy())),
            "{:?}",
            ran.lines
        );
        let printed = Invocation::new("lint", &tool, &[]).reporting(Format::Stdout {
            name: "fixture JSON".into(),
        });
        let ran = run_in(&tree.0, &printed, None).unwrap();
        assert!(
            ran.lines
                .iter()
                .any(|l| l.starts_with("evidence: fixture JSON") && l.contains("standard output")),
            "{:?}",
            ran.lines
        );
    }

    #[cfg(unix)]
    #[test]
    fn tsk_5135_criterion_1_with_no_format_the_evidence_is_captured_output() {
        // TSK-5135 criterion 1, REQ-2416: an ecosystem with no
        // machine-readable format for the stage says so.
        let tree = Scratch::new();
        let (_tools, tool) = tool("echo all good\n");
        let ran = run_in(&tree.0, &Invocation::new("build", &tool, &[]), None).unwrap();
        assert!(
            ran.lines
                .iter()
                .any(|l| l.starts_with("evidence: captured output")),
            "{:?}",
            ran.lines
        );
    }

    #[cfg(unix)]
    #[test]
    fn tsk_5135_criterion_2_files_the_tool_deletes_are_kept_and_named() {
        // TSK-5135 criterion 2, REQ-2418: the fixture tool deletes its test
        // binaries unless `FIX_KEEP` names a directory; the run asks for them
        // and the report names where they are.
        let tree = Scratch::new();
        let state = Scratch::new();
        let (_tools, tool) = tool(
            "scratch=$(mktemp -d)\necho binary > \"$scratch/unit.bin\"\n\
             [ -n \"$FIX_KEEP\" ] && cp \"$scratch/unit.bin\" \"$FIX_KEEP/\"\nrm -r \"$scratch\"\n",
        );
        let invocation = Invocation::new("test", &tool, &[])
            .keeping(Ask::Env("FIX_KEEP".into()), "the test binaries");
        let ran = run_in(&tree.0, &invocation, Some(&state.0)).unwrap();
        let kept = ran
            .lines
            .iter()
            .find_map(|l| l.strip_prefix("kept: the test binaries at "))
            .unwrap_or_else(|| panic!("{:?}", ran.lines));
        assert!(Path::new(kept).join("unit.bin").is_file(), "{kept}");
        assert!(Path::new(kept).starts_with(&state.0), "{kept}");
    }

    #[test]
    fn tsk_5135_criterion_3_a_document_without_the_generated_files_fails() {
        // TSK-5135 criterion 3, REQ-2450: a pack's document that doesn't
        // state which generated files to commit and which to ignore fails.
        let silent = "# meow-fix\n\n## Run it\n\nRun `meow-fix status`.\n";
        assert!(states_generated_files(silent).is_err());
        let half = "# meow-fix\n\n## Generated files\n\nCommit `fix.lock`.\n\n## Run it\n\nIgnore nothing here.\n";
        assert!(states_generated_files(half).is_err());
        let stated = "# meow-fix\n\n## Generated files\n\nCommit `fix.lock`, which is project state.\nIgnore `.fixcache/`, which is cache.\n";
        assert_eq!(states_generated_files(stated), Ok(()));
    }

    #[test]
    fn tsk_5135_criterion_3_every_language_pack_states_its_generated_files() {
        // TSK-5135 criterion 3, REQ-2450: every language pack the repository
        // ships, a unit whose manifest carries the `language` keyword, states
        // its generated files on its page.
        let plugins = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins");
        let mut packs = Vec::new();
        for entry in std::fs::read_dir(&plugins).unwrap().flatten() {
            let manifest = entry.path().join(".claude-plugin/plugin.json");
            let Ok(text) = std::fs::read_to_string(&manifest) else {
                continue;
            };
            let json: serde_json::Value = serde_json::from_str(&text).unwrap();
            let language = json["keywords"]
                .as_array()
                .is_some_and(|words| words.iter().any(|w| w == "language"));
            if language {
                packs.push(entry.path());
            }
        }
        assert!(
            !packs.is_empty(),
            "no language pack found under {plugins:?}"
        );
        let failing: Vec<String> = packs
            .iter()
            .filter_map(|pack| {
                let page = std::fs::read_to_string(pack.join("README.md")).unwrap_or_default();
                states_generated_files(&page)
                    .err()
                    .map(|why| format!("{}: {why}", pack.display()))
            })
            .collect();
        assert!(failing.is_empty(), "{failing:#?}");
    }

    fn walk(dir: &Path) -> Vec<PathBuf> {
        let mut out = Vec::new();
        for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
            let path = entry.path();
            if path.is_dir() {
                out.extend(walk(&path));
            } else {
                out.push(path);
            }
        }
        out
    }
}
