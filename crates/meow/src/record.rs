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

const CHECKS: [&str; 7] = ["front-matter", "identifiers", "relations", "index", "coverage", "shape", "rules"];
const CLEAN: u8 = 0;
const FOUND: u8 = 1;
const USAGE: u8 = 2;
const UNCHECKED: u8 = 3;
/// Directories no walk enters: tooling, build output and the harness's own
/// templates, whose placeholders are not citations.
const SKIP: [&str; 4] = ["node_modules", "target", "templates", "_archive"];

struct Kind {
    name: String,
    artifact: String,
    prefix: Option<String>,
    dir: Option<String>,
    file: Option<String>,
    fields: Vec<String>,
    statuses: Vec<String>,
    index: Option<String>,
    sections: Vec<String>,
    draft_sections: Vec<String>,
    first_section: Option<String>,
    required_values: Vec<String>,
    forbidden_fields: Vec<String>,
    rules: Vec<String>,
    draft_rules: Vec<String>,
}

struct Layout {
    fields: Vec<String>,
    relations: Vec<String>,
    index_name: String,
    kinds: Vec<Kind>,
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
        Finding { shown: doc.shown.clone(), line, message }
    }
}

struct Record {
    layout: Layout,
    docs: Vec<Doc>,
    outside: Vec<Doc>,
    ids: Regex,
}

pub fn main(args: &[String]) -> u8 {
    let (verb, rest) = match args.split_first() {
        Some((verb, rest)) => (verb.as_str(), rest),
        None => ("", &[][..]),
    };
    match verb {
        "check" => check(rest),
        "status" => status(rest),
        "ready" => ready(rest),
        "template" => template(rest),
        "show" => show(rest),
        "index" => index_command(rest),
        "new" => new_identifier(rest),
        "find" => find(rest),
        _ => {
            eprintln!(
                "usage: meow-method check [{} | frozen [--base <rev>]] | status | ready <step> <id>... | template <kind> | show <id> | index <kind> [--write] | new <kind> [--topic <topic>] | find <word>...",
                CHECKS.join(" | ")
            );
            USAGE
        }
    }
}

/// The record at the declared root, or the exit code and why it can't be read.
fn open_record(verb: &str) -> Result<(Record, PathBuf, PathBuf), u8> {
    let layout = match load_layout() {
        Ok(layout) => layout,
        Err(reason) => {
            say!("meow-method {verb}: the record was not checked: {reason}");
            return Err(UNCHECKED);
        }
    };
    let repository = profile::repository_root();
    let root = match record_root(&repository) {
        Ok(root) => root,
        Err(reason) => {
            say!("meow-method {verb}: {reason}");
            return Err(FOUND);
        }
    };
    if !root.is_dir() {
        say!("meow-method {verb}: the record's root {} doesn't exist; nothing was checked", root.display());
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
        eprintln!("usage: meow-method check [{}]", CHECKS.join(" | "));
        return USAGE;
    }
    let chosen: Vec<&str> = match rest.first() {
        Some(name) if CHECKS.contains(&name.as_str()) => vec![name.as_str()],
        Some(name) => {
            eprintln!("meow-method check: no check is named {name}; the checks are {}", CHECKS.join(", "));
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
        findings.sort_by(|a, b| (&a.shown, a.line, &a.message).cmp(&(&b.shown, b.line, &b.message)));
        for finding in &findings {
            match finding.line {
                Some(line) => say!("{}:{}: {}", finding.shown, line, finding.message),
                None => say!("{}: {}", finding.shown, finding.message),
            }
        }
        say!("{check}: {} finding{}", findings.len(), if findings.len() == 1 { "" } else { "s" });
        total += findings.len();
    }
    if total == 0 { CLEAN } else { FOUND }
}

/// Where the layout is: `MEOW_LAYOUT`, or `lib/layout.toml` in the unit this
/// binary ships in.
fn layout_path() -> Result<PathBuf, String> {
    match std::env::var_os("MEOW_LAYOUT") {
        Some(path) => Ok(PathBuf::from(path)),
        None => {
            let exe = std::env::current_exe().map_err(|e| e.to_string())?;
            // The binary sits at <unit>/bin/<target>/meow.
            let unit = exe.parent().and_then(Path::parent).and_then(Path::parent);
            Ok(unit.ok_or("the binary is not inside a unit")?.join("lib").join("layout.toml"))
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
        "coverage" => coverage(record),
        "shape" => shape(record),
        _ => rules(record),
    }
}

/// How many findings every check reports on each file, keyed by its shown path.
fn findings_by_file(record: &Record, root: &Path, repository: &Path) -> BTreeMap<String, usize> {
    let mut out = BTreeMap::new();
    for check in CHECKS {
        for finding in run_check(check, record, root, repository) {
            *out.entry(finding.shown).or_insert(0) += 1;
        }
    }
    out
}

/// Whether the record's root is kept by version control: inside a work tree
/// and not ignored by it.
fn under_version_control(root: &Path) -> bool {
    let git = |args: &[&str]| std::process::Command::new("git").args(args).current_dir(root).output().ok();
    let inside = git(&["rev-parse", "--is-inside-work-tree"]).is_some_and(|o| o.status.success());
    let ignored = git(&["check-ignore", "-q", "."]).is_some_and(|o| o.status.success());
    inside && !ignored
}

/// Each task closing a requirement, with its mark, its epic and the issue the
/// epic was verified under, which is empty until it is.
fn closing_tasks(record: &Record, known: &BTreeMap<String, &Doc>, id: &str) -> Vec<(String, char, String, String)> {
    let mut out = Vec::new();
    for task in of_kind(record, "task") {
        if !requirements_in(record, task.value("closes")).contains(id) {
            continue;
        }
        let epic_id = bare(task.value("epic")).to_string();
        let epic = known.get(epic_id.as_str());
        let mark = epic.and_then(|e| marks(e).into_iter().find(|(t, _)| t == bare(task.id())).map(|(_, m)| m)).unwrap_or(' ');
        let checked = epic.map(|e| bare(e.value("checked-at")).to_string()).unwrap_or_default();
        out.push((bare(task.id()).to_string(), mark, epic_id, checked));
    }
    out.sort();
    out
}

/// A requirement's observed state, derived from the tasks closing it (REQ-0584).
fn requirement_state(tasks: &[(String, char, String, String)]) -> &'static str {
    if tasks.iter().any(|(_, mark, _, checked)| *mark == 'x' && !checked.is_empty()) {
        "verified"
    } else if tasks.iter().any(|(_, mark, _, _)| *mark == 'x') {
        "closed and not yet verified"
    } else if tasks.iter().any(|(_, mark, _, _)| *mark != '~') {
        "in a task not yet done"
    } else {
        "checked by nothing"
    }
}

fn check_frozen(rest: &[String]) -> u8 {
    let base = match rest {
        [] => "HEAD".to_string(),
        [flag, rev] if flag == "--base" => rev.clone(),
        _ => {
            eprintln!("usage: meow-method check frozen [--base <rev>]");
            return USAGE;
        }
    };
    let (record, repository, _) = match open_record("check") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let authority = Regex::new(r"(?:Amended|Corrected) by (?:ADR|BUG|EPC)-\d{4}").expect("authority pattern");
    let mut findings = Vec::new();
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else { continue };
        // A living document describes the present and is rewritten freely.
        let own_index = kind.index.as_deref() == Some(doc.relative.as_str());
        if doc.is_index || own_index || kind.statuses.iter().any(|s| s == "live") || Path::new(&doc.shown).is_absolute() {
            continue;
        }
        let Ok(out) = std::process::Command::new("git")
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
        let old = Doc { path: doc.path.clone(), relative: doc.relative.clone(), shown: doc.shown.clone(), fields: parse_front_matter(&before), text: before.clone(), kind: doc.kind, is_index: false };
        if bare(old.value("status")) != "approved" {
            continue;
        }
        if matches!(bare(doc.value("status")), "withdrawn" | "superseded") {
            continue;
        }
        let was: BTreeSet<&str> = before.lines().collect();
        if doc.text.lines().any(|line| !was.contains(line) && authority.is_match(line)) {
            continue;
        }
        let allowed = match kind.name.as_str() {
            "epic" => bare(old.value("checked-at")).is_empty(),
            "task" => frozen_part(&before) == frozen_part(&doc.text),
            _ => false,
        };
        if !allowed {
            findings.push(format!(
                "{}: approved at {base}, and changed since without a line naming its authority; a change to an approved record invalidates its approval",
                doc.shown
            ));
        }
    }
    findings.sort();
    for finding in &findings {
        say!("{finding}");
    }
    say!("frozen: {} finding{}", findings.len(), if findings.len() == 1 { "" } else { "s" });
    if findings.is_empty() { CLEAN } else { FOUND }
}

