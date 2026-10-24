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

echo "▶ task-done: red commit protection"
r="$tmp/repo"; mkdir -p "$r/tests" "$r/src"; git -C "$r" init -q
g() { git -C "$r" -c user.name=t -c user.email=t@t "$@"; }
done_() { rc=0; python3 "$td" "$r/tasks.md" "$1" -- true >"$tmp/out" 2>&1 || rc=$?; return $rc; }
marked() { grep -q -- "- \[x\] $1\." "$r/tasks.md"; }
fail() { echo "task-done: $1" >&2; cat "$tmp/out" >&2; exit 1; }
printf -- '- [ ] T1. a — tests: E1, E2 — verification: true\n- [ ] T2. b — tests: E3 — verification: true\n- [ ] T3. c — tests: E4 — verification: true\n- [ ] T4. d — tests: E5 — verification: true\n' > "$r/tasks.md"
g add -A; g commit -qm "docs: tasks"
done_ T1 || true; [ $rc = 3 ] && ! marked T1 || fail "marked a task with examples and no red commit"
printf 'def test_E1_a(): assert f() == 1\ndef test_E2_b(): assert f() == 2\n' > "$r/tests/test_a.py"
g add -A; g commit -qm "test(T1): E1 E2 red"
echo 'def f(): return 1' > "$r/src/a.py"; g add -A; g commit -qm "feat(T1): a"
done_ T1 && marked T1 || fail "rejected a protected red commit"
printf 'def test_E3_c(): assert f() == 3\n' >> "$r/tests/test_a.py"; g add -A; g commit -qm "test(T2): E3 red"
done_ T1 || fail "a red commit of another task broke T1's protection"
sed -i 's/== 3/== 1/' "$r/tests/test_a.py"
done_ T2 || true; [ $rc = 3 ] && ! marked T2 || fail "accepted an uncommitted change to a red test"
g commit -qam "feat(T2): c"
done_ T2 || true; [ $rc = 3 ] || fail "accepted a commit that changes a red test"
printf 'def test_E9_d(): pass\n' > "$r/tests/test_d.py"; g add -A; g commit -qm "test(T3): E9 red"
done_ T3 || true; [ $rc = 3 ] && grep -q "E4 has no test" "$tmp/out" || fail "accepted a red commit without the task's example"
printf 'def test_E5_e(): pass\n' > "$r/tests/test_e.py"; g add -A; g commit -qm "test(T4): E5 red"
printf 'def test_E5_e(): pass\ndef test_e_edge(): pass\n' > "$r/tests/test_e.py"; g commit -qam "feat(T4): e"
done_ T4 && marked T4 || fail "rejected new tests added after the red commit"

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
