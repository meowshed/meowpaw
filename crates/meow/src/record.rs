// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Check a repository's record where the repository declares it.
//!
//! SPC-1070 states the behaviour. The record's root comes from `[record] root`
//! in the profile, or is `project/` (REQ-0520, REQ-0521), and the layout of
//! each kind comes from the unit's `lib/layout.toml`. Six checks read the
//! record and none writes a file (REQ-0137): front matter with each kind's
//! status vocabulary (REQ-0573, REQ-0590), identifiers, relations (REQ-0656),
//! each kind's index (REQ-0524), coverage (REQ-0246) and shape (REQ-0145).

use crate::profile::{self, Profile};

/// Prints a line, and stops quietly when the reader has gone, as `head` does,
/// because a closed pipe isn't a failure of the program.
macro_rules! say {
    () => {{
        use std::io::Write;
        if writeln!(std::io::stdout()).is_err() {
            std::process::exit(0);
        }
    }};
    ($($t:tt)*) => {{
        use std::io::Write;
        if writeln!(std::io::stdout(), $($t)*).is_err() {
            std::process::exit(0);
        }
    }};
}
use regex::Regex;
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

mod upgrade;

const CHECKS: [&str; 7] = [
    "front-matter",
    "identifiers",
    "relations",
    "index",
    "coverage",
    "shape",
    "rules",
];
/// What every command says of a record in the form ADR-3090 retired.
const OLD_FORM: &str = "the record holds epics or tasks, a form ADR-3090 retired; run paw upgrade";

const CLEAN: u8 = 0;
const FOUND: u8 = 1;
const USAGE: u8 = 2;
const UNCHECKED: u8 = 3;
/// Directories no walk enters: tooling, build output, the harness's own
/// templates, whose placeholders are not citations, and evaluation cases, whose
/// sample records name identifiers that don't exist on purpose.
const SKIP: [&str; 5] = ["node_modules", "target", "templates", "_archive", "evals"];

pub(crate) struct Kind {
    pub(crate) name: String,
    pub(crate) artifact: String,
    pub(crate) prefix: Option<String>,
    pub(crate) dir: Option<String>,
    pub(crate) file: Option<String>,
    pub(crate) fields: Vec<String>,
    /// Fields the kind may carry and no check requires (ADR-2630).
    pub(crate) optional_fields: Vec<String>,
    pub(crate) statuses: Vec<String>,
    pub(crate) index: Option<String>,
    pub(crate) sections: Vec<String>,
    pub(crate) draft_sections: Vec<String>,
    pub(crate) first_section: Option<String>,
    pub(crate) required_values: Vec<String>,
    pub(crate) forbidden_fields: Vec<String>,
    pub(crate) rules: Vec<String>,
    pub(crate) draft_rules: Vec<String>,
    /// The kinds this one wins over where two artifacts disagree. Only a
    /// kind the repository declares carries any (REQ-0667).
    pub(crate) outranks: Vec<String>,
    /// A retired kind, read and cited and never written (ADR-3090).
    pub(crate) archived: bool,
}

pub(crate) struct Layout {
    pub(crate) fields: Vec<String>,
    pub(crate) relations: Vec<String>,
    pub(crate) index_name: String,
    pub(crate) kinds: Vec<Kind>,
    pub(crate) retired_fields: BTreeMap<String, String>,
    pub(crate) retired_statuses: BTreeMap<String, String>,
    pub(crate) retired_sections: BTreeMap<String, String>,
    /// Phrases that name an earlier version, which a specification doesn't carry.
    pub(crate) history_phrases: Vec<String>,
}

struct Field {
    key: String,
    value: String,
    line: usize,
}

struct Doc {
    path: PathBuf,
    /// The path under the record's root, or empty for a file outside it.
    relative: String,
    shown: String,
    text: String,
    fields: Option<Vec<Field>>,
    kind: Option<usize>,
    is_index: bool,
}

impl Doc {
    fn field(&self, key: &str) -> Option<&Field> {
        self.fields.as_ref()?.iter().find(|f| f.key == key)
    }

    fn value(&self, key: &str) -> &str {
        self.field(key).map(|f| f.value.as_str()).unwrap_or("")
    }

    fn id(&self) -> &str {
        self.value("id")
    }
}

struct Finding {
    shown: String,
    line: Option<usize>,
    message: String,
}

impl Finding {
    fn at(doc: &Doc, line: Option<usize>, message: String) -> Finding {
        Finding {
            shown: doc.shown.clone(),
            line,
            message,
        }
    }
}

pub(crate) struct Record {
    layout: Layout,
    /// What is wrong with the kinds the profile declares, reported by the
    /// front matter check (REQ-0668).
    declarations: Vec<Finding>,
    docs: Vec<Doc>,
    outside: Vec<Doc>,
    ids: Regex,
}

/// One subcommand: what it determines, what a person reads to reach the same
/// answer by hand, and the first word of each kind of line it prints
/// (SPC-1080, REQ-1176, REQ-1184). A subcommand is dispatched through this
/// table only, so one can't be added without all three.
pub(crate) struct Command {
    pub(crate) name: &'static str,
    pub(crate) run: fn(&[String]) -> u8,
    pub(crate) determines: &'static str,
    pub(crate) by_hand: &'static str,
    /// Whitespace-separated. A word in angle brackets stands for a kind of
    /// word: `<id>` an identifier, `<count>` a number, anything else any word.
    pub(crate) lines: &'static str,
}

pub(crate) const COMMANDS: [Command; 15] = [
    Command {
        name: "check",
        run: check,
        determines: "whether the record meets each rule its layout declares",
        by_hand: "read each artifact's front matter, required sections and index table against `lib/layout.toml`, follow each cited identifier to the file that carries it, and for `frozen` compare each approved record with `git show <rev>:<path>`",
        lines: "front-matter: identifiers: relations: index: coverage: shape: rules: frozen: the <path> paw",
    },
    Command {
        name: "status",
        run: status,
        determines: "where each approved decision stands in the chain, as the record says",
        by_hand: "list every artifact whose `status:` is draft, then for each approved decision read its `status:` and whether it carries a `## Plan`, list each open defect, count each requirement's state from the decisions that address it and the archived tasks that `closes:` it, with `--waiting` list the drafts alone, and with `--brief` count the closed decisions, the postponements and the frozen findings in place of listing them",
        lines: "Waiting Decisions Defects Requirements Postponed Only The nothing none <id> <count> waiting: next: closed: postponing: by unconnected, paw",
    },
    Command {
        name: "ready",
        run: ready,
        determines: "whether the input a step names is approved and complete",
        by_hand: "read each named artifact's `status:`, and for `implement` that a decision or defect carries a `## Plan` and that a decision's requirements are in a specification's `states:`",
        lines: "paw <id>",
    },
    Command {
        name: "template",
        run: template,
        determines: "which template is in force for a kind",
        by_hand: "look for the kind's file in `.meowpaw/templates/`, then in the unit's `templates/` directory",
        lines: "<path> paw",
    },
    Command {
        name: "show",
        run: show,
        determines: "what one artifact says, what it names and what cites it",
        by_hand: "open the artifact's file, read its front matter relations, and search the record for its identifier to find what cites it",
        lines: "<id> vision <text> Names State Cited <relation>: body: nothing open, closed postponed paw",
    },
    Command {
        name: "brief",
        run: brief,
        determines: "the brief a delegated agent gets for one decision or defect, from the record, its plan and the requirements it names; `--agent <unit>:<agent>` names the agent definition it is written for, and without it the brief names `general-purpose`, the platform's agent the implement step dispatches",
        by_hand: "copy the record's opening, its Decision or What it should do, its Plan and How I will know it was realised, the body of each requirement it names, and the specifications that state them, word for word",
        lines: "agent: record: # from spec: <fence> paw",
    },
    Command {
        name: "index",
        run: index_command,
        determines: "the index table of one kind of artifact",
        by_hand: "list the kind's directory and write one row for each file from its front matter and its conclusion, and with `--write` replace the table between the index's markers",
        lines: "<count> | Amended: By - paw",
    },
    Command {
        name: "new",
        run: new_identifier,
        determines: "the next free identifier of a kind",
        by_hand: "search the whole repository for each `PREFIX-NNNN` of the kind, and take the next multiple of ten above the highest found, or the next one for research and insight",
        lines: "<id> paw",
    },
    Command {
        name: "find",
        run: find,
        determines: "which artifacts carry the words, by identifier, title and conclusion",
        by_hand: "search each artifact's identifier, heading and conclusion, which is the title or for a requirement its statement, for the words, ranked by how many words match",
        lines: "exhaustive: vision <id> artifacts paw",
    },
    Command {
        name: "count",
        run: count_record,
        determines: "how many artifacts of each kind the record holds, by status",
        by_hand: "list each kind's directory and read each file's `status:`",
        lines: "<kind>: identifiers:",
    },
    Command {
        name: "approve",
        run: approve,
        determines: "whether a draft passes the checks, and sets it approved where it does",
        by_hand: "run `paw check` and read what it reports about the draft, then change its `status:` to approved",
        lines: "paw <path>",
    },
    Command {
        name: "withdraw",
        run: withdraw,
        determines: "that an approved requirement is withdrawn by a named decision",
        by_hand: "change the requirement's `status:` to withdrawn and its `revised:` to today, and name the decision and the replacement in its body",
        lines: "paw",
    },
    Command {
        name: "done",
        run: done,
        determines: "that an approved decision or defect is done in a pull request",
        by_hand: "read that a decision carries its `## Plan` or a defect's Closed by names its check, then change its `status:` to done and add `pr:` with the pull request",
        lines: "paw",
    },
    Command {
        name: "upgrade",
        run: upgrade::upgrade,
        determines: "what moving the record to the current form would change, and with `--write` changes it",
        by_hand: "move `epics/` and `tasks/` under `archive/`, store done on each decision and defect whose tasks are all finished, add each open task to its live authority's `## Plan` with `folded-into:` on the task, and remove epic from the profile's gates",
        lines: "paw would archived folded stored removed needs",
    },
    Command {
        name: "onboarding",
        run: onboarding,
        determines: "what an approved onboarding report placed, and removes it",
        by_hand: "check the report is approved and each migrated or superseded destination exists, then delete each file whose outcome is migrated, superseded or discarded",
        lines: "paw before: removed after: <path>",
    },
];

fn print_help(command: &Command) {
    say!("paw {}: {}", command.name, command.determines);
    say!("by hand: {}", command.by_hand);
    say!("lines: {}", command.lines);
}

pub fn main(args: &[String]) -> u8 {
    let (verb, rest) = match args.split_first() {
        Some((verb, rest)) => (verb.as_str(), rest),
        None => ("", &[][..]),
    };
    if verb == "--help" {
        for command in &COMMANDS {
            say!("paw {}: {}", command.name, command.determines);
        }
        return CLEAN;
    }
    match COMMANDS.iter().find(|command| command.name == verb) {
        Some(command) if rest.first().map(String::as_str) == Some("--help") => {
            print_help(command);
            CLEAN
        }
        Some(command) => (command.run)(rest),
        None => {
            eprintln!(
                "usage: paw check [{} | frozen [--base <rev>]] | status | ready <step> <id>... | template <kind> | show <id> | brief <record> [--agent <unit>:<agent>] | index <kind> [--write] | new <kind> [--topic <topic>] | find <word>... | count | approve <id>... | withdraw <id> --by <id> --replaced-by <id>... | done <record> --pr <number> | upgrade [--write] | onboarding remove; paw <subcommand> --help names what a person reads in its place",
                CHECKS.join(" | ")
            );
            USAGE
        }
    }
}

/// Prints the profile's state and its unknown keys on standard error, because
/// standard output is what a step reads, such as a template or an identifier
/// (SPC-1080).
fn report_profile(repository: &Path) {
    for line in profile::report(&profile::read(repository)) {
        eprintln!("{line}");
    }
}

/// The record at the declared root, or the exit code and why it can't be read.
/// What is open in the record of `repository`: the requirements in force that
/// are neither closed nor postponed, and the defects that are not closed. It
/// prints nothing, so a hook's standard output stays its own answer (REQ-3704).
#[cfg(feature = "loop")]
pub(crate) fn open_counts(repository: &Path) -> Result<(usize, usize), String> {
    let layout = load_layout()?;
    let root = record_root(repository)?;
    if !root.is_dir() {
        return Err(format!(
            "the record's root {} doesn't exist",
            root.display()
        ));
    }
    if upgrade::old_form(&root) {
        return Err(OLD_FORM.to_string());
    }
    let record = read_record(layout, repository, &root);
    let mut requirements = 0;
    for requirement in of_kind(&record, "requirement")
        .into_iter()
        .filter(|r| approved(r))
    {
        let id = bare(requirement.id());
        let state = requirement_state(
            &closing_records(&record, id),
            postponed_by(&record, id).as_deref(),
            &violated_by(&record, id),
        );
        if matches!(
            state,
            "in a decision not yet done" | "reopened by a defect" | "named by no decision"
        ) {
            requirements += 1;
        }
    }
    let defects = of_kind(&record, "defect")
        .into_iter()
        .filter(|d| approved(d) && defect_open(d))
        .count();
    Ok((requirements, defects))
}

fn open_record(verb: &str) -> Result<(Record, PathBuf, PathBuf), u8> {
    let repository = profile::repository_root();
    report_profile(&repository);
    let layout = match load_layout() {
        Ok(layout) => layout,
        Err(reason) => {
            say!("paw {verb}: the record was not checked: {reason}");
            return Err(UNCHECKED);
        }
    };
    let root = match record_root(&repository) {
        Ok(root) => root,
        Err(reason) => {
            say!("paw {verb}: {reason}");
            return Err(FOUND);
        }
    };
    if !root.is_dir() {
        say!(
            "paw {verb}: the record's root {} doesn't exist; nothing was checked",
            root.display()
        );
        return Err(FOUND);
    }
    if verb != "upgrade" && upgrade::old_form(&root) {
        say!("paw {verb}: {OLD_FORM}");
        return Err(FOUND);
    }
    let record = read_record(layout, &repository, &root);
    Ok((record, repository, root))
}

fn check(rest: &[String]) -> u8 {
    if rest.first().map(String::as_str) == Some("frozen") {
        return check_frozen(&rest[1..]);
    }
    if rest.len() > 1 {
        eprintln!("usage: paw check [{}]", CHECKS.join(" | "));
        return USAGE;
    }
    let chosen: Vec<&str> = match rest.first() {
        Some(name) if CHECKS.contains(&name.as_str()) => vec![name.as_str()],
        Some(name) => {
            eprintln!(
                "paw check: no check is named {name}; the checks are {}",
                CHECKS.join(", ")
            );
            return USAGE;
        }
        None => CHECKS.to_vec(),
    };
    let (record, repository, root) = match open_record("check") {
        Ok(opened) => opened,
        Err(code) => return code,
    };

    let mut total = 0;
    for check in chosen {
        let mut findings = run_check(check, &record, &root, &repository);
        findings
            .sort_by(|a, b| (&a.shown, a.line, &a.message).cmp(&(&b.shown, b.line, &b.message)));
        for finding in &findings {
            match finding.line {
                Some(line) => say!("{}:{}: {}", finding.shown, line, finding.message),
                None => say!("{}: {}", finding.shown, finding.message),
            }
        }
        if check == "coverage" {
            // Nothing required and nothing missing look the same to a count of
            // findings, so the coverage itself is stated (REQ-3098).
            let in_force: Vec<&Doc> = of_kind(&record, "requirement")
                .into_iter()
                .filter(|r| approved(r))
                .collect();
            let landed = in_force
                .iter()
                .filter(|r| !closing_records(&record, bare(r.id())).is_empty())
                .count();
            let zero = if in_force.is_empty() {
                "; an empty record's coverage is zero, not complete"
            } else {
                ""
            };
            say!(
                "coverage: {landed} of {} requirements in force land in a record{zero}",
                in_force.len()
            );
        }
        say!(
            "{check}: {} finding{}",
            findings.len(),
            if findings.len() == 1 { "" } else { "s" }
        );
        total += findings.len();
    }
    constitution_length(&repository);
    if total == 0 { CLEAN } else { FOUND }
}

/// The constitution's target length in lines (SPC-1220 "Its length").
const CONSTITUTION_TARGET: usize = 200;

/// Prints advice, counted as no finding, when `CLAUDE.md` at the repository's
/// root is over its target (REQ-2734).
fn constitution_length(repository: &Path) {
    let path = repository.join("CLAUDE.md");
    if !path.exists() {
        return;
    }
    match std::fs::read_to_string(&path) {
        Ok(text) => {
            let lines = text.lines().count();
            if lines > CONSTITUTION_TARGET {
                say!(
                    "CLAUDE.md: over its target of {CONSTITUTION_TARGET} lines at {lines}; cut it"
                );
            }
        }
        Err(e) => say!("CLAUDE.md: couldn't count the constitution: {e}"),
    }
}

/// Where the layout is: `MEOW_LAYOUT`, or `lib/layout.toml` in the unit this
/// binary ships in.
fn layout_path() -> Result<PathBuf, String> {
    match std::env::var_os("MEOW_LAYOUT") {
        Some(path) => Ok(PathBuf::from(path)),
        None => {
            let exe = std::env::current_exe().map_err(|e| e.to_string())?;
            // The binary sits at <unit>/bin/<target>/paw.
            let unit = exe.parent().and_then(Path::parent).and_then(Path::parent);
            Ok(unit
                .ok_or("the binary is not inside a unit")?
                .join("lib")
                .join("layout.toml"))
        }
    }
}

/// Records approved at a base revision and changed since, outside what their
/// kind may change (ADR-1170).
fn run_check(check: &str, record: &Record, root: &Path, repository: &Path) -> Vec<Finding> {
    match check {
        "front-matter" => front_matter(record),
        "identifiers" => identifiers(record),
        "relations" => relations(record),
        "index" => index(record, root, repository),
        "coverage" => {
            let mut findings = coverage(record);
            findings.extend(placement(record, root, repository));
            findings
        }
        "shape" => shape(record),
        _ => rules(record),
    }
}

/// Whether the record's root is kept by version control: inside a work tree
/// and not ignored by it.
fn under_version_control(root: &Path) -> bool {
    let git = |args: &[&str]| {
        profile::reading_git()
            .args(args)
            .current_dir(root)
            .output()
            .ok()
    };
    let inside = git(&["rev-parse", "--is-inside-work-tree"]).is_some_and(|o| o.status.success());
    let ignored = git(&["check-ignore", "-q", "."]).is_some_and(|o| o.status.success());
    inside && !ignored
}

/// Each record that closes a requirement or still works on it: an approved or
/// done decision addressing it, and a done archived task closing it
/// (REQ-3680), each with its mark, `x` done and anything else open.
fn closing_records(record: &Record, id: &str) -> Vec<(String, char)> {
    let mut out = Vec::new();
    for decision in of_kind(record, "decision") {
        if !approved(decision) || !requirements_in(record, decision.value("addresses")).contains(id)
        {
            continue;
        }
        let mark = if bare(decision.value("status")) == "done" {
            'x'
        } else {
            ' '
        };
        out.push((bare(decision.id()).to_string(), mark));
    }
    for task in of_kind(record, "task") {
        if bare(task.value("status")) == "done"
            && requirements_in(record, task.value("closes")).contains(id)
        {
            out.push((bare(task.id()).to_string(), 'x'));
        }
    }
    out.sort();
    out
}

/// Whether a defect is still open. It closes by storing `done` (REQ-3678).
fn defect_open(defect: &Doc) -> bool {
    matches!(bare(defect.value("status")), "draft" | "approved")
}

/// The open defects naming a requirement in `violates`.
fn violated_by(record: &Record, id: &str) -> Vec<String> {
    of_kind(record, "defect")
        .into_iter()
        .filter(|d| {
            d.value("violates").contains(id)
                && requirements_in(record, d.value("violates")).contains(id)
        })
        .filter(|d| defect_open(d))
        .map(|d| bare(d.id()).to_string())
        .collect()
}

/// A requirement's observed state (REQ-0584), derived from the records that
/// name it and the defects that violate it, with nothing after closed
/// (REQ-3602, REQ-3610, REQ-3680).
fn requirement_state(
    records: &[(String, char)],
    postponed: Option<&str>,
    violated: &[String],
) -> &'static str {
    if !violated.is_empty() {
        "reopened by a defect"
    } else if records.iter().any(|(_, mark)| *mark != 'x') {
        "in a decision not yet done"
    } else if !records.is_empty() {
        "closed"
    } else if postponed.is_some() {
        "postponed"
    } else {
        "named by no decision"
    }
}

/// The approved decision that postpones a requirement, if one does (ADR-1330).
fn postponed_by(record: &Record, id: &str) -> Option<String> {
    of_kind(record, "decision")
        .into_iter()
        .filter(|d| approved(d))
        .filter(|d| requirements_in(record, d.value("postpones")).contains(id))
        .map(|d| bare(d.id()).to_string())
        .min()
}

