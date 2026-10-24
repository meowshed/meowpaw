#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""A unit's four copies of its description agree, and its package page mirrors its page (REQ-3196, REQ-4622).

The plugin manifest's `description` is the source. The plugin page carries it
verbatim as `description` in its front matter. The package manifest and the
first paragraph of the package page carry it with the host's substitutions
(Claude Code becomes Pi) and the sentence "Distributed as a Pi package." at the
end. The check fails naming each copy that differs.

A package page also has every `##` section of its unit's page, matched by
heading after the same substitutions, apart from a section whose heading is
followed by the line `<!-- host-specific: claude -->`: that marks a section
about a mechanism only Claude Code has, which the package page doesn't mirror.
The check fails naming each section a package page lacks. A run that reads no
unit fails, because a check over nothing is no pass.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARK = "<!-- host-specific: claude -->"
SUFFIX = " Distributed as a Pi package."


def host(text: str) -> str:
    """The text as the Pi host says it: the agent is Pi and a plugin is a package."""
    text = re.sub(r"(Neovim|Vim)(\s+)plugin", r"\1\2PLUGINWORD", text)
    text = re.sub(r"\bplugins\b", "packages", text)
    text = re.sub(r"\bplugin\b", "package", text)
    text = re.sub(r"\bPlugin\b", "Package", text)
    text = text.replace("PLUGINWORD", "plugin")
    return text.replace("Claude Code's", "Pi's").replace("Claude Code", "Pi").replace("Claude", "Pi")


def host_description(text: str) -> str:
    """A description as the Pi host says it: Claude Code becomes Pi, and nothing else changes."""
    return text.replace("Claude Code's", "Pi's").replace("Claude Code", "Pi")


def front_matter(text: str) -> dict[str, str]:
    """The page's front matter as a dict; a wrapped value is joined with single spaces."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    last = None
    for line in text[4:end].splitlines():
        if line[:1] in (" ", "\t") and last:
            fields[last] = f"{fields[last]} {line.strip()}".strip()
            continue
        key, sep, value = line.partition(":")
        if sep:
            last = key.strip()
            fields[last] = value.strip()
    return fields


def sections(text: str) -> list[list[str]]:
    """The `##` sections of a page, each as its lines, outside fenced code."""
    out: list[list[str]] = []
    fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            fence = not fence
        if not fence and line.startswith("## "):
            out.append([line])
        elif out:
            out[-1].append(line)
    return out


def lead(text: str) -> str:
    """The first paragraph line after the page's title."""
    lines = text.split("\n")
    for n, line in enumerate(lines):
        if line.startswith("# "):
            for rest in lines[n + 1:]:
                if rest.strip():
                    return rest
    return ""


def check(root: Path = ROOT) -> list[str]:
    """Every copy of a description that differs and every section a package page lacks."""
    problems: list[str] = []
    manifests = sorted((root / "plugins").glob("*/.claude-plugin/plugin.json"))
    if not manifests:
        return ["no unit was read: plugins/*/.claude-plugin/plugin.json matched nothing"]
    for manifest in manifests:
        unit = manifest.parent.parent.name
        source = json.loads(manifest.read_text(encoding="utf-8")).get("description", "")
        want = host_description(source) + SUFFIX
        page = root / "plugins" / unit / "README.md"
        package = root / "packages" / unit
        try:
            raw = front_matter(page.read_text(encoding="utf-8")).get("description", "")
            if json.loads(raw) != source if raw else True:
                problems.append(f"plugins/{unit}/README.md: front matter description differs from plugins/{unit}/.claude-plugin/plugin.json (REQ-3196)")
        except (OSError, ValueError):
            problems.append(f"plugins/{unit}/README.md: front matter description is missing or isn't a quoted string (REQ-3196)")
        try:
            described = json.loads((package / "package.json").read_text(encoding="utf-8")).get("description", "")
            if described != want:
                problems.append(f"packages/{unit}/package.json: description differs from plugins/{unit}/.claude-plugin/plugin.json (REQ-3196)")
        except (OSError, ValueError):
            problems.append(f"packages/{unit}/package.json: missing or unreadable (REQ-3196)")
        try:
            package_page = (package / "README.md").read_text(encoding="utf-8")
        except OSError:
            problems.append(f"packages/{unit}/README.md: missing (REQ-3196, REQ-4622)")
            continue
        if lead(package_page) != want:
            problems.append(f"packages/{unit}/README.md: first paragraph differs from plugins/{unit}/.claude-plugin/plugin.json (REQ-3196)")
        have = {s[0] for s in sections(package_page)}
        try:
            unit_sections = sections(page.read_text(encoding="utf-8"))
        except OSError:
            continue
        for section in unit_sections:
            if MARK in section[1:4]:
                continue
            if host(section[0]) not in have:
                problems.append(f"packages/{unit}/README.md: lacks the section '{section[0][3:]}' of plugins/{unit}/README.md, and the unit page doesn't mark it host-specific (REQ-4622)")
    return problems


def main() -> int:
    problems = check()
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print("every unit's description and page agree with its package's")
    return 0


if __name__ == "__main__":
    sys.exit(main())
