// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `paw upgrade`: moves a record from epics and tasks to the form ADR-3090
//! states, and this module holds the one copy of the old marks' rules.
//!
//! SPC-1070 "The upgrade" states the behaviour. With no flag it reports and
//! writes nothing, and a run on a record already in the form says so.

use super::*;

/// Whether the record's root still holds a directory of a retired kind.
pub(super) fn old_form(root: &Path) -> bool {
    RETIRED_DIRS.iter().any(|dir| root.join(dir).is_dir())
}

/// The directories the retired kinds lived in.
const RETIRED_DIRS: [&str; 2] = ["tasks", "epics"];

/// A task entry under a `## Tasks` section, with or without a mark.
static ENTRY: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^- (?:\[(.)\] )?T-\d+ (?:\[P\] )?(TSK-\d{4})").expect("entry pattern")
});

/// The Markdown files of one retired directory, its index left out.
fn retired_docs(dir: &Path, repository: &Path) -> Vec<Doc> {
    let mut paths = Vec::new();
    if dir.is_dir() {
        markdown_under(dir, None, &mut paths);
    }
    paths.sort();
    paths
        .into_iter()
        .map(|path| read_doc(path, repository))
        .filter(|doc| !bare(doc.id()).is_empty())
        .collect()
}

/// A task's own state, as the old record derived it: dropped once withdrawn,
/// rejected or superseded, done once its Evidence is written, and open
/// otherwise.
fn own_mark(task: &Doc) -> char {
    if matches!(
        bare(task.value("status")),
        "withdrawn" | "rejected" | "superseded"
    ) {
        return '~';
    }
    let said = section_lines(task, "Evidence")
        .into_iter()
        .map(|(_, line)| line.trim())
        .find(|line| !line.is_empty());
    if said.is_some_and(|line| !line.starts_with("Not yet.")) {
        'x'
    } else {
        ' '
    }
}

/// Each task an epic or a defect lists, with its mark, taking an unmarked
/// entry's state from the task.
fn listed_marks(doc: &Doc, tasks: &BTreeMap<String, &Doc>) -> Vec<(String, char)> {
    let mut out = Vec::new();
    let mut inside = false;
    for line in doc.text.lines() {
        if let Some(heading) = line.strip_prefix("## ") {
            inside = heading.trim() == "Tasks";
        } else if inside && let Some(found) = ENTRY.captures(line) {
            let id = found[2].to_string();
            let mark = found.get(1).and_then(|m| m.as_str().chars().next());
            let mark = mark.unwrap_or_else(|| tasks.get(&id).map_or(' ', |t| own_mark(t)));
            out.push((id, mark));
        }
    }
    out
}

/// What one run would do.
#[derive(Default)]
struct Moves {
    /// Task, its live authority.
    folded: Vec<(String, String)>,
    /// Open tasks with no live authority.
    orphans: Vec<String>,
    /// Decisions and defects to store `done` on.
    finished: Vec<String>,
}

/// The authority that carries a task, through its epic where it has one.
fn authority(task: &Doc, epics: &BTreeMap<String, &Doc>) -> String {
    let named = ["epic", "bug", "realises"]
        .iter()
        .map(|key| bare(task.value(key)))
        .find(|v| !v.is_empty())
        .unwrap_or("");
    match epics.get(named) {
        Some(epic) => bare(epic.value("realises")).to_string(),
        None => named.to_string(),
    }
}

fn live(doc: &Doc) -> bool {
    matches!(bare(doc.value("status")), "draft" | "approved")
}