fn check_frozen(rest: &[String]) -> u8 {
    let base = match rest {
        [] => "HEAD".to_string(),
        [flag, rev] if flag == "--base" => rev.clone(),
        _ => {
            eprintln!("usage: paw check frozen [--base <rev>]");
            return USAGE;
        }
    };
    let (record, repository, _) = match open_record("check") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let authority =
        Regex::new(r"(?:Amended|Corrected) by (?:ADR|BUG|EPC)-\d{4}").expect("authority pattern");
    let mut findings = Vec::new();
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else {
            continue;
        };
        // A living document describes the present and is rewritten freely.
        let own_index = kind.index.as_deref() == Some(doc.relative.as_str());
        if doc.is_index
            || own_index
            || kind.statuses.iter().any(|s| s == "live")
            || Path::new(&doc.shown).is_absolute()
        {
            continue;
        }
        let Ok(out) = profile::reading_git()
            .args(["show", &format!("{base}:{}", doc.shown)])
            .current_dir(&repository)
            .output()
        else {
            continue;
        };
        if !out.status.success() {
            continue;
        }
        let before = String::from_utf8_lossy(&out.stdout).into_owned();
        if before == doc.text {
            continue;
        }
        let old = Doc {
            path: doc.path.clone(),
            relative: doc.relative.clone(),
            shown: doc.shown.clone(),
            fields: parse_front_matter(&before),
            text: before.clone(),
            kind: doc.kind,
            is_index: false,
        };
        let was_done = bare(old.value("status")) == "done";
        if bare(old.value("status")) != "approved" && !was_done {
            continue;
        }
        if matches!(bare(doc.value("status")), "withdrawn" | "superseded") {
            continue;
        }
        let was: BTreeSet<&str> = before.lines().collect();
        if doc
            .text
            .lines()
            .any(|line| !was.contains(line) && authority.is_match(line))
        {
            continue;
        }
        // Removing a field or a section the record retired is a change of
        // format and not of what was approved (ADR-2300). Only what the new
        // text no longer carries is set aside, so text added or changed under
        // a retired heading is a change like any other, and a record that
        // never carried one is compared as it is.
        let carried = retired_in(&record.layout, &before);
        let gone: BTreeSet<String> = carried
            .difference(&retired_in(&record.layout, &doc.text))
            .cloned()
            .collect();
        let (before, after) = if gone.is_empty() {
            (before.clone(), doc.text.clone())
        } else {
            let pair = (
                without_retired(&record.layout, &before, &gone),
                without_retired(&record.layout, &doc.text, &gone),
            );
            if pair.0 == pair.1 {
                continue;
            }
            pair
        };
        let closing = bare(doc.value("status")) == "done";
        let allowed = matches!(kind.name.as_str(), "decision" | "defect")
            && !was_done
            && work_part(&before, closing) == work_part(&after, closing);
        if !allowed {
            findings.push(format!(
                "{}: approved at {base}, and changed since without a line naming its authority; a change to an approved record invalidates its approval",
                doc.shown
            ));
        }
    }
    findings.extend(hash_citations(&record, &repository, &base));
    findings.sort();
    for finding in &findings {
        say!("{finding}");
    }
    say!(
        "frozen: {} finding{}",
        findings.len(),
        if findings.len() == 1 { "" } else { "s" }
    );
    if findings.is_empty() { CLEAN } else { FOUND }
}

/// Lines added since the base that cite a commit hash as the revision a check
/// ran at. A squash rebuilds the commit, so the hash stops resolving on the
/// trunk, and the pull request that carried the change is what a record cites
/// (REQ-3176). Only added lines are read, so a record keeps what it said.
fn hash_citations(record: &Record, repository: &Path, base: &str) -> Vec<String> {
    let cited = Regex::new(r"\b(?:at|revision)\s+`?([0-9a-f]{7,40})`?(?:[^0-9A-Za-z]|$)")
        .expect("citation pattern");
    let mut out = Vec::new();
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else {
            continue;
        };
        if doc.is_index
            || kind.statuses.iter().any(|s| s == "live")
            || Path::new(&doc.shown).is_absolute()
        {
            continue;
        }
        let before = profile::reading_git()
            .args(["show", &format!("{base}:{}", doc.shown)])
            .current_dir(repository)
            .output()
            .ok()
            .filter(|o| o.status.success())
            .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
            .unwrap_or_default();
        let was: BTreeSet<&str> = before.lines().collect();
        for (i, line) in doc.text.lines().enumerate().skip(body_start(doc)) {
            if was.contains(line) {
                continue;
            }
            for c in cited.captures_iter(line) {
                let hash = &c[1];
                if hash.chars().any(|ch| ch.is_ascii_digit())
                    && hash.chars().any(|ch| ch.is_ascii_alphabetic())
                {
                    out.push(format!("{}:{}: cites the commit {hash} as a revision; cite the pull request that carried it, because a squash rebuilds the commit", doc.shown, i + 1));
                }
            }
        }
    }
    out
}

/// The fence a line opens or closes: its mark and the length of its run. An
/// opening line is a run of three or more backticks or tildes, indented at
/// most three spaces, followed at most by an info string, which for backticks
/// holds no backtick. A prose line that starts with an inline span, such as
/// three backticks round a word, isn't one.
fn fence_of(line: &str) -> Option<(char, usize, bool)> {
    let indent = line.len() - line.trim_start_matches(' ').len();
    let rest = line.trim_start_matches(' ');
    let mark = rest.chars().next().filter(|c| *c == '`' || *c == '~')?;
    let run = rest.chars().take_while(|c| *c == mark).count();
    let after = &rest[run..];
    if indent > 3 || run < 3 || (mark == '`' && after.contains('`')) {
        return None;
    }
    Some((mark, run, after.trim().is_empty()))
}

/// Each line of a text with whether it sits in front matter or fenced code,
/// and the level-two heading it opens where it opens one. A fence closes on a
/// bare run of its own mark at least as long as the one that opened it.
fn outline(text: &str) -> Vec<(&str, bool, bool, Option<&str>)> {
    let mut out = Vec::new();
    let (mut rules, mut fence): (u8, Option<(char, usize)>) = (0, None);
    let front = text.starts_with("---\n") || text.starts_with("---\r\n");
    for line in text.lines() {
        let bare = line.trim_end();
        if front && rules < 2 && bare == "---" {
            rules += 1;
            out.push((line, true, false, None));
            continue;
        }
        if front && rules == 1 {
            out.push((line, true, false, None));
            continue;
        }
        match (fence, fence_of(bare)) {
            (None, Some((mark, run, _))) => {
                fence = Some((mark, run));
                out.push((line, false, true, None));
            }
            (Some((open, length)), Some((mark, run, true))) if open == mark && run >= length => {
                fence = None;
                out.push((line, false, true, None));
            }
            (Some(_), _) => out.push((line, false, true, None)),
            (None, None) => out.push((line, false, false, bare.strip_prefix("## ").map(str::trim))),
        }
    }
    out
}

/// Whether a front matter line continues the field above it: indented, or an
/// item of a block list.
fn continues(line: &str) -> bool {
    line.starts_with(' ') || line.starts_with('\t') || line == "-" || line.starts_with("- ")
}

/// The retired section a heading names: the name itself, or the name
/// followed by more words, as in "Verified, and closed with a criterion
/// unmet".
fn retired_section<'a>(layout: &'a Layout, heading: &str) -> Option<(&'a str, &'a str)> {
    layout.retired_sections.iter().find_map(|(name, why)| {
        let rest = heading.strip_prefix(name.as_str())?;
        let next = rest.chars().next();
        (next.is_none() || next.is_some_and(|c| !c.is_alphanumeric()))
            .then_some((name.as_str(), why.as_str()))
    })
}

/// A record's text without what may change after approval: the named
/// sections, each read from its first heading to the next, and the named
/// front matter fields with their continuation lines. Fenced code is text,
/// never a heading.
fn frozen_text(text: &str, sections: &[&str], fields: &[&str]) -> String {
    let mut out = Vec::new();
    let mut seen = BTreeSet::new();
    let (mut open, mut skipping) = (false, false);
    for (line, front, _, heading) in outline(text) {
        if front {
            if !continues(line) {
                let key = line.split(':').next().unwrap_or("");
                skipping = fields.contains(&key);
            }
            if skipping {
                continue;
            }
        } else if let Some(heading) = heading {
            // Only the first section of a name is free, so a second one
            // added to hold new text is part of what is frozen.
            open = sections.contains(&heading) && seen.insert(heading.to_string());
        }
        if !open {
            out.push(line);
        }
    }
    out.join("\n")
}

/// A decision's or defect's text without what may change before it is done:
/// its plan, the marks a defect kept, what closed it, the tracker's mapping,
/// its pull request, its revision date and, where it closes, its status
/// (REQ-3676).
fn work_part(text: &str, closing: bool) -> String {
    let fields: &[&str] = if closing {
        &["status", "issue", "projected", "tracked", "pr", "revised"]
    } else {
        &["issue", "projected", "tracked", "pr", "revised"]
    };
    frozen_text(text, &["Plan", "Tasks", "Closed by"], fields)
}

/// The fields and sections the layout retired that a record carries.
fn retired_in(layout: &Layout, text: &str) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    for (line, front, _, heading) in outline(text) {
        let key = line.split(':').next().unwrap_or("");
        if front && !continues(line) && layout.retired_fields.contains_key(key) {
            out.insert(key.to_string());
        }
        if let Some((name, _)) = heading.and_then(|h| retired_section(layout, h)) {
            out.insert(name.to_string());
        }
    }
    out
}

/// A record's text without the named retired fields and sections, and without
/// its revision date, which a migration moves. A removed section takes the
/// blank lines round it, and nothing else in the text moves.
fn without_retired(layout: &Layout, text: &str, gone: &BTreeSet<String>) -> String {
    let mut out: Vec<&str> = Vec::new();
    let (mut retired, mut skipping) = (false, false);
    for (line, front, _, heading) in outline(text) {
        if front {
            if !continues(line) {
                let key = line.split(':').next().unwrap_or("");
                skipping = gone.contains(key) || key == "revised";
            }
            if skipping {
                continue;
            }
        } else if let Some(heading) = heading {
            let was = retired;
            retired = retired_section(layout, heading).is_some_and(|(name, _)| gone.contains(name));
            if retired || was {
                while out.last().is_some_and(|l| l.trim().is_empty()) {
                    out.pop();
                }
                if !retired {
                    out.push("");
                }
            }
        }
        if !retired {
            out.push(line.trim_end_matches('\r'));
        }
    }
    while out.last().is_some_and(|l| l.trim().is_empty()) {
        out.pop();
    }
    out.join("\n")
}

/// The layout from `MEOW_LAYOUT`, or from the unit this binary ships in.
pub(crate) fn load_layout() -> Result<Layout, String> {
    let path = layout_path()?;
    let text = std::fs::read_to_string(&path).map_err(|e| format!("{}: {e}", path.display()))?;
    let data: toml::Table = text
        .parse()
        .map_err(|e| format!("{}: {e}", path.display()))?;
    let strings = |table: &toml::Table, key: &str| -> Vec<String> {
        table
            .get(key)
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|v| v.as_str().map(str::to_string))
                    .collect()
            })
            .unwrap_or_default()
    };
    let string = |table: &toml::Table, key: &str| {
        table.get(key).and_then(|v| v.as_str()).map(str::to_string)
    };
    let mut kinds = Vec::new();
    for entry in data
        .get("kind")
        .and_then(|v| v.as_array())
        .into_iter()
        .flatten()
    {
        let Some(table) = entry.as_table() else {
            continue;
        };
        kinds.push(Kind {
            name: string(table, "name").unwrap_or_default(),
            artifact: string(table, "artifact").unwrap_or_default(),
            prefix: string(table, "prefix"),
            dir: string(table, "dir"),
            file: string(table, "file"),
            fields: strings(table, "fields"),
            optional_fields: strings(table, "optional_fields"),
            statuses: strings(table, "statuses"),
            index: string(table, "index"),
            sections: strings(table, "sections"),
            draft_sections: strings(table, "draft_sections"),
            first_section: string(table, "first_section"),
            required_values: strings(table, "required_values"),
            forbidden_fields: strings(table, "forbidden_fields"),
            rules: strings(table, "rules"),
            draft_rules: strings(table, "draft_rules"),
            outranks: Vec::new(),
            archived: table
                .get("archived")
                .and_then(|v| v.as_bool())
                .unwrap_or(false),
        });
    }
    let retired = |key: &str| -> BTreeMap<String, String> {
        data.get("retired")
            .and_then(|r| r.get(key))
            .and_then(|t| t.as_table())
            .map(|t| {
                t.iter()
                    .map(|(k, v)| (k.clone(), v.as_str().unwrap_or_default().to_string()))
                    .collect()
            })
            .unwrap_or_default()
    };
    Ok(Layout {
        fields: strings(&data, "fields"),
        relations: strings(&data, "relations"),
        index_name: string(&data, "index_name").unwrap_or_else(|| "README.md".into()),
        kinds,
        retired_fields: retired("fields"),
        retired_statuses: retired("statuses"),
        retired_sections: retired("sections"),
        history_phrases: strings(&data, "history_phrases"),
    })
}

fn record_root(repository: &Path) -> Result<PathBuf, String> {
    Ok(repository.join(declared_root(repository)?))
}

/// The record's root as the profile declares it, `[record] root`, or
/// `project`.
pub(crate) fn declared_root(repository: &Path) -> Result<String, String> {
    let declared = match profile::read(repository) {
        Profile::Parsed(data, _) => data
            .get("record")
            .and_then(|r| r.as_table())
            .and_then(|r| r.get("root"))
            .and_then(|r| r.as_str())
            .map(str::to_string),
        Profile::Unparseable(reason) => return Err(format!("the profile can't be read: {reason}")),
        Profile::Absent => None,
    };
    Ok(declared.unwrap_or_else(|| "project".into()))
}

fn markdown_under(dir: &Path, leave_out: Option<&Path>, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    let mut entries: Vec<_> = entries.filter_map(Result::ok).map(|e| e.path()).collect();
    entries.sort();
    for path in entries {
        let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        if path.is_dir() {
            if name.starts_with('.') || SKIP.contains(&name) || Some(path.as_path()) == leave_out {
                continue;
            }
            markdown_under(&path, leave_out, out);
        } else if name.ends_with(".md") {
            out.push(path);
        }
    }
}

/// A top-level key starts a field; an indented line continues its value, as a
/// flowed list does.
fn parse_front_matter(text: &str) -> Option<Vec<Field>> {
    let rest = text.strip_prefix("---\n")?;
    let end = rest
        .find("\n---\n")
        .map(|i| i + 1)
        .or_else(|| rest.strip_suffix("\n---").map(str::len))?;
    let mut fields: Vec<Field> = Vec::new();
    for (i, line) in rest[..end].lines().enumerate() {
        let continued = line.starts_with(' ') || line.starts_with('\t');
        match (continued, line.split_once(':')) {
            (false, Some((key, value))) => fields.push(Field {
                key: key.trim().to_string(),
                value: value.trim().to_string(),
                line: i + 2,
            }),
            _ => {
                if let Some(last) = fields.last_mut() {
                    last.value.push(' ');
                    last.value.push_str(line.trim());
                }
            }
        }
    }
    Some(fields)
}

fn shown(path: &Path, repository: &Path) -> String {
    let repository = repository
        .canonicalize()
        .unwrap_or_else(|_| repository.to_path_buf());
    let path = path.canonicalize().unwrap_or_else(|_| path.to_path_buf());
    match path.strip_prefix(&repository) {
        Ok(relative) => relative.display().to_string(),
        Err(_) => path.display().to_string(),
    }
}

fn read_doc(path: PathBuf, repository: &Path) -> Doc {
    let text = std::fs::read_to_string(&path).unwrap_or_default();
    let fields = parse_front_matter(&text);
    let shown = shown(&path, repository);
    Doc {
        path,
        relative: String::new(),
        shown,
        text,
        fields,
        kind: None,
        is_index: false,
    }
}

/// The profile's file, as a declaration's findings name it.
const PROFILE_SHOWN: &str = ".meowpaw/profile.toml";

/// The template directory a declared kind's template sits under (REQ-0668).
const TEMPLATES_DIR: &str = ".meowpaw/templates/";

/// The kinds `[record.kinds.<name>]` declares, each held to every general
/// obligation a built-in kind carries, and a finding for each declaration that
/// lacks a fact or names a thing that doesn't exist. A kind whose prefix is
/// unusable is left out, because no file can be told to belong to it
/// (REQ-0666, REQ-0668, REQ-0670).
fn declared_kinds(repository: &Path, layout: &Layout) -> (Vec<Kind>, Vec<Finding>) {
    let mut kinds: Vec<Kind> = Vec::new();
    let mut findings = Vec::new();
    let Profile::Parsed(data, _) = profile::read(repository) else {
        return (kinds, findings);
    };
    let Some(declared) = data
        .get("record")
        .and_then(|r| r.get("kinds"))
        .and_then(|k| k.as_table())
    else {
        return (kinds, findings);
    };
    let prefix_shape = Regex::new(r"^[A-Z][A-Z0-9]*$").expect("prefix pattern");
    let finding = |message: String| Finding {
        shown: PROFILE_SHOWN.into(),
        line: None,
        message,
    };
    let mut outranks: Vec<(String, Vec<String>)> = Vec::new();
    for (name, declaration) in declared {
        let Some(declaration) = declaration.as_table() else {
            findings.push(finding(format!(
                "the kind {name} is not a table; declare it as [record.kinds.{name}]"
            )));
            continue;
        };
        if layout.kinds.iter().any(|k| &k.name == name) {
            findings.push(finding(format!(
                "the kind {name} is the name of a kind the harness ships, and a declaration can't redefine it"
            )));
            continue;
        }
        let text = |key: &str| declaration.get(key).and_then(|v| v.as_str());
        let lifetime = match text("lifetime") {
            Some("record") => Some("record"),
            Some("living") => Some("living"),
            Some(other) => {
                findings.push(finding(format!(
                    "the kind {name} declares lifetime {other}, where a kind is record or living"
                )));
                None
            }
            None => {
                findings.push(finding(format!(
                    "the kind {name} declares no lifetime; state record or living"
                )));
                None
            }
        };
        match text("template") {
            None => findings.push(finding(format!(
                "the kind {name} declares no template; state a path under {TEMPLATES_DIR}"
            ))),
            Some(template) => {
                if !template.starts_with(TEMPLATES_DIR) || template.contains("..") {
                    findings.push(finding(format!(
                        "the kind {name} declares the template {template}, which is not a path under {TEMPLATES_DIR}"
                    )));
                } else if !repository.join(template).is_file() {
                    findings.push(finding(format!(
                        "the kind {name} declares the template {template}, which doesn't exist"
                    )));
                }
            }
        }
        let list: Vec<String> = declaration
            .get("outranks")
            .and_then(|v| v.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|v| v.as_str().map(str::to_string))
                    .collect()
            })
            .unwrap_or_default();
        outranks.push((name.clone(), list));
        let Some(prefix) = text("prefix") else {
            findings.push(finding(format!(
                "the kind {name} declares no prefix; state the identifier's prefix"
            )));
            continue;
        };
        if !prefix_shape.is_match(prefix) {
            findings.push(finding(format!(
                "the kind {name} declares the prefix {prefix}, which is not capital letters and digits"
            )));
            continue;
        }
        let taken = layout
            .kinds
            .iter()
            .chain(&kinds)
            .find(|k| k.prefix.as_deref() == Some(prefix));
        if let Some(other) = taken {
            findings.push(finding(format!(
                "the kind {name} declares the prefix {prefix}, which the kind {} already uses",
                other.name
            )));
            continue;
        }
        let statuses: &[&str] = if lifetime == Some("living") {
            &["live"]
        } else {
            &["draft", "approved", "withdrawn", "rejected", "superseded"]
        };
        kinds.push(Kind {
            name: name.clone(),
            artifact: name.clone(),
            prefix: Some(prefix.to_string()),
            dir: Some(name.clone()),
            file: None,
            fields: Vec::new(),
            optional_fields: Vec::new(),
            statuses: statuses.iter().map(|s| s.to_string()).collect(),
            index: None,
            sections: Vec::new(),
            draft_sections: Vec::new(),
            first_section: None,
            required_values: Vec::new(),
            forbidden_fields: Vec::new(),
            rules: Vec::new(),
            draft_rules: Vec::new(),
            outranks: Vec::new(),
            archived: false,
        });
    }
    for (name, list) in outranks {
        for entry in &list {
            let known = layout.kinds.iter().any(|k| &k.name == entry)
                || declared.contains_key(entry.as_str());
            if !known || *entry == name {
                findings.push(finding(format!(
                    "the kind {name} outranks {entry}, which names no other kind"
                )));
            }
        }
        if let Some(kind) = kinds.iter_mut().find(|k| k.name == name) {
            kind.outranks = list;
        }
    }
    (kinds, findings)
}

