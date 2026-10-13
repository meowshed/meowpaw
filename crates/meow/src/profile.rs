// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! What every unit shares: the repository's root and its profile.
//!
//! A profile is absent, unparseable or parsed, and the three are reported
//! differently, because falling back on a profile that didn't parse would
//! ignore what the repository tried to say (RES-0261). A parsed profile comes
//! with each key the table of keys doesn't list, which every command that
//! reads the profile names and then ignores (ADR-2370).

#![allow(dead_code)]

use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

pub const PROFILE: &str = ".meowpaw/profile.toml";
/// The personal profile: one machine's own stages, kept out of the repository
/// (REQ-2944).
pub const PERSONAL: &str = ".meowpaw/profile.local.toml";

#[derive(Debug)]
pub enum Profile {
    Absent,
    /// The parser's message, after the line it gives where it gives one.
    Unparseable(String),
    /// The table, and each key in it the table of keys doesn't list.
    Parsed(toml::Table, Vec<String>),
}

/// One key a unit reads from the profile, and why the profile has to carry
/// it: the ecosystem doesn't declare it, the platform doesn't own it, it isn't
/// prose and detection can't produce it (REQ-2950).
#[derive(Clone)]
pub struct Key {
    pub path: &'static str,
    pub reason: &'static str,
}

const VERB: &str = "Only the repository knows the command its stage runs, and guessing one reports a pass nothing ran (REQ-0134)";
const WHOLE: &str = "The command a stage declared as a table runs over the whole work, and only the repository knows it (ADR-1520)";
const SUBSET: &str = "How the repository's tool takes a part of the work differs per tool, and no detection can tell it (ADR-1520)";

