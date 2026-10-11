// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Every subcommand outside `paw` names what a person reads in its place and
//! the first word of each kind of line it prints, and its output on a fixture
//! holds to that (TSK-4340, SPC-1080 "Each subcommand makes one determination").

#![cfg(all(
    feature = "verbs",
    feature = "scm",
    feature = "git",
    feature = "github",
    feature = "licence",
    feature = "author",
    feature = "mise",
    feature = "gotask",
    feature = "prose",
    feature = "markdown",
    feature = "unattended",
    feature = "loop"
))]

use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

thread_local! {
    /// The lines whose first word a help doesn't state, gathered so one run
    /// names them all.
    static MISSING: std::cell::RefCell<Vec<String>> = const { std::cell::RefCell::new(Vec::new()) };
}

/// Fails with every line `held` found whose first word a help doesn't state.
fn none_missing() {
    let missing = MISSING.with(|m| std::mem::take(&mut *m.borrow_mut()));
    assert!(
        missing.is_empty(),
        "lines opening with a word the help doesn't state:\n{}",
        missing.join("\n")
    );
}

/// `text` without the `<...>` and `[...]` groups of a usage line, whose bars
/// don't separate subcommands.
fn without_groups(text: &str) -> String {
    let mut out = String::new();
    let mut depth = 0usize;
    for c in text.chars() {
        match c {
            '<' | '[' => depth += 1,
            '>' | ']' => depth = depth.saturating_sub(1),
            c if depth == 0 => out.push(c),
            _ => {}
        }
    }
    out
}

/// Each unit's subcommand of `paw`, and the name its usage line gives it.
const UNITS: [(&str, &str); 12] = [
    ("verbs", "meow-checks"),
    ("scm", "meow-scm"),
    ("git", "meow-git"),
    ("github", "meow-github"),
    ("licence", "meow-licence"),
    ("author", "meow-author"),
    ("mise", "meow-mise"),
    ("gotask", "meow-gotask"),
    ("prose", "meow-prose-gate"),
    ("markdown", "meow-markdown"),
    ("unattended", "meow-unattended"),
    ("loop", "meow-loop"),
];

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "meow-unit-help-{name}-{}-{stamp}",
            std::process::id()
        ));
        std::fs::create_dir_all(&path).unwrap();
        Dir(path)
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn git(dir: &Path, args: &[&str]) {
    let done = Command::new("git")
        .args(args)
        .current_dir(dir)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap();
    assert!(done.status.success(), "git {args:?} failed: {done:?}");
}

/// A repository with a profile that binds every stage, one commit and a
/// state directory of its own.
fn fixture(name: &str) -> (Dir, PathBuf) {
    let dir = Dir::new(name);
    git(&dir.0, &["init", "-q", "--template="]);
    std::fs::create_dir_all(dir.0.join(".meowpaw")).unwrap();
    std::fs::write(
        dir.0.join(".meowpaw/profile.toml"),
        "[stages]\nformat = \"true\"\nlint = \"true\"\ncheck = \"true\"\ntest = \"true\"\nbuild = \"true\"\n\n\
         [commits]\nsubject_limit = 72\ntrailers = [\"Signed-off-by\"]\n\n\
         [commits.types]\nfeat = \"minor\"\nfix = \"patch\"\n\n\
         [git]\ntrunk = \"main\"\n\n\
         [unattended]\npermission_mode = \"dontAsk\"\ngates = [\"research\", \"implement\"]\nrelease = false\namend_approved = false\n",
    )
    .unwrap();
    std::fs::write(
        dir.0.join("README.md"),
        "# T\n\nText with a [link](other.md).\n",
    )
    .unwrap();
    git(&dir.0, &["add", "-A"]);
    git(
        &dir.0,
        &[
            "-c",
            "user.email=a@b",
            "-c",
            "user.name=n",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "-m",
            "chore: seed",
        ],
    );
    let state = dir.0.join(".state");
    std::fs::create_dir_all(&state).unwrap();
    (dir, state)
}

/// `paw <args>` in `dir`, given `input` on standard input.
fn meow(dir: &Path, state: &Path, args: &[&str], input: &str) -> Output {
    let mut child = Command::new(env!("CARGO_BIN_EXE_paw"))
        .args(args)
        .current_dir(dir)
        .env("XDG_STATE_HOME", state)
        .env("XDG_RUNTIME_DIR", state)
        .env("MEOWPAW_STATE_DIR", state)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}