fn read_record(mut layout: Layout, repository: &Path, root: &Path) -> Record {
    let (declared, declarations) = declared_kinds(repository, &layout);
    layout.kinds.extend(declared);
    let mut paths = Vec::new();
    markdown_under(root, None, &mut paths);
    let mut docs = Vec::new();
    for path in paths {
        let relative = path
            .strip_prefix(root)
            .unwrap_or(&path)
            .to_string_lossy()
            .replace('\\', "/");
        let mut doc = read_doc(path.clone(), repository);
        doc.relative = relative.clone();
        let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        let parent = relative.rsplit_once('/').map(|(dir, _)| dir).unwrap_or("");
        doc.is_index = name == layout.index_name;
        doc.kind = layout.kinds.iter().position(|kind| {
            kind.file.as_deref() == Some(relative.as_str())
                || (kind.dir.as_deref() == Some(parent) && !doc.is_index)
        });
        docs.push(doc);
    }

    let root_canonical = root.canonicalize().unwrap_or_else(|_| root.to_path_buf());
    let mut others = Vec::new();
    markdown_under(repository, Some(&root_canonical), &mut others);
    let outside = others
        .into_iter()
        .filter(|p| {
            !p.canonicalize()
                .map(|c| c.starts_with(&root_canonical))
                .unwrap_or(false)
        })
        .map(|p| read_doc(p, repository))
        .collect();

    let prefixes: Vec<&str> = layout
        .kinds
        .iter()
        .filter_map(|k| k.prefix.as_deref())
        .collect();
    let ids = Regex::new(&format!(r"\b(?:{})-\d{{4}}\b", prefixes.join("|")))
        .expect("identifier pattern");
    Record {
        layout,
        declarations,
        docs,
        outside,
        ids,
    }
}

fn line_of(text: &str, offset: usize) -> usize {
    text[..offset].matches('\n').count() + 1
}

fn today() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    // Howard Hinnant's civil-from-days, so the date needs no calendar crate.
    let z = (secs / 86_400) as i64 + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1_460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let day = doy - (153 * mp + 2) / 5 + 1;
    let month = if mp < 10 { mp + 3 } else { mp - 9 };
    let year = yoe + era * 400 + i64::from(month <= 2);
    format!("{year:04}-{month:02}-{day:02}")
}

fn bare(value: &str) -> &str {
    let value = value.split(" #").next().unwrap_or(value).trim();
    value.trim_matches('"').trim_matches('\'')
}

fn front_matter(record: &Record) -> Vec<Finding> {
    let date = Regex::new(r"^\d{4}-\d{2}-\d{2}$").expect("date pattern");
    let today = today();
    let mut out = Vec::new();
    for found in &record.declarations {
        out.push(Finding {
            shown: found.shown.clone(),
            line: found.line,
            message: found.message.clone(),
        });
    }
    for kind in &record.layout.kinds {
        let reused = kind
            .statuses
            .iter()
            .filter(|s| record.layout.retired_statuses.contains_key(*s));
        let reused = reused.chain(
            kind.fields
                .iter()
                .filter(|f| record.layout.retired_fields.contains_key(*f)),
        );
        for name in reused {
            out.push(Finding {
                shown: "the layout".into(),
                line: None,
                message: format!("the kind {} declares {name}, a retired name", kind.name),
            });
        }
    }
    for doc in record.docs.iter().filter(|d| !d.is_index) {
        let Some(fields) = &doc.fields else {
            out.push(Finding::at(doc, None, "no front matter".into()));
            continue;
        };
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else {
            out.push(Finding::at(
                doc,
                None,
                "an artifact of no known kind".into(),
            ));
            continue;
        };
        for key in record.layout.fields.iter().chain(&kind.fields) {
            if !fields.iter().any(|f| &f.key == key) {
                out.push(Finding::at(doc, None, format!("front matter has no {key}")));
            }
        }
        for key in &kind.forbidden_fields {
            if let Some(field) = doc.field(key) {
                out.push(Finding::at(
                    doc,
                    Some(field.line),
                    format!("carries {key}, which a {} never does", kind.name),
                ));
            }
        }
        for key in &kind.required_values {
            if let Some(field) = doc.field(key) {
                let value = bare(&field.value)
                    .trim_matches(|c: char| c == '[' || c == ']' || c.is_whitespace());
                if value.is_empty() {
                    out.push(Finding::at(
                        doc,
                        Some(field.line),
                        format!("{key} is empty, and a {} must fill it", kind.name),
                    ));
                }
            }
        }
        if let Some(field) = doc.field("artifact")
            && bare(&field.value) != kind.artifact
        {
            out.push(Finding::at(
                doc,
                Some(field.line),
                format!(
                    "artifact is {}, where a {} is {}",
                    bare(&field.value),
                    kind.name,
                    kind.artifact
                ),
            ));
        }
        for field in fields {
            if let Some(why) = record.layout.retired_fields.get(&field.key) {
                out.push(Finding::at(
                    doc,
                    Some(field.line),
                    format!("carries {}, a retired field: {why}", field.key),
                ));
            }
        }
        if let Some(field) = doc.field("status") {
            let status = bare(&field.value);
            if let Some(why) = record.layout.retired_statuses.get(status) {
                out.push(Finding::at(
                    doc,
                    Some(field.line),
                    format!("status {status} is retired: {why}"),
                ));
            } else if !kind.statuses.iter().any(|s| s == status) {
                out.push(Finding::at(
                    doc,
                    Some(field.line),
                    format!(
                        "status {status} is not one a {} stores: {}",
                        kind.name,
                        kind.statuses.join(", ")
                    ),
                ));
            }
        }
        if let Some(field) = doc.field("revised") {
            let revised = bare(&field.value);
            if !date.is_match(revised) {
                out.push(Finding::at(
                    doc,
                    Some(field.line),
                    format!("revised is not a date: {revised}"),
                ));
            } else if revised > today.as_str() {
                out.push(Finding::at(
                    doc,
                    Some(field.line),
                    format!("revised is in the future: {revised}"),
                ));
            }
        }
    }
    out
}

/// Identifier to the document that carries it, first one wins.
fn known(record: &Record) -> BTreeMap<String, &Doc> {
    let mut out = BTreeMap::new();
    for doc in &record.docs {
        if let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k])
            && kind.prefix.is_some()
            && !doc.id().is_empty()
        {
            out.entry(bare(doc.id()).to_string()).or_insert(doc);
        }
    }
    out
}

fn identifiers(record: &Record) -> Vec<Finding> {
    let mut out = Vec::new();
    // A project has one vision, wherever a second would sit (REQ-0614).
    let mut visions = record
        .docs
        .iter()
        .chain(&record.outside)
        .filter(|d| bare(d.value("artifact")) == "vision" && bare(d.id()) == "vision");
    if let Some(first) = visions.next() {
        for other in visions {
            out.push(Finding::at(
                other,
                None,
                format!("vision is also allocated to {}", first.shown),
            ));
        }
    }
    let mut seen: BTreeMap<String, &Doc> = BTreeMap::new();
    let mut name_patterns: BTreeMap<&str, Regex> = BTreeMap::new();
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else {
            continue;
        };
        let Some(prefix) = &kind.prefix else { continue };
        let name = doc.path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        let named = name_patterns.entry(prefix.as_str()).or_insert_with(|| {
            Regex::new(&format!(r"^({prefix}-\d{{4}})-[a-z0-9-]+\.md$")).expect("name pattern")
        });
        let Some(from_name) = named.captures(name).map(|c| c[1].to_string()) else {
            out.push(Finding::at(
                doc,
                None,
                format!("the name doesn't have the form {prefix}-NNNN-<slug>.md"),
            ));
            continue;
        };
        let declared = bare(doc.id());
        if declared != from_name {
            let line = doc.field("id").map(|f| f.line);
            out.push(Finding::at(
                doc,
                line,
                format!(
                    "declares id {}, where its name says {from_name}",
                    if declared.is_empty() {
                        "(none)"
                    } else {
                        declared
                    }
                ),
            ));
        }
        match seen.get(&from_name) {
            Some(first) => out.push(Finding::at(
                doc,
                None,
                format!("{from_name} is also allocated to {}", first.shown),
            )),
            None => {
                seen.insert(from_name, doc);
            }
        }
    }
    let known = known(record);
    for doc in record.docs.iter().chain(&record.outside) {
        let mut cited = BTreeSet::new();
        for found in record
            .ids
            .find_iter(&doc.text)
            .filter(|m| m.as_str().starts_with("REQ-"))
        {
            if !known.contains_key(found.as_str()) && cited.insert(found.as_str()) {
                out.push(Finding::at(
                    doc,
                    Some(line_of(&doc.text, found.start())),
                    format!("cites {}, which has no file", found.as_str()),
                ));
            }
        }
    }
    out
}

fn relations(record: &Record) -> Vec<Finding> {
    let known = known(record);
    let link = Regex::new(r"\]\((?:<([^>]+)>|([^)\s]+))").expect("link pattern");
    let span = Regex::new(r"`[^`]*`").expect("code span pattern");
    let mut out = Vec::new();
    for doc in &record.docs {
        for key in &record.layout.relations {
            let Some(field) = doc.field(key) else {
                continue;
            };
            // A relation is bare identifiers, because a link carries a path and
            // a path changes when a repository is reorganised.
            let rest = record.ids.replace_all(bare(&field.value), "");
            if rest
                .chars()
                .any(|c| !(c.is_whitespace() || c == ',' || c == '[' || c == ']'))
            {
                out.push(Finding::at(
                    doc,
                    Some(field.line),
                    format!(
                        "{key} holds more than bare identifiers: {}",
                        bare(&field.value)
                    ),
                ));
            }
            for found in record.ids.find_iter(&field.value) {
                if !known.contains_key(found.as_str()) {
                    out.push(Finding::at(
                        doc,
                        Some(field.line),
                        format!("{key} names {}, which has no file", found.as_str()),
                    ));
                }
            }
        }
        // Only a draft or a living artifact can be revised to clear a suspect
        // citation; an approved one is frozen, so `show` marks it (ADR-1470).
        if is_draft(doc) || bare(doc.value("status")) == "live" {
            for (field, id, why) in suspects(record, &known, doc) {
                let revised = bare(doc.value("revised"));
                let message = if why.starts_with("revised") {
                    format!(
                        "{} {id}, {why}, after this record's {revised}, so the citation is suspect",
                        field.key
                    )
                } else {
                    format!("{} {id} {why}, so the citation is suspect", field.key)
                };
                out.push(Finding::at(doc, Some(field.line), message));
            }
        }
        // Only a draft's body is read: an approved record may name an identifier
        // that has no file on purpose, as a defect listing what is missing does.
        if is_draft(doc) {
            let mut fenced = false;
            for (i, text) in doc.text.lines().enumerate().skip(body_start(doc)) {
                if text.trim_start().starts_with("```") {
                    fenced = !fenced;
                }
                if fenced {
                    continue;
                }
                let prose = span.replace_all(text, "");
                for found in record.ids.find_iter(&prose) {
                    if !known.contains_key(found.as_str()) {
                        out.push(Finding::at(
                            doc,
                            Some(i + 1),
                            format!("names {}, which has no file", found.as_str()),
                        ));
                    }
                }
            }
        }
        let dir = doc.path.parent().unwrap_or(Path::new("."));
        for found in link.captures_iter(&doc.text) {
            let target = found
                .get(1)
                .or(found.get(2))
                .map(|m| m.as_str())
                .unwrap_or("");
            if target.starts_with("http://")
                || target.starts_with("https://")
                || target.starts_with('#')
                || target.starts_with("mailto:")
            {
                continue;
            }
            let file = target.split('#').next().unwrap_or("");
            if !file.is_empty() && !dir.join(file).exists() {
                let line = line_of(&doc.text, found.get(0).map(|m| m.start()).unwrap_or(0));
                out.push(Finding::at(
                    doc,
                    Some(line),
                    format!("links to {target}, which doesn't exist"),
                ));
            }
        }
    }
    out.extend(order_conflicts(record));
    // REQ-3900: an approved requirement names an approved decision that
    // addresses or postpones it.
    let active = |status: &str| status == "approved" || status == "done";
    let provided = |id: &str| {
        of_kind(record, "decision").iter().any(|d| {
            active(bare(d.value("status")))
                && (requirements_in(record, d.value("addresses")).contains(id)
                    || requirements_in(record, d.value("postpones")).contains(id))
        })
    };
    for requirement in of_kind(record, "requirement") {
        let id = bare(requirement.id());
        if !active(bare(requirement.value("status"))) || provided(id) {
            continue;
        }
        out.push(Finding::at(
            requirement,
            None,
            format!("{id} is in force and names no approved decision that addresses or postpones it (REQ-3900)"),
        ));
    }
    out
}

/// Each pair of artifacts, one of a kind that outranks the other's, that cite
/// each other and state different values for one field of their own. The
/// fields every artifact carries and the relations are left out, because they
/// describe the artifact and not what it claims. The pair is reported and
/// never settled (REQ-0667).
fn order_conflicts(record: &Record) -> Vec<Finding> {
    let general: BTreeSet<&str> = record
        .layout
        .fields
        .iter()
        .chain(&record.layout.relations)
        .map(String::as_str)
        .collect();
    let cites = |doc: &Doc, id: &str| record.ids.find_iter(&doc.text).any(|m| m.as_str() == id);
    let mut out = Vec::new();
    for (k, kind) in record.layout.kinds.iter().enumerate() {
        for lower in &kind.outranks {
            let Some(l) = record.layout.kinds.iter().position(|x| &x.name == lower) else {
                continue;
            };
            for high in record
                .docs
                .iter()
                .filter(|d| d.kind == Some(k) && !d.is_index)
            {
                for low in record
                    .docs
                    .iter()
                    .filter(|d| d.kind == Some(l) && !d.is_index)
                {
                    let (a, b) = (bare(high.id()), bare(low.id()));
                    if a.is_empty() || b.is_empty() || !cites(high, b) || !cites(low, a) {
                        continue;
                    }
                    for field in high.fields.iter().flatten() {
                        if general.contains(field.key.as_str()) {
                            continue;
                        }
                        let Some(other) = low.field(&field.key) else {
                            continue;
                        };
                        if bare(&field.value) != bare(&other.value) {
                            out.push(Finding::at(
                                high,
                                Some(field.line),
                                format!(
                                    "{a} and {b} cite each other and state different {}: {} against {} ({} and {}); {} outranks {lower}, and neither file was changed",
                                    field.key,
                                    bare(&field.value),
                                    bare(&other.value),
                                    high.shown,
                                    low.shown,
                                    kind.name
                                ),
                            ));
                        }
                    }
                }
            }
        }
    }
    out
}

fn index(record: &Record, root: &Path, repository: &Path) -> Vec<Finding> {
    let mut out = Vec::new();
    for (k, kind) in record.layout.kinds.iter().enumerate() {
        let (Some(index), Some(prefix)) = (&kind.index, &kind.prefix) else {
            continue;
        };
        let path = root.join(index);
        let Some(listing) = record.docs.iter().find(|d| d.path == path) else {
            out.push(Finding {
                shown: shown(&path, repository),
                line: None,
                message: format!("the index of each {} doesn't exist", kind.name),
            });
            continue;
        };
        if let Some((open, close)) = generated_block(&listing.text) {
            let generated = generate_index(record, k).unwrap_or_default();
            if normalised(&listing.text[open..close]) != normalised(&generated) {
                out.push(Finding::at(
                    listing,
                    Some(line_of(&listing.text, open)),
                    format!(
                        "its generated block is out of date; run paw index {} --write",
                        kind.name
                    ),
                ));
            }
        }
        let own = Regex::new(&format!(r"\b{prefix}-\d{{4}}\b")).expect("identifier pattern");
        let mut listed: BTreeMap<&str, usize> = BTreeMap::new();
        let mut first: BTreeMap<&str, usize> = BTreeMap::new();
        for found in own.find_iter(&listing.text) {
            listed
                .entry(found.as_str())
                .or_insert_with(|| line_of(&listing.text, found.start()));
            first.entry(found.as_str()).or_insert(found.start());
        }
        // A living kind's index is its reading order, so each document follows
        // everything it cites (REQ-0525); a record's index is ordered by identifier.
        if kind.statuses.iter().any(|s| s == "live") {
            for doc in record
                .docs
                .iter()
                .filter(|d| d.kind == Some(k) && d.path != path)
            {
                let id = bare(doc.id());
                let Some(&at) = first.get(id) else { continue };
                let cited: BTreeSet<&str> = own
                    .find_iter(&doc.text)
                    .map(|m| m.as_str())
                    .filter(|c| *c != id)
                    .collect();
                for c in cited {
                    if first.get(c).is_some_and(|&later| later > at) {
                        out.push(Finding::at(
                            listing,
                            Some(line_of(&listing.text, at)),
                            format!("lists {id} before {c}, which it cites"),
                        ));
                    }
                }
            }
        }
        let mut present = BTreeSet::new();
        for doc in record
            .docs
            .iter()
            .filter(|d| d.kind == Some(k) && d.path != path)
        {
            let id = bare(doc.id());
            present.insert(id.to_string());
            if !id.is_empty() && !listed.contains_key(id) {
                out.push(Finding::at(
                    listing,
                    None,
                    format!("doesn't list {id}, {}", doc.shown),
                ));
            }
        }
        for (id, line) in listed {
            if !present.contains(id) && Some(id) != listing.field("id").map(|f| bare(&f.value)) {
                out.push(Finding::at(
                    listing,
                    Some(line),
                    format!("lists {id}, which has no file"),
                ));
            }
        }
    }
    out
}

fn of_kind<'a>(record: &'a Record, name: &str) -> Vec<&'a Doc> {
    let Some(k) = record
        .layout
        .kinds
        .iter()
        .position(|kind| kind.name == name)
    else {
        return Vec::new();
    };
    record.docs.iter().filter(|d| d.kind == Some(k)).collect()
}

/// The index of a document's first line after its front matter.
fn body_start(doc: &Doc) -> usize {
    if !doc.text.starts_with("---") {
        return 0;
    }
    doc.text
        .lines()
        .enumerate()
        .skip(1)
        .find(|(_, l)| l.trim_end() == "---")
        .map(|(i, _)| i + 1)
        .unwrap_or(0)
}

fn requirements_in(record: &Record, text: &str) -> BTreeSet<String> {
    record
        .ids
        .find_iter(text)
        .map(|m| m.as_str())
        .filter(|id| id.starts_with("REQ-"))
        .map(str::to_string)
        .collect()
}

/// A decision's requirements land in at least one task of the epic realising
/// it, any number of tasks may name one (REQ-3646, REQ-3648), and every one of
/// them is stated by a specification (REQ-0246).
fn coverage(record: &Record) -> Vec<Finding> {
    let mut out = Vec::new();
    let mut stated = BTreeSet::new();
    for spec in of_kind(record, "specification") {
        stated.extend(requirements_in(record, spec.value("states")));
    }
    for requirement in of_kind(record, "requirement") {
        if bare(requirement.value("status")) == "withdrawn" {
            stated.insert(bare(requirement.id()).to_string());
        }
    }
    let known = known(record);
    for decision in of_kind(record, "decision") {
        if !approved(decision) {
            continue;
        }
        for requirement in requirements_in(record, decision.value("addresses")) {
            if !stated.contains(&requirement) {
                out.push(Finding::at(
                    decision,
                    None,
                    format!("{requirement} is stated in no specification"),
                ));
            }
        }
    }
    out.extend(chains(record, &known));
    out
}

/// An approved or living artifact resting on a draft anywhere up its chain,
/// which approving or rejecting the draft clears, and a draft or living one
/// resting on a withdrawn, superseded or rejected provider, which it can
/// still be moved off (REQ-0139). An approved one over a rejected provider only a new record
/// can clear, so `status` reports it and this doesn't.
fn chains(record: &Record, known: &BTreeMap<String, &Doc>) -> Vec<Finding> {
    let mut out = Vec::new();
    for doc in known.values() {
        let status = bare(doc.value("status"));
        let settled = matches!(status, "approved" | "live");
        let open = matches!(status, "draft" | "live");
        if !settled && !open {
            continue;
        }
        for (path, provider) in providers(record, known, doc) {
            let theirs = bare(provider.value("status"));
            let what = match theirs {
                "draft" if settled => "a draft".to_string(),
                "withdrawn" | "superseded" | "rejected" if open => format!("which is {theirs}"),
                _ => continue,
            };
            let id = path.last().cloned().unwrap_or_default();
            out.push(Finding::at(
                doc,
                None,
                format!("rests on {id}, {what}, through {}", path.join(" -> ")),
            ));
        }
    }
    out
}

/// The documents a repository has outside its record, tracked or not ignored,
/// relative to its root.
fn documents(root: &Path, repository: &Path) -> Vec<String> {
    let Ok(out) = profile::reading_git()
        .args([
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
        ])
        .current_dir(repository)
        .output()
    else {
        return Vec::new();
    };
    let record = root
        .strip_prefix(repository)
        .ok()
        .map(|p| p.to_string_lossy().replace('\\', "/"));
    let text = String::from_utf8_lossy(&out.stdout);
    // NUL-separated, so a path git would escape reads as it is (REQ-2522).
    let mut paths: Vec<String> = text
        .split('\0')
        .filter(|p| !p.is_empty())
        .filter(|p| {
            [".md", ".markdown", ".txt", ".rst", ".adoc", ".org"]
                .iter()
                .any(|e| p.to_lowercase().ends_with(e))
        })
        .filter(|p| !p.starts_with(".meowpaw/"))
        .filter(|p| {
            record
                .as_deref()
                .is_none_or(|r| !r.is_empty() && !p.starts_with(&format!("{r}/")))
        })
        .map(str::to_string)
        .collect();
    paths.sort();
    paths.dedup();
    paths
}

