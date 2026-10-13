# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that no unit keeps a copy of its material for a second agent
(TSK-4600, ADR-2500, REQ-1490, REQ-1492)."""

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# A port to another agent adds its platform files outside `plugins/<unit>/`,
# and only by a new decision (ADR-2500).
OTHER_AGENTS = {"codex", "cursor", "gemini", "copilot", "aider", "agents.md"}


def foreign_paths(paths):
    """The paths with a directory or file named for an agent other than Claude Code, without regard to case."""
    found = []
    for path in paths:
        for part in Path(path).parts:
            if part.lower() in OTHER_AGENTS or Path(part).stem.lower() in OTHER_AGENTS:
                found.append(path)
                break
    return sorted(found)


class AgentNeutral(unittest.TestCase):
    def test_a_name_of_another_agent_is_found_whatever_its_case_or_kind(self):
        """TSK-4600 criterion 4: a directory, a file and a differently cased file each fail the check."""
        paths = ["plugins/u/codex/skill.md", "plugins/u/AGENTS.md", "plugins/u/Cursor.json", "plugins/u/skills/a.md"]
        self.assertEqual(foreign_paths(paths), ["plugins/u/AGENTS.md", "plugins/u/Cursor.json", "plugins/u/codex/skill.md"])

    def test_no_unit_holds_a_file_named_for_another_agent(self):
        """TSK-4600 criterion 4 (REQ-1490, REQ-1492): every tracked path under `plugins/` is neutral."""
        tracked = subprocess.run(["git", "ls-files", "--", "plugins"], cwd=ROOT, capture_output=True,
                                 text=True, check=True).stdout.splitlines()
        self.assertTrue(tracked, "git lists no file under plugins/, so the check read nothing")
        self.assertEqual(foreign_paths(tracked), [])


if __name__ == "__main__":
    unittest.main()
