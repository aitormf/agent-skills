# Medición base de la review

Cuántos tokens gastan y qué encuentran `review-pr` y `review-prepush` **tal como están hoy**, ejecutadas con Codex sobre el sandbox de `tests/review-sandbox/`. Es la referencia con la que comparar el reviewer unificado (cambio `review-unificada`). Las secciones de T17, T20 y T1 no sacan conclusiones sobre el reviewer unificado; la de T10 (la primera) lo compara con ellas.

Hay cuatro mediciones, cada una válida para su esfuerzo. **La de T20** (`medium`, la primera sección) es la referencia para T10 en `review-prepush`; en `review-pr` no tiene ejecuciones válidas. **La de T17** (`low`) sigue siendo válida para ese esfuerzo. La de T1, más abajo, quedó marcada como no comparable: los subagentes usaron las personas globales, no las del sandbox.

## Review cruzada con el sandbox (T9, cambio `8-review-cruzada`)

Mide la review que lanza el hook del kit (`harness-review.sh`) cuando empuja un agente Claude (`CLAUDECODE=1`): el hook elige `codex`, con `gpt-6.1-terra` y `medium`, y la skill y las personas del kit (S2). Kit `844dda6` (`origin/main` con T1 a T8 y T10, más la corrección del prompt de codex), `codex-cli 0.167.0`, 2026-11-13. No sustituye a las secciones de abajo: el prompt es otro (apunta al `SKILL.md` del kit).

**Primer intento (descartado).** Con el prompt de `255e4ea`, que decía «no uses las skills ni los subagentes del proyecto», las tres ejecuciones no lanzaron ningún subagente: la sesión principal hizo sola la review (entrada media 140.076, 47 s, B1–B6 6, 5 y 6 de 6) y los informes citaban un `code-reviewer` y un verifier que no existieron. Se corrigió el prompt (pide lanzar `code-reviewer` y, si hay hallazgos, `finding-verifier`) y se repitió todo; lo que sigue es la repetición.

**Resumen.** **No se cumple el criterio**: las tres ejecuciones dan **5 de 6** (B1, B2, B3, B4 y B6; falta B5, el TODO sin ticket, un Nit, en las tres), ningún señuelo sobrevive y los subagentes sí se lanzaron (`code-reviewer` y `finding-verifier` en las tres, con la persona cargada). Frente a la base de T20 (6,0 de 6): un hallazgo menos, el mismo que perdía el unificado en T10. Gasta algo menos: entrada media 501.326 frente a 650.935 (-23%), sin caché 41.294 frente a 64.055 (-36%), 120 s frente a 137 s. Por eso T9 **no se marca como hecha**.

### Cómo se midió

| | |
|---|---|
| Sandbox | `tests/review-sandbox/build.sh --codex`; `repo/` con un remoto local vacío como `origin` (`main` subido con `--no-verify`) y `origin/HEAD` -> `main`. Sin cambios en los scripts del sandbox |
| Ejecución | `git push -u origin feature/orders-pagination-invoices` con `CLAUDECODE=1 REVIEW_KIT_RERUN=1`, por el hook `.git/hooks/pre-push` que instala `build.sh` (llama a `harness-review.sh` del kit). El hook dijo `autor: claude`, la puerta no comprueba nada (la rama no nombra una tarea) y eligió `codex` |
| Comando de codex | el que construye el hook, tal cual (`exec -s read-only -m gpt-6.1-terra -c model_reasoning_effort="medium"`, las cuatro personas del kit con `-c agents.<rol>.*` y el prompt). Para medir, un envoltorio `codex` en el `PATH` añade `--json` y `-o`: guarda los eventos y devuelve al hook el último mensaje (`docs/review/medicion-review/t9/codex-shim.sh`, `run.sh`) |
| Tokens y subagentes | `summarize.py` sobre `events.jsonl` y los registros de sesión de Codex; `problems` vacío en las tres (modelo y esfuerzo correctos en todos los agentes) y persona cargada en los dos subagentes de cada ejecución (`sandbox_match`: las copias del sandbox y las del kit son iguales) |
| Duración | reloj del `git push` completo (incluye la puerta y el envoltorio) |
| Resultados | `report.md` y `summary.json` de cada ejecución en `docs/review/medicion-review/t9/run-<n>/` (sin `events.jsonl`; ruta del sandbox sustituida por `repo/`) |

Límites: n = 3; el envoltorio de medición no está en el hook real; el sandbox no tiene `AGENTS.md`. Los tres empujes terminaron en `rc=1` (el hook bloquea por Critical confirmados, como se espera). Los informes de run-1 y run-2 están en español y el de run-3 en inglés, sin que el hook lo pida.

### Tokens

Entrada / en caché / sin caché / salida / razonamiento (llamadas a la API entre paréntesis). `code-reviewer` y `finding-verifier` lanzados: sí y sí en las tres.

| Agente | run-1 | run-2 | run-3 |
|---|---|---|---|
| sesión principal | 304.633 / 278.528 / 26.105 / 3.375 / 40 (10) | 344.873 / 330.112 / 14.761 / 3.396 / 24 (11) | 258.574 / 246.144 / 12.430 / 3.105 / 26 (9) |
| code-reviewer | 129.996 / 108.160 / 21.836 / 1.360 / 82 (5) | 130.149 / 121.472 / 8.677 / 1.585 / 90 (5) | 130.209 / 121.600 / 8.609 / 1.508 / 63 (5) |
| finding-verifier | 78.111 / 62.592 / 15.519 / 795 / 90 (3) | 77.775 / 69.760 / 8.015 / 792 / 85 (3) | 49.657 / 41.728 / 7.929 / 1.123 / 41 (2) |
| **Total** | **512.740 / 449.280 / 63.460 / 5.530 / 212** | **552.797 / 521.344 / 31.453 / 5.773 / 199** | **438.440 / 409.472 / 28.968 / 5.736 / 130** |
| Duración (s) | 114 | 124 | 121 |
| Veredicto | `BLOCK critical=3 required=3` | `BLOCK critical=3 required=4` | `BLOCK critical=3 required=3` |

| | Entrada | En caché | Sin caché | Salida | Razonamiento | Duración (s) | B1–B6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Media de T9** | **501.326** | **460.032** | **41.294** | **5.680** | **180** | **120** | **5,0** |
| T20 (`medium`, base) | 650.935 | 586.880 | 64.055 | 6.497 | 252 | 137 | 6,0 |
| T10 (unificado) | 597.210 | 509.397 | 87.813 | 6.167 | 256 | 123 | 5,3 |

### Qué encuentra

Puntuado a mano contra `tests/review-sandbox/EXPECTED.md` con el criterio de T17/T20.

| | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 | D1 | D2 | D3 | B1–B6 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| run-1 | sí | sí | sí | sí | no | sí | no | no | no | no | no | no | 5/6 |
| run-2 | sí | sí | sí | sí | no | sí | no | no | no | no | no | no | 5/6 |
| run-3 | sí | sí | sí | sí | no | sí | no | no | no | no | no | no | 5/6 |

B1 es C2, B3 es C1 y B6 es C3 en las tres; B4 es R3 (run-1) y R1 (run-2 y run-3); B2 es R1 (run-1) y R2 (run-2 y run-3), todos diciendo que el test acepta resultados incorrectos. Ni el TODO de `src/invoices.js` ni B7, B8 y B9 aparecen en ninguna (ni siquiera como Nit); el verifier refutó 0 hallazgos en las tres. Fuera de `EXPECTED.md`: falta de test de `/invoices` (discutible, las tres); run-2 añade la falta de test del nuevo orden.

### Lo que queda abierto

- **B5 se pierde siempre** (3 de 3), como en T10: un Nit sin ticket. Quizá la regla «Max Nits» de la skill o el recorte del prompt lo explique; no se ha investigado, y reforzarlo es otra tarea.
- **Ruta de Claude** (revisor `claude` con `--plugin-dir <kit>` frente a un plugin `harness` instalado): no se ejecutó ni se comprobó que `--plugin-dir` tenga prioridad sobre un `harness` instalado.

### Diagnóstico de B5: la misma review sin el hook

Una sola ejecución del método de la base (T20), sin el hook: `build.sh --codex` y `measure.sh review-prepush 1` con `KIT` en un worktree limpio de `origin/main` (`255e4ea`), `gpt-6.1-terra` y `medium`, `codex-cli 0.167.0`. Pregunta: ¿se pierde B5 por el hook y su prompt, o por la evolución del kit desde T20?

