# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that every unit installs by the platform's own commands with no input,
in a scratch configuration directory, and that the test says so where it can't
run (TSK-4600, ADR-2500, REQ-1486)."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin/marketplace.json"
CALL_TIMEOUT = 300


def units():
    """The names the marketplace lists, which is what a provisioning script installs."""
    return [p["name"] for p in json.loads(MARKETPLACE.read_text())["plugins"]]


def missing_units(wanted, listed):
    """The units in `wanted` that the platform's listing doesn't show enabled."""
    enabled = {p["id"].split("@")[0] for p in listed if p.get("enabled")}
    return sorted(set(wanted) - enabled)


class Listing(unittest.TestCase):
    def test_a_unit_left_out_of_the_install_is_reported_missing(self):
        """TSK-4600 criterion 1 (REQ-1486): a unit the listing lacks, or shows disabled, fails the comparison."""
        listed = [{"id": "meow-core@meowpaw", "enabled": True}, {"id": "meow-git@meowpaw", "enabled": False}]
        self.assertEqual(missing_units(["meow-core", "meow-git", "meow-scm"], listed), ["meow-git", "meow-scm"])

    def test_a_complete_listing_reports_nothing_missing(self):
        """TSK-4600 criterion 1 (REQ-1486): every unit enabled leaves nothing to report."""
        listed = [{"id": f"{u}@meowpaw", "enabled": True} for u in ("meow-core", "meow-git")]
        self.assertEqual(missing_units(["meow-core", "meow-git"], listed), [])


@unittest.skipUnless(shutil.which("claude"), "no `claude` command on the path")
class UnattendedInstall(unittest.TestCase):
    def run_claude(self, *args):
        return subprocess.run(["claude", "plugin", *args], env=self.env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=CALL_TIMEOUT)

    def test_every_unit_installs_with_no_input_and_is_listed_enabled(self):
        """TSK-4600 criterion 1 (REQ-1486): add the checkout's marketplace, install each unit, read the platform's listing."""
        with tempfile.TemporaryDirectory() as config:
            self.env = {**os.environ, "CLAUDE_CONFIG_DIR": config}
            added = self.run_claude("marketplace", "add", str(ROOT), "--json")
            self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
            for unit in units():
                done = self.run_claude("install", f"{unit}@meowpaw", "--json")
                self.assertEqual(done.returncode, 0, f"{unit}: {done.stdout}{done.stderr}")
            listing = self.run_claude("list", "--json")
            self.assertEqual(listing.returncode, 0, listing.stderr)
            self.assertEqual(missing_units(units(), json.loads(listing.stdout)), [])


class WithoutThePlatform(unittest.TestCase):
    def test_the_install_test_is_skipped_and_never_passed_where_claude_is_absent(self):
        """TSK-4600 criterion 2: run the install test with a path that holds no `claude` command."""
        with tempfile.TemporaryDirectory() as empty:
            ran = subprocess.run(
                [sys.executable, "-m", "unittest", "-v", "test_unattended_install.UnattendedInstall"],
                cwd=ROOT / "tools", env={**os.environ, "PATH": empty}, capture_output=True, text=True, timeout=60)
        output = ran.stdout + ran.stderr
        self.assertEqual(ran.returncode, 0, output)
        self.assertIn("skipped 'no `claude` command on the path'", output)
        self.assertNotIn("... ok", output)


class Wiring(unittest.TestCase):
    def test_the_test_stage_runs_both_tests(self):
        """TSK-4600 (REQ-1486, REQ-1492): `mise.toml`'s `test-tools` names the install test and the agent-neutral test."""
        with open(ROOT / "mise.toml", "rb") as handle:
            run = tomllib.load(handle)["tasks"]["test-tools"]["run"]
        for name in ("tools/test_unattended_install.py", "tools/test_agent_neutral.py"):
            self.assertIn(name, run)


if __name__ == "__main__":
    unittest.main()
