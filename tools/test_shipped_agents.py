# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Each agent the harness ships declares the values SPC-1030's table gives it
(ADR-1700, REQ-2974, REQ-2982, REQ-2984, REQ-2988, REQ-3270).

`meow-author check` reads whether a field is present and holds an accepted
value. It can't read whether `omitClaudeMd` or `skills` is the value decided
for that agent, because the decision lives in the specification, so this
check compares the two and a flipped value fails it.
"""

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = next((ROOT / "project" / "specs").glob("SPC-1030-*.md"))
FIELDS = ("maxTurns", "model", "effort", "omitClaudeMd", "skills", "tools")


def listed(value):
    """A list or a comma-separated string as a tuple of names."""
    return tuple(n.strip() for n in value.strip().strip("[]").split(",") if n.strip())


def normal(field, value):
    value = value.strip().strip("`").strip()
    return listed(value) if field in ("skills", "tools") else value


def table():
    """The rows under "What an agent declares" naming each shipped agent."""
    text = SPEC.read_text(encoding="utf-8")
    section = text.split("### What an agent declares", 1)[1].split("\n### ", 1)[0]
    rows, header = {}, None
    for line in section.splitlines():
        if not line.startswith("|"):
            header = None if not line.strip() else header
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "Agent":
            header = [c.strip("`") for c in cells]
        elif header and not set(cells[0]) <= set("-: "):
            rows[cells[0].strip("`")] = {h: normal(h, c) for h, c in zip(header[1:], cells[1:])}
    return rows


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    block = text.split("---\n", 2)[1]
    return {k.strip(): v for k, _, v in (line.partition(":") for line in block.splitlines() if ":" in line)}


def shipped():
    """Each agent under a plugin's `agents/`, as `plugin:name`."""
    found = {}
    for path in sorted(ROOT.glob("plugins/*/agents/*.md")):
        fields = front_matter(path)
        found[f"{path.parent.parent.name}:{fields['name'].strip()}"] = fields
    return found


def mismatches(row, fields):
    """Each field whose declared value differs from the table's."""
    return [f for f in FIELDS if f not in fields or normal(f, fields[f]) != row[f]]


class ShippedAgents(unittest.TestCase):
    def test_the_table_names_every_field(self):
        for name, row in table().items():
            with self.subTest(agent=name):
                self.assertEqual(set(row), set(FIELDS))

    def test_every_shipped_agent_has_its_row(self):
        self.assertEqual(sorted(shipped()), sorted(table()),
                         "every agent under plugins/*/agents/ has one row in SPC-1030's table, and no row names another")

    def test_each_shipped_agent_declares_its_row(self):
        rows = table()
        for name, fields in shipped().items():
            with self.subTest(agent=name):
                self.assertIn(name, rows)
                self.assertEqual(mismatches(rows[name], fields), [])

    def test_a_flipped_value_is_a_mismatch(self):
        """The comparison can fail: flipping omitClaudeMd or emptying skills in a copy of each agent is caught."""
        rows = table()
        for name, fields in shipped().items():
            with self.subTest(agent=name):
                flipped = dict(fields, omitClaudeMd="true" if rows[name]["omitClaudeMd"] == "false" else "false")
                self.assertIn("omitClaudeMd", mismatches(rows[name], flipped))
                other = "[]" if rows[name]["skills"] else "[meow-prose:writing]"
                self.assertIn("skills", mismatches(rows[name], dict(fields, skills=other)))


OUTCOMES = ("DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED")


def named_outcomes(path):
    """The outcome words an agent's body names, each read as a whole word so DONE_WITH_CONCERNS isn't DONE."""
    body = path.read_text(encoding="utf-8").split("---\n", 2)[2]
    return {w for w in OUTCOMES if re.search(rf"(?<![A-Z_]){w}(?![A-Z_])", body)}


class ShippedOutcomes(unittest.TestCase):
    """TSK-2702 criterion 2, REQ-0816, SPC-1030 "What an agent reports": the three shipped agents name the four
    outcomes, and `meow-author check` passes over the repository's units with its outcome rule in force."""

    def test_the_three_shipped_agents_name_the_four_outcomes(self):
        paths = sorted(ROOT.glob("plugins/*/agents/*.md"))
        self.assertEqual(sorted(f"{p.parent.parent.name}:{p.stem}" for p in paths),
                         ["meow-flow:record-reviewer", "meow-flow:router", "meow-prose:prose"])
        for path in paths:
            with self.subTest(agent=str(path.relative_to(ROOT))):
                self.assertEqual(named_outcomes(path), set(OUTCOMES))

    def test_the_check_passes_over_the_units(self):
        done = subprocess.run([str(ROOT / "plugins" / "meow-author" / "bin" / "meow-author"), "check"],
                              cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn(" 0 authoring failures", done.stdout)


if __name__ == "__main__":
    unittest.main()
