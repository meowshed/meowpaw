#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Every output style the harness ships keeps the platform's instructions and
states, for each rule, the condition under which it yields.

Two failures this catches, both silent otherwise.

`keep-coding-instructions` defaults to false, so a style written to fix the
wording of a report deletes the platform's software engineering guidance and
says nothing about it.

A rule with no stated exception is switched off entirely the first time it
costs an answer (REQ-0931), and a style whose rules carry no exceptions reads
correct right up to the moment somebody disables the lot.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLES = ROOT / "plugins"
# A tagged rule states its condition as a sentence, "It yields when" or "It
# never yields". The older form under a heading wrote `_Yields_`, where the
# underscore is a word character, so `\b` after it never matches.
YIELDS = re.compile(r"\bIt (?:never )?yields\b|^_Yields(?:_|\s)", re.M)
RULES = re.compile(r"<rules[^>]*>(?P<body>.*?)</rules>", re.S)
ITEM = re.compile(r"^- (?P<id>[A-Z]+\d+)\. (?P<text>.*?)(?=^- |\Z)", re.S | re.M)
FIELD = re.compile(r"^(?P<key>[a-z-]+):\s*(?P<value>.+?)\s*$", re.M)


def front_matter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    return dict(
        (m.group("key"), m.group("value")) for m in FIELD.finditer(text[4:end])
    )


def rules(body):
    """Each rule with its text: a list item led by an identifier inside `<rules>`
    (ADR-1030), or in the older form each `##` section."""
    tagged = [(m.group("id"), m.group("text"))
              for block in RULES.finditer(body) for m in ITEM.finditer(block.group("body") + "\n")]
    if tagged:
        return tagged
    parts = re.split(r"^## (.+)$", body, flags=re.M)[1:]
    return list(zip(parts[0::2], parts[1::2]))


def main() -> int:
    failures = []
    styles = sorted(STYLES.glob("*/output-styles/*.md")) if STYLES.is_dir() else []

    if not styles:
        print("no output styles, nothing to check")
        return 0

    for path in styles:
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        matter = front_matter(text)

        if matter is None:
            failures.append(f"{relative}: no front matter")
            continue

        if matter.get("keep-coding-instructions") != "true":
            failures.append(
                f"{relative}: keep-coding-instructions is "
                f"{matter.get('keep-coding-instructions', 'absent')}, "
                "so the platform's engineering instructions are deleted"
            )

        body = text[text.find("\n---\n", 4) + 5 :]
        for heading, section in rules(body):
            if not YIELDS.search(section):
                failures.append(
                    f"{relative}: the rule '{heading}' states no condition "
                    "under which it yields"
                )

    noun = "output style" if len(styles) == 1 else "output styles"
    print(f"{len(styles)} {noun}, {len(failures)} failures")
    for line in failures:
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
