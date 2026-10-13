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

#![allow(dead_code)]

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
}

impl Candidate {
    pub(crate) fn new(tool: &str, command: &str, configured_by: Vec<String>) -> Candidate {
        Candidate {
            tool: tool.to_string(),
            command: command.to_string(),
            configured_by,
            enables: Vec::new(),
            asked: Vec::new(),
        }
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
        }
    }

    /// A comment printed under the stage's line.
    pub(crate) fn note(mut self, note: &str) -> Binding {
        self.notes.push(note.to_string());
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
}
