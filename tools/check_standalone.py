#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Each unit stands alone (REQ-0012, REQ-0014, ADR-1270).

A unit comes to depend on another by running its files, so the check reads
every file a unit ships and fails on a path that leaves the unit's directory,
through `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}` or a climb into a
sibling, and on a path into another unit's directory. Naming another unit in
prose, as something to install, is allowed. Measurement cases and fixtures
aren't shipped behaviour, so they are skipped.
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIPPED = ("evals", "tests", "__pycache__")
VARIABLE = re.compile(r"\$\{?(CLAUDE_PLUGIN_ROOT|CLAUDE_SKILL_DIR)\}?((?:/[^\s\"'`)\]}]*)?)")
SIBLING = re.compile(r"plugins/(meow-[a-z-]+)|\.\./(meow-[a-z-]+)/")
# An address is a link a reader follows, and runs no file of the unit it names.
ADDRESS = re.compile(r"https?://\S+")


def findings(plugins: Path) -> tuple[list[str], int]:
    out, checked = [], 0
    for unit in sorted(p for p in plugins.iterdir() if p.is_dir()):
        for path in sorted(unit.rglob("*")):
            parts = path.relative_to(unit).parts
            if not path.is_file() or any(part in SKIPPED for part in parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            checked += 1
            shown = path.relative_to(plugins.parent)
            for number, line in enumerate(text.splitlines(), start=1):
                for match in VARIABLE.finditer(line):
                    if match.group(1) == "CLAUDE_PLUGIN_ROOT":
                        base = unit
                    elif parts[0] == "skills" and len(parts) > 2:
                        base = unit / parts[0] / parts[1]
                    else:
                        out.append(f"{shown}:{number}: uses CLAUDE_SKILL_DIR outside a skill")
                        continue
                    target = Path(os.path.normpath(base / match.group(2).lstrip("/")))
                    if target != unit and unit not in target.parents:
                        out.append(f"{shown}:{number}: reaches outside {unit.name}: {match.group(0)}")
                for match in SIBLING.finditer(ADDRESS.sub("", line)):
                    other = match.group(1) or match.group(2)
                    if other != unit.name:
                        out.append(f"{shown}:{number}: runs a file of {other}, another unit")
    return out, checked


def main() -> int:
    out, checked = findings(ROOT / "plugins")
    for line in out:
        print(line)
    print(f"{checked} unit files, {len(out)} paths leaving their unit")
    if checked == 0:
        print("no unit file was read, so nothing was checked")
        return 1
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
