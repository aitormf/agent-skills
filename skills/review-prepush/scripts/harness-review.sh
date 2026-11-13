#!/usr/bin/env bash
# review-kit — harness-review, pre-push hook of the kit (D-0055)
#
# Runs /review-prepush headless with Claude Code and blocks the push ONLY when the
# review reports at least one confirmed Critical finding. Anything else (Required,
# Optional, tool errors, missing claude CLI) lets the push through with a message.
#
# Install:  the `harness-review` hook of .pre-commit-hooks.yaml (prek install). It runs the
# workflow gate first: with the gate red (exit 1) it blocks the push without launching the reviewer.
#
# Environment knobs:
# The review runs only on the push of an agent (CLAUDECODE=1, CODEX_THREAD_ID, OPENCODE=1); the
# four variables below that change or skip it are ignored then, and only a person's push honours them.
#   SKIP_CLAUDE_REVIEW=1        skip the review for this push (or use `git push --no-verify`)
#   REVIEW_KIT_COMMAND=...      skill to run (default /harness:review-prepush)
# The review comes from the kit copy next to this script (the pinned rev), never from the branch under
# review (R8): claude loads it with --plugin-dir, codex gets the path of its SKILL.md and personas.
#   REVIEW_KIT_TIMEOUT=900      seconds before giving up (fail-open)
#   REVIEW_KIT_FAIL_CLOSED=1    block the push when the review itself fails
#   REVIEW_KIT_ALLOWED_TOOLS    override --allowedTools (see README "Permisos en modo headless")
#   REVIEW_KIT_MODEL            pass --model to claude (e.g. a faster model for pre-push)
#   REVIEW_KIT_BASE=...         base branch for the verdict cache (default: origin/HEAD, origin/main,
#                               origin/master, main or master)
#   REVIEW_KIT_RERUN=1          ignore a saved verdict and review again
#
# Verdict cache: the result is saved in .git/review-kit/verdicts with the sha256 of
# `git diff <base>...HEAD`. A later push of the same diff (a retry after a network error,
# another remote) reuses it instead of paying for the review again; any change to the
# diff invalidates it. Each line ends with the family of the reviewer (R6): a PASS is reused only if
# that family is not an author of the push. Without a base branch nothing is cached.

set -u

# Who pushes (D-0056): the families of the agent, by concrete markers of the environment the hook
# inherits (never prefixes: a Codex launched from Claude Code inherits CLAUDE_CODE_* but not CLAUDECODE).
authors=""
[ "${CLAUDECODE:-}" = "1" ] && authors="claude"
[ -n "${CODEX_THREAD_ID:-}" ] && authors="${authors:+$authors }codex"
[ "${OPENCODE:-}" = "1" ] && authors="${authors:+$authors }opencode"
if [ -n "$authors" ]; then
  # An agent cannot turn the review off nor change how it runs.
  unset SKIP_CLAUDE_REVIEW REVIEW_KIT_COMMAND REVIEW_KIT_ALLOWED_TOOLS REVIEW_KIT_MODEL REVIEW_KIT_TIMEOUT
  echo "review-kit: autor: $authors" >&2
elif [ "${SKIP_CLAUDE_REVIEW:-0}" = "1" ]; then
  echo "review-kit: SKIP_CLAUDE_REVIEW=1 — review skipped."; exit 0
fi

# Skip pushes that only delete refs.
# (prek and pre-commit give the hook no ref list: no lines is not a delete.)
only_deletes=0
while read -r _local_ref local_sha _remote_ref _remote_sha; do
  case "$local_sha" in
    *[!0]*) only_deletes=0 ;;
    *) only_deletes=1 ;;
  esac
done
[ "$only_deletes" = "1" ] && exit 0

fail() {
  echo "review-kit: $1" >&2
  if [ "${REVIEW_KIT_FAIL_CLOSED:-0}" = "1" ]; then
    echo "review-kit: REVIEW_KIT_FAIL_CLOSED=1 → push blocked." >&2
    exit 1
  fi
  echo "review-kit: push continues (fail-open)." >&2
  exit 0
}