/// Each row of an onboarding report's Documents table: its line, the document,
/// the outcome and where it went or why.
fn placements(report: &Doc) -> Vec<(usize, String, String, String)> {
    let mut out = Vec::new();
    for (line, text) in section_lines(report, "Documents") {
        let cells: Vec<&str> = text
            .trim()
            .trim_matches('|')
            .split('|')
            .map(str::trim)
            .collect();
        if !text.trim_start().starts_with('|')
            || cells.len() < 3
            || cells[0].starts_with("---")
            || cells[0] == "Document"
        {
            continue;
        }
        out.push((
            line,
            cells[0].trim_matches('`').to_string(),
            cells[1].to_string(),
            cells[2].to_string(),
        ));
    }
    out
}

/// Removes what an approved onboarding report placed, keeping what it cites
/// (ADR-1280). It refuses before removing anything, so a refusal leaves the
/// tree as it was, and it commits nothing.
fn onboarding(rest: &[String]) -> u8 {
    if rest.first().map(String::as_str) != Some("remove") || rest.len() != 1 {
        eprintln!("usage: paw onboarding remove");
        return USAGE;
    }
    let (record, repository, root) = match open_record("onboarding") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let Some(report) = of_kind(&record, "onboarding").into_iter().next() else {
        say!(
            "paw onboarding remove: there is no onboarding report, so nothing is placed and nothing is removed"
        );
        return FOUND;
    };
    let status = bare(report.value("status"));
    if status != "approved" {
        say!(
            "paw onboarding remove: {} is {status}, and nothing is removed before a person approves where each document goes",
            report.shown
        );
        return FOUND;
    }
    let known = known(&record);
    let rows = placements(report);
    let mut refused = Vec::new();
    for (line, path, outcome, destination) in &rows {
        if outcome != "migrated" && outcome != "superseded" {
            continue;
        }
        let ids: Vec<&str> = record
            .ids
            .find_iter(destination)
            .map(|m| m.as_str())
            .collect();
        let named = destination.trim_matches('`');
        let exists = if ids.is_empty() {
            !named.is_empty() && (root.join(named).is_file() || repository.join(named).is_file())
        } else {
            ids.iter().all(|id| known.contains_key(*id))
        };
        if !exists {
            refused.push(format!("{}:{line}: {path} is {outcome} to {destination}, which names no artifact that exists", report.shown));
        }
    }
    if !refused.is_empty() {
        for line in &refused {
            say!("{line}");
        }
        say!("paw onboarding remove: nothing was removed");
        return FOUND;
    }
    let before = documents(&root, &repository).len();
    say!("before: {}", count(before, "document"));
    for (_, path, outcome, _) in &rows {
        if !matches!(outcome.as_str(), "migrated" | "superseded" | "discarded") {
            continue;
        }
        let file = repository.join(path);
        if !file.is_file() {
            continue;
        }
        if let Err(e) = std::fs::remove_file(&file) {
            say!("paw onboarding remove: {path}: {e}; stopped part way");
            return FOUND;
        }
        say!("removed {path} ({outcome})");
    }
    say!(
        "after: {}",
        count(documents(&root, &repository).len(), "document")
    );
    CLEAN
}

/// Every document an onboarding report finds gets exactly one outcome, with
/// where it went or why, so nothing is deleted before it is placed (REQ-1556).
fn placement(record: &Record, root: &Path, repository: &Path) -> Vec<Finding> {
    let Some(report) = of_kind(record, "onboarding").into_iter().next() else {
        return Vec::new();
    };
    let mut placed: BTreeMap<String, Vec<usize>> = BTreeMap::new();
    let mut out = Vec::new();
    for (line, path, outcome, destination) in placements(report) {
        let outcome = outcome.as_str();
        placed.entry(path.clone()).or_default().push(line);
        if !["migrated", "cited", "superseded", "discarded"].contains(&outcome) {
            out.push(Finding::at(report, Some(line), format!("gives {path} the outcome {outcome}, where an outcome is migrated, cited, superseded or discarded")));
        } else if destination.is_empty() {
            out.push(Finding::at(
                report,
                Some(line),
                format!("marks {path} {outcome} with no destination or reason"),
            ));
        }
    }
    let present = documents(root, repository);
    for path in &present {
        match placed.get(path) {
            None => out.push(Finding::at(
                report,
                None,
                format!("doesn't place {path}, a document the repository has"),
            )),
            Some(lines) if lines.len() > 1 => out.push(Finding::at(
                report,
                Some(lines[1]),
                format!("places {path} {} times", lines.len()),
            )),
            _ => {}
        }
    }
    out
}

fn is_draft(doc: &Doc) -> bool {
    bare(doc.value("status")) == "draft"
}

/// Relations that name no provider: a superseded record, a postponed
/// requirement and a requirement a defect violated are what a record moves
/// away from or moved against, not what it rests on (ADR-2960).
const NOT_PROVIDERS: [&str; 3] = ["supersedes", "postpones", "violates"];

/// Kinds that change after approval by design, a decision as its plan is
/// corrected and a defect as its plan and Closed by fill, so their date says
/// nothing about a citation and only their status does (ADR-1470).
const CHANGE_AFTER_APPROVAL: [&str; 2] = ["decision", "defect"];

/// Each provider up a document's chain, once, with the path that reached it,
/// walked in the order the layout lists its relations (REQ-0139).
fn providers<'a>(
    record: &Record,
    known: &BTreeMap<String, &'a Doc>,
    doc: &Doc,
) -> Vec<(Vec<String>, &'a Doc)> {
    let mut out = Vec::new();
    let mut seen = BTreeSet::from([bare(doc.id()).to_string()]);
    let mut path = vec![bare(doc.id()).to_string()];
    walk_up(record, known, doc, &mut path, &mut seen, &mut out);
    out
}

fn walk_up<'a>(
    record: &Record,
    known: &BTreeMap<String, &'a Doc>,
    doc: &Doc,
    path: &mut Vec<String>,
    seen: &mut BTreeSet<String>,
    out: &mut Vec<(Vec<String>, &'a Doc)>,
) {
    for key in record
        .layout
        .relations
        .iter()
        .filter(|k| !NOT_PROVIDERS.contains(&k.as_str()))
    {
        let Some(field) = doc.field(key) else {
            continue;
        };
        for found in record.ids.find_iter(&field.value) {
            let id = found.as_str();
            let Some(provider) = known.get(id).copied() else {
                continue;
            };
            if !seen.insert(id.to_string()) {
                continue;
            }
            path.push(id.to_string());
            out.push((path.clone(), provider));
            walk_up(record, known, provider, path, seen, out);
            path.pop();
        }
    }
}

/// Why a citation of `target` from `doc` is suspect, where it is: the target
/// was revised after the citing record, or, for a kind that changes after
/// approval or a kind's index, which is rewritten as its kind grows, was
/// withdrawn or superseded (REQ-0141).
fn suspect(record: &Record, doc: &Doc, target: &Doc) -> Option<String> {
    let status = bare(target.value("status"));
    let is_index = record
        .layout
        .kinds
        .iter()
        .any(|kind| kind.index.as_deref() == Some(target.relative.as_str()));
    if is_index || CHANGE_AFTER_APPROVAL.contains(&kind_of(record, target)) {
        return matches!(status, "withdrawn" | "superseded").then(|| format!("is {status}"));
    }
    let (theirs, ours) = (bare(target.value("revised")), bare(doc.value("revised")));
    (!theirs.is_empty() && !ours.is_empty() && theirs > ours).then(|| format!("revised {theirs}"))
}

/// Each citation in a document's relations that is suspect, with the field it
/// sits in and why.
fn suspects<'a>(
    record: &Record,
    known: &BTreeMap<String, &'a Doc>,
    doc: &'a Doc,
) -> Vec<(&'a Field, String, String)> {
    let mut out = Vec::new();
    for key in record
        .layout
        .relations
        .iter()
        .filter(|k| k.as_str() != "supersedes")
    {
        let Some(field) = doc.field(key) else {
            continue;
        };
        for found in record.ids.find_iter(&field.value) {
            if let Some(why) = known
                .get(found.as_str())
                .and_then(|target| suspect(record, doc, target))
            {
                out.push((field, found.as_str().to_string(), why));
            }
        }
    }
    out
}

fn shape(record: &Record) -> Vec<Finding> {
    let mut out = Vec::new();
    let withdrawn: BTreeSet<&str> = of_kind(record, "requirement")
        .into_iter()
        .filter(|r| bare(r.value("status")) == "withdrawn")
        .map(|r| bare(r.id()))
        .collect();
    let mut archives = BTreeSet::new();
    for doc in &record.docs {
        // A section the record retired is reported wherever it is still
        // carried, outside fenced code, where it is an example (REQ-3652).
        if doc.kind.is_some() && !doc.is_index {
            for (i, (_, _, _, heading)) in outline(&doc.text).into_iter().enumerate() {
                if let Some((name, why)) = heading.and_then(|h| retired_section(&record.layout, h))
                {
                    out.push(Finding::at(
                        doc,
                        Some(i + 1),
                        format!("carries the section {name}, which is retired: {why}"),
                    ));
                }
            }
        }
        // A directory named for age holds material nobody reads, which neither
        // freezes nor discards it (REQ-0555).
        if let Some((dir, _)) = doc.relative.rsplit_once('/')
            && dir
                .split('/')
                .any(|part| part.to_lowercase().contains("archive"))
            && archives.insert(dir.to_string())
        {
            out.push(Finding::at(doc, None, format!("sits in {dir}, a directory named for an archive; freeze the record or discard it with a reason")));
        }
        let living = doc
            .kind
            .is_some_and(|k| record.layout.kinds[k].statuses.iter().any(|s| s == "live"));
        if living && !doc.is_index {
            let mut aside = false;
            for (i, text) in doc.text.lines().enumerate().skip(body_start(doc)) {
                if let Some(heading) = text.strip_prefix("## ") {
                    aside = heading.trim_start().starts_with("Withdrawn");
                    continue;
                }
                if aside {
                    continue;
                }
                for found in record
                    .ids
                    .find_iter(text)
                    .filter(|m| withdrawn.contains(m.as_str()))
                {
                    out.push(Finding::at(
                        doc,
                        Some(i + 1),
                        format!(
                            "cites {}, which is withdrawn, outside a Withdrawn section",
                            found.as_str()
                        ),
                    ));
                }
            }
        }
    }
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else {
            continue;
        };
        // A kind's own index lists its records and makes no claims of its own.
        if kind.index.as_deref() == Some(doc.relative.as_str()) {
            continue;
        }
        let headings: Vec<&str> = doc
            .text
            .lines()
            .filter(|l| l.starts_with("##"))
            .map(|l| l.trim_start_matches('#'))
            .filter(|l| l.starts_with(' '))
            .map(str::trim)
            .collect();
        let names = |heading: &str, section: &str| {
            heading
                .strip_prefix(section)
                .is_some_and(|rest| !rest.starts_with(|c: char| c.is_alphanumeric()))
        };
        let drafted = if is_draft(doc) {
            kind.draft_sections.as_slice()
        } else {
            &[]
        };
        for section in kind.sections.iter().chain(drafted) {
            if !headings.iter().any(|h| names(h, section)) {
                let scope = if drafted.contains(section) {
                    "a draft "
                } else {
                    "a "
                };
                out.push(Finding::at(
                    doc,
                    None,
                    format!(
                        "has no {section} section, which {scope}{} carries",
                        kind.name
                    ),
                ));
            }
        }
        if let (Some(first), Some(opening)) = (&kind.first_section, headings.first())
            && !names(opening, first)
        {
            out.push(Finding::at(
                doc,
                None,
                format!(
                    "opens with {opening}, where a {} opens with {first}",
                    kind.name
                ),
            ));
        }
    }
    out
}

/// The lines of a `## <name>` section, with their line numbers.
/// The entries of a front matter list written `[a, b]` or as one bare word.
fn listed(value: &str) -> Vec<String> {
    bare(value)
        .trim_matches(|c: char| c == '[' || c == ']' || c.is_whitespace())
        .split(',')
        .map(|item| item.trim().trim_matches('"').trim_matches('\'').to_string())
        .filter(|item| !item.is_empty())
        .collect()
}

/// The lower-case words of a text, split on anything not alphanumeric.
fn words_of(text: &str) -> Vec<String> {
    text.to_lowercase()
        .split(|c: char| !c.is_alphanumeric())
        .filter(|w| !w.is_empty())
        .map(str::to_string)
        .collect()
}

/// Whether `words` occur in `heading` as a run of whole words.
fn contains_run(heading: &[String], words: &[String]) -> bool {
    !words.is_empty() && heading.windows(words.len()).any(|run| run == words)
}

/// The words of every heading in every specification, outside a fenced block
/// (REQ-2254).
fn framing_headings(record: &Record) -> Vec<Vec<String>> {
    let mut out = Vec::new();
    for spec in of_kind(record, "specification") {
        let mut fenced = false;
        for line in spec.text.lines() {
            if line.trim_start().starts_with("```") || line.trim_start().starts_with("~~~") {
                fenced = !fenced;
            } else if !fenced && line.starts_with('#') {
                out.push(words_of(line.trim_start_matches('#')));
            }
        }
    }
    out
}

fn section_lines<'a>(doc: &'a Doc, name: &str) -> Vec<(usize, &'a str)> {
    let mut out = Vec::new();
    let mut inside = false;
    for (i, line) in doc.text.lines().enumerate() {
        if let Some(heading) = line.strip_prefix("## ") {
            inside = heading.trim() == name;
            continue;
        }
        if inside {
            out.push((i + 1, line));
        }
    }
    out
}

/// A requirement's statement: the paragraph under its heading, with its line.
fn statement(doc: &Doc) -> Option<(usize, String)> {
    let lines: Vec<&str> = doc.text.lines().collect();
    let heading = lines.iter().position(|l| l.starts_with("# "))?;
    let start = (heading + 1..lines.len()).find(|&i| !lines[i].trim().is_empty())?;
    let end = (start..lines.len())
        .find(|&i| lines[i].trim().is_empty())
        .unwrap_or(lines.len());
    Some((start + 1, lines[start..end].join(" ")))
}

/// The most words a vision runs to (SPC-1230).
const VISION_WORDS: usize = 2000;

/// The text with each fenced line blanked, so offsets and lines stay.
fn without_fences(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut inside = false;
    for line in text.split_inclusive('\n') {
        let fence = line.trim_start().starts_with("```") || line.trim_start().starts_with("~~~");
        if fence {
            inside = !inside;
        }
        if fence || inside {
            out.extend(line.chars().map(|c| if c == '\n' { '\n' } else { ' ' }));
        } else {
            out.push_str(line);
        }
    }
    out
}

/// Whether `phrase` occurs in `text` as whole words.
fn has_word(text: &str, phrase: &str) -> bool {
    text.match_indices(phrase).any(|(at, found)| {
        let before = text[..at].chars().next_back();
        let after = text[at + found.len()..].chars().next();
        !before.is_some_and(char::is_alphanumeric) && !after.is_some_and(char::is_alphanumeric)
    })
}

