#!/usr/bin/env python3
"""Check a docs/decisions/ directory: frontmatter, numbering, supersession links and index.

Usage:
  check_decisions.py [DIR]           check DIR (default docs/decisions); exit 1 on errors
  check_decisions.py [DIR] --next    print the next free id (D-NNNN) and exit

Each decision is DIR/NNNN-title.md and starts with a frontmatter block. The index is
DIR/README.md, with one table row per decision: | [D-NNNN](NNNN-title.md) | title | type | status | affects |
"""

import re
import sys
from pathlib import Path

TYPES = {"architecture", "rule", "discarded"}
STATUSES = {"proposed", "accepted", "superseded", "obsolete"}
REQUIRED = ["id", "title", "type", "status", "date", "affects", "supersedes", "superseded_by"]
FILE_RE = re.compile(r"^(\d{4})-[a-z0-9][a-z0-9-]*\.md$")
ROW_RE = re.compile(r"^\|\s*\[(D-\d{4})\]\(([^)]+)\)\s*\|(.*)\|\s*$")


def frontmatter(text: str) -> dict[str, str] | None:
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "#")):
            key, value = line.split(":", 1)
            fields[key.strip()] = re.sub(r"\s+#.*$", "", value).strip().strip("\"'")
    return fields


def null(value: str) -> bool:
    return value in ("", "null", "~")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    decisions: dict[str, dict[str, str]] = {}
    files: dict[str, str] = {}
    for path in sorted(root.glob("*.md")):
        if path.name == "README.md":
            continue
        name = path.name
        match = FILE_RE.match(name)
        if not match:
            errors.append(f"{name}: name must be NNNN-title-in-kebab-case.md")
            continue
        fm = frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{name}: no frontmatter at the start of the file")
            continue
        missing = [k for k in REQUIRED if k not in fm]
        if missing:
            errors.append(f"{name}: missing {', '.join(missing)}")
            continue
        expected_id = f"D-{match.group(1)}"
        if fm["id"] != expected_id:
            errors.append(f"{name}: id is {fm['id']}, the file name says {expected_id}")
        if expected_id in decisions:
            errors.append(f"{name}: number {match.group(1)} is already used by {files[expected_id]}")
        if fm["type"] not in TYPES:
            errors.append(f"{name}: type '{fm['type']}' is not one of {sorted(TYPES)}")
        if fm["status"] not in STATUSES:
            errors.append(f"{name}: status '{fm['status']}' is not one of {sorted(STATUSES)}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fm["date"]):
            errors.append(f"{name}: date '{fm['date']}' is not YYYY-MM-DD")
        decisions[expected_id] = fm
        files[expected_id] = name

    for did, fm in decisions.items():
        name = files[did]
        new = fm["superseded_by"]
        if fm["status"] == "superseded" and null(new):
            errors.append(f"{name}: status superseded but superseded_by is empty")
        if not null(new):
            if new not in decisions:
                errors.append(f"{name}: superseded_by {new} does not exist")
            elif decisions[new]["supersedes"] != did:
                errors.append(f"{name}: superseded_by {new}, but {new} does not say supersedes: {did}")
            if fm["status"] != "superseded":
                errors.append(f"{name}: superseded_by {new} but status is {fm['status']}")
        old = fm["supersedes"]
        if not null(old):
            if old not in decisions:
                errors.append(f"{name}: supersedes {old}, which does not exist")
            elif decisions[old]["superseded_by"] != did:
                errors.append(f"{name}: supersedes {old}, but {old} does not say superseded_by: {did}")

    index = root / "README.md"
    if not index.exists():
        return errors + ["README.md: the index is missing"]
    rows: dict[str, list[str]] = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        did, link, rest = match.groups()
        cells = [c.strip() for c in rest.split("|")]
        if did in rows:
            errors.append(f"README.md: {did} appears twice")
        rows[did] = cells
        if did in files and link != files[did]:
            errors.append(f"README.md: {did} links to {link}, the file is {files[did]}")
    for did, fm in decisions.items():
        if did not in rows:
            errors.append(f"README.md: no row for {did}")
            continue
        cells = rows[did]
        if len(cells) < 4:
            errors.append(f"README.md: the row of {did} needs title, type, status and affects")
            continue
        if cells[1] != fm["type"] or cells[2] != fm["status"]:
            errors.append(f"README.md: {did} says {cells[1]}/{cells[2]}, the file says {fm['type']}/{fm['status']}")
    for did in rows.keys() - decisions.keys():
        errors.append(f"README.md: row {did} has no decision file")
    return errors


def next_id(root: Path) -> str:
    numbers = [int(m.group(1)) for p in root.glob("*.md") if (m := FILE_RE.match(p.name))]
    return f"D-{max(numbers, default=0) + 1:04d}"


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--next"]
    root = Path(args[0] if args else "docs/decisions")
    if not root.is_dir():
        print(f"check_decisions: {root} is not a directory", file=sys.stderr)
        return 2
    if "--next" in sys.argv[1:]:
        print(next_id(root))
        return 0
    errors = check(root)
    for error in errors:
        print(f"{root}/{error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
