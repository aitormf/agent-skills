#!/usr/bin/env python3
"""Size of a diff for the review (R1, D-0045): lines added + deleted, tests included.

    python3 diff_size.py <base>...<head>     # from the repo root

Does not count lockfiles (by name), snapshots (`__snapshots__/`, `*.snap`) nor files marked
`linguist-generated` in `.gitattributes` (read from the working tree, with `git check-attr`);
binaries count 0. A renamed file counts only the lines that change in it (`git diff -M`).

Prints `<n> lines, small (at most 200)` or `<n> lines, large (more than 200)`. Exit 0; 2 if the
range does not exist.
"""
import subprocess
import sys

SMALL = 200
LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "uv.lock", "poetry.lock",
             "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock"}


def git(*args, stdin=None):
    run = subprocess.run(["git", *args], input=stdin, capture_output=True, text=True)
    if run.returncode:
        sys.exit(f"diff_size: git {args[0]} failed: {run.stderr.strip()}")
    return run.stdout


def changes(range_):
    """[(path, added, deleted)] from `git diff --numstat -z -M`; binaries are (path, 0, 0); a rename is its new path."""
    out, items, i = git("diff", "--numstat", "-z", "-M", "--no-ext-diff", range_, "--").split("\0"), [], 0
    while i < len(out) and out[i]:
        added, deleted, path = out[i].split("\t", 2)
        i += 1
        if not path:  # rename: "a\td\t", old, new
            path, i = out[i + 1], i + 2
        items.append((path, 0 if added == "-" else int(added), 0 if deleted == "-" else int(deleted)))
    return items


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: diff_size.py <base>...<head>")
    try:
        items = changes(sys.argv[1])
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2
    attrs = git("check-attr", "-z", "--stdin", "linguist-generated", stdin="".join(p + "\0" for p, *_ in items)).split("\0")
    generated = {attrs[i] for i in range(0, len(attrs) - 2, 3) if attrs[i + 2] in ("set", "true")}
    total = 0
    for path, added, deleted in items:
        name = path.rsplit("/", 1)[-1]
        if name in LOCKFILES or name.endswith(".snap") or "__snapshots__/" in f"/{path}" or path in generated:
            continue
        total += added + deleted
    print(f"{total} lines, " + ("small (at most 200)" if total <= SMALL else "large (more than 200)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
