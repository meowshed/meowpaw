#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Every research artifact states its sources and its conclusions.

A claim whose source is not listed is an assertion. A document with no
conclusions is one nothing downstream can be drawn from: requirements are built
from the conclusions, so research that ends without them ends with the reader
inferring what it meant. An index that only points at other research is exempt:
its sources are theirs and its conclusions are theirs.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"_archive", ".claude", ".git", "node_modules", "target", ".github", "tools", "templates"}
KIND = re.compile(r"^artifact:\s*(\S+)", re.M)
REQUIRED = {
    "sources": re.compile(r"^##+\s+Sources\b", re.M),
    "conclusions": re.compile(r"^##+\s+Conclusions\b", re.M),
}
# An index lists other documents; it makes no claims of its own.
EXEMPT = {"README.md"}


def main() -> int:
    failures = []
    checked = 0
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in files:
            if not name.endswith(".md") or name in EXEMPT:
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            kind = KIND.search(text)
            if not kind or kind.group(1) != "research":
                continue
            checked += 1
            for section, pattern in REQUIRED.items():
                if not pattern.search(text):
                    failures.append(
                        f"no {section} section: {os.path.relpath(path, ROOT)}"
                    )

    for failure in sorted(failures):
        print(failure)
    print(f"{checked} research artifacts, {len(failures)} missing sections")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
