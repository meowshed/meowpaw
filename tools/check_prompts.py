#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Every prompt the harness ships is written in one vocabulary of top-level tags.

A prompt's formatting carries into the reply it produces, so a prompt under
Markdown headings teaches headings (REQ-1130), and a tag nobody documented is
one the next author invents differently (REQ-1114). SPC-1010 states the
vocabulary: five tags, none nested, with Markdown inside them (ADR-1030). This
check reads every skill, agent, output style, fragment and prompt hook a unit
ships, and fails on a Markdown heading, on a tag outside the vocabulary, on a
tag opened inside another, and on text standing outside every tag.

Text inside `<example>` or `<input>` is quoted material, such as a failing
example or a text under review, so its headings are read and never judged.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
VOCABULARY = {"role", "rules", "steps", "example", "input"}
QUOTED = {"example", "input"}
PROMPTS = ("skills/**/*.md", "agents/*.md", "output-styles/*.md", "fragments/*.md")

TAG = re.compile(r"<(/?)([A-Za-z_][\w-]*)(?:\s[^<>]*)?>")
HEADING = re.compile(r"^#{1,6}\s")
FENCE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN = re.compile(r"`[^`]*`")


def body(text):
    """The text after the front matter, which is YAML because the platform reads it."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :], text[: end + 5].count("\n")
    return text, 0


def audit(text, where):
    """Each defect in one prompt, as 'where:line: what'."""
    found = []
    content, offset = body(text)
    stack, fenced = [], False
    for number, line in enumerate(content.splitlines(), start=offset + 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        quoted = any(tag in QUOTED for tag in stack)
        bare = CODE_SPAN.sub("", line)
        if not quoted and HEADING.match(line):
            found.append(f"{where}:{number}: a Markdown heading, where the prompt uses tags")
        outside = not stack and line.strip() != ""
        for match in TAG.finditer(bare):
            closing, name = match.group(1) == "/", match.group(2)
            if name not in VOCABULARY:
                message = f"{where}:{number}: <{name}> is not in the vocabulary SPC-1010 states"
                if not quoted and message not in found:
                    found.append(message)
                continue
            if closing:
                if name in stack:
                    while stack and stack.pop() != name:
                        pass
            else:
                if stack:
                    found.append(f"{where}:{number}: <{name}> opens inside <{stack[-1]}>, where tags are top-level only")
                stack.append(name)
        if outside and not TAG.match(line.strip()):
            found.append(f"{where}:{number}: text outside every tag")
    if stack:
        found.append(f"{where}: <{stack[-1]}> is never closed")
    return found


def prompts():
    """Every shipped prompt, as (where, text): the prompt files and each prompt hook's text."""
    for plugin in sorted(p for p in PLUGINS.iterdir() if p.is_dir()) if PLUGINS.is_dir() else []:
        for pattern in PROMPTS:
            for path in sorted(plugin.glob(pattern)):
                if "evals" not in path.parts:
                    yield str(path.relative_to(ROOT)), path.read_text(encoding="utf-8")
        hooks = plugin / "hooks" / "hooks.json"
        if hooks.exists():
            config = json.loads(hooks.read_text(encoding="utf-8"))
            for event, groups in config.get("hooks", {}).items():
                for group in groups:
                    for hook in group.get("hooks", []):
                        if hook.get("type") == "prompt":
                            yield f"{hooks.relative_to(ROOT)} ({event})", hook.get("prompt", "")


def main() -> int:
    failures, count = [], 0
    for where, text in prompts():
        count += 1
        failures += audit(text, where)
    noun = "prompt" if count == 1 else "prompts"
    print(f"{count} shipped {noun}, {len(failures)} failures")
    for line in failures:
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