# The gate first (D-0055): a red gate means the push is blocked anyway, so the reviewer is not paid for.
gate="$(cd "$(dirname "$0")" && pwd)/../../task-done/scripts/gate.py"
python3 "$gate" </dev/null; gate_rc=$?
if [ $gate_rc -eq 1 ]; then
  echo "review-kit: gate en rojo: no se lanza el revisor." >&2
  exit 1
fi
[ $gate_rc -ne 0 ] && fail "the gate could not check the branch (exit $gate_rc); the review continues without it."

if [ -z "$authors" ]; then
  echo "review-kit: push de una persona: sin review automática." >&2
  exit 0
fi

repo_root=$(git rev-parse --show-toplevel) || fail "could not determine the repo root."
cd "$repo_root" || fail "could not cd into $repo_root."

kit=$(cd "$(dirname "$0")/../../.." && pwd) || fail "could not find the kit."   # the pinned copy of the kit, never the branch under review
cmd="${REVIEW_KIT_COMMAND:-/harness:review-prepush}"   # an agent push always gets the default (the variable is unset above)

# Read-only by design: no Edit/Write. Bash stays allowed because the repo's own check
# commands (declared in AGENTS.md) are arbitrary; the prompt forbids state-changing
# commands, and the deny list below plus the repo's .claude/settings.json deny rules
# are enforced by Claude Code regardless of the prompt. Bash(gh:*) is only a prefix rule
# (/usr/bin/gh or `bash -c 'gh …'` get past it): the real control is that claude runs
# with no GitHub credentials (no token variables, an empty gh config directory).
allowed="${REVIEW_KIT_ALLOWED_TOOLS:-Read,Grep,Glob,Agent,Bash}"
denied="Edit,Write,NotebookEdit,Bash(git push:*),Bash(git commit:*),Bash(git reset:*),Bash(git checkout:*),Bash(git switch:*),Bash(git rebase:*),Bash(git merge:*),Bash(git stash:*),Bash(git clean:*),Bash(rm:*),Bash(gh:*)"

out_dir="$(git rev-parse --git-dir)/review-kit"
mkdir -p "$out_dir"
report="$out_dir/last-prepush.md"
verdicts="$out_dir/verdicts"

# The diff the review sees (review-prepush compares <base>...HEAD), hashed.
base="${REVIEW_KIT_BASE:-}"
if [ -z "$base" ]; then
  base=$(git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null)
  for b in origin/main origin/master main master; do
    [ -n "$base" ] && break
    git rev-parse -q --verify "$b^{commit}" >/dev/null 2>&1 && base=$b
  done
fi
# Who reviews (D-0056): the list of the base branch, never the branch's own; none left blocks the push.
chosen=$(python3 "$(dirname "$0")/reviewer.py" "$base" $authors); rrc=$?
[ $rrc -eq 1 ] && exit 1
reviewer=""; copts=()   # the first line is the reviewer; for codex the rest are its options
while IFS= read -r line; do if [ -z "$reviewer" ]; then reviewer=$line; else copts+=("$line"); fi; done <<<"$chosen"
[ $rrc -ne 0 ] && fail "could not choose a reviewer."

key=""
if [ -n "$base" ] && git merge-base "$base" HEAD >/dev/null 2>&1; then   # no common history: no diff to key on
  for h in sha256sum "shasum -a 256"; do
    command -v "${h%% *}" >/dev/null 2>&1 || continue
    key=$(git diff --binary "$base...HEAD" 2>/dev/null | $h | cut -d' ' -f1) && break
  done
fi

