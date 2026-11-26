---
status: open
issue: null
---

# debtector aporta a la review el acoplamiento y la complejidad que añade la rama

**Problema:** la review de un push (`review-prepush`, por el hook `harness-review`) o de una PR (`review-pr`) solo tiene una fuente determinista además de la verificación: Semgrep, que mira seguridad línea a línea. Nada le dice al revisor que la rama crea un ciclo de imports, un god module, una violación del principio de dependencias estables o una función mucho más compleja. Es justo el acoplamiento oculto que los agentes generan más deprisa, y el revisor solo lo ve si se fija en el grafo a mano, cosa que casi nunca hace. A quien ya usa debtector en su repo le importa que la review lo use sin tener que configurar nada más que una clave.

**Plazo máximo:** alrededor de 1 día de trabajo de agente, en 3 tareas.

**Fuera de alcance:**

- Instalar debtector, ni con `uvx` ni con `pip`, ni descargar nada: solo se usa si ya está en el `PATH`.
- Que debtector bloquee el push por sí solo. Su gate en CI es el job de su propia GitHub Action, no la review (D-0063).
- `debtector baseline status`: compara con la deuda acumulada y no con lo que añade la rama.
- Añadir la clave a la plantilla de `setup-guardrails-python`.
- Cambios en debtector.
- Traducir al inglés los mensajes en español que ya tienen `verify.py`, `reviewer.py` y `gate.py` (y lo que `scripts/check.sh` espera de ellos). Es otro cambio.

## Mapa de ejemplos

```
Rule R1: review-context/scripts/debtector_diff.py <base> lista lo que la rama añade según `debtector --json diff --base <base>`, un hallazgo por línea, y cierra con un recuento
  E1: la rama crea el ciclo a.py → b.py → a.py y sube `pkg/x.py::f` de 8 a 15 (high) → «cycle a.py → b.py → a.py», «complexity pkg/x.py::f 8 → 15 (high)» y «debtector: 2 new or worse; 0 resolved»
  E2: la rama no cambia nada de arquitectura → solo «debtector: 0 new or worse; 0 resolved»; exit 0
  E3: debtector sale con 1 (algo nuevo tiene severidad error en debtector.toml) → las mismas líneas y el recuento termina en «; would block its CI job»; exit 0
  E4: debtector no está en el PATH → «debtector_diff: debtector is not on PATH» por stderr; exit 2
  E5: debtector sale con 2 (ref inexistente, índice no comparable) → su mensaje de error por stderr; exit 2
  E6: el resultado trae `skipped` (clon superficial) → una línea «skipped <section>: <reason>» antes del recuento
  E7: la rama resuelve un ciclo y un god module y no añade nada → «debtector: 0 new or worse; 2 resolved»
Rule R2: el hook ejecuta debtector solo si la rama base tiene [review] debtector = true en .harness-config.toml; debtector nunca bloquea el push (→ D-0063)
  E8: la base tiene debtector = true → verification.md tiene una sección «## debtector (architecture)» con la salida de debtector_diff.py
  E9: sin la clave en la base → no se ejecuta y el fichero no tiene la sección
  E10: la rama pone debtector = true y la base no la tiene → no se ejecuta (se lee de la base, D-0054)
  E11: la clave vale "yes" → «review-kit: invalid .harness-config.toml on the base branch: [review] debtector must be true or false»; exit 2
  E12: la clave vale true y debtector no está instalado → «debtector: not available (…)» en el fichero; el push sigue
  E13: debtector_diff.py dice «would block its CI job» → el push sigue y el revisor recibe la salida igual
Rule R3: la review trata la salida de debtector como hallazgos candidatos con Source: debtector, como los de Semgrep
  E14: review-prepush con REVIEW_KIT_VERIFICATION y una sección de debtector con un ciclo nuevo → el ciclo es candidato, pasa por las reglas de precisión y por el verifier, y si sobrevive sale con «Source: debtector»; la última línea de la sección se cita en Verification
  E15: review-prepush o review-pr sin el hook y con debtector = true en la base → ejecuta debtector_diff.py según review-context §2.7; exit 2 → «debtector not available — skipped»
  E16: sin la clave en la base → la review no ejecuta debtector ni lo menciona
Question: ¿se activa con una clave o en cuanto el repo tiene debtector.toml? ¿bloquea? → D-0063 (clave opt-in; nunca bloquea)
```

## Supuestos

- El script llama a `debtector --json diff --base <base>` desde la raíz del repo, con el mismo tiempo límite que los comandos del hook (600 s): indexa la base en un worktree temporal y puede tardar.
- `debtector diff --base` reescribe `.debtector/index.db`, que debtector ignora en git, y crea y borra un worktree temporal. No cambia nada versionado, así que review-context §2 lo admite como excepción explícita, igual que el fichero de resultados del hook.
- Todo el código nuevo va en inglés, también los mensajes, docstrings y comentarios que se añadan a `verify.py`, aunque ese fichero ya tenga mensajes en español.
- Los ítems que cuenta como «new or worse» son las claves `new_*`, `instability_regressions`, `worsened_functions` y `worsened_hotspots`; como «resolved», las `resolved_*` e `improved_functions`. Las mejoras no se listan, solo se cuentan.
- Este repo no tiene la clave en su `.harness-config.toml` (no es un proyecto Python con debtector). Si se quiere, la pone la persona en `main`, porque es un fichero de control (D-0054).

## Tareas

Un fichero por tarea en `tasks/`, cada una con su rama y su PR. Cuáles están listas: el tablero de `task-done` (`scripts/board.py`). No se listan aquí: los ficheros de tareas son la única fuente.
