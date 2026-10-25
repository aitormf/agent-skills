#!/usr/bin/env bash
# scripts/check.sh: verificación del repositorio. Rápida y sin red.
# Van aparte, porque necesitan red: el smoke test de guardrails (scripts/test-guardrails-python.sh)
# y la suite de activación de skills (tests/evals/triggering/run.py).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "▶ agentes generados al día"
scripts/build-agents.py --check

echo "▶ frontmatter de skills y agentes"
python3 - <<'EOF'
import re, sys
from pathlib import Path
bad = []
for f in sorted(Path("skills").glob("*/SKILL.md")) + sorted(Path("agents").glob("*.md")):
    m = re.match(r"---\n(.*?)\n---\n", f.read_text(encoding="utf-8"), re.S)
    fm = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l and not l.startswith(" ")) if m else {}
    name = fm.get("name", "").strip()
    if not name or not fm.get("description", "").strip():
        bad.append(f"{f}: falta name o description")
    elif f.name == "SKILL.md" and name != f.parent.name:
        bad.append(f"{f}: name '{name}' no coincide con el directorio")
for b in bad:
    print(b, file=sys.stderr)
sys.exit(1 if bad else 0)
EOF

echo "▶ test criterion: same text in implement and review-report"
python3 - <<'EOF'
import sys
from pathlib import Path
key = "**When a change needs a test.**"
copies = {f: [l for l in Path(f).read_text(encoding="utf-8").splitlines() if l.startswith(key)]
          for f in ("agents/implement.md", "skills/review-report/SKILL.md")}
texts = {tuple(c) for c in copies.values()}
if any(len(c) != 1 for c in copies.values()) or len(texts) != 1:
    print(f"the paragraph '{key}' must appear once, identical, in {', '.join(copies)}", file=sys.stderr)
    sys.exit(1)
EOF

echo "▶ task-done"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
td=skills/task-done/scripts/task_done.py
printf -- '- [ ] T1. a — verification: `python3 --version`\n- [ ] T2. b — verification: false\n- [ ] T3. c — verification: `python3 --version`\n' > "$tmp/tasks.md"
python3 "$td" "$tmp/tasks.md" T1 -- python3 --version 2>"$tmp/err" >/dev/null
grep -q warning "$tmp/err" && { echo "task-done avisó con el comando declarado" >&2; exit 1; }
python3 "$td" "$tmp/tasks.md" T2 -- false >/dev/null && { echo "task-done marcó una tarea fallida" >&2; exit 1; }
python3 "$td" "$tmp/tasks.md" T3 -- true 2>"$tmp/err" >/dev/null
grep -q warning "$tmp/err" || { echo "task-done no avisó de un comando no declarado" >&2; exit 1; }
python3 "$td" "$tmp/tasks.md" T9 -- true >/dev/null 2>&1 && { echo "task-done aceptó una tarea inexistente" >&2; exit 1; }
grep -q -- '- \[x\] T1\.' "$tmp/tasks.md" && grep -q -- '- \[ \] T2\.' "$tmp/tasks.md" && grep -q -- '- \[x\] T3\.' "$tmp/tasks.md" \
  || { echo "task-done no dejó tasks.md como se esperaba" >&2; exit 1; }

