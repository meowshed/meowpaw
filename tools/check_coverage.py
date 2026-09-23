#!/usr/bin/env python3
"""Every requirement a decision addresses lands in exactly one task.

Reads each epic's authorising record, collects the requirements that record
addresses, and compares them against the union of `closes` over the tasks that
name the epic. A requirement in neither is uncovered; a requirement in two is
claimed twice. Both fail, and a deferral is only honest where the epic says so
under its own heading.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "project"
ID = re.compile(r"REQ-\d{4}")


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return "", text
    end = text.index("\n---\n", 4)
    return text[4:end], text[end + 5 :]


def field(block, name):
    """The raw value of a front matter field, flowed or on one line."""
    match = re.search(rf"^{name}:(.*?)(?=^\S|\Z)", block + "\n", re.S | re.M)
    return match.group(1) if match else ""


def deferred(body, claimed):
    """Named under 'Not covered' and claimed by no task.

    A requirement a task closes is covered, and naming it under that heading is
    prose about what part of it waits, never a deferral.
    """
    match = re.search(r"^## Not covered$(.*)", body, re.S | re.M)
    named = set(ID.findall(match.group(1))) if match else set()
    return named - set(claimed)


def stated() -> set:
    """Every requirement the specifications say they project.

    REQ-0244 wants each requirement in force stated somewhere, and REQ-0246
    wants both directions checked. The task direction below answers who builds
    it; this one answers where it is written down.
    """
    out = set()
    for spec in sorted((PROJECT / "specs").glob("SPC-*.md")):
        out |= set(ID.findall(field(front_matter(spec)[0], "states")))
    return out


def withdrawn() -> set:
    """Requirements withdrawn for a replacement, which no specification states."""
    out = set()
    for req in (PROJECT / "requirements").glob("REQ-*.md"):
        if field(front_matter(req)[0], "status").strip() == "withdrawn":
            out.add(req.name[:8])
    return out


def main():
    failures = []
    epics = sorted((PROJECT / "epics").glob("EPC-*.md"))
    tasks = sorted((PROJECT / "tasks").glob("TSK-*.md"))
    in_a_spec = stated() | withdrawn()

    if not epics:
        print("no epics, nothing to cover")
        return 0

    for epic in epics:
        block, body = front_matter(epic)
        epic_id = field(block, "id").strip()
        authorising = field(block, "realises").strip()
        records = list((PROJECT / "adrs").glob(f"{authorising}-*.md"))
        if not records:
            failures.append(f"{epic.name}: realises {authorising}, which is not a record")
            continue

        addressed = set(ID.findall(field(front_matter(records[0])[0], "addresses")))
        claimed = {}
        for task in tasks:
            t_block = front_matter(task)[0]
            if field(t_block, "epic").strip() != epic_id:
                continue
            for req in ID.findall(field(t_block, "closes")):
                claimed.setdefault(req, []).append(task.name)

        for req in sorted(addressed - set(claimed) - deferred(body, claimed)):
            failures.append(f"{epic_id}: {req} lands in no task")
        for req in sorted(addressed - in_a_spec):
            failures.append(f"{authorising}: {req} is stated in no specification")
        for req in sorted(set(claimed) - addressed):
            failures.append(f"{epic_id}: {req} is closed by a task and addressed by no decision")
        for req, where in sorted(claimed.items()):
            if len(where) > 1:
                failures.append(f"{epic_id}: {req} is claimed by {', '.join(where)}")

        covered = len(addressed & set(claimed))
        print(f"{epic_id}: {covered} of {len(addressed)} addressed requirements in tasks, "
              f"{len(addressed & deferred(body, claimed))} deferred with a reason")

    for line in failures:
        print(line)
    print(f"{len(failures)} coverage failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
