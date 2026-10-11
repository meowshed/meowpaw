#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The checks in the gate that hold what the hooks stop (SPC-1240 "How a rule is layered", REQ-2712).

A rule that has to hold is held three times: a hook stops the call, a check in
the gate finds a tree or a history that breaks it, and an instruction says why.
Each check here is the second layer for one hook:

- `trunk`: each commit on the trunk's own line after a baseline is a merge
  GitHub made, so nobody committed there directly (`meow-git commit-guard`,
  BUG-1560).
- `commits`: each commit a branch adds meets the declared convention, carries a
  good signature where the profile requires one, and breaks no exact rule of
  the prose gate, with the judge's model call switched off (`meow-git
  push-guard` and `meow-prose-gate check`, BUG-1561 and BUG-1564).
- `run-state`: no file of a run's own state is tracked, because a run's state
  lives outside the repository (`meow-loop guard`, BUG-1563).

The commit checks read the launchers of this repository's `plugins/`, which
the build stage fills, and the profile of the repository they run in.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The merge of the pull request that wrote this check: a commit on the trunk
# after it that GitHub didn't make is a commit somebody made there directly.
BASELINE = "18d74fb35d2d2ff2873a27ee0d7a217e8a265f8d"
GITHUB = "noreply@github.com"
RUN_STATE = {"run.toml", "log.jsonl"}
UNRESOLVED = 3


def git(root, *args, check=True):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
    done = subprocess.run(["git", *args], cwd=root, env=env, capture_output=True, text=True)
    if check and done.returncode != 0:
        raise SystemExit(f"check_layers: git {' '.join(args)} failed: {done.stderr.strip()}")
    return done


def profile(root):
    path = root / ".meowpaw" / "profile.toml"
    return tomllib.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def short(sha):
    return sha[:8]


def trunk(root, baseline):
    """Each commit on the first-parent line after `baseline` was made by GitHub."""
    if git(root, "merge-base", "--is-ancestor", baseline, "HEAD", check=False).returncode != 0:
        print(f"trunk: unresolved: the baseline {short(baseline)} is not in this history, so nothing was checked")
        return UNRESOLVED
    found = []
    shas = git(root, "rev-list", "--first-parent", f"{baseline}..HEAD").stdout.split()
    for sha in shas:
        email = git(root, "log", "-1", "--format=%ce", sha).stdout.strip()
        if email != GITHUB:
            subject = git(root, "log", "-1", "--format=%s", sha).stdout.strip()
            found.append(f"{short(sha)} {subject}: on the trunk and made by {email}, so not a merged pull request")
    for line in found:
        print(f"trunk: {line}")
    print(f"trunk: {len(shas)} commits after the baseline, {len(found)} findings")
    return 1 if found else 0


def base_of(root, wanted):
    for candidate in (wanted, "origin/main", "main"):
        if candidate and git(root, "rev-parse", "--verify", "-q", candidate, check=False).returncode == 0:
            return candidate
    return None


def launcher(name):
    repository = Path(os.environ.get("CHECK_LAYERS_REPOSITORY", ROOT))
    return repository / "plugins" / name / "bin" / name


def commits(root, base):
    """Each commit `base..HEAD` adds meets the convention, the signature rule and the prose gate's exact rules."""
    resolved = base_of(root, base)
    if resolved is None:
        print("commits: unresolved: no base to compare with, so nothing was checked")
        return UNRESOLVED
    config = profile(root)
    signed = bool(config.get("git", {}).get("require_signatures"))
    allowed = root / ".github" / "allowed_signers"
    shas = git(root, "rev-list", "--no-merges", "--reverse", f"{resolved}..HEAD").stdout.split()
    env = {**os.environ, "MEOW_PROSE_GATE_JUDGE": "/nonexistent"}
    found = []
    for sha in shas:
        subject = git(root, "log", "-1", "--format=%s", sha).stdout.strip()
        message = git(root, "log", "-1", "--format=%B", sha).stdout
        label = f"{short(sha)} {subject}"
        # The sign-off is compared with the author, which is the commit's own.
        author = git(root, "log", "-1", "--format=%an%n%ae", sha).stdout.splitlines()
        scm_env = {**env, "GIT_AUTHOR_NAME": author[0], "GIT_AUTHOR_EMAIL": author[1]}
        scm = subprocess.run([str(launcher("meow-scm")), "check-message"], cwd=root, input=message,
                             capture_output=True, text=True, env=scm_env)
        if scm.returncode == UNRESOLVED:
            print("commits: unresolved: meow-scm can't run here, so no message was checked")
            return UNRESOLVED
        if scm.returncode != 0:
            detail = next((l for l in scm.stdout.splitlines() if l.startswith("line ")), "breaks the convention")
            found.append(f"{label}: {detail}")
        if signed:
            args = ["-c", f"gpg.ssh.allowedSignersFile={allowed}", "log", "-1", "--format=%G?", sha]
            status = git(root, *args).stdout.strip()
            if status != "G":
                found.append(f"{label}: its signature isn't good ({status or 'none'}) against .github/allowed_signers")
        event = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                 "tool_input": {"command": f"git commit -m {shlex.quote(message)}"}}
        prose = subprocess.run([str(launcher("meow-prose-gate")), "check"], cwd=root, input=json.dumps(event),
                               capture_output=True, text=True, env=env)
        if prose.returncode == 2:
            first = (prose.stderr.strip().splitlines() or ["breaks a prose rule"])[0]
            found.append(f"{label}: {first}")
    for line in found:
        print(f"commits: {line}")
    print(f"commits: {len(shas)} commits after {resolved}, {len(found)} findings")
    return 1 if found else 0


def run_state(root):
    """No tracked file is a run's own state."""
    tracked = git(root, "ls-files").stdout.splitlines()
    found = [path for path in tracked if Path(path).name in RUN_STATE]
    for path in found:
        print(f"run-state: {path}: is a run's own state, which lives outside the repository")
    print(f"run-state: {len(tracked)} tracked files, {len(found)} findings")
    return 1 if found else 0


def on_trunk(root):
    name = profile(root).get("git", {}).get("trunk", "main")
    current = git(root, "branch", "--show-current", check=False).stdout.strip()
    return current == name


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base")
    parser.add_argument("--baseline", default=BASELINE)
    parser.add_argument("check", choices=["trunk", "commits", "run-state", "all"])
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.check == "trunk":
        return trunk(root, args.baseline)
    if args.check == "commits":
        return commits(root, args.base)
    if args.check == "run-state":
        return run_state(root)
    status = run_state(root)
    # On the trunk the commits are the trunk's own, and on a branch they are
    # what the branch adds; a detached checkout, as CI makes of a pull request,
    # is the branch case.
    ours = trunk(root, args.baseline) if on_trunk(root) else commits(root, args.base)
    return max(status, ours)


if __name__ == "__main__":
    sys.exit(main())
