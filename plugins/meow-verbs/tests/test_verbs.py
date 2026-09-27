# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every failure path SPC-1040 states, and for ADR-1070's checks.

Each fixture builds a repository in a temporary directory and runs the
launcher there. `MEOW_VERBS_BIN` names the launcher to test, so the same
fixtures can first run against a program that returns nothing and be seen
failing (REQ-2072).
"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_VERBS_BIN", UNIT / "bin" / "meow-verbs"))
VERBS = ["format", "lint", "check", "test", "build"]


class Repository:
    """A scratch repository with an optional profile."""

    def __init__(self, profile=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # The ledger goes to a state directory of the fixture's own, outside the
        # repository and never the machine's (ADR-1480).
        self.state_tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.state_tmp.name)
        if profile is not None:
            (self.root / ".meowpaw").mkdir()
            (self.root / ".meowpaw" / "profile.toml").write_text(profile, encoding="utf-8")

    def run(self, *args, env=None):
        env = {**(os.environ if env is None else env), "XDG_STATE_HOME": str(self.state),
               "XDG_RUNTIME_DIR": str(self.state),
               "XDG_CONFIG_HOME": str(self.state), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        return subprocess.run([str(BIN), *args], cwd=self.root, capture_output=True,
                              text=True, env=env)

    def git(self, *args):
        # The machine's own git configuration and ignore file stay out, so a
        # fixture gives one verdict on every machine (BUG-1190).
        return subprocess.run(["git", "-c", "user.name=a", "-c", "user.email=a@b", *args], cwd=self.root,
                              capture_output=True, text=True, check=True,
                              env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                                   "XDG_CONFIG_HOME": str(self.state)})

    def records(self):
        ledgers = list((self.state / "meowpaw" / "evidence").glob("*.jsonl"))
        assert len(ledgers) == 1, ledgers
        return [json.loads(line) for line in ledgers[0].read_text(encoding="utf-8").splitlines()]

    def status(self):
        done = self.run("status", "--json")
        return json.loads(done.stdout)

    def close(self):
        self.tmp.cleanup()
        self.state_tmp.cleanup()


