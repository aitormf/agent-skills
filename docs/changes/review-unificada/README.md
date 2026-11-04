---
status: open
issue: null
---
# Review local más barata: un reviewer con pasadas condicionales y tareas atómicas

**Problema:** `review-pr` se usa en local, con Codex, como revisión final antes de abrir la PR (no en CI). En los tiers 1–2 lanza tres personas y el verifier: cuatro contextos que leen el mismo diff, cargan sus instrucciones y escriben los mismos hallazgos varias veces (persona, verifier, informe). Gasta muchos tokens y, en diffs pequeños, `security-auditor` y `test-engineer` aportan poco sobre un `code-reviewer` que ya mira seguridad y tests.

**Plazo máximo:** unos 2–3 días de trabajo de agente, repartidos en tareas de menos de 200 líneas.

**Fuera de alcance:** el workflow de CI y el bloque JSON de `--inline`; borrar personas (siguen para el fan-out); cambiar los tiers de riesgo; bloquear mecánicamente una tarea grande (sigue siendo un aviso, D-0037); elegir el modelo en el código del kit (solo se documenta).

## Mapa de ejemplos

```
Rule R1: el tamaño de un diff para la review son las líneas añadidas + borradas, tests incluidos; no cuentan lockfiles, ficheros generados ni snapshots (D-0045)
  E1: 120 líneas de código + 70 de tests → 190, pequeño
  E2: 150 de código + 60 de tests → 210, grande
  E3: exactamente 200 → pequeño (el límite es "como mucho 200")
  E4: 30 de código + 900 de package-lock.json → 30, pequeño
  E5: un fichero en adapters/ marcado linguist-generated en .gitattributes + 40 de código → 40
  E6: un binario (numstat "-") → cuenta 0
  E34: una rama añade un .gitattributes que marca *.py como generado y 900 líneas de .py → cuentan las 900 líneas, grande: los atributos se leen de la base, no de la rama
  E35: el .gitattributes de la base marca adapters/ como generado y la rama cambia adapters/ → no cuenta, aunque la rama quite la marca

Rule R2: review-prepush y review-pr eligen los revisores por el tamaño del diff (D-0045)
  E7: review-prepush, diff de 190 → code-reviewer unificado + finding-verifier (2 subagentes)
  E8: review-prepush, diff de 210 → fan-out completo (3 personas + verifier) y aviso "pasa de 200 líneas (D-0044)"
  E9: review-prepush --deep, diff de 50 → fan-out completo
  E10: review-pr, diff de 190, tier 2 → code-reviewer unificado con pasada de seguridad obligatoria + verifier; sin security-auditor
  E11: review-pr, diff de 210, tier 1 → fan-out completo, como hoy
  E12: review-pr, tier 0 → solo code-reviewer, como hoy, sea cual sea el tamaño

Rule R3: el reviewer unificado hace siempre la pasada base (corrección, llamadores, decisiones, tarea) y la de tests (§5), y activa las demás por lo que ve en el diff; declara cuáles hizo y por qué
  E13: el diff lee un path de la query (B3 del sandbox) → pasada de seguridad con security-checklist.md; el informe dice "Passes: base, tests, security (file path from request input)"
  E14: el diff solo cambia el texto de un mensaje de error → "Passes: base, tests"
  E15: el diff añade una consulta dentro de un bucle → pasada de rendimiento con performance-checklist.md
  E16: el diff toca un lockfile o una ruta de alto riesgo de AGENTS.md → pasada de seguridad aunque no haya entrada externa

Rule R4: la salida de los subagentes es compacta: no se reescribe lo que otro ya escribió
  E17: persona en el fan-out → solo hallazgos en formato §3, sin resumen ni "what's done well"
  E18: reviewer unificado → hallazgos + un "what's done well"
  E19: finding-verifier → una línea por ID: CONFIRMED | REFUTED <motivo> | UNCERTAIN <qué lo confirmaría>, más el ranking de Optional/Nits; sin repetir el hallazgo

Rule R5: una tarea es atómica: un solo propósito, un solo cambio, y como mucho 200 líneas de diff con los tests (D-0044)
  E20: tarea estimada en 250 líneas con tests → idea-to-change / plan-to-tasks la parten
  E21: "validar el email y paginar el listado" → dos tareas (la frase lleva "y")
  E22: un solo comportamiento, 180 líneas con tests → una tarea
  E23: diff de 230 en la review → Optional con el recuento (D-0037), y además fan-out por R2
  E24: implement ve que el diff pasa de 200 → para y lo informa, como hoy con 150

Rule R6: cada subagente carga solo lo que usa, sin perder criterio: code-reviewer no precarga code-review-and-quality pero lleva su criterio condensado; el formato del informe final solo lo lee la sesión principal; las personas no llevan plantillas que contradigan §3 (D-0045)
  E25: el diff añade un helper casi igual a uno que ya existe (B7 del sandbox) → Required, y el Fix nombra el helper existente
  E26: un refactor mueve las mismas ramas a otro fichero sin quitar ninguna (B8 del sandbox) → Optional con un remedio con nombre ("collapse duplicate branches", "explicit dispatcher"…)
  E27: el diff deja una función sin llamadores (B9 del sandbox) → hallazgo de código muerto que nombra la función
  E28: review con --deep → code-reviewer lee además code-review-and-quality completa
  E29: una persona del fan-out → no carga los layouts §4 ni el JSON §4.3; la sesión principal sí

Rule R7: los subagentes de la review arrancan sin el historial de la sesión principal; lo que necesitan va en su encargo (D-0046)
  E30: review-prepush o review-pr en Codex lanza una persona → spawn_agent con fork_turns "none"
  E31: el encargo de esa persona lleva cómo leer el cambio, los resultados de la verificación y los límites, sin dar por hecho que vio algo de la sesión principal

Rule R9: en Claude Code, el modelo no puede editar .gitattributes
  E36: los permisos de la plantilla de guardrails y los de este repo deniegan Edit(./.gitattributes)

Rule R8: la sesión principal solo lee lo que usa
  E32: review-prepush o review-pr lanza una persona → no lee su definición en .codex/agents/ ni en agents/; la herramienta la carga
  E33: review-pr sin carpeta de cambio → no lee task-done ni review-prepush
```

