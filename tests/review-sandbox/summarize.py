#!/usr/bin/env python3
"""Resume una ejecución de measure.sh: tokens por agente y total, subagentes y modelos.

Uso: python3 -I summarize.py <results/<comando>/run-<i>>   (escribe JSON en stdout)

Las cifras salen de los registros de sesión de Codex ($CODEX_HOME/sessions/**/rollout-*.jsonl): cada llamada
a la API deja un `token_usage_record` con su `usage` y el `thread_id` del agente que la hizo. No se estima nada:
si falta un registro, la cifra falta. El total de `turn.completed` de events.jsonl se guarda aparte, como contraste.
"""
import json
import os
import sys
from pathlib import Path

FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")


def main(run: Path) -> dict:
    root = None
    turn_usage = None
    for line in (run / "events.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "thread.started":
            root = e["thread_id"]
        if e.get("type") == "turn.completed":
            turn_usage = e.get("usage")
    out = {"root_thread": root, "turn_completed_usage": turn_usage, "agents": {}, "problems": []}
    if root is None:
        out["problems"].append("events.jsonl no tiene thread.started")
        return out

    home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    seen = set()
    threads = {}  # thread_id -> {role, models, usage}
    for rollout in sorted((home / "sessions").rglob("rollout-*.jsonl")):
        text = rollout.read_text(encoding="utf-8")
        if root not in text:
            continue
        for line in text.splitlines():
            e = json.loads(line)
            p = e.get("payload", {})
            if e.get("type") == "session_meta":
                t = threads.setdefault(p["id"], {"role": None, "models": [], "usage": dict.fromkeys(FIELDS, 0), "calls": 0})
                if p["id"] == root:
                    t["role"] = "main"
                elif p.get("agent_role"):
                    t["role"] = p["agent_role"]
            elif e.get("type") == "turn_context":
                tid = rollout.stem.rsplit("-", 5)[-5:]
                tid = "-".join(tid)
                t = threads.setdefault(tid, {"role": None, "models": [], "usage": dict.fromkeys(FIELDS, 0), "calls": 0})
                m = (p.get("model"), p.get("effort"))
                if m not in t["models"]:
                    t["models"].append(m)
            elif e.get("type") == "token_usage_record" and p.get("session_id") == root:
                key = (p["thread_id"], p["response_id"])
                if key in seen:
                    continue
                seen.add(key)
                t = threads.setdefault(p["thread_id"], {"role": None, "models": [], "usage": dict.fromkeys(FIELDS, 0), "calls": 0})
                for f in FIELDS:
                    t["usage"][f] += p["usage"].get(f, 0)
                t["calls"] += 1
    total = dict.fromkeys(FIELDS, 0)
    for tid, t in threads.items():
        if t["calls"] == 0:
            continue
        for f in FIELDS:
            total[f] += t["usage"][f]
        out["agents"][tid] = {"role": t["role"], "api_calls": t["calls"], **t["usage"],
                              "models": [f"{m} (effort {eff})" if eff else str(m) for m, eff in t["models"]]}
    out["total"] = total
    out["subagents"] = sum(1 for a in out["agents"].values() if a["role"] != "main")
    out["models_seen"] = sorted({m for t in threads.values() for m, _ in t["models"] if m})
    if "main" not in {a["role"] for a in out["agents"].values()}:
        out["problems"].append("sin registros de la sesión principal")
    if turn_usage and turn_usage.get("input_tokens") != next((a["input_tokens"] for a in out["agents"].values() if a["role"] == "main"), None):
        out["problems"].append("el total de turn.completed no coincide con el de la sesión principal en los registros")
    return out


if __name__ == "__main__":
    json.dump(main(Path(sys.argv[1])), sys.stdout, ensure_ascii=False, indent=1)
    print()