/// A task's text without what may change after approval: its evidence, its
/// issue and its revision date.
fn frozen_part(text: &str) -> String {
    let mut out = Vec::new();
    let mut in_evidence = false;
    for line in text.lines() {
        if let Some(heading) = line.strip_prefix("## ") {
            in_evidence = heading.trim() == "Evidence";
        }
        if in_evidence || line.starts_with("issue:") || line.starts_with("revised:") {
            continue;
        }
        out.push(line);
    }
    out.join("\n")
}

/// The layout from `MEOW_LAYOUT`, or from the unit this binary ships in.
fn load_layout() -> Result<Layout, String> {
    let path = layout_path()?;
    let text = std::fs::read_to_string(&path).map_err(|e| format!("{}: {e}", path.display()))?;
    let data: toml::Table = text.parse().map_err(|e| format!("{}: {e}", path.display()))?;
    let strings = |table: &toml::Table, key: &str| -> Vec<String> {
        table
            .get(key)
            .and_then(|v| v.as_array())
            .map(|a| a.iter().filter_map(|v| v.as_str().map(str::to_string)).collect())
            .unwrap_or_default()
    };
    let string = |table: &toml::Table, key: &str| table.get(key).and_then(|v| v.as_str()).map(str::to_string);
    let mut kinds = Vec::new();
    for entry in data.get("kind").and_then(|v| v.as_array()).into_iter().flatten() {
        let Some(table) = entry.as_table() else { continue };
        kinds.push(Kind {
            name: string(table, "name").unwrap_or_default(),
            artifact: string(table, "artifact").unwrap_or_default(),
            prefix: string(table, "prefix"),
            dir: string(table, "dir"),
            file: string(table, "file"),
            fields: strings(table, "fields"),
            statuses: strings(table, "statuses"),
            index: string(table, "index"),
            sections: strings(table, "sections"),
            draft_sections: strings(table, "draft_sections"),
            first_section: string(table, "first_section"),
            required_values: strings(table, "required_values"),
            forbidden_fields: strings(table, "forbidden_fields"),
            rules: strings(table, "rules"),
            draft_rules: strings(table, "draft_rules"),
        });
    }
    Ok(Layout {
        fields: strings(&data, "fields"),
        relations: strings(&data, "relations"),
        index_name: string(&data, "index_name").unwrap_or_else(|| "README.md".into()),
        kinds,
    })
}

fn record_root(repository: &Path) -> Result<PathBuf, String> {
    let declared = match profile::read(repository) {
        Profile::Parsed(data) => data
            .get("record")
            .and_then(|r| r.as_table())
            .and_then(|r| r.get("root"))
            .and_then(|r| r.as_str())
            .map(str::to_string),
        Profile::Unparseable(reason) => return Err(format!("the profile can't be read: {reason}")),
        Profile::Absent => None,
    };
    Ok(repository.join(declared.unwrap_or_else(|| "project".into())))
}

fn markdown_under(dir: &Path, leave_out: Option<&Path>, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else { return };
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
    let end = rest.find("\n---\n").map(|i| i + 1).or_else(|| rest.strip_suffix("\n---").map(str::len))?;
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
    let repository = repository.canonicalize().unwrap_or_else(|_| repository.to_path_buf());
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
    Doc { path, relative: String::new(), shown, text, fields, kind: None, is_index: false }
}

