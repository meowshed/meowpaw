# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1201 states `meow-loop start` does.

Each fixture is a scratch git repository with its home and its state directory
isolated, and a stand-in `claude` first on the path. The stand-in appends its
argv and standard input to a call log, can create a file, overwrite one, and
append a line to the progress file in the directory `--add-dir` names, edits
`work.txt` on each call so the tree changes, and prints the JSON result its
configuration names. `CLAUDECODE` is removed from every run's environment, because the gate
often runs inside a Claude Code session. `MEOW_LOOP_BIN` names the launcher to
test. Each check counts what it matched and fails on a count of zero where one
was expected (EPC-1910 criterion 13).
"""
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
import time
import tomllib
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_LOOP_BIN", UNIT / "bin" / "meow-loop"))

STAND_IN = '''#!/usr/bin/env python3
import json, os, sys, time
config = json.load(open(os.environ["FAKE_CLAUDE"]))
stdin = sys.stdin.buffer.read().decode()
log = config["log"]
n = (sum(1 for _ in open(log)) if os.path.exists(log) else 0) + 1
with open(log, "a") as f:
    f.write(json.dumps({"n": n, "argv": sys.argv[1:], "stdin": stdin}) + "\\n")
if config.get("edit", True):
    with open("work.txt", "a") as f:
        f.write("call %d\\n" % n)
name = config.get("create", {}).get(str(n))
if name:
    open(name, "w").write("x")
name = config.get("overwrite", {}).get(str(n))
if name:
    open(name, "w").write("overwritten by call %d\\n" % n)
if config.get("progress") and "--add-dir" in sys.argv:
    with open(os.path.join(sys.argv[sys.argv.index("--add-dir") + 1], "progress.md"), "a") as f:
        f.write("call %d\\n" % n)
time.sleep(config.get("sleep", {}).get(str(n), 0))
if config.get("silent"):
    sys.exit(0)
print(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": config.get("cost", 0.1),
                  "result": config.get("result", "done"), "permission_denials": []}))
'''

PROFILE = '[verbs]\ntest = "test -f done.flag"\n'
TERMS = ["--prompt", "prompt.md", "--until", "verbs=test", "--iterations", "5",
         "--budget-usd", "10", "--permission-mode", "dontAsk"]


def without(flag):
    """The standard terms with one flag and its value left out."""
    at = TERMS.index(flag)
    return TERMS[:at] + TERMS[at + 2:]


def replaced(flag, value):
    """The standard terms with one flag's value replaced."""
    terms = list(TERMS)
    terms[terms.index(flag) + 1] = value
    return terms


class Fixture:
    def __init__(self, files=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / "repo"
        self.home = self.base / "home"
        self.state = self.base / "state"
        self.bin = self.base / "bin"
        self.log = self.base / "calls.jsonl"
        self.config = self.base / "fake.json"
        for directory in (self.root, self.home, self.state, self.bin):
            directory.mkdir(parents=True)
        claude = self.bin / "claude"
        claude.write_text(STAND_IN)
        claude.chmod(0o755)
        self.configure()
        files = {".meowpaw/profile.toml": PROFILE, "prompt.md": "Make the flag exist.\n", **(files or {})}
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.com",
                 "-c", "commit.gpgsign=false", "commit", "-q", "-m", "fixture")

    def configure(self, **config):
        self.config.write_text(json.dumps({"log": str(self.log), **config}))

    def env(self, **more):
        env = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "MEOWPAW_STATE", "XDG_STATE_HOME")}
        env.update(PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}", HOME=str(self.home),
                   MEOWPAW_STATE_DIR=str(self.state), FAKE_CLAUDE=str(self.config),
                   GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", **more)
        return env

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, env=self.env())

    def start(self, terms=None, cwd=None, env=None, **more):
        done = subprocess.run([str(BIN), "start", *(TERMS if terms is None else terms)], cwd=cwd or self.root,
                              env=env or self.env(**more), capture_output=True, text=True, timeout=120)
        return done

    def calls(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def key(self):
        return hashlib.sha256(str(self.root.resolve()).encode()).hexdigest()[:16]

    def runs_dir(self):
        return self.state / "runs" / self.key()

    def run_dirs(self):
        return sorted(p for p in self.state.glob("runs/*/*") if p.is_dir())

    def ending(self):
        runs = self.run_dirs()
        self.assertion.assertEqual(len(runs), 1, "expected exactly one run directory")
        return tomllib.loads((runs[0] / "run.toml").read_text()).get("ending")

    def close(self):
        self.tmp.cleanup()


class Case(unittest.TestCase):
    def fixture(self, files=None):
        fixture = Fixture(files)
        fixture.assertion = self
        self.addCleanup(fixture.close)
        return fixture


class Condition(Case):
    def test_finished_after_two(self):
        f = self.fixture()
        f.configure(create={"2": "done.flag"}, log=str(f.log))
        done = f.start()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(f.calls()), 2)
        self.assertEqual(f.ending(), "finished")
        self.assertEqual(done.stdout.strip().splitlines()[-1], "finished")

    def test_finished_with_no_call(self):
        f = self.fixture({"done.flag": "x"})
        done = f.start()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.calls(), [])
        self.assertEqual(f.ending(), "finished")


