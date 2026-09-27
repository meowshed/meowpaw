# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1140 states `meow-mise` reports.

Most fixtures run the real mise in a scratch repository, with its home, state
and parent directories isolated, because what the pack reads is what mise
prints, and a stand-in would only test the stand-in (RES-0126). A few put a
stand-in `mise` first on the path, for output real mise won't produce on
demand. `MEOW_MISE_BIN` names the launcher to test, so the fixtures can first
run against a program that reports nothing and be seen failing (REQ-2072).
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_MISE_BIN", UNIT / "bin" / "meow-mise"))
MISE = shutil.which("mise") or "mise"

TASKS = '''[tasks.test]
run = "echo test"

[tasks.deploy]
run = "echo deploy"
confirm = "Deploy now?"

[tasks.secret]
run = "echo secret"
hide = true

[tasks.greet]
usage = 'arg "<name>"'
run = "echo hello"

[tasks.build]
run = "echo build"
sources = ["src.txt"]
outputs = ["out.txt"]

[tasks.mine]
run = "echo committed"
'''
SHIP = '#!/bin/sh\n#MISE confirm="Ship it?"\necho ship\n'
PLAIN = "#!/bin/sh\necho plain\n"
EXEC = '[tasks.t]\nrun = "echo {{exec(command=\'echo x\')}}"\n'


class Repository:
    """A git repository at `<tmp>/parent/repo`, with mise stopped at `<tmp>`."""

    def __init__(self, files, untracked=None, parent=None, trusted=False, stand_in=None, path=None):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.parent = base / "parent"
        self.root = self.parent / "repo"
        self.home = base / "home"
        for directory in (self.root, self.home):
            directory.mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("MISE_", "__MISE_"))}
        self.env.update(HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / ".config"),
                        XDG_STATE_HOME=str(self.home / ".state"), XDG_CACHE_HOME=str(self.home / ".cache"),
                        XDG_DATA_HOME=str(self.home / ".data"), MISE_CEILING_PATHS=str(base),
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        if trusted:
            self.env["MISE_TRUSTED_CONFIG_PATHS"] = str(self.root)
        if stand_in is not None:
            tools = base / "tools"
            tools.mkdir()
            script = tools / "mise"
            script.write_text("#!/bin/sh\n" + stand_in, encoding="utf-8")
            script.chmod(0o755)
            self.env["PATH"] = f"{tools}{os.pathsep}{self.env['PATH']}"
        if path is not None:
            self.env["PATH"] = path(base)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, env=self.env)
        self.write(self.root, files)
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, env=self.env)
        self.write(self.root, untracked or {})
        self.write(self.parent, parent or {})

    @staticmethod
    def write(where, files):
        for name, text in files.items():
            path = where / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            if text.startswith("#!"):
                path.chmod(0o755)

    def run(self, *args):
        return subprocess.run([str(BIN), *args], cwd=self.root, capture_output=True, text=True, env=self.env,
                              stdin=subprocess.DEVNULL)

    def mise(self, *args):
        return subprocess.run([MISE, *args], cwd=self.root, capture_output=True, text=True, env=self.env,
                              stdin=subprocess.DEVNULL)


class Fixture(unittest.TestCase):
    def repo(self, files, **options):
        repository = Repository(files, **options)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    @staticmethod
    def task(output, name):
        """The lines `status` prints for one task: its own line and those indented under it."""
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if line.startswith(f"  {name}: "):
                block = [line]
                for rest in lines[i + 1:]:
                    if not rest.startswith("    "):
                        break
                    block.append(rest)
                return "\n".join(block)
        raise AssertionError(f"no task {name} in:\n{output}")


