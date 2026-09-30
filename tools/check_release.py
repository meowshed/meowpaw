#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Refuse to release a breaking change the version doesn't show (REQ-3192).

For each unit whose manifest version has no release tag yet, reads the commits
since the unit's last release tag that belong to it: those touching its
directory under `plugins/`, and, for a unit that ships the native binary,
those touching `crates/meow/` (ADR-1570). Where one is marked breaking, with
`!` before the subject's colon or a `BREAKING CHANGE:` footer, the version has
to raise its major number, or its minor while the major is zero. Exits 1
naming each unit that doesn't, and 0 otherwise.

    python3 tools/check_release.py [repository]
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

SUBJECT = re.compile(r"^[a-z][a-z0-9-]*(\([^()]*\))?!: ")
FOOTER = re.compile(r"^BREAKING[ -]CHANGE: ", re.M)
SEPARATOR = "\x1e"


def git(root, *args):
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                          env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    return done.stdout if done.returncode == 0 else None


def version(text):
    return tuple(int(p) for p in text.split(".")[:3])


def last_release(root, name):
    """The highest released version of a unit, from its tags, or None."""
    tags = (git(root, "tag", "--list", f"{name}-v*") or "").split()
    # The version follows the unit's name and `-v`; a name such as
    # `meow-checks` holds `-v` itself, so the name is cut off, not split on.
    versions = [version(t[len(name) + 2:]) for t in tags if re.fullmatch(rf"{re.escape(name)}-v\d+\.\d+\.\d+", t)]
    return max(versions) if versions else None


def ships_binary(root, name):
    return bool((git(root, "ls-files", "-z", "--", f"plugins/{name}/bin") or "").strip("\0"))


def breaking_commits(root, name, since):
    """Each commit since the tag that belongs to the unit and is marked breaking."""
    paths = [f"plugins/{name}"] + (["crates/meow"] if ships_binary(root, name) else [])
    tag = f"{name}-v{'.'.join(map(str, since))}"
    log = git(root, "log", "--format=%h %B" + SEPARATOR, f"{tag}..HEAD", "--", *paths) or ""
    found = []
    for entry in (e.strip() for e in log.split(SEPARATOR)):
        if not entry:
            continue
        sha, _, message = entry.partition(" ")
        subject = message.splitlines()[0] if message else ""
        if SUBJECT.match(subject) or FOOTER.search(message):
            found.append(f"{sha} {subject}")
    return found


def shows_breaking(old, new):
    """Whether a version raise shows a breaking change: the major, or the minor at zero."""
    if old[0] == 0:
        return new[0] > 0 or new[1] > old[1]
    return new[0] > old[0]


def check(root):
    root = Path(root)
    problems = []
    for manifest in sorted(root.glob("plugins/*/.claude-plugin/plugin.json")):
        name = manifest.parent.parent.name
        new = version(json.loads(manifest.read_text(encoding="utf-8"))["version"])
        old = last_release(root, name)
        if old is None or new == old:
            continue
        commits = breaking_commits(root, name, old)
        if commits and not shows_breaking(old, new):
            need = "a minor or major" if old[0] == 0 else "a major"
            problems.append(f"{name}: {'.'.join(map(str, old))} to {'.'.join(map(str, new))} carries a breaking "
                            f"change, which needs {need} version: {'; '.join(commits)}")
    return problems


def main():
    problems = check(sys.argv[1] if len(sys.argv) > 1 else ".")
    for problem in problems:
        print(problem)
    print(f"{len(problems)} unit{'s' if len(problems) != 1 else ''} releasing a breaking change the version doesn't show")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
