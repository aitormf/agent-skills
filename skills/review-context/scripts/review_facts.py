#!/usr/bin/env python3
"""Facts of a branch for the review, gathered without a model (D-0057).

    python3 review_facts.py <base>     # from the repo root

Section "TODO sin ticket": the TODO, FIXME, XXX and HACK comments that `git diff <base>...HEAD`
adds, with no ticket on the same line, one `file:line` per line. A ticket is `#<n>`,
`<PROJECT>-<n>` or a URL. Only the comment shape counts: the word in capitals, then `:`
(optionally `(...)` between). Lockfiles (those of diff_size.py) and deleted files are skipped.
"""
import re
import subprocess
import sys

LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "uv.lock", "poetry.lock",
             "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock"}
MARK = re.compile(r"\b(?:TODO|FIXME|XXX|HACK)\b(?:\([^)]*\))?:")
TICKET = re.compile(r"#\d+|\b[A-Z][A-Z0-9]*-\d+\b|https?://")
HUNK = re.compile(r"^@@ -\S+ \+(\d+)")


def todos_without_ticket(base):
    run = subprocess.run(["git", "-c", "core.quotepath=off", "diff", "-U0", "--no-ext-diff", "-M",
                          f"{base}...HEAD", "--"], capture_output=True, text=True)
    if run.returncode:
        sys.exit(f"review_facts: git diff failed: {run.stderr.strip()}")
    found, path, line = [], None, 0
    for text in run.stdout.splitlines():
        if text.startswith("+++ "):
            path = text[6:] if text.startswith("+++ b/") else None
            if path and path.rsplit("/", 1)[-1] in LOCKFILES:
                path = None
        elif m := HUNK.match(text):
            line = int(m.group(1))
        elif path and text.startswith("+"):
            if MARK.search(text) and not TICKET.search(text):
                found.append(f"{path}:{line}")
            line += 1
    return found


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: review_facts.py <base>")
    print("TODO sin ticket:")
    print("\n".join(todos_without_ticket(sys.argv[1])) or "ninguno")
    return 0


if __name__ == "__main__":
    sys.exit(main())
