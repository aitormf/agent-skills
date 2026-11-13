#!/usr/bin/env python3
# .claude/hooks/ask_on_force_push.py
"""PreToolUse: before a forced `git push`, asks the person for confirmation."""

import json
import shlex
import sys

SEPARATORS = {"&&", "||", ";", "|", "&"}
GIT_FLAGS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def git_invocations(command: str):
    """Yields (words before `git` in its segment, git options, subcommand, its args) per `git` found."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)  # splits ";", "&&", "|"… even when not space-separated
    except ValueError:
        return
    for i, word in enumerate(tokens):
        if word != "git":
            continue
        start = i
        while start > 0 and tokens[start - 1] not in SEPARATORS:
            start -= 1
        j = i + 1
        while j < len(tokens) and tokens[j].startswith("-"):  # git -C <dir> push …
            j += 2 if tokens[j] in GIT_FLAGS_WITH_VALUE else 1
        if j >= len(tokens):
            continue
        end = next((k for k in range(j + 1, len(tokens)) if tokens[k] in SEPARATORS), len(tokens))
        yield tokens[start:i], tokens[i + 1 : j], tokens[j], tokens[j + 1 : end]


def is_force_push(command: str) -> bool:
    for _, _, sub, args in git_invocations(command):
        if sub != "push":
            continue
        for arg in args:
            if arg.startswith(("--force", "+")):  # --force, --force-with-lease, +refspec
                return True
            if arg.startswith("-") and not arg.startswith("--") and "f" in arg:  # -f, -uf
                return True
    return False


def main() -> int:
    event = json.load(sys.stdin)
    if is_force_push(event.get("tool_input", {}).get("command", "")):
        decision = {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": "Forced push: it can overwrite others' history.",
        }
        print(json.dumps({"hookSpecificOutput": decision}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
