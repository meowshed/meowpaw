# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that this repository keeps no run output, as TSK-3830 asks
(REQ-3614, ADR-2300)."""

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class NoKeptEvidence(unittest.TestCase):
    def test_the_record_holds_no_evidence_directory(self):
        """TSK-3830 criterion 1: `project/evidence` doesn't exist."""
        self.assertFalse((ROOT / "project" / "evidence").exists())

    def test_git_tracks_no_kept_run(self):
        """TSK-3830 criterion 1: no tracked file sits under `project/evidence`, so a deleted directory stays deleted."""
        tracked = subprocess.run(["git", "ls-files", "--", "project/evidence"], cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(tracked.stdout, "")


if __name__ == "__main__":
    unittest.main()