class Status(Fixture):
    def setUp(self):
        self.repository = self.repo(
            {"mise.toml": TASKS, "mise-tasks/ship": SHIP, "mise-tasks/plain": PLAIN},
            untracked={"mise.local.toml": '[tasks.mine]\nrun = "echo local"\n'},
            parent={"mise.toml": '[tasks.extra]\nrun = "echo extra"\n'})
        self.done = self.repository.run("status")

    def test_it_reports_and_exits_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stdout + self.done.stderr)

    def test_the_tasks_are_what_this_work_tree_resolves(self):
        """REQ-2460, REQ-2464: listed through mise, and reported as resolved, never as declared."""
        self.assertIn("tasks resolved in this work tree", self.done.stdout)
        self.assertNotIn("declared tasks", self.done.stdout)
        self.assertIn("  plain: repository mise-tasks/plain", self.done.stdout)

    def test_the_version_is_reported(self):
        """REQ-2496: the runner's version."""
        version = self.repository.mise("--version").stdout.split()[0]
        self.assertIn(f"mise: {version}", self.done.stdout)

    def test_a_committed_task_carries_no_block(self):
        self.assertEqual(self.task(self.done.stdout, "test"), "  test: repository mise.toml")

    def test_a_hidden_task_is_blocked(self):
        """REQ-2479: a private task is never bound."""
        self.assertIn("blocked: hidden", self.task(self.done.stdout, "secret"))

    def test_a_confirm_task_is_blocked_in_either_form(self):
        """REQ-2478: a TOML key and a file task's header both ask for a person."""
        self.assertIn("blocked: asks for a person", self.task(self.done.stdout, "deploy"))
        self.assertIn("blocked: asks for a person", self.task(self.done.stdout, "ship"))

    def test_a_required_argument_is_read_not_discovered(self):
        """REQ-2476: the argument comes from the enumeration, and nothing ran."""
        self.assertIn("blocked: needs <name>", self.task(self.done.stdout, "greet"))

    def test_a_task_that_can_skip_says_so(self):
        """REQ-2470: freshness is decided by a method mise doesn't report."""
        block = self.task(self.done.stdout, "build")
        self.assertIn("can skip as fresh: freshness decided by mise, by a method it doesn't report", block)
        self.assertNotIn("blocked", block)

    def test_a_task_from_outside_is_named_so(self):
        """REQ-2465: a task from outside the repository doesn't reproduce elsewhere."""
        block = self.task(self.done.stdout, "extra")
        self.assertIn("extra: outside ", block)
        self.assertIn("blocked: not committed", block)

    def test_a_replaced_task_is_reported(self):
        """REQ-2500: mise.local.toml replaces a committed task silently."""
        block = self.task(self.done.stdout, "mine")
        self.assertIn("mine: work tree only mise.local.toml", block)
        self.assertIn("replaced by mise.local.toml; mise.toml declares it", block)
        self.assertIn("blocked: not committed", block)

    def test_the_listing_says_it_ran_mise(self):
        """REQ-2473: the listing ran mise over the configuration."""
        self.assertIn("listing ran mise over the configuration", self.done.stdout)
        self.assertIn("no committed configuration file calls exec", self.done.stdout)


class Trust(Fixture):
    def test_an_untrusted_template_is_unresolved_and_stays_untrusted(self):
        """REQ-2466, REQ-2467: reported as untrusted, never as empty, and never trusted."""
        repository = self.repo({"mise.toml": EXEC})
        done = repository.run("status")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn(f"unresolved: untrusted {repository.root}; a person runs mise trust {repository.root} after reading it",
                      done.stdout)
        self.assertIn("untrusted", repository.mise("trust", "--show").stdout)
        self.assertNotIn(": trusted", repository.mise("trust", "--show").stdout)

    def test_a_trusted_template_is_named_as_run(self):
        """REQ-2473: listing a trusted file evaluates its templates, and the file is named."""
        done = self.repo({"mise.toml": EXEC}, trusted=True).run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("templates calling exec, evaluated by the listing: mise.toml", done.stdout)