| | B1–B6 | Señuelos | Subagentes | Entrada / en caché / sin caché | Salida | Duración |
|---|---|---|---|---|---:|---:|
| `measure.sh` sin hook | 5/6 (falta B5) | ninguno | `code-reviewer` y `finding-verifier` | 546.053 / 474.624 / 71.429 | 5.262 | 112 s |

Por agente (entrada / salida): sesión principal 337.281 / 3.135 (11 llamadas), `code-reviewer` 131.020 / 1.474 (5), `finding-verifier` 77.752 / 653 (3). `problems` vacío. Hallazgos: C1 (B3), C2 (B1), C3 (B6), R1 (B2), R2 (falta de test de `/invoices`), R3 (B4); ni el TODO ni B7 a B9.

**Lectura (n = 1, no es concluyente).** La pérdida de B5 **no es del hook ni del prompt de la review cruzada**: aparece también con el método de la base. El brief que recibe el `code-reviewer` sigue pidiendo «new TODO/FIXME without a ticket» (`skills/review-prepush/SKILL.md`, paso 3, punto 4) y ese punto es igual que en `20c832c`; `agents/code-reviewer.md` no menciona TODO ni lo mencionaba. Lo que sí cambió desde la base en esas skills y personas: T15 (los subagentes arrancan sin el historial), T16 (la sesión principal solo lee lo que usa), T12 y T13 (formato del informe y plantillas de salida fuera de las personas) y T21 (`agent_type`); T3, T4 y T11 se revirtieron. La medición de T10 (kit `28b00c5`, antes del hook) ya perdía B5 en 4 de 9 ejecuciones y T20 (kit `20c832c`) lo encontraba en 3 de 3, así que lo más verosímil es la evolución del kit entre T20 y T10, y no la review cruzada. Con una ejecución no se puede atribuir a un commit concreto; para eso haría falta medir `20c832c` frente a `255e4ea` con varias repeticiones.

## Reviewer unificado frente a la base (T10)

Mide el kit de `origin/main` tras T4, T5, T11, T12, T13, T15, T16 y T21 (commit `28b00c5`), con Codex, `gpt-6.1-terra` y esfuerzo `medium` (2026-11-04, `codex-cli 0.165.0`). Es la medición de T10: comprueba si el reviewer unificado gasta menos sin perder hallazgos (S3).

**Resumen.** Las 12 ejecuciones son válidas (ninguna se descartó) y ninguna lanzó el fan-out: el diff del sandbox es de 119 líneas y todas usaron `code-reviewer` más `finding-verifier`, con la persona del sandbox cargada. **`review-pr` baja mucho** la entrada total (586.444 frente a 1.081.680 de T17, -46%) y algo la entrada sin caché (-8%). **`review-prepush` apenas cambia** la entrada total (597.210 frente a 650.935 de T20, -8%) y **sube** la entrada sin caché (87.813 frente a 64.055, +37%), con tres ejecuciones por grupo y una variación entre ejecuciones del mismo orden que la diferencia. **El unificado detecta menos B1–B6 que la base, de forma consistente en `review-prepush`** (5,3 de 6 frente a 6,0) y algo menos en `review-pr` (4,0 frente a 4,3); ver «Qué encuentra»: pierde B5 (el TODO, Nit) y B2 (el test inútil) con frecuencia. No se refuerzan los disparadores aquí, y por la tarea (S3) **el cambio no se da por bueno** hasta que otra tarea los refuerce.

### Cómo se midió

| | |
|---|---|
| Kit | `28b00c5` (`origin/main`), el propio worktree: `tests/review-sandbox/build.sh --codex` y `measure.sh` sin `KIT`. `meta.json` registra `kit_commit: 28b00c5` |
| Modelo y esfuerzo | `-m gpt-6.1-terra -c model_reasoning_effort="medium"` en toda ejecución (valores por defecto de `measure.sh`); `summarize.py` los comprueba en todos los agentes, la sesión principal incluida: `problems` vacío en las 12 |
| Ejecución | `-s read-only`, sin `--dangerously-bypass-*`; nada de `~/.codex` tocado ni credenciales copiadas |
| Ejecuciones | `review-prepush` run-1 a run-3 y `review-pr` run-1 a run-3 con el prompt de T17/T20 (sin `fork_turns`); `review-prepush` run-11 a run-13 con `EXTRA` = «Al lanzar cada subagente con spawn_agent pasa fork_turns: "none".»; run-21 a run-23 con `"all"`. `EXTRA` es una variable nueva de `measure.sh`, que añade ese texto al final del prompt |
| Subagentes | en las 12: 2 (`code-reviewer` y `finding-verifier`), persona del sandbox cargada (`persona.sandbox_match`). Ningún `security-auditor` ni `test-engineer`: nunca hubo fan-out |
| Resultados | `report.md`, `summary.json` y `meta.json` de las 12 en `docs/review/medicion-review/t10/<comando>/run-<n>/`, con la ruta del sandbox sustituida por `repo/` |

Límites: Semgrep sigue sin poder ejecutarse en `read-only` (lo anotan las reviews); la duración es de reloj; n = 3 por grupo, así que las medias son orientativas. La tanda de `fork_turns` se cortó por el límite de tiempo del lanzador (no del modelo) durante `run-22`; run-22 se repitió entero con `START=22` junto con run-23. No hay ejecuciones fallidas ni inválidas.

### Ejecuciones inválidas

Ninguna. Las 12 pasan `summarize.py` sin problemas (modelo, esfuerzo y persona). Sin fallos de capacidad.

### Tokens por agente (medias de 3 ejecuciones)

Entrada total / entrada sin caché / salida / razonamiento. Los números de la base salen de los `summary.json` de T17 y T20 (`docs/review/medicion-review/t17`, `t20`).

#### `review-prepush`, unificado (prompt sin `fork_turns`) frente a la base `medium` (T20)

En las tres ejecuciones el modelo pasó `fork_turns: "none"` por sí solo, como dice la skill (la base mezclaba `none` y no indicado).

| Agente | T20 (`medium`, antes de T15) | T10 (`medium`, `28b00c5`) |
|---|---|---|
| sesión principal | 398.661 / 33.179 / 3.999 / 129 | 351.340 / 29.463 / 3.556 / 130 |
| code-reviewer | 142.039 / 17.495 / 1.582 / 76 | 161.392 / 35.525 / 1.546 / 78 |
| finding-verifier | 110.235 / 13.381 / 916 / 47 | 84.478 / 22.825 / 1.066 / 48 |
| **Total** | **650.935 / 64.055 / 6.497 / 252** | **597.210 / 87.813 / 6.167 / 256** |
| Duración (s) | 137 | 123 |
| Bugs de 9 (B1–B6 de 6) | 6,3 (6,0) | 6,0 (5,3) |

#### `review-pr`, unificado frente a la base `low` (T17)

**Esta comparación mezcla dos esfuerzos**: T17 midió con `low` y T10 con `medium`, porque T20 no tiene ninguna ejecución válida de `review-pr` (con `medium` el modelo no pasó `agent_type`). Se ha de leer como orientativa: parte de la diferencia puede ser del esfuerzo, no del cambio. En T17, `review-pr` lanzaba cuatro subagentes; ahora, dos.

| Agente | T17 (`low`, 4 subagentes) | T10 (`medium`, 2 subagentes) |
|---|---|---|
| sesión principal | 571.927 / 34.369 / 3.252 / 95 | 343.125 / 32.426 / 2.578 / 142 |
| code-reviewer | 149.364 / 10.654 / 792 / 18 | 168.929 / 28.726 / 1.503 / 97 |
| security-auditor | 104.941 / 12.355 / 399 / 29 | no lanzado |
| test-engineer | 120.754 / 10.674 / 541 / 30 | no lanzado |
| finding-verifier | 134.694 / 11.771 / 796 / 37 | 74.390 / 12.182 / 967 / 51 |
| **Total** | **1.081.680 / 79.824 / 5.780 / 209** | **586.444 / 73.335 / 5.048 / 290** |
| Duración (s) | 91 | 93 |
| Bugs de 9 (B1–B6 de 6) | 4,7 (4,3) | 4,0 (4,0) |