/// The named rules a section or a field can't express (ADR-1140).
fn rules(record: &Record) -> Vec<Finding> {
    let date = Regex::new(r"\d{4}-\d{2}-\d{2}").expect("date pattern");
    let requirement = Regex::new(r"REQ-\d{4}").expect("requirement pattern");
    // RES-0254: two keywords can't be cited by one check, "such a record" breaks
    // when its neighbour moves, and "No X MUST Y" negates a requirement.
    let keyword = Regex::new(r"\b(?:MUST|SHALL|SHOULD|MAY)(?: NOT)?\b").expect("keyword pattern");
    let neighbour = Regex::new(r"(?i)\b(?:such an? \w+|the (?:above|previous|preceding|following) \w+|that (?:command|record|artifact|check|step|file|document|unit|requirement))\b").expect("neighbour pattern");
    let negated = Regex::new(r"\bNo\b[^.]*?\bMUST\b(?: NOT)?").expect("negation pattern");
    let numbered = Regex::new(r"^\d+\. ").expect("step pattern");
    let dated = Regex::new(r"\d{4}-\d{2}-\d{2}|\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b|\bQ[1-4] \d{4}\b").expect("date pattern");
    let sentences = Regex::new(r"[^.!?]*(?:[.!?]+(?:\s|$)|$)").expect("sentence pattern");
    let struck = Regex::new(r"~~[^~\s][^~]*~~").expect("struck pattern");
    let inline_code = Regex::new(r"`[^`]*`").expect("code span pattern");
    let known = known(record);
    let mut out = Vec::new();
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else {
            continue;
        };
        if kind.index.as_deref() == Some(doc.relative.as_str()) {
            continue;
        }
        let drafted = if is_draft(doc) {
            kind.draft_rules.as_slice()
        } else {
            &[]
        };
        for rule in kind.rules.iter().chain(drafted) {
            match rule.as_str() {
                "sources-dated" => {
                    for (line, text) in section_lines(doc, "Sources") {
                        if text.starts_with("- ") && !date.is_match(text) {
                            out.push(Finding::at(
                                doc,
                                Some(line),
                                "names a source without the date it was read".into(),
                            ));
                        }
                    }
                }
                "cites-no-requirement" => {
                    let body_start = doc
                        .fields
                        .as_ref()
                        .map(|f| f.last().map(|l| l.line).unwrap_or(0))
                        .unwrap_or(0)
                        + 1;
                    for (i, text) in doc.text.lines().enumerate().skip(body_start) {
                        for found in requirement.find_iter(text) {
                            out.push(Finding::at(
                                doc,
                                Some(i + 1),
                                format!(
                                    "cites {}, and research cites no requirement",
                                    found.as_str()
                                ),
                            ));
                        }
                    }
                }
                "verification-kind" => {
                    // One of the four kinds of check, which `status` counts to report
                    // how much of the set rests on judgement (ADR-1510).
                    const KINDS: [&str; 4] = ["static", "behavioural", "evaluation", "judgement"];
                    if let Some(field) = doc.field("verification") {
                        let kind = bare(&field.value);
                        if !KINDS.contains(&kind) {
                            out.push(Finding::at(doc, Some(field.line), format!("verification {kind} is not one of static, behavioural, evaluation and judgement")));
                        }
                    }
                }
                "judgement-verifier" => {
                    if let Some(field) = doc.field("verification")
                        && bare(&field.value) == "judgement"
                        && doc.field("verifier").is_none()
                    {
                        out.push(Finding::at(
                            doc,
                            Some(field.line),
                            "is verified by judgement and names no verifier: agent or person"
                                .into(),
                        ));
                    }
                }
                "concerns-framed" => {
                    if kind.optional_fields.iter().any(|f| f == "concerns")
                        && matches!(bare(doc.value("status")), "draft" | "approved" | "done")
                        && let Some(field) = doc.field("concerns")
                    {
                        let framed = framing_headings(record);
                        for concern in listed(&field.value) {
                            let wanted = words_of(&concern);
                            if !framed.iter().any(|heading| contains_run(heading, &wanted)) {
                                out.push(Finding::at(
                                    doc,
                                    Some(field.line),
                                    format!(
                                        "names the concern {concern}, which no specification section heading names (REQ-2254)"
                                    ),
                                ));
                            }
                        }
                    }
                }
                "alternatives-why-lost" => {
                    let header = section_lines(doc, "Alternatives")
                        .into_iter()
                        .find(|(_, text)| text.trim_start().starts_with('|'));
                    let says = header.is_some_and(|(_, text)| text.to_lowercase().contains("lost"));
                    if !says {
                        out.push(Finding::at(
                            doc,
                            header.map(|(line, _)| line),
                            "has no column saying why each alternative lost".into(),
                        ));
                    }
                }
                "one-obligation" | "stands-alone" | "no-negated-requirement" => {
                    let Some((line, text)) = statement(doc) else {
                        continue;
                    };
                    let (pattern, message) = match rule.as_str() {
                        "one-obligation" => (
                            &keyword,
                            "carries more than one keyword, where a requirement carries one obligation",
                        ),
                        "stands-alone" => (&neighbour, "leans on a neighbour"),
                        _ => (
                            &negated,
                            "negates a requirement with \"No ... MUST\", where a prohibition is MUST NOT",
                        ),
                    };
                    let hits: Vec<&str> = pattern.find_iter(&text).map(|m| m.as_str()).collect();
                    let found = if rule == "one-obligation" {
                        hits.len() > 1
                    } else {
                        !hits.is_empty()
                    };
                    if found {
                        let shown = if rule == "one-obligation" {
                            hits.join(", ")
                        } else {
                            hits[0].to_string()
                        };
                        out.push(Finding::at(doc, Some(line), format!("{message}: {shown}")));
                    }
                }
                "adoption-in-steps" => {
                    let lines = section_lines(doc, "Adoption");
                    if !lines.is_empty() && !lines.iter().any(|(_, l)| numbered.is_match(l)) {
                        out.push(Finding::at(doc, lines.first().map(|(n, _)| n - 1), "has an Adoption section with no numbered steps, where adoption is a sequence each leaving the repository working".into()));
                    }
                }
                "enters-after-triage" => {
                    // A draft defect whose triage is written names the step it enters at.
                    let triaged = section_lines(doc, "Triage")
                        .iter()
                        .any(|(_, l)| !l.trim().is_empty());
                    if triaged && bare(doc.value("enters")).is_empty() {
                        out.push(Finding::at(
                            doc,
                            None,
                            "has a Triage section and no enters: naming the step it enters at"
                                .into(),
                        ));
                    }
                }
                "enters-fits" => {
                    let enters = bare(doc.value("enters"));
                    let line = doc.field("enters").map(|f| f.line);
                    // A defect approved while cover was a step keeps the step it
                    // was triaged to (ADR-2300); a draft names a step in force.
                    let retired = RETIRED_STEPS.contains(&enters);
                    if !enters.is_empty()
                        && !STEPS.contains(&enters)
                        && !(retired && !is_draft(doc))
                    {
                        out.push(Finding::at(
                            doc,
                            line,
                            format!(
                                "enters {enters}, which is not a step; the steps are {}",
                                STEPS.join(", ")
                            ),
                        ));
                    }
                    if matches!(enters, "cover" | "implement" | "design")
                        && bare(doc.value("violates")).is_empty()
                    {
                        out.push(Finding::at(doc, line, format!("enters {enters} and names no requirement it violates, where a defect no requirement covers enters at requirements or research")));
                    }
                    if !enters.is_empty()
                        && !section_lines(doc, "Reproduction")
                            .iter()
                            .any(|(_, l)| !l.trim().is_empty())
                    {
                        out.push(Finding::at(doc, line, "is triaged with an empty Reproduction, where a defect is reproduced before it is triaged".into()));
                    }
                }
                "rejected-says-why" => {
                    if bare(doc.value("status")) == "rejected"
                        && !section_lines(doc, "Triage")
                            .iter()
                            .any(|(_, l)| !l.trim().is_empty())
                    {
                        out.push(Finding::at(doc, None, "is rejected as no defect with an empty Triage, where the reasoning is recorded".into()));
                    }
                }
                "closed-names-check" => {
                    if bare(doc.value("status")) == "done"
                        && !section_lines(doc, "Closed by")
                            .iter()
                            .any(|(_, l)| !l.trim().is_empty())
                    {
                        out.push(Finding::at(doc, None, "is done with an empty Closed by, where it names the check that stays as a regression check".into()));
                    }
                }
                "plan-where-work" => {
                    if matches!(bare(doc.value("status")), "draft" | "approved")
                        && !requirements_in(record, doc.value("addresses")).is_empty()
                        && !has_plan(doc)
                    {
                        out.push(Finding::at(
                            doc,
                            None,
                            "addresses work and carries no ## Plan (REQ-3672)".into(),
                        ));
                    }
                }
                "plan-where-implement" => {
                    if bare(doc.value("enters")) == "implement" && !has_plan(doc) {
                        out.push(Finding::at(
                            doc,
                            doc.field("enters").map(|f| f.line),
                            "enters at implement and carries no ## Plan (REQ-3674)".into(),
                        ));
                    }
                }
                "prompted-by-defect" => {
                    for id in doc
                        .value("prompted-by")
                        .split(|c: char| !(c.is_ascii_alphanumeric() || c == '-'))
                        .filter(|w| !w.is_empty())
                    {
                        if !known
                            .get(id)
                            .is_some_and(|d| matches!(kind_of(record, d), "defect" | "task"))
                        {
                            out.push(Finding::at(
                                doc,
                                doc.field("prompted-by").map(|f| f.line),
                                format!("is prompted by {id}, which is not a defect or a task"),
                            ));
                        }
                    }
                }
                "addresses-or-postpones" => {
                    let named = requirements_in(record, doc.value("addresses")).len()
                        + requirements_in(record, doc.value("postpones")).len();
                    if named == 0 {
                        out.push(Finding::at(doc, doc.field("addresses").map(|f| f.line), "addresses no requirement and postpones none, where a decision does one or both".into()));
                    }
                }
                "title-states-claim" => {
                    let line = doc
                        .text
                        .lines()
                        .position(|l| l.starts_with("# "))
                        .map(|i| i + 1);
                    let heading = title(doc);
                    let words = heading.split_whitespace().count();
                    if date.is_match(&heading) {
                        out.push(Finding::at(doc, line, "has a title carrying a date, where an insight's title states its claim".into()));
                    } else if words < 4 {
                        out.push(Finding::at(doc, line, format!("has a title of {}, where an insight's title states its claim in at least four", count(words, "word"))));
                    }
                }
                "evidence-measured" => {
                    let lines = section_lines(doc, "Evidence");
                    let measured = lines.iter().any(|(_, l)| {
                        l.chars().any(|c| c.is_ascii_digit()) || l.trim_start().starts_with("```")
                    });
                    if !lines.is_empty() && !measured {
                        out.push(Finding::at(
                            doc,
                            lines.first().map(|(n, _)| n - 1),
                            "has evidence with no number, measurement or reproducible block".into(),
                        ));
                    }
                }
                "ends-with-pattern" => {
                    let last = doc
                        .text
                        .lines()
                        .enumerate()
                        .filter(|(_, l)| l.starts_with("## "))
                        .last();
                    if let Some((i, heading)) =
                        last.filter(|(_, l)| l.trim_end() != "## The pattern")
                    {
                        out.push(Finding::at(
                            doc,
                            Some(i + 1),
                            format!(
                                "ends with {}, where an insight ends with The pattern",
                                heading.trim_start_matches("## ").trim()
                            ),
                        ));
                    }
                }
                "vision-no-date" | "vision-no-obligation" | "vision-length" => {
                    let masked = without_fences(&doc.text);
                    let start: usize = masked
                        .split_inclusive('\n')
                        .take(body_start(doc))
                        .map(str::len)
                        .sum();
                    let body = &masked[start..];
                    match rule.as_str() {
                        "vision-no-date" => {
                            for (i, text) in doc.text.lines().enumerate().skip(body_start(doc)) {
                                for found in dated.find_iter(text) {
                                    out.push(Finding::at(
                                        doc,
                                        Some(i + 1),
                                        format!(
                                            "carries the date {}, and a vision carries no dates",
                                            found.as_str()
                                        ),
                                    ));
                                }
                            }
                        }
                        "vision-no-obligation" => {
                            for sentence in sentences.find_iter(body) {
                                let said = sentence.as_str();
                                if let (Some(id), true) =
                                    (requirement.find(said), keyword.is_match(said))
                                {
                                    out.push(Finding::at(
                                        doc,
                                        Some(line_of(&masked, start + sentence.start())),
                                        format!("states {} as an obligation, and a vision restates no requirement", id.as_str()),
                                    ));
                                }
                            }
                        }
                        _ => {
                            let words = body.split_whitespace().count();
                            if words > VISION_WORDS {
                                out.push(Finding::at(
                                    doc,
                                    None,
                                    format!("runs to {words} words, over the {VISION_WORDS} a vision runs to"),
                                ));
                            }
                        }
                    }
                }
                "spec-no-history" => {
                    let masked = without_fences(&doc.text);
                    for (i, text) in masked.lines().enumerate().skip(body_start(doc)) {
                        // A phrase quoted in code is a mention and no use.
                        let text = &inline_code.replace_all(text, "");
                        if struck.is_match(text) {
                            out.push(Finding::at(
                                doc,
                                Some(i + 1),
                                "carries struck text, and a specification states only what the system does now".into(),
                            ));
                        }
                        if text.starts_with('#')
                            && let Some(heading) = text.trim_start_matches('#').strip_prefix(' ')
                        {
                            let heading = heading.trim();
                            let lower = heading.to_lowercase();
                            if lower.starts_with("withdrawn") || lower.contains("tombstone") {
                                out.push(Finding::at(
                                    doc,
                                    Some(i + 1),
                                    format!("carries the heading {heading}, and a specification carries no history"),
                                ));
                            }
                        }
                        let lower = text.to_lowercase();
                        for phrase in &record.layout.history_phrases {
                            if has_word(&lower, &phrase.to_lowercase()) {
                                out.push(Finding::at(
                                    doc,
                                    Some(i + 1),
                                    format!(
                                        "says \"{phrase}\", and a specification carries no history"
                                    ),
                                ));
                            }
                        }
                    }
                }
                "withdrawn-names-record" => {
                    if bare(doc.value("status")) == "withdrawn" {
                        let lines: Vec<&str> = doc.text.lines().collect();
                        let first = lines
                            .iter()
                            .position(|l| l.starts_with("# "))
                            .and_then(|h| {
                                (h + 1..lines.len()).find(|&i| !lines[i].trim().is_empty())
                            });
                        if !first.is_some_and(|i| record.ids.is_match(lines[i])) {
                            out.push(Finding::at(
                                doc,
                                first.map(|i| i + 1),
                                "is withdrawn and its first line names no record that withdrew it"
                                    .into(),
                            ));
                        }
                    }
                }
                unknown => out.push(Finding::at(
                    doc,
                    None,
                    format!("the layout names a rule, {unknown}, this program doesn't know"),
                )),
            }
        }
    }
    out
}

const STEPS: [&str; 6] = [
    "research",
    "requirements",
    "design",
    "spec",
    "implement",
    "review",
];

/// The steps ADR-2300 and ADR-3090 retired. The `enters` rule reads them: an
/// approved defect triaged while they were steps keeps its `enters` (ADR-2350).
const RETIRED_STEPS: [&str; 4] = ["cover", "document", "verify", "epic"];
const TEMPLATES: [&str; 10] = [
    "research",
    "requirement",
    "adr",
    "spec",
    "bug",
    "insight",
    "vision",
    "constitution",
    "profile",
    "onboarding",
];

fn approved(doc: &Doc) -> bool {
    matches!(bare(doc.value("status")), "approved" | "done")
}

fn kind_of<'a>(record: &'a Record, doc: &Doc) -> &'a str {
    doc.kind
        .map(|k| record.layout.kinds[k].name.as_str())
        .unwrap_or("artifact")
}

/// Whether a record carries a plan with something in it (REQ-3672).
fn has_plan(doc: &Doc) -> bool {
    section_lines(doc, "Plan")
        .iter()
        .any(|(_, line)| !line.trim().is_empty())
}

/// What keeps the inputs from being ready for a step, one line each, as `paw
/// ready` prints them: empty where every input is ready.
pub(crate) fn unready(record: &Record, step: &str, ids: &[String]) -> Vec<String> {
    let known = known(record);
    let mut missing: Vec<String> = Vec::new();
    for id in ids {
        let Some(doc) = known.get(id.as_str()) else {
            missing.push(format!("{id} has no file"));
            continue;
        };
        let kind = kind_of(record, doc);
        match step {
            "requirements" | "design" | "spec" | "implement" if !approved(doc) => {
                missing.push(format!(
                    "{id}, a {kind}, is {} and not approved",
                    bare(doc.value("status"))
                ));
                continue;
            }
            _ => {}
        }
        match step {
            "implement" if matches!(kind, "decision" | "defect") => {
                if !has_plan(doc) {
                    missing.push(format!("{id} carries no plan"));
                }
                let mut stated = BTreeSet::new();
                for spec in of_kind(record, "specification") {
                    stated.extend(requirements_in(record, spec.value("states")));
                }
                for requirement in requirements_in(record, doc.value("addresses")) {
                    if !stated.contains(&requirement) {
                        missing.push(format!(
                            "{requirement}, which {id} addresses, is stated by no specification"
                        ));
                    }
                }
            }
            "implement" => missing.push(format!(
                "{id} is a {kind}, and only a decision or a defect is implemented"
            )),
            _ => {}
        }
    }
    missing
}

fn ready(rest: &[String]) -> u8 {
    let Some((step, ids)) = rest.split_first() else {
        eprintln!(
            "usage: paw ready <step> <id>..., where a step is one of {}",
            STEPS.join(", ")
        );
        return USAGE;
    };
    let step = step.as_str();
    if !STEPS.contains(&step) {
        eprintln!(
            "paw ready: no step is named {step}; the steps are {}",
            STEPS.join(", ")
        );
        return USAGE;
    }
    if step == "research" {
        say!("paw ready research: ready; research needs no approved input");
        return CLEAN;
    }
    if ids.is_empty() {
        eprintln!("paw ready {step}: name the identifiers of the step's input");
        return USAGE;
    }
    let (record, _repository, _root) = match open_record("ready") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let missing = unready(&record, step, ids);
    if missing.is_empty() {
        say!(
            "paw ready {step}: ready; {} approved and complete",
            ids.join(", ")
        );
        CLEAN
    } else {
        say!("paw ready {step}: not ready");
        for line in &missing {
            say!("  {line}");
        }
        FOUND
    }
}

/// The steps a run of `meow-loop` takes, which are every step but review
/// (SPC-1201).
#[cfg(feature = "loop")]
pub(crate) const RUN_STEPS: [&str; 5] = ["research", "requirements", "design", "spec", "implement"];

/// The record under `root` as a run reads it, with the layout `MEOW_LAYOUT`
/// names or the copy `meow-loop` ships in its own `lib/layout.toml`.
#[cfg(feature = "loop")]
pub(crate) fn read_for_run(repository: &Path, root: &Path) -> Result<Record, String> {
    Ok(read_record(load_layout()?, repository, root))
}

/// One record as the copy held at the start of a run keeps it.
#[cfg(feature = "loop")]
struct HeldDoc {
    id: String,
    kind: Option<usize>,
    path: PathBuf,
    /// The path under the record root, with `/` for a separator.
    relative: String,
    shown: String,
    status: String,
    text: String,
}

/// The copy of the record a run holds from start, which "new since start" and
/// "changed since start" compare with (SPC-1201).
#[cfg(feature = "loop")]
pub(crate) struct Held {
    docs: Vec<HeldDoc>,
}

/// Takes the copy of the record a run holds: each record's identifier, kind,
/// path, stored status and text.
#[cfg(feature = "loop")]
pub(crate) fn hold(record: &Record) -> Held {
    Held {
        docs: record
            .docs
            .iter()
            .filter(|doc| doc.kind.is_some())
            .map(|doc| HeldDoc {
                id: bare(doc.id()).to_string(),
                kind: doc.kind,
                path: doc.path.clone(),
                relative: doc.relative.clone(),
                shown: doc.shown.clone(),
                status: bare(doc.value("status")).to_string(),
                text: doc.text.clone(),
            })
            .collect(),
    }
}

/// Whether a stored status is a decision a person makes. It is any status but
/// `draft`, and any but `live` in a living kind, because a specification is
/// `live` from its first draft and that marks no approval. A record with no
/// status has decided nothing.
#[cfg(feature = "loop")]
fn decided(kind: &Kind, status: &str) -> bool {
    !status.is_empty()
        && status != "draft"
        && !(status == "live" && kind.statuses.iter().any(|s| s == "live"))
}

/// The decided status an Edit or a Write would give the file at `path`, if it
/// would give one: `before` is the file on disk, if any, and `after` the text
/// the edit would leave. A status counts only where it differs from the one on
/// disk, and the kind comes from the file's directory under `root`, so `live`
/// passes in a specification and not in a requirement (SPC-1201 "The status
/// rule"). `root` and `path` are both resolved.
#[cfg(feature = "loop")]
pub(crate) fn decided_by_edit(
    root: &Path,
    path: &Path,
    before: Option<&str>,
    after: &str,
) -> Option<String> {
    let layout = load_layout().ok()?;
    let relative = path
        .strip_prefix(root)
        .ok()?
        .to_string_lossy()
        .replace('\\', "/");
    let (parent, name) = relative.rsplit_once('/').unwrap_or(("", relative.as_str()));
    // The reader takes Markdown files only, and an index is no record.
    let kind = layout.kinds.iter().find(|kind| {
        kind.file.as_deref() == Some(relative.as_str())
            || (kind.dir.as_deref() == Some(parent)
                && name.ends_with(".md")
                && name != layout.index_name)
    })?;
    let status_of = |text: &str| {
        parse_front_matter(&text.replace("\r\n", "\n"))
            .and_then(|fields| fields.into_iter().find(|field| field.key == "status"))
            .map(|field| bare(&field.value).to_string())
            .unwrap_or_default()
    };
    let new = status_of(after);
    let old = before.map(status_of).unwrap_or_default();
    (new != old && decided(kind, &new)).then_some(new)
}

/// Whether a run of `step` may change an approved record of `kind` from
/// `before` to `after`. A decision or defect may change only in its work part,
/// and only in an `implement` run. None of the frozen comparison's exemptions
/// apply, because a status now `withdrawn` and a line naming an authority are
/// a person's decisions (ADR-2020).
#[cfg(feature = "loop")]
fn run_may_change(kind: &str, step: &str, before: &str, after: &str) -> bool {
    matches!(kind, "decision" | "defect")
        && step == "implement"
        && work_part(before, true) == work_part(after, true)
}

/// Each Markdown file under `root` that can't be read, with the error. The
/// record reader takes such a file as empty text, so a run that started over
/// one could never guard it or tell a change to it.
#[cfg(feature = "loop")]
pub(crate) fn unreadable_files(root: &Path) -> Vec<(PathBuf, String)> {
    let mut paths = Vec::new();
    markdown_under(root, None, &mut paths);
    paths
        .into_iter()
        .filter_map(|path| {
            std::fs::read_to_string(&path)
                .err()
                .map(|error| (path, error.to_string()))
        })
        .collect()
}

/// Each input that is the wrong kind for `step`, with its line: a
/// `requirements` run reads research records, a `design` run requirements, a
/// `spec` run decisions, and an `implement` run decisions or defects. An input
/// with no file is `unready`'s to report.
#[cfg(feature = "loop")]
pub(crate) fn wrong_kind(record: &Record, step: &str, ids: &[String]) -> Vec<(String, String)> {
    let expected = match step {
        "requirements" => "research",
        "design" => "requirement",
        "spec" | "implement" => "decision",
        _ => return Vec::new(),
    };
    let article = |word: &str| {
        if word.starts_with(['a', 'e', 'i', 'o', 'u']) {
            "an"
        } else {
            "a"
        }
    };
    let known = known(record);
    ids.iter()
        .filter_map(|id| {
            let kind = kind_of(record, known.get(id.as_str())?);
            let fits = kind == expected || (step == "implement" && kind == "defect");
            (!fits).then(|| {
                let line = format!(
                    "{id}, {} {kind}, is not {} {expected}, which {} {step} run reads",
                    article(kind),
                    article(expected),
                    article(step)
                );
                (id.clone(), line)
            })
        })
        .collect()
}

/// The work tree's path of a record under the record root `root`, as git
/// lists it. It is built from the path under the root and not from the
/// canonical path, because a link whose target lies elsewhere has the path git
/// lists and not its target's.
#[cfg(feature = "loop")]
fn tree_path(root: &str, relative: &str) -> String {
    if root.is_empty() {
        relative.to_string()
    } else {
        format!("{root}/{relative}")
    }
}

/// The paths of the records that differ from the copy held at start: a record
/// new since start, one whose text changed or that moved, and one gone from its
/// path. A run
/// uses them in place of the paths git lists where it can't list those.
#[cfg(feature = "loop")]
pub(crate) fn changed_record_paths(record: &Record, held: &Held, root: &str) -> Vec<String> {
    let present: BTreeSet<&Path> = record.docs.iter().map(|doc| doc.path.as_path()).collect();
    let mut out: Vec<String> = Vec::new();
    for doc in record.docs.iter().filter(|doc| doc.kind.is_some()) {
        let changed = held_for(held, doc, &present)
            .is_none_or(|(then, moved)| moved || then.text != doc.text);
        if changed {
            out.push(tree_path(root, &doc.relative));
        }
    }
    for then in &held.docs {
        if !present.contains(then.path.as_path()) {
            out.push(tree_path(root, &then.relative));
        }
    }
    out
}

/// What a call wrote that a run of `step` doesn't write, one entry for each
/// changed path and kind, naming the path and why (SPC-1201 "Keeping to one
/// step"). `paths` are the work tree's paths the call changed, with `/` for a
/// separator, and `root` is the record root among them. A step writes the kind
/// its row names, and a defect or an insight in every step. A file under the
/// root that is no record, such as an index, is allowed in every step, and a
/// path outside the root only in `implement`. An `implement` run changes an
/// epic only in its task marks. A path that holds more than one record, as a
/// link and its target do, is judged for each.
#[cfg(feature = "loop")]
pub(crate) fn off_step(
    record: &Record,
    held: &Held,
    step: &str,
    root: &str,
    paths: &[String],
) -> Vec<String> {
    let allowed = |kind: &str| {
        matches!(kind, "defect" | "insight")
            || match step {
                "research" => kind == "research",
                "requirements" => kind == "requirement",
                "design" => kind == "decision",
                "spec" => kind == "specification",
                _ => kind == "decision",
            }
    };
    let mut out = Vec::new();
    for path in paths {
        let inside = root.is_empty()
            || path == root
            || path
                .strip_prefix(root)
                .is_some_and(|rest| rest.starts_with('/'));
        if !inside {
            if step != "implement" {
                out.push(format!(
                    "{path} (outside the record root, which the {step} step doesn't write)"
                ));
            }
            continue;
        }
        let mut kinds: Vec<usize> = record
            .docs
            .iter()
            .filter(|doc| tree_path(root, &doc.relative) == *path)
            .filter_map(|doc| doc.kind)
            .collect();
        if kinds.is_empty() {
            kinds.extend(
                held.docs
                    .iter()
                    .filter(|then| tree_path(root, &then.relative) == *path)
                    .filter_map(|then| then.kind),
            );
        }
        for k in kinds {
            let kind = record.layout.kinds[k].name.as_str();
            if !allowed(kind) {
                out.push(format!(
                    "{path} ({kind} record, which the {step} step doesn't write)"
                ));
            }
        }
    }
    out
}

