#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Requirement identifiers resolve, and none is allocated twice.

One file per requirement, named for its identifier and a slug. Checks that the
name and the front matter agree, that no identifier is allocated twice, and
that every identifier cited anywhere in the corpus resolves to a file.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQS = os.path.join(ROOT, "project", "requirements")
CITED = re.compile(r"REQ-\d{4}")
NAMED = re.compile(r"^(REQ-\d{4})-[a-z0-9-]+\.md$")
SKIP = {"_archive", ".claude", ".git", "node_modules", "target", "templates"}


def defined() -> dict[str, str]:
    """Identifier to file name, for every requirement on disk."""
    out: dict[str, str] = {}
    # The directory appears with its first requirement. Absent is empty, not an
    # error: a repository that has written none is in a legal state.
    if not os.path.isdir(REQS):
        return out
    for name in sorted(os.listdir(REQS)):
        if not name.endswith(".md") or name == "README.md":
            continue
        match = NAMED.match(name)
        if not match:
            out.setdefault("__malformed__", "")
            print(f"malformed name: {name}")
            continue
        ident = match.group(1)
        with open(os.path.join(REQS, name), encoding="utf-8") as handle:
            declared = re.search(r"^id: (\S+)", handle.read(), re.M)
        got = declared.group(1) if declared else "(none)"
        if got != ident:
            print(f"{name} declares id {got}")
        if ident in out:
            # An identifier allocated twice is the defect this check exists for,
            # so it fails the run rather than printing and passing.
            out.setdefault("__duplicate__", "")
            print(f"{ident} allocated twice: {out[ident]} and {name}")
        out[ident] = name
    return out


def main() -> int:
    known = defined()
    failures = [k for k in ("__malformed__", "__duplicate__") if k in known]
    known.pop("__malformed__", None)
    known.pop("__duplicate__", None)

    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            if os.path.dirname(path) == REQS:
                continue
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for ident in sorted(set(CITED.findall(text))):
                if ident not in known:
                    failures.append(
                        f"{os.path.relpath(path, ROOT)} cites undefined {ident}"
                    )

    for failure in sorted(f for f in failures if not f.startswith("__")):
        print(failure)
    print(f"{len(known)} requirements, {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