### Efecto de `fork_turns` (T15), solo `review-prepush`

Mismo commit, mismo esfuerzo; el prompt pide `none` o `all` para los dos subagentes (media de 3):

| `fork_turns` | Entrada total | Sin caché | Entrada de la sesión principal / sin caché | Entrada de la 1.ª llamada de cada subagente | Salida | Razonamiento | Duración (s) | Bugs de 9 |
|---|---:|---:|---|---|---:|---:|---:|---:|
| `none` (run-11 a 13) | 578.875 | 52.283 | 338.373 / 19.610 | ~22.400 y ~21.600 | 7.268 | 269 | 138 | 6,3 |
| `all` (run-21 a 23) | 508.160 | 42.966 | 295.502 / 14.328 | ~37.100 y ~38.700 | 5.647 | 189 | 120 | 5,0 |

Con `all` la primera llamada de cada subagente es ~15.000 tokens mayor (hereda el historial), pero la entrada total y la sin caché de la ejecución salen más bajas: los subagentes hacen menos llamadas (3 y 2 frente a 5 y 3-4) y la sesión principal, menos. Con n = 3 y esta variación (la entrada sin caché con `none` va de 37.310 a 75.533) **no se puede decir que `all` gaste menos**: es un solo diff de 119 líneas y un modelo que ya entiende la tarea desde el historial. Además, con `all` los hallazgos fueron un poco peores (B2 solo en 1 de 3; ver abajo), y T15 pide `none` para que las personas revisen con contexto fresco e independiente. No cambia la recomendación de T15.

### Qué encuentra

Puntuado a mano, leyendo cada `report.md` contra `tests/review-sandbox/EXPECTED.md` con el criterio de T17: B2 exige decir que el test actual no comprueba el contenido o que pasa con el bug (pedir contenido exacto solo en el arreglo de B1 es «parcial» y no cuenta); B8 pide un remedio con nombre.

| | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 | D1 | D2 | D3 | Bugs |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `review-prepush` run-1 | sí | sí | sí | sí | sí | sí | no | no | sí | no | no | no | 7/9 |
| `review-prepush` run-2 | sí | sí | sí | sí | no | sí | no | no | no | no | no | no | 5/9 |
| `review-prepush` run-3 | sí | sí | sí | sí | no | sí | no | no | sí | no | no | no | 6/9 |
| `review-prepush` run-11 (`none`) | sí | sí | sí | sí | sí | sí | no | no | sí | no | no | no | 7/9 |
| `review-prepush` run-12 (`none`) | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| `review-prepush` run-13 (`none`) | sí | sí | sí | sí | no | sí | no | no | sí | no | no | no | 6/9 |
| `review-prepush` run-21 (`all`) | sí | parcial | sí | sí | sí | sí | no | no | no | no | no | no | 5/9 |
| `review-prepush` run-22 (`all`) | sí | parcial | sí | sí | sí | sí | no | no | no | no | no | no | 5/9 |
| `review-prepush` run-23 (`all`) | sí | sí | sí | sí | no | sí | no | no | no | no | no | no | 5/9 |
| `review-pr` run-1 | sí | parcial | sí | sí | no | sí | no | no | no | no | no | no | 4/9 |
| `review-pr` run-2 | sí | parcial | sí | sí | no | sí | no | no | no | no | no | no | 4/9 |
| `review-pr` run-3 | sí | parcial | sí | sí | no | sí | no | no | no | no | no | no | 4/9 |

Medias: `review-prepush` sin `fork_turns` indicado en el prompt 6,0 (T20: 6,3; T17: 6,0); con `none` 6,3; con `all` 5,0; `review-pr` 4,0 (T17: 4,7). B7 (duplicación con `sumTotals`), B8 y B9 casi no aparecen: B7 y B8 en ninguna de las 12; B9 (código muerto `latestFirst`) en 4 de las 9 de `review-prepush`, que la base no encontraba. Ningún señuelo sobrevive en ninguna.

**El unificado detecta menos B1–B6 que la base en `review-prepush`, de forma consistente.** Contando solo B1–B6: 6, 5, 5 sin `fork_turns` en el prompt, 6, 6, 5 con `none` y 5, 5, 5 con `all` (media de las 9: 5,3), frente a 6, 6, 6 en T20 y también en T17: 6 de las 9 ejecuciones quedan por debajo y ninguna supera la base. Siempre aparecen B1, B3, B4 y B6; lo que se pierde es B5 (el TODO sin ticket, un Nit: presente en 5 de las 9, y con `all` en 2 de 3) y B2 (el test inútil: «parcial» en 2 de 3 con `all`). En `review-pr` la diferencia es menor: 4, 4, 4 frente a 4, 5, 4 de T17 (B1–B6 con el criterio de T17), y B5 faltaba también en T17; lo que ya no aparece es B7 (1 de 3 en T17) y B2 es «parcial» en las tres (en T17, en dos). En `review-pr` run-1 el verifier refutó un hallazgo de cobertura de tests por duplicar C1–C3. Hallazgos fuera de `EXPECTED.md`: falta de test de `/invoices` (discutible) y, en 4 de 12, que la factura incluida no es un PDF válido (Critical). Las nueve de `review-prepush` acaban en BLOCK y las de `review-pr` en `CHANGES NEEDED` (tier 2).

**No se da el cambio por bueno**: B2 y B5 (y, en `review-pr`, B7) se pierden con frecuencia; reforzar los disparadores es otra tarea; aquí no se tocan.

## Base con esfuerzo `medium` (T20)

Repite la medición de T17 fijando el esfuerzo de razonamiento en `medium`, el que se usa de verdad, y con la review de **antes de T15**. **T17 sigue siendo válida para esfuerzo `low`** (el que `gpt-6.1-terra` trae por defecto en el catálogo): sus cifras no se tocan y no son comparables a las de esta sección sin decir el esfuerzo. Este apartado no saca conclusiones sobre el reviewer unificado.

**Resultado en una línea:** `review-prepush` tiene base válida con `medium` (3 ejecuciones). `review-pr` **no la tiene**: sus 8 ejecuciones completas son inválidas, porque con `medium` el modelo lanzó los subagentes sin `agent_type` y no cargaron ninguna persona (ver «Ejecuciones inválidas y fallidas»). Para T10, `review-pr` sigue sin referencia con `medium`.

### Cómo se midió

| | |
|---|---|
| Fecha | 2026-11-04 |
| Codex | `codex-cli 0.165.0` |
| Modelo y esfuerzo | `gpt-6.1-terra` con `-m`, y esfuerzo `medium` con `-c model_reasoning_effort="medium"`, ambos explícitos en toda ejecución y registrados en cada `meta.json` (`model`, `effort`) |
| Commit del kit | `20c832c` (anterior a T15). Skills, personas y casos B1–B9 salen de un `git worktree` temporal en ese commit, borrado al terminar, con `KIT=<worktree> tests/review-sandbox/build.sh --codex` y `KIT=<worktree> tests/review-sandbox/measure.sh`. Se comprobó que `tests/review-sandbox/layers/` y `EXPECTED.md` de `20c832c` son idénticos a los de la rama, y que las skills y personas del sandbox son las de ese commit. `meta.json` registra `kit_commit: 20c832c` |
| Scripts | los de esta rama (`measure.sh`, `summarize.py`), con la opción `EFFORT` (por defecto `medium`) y `KIT` |
| Ejecución | `-s read-only`, sin `--dangerously-bypass-*`, sin ampliar permisos. No se tocó nada de `~/.codex` ni se copió ninguna credencial. Sin `fork_turns` en el prompt |
| Prompts | los de T17, sin cambios |

### Cómo se fijó el esfuerzo y prueba de que los subagentes lo usaron

Con una llamada mínima (sin review) antes de medir: `codex exec -m gpt-6.1-terra -c model_reasoning_effort=medium -s read-only --json "Responde solo: ok"`. El `turn_context` del registro de sesión de la principal dice `model: gpt-6.1-terra`, `effort: medium` (T17 mostraba `low` en los subagentes y vacío en la principal). Después, una segunda llamada mínima donde la principal lanza un subagente con `spawn_agent` **sin indicar modelo ni esfuerzo**: el `turn_context` del subagente también dice `gpt-6.1-terra` y `medium`. Es decir, **el subagente hereda el esfuerzo de la sesión**, como dice la descripción de `spawn_agent` («Omit to inherit the parent effort»); no hizo falta tocar `~/.codex` ni el texto de las skills.

