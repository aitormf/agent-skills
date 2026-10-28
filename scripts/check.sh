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
fail() { echo "task-done: $1" >&2; cat "$tmp/out" >&2; exit 1; }
task() {  # task <change folder> <id> <examples> [status] [depends_on] [verification]: writes <folder>/tasks/<id>-t.md
  mkdir -p "$1/tasks"
  printf -- '---\nid: %s\ntitle: task %s\nstatus: %s   # todo | doing | done\ndepends_on: [%s]\nexamples: [%s]\nverification: %s\n---\nPurpose.\n' \
    "$2" "$2" "${4:-todo}" "${5:-}" "$3" "${6:-true}" > "$1/tasks/$2-t.md"
}
status_is() { grep -q "^status: $2 " "$1"; }  # status_is <task file> <status>
: > "$tmp/out"
f="$tmp/plain"; task "$f" T1 "" todo "" 'python3 --version'; task "$f" T2 "" todo "" false; task "$f" T3 "" todo "" 'python3 --version'
printf -- '---\nstatus: open\n---\n' > "$f/README.md"
python3 "$td" "$f" T1 -- python3 --version 2>"$tmp/err" >/dev/null
grep -q warning "$tmp/err" && fail "warned with the declared command"
python3 "$td" "$f" T2 -- false >/dev/null && fail "marked a failing task"
python3 "$td" "$f/tasks/T3-t.md" -- true 2>"$tmp/err" >/dev/null || fail "did not take the task from its file"
grep -q warning "$tmp/err" || fail "did not warn about a command that is not the declared one"
python3 "$td" "$f" T9 -- true >"$tmp/out" 2>&1 && fail "accepted a task that does not exist"
grep -q "T9-\*\.md" "$tmp/out" || fail "did not name the task file searched"
status_is "$f/tasks/T1-t.md" done && status_is "$f/tasks/T2-t.md" todo && status_is "$f/tasks/T3-t.md" done \
  && grep -q '^status: open$' "$f/README.md" || fail "did not leave the task files and the README as expected"
grep -q '^status: done   # todo | doing | done$' "$f/tasks/T1-t.md" || fail "dropped the comment of the status line"
sed -i 's/^status: todo /status: wip /' "$f/tasks/T2-t.md"
python3 "$td" "$f" T2 -- true >"$tmp/out" 2>&1 && fail "accepted a task file with a malformed frontmatter"
grep -q "status 'wip'" "$tmp/out" || fail "did not say what is malformed in the task file"