**Pasos sin ejemplos:**

- S1: medición base en `tests/review-sandbox/` con Codex: tokens por agente y hallazgos contra `EXPECTED.md` de `review-pr` y `review-prepush` actuales, 3 ejecuciones de cada → resultados en `docs/review/medicion-review.md`.
- S2: documentar cómo elegir el modelo de los subagentes en Codex por llamada → `docs/review/README.md`.
- S0: el sandbox gana tres casos plantados del criterio que hoy viene de code-review-and-quality (B7 helper duplicado, B8 refactor que solo mueve complejidad, B9 código muerto), con sus filas en `EXPECTED.md`, antes de la medición base.
- S4: repetir la medición base con las personas del sandbox, porque T1 midió las copias globales de `~/.codex/agents/` → `docs/review/medicion-review.md`; una ejecución cuyas personas no sean las del sandbox se marca como inválida.
- S5: repetir la base con esfuerzo `medium`, que es el de uso real: `gpt-6.1-terra` tiene `low` por defecto y T17 midió con él. Se mide la review anterior a T15 → `docs/review/medicion-review.md`.
- S3: repetir la medición con el reviewer unificado y comparar con S5 → misma página; si detecta menos B1–B6 de forma consistente, se dice y se refuerzan los disparadores antes de cerrar. B7–B9 cuentan como posible mejora, porque la base casi nunca los detecta; por eso la medición no cubre el riesgo de T11.

## Supuestos

- "Generado" es lo que `.gitattributes` marca como `linguist-generated`; los lockfiles se reconocen por nombre (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `uv.lock`, `poetry.lock`, `Cargo.lock`, `go.sum`, `Gemfile.lock`, `composer.lock`) y los snapshots por `__snapshots__/` o `*.snap`. Este repo marca `adapters/` como generado.
- El tamaño lo calcula un script (`skills/review-context/scripts/diff_size.py`), no el modelo: es determinista y se prueba en `check.sh`.
- `review-prepush` no necesita calcular tiers: la pasada de seguridad se dispara por la lista de áreas sensibles de tier 2, que es la misma.
- Los ejemplos de R2–R5 son comportamiento de prompts: su test en `check.sh` comprueba que el texto de la skill o el agente dice la regla (como el check "test criterion"). Lo que de verdad hacen se mide en S1/S3.
- `review-report` ronda el tope de 12.500 caracteres: la salida compacta va en el texto de las personas y del verifier; si `review-report` crece, se recorta en la misma tarea.
- El criterio condensado de `code-reviewer` sale de un inventario sección por sección de `code-review-and-quality`: cada sección va al agente, a `review-report`, a una pasada, o se descarta con su motivo; el inventario va en la PR de T11.
- El ahorro se compara en entrada total y en entrada sin caché, porque no sabemos cómo cuenta el plan de Codex la entrada en caché.
- Sin `AGENTS.md` en este repo, la verificación de cada tarea es `scripts/check.sh`, como en las fases de v3.

## Tareas

Un fichero por tarea en `tasks/`, cada una con su rama y su PR. Cuáles están listas: el tablero de `task-done`
(`scripts/board.py`). No se listan aquí: los ficheros de tarea son la única fuente.
