#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Every relative Markdown link resolves to a file that exists."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"_archive", ".claude", ".git", "node_modules", "target"}


def main() -> int:
    bad = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for link in re.findall(r"\]\(([^)]+)\)", text):
                if link.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target = os.path.normpath(os.path.join(root, link.split("#")[0]))
                if not os.path.exists(target):
                    bad.append(f"{os.path.relpath(path, ROOT)} -> {link}")

    for entry in bad:
        print(f"dangling link: {entry}")
    print(f"{len(bad)} dangling links")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