echo "▶ task-done: red commit protection (commits of the branch since the base branch)"
r="$tmp/repo"; mkdir -p "$r/tests" "$r/src"; git -C "$r" init -q -b main
ch="$r/docs/changes/a"
g() { git -C "$r" -c user.name=t -c user.email=t@t "$@"; }
done_() { rc=0; python3 "$td" "$ch" "$1" -- true >"$tmp/out" 2>&1 || rc=$?; return $rc; }
marked() { status_is "$ch/tasks/$1-t.md" done; }
printf 'def test_E1_old(): assert f() == 0\n' > "$r/tests/test_old.py"; g add -A; g commit -qm "test(T1): E1 red, an older change"
g checkout -qb feat/1-a
mkdir -p "$ch"; { printf -- '---\nstatus: open\n---\n\n## Example map\n\n'; for i in $(seq 1 20); do echo "  E$i: e$i"; done; } > "$ch/README.md"
task "$ch" T1 "E1, E2"; task "$ch" T2 E3; task "$ch" T3 E4; task "$ch" T4 E5; task "$ch" T5 E6; task "$ch" T6 E7; task "$ch" T7 E8 done
g add -A; g commit -qm "docs: tasks"
done_ T1 || true; [ $rc = 3 ] && ! marked T1 && grep -q "since main" "$tmp/out" || fail "counted a red commit from the base branch"
printf 'def test_E1_a(): assert f() == 1\ndef test_E2_b(): assert f() == 2\n' > "$r/tests/test_a.py"
g add tests; g commit -qm "test(T1): E1 E2 red"
echo 'def f(): return 1' > "$r/src/a.py"; g add src; g commit -qm "feat(T1): a"
done_ T1 && marked T1 || fail "rejected a protected red commit"
printf 'def test_E3_c(): assert f() == 3\n' >> "$r/tests/test_a.py"; g add tests; g commit -qm "test(T2): E3 red"
done_ T1 || fail "a red commit of another task that only adds tests broke T1's protection"
sed -i 's/== 3/== 1/' "$r/tests/test_a.py"
done_ T2 || true; [ $rc = 3 ] && ! marked T2 || fail "accepted an uncommitted change to a red test"
g commit -qm "feat(T2): c" -- tests
done_ T2 || true; [ $rc = 3 ] || fail "accepted a commit that changes a red test"
printf 'def test_E9_d(): pass\n' > "$r/tests/test_d.py"; g add tests; g commit -qm "test(T3): E9 red"
done_ T3 || true; [ $rc = 3 ] && grep -q "E4 has no test" "$tmp/out" || fail "accepted a red commit without the task's example"
printf 'def test_E5_e(): pass\n' > "$r/tests/test_e.py"; g add tests; g commit -qm "test(T4): E5 red"
printf 'def test_E5_e(): pass\ndef test_e_edge(): pass\n' > "$r/tests/test_e.py"; g commit -qm "feat(T4): e" -- tests
done_ T4 && marked T4 || fail "rejected new tests added after the red commit"
printf 'def test_E6_f(): assert f() == 6\n' > "$r/tests/test_f.py"; g add tests; g commit -qm "test(T5): E6 red"
printf 'def test_E6_f(): assert True\ndef test_E7_g(): assert f() == 7\n' > "$r/tests/test_f.py"; g commit -qm "test(T6): E7 red" -- tests
done_ T5 || true; [ $rc = 3 ] && ! marked T5 && grep -q "test(T6)" "$tmp/out" || fail "accepted a red test changed by the red commit of another task"
task "$ch" T8 E1; task "$ch" T9 E11; task "$ch" T10 E12
printf 'def test_E10_h(): pass\n' > "$r/tests/test_h.py"; g add tests; g commit -qm "test(T8): E10 red"
done_ T8 || true; [ $rc = 3 ] && grep -q "E1 has no test" "$tmp/out" || fail "took a test of E10 for a test of E1"
printf 'def test_E11_i(): assert f() == 11\n' > "$r/tests/test_i.py"; g add tests; g commit -qm "test(T9): E11 red"
printf 'def test_E11_i(): assert True\n' > "$r/tests/test_i.py"; g commit -qm "test(T9): E11 again" -- tests
done_ T9 || true; [ $rc = 3 ] && grep -q "removes or changes" "$tmp/out" || fail "accepted a second red commit of the task that changes the first one's test"
printf 'def test_E12_j(): pass\n' >> "$r/tests/test_old.py"; g add tests; g commit -qm "test(T10): E12 red"
sed -i 's/== 0/== 10/' "$r/tests/test_old.py"; g commit -qm "feat(T10): j" -- tests
done_ T10 && marked T10 || fail "rejected a change to a line the red commit did not add, in a file it touched"
task "$ch" T11 E13; task "$ch" T12 E14; task "$ch" T13 E15; task "$ch" T14 E16; task "$ch" T15 E17; task "$ch" T16 E18
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
task "$ch" T17 E19
printf 'def test_E19_q(): assert f() == 19\n' > "$r/tests/test_q.py"; g add docs tests; g commit -qm "test(T17): E19 red"
printf 'def test_E19_q(): pass\n' > "$r/tests/test_q.py"; sed -i 's/^examples: \[E19\]$/examples: []/' "$ch/tasks/T17-t.md"
g add docs tests; g commit -qm "feat(T17): q, and E19 dropped from the task file"
done_ T17 || true; [ $rc = 3 ] && ! marked T17 && grep -q "no longer declares E19" "$tmp/out" || fail "dropping the examples from the task file turned off the protection of the red commit"
python3 "$td" --audit "$ch" T17 >"$tmp/out" 2>&1 || true
grep -q "^T17 (todo): PROBLEM: the task file of T17 no longer declares E19" "$tmp/out" || fail "--audit missed a task whose examples were dropped after its red commit"
if command -v ssh-keygen >/dev/null; then  # signed commits with log.showSignature=true
  ssh-keygen -q -t ed25519 -N '' -f "$tmp/sign" >/dev/null
  task "$ch" T18 E20
  printf 'def test_E20_r(): assert f() == 20\n' > "$r/tests/test_r.py"; g add docs tests
  g -c gpg.format=ssh -c user.signingkey="$tmp/sign" commit -S -qm "test(T18): E20 red"
  g config log.showSignature true
  done_ T18 || true; g config --unset log.showSignature; [ $rc = 0 ] && marked T18 || fail "log.showSignature=true with signed commits broke the history parsing"