fn read_record(layout: Layout, repository: &Path, root: &Path) -> Record {
    let mut paths = Vec::new();
    markdown_under(root, None, &mut paths);
    let mut docs = Vec::new();
    for path in paths {
        let relative = path.strip_prefix(root).unwrap_or(&path).to_string_lossy().replace('\\', "/");
        let mut doc = read_doc(path.clone(), repository);
        doc.relative = relative.clone();
        let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        let parent = relative.rsplit_once('/').map(|(dir, _)| dir).unwrap_or("");
        doc.is_index = name == layout.index_name;
        doc.kind = layout.kinds.iter().position(|kind| {
            kind.file.as_deref() == Some(relative.as_str()) || (kind.dir.as_deref() == Some(parent) && !doc.is_index)
        });
        docs.push(doc);
    }

    let root_canonical = root.canonicalize().unwrap_or_else(|_| root.to_path_buf());
    let mut others = Vec::new();
    markdown_under(repository, Some(&root_canonical), &mut others);
    let outside = others
        .into_iter()
        .filter(|p| !p.canonicalize().map(|c| c.starts_with(&root_canonical)).unwrap_or(false))
        .map(|p| read_doc(p, repository))
        .collect();

    let prefixes: Vec<&str> = layout.kinds.iter().filter_map(|k| k.prefix.as_deref()).collect();
    let ids = Regex::new(&format!(r"\b(?:{})-\d{{4}}\b", prefixes.join("|"))).expect("identifier pattern");
    Record { layout, docs, outside, ids }
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
    for doc in record.docs.iter().filter(|d| !d.is_index) {
        let Some(fields) = &doc.fields else {
            out.push(Finding::at(doc, None, "no front matter".into()));
            continue;
        };
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else {
            out.push(Finding::at(doc, None, "an artifact of no known kind".into()));
            continue;
        };
        for key in record.layout.fields.iter().chain(&kind.fields) {
            if !fields.iter().any(|f| &f.key == key) {
                out.push(Finding::at(doc, None, format!("front matter has no {key}")));
            }
        }
        for key in &kind.forbidden_fields {
            if let Some(field) = doc.field(key) {
                out.push(Finding::at(doc, Some(field.line), format!("carries {key}, which a {} never does", kind.name)));
            }
        }
        for key in &kind.required_values {
            if let Some(field) = doc.field(key) {
                let value = bare(&field.value).trim_matches(|c: char| c == '[' || c == ']' || c.is_whitespace());
                if value.is_empty() {
                    out.push(Finding::at(doc, Some(field.line), format!("{key} is empty, and a {} must fill it", kind.name)));
                }
            }
        }
        if let Some(field) = doc.field("artifact") {
            if bare(&field.value) != kind.artifact {
                out.push(Finding::at(doc, Some(field.line), format!("artifact is {}, where a {} is {}", bare(&field.value), kind.name, kind.artifact)));
            }
        }
        if let Some(field) = doc.field("status") {
            let status = bare(&field.value);
            if !kind.statuses.iter().any(|s| s == status) {
                out.push(Finding::at(doc, Some(field.line), format!("status {status} is not one a {} stores: {}", kind.name, kind.statuses.join(", "))));
            }
        }
        if let Some(field) = doc.field("revised") {
            let revised = bare(&field.value);
            if !date.is_match(revised) {
                out.push(Finding::at(doc, Some(field.line), format!("revised is not a date: {revised}")));
            } else if revised > today.as_str() {
                out.push(Finding::at(doc, Some(field.line), format!("revised is in the future: {revised}")));
            }
        }
    }
    out
}

/// Identifier to the document that carries it, first one wins.
fn known(record: &Record) -> BTreeMap<String, &Doc> {
    let mut out = BTreeMap::new();
    for doc in &record.docs {
        if let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) {
            if kind.prefix.is_some() && !doc.id().is_empty() {
                out.entry(bare(doc.id()).to_string()).or_insert(doc);
            }
        }
    }
    out
}

fn identifiers(record: &Record) -> Vec<Finding> {
    let mut out = Vec::new();
    let mut seen: BTreeMap<String, &Doc> = BTreeMap::new();
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else { continue };
        let Some(prefix) = &kind.prefix else { continue };
        let name = doc.path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        let named = Regex::new(&format!(r"^({prefix}-\d{{4}})-[a-z0-9-]+\.md$")).expect("name pattern");
        let Some(from_name) = named.captures(name).map(|c| c[1].to_string()) else {
            out.push(Finding::at(doc, None, format!("the name doesn't have the form {prefix}-NNNN-<slug>.md")));
            continue;
        };
        let declared = bare(doc.id());
        if declared != from_name {
            let line = doc.field("id").map(|f| f.line);
            out.push(Finding::at(doc, line, format!("declares id {}, where its name says {from_name}", if declared.is_empty() { "(none)" } else { declared })));
        }
        match seen.get(&from_name) {
            Some(first) => out.push(Finding::at(doc, None, format!("{from_name} is also allocated to {}", first.shown))),
            None => {
                seen.insert(from_name, doc);
            }
        }
    }
    let known = known(record);
    for doc in record.docs.iter().chain(&record.outside) {
        let mut cited = BTreeSet::new();
        for found in record.ids.find_iter(&doc.text).filter(|m| m.as_str().starts_with("REQ-")) {
            if !known.contains_key(found.as_str()) && cited.insert(found.as_str()) {
                out.push(Finding::at(doc, Some(line_of(&doc.text, found.start())), format!("cites {}, which has no file", found.as_str())));
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
            let Some(field) = doc.field(key) else { continue };
            // A relation is bare identifiers, because a link carries a path and
            // a path changes when a repository is reorganised.
            let rest = record.ids.replace_all(bare(&field.value), "");
            if rest.chars().any(|c| !(c.is_whitespace() || c == ',' || c == '[' || c == ']')) {
                out.push(Finding::at(doc, Some(field.line), format!("{key} holds more than bare identifiers: {}", bare(&field.value))));
            }
            for found in record.ids.find_iter(&field.value) {
                if !known.contains_key(found.as_str()) {
                    out.push(Finding::at(doc, Some(field.line), format!("{key} names {}, which has no file", found.as_str())));
                }
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
                        out.push(Finding::at(doc, Some(i + 1), format!("names {}, which has no file", found.as_str())));
                    }
                }
            }
        }
        let dir = doc.path.parent().unwrap_or(Path::new("."));
        for found in link.captures_iter(&doc.text) {
            let target = found.get(1).or(found.get(2)).map(|m| m.as_str()).unwrap_or("");
            if target.starts_with("http://") || target.starts_with("https://") || target.starts_with('#') || target.starts_with("mailto:") {
                continue;
            }
            let file = target.split('#').next().unwrap_or("");
            if !file.is_empty() && !dir.join(file).exists() {
                let line = line_of(&doc.text, found.get(0).map(|m| m.start()).unwrap_or(0));
                out.push(Finding::at(doc, Some(line), format!("links to {target}, which doesn't exist")));
            }
        }
    }
    out
}

fn index(record: &Record, root: &Path, repository: &Path) -> Vec<Finding> {
    let mut out = Vec::new();
    for (k, kind) in record.layout.kinds.iter().enumerate() {
        let (Some(index), Some(prefix)) = (&kind.index, &kind.prefix) else { continue };
        let path = root.join(index);
        let Some(listing) = record.docs.iter().find(|d| d.path == path) else {
            out.push(Finding { shown: shown(&path, repository), line: None, message: format!("the index of each {} doesn't exist", kind.name) });
            continue;
        };
        if let Some((open, close)) = generated_block(&listing.text) {
            let generated = generate_index(record, k).unwrap_or_default();
            if normalised(&listing.text[open..close]) != normalised(&generated) {
                out.push(Finding::at(listing, Some(line_of(&listing.text, open)), format!("its generated block is out of date; run meow-method index {} --write", kind.name)));
            }
        }
        let own = Regex::new(&format!(r"\b{prefix}-\d{{4}}\b")).expect("identifier pattern");
        let mut listed: BTreeMap<&str, usize> = BTreeMap::new();
        for found in own.find_iter(&listing.text) {
            listed.entry(found.as_str()).or_insert_with(|| line_of(&listing.text, found.start()));
        }
        let mut present = BTreeSet::new();
        for doc in record.docs.iter().filter(|d| d.kind == Some(k) && d.path != path) {
            let id = bare(doc.id());
            present.insert(id.to_string());
            if !id.is_empty() && !listed.contains_key(id) {
                out.push(Finding::at(listing, None, format!("doesn't list {id}, {}", doc.shown)));
            }
        }
        for (id, line) in listed {
            if !present.contains(id) && Some(id) != listing.field("id").map(|f| bare(&f.value)) {
                out.push(Finding::at(listing, Some(line), format!("lists {id}, which has no file")));
            }
        }
    }
    out
}

