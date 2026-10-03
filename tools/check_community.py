#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The six community files sit under `.github/`.

A newcomer needs how to contribute, how to report a vulnerability, the
behaviour expected, the code owners and the templates for an issue and a pull
request (REQ-2214), each where GitHub reads it (REQ-2216, ADR-2510). The check
reads `.github/` alone, so a file kept only at the root counts as missing, and
it fails naming each file it can't find.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = (
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CODEOWNERS",
    "pull_request_template.md",
)
ISSUE_TEMPLATES = "ISSUE_TEMPLATE"


def missing(root: Path) -> list[str]:
    github = root / ".github"
    absent = [f".github/{name}" for name in FILES if not (github / name).is_file()]
    templates = github / ISSUE_TEMPLATES
    if not (templates.is_dir() and any(p.is_file() for p in templates.iterdir())):
        absent.append(f".github/{ISSUE_TEMPLATES}/")
    return absent


def main(root: Path = ROOT) -> int:
    absent = missing(root)
    for name in absent:
        print(f"missing: {name}")
    print(f"{len(FILES) + 1} community files, {len(absent)} missing from .github/")
    return 1 if absent else 0


if __name__ == "__main__":
    sys.exit(main())
