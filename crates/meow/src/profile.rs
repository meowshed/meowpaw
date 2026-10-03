// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! What every unit shares: the repository's root and its profile.
//!
//! A profile is absent, unparseable or parsed, and the three are reported
//! differently, because falling back on a profile that didn't parse would
//! ignore what the repository tried to say (RES-0261).

#![allow(dead_code)]

use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

pub const PROFILE: &str = ".meowpaw/profile.toml";

pub enum Profile {
    Absent,
    Unparseable(String),
    Parsed(toml::Table),
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
        Ok(table) => Profile::Parsed(table),
        Err(error) => Profile::Unparseable(error.message().to_string()),
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
            Profile::Parsed(table) => assert!(table.contains_key("verbs")),
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
