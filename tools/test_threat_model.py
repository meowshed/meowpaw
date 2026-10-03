# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Holds SPC-1080's "The threat model" to the form ADR-2470 sets, as TSK-4380 asks: STRIDE's six categories each
mapped, an accident by the harness first, every trust boundary listed and every threat ranked in words."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECIFICATION = next((ROOT / "project" / "specs").glob("SPC-1080-*.md"))
HEADING = "### The threat model"
STRIDE = ("Spoofing", "Tampering", "Repudiation", "Information disclosure", "Denial of service",
          "Elevation of privilege")


def section(text):
    """The section under the heading, up to the next heading of the same level or above, read by its heading so
    the fixtures fail when it moves or is renamed."""
    lines = text.splitlines()
    start = lines.index(HEADING)
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"#{1,3} ", lines[i])), len(lines))
    return "\n".join(lines[start + 1:end])


def tables(text):
    """Each Markdown table in the text, as a list of rows keyed by the header's cells."""
    found, block = [], []
    for line in text.splitlines() + [""]:
        if line.startswith("|"):
            block.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        elif block:
            header, rows = block[0], [row for row in block[1:] if not set("".join(row)) <= set("-: ")]
            found.append([dict(zip(header, row)) for row in rows])
            block = []
    return found


def table_with(text, column):
    """The one table whose header names the column."""
    matching = [table for table in tables(text) if table and column in table[0]]
    if len(matching) != 1:
        raise AssertionError(f"{len(matching)} tables have a {column} column, not one")
    return matching[0]


PLACEHOLDER = re.compile(r"^(?:|tbd|todo|na)$")
RANK = {"likely": 1, "unlikely": 0, "severe": 1, "minor": 0}
# The insiders ADR-2470 names: the harness itself, and the person's own session.
INSIDER = re.compile(r"^The (?:harness|person's own session) ")
BOUNDARIES = {
    "a repository's files": r"\brepository\b",
    "a tracker's issue text": r"\btracker\b.*\bissue\b",
    "a pull request comment": r"\bpull request comment\b",
    "a tool's output": r"\btool's output\b",
}


def placeholder(cell):
    """Whether a cell holds nothing but a placeholder, read with its punctuation and dashes dropped."""
    return bool(PLACEHOLDER.match(re.sub(r"[\W_]+", "", cell).lower()))


def stride_gaps(text):
    """Each STRIDE category the section's category table leaves out or maps to nothing but a placeholder."""
    controls = {row["Category"]: row.get("Control", "") for row in table_with(text, "Category")}
    return [name for name in STRIDE if placeholder(controls.get(name, ""))]


class ThreatModel(unittest.TestCase):
    def setUp(self):
        self.text = section(SPECIFICATION.read_text(encoding="utf-8"))

    def test_each_stride_category_is_mapped(self):
        """TSK-4380 criterion 1, REQ-2786: the section names STRIDE's six categories, each with a control or
        `None`."""
        self.assertEqual(stride_gaps(self.text), [])

    def test_a_category_removed_is_found(self):
        """TSK-4380 criterion 1, REQ-2786: the fixture fails against a copy with one category removed, so it can
        fail at all."""
        copy = "\n".join(line for line in self.text.splitlines() if not line.startswith("| Repudiation "))
        self.assertEqual(stride_gaps(copy), ["Repudiation"])
        placeholder = re.sub(r"^(\| Tampering +\|).*$", r"\1 TBD |", self.text, flags=re.MULTILINE)
        self.assertEqual(stride_gaps(placeholder), ["Tampering"])

    def test_the_first_ranked_threat_is_an_accident_by_the_harness(self):
        """TSK-4380 criterion 2, REQ-2784, REQ-2792: the first threat ranked names the harness as its actor, no
        threat below it ranks higher, and the insiders' threats come before every other."""
        threats = table_with(self.text, "Likelihood")
        self.assertGreater(len(threats), 0, "the threat table has no rows")
        self.assertRegex(threats[0]["Threat"], r"^The harness ")
        rank = [(RANK[row["Likelihood"]], RANK[row["Impact"]]) for row in threats]
        self.assertEqual([row["Threat"] for row, r in zip(threats, rank) if r > rank[0]], [])
        insiders = [bool(INSIDER.match(row["Threat"])) for row in threats]
        self.assertEqual(insiders, sorted(insiders, reverse=True), "an insider's threat follows an attacker's")

    def test_the_trust_boundaries_are_listed(self):
        """TSK-4380 criterion 3, REQ-2788: the section holds a table of the boundaries where data changes trust
        level, each saying what crosses it, and the four ADR-2470 names are among them."""
        boundaries = table_with(self.text, "Boundary")
        self.assertGreater(len(boundaries), 0, "the boundary table has no rows")
        for row in boundaries:
            with self.subTest(boundary=row["Boundary"]):
                self.assertFalse(placeholder(row["Boundary"]) or placeholder(row.get("What crosses it", "")))
        rows = [f"{row['Boundary']} {row.get('What crosses it', '')}" for row in boundaries]
        for name, pattern in BOUNDARIES.items():
            with self.subTest(boundary=name):
                self.assertTrue(any(re.search(pattern, row, re.IGNORECASE) for row in rows), name)

    def test_each_threat_is_ranked_in_words(self):
        """TSK-4380 criterion 3, REQ-2790: each threat's likelihood is likely or unlikely and its impact severe or
        minor, which leaves no room for a digit in either column."""
        threats = table_with(self.text, "Likelihood")
        self.assertGreater(len(threats), 0, "the threat table has no rows")
        for row in threats:
            with self.subTest(threat=row["Threat"]):
                self.assertIn(row["Likelihood"], ("likely", "unlikely"))
                self.assertIn(row["Impact"], ("severe", "minor"))


if __name__ == "__main__":
    unittest.main()