/// The held record a document is, and whether it moved. A record is the held
/// one at its path with its identifier, else the held one of its identifier
/// whose path is gone, which is a rename, else the held one at its path with
/// another identifier. Anything else is new. Identifiers can repeat, so the
/// path decides first.
#[cfg(feature = "loop")]
fn held_for<'a>(
    held: &'a Held,
    doc: &Doc,
    present: &BTreeSet<&Path>,
) -> Option<(&'a HeldDoc, bool)> {
    let id = bare(doc.id());
    let same = |then: &&HeldDoc| then.path == doc.path;
    held.docs
        .iter()
        .find(|then| same(then) && then.id == id)
        .map(|then| (then, false))
        .or_else(|| {
            held.docs
                .iter()
                .find(|then| {
                    !id.is_empty() && then.id == id && !present.contains(then.path.as_path())
                })
                .map(|then| (then, true))
        })
        .or_else(|| held.docs.iter().find(same).map(|then| (then, false)))
}

/// What a call or an evaluation changed in the record since `held` was taken
/// that a run of `step` must not change, one entry for each record naming its
/// path and why (SPC-1201 "Keeping to one step"). The four changes are a
/// stored status that became a decided one, a new record that carries one, an
/// approved record gone from its path, and an approved record changed outside
/// what the run may change in it.
#[cfg(feature = "loop")]
pub(crate) fn crossings(record: &Record, held: &Held, step: &str) -> Vec<String> {
    let present: BTreeSet<&Path> = record.docs.iter().map(|doc| doc.path.as_path()).collect();
    let mut moved: BTreeSet<&Path> = BTreeSet::new();
    let mut out = Vec::new();
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else {
            continue;
        };
        let status = bare(doc.value("status"));
        match held_for(held, doc, &present) {
            None if decided(kind, status) => {
                out.push(format!("{} (new, and {status})", doc.shown));
            }
            Some((then, true)) if then.status == "approved" => {
                moved.insert(then.path.as_path());
                out.push(format!(
                    "{} (an approved record moved from {})",
                    doc.shown, then.shown
                ));
            }
            Some((then, _)) if then.status != status && decided(kind, status) => {
                out.push(format!("{} (became {status})", doc.shown));
            }
            Some((then, _))
                if then.status == "approved"
                    && then.text != doc.text
                    && !run_may_change(&kind.name, step, &then.text, &doc.text) =>
            {
                out.push(format!(
                    "{} (an approved {} changed outside what the {step} step may change)",
                    doc.shown, kind.name
                ));
            }
            _ => {}
        }
    }
    for then in held.docs.iter().filter(|then| then.status == "approved") {
        if !present.contains(then.path.as_path()) && !moved.contains(then.path.as_path()) {
            out.push(format!(
                "{} (an approved record is gone from its path)",
                then.shown
            ));
        }
    }
    out
}

/// Whether the step's test holds over `inputs`, as SPC-1201's table states.
/// A record counts whatever its status. Every step but `implement` counts
/// only a record new or changed since `held` was taken, so before the copy
/// exists only `implement` can hold.
#[cfg(feature = "loop")]
pub(crate) fn step_holds(
    record: &Record,
    held: Option<&Held>,
    step: &str,
    inputs: &[String],
) -> bool {
    let known = known(record);
    if step == "implement" {
        return inputs.iter().all(|id| {
            known.get(id.as_str()).is_some_and(|doc| {
                matches!(kind_of(record, doc), "decision" | "defect")
                    && bare(doc.value("status")) == "done"
            })
        });
    }
    let Some(held) = held else {
        return false;
    };
    let present: BTreeSet<&Path> = record.docs.iter().map(|doc| doc.path.as_path()).collect();
    let found = |doc: &Doc| held_for(held, doc, &present);
    let new = |doc: &Doc| found(doc).is_none();
    let touched = |doc: &Doc| found(doc).is_none_or(|(then, _)| then.text != doc.text);
    let cites = |doc: &Doc, keys: &[&str], id: &str| {
        keys.iter().any(|key| {
            record
                .ids
                .find_iter(doc.value(key))
                .any(|m| m.as_str() == id)
        })
    };
    let any = |kind: &str, keep: &dyn Fn(&Doc) -> bool| of_kind(record, kind).into_iter().any(keep);
    match step {
        "research" => any("research", &|doc| new(doc)),
        "requirements" => inputs.iter().all(|id| {
            any("requirement", &|doc| {
                touched(doc) && cites(doc, &["elaborates"], id)
            })
        }),
        "design" => inputs.iter().all(|id| {
            any("decision", &|doc| {
                new(doc) && cites(doc, &["addresses", "postpones"], id)
            })
        }),
        // A decision that addresses nothing, or an input that is no decision,
        // gives the step no work, so its test never holds.
        "spec" => inputs.iter().all(|id| {
            known.get(id.as_str()).is_some_and(|decision| {
                let addressed = requirements_in(record, decision.value("addresses"));
                kind_of(record, decision) == "decision"
                    && !addressed.is_empty()
                    && addressed.iter().all(|requirement| {
                        any("specification", &|doc| {
                            touched(doc) && cites(doc, &["states"], requirement)
                        })
                    })
            })
        }),
        _ => false,
    }
}

fn count(n: usize, noun: &str) -> String {
    format!("{n} {noun}{}", if n == 1 { "" } else { "s" })
}

fn title(doc: &Doc) -> String {
    let heading = doc
        .text
        .lines()
        .find(|l| l.starts_with("# "))
        .unwrap_or("# ")
        .trim_start_matches("# ");
    // A decision's heading carries its number, "1130. The chain ...".
    heading
        .split_once(". ")
        .filter(|(n, _)| n.chars().all(|c| c.is_ascii_digit()))
        .map(|(_, t)| t)
        .unwrap_or(heading)
        .to_string()
}

/// Where one decision stands in the chain, and what comes next.
fn position(record: &Record, decision: &Doc) -> String {
    let id = bare(decision.id());
    if bare(decision.value("status")) == "done" {
        return format!("closed: {id}");
    }
    let postponed = requirements_in(record, decision.value("postpones"));
    if requirements_in(record, decision.value("addresses")).is_empty() && !postponed.is_empty() {
        return format!(
            "postponing: {}, listed under Postponed",
            count(postponed.len(), "requirement")
        );
    }
    if has_plan(decision) {
        format!("next: implement {id}")
    } else {
        format!("waiting: {id} carries no plan")
    }
}

/// The gate a draft of each kind waits at.
fn gate_of(kind: &str) -> &'static str {
    match kind {
        "research" => "the research gate",
        "requirement" => "the requirements gate",
        "decision" => "the design gate",
        "defect" => "triage",
        _ => "approval",
    }
}

/// Each requirement an approved decision postpones and no record has taken up,
/// with the condition that would end the postponement, which is the first
/// line of the decision's What would reverse it (REQ-3622).
fn postponements(record: &Record, known: &BTreeMap<String, &Doc>) -> Vec<String> {
    let mut out = Vec::new();
    let mut decisions: Vec<&Doc> = of_kind(record, "decision")
        .into_iter()
        .filter(|d| approved(d))
        .collect();
    decisions.sort_by_key(|d| bare(d.id()).to_string());
    let item = Regex::new(r"^(?:[-*+]|\d+\.) +").expect("list item pattern");
    for decision in decisions {
        // The first paragraph or bullet, joined across its wrapped lines.
        let mut words: Vec<&str> = Vec::new();
        for (_, line) in section_lines(decision, "What would reverse it") {
            let line = line.trim();
            let starts = line.is_empty() || item.is_match(line) || line.starts_with('#');
            if starts && !words.is_empty() {
                break;
            }
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            words.push(item.find(line).map_or(line, |m| &line[m.end()..]));
        }
        let condition = if words.is_empty() {
            "no condition stated".to_string()
        } else {
            words.join(" ")
        };
        for requirement in requirements_in(record, decision.value("postpones")) {
            let still = known.get(requirement.as_str()).is_some_and(|r| approved(r))
                && requirement_state(
                    &closing_records(record, &requirement),
                    Some(bare(decision.id())),
                    &violated_by(record, &requirement),
                ) == "postponed";
            if still {
                out.push(format!(
                    "{requirement} by {}, until: {condition}",
                    bare(decision.id())
                ));
            }
        }
    }
    out
}

fn status(rest: &[String]) -> u8 {
    let (waiting_only, brief) = match rest {
        [] => (false, false),
        [flag] if flag == "--waiting" => (true, false),
        [flag] if flag == "--brief" => (false, true),
        _ => {
            eprintln!("usage: paw status [--waiting | --brief]");
            return USAGE;
        }
    };
    if waiting_only {
        // Run at the start of every session, so it says nothing unless
        // something waits: a repository with no record pays nothing.
        let repository = profile::repository_root();
        let (Ok(layout), Ok(root)) = (load_layout(), record_root(&repository)) else {
            return CLEAN;
        };
        if !root.is_dir() {
            return CLEAN;
        }
        let record = read_record(layout, &repository, &root);
        let known = known(&record);
        let drafts: Vec<&&Doc> = known
            .values()
            .filter(|doc| bare(doc.value("status")) == "draft")
            .collect();
        if !drafts.is_empty() {
            say!("Waiting for approval in this repository's record:");
            for doc in &drafts {
                let kind = kind_of(&record, doc);
                say!(
                    "  {} {kind}, at {}: {}",
                    bare(doc.id()),
                    gate_of(kind),
                    title(doc)
                );
            }
        }
        return CLEAN;
    }
    let (record, _repository, root) = match open_record("status") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    if !under_version_control(&root) {
        say!(
            "The record is local to this machine: {} is under no version control.",
            root.display()
        );
        say!();
    }
    let known = known(&record);
    let drafts: Vec<&&Doc> = known
        .values()
        .filter(|doc| bare(doc.value("status")) == "draft")
        .collect();
    say!("Waiting for approval");
    if drafts.is_empty() {
        say!("  nothing");
    }
    for doc in &drafts {
        let kind = kind_of(&record, doc);
        say!(
            "  {} {kind}, draft at {}: {}",
            bare(doc.id()),
            gate_of(kind),
            title(doc)
        );
    }
    say!();
    say!("Decisions");
    let mut decisions: Vec<&Doc> = of_kind(&record, "decision")
        .into_iter()
        .filter(|d| approved(d))
        .collect();
    decisions.sort_by_key(|d| bare(d.id()).to_string());
    if decisions.is_empty() {
        say!("  none approved");
    }
    let mut closed = 0;
    for decision in decisions {
        let place = position(&record, decision);
        if brief && place.starts_with("closed:") {
            closed += 1;
            continue;
        }
        say!("  {} {}", bare(decision.id()), title(decision));
        say!("    {place}");
    }
    if brief && closed > 0 {
        say!("  {closed} closed, listed by `paw status`");
    }
    say!();
    say!("Defects");
    let open: Vec<&Doc> = of_kind(&record, "defect")
        .into_iter()
        .filter(|d| bare(d.value("status")) == "approved")
        .collect();
    if open.is_empty() {
        say!("  none open");
    }
    for defect in open {
        let id = bare(defect.id());
        say!("  {id} {}", title(defect));
        match bare(defect.value("enters")) {
            "implement" | "" if has_plan(defect) => say!("    next: implement {id}"),
            "implement" | "" => say!("    waiting: {id} carries no plan"),
            step => say!("    enters at {step}"),
        }
    }
    say!();
    say!("Requirements");
    let states = [
        "closed",
        "in a decision not yet done",
        "reopened by a defect",
        "postponed",
        "named by no decision",
    ];
    let mut tally = [0usize; 5];
    let in_force: Vec<&Doc> = of_kind(&record, "requirement")
        .into_iter()
        .filter(|r| approved(r))
        .collect();
    for requirement in &in_force {
        let id = bare(requirement.id());
        let state = requirement_state(
            &closing_records(&record, id),
            postponed_by(&record, id).as_deref(),
            &violated_by(&record, id),
        );
        tally[states.iter().position(|s| *s == state).unwrap_or(4)] += 1;
    }
    let parts: Vec<String> = states
        .iter()
        .zip(tally)
        .map(|(s, n)| format!("{n} {s}"))
        .collect();
    if in_force.is_empty() {
        say!("  none in force, so coverage is zero, not complete");
    } else {
        say!("  {} in force: {}", in_force.len(), parts.join(", "));
        verification_share(&in_force);
    }
    say!();
    say!("Postponed");
    let postponements = postponements(&record, &known);
    if postponements.is_empty() {
        say!("  nothing");
    } else if brief {
        // One requirement can be postponed by two decisions, so count each once.
        let count = postponements
            .iter()
            .filter_map(|line| line.split_whitespace().next())
            .collect::<BTreeSet<_>>()
            .len();
        let noun = if count == 1 {
            "requirement"
        } else {
            "requirements"
        };
        say!("  {count} {noun}, listed by `paw status`");
    } else {
        for line in postponements {
            say!("  {line}");
        }
    }
    say!();
    say!("Only a new record can fix");
    let fixes = frozen_findings(&record, &known);
    if fixes.is_empty() {
        say!("  nothing");
    }
    for line in fixes {
        // A frozen finding's line lists every citation, which only the full
        // status needs: the brief one keeps what comes before the list.
        match line.split_once(": ") {
            Some((head, _)) if brief => say!("  {head}, listed by `paw status`"),
            _ => say!("  {line}"),
        }
    }
    CLEAN
}

/// How the requirements in force are verified, and the share resting on
/// evaluation or judgement rather than a mechanical check (REQ-0161).
fn verification_share(in_force: &[&Doc]) {
    let kinds = ["static", "behavioural", "evaluation", "judgement"];
    let mut tally = [0usize; 4];
    let (mut agent, mut person, mut unstated) = (0, 0, 0);
    for requirement in in_force {
        let verification = bare(requirement.value("verification"));
        match kinds.iter().position(|k| *k == verification) {
            Some(i) => tally[i] += 1,
            None => unstated += 1,
        }
        if verification == "judgement" {
            match bare(requirement.value("verifier")) {
                "agent" => agent += 1,
                "person" => person += 1,
                _ => {}
            }
        }
    }
    let mut parts: Vec<String> = kinds
        .iter()
        .zip(tally)
        .map(|(k, n)| format!("{n} {k}"))
        .collect();
    if unstated > 0 {
        parts.push(format!("{unstated} unstated"));
    }
    // Requirements approved before a judgement had to name its verifier name none.
    let unnamed = tally[3] - agent - person;
    let named = if unnamed > 0 {
        format!(", {unnamed} naming none")
    } else {
        String::new()
    };
    say!(
        "  by verification: {} ({agent} by an agent, {person} by a person{named})",
        parts.join(", ")
    );
    say!(
        "  {} of {} rest on evaluation or judgement, not on a mechanical check",
        tally[2] + tally[3],
        in_force.len()
    );
}

/// What `check` leaves to `status` because the artifact is approved and
/// frozen: a rejected provider under it, a citation of a target revised or
/// retired since, and an artifact nothing connects (REQ-0143, ADR-1470).
fn frozen_findings(record: &Record, known: &BTreeMap<String, &Doc>) -> Vec<String> {
    let mut out = Vec::new();
    let mut under_rejected: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    let mut suspected = Vec::new();
    let mut cited = BTreeSet::new();
    let mut citing = BTreeSet::new();
    for doc in known.values() {
        for key in &record.layout.relations {
            if let Some(field) = doc.field(key) {
                for found in record
                    .ids
                    .find_iter(&field.value)
                    .filter(|m| known.contains_key(m.as_str()))
                {
                    cited.insert(found.as_str().to_string());
                    citing.insert(bare(doc.id()).to_string());
                }
            }
        }
        if !approved(doc) {
            continue;
        }
        for (path, provider) in providers(record, known, doc) {
            if bare(provider.value("status")) == "rejected" {
                under_rejected
                    .entry(path.last().cloned().unwrap_or_default())
                    .or_default()
                    .insert(bare(doc.id()).to_string());
            }
        }
        for (field, id, _) in suspects(record, known, doc) {
            suspected.push(format!("{} {} {id}", bare(doc.id()), field.key));
        }
    }
    for (provider, under) in under_rejected {
        let noun = if under.len() == 1 {
            "artifact"
        } else {
            "artifacts"
        };
        out.push(format!(
            "{provider}, rejected, under {} approved {noun}: {}",
            under.len(),
            under.into_iter().collect::<Vec<_>>().join(", ")
        ));
    }
    if !suspected.is_empty() {
        let noun = if suspected.len() == 1 {
            "citation"
        } else {
            "citations"
        };
        out.push(format!(
            "{} suspect {noun} in approved artifacts: {}",
            suspected.len(),
            suspected.join(", ")
        ));
    }
    let alone: Vec<&str> = known
        .iter()
        .filter(|(id, doc)| {
            matches!(bare(doc.value("status")), "approved" | "live")
                && !cited.contains(*id)
                && !citing.contains(*id)
        })
        .map(|(id, _)| id.as_str())
        .collect();
    if !alone.is_empty() {
        out.push(format!(
            "unconnected, citing nothing and cited by nothing: {}",
            alone.join(", ")
        ));
    }
    out
}

fn template(rest: &[String]) -> u8 {
    let [kind] = rest else {
        eprintln!(
            "usage: paw template <kind>, where a kind is one of {}",
            TEMPLATES.join(", ")
        );
        return USAGE;
    };
    if !TEMPLATES.contains(&kind.as_str()) {
        eprintln!(
            "paw template: no kind is named {kind}; the kinds are {}",
            TEMPLATES.join(", ")
        );
        return USAGE;
    }
    // The profile is configuration, and configuration the harness owns is TOML.
    let file = if kind == "profile" {
        "profile.toml".to_string()
    } else {
        format!("{kind}.md")
    };
    let repository = profile::repository_root();
    let own = repository.join(".meowpaw").join("templates").join(&file);
    if own.is_file() {
        say!("{}", own.display());
        return CLEAN;
    }
    let unit = match layout_path() {
        Ok(path) => path
            .parent()
            .and_then(Path::parent)
            // The launcher names the layout through `bin/..`, and the path a
            // person reads should name the unit directly.
            .map(|u| {
                u.canonicalize()
                    .unwrap_or(u.to_path_buf())
                    .join("templates")
                    .join(&file)
            }),
        Err(reason) => {
            say!("paw template: no template was found: {reason}");
            return UNCHECKED;
        }
    };
    match unit {
        Some(path) if path.is_file() => {
            say!("{}", path.display());
            CLEAN
        }
        Some(path) => {
            say!(
                "paw template: the unit has no template for {kind} at {}",
                path.display()
            );
            FOUND
        }
        None => {
            say!("paw template: no template was found for {kind}");
            UNCHECKED
        }
    }
}

fn show(rest: &[String]) -> u8 {
    let [id] = rest else {
        eprintln!("usage: paw show <id>");
        return USAGE;
    };
    let (record, _, _) = match open_record("show") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let known = known(&record);
    let Some(doc) = known.get(id.as_str()) else {
        say!("paw show: {id} resolves to nothing in the record");
        return FOUND;
    };
    say!(
        "{id} {}, {}: {}",
        kind_of(&record, doc),
        bare(doc.value("status")),
        doc.shown
    );
    let heading = title(doc);
    if heading != id.as_str() {
        say!("{heading}");
    }
    let first = doc
        .text
        .split("\n\n")
        .find(|p| !(p.starts_with("---") || p.trim_start().starts_with('#') || p.trim().is_empty()))
        .map(|p| p.split_whitespace().collect::<Vec<_>>().join(" "))
        .unwrap_or_default();
    if !first.is_empty() {
        say!("{first}");
    }
    say!();
    say!("Names");
    let mut named = false;
    for key in &record.layout.relations {
        if let Some(field) = doc.field(key) {
            let ids: Vec<String> = record
                .ids
                .find_iter(&field.value)
                .map(|m| {
                    let marked = known
                        .get(m.as_str())
                        .filter(|_| key != "supersedes")
                        .and_then(|target| suspect(&record, doc, target));
                    match marked {
                        Some(why) if why.starts_with("revised") => {
                            format!("{} (suspect: {why}, after this record)", m.as_str())
                        }
                        Some(why) => format!("{} (suspect: {why})", m.as_str()),
                        None => m.as_str().to_string(),
                    }
                })
                .collect();
            if !ids.is_empty() {
                say!("  {key}: {}", ids.join(", "));
                named = true;
            }
        }
    }
    if !named {
        say!("  nothing");
    }
    if kind_of(&record, doc) == "requirement" {
        say!();
        say!("State");
        let records = closing_records(&record, id);
        let by = postponed_by(&record, id);
        let violated = violated_by(&record, id);
        match requirement_state(&records, by.as_deref(), &violated) {
            "postponed" => say!("  postponed by {}", by.unwrap_or_default()),
            "reopened by a defect" => say!("  open, violated by {}", violated.join(", ")),
            "closed" => say!("  closed"),
            state => say!("  open, {state}"),
        }
        for (name, mark) in &records {
            let done = if *mark == 'x' { "done" } else { "open" };
            say!("  {name} {done}");
        }
    }
    say!();
    say!("Cited by");
    let mut cited: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    for other in &record.docs {
        if other.path == doc.path {
            continue;
        }
        let mut in_field = false;
        for key in &record.layout.relations {
            if let Some(field) = other.field(key)
                && record.ids.find_iter(&field.value).any(|m| m.as_str() == id)
            {
                let who = if bare(other.id()).is_empty() {
                    other.shown.clone()
                } else {
                    bare(other.id()).to_string()
                };
                cited.entry(key.clone()).or_default().insert(who);
                in_field = true;
            }
        }
        if !in_field && record.ids.find_iter(&other.text).any(|m| m.as_str() == id) {
            cited
                .entry("body".into())
                .or_default()
                .insert(other.shown.clone());
        }
    }
    if cited.is_empty() {
        say!("  nothing");
    }
    for key in record
        .layout
        .relations
        .iter()
        .map(String::as_str)
        .chain(std::iter::once("body"))
    {
        if let Some(who) = cited.get(key) {
            say!(
                "  {key}: {}",
                who.iter().cloned().collect::<Vec<_>>().join(", ")
            );
        }
    }
    CLEAN
}

