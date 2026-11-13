#!/usr/bin/env bash
i=$1; D=<scratchpad>/run-$i; mkdir -p $D
cd ~/git/agent-skills/tests/review-sandbox/repo
git switch -q feature/orders-pagination-invoices
T0=$(date +%s)
CLAUDECODE=1 REVIEW_KIT_RERUN=1 EV=$D/events.jsonl PATH=<scratchpad>/shim:$PATH git push -u origin feature/orders-pagination-invoices > $D/push.out 2>&1
echo "rc=$? dur=$(($(date +%s)-T0))" > $D/rc
cp .git/review-kit/last-prepush.md $D/report.md
git push origin --delete feature/orders-pagination-invoices -q --no-verify 2>/dev/null
