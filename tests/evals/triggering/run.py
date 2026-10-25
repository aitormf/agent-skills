#!/usr/bin/env python3
"""Activation suite: checks that real requests invoke the expected skill.

Runs each case of cases.tsv with `claude -p --plugin-dir <repo>` in an empty directory and
reads the first Skill call from the stream-json output. Needs network and a logged-in claude;
it is not part of scripts/check.sh (only the parser is, via --self-test).

    tests/evals/triggering/run.py [--model M] [--runs N] [--jobs J] [--only SKILL] [--save]
"""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
import tempfile
import threading
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PLUGIN = json.loads((REPO / ".claude-plugin/plugin.json").read_text())["name"]
# The agent may read and search, but never change anything or leave the sandbox.
DISALLOWED = ["Bash", "Edit", "Write", "NotebookEdit", "Agent", "WebFetch", "WebSearch"]
TIMEOUT = 180


def load_cases(path: Path) -> list[tuple[set[str], str]]:
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        expected, prompt = line.split("\t", 1)
        cases.append((set(expected.split("|")), prompt.strip()))
    return cases


def first_skill(lines: Iterable[str]) -> str | None:
    """First skill invoked in a stream-json transcript, or None."""
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                return str(block.get("input", {}).get("skill", ""))
    return None


def verdict(expected: set[str], skill: str | None) -> bool:
    ours = skill.removeprefix(f"{PLUGIN}:") if skill and skill.startswith(f"{PLUGIN}:") else None
    if expected == {"none"}:
        return ours is None
    return ours in expected


def run_case(prompt: str, model: str | None) -> str | None:
    cmd = ["claude", "-p", prompt, "--plugin-dir", str(REPO), "--setting-sources", "",
           "--strict-mcp-config", "--no-session-persistence", "--max-turns", "4",
           "--output-format", "stream-json", "--verbose", "--disallowed-tools", *DISALLOWED]
    if model:
        cmd += ["--model", model]
    with tempfile.TemporaryDirectory() as cwd:
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                stdin=subprocess.DEVNULL, text=True)
        assert proc.stdout is not None
        # A stalled claude would block the read for good: kill it after TIMEOUT, which ends the read.
        timer = threading.Timer(TIMEOUT, proc.kill)
        timer.start()
        try:
            # Stop as soon as the first skill shows up: the rest of the run costs and tells nothing.
            skill = first_skill(proc.stdout)
        finally:
            timer.cancel()
            proc.kill()
            proc.wait(timeout=TIMEOUT)
    return skill


def self_test() -> None:
    call = {"type": "assistant", "message": {"content": [
        {"type": "text", "text": "x"},
        {"type": "tool_use", "name": "Skill", "input": {"skill": f"{PLUGIN}:review-pr"}}]}}
    other = {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Read", "input": {"file_path": "a"}}]}}
    lines = ["no json", json.dumps({"type": "system"}), json.dumps(other), json.dumps(call)]
    assert first_skill(lines) == f"{PLUGIN}:review-pr"
    assert first_skill(lines[:3]) is None
    assert verdict({"review-pr"}, f"{PLUGIN}:review-pr")
    assert not verdict({"review-pr"}, "code-review")
    assert verdict({"none"}, None) and verdict({"none"}, "simplify")
    assert not verdict({"none"}, f"{PLUGIN}:idea-to-spec")
    assert verdict({"a", "b"}, f"{PLUGIN}:b")
    cases = load_cases(HERE / "cases.tsv")
    skills = {p.name for p in (REPO / "skills").iterdir() if (p / "SKILL.md").exists()}
    unknown = {s for exp, _ in cases for s in exp} - skills - {"none"}
    assert not unknown, f"cases.tsv names unknown skills: {unknown}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model")
    ap.add_argument("--runs", type=int, default=1, help="runs per case (default 1)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", help="only the cases that expect this skill")
    ap.add_argument("--save", action="store_true", help="write the results to results/<date>.json")
    ap.add_argument("--self-test", action="store_true", help="test the parser, without claude")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0

    cases = [c for c in load_cases(HERE / "cases.tsv") if not args.only or args.only in c[0]]
    jobs = [(exp, prompt) for exp, prompt in cases for _ in range(args.runs)]
    with ThreadPoolExecutor(args.jobs) as pool:
        got = list(pool.map(lambda j: run_case(j[1], args.model), jobs))

    results = []
    for (exp, prompt), skill in zip(jobs, got):
        ok = verdict(exp, skill)
        results.append({"expected": sorted(exp), "prompt": prompt, "got": skill, "ok": ok})
        print(f"{'✔' if ok else '✘'} {'|'.join(sorted(exp)):26} {skill or '-':34} {prompt}")
    passed = sum(r["ok"] for r in results)
    print(f"\n{passed}/{len(results)} OK")

    if args.save:
        out = HERE / "results" / f"{datetime.date.today()}.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps({"model": args.model, "runs": args.runs, "passed": passed,
                                   "total": len(results), "results": results},
                                  ensure_ascii=False, indent=2) + "\n")
        print(f"saved to {out.relative_to(REPO)}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
