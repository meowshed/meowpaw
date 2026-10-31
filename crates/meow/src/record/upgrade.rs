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

/// The records of one retired directory, its index left out, and each file
/// that can't be read as a record, which moves unread.
fn retired_docs(dir: &Path, repository: &Path) -> (Vec<Doc>, Vec<String>) {
    let mut paths = Vec::new();
    if dir.is_dir() {
        markdown_under(dir, None, &mut paths);
    }
    paths.sort();
    let (mut docs, mut unread) = (Vec::new(), Vec::new());
    for path in paths {
        let doc = read_doc(path, repository);
        if !bare(doc.id()).is_empty() {
            docs.push(doc);
        } else if doc.path.file_name().and_then(|n| n.to_str()) != Some("README.md") {
            unread.push(doc.shown);
        }
    }
    (docs, unread)
}

/// The mark a task's stored status settles, where it does.
fn final_mark(task: &Doc) -> Option<char> {
    match bare(task.value("status")) {
        "done" => Some('x'),
        "withdrawn" | "rejected" | "superseded" => Some('~'),
        _ => None,
    }
}

/// A task's own state, as the old record derived it: settled by a final
/// status, done once its Evidence is written, and open otherwise.
fn own_mark(task: &Doc) -> char {
    if let Some(mark) = final_mark(task) {
        return mark;
    }
    let said = section_lines(task, "Evidence")
        .into_iter()
        .map(|(_, line)| line.trim())
        .find(|line| !line.is_empty());
    if said.is_some_and(|line| !line.starts_with("Not yet")) {
        'x'
    } else {
        ' '
    }
}

