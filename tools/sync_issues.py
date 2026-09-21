#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The work item on the forge carries the record's own text.

A record and its issue say the same thing in two places, and two wordings drift
(REQ-1360 wants one work item mapped to one record, linked both ways). This
sends the record's body to the issue named in its front matter, so the forge
mirrors the repository and the repository stays the original.

Run it after a record changes:

    python3 tools/sync_issues.py            # report what differs
    python3 tools/sync_issues.py --write    # send the bodies
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "project"
KINDS = ("bugs", "tasks")


def parts(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    end = text.index("\n---\n", 4)
    block = text[4:end]
    front = dict(
        (m.group(1), m.group(2).strip())
        for m in re.finditer(r"^([a-z-]+):\s*(.*)$", block, re.M)
    )
    return front, text[end + 5 :].lstrip("\n")


def body_for(path, record):
    return f"{record}\n---\n\nThe record is `{path.relative_to(ROOT)}`, and it is the original.\n"


def main(write):
    changed = 0
    for kind in KINDS:
        for path in sorted((PROJECT / kind).glob("*.md")):
            front, record = parts(path)
            number = front.get("issue")
            if not number:
                continue
            want = body_for(path, record)
            have = subprocess.run(
                ["gh", "issue", "view", number, "--json", "body", "-q", ".body"],
                capture_output=True, text=True, check=True,
            ).stdout
            if have.strip() == want.strip():
                continue
            changed += 1
            print(f"#{number} differs from {path.name}")
            if write:
                subprocess.run(
                    ["gh", "issue", "edit", number, "--body", want],
                    capture_output=True, text=True, check=True,
                )
                print(f"#{number} updated from {path.name}")

    print(f"{changed} issues differ from their record")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