/// The table of keys: every key path a unit reads, with its reason. A key
/// whose path isn't here, and isn't a table on the way to one, is unknown. The
/// keys under a listed key with no entry below it, such as each type in
/// `commits.types`, are the repository's own names and aren't checked.
pub const KEYS: &[Key] = &[
    Key {
        path: "verbs.format",
        reason: VERB,
    },
    Key {
        path: "verbs.format.command",
        reason: WHOLE,
    },
    Key {
        path: "verbs.format.subset",
        reason: SUBSET,
    },
    Key {
        path: "verbs.lint",
        reason: VERB,
    },
    Key {
        path: "verbs.lint.command",
        reason: WHOLE,
    },
    Key {
        path: "verbs.lint.subset",
        reason: SUBSET,
    },
    Key {
        path: "verbs.check",
        reason: VERB,
    },
    Key {
        path: "verbs.check.command",
        reason: WHOLE,
    },
    Key {
        path: "verbs.check.subset",
        reason: SUBSET,
    },
    Key {
        path: "verbs.test",
        reason: VERB,
    },
    Key {
        path: "verbs.test.command",
        reason: WHOLE,
    },
    Key {
        path: "verbs.test.subset",
        reason: SUBSET,
    },
    Key {
        path: "verbs.build",
        reason: VERB,
    },
    Key {
        path: "verbs.build.command",
        reason: WHOLE,
    },
    Key {
        path: "verbs.build.subset",
        reason: SUBSET,
    },
    Key {
        path: "stages.format",
        reason: VERB,
    },
    Key {
        path: "stages.format.command",
        reason: WHOLE,
    },
    Key {
        path: "stages.format.subset",
        reason: SUBSET,
    },
    Key {
        path: "stages.lint",
        reason: VERB,
    },
    Key {
        path: "stages.lint.command",
        reason: WHOLE,
    },
    Key {
        path: "stages.lint.subset",
        reason: SUBSET,
    },
    Key {
        path: "stages.check",
        reason: VERB,
    },
    Key {
        path: "stages.check.command",
        reason: WHOLE,
    },
    Key {
        path: "stages.check.subset",
        reason: SUBSET,
    },
    Key {
        path: "stages.test",
        reason: VERB,
    },
    Key {
        path: "stages.test.command",
        reason: WHOLE,
    },
    Key {
        path: "stages.test.subset",
        reason: SUBSET,
    },
    Key {
        path: "stages.build",
        reason: VERB,
    },
    Key {
        path: "stages.build.command",
        reason: WHOLE,
    },
    Key {
        path: "stages.build.subset",
        reason: SUBSET,
    },
    Key {
        path: "commits.types",
        reason: "Which commit types a repository uses and what each means for a release is its own convention, and no ecosystem file declares it (REQ-1318)",
    },
    Key {
        path: "commits.subject_limit",
        reason: "The subject's length is the repository's choice, and the history shows only the subjects already written (REQ-1302)",
    },
    Key {
        path: "commits.trailers",
        reason: "The trailers every commit carries are the repository's rule, and a history that lacks them can't show it (REQ-1308)",
    },
    Key {
        path: "commits.may_name",
        reason: "Who agreed to be named in a trailer is a person's consent, which no file outside the repository records (REQ-2208)",
    },
    Key {
        path: "git.trunk",
        reason: "The branch nobody commits to is a decision, and the code host's default branch is a setting outside the repository (REQ-1292)",
    },
    Key {
        path: "git.require_signatures",
        reason: "Whether every pushed commit must be signed is the repository's policy, and no file git reads declares it (REQ-1326)",
    },
    Key {
        path: "tracker.kind",
        reason: "Which tracker the record is projected onto is a choice, and a code host with issues doesn't make it one (REQ-1351)",
    },
    Key {
        path: "record.root",
        reason: "Where the record lives is the repository's layout, and a directory of Markdown doesn't say it is the record (SPC-1070)",
    },
    Key {
        path: "docs.style",
        reason: "The documentation style is the repository's decision, and the pages already written can't name it (SPC-1090)",
    },
    Key {
        path: "markdown.target",
        reason: "The renderer a document is written for is outside the repository, and the Markdown alone doesn't name it (REQ-2452)",
    },
    Key {
        path: "licence.header",
        reason: "The header each new file carries is the project's legal choice, and a tool never picks a licence for it (REQ-1022)",
    },
    Key {
        path: "unattended.permission_mode",
        reason: "The permission an unattended run gets is a person's grant, and nothing in the repository can infer one",
    },
    Key {
        path: "unattended.release",
        reason: "The command that releases a merged change is the repository's, and a run never guesses one (REQ-3722)",
    },
    Key {
        path: "unattended.gates",
        reason: "Which gates a run passes alone is a person's grant of authority, and no detection can produce it",
    },
    Key {
        path: "unattended.amend_approved",
        reason: "Whether a run may edit an approved record is a person's grant, and the record can't grant it to itself",
    },
    Key {
        path: "prose.language",
        reason: "The language the repository's prose is written in is its choice, and the files already written may mix several",
    },
    Key {
        path: "method.principles",
        reason: "Which files hold the repository's principles is its choice, and no file name says a document is one",
    },
    Key {
        path: "parts",
        reason: "Only the project knows what it is built from, and a marker says which tool a directory uses, not which part it is (REQ-0343)",
    },
];

/// The keys a part's profile may hold: every key but the record's and the
/// parts', because the record stays at the root and a part declares no parts
/// of its own (REQ-3046).
fn part_keys() -> Vec<&'static str> {
    KEYS.iter()
        .map(|key| key.path)
        .filter(|path| *path != "parts" && *path != "record" && !path.starts_with("record."))
        .collect()
}

/// One part the root profile declares under `[parts]`: its name, and its
/// directory relative to the root, written without a leading `./` or a
/// trailing `/` (REQ-0343).
#[derive(Clone, Debug, PartialEq)]
pub struct Part {
    pub name: String,
    pub directory: String,
}

/// The parts the root profile declares, in the order it gives them, and a line
/// for each entry that names no directory inside the repository. A profile
/// with no `[parts]` declares none, and the repository is one part, its root.
pub fn parts(table: &toml::Table) -> (Vec<Part>, Vec<String>) {
    let mut found = Vec::new();
    let mut problems = Vec::new();
    let Some(declared) = table.get("parts") else {
        return (found, problems);
    };
    let Some(declared) = declared.as_table() else {
        problems.push(
            "profile: [parts] isn't a table; write one line a part, name = \"directory\""
                .to_string(),
        );
        return (found, problems);
    };
    for (name, value) in declared {
        let directory = value.as_str().and_then(part_directory);
        match directory {
            Some(directory) => found.push(Part {
                name: name.clone(),
                directory,
            }),
            None => problems.push(format!(
                "profile: part {name} names no directory inside the repository; write {name} = \"<directory>\" under [parts]"
            )),
        }
    }
    (found, problems)
}

