---
status: open
issue: 97
---

# La verificación y Semgrep los ejecuta el hook, no el revisor

**Problema:** en `harness-review`, Codex trabaja con `codex exec -s read-only` y no tiene directorio temporal. Por eso la review de cada push se hace sin `check.sh`, sin tests, sin mypy y sin Semgrep (`uv` y Semgrep fallan con «No usable temporary directory»). El informe lo dice en Verification, pero el veredicto no lo refleja, así que un push con los tests rotos puede pasar. Además, ejecutar la verificación desde la sesión principal del revisor es parte de la entrada que #95 no consiguió bajar. Le importa a quien confía en la review cruzada para no subir código roto.

**Plazo máximo:** unos 2 días de trabajo de agente, en 3 tareas.

**Fuera de alcance:**
- Dar escritura al sandbox de Codex (`workspace-write`, `writable_roots`, `TMPDIR` propio). Queda descartado en D-0061.
- Ejecutar la verificación en el push de una persona: no se revisa (D-0056) y sigue así.
- `review-pr` en CI.
- Leer los comandos de la sección Commands de `AGENTS.md` desde el hook. Esa sección es texto libre y la rama puede cambiarla.
- Medir de nuevo la entrada de la sesión principal (#95). Se puede hacer después, en otro cambio.

## Mapa de ejemplos

```
Rule R1: los comandos de verificación del hook están en [review] verify de .harness-config.toml, leído de la rama base (→ D-0061)
  E1: la base tiene verify = ["./scripts/check.sh"] → el hook lo ejecuta desde la raíz del repo antes de lanzar al revisor, en el push de un agente
  E2: la rama cambia verify a ["true"] en su .harness-config.toml → el hook usa el de la base
  E3: verify = ["uv run pytest -q", "uv run mypy src"] → los ejecuta en orden y guarda el resultado de cada uno
  E4: sin la clave → el hook no ejecuta nada y la review hace la verificación como hoy
  E5: push de una persona → el hook no ejecuta la verificación (como hoy, D-0056)
  E6: la caché de veredictos tiene ya un veredicto para este diff (D-0042) → se reutiliza sin ejecutar la verificación

Rule R2: si la verificación sale en rojo, el push del agente se bloquea sin lanzar al revisor (→ D-0062)
  E7: ./scripts/check.sh sale con 1 → «review-kit: verificación en rojo: ./scripts/check.sh (exit 1)» con las últimas 40 líneas de su salida; exit 1; no se lanza el revisor ni se guarda veredicto
  E8: un comando pasa del tiempo límite (600 s) → se bloquea igual, con «(timeout 600 s)»
  E9: todos salen con 0 → sigue con la review

Rule R3: el hook ejecuta Semgrep sobre las líneas añadidas y pasa el resultado a la review; Semgrep nunca bloquea por sí solo
  E10: Semgrep instalado, un hallazgo en una línea añadida → aparece en el fichero de resultados con su línea final de semgrep_added.py
  E11: Semgrep no instalado → «Semgrep: no disponible» en el fichero de resultados; el push sigue
  E12: [review] semgrep = false en la base → no se ejecuta y el fichero lo dice

Rule R4: la review usa los resultados del hook y no vuelve a ejecutar nada
  E13: el hook pasa REVIEW_KIT_VERIFICATION=<fichero> → el paso 2 de review-prepush no ejecuta comandos ni Semgrep: cita el fichero en Verification y trata los hallazgos de Semgrep como candidatos (verifier incluido)
  E14: review-prepush lanzado a mano, sin la variable → el paso 2 es el de hoy
  E15: un revisor falso en el test del hook (como codex en read-only) → recibe la variable y el fichero tiene el resultado de check.sh y de Semgrep (el test que pide #97)

Rule R5: un proyecto nuevo trae la clave
  E16: setup-guardrails-python escribe [review] verify = ["./scripts/check.sh"] en el .harness-config.toml que genera
```

## Supuestos

- El fichero de resultados va en `.git/review-kit/verification.md`, junto al informe. Lleva cada comando, su código de salida, las últimas 40 líneas de su salida y la salida de `semgrep_added.py`.
- El tiempo límite de cada comando es 600 s. Un agente no puede cambiarlo, igual que las demás variables del hook.
- Los comandos se ejecutan con `bash -c` desde la raíz del repo y sin las credenciales de GitHub, como el revisor.
- `[review] semgrep` vale `true` por defecto.
- Este repo no tiene la clave en su `.harness-config.toml`. Si se quiere, la pone la persona en `main`, porque es un fichero de control (D-0054).

## Tareas

Un fichero por tarea en `tasks/`, cada una con su rama y su PR. Cuáles están listas: el tablero de `task-done` (`scripts/board.py`). No se listan aquí: los ficheros de tareas son la única fuente.
