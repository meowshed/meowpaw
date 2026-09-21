#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The documentation index and the tree agree, in both directions.

A file present and unlisted is as much a defect as a listing with no file: the
first is undiscoverable, the second is a promise the repository does not keep.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "docs", "README.md")
EXTRA = os.path.join(ROOT, "project", "README.md")
SKIP = {"_archive", ".claude", ".git", "node_modules", "target", ".github", "tools", "templates", "plugins"}
# One file per requirement, listed by its area overview rather than by the
# documentation index: 264 rows would drown the index it is meant to serve.
GENERATED = ("project/",)
# The index lists these; they are not documentation and are not walked for.
EXEMPT = {"docs/README.md", "project/README.md", "CLAUDE.md", "README.md"}


def listed() -> set[str]:
    # A repository with no documentation yet is in a legal state, and an index
    # that does not exist lists nothing rather than failing the gate.
    if not os.path.isfile(INDEX):
        return set()
    with open(INDEX, encoding="utf-8") as handle:
        text = handle.read()
    out = set()
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if link.startswith(("http", "#", "mailto")):
            continue
        target = os.path.normpath(os.path.join(ROOT, "docs", link.split("#")[0]))
        out.add(os.path.relpath(target, ROOT))
    return out


def present() -> set[str]:
    out = set()
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.relpath(os.path.join(root, name), ROOT)
            if path in EXEMPT or path.startswith(GENERATED):
                continue
            out.add(path)
    return out


def main() -> int:
    have, want = present(), listed()
    failures = [f"not in the index: {p}" for p in sorted(have - want)]
    # An entry may point at something that is not a walked document — the gate
    # configuration, the workflow — so only a missing *file* is a failure.
    for path in sorted(want - have):
        if not os.path.exists(os.path.join(ROOT, path)):
            failures.append(f"in the index, no file: {path}")

    for failure in failures:
        print(failure)
    print(f"{len(have)} documents, {len(failures)} index failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
