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
    f.write(json.dumps({"n": n, "argv": sys.argv[1:], "stdin": stdin, "run": os.environ.get("MEOW_LOOP_RUN")}) + "\\n")
if config.get("edit", True):
    # A step that writes only records may not touch the work tree's root, so its calls edit a file under the record
    # root that is no record. An implement step may write anywhere.
    import tomllib
    step = "implement"
    if "--add-dir" in sys.argv:
        run_dir = os.path.dirname(sys.argv[sys.argv.index("--add-dir") + 1])
        step = tomllib.load(open(os.path.join(run_dir, "run.toml"), "rb"))["step"]
    with open("work.txt" if step == "implement" else "project/work.txt", "a") as f:
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
for name in config.get("delete", {}).get(str(n), []):
    os.remove(name)
for old, new in config.get("rename", {}).get(str(n), {}).items():
    os.rename(old, new)
for name, text in config.get("write", {}).get(str(n), {}).items():
    os.makedirs(os.path.dirname(name) or ".", exist_ok=True)
    open(name, "w").write(text)
ledger = config.get("ledger", {}).get(str(n))
if ledger:
    import shutil, subprocess, tempfile
    git = lambda *args, **env: subprocess.run(["git", *args], capture_output=True, text=True,
                                              env={**os.environ, **env}).stdout.strip()
    # The tree id the work tree has once this call's edits are made, read as the ledger reads it.
    index = git("rev-parse", "--path-format=absolute", "--git-path", "index")
    handle, scratch = tempfile.mkstemp()
    os.close(handle)
    try:
        shutil.copy(index, scratch)
        git("add", "--all", "--", ".", GIT_INDEX_FILE=scratch)
        tree = git("write-tree", GIT_INDEX_FILE=scratch)
    finally:
        os.remove(scratch)
    filled = {"@tree": tree, "@repository": git("rev-list", "--max-parents=0", "HEAD"),
              "@work_tree": os.path.realpath(".")}
    line = {key: filled.get(value, value) if isinstance(value, str) else value
            for key, value in ledger["line"].items()}
    os.makedirs(os.path.dirname(ledger["path"]), exist_ok=True)
    with open(ledger["path"], "a") as f:
        f.write(json.dumps(line) + "\\n")
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

