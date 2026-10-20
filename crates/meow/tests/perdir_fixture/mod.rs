// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! A fixture repository for the Godot, Starlark and Scheme packs' tests: a scratch git work tree
//! holding the files a test commits, and `paw <pack> <command>` run in it.

#![allow(dead_code)]

use std::path::{Path, PathBuf};
use std::process::{Command, Output};

/// A git work tree of its own, removed when the test ends.
pub struct Repo(pub PathBuf);

impl Repo {
    /// A repository named for `name`, holding each `(path, text)` in `files`,
    /// every one added to the index.
    pub fn new(name: &str, files: &[(&str, &str)]) -> Repo {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path =
            std::env::temp_dir().join(format!("meow-pack-{name}-{}-{stamp}", std::process::id()));
        std::fs::create_dir_all(&path).unwrap();
        let path = std::fs::canonicalize(&path).unwrap();
        let repo = Repo(path);
        repo.git(&["init", "-q", "--template="]);
        for (file, text) in files {
            repo.write(file, text);
        }
        repo.git(&["add", "-A"]);
        repo
    }

    pub fn write(&self, file: &str, text: &str) {
        let path = self.0.join(file);
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(path, text).unwrap();
    }

    pub fn git(&self, args: &[&str]) {
        let done = Command::new("git")
            .args(args)
            .current_dir(&self.0)
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .output()
            .unwrap();
        assert!(done.status.success(), "git {args:?} failed: {done:?}");
    }

    /// Every path under the work tree outside `.git`, so a test can say a
    /// command left nothing behind.
    pub fn files(&self) -> Vec<PathBuf> {
        fn walk(dir: &Path, root: &Path, out: &mut Vec<PathBuf>) {
            for entry in std::fs::read_dir(dir).unwrap().flatten() {
                let path = entry.path();
                if path.file_name().is_some_and(|n| n == ".git") {
                    continue;
                }
                out.push(path.strip_prefix(root).unwrap().to_path_buf());
                if path.is_dir() {
                    walk(&path, root, out);
                }
            }
        }
        let mut out = Vec::new();
        walk(&self.0, &self.0, &mut out);
        out.sort();
        out
    }

    /// `paw <args>` run at the root, with `env` added to its environment.
    pub fn run(&self, args: &[&str], env: &[(&str, &str)]) -> Run {
        let mut command = Command::new(env!("CARGO_BIN_EXE_paw"));
        command
            .args(args)
            .current_dir(&self.0)
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_CONFIG_NOSYSTEM", "1");
        for (key, value) in env {
            command.env(key, value);
        }
        Run(command.output().unwrap())
    }
}

impl Drop for Repo {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

/// What a command printed and how it exited.
pub struct Run(pub Output);

impl Run {
    pub fn code(&self) -> i32 {
        self.0.status.code().unwrap_or(-1)
    }

    pub fn out(&self) -> String {
        String::from_utf8_lossy(&self.0.stdout).into_owned()
    }

    pub fn lines(&self) -> Vec<String> {
        self.out().lines().map(str::to_string).collect()
    }

    /// The line `bind` printed for `stage`, bound or commented.
    pub fn stage(&self, stage: &str) -> Vec<String> {
        self.lines()
            .into_iter()
            .filter(|line| {
                line.starts_with(&format!("{stage} = "))
                    || line.starts_with(&format!("# {stage}: "))
            })
            .collect()
    }

    /// The command `bind` bound `stage` to, unquoted.
    pub fn bound(&self, stage: &str) -> Option<String> {
        let prefix = format!("{stage} = ");
        self.lines().into_iter().find_map(|line| {
            line.strip_prefix(&prefix).map(|value| {
                toml::from_str::<toml::Table>(&format!("v = {value}")).unwrap()["v"]
                    .as_str()
                    .unwrap()
                    .to_string()
            })
        })
    }

    /// Asserts each of the five stages is printed, bound or commented with a
    /// reason, which is what a pack's `bind` owes every stage.
    pub fn every_stage_printed(&self) {
        for stage in ["format", "lint", "check", "test", "build"] {
            let lines = self.stage(stage);
            assert!(
                !lines.is_empty(),
                "bind printed nothing for {stage}:\n{}",
                self.out()
            );
            for line in lines {
                if let Some(rest) = line.strip_prefix(&format!("# {stage}: ")) {
                    assert!(
                        rest.starts_with("unresolved") || rest.starts_with("unbound"),
                        "the {stage} comment names no state: {line}"
                    );
                    assert!(
                        rest.contains(", "),
                        "the {stage} comment gives no reason: {line}"
                    );
                }
            }
        }
    }
}

pub const PROFILE: (&str, &str) = (".meowpaw/profile.toml", "[stages]\n");
