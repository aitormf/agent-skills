#!/usr/bin/env bash
# build.sh <threshold|none>: builds tests/review-sandbox/repo = kit at be48495^ + Codex layout + T2..T6 of change 95 as commits on the feature branch (needs the refs origin/main and origin/95-hechos-de-la-review/T6 of the kit checkout)
set -euo pipefail
KIT="${KIT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}"; T="$1"
cd $KIT && bash tests/review-sandbox/build.sh --codex >/dev/null
R=$KIT/tests/review-sandbox/repo; X=$(mktemp -d)
cp -R $R/.agents $R/.codex $X/; cp $R/.git/hooks/pre-push $X/
rm -rf $R; mkdir $R; cd $R
git init -q -b main; git config user.name "Sandbox Dev"; git config user.email s@example.invalid; git config commit.gpgsign false
git -C $KIT archive be48495^ | tar -x
cp -R $X/.agents $X/.codex .
if [ "$T" = none ]; then printf '[gate.control]\n' > .harness-config.toml; else printf '[review]\nmax_lines_per_reviewer = %s\n' "$T" > .harness-config.toml; fi
git add -A; git commit -q -m "Base: kit at be48495^ with the Codex layout"
git switch -q -c feature/orders-pagination-invoices
git fetch -q $KIT refs/remotes/origin/main refs/remotes/origin/95-hechos-de-la-review/T6
for c in be48495 5072da7 b75282c 96fbd51 8660035; do git cherry-pick $c >/dev/null; done
git log --oneline; python3 $KIT/skills/review-context/scripts/review_facts.py main | sed -n 1,25p