class Carried(Fixture):
    """What mise carries beyond tasks, named and never read out."""

    CONFIG = '''[tools]
python = "3.14"
node = { version = "22" }

[env]
_.file = ".env"
_.source = ["scripts/env.sh"]
SECRET_TOKEN = "never-printed-value"
'''

    def section(self, output, heading):
        lines = output.splitlines()
        start = next(i for i, line in enumerate(lines) if line.startswith(heading))
        block = []
        for line in lines[start + 1:]:
            if not line.startswith("  "):
                break
            block.append(line)
        return "\n".join(block)

    def test_pinned_tools_and_the_lock_are_named(self):
        """REQ-2482: the toolchain a committed file pins, and whether a lock records it."""
        done = self.repo({"mise.toml": self.CONFIG, "mise.lock": "", ".python-version": "3.13\n"}, trusted=True).run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        tools = self.section(done.stdout, "tools pinned by committed files:")
        self.assertIn("  python = 3.14 (mise.toml)", tools)
        self.assertIn("  node = 22 (mise.toml)", tools)
        self.assertIn("  mise.lock: committed", tools)

    def test_a_missing_lock_is_named(self):
        done = self.repo({"mise.toml": '[tools]\npython = "3.14"\n'}).run("status")
        self.assertIn("  mise.lock: not committed", self.section(done.stdout, "tools pinned by committed files:"))

    def test_the_environment_files_are_named_and_no_value_printed(self):
        """REQ-2490: the files mise loads the environment from, with contents unread."""
        repository = self.repo({"mise.toml": self.CONFIG}, trusted=True)
        done = repository.run("status")
        loaded = self.section(done.stdout, "configuration and environment loaded from:")
        self.assertIn("  mise.toml", loaded)
        self.assertIn("  .env (_.file in mise.toml)", loaded)
        self.assertIn("  scripts/env.sh (_.source in mise.toml)", loaded)
        self.assertNotIn("never-printed-value", done.stdout)
        self.assertNotIn("SECRET_TOKEN", done.stdout)

    def test_an_idiomatic_file_is_possibly_inert_by_default(self):
        """REQ-2506: mise leaves an idiomatic version file unread unless a setting names its tool."""
        done = self.repo({"mise.toml": '[tools]\npython = "3.14"\n', ".python-version": "3.13\n"}).run("status")
        self.assertIn("  .python-version: possibly inert, since idiomatic_version_file_enable_tools doesn't name python",
                      self.section(done.stdout, "idiomatic version files:"))

    def test_an_enabled_idiomatic_file_is_read(self):
        repository = self.repo({"mise.toml": '[settings]\nidiomatic_version_file_enable_tools = ["python"]\n',
                                ".python-version": "3.13\n", ".nvmrc": "22\n"}, trusted=True)
        idiomatic = self.section(repository.run("status").stdout, "idiomatic version files:")
        self.assertIn("  .python-version: read by mise", idiomatic)
        self.assertIn("  .nvmrc: possibly inert", idiomatic)


BINDABLE = '''[tasks.test]
run = "echo test"

[tasks.tests]
run = "echo tests"

[tasks.unit]
run = "python3 -m pytest"

[tasks.lint]
run = "echo lint"
hide = true

[tasks.build]
run = "echo build"
sources = ["src.txt"]
outputs = ["out.txt"]
'''


def profile(verbs):
    return "[verbs]\n" + "".join(f'{verb} = "{command}"\n' for verb, command in verbs.items())


class Bind(Fixture):
    def setUp(self):
        self.done = self.repo({"mise.toml": BINDABLE}).run("bind")

    def test_a_verb_binds_to_its_exact_task_with_force(self):
        """REQ-1316, REQ-2354, REQ-2468: the verb runs the declared task, and a skip can't pass."""
        self.assertEqual(self.done.returncode, 0, self.done.stdout + self.done.stderr)
        self.assertIn("[verbs]\n", self.done.stdout)
        self.assertIn('test = "mise run --force test"', self.done.stdout)
        self.assertIn('build = "mise run --force build"', self.done.stdout)

    def test_a_near_name_or_a_body_binds_nothing(self):
        """REQ-2474, REQ-2492: only the exact name, never a near one or what a task runs."""
        self.assertNotIn("run --force tests", self.done.stdout)
        self.assertNotIn("run --force unit", self.done.stdout)
        self.assertIn("# format: no task named format", self.done.stdout)
        self.assertIn("# check: no task named check", self.done.stdout)

    def test_a_blocked_task_is_left_unbound_with_its_reason(self):
        self.assertIn("# lint: task lint is blocked: hidden", self.done.stdout)
        self.assertNotIn("lint = ", self.done.stdout)

    def test_an_unresolved_tree_binds_nothing(self):
        done = self.repo({"mise.toml": EXEC}).run("bind")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: untrusted", done.stdout)
        self.assertNotIn("[verbs]", done.stdout)


class Check(Fixture):
    def check(self, verbs, files=None):
        return self.repo({"mise.toml": BINDABLE, ".meowpaw/profile.toml": profile(verbs), **(files or {})}).run("check")

    def test_a_skippable_task_without_force_is_a_finding(self):
        """REQ-2468: that verb can pass without running."""
        done = self.check({"test": "mise run build"})
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("  test: task build can skip as fresh and runs without --force", done.stdout)

    def test_a_forced_skippable_task_is_clean(self):
        done = self.check({"test": "mise run -f build", "build": "mise run --force build"})
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("0 findings", done.stdout)

    def test_each_part_of_a_chain_is_checked(self):
        done = self.check({"lint": "mise run --force build && mise run lint"})
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("  lint: task lint is blocked: hidden", done.stdout)

    def test_a_missing_task_is_a_finding(self):
        done = self.check({"test": "mise run nope"})
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("  test: no task named nope", done.stdout)

    def test_a_profile_running_no_task_has_nothing_to_check(self):
        done = self.check({"test": "./run-tests"})
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("nothing to check", done.stdout)

    def test_no_profile_is_unresolved(self):
        done = self.repo({"mise.toml": BINDABLE}).run("check")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: no profile", done.stdout)

    def test_this_repositorys_profile_is_clean(self):
        root = UNIT.parent.parent
        env = {k: v for k, v in os.environ.items() if not k.startswith(("MISE_", "__MISE_"))}
        done = subprocess.run([str(BIN), "check"], cwd=root, capture_output=True, text=True, env=env,
                              stdin=subprocess.DEVNULL)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("0 findings", done.stdout)