/// Works out each move from the old marks, once, with nothing written.
fn plan(record: &Record, tasks: &[Doc], epics: &[Doc]) -> Moves {
    let by_task: BTreeMap<String, &Doc> = tasks
        .iter()
        .map(|t| (bare(t.id()).to_string(), t))
        .collect();
    let by_epic: BTreeMap<String, &Doc> = epics
        .iter()
        .map(|e| (bare(e.id()).to_string(), e))
        .collect();
    let known = known(record);
    let mut marks: BTreeMap<String, Vec<(String, char)>> = BTreeMap::new();
    for epic in epics {
        marks
            .entry(bare(epic.value("realises")).to_string())
            .or_default()
            .extend(listed_marks(epic, &by_task));
    }
    for defect in of_kind(record, "defect") {
        marks
            .entry(bare(defect.id()).to_string())
            .or_default()
            .extend(listed_marks(defect, &by_task));
    }
    let listed: BTreeMap<String, char> = marks.values().flatten().cloned().collect();
    for task in tasks {
        let id = bare(task.id()).to_string();
        if !listed.contains_key(&id) {
            let realised = authority(task, &by_epic);
            marks
                .entry(realised)
                .or_default()
                .push((id, own_mark(task)));
        }
    }
    let mut moves = Moves::default();
    for task in tasks {
        let id = bare(task.id()).to_string();
        // A withdrawn task is dropped whatever a list still says of it.
        let mark = listed.get(&id).copied().unwrap_or_else(|| own_mark(task));
        if own_mark(task) == '~' || matches!(mark, 'x' | '~') {
            continue;
        }
        let carrier = authority(task, &by_epic);
        match known.get(carrier.as_str()) {
            Some(doc) if live(doc) && matches!(kind_of(record, doc), "decision" | "defect") => {
                moves.folded.push((id, carrier));
            }
            _ => moves.orphans.push(id),
        }
    }
    for decision in of_kind(record, "decision") {
        let id = bare(decision.id());
        let held = marks.get(id).map(Vec::as_slice).unwrap_or_default();
        let finished = !held.is_empty() && held.iter().all(|(_, mark)| matches!(mark, 'x' | '~'));
        if bare(decision.value("status")) == "approved"
            && (finished || (held.is_empty() && landed_elsewhere(record, decision, epics)))
        {
            moves.finished.push(id.to_string());
        }
    }
    for defect in of_kind(record, "defect") {
        let id = bare(defect.id());
        let held = marks.get(id).map(Vec::as_slice).unwrap_or_default();
        if bare(defect.value("status")) == "approved" && defect_closed(defect, held) {
            moves.finished.push(id.to_string());
        }
    }
    moves.folded.sort();
    moves.orphans.sort();
    moves.finished.sort();
    moves
}

/// Whether an epic realising the decision lists no tasks because other work
/// closed all it addresses, naming each requirement under Not covered
/// (BUG-1250).
fn landed_elsewhere(record: &Record, decision: &Doc, epics: &[Doc]) -> bool {
    let addressed = requirements_in(record, decision.value("addresses"));
    !addressed.is_empty()
        && epics
            .iter()
            .filter(|epic| bare(epic.value("realises")) == bare(decision.id()))
            .any(|epic| {
                let lines: Vec<&str> = section_lines(epic, "Not covered")
                    .into_iter()
                    .map(|(_, line)| line)
                    .collect();
                let named = requirements_in(record, &lines.join("\n"));
                addressed
                    .iter()
                    .all(|requirement| named.contains(requirement))
            })
}

/// Whether the old rules read a defect as closed: every task it holds is
/// finished and one is done, or it holds none and `Closed by` says what closed
/// it, where a defect still waiting opens with "Not" or "Open".
fn defect_closed(defect: &Doc, held: &[(String, char)]) -> bool {
    if held.iter().any(|(_, mark)| !matches!(mark, 'x' | '~')) {
        return false;
    }
    if held.iter().any(|(_, mark)| *mark == 'x') {
        return true;
    }
    let first = section_lines(defect, "Closed by")
        .into_iter()
        .map(|(_, line)| line.trim())
        .find(|line| !line.is_empty())
        .unwrap_or("");
    !(first.is_empty() || first.starts_with("Not") || first.starts_with("Open"))
}

