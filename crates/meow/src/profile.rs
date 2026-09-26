// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! What every unit shares: the repository's root and its profile.
//!
//! A profile is absent, unparseable or parsed, and the three are reported
//! differently, because falling back on a profile that didn't parse would
//! ignore what the repository tried to say (RES-0261).

#![allow(dead_code)]

use std::path::{Path, PathBuf};
use std::process::Command;

pub const PROFILE: &str = ".meowpaw/profile.toml";

pub enum Profile {
    Absent,
    Unparseable(String),
    Parsed(toml::Table),
}

/// The top of the working tree, or the current directory where there is none.
pub fn repository_root() -> PathBuf {
    let top = Command::new("git").args(["rev-parse", "--show-toplevel"]).output();
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

    mod tempdir {
        use std::path::{Path, PathBuf};

        pub struct Dir(PathBuf);

        impl Dir {
            pub fn new() -> Dir {
                // Tests run in parallel threads of one process, and two of them
                // can read the same clock, so a counter keeps each directory
                // its own.
                static NEXT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
                let n = NEXT.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                let stamp = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_nanos();
                let path = std::env::temp_dir().join(format!("meow-test-{}-{n}-{stamp}", std::process::id()));
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
