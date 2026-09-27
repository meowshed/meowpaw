# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for check_standalone: each unit stands alone (ADR-1270)."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_standalone import findings  # noqa: E402


class Standalone(unittest.TestCase):
    def plugins(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "plugins"
        for name, text in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    def test_a_path_inside_the_unit_passes(self):
        root = self.plugins({
            "meow-a/hooks/hooks.json": '{"command": "${CLAUDE_PLUGIN_ROOT}/bin/meow-a"}',
            "meow-a/skills/run/SKILL.md": "Run `${CLAUDE_SKILL_DIR}/../../bin/meow-a status`. Install meow-b for more.",
        })
        self.assertEqual(findings(root), ([], 2))

    def test_a_path_climbing_out_of_the_unit_is_reported(self):
        root = self.plugins({"meow-a/skills/run/SKILL.md": "Run `${CLAUDE_SKILL_DIR}/../../../meow-b/bin/meow-b`."})
        out, _ = findings(root)
        self.assertIn("plugins/meow-a/skills/run/SKILL.md:1: reaches outside meow-a: ${CLAUDE_SKILL_DIR}/../../../meow-b/bin/meow-b", out)

    def test_a_path_into_another_unit_is_reported(self):
        root = self.plugins({"meow-a/bin/meow-a": "exec plugins/meow-b/bin/meow-b\n"})
        out, _ = findings(root)
        self.assertEqual(out, ["plugins/meow-a/bin/meow-a:1: runs a file of meow-b, another unit"])

    def test_a_link_to_another_units_page_runs_nothing(self):
        """REQ-0012: a page linking another unit's page by address depends on nothing it runs."""
        root = self.plugins({"meow-a/README.md": "See [its page](https://example.org/blob/main/plugins/meow-b/README.md).\n"})
        self.assertEqual(findings(root), ([], 1))

    def test_fixtures_are_not_shipped_behaviour(self):
        root = self.plugins({"meow-a/tests/test_a.py": "PATH = 'plugins/meow-b/'\n",
                             "meow-a/bin/meow-a": "exec plugins/meow-b/bin/meow-b\n"})
        self.assertEqual(findings(root), (["plugins/meow-a/bin/meow-a:1: runs a file of meow-b, another unit"], 1))


if __name__ == "__main__":
    unittest.main()
