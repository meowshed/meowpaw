#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Every workflow under `.github/workflows/` starts read-only and trusts no foreign value.

A workflow declares `permissions:` at its top level with `contents: read` and
nothing else, so a job gets write access only where it asks for it
(REQ-2196). A workflow triggered by `pull_request_target` or `workflow_run`
runs with a write token, so it runs no `actions/checkout` (REQ-2198). A `run:`
value holds no `${{`, so a value the workflow doesn't control reaches a script
only through `env:` (REQ-2200). ADR-2520 decided the rules and SPC-1210 states
them under "The workflows".

The check reads each file as YAML, because a `run:` value spans several lines
and only the structure says which key a line belongs to. The standard library
has no YAML parser and the gate installs none, so `Reader` takes the block and
flow forms a workflow is written in, and reports an anchor, an alias, a tag, a
tab in the indentation or a quoted scalar spanning lines as a file that
doesn't parse.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ".github/workflows"
SUFFIXES = (".yml", ".yaml")
ALLOWED = ("contents", "read")
FORBIDDEN_TRIGGERS = ("pull_request_target", "workflow_run")
CHECKOUT = "actions/checkout"
BLOCK_HEADER = re.compile(r"([|>])([1-9]?)([+-]?)([1-9]?)\s*(#.*)?")


class ParseError(Exception):
    def __init__(self, line, message):
        super().__init__(f"line {line}: {message}")


class Scalar(str):
    """A string that keeps each file line it was read from, as (line number, text) pairs."""

    source: list


class Mapping(dict):
    """A mapping that keeps the file line of each key in `lines`."""

    def __init__(self):
        super().__init__()
        self.lines = {}


def scalar(text, source):
    value = Scalar(text)
    value.source = source
    return value


def is_item(content):
    return content == "-" or content.startswith("- ")


def quoted(text, start, line):
    """Read the quoted scalar opening at `text[start]` and return it with the index after it."""
    quote = text[start]
    out = []
    i = start + 1
    while i < len(text):
        c = text[i]
        if quote == "'" and c == "'":
            if text[i + 1 : i + 2] == "'":
                out.append("'")
                i += 2
                continue
            return "".join(out), i + 1
        if quote == '"' and c == "\\" and i + 1 < len(text):
            out.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(text[i + 1], "\\" + text[i + 1]))
            i += 2
            continue
        if quote == '"' and c == '"':
            return "".join(out), i + 1
        out.append(c)
        i += 1
    raise ParseError(line, f"a {quote}-quoted scalar has no closing quote on its line")


def key_split(content, line):
    """Return (key, the text after its colon) where `content` opens with a key, and None otherwise."""
    if not content or content[0] in "[{":
        return None
    if content[0] in "\"'":
        key, end = quoted(content, 0, line)
        rest = content[end:]
        if rest == ":" or rest.startswith(": "):
            return key, rest[1:]
        return None
    index = content.find(": ")
    if index < 0:
        if not content.endswith(":"):
            return None
        index = len(content) - 1
    return content[:index].rstrip(), content[index + 1 :]


def strip_comment(text):
    index = text.find(" #")
    return text if index < 0 else text[:index].rstrip()


class Flow:
    """Reads one flow collection or scalar, `[a, b]` or `{ k: v }`, from `text` at `start`."""

    STOPS = ",[]{}\n"

    def __init__(self, text, start, first_line):
        self.text = text
        self.p = start
        self.first_line = first_line

    def line(self):
        return self.first_line + self.text.count("\n", 0, self.p)

    def peek(self):
        if self.p >= len(self.text):
            raise ParseError(self.line(), "a flow collection has no closing bracket")
        return self.text[self.p]

    def space(self):
        while self.p < len(self.text):
            c = self.text[self.p]
            if c in " \n":
                self.p += 1
            elif c == "#" and (self.p == 0 or self.text[self.p - 1] in " \n"):
                end = self.text.find("\n", self.p)
                self.p = len(self.text) if end < 0 else end
            else:
                return

    def node(self):
        self.space()
        c = self.peek()
        if c == "[":
            return self.sequence()
        if c == "{":
            return self.mapping()
        line = self.line()
        if c in "\"'":
            value, end = quoted(self.text, self.p, line)
            raw = self.text[self.p : end]
            self.p = end
            return scalar(value, [(line, raw)])
        if c in "&*!":
            raise ParseError(line, "anchors, aliases and tags aren't read")
        start = self.p
        while self.p < len(self.text):
            c = self.text[self.p]
            if c in self.STOPS or (c == ":" and self.text[self.p + 1 : self.p + 2] in ("", " ", ",", "]", "}", "\n")):
                break
            if c == "#" and self.text[self.p - 1] == " ":
                break
            self.p += 1
        raw = self.text[start : self.p].strip()
        if not raw:
            raise ParseError(line, f"unexpected {c!r} in a flow collection")
        return scalar(raw, [(line, raw)])

    def sequence(self):
        self.p += 1
        items = []
        while True:
            self.space()
            if self.peek() == "]":
                self.p += 1
                return items
            items.append(self.node())
            self.space()
            c = self.peek()
            if c == ",":
                self.p += 1
            elif c != "]":
                raise ParseError(self.line(), f"expected , or ] in a flow sequence, found {c!r}")

    def mapping(self):
        self.p += 1
        result = Mapping()
        while True:
            self.space()
            if self.peek() == "}":
                self.p += 1
                return result
            line = self.line()
            key = self.node()
            if not isinstance(key, str):
                raise ParseError(line, "a flow mapping's key is a collection")
            self.space()
            value = None
            if self.peek() == ":":
                self.p += 1
                self.space()
                if self.peek() not in ",}":
                    value = self.node()
            result[str(key)] = value
            result.lines[str(key)] = line
            self.space()
            c = self.peek()
            if c == ",":
                self.p += 1
            elif c != "}":
                raise ParseError(self.line(), f"expected , or }} in a flow mapping, found {c!r}")