# `[verbs]` comes last, so a check that appends a verb's line to the profile adds it to that table.
PROFILE = '[git]\ntrunk = "main"\n\n[verbs]\ntest = "test -f done.flag"\n'
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
            + "\n# A plan\n\n## Acceptance criteria\n\n1. It works.\n\n## Tasks\n\n"
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
        env = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "MEOWPAW_STATE", "XDG_STATE_HOME", "MEOW_LOOP_RUN")}
        env.update(PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}", HOME=str(self.home),
                   MEOWPAW_STATE_DIR=str(self.state), FAKE_CLAUDE=str(self.config),
                   GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", **more)
        return env

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, env=self.env())

    def start(self, terms=None, cwd=None, env=None, **more):
        # The output lands in files, not pipes: a run the timeout kills leaves a
        # call still running, and a pipe that call inherited never closes, which
        # hangs the drain in place of a failed assertion.
        out = tempfile.TemporaryFile()
        err = tempfile.TemporaryFile()
        try:
            done = subprocess.run([str(BIN), "start", *(TERMS if terms is None else terms)], cwd=cwd or self.root,
                                  env=env or self.env(**more), stdout=out, stderr=err, timeout=600)
            out.seek(0)
            err.seek(0)
            done.stdout = out.read().decode(errors="replace")
            done.stderr = err.read().decode(errors="replace")
        finally:
            out.close()
            err.close()
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

    def dirty(self, f):
        """A dirty submodule in the fixture's work tree, so its tree id is unidentified."""
        origin = f.base / "sub-origin"
        origin.mkdir()
        (origin / "a.txt").write_text("a\n")
        identity = ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.com", "-c", "commit.gpgsign=false"]
        for args in (["init", "-q", "-b", "main"], ["add", "-A"], [*identity, "commit", "-q", "-m", "sub"]):
            subprocess.run(["git", *args], cwd=origin, check=True, capture_output=True, env=f.env())
        f.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", str(origin), "sub")
        f.git(*identity, "commit", "-q", "-m", "add the submodule")
        (f.root / "sub" / "a.txt").write_text("changed\n")


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
        # The copy has no core unit beside it, so it finds the shared binary through the data file (REQ-4504).
        data = f.base / "data"
        (data / "meow-core-x").mkdir(parents=True)
        (data / "meow-core-x" / "meow-root").write_text(str(UNIT.parent / "meow-core") + "\n")
        done = subprocess.run([str(copy / "bin" / "meow-loop"), "start",
                               *replaced("--iterations", "2"), "--plugin-dir", "/a", "--plugin-dir", "/b"],
                              cwd=f.root, env=f.env(CLAUDE_PLUGIN_DATA=str(data / "meow-loop-x")),
                              capture_output=True, text=True, timeout=120)
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
                shutil.copy2(next((UNIT.parent / "meow-core" / "bin").glob("*-*/meow*")), stray)
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

    def edit(self, f, tool, run=True, **tool_input):
        """The hook's answer to `tool` with `tool_input`, inside a run unless `run` is false."""
        event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}
        env = f.env(MEOW_LOOP_RUN="00000000000000000001") if run else f.env()
        return subprocess.run([str(BIN), "guard"], input=json.dumps(event), capture_output=True, text=True,
                              env=env, cwd=f.root)

    def denied(self, done, what):
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        answer = json.loads(done.stdout)["hookSpecificOutput"]
        self.assertEqual((answer["hookEventName"], answer["permissionDecision"]), ("PreToolUse", "deny"), what)
        return answer["permissionDecisionReason"]

    def allowed(self, done, what):
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""), what)

    def reason(self, done, what, *names):
        """The denial's reason, which names every one of `names`."""
        reason = self.denied(done, what)
        for name in names:
            self.assertIn(name, reason, what)
        return reason

    def test_status_rule(self):
        """TSK-3430 criterion 1, REQ-0888: with `MEOW_LOOP_RUN` set, an Edit that gives a record a decided status is
        denied, naming the status and the file: approving a draft, setting a requirement `live`, withdrawing an
        approved record, an edit through a relative path or a link, `replace_all`, a status a record gained, a CRLF
        file, and an Edit with an empty `old_string` that creates a file. An Edit that leaves a status as it is,
        removes one, sits in a body fence or lies outside the record is allowed in silence, and so is every Edit
        without the variable."""
        f = self.fixture({"notes.md": "---\nstatus: draft\n---\nText\n",
                          "project/requirements/REQ-0005-no-status.md":
                          RECORD["project/requirements/REQ-0002-a-draft.md"].replace("status: draft\n", ""),
                          "project/requirements/REQ-0006-crlf.md":
                          RECORD["project/requirements/REQ-0002-a-draft.md"].replace("\n", "\r\n")})
        draft = f.root / "project/requirements/REQ-0002-a-draft.md"
        approved = f.root / "project/requirements/REQ-0001-a-duty.md"
        task_file = f.root / "project/tasks/TSK-0002-the-second.md"
        inside, outside = f.root / "project/requirements/REQ-0007-link.md", f.root / "project/requirements/REQ-0008-out.md"
        inside.symlink_to(draft)
        (f.base / "elsewhere.md").write_text("---\nstatus: draft\n---\nText\n")
        outside.symlink_to(f.base / "elsewhere.md")
        no_status = f.root / "project/requirements/REQ-0005-no-status.md"
        crlf = f.root / "project/requirements/REQ-0006-crlf.md"
        approve = ("status: draft", "status: approved")
        deny = (("approve a draft", draft, *approve, "approved"),
                ("set a requirement live", draft, "status: draft", "status: live", "live"),
                ("withdraw an approved record", approved, "status: approved", "status: withdrawn", "withdrawn"),
                ("approve through a relative path", Path("project/requirements/REQ-0002-a-draft.md"), *approve, "approved"),
                ("approve through a link into the record", inside, *approve, "approved"),
                ("approve with replace_all", draft, "draft", "approved", "approved"),
                ("give a record a status", no_status, "revised: 2026-01-01", "revised: 2026-01-01\nstatus: approved",
                 "approved"),
                ("approve a CRLF file", crlf, "status: draft\r\n", "status: approved\r\n", "approved"),
                ("approve a CRLF file across a line break", crlf, "status: draft\nrevised: 2026-01-01",
                 "status: approved\nrevised: 2026-01-01", "approved"),
                ("create a file with an empty old_string", f.root / "project/adrs/ADR-0009-new.md", "",
                 DRAFT_DECISION.replace("status: draft", "status: approved"), "approved"))
        allow = (("edit an approved task's Evidence", task_file, "Not yet.", "Not yet. More."),
                 ("keep an approved status", approved, "status: approved", "status: approved"),
                 ("edit a draft's body", draft, "# REQ-0002", "# REQ-0002 reworded"),
                 ("remove a status", approved, "status: approved\n", ""),
                 ("quote a status in a body fence", draft, "# REQ-0002", "# REQ-0002\n\n```\nstatus: approved\n```"),
                 ("edit a file outside the record", f.root / "notes.md", *approve),
                 ("approve through a link out of the record", outside, *approve),
                 ("edit with an old_string that isn't there", draft, "nothing like this", "status: approved"))
        denied = allowed = 0
        for what, path, old, new, status in deny:
            with self.subTest(what=what):
                done = self.edit(f, "Edit", file_path=str(path), old_string=old, new_string=new)
                # A denial names the file a link resolves to.
                self.reason(done, what, "decided status", status, (f.root / path).resolve().name)
                denied += 1
        for what, path, old, new in allow:
            with self.subTest(what=what):
                self.allowed(self.edit(f, "Edit", file_path=str(path), old_string=old, new_string=new), what)
                allowed += 1
        # Without the variable, a session writes an approval a person gave.
        for what, path, old, new, status in deny:
            with self.subTest(what=what, run=False):
                self.allowed(self.edit(f, "Edit", run=False, file_path=str(path), old_string=old, new_string=new), what)
                allowed += 1
        self.assertEqual((denied, allowed), (len(deny), len(allow) + len(deny)))

    def test_status_rule_with_an_empty_variable(self):
        """TSK-3430 criterion 1, REQ-0888: `MEOW_LOOP_RUN` set to an empty string counts as set, so the rule denies
        an Edit that approves a draft."""
        f = self.fixture()
        event = {"hook_event_name": "PreToolUse", "tool_name": "Edit",
                 "tool_input": {"file_path": str(f.root / "project/requirements/REQ-0002-a-draft.md"),
                                "old_string": "status: draft", "new_string": "status: approved"}}
        done = subprocess.run([str(BIN), "guard"], input=json.dumps(event), capture_output=True, text=True,
                              env=f.env(MEOW_LOOP_RUN=""), cwd=f.root)
        self.reason(done, "an empty variable", "decided status", "approved")

    def test_status_rule_on_write(self):
        """TSK-3430 criterion 2, REQ-0888: with `MEOW_LOOP_RUN` set, a Write whose content holds `status: approved`
        for a draft record is denied, and so is a Write of a new approved decision and of a CRLF file; a Write of a
        new specification with `status: live`, one that keeps a draft a draft, one that keeps an approved status,
        one to the index or to a file that is no record in a kind directory, and one outside the record are
        allowed."""
        f = self.fixture()
        draft_text = RECORD["project/requirements/REQ-0002-a-draft.md"]
        draft_file = f.root / "project/requirements/REQ-0002-a-draft.md"
        approved_text = RECORD[REQUIREMENT_FILE]
        spec = front(id="SPC-0002", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Another part\n"
        deny = (("approve a draft", draft_file, draft_text.replace("status: draft", "status: approved"), "approved"),
                ("write a new approved decision", f.root / "project/adrs/ADR-0002-new.md",
                 DRAFT_DECISION.replace("status: draft", "status: approved"), "approved"),
                ("write an approved CRLF file", draft_file,
                 draft_text.replace("status: draft", "status: approved").replace("\n", "\r\n"), "approved"))
        allow = (("write a new live specification", f.root / "project/specs/SPC-0002-new.md", spec),
                 ("keep a draft a draft", draft_file, draft_text + "\nMore.\n"),
                 ("keep an approved status", f.root / REQUIREMENT_FILE, approved_text + "\nMore.\n"),
                 ("write an index", f.root / "project/requirements/README.md", approved_text),
                 ("write a file that is no record", f.root / "project/requirements/notes.txt", approved_text),
                 ("write outside the record", f.root / "notes.md", "---\nstatus: approved\n---\n"))
        denied = allowed = 0
        for what, path, content, status in deny:
            with self.subTest(what=what):
                self.reason(self.edit(f, "Write", file_path=str(path), content=content), what, "decided status",
                            status, path.name)
                denied += 1
        for what, path, content in allow:
            with self.subTest(what=what):
                self.allowed(self.edit(f, "Write", file_path=str(path), content=content), what)
                allowed += 1
        self.assertEqual((denied, allowed), (len(deny), len(allow)))

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
        # Every field a real line holds, at the tree the call leaves, so a runner that read passes back would
        # take this one.
        line = {"record": "0123456789ab", "phase": "ended", "verb": "test", "command": "test -f done.flag",
                "outcome": "passed", "status": 0, "time": "2026-01-01T00:00:00Z", "tree_before": "@tree",
                "tree": "@tree", "targets": None, "repository": "@repository", "work_tree": "@work_tree"}
        f.configure(ledger={str(n): {"path": str(ledger), "line": line} for n in (1, 2, 3)})
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "ceiling")
        self.assertEqual(len(f.calls()), 3)
        forged = [json.loads(text)["tree"] for text in ledger.read_text().splitlines() if "0123456789ab" in text]
        logged = [json.loads(text)["tree_after"] for text in (f.run_dirs()[0] / "log.jsonl").read_text().splitlines()]
        # Each forged line sits at the tree the runner read after that call.
        self.assertEqual(len(forged), 3)
        self.assertEqual(forged, logged)

    def test_repeat_once_after_a_write(self):
        """TSK-3410 criterion 3, REQ-0884: a verb that rewrites a tracked file on its first run and exits 0 ends the
        run `finished` after the evaluation is repeated once."""
        settle = "grep -q formatted f.txt || echo formatted > f.txt"
        f = self.fixture({".meowpaw/profile.toml": f'[verbs]\ntest = "{settle}"\n', "f.txt": "plain\n"})
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
        self.dirty(f)
        done = f.start(step_terms("implement", "TSK-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        # An unidentified tree ends no `implement` run `off-step`: its paths outside the record are its to write.
        self.assertEqual(f.ending(), "ceiling")
        lines = [json.loads(line) for line in (f.run_dirs()[0] / "log.jsonl").read_text().splitlines()]
        self.assertTrue(lines)
        self.assertTrue(all(line["unidentified"] for line in lines))

    def test_dropped_is_not_done(self):
        """TSK-3410 criterion 5, REQ-0884: a call that marks the input task `~`, dropped, doesn't finish an
        `implement` run, though the verb passes."""
        f = self.fixture()
        # The Evidence is written too, so the mark alone keeps the run from finishing.
        f.configure(write={"1": {"project/epics/EPC-0001-a-plan.md": epic("x", "~"),
                                 "project/tasks/TSK-0002-the-second.md": task("TSK-0002", "Done.")}},
                    create={"1": "done.flag"})
        done = f.start(step_terms("implement", "TSK-0002", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "ceiling")
        self.assertEqual(len(f.calls()), 2)

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
                 (["--step", "research", "--inputs", ""] + rest, "usage: research takes no --inputs"),
                 (["--step", "design", "--inputs", " , "] + rest, "usage: --step design needs --inputs"),
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

    def test_inputs_are_trimmed(self):
        """TSK-3410: each input is read without the spaces around it, so `TSK-0001, ` names TSK-0001."""
        f = self.fixture({"done.flag": "x"})
        done = f.start(step_terms("implement", " TSK-0001, "))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        table = tomllib.loads((f.run_dirs()[0] / "run.toml").read_text())
        self.assertEqual(table["inputs"], ["TSK-0001"])

    def test_absolute_record_root(self):
        """TSK-3410 criterion 6: an absolute `[record] root` inside the work tree starts a run, and one outside it
        is refused as outside the work tree."""
        f = self.fixture({"done.flag": "x"})
        profile = f.root / ".meowpaw" / "profile.toml"
        profile.write_text(PROFILE + f'\n[record]\nroot = "{f.root / "project"}"\n')
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        elsewhere = f.base / "elsewhere"
        shutil.copytree(f.root / "project", elsewhere)
        profile.write_text(PROFILE + f'\n[record]\nroot = "{elsewhere}"\n')
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn(f"unresolved: record root {elsewhere} is outside the work tree", done.stdout)
        self.assertEqual(len(f.run_dirs()), 1)

    def test_wrong_kind_input_is_refused(self):
        """TSK-4050 criterion 1, REQ-1240: an input of the wrong kind for each step that takes inputs ends `start`
        with exit 3, the line naming the input, its kind and what the step reads, and no run directory."""
        cases = (("requirements", "REQ-0001", "REQ-0001, a requirement, is not a research, which a requirements run reads"),
                 ("design", "RES-0001", "RES-0001, a research, is not a requirement, which a design run reads"),
                 ("spec", "REQ-0001", "REQ-0001, a requirement, is not a decision, which a spec run reads"),
                 ("epic", "REQ-0001", "REQ-0001, a requirement, is not a decision, which an epic run reads"),
                 ("implement", "ADR-0001", "ADR-0001, a decision, is not a task, which an implement run reads"),
                 # A draft input of the wrong kind gets the kind line alone, because the reader fixes the kind.
                 ("spec", "REQ-0002", "REQ-0002, a requirement, is not a decision, which a spec run reads"))
        matched = 0
        for step, input, line in cases:
            with self.subTest(step=step):
                f = self.fixture()
                done = f.start(step_terms(step, input))
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                self.assertIn(f"unresolved: {line}", done.stdout)
                self.assertEqual(done.stdout.count("unresolved:"), 1, done.stdout)
                # The refusal comes before the lock, so not even the lock file's directory exists.
                self.assertFalse(f.runs_dir().exists())
                self.assertEqual(f.run_dirs(), [])
                self.assertEqual(f.calls(), [])
                matched += 1
        self.assertEqual(matched, 6)

    def test_an_input_with_no_file_keeps_its_own_line(self):
        """TSK-4050 criterion 1, REQ-1240: an input with no file is `paw ready`'s report and not a wrong kind, and in
        a list the wrong-kind line and the missing-file line each appear once."""
        f = self.fixture()
        done = f.start(step_terms("spec", "ADR-9999"))
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: ADR-9999 has no file", done.stdout)
        self.assertNotIn("is not a", done.stdout)
        g = self.fixture()
        done = g.start(step_terms("design", "REQ-0001,RES-0001,REQ-7777"))
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertEqual(done.stdout.count("RES-0001, a research, is not a requirement, which a design run reads"), 1)
        self.assertEqual(done.stdout.count("unresolved: REQ-7777 has no file"), 1)
        self.assertNotIn("REQ-0001,", done.stdout)

    def test_a_repeated_input_is_read_once(self):
        """SPC-1201 "The terms", REQ-1240: an input named twice is one input, so `run.toml` lists it once and a
        refusal prints its line once."""
        f = self.fixture({"done.flag": "x"})
        done = f.start(step_terms("implement", "TSK-0001,TSK-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        table = tomllib.loads((f.run_dirs()[0] / "run.toml").read_text())
        self.assertEqual(table["inputs"], ["TSK-0001"])
        g = self.fixture()
        done = g.start(step_terms("design", "RES-0001,RES-0001"))
        self.assertEqual(done.stdout.count("RES-0001, a research, is not a requirement"), 1, done.stdout)

    def test_right_kind_input_is_not_refused(self):
        """TSK-4050 criterion 2, REQ-1240: an input of the right kind for each of the five steps that take inputs
        is refused on no account of its kind, so `start` makes its call."""
        matched = 0
        for step, input in (("requirements", "RES-0001"), ("design", "REQ-0001"), ("spec", "ADR-0001"),
                            ("epic", "ADR-0001"), ("implement", "TSK-0001")):
            with self.subTest(step=step):
                f = self.fixture()
                done = f.start(step_terms(step, input, iterations="1"))
                self.assertNotIn("unresolved", done.stdout, done.stdout + done.stderr)
                self.assertEqual(len(f.calls()), 1)
                matched += 1
        self.assertEqual(matched, 5)

    @unittest.skipIf(os.geteuid() == 0, "a file's mode doesn't stop the superuser reading it")
    def test_unreadable_record_file_is_refused(self):
        """TSK-4050 criterion 3, REQ-1240: a Markdown file under the record root that can't be read ends `start`
        with exit 3, the line naming the file, and no run directory."""
        f = self.fixture()
        path = f.root / "project/requirements/REQ-0002-a-draft.md"
        path.chmod(0)
        try:
            done = f.start(step_terms("implement", "TSK-0001"))
        finally:
            path.chmod(0o644)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: record file project/requirements/REQ-0002-a-draft.md can't be read:", done.stdout)
        self.assertFalse(f.runs_dir().exists())
        self.assertEqual(f.run_dirs(), [])
        self.assertEqual(f.calls(), [])

    def test_run_toml_holds_the_step(self):
        """TSK-3410 criterion 6: `run.toml` holds the step as a string and the inputs as a list."""
        f = self.fixture({"done.flag": "x"})
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        table = tomllib.loads((f.run_dirs()[0] / "run.toml").read_text())
        self.assertEqual((table["step"], table["inputs"]), ("implement", ["TSK-0001"]))

    def test_run_id_in_every_call(self):
        """TSK-3430 criterion 3, REQ-0888: each call's environment holds `MEOW_LOOP_RUN` equal to the run's id."""
        f = self.fixture()
        done = f.start(step_terms("implement", "TSK-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        calls = f.calls()
        self.assertEqual(len(calls), 2)
        self.assertEqual([call["run"] for call in calls], [f.run_dirs()[0].name] * 2)

    def test_run_id_only_in_calls(self):
        """TSK-3430 criterion 3, REQ-0888: the verbs, which the runner runs outside a call, see no `MEOW_LOOP_RUN`,
        so the variable is set in a call's environment and not in the runner's."""
        f = self.fixture()
        seen = f.base / "seen"
        script = f.base / "verb.sh"
        script.write_text(f'echo "[$MEOW_LOOP_RUN]" >> {seen}\ntest -f done.flag\n')
        (f.root / ".meowpaw" / "profile.toml").write_text(PROFILE.replace('test -f done.flag', f"sh {script}"))
        done = f.start(step_terms("implement", "TSK-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        lines = seen.read_text().splitlines()
        self.assertGreaterEqual(len(lines), 2)
        self.assertEqual(set(lines), {"[]"})

    def test_spec_run_finishes(self):
        """TSK-3410 criterion 7: a call that writes a new specification stating each requirement the input decision
        addresses, while the verb passes, finishes a `spec` run."""
        f = self.fixture({"done.flag": "x"})
        spec = front(id="SPC-0002", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Another part\n"
        f.configure(write={"1": {"project/specs/SPC-0002-another.md": spec}})
        done = f.start(step_terms("spec", "ADR-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
        self.assertEqual(len(f.calls()), 1)

    def test_spec_run_over_no_requirement_never_finishes(self):
        """TSK-3410 criterion 7: a `spec` run over a decision that addresses nothing never finishes, though a call
        writes a specification and the verb passes. An input that is no decision is refused at start since
        TSK-4050, which `test_wrong_kind_input_is_refused` checks."""
        decision = front(id="ADR-0002", artifact="adr", status="approved", revised="2026-01-01", addresses="[]",
                         supersedes="[]") + "\n# 0002. Another choice\n"
        spec = front(id="SPC-0002", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Another part\n"
        f = self.fixture({"done.flag": "x", "project/adrs/ADR-0002-another.md": decision})
        f.configure(write={"1": {"project/specs/SPC-0002-another.md": spec}})
        done = f.start(step_terms("spec", "ADR-0002", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "ceiling")
        self.assertEqual(len(f.calls()), 2)

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

    def test_layout_is_meow_flows(self):
        """TSK-3410: the layout `meow-loop` ships is byte for byte the one `meow-flow` ships, so the run reads the
        record as `paw` reads it."""
        ours = (UNIT / "lib" / "layout.toml").read_bytes()
        self.assertTrue(ours)
        self.assertEqual(ours, (UNIT.parent / "meow-flow" / "lib" / "layout.toml").read_bytes())

    def test_done_work_makes_no_call(self):
        """TSK-3410 criterion 10: an `implement` run whose work is done and whose verbs pass ends `finished` with no
        call."""
        f = self.fixture({"done.flag": "x"})
        done = f.start(step_terms("implement", "TSK-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
        self.assertEqual(f.calls(), [])


DRAFT_DECISION = front(id="ADR-0002", artifact="adr", status="draft", revised="2026-01-01", addresses="[REQ-0002]",
                       supersedes="[]") + "\n# 0002. A draft\n"
DECISION_FILE = "project/adrs/ADR-0002-a-draft.md"
REQUIREMENT_FILE = "project/requirements/REQ-0001-a-duty.md"
DEFECT_FILE = "project/bugs/BUG-0001-a-defect.md"
DEFECT = (front(id="BUG-0001", artifact="bug", status="approved", severity="minor", violates="REQ-0001",
                enters="implement", found="2026-01-01", revised="2026-01-01")
          + "\n# A defect\n\nIt is broken.\n\n## Reproduction\n\nRun it.\n\n## Tasks\n\n- [ ] T-001 TSK-0003 fix it\n")
DEFECT_TASK = task("TSK-0003", "Not yet.").replace("epic: EPC-0001", "bug: BUG-0001")


class Crossed(Case):
    """ADR-2020: a call or an evaluation that decides a status, or changes or removes an approved record outside what
    the step may change in it, ends the run `crossed`, and the last line names each record."""

    def crossed(self, f, done, *names, calls=1, found="after iteration 1", other=()):
        """The run ended `crossed` after `calls` calls, and its last line starts with `found` and names every record
        in `names` and none in `other`, so a bystander named as well fails."""
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "crossed")
        last = done.stdout.strip().splitlines()[-1]
        self.assertTrue(last.startswith(f"crossed: {found}"), last)
        for name in names:
            self.assertIn(name, last)
        for name in other:
            self.assertNotIn(name, last)
        self.assertEqual(len(f.calls()), calls)

    def design(self, f, **config):
        f.configure(**config)
        return f.start(step_terms("design", "REQ-0001"))

    def test_decided_status(self):
        """TSK-3420 criterion 1, REQ-0888: a call that sets a draft decision's status to `approved` ends a `design`
        run `crossed` after that call, and the last line names the decision."""
        f = self.fixture({DECISION_FILE: DRAFT_DECISION})
        done = self.design(f, write={"1": {DECISION_FILE: DRAFT_DECISION.replace("status: draft", "status: approved")}})
        self.crossed(f, done, "ADR-0002", other=("ADR-0001", "REQ-0001", "TSK-0001"))

    def test_withdrawal(self):
        """TSK-3420 criterion 1, REQ-0888: a call that sets an approved requirement to `withdrawn` ends the run
        `crossed`, though the frozen comparison accepts a withdrawal."""
        f = self.fixture()
        text = RECORD[REQUIREMENT_FILE].replace("status: approved", "status: withdrawn")
        self.crossed(f, self.design(f, write={"1": {REQUIREMENT_FILE: text}}), "REQ-0001")

    def test_authority_line(self):
        """TSK-3420 criterion 1, REQ-0888: a call that appends to an approved requirement a line naming an
        amendment ends the run `crossed`, though the frozen comparison accepts that line."""
        f = self.fixture()
        text = RECORD[REQUIREMENT_FILE] + "\nAmended by ADR-0002.\n"
        self.crossed(f, self.design(f, write={"1": {REQUIREMENT_FILE: text}}), "REQ-0001")

    def test_removed(self):
        """TSK-3420 criterion 1, REQ-0888: a call that deletes an approved requirement ends the run `crossed`,
        naming it."""
        f = self.fixture()
        self.crossed(f, self.design(f, delete={"1": [REQUIREMENT_FILE]}), "REQ-0001")

    def test_renamed(self):
        """TSK-3420 criterion 1, REQ-0888: a call that renames an approved requirement ends the run `crossed`,
        naming it."""
        f = self.fixture()
        moved = "project/requirements/REQ-0001-another-name.md"
        self.crossed(f, self.design(f, rename={"1": {REQUIREMENT_FILE: moved}}), "REQ-0001")

    def test_epic_allowances(self):
        """TSK-3420 criterion 2, REQ-0888: in an `implement` run, rewording a criterion of the approved epic ends the
        run `crossed` naming the epic, and marking the input task `x` there and changing nothing else does not."""
        epic_file = "project/epics/EPC-0001-a-plan.md"
        f = self.fixture()
        reworded = epic("x", "x").replace("1. It works.", "1. It works well.")
        f.configure(write={"1": {epic_file: reworded, "project/tasks/TSK-0002-the-second.md": task("TSK-0002", "Done.")}})
        self.crossed(f, f.start(step_terms("implement", "TSK-0002")), "EPC-0001")
        marked = self.fixture()
        marked.configure(write={"1": {epic_file: epic("x", "x"),
                                      "project/tasks/TSK-0002-the-second.md": task("TSK-0002", "Done.")}},
                         create={"1": "done.flag"})
        done = marked.start(step_terms("implement", "TSK-0002"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(marked.ending(), "finished")

    def test_defect_allowances(self):
        """TSK-3420 criterion 2, REQ-0888: in an `implement` run of a task an approved defect authorises, marking the
        task `x` in the defect does not end the run `crossed`, and rewording the defect's reproduction does."""
        files = {DEFECT_FILE: DEFECT, "project/tasks/TSK-0003-the-third.md": DEFECT_TASK}
        done_task = {"project/tasks/TSK-0003-the-third.md": task("TSK-0003", "Done.").replace("epic: EPC-0001",
                                                                                           "bug: BUG-0001")}
        marked = DEFECT.replace("- [ ] T-001", "- [x] T-001")
        f = self.fixture(files)
        f.configure(write={"1": {DEFECT_FILE: marked, **done_task}}, create={"1": "done.flag"})
        done = f.start(step_terms("implement", "TSK-0003"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
        g = self.fixture(files)
        g.configure(write={"1": {DEFECT_FILE: marked.replace("Run it.", "Run it twice."), **done_task}},
                    create={"1": "done.flag"})
        self.crossed(g, g.start(step_terms("implement", "TSK-0003")), "BUG-0001")

    def test_crossed_with_unidentified_tree(self):
        """TSK-3420 criterion 3, REQ-0888: with a dirty submodule, a call that sets a draft decision to `approved`
        still ends a `design` run `crossed`, because the comparison is skipped only for two equal identified trees."""
        f = self.fixture({DECISION_FILE: DRAFT_DECISION})
        self.dirty(f)
        done = self.design(f, write={"1": {DECISION_FILE: DRAFT_DECISION.replace("status: draft", "status: approved")}})
        self.crossed(f, done, "ADR-0002")

    def test_live_only_in_a_living_kind(self):
        """TSK-3420 criterion 4, REQ-0888: in a `spec` run, setting a draft requirement's status to `live` ends the
        run `crossed`, and writing a new specification with status `live` does not."""
        f = self.fixture()
        f.configure(write={"1": {"project/requirements/REQ-0002-a-draft.md":
                                 RECORD["project/requirements/REQ-0002-a-draft.md"].replace("status: draft",
                                                                                          "status: live")}})
        self.crossed(f, f.start(step_terms("spec", "ADR-0001")), "REQ-0002")
        g = self.fixture({"done.flag": "x"})
        spec = front(id="SPC-0002", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Another part\n"
        g.configure(write={"1": {"project/specs/SPC-0002-another.md": spec}})
        done = g.start(step_terms("spec", "ADR-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(g.ending(), "finished")

    def test_drafts_and_task_evidence_cross_nothing(self):
        """TSK-3420 criterion 1, REQ-0888: a new draft and an edit to a draft cross nothing in a `design` run, and a
        change to an approved task's Evidence crosses nothing in an `implement` run, where a `design` run that
        writes it ends `off-step` and not `crossed`."""
        f = self.fixture({DECISION_FILE: DRAFT_DECISION})
        f.configure(write={"1": {DECISION_FILE: DRAFT_DECISION + "\nMore.\n",
                                 "project/adrs/ADR-0003-new.md": DRAFT_DECISION.replace("0002", "0003")}})
        done = f.start(step_terms("design", "REQ-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "ceiling")
        # The writes landed, so the run crossed nothing though it changed two records.
        self.assertIn("More.", (f.root / DECISION_FILE).read_text())
        self.assertTrue((f.root / "project/adrs/ADR-0003-new.md").exists())
        # A task's Evidence is an `implement` run's to write, and a `design` run that writes it is off its step.
        h = self.fixture()
        h.configure(write={"1": {"project/tasks/TSK-0002-the-second.md": task("TSK-0002", "Not yet.\n\nMore.")}})
        done = h.start(step_terms("design", "REQ-0001"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(h.ending(), "off-step")
        g = self.fixture()
        g.configure(write={"1": {"project/tasks/TSK-0002-the-second.md": task("TSK-0002", "Not yet.\n\nMore.")}})
        done = g.start(step_terms("implement", "TSK-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(g.ending(), "ceiling")
        self.assertIn("More.", (g.root / "project/tasks/TSK-0002-the-second.md").read_text())

    def test_evaluation_crosses(self):
        """TSK-3420 criterion 5, REQ-0888: a verb whose command withdraws an approved requirement on its second run
        and not its first ends the run `crossed` in the evaluation after the call, and the last line names the
        evaluation, the verb and the record, not a call."""
        f = self.fixture()
        count = f.base / "count"
        script = f.base / "verb.sh"
        script.write_text(
            f"n=$(cat {count} 2>/dev/null || echo 0)\necho $((n + 1)) > {count}\n"
            f"if [ \"$n\" -ge 1 ]; then\n  sed 's/^status: approved/status: withdrawn/' {REQUIREMENT_FILE} > tmp.md\n"
            f"  mv tmp.md {REQUIREMENT_FILE}\nfi\nexit 1\n")
        (f.root / ".meowpaw" / "profile.toml").write_text(PROFILE.replace('test -f done.flag', f"sh {script}"))
        done = f.start(step_terms("design", "REQ-0001"))
        self.crossed(f, done, "REQ-0001", found="in the evaluation after iteration 1, stage test")

    def test_a_verb_that_leaves_the_record_alone_crosses_nothing(self):
        """TSK-3420 criterion 5, REQ-0888: a verb that changes the tree on its second run and leaves every record as
        it was does not end the run `crossed`. The check pins that outcome and no other."""
        f = self.fixture()
        count = f.base / "count"
        script = f.base / "verb.sh"
        script.write_text(f"n=$(cat {count} 2>/dev/null || echo 0)\necho $((n + 1)) > {count}\n"
                          "if [ \"$n\" -ge 1 ]; then echo more >> side.txt; fi\nexit 1\n")
        (f.root / ".meowpaw" / "profile.toml").write_text(PROFILE.replace('test -f done.flag', f"sh {script}"))
        done = f.start(step_terms("design", "REQ-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "ceiling")
        self.assertTrue((f.root / "side.txt").exists())

    def test_new_records_with_a_decided_status(self):
        """TSK-3420 criterion 1, REQ-0888: a call that writes a new approved decision, or a new requirement with
        status `live`, ends the run `crossed` naming it, because a record new since start carries a decided
        status."""
        approved = DRAFT_DECISION.replace("status: draft", "status: approved")
        live = RECORD[REQUIREMENT_FILE].replace("REQ-0001", "REQ-0003").replace("status: approved", "status: live")
        for path, text, name in (("project/adrs/ADR-0004-new.md", approved.replace("0002", "0004"), "ADR-0004"),
                                 ("project/requirements/REQ-0003-new.md", live, "REQ-0003")):
            with self.subTest(name=name):
                f = self.fixture()
                self.crossed(f, self.design(f, write={"1": {path: text}}), name, other=("REQ-0001",))

    def test_superseded_crosses(self):
        """TSK-3420 criterion 1, REQ-0888: a call that sets an approved requirement to `superseded` ends the run
        `crossed`, as `withdrawn` does."""
        f = self.fixture()
        text = RECORD[REQUIREMENT_FILE].replace("status: approved", "status: superseded")
        self.crossed(f, self.design(f, write={"1": {REQUIREMENT_FILE: text}}), "REQ-0001")

    def test_a_draft_becoming_a_decided_status(self):
        """TSK-3420 criterion 1, REQ-0888: a call that sets a draft decision to `superseded` or `withdrawn` ends the
        run `crossed`, because each is a decided status, whatever the allowance for approved records says."""
        for status in ("superseded", "withdrawn", "rejected"):
            with self.subTest(status=status):
                f = self.fixture({DECISION_FILE: DRAFT_DECISION})
                text = DRAFT_DECISION.replace("status: draft", f"status: {status}")
                self.crossed(f, self.design(f, write={"1": {DECISION_FILE: text}}), "ADR-0002")

    def test_epic_marks_cross_outside_an_implement_run(self):
        """TSK-3420 criterion 2, REQ-0888: a call that marks a task in the approved epic ends a `design` run
        `crossed`, because an epic's marks change only in an `implement` run."""
        f = self.fixture()
        self.crossed(f, self.design(f, write={"1": {"project/epics/EPC-0001-a-plan.md": epic("x", "x")}}),
                     "EPC-0001")

    def test_epic_changes_only_marks_and_their_evidence(self):
        """TSK-3420 criterion 2, REQ-0888: in an `implement` run, a mark with an evidence line is allowed, and a
        reworded task title, a changed `closes` line or a new `revised` date in the epic each end the run
        `crossed`, because the spec lets a run change only the task marks."""
        epic_file = "project/epics/EPC-0001-a-plan.md"
        task_file = "project/tasks/TSK-0002-the-second.md"
        done_task = task("TSK-0002", "Done.")
        marked = epic("x", "x")
        # The evidence wraps over lines, one of them shaped like a field, as an evidence line may be.
        with_evidence = marked.rstrip("\n") + "\n      evidence: it passed\n      passed: 3 of 3\n      and wraps\n"
        f = self.fixture()
        f.configure(write={"1": {epic_file: with_evidence, task_file: done_task}}, create={"1": "done.flag"})
        done = f.start(step_terms("implement", "TSK-0002"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
        for name, text in (("a reworded title", marked.replace("the second", "the second, reworded")),
                           ("a changed closes line", marked.replace("closes: REQ-0001\n", "closes: REQ-0002\n", 1)),
                           ("a new revised date", marked.replace("revised: 2026-01-01", "revised: 2026-02-02"))):
            with self.subTest(name=name):
                g = self.fixture()
                g.configure(write={"1": {epic_file: text, task_file: done_task}}, create={"1": "done.flag"})
                self.crossed(g, g.start(step_terms("implement", "TSK-0002")), "EPC-0001")

    def test_other_changes_to_an_approved_epic(self):
        """TSK-3420 criterion 2, REQ-0888: in an `implement` run, a changed `depends` line after an evidence line, a
        deleted task entry and a change of every line ending each end the run `crossed` naming the epic."""
        epic_file = "project/epics/EPC-0001-a-plan.md"
        task_file = "project/tasks/TSK-0002-the-second.md"
        done_task = task("TSK-0002", "Done.")
        marked = epic("x", "x")
        evidence = marked.replace("      closes: REQ-0001\n", "      closes: REQ-0001\n      evidence: it passed\n      depends: TSK-0001\n")
        changed = evidence.replace("depends: TSK-0001", "depends: TSK-0009")
        shorter = marked[:marked.index("- [x] T-002")]
        for name, base, text in (("a changed depends line", evidence, changed), ("a deleted entry", marked, shorter),
                                 ("CRLF line endings", marked, marked.replace("\n", "\r\n"))):
            with self.subTest(name=name):
                f = self.fixture({"project/epics/EPC-0001-a-plan.md": base})
                f.configure(write={"1": {epic_file: text, task_file: done_task}}, create={"1": "done.flag"})
                self.crossed(f, f.start(step_terms("implement", "TSK-0002")), "EPC-0001")

    def test_swapped_paths_cross(self):
        """TSK-3420 criterion 1, REQ-0888: a call that swaps the files of an approved requirement and a draft ends
        the run `crossed` naming both, because each path now holds the other record."""
        f = self.fixture()
        draft_file = "project/requirements/REQ-0002-a-draft.md"
        swap = {REQUIREMENT_FILE: RECORD[draft_file], draft_file: RECORD[REQUIREMENT_FILE]}
        self.crossed(f, self.design(f, write={"1": swap}), "REQ-0001-a-duty")

    def test_a_cap_ends_a_run_before_it_is_crossed(self):
        """TSK-3420 criterion 6, REQ-0888: a call that approves a draft and reaches its own cap ends the run
        `budget`, because a broken bound is reported before a crossed gate."""
        f = self.fixture({DECISION_FILE: DRAFT_DECISION})
        approved = {"1": {DECISION_FILE: DRAFT_DECISION.replace("status: draft", "status: approved")}}
        done = self.design(f, write=approved, subtype="error_max_budget_usd")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "budget")

    def test_a_copied_approved_record_is_new(self):
        """TSK-3420 criterion 1, REQ-0888: a call that copies an approved requirement to a new path with the same
        identifier ends the run `crossed` naming the copy, because the copy is a record new since start that
        carries a decided status."""
        f = self.fixture()
        copy = "project/requirements/REQ-0001-a-copy.md"
        self.crossed(f, self.design(f, write={"1": {copy: RECORD[REQUIREMENT_FILE]}}), "REQ-0001-a-copy")

    def test_an_approved_record_overwritten_by_a_draft_of_a_held_identifier(self):
        """TSK-3420 criterion 1, REQ-0888: a call that overwrites an approved requirement with a draft carrying the
        identifier of another held draft ends the run `crossed` naming the overwritten file, because the approved
        record changed outside what a run may change."""
        f = self.fixture()
        draft = RECORD["project/requirements/REQ-0002-a-draft.md"]
        self.crossed(f, self.design(f, write={"1": {REQUIREMENT_FILE: draft}}), "REQ-0001-a-duty")

    def test_identifiers_shared_at_start_cross_nothing(self):
        """TSK-3420 criterion 1, REQ-0888: two records that share an identifier at start, a draft and an approved
        one, are each compared with their own held copy, so a call that changes only another file crosses
        nothing."""
        twin = DRAFT_DECISION.replace("status: draft", "status: approved")
        f = self.fixture({"project/adrs/ADR-0002-a-draft.md": DRAFT_DECISION, "project/adrs/ADR-0002-b-approved.md": twin})
        done = self.design(f, edit=True)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "ceiling")

    def test_crossed_is_reported_after_the_other_endings(self):
        """TSK-3420 criterion 6, REQ-0888: a call that approves a draft and also prints no cost ends the run
        `unmetered`, and one that also changes `run.toml` ends it `tampered`, because a broken bound and a changed
        term are reported before a crossed gate."""
        approved = {"1": {DECISION_FILE: DRAFT_DECISION.replace("status: draft", "status: approved")}}
        for name, config in (("unmetered", {"no_cost": True}), ("tampered", {"touch": {"1": "run.toml"}})):
            with self.subTest(name=name):
                f = self.fixture({DECISION_FILE: DRAFT_DECISION})
                done = self.design(f, write=approved, **config)
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertEqual(f.ending(), name)

    def test_crossed_before_finished(self):
        """TSK-3420 criterion 6, REQ-0888: a call that approves a draft and makes the verbs pass ends the run
        `crossed` and not `finished`."""
        f = self.fixture({DECISION_FILE: DRAFT_DECISION})
        f.configure(write={"1": {DECISION_FILE: DRAFT_DECISION.replace("status: draft", "status: approved")}},
                    create={"1": "done.flag"})
        done = f.start(step_terms("implement", "TSK-0001"))
        self.crossed(f, done, "ADR-0002")


class OffStep(Case):
    """ADR-2020: a call that writes another step's files, or leaves its input unready, ends the run `off-step`,
    after `crossed`, and the last line names each record or path."""

    def off_step(self, f, done, *names, calls=1, found="after iteration 1", other=()):
        """The run ended `off-step` after `calls` calls, and its last line starts with `found`, names every one of
        `names` and none of `other`."""
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "off-step")
        last = done.stdout.strip().splitlines()[-1]
        self.assertTrue(last.startswith(f"off-step: {found}"), last)
        for name in names:
            self.assertIn(name, last)
        for name in other:
            self.assertNotIn(name, last)
        self.assertNotRegex(last, r"\ba (implement|epic) ")
        self.assertEqual(len(f.calls()), calls)

    def design(self, f, **config):
        f.configure(**config)
        return f.start(step_terms("design", "REQ-0001"))

    def test_design_run_kinds(self):
        """TSK-3440 criterion 1, REQ-0888: in a `design` run, a call that writes a draft decision addressing the
        input and a specification ends the run `off-step` naming the specification; one that writes a file outside
        the record root ends it `off-step` naming the file; one that writes only the decision, while the verb
        passes, ends it `finished`."""
        decision = DRAFT_DECISION.replace("[REQ-0002]", "[REQ-0001]")
        spec = front(id="SPC-0002", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Another part\n"
        f = self.fixture({"done.flag": "x"})
        self.off_step(f, self.design(f, write={"1": {"project/adrs/ADR-0002-new.md": decision,
                                                      "project/specs/SPC-0002-another.md": spec}}),
                      "SPC-0002", other=("ADR-0002",))
        g = self.fixture({"done.flag": "x"})
        self.off_step(g, self.design(g, write={"1": {"stray.txt": "x"}}), "stray.txt")
        h = self.fixture({"done.flag": "x"})
        h.configure(write={"1": {"project/adrs/ADR-0002-new.md": decision}})
        done = h.start(step_terms("design", "REQ-0001"))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(h.ending(), "finished")

    def test_implement_run_limits(self):
        """TSK-3440 criterion 2, REQ-0888: in an `implement` run of a task with a blocking dependency marked done, a
        call that clears the dependency's mark in the approved epic and changes nothing else leaves the input
        failing the start test, so the run ends `off-step` naming the input task; one that writes a
        specification ends it `off-step` naming the specification; one that writes a file outside the record
        root does not."""
        dependent = task("TSK-0002", "Not yet.").replace("Nothing.", "- TSK-0001 (blocking): the first.")
        files = {"project/tasks/TSK-0002-the-second.md": dependent}
        f = self.fixture(files)
        f.configure(write={"1": {"project/epics/EPC-0001-a-plan.md": epic(" ", " ")}})
        self.off_step(f, f.start(step_terms("implement", "TSK-0002")), "TSK-0002", "TSK-0001", other=("EPC-0001",))
        spec = front(id="SPC-0002", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Another part\n"
        g = self.fixture(files)
        g.configure(write={"1": {"project/specs/SPC-0002-another.md": spec}})
        self.off_step(g, g.start(step_terms("implement", "TSK-0002")), "SPC-0002")
        h = self.fixture(files)
        h.configure(write={"1": {"stray.txt": "x"}})
        done = h.start(step_terms("implement", "TSK-0002", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(h.ending(), "ceiling")

    def test_unidentified_tree_in_a_record_step(self):
        """TSK-3440 criterion 3, REQ-0888: in a `design` run with a dirty submodule, a call that writes the decision
        ends the run `off-step`, because the changed paths can't be listed, and `log.jsonl` records the tree as
        `unidentified`."""
        decision = DRAFT_DECISION.replace("[REQ-0002]", "[REQ-0001]")
        f = self.fixture({"done.flag": "x"})
        self.dirty(f)
        done = self.design(f, write={"1": {"project/adrs/ADR-0002-new.md": decision}})
        self.off_step(f, done, "can't be listed")
        lines = [json.loads(text) for text in (f.run_dirs()[0] / "log.jsonl").read_text().splitlines()]
        self.assertTrue(lines)
        self.assertTrue(all(line["unidentified"] for line in lines))

    def test_verb_rewrites_are_not_the_calls(self):
        """TSK-3440 criterion 4, REQ-0888: in a `design` run whose verb rewrites an approved requirement and a file
        outside the record root on its first run, a call that writes only the decision ends the run `finished`, and
        neither `crossed` nor `off-step`, because the copy and the paths are taken after the verb's run."""
        decision = DRAFT_DECISION.replace("[REQ-0002]", "[REQ-0001]")
        f = self.fixture({"stray.txt": "plain\n"})
        count = f.base / "count"
        script = f.base / "verb.sh"
        script.write_text(
            f"n=$(cat {count} 2>/dev/null || echo 0)\necho $((n + 1)) > {count}\n"
            f"if [ \"$n\" -eq 0 ]; then\n  echo '' >> {REQUIREMENT_FILE}\n  echo changed >> stray.txt\nfi\n"
            f"test -f project/adrs/ADR-0002-new.md\n")
        (f.root / ".meowpaw" / "profile.toml").write_text(PROFILE.replace('test -f done.flag', f"sh {script}"))
        done = self.design(f, write={"1": {"project/adrs/ADR-0002-new.md": decision}})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "finished")
        self.assertEqual(len(f.calls()), 1)
        # The verb's rewrites happened, and it ran again after the call.
        self.assertIn("changed", (f.root / "stray.txt").read_text())
        self.assertTrue((f.root / REQUIREMENT_FILE).read_text().endswith("\n\n"))
        self.assertGreaterEqual(int(count.read_text()), 2)

    def test_always_allowed(self):
        """TSK-3440 criterion 5, REQ-0888: in every step, a call that writes a draft defect, a draft insight and an
        index under the record root does not end the run `off-step`."""
        defect = front(id="BUG-0002", artifact="bug", status="draft", severity="minor", violates="REQ-0001",
                       enters="implement", found="2026-01-01", revised="2026-01-01") + "\n# A defect\n"
        insight = front(id="INS-0001", artifact="insight", status="draft", revised="2026-01-01") + "\n# A lesson\n"
        writes = {"project/bugs/BUG-0002-a-defect.md": defect, "project/insights/INS-0001-a-lesson.md": insight,
                  "project/README.md": "# Index\n"}
        matched = 0
        for step, inputs in (("research", None), ("requirements", "RES-0001"), ("design", "REQ-0001"),
                             ("spec", "ADR-0001"), ("epic", "ADR-0001"), ("implement", "TSK-0001")):
            with self.subTest(step=step):
                f = self.fixture()
                f.configure(write={"1": writes})
                done = f.start(step_terms(step, inputs, iterations="2"))
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertEqual(f.ending(), "ceiling")
                self.assertTrue((f.root / "project/insights/INS-0001-a-lesson.md").exists())
                matched += 1
        self.assertEqual(matched, 6)

    def test_crossed_first(self):
        """TSK-3440 criterion 6, REQ-0888: a call that approves a draft and writes another step's record ends the
        run `crossed`, because a crossed gate is the graver of the two."""
        spec = front(id="SPC-0002", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Another part\n"
        f = self.fixture({DECISION_FILE: DRAFT_DECISION})
        f.configure(write={"1": {DECISION_FILE: DRAFT_DECISION.replace("status: draft", "status: approved"),
                                 "project/specs/SPC-0002-another.md": spec}})
        done = f.start(step_terms("design", "REQ-0001"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "crossed")

    def test_unidentified_tree_in_an_implement_step(self):
        """TSK-3440 criterion 3, REQ-0888: in an `implement` run with a dirty submodule, a call that writes a
        specification still ends the run `off-step` naming it, because the kind of a record needs no list of
        paths, while a call that writes only a file outside the record root does not."""
        spec = front(id="SPC-0002", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Another part\n"
        f = self.fixture()
        self.dirty(f)
        f.configure(write={"1": {"project/specs/SPC-0002-another.md": spec}})
        self.off_step(f, f.start(step_terms("implement", "TSK-0001")), "SPC-0002")
        g = self.fixture()
        self.dirty(g)
        g.configure(write={"1": {"stray.txt": "x"}})
        done = g.start(step_terms("implement", "TSK-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(g.ending(), "ceiling")

    def test_a_link_hides_no_record(self):
        """TSK-3440 criterion 1, REQ-0888: a `design` run that edits a specification through a link in the decisions
        directory ends `off-step` naming the specification, because the link and the file are one path to git and
        the file is a specification."""
        f = self.fixture()
        (f.root / "project/adrs/ADR-0007-link.md").symlink_to("../specs/SPC-0001-a-part.md")
        f.git("add", "-A")
        f.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.com", "-c", "commit.gpgsign=false",
              "commit", "-q", "-m", "a link")
        text = RECORD["project/specs/SPC-0001-a-part.md"] + "\nMore.\n"
        done = self.design(f, write={"1": {"project/adrs/ADR-0007-link.md": text}})
        self.off_step(f, done, "SPC-0001")

    def test_a_link_out_of_the_work_tree_hides_no_record(self):
        """TSK-3440 criterion 1, REQ-0888: a call that moves a tracked link, whose target lies outside the work tree
        and reads as a specification, into the specifications directory ends the run `off-step` naming the new path,
        in a `design` run and, with a dirty submodule, in an `implement` run, and never names the target."""
        spec = front(id="SPC-0008", artifact="spec", status="live", revised="2026-01-01",
                     states="[REQ-0001]") + "\n# Outside\n"
        moved = {"1": {}}
        for step, inputs in (("design", "REQ-0001"), ("implement", "TSK-0001")):
            with self.subTest(step=step):
                f = self.fixture()
                outside = f.base / "outside.md"
                outside.write_text(spec)
                (f.root / "project/adrs/ADR-0008-out.md").symlink_to(outside)
                f.git("add", "-A")
                f.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.com", "-c", "commit.gpgsign=false",
                      "commit", "-q", "-m", "a link")
                if step == "implement":
                    self.dirty(f)
                f.configure(rename={"1": {"project/adrs/ADR-0008-out.md": "project/specs/SPC-0008-out.md"}})
                done = f.start(step_terms(step, inputs))
                self.off_step(f, done, "project/specs/SPC-0008-out.md", other=("outside.md",))

    def test_a_verb_rewrite_after_a_call_is_not_the_next_calls(self):
        """TSK-3440 criterion 4, REQ-0888: a verb that rewrites a file outside the record root in the evaluation
        after the first call does not take the second call off its step, because the tree id before a call is
        read after the evaluation."""
        f = self.fixture({"stray.txt": "plain\n"})
        count = f.base / "count"
        script = f.base / "verb.sh"
        script.write_text(f"n=$(cat {count} 2>/dev/null || echo 0)\necho $((n + 1)) > {count}\n"
                          "if [ \"$n\" -eq 1 ]; then echo changed >> stray.txt; fi\nexit 1\n")
        (f.root / ".meowpaw" / "profile.toml").write_text(PROFILE.replace('test -f done.flag', f"sh {script}"))
        done = f.start(step_terms("design", "REQ-0001", iterations="2"))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(f.ending(), "ceiling")
        self.assertEqual(len(f.calls()), 2)
        self.assertIn("changed", (f.root / "stray.txt").read_text())

    def test_every_step_and_kind(self):
        """TSK-3440 criterion 1, REQ-0888: for each of the six steps and each of the ten kinds, a call that writes a
        new record of that kind ends the run `off-step` unless the step's row names the kind or the kind is a
        defect or an insight, and then the run ends `ceiling`."""
        def new(artifact, status, **fields):
            return front(id=fields.pop("id", None) or "X-0009", artifact=artifact, status=status, revised="2026-01-01",
                         **fields) + "\n# New\n"
        kinds = {
            "research": ("project/research/RES-0009-new.md", new("research", "draft", id="RES-0009")),
            "requirement": ("project/requirements/REQ-0009-new.md", RECORD["project/requirements/REQ-0002-a-draft.md"]
                            .replace("REQ-0002", "REQ-0009")),
            "decision": ("project/adrs/ADR-0009-new.md", DRAFT_DECISION.replace("0002", "0009")),
            "specification": ("project/specs/SPC-0009-new.md", new("spec", "live", id="SPC-0009", states="[REQ-0001]")),
            "epic": ("project/epics/EPC-0009-new.md", epic().replace("EPC-0001", "EPC-0009").replace(
                "status: approved", "status: draft")),
            "task": ("project/tasks/TSK-0009-new.md", task("TSK-0009", "Not yet.").replace(
                "status: approved", "status: draft")),
            "defect": ("project/bugs/BUG-0009-new.md", new("bug", "draft", id="BUG-0009", severity="minor",
                                                           violates="REQ-0001", enters="implement", found="2026-01-01")),
            "insight": ("project/insights/INS-0009-new.md", new("insight", "draft", id="INS-0009")),
            "vision": ("project/vision.md", new("vision", "live", id="vision")),
            "onboarding": ("project/onboarding.md", new("onboarding", "draft", id="onboarding")),
        }
        writes = {"research": {"research"}, "requirements": {"requirement"}, "design": {"decision"},
                  "spec": {"specification"}, "epic": {"epic", "task"}, "implement": {"task"}}
        inputs = {"research": None, "requirements": "RES-0001", "design": "REQ-0001", "spec": "ADR-0001",
                  "epic": "ADR-0001", "implement": "TSK-0001"}
        matched = 0
        for step, allowed in writes.items():
            for kind, (path, text) in kinds.items():
                with self.subTest(step=step, kind=kind):
                    f = self.fixture()
                    f.configure(write={"1": {path: text}})
                    done = f.start(step_terms(step, inputs[step], iterations="1"))
                    self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                    off = kind not in allowed | {"defect", "insight"}
                    self.assertEqual(f.ending(), "off-step" if off else "ceiling", done.stdout)
                    self.assertTrue((f.root / path).exists())
                    matched += 1
        self.assertEqual(matched, 60)


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
            ("stage lint resolves to no command", dict(terms=replaced("--until", "verbs=lint"))),
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
        self.dirty(f)
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
