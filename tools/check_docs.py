#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The documentation agrees with the tree, as SPC-1110 states it.

A user-facing page is each unit's `README.md` and every Markdown file under
`docs/`. Each opens with front matter naming its reader, what it answers, its
kind and the unit versions it describes, so a version bump fails here until
every page describing that unit is read again and restamped. A page never
cites the record: an identifier in its prose or a link into `project/` sends
the reader somewhere written for somebody else. A page, the root README, the
constitution, the vision and the route file each state the number of steps
the method skill names, and no other.

    python3 tools/check_docs.py [--root DIR]
"""
import argparse
import json
import os
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
START = "<!-- check_docs index -->"
END = "<!-- /check_docs index -->"
NOT_WRITTEN = re.compile(r"^- `([a-z-]+)`:", re.M)
WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
         "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty")
NUMBER = r"[*_]*(" + "|".join(WORDS) + r"|\d+)[*_]*"
# The ways a page states how many steps the method has, each naming the method,
# the harness or the chain. A count of anything else, such as "install it in
# three steps" or "each tutorial follows the same three steps", matches none.
STEP_COUNT = re.compile(
    rf"\bthrough\s+the\s+same\s+{NUMBER}\s+steps\b"
    rf"|\bmethod(?:['\u2019]s|:|\s+has)\s+{NUMBER}\s+steps\b"
    rf"|\b(?:method|harness)\s+(?:that\s+)?(?:costs|costing|demands)\s+{NUMBER}\s+steps\b"
    rf"|{NUMBER}\s+steps\s+(?:run\s+in\s+a\s+chain|from\s+research)\b"
    rf"|{NUMBER}-step\s+chain\b",
    re.I,
)
STEP_LIST = re.compile(r"The\s+steps,\s+in\s+order,\s+are:?\s+(.*?)\.(?=\s|$)", re.S)
STEP_NAME = re.compile(r"^[a-z]+$")
QUOTE = re.compile(r"^\s*(?:>\s*)+")
COMMENT = re.compile(r"<!--.*?-->")
# Pages outside `docs/` and the units that state the chain to a reader.
LIVING = ("README.md", "CLAUDE.md", "llms.txt", "project/vision.md")


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


def table(root):
    """The index table, one row per page other than the index itself."""
    index = root / "docs" / "README.md"
    rows = ["| Page | For | Answers | Kind |", "| --- | --- | --- | --- |"]
    for path in pages(root):
        if path == index:
            continue
        fields = front_matter(path.read_text(encoding="utf-8")) or {}
        link = Path(os.path.relpath(path, index.parent)).as_posix()
        title = path.parent.name if path.name == "README.md" else path.stem
        rows.append(f"| [{title}]({link}) | {fields.get('reader', '')} | {fields.get('answers', '')} | {fields.get('kind', '')} |")
    return "\n".join(rows)


def section(text, heading):
    """The body of a `## heading` section, or None where there is none."""
    found = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return found.group(1) if found else None


def check_index(root):
    """The index lists every page, names what is planned, and records each kind not written."""
    index = root / "docs" / "README.md"
    if not index.is_file():
        return ["docs/README.md: there is no index"]
    text = index.read_text(encoding="utf-8")
    out = []
    if START not in text or END not in text:
        out.append(f"docs/README.md: has no {START} block")
    else:
        current = text.split(START, 1)[1].split(END, 1)[0].strip()
        if normalise(current) != normalise(table(root)):
            out.append("docs/README.md: the table is out of date; run --write")
    if section(text, "Planned") is None:
        out.append("docs/README.md: has no Planned section")
    carried = {(front_matter(path.read_text(encoding="utf-8")) or {}).get("kind") for path in pages(root)}
    listed = set(NOT_WRITTEN.findall(section(text, "Not written") or ""))
    for kind in KINDS:
        if kind not in carried and kind not in listed:
            out.append(f"docs/README.md: no page is {kind}, and Not written doesn't list it")
    return out


def normalise(table_text):
    """A table's cells, so a formatter padding the columns changes nothing."""
    return [[cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in table_text.splitlines() if line.strip() and not re.match(r"^\|[\s|:-]+\|$", line.strip())]


def write_index(root):
    index = root / "docs" / "README.md"
    text = index.read_text(encoding="utf-8")
    head, rest = text.split(START, 1)
    tail = rest.split(END, 1)[1]
    index.write_text(f"{head}{START}\n\n{table(root)}\n\n{END}{tail}", encoding="utf-8")


def method_steps(root):
    """How many steps the method skill names, with why it couldn't be read.

    `(None, [])` where no unit ships a method skill, so there is no count to
    hold; a failure where one does and its list can't be read, because a count
    nobody could read must never pass as a count that agreed.
    """
    skills = sorted((root / "plugins").glob("*/skills/method/SKILL.md"))
    if not skills:
        return None, []
    skill = skills[0]
    rel = skill.relative_to(root)
    try:
        text = skill.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, [f"{rel}: isn't UTF-8, so the method's step count can't be read"]
    listed = STEP_LIST.search(text)
    if not listed:
        return None, [f"{rel}: names no step list, \"The steps, in order, are ...\", so the step count can't be held"]
    # `a, b, ... and z`: commas separate, and only the last item holds `and`.
    items = [item.strip() for item in " ".join(listed.group(1).split()).split(",")]
    items[-1:] = [name.strip() for name in items[-1].rsplit(" and ", 1)] if " and " in items[-1] else items[-1:]
    names = [re.sub(r"^and\s+", "", item) for item in items if item]
    odd = [name for name in names if not STEP_NAME.match(name)]
    if odd:
        return None, [f"{rel}: names the step \"{odd[0]}\", where a step is one word, so the step count can't be held"]
    return len(names), []


def paragraphs(text):
    """Each run of non-blank lines outside fenced code, as its lines with their numbers."""
    run = []
    for number, line in body_lines(text):
        if line.strip():
            run.append((number, line))
        elif run:
            yield run
            run = []
    if run:
        yield run


def check_steps(root):
    """A living page states the number of steps the method skill names, and no other."""
    count, failures = method_steps(root)
    if count is None:
        return failures
    named = WORDS[count] if count < len(WORDS) else str(count)
    out = []
    for path in [root / name for name in LIVING] + pages(root):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            out.append(f"{rel}: isn't UTF-8")
            continue
        for run in paragraphs(text):
            # A statement wraps, so a paragraph is read as one line, with each
            # offset mapped back to the line it came from.
            joined, starts = "", []
            for number, line in run:
                starts.append((len(joined), number))
                joined += COMMENT.sub("", CODE_SPAN.sub("", QUOTE.sub("", line))).strip() + " "
            for match in STEP_COUNT.finditer(joined):
                said = next(group for group in match.groups() if group)
                at = match.start(match.lastindex)
                value = int(said) if said.isdigit() else WORDS.index(said.lower())
                if value != count:
                    line = max(number for offset, number in starts if offset <= at)
                    out.append(f"{rel}:{line}: states {said.lower()} steps, and the method names {named}")
    return out


ROUTE_ITEM = re.compile(r"^- \[[^\]]+\]\(([^)\s]+)\)(?:: .+)?$")


def check_route(root):
    """`llms.txt` routes an agent in the published format, and links what exists."""
    route = root / "llms.txt"
    if not route.is_file():
        return ["llms.txt: there is none"]
    lines = route.read_text(encoding="utf-8").splitlines()
    filled = [(number, line) for number, line in enumerate(lines, 1) if line.strip()]
    out = []
    if not filled or not filled[0][1].startswith("# "):
        out.append("llms.txt: lacks its H1")
    if len(filled) < 2 or not filled[1][1].startswith("> "):
        out.append("llms.txt: lacks its summary")
    for number, line in filled[2:]:
        if line.startswith("## "):
            continue
        item = ROUTE_ITEM.match(line)
        if not item:
            out.append(f"llms.txt:{number}: neither a heading, the summary nor a link")
            continue
        link = item.group(1).split("#")[0]
        if not link.startswith(("http://", "https://")) and not (root / link).exists():
            out.append(f"llms.txt:{number}: links to {link}, which doesn't exist")
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
    return failures + check_index(root) + check_route(root) + check_steps(root)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--write", action="store_true", help="regenerate the index table in docs/README.md")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.write:
        write_index(root)
    failures = check(root)
    for failure in failures:
        print(failure)
    print(f"{len(pages(root))} pages, {len(failures)} documentation failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
