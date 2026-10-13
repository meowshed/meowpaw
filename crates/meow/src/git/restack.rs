// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Rebuild a stack of branches, given from the bottom layer up, and push
//! nothing (SPC-1060 "Restacking").
//!
//! Each branch is rebased onto the one below it, the first onto the declared
//! trunk, and a branch whose base hasn't moved is left as it is. A conflict
//! aborts that rebase, so neither side is discarded, and stops the restack
//! (REQ-1826). Wherever it stops, each branch is reported as updated or not
//! updated (REQ-1824). Each updated branch is printed with the lease push
//! that publishes it, naming the remote-tracking revision read before the
//! rewrite (REQ-1828). A branch with uncommitted changes, or checked out in
//! another working tree, stops it before anything is rewritten (REQ-2534).

use std::path::{Path, PathBuf};

const DONE: u8 = 0;
const STOPPED: u8 = 1;

/// Runs git through the one helper, as its success, standard output and
/// standard error.
fn run(root: &Path, args: &[&str]) -> (bool, String, String) {
    match crate::profile::reading_git()
        .args(args)
        .current_dir(root)
        .output()
    {
        Ok(out) => (
            out.status.success(),
            String::from_utf8_lossy(&out.stdout).trim().to_string(),
            String::from_utf8_lossy(&out.stderr).trim().to_string(),
        ),
        Err(error) => (false, String::new(), error.to_string()),
    }
}

/// The commit a name points at, where it names one.
fn revision(root: &Path, name: &str) -> Option<String> {
    let (ok, out, _) = run(
        root,
        &["rev-parse", "-q", "--verify", &format!("{name}^{{commit}}")],
    );
    (ok && !out.is_empty()).then_some(out)
}

/// Each working tree's path and the branch checked out in it.
fn checked_out(root: &Path) -> Vec<(PathBuf, String)> {
    let (_, out, _) = run(root, &["worktree", "list", "--porcelain", "-z"]);
    let mut found = Vec::new();
    let mut path: Option<PathBuf> = None;
    for field in out.split('\0') {
        if let Some(at) = field.strip_prefix("worktree ") {
            path = Some(PathBuf::from(at));
        } else if let Some(branch) = field.strip_prefix("branch refs/heads/")
            && let Some(at) = &path
        {
            found.push((at.clone(), branch.to_string()));
        }
    }
    found
}

fn same(a: &Path, b: &Path) -> bool {
    match (a.canonicalize(), b.canonicalize()) {
        (Ok(a), Ok(b)) => a == b,
        _ => a == b,
    }
}

fn dirty(at: &Path) -> bool {
    let (ok, out, _) = run(at, &["status", "--porcelain", "-z", "--untracked-files=no"]);
    !ok || !out.is_empty()
}

/// Why the restack can't start, or None where nothing stops it.
fn obstacle(root: &Path, trunk: &str, branches: &[String]) -> Option<String> {
    if revision(root, &format!("refs/heads/{trunk}")).is_none() {
        return Some(format!("the trunk {trunk} isn't a branch here"));
    }
    if let Some(missing) = branches
        .iter()
        .find(|b| revision(root, &format!("refs/heads/{b}")).is_none())
    {
        return Some(format!("{missing} isn't a branch here"));
    }
    let trees = checked_out(root);
    for branch in branches {
        for (at, held) in &trees {
            if held != branch {
                continue;
            }
            if !same(at, root) {
                return Some(format!("{branch} is checked out in {}", at.display()));
            }
            if dirty(at) {
                return Some(format!("{branch} has uncommitted changes"));
            }
        }
    }
    if dirty(root) {
        return Some(format!(
            "the working tree at {} has uncommitted changes",
            root.display()
        ));
    }
    None
}

/// The files a stopped rebase left in conflict.
fn conflicted(root: &Path) -> Vec<String> {
    let (_, out, _) = run(root, &["diff", "--name-only", "--diff-filter=U", "-z"]);
    out.split('\0')
        .filter(|f| !f.is_empty())
        .map(str::to_string)
        .collect()
}

/// Rebuilds the stack `branches`, bottom first, onto `trunk`.
pub(super) fn restack(root: &Path, trunk: Option<&str>, sign: bool, branches: &[String]) -> u8 {
    let not_updated = |from: usize| {
        for branch in &branches[from..] {
            println!("not updated: {branch}");
        }
    };
    let Some(trunk) = trunk else {
        println!("meow-git restack: no trunk declared under [git]; rewrote nothing");
        not_updated(0);
        return STOPPED;
    };
    if let Some(reason) = obstacle(root, trunk, branches) {
        println!("meow-git restack: {reason}; rewrote nothing");
        not_updated(0);
        return STOPPED;
    }
    let start = match run(root, &["symbolic-ref", "--short", "-q", "HEAD"]) {
        (true, branch, _) if !branch.is_empty() => branch,
        _ => revision(root, "HEAD").unwrap_or_default(),
    };
    let restore = || {
        if !start.is_empty() {
            let _ = run(root, &["checkout", "-q", &start]);
        }
    };

    let mut below_new = revision(root, &format!("refs/heads/{trunk}")).unwrap_or_default();
    let mut below_old: Option<String> = None;
    let mut below_moved = false;
    for (i, branch) in branches.iter().enumerate() {
        let local = format!("refs/heads/{branch}");
        let old = revision(root, &local).unwrap_or_default();
        let base = run(root, &["merge-base", &below_new, &old]).1;
        if !below_moved && base == below_new {
            println!("unchanged: {branch}, its base hasn't moved");
            below_old = Some(old.clone());
            below_new = old;
            below_moved = false;
            continue;
        }
        let seen = revision(root, &format!("refs/remotes/origin/{branch}")).unwrap_or_default();
        let mut args = vec!["rebase", "-q"];
        if sign {
            args.push("--gpg-sign");
        }
        let upstream = below_old.clone().unwrap_or_else(|| below_new.clone());
        args.extend(["--onto", &below_new, &upstream, branch]);
        let (ok, _, error) = run(root, &args);
        if !ok {
            let files = conflicted(root);
            let _ = run(root, &["rebase", "--abort"]);
            restore();
            if files.is_empty() {
                println!("meow-git restack: the rebase of {branch} failed: {error}");
            } else {
                println!("conflict: {branch} in {}", files.join(", "));
            }
            not_updated(i);
            return STOPPED;
        }
        println!("updated: {branch}");
        println!("git push --force-with-lease={branch}:{seen} origin {branch}");
        below_old = Some(old);
        below_new = revision(root, &local).unwrap_or_default();
        below_moved = true;
    }
    restore();
    DONE
}
