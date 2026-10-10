# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what `meow-unattended plan` prints in place of a command line (TSK-4120, SPC-1200).

Each fixture is a scratch git repository with its home and state isolated.
The launcher finds the shared binary through a data file, as an installed unit
does, so a stale build beside the unit is never the program under test.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
CORE = UNIT.parent / "meow-core"
BIN = UNIT / "bin" / "meow-unattended"
GIT = '[git]\ntrunk = "main"\n'
TABLE = '[unattended]\npermission_mode = "dontAsk"\ngates = ["review", "merge"]\nrelease = false\n'


def table(**keys):
    """An `[unattended]` table of the four keys, each overridden or, where None, left out."""
    values = {"permission_mode": '"dontAsk"', "gates": '["review", "merge"]', "release": "false",
              "amend_approved": None}
    values.update(keys)
    return "[unattended]\n" + "".join(f"{k} = {v}\n" for k, v in values.items() if v is not None)


class Posture(unittest.TestCase):
    def repo(self, profile):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name).resolve()
        self.root = base / "repo"
        data = base / "data"
        (data / "meow-core-test").mkdir(parents=True)
        (data / "meow-core-test" / "meow-root").write_text(f"{CORE}\n")
        self.env = {"PATH": os.environ["PATH"], "HOME": str(base / "home"), "MEOWPAW_STATE_DIR": str(base / "state"),
                    "CLAUDE_PLUGIN_DATA": str(data / "meow-unattended-test"), "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_NOSYSTEM": "1"}
        self.root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, env=self.env)
        if profile is not None:
            (self.root / ".meowpaw").mkdir()
            (self.root / ".meowpaw" / "profile.toml").write_text(profile)
        return self.root

    def plan(self, profile):
        self.repo(profile)
        done = subprocess.run([str(BIN), "plan"], cwd=self.root, capture_output=True, text=True, env=self.env,
                              stdin=subprocess.DEVNULL)
        return done.returncode, done.stdout + done.stderr

    def test_a_resolved_posture_prints_its_table_its_deny_rules_and_their_limits(self):
        """TSK-4120 criterion 1, REQ-2370, REQ-2388: exit 0, the table, the rules, the limits, no command line."""
        status, said = self.plan(GIT + table(amend_approved="false"))
        self.assertEqual(status, 0, said)
        for line in ('permission_mode = "dontAsk"', 'gates = ["review", "merge"]', "release = false",
                     "amend_approved = false", "deny rules:"):
            self.assertIn(line, said)
        self.assertIn(".meowpaw/**", said)
        self.assertIn("git push", said)
        self.assertIn("approved requirement or decision", said)
        self.assertIn("limits", said)
        self.assertNotIn("claude -p", said)
        self.assertNotIn("--max-budget-usd", said)
        self.assertNotIn("snapshot:", said)

    def test_a_release_of_false_is_printed_as_no_release(self):
        """TSK-4120 criterion 4, REQ-3722: the run releases nothing, and the plan says so."""
        status, said = self.plan(GIT + table(release="false"))
        self.assertEqual(status, 0, said)
        self.assertIn("the run releases nothing", said)

    def test_a_release_command_is_printed_as_the_one_command(self):
        """TSK-4120 criterion 4, REQ-3722: a release command is the one the run may run, once."""
        status, said = self.plan(GIT + table(release='"./scripts/release"'))
        self.assertEqual(status, 0, said)
        self.assertIn('release = "./scripts/release"', said)

    def test_each_refusal_is_reported_with_its_line_and_exit_status_3(self):
        """TSK-4120 criterion 2: one fixture for each line of SPC-1200's failure table."""
        cases = [
            (None, "unresolved: no [unattended] table in .meowpaw/profile.toml"),
            (GIT, "unresolved: no [unattended] table in .meowpaw/profile.toml"),
            ("[unattended\n", "unresolved: the profile doesn't parse:"),
            (GIT + table(permission_mode=None), "unresolved: [unattended] permission_mode is not declared"),
            (GIT + table(gates=None), "unresolved: [unattended] gates is not declared"),
            (GIT + table(release=None), "unresolved: [unattended] release is not declared"),
            (GIT + table(permission_mode='"bypassPermissions"'),
             "unresolved: [unattended] permission_mode bypassPermissions is refused"),
            (GIT + table(permission_mode='"manual"'), "unresolved: [unattended] permission_mode manual is refused"),
            (GIT + table(gates='["verify"]'),
             "unresolved: [unattended] gates names verify, which is not a gate"),
            (GIT + table(gates='"review"'), "unresolved: [unattended] gates review is not a list of strings"),
            (GIT + table(release="3"), "unresolved: [unattended] release 3 is not a command or false"),
            (GIT + table(amend_approved='"yes"'),
             "unresolved: [unattended] amend_approved yes is not true or false"),
            (table(), "unresolved: [git] trunk is not declared, so the push rule has no trunk"),
        ]
        for profile, expected in cases:
            with self.subTest(expected=expected):
                status, said = self.plan(profile)
                self.assertEqual(status, 3, said)
                self.assertEqual(said.count(expected), 1, said)

    def test_every_refusal_is_reported_in_one_run(self):
        """TSK-4120 criterion 2: one run names every key a repository has to fix."""
        status, said = self.plan("[unattended]\n")
        self.assertEqual(status, 3, said)
        for key in ("permission_mode", "gates", "release"):
            self.assertIn(f"unresolved: [unattended] {key} is not declared", said)


if __name__ == "__main__":
    unittest.main()
