# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for a run that lives in the session, which SPC-1201 states (EPC-2300).

Each fixture is a scratch git repository with its home and its state directory
isolated. The hooks are driven the way Claude Code drives them: one JSON object
on standard input, one JSON object on standard output. The launcher finds the
shared binary through a data file, as an installed unit does, so a stale build
beside the unit is never the program under test.
"""

import json
import os
import platform
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
CORE = UNIT.parent / "meow-core"
BIN = UNIT / "bin" / "meow-loop"
SESSION = "11111111-1111-4111-8111-111111111111"
START = "/meow-loop:run --iterations 3 --hours 1 --tokens 100000"
DEPRECATION = "meow-loop start is deprecated: a run now lives in the session, so type /meow-loop:run there"
PROFILE = '[git]\ntrunk = "main"\n'


def front(**fields):
    return "\n".join(["---"] + [f"{key}: {value}" for key, value in fields.items()] + ["---", ""])


def requirement(id, status="approved"):
    return (front(id=id, artifact="requirement", topic="loop", **{"class": "functional"}, status=status,
                  revised="2026-01-01", elaborates="RES-0001", verification="static")
            + f"\n# {id}\n\nThe run MUST stop.\n")


class Session(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.repo = base / "repo"
        self.state = base / "state"
        self.home = base / "home"
        data = base / "data"
        self.home.mkdir()
        (data / "meow-core-test").mkdir(parents=True)
        (data / "meow-core-test" / "meow-root").write_text(f"{CORE}\n")
        self.env = {"PATH": os.environ["PATH"], "HOME": str(self.home), "MEOWPAW_STATE_DIR": str(self.state),
                    "CLAUDE_PLUGIN_DATA": str(data / "meow-loop-test"), "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.write(".meowpaw/profile.toml", PROFILE)
        self.write("project/requirements/REQ-0001-a-duty.md", requirement("REQ-0001"))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, text=True, env=self.env)

    def write(self, name, text):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def hook(self, sub, event, **env):
        """Runs `meow-loop <sub>` with the event on standard input; returns the process and its parsed answer."""
        done = subprocess.run([str(BIN), sub], input=json.dumps(event), cwd=self.repo, capture_output=True,
                              text=True, env={**self.env, **env})
        answer = json.loads(done.stdout) if done.stdout.strip().startswith("{") else {}
        return done, answer

    def prompt(self, text, session=SESSION, mode="dontAsk"):
        return self.hook("prompt", {"hook_event_name": "UserPromptSubmit", "session_id": session,
                                    "prompt": text, "cwd": str(self.repo), "permission_mode": mode})

    def runs(self):
        return sorted(self.state.glob("**/runs/*/*/run.toml"))

    def run_toml(self):
        found = self.runs()
        self.assertEqual(len(found), 1, found)
        return tomllib.loads(found[0].read_text()), found[0].parent

    def start(self):
        done, answer = self.prompt(START)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return answer


class Starting(Session):
    def test_the_start_command_writes_a_run_with_its_bounds(self):
        """TSK-4100 criterion 1, REQ-3700, REQ-0872: a run directory holds the session id and the three bounds."""
        answer = self.start()
        table, directory = self.run_toml()
        self.assertEqual(table["session_id"], SESSION)
        self.assertEqual((table["iterations"], table["hours"], table["tokens"]), (3, 1, 100000))
        self.assertEqual(table["started_by"], "person")
        self.assertEqual((directory / "progress" / "progress.md").read_text(), "")
        context = answer["hookSpecificOutput"]["additionalContext"]
        self.assertIn(directory.name, context)
        self.assertEqual(answer["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")

    def test_a_missing_or_bad_bound_writes_nothing_and_names_each(self):
        """TSK-4100 criterion 2, REQ-0872: each bound that is missing or not above zero is named."""
        done, answer = self.prompt("/meow-loop:run --iterations 0 --tokens 5")
        self.assertEqual(self.runs(), [])
        message = answer["systemMessage"]
        self.assertIn("unresolved: --iterations 0 is not a number above 0", message)
        self.assertIn("unresolved: /meow-loop:run needs --hours", message)

    def test_a_second_start_in_the_same_session_is_refused(self):
        """TSK-4100, SPC-1201 failure paths: a run already holds this work tree."""
        self.start()
        done, answer = self.prompt(START)
        self.assertIn("unresolved: a run already holds this work tree", answer["systemMessage"])
        self.assertEqual(len(self.runs()), 1)

    def test_an_ordinary_prompt_starts_nothing(self):
        """TSK-4100: a prompt that isn't the start command is let through and writes no run."""
        done, answer = self.prompt("fix the typo in the readme")
        self.assertEqual(done.returncode, 0)
        self.assertEqual(self.runs(), [])
        self.assertNotIn("decision", answer)

    def test_twenty_one_runs_leave_twenty_and_purge_removes_them_all(self):
        """TSK-4100 criterion 6, REQ-2962: the newest 20 are kept, and purge removes every one."""
        self.start()
        _, first = self.run_toml()
        parent = first.parent
        for n in range(1, 21):
            old = parent / f"{n:020d}"
            old.mkdir()
            (old / "run.toml").write_text('session_id = "old"\nending = "finished"\n')
        self.assertEqual(len(list(parent.glob("*/run.toml"))), 21)
        done, _ = self.prompt(START, session="22222222-2222-4222-8222-222222222222")
        self.assertEqual(len(list(parent.glob("*/run.toml"))), 20, done.stdout)
        purge = subprocess.run([str(BIN), "purge"], cwd=self.repo, capture_output=True, text=True, env=self.env)
        self.assertEqual(purge.returncode, 0, purge.stdout + purge.stderr)
        self.assertEqual(list(parent.glob("*/run.toml")), [])


