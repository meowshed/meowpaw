#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Every artifact carries front matter naming its kind, status and revision date."""
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"_archive", ".claude", ".git", "node_modules", "target", ".github", "templates", "plugins", "docs"}
EXEMPT = {"README.md", "CLAUDE.md", "LICENSE"}
REQUIRED = ("id", "artifact", "status", "revised")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def main() -> int:
    failures = []
    identifiers: list[tuple[str, str]] = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in files:
            if not name.endswith(".md") or name in EXEMPT:
                continue
            path = os.path.join(root, name)
            relative = os.path.relpath(path, ROOT)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            if not text.startswith("---\n"):
                failures.append(f"{relative}: no front matter")
                continue
            block = text.split("---\n", 2)[1]
            fields = dict(
                line.split(":", 1) for line in block.splitlines() if ":" in line
            )
            fields = {key.strip(): value.strip() for key, value in fields.items()}
            for key in REQUIRED:
                if key not in fields:
                    failures.append(f"{relative}: front matter has no {key}")
            if "id" in fields:
                identifiers.append((relative, fields["id"]))
            revised = fields.get("revised", "")
            if revised and not DATE.match(revised):
                failures.append(f"{relative}: revised is not a date: {revised}")
            elif revised and revised > datetime.date.today().isoformat():
                failures.append(f"{relative}: revised is in the future: {revised}")

    seen: dict[str, str] = {}
    for path, ident in identifiers:
        if ident in seen:
            failures.append(f"{path}: identifier {ident} also used by {seen[ident]}")
        seen[ident] = path

    for failure in sorted(failures):
        print(failure)
    print(f"{len(seen)} artifacts, {len(failures)} front matter failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