class Reader:
    """Reads the YAML subset a workflow is written in into dicts, lists and `Scalar` strings."""

    def __init__(self, text):
        self.lines = [line.rstrip("\r") for line in text.split("\n")]
        for number, line in enumerate(self.lines, 1):
            if "\t" in line[: len(line) - len(line.lstrip(" \t"))]:
                raise ParseError(number, "a tab in the indentation")

    def indent(self, i):
        line = self.lines[i]
        return len(line) - len(line.lstrip(" "))

    def content(self, i):
        return self.lines[i].lstrip(" ").rstrip()

    def skip(self, i):
        while i < len(self.lines):
            content = self.content(i)
            if content and not content.startswith("#"):
                return i
            i += 1
        return i

    def document(self):
        i = self.skip(0)
        if i < len(self.lines) and self.content(i) == "---":
            i = self.skip(i + 1)
        if i >= len(self.lines):
            return None
        node, i = self.node(i, -1)
        i = self.skip(i)
        if i < len(self.lines) and self.content(i) != "...":
            raise ParseError(i + 1, "unexpected indentation")
        return node

    def node(self, i, parent):
        """Read the node opening on line `i`, whose owner sits at column `parent`."""
        content = self.content(i)
        if is_item(content):
            return self.sequence(i, self.indent(i))
        if key_split(content, i + 1) is not None:
            return self.mapping(i, self.indent(i))
        return self.value(i, parent, content, self.indent(i))

    def sequence(self, i, indent):
        items = []
        while True:
            i = self.skip(i)
            if i >= len(self.lines) or self.indent(i) < indent:
                return items, i
            content = self.content(i)
            if self.indent(i) > indent:
                raise ParseError(i + 1, "unexpected indentation")
            if not is_item(content):
                return items, i
            rest = content[1:]
            text = rest.lstrip(" ")
            if not text or text.startswith("#"):
                j = self.skip(i + 1)
                if j < len(self.lines) and self.indent(j) > indent:
                    item, i = self.node(j, indent)
                else:
                    item, i = None, i + 1
            else:
                # The item opens on the dash's line, so read that line as if it began at the item.
                self.lines[i] = " " * (indent + 1 + len(rest) - len(text)) + text
                item, i = self.node(i, indent)
            items.append(item)

    def mapping(self, i, indent):
        result = Mapping()
        while True:
            i = self.skip(i)
            if i >= len(self.lines) or self.indent(i) < indent:
                return result, i
            if self.indent(i) > indent:
                raise ParseError(i + 1, "unexpected indentation")
            content = self.content(i)
            if is_item(content):
                raise ParseError(i + 1, "a sequence item among a mapping's keys")
            split = key_split(content, i + 1)
            if split is None:
                raise ParseError(i + 1, "expected a key")
            key, rest = split
            if key in result:
                raise ParseError(i + 1, f"the key {key} appears twice")
            result.lines[key] = i + 1
            text = rest.lstrip(" ")
            if not text or text.startswith("#"):
                j = self.skip(i + 1)
                below = j < len(self.lines) and (
                    self.indent(j) > indent or (self.indent(j) == indent and is_item(self.content(j)))
                )
                if below:
                    value, i = self.node(j, indent)
                else:
                    value, i = None, i + 1
            else:
                column = indent + len(content) - len(text)
                value, i = self.value(i, indent, text, column)
            result[key] = value

    def value(self, i, parent, text, column):
        """Read the scalar or flow value `text`, found on line `i` at `column`."""
        head = text[0]
        if head in "|>":
            return self.block_scalar(i, parent, text)
        if head in "[{":
            flow = Flow("\n".join(self.lines[i:]), column, i + 1)
            node = flow.node()
            end = i + flow.text.count("\n", 0, flow.p)
            tail = flow.text[flow.p :].split("\n", 1)[0].strip()
            if tail and not tail.startswith("#"):
                raise ParseError(end + 1, f"unexpected {tail!r} after a flow collection")
            return node, end + 1
        if head in "&*!":
            raise ParseError(i + 1, "anchors, aliases and tags aren't read")
        if head in "\"'":
            value, end = quoted(text, 0, i + 1)
            tail = text[end:].strip()
            if tail and not tail.startswith("#"):
                raise ParseError(i + 1, f"unexpected {tail!r} after a quoted scalar")
            return scalar(value, [(i + 1, text[:end])]), i + 1
        source = [(i + 1, strip_comment(text))]
        j = i + 1
        while j < len(self.lines):
            content = self.content(j)
            if not content or content.startswith("#") or self.indent(j) <= parent:
                break
            source.append((j + 1, strip_comment(content)))
            j += 1
        return scalar(" ".join(part for _, part in source), source), j

    def block_scalar(self, i, parent, header):
        match = BLOCK_HEADER.fullmatch(header)
        if not match:
            raise ParseError(i + 1, f"a block scalar's header {header!r} isn't read")
        style, before, chomp, after = match.group(1, 2, 3, 4)
        indicator = before or after
        body = []
        content_indent = parent + int(indicator) if indicator else None
        j = i + 1
        while j < len(self.lines):
            line = self.lines[j]
            if not line.strip():
                body.append((j + 1, ""))
                j += 1
                continue
            if content_indent is None:
                if self.indent(j) <= parent:
                    break
                content_indent = self.indent(j)
            if self.indent(j) < content_indent:
                break
            body.append((j + 1, line[content_indent:]))
            j += 1
        while body and not body[-1][1]:
            body.pop()
        joiner = "\n" if style == "|" else " "
        text = joiner.join(part for _, part in body)
        if body and chomp != "-":
            text += "\n"
        return scalar(text, body), j


