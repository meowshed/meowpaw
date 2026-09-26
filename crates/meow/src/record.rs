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
        _ => {
            eprintln!(
                "usage: meow-method check [{}] | status | ready <step> <id>... | template <kind>",
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
            println!("meow-method {verb}: the record was not checked: {reason}");
            return Err(UNCHECKED);
        }
    };
    let repository = profile::repository_root();
    let root = match record_root(&repository) {
        Ok(root) => root,
        Err(reason) => {
            println!("meow-method {verb}: {reason}");
            return Err(FOUND);
        }
    };
    if !root.is_dir() {
        println!("meow-method {verb}: the record's root {} doesn't exist; nothing was checked", root.display());
        return Err(FOUND);
    }
    let record = read_record(layout, &repository, &root);
    Ok((record, repository, root))
}

fn check(rest: &[String]) -> u8 {
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
        let mut findings = match check {
            "front-matter" => front_matter(&record),
            "identifiers" => identifiers(&record),
            "relations" => relations(&record),
            "index" => index(&record, &root, &repository),
            "coverage" => coverage(&record),
            "shape" => shape(&record),
            _ => rules(&record),
        };
        findings.sort_by(|a, b| (&a.shown, a.line, &a.message).cmp(&(&b.shown, b.line, &b.message)));
        for finding in &findings {
            match finding.line {
                Some(line) => println!("{}:{}: {}", finding.shown, line, finding.message),
                None => println!("{}: {}", finding.shown, finding.message),
            }
        }
        println!("{check}: {} finding{}", findings.len(), if findings.len() == 1 { "" } else { "s" });
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
    let mut out = Vec::new();
    for doc in &record.docs {
        for key in &record.layout.relations {
            let Some(field) = doc.field(key) else { continue };
            for found in record.ids.find_iter(&field.value) {
                if !known.contains_key(found.as_str()) {
                    out.push(Finding::at(doc, Some(field.line), format!("{key} names {}, which has no file", found.as_str())));
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
    let not_covered = Regex::new(r"(?ms)^## Not covered$(.*)").expect("section pattern");
    for epic in of_kind(record, "epic") {
        let epic_id = bare(epic.id());
        let realises = bare(epic.value("realises"));
        let Some(decision) = decisions.iter().find(|d| bare(d.id()) == realises) else {
            out.push(Finding::at(epic, epic.field("realises").map(|f| f.line), format!("realises {realises}, which is not a decision")));
            continue;
        };
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
        println!("meow-method ready research: ready; research needs no approved input");
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
        println!("meow-method ready {step}: ready; {} approved and complete", ids.join(", "));
        CLEAN
    } else {
        println!("meow-method ready {step}: not ready");
        for line in &missing {
            println!("  {line}");
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
fn position(record: &Record, known: &BTreeMap<String, &Doc>, id: &str) -> String {
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
        format!("next: document, then verify {epic_id} ({} done)", count(tasks.len(), "task"))
    } else {
        format!("realised: {epic_id} verified under {checked}")
    }
}

fn status(rest: &[String]) -> u8 {
    if !rest.is_empty() {
        eprintln!("usage: meow-method status");
        return USAGE;
    }
    let (record, _, _) = match open_record("status") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let known = known(&record);
    let drafts: Vec<&&Doc> = known.values().filter(|doc| bare(doc.value("status")) == "draft").collect();
    println!("Waiting for approval");
    if drafts.is_empty() {
        println!("  nothing");
    }
    for doc in &drafts {
        println!("  {} {}, draft: {}", bare(doc.id()), kind_of(&record, doc), title(doc));
    }
    println!();
    println!("Decisions");
    let mut decisions: Vec<&Doc> = of_kind(&record, "decision").into_iter().filter(|d| approved(d)).collect();
    decisions.sort_by_key(|d| bare(d.id()).to_string());
    if decisions.is_empty() {
        println!("  none approved");
    }
    for decision in decisions {
        let id = bare(decision.id());
        println!("  {id} {}", title(decision));
        println!("    {}", position(&record, &known, id));
    }
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
        println!("{}", own.display());
        return CLEAN;
    }
    let unit = match layout_path() {
        Ok(path) => path.parent().and_then(Path::parent).map(|u| u.join("templates").join(format!("{kind}.md"))),
        Err(reason) => {
            println!("meow-method template: no template was found: {reason}");
            return UNCHECKED;
        }
    };
    match unit {
        Some(path) if path.is_file() => {
            println!("{}", path.display());
            CLEAN
        }
        Some(path) => {
            println!("meow-method template: the unit has no template for {kind} at {}", path.display());
            FOUND
        }
        None => {
            println!("meow-method template: no template was found for {kind}");
            UNCHECKED
        }
    }
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