echo "▶ task-done: red commit protection (commits of the branch since the base branch)"
r="$tmp/repo"; mkdir -p "$r/tests" "$r/src"; git -C "$r" init -q -b main
g() { git -C "$r" -c user.name=t -c user.email=t@t "$@"; }
done_() { rc=0; python3 "$td" "$r/tasks.md" "$1" -- true >"$tmp/out" 2>&1 || rc=$?; return $rc; }
marked() { grep -q -- "- \[x\] $1\." "$r/tasks.md"; }
fail() { echo "task-done: $1" >&2; cat "$tmp/out" >&2; exit 1; }
printf 'def test_E1_old(): assert f() == 0\n' > "$r/tests/test_old.py"; g add -A; g commit -qm "test(T1): E1 red, an older change"
g checkout -qb feat/1-a
printf -- '- [ ] T1. a — tests: E1, E2 — verification: true\n- [ ] T2. b — tests: E3 — verification: true\n- [ ] T3. c — tests: E4 — verification: true\n- [ ] T4. d — tests: E5 — verification: true\n- [ ] T5. e — tests: E6 — verification: true\n- [ ] T6. f — tests: E7 — verification: true\n- [x] T7. g — tests: E8 — verification: true\n' > "$r/tasks.md"
g add -A; g commit -qm "docs: tasks"
done_ T1 || true; [ $rc = 3 ] && ! marked T1 && grep -q "since main" "$tmp/out" || fail "counted a red commit from the base branch"
printf 'def test_E1_a(): assert f() == 1\ndef test_E2_b(): assert f() == 2\n' > "$r/tests/test_a.py"
g add -A; g commit -qm "test(T1): E1 E2 red"
echo 'def f(): return 1' > "$r/src/a.py"; g add -A; g commit -qm "feat(T1): a"
done_ T1 && marked T1 || fail "rejected a protected red commit"
printf 'def test_E3_c(): assert f() == 3\n' >> "$r/tests/test_a.py"; g add -A; g commit -qm "test(T2): E3 red"
done_ T1 || fail "a red commit of another task that only adds tests broke T1's protection"
sed -i 's/== 3/== 1/' "$r/tests/test_a.py"
done_ T2 || true; [ $rc = 3 ] && ! marked T2 || fail "accepted an uncommitted change to a red test"
g commit -qam "feat(T2): c"
done_ T2 || true; [ $rc = 3 ] || fail "accepted a commit that changes a red test"
printf 'def test_E9_d(): pass\n' > "$r/tests/test_d.py"; g add -A; g commit -qm "test(T3): E9 red"
done_ T3 || true; [ $rc = 3 ] && grep -q "E4 has no test" "$tmp/out" || fail "accepted a red commit without the task's example"
printf 'def test_E5_e(): pass\n' > "$r/tests/test_e.py"; g add -A; g commit -qm "test(T4): E5 red"
printf 'def test_E5_e(): pass\ndef test_e_edge(): pass\n' > "$r/tests/test_e.py"; g commit -qam "feat(T4): e"
done_ T4 && marked T4 || fail "rejected new tests added after the red commit"
printf 'def test_E6_f(): assert f() == 6\n' > "$r/tests/test_f.py"; g add -A; g commit -qm "test(T5): E6 red"
printf 'def test_E6_f(): assert True\ndef test_E7_g(): assert f() == 7\n' > "$r/tests/test_f.py"; g commit -qam "test(T6): E7 red"
done_ T5 || true; [ $rc = 3 ] && ! marked T5 && grep -q "test(T6)" "$tmp/out" || fail "accepted a red test changed by the red commit of another task"
printf -- '- [ ] T8. h — tests: E1 — verification: true\n- [ ] T9. i — tests: E11 — verification: true\n- [ ] T10. j — tests: E12 — verification: true\n' >> "$r/tasks.md"
printf 'def test_E10_h(): pass\n' > "$r/tests/test_h.py"; g add tests; g commit -qm "test(T8): E10 red"
done_ T8 || true; [ $rc = 3 ] && grep -q "E1 has no test" "$tmp/out" || fail "took a test of E10 for a test of E1"
printf 'def test_E11_i(): assert f() == 11\n' > "$r/tests/test_i.py"; g add tests; g commit -qm "test(T9): E11 red"
printf 'def test_E11_i(): assert True\n' > "$r/tests/test_i.py"; g commit -qm "test(T9): E11 again" -- tests
done_ T9 || true; [ $rc = 3 ] && grep -q "removes or changes" "$tmp/out" || fail "accepted a second red commit of the task that changes the first one's test"
printf 'def test_E12_j(): pass\n' >> "$r/tests/test_old.py"; g add tests; g commit -qm "test(T10): E12 red"
sed -i 's/== 0/== 10/' "$r/tests/test_old.py"; g commit -qm "feat(T10): j" -- tests
done_ T10 && marked T10 || fail "rejected a change to a line the red commit did not add, in a file it touched"
printf -- '- [ ] T11. k — tests: E13 — verification: true\n- [ ] T12. l — tests: E14 — verification: true\n- [ ] T13. m — tests: E15 — verification: true\n- [ ] T14. n — tests: E16 — verification: true\n- [ ] T15. o — tests: E17 — verification: true\n- [ ] T16. p — tests: E18 — verification: true\n' >> "$r/tasks.md"
printf "it('old', () => {\n  expect(g()).toBe(0);\n});\n" > "$r/tests/k.test.js"; g add tests; g commit -qm "test: an older test"
printf "it('E13 k', () => {\n  expect(k()).toBe(13);\n});\n" >> "$r/tests/k.test.js"; g add tests; g commit -qm "test(T11): E13 red"
printf "it('E13 k', () => {\n  expect(k()).toBe(13);\n});\n" > "$r/tests/k.test.js"; g commit -qm "feat(T11): drop the old test" -- tests
done_ T11 && marked T11 || fail "took a removed line with the same text as a red one for the red one"
printf 'def test_E14_l(): assert f() == 14\n' > "$r/tests/test_canción.py"; g add tests; g commit -qm "test(T12): E14 red"
printf 'def test_E14_l(): assert True\n' > "$r/tests/test_canción.py"; g commit -qm "feat(T12): l" -- tests
done_ T12 || true; [ $rc = 3 ] && grep -q "test_canción.py" "$tmp/out" || fail "accepted a changed red test whose path is not ASCII"
g rev-parse HEAD > "$tmp/ignore-revs"; g config blame.ignoreRevsFile "$tmp/ignore-revs"  # the change hidden from git blame
done_ T12 || true; g config --unset blame.ignoreRevsFile; [ $rc = 3 ] || fail "a blame.ignoreRevsFile hid a change to a red test"
printf 'X = 0\n' > "$r/tests/test_m.py"; g add tests; g commit -qm "test: m fixture"
printf 'def test_E15_m(): assert f() == 15\n' >> "$r/tests/test_m.py"; g add tests; g commit -qm "test(T13): E15 red"
g checkout -qb side; sed -i 's/X = 0/X = 1/' "$r/tests/test_m.py"; g commit -qm "feat(T13): m on a side branch" -- tests
g checkout -q feat/1-a; sed -i 's/X = 0/X = 2/' "$r/tests/test_m.py"; g commit -qm "feat(T13): m" -- tests
g merge -q side >/dev/null 2>&1 || true  # conflict on X; the resolution also weakens the red test (an evil merge)
printf 'X = 3\ndef test_E15_m(): assert f() == 99\n' > "$r/tests/test_m.py"; g add tests; g commit -qm "merge side into feat/1-a"
done_ T13 || true; [ $rc = 3 ] && grep -q "'merge side into feat/1-a' removes or changes" "$tmp/out" || fail "accepted a merge commit that changes a red test"
printf 'def test_E16_n(): assert f() == 16\n' > "$r/tests/test_n.py"; g add tests; g commit -qm "test(T14): E16 red"
g mv tests/test_n.py tests/test_n2.py; g commit -qm "refactor(T14): rename the test file"
done_ T14 && marked T14 || fail "a rename of the whole red test file broke its protection"
sed -i 's/== 16/== 0/' "$r/tests/test_n2.py"; g commit -qm "feat(T14): n" -- tests
done_ T14 || true; [ $rc = 3 ] && grep -q "test_n2.py" "$tmp/out" || fail "lost the protection of a red test after its file was renamed"
printf 'def test_XE17_o(): pass\n' > "$r/tests/test_o.py"; g add tests; g commit -qm "test(T15): E17 red"
done_ T15 || true; [ $rc = 3 ] && grep -q "E17 has no test" "$tmp/out" || fail "took a test of XE17 for a test of E17"
printf 'def test_E18_p(): pass\n\ndef test_E18_q(): pass\n' > "$r/tests/test_p.py"; g add tests; g commit -qm "test(T16): E18 red"
printf 'def test_E18_p(): pass\ndef test_E18_q(): pass\n' > "$r/tests/test_p.py"; g commit -qm "style(T16): drop a blank line" -- tests
done_ T16 && marked T16 || fail "a blank line the red commit added was protected"
printf -- '- [ ] T17. q — tests: E19 — verification: true\n' >> "$r/tasks.md"
printf 'def test_E19_q(): assert f() == 19\n' > "$r/tests/test_q.py"; g add tasks.md tests; g commit -qm "test(T17): E19 red"
printf 'def test_E19_q(): pass\n' > "$r/tests/test_q.py"; sed -i 's/T17\. q — tests: E19 — /T17. q — /' "$r/tasks.md"
g add tasks.md tests; g commit -qm "feat(T17): q, and E19 dropped from tasks.md"
done_ T17 || true; [ $rc = 3 ] && ! marked T17 && grep -q "no longer declares E19" "$tmp/out" || fail "dropping the examples from tasks.md turned off the protection of the red commit"
python3 "$td" --audit "$r/tasks.md" >"$tmp/out" 2>&1 || true
grep -q "^T17 \[ \]: PROBLEM: tasks.md no longer declares E19" "$tmp/out" || fail "--audit missed a task whose examples were dropped after its red commit"
if command -v ssh-keygen >/dev/null; then  # signed commits with log.showSignature=true
  ssh-keygen -q -t ed25519 -N '' -f "$tmp/sign" >/dev/null
  printf -- '- [ ] T18. r — tests: E20 — verification: true\n' >> "$r/tasks.md"
  printf 'def test_E20_r(): assert f() == 20\n' > "$r/tests/test_r.py"; g add tasks.md tests
  g -c gpg.format=ssh -c user.signingkey="$tmp/sign" commit -S -qm "test(T18): E20 red"
  g config log.showSignature true
  done_ T18 || true; g config --unset log.showSignature; [ $rc = 0 ] && marked T18 || fail "log.showSignature=true with signed commits broke the history parsing"