fn lines(bytes: &[u8]) -> Vec<String> {
    String::from_utf8_lossy(bytes)
        .lines()
        .map(str::to_string)
        .collect()
}

/// The subcommands `paw <unit> --help` lists, one a line.
fn listed(dir: &Path, state: &Path, unit: &str, binary: &str) -> Vec<String> {
    let help = meow(dir, state, &[unit, "--help"], "");
    assert!(help.status.success(), "paw {unit} --help failed: {help:?}");
    let prefix = format!("{binary} ");
    lines(&help.stdout)
        .iter()
        .filter_map(|line| line.strip_prefix(&prefix))
        .filter_map(|line| line.split(':').next())
        .map(str::to_string)
        .collect()
}

/// The value of the help line that opens `key:`.
fn help_value(dir: &Path, state: &Path, unit: &str, name: &str, key: &str) -> Option<String> {
    let help = meow(dir, state, &[unit, name, "--help"], "");
    assert!(
        help.status.success(),
        "paw {unit} {name} --help failed: {help:?}"
    );
    lines(&help.stdout)
        .iter()
        .find_map(|line| line.strip_prefix(&format!("{key}: ")).map(str::to_string))
}

/// Whether `word` is one the help states: a literal as printed, or a
/// placeholder in angle brackets.
fn stated(word: &str, kinds: &[&str]) -> bool {
    let bare = word.trim_end_matches([',', ':']);
    kinds.iter().any(|kind| match *kind {
        "<id>" => {
            let (prefix, number) = bare.split_once('-').unwrap_or(("", ""));
            !prefix.is_empty()
                && prefix.chars().all(|c| c.is_ascii_uppercase())
                && !number.is_empty()
                && number.chars().all(|c| c.is_ascii_digit())
        }
        "<count>" => !bare.is_empty() && bare.chars().all(|c| c.is_ascii_digit()),
        "<path>" => bare.contains('/') || bare.contains('.') || word.ends_with(':'),
        "<hash>" => bare.len() >= 7 && bare.chars().all(|c| c.is_ascii_hexdigit()),
        "<unit>:" => word.ends_with(':') && word.starts_with("meow-"),
        // A line that is a JSON object is held to its keys in `held`.
        "<json>" => word.starts_with('{'),
        "<text>" => !word.is_empty(),
        placeholder if placeholder.starts_with('<') => {
            panic!("the help states a placeholder this test can't check: {placeholder}")
        }
        literal => literal == word,
    })
}

/// Runs `paw <unit> <args>` and holds every line of standard output to the
/// first words the subcommand's help states. Lines between `skip_from` and
/// `skip_to`, which a command the subcommand ran printed, are exempt.
fn held(dir: &Path, state: &Path, unit: &str, args: &[&str], input: &str) -> (Output, Vec<String>) {
    let name = args[0];
    let kinds = help_value(dir, state, unit, name, "lines")
        .unwrap_or_else(|| panic!("paw {unit} {name} --help states no `lines:` line"));
    let kinds: Vec<&str> = kinds.split_whitespace().collect();
    let json = help_value(dir, state, unit, name, "json").unwrap_or_default();
    let json: Vec<&str> = json.split_whitespace().collect();
    let mut all = vec![unit];
    all.extend_from_slice(args);
    let output = meow(dir, state, &all, input);
    let printed = lines(&output.stdout);
    let mut inside = false;
    for line in &printed {
        if line.starts_with("-- whole output of ") {
            inside = true;
            continue;
        }
        if line.starts_with("-- end of ") {
            inside = false;
            continue;
        }
        if inside {
            continue;
        }
        let Some(word) = line.split_whitespace().next() else {
            continue;
        };
        if kinds.contains(&"<json>") && word.starts_with('{') {
            match serde_json::from_str::<serde_json::Value>(line) {
                Ok(value) => {
                    for key in value.as_object().into_iter().flat_map(|o| o.keys()) {
                        if !json.contains(&key.as_str()) {
                            MISSING.with(|m| {
                                m.borrow_mut().push(format!(
                                    "paw {unit} {}: the key {key:?} in {line:?}",
                                    args.join(" ")
                                ))
                            });
                        }
                    }
                }
                Err(_) => MISSING.with(|m| {
                    m.borrow_mut().push(format!(
                        "paw {unit} {}: {line:?} isn't a JSON object",
                        args.join(" ")
                    ))
                }),
            }
            continue;
        }
        if !stated(word, &kinds) {
            MISSING.with(|m| {
                m.borrow_mut().push(format!(
                    "paw {unit} {}: {word:?} in {line:?}",
                    args.join(" ")
                ))
            });
        }
    }
    (output, printed)
}

