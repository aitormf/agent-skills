#!/usr/bin/env bash
# Observation shim: same args as the hook builds, plus --json (events to $EV) and -o (last message to stdout)
real=~/.local/bin/codex
echo "$@" > "$EV.argv"
o=$(mktemp)
"$real" exec --json -o "$o" "${@:2}" > "$EV" 
rc=$?
cat "$o"; exit $rc