class WritesNothing(Fixture):
    def test_no_command_changes_the_tree(self):
        """REQ-2504: the pack writes no file, mise.local.toml least of all."""
        repository = self.repo({"mise.toml": BINDABLE, ".meowpaw/profile.toml": profile({"test": "mise run test"})})
        state = lambda: subprocess.run(["git", "status", "--porcelain", "--ignored", "--untracked-files=all"],
                                       cwd=repository.root, capture_output=True, text=True, env=repository.env).stdout
        before = state()
        for command in ("status", "bind", "check"):
            repository.run(command)
        self.assertEqual(state(), before)
        self.assertFalse((repository.root / "mise.local.toml").exists())


class Unresolved(Fixture):
    def test_no_marker_runs_no_mise(self):
        """REQ-2472: detection is a static read, and mise never starts."""
        repository = self.repo({"README.md": "# r\n"}, stand_in='touch "$HOME/ran"\n')
        done = repository.run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: not a mise repository", done.stdout)
        self.assertFalse((repository.home / "ran").exists(), "mise ran")

    def test_a_file_task_directory_is_a_marker(self):
        """REQ-2472: a repository holding only file tasks is still a mise repository."""
        repository = self.repo({".mise/tasks/t": PLAIN}, stand_in='touch "$HOME/ran"; echo "2026.9.11 x"; echo "[]"\n')
        repository.run("status")
        self.assertTrue((repository.home / "ran").exists())

    def test_mise_missing_is_unresolved(self):
        def without_mise(base):
            tools = base / "git-only"
            tools.mkdir()
            (tools / "git").symlink_to(shutil.which("git"))
            return f"{tools}{os.pathsep}/usr/bin{os.pathsep}/bin"
        done = self.repo({"mise.toml": ""}, path=without_mise).run("status")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: mise not found", done.stdout)

    def test_an_unrecognised_listing_is_never_empty(self):
        """REQ-2462: another shape is unresolved, never an empty task list."""
        stand_in = 'case "$1" in --version) echo "2026.9.11 macos-arm64";; tasks) echo \'{"tasks": []}\';; *) echo "[]";; esac\n'
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn('unresolved: unrecognised shape: {"tasks": []}', done.stdout)

    def test_an_entry_without_a_name_is_unrecognised(self):
        """REQ-2462: an array whose entries lack a string name is not a listing."""
        stand_in = 'case "$1" in --version) echo "2026.9.11 macos-arm64";; tasks) echo \'[{"source": "x"}]\';; *) echo "[]";; esac\n'
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: unrecognised shape", done.stdout)

    def test_an_older_mise_is_an_environment_failure(self):
        """REQ-2496: a flag an older version lacks is the environment's, not the repository's."""
        stand_in = ('case "$1" in --version) echo "2025.1.0 macos-arm64";; '
                    "tasks) echo \"error: unexpected argument '--hidden' found\" >&2; exit 2;; *) echo '[]';; esac\n")
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: environment: mise 2025.1.0 predates --hidden", done.stdout)

    def test_a_current_mise_rejecting_a_flag_is_the_packs_defect(self):
        stand_in = ('case "$1" in --version) echo "2026.9.11 macos-arm64";; '
                    "tasks) echo \"error: unexpected argument '--hidden' found\" >&2; exit 2;; *) echo '[]';; esac\n")
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: meow-mise defect: --hidden", done.stdout)

    def test_another_failure_is_never_empty(self):
        stand_in = 'case "$1" in --version) echo "2026.9.11 macos-arm64";; tasks) echo boom >&2; exit 5;; *) echo "[]";; esac\n'
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: mise failed with exit status 5: boom", done.stdout)


if __name__ == "__main__":
    unittest.main()