fi

echo "▶ task-done --audit (read-only, for the review)"
audit() { rc=0; python3 "$td" --audit "$@" >"$tmp/out" 2>&1 || rc=$?; return $rc; }
cp "$r/tasks.md" "$tmp/before.md"
audit "$r/tasks.md" || true; [ $rc = 3 ] || fail "--audit did not fail on broken red tests"
grep -q "^T4 \[x\]: ok" "$tmp/out" || fail "--audit did not accept a protected task"
grep -q "^T2 \[ \]: PROBLEM: commit .* removes or changes" "$tmp/out" || fail "--audit missed a red test changed later"
grep -q "^T5 \[ \]: PROBLEM: commit .* 'test(T6)" "$tmp/out" || fail "--audit missed a red test changed by another task's red commit"
grep -q "^T3 \[ \]: PROBLEM: E4 has no test" "$tmp/out" || fail "--audit missed an example without a test"
grep -q "^T7 \[x\]: PROBLEM: no red commit" "$tmp/out" || fail "--audit missed a ticked task without a red commit"
cmp -s "$r/tasks.md" "$tmp/before.md" || fail "--audit edited tasks.md"
printf 'def test_E5_e(): assert False\n' > "$r/tests/test_e.py"
audit "$r/tasks.md" || true; grep -q "^T4 \[x\]: ok" "$tmp/out" || fail "--audit counted uncommitted changes"
git -C "$r" checkout -q -- tests/test_e.py
printf '  E9: an example of the map in no task\n' >> "$r/tasks.md"
audit "$r/tasks.md" || true; grep -q "^E9: PROBLEM" "$tmp/out" || fail "--audit missed a map example in no task"

