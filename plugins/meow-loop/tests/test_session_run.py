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
POSTURE = '[unattended]\npermission_mode = "dontAsk"\ngates = []\nrelease = false\n'
PROFILE = '[git]\ntrunk = "main"\n\n' + POSTURE


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


class Stopping(Session):
    FROZEN = ("meow-loop run {id}: run /meow-flow:run once and carry the chain to its next stop. Read {progress} "
              "first and update it before you finish. The record decides when this run ends; you don't.")

    def transcript(self, *usages):
        path = Path(self.tmp.name) / "transcript.jsonl"
        lines = [json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": i, "output_tokens": o}}})
                 for i, o in usages]
        path.write_text("\n".join(lines) + "\n")
        return str(path)

    def stop(self, *usages, session=SESSION):
        return self.hook("stop", {"hook_event_name": "Stop", "session_id": session, "cwd": str(self.repo),
                                  "transcript_path": self.transcript(*(usages or [(10, 5)])),
                                  "stop_hook_active": False})

    def change_tree(self, text="x"):
        self.write("work.txt", text + "\n")

    def log(self):
        _, directory = self.run_toml()
        path = directory / "log.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_an_open_record_blocks_the_stop_with_the_same_frozen_prompt(self):
        """TSK-4110 criterion 1, REQ-3702, REQ-0870: two iterations get the same bytes naming the run."""
        self.prompt("/meow-loop:run --iterations 5 --hours 1 --tokens 100000")
        table, directory = self.run_toml()
        expected = self.FROZEN.format(id=directory.name, progress=directory / "progress" / "progress.md")
        self.change_tree("one")
        done, first = self.stop()
        self.change_tree("two")
        done, second = self.stop()
        self.assertEqual(first.get("decision"), "block", done.stdout + done.stderr)
        self.assertEqual(first["reason"], expected)
        self.assertEqual(second["reason"], expected)

    def test_a_record_with_nothing_open_ends_the_run_finished(self):
        """TSK-4110 criterion 2, REQ-3704, REQ-3706, REQ-0884: a postponed requirement doesn't keep a run open."""
        self.start()
        (self.repo / "project/requirements/REQ-0001-a-duty.md").unlink()
        self.write("project/requirements/REQ-0002-a-later-duty.md", requirement("REQ-0002"))
        self.write("project/adrs/ADR-0001-postpone.md", front(
            id="ADR-0001", artifact="adr", status="approved", revised="2026-01-01", addresses="[]",
            postpones="[REQ-0002]") + "\n# 1. Postpone it\n")
        done, answer = self.stop()
        self.assertNotEqual(answer.get("decision"), "block", done.stdout)
        table, _ = self.run_toml()
        self.assertEqual(table["ending"], "finished")

    def test_each_bound_ends_the_run_with_its_own_ending(self):
        """TSK-4110 criterion 3, REQ-3708, REQ-0876, REQ-0878: ceiling, time and tokens."""
        cases = {
            "ceiling": ("/meow-loop:run --iterations 1 --hours 1 --tokens 100000", (10, 5), None),
            "tokens": ("/meow-loop:run --iterations 5 --hours 1 --tokens 1000", (900, 600), None),
            "time": ("/meow-loop:run --iterations 5 --hours 1 --tokens 100000", (10, 5), "2000-01-01T00:00:00Z"),
        }
        for ending, (command, usage, started) in cases.items():
            with self.subTest(ending=ending):
                shutil.rmtree(self.state, ignore_errors=True)
                self.prompt(command)
                if started:
                    _, directory = self.run_toml()
                    table = tomllib.loads((directory / "run.toml").read_text())
                    text = (directory / "run.toml").read_text().replace(table["started_at"], started)
                    (directory / "run.toml").write_text(text)
                self.change_tree(ending)
                done, answer = self.stop(usage)
                self.assertNotEqual(answer.get("decision"), "block", done.stdout)
                table, _ = self.run_toml()
                self.assertEqual(table["ending"], ending)

    def test_two_unchanged_iterations_end_the_run_stuck_and_name_the_counts(self):
        """TSK-4110 criterion 4, REQ-3710, REQ-0886: the tree id, the counts and the notes stayed as they were."""
        self.start()
        done, first = self.stop()
        self.assertEqual(first.get("decision"), "block", done.stdout)
        done, second = self.stop()
        self.assertNotEqual(second.get("decision"), "block", done.stdout)
        table, _ = self.run_toml()
        self.assertEqual(table["ending"], "stuck")
        self.assertRegex(second["systemMessage"], r"1 requirement")

    def test_every_iteration_appends_one_log_line(self):
        """TSK-4110 criterion 5, REQ-2654, REQ-0892, REQ-0882: the line carries the state the checks used."""
        self.start()
        self.change_tree("a")
        self.stop((100, 50))
        self.change_tree("b")
        self.stop((300, 150))
        lines = self.log()
        self.assertEqual([line["iteration"] for line in lines], [1, 2])
        for line in lines:
            for key in ("tree_before", "tree_after", "open_requirements", "open_defects", "progress_changed", "tokens"):
                self.assertIn(key, line)
        self.assertEqual(lines[1]["tokens"], 450)

    def test_an_ending_is_one_of_six_and_reverts_nothing(self):
        """TSK-4110 criterion 6, REQ-2658, REQ-2656: the work tree keeps what the iteration changed."""
        self.prompt("/meow-loop:run --iterations 1 --hours 1 --tokens 100000")
        self.change_tree("kept")
        self.stop()
        table, _ = self.run_toml()
        self.assertIn(table["ending"], {"finished", "ceiling", "time", "tokens", "stuck", "cancelled"})
        self.assertEqual((self.repo / "work.txt").read_text(), "kept\n")

    def test_no_active_run_allows_the_stop_and_writes_nothing(self):
        """TSK-4110 criterion 7: with no run for the session the hook answers nothing and creates no run."""
        done, answer = self.stop()
        self.assertEqual(done.returncode, 0)
        self.assertEqual(done.stdout.strip(), "")
        self.assertEqual(self.runs(), [])