fn of_kind<'a>(record: &'a Record, name: &str) -> Vec<&'a Doc> {
    let Some(k) = record.layout.kinds.iter().position(|kind| kind.name == name) else { return Vec::new() };
    record.docs.iter().filter(|d| d.kind == Some(k)).collect()
}

/// The index of a document's first line after its front matter.
fn body_start(doc: &Doc) -> usize {
    if !doc.text.starts_with("---") {
        return 0;
    }
    doc.text.lines().enumerate().skip(1).find(|(_, l)| l.trim_end() == "---").map(|(i, _)| i + 1).unwrap_or(0)
}

fn requirements_in(record: &Record, text: &str) -> BTreeSet<String> {
    record.ids.find_iter(text).map(|m| m.as_str()).filter(|id| id.starts_with("REQ-")).map(str::to_string).collect()
}

/// A decision's requirements land in exactly one task of the epic realising it,
/// and every one of them is stated by a specification (REQ-0246).
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
    let decisions = of_kind(record, "decision");
    let tasks = of_kind(record, "task");
    let known = known(record);
    let not_covered = Regex::new(r"(?ms)^## Not covered$(.*)").expect("section pattern");
    for epic in of_kind(record, "epic") {
        let epic_id = bare(epic.id());
        let realises = bare(epic.value("realises"));
        let Some(decision) = decisions.iter().find(|d| bare(d.id()) == realises) else {
            out.push(Finding::at(epic, epic.field("realises").map(|f| f.line), format!("realises {realises}, which is not a decision")));
            continue;
        };
        let verified = !bare(epic.value("checked-at")).is_empty();
        for (line, mark, task, _) in entries(epic) {
            let Some(doc) = known.get(task.as_str()) else { continue };
            if mark == ' ' && claims_done(doc) {
                out.push(Finding::at(epic, Some(line), format!("leaves {task} unmarked, and its Evidence section is written")));
            }
            if verified || mark == '~' {
                continue;
            }
            for requirement in requirements_in(record, doc.value("closes")) {
                if known.get(requirement.as_str()).is_some_and(|r| bare(r.value("status")) == "withdrawn") {
                    out.push(Finding::at(doc, doc.field("closes").map(|f| f.line), format!("closes {requirement}, which is withdrawn, in {epic_id}, which is not verified")));
                }
            }
        }
        let addressed = requirements_in(record, decision.value("addresses"));
        let mut claimed: BTreeMap<String, Vec<&str>> = BTreeMap::new();
        for task in tasks.iter().filter(|t| bare(t.value("epic")) == epic_id) {
            for requirement in requirements_in(record, task.value("closes")) {
                claimed.entry(requirement).or_default().push(&task.shown);
            }
        }
        let named = not_covered
            .captures(&epic.text)
            .map(|c| requirements_in(record, &c[1]))
            .unwrap_or_default();
        for requirement in &addressed {
            if !claimed.contains_key(requirement) && !named.contains(requirement) {
                out.push(Finding::at(epic, None, format!("{requirement} lands in no task")));
            }
            if !stated.contains(requirement) {
                out.push(Finding::at(decision, None, format!("{requirement} is stated in no specification")));
            }
        }
        for (requirement, where_) in &claimed {
            if !addressed.contains(requirement) {
                out.push(Finding::at(epic, None, format!("{requirement} is closed by a task and addressed by no decision")));
            }
            if where_.len() > 1 {
                out.push(Finding::at(epic, None, format!("{requirement} is claimed by {}", where_.join(", "))));
            }
        }
    }
    out
}

fn is_draft(doc: &Doc) -> bool {
    bare(doc.value("status")) == "draft"
}

fn shape(record: &Record) -> Vec<Finding> {
    let mut out = Vec::new();
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else { continue };
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
            heading.strip_prefix(section).is_some_and(|rest| !rest.starts_with(|c: char| c.is_alphanumeric()))
        };
        let drafted = if is_draft(doc) { kind.draft_sections.as_slice() } else { &[] };
        for section in kind.sections.iter().chain(drafted) {
            if !headings.iter().any(|h| names(h, section)) {
                let scope = if drafted.contains(section) { "a draft " } else { "a " };
                out.push(Finding::at(doc, None, format!("has no {section} section, which {scope}{} carries", kind.name)));
            }
        }
        if let (Some(first), Some(opening)) = (&kind.first_section, headings.first()) {
            if !names(opening, first) {
                out.push(Finding::at(doc, None, format!("opens with {opening}, where a {} opens with {first}", kind.name)));
            }
        }
    }
    out
}


/// The lines of a `## <name>` section, with their line numbers.
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

/// Each task entry an epic lists: its line, its mark, its task and the whole
/// entry with its continuation lines.
fn entries(epic: &Doc) -> Vec<(usize, char, String, String)> {
    let head = Regex::new(r"^- \[(.)\] T-\d+ (TSK-\d{4})").expect("entry pattern");
    let mut out: Vec<(usize, char, String, String)> = Vec::new();
    for (i, line) in epic.text.lines().enumerate() {
        if let Some(c) = head.captures(line) {
            let mark = c[1].chars().next().unwrap_or(' ');
            out.push((i + 1, mark, c[2].to_string(), line.to_string()));
        } else if let Some(last) = out.last_mut() {
            if line.starts_with(' ') && !line.trim().is_empty() {
                last.3.push('\n');
                last.3.push_str(line);
            }
        }
    }
    out
}

/// Whether a task's Evidence section says the work is done: it holds text and
/// doesn't open with "Not yet.", which a postponed task keeps above its note.
fn claims_done(task: &Doc) -> bool {
    let lines = section_lines(task, "Evidence");
    let first = lines.iter().map(|(_, l)| l.trim()).find(|l| !l.is_empty());
    first.is_some_and(|l| !l.starts_with("Not yet"))
}

/// A task's evidence, without a leading "Not yet." paragraph.
fn evidence_of(task: &Doc) -> String {
    let lines: Vec<&str> = section_lines(task, "Evidence").into_iter().map(|(_, l)| l).collect();
    let text = lines.join("\n");
    let mut paragraphs = text.split("\n\n").map(str::trim).filter(|p| !p.is_empty()).peekable();
    if paragraphs.peek().is_some_and(|p| p.starts_with("Not yet")) {
        paragraphs.next();
    }
    paragraphs.collect::<Vec<_>>().join("\n\n")
}