`summarize.py` lo comprueba en cada ejecución, no solo en las pruebas: toma el modelo y el esfuerzo esperados de `meta.json` (o de los argumentos 3 y 4) y añade a `problems` cualquier agente, **sesión principal incluida**, cuyo `turn_context` tenga otro modelo u otro esfuerzo, o ninguno. Las 12 ejecuciones con registros pasan esa comprobación (las 9 inválidas lo son solo por las personas).

La comprobación de personas no cambia: el cuerpo completo del `.toml` del sandbox (el de `20c832c`, que `build.sh` instaló en esa ejecución, no `adapters/` de la rama) debe estar en los mensajes `developer` del subagente. En los 6 subagentes de las ejecuciones válidas la persona cargada es la del sandbox. Ahora `code-reviewer` y `finding-verifier` del sandbox coinciden con las de `~/.codex/agents/` (en T17 diferían), así que esta comprobación **ya no distingue** la copia del sandbox de la global: prueba que se cargó la persona medida, no que no fuera la global.

### Límites y condiciones

- Semgrep sigue sin funcionar, por lo mismo que en T17 (sin red y sin directorio temporal escribible en `read-only`); las reviews lo anotan como omitido.
- `fork_turns`: el prompt no lo indica. En `review-prepush` run-4 el modelo usó `none` (primera llamada de ~21.700 tokens de entrada) y en run-1 y run-3 no lo indicó (37.742 a 51.596). Es parte de lo medido.
- La duración es de reloj, de principio a fin de `codex exec`.
- Los registros crudos quedan en `tests/review-sandbox/results/` (ignorado por git). En el repo van `report.md`, `summary.json` y `meta.json` de **todas** las ejecuciones, válidas o no, en `docs/review/medicion-review/t20/<comando>/run-<n>/`, con la ruta del sandbox sustituida por `repo/`. No hay secretos.

### Ejecuciones inválidas y fallidas

Se registran todas; ninguna se omite.

| Ejecución | Exit | Duración (s) | Subagentes | Roles de los subagentes | Entrada | Sin caché | Salida | Razonamiento | Motivo |
|---|---:|---:|---:|---|---:|---:|---:|---:|---|
| `review-prepush` run-2 | 0 | 99 | 2 | `default`, `default` | 643.468 | 70.924 | 5.980 | 221 | inválida: subagentes con `agent_type: default`, sin persona |
| `review-pr` run-1 | 0 | 85 | 4 | sin rol ×4 | 1.214.461 | 67.069 | 5.370 | 244 | inválida: subagentes sin `agent_type`, sin persona |
| `review-pr` run-2 | 0 | 94 | 4 | sin rol ×4 | 997.454 | 59.598 | 5.562 | 382 | ídem |
| `review-pr` run-3 | 0 | 99 | 4 | sin rol ×4 | 1.338.621 | 100.861 | 6.189 | 517 | ídem |
| `review-pr` run-4 | 0 | 90 | 4 | sin rol ×4 | 1.027.413 | 78.933 | 5.559 | 242 | ídem (repetición) |
| `review-pr` run-5 | 0 | 84 | 4 | sin rol ×4 | 1.027.139 | 74.563 | 5.470 | 330 | ídem (repetición) |
| `review-pr` run-6 | 1 | 3 | 0 | — | — | — | — | — | **fallida**: `Selected model is at capacity` (`turn.failed`), sin llamadas a la API |
| `review-pr` run-7 | 0 | 98 | 4 | sin rol ×4 | 1.107.868 | 61.212 | 5.232 | 440 | ídem (repetición) |
| `review-pr` run-8 | 0 | 118 | 4 | sin rol ×4 | 1.053.405 | 75.485 | 6.401 | 602 | ídem (repetición) |
| `review-pr` run-9 | 0 | 86 | 4 | sin rol ×4 | 1.249.973 | 136.245 | 5.275 | 282 | ídem (repetición) |

En las inválidas todos los agentes sí corren con `gpt-6.1-terra` y `medium`; lo que falla es la persona. En `review-pr` run-4 se comprobó que ningún subagente tiene el cuerpo de una persona del sandbox ni en sus mensajes `developer` ni en el prompt que recibió: son agentes genéricos, no personas mal etiquetadas. La skill es la misma en `20c832c` y en `6d9fd8a` (T17: sin diferencias en `skills/`, `agents/` ni `adapters/`), y con `low` los 18 subagentes de T17 cargaron la persona; con `medium` el modelo no pasó `agent_type` en ninguna de las 8 ejecuciones completas de `review-pr` (y en 1 de 4 de `review-prepush`). No se puntuaron a mano: sin persona no es la review que se mide.

**Repeticiones** (todas anotadas): `review-prepush` run-4 repite la inválida run-2. `review-pr` run-4 a run-6 repiten las tres inválidas de run-1 a run-3 (run-6 falló por capacidad del modelo); run-7 a run-9 son un último intento acotado tras ver que 5 de 5 eran inválidas. Total: 9 ejecuciones de `review-pr` (1 fallida, 8 inválidas, 0 válidas) y 4 de `review-prepush` (1 inválida, 3 válidas). No se lanzaron más y los números no se reutilizan.

### Tokens (ejecuciones válidas)

#### `review-prepush`

**run-1** (exit 0, 119 s, 2 subagentes, modelo y esfuerzo en todos los agentes: gpt-6.1-terra / medium, `problems`: vacío)

| Agente | Llamadas | Entrada | En caché | Sin caché | Salida | Razonamiento | `fork_turns` | Entrada de su 1.ª llamada | Persona cargada |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| sesión principal | 9 | 291.821 | 262.400 | 29.421 | 3.653 | 63 | — | — | — |
| code-reviewer | 3 | 119.709 | 112.000 | 7.709 | 1.277 | 42 | no indicado | 37.742 | sandbox |
| finding-verifier | 2 | 84.064 | 76.672 | 7.392 | 569 | 51 | no indicado | 40.112 | sandbox |
| **Total** | 14 | **495.594** | **451.072** | **44.522** | **5.499** | **156** | | | |

**run-3** (exit 0, 142 s, 2 subagentes, modelo y esfuerzo en todos los agentes: gpt-6.1-terra / medium, `problems`: vacío)

| Agente | Llamadas | Entrada | En caché | Sin caché | Salida | Razonamiento | `fork_turns` | Entrada de su 1.ª llamada | Persona cargada |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| sesión principal | 12 | 440.368 | 408.832 | 31.536 | 4.035 | 87 | — | — | — |
| code-reviewer | 2 | 102.569 | 90.496 | 12.073 | 1.239 | 126 | no indicado | 49.391 | sandbox |
| finding-verifier | 3 | 168.453 | 153.344 | 15.109 | 1.690 | 40 | no indicado | 51.596 | sandbox |
| **Total** | 17 | **711.390** | **652.672** | **58.718** | **6.964** | **253** | | | |

**run-4** (exit 0, 149 s, 2 subagentes, modelo y esfuerzo en todos los agentes: gpt-6.1-terra / medium, `problems`: vacío)

| Agente | Llamadas | Entrada | En caché | Sin caché | Salida | Razonamiento | `fork_turns` | Entrada de su 1.ª llamada | Persona cargada |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| sesión principal | 14 | 463.795 | 425.216 | 38.579 | 4.310 | 236 | — | — | — |
| code-reviewer | 7 | 203.838 | 171.136 | 32.702 | 2.230 | 61 | `none` | 21.730 | sandbox |
| finding-verifier | 3 | 78.187 | 60.544 | 17.643 | 488 | 50 | `none` | 21.789 | sandbox |
| **Total** | 24 | **745.820** | **656.896** | **88.924** | **7.028** | **347** | | | |

#### `review-pr`

Sin ejecuciones válidas: no hay tabla ni media. Las cifras de las inválidas están arriba solo como registro.

#### Medias (ejecuciones válidas)

| Comando | Ejecuciones | Subagentes | Duración (s) | Entrada | Entrada en caché | Salida | Razonamiento | Entrada sin caché |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `review-prepush` | 3 | 2 | 137 | 650.935 | 586.880 | 6.497 | 252 | 64.055 |
| `review-pr` | 0 | — | — | — | — | — | — | — |