echo "▶ task-done: the change of the branch, docs/changes/<branch>/tasks.md"
tda="$PWD/$td"; c="$tmp/change"; mkdir -p "$c/tests" "$c/src"; git -C "$c" init -q -b main
gc() { git -C "$c" -c user.name=t -c user.email=t@t "$@"; }
tdc() { rc=0; (cd "$c/src" && python3 "$tda" "$@") >"$tmp/out" 2>&1 || rc=$?; return $rc; }
printf 'def test_E1_old(): pass\n' > "$c/tests/test_old.py"; gc add -A; gc commit -qm "test(T1): E1 red, an older change"
gc checkout -qb feat/7-cancel; mkdir -p "$c/docs/changes/7-cancel"; ct="$c/docs/changes/7-cancel/tasks.md"
printf -- '---\nstatus: open\nissue: 7\n---\n\n## Tasks\n\n- [ ] T1. a — tests: E1 — verification: true\n- [ ] W1. Full verification — verification: true\n' > "$ct"
tdc T1 -- true || true; [ $rc = 3 ] || fail "with tasks.md not committed, counted a red commit from the base branch"
printf 'def test_E1_a(): pass\n' > "$c/tests/test_a.py"; gc add tests; gc commit -qm "test(T1): E1 red"
echo 'x = 1' > "$c/src/a.py"; gc add src; gc commit -qm "feat(T1): a"
tdc T1 -- true && grep -q -- '- \[x\] T1\.' "$ct" || fail "did not tick T1 in the change of the branch, with tasks.md not committed"
grep -q '^status: open$' "$ct" || fail "set status: done with tasks left"
cp "$ct" "$tmp/ct"; printf -- '- [ ] T2. b — tests: E2 — verification: true\n' >> "$ct"
tdc --audit && grep -q "^T2 \[ \]: pending" "$tmp/out" || fail "--audit did not report an unticked task without a red commit as pending"
cp "$tmp/ct" "$ct"
tdc W1 -- true && grep -q '^status: done$' "$ct" && grep -q '^issue: 7$' "$ct" || fail "did not set status: done when the last task was ticked"
tdc --audit && grep -q "^T1 \[x\]: ok" "$tmp/out" || fail "--audit did not check the change of the branch"
gc checkout -qb feat/8-other
tdc W1 -- true || true; [ $rc = 2 ] && grep -q "docs/changes/8-other/tasks.md" "$tmp/out" || fail "did not exit 2 naming the path searched for a branch without a change folder"
tdc --audit || true; [ $rc = 2 ] || fail "--audit did not exit 2 for a branch without a change folder"
gc checkout -q feat/7-cancel; gc add docs; gc commit -qm "docs: 7-cancel done"; gc checkout -q main; gc merge -q --ff-only feat/7-cancel
gc checkout -qb fix/7-cancel  # same last segment as a change already finished in main
tdc W1 -- true || true; [ $rc = 2 ] && grep -q "finished change" "$tmp/out" || fail "reused the folder of a finished change"
tdc --audit || true; [ $rc = 2 ] && grep -q "finished change" "$tmp/out" || fail "--audit reused the folder of a finished change"
gc checkout -q main; mkdir -p "$c/docs/changes/11-z"; zt="$c/docs/changes/11-z/tasks.md"
printf -- '---\nstatus: open\n---\n\n- [ ] T1. a — verification: true\n\nstatus: done (only the frontmatter counts)\n' > "$zt"
gc add docs; gc commit -qm "docs: 11-z, open"; gc checkout -qb feat/11-z
tdc T1 -- true && grep -q -- '- \[x\] T1\.' "$zt" || fail "took 'status: done' outside the frontmatter for a finished change"
n="$tmp/nobase"; mkdir -p "$n"; git -C "$n" init -q -b trunk
git -C "$n" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "chore: start"
printf -- '- [ ] T1. a — tests: E1 — verification: true\n' > "$n/tasks.md"
rc=0; python3 "$td" "$n/tasks.md" T1 -- true >"$tmp/out" 2>&1 || rc=$?
[ $rc = 3 ] && grep -q "PROBLEM: .*no base branch" "$tmp/out" || fail "did not exit 3 with a PROBLEM line without a base branch"
audit "$n/tasks.md" || true; [ $rc = 3 ] && grep -q "^PROBLEM: .*no base branch" "$tmp/out" || fail "--audit did not exit 3 with a PROBLEM line without a base branch"
w="$tmp/work"; mkdir -p "$w/tests"; git init -q --bare -b main "$tmp/origin.git"; git -C "$w" init -q -b main
gw() { git -C "$w" -c user.name=t -c user.email=t@t "$@"; }
gw commit -q --allow-empty -m "chore: start"; gw remote add origin "$tmp/origin.git"; gw push -q origin main main:develop
gw checkout -qb feat/9-x origin/develop; printf -- '- [ ] T1. a — tests: E1 — verification: true\n' > "$w/tasks.md"; gw add -A; gw commit -qm "docs: tasks"
gw remote set-head origin develop
audit "$w/tasks.md" || true; grep -q "since origin/develop" "$tmp/out" || fail "--audit did not take origin/HEAD as the base branch"
gw checkout -qb old main; printf 'def test_E1_old(): pass\n' > "$w/tests/test_old.py"; gw add tests; gw commit -qm "test(T1): E1 red, merged earlier"
gw push -q origin old:main; gw checkout -qb feat/10-y origin/main  # the local main is stale: it lacks that commit
printf -- '- [x] T1. a — tests: E1 — verification: true\n' > "$w/tasks.md"; gw add -A; gw commit -qm "docs: tasks"
gw remote set-head origin -d
audit "$w/tasks.md" || true; grep -q "since origin/main" "$tmp/out" && grep -q "^T1 \[x\]: PROBLEM: no red commit" "$tmp/out" || fail "--audit took a stale local main over origin/main"