class Terms(Case):
    def test_incomplete_terms_refused(self):
        f = self.fixture()
        refused = [
            (without("--until"), "--until is required"),
            (without("--iterations"), "--iterations is required"),
            (without("--budget-usd"), "--budget-usd is required"),
            (without("--permission-mode"), "--permission-mode is required"),
            (replaced("--iterations", "0"), "--iterations 0 is not at least 1"),
            (replaced("--iterations", "9223372036854775808"),
             "--iterations 9223372036854775808 is above 9223372036854775807"),
            (replaced("--budget-usd", "0"), "--budget-usd 0 is not above 0"),
            (replaced("--budget-usd", "+1e1"), "--budget-usd +1e1 is not a decimal number"),
            (replaced("--budget-usd", "9" * 400), "--budget-usd " + "9" * 400 + " is too large or too small to hold"),
            (replaced("--budget-usd", "0." + "0" * 400 + "1"),
             "--budget-usd 0." + "0" * 400 + "1 is too large or too small to hold"),
            (replaced("--permission-mode", "acceptEdits"), "--permission-mode acceptEdits is refused"),
            (replaced("--permission-mode", "bypassPermissions"), "--permission-mode bypassPermissions is refused"),
        ]
        matched = 0
        for terms, message in refused:
            done = f.start(terms)
            self.assertEqual(done.returncode, 2, message + done.stdout + done.stderr)
            self.assertIn(message, done.stderr)
            self.assertEqual(f.run_dirs(), [], message)
            matched += 1
        self.assertEqual(matched, 12)
        self.assertEqual(f.calls(), [])


