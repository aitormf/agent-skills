#!/usr/bin/env python3
"""What the branch adds to the dependency graph, according to debtector, one finding per line.

    python3 debtector_diff.py <base>     # from the repo root; compares <base> with the working tree

Runs `debtector --json diff --base <base>` and prints one line per new cycle, god module, SDP
violation, instability regression, worsened function and new or worsened hotspot, then a line
for each section debtector skipped, then a count: `debtector: <n> new or worse; <m> resolved`,
ending in `; would block its CI job` if debtector exited 1 (something new has severity error in
debtector.toml). Improvements are only counted. debtector never blocks the push (D-0063).

Exit 0 with or without findings; 2 if debtector is not on PATH or fails (say "debtector not
available — skipped" or quote the error, and go on with the review).
"""
import json
import os
import shutil
import signal
import subprocess
import sys

TIMEOUT = 600  # it indexes the base in a temporary worktree, so it can take a while
GRACE = 30  # seconds debtector gets after SIGINT to remove its worktree before it is killed
WORKTREE_PREFIX = "debtector-diff-"  # tempfile prefix of the worktree debtector diff --base creates
NEW_OR_WORSE = ("new_cycles", "new_god_modules", "new_sdp_violations", "instability_regressions",
                "worsened_functions", "new_hotspots", "worsened_hotspots")
RESOLVED = ("resolved_cycles", "resolved_god_modules", "resolved_sdp_violations", "improved_functions")


def lines(result):
    """The finding lines of a diff result, in the order of NEW_OR_WORSE."""
    for cycle in result.get("new_cycles", []):
        # A cycle is a strongly connected component, not an ordered path: with three or more
        # modules the order says nothing about which imports which, so only list the members.
        if len(cycle) == 2:
            yield "cycle " + " → ".join([*cycle, cycle[0]])
        else:
            yield "cycle among " + ", ".join(cycle)
    for path in result.get("new_god_modules", []):
        yield f"god module {path}"
    for v in result.get("new_sdp_violations", []):
        yield (f"sdp {v['source']} → {v['target']} "
               f"(instability {v['source_instability']} → {v['target_instability']})")
    for r in result.get("instability_regressions", []):
        yield f"instability {r['file_path']} {r['before']} → {r['after']}"
    for f in result.get("worsened_functions", []):
        before = "new" if f["before"] is None else f["before"]
        yield f"complexity {f['qualified_name']} {before} → {f['after']} ({f['severity']})"
    for h in result.get("new_hotspots", []):
        yield f"hotspot {h['file_path']} churn {h['churn']} complexity {h['complexity']} ({h['severity']})"
    for h in result.get("worsened_hotspots", []):
        yield (f"hotspot {h['file_path']} complexity {h['complexity_before']} → {h['complexity_after']} "
               f"({h['severity_before']} → {h['severity']})")


def one_line(text):
    """*text* with its line breaks escaped, so one finding is always one line."""
    return text.replace("\n", "\\n").replace("\r", "\\r")


def remove_leftover_worktrees():
    """Remove the worktrees a killed debtector left registered; the others are not touched."""
    listed = subprocess.run(["git", "worktree", "list", "--porcelain"], capture_output=True, text=True)
    for line in listed.stdout.splitlines():
        path = line.removeprefix("worktree ")
        if line.startswith("worktree ") and WORKTREE_PREFIX in path:
            subprocess.run(["git", "worktree", "remove", "--force", path], capture_output=True)
    subprocess.run(["git", "worktree", "prune"], capture_output=True)


def run_debtector(base):
    """(exit code, stdout, stderr) of debtector diff, or None if it went over TIMEOUT.

    On timeout it gets SIGINT first, so its own cleanup removes the temporary worktree; if it is
    still running after GRACE seconds, it is killed and its leftover worktree removed here.
    """
    process = subprocess.Popen(["debtector", "--json", "diff", "--base", base], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True,
                               start_new_session=True)
    try:
        out, err = process.communicate(timeout=TIMEOUT)
        return process.returncode, out, err
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGINT)
        try:
            process.communicate(timeout=GRACE)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
        remove_leftover_worktrees()
        return None


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: debtector_diff.py <base>")
    if not shutil.which("debtector"):
        print("debtector_diff: debtector is not on PATH", file=sys.stderr)
        return 2
    try:
        run = run_debtector(sys.argv[1])
    except OSError as error:
        print(f"debtector_diff: debtector could not start: {error}", file=sys.stderr)
        return 2
    if run is None:
        print(f"debtector_diff: debtector took more than {TIMEOUT} s", file=sys.stderr)
        return 2
    code, stdout, stderr = run
    try:
        if code not in (0, 1):
            raise ValueError
        result = json.loads(stdout)
        out = list(lines(result))
        out += [f"skipped {s['section']}: {s['reason']}" for s in result.get("skipped", [])]
    except (ValueError, KeyError, TypeError):
        print(f"debtector_diff: debtector failed (exit {code}): {stderr.strip()[-500:]}", file=sys.stderr)
        return 2
    for line in out:
        print(one_line(line))
    new = sum(len(result.get(k, [])) for k in NEW_OR_WORSE)
    resolved = sum(len(result.get(k, [])) for k in RESOLVED)
    block = "; would block its CI job" if code == 1 else ""
    print(f"debtector: {new} new or worse; {resolved} resolved{block}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
