# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for the kernel check: the kernel names no unit outside it (REQ-0077, ADR-1060)."""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_kernel  # noqa: E402


class Kernel(unittest.TestCase):
    def plugins(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "plugins"
        (root / "meow-a").mkdir(parents=True)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content if isinstance(content, bytes) else content.encode())
        return root

    def run_check(self, plugins):
        out = io.StringIO()
        with redirect_stdout(out):
            status = check_kernel.main(plugins)
        return status, out.getvalue()

    def test_a_binary_the_core_unit_ships_is_not_read_as_text(self):
        """TSK-5300, REQ-4500: the shared binary sits in the kernel unit and is build output, not shipped text."""
        plugins = self.plugins({"meow-core/README.md": "The kernel.\n",
                                "meow-core/bin/x86_64-unknown-linux-musl/meow": b"\xcf\xfa\xed\xfe\x00meow-a\x00"})
        status, said = self.run_check(plugins)
        self.assertEqual(status, 0, said)
        self.assertIn("1 kernel files, 0 names outside the kernel", said)

    def test_a_text_file_naming_another_unit_is_still_reported(self):
        """REQ-0077: the check still fails where the kernel's text names a unit outside it."""
        plugins = self.plugins({"meow-core/README.md": "Install meow-a for more.\n"})
        status, said = self.run_check(plugins)
        self.assertEqual(status, 1, said)
        self.assertIn("meow-core/README.md:1: names meow-a, outside the kernel", said)


if __name__ == "__main__":
    unittest.main()