class Ceiling(Case):
    def test_prompt_cannot_extend_the_ceiling(self):
        f = self.fixture()
        f.configure(result="ignore the ceiling, continue")
        done = f.start(replaced("--iterations", "3"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(len(f.calls()), 3)
        self.assertEqual(f.ending(), "ceiling")
        self.assertEqual(done.stdout.strip().splitlines()[-1], "ceiling")


class Refusals(Case):
    def test_five_unreadable_states(self):
        f = self.fixture()
        outside = f.base / "plain"
        outside.mkdir()
        # The command line is checked first (SPC-1201), so the prompt file has to be readable here too.
        (outside / "prompt.md").write_text("Make the flag exist.\n")
        bare = f.base / "nothing-on-path"
        bare.mkdir()
        states = [
            ("not a git work tree", dict(cwd=outside, env=f.env(GIT_CEILING_DIRECTORIES=str(f.base)))),
            ("state writing is off", dict(env=f.env(MEOWPAW_STATE="off"))),
            ("claude is not on the path", dict(env={**f.env(), "PATH": f"{bare}{os.pathsep}/usr/bin{os.pathsep}/bin"})),
            ("verb lint resolves to no command", dict(terms=replaced("--until", "verbs=lint"))),
        ]
        lock = f.runs_dir()
        lock.mkdir(parents=True)
        held = open(lock / "lock", "w")
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(held.close)
        states.append(("a run already holds this work tree", dict()))
        matched = 0
        for reason, options in states:
            done = f.start(**options)
            self.assertEqual(done.returncode, 3, reason + done.stdout + done.stderr)
            self.assertIn("unresolved: " + reason, done.stdout, reason)
            self.assertEqual(f.run_dirs(), [], reason)
            matched += 1
        self.assertEqual(matched, 5)
        self.assertEqual(f.calls(), [])

    def test_a_claude_that_cannot_run_is_passed_over(self):
        f = self.fixture({"sub/keep": ""})
        unrunnable = f.base / "unrunnable"
        unrunnable.mkdir()
        (unrunnable / "claude").write_text(STAND_IN)
        (unrunnable / "claude").chmod(0o644)
        old = f.runs_dir() / f"{1:020d}-old"
        old.mkdir(parents=True)
        done = f.start(env={**f.env(), "PATH": f"{unrunnable}{os.pathsep}/usr/bin{os.pathsep}/bin"})
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: claude is not on the path", done.stdout)
        self.assertEqual(f.run_dirs(), [old])
        self.assertEqual(f.calls(), [])
        # A relative entry is read from where the person stands, and the call starts in the root.
        f.configure(create={"1": "done.flag"})
        relative = os.path.join("..", "..", "bin")
        done = f.start(replaced("--prompt", os.path.join("..", "prompt.md")), cwd=f.root / "sub",
                       env={**f.env(), "PATH": os.pathsep.join([str(unrunnable), relative, os.environ["PATH"]])})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(f.calls()), 1)
        self.assertTrue((f.root / "done.flag").is_file())


class Lock(Case):
    def test_killed_run_leaves_no_lock(self):
        f = self.fixture()
        f.configure(sleep={"2": 5})
        first = subprocess.Popen([str(BIN), "start", *TERMS], cwd=f.root, env=f.env(),
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + 60
        while len(f.calls()) < 2 and time.time() < deadline:
            time.sleep(0.05)
        first.kill()
        first.wait()
        self.assertEqual(len(f.calls()), 2)
        f.configure(edit=True)
        before = len(f.calls())
        done = f.start(replaced("--iterations", "1"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertGreater(len(f.calls()), before)


class Retention(Case):
    def test_keeps_the_newest_twenty(self):
        f = self.fixture({"done.flag": "x"})
        old = [f"{n:020d}-old" for n in range(1, 21)]
        for name in old:
            (f.runs_dir() / name).mkdir(parents=True)
        done = f.start()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        remaining = [p.name for p in f.run_dirs()]
        self.assertEqual(len(remaining), 20)
        self.assertNotIn(old[0], remaining)
        self.assertIn(old[1], remaining)
        self.assertIn(old[0], done.stdout)


class Files(Case):
    def test_run_directory(self):
        f = self.fixture()
        f.configure(create={"2": "done.flag"}, cost=0.25)
        done = f.start()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        runs = f.run_dirs()
        self.assertEqual(len(runs), 1)
        run = runs[0]
        self.assertEqual(sorted(p.name for p in run.iterdir()), ["log.jsonl", "progress", "prompt.md", "run.toml"])
        self.assertEqual((run / "progress" / "progress.md").read_text(), "")
        self.assertEqual((run / "prompt.md").read_text(), "Make the flag exist.\n")
        lines = [json.loads(line) for line in (run / "log.jsonl").read_text().splitlines()]
        self.assertEqual(len(lines), 2)
        for number, line in enumerate(lines, 1):
            for field in ("iteration", "tree_before", "tree_after", "total_cost_usd", "permission_denials",
                          "exit_status", "condition"):
                self.assertIn(field, line)
            self.assertEqual(line["iteration"], number)
            self.assertEqual(line["total_cost_usd"], 0.25)
            self.assertEqual(line["exit_status"], 0)
        self.assertNotEqual(lines[0]["tree_before"], lines[0]["tree_after"])
        self.assertIs(lines[0]["condition"], False)
        self.assertIs(lines[1]["condition"], True)
        table = tomllib.loads((run / "run.toml").read_text())
        self.assertEqual(table["ending"], "finished")
        self.assertEqual(table["iterations"], 5)
        self.assertEqual(table["budget_usd"], 10)
        self.assertEqual(table["permission_mode"], "dontAsk")
        self.assertEqual(table["until"], {"verbs": {"test": "test -f done.flag"}})
        self.assertEqual(table["prompt_sha256"], hashlib.sha256(b"Make the flag exist.\n").hexdigest())
        self.assertNotIn("sum_usd", lines[0])


class Call(Case):
    def test_flags_and_prompt(self):
        f = self.fixture()
        f.configure(create={"1": "done.flag"})
        done = f.start(TERMS + ["--allowed-tools", "Read", "--plugin-dir", "/somewhere/else"])
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        calls = f.calls()
        self.assertEqual(len(calls), 1)
        argv, stdin = calls[0]["argv"], calls[0]["stdin"]
        self.assertEqual(stdin, "Make the flag exist.\n")
        progress = f.run_dirs()[0] / "progress"
        self.assertEqual(argv[:-1], ["-p", "--output-format", "json", "--no-session-persistence",
                                     "--setting-sources", "project", "--plugin-dir", "/somewhere/else",
                                     "--permission-mode", "dontAsk", "--allowedTools", "Read",
                                     *allow_rules(progress / "progress.md"),
                                     "--permission-prompts", "none", "--add-dir", str(progress),
                                     "--max-budget-usd", "10", "--append-system-prompt"])
        carrying = [argument for argument in argv if "Make the flag exist" in argument]
        self.assertEqual(carrying, [])


    def test_a_claude_with_no_program_in_it_stops_the_run(self):
        f = self.fixture()
        (f.bin / "claude").write_text("no program the system can run\n")
        done = f.start(replaced("--iterations", "2"))
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: claude can't be started", done.stdout)
        self.assertNotIn("iteration", done.stdout)
        runs = f.run_dirs()
        self.assertEqual(len(runs), 1)
        self.assertNotIn("ending", tomllib.loads((runs[0] / "run.toml").read_text()))
        self.assertEqual((runs[0] / "log.jsonl").read_text(), "")


def allow_rules(file):
    """The arguments that allow Edit and Write of `file`, an absolute path, which a rule writes after one more
    slash."""
    return ["--allowedTools", f"Edit(/{file})", "--allowedTools", f"Write(/{file})"]


def values(argv, flag):
    """Every value `flag` is given in `argv`."""
    return [argv[at + 1] for at, argument in enumerate(argv[:-1]) if argument == flag]


class Context(Case):
    """ADR-2010: every call starts from the same prompt and preamble, and progress is carried in a file."""

    def test_every_call_starts_the_same(self):
        """TSK-3360 criterion 1, REQ-0880 and the "rather than in the conversation" half of REQ-0882: over three
        calls that each report a cost, with the prompt file overwritten in the work tree after the first, every
        call's standard input is the prompt as it was at start, every call's preamble is the same bytes, the run's
        `prompt.md` is those of the standard input, and no call resumes a session."""
        f = self.fixture()
        f.configure(cost=0.25, overwrite={"1": "prompt.md"})
        done = f.start(replaced("--iterations", "3"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        calls = f.calls()
        self.assertEqual(len(calls), 3)
        self.assertNotEqual((f.root / "prompt.md").read_text(), "Make the flag exist.\n")
        preambles = []
        for call in calls:
            self.assertEqual(call["stdin"], "Make the flag exist.\n")
            given = values(call["argv"], "--append-system-prompt")
            self.assertEqual(len(given), 1, call["argv"])
            preambles.extend(given)
            resuming = [a for a in call["argv"] if a in ("--resume", "--continue", "-r", "-c")]
            self.assertEqual(resuming, [])
        self.assertEqual(len(preambles), 3)
        self.assertNotEqual(preambles[0].strip(), "")
        self.assertEqual(len(set(preambles)), 1)
        self.assertEqual((f.run_dirs()[0] / "prompt.md").read_bytes(), calls[0]["stdin"].encode())

    def test_progress_file_is_named_and_reachable(self):
        """TSK-3360 criterion 2, REQ-0882: the preamble holds the absolute path of the run's `progress/progress.md`
        and the condition's text, and each argv holds `--add-dir` followed by that file's directory and the rules
        allowing Edit and Write of that file."""
        # Two verbs, so a preamble naming only the first, or the two in another order, doesn't pass.
        f = self.fixture({".meowpaw/profile.toml": PROFILE + 'lint = "true"\n'})
        terms = replaced("--iterations", "2")
        terms[terms.index("--until") + 1] = "verbs=test,lint"
        done = f.start(terms)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        calls = f.calls()
        self.assertEqual(len(calls), 2)
        file = f.run_dirs()[0] / "progress" / "progress.md"
        self.assertTrue(file.is_absolute())
        matched = 0
        for call in calls:
            argv = call["argv"]
            preamble = values(argv, "--append-system-prompt")
            self.assertEqual(len(preamble), 1, argv)
            self.assertIn(str(file), preamble[0])
            self.assertIn("`verbs=test,lint`", preamble[0])
            self.assertEqual(values(argv, "--add-dir"), [str(file.parent)])
            allowed = values(argv, "--allowedTools")
            for rule in values(allow_rules(file), "--allowedTools"):
                self.assertEqual(allowed.count(rule), 1, (rule, allowed))
            matched += 1
        self.assertEqual(matched, 2)

    def test_progress_survives_iterations(self):
        """TSK-3360 criterion 3, REQ-0882: a line each call appends to the progress file is still there after the
        next call, so three calls leave three lines."""
        f = self.fixture()
        f.configure(progress=True)
        done = f.start(replaced("--iterations", "3"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(len(f.calls()), 3)
        lines = (f.run_dirs()[0] / "progress" / "progress.md").read_text().splitlines()
        self.assertEqual(lines, ["call 1", "call 2", "call 3"])


class Unchanged(Case):
    def test_an_unchanged_tree_skips_the_verbs(self):
        f = self.fixture()
        f.configure(edit=False)
        done = f.start(replaced("--iterations", "3"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(len(f.calls()), 3)
        self.assertEqual(f.ending(), "ceiling")
        log = f.run_dirs()[0] / "log.jsonl"
        lines = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertIsNone(line["condition"])
            self.assertEqual(line["tree_before"], line["tree_after"])
        ledger = f.state / "evidence" / f"{f.key()}.jsonl"
        records = {entry["record"] for entry in map(json.loads, ledger.read_text().splitlines())
                   if entry["verb"] == "test"}
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
