# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Refuse a commit on the trunk, and check every commit a push would publish.

SPC-1060 states the behaviour. The hooks pass the tool call as JSON on standard
input; a guard blocks by exiting 2 with its reason on standard error, and lets
the command through by exiting 0. `commit-guard` blocks a commit on the
declared trunk (REQ-1292). `push-guard` checks each commit a push would publish
through `meow-scm check-message` where that unit is installed, and reports the
check as unrun where it isn't (REQ-0079), and passes only a good signature from
a trusted key where the repository requires one (REQ-1326, REQ-2530).
"""

import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

PROFILE = Path(".meowpaw") / "profile.toml"
KEYS = ("trunk", "require_signatures")
BLOCK, ALLOW = 2, 0
PACK = Path(__file__).resolve().parent.parent

VERDICTS = {
    "U": "signed by a key this repository doesn't trust",
    "B": "carries a bad signature",
    "X": "carries a signature that has expired",
    "Y": "was signed by a key that has expired",
    "R": "was signed by a key that has been revoked",
}


def git(root, *args):
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                          env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_PAGER": "cat"})
    return done.returncode, done.stdout


def working_directory():
    """The session's directory, from the hook's input where it names one."""
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        event = {}
    return Path(event.get("cwd") or os.getcwd())


def policy(root):
    """The declared trunk and signing policy, and what the profile left undeclared."""
    path = root / PROFILE
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        data = {}
    table = data.get("git") if isinstance(data.get("git"), dict) else {}
    trunk = table.get("trunk") if isinstance(table.get("trunk"), str) else None
    signatures = table.get("require_signatures") is True
    ignored = [f"git.{key}" for key in table if key not in KEYS]
    return trunk, signatures, bool(table), ignored


def find_meow_scm():
    """meow-scm's launcher, where it is installed, and never installed by this pack."""
    named = os.environ.get("MEOW_SCM")
    if named is not None:
        return Path(named) if Path(named).is_file() else None
    beside = PACK.parent / "meow-scm" / "bin" / "meow-scm"
    if beside.is_file():
        return beside
    cache = Path.home() / ".claude" / "plugins" / "cache"
    found = sorted(cache.glob("*/meow-scm/*/bin/meow-scm"),
                   key=lambda p: [int(n) if n.isdigit() else n for n in re.split(r"(\d+)", p.parts[-3])])
    return found[-1] if found else None


def commit_guard(root):
    trunk, _, declared, _ = policy(root)
    if not trunk:
        print("meow-git commit-guard: no trunk declared under [git]; nothing refused")
        return ALLOW
    code, branch = git(root, "symbolic-ref", "--short", "-q", "HEAD")
    if code == 0 and branch.strip() == trunk:
        print(f"meow-git: refused a commit on `{trunk}`, the trunk this repository declares. "
              f"Take a branch and commit there.", file=sys.stderr)
        return BLOCK
    print(f"meow-git commit-guard: `{branch.strip() or 'a detached head'}` isn't the trunk `{trunk}`")
    return ALLOW


def signature(root, commit):
    """None where the commit's signature is good, otherwise what is wrong with it."""
    _, verdict = git(root, "log", "-1", "--format=%G?", commit)
    verdict = verdict.strip()
    if verdict == "G":
        return None
    _, raw = git(root, "cat-file", "commit", commit)
    signed = "\ngpgsig " in raw or raw.startswith("gpgsig ")
    if verdict in ("E", "N") and signed:
        return "is signed, but the signature is unverifiable here: the key material or the list of allowed signers is missing"
    if verdict == "N":
        return "is unsigned"
    return VERDICTS.get(verdict, f"has the signature verdict {verdict!r}")


def push_guard(root):
    trunk, signatures, declared, ignored = policy(root)
    code, listed = git(root, "rev-list", "--reverse", "HEAD", "--not", "--remotes")
    commits = listed.split() if code == 0 else []
    notes = []
    if not declared:
        notes.append("no [git] table: the trunk and the signing policy are undeclared")
    if ignored:
        notes.append(f"not read by meow-git: {', '.join(ignored)}")
    if not commits:
        print("meow-git push-guard: no commit to publish was found; checked nothing")
        return ALLOW

    scm = find_meow_scm()
    if scm is None:
        notes.append("meow-scm isn't installed: the message check is unrun for every commit")
    failures = []
    for commit in commits:
        _, subject = git(root, "log", "-1", "--format=%h %s", commit)
        subject = subject.strip()
        if scm is not None:
            _, message = git(root, "log", "-1", "--format=%B", commit)
            checked = subprocess.run([str(scm), "check-message"], cwd=root, input=message,
                                     capture_output=True, text=True)
            if checked.returncode == 1:
                lines = [line for line in checked.stdout.splitlines() if line.startswith("line ")]
                failures.append(f"{subject}\n" + "\n".join(f"    {line}" for line in lines))
            elif checked.returncode == 3 and not any("convention" in n for n in notes):
                notes.append("meow-scm: " + checked.stdout.strip().splitlines()[-1])
        if signatures:
            problem = signature(root, commit)
            if problem:
                failures.append(f"{subject}\n    signature: the commit {problem}")

    for note in notes:
        print(f"meow-git push-guard: {note}")
    if failures:
        print(f"meow-git: refused the push; {len(failures)} problem{'s' if len(failures) > 1 else ''} "
              f"in the {len(commits)} commit{'s' if len(commits) > 1 else ''} it would publish:\n\n"
              + "\n".join(failures), file=sys.stderr)
        return BLOCK
    print(f"meow-git push-guard: {len(commits)} commit{'s' if len(commits) > 1 else ''} checked")
    return ALLOW


def main(argv):
    if argv not in (["commit-guard"], ["push-guard"]):
        print("usage: meow-git commit-guard | meow-git push-guard", file=sys.stderr)
        return 1
    start = working_directory()
    code, top = git(start, "rev-parse", "--show-toplevel")
    if code != 0:
        print(f"meow-git {argv[0]}: not inside a repository; checked nothing")
        return ALLOW
    root = Path(top.strip())
    return commit_guard(root) if argv == ["commit-guard"] else push_guard(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