/// Each task an epic or a defect lists, with its mark. A final status wins over
/// a list that went stale, and an unmarked entry takes its state from the task.
fn listed_marks(doc: &Doc, tasks: &BTreeMap<String, &Doc>) -> Vec<(String, char)> {
    let mut out = Vec::new();
    let mut inside = false;
    for line in doc.text.lines() {
        if let Some(heading) = line.strip_prefix("## ") {
            inside = heading.trim() == "Tasks";
        } else if inside && let Some(found) = ENTRY.captures(line) {
            let id = found[2].to_string();
            let task = tasks.get(&id);
            let mark = task
                .and_then(|t| final_mark(t))
                .or_else(|| found.get(1).and_then(|m| m.as_str().chars().next()))
                .unwrap_or_else(|| task.map_or(' ', |t| own_mark(t)));
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
    /// Finished tasks whose status doesn't say so yet, with the status that does.
    settled: Vec<(String, &'static str)>,
    /// Approved decisions with work and no plan, which a person has to plan.
    planless: Vec<String>,
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
        let mark = listed.get(&id).copied().unwrap_or_else(|| own_mark(task));
        if matches!(mark, 'x' | '~') {
            if final_mark(task).is_none() {
                let status = if mark == 'x' { "done" } else { "withdrawn" };
                moves.settled.push((id, status));
            }
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
    // A record that takes open work on isn't finished, whatever its own list
    // says: an epic of another decision can list a defect's task.
    let carriers: Vec<String> = moves.folded.iter().map(|(_, c)| c.clone()).collect();
    moves.finished.retain(|id| !carriers.contains(id));
    for decision in of_kind(record, "decision") {
        let id = bare(decision.id()).to_string();
        if bare(decision.value("status")) == "approved"
            && !requirements_in(record, decision.value("addresses")).is_empty()
            && !has_plan(decision)
            && !carriers.contains(&id)
            && !moves.finished.contains(&id)
        {
            moves.planless.push(id);
        }
    }
    moves.folded.sort();
    moves.orphans.sort();
    moves.finished.sort();
    moves.planless.sort();
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

/// The profile's text with the retired step gone from `[unattended] gates`, or
/// nothing where that list doesn't name it. The list is read as TOML and only
/// its span is rewritten, so every other line stays as it was.
fn without_retired_gate(text: &str) -> Option<String> {
    let table: toml::Table = text.parse().ok()?;
    let gates = table.get("unattended")?.get("gates")?.as_array()?;
    let kept: Vec<&str> = gates
        .iter()
        .filter_map(|gate| gate.as_str())
        .filter(|gate| *gate != "epic")
        .collect();
    if kept.len() == gates.len() {
        return None;
    }
    let (start, end) = gates_span(text)?;
    let list: Vec<String> = kept.iter().map(|gate| format!("\"{gate}\"")).collect();
    Some(format!(
        "{}[{}]{}",
        &text[..start],
        list.join(", "),
        &text[end..]
    ))
}

/// Where the `gates` array of `[unattended]` starts and ends in the text.
fn gates_span(text: &str) -> Option<(usize, usize)> {
    let (mut offset, mut inside) = (0, false);
    for line in text.split_inclusive('\n') {
        let bare = line.split('#').next().unwrap_or("").trim();
        if bare.starts_with('[') {
            inside = bare == "[unattended]";
        } else if inside && bare.split('=').next().map(str::trim) == Some("gates") {
            let start = offset + line.find('[')?;
            return Some((start, start + array_length(&text[start..])?));
        }
        offset += line.len();
    }
    None
}

/// The length of the TOML array that opens `text`, reading past strings and
/// comments, where a bracket means nothing.
fn array_length(text: &str) -> Option<usize> {
    let (mut depth, mut quote, mut comment) = (0usize, None, false);
    for (at, c) in text.char_indices() {
        match (quote, c) {
            _ if comment => comment = c != '\n',
            (Some(open), _) if open == c => quote = None,
            (Some(_), _) => {}
            (None, '"' | '\'') => quote = Some(c),
            (None, '#') => comment = true,
            (None, '[') => depth += 1,
            (None, ']') => {
                depth -= 1;
                if depth == 0 {
                    return Some(at + 1);
                }
            }
            _ => {}
        }
    }
    None
}

/// A record's text with each folded task added as a step of its `## Plan`. A
/// step already there is left out, so a rerun after an interrupted one adds
/// nothing.
fn with_steps(text: &str, steps: &[String]) -> String {
    let steps: Vec<&String> = steps
        .iter()
        .filter(|step| !text.contains(step.as_str()))
        .collect();
    if steps.is_empty() {
        return text.to_string();
    }
    let outline = outline(text);
    let mut lines: Vec<String> = outline.iter().map(|(l, ..)| l.to_string()).collect();
    let items = Regex::new(r"^(\d+)\. ").expect("step pattern");
    let opened = outline.iter().position(|(.., h)| *h == Some("Plan"));
    let (end, first) = match opened {
        Some(at) => {
            let end = outline[at + 1..]
                .iter()
                .position(|(.., h)| h.is_some())
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

/// The text with `key: value` added after the status line of its front matter.
pub(super) fn with_added_field(text: &str, key: &str, value: &str) -> Option<String> {
    let mut at = 0;
    for (i, line) in text.split_inclusive('\n').enumerate() {
        let bare = line.trim_end();
        if i == 0 && bare != "---" || i > 0 && bare == "---" {
            return None;
        }
        at += line.len();
        if bare.starts_with("status:") {
            return Some(format!("{}{key}: {value}\n{}", &text[..at], &text[at..]));
        }
    }
    None
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
    let (tasks, mut unread) = retired_docs(&root.join("tasks"), &repository);
    let (epics, others) = retired_docs(&root.join("epics"), &repository);
    unread.extend(others);
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
    for (task, status) in &moves.settled {
        say!("  {verb} {status} on {task}");
    }
    for task in &moves.orphans {
        say!("  {task} needs a decision: it is open and no live record authorises it");
    }
    for id in &moves.planless {
        say!("  {id} needs a plan: it is approved, addresses work and no task carries it");
    }
    for path in &unread {
        say!("  {path} can't be read as a record, and moves unread");
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
    let archive = root.join("archive");
    for dir in RETIRED_DIRS {
        if let Some(name) = taken_name(&root.join(dir), &archive.join(dir)) {
            return Err(format!(
                "archive/{dir} already holds {name}; nothing was written"
            ));
        }
    }
    let known = known(record);
    let mut grouped: BTreeMap<&str, Vec<String>> = BTreeMap::new();
    for (task, status) in &moves.settled {
        let Some(doc) = tasks.iter().find(|t| bare(t.id()) == task) else {
            continue;
        };
        if let Some(text) = with_field(&doc.text, "status", status) {
            write_text(&doc.path, &text)?;
        }
    }
    for (task, carrier) in &moves.folded {
        let Some(doc) = tasks.iter().find(|t| bare(t.id()) == task) else {
            continue;
        };
        let name = doc.path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        grouped
            .entry(carrier)
            .or_default()
            .push(format!("{} (`archive/tasks/{name}`)", title(doc)));
        let text = with_field(&doc.text, "folded-into", carrier)
            .or_else(|| with_added_field(&doc.text, "folded-into", carrier));
        if let Some(text) = text {
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
    for dir in RETIRED_DIRS {
        move_files(&root.join(dir), &archive.join(dir))?;
    }
    Ok(())
}

/// A file of `from` that `to` already holds, which a move would overwrite.
fn taken_name(from: &Path, to: &Path) -> Option<String> {
    std::fs::read_dir(from)
        .ok()?
        .filter_map(Result::ok)
        .map(|entry| entry.file_name())
        .find(|name| to.join(name).exists())
        .map(|name| name.to_string_lossy().into_owned())
}

/// Moves each file of `from` into `to`, then removes `from`, so a directory
/// half moved by an interrupted run is finished by the next.
fn move_files(from: &Path, to: &Path) -> Result<(), String> {
    if !from.is_dir() {
        return Ok(());
    }
    let shown = |e: std::io::Error| format!("{}: {e}", from.display());
    std::fs::create_dir_all(to).map_err(shown)?;
    for entry in std::fs::read_dir(from).map_err(shown)? {
        let entry = entry.map_err(shown)?;
        std::fs::rename(entry.path(), to.join(entry.file_name())).map_err(shown)?;
    }
    std::fs::remove_dir(from).map_err(shown)
}