fi

echo "▶ task-done --audit of a task (read-only, for the review)"
audit() { rc=0; python3 "$td" --audit "$@" >"$tmp/out" 2>&1 || rc=$?; return $rc; }
cp -r "$ch" "$tmp/before"
audit "$ch" T4; [ $rc = 0 ] && grep -q "^T4 (done): ok" "$tmp/out" || fail "--audit did not accept a protected task"
audit "$ch" T2 || true; [ $rc = 3 ] && grep -q "^T2 (todo): PROBLEM: commit .* removes or changes" "$tmp/out" || fail "--audit missed a red test changed later"
audit "$ch" T5 || true; grep -q "^T5 (todo): PROBLEM: commit .* 'test(T6)" "$tmp/out" || fail "--audit missed a red test changed by another task's red commit"
audit "$ch" T3 || true; grep -q "^T3 (todo): PROBLEM: E4 has no test" "$tmp/out" || fail "--audit missed an example without a test"
audit "$ch" T7 || true; grep -q "^T7 (done): PROBLEM: no red commit" "$tmp/out" || fail "--audit missed a done task without a red commit"
diff -r "$ch" "$tmp/before" >/dev/null || fail "--audit edited the change folder"
printf 'def test_E5_e(): assert False\n' > "$r/tests/test_e.py"
audit "$ch" T4 || true; grep -q "^T4 (done): ok" "$tmp/out" || fail "--audit counted uncommitted changes"
git -C "$r" checkout -q -- tests/test_e.py