Las medias son aritméticas sobre 3 ejecuciones; la variación entre ellas es grande (entrada entre 495.594 y 745.820).

### Qué encuentran

Puntuado **a mano**, leyendo cada `report.md` contra `tests/review-sandbox/EXPECTED.md`, con el criterio de T17: un bug cuenta si un hallazgo (o el arreglo de otro) lo señala con su causa; B2 exige señalar que el test no comprueba el contenido de la página; B8 cuenta solo con un remedio con nombre; un señuelo aparece si sobrevive como hallazgo.

| | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 | D1 | D2 | D3 | Bugs detectados |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `review-prepush` run-1 | sí | sí | sí | sí | sí | sí | sí | no | no | no | no | no | 7/9 |
| `review-prepush` run-3 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| `review-prepush` run-4 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| **`review-prepush`, de 3** | 3 | 3 | 3 | 3 | 3 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 6,3 de media |
| `review-pr` | sin ejecuciones válidas | | | | | | | | | | | | |

Notas: las tres terminan en BLOCK con 3 o 4 Critical. B2 aparece como hallazgo propio en las tres («el offset incorrecto pasa el test»). B5 sale como Nit en run-1 y run-3 y como Optional en run-4. B7 solo en run-1 (R4, `pageTotal` frente a `sumTotals`, «sin introducir una dependencia circular»). B8 y B9 no aparecen en ninguna. Ningún señuelo sobrevive. Fuera de `EXPECTED.md`: falta de test de `/invoices` (lo discutible, las tres); run-3 añade un Critical (C4, `data/invoices/2026-001.pdf` no es un PDF válido) y run-4 un Required (falta de test del orden de `listOrders`). El verifier refutó 0 hallazgos en las tres.

### Medias, T17 frente a T20

Solo datos. T17: esfuerzo `low`, kit `6d9fd8a`. T20: esfuerzo `medium`, kit `20c832c`.

| Comando | Base | Ejecuciones válidas | Duración (s) | Entrada | Entrada en caché | Entrada sin caché | Salida | Razonamiento | Bugs detectados (de 9) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `review-prepush` | T17 (`low`) | 3 | 112 | 687.731 | 615.765 | 71.966 | 5.882 | 87 | 6,0 |
| `review-prepush` | T20 (`medium`) | 3 | 137 | 650.935 | 586.880 | 64.055 | 6.497 | 252 | 6,3 |
| `review-pr` | T17 (`low`) | 3 | 91 | 1.081.680 | 1.001.856 | 79.824 | 5.780 | 209 | 4,7 |
| `review-pr` | T20 (`medium`) | 0 | — | — | — | — | — | — | — |

## Base con esfuerzo `low` (T17)

Válida para el esfuerzo `low`, el que `gpt-6.1-terra` trae por defecto; T20 la complementa con `medium`.

### Cómo se midió

| | |
|---|---|
| Fecha | 2026-11-04 |
| Codex | `codex-cli 0.165.0` |
| Modelo | `gpt-6.1-terra`, explícito con `-m` en toda ejecución (también en las pruebas previas) y registrado en cada `meta.json`. Los hilos de las seis ejecuciones, subagentes incluidos, lo tienen en su `turn_context` |
| Commit del kit | `6d9fd8a` (`main`). `skills/`, `agents/` y `adapters/` no cambian: la review medida es la de ese commit. La PR toca solo `measure.sh`, `summarize.py` y esta documentación |
| Sandbox | `tests/review-sandbox/build.sh --codex`, rama `feature/orders-pagination-invoices` (sin remoto; no hay push) |
| Ejecución | `-s read-only`, sin `--dangerously-bypass-*`, sin ampliar permisos. No se tocó nada de `~/.codex` ni se copió ninguna credencial |
| Prompts | los de T1, sin cambios y sin indicar `fork_turns` (ver más abajo): se mide la review de hoy y la variación del modelo es parte de lo medido |

Comandos (desde la raíz del repo):

```bash
tests/review-sandbox/build.sh --codex
tests/review-sandbox/measure.sh review-prepush 1     # ejecución de prueba; solo si es válida:
START=2 tests/review-sandbox/measure.sh review-prepush 2
tests/review-sandbox/measure.sh review-pr 3
```

### Por qué T1 usó las personas globales y cómo se resolvió

Comprobado, no supuesto. Para saber qué persona carga un subagente se compara el mensaje `developer` de arranque de su registro en `~/.codex/sessions` con el cuerpo (`developer_instructions`) de cada `.toml`.

1. En el sandbox, `code-reviewer`, `test-engineer` y `finding-verifier` difieren de las de `~/.codex/agents/`; `security-auditor` es idéntica.
2. Sondeos pequeños con `gpt-6.1-terra` (seis ejecuciones, no incluidas en las tablas). Un agente de nombre único (`zz-probe`) en `.codex/agents/` del proyecto, y otro declarado en un `.codex/config.toml` del proyecto, dan `unknown agent_type`: **Codex no carga la capa `.codex/` del proyecto**. Pasa igual con `-c projects."<ruta>".trust_level="trusted"`, y el `code-reviewer` lanzado con ese `-c` cargó la global.
3. La sobrescritura de una sola llamada `-c agents.<rol>.config_file=<ruta al .toml>` (con `agents.<rol>.description`) sí funciona: el agente de nombre único se carga, y con el nombre de una persona global **tiene prioridad sobre la global**.
4. **Causa, parcialmente confirmada:** el proyecto del sandbox no figura en `[projects]` de `~/.codex/config.toml` (solo está de confianza otro) y la capa del proyecto no se carga. No se pudo separar «falta de confianza» de «`codex exec` no lee esa capa»: lo único que lo distinguiría es marcar el proyecto de confianza en `~/.codex/config.toml`, que está fuera de los límites de esta tarea (y `-c projects...` no basta). Lo confirmado es el efecto y que declarar las personas con `-c` lo evita.
5. **Arreglo:** `measure.sh` pasa a `codex exec` un `-c agents.<rol>.config_file` y un `description` por cada `.toml` de `.codex/agents/` del sandbox. No cambia nada fuera del repo generado.

### Prueba de que cargaron las personas del sandbox

`summarize.py` comprueba, por subagente, que el **cuerpo completo** de su `.toml` del sandbox está en los mensajes `developer` de su registro; si no, añade el problema a `problems` y la ejecución es inválida. También lo compara con `~/.codex/agents/` y dice si las dos copias se pueden distinguir. Las seis ejecuciones tienen `problems` vacío y los 18 subagentes cargaron la persona del sandbox (los 6 `code-reviewer`, 3 `test-engineer` y 6 `finding-verifier` se distinguen de la global; los 3 `security-auditor` son idénticos en ambos sitios y **no se puede distinguir** cuál cargaron).

La comprobación discrimina: aplicada a los registros de T1 marca como inválidos `code-reviewer`, `test-engineer` y `finding-verifier` («cargó la global de ~/.codex/agents») y deja pasar a `security-auditor` marcándolo como indistinguible.

### De dónde salen las cifras

Igual que en T1: `summarize.py` suma los `token_usage_record` de los registros de sesión por agente (la sesión principal coincide con `turn.completed`: ningún `problems` por eso). «Entrada» incluye la «entrada en caché»; «sin caché» es la resta. **No hay cifras estimadas.** Se añade por subagente: el `fork_turns` con el que lo lanzó la principal (`spawn_agent`; «no indicado» = hereda todo el historial) y los tokens de entrada de su primera llamada, que son el historial heredado más sus instrucciones.

### Límites y condiciones