/// A part's directory as written, without `./` or a trailing `/`, or `None`
/// where it is empty, the root itself, absolute, or climbs out with `..`.
fn part_directory(text: &str) -> Option<String> {
    let trimmed = text.trim().trim_end_matches('/');
    let trimmed = trimmed.strip_prefix("./").unwrap_or(trimmed);
    let path = Path::new(trimmed);
    let inside = path
        .components()
        .all(|part| matches!(part, std::path::Component::Normal(_)));
    (inside && !trimmed.is_empty()).then(|| trimmed.to_string())
}

/// Where a part's own profile would be.
pub fn part_profile(root: &Path, part: &Part) -> PathBuf {
    root.join(&part.directory).join(PROFILE)
}

/// The profile a part reads: the root's, with the part's own
/// `.meowpaw/profile.toml` read over it where the part's directory holds one
/// (REQ-3040). A key the part declares replaces the root's, and the part's
/// stages are the ones it declares and never the root's. A `[record]` or
/// `[parts]` in the part's profile is reported as an unknown key and the
/// root's stands (REQ-3046). The tool reads both files itself and relies on no
/// setting the platform inherits from a parent directory.
pub fn read_part(root: &Path, part: &Part) -> Profile {
    let shared = read(root);
    let own = part_profile(root, part);
    if !own.is_file() {
        return shared;
    }
    let shown = format!("{}/{PROFILE}", part.directory);
    let text = match std::fs::read(&own).map(String::from_utf8) {
        Ok(Ok(text)) => text,
        Ok(Err(error)) => return Profile::Unparseable(format!("{shown}: {error}")),
        Err(error) => return Profile::Unparseable(format!("{shown}: {error}")),
    };
    let table = match text.parse::<toml::Table>() {
        Ok(table) => table,
        Err(error) => {
            let message = error
                .message()
                .lines()
                .map(str::trim)
                .filter(|line| !line.is_empty())
                .collect::<Vec<_>>()
                .join("; ");
            return match error.span() {
                Some(span) => {
                    let line = text[..span.start.min(text.len())].matches('\n').count() + 1;
                    Profile::Unparseable(format!("{shown}: line {line}: {message}"))
                }
                None => Profile::Unparseable(format!("{shown}: {message}")),
            };
        }
    };
    let (base, mut unknown) = match shared {
        Profile::Unparseable(message) => return Profile::Unparseable(message),
        Profile::Absent => (toml::Table::new(), Vec::new()),
        Profile::Parsed(table, unknown) => (table, unknown),
    };
    let mut found = Vec::new();
    unknown_among(&table, "", &part_keys(), &mut found);
    unknown.extend(found.into_iter().map(|key| format!("{key} (in {shown})")));
    Profile::Parsed(layer(&base, &table), unknown)
}

/// The root's table with the part's read over it.
fn layer(root: &toml::Table, part: &toml::Table) -> toml::Table {
    let mut out = root.clone();
    out.remove("stages");
    out.remove("verbs");
    for (key, value) in part {
        if key == "record" || key == "parts" {
            continue;
        }
        over(&mut out, key, value);
    }
    out
}

/// Sets `key` in `table` to `value`, merging where both are tables, so the
/// part replaces each key it declares and keeps the root's others.
fn over(table: &mut toml::Table, key: &str, value: &toml::Value) {
    match (table.get_mut(key), value) {
        (Some(toml::Value::Table(inner)), toml::Value::Table(theirs)) => {
            for (name, value) in theirs {
                over(inner, name, value);
            }
        }
        _ => {
            table.insert(key.to_string(), value.clone());
        }
    }
}