echo "▶ task-done: the change and the task of the branch, <change>/T<n>"
tda="$PWD/$td"; c="$tmp/change"; mkdir -p "$c/tests" "$c/src"; git -C "$c" init -q -b main
gc() { git -C "$c" -c user.name=t -c user.email=t@t "$@"; }
tdc() { rc=0; (cd "$c/tests" && python3 "$tda" "$@") >"$tmp/out" 2>&1 || rc=$?; return $rc; }
printf 'def test_E1_old(): pass\n' > "$c/tests/test_old.py"; gc add -A; gc commit -qm "test(T1): E1 red, an older change"
cc="$c/docs/changes/7-cancel"; mkdir -p "$cc"
printf -- '---\nstatus: open\nissue: 7\n---\n\n## Example map\n\n  E1: a\n  E2: b\n' > "$cc/README.md"
printf -- '---\nstatus: approved   # draft | approved | obsolete\n---\n' | tee "$cc/spec.md" > "$cc/plan.md"
task "$cc" T1 E1; task "$cc" T2 E2 todo T1
gc add docs; gc commit -qm "docs: plan of 7-cancel"  # the plan PR, merged
gc checkout -qb 7-cancel/plan
tdc -- true || true; [ $rc = 2 ] && grep -q "plan branch" "$tmp/out" || fail "marked a task on the plan branch"
gc checkout -qb 7-cancel/T9 main
tdc -- true || true; [ $rc = 2 ] && grep -q "7-cancel/tasks/T9-\*\.md" "$tmp/out" || fail "did not exit 2 naming the task file searched for a task that does not exist"
gc checkout -qb 8-other/T1 main
tdc -- true || true; [ $rc = 2 ] && grep -q "docs/changes/8-other" "$tmp/out" || fail "did not exit 2 naming the folder searched for a branch without a change folder"
tdc --audit || true; [ $rc = 2 ] || fail "--audit did not exit 2 for a branch without a change folder"
gc checkout -qb 7-cancel/T1 main
tdc -- true || true; [ $rc = 3 ] || fail "counted a red commit from the base branch for the task of the branch"
printf 'def test_E1_a(): pass\n' > "$c/tests/test_a.py"; gc add tests; gc commit -qm "test(T1): E1 red"
echo 'x = 1' > "$c/src/a.py"; gc add src; gc commit -qm "feat(T1): a"
tdc -- true && status_is "$cc/tasks/T1-t.md" done && status_is "$cc/tasks/T2-t.md" todo || fail "did not mark the task of the branch"
grep -q '^status: open$' "$cc/README.md" || fail "set status: done in the README with tasks left"
grep -q '^status: approved ' "$cc/spec.md" || fail "set the spec obsolete with tasks left"
tdc --audit && grep -q "^T1 (done): ok" "$tmp/out" || fail "--audit did not check the task of the branch"
gc commit -qam "feat(T1): done"
gc checkout -qb feat/7-cancel/T2 main  # branched before T1 is merged: its T1 is still todo
tdc --audit || true; [ $rc = 3 ] && grep -q "^T2 (todo): pending" "$tmp/out" \
  && grep -q "^T2 (todo): PROBLEM: depends on T1, not done in main" "$tmp/out" || fail "--audit missed a dependency not done in the base branch"