class PostureAtStart(Session):
    def test_a_session_in_another_mode_is_refused_naming_both(self):
        """TSK-4120 criterion 3, REQ-2388: the declared mode and the session's mode are both named."""
        done, answer = self.prompt(START, mode="default")
        self.assertEqual(self.runs(), [])
        self.assertIn("unresolved: the session is in default, and the posture declares dontAsk",
                      answer["systemMessage"])

    def test_a_release_of_false_is_recorded_and_other_values_are_refused(self):
        """TSK-4120 criterion 4, REQ-3722: `release = false` is a run that releases nothing."""
        self.start()
        table, _ = self.run_toml()
        self.assertIs(table["release"], False)
        self.write(".meowpaw/profile.toml", PROFILE.replace("release = false", "release = 3"))
        shutil.rmtree(self.state, ignore_errors=True)
        done, answer = self.prompt(START)
        self.assertEqual(self.runs(), [])
        self.assertIn("unresolved: [unattended] release 3 is not a command or false", answer["systemMessage"])

    def test_a_repository_with_no_posture_starts_no_run(self):
        """TSK-4120, SPC-1201 failure paths: an unresolved posture gives each line SPC-1200 states."""
        self.write(".meowpaw/profile.toml", PROFILE.split("[unattended]")[0])
        done, answer = self.prompt(START)
        self.assertEqual(self.runs(), [])
        self.assertIn("unresolved: no [unattended] table in .meowpaw/profile.toml", answer["systemMessage"])


class PostureGuard(Guarding):
    def active(self, **changes):
        text = PROFILE
        for old, new in changes.items():
            text = text.replace(old, new)
        self.write(".meowpaw/profile.toml", text)
        self.start()

    def test_the_guard_denies_the_profile_a_push_to_the_trunk_and_an_approved_record(self):
        """TSK-4120 criterion 5, REQ-3718: each of the three the posture forbids is denied."""
        self.start()
        self.assertEqual(self.guard("Edit", file_path=str(self.repo / ".meowpaw" / "profile.toml")), "deny")
        self.assertEqual(self.guard("Bash", command="git push origin main"), "deny")
        self.assertEqual(self.guard("Bash", command="git push"), "deny")
        self.assertEqual(self.guard("Bash", command="git push origin HEAD"), "deny")
        self.assertEqual(self.guard("Edit", file_path=str(self.repo / "project/requirements/REQ-0001-a-duty.md")),
                         "deny")

    def test_the_guard_allows_a_push_of_a_branch_and_a_draft_record(self):
        """TSK-4120 criterion 5: a branch, a new record and a draft are what a run may write."""
        self.start()
        self.assertIsNone(self.guard("Bash", command="git push origin feat/a-change"))
        self.write("project/requirements/REQ-0009-a-draft.md", requirement("REQ-0009", status="draft"))
        self.assertIsNone(self.guard("Edit", file_path=str(self.repo / "project/requirements/REQ-0009-a-draft.md")))
        self.assertIsNone(self.guard("Write", file_path=str(self.repo / "notes.md")))

    def test_amend_approved_lets_the_run_edit_an_approved_record(self):
        """TSK-4120 criterion 5, REQ-3718: where the repository declares it, the record's file may be edited."""
        self.write(".meowpaw/profile.toml", PROFILE + "amend_approved = true\n")
        self.start()
        self.assertIsNone(self.guard("Edit", file_path=str(self.repo / "project/requirements/REQ-0001-a-duty.md")))
        self.assertEqual(self.guard("Edit", file_path=str(self.repo / ".meowpaw" / "profile.toml")), "deny")


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
