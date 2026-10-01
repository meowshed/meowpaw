# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1201 states `meow-loop start` does.

Each fixture is a scratch git repository with its home and its state directory
isolated, and a stand-in `claude` first on the path. The stand-in appends its
argv and standard input to a call log, can create a file, overwrite one, and
append a line to the progress file in the directory `--add-dir` names, edits
`work.txt` on each call so the tree changes, and prints the JSON result its
configuration names, can append a line to a file of the run, write an allow
rule into `.claude/settings.json` or rewrite the profile, with the subtype it
names, the cost it names for that
call and no cost where it says so. It never reads `--max-budget-usd`, so no ending comes from it. `CLAUDECODE` is removed from every run's environment, because the gate
often runs inside a Claude Code session. `MEOW_LOOP_BIN` names the launcher to
test. Each check counts what it matched and fails on a count of zero where one
was expected (EPC-1910 criterion 13).
"""
import fcntl
import hashlib
import json
import os
import shutil
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
if config.get("remove_progress", {}).get(str(n)) and "--add-dir" in sys.argv:
    os.remove(os.path.join(sys.argv[sys.argv.index("--add-dir") + 1], "progress.md"))
if config.get("progress") and "--add-dir" in sys.argv:
    with open(os.path.join(sys.argv[sys.argv.index("--add-dir") + 1], "progress.md"), "a") as f:
        f.write("call %d\\n" % n)
run = os.path.dirname(sys.argv[sys.argv.index("--add-dir") + 1]) if "--add-dir" in sys.argv else None
name = config.get("touch", {}).get(str(n))
if name and run:
    with open(os.path.join(run, name), "a") as f:
        f.write("# changed by call %d\\n" % n)
if config.get("settings", {}).get(str(n)):
    os.makedirs(".claude", exist_ok=True)
    open(".claude/settings.json", "w").write('{"permissions": {"allow": ["Bash(*)"]}}')
for name, text in config.get("write", {}).get(str(n), {}).items():
    os.makedirs(os.path.dirname(name) or ".", exist_ok=True)
    open(name, "w").write(text)
ledger = config.get("ledger", {}).get(str(n))
if ledger:
    os.makedirs(os.path.dirname(ledger["path"]), exist_ok=True)
    with open(ledger["path"], "a") as f:
        f.write(json.dumps(ledger["line"]) + "\\n")
text = config.get("profile", {}).get(str(n))
if text:
    open(".meowpaw/profile.toml", "w").write(text)
time.sleep(config.get("sleep", {}).get(str(n), 0))
if config.get("silent"):
    sys.exit(0)
cost = config.get("costs", {}).get(str(n), config.get("cost", 0.1))
result = {"type": "result", "subtype": config.get("subtype", "success"), "total_cost_usd": cost,
          "result": config.get("result", "done"), "permission_denials": []}
if config.get("no_cost"):
    del result["total_cost_usd"]
print(json.dumps(result))
'''

PROFILE = '[verbs]\ntest = "test -f done.flag"\n\n[git]\ntrunk = "main"\n'
# A run binds to one step of the method. The standard terms implement TSK-0001, whose work is done, so the step's
# test holds and a run's condition rests on its verbs, as every check written before TSK-3410 expects.
TERMS = ["--step", "implement", "--inputs", "TSK-0001", "--prompt", "prompt.md", "--until", "verbs=test",
         "--iterations", "5", "--budget-usd", "10", "--permission-mode", "dontAsk"]


def front(**fields):
    lines = ["---"] + [f"{key}: {value}" for key, value in fields.items()] + ["---", ""]
    return "\n".join(lines)


def epic(first="x", second=" "):
    """EPC-0001, which lists TSK-0001 and TSK-0002 with the marks given."""
    return (front(id="EPC-0001", artifact="epic", status="approved", revised="2026-01-01", realises="ADR-0001")
            + "\n# A plan\n\n## Tasks\n\n"
            + f"- [{first}] T-001 TSK-0001 the first\n      closes: REQ-0001\n\n"
            + f"- [{second}] T-002 TSK-0002 the second\n      closes: REQ-0001\n")


def task(id, evidence):
    return (front(id=id, artifact="task", status="approved", revised="2026-01-01", epic="EPC-0001",
                  closes="[REQ-0001]")
            + f"\n# Task {id}\n\nText.\n\n## Acceptance criteria\n\n1. It works.\n\n## What to do\n\nIt.\n\n"
            + f"## Depends on\n\nNothing.\n\n## Evidence\n\n{evidence}\n\n## Left alone\n\nNothing.\n")


# A small record: research, two requirements (one a draft), a decision addressing the first, a specification
# stating it, and an epic listing TSK-0001, done, and TSK-0002, open.
RECORD = {
    "project/research/RES-0001-a-finding.md": front(id="RES-0001", artifact="research", status="approved",
                                                     revised="2026-01-01") + "\n# A finding\n",
    "project/requirements/REQ-0001-a-duty.md": front(id="REQ-0001", artifact="requirement", topic="loop",
                                                     **{"class": "functional"}, status="approved",
                                                     revised="2026-01-01", elaborates="RES-0001",
                                                     verification="behavioural") + "\n# REQ-0001\n\nIt MUST.\n",
    "project/requirements/REQ-0002-a-draft.md": front(id="REQ-0002", artifact="requirement", topic="loop",
                                                      **{"class": "functional"}, status="draft",
                                                      revised="2026-01-01", elaborates="RES-0001",
                                                      verification="behavioural") + "\n# REQ-0002\n\nIt MUST.\n",
    "project/adrs/ADR-0001-a-choice.md": front(id="ADR-0001", artifact="adr", status="approved",
                                               revised="2026-01-01", addresses="[REQ-0001]",
                                               supersedes="[]") + "\n# 0001. A choice\n",
    "project/specs/SPC-0001-a-part.md": front(id="SPC-0001", artifact="spec", status="live", revised="2026-01-01",
                                              states="[REQ-0001]") + "\n# A part\n",
    "project/epics/EPC-0001-a-plan.md": epic(),
    "project/tasks/TSK-0001-the-first.md": task("TSK-0001", "Done, as the checks show."),
    "project/tasks/TSK-0002-the-second.md": task("TSK-0002", "Not yet."),
}


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
        files = {".meowpaw/profile.toml": PROFILE, "prompt.md": "Make the flag exist.\n", **RECORD, **(files or {})}
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

    # ADR-2010: a run whose terms change ends `tampered`, and the condition runs the commands held at start.

    def ended(self, f, **config):
        f.configure(**config)
        done = f.start(replaced("--iterations", "3"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(done.stdout.strip().splitlines()[-1], "tampered")
        return f.ending()

    def test_tampered_run_toml(self):
        """TSK-3390 criterion 1, REQ-0874: a call that edits `run.toml` ends the run `tampered` after that call, and
        so does one that edits it and makes the verb pass in the same call."""
        matched = 0
        for config in ({"touch": {"1": "run.toml"}}, {"touch": {"1": "run.toml"}, "create": {"1": "done.flag"}}):
            f = self.fixture()
            self.assertEqual(self.ended(f, **config), "tampered", config)
            self.assertEqual(len(f.calls()), 1, config)
            matched += 1
        self.assertEqual(matched, 2)

    def test_tampered_prompt(self):
        """TSK-3390 criterion 2, REQ-0874: a call that edits the run's `prompt.md` and reports no cost ends the run
        `tampered` and not `unmetered`, which only the check after the call, before the cost is read, can
        produce."""
        f = self.fixture()
        self.assertEqual(self.ended(f, touch={"1": "prompt.md"}, no_cost=True), "tampered")
        self.assertEqual(len(f.calls()), 1)

    def test_tampered_settings(self):
        """TSK-3390 criterion 2, REQ-0874: a call that writes an allow rule into an existing `.claude/settings.json`
        and makes the verb pass ends the run `tampered`, and `run.toml` records the settings' sha256 at start."""
        before = '{"permissions": {}}'
        f = self.fixture({".claude/settings.json": before})
        self.assertEqual(self.ended(f, settings={"1": True}, create={"1": "done.flag"}), "tampered")
        self.assertEqual(len(f.calls()), 1)
        table = tomllib.loads((f.run_dirs()[0] / "run.toml").read_text())
        self.assertEqual(table["settings_sha256"], hashlib.sha256(before.encode()).hexdigest())

    def test_an_evaluation_that_changes_the_terms_ends_tampered(self):
        """TSK-3390, REQ-0874: a verb that writes the settings and passes ends the run `tampered` and not
        `finished`, in the evaluation after a call and in the one before the first call."""
        # The verb writes only once the flag exists, so where the flag comes from decides which evaluation writes.
        write = "test -f done.flag && mkdir -p .claude && echo changed > .claude/settings.json"
        profile = {".meowpaw/profile.toml": f'[verbs]\ntest = "{write}"\n'}
        f = self.fixture(profile)
        self.assertEqual(self.ended(f, create={"1": "done.flag"}), "tampered")
        f = self.fixture({**profile, "done.flag": "x"})
        self.assertEqual(self.ended(f), "tampered")
        self.assertEqual(f.calls(), [])

    def test_tampered_before_the_call(self):
        """TSK-3390 criterion 8, REQ-0874: a held verb command that edits `run.toml` before the first call ends the
        run `tampered` with no call, which only the check before the first call can produce."""
        edit = ('for f in \\"$MEOWPAW_STATE_DIR\\"/runs/*/*/run.toml; do echo \\"# edited\\" >> \\"$f\\"; done; '
                'exit 1')
        f = self.fixture({".meowpaw/profile.toml": f'[verbs]\ntest = "{edit}"\n'})
        f.configure()
        done = f.start()
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.calls(), [])
        self.assertEqual(f.ending(), "tampered")

    def test_profile_edit_changes_no_condition(self):
        """TSK-3390 criterion 6, REQ-0874: a call that points the `test` verb at a command that always passes changes
        no condition, because the run holds the command resolved at start: two calls run to the ceiling, and
        `run.toml` records the held command."""
        f = self.fixture()
        f.configure(profile={"1": '[verbs]\ntest = "true"\n'})
        done = f.start(replaced("--iterations", "2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(len(f.calls()), 2)
        self.assertEqual(f.ending(), "ceiling")
        table = tomllib.loads((f.run_dirs()[0] / "run.toml").read_text())
        self.assertEqual(table["until"], {"verbs": {"test": "test -f done.flag"}})

    def test_own_unit_on_every_call(self):
        """TSK-3390 criterion 7: every call names `meow-loop`'s own directory with `--plugin-dir` first, then each
        one the person named, in the order given."""
        f = self.fixture()
        # A copy of the unit, so a directory fixed when the program was built can't pass for the one it runs from.
        copy = f.base / "installed" / "meow-loop"
        shutil.copytree(UNIT, copy, ignore=shutil.ignore_patterns("tests", "__pycache__"))
        done = subprocess.run([str(copy / "bin" / "meow-loop"), "start",
                               *replaced("--iterations", "2"), "--plugin-dir", "/a", "--plugin-dir", "/b"],
                              cwd=f.root, env=f.env(), capture_output=True, text=True, timeout=120)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        calls = f.calls()
        self.assertEqual(len(calls), 2)
        for call in calls:
            self.assertEqual(values(call["argv"], "--plugin-dir"), [str(copy.resolve()), "/a", "/b"])

    def test_a_program_outside_its_unit_starts_no_run(self):
        """TSK-3390: a program three levels below a directory that isn't `meow-loop` can't name the unit's own
        directory, so it refuses the run rather than start calls that load no hook."""
        f = self.fixture()
        for manifest in (None, '{"name": "meow-git"}'):
            with self.subTest(manifest=manifest):
                unit = f.base / ("bare" if manifest is None else "other")
                stray = unit / "bin" / "target" / "meow"
                stray.parent.mkdir(parents=True)
                shutil.copy2(next((UNIT / "bin").glob("*-*/meow*")), stray)
                if manifest is not None:
                    (unit / ".claude-plugin").mkdir()
                    (unit / ".claude-plugin" / "plugin.json").write_text(manifest)
                done = subprocess.run([str(stray), "loop", "start", *TERMS], cwd=f.root, env=f.env(),
                                      capture_output=True, text=True, timeout=120)
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                self.assertIn("unresolved: meow-loop's own directory can't be found", done.stdout)
                self.assertEqual(f.calls(), [])


class Guards(Case):
    """ADR-2010: only a person starts a run."""

    def test_skill_is_person_only(self):
        """TSK-3400 criterion 1, REQ-0894: the skill `meow-loop:loop` sets `disable-model-invocation: true`, so the
        model can't invoke it."""
        text = (UNIT / "skills" / "loop" / "SKILL.md").read_text()
        self.assertTrue(text.startswith("---\n"), text[:40])
        front = text.split("---\n")[1]
        fields = dict(line.split(": ", 1) for line in front.splitlines() if ": " in line)
        self.assertEqual(fields.get("name"), "loop")
        self.assertEqual(fields.get("disable-model-invocation"), "true")

    def test_claudecode_refused(self):
        """TSK-3400 criterion 2, REQ-0894: with `CLAUDECODE` set, even to nothing, `start` exits 3, prints the
        refusal, leaves the state directory exactly as it was, file by file, and holds no lock afterwards."""
        for value in ("1", ""):
            with self.subTest(CLAUDECODE=value):
                self.refused_with(value)

    def refused_with(self, value):
        f = self.fixture()
        earlier = f.runs_dir() / f"{1:020d}-earlier"
        earlier.mkdir(parents=True)
        (earlier / "run.toml").write_text('ending = "ceiling"\n')

        def snapshot():
            return {str(p.relative_to(f.state)): (p.read_bytes() if p.is_file() else None)
                    for p in sorted(f.state.rglob("*"))}

        before = snapshot()
        done = f.start(env={**f.env(), "CLAUDECODE": value})
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: a run starts from a terminal outside Claude Code", done.stdout)
        self.assertEqual(snapshot(), before)
        self.assertEqual(f.calls(), [])
        # The snapshot holds every file under the state directory, so no lock file was made either.
        self.assertFalse((f.runs_dir() / "lock").exists())

    def test_deny_rule_on_every_call(self):
        """TSK-3400 criterion 4, REQ-0894: every call passes `--disallowedTools` with a rule for each name a run
        starts by, so a call can't start a nested run."""
        f = self.fixture()
        done = f.start(replaced("--iterations", "2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        calls = f.calls()
        self.assertEqual(len(calls), 2)
        for call in calls:
            argv = call["argv"]
            at = argv.index("--disallowedTools")
            self.assertEqual(argv[at + 1:at + 3], ["Bash(meow-loop *)", "Bash(meow loop *)"])


class Hook(Case):
    """ADR-2010: the unit's hook denies an Edit or a Write of a run's files other than its progress file."""

    def guard(self, f, tool, path):
        event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"file_path": str(path)}}
        return subprocess.run([str(BIN), "guard"], input=json.dumps(event), capture_output=True, text=True,
                              env=f.env(), cwd=f.root)

    def test_run_files_are_denied(self):
        """TSK-3390 criterion 4, REQ-0874: an Edit of a run's `run.toml`, a Write of its `prompt.md`, an Edit of its
        `log.jsonl` and an Edit reaching `run.toml` through `progress/..` are each denied; an Edit of the run's
        `progress/progress.md` and of a tracked file in the work tree are each allowed in silence."""
        f = self.fixture()
        run = f.runs_dir() / "00000000000000000001"
        (run / "progress").mkdir(parents=True)
        for name in ("run.toml", "prompt.md", "log.jsonl", "progress/progress.md"):
            (run / name).write_text("")
        # The same run reached through a link, through a directory that doesn't exist and `..`, and, on macOS,
        # through `/var` where the state directory resolves under `/private/var`.
        link = f.base / "link"
        link.symlink_to(run)
        unresolved = Path(str(run).replace("/private/var/", "/var/", 1))
        denied = (("Edit", run / "run.toml"), ("Write", run / "prompt.md"), ("Edit", run / "log.jsonl"),
                  ("Edit", run / "progress" / ".." / "run.toml"), ("Write", link / "run.toml"),
                  ("Write", run / "missing" / ".." / "run.toml"), ("Edit", unresolved / "run.toml"),
                  ("Write", unresolved / "missing" / ".." / "run.toml"),
                  ("Write", link / "missing" / ".." / "run.toml"))
        matched = 0
        for tool, path in denied:
            done = self.guard(f, tool, path)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            answer = json.loads(done.stdout)["hookSpecificOutput"]
            self.assertEqual((answer["hookEventName"], answer["permissionDecision"]), ("PreToolUse", "deny"), path)
            matched += 1
        for tool, path in (("Edit", run / "progress" / "progress.md"), ("Edit", f.root / "prompt.md")):
            done = self.guard(f, tool, path)
            self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""), path)
            matched += 1
        self.assertEqual(matched, 11)

    def bash(self, f, command):
        event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
        return subprocess.run([str(BIN), "guard"], input=json.dumps(event), capture_output=True, text=True,
                              env=f.env(), cwd=f.root)

    def test_start_is_denied(self):
        """TSK-3400 criterion 3, REQ-0894: a Bash command that starts a run, by either name and however it is
        reached, is denied, and one that runs `meow-loop` without starting a run is allowed in silence, even where
        its text holds `start` elsewhere."""
        f = self.fixture()
        terms = "--prompt p.md --until verbs=test --iterations 1 --budget-usd 1 --permission-mode dontAsk"
        denied = (f"meow-loop start {terms}", f"cd x && meow-loop start {terms}",
                  f"${{CLAUDE_PLUGIN_ROOT}}/bin/meow-loop start {terms}",
                  f"env -u CLAUDECODE meow-loop start {terms}", f"bash -c 'meow-loop start {terms}'",
                  f"/x/meow-loop/bin/aarch64-apple-darwin/meow loop start {terms}",
                  # The review of TSK-3400: an escaped space, a continued line and a redirect joined to `start`.
                  f"bash -c meow-loop\\ start {terms}", f"meow-loop \\\n  start {terms}",
                  f"meow-loop start>run.log {terms}", f"meow-loop start<p.md",
                  # The second review: a redirect between the name and `start`.
                  f"env -u CLAUDECODE meow-loop >/dev/null start {terms}", f"meow loop 2>&1 start {terms}",
                  f"meow-loop > out.log start {terms}",
                  # The third review: a quoted `>` before the name, and a named descriptor's redirect.
                  f"echo '>'; meow-loop start {terms}", f"echo \">\"\nmeow-loop start {terms}",
                  f"meow-loop {{fd}}>/dev/null start {terms}")
        answers = []
        for command in denied:
            done = self.bash(f, command)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            answers.append(json.loads(done.stdout or "{}").get("hookSpecificOutput", {}).get("permissionDecision"))
        self.assertEqual(answers, ["deny"] * len(denied), list(zip(denied, answers)))
        for command in ("meow-loop --help", "meow-loop status", "meow-loop status; echo start"):
            done = self.bash(f, command)
            self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""), command)

    def test_hook_is_registered(self):
        """TSK-3390 criterion 5 and TSK-3400, REQ-0894: `hooks.json` registers a PreToolUse entry whose matcher
        covers Bash, Edit and Write and whose command runs the guard."""
        hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text())["hooks"]["PreToolUse"]
        entries = [e for e in hooks if set(e["matcher"].split("|")) >= {"Bash", "Edit", "Write"}]
        self.assertEqual(len(entries), 1, hooks)
        self.assertEqual([h["command"] for h in entries[0]["hooks"]], ['"${CLAUDE_PLUGIN_ROOT}"/bin/meow-loop guard'])