sed -i 's/^examples: \[E2\]$/examples: [E2, E5]/' "$cc/tasks/T2-t.md"
tdc --audit || true; grep -q "^T2 (todo): PROBLEM: E5 not in the example map" "$tmp/out" || fail "--audit missed an example of the task that is not in the map"
gc checkout -q -- docs
gc checkout -q main; gc merge -q --ff-only 7-cancel/T1; gc checkout -q feat/7-cancel/T2
tdc --audit && ! grep -q PROBLEM "$tmp/out" || fail "--audit did not take T1 as done once merged into the base branch"
printf 'def test_E2_b(): pass\n' > "$c/tests/test_b.py"; gc add tests; gc commit -qm "test(T2): E2 red"
mkdir -p "$c/src"; echo 'y = 2' > "$c/src/b.py"; gc add src; gc commit -qm "feat(T2): b"
tdc -- true && status_is "$cc/tasks/T2-t.md" done || fail "did not mark T2"
grep -q '^status: done$' "$cc/README.md" && grep -q '^issue: 7$' "$cc/README.md" || fail "did not set status: done in the README when the last task was done (T1 done in the base branch)"
grep -q '^status: obsolete   # draft' "$cc/spec.md" && grep -q '^status: obsolete ' "$cc/plan.md" || fail "did not set spec.md and plan.md obsolete when the change was done (D-0006)"
gc commit -qam "feat(T2): done"; gc checkout -q main; gc merge -q --no-edit feat/7-cancel/T2
gc checkout -qb fix/7-cancel/T1  # same name as a change already finished in main
tdc -- true || true; [ $rc = 2 ] && grep -q "finished change" "$tmp/out" || fail "reused the folder of a finished change"
tdc --audit || true; [ $rc = 2 ] && grep -q "finished change" "$tmp/out" || fail "--audit reused the folder of a finished change"
gc checkout -q main; zc="$c/docs/changes/11-z"; mkdir -p "$zc"
printf -- '---\nstatus: open\n---\n\nstatus: done (only the frontmatter counts)\n' > "$zc/README.md"; task "$zc" T1 ""
gc add docs; gc commit -qm "docs: 11-z, open"; gc checkout -qb 11-z/T1
tdc -- true && status_is "$zc/tasks/T1-t.md" done || fail "took 'status: done' outside the frontmatter for a finished change"
n="$tmp/nobase"; mkdir -p "$n"; git -C "$n" init -q -b trunk
git -C "$n" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "chore: start"
task "$n/ch" T1 E1
rc=0; python3 "$td" "$n/ch" T1 -- true >"$tmp/out" 2>&1 || rc=$?
[ $rc = 3 ] && grep -q "PROBLEM: .*no base branch" "$tmp/out" || fail "did not exit 3 with a PROBLEM line without a base branch"
audit "$n/ch" T1 || true; [ $rc = 3 ] && grep -q "^PROBLEM: .*no base branch" "$tmp/out" || fail "--audit did not exit 3 with a PROBLEM line without a base branch"
w="$tmp/work"; mkdir -p "$w/tests"; git init -q --bare -b main "$tmp/origin.git"; git -C "$w" init -q -b main
gw() { git -C "$w" -c user.name=t -c user.email=t@t "$@"; }
gw commit -q --allow-empty -m "chore: start"; gw remote add origin "$tmp/origin.git"; gw push -q origin main main:develop
gw checkout -qb feat/9-x origin/develop; task "$w/ch" T1 E1; gw add -A; gw commit -qm "docs: tasks"
gw remote set-head origin develop
audit "$w/ch" T1 || true; grep -q "since origin/develop" "$tmp/out" || fail "--audit did not take origin/HEAD as the base branch"
gw checkout -qb old main; printf 'def test_E1_old(): pass\n' > "$w/tests/test_old.py"; gw add tests; gw commit -qm "test(T1): E1 red, merged earlier"
gw push -q origin old:main; gw checkout -qb feat/10-y origin/main  # the local main is stale: it lacks that commit
task "$w/ch" T1 E1 done; gw add -A; gw commit -qm "docs: tasks"
gw remote set-head origin -d
audit "$w/ch" T1 || true; grep -q "since origin/main" "$tmp/out" && grep -q "^T1 (done): PROBLEM: no red commit" "$tmp/out" || fail "--audit took a stale local main over origin/main"

echo "▶ task-done: board (D-0030) and --audit of the plan (D-0032)"
bd=skills/task-done/scripts/board.py
b="$tmp/board"; bc="$b/docs/changes/9-board"; mkdir -p "$bc"; git -C "$b" init -q -b main
gb() { git -C "$b" -c user.name=t -c user.email=t@t "$@"; }
board() { rc=0; python3 "$bd" "$@" >"$tmp/out" 2>&1 || rc=$?; return $rc; }
printf -- '---\nstatus: open\n---\n\n## Example map\n\n  E1: a\n  E2: b\n  E3: c\n  E4: d\n' > "$bc/README.md"
task "$bc" T1 E1 done; task "$bc" T2 E2 todo T1; task "$bc" T3 E3 todo T2; task "$bc" T4 E4; task "$bc" T5 "" todo "T1, T6"; task "$bc" T6 ""
gb add -A; gb commit -qm "docs: plan of 9-board"; gb branch 9-board/T4
task "$bc" T6 "" done  # done here, not merged
board "$bc"; [ $rc = 0 ] || fail "the board failed on a valid change"
grep -q "^T1 done: task T1$" "$tmp/out" && grep -q "^T2 ready: task T2$" "$tmp/out" && grep -q "^T3 blocked by T2: task T3$" "$tmp/out" \
  || fail "the board did not list done, ready and blocked tasks"