echo "▶ review: no GitHub credentials in the pre-push hook nor in the review job; gh denied as defence in depth (D-0021, D-0027)"
mkdir -p "$tmp/bin"
cat > "$tmp/bin/claude" <<'FAKE'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$CLAUDE_ARGS"
{ echo "tokens=${GH_TOKEN-}${GITHUB_TOKEN-}${GH_ENTERPRISE_TOKEN-}${GITHUB_ENTERPRISE_TOKEN-}"; echo "$GH_CONFIG_DIR"; ls -A "$GH_CONFIG_DIR"; } > "$CLAUDE_ENV"
echo "REVIEW_RESULT: PASS critical=0 required=0 uncertain=0"
FAKE
chmod +x "$tmp/bin/claude"
hook="$PWD/skills/review-prepush/assets/pre-push"
(cd "$r" && echo "refs/heads/x $(git rev-parse HEAD) refs/heads/x 0000000000000000000000000000000000000000" \
  | GH_TOKEN=t GITHUB_TOKEN=t GH_ENTERPRISE_TOKEN=t GITHUB_ENTERPRISE_TOKEN=t REVIEW_KIT_FAIL_CLOSED=1 CLAUDE_ARGS="$tmp/args" CLAUDE_ENV="$tmp/env" PATH="$tmp/bin:$PATH" bash "$hook") >/dev/null 2>&1 || { echo "the pre-push hook failed with a passing review" >&2; exit 1; }
