// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-git restack`, which rebuilds a stack of branches from the bottom
//! layer up and pushes nothing (TSK-4680, SPC-1060 "Restacking").

#![cfg(feature = "git")]

use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Dir {
    fn new(name: &str) -> Dir {
        let stamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "meow-restack-{name}-{}-{stamp}",
            std::process::id()
        ));
        std::fs::create_dir_all(&path).unwrap();
        Dir(path.canonicalize().unwrap())
    }
}

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn git(dir: &Path, args: &[&str]) -> String {
    let done = Command::new("git")
        .args(args)
        .current_dir(dir)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap();
    assert!(done.status.success(), "git {args:?} failed: {done:?}");
    String::from_utf8_lossy(&done.stdout).trim().to_string()
}

fn commit(dir: &Path, file: &str, text: &str, message: &str) {
    std::fs::write(dir.join(file), text).unwrap();
    git(dir, &["add", "-A"]);
    git(dir, &["commit", "-q", "-m", message]);
}

/// A repository with a remote, a trunk `main`, and the stack `a`, `b`, `c`
/// pushed to the remote, after which `main` moves on. Where `clash` is set,
/// the trunk's new commit changes the file `b` changes, so `b` conflicts.
fn fixture(name: &str, profile: &str, clash: bool) -> (Dir, PathBuf) {
    let dir = Dir::new(name);
    let remote = dir.0.join("remote.git");
    let work = dir.0.join("work");
    std::fs::create_dir_all(&work).unwrap();
    git(
        &dir.0,
        &["init", "-q", "--bare", "--template=", "remote.git"],
    );
    git(&work, &["init", "-q", "--template=", "-b", "main"]);
    git(&work, &["config", "user.name", "A Person"]);
    git(&work, &["config", "user.email", "a@example.org"]);
    git(&work, &["config", "commit.gpgsign", "false"]);
    std::fs::create_dir_all(work.join(".meowpaw")).unwrap();
    std::fs::write(work.join(".meowpaw/profile.toml"), profile).unwrap();
    commit(&work, "shared.txt", "one\n", "chore: seed");
    git(
        &work,
        &["remote", "add", "origin", remote.to_str().unwrap()],
    );
    for (branch, below) in [("a", "main"), ("b", "a"), ("c", "b")] {
        git(&work, &["switch", "-q", "-c", branch, below]);
        commit(
            &work,
            &format!("{branch}.txt"),
            branch,
            &format!("feat: {branch}"),
        );
    }
    git(&work, &["switch", "-q", "b"]);
    if clash {
        commit(&work, "shared.txt", "from b\n", "feat: b changes shared");
        git(&work, &["switch", "-q", "c"]);
        git(&work, &["rebase", "-q", "b"]);
    }
    git(&work, &["push", "-q", "origin", "main", "a", "b", "c"]);
    git(&work, &["switch", "-q", "main"]);
    let moved = if clash { "from main\n" } else { "two\n" };
    commit(&work, "shared.txt", moved, "fix: the trunk moves on");
    (dir, work)
}

const PROFILE: &str = "[git]\ntrunk = \"main\"\n";

fn restack(work: &Path, branches: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_paw"))
        .arg("git")
        .arg("restack")
        .args(branches)
        .current_dir(work)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .stdin(Stdio::null())
        .output()
        .unwrap()
}

fn rev(work: &Path, name: &str) -> String {
    git(work, &["rev-parse", name])
}

fn remote_refs(dir: &Path) -> String {
    git(&dir.join("remote.git"), &["for-each-ref"])
}

