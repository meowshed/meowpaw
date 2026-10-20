// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Fixture repositories and stand-in tools for the language packs' tests
//! (TSK-5080, TSK-5085): a git repository written in a temporary directory,
//! and a directory of executables a test puts first on `PATH`.

#![allow(dead_code)]

use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

/// A scratch directory of its own, removed when the test ends.
pub struct Dir(pub PathBuf);

impl Dir {
    pub fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path =
            std::env::temp_dir().join(format!("meow-pack-{name}-{}-{stamp}", std::process::id()));
        std::fs::create_dir_all(&path).unwrap();
        Dir(std::fs::canonicalize(&path).unwrap())
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

/// A git repository holding `files`, each tracked, and a directory of
/// stand-in tools, each a shell script that records its own start by
/// touching `ran` in the directory the tests give as `HOME`.
pub fn fixture(name: &str, files: &[(&str, &str)], tools: &[&str]) -> (Dir, Dir) {
    let dir = Dir::new(name);
    let bin = Dir::new(&format!("{name}-bin"));
    for (file, text) in files {
        let path = dir.0.join(file);
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(&path, text).unwrap();
    }
    for tool in tools {
        let path = bin.0.join(tool);
        std::fs::write(&path, "#!/bin/sh\ntouch \"$HOME/ran\"\n").unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o755)).unwrap();
        }
    }
    for args in [&["init", "-q", "--template="][..], &["add", "-A"]] {
        let done = Command::new("git")
            .args(args)
            .current_dir(&dir.0)
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .output()
            .unwrap();
        assert!(done.status.success(), "git {args:?} failed: {done:?}");
    }
    (dir, bin)
}

/// `paw <args>` in `dir`, with the stand-in tools first on `PATH`: the
/// process, its standard output as lines and its standard error.
pub fn paw(dir: &Path, bin: &Path, args: &[&str]) -> (Output, Vec<String>, String) {
    let path = format!("{}:/usr/bin:/bin", bin.display());
    let done = Command::new(env!("CARGO_BIN_EXE_paw"))
        .args(args)
        .current_dir(dir)
        .env("PATH", path)
        .env("HOME", bin)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .stdin(Stdio::null())
        .output()
        .unwrap();
    let lines = String::from_utf8_lossy(&done.stdout)
        .lines()
        .map(str::to_string)
        .collect();
    let stderr = String::from_utf8_lossy(&done.stderr).into_owned();
    (done, lines, stderr)
}

/// Whether a stand-in tool started.
pub fn started(bin: &Path) -> bool {
    bin.join("ran").exists()
}

/// The profile a fixture commits, declaring the given stages.
pub fn profile(stages: &[(&str, &str)]) -> String {
    let mut text = String::from("[stages]\n");
    for (stage, command) in stages {
        text.push_str(&format!("{stage} = \"{command}\"\n"));
    }
    text
}