grep -A1 -x -- --disallowedTools "$tmp/args" | grep -q 'Bash(gh:\*)' || { echo "the pre-push hook does not deny Bash(gh:*)" >&2; exit 1; }
# The real control: claude runs with no token variables and an empty gh config directory, removed afterwards.
gh_dir=$(sed -n 2p "$tmp/env")
[ "$(sed -n 1p "$tmp/env")" = "tokens=" ] && [ -n "$gh_dir" ] && [ "$(wc -l < "$tmp/env")" -eq 2 ] && [ ! -e "$gh_dir" ] \
  || { echo "the pre-push hook gives claude GitHub credentials (a token, or a gh config directory that is not empty and temporary)" >&2; cat "$tmp/env" >&2; exit 1; }
wf=skills/review-pr/assets/claude-review.yml
grep -q -- '--disallowedTools ".*Bash(gh:\*)' "$wf" || { echo "claude-review.yml does not deny Bash(gh:*) in the review job" >&2; exit 1; }
! grep -Eq '^ +(issues|pull-requests): read' "$wf" || { echo "the review job of claude-review.yml can read issues or PRs" >&2; exit 1; }
# The real control: the review job has no token at all (the gh deny is defence in depth).
job=$(awk '/^  review:$/ { on=1; next } on && /^  [a-z]/ { exit } on' "$wf")
[ "$(printf '%s\n' "$job" | awk '/^    permissions:$/ { on=1; next } on && /^    [a-z]/ { exit } on')" = "      contents: read" ] \
  || { echo "the review job of claude-review.yml must have only 'contents: read'" >&2; exit 1; }
printf '%s\n' "$job" | grep -q 'persist-credentials: false' || { echo "the review job of claude-review.yml leaves the checkout token in .git/config" >&2; exit 1; }
! printf '%s\n' "$job" | grep -Eq 'GH_TOKEN|GITHUB_TOKEN|github\.token|secrets\.GITHUB' || { echo "the review job of claude-review.yml gets a GitHub token" >&2; exit 1; }

echo "▶ record-decision"
cd_=skills/record-decision/scripts/check_decisions.py
dd="$tmp/decisions"; mkdir -p "$dd"; cp skills/record-decision/assets/en/README.md "$dd/"
for lang in en es; do  # the templates, without their opening comment, must pass the check
  sed '1,/^-->$/d' "skills/record-decision/assets/$lang/decision.md" | sed 's/D-NNNN/D-0001/; s/YYYY-MM-DD/2026-01-01/' > "$dd/0001-a.md"
  grep -q '^| \[D-0001\]' "$dd/README.md" || echo '| [D-0001](0001-a.md) | a | architecture | proposed | src/ |' >> "$dd/README.md"
  python3 "$cd_" "$dd" || { echo "the $lang decision template does not pass check_decisions" >&2; exit 1; }
done
[ "$(python3 "$cd_" "$dd" --next)" = D-0002 ] || { echo "check_decisions --next is wrong" >&2; exit 1; }
sed 's/D-0001/D-0002/; s/^supersedes: null/supersedes: D-0001/' "$dd/0001-a.md" > "$dd/0002-b.md"
echo '| [D-0002](0002-b.md) | b | architecture | proposed | src/ |' >> "$dd/README.md"
python3 "$cd_" "$dd" 2>/dev/null && { echo "check_decisions accepted a one-sided supersedes" >&2; exit 1; }
sed -i 's/^status: proposed/status: superseded/; s/^superseded_by: null/superseded_by: D-0002/' "$dd/0001-a.md"
sed -i 's/| a | architecture | proposed/| a | architecture | superseded/' "$dd/README.md"
python3 "$cd_" "$dd" || { echo "check_decisions rejected a valid supersession" >&2; exit 1; }