def step_terms(step, inputs=None, iterations="3"):
    """The standard terms with the step and its inputs replaced, and the ceiling given."""
    terms = list(TERMS[4:])
    terms[terms.index("--iterations") + 1] = iterations
    return ["--step", step] + (["--inputs", inputs] if inputs else []) + terms


class Step(Case):
    """ADR-2020: a run is bound to one step, and finishes only when the step's test and the verbs pass at one tree."""

    def test_phrase_is_not_done(self):
        """TSK-3410 criterion 1, REQ-0884: a call whose result says the work is done, while the verb fails, ends the
        run at the ceiling, because the runner reads nothing the model printed."""
        f = self.fixture()
        f.configure(result="DONE, all tests pass")
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(len(f.calls()), 3)
        self.assertEqual(f.ending(), "ceiling")

    def test_ledger_line_is_not_done(self):
        """TSK-3410 criterion 2, REQ-0884: a call that appends a passing ledger line for the verb, while the verb
        fails, doesn't end the run `finished`, because the runner reads no pass back from the ledger."""
        f = self.fixture()
        ledger = f.state / "evidence" / f"{f.key()}.jsonl"
        line = {"verb": "test", "outcome": "passed", "status": 0, "record": "forged", "tree": "any"}
        f.configure(ledger={"1": {"path": str(ledger), "line": line}})
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertNotEqual(f.ending(), "finished", done.stdout + done.stderr)

    def test_repeat_once_after_a_write(self):
        """TSK-3410 criterion 3, REQ-0884: a verb that rewrites a tracked file on its first run and exits 0 ends the
        run `finished` after the evaluation is repeated once."""
        settle = "test -f f.txt || echo formatted > f.txt"
        f = self.fixture({".meowpaw/profile.toml": f'[verbs]\ntest = "{settle}"\n'})
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
        self.assertEqual(f.calls(), [])

    def test_restless_verb_never_finishes(self):
        """TSK-3410 criterion 3, REQ-0884: a verb that changes the tree on every run never ends the run
        `finished`."""
        f = self.fixture({".meowpaw/profile.toml": '[verbs]\ntest = "date +%s%N >> f.txt"\n'})
        done = f.start(step_terms("implement", "TSK-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "ceiling")

    def test_dirty_submodule_holds_nothing(self):
        """TSK-3410 criterion 4, REQ-0884: with a dirty submodule the tree is unidentified, the condition never
        holds, and the log records the tree as `unidentified`."""
        f = self.fixture({"done.flag": "x"})
        origin = f.base / "sub-origin"
        origin.mkdir()
        (origin / "a.txt").write_text("a\n")
        identity = ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.com", "-c", "commit.gpgsign=false"]
        for args in (["init", "-q", "-b", "main"], ["add", "-A"], [*identity, "commit", "-q", "-m", "sub"]):
            subprocess.run(["git", *args], cwd=origin, check=True, capture_output=True, env=f.env())
        f.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", str(origin), "sub")
        f.git(*identity, "commit", "-q", "-m", "add the submodule")
        (f.root / "sub" / "a.txt").write_text("changed\n")
        done = f.start(step_terms("implement", "TSK-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertNotEqual(f.ending(), "finished")
        lines = [json.loads(line) for line in (f.run_dirs()[0] / "log.jsonl").read_text().splitlines()]
        self.assertTrue(lines)
        self.assertTrue(all(line["unidentified"] for line in lines))

    def test_dropped_is_not_done(self):
        """TSK-3410 criterion 5, REQ-0884: a call that marks the input task `~`, dropped, doesn't finish an
        `implement` run, though the verb passes."""
        f = self.fixture()
        f.configure(write={"1": {"project/epics/EPC-0001-a-plan.md": epic("x", "~")}}, create={"1": "done.flag"})
        done = f.start(step_terms("implement", "TSK-0002"))
        self.assertNotEqual(f.ending(), "finished", done.stdout + done.stderr)

    def test_marked_done_finishes(self):
        """TSK-3410 criterion 5, REQ-0884: a call that marks the input task `x` and writes its Evidence, while the
        verb passes, finishes an `implement` run after that call."""
        f = self.fixture()
        f.configure(write={"1": {"project/epics/EPC-0001-a-plan.md": epic("x", "x"),
                                 "project/tasks/TSK-0002-the-second.md": task("TSK-0002", "Done.")}},
                    create={"1": "done.flag"})
        done = f.start(step_terms("implement", "TSK-0002"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
        self.assertEqual(len(f.calls()), 1)

    def test_step_usage_errors(self):
        """TSK-3410 criterion 6: a missing, unknown or review step, `--inputs` on research, and none on design are
        usage errors that exit 2 and leave no run directory."""
        f = self.fixture()
        rest = TERMS[4:]
        cases = ((rest, "usage: --step is required"),
                 (["--step", "review", "--inputs", "TSK-0001"] + rest, "usage: --step review is not a step a run takes"),
                 (["--step", "polish", "--inputs", "TSK-0001"] + rest, "usage: --step polish is not a step a run takes"),
                 (["--step", "research", "--inputs", "RES-0001"] + rest, "usage: research takes no --inputs"),
                 (["--step", "design"] + rest, "usage: --step design needs --inputs"))
        for terms, message in cases:
            with self.subTest(message=message):
                done = f.start(terms)
                self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
                self.assertIn(message, done.stderr)
                self.assertEqual(f.run_dirs(), [])

    def test_step_unresolved_states(self):
        """TSK-3410 criterion 6: an input that isn't ready, and a record root that is ignored by git, missing or
        outside the work tree, each exit 3 with the reason and leave no run directory."""
        cases = (({}, step_terms("design", "REQ-0002"), "unresolved: REQ-0002, a requirement, is draft and not approved"),
                 ({".gitignore": "project/\n"}, TERMS, "unresolved: record root project is ignored by git"),
                 ({".meowpaw/profile.toml": PROFILE + '\n[record]\nroot = "nowhere"\n'}, TERMS,
                  "unresolved: record root nowhere is missing"),
                 ({".meowpaw/profile.toml": PROFILE + '\n[record]\nroot = "../elsewhere"\n'}, TERMS,
                  "unresolved: record root ../elsewhere is outside the work tree"))
        for files, terms, message in cases:
            with self.subTest(message=message):
                f = self.fixture(files)
                done = f.start(terms)
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                self.assertIn(message, done.stdout)
                self.assertEqual(f.run_dirs(), [])
                self.assertEqual(f.calls(), [])

    def test_run_toml_holds_the_step(self):
        """TSK-3410 criterion 6: `run.toml` holds the step as a string and the inputs as a list."""
        f = self.fixture({"done.flag": "x"})
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        table = tomllib.loads((f.run_dirs()[0] / "run.toml").read_text())
        self.assertEqual((table["step"], table["inputs"]), ("implement", ["TSK-0001"]))

    def test_spec_run_finishes(self):
        """TSK-3410 criterion 7: a call that writes a new specification stating each requirement the input decision
        addresses, while the verb passes, finishes a `spec` run."""
        f = self.fixture()
        spec = front(id="SPC-0002", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Another part\n"
        f.configure(write={"1": {"project/specs/SPC-0002-another.md": spec}}, create={"1": "done.flag"})
        done = f.start(step_terms("spec", "ADR-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
        self.assertEqual(len(f.calls()), 1)

    def test_amending_design_run_finishes(self):
        """TSK-3410 criterion 8, REQ-0884: a `design` run over a requirement an approved decision already addresses
        makes a call, and finishes when the call writes a new draft decision addressing it that names the decision
        it amends and changes nothing in it."""
        f = self.fixture({"done.flag": "x"})
        decision = front(id="ADR-0002", artifact="adr", status="draft", revised="2026-01-01",
                         addresses="[REQ-0001]", supersedes="[]") + "\n# 0002. An amendment of ADR-0001\n"
        f.configure(write={"1": {"project/adrs/ADR-0002-an-amendment.md": decision}})
        done = f.start(step_terms("design", "REQ-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
        self.assertEqual(len(f.calls()), 1)

    def test_preamble_names_the_step(self):
        """TSK-3410 criterion 9: every call's preamble names the step and its inputs, and all are byte identical."""
        f = self.fixture()
        done = f.start(step_terms("implement", "TSK-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        preambles = [values(call["argv"], "--append-system-prompt")[0] for call in f.calls()]
        self.assertEqual(len(preambles), 2)
        self.assertEqual(len(set(preambles)), 1)
        self.assertIn("`implement`", preambles[0])
        self.assertIn("TSK-0001", preambles[0])

    def test_done_work_makes_no_call(self):
        """TSK-3410 criterion 10: an `implement` run whose work is done and whose verbs pass ends `finished` with no
        call."""
        f = self.fixture({"done.flag": "x"})
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
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
        self.assertEqual([line["sum_usd"] for line in lines], [0.25, 0.5])


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
                                     "--setting-sources", "project", "--plugin-dir", str(UNIT),
                                     "--plugin-dir", "/somewhere/else",
                                     "--permission-mode", "dontAsk", "--allowedTools", "Read",
                                     *allow_rules(progress / "progress.md"),
                                     "--permission-prompts", "none", "--add-dir", str(progress),
                                     "--max-budget-usd", "10",
                                     "--disallowedTools", "Bash(meow-loop *)", "Bash(meow loop *)",
                                     "--append-system-prompt"])
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
        # The state directory is named through a link, so a path taken as typed differs from the resolved one the
        # run's directory is read by below.
        link = f.base / "link"
        link.symlink_to(f.state)
        done = f.start(terms, env={**f.env(), "MEOWPAW_STATE_DIR": str(link)})
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        calls = f.calls()
        self.assertEqual(len(calls), 2)
        file = f.run_dirs()[0] / "progress" / "progress.md"
        self.assertTrue(file.is_absolute())
        self.assertNotIn("link", file.parts)
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


class Budget(Case):
    """ADR-2010: the runner checks the budget before each call, and ends a run whose spend it can't count."""

    def run_of(self, iterations="10", budget="1.00", **config):
        """A run with a budget of 1.00, or the one named, whose verb never passes, and its calls, its log's lines
        and its result."""
        f = self.fixture()
        f.configure(**config)
        terms = replaced("--budget-usd", budget)
        terms[terms.index("--iterations") + 1] = iterations
        done = f.start(terms)
        log = f.run_dirs()[0] / "log.jsonl"
        return f, done, [json.loads(line) for line in log.read_text().splitlines()]

    def test_forecast_before_the_call(self):
        """TSK-3370 criterion 1, REQ-0878 and the budget halves of REQ-0870 and REQ-0876: with a budget of 1.00 and
        a stand-in that ignores its cap, a run costing 0.60 a call makes one call and ends `budget`, and one costing
        0.30 a call makes three and never starts the fourth. Three more runs pin the forecast: 0.50 a call lands on
        the budget, so the second call starts and the third doesn't; a first call of 0.40 followed by calls of 0.10
        makes four calls, where a forecast from the last call's cost makes seven; and a budget of 0.3 with calls
        of 0.1 makes three, though 0.2 + 0.1 is above 0.3 in binary floating point."""
        runs = (({"cost": 0.60}, "1.00", 1), ({"cost": 0.30}, "1.00", 3), ({"cost": 0.50}, "1.00", 2),
                ({"cost": 0.10, "costs": {"1": 0.40}}, "1.00", 4), ({"cost": 0.1}, "0.3", 3))
        matched = 0
        for config, budget, calls in runs:
            f, done, lines = self.run_of(budget=budget, **config)
            self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
            self.assertEqual(len(f.calls()), calls, config)
            self.assertEqual(len(lines), calls, config)
            self.assertEqual(f.ending(), "budget")
            self.assertEqual(done.stdout.strip().splitlines()[-1], "budget")
            matched += 1
        self.assertEqual(matched, 5)

    def test_unmetered(self):
        """TSK-3370 criterion 2: a call that prints no result, and one whose result has no `total_cost_usd`, each
        end the run `unmetered` after that one call, and its line in the log holds no sum. A result with no cost
        and the subtype of a reached cap ends `unmetered` too, because the cost is read first."""
        matched = 0
        for config in ({"silent": True}, {"no_cost": True}, {"no_cost": True, "subtype": "error_max_budget_usd"}):
            f, done, lines = self.run_of(**config)
            self.assertEqual(done.returncode, 1, str(config) + done.stdout + done.stderr)
            self.assertEqual(len(f.calls()), 1, config)
            self.assertEqual(f.ending(), "unmetered")
            self.assertEqual(done.stdout.strip().splitlines()[-1], "unmetered")
            self.assertEqual(len(lines), 1, config)
            self.assertIsNone(lines[0]["condition"])
            self.assertIn("sum_usd", lines[0])
            self.assertIsNone(lines[0]["sum_usd"])
            matched += 1
        self.assertEqual(matched, 3)

    def test_platform_cap_ends_the_run(self):
        """TSK-3370 criterion 3: a call costing 0.01 whose result has the subtype `error_max_budget_usd` ends the
        run `budget` after that one call, where the forecast can't."""
        f, done, lines = self.run_of(cost=0.01, subtype="error_max_budget_usd")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(len(f.calls()), 1)
        self.assertEqual(f.ending(), "budget")
        self.assertEqual(done.stdout.strip().splitlines()[-1], "budget")

    def test_cap_is_the_budget_left(self):
        """TSK-3370 criterion 4: over two calls at 0.30, `--max-budget-usd` is 1.00 and then 0.70, as numbers."""
        f, done, lines = self.run_of(iterations="2", cost=0.30)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "ceiling")
        caps = [values(call["argv"], "--max-budget-usd") for call in f.calls()]
        self.assertEqual([len(cap) for cap in caps], [1, 1])
        for cap, expected in zip(caps, (1.00, 0.70)):
            self.assertAlmostEqual(float(cap[0]), expected, delta=0.000001)

    def test_sum_so_far_is_logged(self):
        """TSK-3370 criterion 5: over three calls at 0.30, the log's lines carry the sums 0.30, 0.60 and 0.90, as
        numbers."""
        f, done, lines = self.run_of(cost=0.30)
        self.assertEqual(len(lines), 3)
        for line, expected in zip(lines, (0.30, 0.60, 0.90)):
            self.assertAlmostEqual(line["sum_usd"], expected, delta=0.000001)


class Idle(Case):
    """ADR-2010: two iterations in a row that change neither the tree nor the progress file end the run `idle`."""

    def run_of(self, f, iterations, **config):
        """A run whose verb never passes and whose stand-in edits no file unless `config` says so, as its result
        and its log's lines."""
        f.configure(edit=False, **config)
        done = f.start(replaced("--iterations", iterations))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        log = f.run_dirs()[0] / "log.jsonl"
        return done, [json.loads(line) for line in log.read_text().splitlines()]

    def test_two_idle_iterations_end_the_run(self):
        """TSK-3380 criterion 1, REQ-0886: a stand-in that changes nothing ends the run `idle` after two of five
        calls, and each line of the log records that the progress file didn't change."""
        f = self.fixture()
        done, lines = self.run_of(f, "5")
        self.assertEqual(len(f.calls()), 2)
        self.assertEqual(f.ending(), "idle")
        self.assertEqual(done.stdout.strip().splitlines()[-1], "idle")
        self.assertEqual([line["progress_changed"] for line in lines], [False, False])
        self.assertEqual([line["unidentified"] for line in lines], [False, False])

    def test_progress_alone_is_a_change(self):
        """TSK-3380 criterion 2, REQ-0886: a stand-in that writes only the progress file is never idle, so four
        calls run to the ceiling, and each line records that the progress file changed."""
        f = self.fixture()
        done, lines = self.run_of(f, "4", progress=True)
        self.assertEqual(len(f.calls()), 4)
        self.assertEqual(f.ending(), "ceiling")
        self.assertEqual([line["progress_changed"] for line in lines], [True] * 4)
        for line in lines:
            self.assertEqual(line["tree_before"], line["tree_after"])

    def test_idle_iterations_must_be_consecutive(self):
        """TSK-3380 criterion 3, REQ-0886: nothing on the first call, a tracked file on the second and nothing on
        the third and fourth ends the run `idle` after the fourth of six calls."""
        f = self.fixture()
        done, lines = self.run_of(f, "6", overwrite={"2": "prompt.md"})
        self.assertEqual(len(f.calls()), 4)
        self.assertEqual(f.ending(), "idle")
        changed = [line["tree_before"] != line["tree_after"] for line in lines]
        self.assertEqual(changed, [False, True, False, False])

    def test_a_removed_progress_file_can_go_idle(self):
        """TSK-3380, REQ-0886: a call that removes the progress file changes it, and two calls after it that change
        nothing, with the file absent before and after each, end the run `idle`."""
        f = self.fixture()
        done, lines = self.run_of(f, "6", remove_progress={"1": True})
        self.assertEqual(len(f.calls()), 3)
        self.assertEqual(f.ending(), "idle")
        self.assertEqual([line["progress_changed"] for line in lines], [True, False, False])

    def test_unidentified_tree_is_a_change(self):
        """TSK-3380 criterion 4, SPC-1201 "The loop": with a dirty submodule the tree id is `none` on every call,
        which counts as a change, so three calls run to the ceiling and each line is marked `unidentified`."""
        f = self.fixture()
        origin = f.base / "sub-origin"
        origin.mkdir()
        (origin / "a.txt").write_text("a\n")
        identity = ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.com", "-c", "commit.gpgsign=false"]
        for args in (["init", "-q", "-b", "main"], ["add", "-A"], [*identity, "commit", "-q", "-m", "sub"]):
            subprocess.run(["git", *args], cwd=origin, check=True, capture_output=True, env=f.env())
        f.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", str(origin), "sub")
        f.git(*identity, "commit", "-q", "-m", "add the submodule")
        (f.root / "sub" / "a.txt").write_text("changed\n")
        done, lines = self.run_of(f, "3")
        self.assertEqual(len(f.calls()), 3)
        self.assertEqual(f.ending(), "ceiling")
        self.assertEqual([line["unidentified"] for line in lines], [True] * 3)
        self.assertEqual([line["tree_after"] for line in lines], ["none"] * 3)
        self.assertEqual([line["progress_changed"] for line in lines], [False] * 3)


class Unchanged(Case):
    def test_an_unchanged_tree_skips_the_verbs(self):
        f = self.fixture()
        f.configure(edit=False)
        # TSK-3380: two calls are the ceiling too, so the run ends `idle` only where the idle check comes after the
        # call and before the ceiling is checked again.
        done = f.start(replaced("--iterations", "2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(len(f.calls()), 2)
        self.assertEqual(f.ending(), "idle")
        log = f.run_dirs()[0] / "log.jsonl"
        lines = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual(len(lines), 2)
        for line in lines:
            self.assertIsNone(line["condition"])
            self.assertEqual(line["tree_before"], line["tree_after"])
        ledger = f.state / "evidence" / f"{f.key()}.jsonl"
        records = {entry["record"] for entry in map(json.loads, ledger.read_text().splitlines())
                   if entry["verb"] == "test"}
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