/// Each entry in `keys` whose reason is empty.
fn unreasoned(keys: &[Key]) -> Vec<&'static str> {
    keys.iter()
        .filter(|key| key.reason.trim().is_empty())
        .map(|key| key.path)
        .collect()
}

/// Each key path in `table`, under `prefix`, that `known` doesn't list, in the
/// order the profile gives them.
fn unknown_among(table: &toml::Table, prefix: &str, known: &[&str], out: &mut Vec<String>) {
    for (name, value) in table {
        let path = if prefix.is_empty() {
            name.clone()
        } else {
            format!("{prefix}.{name}")
        };
        let below = format!("{path}.");
        let listed = known.iter().any(|key| *key == path);
        let leads = known.iter().any(|key| key.starts_with(&below));
        if !listed && !leads {
            out.push(path);
        } else if leads && let toml::Value::Table(inner) = value {
            unknown_among(inner, &path, known, out);
        }
    }
}

/// Each key path in `table` that the table of keys doesn't list.
fn unknown(table: &toml::Table, prefix: &str, out: &mut Vec<String>) {
    let known: Vec<&str> = KEYS.iter().map(|key| key.path).collect();
    unknown_among(table, prefix, &known, out);
}

/// The personal profile as read: absent, unparseable, or the table and each
/// key in it that a personal profile may not hold. Only the stage tables are
/// known there, because the file confines itself to one machine's stages
/// (ADR-2370).
pub enum Personal {
    Absent,
    Unparseable(String),
    Parsed(toml::Table, Vec<String>),
}

pub fn read_personal(root: &Path) -> Personal {
    let path = root.join(PERSONAL);
    if !path.is_file() {
        return Personal::Absent;
    }
    let text = match std::fs::read_to_string(&path) {
        Ok(text) => text,
        Err(error) => return Personal::Unparseable(error.to_string()),
    };
    match text.parse::<toml::Table>() {
        Ok(table) => {
            let known: Vec<&str> = KEYS
                .iter()
                .map(|key| key.path)
                .filter(|path| path.starts_with("stages.") || path.starts_with("verbs."))
                .collect();
            let mut found = Vec::new();
            unknown_among(&table, "", &known, &mut found);
            Personal::Parsed(table, found)
        }
        Err(error) => Personal::Unparseable(
            error
                .message()
                .lines()
                .map(str::trim)
                .filter(|line| !line.is_empty())
                .collect::<Vec<_>>()
                .join("; "),
        ),
    }
}

/// The table that declares the stages: `[stages]`, and `[verbs]` where the
/// profile has no `[stages]` (REQ-4202, REQ-4204).
pub fn stages(table: &toml::Table) -> Option<&toml::Value> {
    table.get("stages").or_else(|| table.get("verbs"))
}

/// What a profile that still declares `[stages]` is told, one line a notice.
fn deprecations(table: &toml::Table) -> Vec<String> {
    match (table.contains_key("verbs"), table.contains_key("stages")) {
        (true, true) => vec![
            "profile: [verbs] and [stages] are both declared; [stages] wins, so remove [verbs]"
                .to_string(),
        ],
        (true, false) => {
            vec!["profile: [verbs] is deprecated; declare the stages under [stages]".to_string()]
        }
        _ => Vec::new(),
    }
}

/// The lines every command that reads the profile prints: its state, then
/// the parser's message or each unknown key, one line a key (SPC-1080).
pub fn report(profile: &Profile) -> Vec<String> {
    match profile {
        Profile::Absent => vec!["profile: absent".to_string()],
        Profile::Unparseable(message) => vec![
            "profile: unparseable".to_string(),
            format!("profile error: {message}"),
        ],
        Profile::Parsed(table, unknown) => std::iter::once("profile: parsed".to_string())
            .chain(unknown.iter().map(|key| format!("unknown key: {key}")))
            .chain(deprecations(table))
            .collect(),
    }
}