ok_dir() {  # a fresh decisions dir with one valid decision, D-0001
  rm -rf "$tmp/proj"; mkdir -p "$tmp/proj/docs/decisions" "$tmp/proj/docs/adr"; pd="$tmp/proj/docs/decisions"
  cp skills/record-decision/assets/en/README.md "$pd/"
  sed '1,/^-->$/d' skills/record-decision/assets/en/decision.md | sed 's/D-NNNN/D-0001/; s/YYYY-MM-DD/2026-01-01/' > "$pd/0001-a.md"
  echo '| [D-0001](0001-a.md) | a | architecture | proposed | src/ |' >> "$pd/README.md"
}
rejects() { python3 "$cd_" "$pd" 2>"$tmp/out" && { echo "check_decisions accepted $1" >&2; exit 1; }; grep -q "$2" "$tmp/out" || { echo "check_decisions did not say why it rejected $1" >&2; cat "$tmp/out" >&2; exit 1; }; }
ok_dir; cp "$pd/0001-a.md" "$pd/0003-c.md"; echo '| [D-0003](0003-c.md) | c | architecture | proposed | src/ |' >> "$pd/README.md"
rejects "an id that does not match the file name" "id is D-0001, the file name says D-0003"
ok_dir; cp "$pd/0001-a.md" "$pd/0001-b.md"
rejects "a duplicated number" "number 0001 is already used"
ok_dir; sed -i 's/^status: proposed/status: accepted/' "$pd/0001-a.md"
rejects "an index row whose status differs from the file" "D-0001 says architecture/proposed"
ok_dir; printf '# 5. Use uv\n' > "$tmp/proj/docs/adr/0005-use-uv.md"  # D-0010: ADRs kept in docs/adr/, linked from the index
echo '| [D-0005](../adr/0005-use-uv.md) | Use uv | architecture | accepted | . |' >> "$pd/README.md"
python3 "$cd_" "$pd" || { echo "check_decisions rejected an index row linking an ADR in docs/adr/" >&2; exit 1; }
[ "$(python3 "$cd_" "$pd" --next)" = D-0006 ] || { echo "check_decisions --next reused the number of an ADR" >&2; exit 1; }
echo '| [D-0007](../adr/0007-gone.md) | Gone | architecture | accepted | . |' >> "$pd/README.md"
rejects "an index row linking an ADR that does not exist" "0007-gone.md, which does not exist"
ok_dir; printf '# 5. Use uv\n' > "$tmp/proj/docs/adr/0005-use-uv.md"
echo '| [D-0006](../adr/0005-use-uv.md) | Use uv | architecture | accepted | . |' >> "$pd/README.md"
rejects "an index row linking an ADR with another number" "D-0006 links to ../adr/0005-use-uv.md, an ADR with another number"
ok_dir; sed -i '/^| \[D-0001\]/d' "$pd/README.md"
rejects "a decision without an index row" "no row for D-0001"
ok_dir; echo '| [D-0001](0001-a.md) | a | architecture | proposed | src/ |' >> "$pd/README.md"
rejects "a duplicated index row" "D-0001 appears twice"
ok_dir; sed -i 's/(0001-a.md)/(0001-b.md)/' "$pd/README.md"
rejects "an index row linking another file" "D-0001 links to 0001-b.md, the file is 0001-a.md"
ok_dir; sed -i 's/^status: proposed/status: superseded/' "$pd/0001-a.md"
rejects "superseded without superseded_by" "status superseded but superseded_by is empty"
ok_dir; sed -i 's/^superseded_by: null/superseded_by: D-0009/' "$pd/0001-a.md"
rejects "a superseded_by that does not exist" "superseded_by D-0009 does not exist"
ok_dir; sed -i 's/^supersedes: null/supersedes: D-0009/' "$pd/0001-a.md"
rejects "a supersedes that does not exist" "supersedes D-0009, which does not exist"
ok_dir; sed 's/D-0001/D-0002/; s/^supersedes: null/supersedes: D-0001/' "$pd/0001-a.md" > "$pd/0002-b.md"
echo '| [D-0002](0002-b.md) | b | architecture | proposed | src/ |' >> "$pd/README.md"
sed -i 's/^superseded_by: null/superseded_by: D-0002/' "$pd/0001-a.md"
rejects "a superseded_by with a live status" "superseded_by D-0002 but status is proposed"
ok_dir; echo '| [D-0002](0002-b.md) | b | architecture | proposed | src/ |' >> "$pd/README.md"
rejects "an index row without a file" "row D-0002 has no decision file"
ok_dir; sed 's/D-0001/D-0002/' "$pd/0001-a.md" > "$pd/0002-b.md"
echo '| [D-0002](0002-b.md) | b | architecture | proposed | src/ |' >> "$pd/README.md"
sed -i 's/^status: proposed/status: superseded/; s/^superseded_by: null/superseded_by: D-0002/' "$pd/0001-a.md"
sed -i 's/| a | architecture | proposed/| a | architecture | superseded/' "$pd/README.md"
rejects "a one-sided superseded_by" "superseded_by D-0002, but D-0002 does not say supersedes: D-0001"
ok_dir; mv "$pd/0001-a.md" "$pd/0001_A.md"
rejects "a file name that is not NNNN-kebab-case" "0001_A.md: name must be NNNN-title-in-kebab-case.md"
ok_dir; sed -i '1,/^---$/d' "$pd/0001-a.md"
rejects "a decision without frontmatter" "0001-a.md: no frontmatter"
ok_dir; sed -i '/^affects:/d' "$pd/0001-a.md"
rejects "a decision without affects" "0001-a.md: missing affects"
ok_dir; sed -i 's/^type: architecture/type: architectural/' "$pd/0001-a.md"
rejects "a type outside the list" "type 'architectural' is not one of"
ok_dir; sed -i 's/^status: proposed/status: acepted/' "$pd/0001-a.md"
rejects "a status outside the list" "status 'acepted' is not one of"
ok_dir; sed -i 's/^date: .*/date: 26-1-1/' "$pd/0001-a.md"
rejects "a date that is not YYYY-MM-DD" "date '26-1-1' is not YYYY-MM-DD"
ok_dir; sed -i 's/^| \[D-0001\].*/| [D-0001](0001-a.md) | a | architecture |/' "$pd/README.md"
rejects "an index row with too few cells" "the row of D-0001 needs title, type, status and affects"
ok_dir; sed -i 's/^status: proposed/status: superseded/; s/^supersedes: null/supersedes: D-0001/; s/^superseded_by: null/superseded_by: D-0001/' "$pd/0001-a.md"
sed -i 's/| a | architecture | proposed/| a | architecture | superseded/' "$pd/README.md"
rejects "a decision that supersedes itself" "D-0001 supersedes itself"
ok_dir; sed -i 's/^status: proposed/status: superseded/; s/^supersedes: null/supersedes: D-0002/; s/^superseded_by: null/superseded_by: D-0002/' "$pd/0001-a.md"
sed 's/D-0001/D-0002/; s/^supersedes: D-0002/supersedes: D-0001/; s/^superseded_by: D-0002/superseded_by: D-0001/' "$pd/0001-a.md" > "$pd/0002-b.md"
sed -i 's/| a | architecture | proposed/| a | architecture | superseded/' "$pd/README.md"
echo '| [D-0002](0002-b.md) | b | architecture | superseded | src/ |' >> "$pd/README.md"
rejects "a supersession cycle" "supersession cycle D-0001 -> D-0002"