if [ -n "$key" ] && [ "${REVIEW_KIT_RERUN:-0}" != "1" ] && [ -f "$verdicts" ]; then
  # A PASS counts only from a reviewer of another family than the authors of this push, and an old line
  # without family does not (R6); a BLOCK blocks whoever wrote it: stopping is never a self-review.
  saved=$(awk -v k="$key" -v a=" $authors " '$1 == k && ($2 == "BLOCK" || ($5 != "" && index(a, " " $5 " ") == 0))' "$verdicts" | tail -n 1)
  case "$saved" in
    *" BLOCK "*)
      echo "review-kit: ✋ push blocked — this diff was already reviewed with confirmed Critical findings (${saved#* BLOCK })." >&2
      echo "review-kit: report: $out_dir/$key.md. Change the diff, set REVIEW_KIT_RERUN=1 to review again, or 'git push --no-verify'." >&2
      exit 1 ;;
    *" PASS "*)
      echo "review-kit: ✅ this diff was already reviewed with no confirmed Critical findings (${saved#* PASS }); REVIEW_KIT_RERUN=1 to review again." >&2
      exit 0 ;;
  esac
fi
remember() {  # remember PASS|BLOCK: the verdict for this diff, with its base and date, and its report
  [ -n "$key" ] || return 0
  echo "$key $1 $base $(date -u +%Y-%m-%dT%H:%M:%SZ) $reviewer" >> "$verdicts"
  [ "$1" = BLOCK ] && cp "$report" "$out_dir/$key.md"
  return 0
}

echo "review-kit: running $cmd (Ctrl+C or SKIP_CLAUDE_REVIEW=1 to skip)…" >&2

gh_config=$(mktemp -d) || fail "could not create an empty gh config directory."
trap 'rm -rf "$gh_config"' EXIT
no_github=(env -u GH_TOKEN -u GITHUB_TOKEN -u GH_ENTERPRISE_TOKEN -u GITHUB_ENTERPRISE_TOKEN GH_CONFIG_DIR="$gh_config")

args=(--plugin-dir "$kit" -p "$cmd" --output-format text --allowedTools "$allowed" --disallowedTools "$denied")
[ -n "${REVIEW_KIT_MODEL:-}" ] && args+=(--model "$REVIEW_KIT_MODEL")

runner=()
for t in timeout gtimeout; do   # gtimeout: macOS with coreutils
  command -v "$t" >/dev/null 2>&1 && { runner=("$t" "${REVIEW_KIT_TIMEOUT:-900}"); break; }
done
# </dev/null: the hook's stdin holds the ref list; claude -p would read it as prompt input.
# ${runner[@]+...}: empty-array safe under `set -u` on macOS's bash 3.2.
if [ "$reviewer" = codex ]; then   # the review and the agents of the project, read-only (model, effort and personas from reviewer.py)
  args=(exec -s read-only "${copts[@]}" "Ejecuta la skill review-prepush ($kit/skills/review-prepush/SKILL.md) con los argumentos: $base, estando en la rama actual. Sus skills hermanas (review-context, review-report) están junto a ella en $kit/skills/; no uses las skills ni los subagentes del proyecto. No cambies ningún fichero.")
fi
${runner[@]+"${runner[@]}"} "${no_github[@]}" "$reviewer" "${args[@]}" </dev/null >"$report" 2>&1
status=$?

cat "$report"
echo
echo "review-kit: report saved to $report" >&2

[ $status -eq 124 ] && [ ${#runner[@]} -gt 0 ] && fail "$reviewer timed out after ${REVIEW_KIT_TIMEOUT:-900}s."
[ $status -ne 0 ] && fail "$reviewer exited with code $status."

result=$(grep -E '^REVIEW_RESULT:' "$report" | tail -n 1)
[ -z "$result" ] && fail "output has no REVIEW_RESULT line; cannot decide."

case "$result" in
  *"REVIEW_RESULT: BLOCK"*)
    remember BLOCK
    echo "review-kit: ✋ push blocked — confirmed Critical findings." >&2
    echo "review-kit: fix them, or force with 'git push --no-verify' if you know what you are doing." >&2
    exit 1 ;;
  *"REVIEW_RESULT: PASS"*)
    remember PASS
    echo "review-kit: ✅ no confirmed Critical findings ($result)." >&2
    exit 0 ;;
  *)
    fail "unrecognised REVIEW_RESULT line: $result" ;;
esac
