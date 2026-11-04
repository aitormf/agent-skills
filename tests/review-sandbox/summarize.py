#!/usr/bin/env python3
"""Resume una ejecución de measure.sh: tokens por agente y total, subagentes y modelos.

Uso: python3 -I summarize.py <results/<comando>/run-<i>> [<sandbox>]   (escribe JSON en stdout)

Además de los tokens, comprueba qué persona cargó cada subagente: el cuerpo completo (`developer_instructions`)
del .toml del sandbox (por defecto `<results>/../../repo/.codex/agents/`) debe estar en los mensajes `developer`
de arranque del subagente; si no, la ejecución es inválida (`problems`). Se compara también con el de
~/.codex/agents/ (o $CODEX_HOME/agents/) si existe, y se dice si las dos copias son distinguibles. Que Codex
"liste" una persona, o que la sesión principal la lea con `cat`, no prueba qué cargó el subagente. Registra
además, por subagente, el `fork_turns` con que se lanzó (None = no se indicó) y los tokens de entrada de su
primera llamada (lo que ya lleva antes de empezar: el historial heredado).

Las cifras salen de los registros de sesión de Codex ($CODEX_HOME/sessions/**/rollout-*.jsonl): cada llamada
a la API deja un `token_usage_record` con su `usage` y el `thread_id` del agente que la hizo. No se estima nada:
si falta un registro, la cifra falta. El total de `turn.completed` de events.jsonl se guarda aparte, como contraste.
"""
import json
import os
import sys
import tomllib
from pathlib import Path

FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")


def body(path: Path):
    """developer_instructions de un .toml de persona (None si no existe)."""
    if not path.is_file():
        return None
    return tomllib.loads(path.read_text(encoding="utf-8"))["developer_instructions"].strip()


def main(run: Path, sandbox: Path | None = None) -> dict:
    sandbox = sandbox or run.resolve().parent.parent.parent / "repo"
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
    spawn_args, spawn_paths = {}, {}  # call_id -> argumentos de spawn_agent; call_id -> agent_path del hijo
    threads = {}  # thread_id -> {role, models, usage}
    new = lambda: {"role": None, "models": [], "usage": dict.fromkeys(FIELDS, 0), "calls": 0, "dev": [], "path": None, "first": None}
    for rollout in sorted((home / "sessions").rglob("rollout-*.jsonl")):
        text = rollout.read_text(encoding="utf-8")
        if root not in text:
            continue
        cur = None  # hilo al que pertenece este fichero
        for line in text.splitlines():
            e = json.loads(line)
            p = e.get("payload", {})
            if e.get("type") == "session_meta":
                # Un hijo con historial heredado trae después la session_meta de su padre: el hilo del fichero es el primero.
                cur = cur or p["id"]
                t = threads.setdefault(p["id"], new())
                t["path"] = t["path"] or p.get("agent_path")
                if p["id"] == root:
                    t["role"] = "main"
                elif p.get("agent_role"):
                    t["role"] = p["agent_role"]
            elif e.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "developer" and cur:
                threads[cur]["dev"].append("".join(c.get("text", "") for c in p.get("content", [])))
            elif e.get("type") == "response_item" and p.get("type") == "function_call" and p.get("name") == "spawn_agent":
                spawn_args[p["call_id"]] = json.loads(p["arguments"])
            elif e.get("type") == "response_item" and p.get("type") == "function_call_output" and p.get("call_id") in spawn_args:
                try:
                    spawn_paths[p["call_id"]] = json.loads(p["output"]).get("task_name")
                except (ValueError, AttributeError):
                    pass
            elif e.get("type") == "turn_context":
                tid = rollout.stem.rsplit("-", 5)[-5:]
                tid = "-".join(tid)
                t = threads.setdefault(tid, new())
                m = (p.get("model"), p.get("effort"))
                if m not in t["models"]:
                    t["models"].append(m)
            elif e.get("type") == "token_usage_record" and p.get("session_id") == root:
                key = (p["thread_id"], p["response_id"])
                if key in seen:
                    continue
                seen.add(key)
                t = threads.setdefault(p["thread_id"], new())
                if t["first"] is None:
                    t["first"] = p["usage"].get("input_tokens")
                for f in FIELDS:
                    t["usage"][f] += p["usage"].get(f, 0)
                t["calls"] += 1
    forks = {spawn_paths[c]: a.get("fork_turns") for c, a in spawn_args.items() if c in spawn_paths}
    global_agents = home / "agents"
    total = dict.fromkeys(FIELDS, 0)
    for tid, t in threads.items():
        if t["calls"] == 0:
            continue
        for f in FIELDS:
            total[f] += t["usage"][f]
        out["agents"][tid] = {"role": t["role"], "api_calls": t["calls"], **t["usage"],
                              "models": [f"{m} (effort {eff})" if eff else str(m) for m, eff in t["models"]]}
        if t["role"] != "main":
            out["agents"][tid]["fork_turns"] = forks.get(t["path"])
            out["agents"][tid]["first_call_input_tokens"] = t["first"]
            out["agents"][tid]["persona"] = persona = check_persona(t["role"], "\n".join(t["dev"]), sandbox, global_agents)
            if not persona["sandbox_match"]:
                out["problems"].append(f"{t['role']} ({tid}): la persona cargada no es la del sandbox ({persona['detail']})")
    out["total"] = total
    out["subagents"] = sum(1 for a in out["agents"].values() if a["role"] != "main")
    out["models_seen"] = sorted({m for t in threads.values() for m, _ in t["models"] if m})
    if "main" not in {a["role"] for a in out["agents"].values()}:
        out["problems"].append("sin registros de la sesión principal")
    if turn_usage and turn_usage.get("input_tokens") != next((a["input_tokens"] for a in out["agents"].values() if a["role"] == "main"), None):
        out["problems"].append("el total de turn.completed no coincide con el de la sesión principal en los registros")
    return out


def check_persona(role, dev_text: str, sandbox: Path, global_agents: Path) -> dict:
    sb = body(sandbox / ".codex" / "agents" / f"{role}.toml") if role else None
    gl = body(global_agents / f"{role}.toml") if role else None
    if sb is None:
        return {"sandbox_match": False, "global_match": None, "distinguishable": None,
                "detail": "el sandbox no tiene .toml para ese rol"}
    in_sb = sb in dev_text
    in_gl = None if gl is None else gl in dev_text
    dist = None if gl is None else gl != sb
    what = "la del sandbox" if in_sb else ("la global de ~/.codex/agents" if in_gl else "ninguna de las dos")
    if in_sb and dist is False:
        what += " (idéntica a la global: no se puede distinguir)"
    return {"sandbox_match": in_sb, "global_match": in_gl, "distinguishable": dist,
            "detail": f"cargó {what}", "body_chars": len(sb)}


if __name__ == "__main__":
    json.dump(main(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else None), sys.stdout, ensure_ascii=False, indent=1)
    print()