echo "▶ docs/decisions of this repo"
python3 "$cd_" docs/decisions

echo "▶ parser de la suite de activación"
python3 tests/evals/triggering/run.py --self-test

echo "▶ manifiestos"
python3 - <<'EOF'
import json, sys
claude = json.load(open(".claude-plugin/plugin.json"))
codex = json.load(open(".codex-plugin/plugin.json"))
markets = [json.load(open(p)) for p in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json")]
errors = []
if claude["name"] != codex["name"]:
    errors.append("el nombre del plugin no coincide entre Claude y Codex")
if claude["version"] != codex["version"]:
    errors.append(f"versión distinta: Claude {claude['version']}, Codex {codex['version']}")
for m in markets:
    if claude["name"] not in {p["name"] for p in m["plugins"]}:
        errors.append(f"el catálogo '{m['name']}' no incluye el plugin '{claude['name']}'")
for e in errors:
    print(e, file=sys.stderr)
sys.exit(1 if errors else 0)
EOF
if command -v claude >/dev/null; then
  claude plugin validate --strict .claude-plugin/plugin.json >/dev/null
  claude plugin validate --strict .claude-plugin/marketplace.json >/dev/null
else
  echo "  (claude no está instalado: se omite claude plugin validate)"
fi

echo "✔ todo en verde"
