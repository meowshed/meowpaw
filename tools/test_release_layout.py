# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The build and the release put one binary in the core unit and none in the others (TSK-5302, REQ-4500)."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ReleaseLayout(unittest.TestCase):
    def test_build_units_builds_only_the_core_unit(self):
        """TSK-5302 criterion 2, REQ-4500: the build script has no loop over the units' own builds."""
        text = (ROOT / "crates/meow/build-units").read_text()
        self.assertNotIn("for pair in", text)
        self.assertIn('plugins/meow-core/bin/$target', text)
        self.assertNotIn('plugins/$unit/bin', text)

    def test_the_workflows_upload_what_the_build_wrote_beside_the_core_unit_only(self):
        """TSK-5302 criterion 1, REQ-4500: the binary artifact path is a glob that the build fills for one unit."""
        text = (ROOT / ".github/workflows/rust-tool.yml").read_text()
        self.assertIn("path: plugins/*/bin/${{ matrix.target }}/", text)


if __name__ == "__main__":
    unittest.main()