/// The agent a brief names where `--agent` names none: the platform's own
/// agent, which the implement step dispatches because no unit ships an
/// implementer (TSK-4945).
const BRIEF_AGENT: &str = "general-purpose";

/// What a delegated agent reports, as ADR-1710 and ADR-2730 state it.
const BRIEF_REPORT: &str =
    "Report on your first line `outcome:` and one of DONE, DONE_WITH_CONCERNS,
NEEDS_CONTEXT or BLOCKED. Below it, name the test that closes each planned
outcome, each stage you ran with its command and exit status, and each file
you changed. If a tool call is denied, end with `outcome: BLOCKED`, naming the
tool and what it was called on, and make no other call for it.

A pull request carrying this work names the record, RECORD, and the command
that prints this brief, `paw brief RECORD`, and names no agent, model or vendor.";

/// Lines with the blank ones at either end removed, joined as they stood.
fn trimmed(lines: &[&str]) -> String {
    let start = lines.iter().position(|l| !l.trim().is_empty());
    let end = lines.iter().rposition(|l| !l.trim().is_empty());
    match (start, end) {
        (Some(start), Some(end)) => lines[start..=end].join("\n"),
        _ => String::new(),
    }
}

/// A section's text, copied as it stands.
fn section_text(doc: &Doc, name: &str) -> String {
    let lines: Vec<&str> = section_lines(doc, name)
        .into_iter()
        .map(|(_, l)| l)
        .collect();
    trimmed(&lines)
}

/// The text under a document's title: up to its first section where `whole`
/// is false, and to its end where it is true.
fn under_title(doc: &Doc, whole: bool) -> String {
    let lines: Vec<&str> = doc.text.lines().collect();
    let Some(heading) = lines.iter().position(|l| l.starts_with("# ")) else {
        return String::new();
    };
    let rest = &lines[heading + 1..];
    let end = if whole {
        rest.len()
    } else {
        rest.iter()
            .position(|l| l.starts_with("## "))
            .unwrap_or(rest.len())
    };
    trimmed(&rest[..end])
}

/// Prints one copy from the record inside a fence longer than any run of
/// backticks in it, so the copy reaches the agent byte for byte (REQ-0814).
fn quote(from: &str, text: &str) {
    if text.is_empty() {
        return;
    }
    let mut longest = 0;
    let mut run = 0;
    for c in text.chars() {
        run = if c == '`' { run + 1 } else { 0 };
        longest = longest.max(run);
    }
    let fence = "`".repeat((longest + 1).max(3));
    say!("from {from}");
    say!("{fence}text");
    say!("{text}");
    say!("{fence}");
    say!();
}

fn brief(rest: &[String]) -> u8 {
    let (id, agent) = match rest {
        [id] => (id, BRIEF_AGENT),
        [id, flag, agent] if flag == "--agent" && !agent.is_empty() => (id, agent.as_str()),
        _ => {
            eprintln!("usage: paw brief <record> [--agent <unit>:<agent>]");
            return USAGE;
        }
    };
    let (record, _, _) = match open_record("brief") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let known = known(&record);
    let Some(doc) = known.get(id.as_str()) else {
        say!("paw brief: {id} resolves to nothing in the record");
        return FOUND;
    };
    let kind = kind_of(&record, doc);
    if !matches!(kind, "decision" | "defect") {
        say!("paw brief: {id} is a {kind}, and only a decision or a defect has a brief");
        return FOUND;
    }
    say!("agent: {agent}");
    say!("record: {id}, a {kind}");
    say!();

    say!("# What to build");
    say!();
    quote(&format!("{id}, its title and opening: {}", doc.shown), &{
        let opening = under_title(doc, false);
        format!("{}\n\n{opening}", title(doc))
            .trim_end()
            .to_string()
    });
    if kind == "decision" {
        quote(&format!("{id}, Decision"), &section_text(doc, "Decision"));
    } else {
        quote(
            &format!("{id}, What it should do, and why"),
            &section_text(doc, "What it should do, and why"),
        );
    }
    quote(&format!("{id}, Plan"), &section_text(doc, "Plan"));

    say!("# Constraints");
    say!();
    let names = doc.value(if kind == "decision" {
        "addresses"
    } else {
        "violates"
    });
    let named: Vec<String> = record
        .ids
        .find_iter(names)
        .map(|m| m.as_str().to_string())
        .collect();
    for requirement in &named {
        match known.get(requirement.as_str()) {
            Some(cited) => quote(
                &format!("{requirement}: {}", cited.shown),
                &under_title(cited, true),
            ),
            None => say!("from {requirement}, which resolves to nothing in the record"),
        }
    }
    quote(
        &format!("{id}, How I will know it was realised"),
        &section_text(doc, "How I will know it was realised"),
    );
    quote(
        &format!("{id}, What this does not settle"),
        &section_text(doc, "What this does not settle"),
    );

    say!("# Interfaces");
    say!();
    for spec in of_kind(&record, "specification") {
        let stated: Vec<&str> = record
            .ids
            .find_iter(spec.value("states"))
            .map(|m| m.as_str())
            .filter(|r| named.iter().any(|c| c == r))
            .collect();
        if !stated.is_empty() {
            say!(
                "spec: {} states {}: {}",
                bare(spec.id()),
                stated.join(", "),
                spec.shown
            );
        }
    }
    say!();

    say!("# Report back");
    say!();
    quote(
        "the method, ADR-1710 and ADR-2730",
        &BRIEF_REPORT.replace("RECORD", id),
    );
    CLEAN
}

const INDEX_OPEN: &str = "<!-- meow-flow index -->";
const INDEX_CLOSE: &str = "<!-- /meow-flow index -->";

/// A kind by its name or its artifact word, such as `decision` or `adr`.
fn kind_named(record: &Record, word: &str) -> Option<usize> {
    record
        .layout
        .kinds
        .iter()
        .position(|k| k.name == word || k.artifact == word)
}

/// What an artifact concluded, in one line: a requirement's statement, a
/// research record's summary, and otherwise its title.
fn conclusion(record: &Record, doc: &Doc) -> String {
    let kind = kind_of(record, doc);
    let paragraph = |text: &str| -> String {
        text.split("\n\n")
            .map(str::trim)
            .find(|p| {
                !p.is_empty()
                    && !p.starts_with('#')
                    && !p.starts_with("---")
                    && !p.starts_with("<!--")
            })
            .map(|p| p.split_whitespace().collect::<Vec<_>>().join(" "))
            .unwrap_or_default()
    };
    let text = match kind {
        "requirement" => paragraph(doc.text.splitn(3, "\n---\n").last().unwrap_or("")),
        "research" => {
            let summary: Vec<&str> = section_lines(doc, "Summary")
                .into_iter()
                .map(|(_, l)| l)
                .collect();
            let first = paragraph(&summary.join("\n"));
            first
                .split_inclusive(". ")
                .next()
                .unwrap_or(&first)
                .trim()
                .to_string()
        }
        _ => title(doc),
    };
    text.replace("**", "").replace('|', "\\|")
}

/// A path from the directory holding `from` to `to`, both under one root.
fn relative_link(from: &str, to: &str) -> String {
    let base: Vec<&str> = from.split('/').collect();
    let base = &base[..base.len().saturating_sub(1)];
    let target: Vec<&str> = to.split('/').collect();
    let common = base.iter().zip(&target).take_while(|(a, b)| a == b).count();
    let mut parts: Vec<String> =
        std::iter::repeat_n("..".to_string(), base.len() - common).collect();
    parts.extend(target[common..].iter().map(|s| s.to_string()));
    parts.join("/")
}

/// The generated index of a kind, the block between the markers.
fn generate_index(record: &Record, k: usize) -> Option<String> {
    let kind = &record.layout.kinds[k];
    let index = kind.index.as_deref()?;
    let mut docs: Vec<&Doc> = record
        .docs
        .iter()
        .filter(|d| d.kind == Some(k) && d.relative != index && !bare(d.id()).is_empty())
        .collect();
    docs.sort_by(|a, b| bare(a.id()).cmp(bare(b.id())));
    let mut statuses: BTreeMap<String, usize> = BTreeMap::new();
    for doc in &docs {
        *statuses
            .entry(bare(doc.value("status")).to_string())
            .or_default() += 1;
    }
    let mut out = String::new();
    let counted: Vec<String> = statuses.iter().map(|(s, n)| format!("{n} {s}")).collect();
    out.push_str(&format!(
        "{} in all: {}.\n\n",
        count(docs.len(), &kind.name),
        counted.join(", ")
    ));
    let header = [
        "Identifier".to_string(),
        format!(
            "What it {}",
            if kind.name == "requirement" {
                "requires"
            } else {
                "concluded"
            }
        ),
        "Status".to_string(),
    ];
    let rows: Vec<[String; 3]> = docs
        .iter()
        .map(|doc| {
            let id = bare(doc.id());
            [
                format!("[{id}]({})", relative_link(index, &doc.relative)),
                conclusion(record, doc),
                bare(doc.value("status")).to_string(),
            ]
        })
        .collect();
    out.push_str(&aligned_table(&header, &rows));
    let amended = Regex::new(r"\*\*Amended by ((?:ADR|BUG|EPC)-\d{4})").expect("amendment pattern");
    let amendments: Vec<String> = docs
        .iter()
        .filter_map(|doc| {
            let by: Vec<&str> = amended
                .captures_iter(&doc.text)
                .filter_map(|c| c.get(1))
                .map(|m| m.as_str())
                .collect();
            (!by.is_empty()).then(|| format!("{} by {}", bare(doc.id()), by.join(" and ")))
        })
        .collect();
    if !amendments.is_empty() {
        out.push_str(&format!("\nAmended: {}.\n", amendments.join("; ")));
    }
    let topical = docs.iter().any(|d| d.field("topic").is_some());
    if docs.len() > 36 && topical {
        let mut topics: BTreeMap<String, Vec<&str>> = BTreeMap::new();
        for doc in &docs {
            topics
                .entry(bare(doc.value("topic")).to_string())
                .or_default()
                .push(bare(doc.id()));
        }
        out.push_str("\nBy topic:\n\n");
        for (topic, ids) in &topics {
            out.push_str(&format!("- {topic}: {}\n", ids.join(", ")));
        }
    }
    Some(out)
}

/// A table padded as the Markdown formatter leaves it, each column as wide as
/// its widest cell, so a written index passes the format check unchanged.
fn aligned_table(header: &[String; 3], rows: &[[String; 3]]) -> String {
    let mut widths: [usize; 3] = std::array::from_fn(|i| header[i].chars().count().max(3));
    for row in rows {
        for (width, cell) in widths.iter_mut().zip(row) {
            *width = (*width).max(cell.chars().count());
        }
    }
    let line = |cells: [&str; 3]| {
        let padded: Vec<String> = cells
            .iter()
            .zip(widths)
            .map(|(cell, width)| format!("{cell}{}", " ".repeat(width - cell.chars().count())))
            .collect();
        format!("| {} |\n", padded.join(" | "))
    };
    let mut out = line([&header[0], &header[1], &header[2]]);
    let rules = widths.map(|width| "-".repeat(width));
    out.push_str(&line([&rules[0], &rules[1], &rules[2]]));
    for row in rows {
        out.push_str(&line([&row[0], &row[1], &row[2]]));
    }
    out
}

/// A block's text as a formatter leaves its meaning: blank lines, the padding
/// in a table's cells and the length of its separator rules don't count.
fn normalised(text: &str) -> Vec<String> {
    let rule = Regex::new(r"-{3,}").expect("rule pattern");
    text.lines()
        .map(|line| {
            let line = line.split_whitespace().collect::<Vec<_>>().join(" ");
            let line = line.replace("| ", "|").replace(" |", "|");
            rule.replace_all(&line, "---").into_owned()
        })
        .filter(|line| !line.is_empty())
        .collect()
}

/// The block between the markers in an index file's text, if it has one.
fn generated_block(text: &str) -> Option<(usize, usize)> {
    markers(text).map(|(_, open, close, _)| (open, close))
}

/// Where the block's markers sit: the opening marker's start, the block's
/// start and end, and the closing marker's end.
fn markers(text: &str) -> Option<(usize, usize, usize, usize)> {
    let start = text.find(INDEX_OPEN)?;
    let open = start + INDEX_OPEN.len();
    let close = open + text[open..].find(INDEX_CLOSE)?;
    Some((start, open, close, close + INDEX_CLOSE.len()))
}

fn index_command(rest: &[String]) -> u8 {
    let (word, write) = match rest {
        [word] => (word, false),
        [word, flag] if flag == "--write" => (word, true),
        _ => {
            eprintln!("usage: paw index <kind> [--write]");
            return USAGE;
        }
    };
    let (record, _, root) = match open_record("index") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let Some(k) = kind_named(&record, word) else {
        let kinds: Vec<&str> = record
            .layout
            .kinds
            .iter()
            .filter(|k| k.index.is_some())
            .map(|k| k.name.as_str())
            .collect();
        eprintln!(
            "paw index: no kind is named {word}; the kinds with an index are {}",
            kinds.join(", ")
        );
        return USAGE;
    };
    let Some(block) = generate_index(&record, k) else {
        say!(
            "paw index: a {} has no index file in the layout",
            record.layout.kinds[k].name
        );
        return FOUND;
    };
    if !write {
        print!("{block}");
        return CLEAN;
    }
    let path = root.join(record.layout.kinds[k].index.as_deref().unwrap_or_default());
    let text = std::fs::read_to_string(&path).unwrap_or_default();
    let Some((start, _, _, end)) = markers(&text) else {
        say!(
            "paw index: {} has no {INDEX_OPEN} block to write into",
            path.display()
        );
        return FOUND;
    };
    // Writing moves an index still carrying the old markers onto the new ones.
    // The blank line before the closing marker is where the formatter puts it
    // after a list.
    let updated = format!(
        "{}{INDEX_OPEN}\n\n{}\n\n{INDEX_CLOSE}{}",
        &text[..start],
        block.trim_end(),
        &text[end..]
    );
    if updated != text {
        // Written beside the index and renamed into place, so an interrupted
        // write leaves the old index or the new one and never half of either.
        let temporary = path.with_extension("md.meow-tmp");
        let written =
            std::fs::write(&temporary, updated).and_then(|_| std::fs::rename(&temporary, &path));
        if let Err(e) = written {
            let _ = std::fs::remove_file(&temporary);
            say!("paw index: {}: {e}", path.display());
            return FOUND;
        }
    }
    say!(
        "paw index: wrote the {} index to {}",
        record.layout.kinds[k].name,
        path.display()
    );
    CLEAN
}

/// The next identifier to allocate for a kind (ADR-1180): a requirement's
/// next free number above its topic's highest, stepping by two, a new topic a
/// block a hundred above the highest, research the next number, and every other
/// kind the next block of ten. No identifier any file carries is given again.
fn new_identifier(rest: &[String]) -> u8 {
    let (word, topic) = match rest {
        [word] => (word, None),
        [word, flag, topic] if flag == "--topic" => (word, Some(topic.as_str())),
        _ => {
            eprintln!("usage: paw new <kind> [--topic <topic>]");
            return USAGE;
        }
    };
    let (record, _, _) = match open_record("new") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    if kind_named(&record, word).is_some_and(|k| record.layout.kinds[k].archived) {
        say!("paw new: the {word} is retired (ADR-3090); a decision or a defect carries its plan");
        return FOUND;
    }
    let Some(k) = kind_named(&record, word).filter(|&k| record.layout.kinds[k].prefix.is_some())
    else {
        let kinds: Vec<&str> = record
            .layout
            .kinds
            .iter()
            .filter(|k| k.prefix.is_some())
            .map(|k| k.name.as_str())
            .collect();
        eprintln!(
            "paw new: no numbered kind is named {word}; the kinds are {}",
            kinds.join(", ")
        );
        return USAGE;
    };
    let kind = &record.layout.kinds[k];
    let prefix = kind.prefix.clone().unwrap_or_default();
    let number = Regex::new(&format!(r"\b{prefix}-(\d{{4}})\b")).expect("identifier pattern");
    // Taken: every identifier of the kind that any file names, withdrawn ones
    // and citations of missing ones included, because a cited number is spent.
    let mut taken = BTreeSet::new();
    for doc in record.docs.iter().chain(&record.outside) {
        for c in number.captures_iter(&doc.text) {
            if let Ok(n) = c[1].parse::<u32>() {
                taken.insert(n);
            }
        }
        if let Some(c) = doc
            .path
            .file_name()
            .and_then(|n| n.to_str())
            .and_then(|n| number.captures(n))
            && let Ok(n) = c[1].parse::<u32>()
        {
            taken.insert(n);
        }
    }
    let highest = taken.iter().max().copied().unwrap_or(0);
    let (mut next, step) = if kind.name == "requirement" {
        let Some(topic) = topic else {
            eprintln!(
                "paw new: a requirement is allocated in its topic's block; name it with --topic"
            );
            return USAGE;
        };
        let in_topic: Vec<u32> = of_kind(&record, "requirement")
            .iter()
            .filter(|d| bare(d.value("topic")) == topic)
            .filter_map(|d| {
                bare(d.id())
                    .strip_prefix(&format!("{prefix}-"))
                    .and_then(|n| n.parse().ok())
            })
            .collect();
        match in_topic.iter().max() {
            Some(top) => (top + 2, 2),
            None => ((highest / 100 + 1) * 100, 2),
        }
    } else if kind.name == "research" || kind.name == "insight" {
        // Nothing is written later between two of these, so they need no gaps.
        (highest + 1, 1)
    } else {
        ((highest / 10 + 1) * 10, 10)
    };
    while taken.contains(&next) {
        next += step;
    }
    if next > 9999 {
        say!("paw new: the {} block is full", kind.name);
        return FOUND;
    }
    say!("{prefix}-{next:04}");
    CLEAN
}

/// Each kind's artifacts by status, and the identifiers, for a migration's
/// evidence before and after: a lost artifact fails no other check (REQ-3020).
fn count_record(rest: &[String]) -> u8 {
    if !rest.is_empty() {
        eprintln!("usage: paw count");
        return USAGE;
    }
    let (record, _, _) = match open_record("count") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    for (k, kind) in record.layout.kinds.iter().enumerate() {
        let index = kind.index.as_deref();
        let docs: Vec<&Doc> = record
            .docs
            .iter()
            .filter(|d| d.kind == Some(k) && Some(d.relative.as_str()) != index && !d.is_index)
            .collect();
        let mut statuses: BTreeMap<&str, usize> = BTreeMap::new();
        for doc in &docs {
            *statuses.entry(bare(doc.value("status"))).or_default() += 1;
        }
        let parts: Vec<String> = statuses.iter().map(|(s, n)| format!("{n} {s}")).collect();
        let detail = if parts.is_empty() {
            String::new()
        } else {
            format!(": {}", parts.join(", "))
        };
        say!("{}: {}{detail}", kind.name, docs.len());
    }
    say!("identifiers: {}", known(&record).len());
    CLEAN
}