class Verbs(unittest.TestCase):
    def repo(self, profile=None):
        repository = Repository(profile)
        self.addCleanup(repository.close)
        return repository

    def test_no_profile_leaves_every_verb_unresolved(self):
        repo = self.repo()
        verbs = repo.status()["verbs"]
        self.assertEqual(sorted(verbs), sorted(VERBS))
        for entry in verbs.values():
            self.assertEqual((entry["state"], entry["kind"]), ("unresolved", "no profile"))

    def test_run_without_a_profile_runs_nothing_and_fails(self):
        done = self.repo().run("run", "lint")
        self.assertEqual(done.returncode, 3)
        self.assertIn("lint: unresolved (no profile", done.stdout)
        self.assertIn("not run", done.stdout)
        self.assertNotIn("passed", done.stdout)

    def test_an_unparseable_profile_resolves_nothing_and_runs_nothing(self):
        repo = self.repo('[verbs\nlint = "touch ran"\n')
        report = repo.status()
        self.assertEqual(report["profile_state"], "unparseable")
        self.assertTrue(report["error"])
        for entry in report["verbs"].values():
            self.assertEqual(entry["kind"], "profile unparseable")
        done = repo.run("run", "lint")
        self.assertEqual(done.returncode, 3)
        self.assertFalse((repo.root / "ran").exists())

    def test_a_value_that_is_not_one_command_is_malformed(self):
        report = self.repo('[verbs]\nlint = ["a", "b"]\ntest = ""\n').status()
        self.assertEqual(report["verbs"]["lint"]["kind"], "malformed declaration")
        self.assertEqual(report["verbs"]["test"]["kind"], "malformed declaration")
        self.assertEqual(report["verbs"]["format"]["kind"], "undeclared")
        self.assertIn("declare it under [verbs] in .meowpaw/profile.toml", report["verbs"]["format"]["detail"])

    def test_a_declared_verb_resolves_and_status_runs_nothing(self):
        repo = self.repo('[verbs]\nlint = "touch ran"\n')
        entry = repo.status()["verbs"]["lint"]
        self.assertEqual((entry["state"], entry["command"]), ("resolved", "touch ran"))
        self.assertEqual(entry["source"], ".meowpaw/profile.toml")
        repo.run("status")
        self.assertFalse((repo.root / "ran").exists())

    def test_an_unknown_key_is_reported_and_the_rest_still_resolve(self):
        report = self.repo('[verbs]\nlint = "true"\ndeploy = "true"\n[prose]\n'
                           'language = "en-US"\n').status()
        self.assertIn("verbs.deploy", report["ignored"])
        self.assertIn("[prose]", report["ignored"])
        self.assertEqual(report["verbs"]["lint"]["state"], "resolved")

    def test_a_failing_verb_reports_its_command_status_and_whole_output(self):
        lines = "; ".join(f"echo line{n}" for n in range(1, 31))
        repo = self.repo(f'[verbs]\nlint = "{lines}; echo boom >&2; exit 4"\n')
        done = repo.run("run", "lint")
        self.assertEqual(done.returncode, 1)
        self.assertIn(f"== lint: `{lines}; echo boom >&2; exit 4`", done.stdout)
        self.assertIn("failed, exit status 4", done.stdout)
        head, whole = done.stdout.split("-- whole output of lint:")
        self.assertIn("boom", head)
        self.assertNotIn("line1\n", head)
        self.assertIn("line1\n", whole)
        self.assertIn("line30\n", whole)
        self.assertIn("summary: lint failed", done.stdout)

    def test_a_command_the_shell_cannot_find_is_a_failure(self):
        done = self.repo('[verbs]\ntest = "no-such-tool-anywhere"\n').run("run", "test")
        self.assertEqual(done.returncode, 1)
        self.assertIn("failed, exit status 127", done.stdout)

    def test_a_passing_verb_passes_and_an_unresolved_one_never_does(self):
        done = self.repo('[verbs]\nformat = "true"\n').run("run", "format", "build")
        self.assertEqual(done.returncode, 3)
        self.assertIn("summary: format passed, build unresolved", done.stdout)

    def test_run_with_no_verb_is_an_error_and_runs_nothing(self):
        repo = self.repo('[verbs]\nlint = "touch ran"\n')
        done = repo.run("run")
        self.assertEqual(done.returncode, 2)
        self.assertIn("name the verbs to run", done.stderr)
        self.assertFalse((repo.root / "ran").exists())

    def test_the_verbs_are_named_as_decided(self):
        """REQ-2908: the five verbs are format, lint, check, test and build."""
        repo = self.repo('[verbs]\nformat = "echo formatted"\ncheck = "true"\n')
        self.assertEqual(sorted(repo.status()["verbs"]), sorted(VERBS))
        done = repo.run("run", "format")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("formatted", done.stdout)

    def test_an_old_key_is_ignored_from_0_4_0(self):
        """REQ-2908, ADR-1410: from 0.4.0 a profile key under an old name resolves nothing and is listed as ignored."""
        report = self.repo('[verbs]\nfmt = "true"\n').status()
        self.assertEqual(report["verbs"]["format"]["state"], "unresolved")
        self.assertIn("verbs.fmt", report["ignored"])

    def test_an_old_name_on_the_command_line_is_refused(self):
        """REQ-2908, ADR-1410: from 0.4.0 typecheck isn't a verb."""
        done = self.repo('[verbs]\ncheck = "echo checked"\n').run("run", "typecheck")
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("typecheck isn't a verb", done.stderr)

    def test_a_sixth_verb_is_refused(self):
        done = self.repo('[verbs]\ndeploy = "true"\n').run("run", "deploy")
        self.assertEqual(done.returncode, 2)
        self.assertIn("isn't a verb", done.stderr)

    def test_no_interpreter_leaves_every_verb_unresolved(self):
        repo = self.repo('[verbs]\nlint = "true"\n')
        fake = repo.root / "bin"
        fake.mkdir()
        old = fake / "python3"
        old.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        old.chmod(0o755)
        env = {"PATH": str(fake), "HOME": str(repo.root)}
        report = json.loads(repo.run("status", "--json", env=env).stdout)
        for entry in report["verbs"].values():
            self.assertEqual((entry["state"], entry["kind"]), ("unresolved", "no interpreter"))
        done = repo.run("run", "lint", env=env)
        self.assertEqual(done.returncode, 3)
        self.assertNotIn("passed", done.stdout)


