# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that this repository's record carries none of the old chain's
sections or fields, as TSK-3860 asks (REQ-3652, ADR-2300)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD = re.compile(r"^## (?:Cover|Verified|Open review findings)\s*$|^checked-at:")
FENCE = re.compile(r"^\s*(```|~~~)")


class MigratedRecord(unittest.TestCase):
    def test_no_record_carries_an_old_section_or_checked_at(self):
        """TSK-3860 criterion 1: no line of a record opens `## Cover`, `## Verified`, `## Open review findings` or
        `checked-at:`, outside fenced code."""
        found = []
        for path in sorted((ROOT / "project").rglob("*.md")):
            fenced = False
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if FENCE.match(line):
                    fenced = not fenced
                elif not fenced and OLD.match(line):
                    found.append(f"{path.relative_to(ROOT)}:{number}")
        self.assertEqual(found[:20], [], f"{len(found)} lines in all")


if __name__ == "__main__":
    unittest.main()
