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
import shutil
import subprocess
import sys

TIMEOUT = 600  # it indexes the base in a temporary worktree, so it can take a while
NEW_OR_WORSE = ("new_cycles", "new_god_modules", "new_sdp_violations", "instability_regressions",
                "worsened_functions", "new_hotspots", "worsened_hotspots")
RESOLVED = ("resolved_cycles", "resolved_god_modules", "resolved_sdp_violations", "improved_functions")


def lines(result):
    """The finding lines of a diff result, in the order of NEW_OR_WORSE."""
    for cycle in result.get("new_cycles", []):
        yield "cycle " + " → ".join([*cycle, cycle[0]])
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


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: debtector_diff.py <base>")
    if not shutil.which("debtector"):
        print("debtector_diff: debtector is not on PATH", file=sys.stderr)
        return 2
    try:
        run = subprocess.run(["debtector", "--json", "diff", "--base", sys.argv[1]],
                             capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"debtector_diff: debtector took more than {TIMEOUT} s", file=sys.stderr)
        return 2
    try:
        if run.returncode not in (0, 1):
            raise ValueError
        result = json.loads(run.stdout)
        out = list(lines(result))
    except (ValueError, KeyError, TypeError):
        print(f"debtector_diff: debtector failed (exit {run.returncode}): {run.stderr.strip()[-500:]}", file=sys.stderr)
        return 2
    for line in out:
        print(line)
    for s in result.get("skipped", []):
        print(f"skipped {s['section']}: {s['reason']}")
    new = sum(len(result.get(k, [])) for k in NEW_OR_WORSE)
    resolved = sum(len(result.get(k, [])) for k in RESOLVED)
    block = "; would block its CI job" if run.returncode == 1 else ""
    print(f"debtector: {new} new or worse; {resolved} resolved{block}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
