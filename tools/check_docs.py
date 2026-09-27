#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The documentation agrees with the tree, as SPC-1110 states it.

A user-facing page is each unit's `README.md` and every Markdown file under
`docs/`. Each opens with front matter naming its reader, what it answers, its
kind and the unit versions it describes, so a version bump fails here until
every page describing that unit is read again and restamped. A page never
cites the record: an identifier in its prose or a link into `project/` sends
the reader somewhere written for somebody else.

    python3 tools/check_docs.py [--root DIR]
"""
import argparse
import json
import re
import sys
from pathlib import Path

FIELDS = ("reader", "answers", "kind", "describes")
CATALOGUE = ("description", "homepage", "repository", "license", "keywords")
CEILING = re.compile(r"^permanent_characters\s*=\s*(\d+)", re.M)
KINDS = ("introduction", "tutorial", "how-to", "reference", "explanation", "troubleshooting")
RECORD_KEYS = ("id", "artifact", "status")
IDENTIFIER = re.compile(r"\b(?:REQ|ADR|SPC|EPC|TSK|BUG|RES|INS)-\d{4}\b")
RECORD_PATH = re.compile(r"\bproject/(?:adrs|specs|research|requirements|epics|tasks|bugs|insights)/")
LINK = re.compile(r"\]\((?:<([^>]+)>|([^)\s]+))")
CODE_SPAN = re.compile(r"`[^`]*`")
FENCE = re.compile(r"^\s*(```|~~~)")


def front_matter(text):
    """The page's front matter as a dict, or None where it has none."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fields, last = {}, None
    for line in text[4:end].splitlines():
        # A formatter wraps a long list onto indented lines under its key.
        if line[:1] in (" ", "\t") and last:
            fields[last] = f"{fields[last]} {line.strip()}".strip()
            continue
        key, sep, value = line.partition(":")
        if sep:
            last = key.strip()
            fields[last] = value.strip()
    return fields


def described(value):
    """Each `unit@version` in a `describes` value, as pairs."""
    inner = value.strip().removeprefix("[").removesuffix("]")
    pairs = []
    for item in (part.strip() for part in inner.split(",")):
        if item:
            unit, _, version = item.partition("@")
            pairs.append((unit.strip(), version.strip()))
    return pairs


def units(root):
    """Each unit's name and version, from its `plugin.json`."""
    out = {}
    for manifest in sorted((root / "plugins").glob("*/.claude-plugin/plugin.json")):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        out[manifest.parent.parent.name] = data.get("version", "")
    return out


def pages(root):
    found = [path for path in sorted((root / "plugins").glob("*/README.md"))]
    docs = root / "docs"
    if docs.is_dir():
        found += sorted(docs.rglob("*.md"))
    return found


def body_lines(text):
    """Each line after the front matter with its number, outside fenced code."""
    lines = text.splitlines()
    start = 0
    if text.startswith("---\n"):
        for index in range(1, len(lines)):
            if lines[index] == "---":
                start = index + 1
                break
    fenced = False
    for number, line in enumerate(lines[start:], start + 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line


def check_page(root, path, versions):
    rel = path.relative_to(root)
    text = path.read_text(encoding="utf-8")
    fields = front_matter(text)
    if fields is None:
        return [f"{rel}: has no front matter"]
    out = [f"{rel}: front matter lacks {field}" for field in FIELDS if not fields.get(field)]
    out += [f"{rel}: front matter carries the record's {key}" for key in RECORD_KEYS if key in fields]
    if fields.get("kind") and fields["kind"] not in KINDS:
        out.append(f"{rel}: kind {fields['kind']} is not one of the six")
    for unit, version in described(fields.get("describes", "")):
        if unit not in versions:
            out.append(f"{rel}: describes {unit}, which doesn't exist")
        elif version != versions[unit]:
            out.append(f"{rel}: describes {unit}@{version}, the unit is at {versions[unit]}")
    for number, line in body_lines(text):
        prose = CODE_SPAN.sub("", line)
        for identifier in IDENTIFIER.findall(prose):
            out.append(f"{rel}:{number}: cites the record: {identifier}")
        for record_path in RECORD_PATH.findall(line):
            out.append(f"{rel}:{number}: cites the record: {record_path}")
        for bracketed, bare in LINK.findall(line):
            link = (bracketed or bare).split("#")[0]
            if not link or link.startswith(("http://", "https://", "mailto:")):
                continue
            target = (path.parent / link).resolve()
            if target == (root / "project").resolve() or (root / "project").resolve() in target.parents:
                out.append(f"{rel}:{number}: cites the record: {link}")
    return out


def ceiling(root, unit):
    """The characters the unit keeps in context on every turn, from its `budget.toml`."""
    budget = root / "plugins" / unit / "budget.toml"
    found = CEILING.search(budget.read_text(encoding="utf-8")) if budget.is_file() else None
    return int(found.group(1)) if found else None


def check_catalogue(root, unit):
    """The fields a reader sees before an install, written once in `plugin.json`."""
    data = json.loads((root / "plugins" / unit / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    out = [f"{unit}: plugin.json lacks {field}" for field in CATALOGUE if not data.get(field)]
    homepage = data.get("homepage", "")
    if homepage and not homepage.endswith(f"/plugins/{unit}/README.md"):
        out.append(f"{unit}: homepage doesn't point at plugins/{unit}/README.md")
    limit = ceiling(root, unit)
    description = data.get("description", "")
    if limit is None:
        out.append(f"{unit}: budget.toml states no ceiling")
    elif description:
        named = "nothing in context" if limit == 0 else f"{limit:,} characters"
        if named not in description:
            out.append(f"{unit}: the description doesn't name its ceiling, {named}")
    return out


def check(root):
    versions = units(root)
    failures = []
    for unit in versions:
        failures += check_catalogue(root, unit)
    for unit in versions:
        if not (root / "plugins" / unit / "README.md").is_file():
            failures.append(f"{unit}: has no README.md")
    for path in pages(root):
        failures += check_page(root, path, versions)
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.root.resolve()
    failures = check(root)
    for failure in failures:
        print(failure)
    print(f"{len(pages(root))} pages, {len(failures)} documentation failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