grep -q "^T4 doing (branch 9-board/T4): task T4$" "$tmp/out" || fail "the board did not take a task with a branch as doing"
grep -q "^T6 doing: task T6$" "$tmp/out" && grep -q "^T5 blocked by T6: task T5$" "$tmp/out" || fail "the board took a task done but not merged as done"
gb checkout -q -- docs; gb checkout -qb 9-board/plan
rc=0; (cd "$b" && python3 "$tda" --audit) >"$tmp/out" 2>&1 || rc=$?
[ $rc = 0 ] && grep -q "audit of the plan" "$tmp/out" || fail "--audit of the plan branch failed on a valid plan"
(cd "$b/docs" && python3 "${tda%/*}/board.py") >"$tmp/out" 2>&1 && grep -q "^T2 ready" "$tmp/out" || fail "the board did not take the change from the branch"
task "$bc" T2 E2 todo T9
board "$bc" || true; [ $rc = 2 ] && grep -q "T2 depends on T9, which does not exist" "$tmp/out" || fail "the board did not exit 2 on a dependency that does not exist"
(cd "$b" && python3 "$tda" --audit) >"$tmp/out" 2>&1 && fail "--audit of the plan branch accepted a dependency that does not exist"
grep -q "^PROBLEM: T2 depends on T9" "$tmp/out" || fail "--audit of the plan missed a dependency that does not exist"
task "$bc" T2 E2 todo T3
board "$bc" || true; [ $rc = 2 ] && grep -q "cycle: T2 -> T3 -> T2" "$tmp/out" || fail "the board did not exit 2 on a cycle"
audit "$bc" || true; [ $rc = 3 ] && grep -q "^PROBLEM: cycle: T2 -> T3 -> T2" "$tmp/out" || fail "--audit of the plan missed a cycle"
task "$bc" T2 E2 wip T1
board "$bc" || true; [ $rc = 2 ] && grep -q "status 'wip'" "$tmp/out" || fail "the board did not exit 2 on a malformed frontmatter"
audit "$bc" || true; [ $rc = 3 ] && grep -q "^PROBLEM: T2-t.md: status 'wip'" "$tmp/out" || fail "--audit of the plan missed a malformed frontmatter"
gb checkout -q -- docs; printf '  E9: an example of the map in no task\n' >> "$bc/README.md"
audit "$bc" || true; [ $rc = 3 ] && grep -q "^PROBLEM: E9 is in the example map but in no task's examples" "$tmp/out" || fail "--audit of the plan missed a map example in no task"

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

echo "▶ review: the publish job comments each finding on its line and keeps one summary comment"
grep -q -- '--inline' "$wf" || { echo "claude-review.yml does not ask /review-pr for the findings block (--inline)" >&2; exit 1; }
! grep -Eq 'APPROVE"|REQUEST_CHANGES"' "$wf" || { echo "claude-review.yml can approve or request changes" >&2; exit 1; }
pub="$tmp/pub"; mkdir -p "$pub"
awk "/<<'PY'\$/ { on=1; next } on && /^ +PY\$/ { exit } on" "$wf" | sed 's/^          //' > "$pub/publish.py"
cat > "$pub/gh" <<'EOF'
#!/usr/bin/env python3
# Fake gh: serves the PR from $FAKE/*.json and logs every write to $FAKE/log.
import json, os, re, sys
d = os.environ["FAKE"]; args = sys.argv[1:]
method, path = args[args.index("-X") + 1], args[args.index("-X") + 2]
path, _, query = path.partition("?")
data = json.load(sys.stdin) if "--input" in args else None
if method != "GET":
    with open(f"{d}/log", "a") as f: f.write(json.dumps({"method": method, "path": path, "data": data}) + "\n")
def load(name): return json.load(open(f"{d}/{name}")) if os.path.exists(f"{d}/{name}") else []
if method == "GET" and "page=1" not in query: print("[]")
elif re.search(r"/pulls/\d+/files$", path): print(json.dumps(load("files.json")))
elif re.search(r"/pulls/\d+/comments$", path): print(json.dumps(load("comments.json")))
elif re.search(r"/issues/\d+/comments$", path) and method == "GET": print(json.dumps(load("issue.json")))
elif re.search(r"/pulls/\d+/reviews$", path):
    if os.environ.get("FAIL_REVIEW"): sys.exit("HTTP 422: line must be part of the diff")
    json.dump(data["comments"], open(f"{d}/review.json", "w")); print('{"id": 7}')