class Cancelling(Session):
    def test_the_next_prompt_cancels_an_active_run(self):
        """TSK-4100 criterion 3, REQ-3712, REQ-0890: any later prompt ends the run `cancelled` by the person."""
        self.start()
        done, answer = self.prompt("stop, I want to look at it")
        self.assertEqual(done.returncode, 0)
        table, _ = self.run_toml()
        self.assertEqual(table["ending"], "cancelled")
        self.assertEqual(table["cancelled_by"], "person")
        self.assertIn("ended_at", table)
        self.assertNotIn("decision", answer)


class Guarding(Session):
    def guard(self, tool, **tool_input):
        done, answer = self.hook("guard", {"hook_event_name": "PreToolUse", "session_id": SESSION,
                                           "tool_name": tool, "tool_input": tool_input, "cwd": str(self.repo)})
        return answer.get("hookSpecificOutput", {}).get("permissionDecision")

    def test_the_guard_denies_the_runs_terms_and_its_own_command_and_allows_its_notes(self):
        """TSK-4100 criterion 4, REQ-0874, REQ-2660: run.toml and a meow-loop command are denied while active."""
        self.start()
        _, directory = self.run_toml()
        self.assertEqual(self.guard("Edit", file_path=str(directory / "run.toml")), "deny")
        self.assertEqual(self.guard("Bash", command="meow-loop stop"), "deny")
        self.assertIsNone(self.guard("Edit", file_path=str(directory / "progress" / "progress.md")))
        self.assertIsNone(self.guard("Write", file_path=str(directory / "report.md")))


class Skill(unittest.TestCase):
    def test_the_start_command_cannot_be_invoked_by_the_model(self):
        """TSK-4100 criterion 5, REQ-0894: the skill sets `disable-model-invocation: true`."""
        text = (UNIT / "skills" / "run" / "SKILL.md").read_text()
        header = text.split("---")[1]
        self.assertRegex(header, r"(?m)^disable-model-invocation:\s*true\s*$")
        self.assertRegex(header, r"(?m)^name:\s*run\s*$")


class Deprecated(Session):
    def test_the_terminal_runner_says_it_is_deprecated_first(self):
        """TSK-4100 criterion 7: the first line `start` prints is the deprecation line."""
        done = subprocess.run([str(BIN), "start"], cwd=self.repo, capture_output=True, text=True, env=self.env)
        self.assertEqual(done.stdout.splitlines()[0], DEPRECATION, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