/// The profile's text with the retired step gone from its gates, or nothing
/// where no gate names it. Only the `gates` list is touched, so every comment
/// and every other line stays as it was.
fn without_retired_gate(text: &str) -> Option<String> {
    let gates = Regex::new(r#"(?m)^gates\s*=\s*\[[^\]]*\]"#).expect("gates pattern");
    let found = gates.find(text)?;
    let step = Regex::new(r#""epic"\s*,?\s*"#).expect("step pattern");
    if !step.is_match(found.as_str()) {
        return None;
    }
    let list = step.replace(found.as_str(), "");
    let list = list.replace(", ]", "]").replace(",]", "]");
    Some(format!(
        "{}{list}{}",
        &text[..found.start()],
        &text[found.end()..]
    ))
}

/// A record's text with each folded task added as a step of its `## Plan`.
fn with_steps(text: &str, steps: &[String]) -> String {
    let mut lines: Vec<String> = text.lines().map(str::to_string).collect();
    let items = Regex::new(r"^(\d+)\. ").expect("step pattern");
    let opened = lines.iter().position(|line| line.trim() == "## Plan");
    let (end, first) = match opened {
        Some(at) => {
            let end = lines[at + 1..]
                .iter()
                .position(|line| line.starts_with("## "))
                .map_or(lines.len(), |off| at + 1 + off);
            let last = lines[at..end]
                .iter()
                .filter_map(|line| items.captures(line)?[1].parse::<usize>().ok())
                .max()
                .unwrap_or(0);
            (end, last + 1)
        }
        None => {
            lines.extend([String::new(), "## Plan".to_string(), String::new()]);
            lines.push(
                "The upgrade folded these open tasks in (ADR-3090). Read each one before its step."
                    .to_string(),
            );
            lines.push(String::new());
            (lines.len(), 1)
        }
    };
    let mut end = end;
    while end > 0 && lines[end - 1].trim().is_empty() {
        end -= 1;
    }
    let added: Vec<String> = steps
        .iter()
        .enumerate()
        .map(|(i, step)| format!("{}. {step}", first + i))
        .collect();
    lines.splice(end..end, added);
    let mut out = lines.join("\n");
    out.push('\n');
    out
}

/// The text with `key: value` added after the status line.
pub(super) fn with_added_field(text: &str, key: &str, value: &str) -> Option<String> {
    let status = text.lines().find(|line| line.starts_with("status:"))?;
    let at = text.find(status)? + status.len();
    Some(format!("{}\n{key}: {value}{}", &text[..at], &text[at..]))
}

/// `paw upgrade [--write]`: reports each move, and with `--write` makes them.
pub(super) fn upgrade(rest: &[String]) -> u8 {
    let write = match rest {
        [] => false,
        [flag] if flag == "--write" => true,
        _ => {
            eprintln!("usage: paw upgrade [--write]");
            return USAGE;
        }
    };
    let (record, repository, root) = match open_record("upgrade") {
        Ok(opened) => opened,
        Err(code) => return code,
    };
    let profile_path = repository.join(PROFILE_SHOWN);
    let profile_text = std::fs::read_to_string(&profile_path).unwrap_or_default();
    let new_profile = without_retired_gate(&profile_text);
    if !old_form(&root) && new_profile.is_none() {
        say!("paw upgrade: nothing to upgrade; the record is in the form ADR-3090 states");
        return CLEAN;
    }
    let tasks = retired_docs(&root.join("tasks"), &repository);
    let epics = retired_docs(&root.join("epics"), &repository);
    let moves = plan(&record, &tasks, &epics);
    let verb = if write { "archived" } else { "would archive" };
    say!(
        "paw upgrade: {verb} {} and {}",
        count(tasks.len(), "task"),
        count(epics.len(), "epic")
    );
    let verb = if write { "folded" } else { "would fold" };
    for (task, carrier) in &moves.folded {
        say!("  {verb} {task} into {carrier}");
    }
    let verb = if write { "stored" } else { "would store" };
    for id in &moves.finished {
        say!("  {verb} done on {id}");
    }
    for task in &moves.orphans {
        say!("  {task} needs a decision: it is open and no live record authorises it");
    }
    if new_profile.is_some() {
        let verb = if write { "removed" } else { "would remove" };
        say!("  {verb} epic from the profile's gates");
    }
    for name in ["task.md", "epic.md"] {
        let own = repository.join(TEMPLATES_DIR).join(name);
        if own.is_file() {
            say!("  {TEMPLATES_DIR}{name} overrides a retired template, and is yours to remove");
        }
    }
    if !write {
        return CLEAN;
    }
    match apply(&record, &root, &tasks, &moves) {
        Ok(()) => {}
        Err(reason) => {
            say!("paw upgrade: {reason}");
            return FOUND;
        }
    }
    if let Some(text) = new_profile
        && let Err(e) = std::fs::write(&profile_path, text)
    {
        say!("paw upgrade: {}: {e}", profile_path.display());
        return FOUND;
    }
    regenerate(&["decision".to_string(), "defect".to_string()]);
    CLEAN
}

/// Writes the moves, the records first and the directories last, so a run that
/// stops leaves a record the next run finishes.
fn apply(record: &Record, root: &Path, tasks: &[Doc], moves: &Moves) -> Result<(), String> {
    let known = known(record);
    let mut grouped: BTreeMap<&str, Vec<String>> = BTreeMap::new();
    for (task, carrier) in &moves.folded {
        let Some(doc) = tasks.iter().find(|t| bare(t.id()) == task) else {
            continue;
        };
        let name = doc.path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        grouped
            .entry(carrier)
            .or_default()
            .push(format!("{} (`archive/tasks/{name}`)", title(doc)));
        if let Some(text) = with_added_field(&doc.text, "folded-into", carrier) {
            write_text(&doc.path, &text)?;
        }
    }
    for (carrier, steps) in grouped {
        if let Some(doc) = known.get(carrier) {
            write_text(&doc.path, &with_steps(&doc.text, &steps))?;
        }
    }
    for id in &moves.finished {
        let Some(doc) = known.get(id.as_str()) else {
            continue;
        };
        if let Some(text) = with_field(&doc.text, "status", "done") {
            write_text(&doc.path, &text)?;
        }
    }
    let archive = root.join("archive");
    std::fs::create_dir_all(&archive).map_err(|e| format!("{}: {e}", archive.display()))?;
    for dir in RETIRED_DIRS {
        let (from, to) = (root.join(dir), archive.join(dir));
        if from.is_dir() {
            std::fs::rename(&from, &to).map_err(|e| format!("{}: {e}", from.display()))?;
        }
    }
    Ok(())
}
