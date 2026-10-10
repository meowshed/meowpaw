#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Living and shipped text calls the five stages stages (REQ-4200, ADR-2850).

Reads each tracked file and reports "verb" or "verbs" outside the allow-list
below, naming the file and the line, so the old word doesn't return the first
time a page is written from memory. A frozen record keeps the word it was
written with, so the record kinds that freeze aren't read. Each allow-list
entry carries its reason, because an entry without one is a hole nobody can
close.

    python3 tools/check_terms.py
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WORD = re.compile(r"\bverbs?\b", re.IGNORECASE)

# Directories and files that aren't read, each with the reason.
SKIPPED_PREFIXES = {
    "project/research/": "approved records are frozen and keep their word",
    "project/adrs/": "approved records are frozen and keep their word",
    "project/tasks/": "approved records are frozen and keep their word",
    "project/requirements/": "approved records are frozen and keep their word",
    "project/bugs/": "approved records are frozen and keep their word",
    "project/epics/": "approved records are frozen and keep their word",
    "project/insights/": "approved records are frozen and keep their word",
    "plugins/meow-prose/": "the writing standard says verb as the grammatical term",
    "packages/meow-prose/": "the mirror of the writing standard",
    "crates/": "Rust identifiers and module names, which no reader of the harness meets",
}
SKIPPED_FILES = {
    "project/README.md": "the index quotes the titles of frozen records",
    "plugins/meow-flow/lib/layout.toml": "the onboarding section name `Verbs` is record shape and needs a migration",
    "plugins/meow-loop/lib/layout.toml": "the onboarding section name `Verbs` is record shape and needs a migration",
    "tools/check_subagent_shape.py": "a grammatical use: the verb of a sentence",
    "tools/check_gate_covers_verbs.py": "a file name and a local variable",
}
SKIPPED_PARTS = {
    "/evals/": "evaluation cases are measured inputs and keep their wording",
    "/tests/": "tests that exercise the deprecated table and the old names",
    "bin/meow-checks": "shell variables and the `verbs` subcommand of the tool",
}
SKIPPED_NAMES = ("test_",)

# A line that names something which keeps its spelling, with the reason.
KEPT = re.compile(
    r"meow-verbs"  # the retired unit's name
    r"|verbs="  # the loop's --until argument
    r"|`verbs`"  # the tool's subcommand, spelled as code
    r"|\[verbs[\].]"  # the deprecated profile table
    r"|\"verbs\""  # the key of the tool's JSON report
    r"|\bVERBS\b"  # a constant
)


def tracked(root):
    done = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True)
    return [name for name in done.stdout.splitlines() if name]


def skipped(name):
    return (
        name.startswith(tuple(SKIPPED_PREFIXES))
        or name in SKIPPED_FILES
        or any(part in name for part in SKIPPED_PARTS)
        or Path(name).name.startswith(SKIPPED_NAMES)
    )


def main(root: Path = ROOT) -> int:
    found = []
    read = 0
    for name in tracked(root):
        if skipped(name):
            continue
        try:
            text = (root / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        read += 1
        for number, line in enumerate(text.splitlines(), 1):
            match = WORD.search(line)
            if match and not KEPT.search(line):
                found.append(f"{name}:{number}: says {match.group(0).lower()}, where the text says stages")
    for line in found:
        print(line)
    print(f"{read} files read, {len(found)} uses of the old word")
    return 1 if found or not read else 0


if __name__ == "__main__":
    sys.exit(main())
