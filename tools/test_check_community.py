# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for check_community: the six community files sit under `.github/` (ADR-2510)."""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_community import main  # noqa: E402

FILES = {
    ".github/CONTRIBUTING.md": ".github/CONTRIBUTING.md",
    ".github/SECURITY.md": ".github/SECURITY.md",
    ".github/CODE_OF_CONDUCT.md": ".github/CODE_OF_CONDUCT.md",
    ".github/CODEOWNERS": ".github/CODEOWNERS",
    ".github/ISSUE_TEMPLATE/defect.md": ".github/ISSUE_TEMPLATE/",
    ".github/pull_request_template.md": ".github/pull_request_template.md",
}


class Community(unittest.TestCase):
    def tree(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for name in files:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("text\n", encoding="utf-8")
        return root

    def run_check(self, root):
        out = io.StringIO()
        with redirect_stdout(out):
            status = main(root)
        return status, out.getvalue().splitlines()

    def test_all_six_files_pass(self):
        """REQ-2214, REQ-2216: a tree carrying all six under .github/ passes."""
        status, out = self.run_check(self.tree(FILES))
        self.assertEqual(status, 0, out)
        self.assertEqual(out, ["6 community files, 0 missing from .github/"])

    def test_each_missing_file_fails_naming_it(self):
        """REQ-2214, REQ-2216: removing any one of the six fails, naming that file."""
        for removed, named in FILES.items():
            with self.subTest(removed=removed):
                status, out = self.run_check(self.tree(f for f in FILES if f != removed))
                self.assertEqual(status, 1, out)
                self.assertEqual(out, [f"missing: {named}", "6 community files, 1 missing from .github/"])

    def test_a_file_at_the_root_counts_as_missing(self):
        """REQ-2216: CONTRIBUTING.md at the root is not where the code host looks."""
        files = [f for f in FILES if f != ".github/CONTRIBUTING.md"] + ["CONTRIBUTING.md"]
        status, out = self.run_check(self.tree(files))
        self.assertEqual(status, 1, out)
        self.assertEqual(out, ["missing: .github/CONTRIBUTING.md", "6 community files, 1 missing from .github/"])

    def test_an_empty_issue_template_directory_counts_as_missing(self):
        """REQ-2214: a directory holding no template is no issue template."""
        root = self.tree(f for f in FILES if "ISSUE_TEMPLATE" not in f)
        (root / ".github/ISSUE_TEMPLATE").mkdir()
        status, out = self.run_check(root)
        self.assertEqual(status, 1, out)
        self.assertEqual(out, ["missing: .github/ISSUE_TEMPLATE/", "6 community files, 1 missing from .github/"])

    def test_a_chooser_configuration_alone_is_no_issue_template(self):
        """REQ-2214: ISSUE_TEMPLATE/config.yml configures GitHub's chooser and is no template."""
        files = [f for f in FILES if "ISSUE_TEMPLATE" not in f] + [".github/ISSUE_TEMPLATE/config.yml"]
        status, out = self.run_check(self.tree(files))
        self.assertEqual(status, 1, out)
        self.assertEqual(out, ["missing: .github/ISSUE_TEMPLATE/", "6 community files, 1 missing from .github/"])

    def test_a_file_that_is_no_template_counts_as_missing(self):
        """REQ-2214: a .gitkeep keeping the directory in git is no issue template."""
        files = [f for f in FILES if "ISSUE_TEMPLATE" not in f] + [".github/ISSUE_TEMPLATE/.gitkeep"]
        status, out = self.run_check(self.tree(files))
        self.assertEqual(status, 1, out)
        self.assertEqual(out, ["missing: .github/ISSUE_TEMPLATE/", "6 community files, 1 missing from .github/"])


if __name__ == "__main__":
    unittest.main()