- **Semgrep no funciona, igual que en T1.** El motivo cambia al intentarlo. La falta de directorio temporal se resuelve con `-s workspace-write`, `TMPDIR` y las variables `SEMGREP_*` dentro del sandbox generado y sin `/tmp` escribible (comprobado con `codex sandbox`). Pero `semgrep scan --config p/default` descarga las reglas de `semgrep.dev` y falla con `Name or service not known`: hace falta red, y dársela sería ampliar los permisos fuera del sandbox. Fuera del sandbox de Codex el script sí corre. Se mantuvo `read-only`, así que las condiciones son las de T1: los informes dicen «Semgrep: skipped/failed».
- **Variación del modelo:** con el mismo prompt, el modelo lanzó los subagentes con `fork_turns: "none"` en `review-prepush` run-1 y run-3 (primera llamada de ~21.500 tokens de entrada) y sin indicarlo en el resto (entre 35.570 y 50.017). Es parte de lo medido, pero explica gran parte de la diferencia entre ejecuciones.
- **Esfuerzo:** los subagentes aparecen con `effort low` en su `turn_context`; la sesión principal no lo registra (campo vacío). Los `.toml` no lo declaran. T20 lo investigó: `low` es el valor por defecto del catálogo para este modelo y los subagentes heredan el de la sesión. Los hijos con historial heredado muestran además un primer `turn_context` del padre (sin esfuerzo), copiado del historial.
- **Idioma:** el prompt no lo fija y el informe salió en español en cinco ejecuciones y en inglés en `review-prepush` run-1.
- **Repeticiones y fallos:** ninguna ejecución de Codex se repitió ni falló (todas `exit 0`). `review-prepush` run-1 fue la ejecución de prueba y es válida, así que cuenta. Con la primera versión de `summarize.py` cuatro ejecuciones salieron «inválidas» (las de subagentes con historial heredado): era un fallo del script (atribuía los mensajes `developer` de un hijo a su padre, porque el registro de un hijo trae al final la `session_meta` del padre). Se corrigió y se resumieron de nuevo los mismos registros; no se relanzó Codex. Aparte, seis sondeos pequeños de diagnóstico (arriba) y una ejecución de `codex sandbox` para Semgrep.
- Los registros crudos (`events.jsonl`, `stderr.txt`) quedan en `tests/review-sandbox/results/` (ignorado por git). En el repo van `report.md`, `summary.json` y `meta.json` de cada ejecución en `docs/review/medicion-review/t17/<comando>/run-<n>/`, con la ruta absoluta del sandbox sustituida por `repo/`. No hay secretos.
- La duración es de reloj, de principio a fin de `codex exec`.

### Tokens

#### `review-prepush`

**run-1** (exit 0, 113 s, 2 subagentes, modelo visto: gpt-6.1-terra, esfuerzo de los subagentes: low, `problems`: vacío)

| Agente | Llamadas | Entrada | En caché | Sin caché | Salida | Razonamiento | `fork_turns` | Entrada de su 1.ª llamada | Persona cargada |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| sesión principal | 14 | 447.230 | 417.408 | 29.822 | 3.484 | 64 | — | — | — |
| code-reviewer | 6 | 168.325 | 137.216 | 31.109 | 1.501 | 0 | `none` | 21.612 | sandbox |
| finding-verifier | 3 | 81.338 | 64.000 | 17.338 | 1.584 | 50 | `none` | 21.465 | sandbox |
| **Total** | 23 | **696.893** | **618.624** | **78.269** | **6.569** | **114** | | | |

**run-2** (exit 0, 92 s, 2 subagentes, modelo visto: gpt-6.1-terra, esfuerzo de los subagentes: low, `problems`: vacío)

| Agente | Llamadas | Entrada | En caché | Sin caché | Salida | Razonamiento | `fork_turns` | Entrada de su 1.ª llamada | Persona cargada |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| sesión principal | 10 | 282.896 | 262.784 | 20.112 | 2.884 | 25 | — | — | — |
| code-reviewer | 4 | 167.707 | 151.424 | 16.283 | 1.168 | 9 | no indicado | 36.421 | sandbox |
| finding-verifier | 3 | 137.707 | 120.960 | 16.747 | 738 | 27 | no indicado | 39.808 | sandbox |
| **Total** | 17 | **588.310** | **535.168** | **53.142** | **4.790** | **61** | | | |

**run-3** (exit 0, 131 s, 2 subagentes, modelo visto: gpt-6.1-terra, esfuerzo de los subagentes: low, `problems`: vacío)

| Agente | Llamadas | Entrada | En caché | Sin caché | Salida | Razonamiento | `fork_turns` | Entrada de su 1.ª llamada | Persona cargada |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| sesión principal | 15 | 526.510 | 492.416 | 34.094 | 3.481 | 10 | — | — | — |
| code-reviewer | 6 | 168.810 | 137.600 | 31.210 | 1.439 | 28 | `none` | 21.623 | sandbox |
| finding-verifier | 3 | 82.671 | 63.488 | 19.183 | 1.366 | 48 | `none` | 21.436 | sandbox |
| **Total** | 24 | **777.991** | **693.504** | **84.487** | **6.286** | **86** | | | |

#### `review-pr`

**run-1** (exit 0, 86 s, 4 subagentes, modelo visto: gpt-6.1-terra, esfuerzo de los subagentes: low, `problems`: vacío)

| Agente | Llamadas | Entrada | En caché | Sin caché | Salida | Razonamiento | `fork_turns` | Entrada de su 1.ª llamada | Persona cargada |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| sesión principal | 14 | 434.334 | 409.216 | 25.118 | 3.243 | 43 | — | — | — |
| code-reviewer | 4 | 168.224 | 151.808 | 16.416 | 1.027 | 39 | no indicado | 36.125 | sandbox |
| security-auditor | 3 | 125.089 | 108.544 | 16.545 | 543 | 8 | no indicado | 35.570 | sandbox (idéntica a la global) |
| test-engineer | 3 | 120.875 | 106.752 | 14.123 | 630 | 9 | no indicado | 35.697 | sandbox |
| finding-verifier | 3 | 146.227 | 130.944 | 15.283 | 813 | 54 | no indicado | 43.746 | sandbox |
| **Total** | 27 | **994.749** | **907.264** | **87.485** | **6.256** | **153** | | | |

**run-2** (exit 0, 92 s, 4 subagentes, modelo visto: gpt-6.1-terra, esfuerzo de los subagentes: low, `problems`: vacío)

| Agente | Llamadas | Entrada | En caché | Sin caché | Salida | Razonamiento | `fork_turns` | Entrada de su 1.ª llamada | Persona cargada |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| sesión principal | 15 | 532.570 | 490.368 | 42.202 | 2.980 | 26 | — | — | — |
| code-reviewer | 3 | 135.174 | 125.312 | 9.862 | 759 | 8 | no indicado | 44.015 | sandbox |
| security-auditor | 2 | 91.055 | 79.616 | 11.439 | 309 | 32 | no indicado | 43.436 | sandbox (idéntica a la global) |
| test-engineer | 2 | 88.505 | 80.000 | 8.505 | 419 | 50 | no indicado | 43.560 | sandbox |
| finding-verifier | 2 | 98.712 | 86.144 | 12.568 | 1.002 | 22 | no indicado | 46.846 | sandbox |
| **Total** | 24 | **946.016** | **861.440** | **84.576** | **5.469** | **138** | | | |

**run-3** (exit 0, 95 s, 4 subagentes, modelo visto: gpt-6.1-terra, esfuerzo de los subagentes: low, `problems`: vacío)

| Agente | Llamadas | Entrada | En caché | Sin caché | Salida | Razonamiento | `fork_turns` | Entrada de su 1.ª llamada | Persona cargada |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| sesión principal | 18 | 748.876 | 713.088 | 35.788 | 3.534 | 216 | — | — | — |
| code-reviewer | 3 | 144.693 | 139.008 | 5.685 | 589 | 7 | no indicado | 46.624 | sandbox |
| security-auditor | 2 | 98.680 | 89.600 | 9.080 | 345 | 47 | no indicado | 46.053 | sandbox (idéntica a la global) |
| test-engineer | 3 | 152.883 | 143.488 | 9.395 | 573 | 32 | no indicado | 46.211 | sandbox |
| finding-verifier | 3 | 159.142 | 151.680 | 7.462 | 573 | 35 | no indicado | 50.017 | sandbox |
| **Total** | 29 | **1.304.274** | **1.236.864** | **67.410** | **5.614** | **337** | | | |

#### Medias

| Comando | Ejecuciones | Subagentes | Duración (s) | Entrada | Entrada en caché | Salida | Razonamiento | Entrada sin caché |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `review-prepush` | 3 | 2 | 112 | 687.731 | 615.765 | 5.882 | 87 | 71.966 |
| `review-pr` | 3 | 4 | 91 | 1.081.680 | 1.001.856 | 5.780 | 209 | 79.824 |


Las medias son aritméticas sobre 3 ejecuciones; la variación entre ellas es grande, así que sirven de orden de magnitud.

