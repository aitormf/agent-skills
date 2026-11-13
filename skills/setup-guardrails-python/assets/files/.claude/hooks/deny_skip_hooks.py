#!/usr/bin/env python3
# .claude/hooks/deny_skip_hooks.py
"""PreToolUse: denies the usual ways of skipping the hooks of `git push` and `git commit`.

Defence in depth: the guarantee is the check outside the agent's reach (CI, branch protection).
"""
import json
import re
import sys

from ask_on_force_push import git_invocations

SKIP_ENV = re.compile(r"^(SKIP|SKIP_CLAUDE_REVIEW)=")


def skips_hooks(command: str) -> bool:
    for env, opts, sub, args in git_invocations(command):
        if sub not in ("push", "commit"):
            continue
        if any(SKIP_ENV.match(w) for w in env):
            return True
        if any(o.lower().startswith("core.hookspath") for o in opts):  # git -c core.hooksPath=…
            return True
        if "--no-verify" in args:
            return True
        # `commit -n` is --no-verify; `push -n` is --dry-run and is fine
        if sub == "commit" and any(a.startswith("-") and not a.startswith("--") and "n" in a for a in args):
            return True
    return False


def main() -> int:
    event = json.load(sys.stdin)
    if skips_hooks(event.get("tool_input", {}).get("command", "")):
        decision = {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Skipping the hooks of a push or commit (--no-verify, SKIP=, core.hooksPath) is not allowed.",
        }
        print(json.dumps({"hookSpecificOutput": decision}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