/// Source control run to read it, never to record authorship: nothing
/// prompts, pages, advises or reads the machine-wide configuration, so a
/// missing credential fails where it would wait (REQ-2526, REQ-2528). The
/// user's own configuration stays, because it holds their identity and keys.
pub fn reading_git() -> Command {
    let mut git = Command::new("git");
    git.env("GIT_TERMINAL_PROMPT", "0")
        .env("GIT_PAGER", "cat")
        .env("GIT_ADVICE", "0")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .env("GIT_OPTIONAL_LOCKS", "0")
        .stdin(Stdio::null());
    git
}

/// The top of the working tree, or the current directory where there is none.
pub fn repository_root() -> PathBuf {
    let top = reading_git()
        .args(["rev-parse", "--show-toplevel"])
        .output();
    if let Ok(done) = top {
        let text = String::from_utf8_lossy(&done.stdout).trim().to_string();
        if done.status.success() && !text.is_empty() {
            return PathBuf::from(text);
        }
    }
    std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."))
}

pub fn read(root: &Path) -> Profile {
    let path = root.join(PROFILE);
    if !path.is_file() {
        return Profile::Absent;
    }
    let bytes = match std::fs::read(&path) {
        Ok(bytes) => bytes,
        Err(error) => return Profile::Unparseable(error.to_string()),
    };
    let text = match String::from_utf8(bytes) {
        Ok(text) => text,
        Err(error) => return Profile::Unparseable(error.to_string()),
    };
    match text.parse::<toml::Table>() {
        Ok(table) => {
            let mut found = Vec::new();
            unknown(&table, "", &mut found);
            Profile::Parsed(table, found)
        }
        Err(error) => {
            let message = error
                .message()
                .lines()
                .map(str::trim)
                .filter(|line| !line.is_empty())
                .collect::<Vec<_>>()
                .join("; ");
            match error.span() {
                Some(span) => {
                    let line = text[..span.start.min(text.len())].matches('\n').count() + 1;
                    Profile::Unparseable(format!("line {line}: {message}"))
                }
                None => Profile::Unparseable(message),
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn with_profile(text: Option<&str>) -> (tempdir::Dir, Profile) {
        let dir = tempdir::Dir::new();
        if let Some(text) = text {
            std::fs::create_dir_all(dir.path().join(".meowpaw")).unwrap();
            std::fs::write(dir.path().join(PROFILE), text).unwrap();
        }
        let read = read(dir.path());
        (dir, read)
    }

    /// Every file under `dir` with one of `extensions`, recursively.
    fn files(dir: &Path, extensions: &[&str], out: &mut Vec<PathBuf>) {
        let Ok(entries) = std::fs::read_dir(dir) else {
            return;
        };
        for entry in entries.flatten() {
            let path = entry.path();
            let name = entry.file_name().to_string_lossy().to_string();
            if path.is_dir() && !["target", "evals", "tests", ".git"].contains(&name.as_str()) {
                files(&path, extensions, out);
            } else if extensions.iter().any(|e| name.ends_with(e)) {
                out.push(path);
            }
        }
    }

    /// TSK-5145, REQ-3800: comments before a table, beside a value and after
    /// it stay valid TOML the parser reads.
    #[test]
    fn a_profile_with_comments_parses() {
        let text = "# the stages the repository declares\n\n[stages]\n# one stage per line\ntest = \"true\" # the command the shell runs\n\n# the record lives here\n[record]\nroot = \"project\"\n";
        let (_dir, profile) = with_profile(Some(text));
        let Profile::Parsed(table, unknown) = &profile else {
            panic!("the profile with comments didn't parse: {profile:?}");
        };
        assert!(unknown.is_empty(), "{unknown:?}");
        let declared = stages(table).and_then(toml::Value::as_table).unwrap();
        assert!(declared.contains_key("test"));
    }

    /// TSK-5270, criterion 1, REQ-4202: a `[stages]` table is the declaration,
    /// and nothing about it is deprecated.
    #[test]
    fn a_stages_table_is_the_declaration_and_names_no_deprecation() {
        let (_dir, profile) = with_profile(Some("[stages]\ntest = \"true\"\n"));
        let Profile::Parsed(table, unknown) = &profile else {
            panic!("the profile didn't parse");
        };
        assert!(unknown.is_empty(), "{unknown:?}");
        assert_eq!(report(&profile), ["profile: parsed"]);
        let declared = stages(table).and_then(toml::Value::as_table).unwrap();
        assert!(declared.contains_key("test"));
    }

    /// TSK-5270, criterion 2, REQ-4204: a `[verbs]` table still declares them,
    /// and the report names `[stages]` as the table to use.
    #[test]
    fn a_verbs_table_declares_the_stages_and_names_the_table_to_use() {
        let (_dir, profile) = with_profile(Some("[verbs]\ntest = \"true\"\n"));
        let Profile::Parsed(table, _) = &profile else {
            panic!("the profile didn't parse");
        };
        let declared = stages(table).and_then(toml::Value::as_table).unwrap();
        assert!(declared.contains_key("test"));
        let lines = report(&profile);
        assert_eq!(lines[0], "profile: parsed");
        assert!(
            lines
                .iter()
                .any(|line| line.contains("[verbs]") && line.contains("[stages]")),
            "{lines:?}"
        );
    }

    /// TSK-5270, criterion 3, REQ-4204: with both tables, `[stages]` wins and
    /// the report names the duplicate.
    #[test]
    fn with_both_tables_stages_wins_and_the_report_names_the_duplicate() {
        let (_dir, profile) =
            with_profile(Some("[verbs]\ntest = \"old\"\n[stages]\ntest = \"new\"\n"));
        let Profile::Parsed(table, _) = &profile else {
            panic!("the profile didn't parse");
        };
        let declared = stages(table).and_then(toml::Value::as_table).unwrap();
        assert_eq!(
            declared.get("test").and_then(toml::Value::as_str),
            Some("new")
        );
        let lines = report(&profile);
        assert!(lines.iter().any(|line| line.contains("both")), "{lines:?}");
    }

    #[test]
    fn a_read_takes_no_optional_lock() {
        // REQ-2524: a read never takes the index lock or refreshes the index.
        let git = reading_git();
        let set = git
            .get_envs()
            .any(|(k, v)| k == "GIT_OPTIONAL_LOCKS" && v == Some(std::ffi::OsStr::new("0")));
        assert!(set, "the reading helper doesn't set GIT_OPTIONAL_LOCKS=0");
    }

    #[test]
    fn git_starts_only_in_the_reading_helper() {
        // REQ-2524: a git started elsewhere would read without the helper's settings.
        let pattern = format!("Command::new({:?})", "git");
        let mut sources = Vec::new();
        files(
            &Path::new(env!("CARGO_MANIFEST_DIR")).join("src"),
            &[".rs"],
            &mut sources,
        );
        let outside: Vec<String> = sources
            .iter()
            .filter(|p| p.file_name().is_some_and(|n| n != "profile.rs"))
            .filter(|p| {
                std::fs::read_to_string(p)
                    .unwrap_or_default()
                    .contains(&pattern)
            })
            .map(|p| p.display().to_string())
            .collect();
        assert!(
            outside.is_empty(),
            "git started outside the reading helper in {outside:?}"
        );
    }

    #[test]
    fn nothing_the_harness_ships_writes_global_git_configuration() {
        // REQ-2540: configuration outside the repository reaches every repository on the machine.
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("..").join("..");
        let mut scanned = Vec::new();
        files(
            &Path::new(env!("CARGO_MANIFEST_DIR")).join("src"),
            &[".rs"],
            &mut scanned,
        );
        files(
            &root.join("plugins"),
            &[".md", ".json", ".toml"],
            &mut scanned,
        );
        files(&root.join(".github"), &[".yml", ".yaml"], &mut scanned);
        let command = ["git", "config"].join(" ");
        let scopes = [["--", "global"].concat(), ["--", "system"].concat()];
        let mut found = Vec::new();
        for path in &scanned {
            for (n, line) in std::fs::read_to_string(path)
                .unwrap_or_default()
                .lines()
                .enumerate()
            {
                if line.contains(&command) && scopes.iter().any(|s| line.contains(s.as_str())) {
                    found.push(format!("{}:{}", path.display(), n + 1));
                }
            }
        }
        assert!(
            scanned.len() > 20,
            "scanned only {} files, so the scan found nothing to judge",
            scanned.len()
        );
        assert!(
            found.is_empty(),
            "global or system git configuration written at {found:?}"
        );
    }

    /// A root profile and each part's own, written under one directory.
    fn with_parts(root: &str, parts: &[(&str, &str)]) -> tempdir::Dir {
        let dir = tempdir::Dir::new();
        std::fs::create_dir_all(dir.path().join(".meowpaw")).unwrap();
        std::fs::write(dir.path().join(PROFILE), root).unwrap();
        for (directory, text) in parts {
            let at = dir.path().join(directory).join(".meowpaw");
            std::fs::create_dir_all(&at).unwrap();
            std::fs::write(at.join("profile.toml"), text).unwrap();
        }
        dir
    }

    const TWO_PARTS: &str = "[stages]\ntest = \"root-test\"\nlint = \"root-lint\"\n\n[record]\nroot = \"project\"\n\n[parts]\nsite = \"site/\"\ncrate = \"./crates/x\"\n";

    /// TSK-5050 criterion 1, REQ-0343: the root profile declares its parts,
    /// each a name and a directory, and `parts` is no unknown key.
    #[test]
    fn the_root_profile_declares_its_parts() {
        let dir = with_parts(TWO_PARTS, &[]);
        let Profile::Parsed(table, unknown) = read(dir.path()) else {
            panic!("the profile didn't parse");
        };
        assert_eq!(unknown, Vec::<String>::new());
        let (found, problems) = parts(&table);
        assert_eq!(problems, Vec::<String>::new());
        assert_eq!(
            found,
            [
                Part {
                    name: "site".into(),
                    directory: "site".into()
                },
                Part {
                    name: "crate".into(),
                    directory: "crates/x".into()
                },
            ]
        );
    }

    /// TSK-5050 criterion 1, REQ-0343: an entry naming no directory inside
    /// the repository is reported, and never taken as a part.
    #[test]
    fn a_part_outside_the_repository_is_reported() {
        let table: toml::Table = "[parts]\nup = \"../other\"\nroot = \"/\"\nnone = 3\nok = \"a\"\n"
            .parse()
            .unwrap();
        let (found, problems) = parts(&table);
        assert_eq!(found.len(), 1, "{found:?}");
        assert_eq!(found[0].directory, "a");
        assert_eq!(problems.len(), 3, "{problems:?}");
    }

    /// TSK-5050 criterion 2, REQ-3040: a part's profile is read over the
    /// root's, and a stage the part leaves out is unresolved there, never the
    /// root's.
    #[test]
    fn a_part_declares_its_own_stages_and_takes_none_from_the_root() {
        let dir = with_parts(
            TWO_PARTS,
            &[(
                "site",
                "[stages]\ntest = \"site-test\"\n\n[markdown]\ntarget = \"hugo\"\n",
            )],
        );
        let Profile::Parsed(table, _) = read(dir.path()) else {
            panic!("the profile didn't parse");
        };
        let (found, _) = parts(&table);
        let Profile::Parsed(site, unknown) = read_part(dir.path(), &found[0]) else {
            panic!("the part's profile didn't parse");
        };
        assert_eq!(unknown, Vec::<String>::new());
        let declared = stages(&site).and_then(toml::Value::as_table).unwrap();
        assert_eq!(
            declared.get("test").and_then(toml::Value::as_str),
            Some("site-test")
        );
        assert!(declared.get("lint").is_none(), "{declared:?}");
        assert_eq!(
            site.get("markdown").and_then(|m| m.get("target")),
            Some(&toml::Value::from("hugo"))
        );
        // A part with no profile of its own reads the root's.
        let Profile::Parsed(whole, _) = read_part(dir.path(), &found[1]) else {
            panic!("the root's profile didn't parse");
        };
        let declared = stages(&whole).and_then(toml::Value::as_table).unwrap();
        assert_eq!(
            declared.get("lint").and_then(toml::Value::as_str),
            Some("root-lint")
        );
    }

    /// TSK-5050 criterion 3, REQ-3046: a part's `[record]` and `[parts]` are
    /// unknown keys, and the root's record and parts stand.
    #[test]
    fn a_parts_record_and_parts_are_unknown_and_the_roots_stand() {
        let dir = with_parts(
            TWO_PARTS,
            &[(
                "site",
                "[stages]\ntest = \"t\"\n\n[record]\nroot = \"elsewhere\"\n\n[parts]\ninner = \"x\"\n",
            )],
        );
        let site = Part {
            name: "site".into(),
            directory: "site".into(),
        };
        let Profile::Parsed(table, unknown) = read_part(dir.path(), &site) else {
            panic!("the part's profile didn't parse");
        };
        assert_eq!(
            unknown,
            [
                format!("record (in site/{PROFILE})"),
                format!("parts (in site/{PROFILE})")
            ]
        );
        assert_eq!(
            table.get("record").and_then(|r| r.get("root")),
            Some(&toml::Value::from("project"))
        );
        assert_eq!(parts(&table).0.len(), 2);
    }

    /// TSK-5050 criterion 2: a part's profile that doesn't parse is reported
    /// with its path, and nothing falls back to the root's.
    #[test]
    fn a_parts_broken_profile_is_unparseable_and_names_its_file() {
        let dir = with_parts(TWO_PARTS, &[("site", "[stages\n")]);
        let site = Part {
            name: "site".into(),
            directory: "site".into(),
        };
        match read_part(dir.path(), &site) {
            Profile::Unparseable(message) => {
                assert!(
                    message.starts_with("site/.meowpaw/profile.toml: line 1"),
                    "{message}"
                )
            }
            other => panic!("expected unparseable, got {other:?}"),
        }
    }

    #[test]
    fn a_missing_profile_is_absent() {
        assert!(matches!(with_profile(None).1, Profile::Absent));
    }

    #[test]
    fn a_broken_profile_is_unparseable_and_says_why() {
        match with_profile(Some("[verbs\n")).1 {
            Profile::Unparseable(message) => assert!(!message.is_empty()),
            _ => panic!("expected unparseable"),
        }
    }

    #[test]
    fn a_profile_parses_into_its_tables() {
        match with_profile(Some("[verbs]\nlint = \"true\"\n")).1 {
            Profile::Parsed(table, _) => assert!(table.contains_key("verbs")),
            _ => panic!("expected parsed"),
        }
    }

    #[test]
    fn every_key_in_the_table_carries_a_reason() {
        // TSK-4300 criterion 4, REQ-2950: a key without its reason is one
        // nobody showed the profile has to carry.
        assert!(KEYS.len() > 20, "the table holds only {} keys", KEYS.len());
        assert_eq!(unreasoned(KEYS), Vec::<&str>::new());
        let added = [
            KEYS,
            &[Key {
                path: "verbs.added",
                reason: " ",
            }],
        ]
        .concat();
        assert_eq!(unreasoned(&added), ["verbs.added"]);
    }

    #[test]
    fn this_repositorys_profile_names_no_unknown_key() {
        // TSK-4300 criterion 5: every key this repository declares is one a unit reads.
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("..").join("..");
        match read(&root) {
            Profile::Parsed(_, unknown) => assert_eq!(unknown, Vec::<String>::new()),
            _ => panic!("this repository's profile doesn't parse"),
        }
    }

    mod tempdir {
        use std::path::{Path, PathBuf};

        pub struct Dir(PathBuf);

        impl Dir {
            pub fn new() -> Dir {
                // Tests run in parallel threads of one process, and two of them
                // can read the same clock, so a counter keeps each directory
                // its own.
                static NEXT: std::sync::atomic::AtomicUsize =
                    std::sync::atomic::AtomicUsize::new(0);
                let n = NEXT.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                let stamp = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_nanos();
                let path = std::env::temp_dir()
                    .join(format!("meow-test-{}-{n}-{stamp}", std::process::id()));
                std::fs::create_dir_all(&path).unwrap();
                Dir(path)
            }

            pub fn path(&self) -> &Path {
                &self.0
            }
        }

        impl Drop for Dir {
            fn drop(&mut self) {
                let _ = std::fs::remove_dir_all(&self.0);
            }
        }
    }
}
