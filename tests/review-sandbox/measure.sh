#!/usr/bin/env bash
# Uso: tests/review-sandbox/measure.sh <review-pr|review-prepush> <n>
# Ejecuta la review <n> veces con Codex sobre el sandbox generado (build.sh --codex) y guarda, por ejecución,
# en results/<comando>/run-<i>/: events.jsonl (salida --json), report.md (último mensaje), meta.json y summary.json
# (tokens por agente y total, subagentes y duración, de summarize.py). results/ no se sube al repo.
# Las ejecuciones se puntúan a mano contra EXPECTED.md. Necesita red (API de Codex): no va en scripts/check.sh.
# Modelo: MODEL (por defecto gpt-6.1-terra), siempre explícito con -m. Los subagentes no fijan modelo y heredan el de la sesión.
# START=<k> numera desde k (para añadir una repetición sin pisar las anteriores).
# Personas: Codex no carga .codex/agents/ de un proyecto que no es de confianza en ~/.codex/config.toml, y
# `-c projects."<ruta>".trust_level=...` no lo hace de confianza; entonces el subagente usa la copia global de
# ~/.codex/agents/ (T1 midió eso). Aquí cada persona del sandbox se declara con un -c de una sola llamada
# (`agents.<rol>.config_file`), que tiene prioridad sobre la global del mismo nombre. No se toca ~/.codex.
# summarize.py comprueba después, en el registro del subagente, que la persona cargada es la del sandbox.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMD="${1:?uso: measure.sh <review-pr|review-prepush> <n>}"
N="${2:?uso: measure.sh <review-pr|review-prepush> <n>}"
MODEL="${MODEL:-gpt-6.1-terra}"
START="${START:-1}"
BRANCH=feature/orders-pagination-invoices
REPO="$HERE/repo"
[ -d "$REPO/.agents/skills" ] || { echo "falta el sandbox con la disposición de Codex: ejecuta tests/review-sandbox/build.sh --codex" >&2; exit 2; }

# Las skills y personas del proyecto, no las globales de ~/.agents o ~/.codex (pueden ser de otra versión).
SCOPE="Usa solo las skills de este proyecto, en .agents/skills/ (también las que ella cite: review-context, review-report, task-done); no leas ~/.agents ni ~/.codex. Los subagentes son los de .codex/agents/. No cambies ningún fichero."
case "$CMD" in
  review-pr)      PROMPT="Ejecuta la skill review-pr (.agents/skills/review-pr/SKILL.md) con los argumentos: $BRANCH main. $SCOPE" ;;
  review-prepush) PROMPT="Ejecuta la skill review-prepush (.agents/skills/review-prepush/SKILL.md) con los argumentos: main, estando en la rama $BRANCH. $SCOPE" ;;
  *) echo "comando desconocido: $CMD" >&2; exit 2 ;;
esac

AGENT_ARGS=()
while IFS= read -r line; do AGENT_ARGS+=("$line"); done < <(python3 -I - "$REPO/.codex/agents" <<'PY'
import json, sys, tomllib
from pathlib import Path
for f in sorted(Path(sys.argv[1]).glob("*.toml")):
    t = tomllib.loads(f.read_text(encoding="utf-8"))
    print("-c"); print(f"agents.{t['name']}.description={json.dumps(t['description'])}")
    print("-c"); print(f"agents.{t['name']}.config_file={json.dumps(str(f.resolve()))}")
PY
)

VERSION="$(codex --version)"
KIT_COMMIT="$(git -C "$HERE" rev-parse --short HEAD)"
for ((i = START; i < START + N; i++)); do
  DIR="$HERE/results/$CMD/run-$i"
  rm -rf "$DIR"
  mkdir -p "$DIR"
  git -C "$REPO" switch -q "$BRANCH"
  T0=$(date +%s)
  # Sin --dangerously-bypass-*: sandbox de solo lectura. Sin push, así que el hook pre-push no se dispara.
  set +e
  (cd "$REPO" && codex exec -m "$MODEL" -s read-only --json "${AGENT_ARGS[@]}" -o "$DIR/report.md" "$PROMPT") >"$DIR/events.jsonl" 2>"$DIR/stderr.txt"
  RC=$?
  set -e
  T1=$(date +%s)
  python3 -I - "$DIR/meta.json" "$CMD" "$i" "$MODEL" "$VERSION" "$RC" "$((T1 - T0))" "$KIT_COMMIT" "$PROMPT" <<'PY'
import json, sys
keys = ["command", "run", "model", "codex", "exit_code", "seconds", "kit_commit", "prompt"]
meta = dict(zip(keys, sys.argv[2:]))
for k in ("run", "exit_code", "seconds"):
    meta[k] = int(meta[k])
meta["codex_exec"] = f"codex exec -m {meta['model']} -s read-only --json -c agents.<rol>.{{description,config_file}}=... -o report.md \"<prompt>\" (en repo/)"
meta["personas"] = "las de .codex/agents/ del sandbox, con -c agents.<rol>.config_file (una por persona)"
json.dump(meta, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
PY
  python3 -I "$HERE/summarize.py" "$DIR" >"$DIR/summary.json" || echo "summarize.py falló en $DIR" >&2
  echo "$CMD run-$i: exit $RC, $((T1 - T0)) s -> $DIR"
done