elif path.endswith("/reviews/7/comments"):
    print(json.dumps([dict(c, html_url=f"u/{c['path']}:{c['line']}") for c in load("review.json")]))
else: print("{}")
EOF
chmod +x "$pub/gh"
publish() {  # publish <report | -> [fail the review POST]: runs the publish script in $pub, with $pub/{files,comments,issue}.json
  rm -f "$pub/log" "$pub/review.json"; if [ "$1" = - ]; then rm -f "$pub/report.md"; else printf '%s\n' "$1" > "$pub/report.md"; fi
  (cd "$pub" && FAKE="$pub" GH="$pub/gh" REPO=o/r PR=5 HEAD_SHA=abc RUN_URL=run FAIL_REVIEW="${2:-}" python3 publish.py) >"$pub/out" 2>&1 \
    || { cat "$pub/out" >&2; echo "the publish script of claude-review.yml failed" >&2; exit 1; }
}
pfail() { echo "publish: $1" >&2; cat "$pub/log" >&2 2>/dev/null; exit 1; }
written() {  # written <method> <path suffix>: the body of that write in the last run
  python3 -c 'import json, sys
for l in open(sys.argv[1]):
    w = json.loads(l)
    if w["method"] == sys.argv[2] and w["path"].endswith(sys.argv[3]): print(json.dumps(w["data"]))' "$pub/log" "$@"
}
body_is() {  # body_is <method> <path suffix> <python assertion on b, the comment body>
  python3 -c "import json, sys; b = json.loads(sys.argv[1])['body']; assert $3, b" "$(written "$1" "$2")"
}
printf '%s' '[{"filename": "a.py", "patch": "@@ -1,2 +1,4 @@\n x = 1\n+y = 2\n+z = 3\n-w = 0\n w2 = 4"},
  {"filename": "b.py", "patch": "@@ -0,0 +1,3 @@\n+a\n+b\n+c\n@@ -10,2 +12,2 @@\n k\n+m"}, {"filename": "img.png"}]' > "$pub/files.json"