/// REQ-1176: every subcommand's help says what a person reads in its place,
/// and none the parser accepts is missing from the list.
#[test]
fn every_subcommand_names_what_a_person_reads_in_its_place() {
    let (dir, state) = fixture("by-hand");
    for (unit, binary) in UNITS {
        let names = listed(&dir.0, &state, unit, binary);
        assert!(!names.is_empty(), "paw {unit} --help lists nothing");
        for name in &names {
            let by_hand = help_value(&dir.0, &state, unit, name, "by hand")
                .unwrap_or_else(|| panic!("paw {unit} {name} --help has no `by hand:` line"));
            assert!(
                by_hand.split_whitespace().count() >= 4,
                "paw {unit} {name}: the `by hand:` line names too little to follow: {by_hand:?}"
            );
            let kinds = help_value(&dir.0, &state, unit, name, "lines")
                .unwrap_or_else(|| panic!("paw {unit} {name} --help has no `lines:` line"));
            assert!(
                !kinds.trim().is_empty(),
                "paw {unit} {name}: the `lines:` line states no first word"
            );
        }
        // The parser's own list: the string literals its `match` names.
        let source = std::fs::read_to_string(
            Path::new(env!("CARGO_MANIFEST_DIR"))
                .join("src")
                .join(if unit == "loop" { "runloop" } else { unit })
                .with_extension("rs"),
        )
        .unwrap();
        let main = &source[source.find("pub fn main(args").unwrap()..];
        let main = &main[..main.find("\n}\n").unwrap()];
        let arms = main
            .lines()
            .filter(|line| line.contains("=>") || line.contains("Some(\"") || line.contains("=="))
            .flat_map(|line| line.split('"').skip(1).step_by(2).map(str::to_string))
            .filter(|word| {
                !word.is_empty()
                    && word.starts_with(|c: char| c.is_ascii_lowercase())
                    && word.chars().all(|c| c.is_ascii_lowercase() || c == '-')
                    && !word.starts_with("paw")
            })
            .collect::<std::collections::BTreeSet<_>>();
        for word in &arms {
            if matches!(word.as_str(), "usage" | "help") {
                continue;
            }
            assert!(
                names.contains(word),
                "paw {unit}: the parser names {word}, and `--help` doesn't list it ({names:?})"
            );
        }
        // The usage line is the parser's own list of what it accepts.
        let usage = meow(&dir.0, &state, &[unit, "no-such-subcommand"], "");
        let text = String::from_utf8_lossy(&usage.stderr).to_string();
        let mut accepted = Vec::new();
        for part in without_groups(&text).split('|') {
            let mut words = part
                .split_whitespace()
                .map(|w| w.trim_matches(|c| c == ',' || c == ';'))
                .filter(|w| *w != "usage:" && !w.starts_with("meow-"));
            if let Some(word) = words.next() {
                accepted.push(word.to_string());
            }
        }
        assert!(
            !accepted.is_empty(),
            "paw {unit}: its usage line names no subcommand ({binary}): {text:?}"
        );
        for word in accepted {
            if word.starts_with("--") {
                continue;
            }
            assert!(
                names.contains(&word),
                "paw {unit}: the usage line accepts {word}, and `--help` doesn't list it ({names:?})"
            );
        }
    }
}