/// The named rules a section or a field can't express (ADR-1140).
fn rules(record: &Record) -> Vec<Finding> {
    let date = Regex::new(r"\d{4}-\d{2}-\d{2}").expect("date pattern");
    let requirement = Regex::new(r"REQ-\d{4}").expect("requirement pattern");
    let authority = Regex::new(r"(?:ADR|BUG)-\d{4}").expect("authority pattern");
    let mut out = Vec::new();
    for doc in &record.docs {
        let Some(kind) = doc.kind.map(|k| &record.layout.kinds[k]) else { continue };
        if kind.index.as_deref() == Some(doc.relative.as_str()) {
            continue;
        }
        let drafted = if is_draft(doc) { kind.draft_rules.as_slice() } else { &[] };
        for rule in kind.rules.iter().chain(drafted) {
            match rule.as_str() {
                "sources-dated" => {
                    for (line, text) in section_lines(doc, "Sources") {
                        if text.starts_with("- ") && !date.is_match(text) {
                            out.push(Finding::at(doc, Some(line), "names a source without the date it was read".into()));
                        }
                    }
                }
                "cites-no-requirement" => {
                    let body_start = doc.fields.as_ref().map(|f| f.last().map(|l| l.line).unwrap_or(0)).unwrap_or(0) + 1;
                    for (i, text) in doc.text.lines().enumerate().skip(body_start) {
                        for found in requirement.find_iter(text) {
                            out.push(Finding::at(doc, Some(i + 1), format!("cites {}, and research cites no requirement", found.as_str())));
                        }
                    }
                }
                "judgement-verifier" => {
                    if let Some(field) = doc.field("verification") {
                        if bare(&field.value) == "judgement" && doc.field("verifier").is_none() {
                            out.push(Finding::at(doc, Some(field.line), "is verified by judgement and names no verifier: agent or person".into()));
                        }
                    }
                }
                "realises-one" => {
                    let field = doc.field("realises");
                    let named = field.map(|f| authority.find_iter(&f.value).count()).unwrap_or(0);
                    if named != 1 {
                        out.push(Finding::at(doc, field.map(|f| f.line), format!("realises {named} records, where an epic realises exactly one decision or defect")));
                    }
                }
                "alternatives-why-lost" => {
                    let header = section_lines(doc, "Alternatives").into_iter().find(|(_, text)| text.trim_start().starts_with('|'));
                    let says = header.is_some_and(|(_, text)| text.to_lowercase().contains("lost"));
                    if !says {
                        out.push(Finding::at(doc, header.map(|(line, _)| line), "has no column saying why each alternative lost".into()));
                    }
                }
                "done-has-evidence" | "added-says-why" | "dropped-says-why" => {
                    let known = known(record);
                    for (line, mark, task, entry) in entries(doc) {
                        match (rule.as_str(), mark) {
                            ("done-has-evidence", 'x') => {
                                let evidence = known.get(task.as_str()).map(|t| evidence_of(t)).unwrap_or_default();
                                if evidence.is_empty() {
                                    out.push(Finding::at(doc, Some(line), format!("marks {task} done, and its Evidence section holds nothing past \"Not yet.\"")));
                                }
                            }
                            ("added-says-why", '+') if !entry.contains("added:") => {
                                out.push(Finding::at(doc, Some(line), format!("marks {task} added after approval with no added: line saying why")));
                            }
                            ("dropped-says-why", '~') if !entry.contains("dropped:") => {
                                out.push(Finding::at(doc, Some(line), format!("marks {task} dropped with no dropped: line saying why")));
                            }
                            _ => {}
                        }
                    }
                }
                unknown => out.push(Finding::at(doc, None, format!("the layout names a rule, {unknown}, this program doesn't know"))),
            }
        }
    }
    out
}

const STEPS: [&str; 9] = ["research", "requirements", "design", "spec", "epic", "implement", "document", "verify", "review"];
const TEMPLATES: [&str; 9] = ["research", "requirement", "adr", "spec", "epic", "task", "bug", "vision", "constitution"];

fn approved(doc: &Doc) -> bool {
    bare(doc.value("status")) == "approved"
}

fn kind_of<'a>(record: &'a Record, doc: &Doc) -> &'a str {
    doc.kind.map(|k| record.layout.kinds[k].name.as_str()).unwrap_or("artifact")
}

/// Each task an epic lists, with the mark it carries: `x` done, `~` dropped,
/// and anything else open.
fn marks(epic: &Doc) -> Vec<(String, char)> {
    let line = Regex::new(r"(?m)^- \[(.)\] T-\d+ (TSK-\d{4})").expect("mark pattern");
    line.captures_iter(&epic.text)
        .filter_map(|c| Some((c.get(2)?.as_str().to_string(), c.get(1)?.as_str().chars().next()?)))
        .collect()
}

fn finished(mark: char) -> bool {
    mark == 'x' || mark == '~'
}

/// The tasks a task depends on: the `TSK-` identifiers under `## Depends on`.
fn depends_on(task: &Doc) -> Vec<String> {
    let section = Regex::new(r"(?ms)^## Depends on$(.*?)(?:^## |\z)").expect("section pattern");
    let id = Regex::new(r"TSK-\d{4}").expect("identifier pattern");
    section
        .captures(&task.text)
        .map(|c| id.find_iter(&c[1]).map(|m| m.as_str().to_string()).collect())
        .unwrap_or_default()
}

/// Whether a task is marked done or dropped by the epic it names.
fn task_finished(known: &BTreeMap<String, &Doc>, task: &str) -> bool {
    let Some(doc) = known.get(task) else { return false };
    let Some(epic) = known.get(bare(doc.value("epic"))) else { return false };
    marks(epic).iter().any(|(id, mark)| id == task && finished(*mark))
}