class Ledger(unittest.TestCase):
    """ADR-1480: each result is recorded against the tree it ran on, and evidence reports whether it holds."""

    PROFILE = '[verbs]\ntest = "echo tested"\nlint = "echo broken; exit 1"\nformat = "printf x >> formatted.txt"\n'

    def repo(self, git=True):
        repository = Repository(self.PROFILE)
        self.addCleanup(repository.close)
        if git:
            repository.git("init", "-q", "-b", "work")
        return repository

    def test_run_records_every_verb_outside_the_repository(self):
        """REQ-0146: a record per verb, the unresolved one included, with its whole output."""
        repo = self.repo()
        before = sorted(p.name for p in repo.root.iterdir())
        done = repo.run("run", "test", "lint", "check")
        self.assertEqual(done.returncode, 1, done.stdout)
        records = repo.records()
        self.assertEqual([(r["verb"], r["outcome"]) for r in records],
                         [("test", "passed"), ("lint", "failed"), ("check", "unresolved")])
        for r in records:
            self.assertRegex(r["tree"], r"^[0-9a-f]{40}$")
            self.assertIn(f"recorded: {r['verb']} {r['record']} at tree {r['tree'][:12]}", done.stdout)
        logs = repo.state / "meowpaw" / "evidence"
        self.assertEqual((next(logs.glob(f"*/{records[1]['record']}.log"))).read_text(encoding="utf-8"), "broken\n")
        self.assertEqual(sorted(p.name for p in repo.root.iterdir()), before)

    def test_evidence_holds_only_for_the_tree_it_ran_on(self):
        """REQ-0146, REQ-0148: current after a pass, stale after an edit, failing after a failure."""
        repo = self.repo()
        repo.run("run", "test")
        done = repo.run("evidence", "test")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("test: passed, record", done.stdout)
        self.assertIn(", current at tree", done.stdout)
        (repo.root / "edited.txt").write_text("a\n", encoding="utf-8")
        done = repo.run("evidence", "test")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("stale: ran on tree", done.stdout)
        repo.run("run", "lint")
        self.assertEqual(repo.run("evidence", "lint").returncode, 1)
        self.assertEqual(repo.run("evidence", "build").returncode, 3)
        self.assertIn("build: no record", repo.run("evidence", "build").stdout)

    def test_a_verb_that_rewrites_the_tree_is_stale_until_it_runs_clean(self):
        """REQ-0148: a result taken while the tree changed describes no one tree."""
        repo = self.repo()
        repo.run("run", "format")
        done = repo.run("evidence", "format")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("the tree changed during its run", done.stdout)

    def test_going_back_to_an_earlier_tree_is_stale_until_the_verb_runs_again(self):
        """REQ-0148: the latest record decides, so an earlier pass on the same content doesn't count."""
        repo = self.repo()
        repo.run("run", "test")
        (repo.root / "edited.txt").write_text("a\n", encoding="utf-8")
        repo.run("run", "test")
        (repo.root / "edited.txt").unlink()
        self.assertEqual(repo.run("evidence", "test").returncode, 1)
        repo.run("run", "test")
        self.assertEqual(repo.run("evidence", "test").returncode, 0)

    def test_the_tree_id_is_the_tree_of_a_commit_adding_every_file(self):
        """REQ-0146: a reviewer can compare a recorded tree with the commit made from that state."""
        repo = self.repo()
        (repo.root / "untracked.txt").write_text("a\n", encoding="utf-8")
        repo.run("run", "test")
        tree = repo.records()[-1]["tree"]
        self.assertIn("?? untracked.txt", repo.git("status", "--short").stdout)
        repo.git("add", "-A")
        repo.git("commit", "-q", "-m", "c")
        self.assertEqual(repo.git("rev-parse", "HEAD^{tree}").stdout.strip(), tree)

    def test_outside_git_a_record_is_bound_to_no_tree(self):
        """REQ-0146: with no tree to bind to, evidence never reads as current."""
        repo = self.repo(git=False)
        repo.run("run", "test")
        self.assertEqual(repo.records()[-1]["tree"], "none")
        done = repo.run("evidence", "test")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("bound to no tree", done.stdout)


