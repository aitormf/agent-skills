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
tdc W1 -- true && grep -q '^status: done$' "$ct" && grep -q '^issue: 7$' "$ct" || fail "did not set status: done when the last task was ticked"
tdc --audit && grep -q "^T1 \[x\]: ok" "$tmp/out" || fail "--audit did not check the change of the branch"
gc checkout -qb feat/8-other
tdc W1 -- true || true; [ $rc = 2 ] && grep -q "docs/changes/8-other/tasks.md" "$tmp/out" || fail "did not exit 2 naming the path searched for a branch without a change folder"
tdc --audit || true; [ $rc = 2 ] || fail "--audit did not exit 2 for a branch without a change folder"
n="$tmp/nobase"; mkdir -p "$n"; git -C "$n" init -q -b trunk
git -C "$n" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "chore: start"
printf -- '- [ ] T1. a — tests: E1 — verification: true\n' > "$n/tasks.md"
rc=0; python3 "$td" "$n/tasks.md" T1 -- true >"$tmp/out" 2>&1 || rc=$?
[ $rc = 3 ] && grep -q "PROBLEM: .*no base branch" "$tmp/out" || fail "did not exit 3 with a PROBLEM line without a base branch"
audit "$n/tasks.md" || true; [ $rc = 3 ] && grep -q "^PROBLEM: .*no base branch" "$tmp/out" || fail "--audit did not exit 3 with a PROBLEM line without a base branch"

echo "▶ review: gh fully denied in the pre-push hook and in the review job (D-0021)"
mkdir -p "$tmp/bin"
printf '#!/usr/bin/env bash\nprintf "%%s\\n" "$@" > "$CLAUDE_ARGS"\necho "REVIEW_RESULT: PASS critical=0 required=0 uncertain=0"\n' > "$tmp/bin/claude"; chmod +x "$tmp/bin/claude"
hook="$PWD/skills/review-prepush/assets/pre-push"
(cd "$r" && echo "refs/heads/x $(git rev-parse HEAD) refs/heads/x 0000000000000000000000000000000000000000" \
  | CLAUDE_ARGS="$tmp/args" PATH="$tmp/bin:$PATH" bash "$hook") >/dev/null 2>&1 || { echo "the pre-push hook failed with a passing review" >&2; exit 1; }
grep -A1 -x -- --disallowedTools "$tmp/args" | grep -q 'Bash(gh:\*)' || { echo "the pre-push hook does not deny Bash(gh:*)" >&2; exit 1; }
wf=skills/review-pr/assets/claude-review.yml
grep -q -- '--disallowedTools ".*Bash(gh:\*)' "$wf" || { echo "claude-review.yml does not deny Bash(gh:*) in the review job" >&2; exit 1; }
! grep -Eq '^ +(issues|pull-requests): read' "$wf" || { echo "the review job of claude-review.yml can read issues or PRs" >&2; exit 1; }

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
rm "$dd/0002-b.md"
python3 "$cd_" "$dd" 2>/dev/null && { echo "check_decisions accepted an index row without a file" >&2; exit 1; }

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
