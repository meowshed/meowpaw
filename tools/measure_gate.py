#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Measure a blocking hook as a classifier, from the hook's own verdict.

SPC-1020 measures a prompt that blocks by how often it blocks each kind of
labelled text. `claude plugin eval` runs its sessions without a shell, so a
hook on `Bash` never fires there. This runs each case as a real session instead:
a fresh git repository, the unit under test installed from its directory, and
Bash allowed. It reads the verdict from the hook's answer in the debug log, so
no judge is needed, and a run where the hook never answered counts as an error
and never as a pass.

    python3 tools/measure_gate.py plugins/meow-prose-gate --runs 5

Every run is a real model call, so the gate never runs this.
"""

import argparse
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

VERDICT = re.compile(r"Hooks: Model response: (\{.*)")
ASK = ("Run exactly the command below with the Bash tool, once. If a hook blocks it, "
       "don't change the text and don't run it again.\n\n```bash\n{cmd}\n```\n")


def cases(unit):
    for prompt in sorted((unit / "evals").glob("*/prompt.md")):
        text = prompt.read_text(encoding="utf-8")
        kind = "defect" if re.search(r"^tags: \[defect\]", text, re.M) else "clean"
        cmd = re.search(r"```bash\n(.*?)\n```", text, re.S).group(1)
        yield prompt.parent.name, kind, cmd


def run(unit, model, name, cmd):
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=work, check=True)
        log = work / "debug.log"
        subprocess.run(
            ["claude", "-p", ASK.format(cmd=cmd), "--model", model, "--plugin-dir", str(unit.resolve()),
             "--allowedTools", "Bash", "--max-turns", "3", "--debug-file", str(log),
             "--settings", json.dumps({"enabledPlugins": {"meow-prose@meowpaw": False, "meow-core@meowpaw": False}})],
            cwd=work, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600)
        answers = VERDICT.findall(log.read_text(encoding="utf-8", errors="replace")) if log.exists() else []
    if not answers:
        return name, None, "the hook never answered"
    blocked = '"ok": false' in answers[0].replace('"ok":false', '"ok": false')
    return name, blocked, answers[0][:300]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("unit", type=Path)
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    args = ap.parse_args()
    labelled = list(cases(args.unit))
    kinds = {name: kind for name, kind, _ in labelled}
    jobs = [(name, cmd) for name, _, cmd in labelled for _ in range(args.runs)]
    with ThreadPoolExecutor(args.jobs) as pool:
        results = list(pool.map(lambda j: run(args.unit, args.model, *j), jobs))
    table = {}
    for name, blocked, detail in results:
        row = table.setdefault(name, {"blocked": 0, "passed": 0, "errors": 0, "first": detail})
        row["errors" if blocked is None else "blocked" if blocked else "passed"] += 1
    print(f"{args.unit.name} on {args.model}, {args.runs} runs per case, verdicts from the hook's own answer\n")
    print("| Case | Kind | Blocked | Passed | Errors |\n| --- | --- | --- | --- | --- |")
    for name in sorted(table):
        r = table[name]
        print(f"| {name} | {kinds[name]} | {r['blocked']} | {r['passed']} | {r['errors']} |")
    for kind, want in (("defect", "blocked"), ("clean", "passed")):
        rows = [r for n, r in table.items() if kinds[n] == kind]
        done = sum(r["blocked"] + r["passed"] for r in rows)
        print(f"\n{kind}: {sum(r[want] for r in rows)} of {done} {want}, {sum(r['errors'] for r in rows)} errors")
    print("\nFirst answer per case:")
    for name in sorted(table):
        print(f"- {name}: {table[name]['first']}")


if __name__ == "__main__":
    main()