/// REQ-1184: each line the read-only subcommands print opens with a first word
/// the subcommand's help states.
#[test]
fn output_opens_with_stated_first_words() {
    let (dir, state) = fixture("output");
    let (d, s) = (&dir.0, &state);
    held(d, s, "verbs", &["status"], "");
    held(d, s, "verbs", &["run", "lint"], "");
    held(d, s, "verbs", &["run", "format", "--", "README.md"], "");
    held(d, s, "verbs", &["evidence"], "");
    held(d, s, "verbs", &["evidence", "lint"], "");
    held(d, s, "verbs", &["state"], "");
    held(d, s, "verbs", &["tree", "HEAD"], "");
    held(d, s, "verbs", &["revision"], "{}");
    held(d, s, "verbs", &["local", "lint", "true"], "");
    held(d, s, "scm", &["convention"], "");
    held(d, s, "scm", &["check-message"], "");
    held(
        d,
        s,
        "scm",
        &["check-message"],
        "feat: add a thing\n\nSigned-off-by: A <a@b>\n",
    );
    held(d, s, "git", &["commit-guard"], "");
    held(d, s, "git", &["push-guard"], "");
    held(d, s, "licence", &["check"], "");
    held(d, s, "author", &["check", "plugins"], "");
    for unit in ["mise", "gotask"] {
        held(d, s, unit, &["status"], "");
        held(d, s, unit, &["bind"], "");
        held(d, s, unit, &["check"], "");
    }
    held(d, s, "markdown", &["status"], "");
    held(d, s, "markdown", &["bind"], "");
    held(d, s, "markdown", &["check"], "");
    held(d, s, "markdown", &["links", "README.md"], "");
    held(d, s, "unattended", &["plan"], "");
    held(d, s, "loop", &["purge"], "");
    held(d, s, "loop", &["start", "--step", "implement"], "");
    none_missing();
}

/// REQ-1184: the hooks answer in JSON, and each object holds to the keys the
/// help states.
#[test]
fn a_hook_answers_with_the_keys_its_help_states() {
    let (dir, state) = fixture("hooks");
    let (d, s) = (&dir.0, &state);
    let cwd = d.display().to_string();
    let event = |name: &str, extra: &str| {
        format!(
            "{{\"hook_event_name\":\"{name}\",\"session_id\":\"s1\",\"cwd\":{},{extra}}}",
            serde_json::to_string(&cwd).unwrap()
        )
    };
    let bash = |command: &str| {
        event(
            "PreToolUse",
            &format!(
                "\"tool_name\":\"Bash\",\"tool_input\":{{\"command\":{}}}",
                serde_json::to_string(command).unwrap()
            ),
        )
    };
    let (_, said) = held(
        d,
        s,
        "github",
        &["governance-guard"],
        &bash("gh api -X PUT repos/o/r/branches/main/protection"),
    );
    assert_eq!(said.len(), 1, "{said:?}");
    let (_, said) = held(
        d,
        s,
        "loop",
        &["prompt"],
        &event("UserPromptSubmit", "\"prompt\":\"/meow-loop:run go\""),
    );
    assert_eq!(said.len(), 1, "{said:?}");
    held(d, s, "loop", &["guard"], &bash("git push origin main"));
    held(
        d,
        s,
        "loop",
        &["stop"],
        &event("Stop", "\"stop_hook_active\":false"),
    );
    held(
        d,
        s,
        "prose",
        &["check"],
        &bash(&format!("git comm{}it -m \"feat: add a thing\"", "")),
    );
    none_missing();
}

/// REQ-1184: the unit's refusals when it is not in a repository it serves,
/// and a tracker the profile doesn't declare, open with stated words.
#[test]
fn the_tracker_commands_refuse_with_stated_first_words() {
    let (dir, state) = fixture("tracker");
    let (d, s) = (&dir.0, &state);
    held(d, s, "github", &["history"], "");
    held(d, s, "github", &["project", "EPC-0001"], "");
    held(d, s, "github", &["sync", "EPC-0001"], "");
    none_missing();
}

/// REQ-1184: an answer in JSON has the fields the help states.
#[test]
fn a_json_answer_has_the_fields_the_help_states() {
    let (dir, state) = fixture("json");
    let stated = help_value(&dir.0, &state, "verbs", "status", "json")
        .expect("meow verbs status --help states no `json:` line");
    let mut stated: Vec<&str> = stated.split_whitespace().collect();
    stated.sort_unstable();
    let output = meow(&dir.0, &state, &["verbs", "status", "--json"], "");
    let value: serde_json::Value = serde_json::from_slice(&output.stdout).unwrap();
    let mut keys: Vec<&str> = value
        .as_object()
        .unwrap()
        .keys()
        .map(String::as_str)
        .collect();
    keys.sort_unstable();
    assert_eq!(keys, stated);
}
