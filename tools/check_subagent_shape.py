#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""A prompt that dispatches a subordinate agent carries the reply shape.

An output style reaches a fork and never a subordinate agent, which runs its
own system prompt, so a unit that dispatches one includes the style's rules
block in the prompt it sends (REQ-0954). This check reads every unit the harness ships,
finds the ones that dispatch, and fails on any that does not name the style
whose rules block it carries (ADR-1040).

It cannot see what a prompt does at run time. What it can see is whether the
material that writes the prompt names the file, which is the difference between
a unit that forgot and a unit that did not.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
FRAGMENT = "output-styles/meow.md"

# A unit dispatches when it names the platform's mechanism for doing so. A
# mention of the word "agent" is not a dispatch, or every document here would
# be one.
DISPATCHES = re.compile(
    r"\bTask tool\b|\bsubagent_type\b|\bdispatch(?:es|ing)? (?:a|the) "
    r"(?:subordinate|sub)[- ]agent\b",
    re.I,
)


def main() -> int:
    if not PLUGINS.is_dir():
        print("no plugins, nothing to check")
        return 0

    failures = []
    dispatchers = 0
    for path in sorted(PLUGINS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        if not DISPATCHES.search(text):
            continue
        dispatchers += 1
        if FRAGMENT not in text:
            failures.append(f"dispatches without the shape: {relative}")

    fragment = PLUGINS / "meow-core" / FRAGMENT
    if not fragment.is_file():
        failures.append(f"the style whose rules block a subordinate agent carries is missing: {fragment.relative_to(ROOT)}")

    verb = "dispatches" if dispatchers == 1 else "dispatch"
    print(f"{dispatchers} {verb} a subordinate agent, "
          f"{len(failures)} without the shape")
    for line in failures:
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