class Subset(unittest.TestCase):
    """ADR-1520: a verb runs over part of the work only through a form the repository declares."""

    PROFILE = ('[verbs]\nlint = "echo linted"\n\n[verbs.test]\ncommand = "echo whole"\n'
               'subset = "printf \'[%s]\' {targets}"\n')

    def repo(self, profile=None, git=False):
        repository = Repository(profile or self.PROFILE)
        self.addCleanup(repository.close)
        if git:
            repository.git("init", "-q", "-b", "work")
        return repository

    def test_a_declared_form_runs_the_targets_quoted(self):
        """REQ-0140: each target reaches the tool as one argument."""
        done = self.repo().run("run", "test", "--", "a b", "c;d")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("[a b][c;d]", done.stdout)
        self.assertNotIn("`echo whole`", done.stdout)

    def test_a_verb_with_no_form_is_unresolved_and_nothing_runs(self):
        """REQ-0142: the whole command never runs in the part's place."""
        done = self.repo().run("run", "lint", "--", "a")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("lint: unresolved (no subset form", done.stdout)
        self.assertNotIn("linted", done.stdout)

    def test_verbs_with_and_without_a_form_run_and_report_each(self):
        """REQ-0140, REQ-0142: the verb with a form runs, the one without is reported."""
        done = self.repo().run("run", "test", "lint", "--", "a")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("[a]", done.stdout)
        self.assertIn("lint: unresolved (no subset form", done.stdout)
        self.assertIn("summary: test passed, lint unresolved", done.stdout)

    def test_a_string_value_still_resolves_the_whole_verb(self):
        """ADR-1520: every profile written before keeps its meaning."""
        done = self.repo().run("run", "lint")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("linted", done.stdout)

    def test_a_double_dash_with_no_target_is_refused(self):
        """ADR-1520: an empty part could mean the whole work or nothing."""
        done = self.repo().run("run", "test", "--")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("names no target", done.stderr)

    def test_a_form_without_the_placeholder_is_malformed(self):
        """REQ-0142: a form with no {targets} would run the whole work as the part."""
        repo = self.repo('[verbs.test]\ncommand = "echo whole"\nsubset = "echo whole"\n')
        entry = repo.status()["verbs"]["test"]
        self.assertEqual((entry["state"], entry["kind"]), ("unresolved", "malformed declaration"))

    def test_status_shows_each_subset_form(self):
        """ADR-1520: the model sees which verbs run over a part before it asks."""
        repo = self.repo()
        verbs = repo.status()["verbs"]
        self.assertEqual(verbs["test"]["subset"], "printf '[%s]' {targets}")
        self.assertIsNone(verbs["lint"]["subset"])
        said = repo.run("status").stdout
        self.assertIn("subset      printf '[%s]' {targets}", said)
        self.assertIn("subset      none", said)

    def test_a_subset_record_never_stands_for_the_whole_verb(self):
        """REQ-0142: evidence for the whole verb reads the latest whole run."""
        repo = self.repo(git=True)
        repo.run("run", "test")
        repo.run("run", "test", "--", "a")
        done = repo.run("evidence", "test")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("test: subset only, passed", done.stdout)
        self.assertIn("targets a,", done.stdout)
        self.assertIn("test: passed, record", done.stdout)
        records = repo.records()
        self.assertEqual([r["targets"] for r in records], [None, ["a"]])