fn ready(rest: &[String]) -> u8 {
    let Some((step, ids)) = rest.split_first() else {
        eprintln!("usage: meow-method ready <step> <id>..., where a step is one of {}", STEPS.join(", "));
        return USAGE;
    };
    let step = step.as_str();
    if !STEPS.contains(&step) {
        eprintln!("meow-method ready: no step is named {step}; the steps are {}", STEPS.join(", "));
        return USAGE;
    }
    if step == "research" {
        say!("meow-method ready research: ready; research needs no approved input");
        return CLEAN;
    }
    if ids.is_empty() {
        eprintln!("meow-method ready {step}: name the identifiers of the step's input");
        return USAGE;
    }
    let (record, _, _) = match open_record("ready") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let known = known(&record);
    let mut missing: Vec<String> = Vec::new();
    for id in ids {
        let Some(doc) = known.get(id.as_str()) else {
            missing.push(format!("{id} has no file"));
            continue;
        };
        let kind = kind_of(&record, doc);
        match step {
            "requirements" | "design" | "spec" | "epic" | "implement" => {
                if !approved(doc) {
                    missing.push(format!("{id}, a {kind}, is {} and not approved", bare(doc.value("status"))));
                    continue;
                }
            }
            _ => {}
        }
        match step {
            "epic" if kind == "decision" => {
                let mut stated = BTreeSet::new();
                for spec in of_kind(&record, "specification") {
                    stated.extend(requirements_in(&record, spec.value("states")));
                }
                for requirement in requirements_in(&record, doc.value("addresses")) {
                    if !stated.contains(&requirement) {
                        missing.push(format!("{requirement}, which {id} addresses, is stated by no specification"));
                    }
                }
            }
            "implement" => {
                let epic_id = bare(doc.value("epic"));
                match known.get(epic_id) {
                    Some(epic) if approved(epic) => {}
                    Some(epic) => missing.push(format!("{epic_id}, the epic of {id}, is {} and not approved", bare(epic.value("status")))),
                    None => missing.push(format!("{epic_id}, the epic of {id}, has no file")),
                }
                for dependency in depends_on(doc) {
                    if !task_finished(&known, &dependency) {
                        missing.push(format!("{dependency}, which {id} depends on, isn't done"));
                    }
                }
            }
            "document" | "verify" => {
                let open: Vec<String> = marks(doc)
                    .into_iter()
                    .filter(|(_, mark)| !finished(*mark))
                    .map(|(task, _)| task)
                    .collect();
                if marks(doc).is_empty() {
                    missing.push(format!("{id} lists no tasks"));
                }
                for task in open {
                    missing.push(format!("{task}, a task of {id}, isn't done"));
                }
            }
            "review" => {
                if bare(doc.value("checked-at")).is_empty() {
                    missing.push(format!("{id} hasn't been verified: its checked-at is empty"));
                }
            }
            _ => {}
        }
    }
    if missing.is_empty() {
        say!("meow-method ready {step}: ready; {} approved and complete", ids.join(", "));
        CLEAN
    } else {
        say!("meow-method ready {step}: not ready");
        for line in &missing {
            say!("  {line}");
        }
        FOUND
    }
}

fn count(n: usize, noun: &str) -> String {
    format!("{n} {noun}{}", if n == 1 { "" } else { "s" })
}

fn title(doc: &Doc) -> String {
    let heading = doc.text.lines().find(|l| l.starts_with("# ")).unwrap_or("# ").trim_start_matches("# ");
    // A decision's heading carries its number, "1130. The chain ...".
    heading.split_once(". ").filter(|(n, _)| n.chars().all(|c| c.is_ascii_digit())).map(|(_, t)| t).unwrap_or(heading).to_string()
}

/// Where one authorising record stands in the chain, and what comes next.
fn position(record: &Record, known: &BTreeMap<String, &Doc>, findings: &BTreeMap<String, usize>, decision: &Doc) -> String {
    let id = bare(decision.id());
    let epics: Vec<&Doc> = of_kind(record, "epic").into_iter().filter(|e| bare(e.value("realises")) == id).collect();
    let Some(epic) = epics.first() else { return "next: spec, then epic".to_string() };
    let epic_id = bare(epic.id());
    if !approved(epic) {
        return format!("waiting: {epic_id} is {} and not approved", bare(epic.value("status")));
    }
    let tasks = marks(epic);
    let open: Vec<&String> = tasks.iter().filter(|(_, mark)| !finished(*mark)).map(|(task, _)| task).collect();
    if !open.is_empty() {
        let doable = open.iter().find(|task| {
            known.get(task.as_str()).map(|doc| depends_on(doc).iter().all(|d| task_finished(known, d))).unwrap_or(true)
        });
        return match doable {
            Some(task) => format!("next: implement {task} ({epic_id}, {} of {} done)", tasks.len() - open.len(), count(tasks.len(), "task")),
            None => format!("waiting: every open task of {epic_id} depends on one that isn't done"),
        };
    }
    let checked = bare(epic.value("checked-at"));
    if checked.is_empty() {
        return format!("next: document, then verify {epic_id} ({} done)", count(tasks.len(), "task"));
    }
    // A verification holds only while the check reports nothing on what it verified (REQ-0706).
    let on = |doc: &Doc| findings.get(&doc.shown).copied().unwrap_or(0);
    let drifted = on(decision) + on(epic) + tasks.iter().filter_map(|(t, _)| known.get(t.as_str())).map(|t| on(t)).sum::<usize>();
    if drifted > 0 {
        format!("drifted: {epic_id} was verified under {checked}, and check reports {} on it now", count(drifted, "finding"))
    } else {
        format!("realised: {epic_id} verified under {checked}")
    }
}

/// The gate a draft of each kind waits at.
fn gate_of(kind: &str) -> &'static str {
    match kind {
        "research" => "the research gate",
        "requirement" => "the requirements gate",
        "decision" => "the design gate",
        "epic" | "task" => "the epic gate",
        "defect" => "triage",
        _ => "approval",
    }
}

fn status(rest: &[String]) -> u8 {
    let waiting_only = match rest {
        [] => false,
        [flag] if flag == "--waiting" => true,
        _ => {
            eprintln!("usage: meow-method status [--waiting]");
            return USAGE;
        }
    };
    if waiting_only {
        // Run at the start of every session, so it says nothing unless
        // something waits: a repository with no record pays nothing.
        let repository = profile::repository_root();
        let (Ok(layout), Ok(root)) = (load_layout(), record_root(&repository)) else { return CLEAN };
        if !root.is_dir() {
            return CLEAN;
        }
        let record = read_record(layout, &repository, &root);
        let known = known(&record);
        let drafts: Vec<&&Doc> = known.values().filter(|doc| bare(doc.value("status")) == "draft").collect();
        if !drafts.is_empty() {
            say!("Waiting for approval in this repository's record:");
            for doc in &drafts {
                let kind = kind_of(&record, doc);
                say!("  {} {kind}, at {}: {}", bare(doc.id()), gate_of(kind), title(doc));
            }
        }
        return CLEAN;
    }
    let (record, repository, root) = match open_record("status") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    if !under_version_control(&root) {
        say!("The record is local to this machine: {} is under no version control.", root.display());
        say!();
    }
    let known = known(&record);
    let findings = findings_by_file(&record, &root, &repository);
    let drafts: Vec<&&Doc> = known.values().filter(|doc| bare(doc.value("status")) == "draft").collect();
    say!("Waiting for approval");
    if drafts.is_empty() {
        say!("  nothing");
    }
    for doc in &drafts {
        let kind = kind_of(&record, doc);
        say!("  {} {kind}, draft at {}: {}", bare(doc.id()), gate_of(kind), title(doc));
    }
    say!();
    say!("Decisions");
    let mut decisions: Vec<&Doc> = of_kind(&record, "decision").into_iter().filter(|d| approved(d)).collect();
    decisions.sort_by_key(|d| bare(d.id()).to_string());
    if decisions.is_empty() {
        say!("  none approved");
    }
    for decision in decisions {
        let id = bare(decision.id());
        say!("  {id} {}", title(decision));
        say!("    {}", position(&record, &known, &findings, decision));
    }
    say!();
    say!("Requirements");
    let states = ["verified", "closed and not yet verified", "in a task not yet done", "checked by nothing"];
    let mut tally = [0usize; 4];
    let in_force: Vec<&Doc> = of_kind(&record, "requirement").into_iter().filter(|r| approved(r)).collect();
    for requirement in &in_force {
        let state = requirement_state(&closing_tasks(&record, &known, bare(requirement.id())));
        tally[states.iter().position(|s| *s == state).unwrap_or(3)] += 1;
    }
    let parts: Vec<String> = states.iter().zip(tally).map(|(s, n)| format!("{n} {s}")).collect();
    say!("  {} in force: {}", in_force.len(), parts.join(", "));
    CLEAN
}