echo '[]' > "$pub/comments.json"
echo '[{"id": 1, "body": "<!-- review-kit:review-pr --> by a person", "user": {"login": "someone"}}]' > "$pub/issue.json"
report='Preamble
<!-- review-kit:review-pr -->
## Summary and verdict
Markdown report.
```json review-kit
{"verdict": "CHANGES NEEDED", "tier": 1, "summary": "Adds z.", "done_well": ["a.py:3 is clear"], "verification": ["pytest: 3 passed"],
 "findings": [
  {"id": "O1", "title": "Range", "path": "b.py", "start_line": 2, "line": 3, "body": "- **Problem:** o"},
  {"id": "C1", "title": "Breaks\nz", "path": "a.py", "line": 3, "body": "- **Problem:** c"},
  {"id": "R1", "title": "Far away", "path": "a.py", "line": 50, "body": "- **Problem:** r"},
  {"id": "R2", "title": "Deleted line", "path": "a.py", "line": 5, "body": "- **Problem:** deleted"},
  {"id": "N1", "title": "Whole file", "path": null, "body": "- **Problem:** n"},
  {"id": "N2", "title": "Range across hunks", "path": "b.py", "start_line": 3, "line": 13, "body": "- **Problem:** n2"}]}
```
REVIEW_RESULT: CHANGES tier=1 critical=1 required=2 uncertain=0'
publish "$report"
[ -z "$(written PATCH /issues/comments/1)" ] && [ -n "$(written POST /issues/5/comments)" ] || pfail "edited a summary comment that a person wrote"
python3 - "$(written POST /pulls/5/reviews)" "$(written POST /issues/5/comments)" <<'EOF' || pfail "wrong review or summary on the first run"
import json, sys
rev, body = json.loads(sys.argv[1]), json.loads(sys.argv[2])["body"]
assert rev["event"] == "COMMENT" and rev["commit_id"] == "abc", rev
got = {(c["path"], c.get("start_line"), c["line"]) for c in rev["comments"]}
assert got == {("a.py", None, 3), ("b.py", 2, 3), ("b.py", None, 13)}, got   # R1 outside the diff, R2 on a deleted line, N1 without a line
c1 = next(c for c in rev["comments"] if c["path"] == "a.py")
assert c1["body"].startswith("<!-- review-kit:finding -->\n**C1 · Critical** Breaks z\n"), c1["body"]
assert body.startswith("<!-- review-kit:review-pr -->\n## review-kit: CHANGES NEEDED · tier 1\n"), body
assert "Critical 1 · Required 2 · Optional 1 · Nits 2" in body, body
assert "- [**C1** Breaks z](u/a.py:3) — `a.py:3`" in body, body
assert "### Outside the diff" in body and "#### R1 Far away\n- **Location:** `a.py:50`\n- **Problem:** r" in body, body
assert body.index("**C1**") < body.index("**R1**") < body.index("<details>"), body
assert "- [**O1** Range](u/b.py:3) — `b.py:2-3`" in body and "#### N1 Whole file" in body, body
assert "Markdown report." not in body and "Preamble" not in body and "- pytest: 3 passed" in body, body
EOF
python3 - "$pub" <<'EOF'  # second run: C1 already commented by the bot, a fake finding comment by a person, the summary posted by the bot
import json, sys
d = sys.argv[1]
json.dump([{"path": "a.py", "line": 3, "html_url": "old/c1", "user": {"login": "github-actions[bot]"},
            "body": "<!-- review-kit:finding -->\n**C1 · Critical** Breaks z\n\nold"},
           {"path": "b.py", "line": 3, "html_url": "x", "user": {"login": "someone"},
            "body": "<!-- review-kit:finding -->\n**O1 · Optional** Range\n\nfake"}], open(f"{d}/comments.json", "w"))
issue = json.load(open(f"{d}/issue.json"))
json.dump(issue + [{"id": 2, "body": "<!-- review-kit:review-pr -->\nold", "user": {"login": "github-actions[bot]"}}], open(f"{d}/issue.json", "w"))
EOF
publish "$report"
python3 -c 'import json, sys; r = json.loads(sys.argv[1]); assert {(c["path"], c["line"]) for c in r["comments"]} == {("b.py", 3), ("b.py", 13)}, r' \
  "$(written POST /pulls/5/reviews)" || pfail "repeated a finding the bot already commented on that line"
body_is PATCH /issues/comments/2 '"[**C1** Breaks z](old/c1)" in b' && [ -z "$(written POST /issues/5/comments)" ] \
  || pfail "did not update the bot's summary comment"
publish "$report" 1
body_is PATCH /issues/comments/2 '"could not be posted" in b and "#### O1 Range" in b and "[**C1** Breaks z](old/c1)" in b' \
  || pfail "lost findings when the review could not be posted"
publish "$(printf '%s\n' "$report" | sed 's/"findings": \[/"findings": [x/')"
body_is PATCH /issues/comments/2 'b.startswith("<!-- review-kit:review-pr -->\n## Summary and verdict\nMarkdown report.")' \
  && [ -z "$(written POST /pulls/5/reviews)" ] || pfail "did not post the report as it is when the findings block is not valid JSON"
publish "$(printf '%s\n' "$report" | sed '/^```json/,/^```$/d')"
body_is PATCH /issues/comments/2 'b.startswith("<!-- review-kit:review-pr -->\n## Summary and verdict\nMarkdown report.")' \
  || pfail "did not post a report without a findings block"
echo 'exit=1' > "$pub/status.txt"; publish -
body_is PATCH /issues/comments/2 '"did not finish correctly (exit=1)" in b' || pfail "did not say that the review failed"

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