class Kept(unittest.TestCase):
    """ADR-1530: a cited record is kept in the repository, outside the tree id."""

    PROFILE = '[verbs]\ntest = "echo tested"\n'

    def repo(self, profile=None):
        repository = Repository(profile or self.PROFILE)
        self.addCleanup(repository.close)
        repository.git("init", "-q", "-b", "work")
        return repository

    def test_a_current_record_is_kept_with_its_header_and_output(self):
        """REQ-2956, REQ-2964: the kept file is the contract a person reads."""
        repo = self.repo()
        repo.run("run", "test")
        record = repo.records()[-1]
        done = repo.run("evidence", "--keep", "test")
        self.assertEqual(done.returncode, 0, done.stdout)
        kept = repo.root / "project" / "evidence" / f"{record['record']}.txt"
        self.assertIn(f"kept: project/evidence/{record['record']}.txt", done.stdout)
        text = kept.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("meow-verbs evidence 1\n"), text)
        for line in (f"record: {record['record']}", "verb: test", "command: echo tested", "outcome: passed",
                     "exit status: 0", f"tree: {record['tree']}"):
            self.assertIn(line + "\n", text)
        self.assertTrue(text.endswith("\n\ntested\n"), text)

    def test_keeping_a_record_leaves_it_current(self):
        """REQ-2956: the evidence directory is not part of the work it describes."""
        repo = self.repo()
        repo.run("run", "test")
        repo.run("evidence", "--keep", "test")
        done = repo.run("evidence", "test")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("current at tree", done.stdout)

    def test_a_stale_record_is_not_kept(self):
        """REQ-2956: a record describing other content than the tree isn't evidence for it."""
        repo = self.repo()
        repo.run("run", "test")
        (repo.root / "edited.txt").write_text("a\n", encoding="utf-8")
        done = repo.run("evidence", "--keep", "test")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("not kept", done.stdout)
        self.assertFalse((repo.root / "project" / "evidence").exists())

    def test_the_declared_directory_is_used_and_left_out(self):
        """REQ-2956: a repository chooses where its evidence lives."""
        repo = self.repo(self.PROFILE.replace("[verbs]\n", '[verbs]\nevidence_dir = "proof"\n'))
        repo.run("run", "test")
        repo.run("evidence", "--keep")
        self.assertEqual(len(list((repo.root / "proof").glob("*.txt"))), 1)
        self.assertNotIn("verbs.evidence_dir", repo.status()["ignored"])
        self.assertEqual(repo.run("evidence", "test").returncode, 0)

    def test_the_default_follows_a_moved_record(self):
        """REQ-2956, ADR-1550: evidence sits beside the record wherever the profile puts it."""
        repo = self.repo(self.PROFILE + '\n[record]\nroot = "docs/record"\n')
        repo.run("run", "test")
        done = repo.run("evidence", "--keep")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(len(list((repo.root / "docs" / "record" / "evidence").glob("*.txt"))), 1)

    def test_a_kept_file_git_ignores_is_reported_and_left(self):
        """REQ-2956, ADR-1550: a file git won't commit isn't kept."""
        repo = self.repo()
        (repo.root / ".gitignore").write_text("project/evidence/\n", encoding="utf-8")
        repo.run("run", "test")
        done = repo.run("evidence", "--keep", "test")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("ignored by .gitignore:1", done.stdout)
        self.assertEqual(len(list((repo.root / "project" / "evidence").glob("*.txt"))), 1)

    def test_outside_git_a_kept_file_is_unchecked(self):
        """REQ-2956, ADR-1550: an ignore check git can't answer is unresolved, never a keep."""
        repository = Repository(self.PROFILE)
        self.addCleanup(repository.close)
        repository.run("run", "test")
        done = repository.run("evidence", "--keep", "test")
        self.assertEqual(done.returncode, 3, done.stdout)

    def test_a_commit_tree_matches_the_kept_record(self):
        """REQ-2956: a reviewer compares a kept record with the commit that carries it."""
        repo = self.repo()
        repo.run("run", "test")
        record = repo.records()[-1]
        repo.run("evidence", "--keep", "test")
        repo.git("add", "-A")
        repo.git("commit", "-q", "-m", "c")
        done = repo.run("tree", "HEAD")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(done.stdout.strip(), record["tree"])
        self.assertNotEqual(repo.git("rev-parse", "HEAD^{tree}").stdout.strip(), record["tree"])