fn template(rest: &[String]) -> u8 {
    let [kind] = rest else {
        eprintln!("usage: meow-method template <kind>, where a kind is one of {}", TEMPLATES.join(", "));
        return USAGE;
    };
    if !TEMPLATES.contains(&kind.as_str()) {
        eprintln!("meow-method template: no kind is named {kind}; the kinds are {}", TEMPLATES.join(", "));
        return USAGE;
    }
    let repository = profile::repository_root();
    let own = repository.join(".meowpaw").join("templates").join(format!("{kind}.md"));
    if own.is_file() {
        say!("{}", own.display());
        return CLEAN;
    }
    let unit = match layout_path() {
        Ok(path) => path.parent().and_then(Path::parent).map(|u| u.join("templates").join(format!("{kind}.md"))),
        Err(reason) => {
            say!("meow-method template: no template was found: {reason}");
            return UNCHECKED;
        }
    };
    match unit {
        Some(path) if path.is_file() => {
            say!("{}", path.display());
            CLEAN
        }
        Some(path) => {
            say!("meow-method template: the unit has no template for {kind} at {}", path.display());
            FOUND
        }
        None => {
            say!("meow-method template: no template was found for {kind}");
            UNCHECKED
        }
    }
}

fn show(rest: &[String]) -> u8 {
    let [id] = rest else {
        eprintln!("usage: meow-method show <id>");
        return USAGE;
    };
    let (record, _, _) = match open_record("show") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let known = known(&record);
    let Some(doc) = known.get(id.as_str()) else {
        say!("meow-method show: {id} resolves to nothing in the record");
        return FOUND;
    };
    say!("{id} {}, {}: {}", kind_of(&record, doc), bare(doc.value("status")), doc.shown);
    let heading = title(doc);
    if heading != id.as_str() {
        say!("{heading}");
    }
    let first = doc
        .text
        .split("\n\n")
        .skip_while(|p| p.starts_with("---") || p.trim_start().starts_with('#') || p.trim().is_empty())
        .next()
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
            let ids: Vec<&str> = record.ids.find_iter(&field.value).map(|m| m.as_str()).collect();
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
        let tasks = closing_tasks(&record, &known, id);
        say!("  {}", requirement_state(&tasks));
        for (task, mark, epic, checked) in &tasks {
            let done = match mark {
                'x' => "done",
                '~' => "dropped",
                _ => "open",
            };
            let verified = if checked.is_empty() { "not yet verified".to_string() } else { format!("verified under {checked}") };
            say!("  {task} {done} in {epic}, {verified}");
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
            if let Some(field) = other.field(key) {
                if record.ids.find_iter(&field.value).any(|m| m.as_str() == id) {
                    let who = if bare(other.id()).is_empty() { other.shown.clone() } else { bare(other.id()).to_string() };
                    cited.entry(key.clone()).or_default().insert(who);
                    in_field = true;
                }
            }
        }
        if !in_field && record.ids.find_iter(&other.text).any(|m| m.as_str() == id) {
            cited.entry("body".into()).or_default().insert(other.shown.clone());
        }
    }
    if cited.is_empty() {
        say!("  nothing");
    }
    for key in record.layout.relations.iter().map(String::as_str).chain(std::iter::once("body")) {
        if let Some(who) = cited.get(key) {
            say!("  {key}: {}", who.iter().cloned().collect::<Vec<_>>().join(", "));
        }
    }
    CLEAN
}

const INDEX_OPEN: &str = "<!-- meow-method index -->";
const INDEX_CLOSE: &str = "<!-- /meow-method index -->";

/// A kind by its name or its artifact word, such as `decision` or `adr`.
fn kind_named(record: &Record, word: &str) -> Option<usize> {
    record.layout.kinds.iter().position(|k| k.name == word || k.artifact == word)
}