### Qué encuentran

Puntuado **a mano**, leyendo cada `report.md` contra `tests/review-sandbox/EXPECTED.md`. Criterio: un bug cuenta si un hallazgo (o el arreglo de otro) lo señala con su causa. B2 exige señalar que el test no comprueba el contenido de la página (o que pasa con el bug); si solo aparece como «comprobar contenido exacto» en el arreglo de B1 se anota «parcial» y no cuenta. B8 cuenta solo con un remedio con nombre. Un señuelo aparece si sobrevive como hallazgo.

| | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 | D1 | D2 | D3 | Bugs detectados |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `review-prepush` run-1 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| `review-prepush` run-2 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| `review-prepush` run-3 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| **`review-prepush`, de 3** | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 6,0 de media |
| `review-pr` run-1 | sí | parcial | sí | sí | no | sí | sí | no | no | no | no | no | 5/9 |
| `review-pr` run-2 | sí | sí | sí | sí | no | sí | no | no | no | no | no | no | 5/9 |
| `review-pr` run-3 | sí | parcial | sí | sí | no | sí | no | no | no | no | no | no | 4/9 |
| **`review-pr`, de 3** | 3 | 1 (+2 parcial) | 3 | 3 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 4,7 de media |

Notas por ejecución:

- **`review-prepush`** (las tres, BLOCK, 3 Critical): B2 aparece como hallazgo propio («la prueba acepta páginas incorrectas», «pasa con el offset desplazado»); B5 como Nit («TODO sin referencia»). Fuera de `EXPECTED.md`: falta de test del endpoint `/invoices` (lo discutible) y de test del orden de `listOrders`.
- **`review-pr` run-1:** B2 parcial (C2 pide comprobar contenido y totales exactos, pero ningún hallazgo dice que el test actual pase con el bug); B7 sí: R3 nombra `pageTotal` y `sumTotals` y pide compartir la función sin dependencia circular. Tier 2, CHANGES.
- **`review-pr` run-2:** B2 sí (R2: «el test no comprueba items; la primera página incorrecta pasa todas las aserciones»). Sin B7. Tier 2.
- **`review-pr` run-3:** B2 parcial (solo en el arreglo de C2); un Optional fuera de `EXPECTED.md` (O1, la descripción del commit no explica motivo ni verificación, fuente `pr-description`). Tier 2.
- **B5 no aparece en ninguna de `review-pr`** (Nits: 0 en las tres). **B8 y B9 no aparecen en ninguna de las seis ejecuciones; B7 solo en una.** Ningún señuelo (D1–D3) sobrevive en ninguna.
- El verifier refutó 0 hallazgos en las seis ejecuciones.


## Medición de T1: no comparable

> **No usar como base.** Al lanzar los subagentes, Codex usó las copias globales de `~/.codex/agents/` (del 2026-10-19), no las personas del sandbox. La comprobación de T17 sobre los registros de T1 lo confirma: `code-reviewer`, `test-engineer` y `finding-verifier` cargaron la global; `security-auditor` es idéntica en ambos sitios, así que no se puede distinguir. La `code-reviewer` global no tiene la sección «Beyond the diff». Las skills sí eran las del sandbox. Los hallazgos y los tokens de los subagentes de esta sección no son comparables con los de la base válida de arriba. (La comprobación de T1, «Codex las lista y la sesión principal las lee con `cat`», no demuestra qué carga el subagente; la nota anterior decía que `finding-verifier` no se pudo distinguir porque solo comparaba los primeros 2.500 caracteres.)

Cuántos tokens gastan y qué encuentran `review-pr` y `review-prepush` **tal como están hoy**, ejecutadas con Codex sobre el sandbox de `tests/review-sandbox/`. Es la referencia con la que comparar el reviewer unificado (cambio `review-unificada`, paso S1). Este documento no saca conclusiones sobre el reviewer unificado: aún no existe.

### Cómo se midió

| | |
|---|---|
| Fecha | 2026-11-03 |
| Codex | `codex-cli 0.165.0` |
| Modelo | `gpt-6.1-terra`, explícito con `-m` (por defecto de `measure.sh`, variable `MODEL`) y registrado en cada `meta.json` |
| Commit del repo | `ebaeec1` (`main` con T14 mergeada). `skills/`, `agents/` y `adapters/` no cambian: la review medida es la de ese commit. La PR añade `build.sh --codex`, `measure.sh` y `summarize.py` |
| Sandbox | `tests/review-sandbox/build.sh --codex`, rama `feature/orders-pagination-invoices` (sin red, sin remoto; el hook `pre-push` no se dispara porque no se hace push) |
| Disposición de Codex | skills en `.agents/skills/` y personas en `.codex/agents/*.toml` del sandbox (comprobado: Codex las lista y lee desde ahí) |
| Ejecución | solo lectura (`-s read-only`), sin `--dangerously-bypass-*` |

Comandos exactos (desde la raíz del repo):

```bash
tests/review-sandbox/build.sh --codex
tests/review-sandbox/measure.sh review-prepush 3
tests/review-sandbox/measure.sh review-pr 3
```

Cada ejecución lanza, dentro de `tests/review-sandbox/repo`:

```bash
codex exec -m gpt-6.1-terra -s read-only --json -o report.md "<prompt>"
```

con estos prompts (`$BRANCH` = `feature/orders-pagination-invoices`):

- `review-pr`: «Ejecuta la skill review-pr (.agents/skills/review-pr/SKILL.md) con los argumentos: $BRANCH main. Usa solo las skills de este proyecto, en .agents/skills/ (también las que ella cite: review-context, review-report, task-done); no leas ~/.agents ni ~/.codex. Los subagentes son los de .codex/agents/. No cambies ningún fichero.»
- `review-prepush`: «Ejecuta la skill review-prepush (.agents/skills/review-prepush/SKILL.md) con los argumentos: main, estando en la rama $BRANCH.» y la misma coletilla.

`codex exec` no tiene comandos de barra: la skill se invoca nombrándola en el prompt.

#### De dónde salen las cifras

- `turn.completed` de `--json` da solo el uso de la **sesión principal**. No incluye a los subagentes, y la salida `--json` no muestra su arranque (solo eventos `wait` sin ids).
- Los subagentes sí dejan su propio fichero de sesión en `~/.codex/sessions/`, con su rol, su modelo (`turn_context`) y un `token_usage_record` por llamada a la API. `summarize.py` suma esos registros por agente. Para la sesión principal coinciden exactamente con `turn.completed` (comprobado en las seis ejecuciones: campo `problems` vacío en cada `summary.json`).
- Cada cifra sale de esos registros; no hay estimaciones. «Entrada» incluye la «entrada en caché», como la entrega Codex; «razonamiento» se da tal cual, sin sumarlo a la salida.
- **Modelo de los subagentes:** los 24 hilos de las seis ejecuciones (3 por ejecución de `review-prepush` y 5 por la de `review-pr`, la sesión principal incluida) tienen `gpt-6.1-terra` en su `turn_context`. Los subagentes aparecen además con `effort low` en su `turn_context`; los `.toml` de las personas no declaran modelo ni esfuerzo, así que ese valor no sale del kit (no se ha investigado quién lo fija).

#### Límites y cosas a tener en cuenta

- **Semgrep falló en las seis ejecuciones** («no hay directorio temporal escribible» en el sandbox de solo lectura), así que cada informe dice «Semgrep: skipped». Una review real lo ejecutaría si está instalado; aquí no cuenta ni en tokens ni en hallazgos.
- **Skills globales:** la máquina tiene copias antiguas en `~/.agents/skills/` y el plugin `harness` activado en `~/.codex/config.toml`. Para que no se cuelen, el prompt manda usar solo `.agents/skills/` del sandbox y ninguna ejecución ha leído `~/.agents` (comprobado en `events.jsonl`). No se aisló `CODEX_HOME` ni `HOME`.
- Cada comando se ejecutó una sola vez por número: **sin repeticiones ni fallos**. La primera ejecución de cada comando hizo de prueba (arranque de subagentes, modelo, tokens) y cuenta como `run-1`. Antes hubo dos llamadas diminutas a `codex exec` (listar skills y agentes, unos 50.000 tokens de entrada) para comprobar qué ve Codex; no están en las tablas.
- `summarize.py` se escribió después del `run-1` de `review-prepush` (hubo que ver el formato de los registros antes); su `summary.json` se generó a mano con el mismo script sobre los mismos datos.
- Los resultados crudos (`events.jsonl`, `stderr.txt`, informes) quedan en `tests/review-sandbox/results/` (en `.gitignore`) y, en esta máquina, copiados a `/tmp/t1-medicion-raw/`. En el repo van los informes, `summary.json` y `meta.json` de cada ejecución en `docs/review/medicion-review/<comando>/run-<n>/`; en los informes se sustituyó la ruta absoluta del sandbox por `repo/`. No hay secretos en ninguno.
- La duración es de reloj, de principio a fin de `codex exec`.

