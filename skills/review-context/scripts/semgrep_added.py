#!/usr/bin/env python3
"""Semgrep on the lines a branch adds, not on whole files: the debt already there is not the author's.

    python3 semgrep_added.py <base>     # from the repo root; compares <base>...HEAD

Runs `semgrep scan --config p/default` on the files the diff adds or changes and prints only the
findings that touch an added line, one per line (`path:line severity rule — message`), then a
count of the findings it left out, which are on lines the diff did not touch.

Exit 0 with or without findings; 2 if semgrep is not on PATH or fails (say "Semgrep not
available — skipped" or quote the error, and go on with the review).
"""
import json
import re
import shutil
import subprocess
import sys


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def added_lines(base):
    """{path: set of line numbers} added or changed by <base>...HEAD."""
    added, path = {}, None
    for line in git("diff", "--unified=0", "--no-color", "--no-ext-diff", f"{base}...HEAD").splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@") and path:
            m = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", line)
            start, count = int(m.group(1)), int(m.group(2) or 1)
            added.setdefault(path, set()).update(range(start, start + count))
    return added


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: semgrep_added.py <base>")
    if not shutil.which("semgrep"):
        print("semgrep_added: semgrep is not on PATH", file=sys.stderr)
        return 2
    added = added_lines(sys.argv[1])
    if not added:
        print("Semgrep: no added lines to scan")
        return 0
    run = subprocess.run(["semgrep", "scan", "--config", "p/default", "--metrics=off", "--quiet", "--json", *sorted(added)],
                         capture_output=True, text=True)
    try:
        results = json.loads(run.stdout)["results"]
    except (ValueError, KeyError):
        print(f"semgrep_added: semgrep failed (exit {run.returncode}): {run.stderr.strip()[-500:]}", file=sys.stderr)
        return 2
    kept = [r for r in results
            if added.get(r["path"], set()) & set(range(r["start"]["line"], r["end"]["line"] + 1))]
    for r in kept:
        extra = r.get("extra", {})
        message = " ".join(extra.get("message", "").split())
        print(f"{r['path']}:{r['start']['line']} {extra.get('severity', '?')} {r['check_id']} — {message}")
    print(f"Semgrep: {len(kept)} finding(s) on added lines; {len(results) - len(kept)} on lines the diff did not touch (not reported)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
