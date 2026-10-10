# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The `task` record type says a task is a group of commits in its epic's pull request (TSK-5360, REQ-4400)."""

import re
import unittest
from pathlib import Path

TYPE = Path(__file__).resolve().parent.parent / "skills" / "writing" / "types" / "record" / "task.md"
OPENING = re.sub(r"\s+", " ", TYPE.read_text(encoding="utf-8"))[:400]


class TaskType(unittest.TestCase):
    def test_a_task_has_no_branch_or_review_of_its_own(self):
        """TSK-5360 criterion 3, REQ-4400."""
        self.assertRegex(OPENING, r"epic or defect")
        self.assertRegex(OPENING, r"pull request")
        self.assertNotRegex(OPENING, r"one branch|one review|its own pull request")


if __name__ == "__main__":
    unittest.main()