### Tokens

#### `review-prepush`

**run-1** (exit 0, 119 s, 2 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 10 | 348.248 | 313.344 | 3.104 | 59 |
| code-reviewer | 2 | 96.778 | 82.688 | 1.095 | 34 |
| finding-verifier | 3 | 155.051 | 142.208 | 1.425 | 21 |
| **Total** | 15 | **600.077** | **538.240** | **5.624** | **114** |

**run-2** (exit 0, 112 s, 2 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 9 | 299.529 | 260.864 | 3.078 | 27 |
| code-reviewer | 2 | 92.355 | 79.360 | 882 | 30 |
| finding-verifier | 3 | 151.423 | 136.192 | 1.286 | 38 |
| **Total** | 14 | **543.307** | **476.416** | **5.246** | **95** |

**run-3** (exit 0, 107 s, 2 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 9 | 283.694 | 253.952 | 3.294 | 9 |
| code-reviewer | 4 | 104.046 | 74.368 | 1.382 | 0 |
| finding-verifier | 3 | 81.056 | 63.744 | 1.544 | 44 |
| **Total** | 16 | **468.796** | **392.064** | **6.220** | **53** |


#### `review-pr`

**run-1** (exit 0, 91 s, 4 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 14 | 474.461 | 447.616 | 3.419 | 108 |
| code-reviewer | 3 | 133.142 | 120.832 | 657 | 86 |
| security-auditor | 2 | 90.603 | 76.288 | 276 | 14 |
| test-engineer | 2 | 85.886 | 76.544 | 408 | 31 |
| finding-verifier | 3 | 146.803 | 134.784 | 715 | 47 |
| **Total** | 24 | **930.895** | **856.064** | **5.475** | **286** |

**run-2** (exit 0, 97 s, 4 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 14 | 569.239 | 528.512 | 3.480 | 106 |
| code-reviewer | 3 | 152.600 | 140.160 | 833 | 8 |
| security-auditor | 3 | 154.328 | 142.080 | 630 | 86 |
| test-engineer | 2 | 95.219 | 87.552 | 488 | 35 |
| finding-verifier | 3 | 167.799 | 155.904 | 797 | 48 |
| **Total** | 25 | **1.139.185** | **1.054.208** | **6.228** | **283** |

**run-3** (exit 0, 86 s, 4 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 15 | 570.105 | 525.952 | 3.093 | 134 |
| code-reviewer | 3 | 127.130 | 122.112 | 737 | 7 |
| security-auditor | 2 | 86.636 | 80.000 | 286 | 23 |
| test-engineer | 3 | 135.469 | 127.360 | 593 | 44 |
| finding-verifier | 3 | 141.014 | 136.064 | 428 | 43 |
| **Total** | 26 | **1.060.354** | **991.488** | **5.137** | **251** |


#### Medias

| Comando | Ejecuciones | Subagentes | Duración (s) | Entrada | Entrada en caché | Salida | Razonamiento | Entrada sin caché |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `review-prepush` | 3 | 2 | 113 | 537.393 | 468.907 | 5.697 | 87 | 68.487 |
| `review-pr` | 3 | 4 | 91 | 1.043.478 | 967.253 | 5.613 | 273 | 76.225 |

Las medias son aritméticas sobre 3 ejecuciones; la variación entre ellas es grande (p. ej. entrada de `review-prepush` entre 468.796 y 600.077), así que sirven de orden de magnitud, no de cifra exacta.

### Qué encuentran

Puntuado **a mano**, leyendo cada `report.md` contra `tests/review-sandbox/EXPECTED.md`. Criterio: un bug cuenta si un hallazgo (o el arreglo de otro) lo señala con su causa. B2 exige señalar que el test no comprueba el contenido de la página; si solo lo menciona de pasada en el arreglo de B1 se anota «parcial» y no cuenta. B8 cuenta solo si propone un remedio con nombre (*collapse duplicate branches*, *explicit dispatcher*…), como pide su fila. Un señuelo aparece si sobrevive como hallazgo.

| | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 | D1 | D2 | D3 | Bugs detectados |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `review-prepush` run-1 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| `review-prepush` run-2 | sí | no | sí | sí | sí | sí | no | no | no | no | no | no | 5/9 |
| `review-prepush` run-3 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| **`review-prepush`, de 3** | 3 | 2 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 5,7 de media |
| `review-pr` run-1 | sí | parcial | sí | no | no | sí | sí | no | no | no | no | no | 4/9 |
| `review-pr` run-2 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| `review-pr` run-3 | sí | parcial | sí | sí | no | sí | no | no | no | no | no | no | 4/9 |
| **`review-pr`, de 3** | 3 | 1 (+2 parcial) | 3 | 2 | 1 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 4,7 de media |

Notas por ejecución:

- **`review-prepush` run-1:** además un hallazgo no previsto en `EXPECTED.md`, C4 «el PDF de ejemplo no es un PDF válido» (Critical), sobre `data/invoices/2026-001.pdf`, que es un fichero de prueba mínimo. Veredicto BLOCK.
- **`review-prepush` run-2 y run-3:** veredicto BLOCK; el B2 de run-2 no aparece (solo pide tests del endpoint `/invoices`).
- **`review-pr` run-1:** B2 parcial (R3 critica que el test no comprueba `pageTotal`; el arreglo de C2 pide ids exactos, pero no dice que el test actual pase con el bug). B7 sí: R1 nombra `sumTotals` y propone un módulo común sin ciclo. Tier 2, `CHANGES`.
- **`review-pr` run-2:** B4 y B5 sí; sin B7. Tier 2.
- **`review-pr` run-3:** B2 parcial (la verificación dice «the pagination test gap was folded into C2» y el arreglo de C2 pide ids exactos, sin hallazgo propio). Tier 2.
- **B8 y B9 no aparecen en ninguna de las seis ejecuciones; B7 solo en una.** Ningún señuelo (D1–D3) sobrevive en ninguna.
- Fuera de `EXPECTED.md`, en todas las ejecuciones aparece «falta de test del endpoint `/invoices`» (lo que `EXPECTED.md` da por discutible/aceptable) y, en ninguna, «distinguir ENOENT» como Optional.
- Los `.toml` de las personas y las skills se leyeron de `.codex/agents/` y `.agents/skills/` del sandbox.

### Qué ocupa la entrada

Análisis posterior de los registros de sesión de las mismas 6 ejecuciones. Las columnas "~" son estimaciones (caracteres / 4 × llamadas posteriores); el resto son cifras registradas.

**Historial heredado.** `spawn_agent` hereda todo el historial por defecto. 16 de los 18 subagentes se lanzaron sin `fork_turns` y empezaron con entre 41.000 y 50.000 tokens de entrada en su primera llamada. Los 2 de `review-prepush` run-3 usaron `fork_turns: "none"` por decisión del modelo y empezaron con 20.627 y 21.358. Esa ejecución es la de menor entrada de `review-prepush` (468.796) y detectó B1–B6, pero es un solo caso.

**Sesión principal.** Parte de unos 19.000 tokens en su primera llamada, antes de leer nada, y los reenvía en cada llamada:

| Parte de lo reenviado en `review-pr` y `review-prepush` | ~ % |
|---|---:|
| Salidas de comandos | 32–42 |
| Instrucciones de Codex, lista de skills y otros mensajes de sistema | 25–30 |
| Definición de herramientas | 23–30 |
| Mensajes de los subagentes | 1 |

**Las salidas de comandos son casi todas instrucciones.** En `review-pr` run-2 suman 94.785 caracteres, y las tres lecturas de skills y personas ocupan 88.902. La principal leyó las definiciones de las personas en 5 de 6 ejecuciones, aunque la herramienta ya las carga.