fn said(output: &Output) -> String {
    format!(
        "{}{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    )
}

#[test]
fn each_layer_is_rebased_onto_the_one_below_and_nothing_is_pushed() {
    // TSK-4680 criterion 1, REQ-1828: each layer lands on the one below, and
    // the lease names the remote-tracking revision read before the rewrite.
    let (dir, work) = fixture("chain", PROFILE, false);
    let seen: Vec<String> = ["a", "b", "c"]
        .iter()
        .map(|b| rev(&work, &format!("origin/{b}")))
        .collect();
    let before = remote_refs(&dir.0);
    let output = restack(&work, &["a", "b", "c"]);
    let text = said(&output);
    assert_eq!(output.status.code(), Some(0), "{text}");
    for (below, branch) in [("main", "a"), ("a", "b"), ("b", "c")] {
        assert_eq!(
            git(&work, &["rev-parse", &format!("{branch}~1")]),
            rev(&work, below),
            "{branch} isn't on {below}: {text}"
        );
    }
    for (branch, revision) in ["a", "b", "c"].iter().zip(&seen) {
        assert!(
            text.contains(&format!("updated: {branch}\n")),
            "no updated line for {branch}: {text}"
        );
        assert!(
            text.contains(&format!(
                "git push --force-with-lease={branch}:{revision} origin {branch}"
            )),
            "no lease push for {branch}: {text}"
        );
    }
    assert!(!text.contains("not updated:"), "{text}");
    assert_eq!(remote_refs(&dir.0), before, "a remote ref changed");
    assert_eq!(git(&work, &["branch", "--show-current"]), "main");
}

#[test]
fn a_conflict_stops_the_restack_and_names_the_branch() {
    // TSK-4680 criterion 2, REQ-1824, REQ-1826: the rebase is aborted, so
    // neither side is discarded, and the report names what was and wasn't
    // reached.
    let (_dir, work) = fixture("conflict", PROFILE, true);
    let b_before = rev(&work, "b");
    let c_before = rev(&work, "c");
    let output = restack(&work, &["a", "b", "c"]);
    let text = said(&output);
    assert_eq!(output.status.code(), Some(1), "{text}");
    assert!(text.contains("conflict: b in shared.txt"), "{text}");
    assert!(text.contains("updated: a\n"), "{text}");
    assert!(text.contains("not updated: b\n"), "{text}");
    assert!(text.contains("not updated: c\n"), "{text}");
    assert_eq!(rev(&work, "b"), b_before, "b was rewritten");
    assert_eq!(rev(&work, "c"), c_before, "c was rewritten");
    assert_eq!(git(&work, &["branch", "--show-current"]), "main");
    assert_eq!(git(&work, &["status", "--porcelain"]), "", "{text}");
    assert!(
        !work.join(".git/rebase-merge").exists() && !work.join(".git/rebase-apply").exists(),
        "a rebase was left in progress"
    );
}

#[test]
fn a_rewritten_commit_is_signed_where_the_profile_asks() {
    // TSK-4680 criterion 3, REQ-2614: a rebase after signing signs again.
    if Command::new("ssh-keygen")
        .arg("-?")
        .stderr(Stdio::null())
        .stdout(Stdio::null())
        .status()
        .is_err()
    {
        eprintln!("skipped: the signature case needs ssh-keygen");
        return;
    }
    let profile = "[git]\ntrunk = \"main\"\nrequire_signatures = true\n";
    let (dir, work) = fixture("signed", profile, false);
    let key = dir.0.join("key");
    let made = Command::new("ssh-keygen")
        .args(["-q", "-t", "ed25519", "-N", "", "-f"])
        .arg(&key)
        .status()
        .unwrap();
    assert!(made.success());
    let public = std::fs::read_to_string(key.with_extension("pub")).unwrap();
    let allowed = dir.0.join("allowed");
    std::fs::write(&allowed, format!("a@example.org {public}")).unwrap();
    git(&work, &["config", "gpg.format", "ssh"]);
    git(&work, &["config", "user.signingkey", key.to_str().unwrap()]);
    git(
        &work,
        &[
            "config",
            "gpg.ssh.allowedSignersFile",
            allowed.to_str().unwrap(),
        ],
    );
    let output = restack(&work, &["a", "b", "c"]);
    let text = said(&output);
    assert_eq!(output.status.code(), Some(0), "{text}");
    let verdicts = git(&work, &["log", "--format=%G?", "main..c"]);
    assert_eq!(verdicts, "G\nG\nG", "{text}");
}

#[test]
fn a_branch_with_uncommitted_changes_stops_it_before_any_rewrite() {
    // TSK-4680 criterion 4, REQ-2534: nothing is rewritten, and the branch is
    // named.
    let (_dir, work) = fixture("dirty", PROFILE, false);
    git(&work, &["switch", "-q", "b"]);
    std::fs::write(work.join("b.txt"), "not committed").unwrap();
    let before: Vec<String> = ["a", "b", "c"].iter().map(|b| rev(&work, b)).collect();
    let output = restack(&work, &["a", "b", "c"]);
    let text = said(&output);
    assert_eq!(output.status.code(), Some(1), "{text}");
    assert!(text.contains("b has uncommitted changes"), "{text}");
    let after: Vec<String> = ["a", "b", "c"].iter().map(|b| rev(&work, b)).collect();
    assert_eq!(before, after, "a branch was rewritten: {text}");
    assert!(text.contains("not updated: a\n"), "{text}");
}

#[test]
fn a_branch_checked_out_in_another_working_tree_stops_it() {
    // REQ-2534: a branch in another working tree is that tree's to change.
    let (dir, work) = fixture("elsewhere", PROFILE, false);
    let other = dir.0.join("other");
    git(
        &work,
        &["worktree", "add", "-q", other.to_str().unwrap(), "c"],
    );
    let before = rev(&work, "a");
    let output = restack(&work, &["a", "b", "c"]);
    let text = said(&output);
    assert_eq!(output.status.code(), Some(1), "{text}");
    assert!(text.contains("c is checked out in"), "{text}");
    assert_eq!(rev(&work, "a"), before, "a was rewritten: {text}");
}

#[test]
fn a_layer_whose_base_has_not_moved_is_left_as_it_is() {
    // SPC-1060 "Restacking": only a moved base is rebased.
    let (_dir, work) = fixture("still", PROFILE, false);
    git(&work, &["switch", "-q", "a"]);
    git(&work, &["rebase", "-q", "main"]);
    git(&work, &["switch", "-q", "main"]);
    let a = rev(&work, "a");
    let output = restack(&work, &["a", "b", "c"]);
    let text = said(&output);
    assert_eq!(output.status.code(), Some(0), "{text}");
    assert_eq!(rev(&work, "a"), a, "{text}");
    assert!(text.contains("unchanged: a"), "{text}");
    assert!(text.contains("updated: b\n"), "{text}");
}
