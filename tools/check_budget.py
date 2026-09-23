#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Every unit stays within the budget it states for what loads on every turn.

Only what a model needs to decide whether a unit is relevant sits in context on
every turn (REQ-1050), and each unit states a budget for it, measured and not
guessed (REQ-1056). This check counts that permanent load in characters, which
needs no model and gives the same number twice: the description and
`when_to_use` of each skill and agent, and the whole of each output style,
which loads on every turn it is in force. A hook's prompt loads only when the
hook fires, so it counts nothing. It fails on a unit over its budget, on a unit
with no budget, and on a description over the platform's cap of 1,536
characters (REQ-1058, REQ-1060).
"""

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
CAP = 1536


def front_matter(text):
    if not text.startswith("---\n"):
        return {}
    block = text[4 : text.index("\n---\n", 4)]
    fields = {}
    for name in ("description", "when_to_use"):
        match = re.search(rf"^{name}:\s*(.*)$", block, re.M)
        if match:
            fields[name] = match.group(1).strip().strip("\"'")
    return fields


def permanent(unit):
    """Each piece of the unit that loads on every turn, as (path, characters)."""
    pieces = []
    for path in sorted(unit.glob("skills/*/SKILL.md")) + sorted(unit.glob("agents/**/*.md")):
        fields = front_matter(path.read_text(encoding="utf-8"))
        listed = " ".join(v for v in (fields.get("description"), fields.get("when_to_use")) if v)
        pieces.append((path, len(listed)))
    for path in sorted(unit.glob("output-styles/*.md")):
        pieces.append((path, len(path.read_text(encoding="utf-8"))))
    return pieces


def main() -> int:
    failures = []
    units = sorted(p for p in PLUGINS.iterdir() if (p / ".claude-plugin" / "plugin.json").exists())
    for unit in units:
        pieces = permanent(unit)
        for path, size in pieces:
            if "SKILL.md" in path.name or "agents" in path.parts:
                if size > CAP:
                    failures.append(f"{path.relative_to(ROOT)}: description is {size} characters, over the cap of {CAP}")
        total = sum(size for _, size in pieces)
        budget_file = unit / "budget.toml"
        if not budget_file.exists():
            failures.append(f"{unit.name}: states no budget in budget.toml")
            continue
        budget = tomllib.loads(budget_file.read_text(encoding="utf-8"))["permanent_characters"]
        if total > budget:
            failures.append(f"{unit.name}: loads {total} characters on every turn, {total - budget} over its budget of {budget}")
        print(f"{unit.name}: {total} of {budget} characters on every turn")
    for line in failures:
        print(line)
    print(f"{len(units)} units, {len(failures)} budget failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