/// What an artifact concluded, in one line: a requirement's statement, a
/// research record's summary, and otherwise its title.
fn conclusion(record: &Record, doc: &Doc) -> String {
    let kind = kind_of(record, doc);
    let paragraph = |text: &str| -> String {
        text.split("\n\n")
            .map(str::trim)
            .find(|p| !p.is_empty() && !p.starts_with('#') && !p.starts_with("---") && !p.starts_with("<!--"))
            .map(|p| p.split_whitespace().collect::<Vec<_>>().join(" "))
            .unwrap_or_default()
    };
    let text = match kind {
        "requirement" => paragraph(doc.text.splitn(3, "\n---\n").last().unwrap_or("")),
        "research" => {
            let summary: Vec<&str> = section_lines(doc, "Summary").into_iter().map(|(_, l)| l).collect();
            let first = paragraph(&summary.join("\n"));
            first.split_inclusive(". ").next().unwrap_or(&first).trim().to_string()
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
    let mut parts: Vec<String> = std::iter::repeat("..".to_string()).take(base.len() - common).collect();
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
        *statuses.entry(bare(doc.value("status")).to_string()).or_default() += 1;
    }
    let mut out = String::new();
    let counted: Vec<String> = statuses.iter().map(|(s, n)| format!("{n} {s}")).collect();
    out.push_str(&format!("{} in all: {}.\n\n", count(docs.len(), &kind.name), counted.join(", ")));
    out.push_str(&format!("| Identifier | What it {} | Status |\n| --- | --- | --- |\n", if kind.name == "requirement" { "requires" } else { "concluded" }));
    for doc in &docs {
        let id = bare(doc.id());
        out.push_str(&format!(
            "| [{id}]({}) | {} | {} |\n",
            relative_link(index, &doc.relative),
            conclusion(record, doc),
            bare(doc.value("status"))
        ));
    }
    let amended = Regex::new(r"\*\*Amended by ((?:ADR|BUG|EPC)-\d{4})").expect("amendment pattern");
    let amendments: Vec<String> = docs
        .iter()
        .filter_map(|doc| {
            let by: Vec<&str> = amended.captures_iter(&doc.text).filter_map(|c| c.get(1)).map(|m| m.as_str()).collect();
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
            topics.entry(bare(doc.value("topic")).to_string()).or_default().push(bare(doc.id()));
        }
        out.push_str("\nBy topic:\n\n");
        for (topic, ids) in &topics {
            out.push_str(&format!("- {topic}: {}\n", ids.join(", ")));
        }
    }
    Some(out)
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
    let open = text.find(INDEX_OPEN)? + INDEX_OPEN.len();
    let close = text[open..].find(INDEX_CLOSE)? + open;
    Some((open, close))
}

fn index_command(rest: &[String]) -> u8 {
    let (word, write) = match rest {
        [word] => (word, false),
        [word, flag] if flag == "--write" => (word, true),
        _ => {
            eprintln!("usage: meow-method index <kind> [--write]");
            return USAGE;
        }
    };
    let (record, _, root) = match open_record("index") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let Some(k) = kind_named(&record, word) else {
        let kinds: Vec<&str> = record.layout.kinds.iter().filter(|k| k.index.is_some()).map(|k| k.name.as_str()).collect();
        eprintln!("meow-method index: no kind is named {word}; the kinds with an index are {}", kinds.join(", "));
        return USAGE;
    };
    let Some(block) = generate_index(&record, k) else {
        say!("meow-method index: a {} has no index file in the layout", record.layout.kinds[k].name);
        return FOUND;
    };
    if !write {
        print!("{block}");
        return CLEAN;
    }
    let path = root.join(record.layout.kinds[k].index.as_deref().unwrap_or_default());
    let text = std::fs::read_to_string(&path).unwrap_or_default();
    let Some((open, close)) = generated_block(&text) else {
        say!("meow-method index: {} has no {INDEX_OPEN} block to write into", path.display());
        return FOUND;
    };
    let updated = format!("{}\n\n{}\n{}", &text[..open], block.trim_end(), &text[close..]);
    if updated != text {
        // Written beside the index and renamed into place, so an interrupted
        // write leaves the old index or the new one and never half of either.
        let temporary = path.with_extension("md.meow-tmp");
        let written = std::fs::write(&temporary, updated).and_then(|_| std::fs::rename(&temporary, &path));
        if let Err(e) = written {
            let _ = std::fs::remove_file(&temporary);
            say!("meow-method index: {}: {e}", path.display());
            return FOUND;
        }
    }
    say!("meow-method index: wrote the {} index to {}", record.layout.kinds[k].name, path.display());
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
            eprintln!("usage: meow-method new <kind> [--topic <topic>]");
            return USAGE;
        }
    };
    let (record, _, _) = match open_record("new") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let Some(k) = kind_named(&record, word).filter(|&k| record.layout.kinds[k].prefix.is_some()) else {
        let kinds: Vec<&str> = record.layout.kinds.iter().filter(|k| k.prefix.is_some()).map(|k| k.name.as_str()).collect();
        eprintln!("meow-method new: no numbered kind is named {word}; the kinds are {}", kinds.join(", "));
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
        if let Some(c) = doc.path.file_name().and_then(|n| n.to_str()).and_then(|n| number.captures(n)) {
            if let Ok(n) = c[1].parse::<u32>() {
                taken.insert(n);
            }
        }
    }
    let highest = taken.iter().max().copied().unwrap_or(0);
    let (mut next, step) = if kind.name == "requirement" {
        let Some(topic) = topic else {
            eprintln!("meow-method new: a requirement is allocated in its topic's block; name it with --topic");
            return USAGE;
        };
        let in_topic: Vec<u32> = of_kind(&record, "requirement")
            .iter()
            .filter(|d| bare(d.value("topic")) == topic)
            .filter_map(|d| bare(d.id()).strip_prefix(&format!("{prefix}-")).and_then(|n| n.parse().ok()))
            .collect();
        match in_topic.iter().max() {
            Some(top) => (top + 2, 2),
            None => ((highest / 100 + 1) * 100, 2),
        }
    } else if kind.name == "research" {
        (highest + 1, 1)
    } else {
        ((highest / 10 + 1) * 10, 10)
    };
    while taken.contains(&next) {
        next += step;
    }
    if next > 9999 {
        say!("meow-method new: the {} block is full", kind.name);
        return FOUND;
    }
    say!("{prefix}-{next:04}");
    CLEAN
}

/// Artifacts whose identifier, title or conclusion carry the words, ranked by
/// how many they carry: identifiers and headings first, never a body
/// (ADR-1180).
fn find(rest: &[String]) -> u8 {
    if rest.is_empty() {
        eprintln!("usage: meow-method find <word>...");
        return USAGE;
    }
    let (record, _, _) = match open_record("find") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let words: Vec<String> = rest.iter().map(|w| w.to_lowercase()).collect();
    let mut hits: Vec<(usize, String, String)> = Vec::new();
    for doc in &record.docs {
        let id = bare(doc.id());
        if id.is_empty() || doc.is_index {
            continue;
        }
        let concluded = conclusion(&record, doc);
        // A requirement's heading is its identifier, so its statement heads it.
        let heading = if title(doc) == id { concluded.clone() } else { title(doc) };
        let haystack = format!("{id} {heading} {concluded}").to_lowercase();
        let score = words.iter().filter(|w| haystack.contains(w.as_str())).count();
        if score > 0 {
            let line = format!("{id} {}, {}: {heading}", kind_of(&record, doc), bare(doc.value("status")));
            hits.push((score, id.to_string(), line));
        }
    }
    hits.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
    if hits.is_empty() {
        say!("meow-method find: nothing in the record carries {}", rest.join(" "));
        return FOUND;
    }
    for (_, _, line) in hits.iter().take(20) {
        say!("{line}");
    }
    if hits.len() > 20 {
        say!("... and {} more; narrow the words", hits.len() - 20);
    }
    CLEAN
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_flowed_list_is_one_field() {
        let fields = parse_front_matter("---\nid: TSK-1\ncloses:\n  [\n    REQ-0001,\n    REQ-0002,\n  ]\n---\n# T\n").unwrap();
        let closes = fields.iter().find(|f| f.key == "closes").unwrap();
        assert!(closes.value.contains("REQ-0001") && closes.value.contains("REQ-0002"));
        assert_eq!(closes.line, 3);
    }

    #[test]
    fn today_is_a_date() {
        assert!(Regex::new(r"^\d{4}-\d{2}-\d{2}$").unwrap().is_match(&today()));
    }
}