class State(unittest.TestCase):
    """ADR-1530: the ledger is run state and holds to the state rules."""

    PROFILE = '[verbs]\ntest = "echo tested"\n'

    def repo(self, commit=True):
        repository = Repository(self.PROFILE)
        self.addCleanup(repository.close)
        repository.git("init", "-q", "-b", "work")
        if commit:
            repository.git("add", "-A")
            repository.git("commit", "-q", "-m", "first")
        return repository

    def ledger(self, repo):
        return next((repo.state / "meowpaw" / "evidence").glob("*.jsonl"))

    def old_line(self, record="0ld000000000"):
        return json.dumps({"record": record, "verb": "test", "outcome": "passed", "time": "2020-01-01T00:00:00Z",
                           "tree": "x", "tree_before": "x"})

    def test_each_record_names_the_repository_and_work_tree(self):
        """REQ-0752: state can be found by the work tree and by the repository."""
        repo = self.repo()
        repo.run("run", "test")
        record = repo.records()[-1]
        self.assertEqual(record["repository"], repo.git("rev-list", "--max-parents=0", "HEAD").stdout.strip())
        self.assertEqual(record["work_tree"], str(repo.root.resolve()))

    def test_a_corrupt_line_reads_as_absent(self):
        """REQ-0754: a line that doesn't parse is never a result."""
        repo = self.repo()
        repo.run("run", "test")
        with self.ledger(repo).open("a", encoding="utf-8") as f:
            f.write('{"record": "cut sho')
        done = repo.run("evidence", "test")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("records: 1", repo.run("state").stdout)

    def test_state_prints_the_ledger_facts(self):
        """REQ-0756: a person can read where state is and what it holds."""
        repo = self.repo()
        repo.run("run", "test")
        said = repo.run("state").stdout
        for fact in ("ledger: ", "records: 1", "oldest: ", "newest: ", "evidence directory: project/evidence", "lock: "):
            self.assertIn(fact, said)

    def test_old_records_and_their_output_are_pruned(self):
        """REQ-2962: retention is bounded."""
        repo = self.repo()
        repo.run("run", "test")
        ledger = self.ledger(repo)
        output = ledger.with_suffix("") / "0ld000000000.log"
        output.write_text("old\n", encoding="utf-8")
        with ledger.open("a", encoding="utf-8") as f:
            f.write(self.old_line() + "\n")
        done = repo.run("run", "test")
        self.assertIn("pruned 1 records older than 30 days", done.stdout)
        self.assertNotIn("0ld000000000", ledger.read_text(encoding="utf-8"))
        self.assertFalse(output.exists())
        self.assertFalse(list(ledger.parent.glob("*.partial")))

    def test_purge_empties_the_ledger(self):
        """REQ-2962: state is purgeable."""
        repo = self.repo()
        repo.run("run", "test")
        done = repo.run("state", "--purge")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("records: 0", repo.run("state").stdout)

    def test_a_fresh_lock_holds_the_prune_and_the_append_waits(self):
        """REQ-0758, REQ-2958, REQ-2967: a read-modify-write takes a lock in the runtime directory."""
        repo = self.repo()
        repo.run("run", "test")
        ledger = self.ledger(repo)
        with ledger.open("a", encoding="utf-8") as f:
            f.write(self.old_line() + "\n")
        lock = repo.state / f"meowpaw-{ledger.stem}.lock"
        lock.write_text("1", encoding="utf-8")
        env = {**os.environ, "XDG_STATE_HOME": str(repo.state), "XDG_RUNTIME_DIR": str(repo.state),
               "XDG_CONFIG_HOME": str(repo.state), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        running = subprocess.Popen([str(BIN), "run", "test"], cwd=repo.root, env=env, stdout=subprocess.PIPE, text=True)
        import time
        time.sleep(1.0)
        self.assertIsNone(running.poll(), "the append waited for the lock")
        lock.unlink()
        out, _ = running.communicate(timeout=30)
        self.assertNotIn("pruned", out)
        self.assertIn("0ld000000000", ledger.read_text(encoding="utf-8"))
        self.assertEqual(len([r for r in repo.records() if r.get("verb") == "test"]), 3)

    def test_a_stale_lock_is_replaced(self):
        """REQ-2967: a lock a dead process left holds nothing back past a minute."""
        repo = self.repo()
        repo.run("run", "test")
        lock = repo.state / f"meowpaw-{self.ledger(repo).stem}.lock"
        lock.write_text("1", encoding="utf-8")
        os.utime(lock, (0, 0))
        done = repo.run("run", "test")
        self.assertIn("recorded: test", done.stdout)
        self.assertFalse(lock.exists())

    def test_state_off_writes_nothing_outside_the_repository(self):
        """REQ-2960: writing state is suppressible."""
        repo = self.repo()
        done = repo.run("run", "test", env={**os.environ, "MEOWPAW_STATE": "off"})
        self.assertIn("not recorded: test (state writing is off (MEOWPAW_STATE=off))", done.stdout)
        self.assertFalse((repo.state / "meowpaw").exists())

    def test_the_state_directory_moves(self):
        """REQ-2960: the state directory is configurable."""
        repo = self.repo()
        moved = repo.state / "elsewhere"
        repo.run("run", "test", env={**os.environ, "MEOWPAW_STATE_DIR": str(moved)})
        self.assertEqual(len(list((moved / "evidence").glob("*.jsonl"))), 1)

    def test_all_adds_the_other_work_trees(self):
        """REQ-2970: aggregation across work trees is offered, never assumed."""
        repo = self.repo()
        second = repo.state / "second"
        repo.git("worktree", "add", "-q", "-b", "other", str(second))
        repo.run("run", "test")
        env = {**os.environ, "XDG_STATE_HOME": str(repo.state), "XDG_RUNTIME_DIR": str(repo.state),
               "XDG_CONFIG_HOME": str(repo.state), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        subprocess.run([str(BIN), "run", "test"], cwd=second, env=env, capture_output=True, check=False)
        alone = repo.run("evidence", "test").stdout
        self.assertNotIn("== work tree", alone)
        together = repo.run("evidence", "--all", "test").stdout
        self.assertIn(f"== work tree {second.resolve()}", together)


class Launcher(unittest.TestCase):
    """ADR-1270: a launcher with no binary for the machine names the machine and the fix."""

    def test_a_missing_binary_names_the_machine_and_the_reinstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "meow-verbs"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "meow-verbs").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            done = subprocess.run(["sh", str(launcher), "status"], cwd=tmp, capture_output=True, text=True, input="")
            machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("unresolved", done.stdout)
            self.assertIn(machine, done.stdout)
            self.assertIn("reinstall the unit", done.stdout)


if __name__ == "__main__":
    unittest.main()