/// Artifacts whose identifier, title or conclusion carry the words, ranked by
/// how many they carry: identifiers and headings first, never a body
/// (ADR-1180). It reads every artifact, so it says `exhaustive`, and it
/// counts artifacts, never matching lines (ADR-2410).
fn find(rest: &[String]) -> u8 {
    if rest.is_empty() {
        eprintln!("usage: paw find <word>...");
        return USAGE;
    }
    let (record, _, _) = match open_record("find") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let words: Vec<String> = rest.iter().map(|w| w.to_lowercase()).collect();
    let mut hits: Vec<(usize, String, String)> = Vec::new();
    let mut read = 0;
    for doc in &record.docs {
        let id = bare(doc.id());
        if id.is_empty() || doc.is_index {
            continue;
        }
        read += 1;
        let kind = kind_of(&record, doc);
        let concluded = conclusion(&record, doc);
        // A research record's conclusion is its Summary's first sentence;
        // every other conclusion is a title or a statement.
        let named = format!("{id} {}", title(doc)).to_lowercase();
        let section = if kind == "research" && !words.iter().any(|w| named.contains(w.as_str())) {
            "Summary"
        } else {
            "front matter"
        };
        // A requirement's heading is its identifier, so its statement heads it.
        let heading = if title(doc) == id {
            concluded.clone()
        } else {
            title(doc)
        };
        let haystack = format!("{id} {heading} {concluded}").to_lowercase();
        let score = words
            .iter()
            .filter(|w| haystack.contains(w.as_str()))
            .count();
        if score > 0 {
            let line = format!(
                "{id} {kind}, {}: {heading} ({}, {section})",
                bare(doc.value("status")),
                doc.shown
            );
            hits.push((score, id.to_string(), line));
        }
    }
    hits.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
    say!("exhaustive: read {read} artifacts");
    if hits.is_empty() {
        say!("paw find: nothing in the record carries {}", rest.join(" "));
        return FOUND;
    }
    for (_, _, line) in hits.iter().take(20) {
        say!("{line}");
    }
    say!("artifacts matched: {}", hits.len());
    CLEAN
}

/// The text with the value of one front matter field replaced, and every other
/// line, a trailing comment on that line included, as it was (REQ-4602).
fn with_field(text: &str, key: &str, value: &str) -> Option<String> {
    let mut out = String::with_capacity(text.len() + 16);
    let mut opened = false;
    let mut inside = false;
    let mut replaced = false;
    for line in text.split_inclusive('\n') {
        let content = line.trim_end_matches(['\n', '\r']);
        if !opened {
            opened = content == "---";
            inside = opened;
            out.push_str(line);
            continue;
        }
        if inside && content == "---" {
            inside = false;
            out.push_str(line);
            continue;
        }
        let continued = line.starts_with(' ') || line.starts_with('\t');
        if inside
            && !replaced
            && !continued
            && let Some((name, rest)) = content.split_once(':')
            && name.trim() == key
        {
            let comment = rest.find(" #").map(|at| &rest[at..]).unwrap_or("");
            out.push_str(&format!(
                "{key}: {value}{comment}{}",
                &line[content.len()..]
            ));
            replaced = true;
            continue;
        }
        out.push_str(line);
    }
    replaced.then_some(out)
}

/// A file written beside itself and renamed into place, so an interrupted
/// write leaves the old text or the new and never half of either.
fn write_text(path: &Path, text: &str) -> Result<(), String> {
    let temporary = path.with_extension("md.meow-tmp");
    std::fs::write(&temporary, text)
        .and_then(|_| std::fs::rename(&temporary, path))
        .map_err(|e| {
            let _ = std::fs::remove_file(&temporary);
            format!("{}: {e}", path.display())
        })
}

/// Regenerates the index of each kind whose index file carries a generated
/// block, after a write moved a status an index shows (REQ-0575). A kind with
/// no index, or whose index a person writes, is left out without a word.
fn regenerate(kinds: &[String]) {
    let Ok((record, _, root)) = open_record("index") else {
        return;
    };
    let mut seen: Vec<&String> = Vec::new();
    for kind in kinds {
        if seen.contains(&kind) {
            continue;
        }
        seen.push(kind);
        let Some(k) = kind_named(&record, kind) else {
            continue;
        };
        let Some(index) = record.layout.kinds[k].index.as_deref() else {
            continue;
        };
        let carries = std::fs::read_to_string(root.join(index))
            .ok()
            .is_some_and(|text| markers(&text).is_some());
        if carries {
            let _ = index_command(&[kind.clone(), "--write".to_string()]);
        }
    }
}

/// The identifiers a list names as prose: `A`, `A and B`, `A, B and C`.
fn named_list(ids: &[String]) -> String {
    match ids {
        [] => String::new(),
        [one] => one.clone(),
        [init @ .., last] => format!("{} and {last}", init.join(", ")),
    }
}

/// `paw approve <id>...`: moves each draft to `approved` where the checks
/// report nothing about it, and writes nothing otherwise (ADR-2880).
fn approve(rest: &[String]) -> u8 {
    if rest.is_empty() {
        eprintln!("usage: paw approve <id>...");
        return USAGE;
    }
    let (record, repository, root) = match open_record("approve") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let known = known(&record);
    let mut targets: Vec<&Doc> = Vec::new();
    for id in rest {
        match known.get(id.as_str()) {
            None => {
                say!("paw approve: {id} names no record");
                return FOUND;
            }
            Some(doc) if bare(doc.value("status")) != "draft" => {
                say!(
                    "paw approve: {id} is {}, not a draft",
                    bare(doc.value("status"))
                );
                return FOUND;
            }
            Some(doc) => targets.push(doc),
        }
    }
    let mut found = 0;
    for check in CHECKS {
        for finding in run_check(check, &record, &root, &repository) {
            if targets.iter().any(|doc| doc.shown == finding.shown) {
                match finding.line {
                    Some(line) => say!("{}:{}: {}", finding.shown, line, finding.message),
                    None => say!("{}: {}", finding.shown, finding.message),
                }
                found += 1;
            }
        }
    }
    if found > 0 {
        say!(
            "paw approve: {found} finding{} about what you asked to approve; nothing was changed",
            if found == 1 { "" } else { "s" }
        );
        return FOUND;
    }
    let mut written: Vec<String> = Vec::new();
    for doc in &targets {
        let Some(text) = with_field(&doc.text, "status", "approved") else {
            say!(
                "paw approve: {} carries no status line to change",
                doc.shown
            );
            return FOUND;
        };
        if let Err(reason) = write_text(&doc.path, &text) {
            say!("paw approve: {reason}");
            return FOUND;
        }
        written.push(kind_of(&record, doc).to_string());
        say!("paw approve: {} is approved", bare(doc.id()));
    }
    regenerate(&written);
    CLEAN
}

/// `paw withdraw <requirement> --by <decision> --replaced-by <id>...`: writes
/// the tombstone and the status of a requirement (ADR-2880).
fn withdraw(rest: &[String]) -> u8 {
    let usage = "usage: paw withdraw <requirement> --by <decision> --replaced-by <id>...";
    let [id, by_flag, by, replaced_flag, replaced @ ..] = rest else {
        eprintln!("{usage}");
        return USAGE;
    };
    if by_flag != "--by" || replaced_flag != "--replaced-by" || replaced.is_empty() {
        eprintln!("{usage}");
        return USAGE;
    }
    let (record, _, _) = match open_record("withdraw") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let known = known(&record);
    let Some(doc) = known.get(id.as_str()) else {
        say!("paw withdraw: {id} names no record");
        return FOUND;
    };
    if kind_of(&record, doc) != "requirement" || !approved(doc) {
        say!("paw withdraw: {id} is not an approved requirement");
        return FOUND;
    }
    match known.get(by.as_str()) {
        Some(d) if kind_of(&record, d) == "decision" => {}
        _ => {
            say!("paw withdraw: {by} is not a decision in the record");
            return FOUND;
        }
    }
    for other in replaced {
        if !known.contains_key(other.as_str()) || other == id {
            say!("paw withdraw: {other} names no record other than {id}");
            return FOUND;
        }
    }
    // The statement a tombstone quotes: the first paragraph after the heading,
    // leaving out the comment line templates carry.
    let heading = format!("\n# {id}");
    let Some(at) = doc.text.find(&heading) else {
        say!("paw withdraw: {} has no heading `# {id}`", doc.shown);
        return FOUND;
    };
    let after = &doc.text[at + heading.len()..];
    let after = after.split_once('\n').map(|(_, rest)| rest).unwrap_or("");
    let statement: Vec<&str> = after
        .lines()
        .skip_while(|l| l.trim().is_empty() || l.trim_start().starts_with("<!--"))
        .take_while(|l| !l.trim().is_empty())
        .collect();
    let mut quoted = statement.join("\n");
    if let Some(first) = quoted.chars().next() {
        quoted = format!("{}{}", first.to_lowercase(), &quoted[first.len_utf8()..]);
    }
    let head = &doc.text[..at + heading.len()];
    let body = format!(
        "{head}\n\n**Withdrawn. Replaced by {}.**\n\nIt read: {quoted}\n\nWithdrawn by {by}.\n",
        named_list(replaced)
    );
    let Some(text) =
        with_field(&body, "status", "withdrawn").and_then(|t| with_field(&t, "revised", &today()))
    else {
        say!(
            "paw withdraw: {} carries no status or revised line",
            doc.shown
        );
        return FOUND;
    };
    if let Err(reason) = write_text(&doc.path, &text) {
        say!("paw withdraw: {reason}");
        return FOUND;
    }
    say!(
        "paw withdraw: {id} is withdrawn, replaced by {}",
        named_list(replaced)
    );
    regenerate(&["requirement".to_string()]);
    CLEAN
}

/// `paw done <record> --pr <number>`: stores `done` in an approved decision or
/// defect and names the pull request that completes it (REQ-3678).
fn done(rest: &[String]) -> u8 {
    let usage = "usage: paw done <record> --pr <number>";
    let [id, flag, number] = rest else {
        eprintln!("{usage}");
        return USAGE;
    };
    if flag != "--pr" || number.is_empty() || !number.chars().all(|c| c.is_ascii_digit()) {
        eprintln!("{usage}");
        return USAGE;
    }
    let (record, _, _) = match open_record("done") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let known_now = known(&record);
    let Some(doc) = known_now.get(id.as_str()) else {
        say!("paw done: {id} names no record");
        return FOUND;
    };
    let kind = kind_of(&record, doc);
    if !matches!(kind, "decision" | "defect") {
        say!("paw done: {id} is a {kind}, and only a decision or a defect is closed");
        return FOUND;
    }
    match bare(doc.value("status")) {
        "approved" => {}
        other => {
            say!("paw done: {id} is {other}, and only an approved record is closed");
            return FOUND;
        }
    }
    if kind == "decision"
        && !requirements_in(&record, doc.value("addresses")).is_empty()
        && !has_plan(doc)
    {
        say!("paw done: {id} carries no plan");
        return FOUND;
    }
    let first = section_lines(doc, "Closed by")
        .into_iter()
        .map(|(_, line)| line.trim())
        .find(|line| !line.is_empty())
        .unwrap_or("");
    if kind == "defect"
        && (first.is_empty() || first.starts_with("Not") || first.starts_with("Open"))
    {
        say!("paw done: {id}'s Closed by doesn't name the check that closed it");
        return FOUND;
    }
    let text = with_field(&doc.text, "status", "done").and_then(|text| {
        with_field(&text, "pr", number).or_else(|| upgrade::with_added_field(&text, "pr", number))
    });
    let Some(text) = text else {
        say!("paw done: {} carries no status line to change", doc.shown);
        return FOUND;
    };
    if let Err(reason) = write_text(&doc.path, &text) {
        say!("paw done: {reason}");
        return FOUND;
    }
    say!("paw done: {id} is done in pull request {number}");
    regenerate(&[kind.to_string()]);
    CLEAN
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_document_with_an_unusual_name_is_listed_as_it_is() {
        // REQ-2522: a path git would escape reaches the check as the path it is.
        let dir = std::env::temp_dir().join(format!("meow-docs-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let init = profile::reading_git()
            .current_dir(&dir)
            .args(["init", "-q"])
            .output()
            .unwrap();
        assert!(init.status.success());
        let name = "we\"ird\nnamé.md";
        std::fs::write(dir.join(name), "text\n").unwrap();
        let listed = documents(&dir.join("project"), &dir);
        let _ = std::fs::remove_dir_all(&dir);
        assert_eq!(listed, vec![name.to_string()]);
    }

    #[test]
    fn a_flowed_list_is_one_field() {
        let fields = parse_front_matter(
            "---\nid: TSK-1\ncloses:\n  [\n    REQ-0001,\n    REQ-0002,\n  ]\n---\n# T\n",
        )
        .unwrap();
        let closes = fields.iter().find(|f| f.key == "closes").unwrap();
        assert!(closes.value.contains("REQ-0001") && closes.value.contains("REQ-0002"));
        assert_eq!(closes.line, 3);
    }

    #[test]
    fn today_is_a_date() {
        assert!(
            Regex::new(r"^\d{4}-\d{2}-\d{2}$")
                .unwrap()
                .is_match(&today())
        );
    }

    /// A fixture record: a live specification stating a requirement that
    /// elaborates an approved defect, which violates a second requirement
    /// whose statuses the test sets (BUG-1640, TSK-5500).
    fn chain_fixture(first: &str, second: &str) -> (Record, std::path::PathBuf) {
        // The layout is the record's, which the repository ships beside the
        // crate, and the test names it where the binary's own copy doesn't
        // exist.
        // unsafe: a test sets the environment before the fixture reads it.
        unsafe {
            std::env::set_var(
                "MEOW_LAYOUT",
                concat!(
                    env!("CARGO_MANIFEST_DIR"),
                    "/../../plugins/meow-flow/lib/layout.toml"
                ),
            );
        }
        // The statuses name the directory, because the tests run in parallel
        // in one process and share the id.
        let dir = std::env::temp_dir().join(format!(
            "meow-chain-{first}-{second}-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(dir.join(".meowpaw")).unwrap();
        std::fs::create_dir_all(dir.join("project").join("specs")).unwrap();
        std::fs::create_dir_all(dir.join("project").join("requirements")).unwrap();
        std::fs::create_dir_all(dir.join("project").join("bugs")).unwrap();
        std::fs::write(
            dir.join(".meowpaw").join("profile.toml"),
            "[record]\nroot = \"project\"\n",
        )
        .unwrap();
        std::fs::write(
            dir.join("project")
                .join("requirements")
                .join("REQ-0001-first.md"),
            format!(
                "---\nid: REQ-0001\nstatus: {first}\nelaborates: [BUG-0001]\n---\n\n# REQ-0001\n"
            ),
        )
        .unwrap();
        std::fs::write(
            dir.join("project")
                .join("requirements")
                .join("REQ-0002-second.md"),
            format!("---\nid: REQ-0002\nstatus: {second}\n---\n\n# REQ-0002\n"),
        )
        .unwrap();
        std::fs::write(
            dir.join("project").join("bugs").join("BUG-0001-broke.md"),
            "---\nid: BUG-0001\nstatus: approved\nviolates: [REQ-0002]\n---\n\n# BUG-0001\n",
        )
        .unwrap();
        std::fs::write(
            dir.join("project").join("specs").join("SPC-0001-part.md"),
            "---\nid: SPC-0001\nstatus: live\nstates: [REQ-0001]\n---\n\n# SPC-0001\n",
        )
        .unwrap();
        let layout = load_layout().unwrap();
        let record = read_record(layout, &dir, &dir.join("project"));
        (record, dir)
    }

    /// TSK-5140, REQ-3900, REQ-3902: an approved requirement, an approved
    /// decision addressing it, and an epic realising it, each written where
    /// `with` names it, so a test asks for exactly one gap.
    fn gap_fixture(
        requirement: bool,
        decision: bool,
        epic: bool,
        postpones: bool,
    ) -> (Record, std::path::PathBuf) {
        unsafe {
            std::env::set_var(
                "MEOW_LAYOUT",
                concat!(
                    env!("CARGO_MANIFEST_DIR"),
                    "/../../plugins/meow-flow/lib/layout.toml"
                ),
            );
        }
        // Tests run in parallel and two ask for the same shape, so a counter
        // keeps each directory its own.
        static COUNT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
        let count = COUNT.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        let dir = std::env::temp_dir().join(format!(
            "meow-gap-{requirement}-{decision}-{epic}-{postpones}-{}-{count}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(dir.join(".meowpaw")).unwrap();
        std::fs::create_dir_all(dir.join("project").join("requirements")).unwrap();
        std::fs::create_dir_all(dir.join("project").join("adrs")).unwrap();
        std::fs::create_dir_all(dir.join("project").join("epics")).unwrap();
        std::fs::write(
            dir.join(".meowpaw").join("profile.toml"),
            "[record]\nroot = \"project\"\n",
        )
        .unwrap();
        if requirement {
            std::fs::write(
                dir.join("project")
                    .join("requirements")
                    .join("REQ-0001-first.md"),
                "---\nid: REQ-0001\nstatus: approved\nrevised: 2026-01-01\n---\n\n# REQ-0001\n",
            )
            .unwrap();
        }
        if decision {
            let relation = if postpones {
                "postpones: [REQ-0001]"
            } else {
                "addresses: [REQ-0001]"
            };
            std::fs::write(
                dir.join("project").join("adrs").join("ADR-0001-a-choice.md"),
                format!("---\nid: ADR-0001\nstatus: approved\nrevised: 2026-01-01\n{relation}\n---\n\n# 0001. A choice\n"),
            )
            .unwrap();
        }
        if epic {
            std::fs::write(
                dir.join("project").join("epics").join("EPC-0001-a-plan.md"),
                "---\nid: EPC-0001\nstatus: approved\nrevised: 2026-01-01\nrealises: ADR-0001\n---\n\n# A plan\n",
            )
            .unwrap();
        }
        let layout = load_layout().unwrap();
        let record = read_record(layout, &dir, &dir.join("project"));
        (record, dir)
    }

    #[test]
    fn an_active_requirement_without_a_provider_is_reported() {
        // TSK-5140 criterion 1, REQ-3900: an approved requirement names an
        // approved decision that addresses or postpones it.
        let (record, dir) = gap_fixture(true, false, false, false);
        let found = relations(&record);
        let _ = std::fs::remove_dir_all(&dir);
        assert!(
            found
                .iter()
                .any(|f| f.message.contains("REQ-0001") && f.message.contains("REQ-3900")),
            "the providerless requirement went unreported: {:?}",
            found.iter().map(|f| &f.message).collect::<Vec<_>>()
        );
    }

    #[test]
    fn a_provider_clears_the_requirement() {
        // TSK-5140 criterion 1, REQ-3900: the addressing decision is the
        // provider, so no finding.
        let (record, dir) = gap_fixture(true, true, false, false);
        let found = relations(&record);
        let _ = std::fs::remove_dir_all(&dir);
        assert!(
            found.iter().all(|f| !f.message.contains("REQ-3900")),
            "a provided requirement was reported: {:?}",
            found.iter().map(|f| &f.message).collect::<Vec<_>>()
        );
    }

    #[test]
    fn an_addressing_decision_without_a_plan_is_reported() {
        // TSK-5140 criterion 1, REQ-3902: an approved decision that addresses
        // a requirement names an approved epic or direct task.
        let (record, dir) = gap_fixture(true, true, false, false);
        let found = relations(&record);
        let _ = std::fs::remove_dir_all(&dir);
        assert!(
            found
                .iter()
                .any(|f| f.message.contains("ADR-0001") && f.message.contains("REQ-3902")),
            "the planless decision went unreported: {:?}",
            found.iter().map(|f| &f.message).collect::<Vec<_>>()
        );
    }

    #[test]
    fn an_approved_epic_clears_the_decision() {
        // TSK-5140 criterion 1, REQ-3902: the realising epic is the plan.
        let (record, dir) = gap_fixture(true, true, true, false);
        let found = relations(&record);
        let _ = std::fs::remove_dir_all(&dir);
        assert!(
            found.iter().all(|f| !f.message.contains("REQ-3902")),
            "a planned decision was reported: {:?}",
            found.iter().map(|f| &f.message).collect::<Vec<_>>()
        );
    }

    #[test]
    fn a_postponing_only_decision_needs_no_plan() {
        // TSK-5140 criterion 1, REQ-3902: a decision that only postpones
        // defers the work instead of authorising it, so it names no plan.
        let (record, dir) = gap_fixture(true, true, false, true);
        let found = relations(&record);
        let _ = std::fs::remove_dir_all(&dir);
        assert!(
            found.iter().all(|f| !f.message.contains("REQ-3902")),
            "a postponing decision was held to a plan: {:?}",
            found.iter().map(|f| &f.message).collect::<Vec<_>>()
        );
    }

    #[test]
    fn a_violation_behind_a_specification_is_no_provider() {
        // TSK-5500 criterion 1, REQ-0139: a defect's violates names what it
        // moved against, so a withdrawn requirement behind it flags nothing.
        let (record, dir) = chain_fixture("approved", "withdrawn");
        let known = known(&record);
        let found = chains(&record, &known);
        let _ = std::fs::remove_dir_all(&dir);
        assert!(
            found.iter().all(|f| !f.message.contains("REQ-0002")),
            "the walk reached the withdrawn requirement: {:?}",
            found.iter().map(|f| &f.message).collect::<Vec<_>>()
        );
    }

    #[test]
    fn a_draft_behind_a_specification_still_reports() {
        // TSK-5500 criterion 2: the exclusion hides no draft finding.
        let (record, dir) = chain_fixture("draft", "approved");
        let known = known(&record);
        let found = chains(&record, &known);
        let _ = std::fs::remove_dir_all(&dir);
        assert!(
            found.iter().any(|f| f.message.contains("a draft")),
            "the draft provider went unreported: {:?}",
            found.iter().map(|f| &f.message).collect::<Vec<_>>()
        );
    }
}