def walk(node):
    yield node
    children = node.values() if isinstance(node, dict) else node if isinstance(node, list) else ()
    for child in children:
        yield from walk(child)


def first_line(node, default):
    return node.source[0][0] if isinstance(node, Scalar) and node.source else default


def permissions(name, doc):
    if "permissions" not in doc:
        return [f"{name}: no top-level permissions"]
    value = doc["permissions"]
    line = doc.lines["permissions"]
    if isinstance(value, Mapping):
        return [
            f"{name}:{value.lines[key]}: top-level permission {key}: {grant}, where only contents: read is allowed"
            for key, grant in value.items()
            if (key, grant) != ALLOWED
        ]
    shown = value if isinstance(value, str) else "with no value" if value is None else "as a list"
    return [f"{name}:{line}: top-level permission {shown}, where only contents: read is allowed"]


def triggers(name, doc):
    on = doc.get("on")
    line = doc.lines.get("on")
    if isinstance(on, Mapping):
        named = [(key, on.lines[key]) for key in on]
    elif isinstance(on, list):
        named = [(str(item), first_line(item, line)) for item in on if isinstance(item, str)]
    elif isinstance(on, str):
        named = [(str(on), line)]
    else:
        named = []
    checks_out = any(
        isinstance(node, dict)
        and isinstance(node.get("uses"), str)
        and (node["uses"] == CHECKOUT or node["uses"].startswith(CHECKOUT + "@"))
        for node in walk(doc)
    )
    if not checks_out:
        return []
    return [
        f"{name}:{at}: trigger {trigger} in a workflow that runs {CHECKOUT}"
        for trigger, at in named
        if trigger in FORBIDDEN_TRIGGERS
    ]


def runs(name, doc):
    found = []
    for node in walk(doc):
        if isinstance(node, dict) and isinstance(node.get("run"), Scalar):
            found += [f"{name}:{line}: ${{{{ in a run: line" for line, text in node["run"].source if "${{" in text]
    return found


def findings(name, text):
    try:
        doc = Reader(text).document()
    except ParseError as error:
        return [f"{name}: doesn't parse: {error}"]
    if not isinstance(doc, Mapping):
        return [f"{name}: doesn't parse: the top level isn't a mapping"]
    return permissions(name, doc) + triggers(name, doc) + runs(name, doc)


def main(root: Path = ROOT) -> int:
    directory = root / WORKFLOWS
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.suffix in SUFFIXES) if directory.is_dir() else []
    found = [] if files else [f"no workflow files under {WORKFLOWS}/"]
    for path in files:
        found += findings(path.relative_to(root).as_posix(), path.read_text(encoding="utf-8"))
    for line in found:
        print(line)
    print(f"{len(files)} workflow files, {len(found)} findings")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
