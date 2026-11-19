---
status: done
issue: null
---

# Tareas por objetivo y review por tramos de commits

**Problema:** las tareas se parten pensando en el revisor: como mucho 200 líneas con los tests y una sola regla del mapa cada una (D-0044). Eso trocea las funcionalidades en pasos que no tienen sentido por sí solos, encarece el plan y multiplica las ramas, las PRs y las reviews. Además, la review de cada PR no ve el conjunto. Queremos partir las historias por utilidad: cada tarea es una parte con sentido de una funcionalidad y tiene un solo objetivo (por ejemplo, el endpoint que expone los datos y, en otra tarea, la tabla que los muestra). Así el tamaño es una consecuencia y no un límite. Para que la review no pierda precisión cuando una rama sale grande, `review-prepush` la revisa por tramos de commits seguidos. Le importa a quien planifica los cambios y a quien paga y lee las reviews.

**Plazo máximo:** unos 2–3 días de trabajo de agente, en 4 tareas.

**Fuera de alcance:**
- `review-pr` (CI) por tramos: se hará después, en otro cambio, si la medición lo justifica.
- Un registro de la revisión commiteado en git. El hook `harness-review` ya ejecuta la review él mismo, con otra familia de modelo (D-0055, D-0056), y el agente no puede desactivarlo. Así que el registro no hace falta para obligar a revisar.
- Que el agente que implementa proponga los tramos: los decide el script y la review la lanza el hook.
- Revisiones intermedias durante la implementación (puntos de control).
- Cambiar la caché de veredictos (D-0042): sigue ligada al diff entero de la rama.
- Cambiar los revisores o su número (D-0047, que se mantiene en lo demás).

## Mapa de ejemplos

```
Rule R1: el plan parte por objetivo: cada tarea es una parte con sentido de una funcionalidad, con un solo objetivo explicado en una frase sin "y", y sin límite de líneas (→ D-0058)
  E1: idea-to-change y plan-to-tasks explican el criterio por objetivo con el ejemplo endpoint / tabla y no mencionan «200 líneas» → check.sh lo comprueba en sus textos
  E2: una tarea «exponer las facturas en GET /invoices» cubre R1 (filtrar por fecha) y R2 (paginar) del mapa → es válida: varias reglas, un solo objetivo
  E3: una tarea «añadir el endpoint y además refactorizar el cliente HTTP» → el plan la parte en dos (dos objetivos)
  E4: implement termina una tarea de 450 líneas con un solo objetivo → no para ni informa por el tamaño
  E5: la rama base sigue desplegable tras cada tarea; lo que queda a medias va detrás de un flag que retira la última tarea → igual que hoy (D-0044 se mantiene en esto)

Rule R2: el tamaño solo es una pista: nada bloquea ni avisa por líneas, y la review señala los objetivos mezclados, no el tamaño (→ D-0059)
  E6: el gate en una rama de 450 líneas → sale 0 sin aviso de tamaño
  E7: los hechos de review_facts.py incluyen el recuento de diff_size.py → «tamaño: 450 líneas (3 tramos)»
  E8: una rama de 450 líneas con un solo objetivo → code-reviewer no informa nada por el tamaño
  E9: una rama que añade el endpoint y cambia un formateador que el endpoint no usa → hallazgo Optional de objetivos mezclados, con los ficheros de cada uno (D-0037)

Rule R3: review_facts.py parte base..HEAD en tramos de commits seguidos cuando la rama pasa del umbral de .harness-config.toml de la rama base (→ D-0060)
  E10: rama de 180 líneas con max_lines_per_reviewer = 300 → un solo tramo base..HEAD; la review es la de hoy
  E11: rama de 520 líneas en 5 commits (120, 90, 150, 60, 100) con umbral 300 → tramos de commits seguidos de como mucho 300 líneas: [c1–c2] 210, [c3–c4] 210, [c5] 100
  E12: un commit test(T2) seguido de feat(T2) → siempre en el mismo tramo, aunque juntos pasen del umbral
  E13: un commit de 400 líneas con umbral 300 → tramo propio, marcado «tramo grande»
  E14: sin la clave en .harness-config.toml → un solo tramo base..HEAD y la review de hoy (opt-in, sin umbral por defecto)
  E15: la rama cambia el umbral en su propio .harness-config.toml → se usa el de la base (fichero de control, D-0054)
  E16: las líneas se cuentan como diff_size.py: sin lockfiles, generados ni snapshots → un lockfile de 2.000 líneas no abre tramos
  E17: los tramos cubren todos los commits de base..HEAD, sin huecos ni solapes, en orden → cada tramo con su rango a..b y sus líneas

Rule R4: con varios tramos, review-prepush lanza un code-reviewer por tramo, verifica contra HEAD y hace una pasada de costuras
  E18: 3 tramos → 3 code-reviewer en paralelo; cada brief lleva su diff a..b, la tarea, los hechos completos y la orden de leer git diff base...HEAD si falta contexto
  E19: el revisor del tramo 1 sospecha que falta una validación que añade el tramo 2 → la encuentra en el diff de la rama y no informa
  E20: un hallazgo del tramo 1 sobre código que borra el tramo 3 → el verifier lo refuta porque no es cierto en HEAD
  E21: el mismo hallazgo en dos tramos → aparece una vez en el informe
  E22: 2 o más tramos → un code-reviewer más hace la pasada de costuras (lo que expone cada tramo y quién lo usa en otro, y si están todos los ejemplos de la tarea), y el informe tiene su sección; con 1 tramo no hay pasada de costuras
  E23: un Critical confirmado en cualquier tramo o en las costuras → el push se bloquea como hoy
  E24: sin subagentes (pi) → los tramos se revisan uno detrás de otro en la sesión principal y se dice en Verification

Decidido: la pasada de costuras la hace un code-reviewer más, sin historial (D-0046), con un brief de costuras (descartado: la sesión principal al fusionar, sin contexto limpio)
```

La medición final (sin ejemplos) junta en una rama los commits de T2 a T6 del cambio `95-hechos-de-la-review` y la revisa por tramos con `tests/review-sandbox` (Codex, `gpt-6.1-terra`, `medium`, 3 ejecuciones). La compara con lo medido en T6: coste, hallazgos confirmados frente a refutados, hallazgos de «falta X, que está en otro tramo» (deberían ser casi cero) y lo que encuentra solo la pasada de costuras. Con ese dato, la misma tarea escribe en `docs/review/medicion-review.md` el valor recomendado de `[review] max_lines_per_reviewer` y su justificación. La tarea no toca el `.harness-config.toml` de este repo: es un fichero de control (D-0054) y el gate lo bloquea en una rama de tarea; la persona pone el valor directamente en `main`.

## Supuestos

- El límite de cada tramo y el umbral para partir son el mismo número: si la rama cabe en un tramo, no se parte.
- La pareja roja/verde es el commit `test(Tn)` y el siguiente commit de la rama que no es `test(…)`.
- Un tramo se forma juntando commits seguidos mientras no pase del umbral (voraz, en orden). No se buscan cortes óptimos.
- La clave va en `.harness-config.toml` como `[review] max_lines_per_reviewer = <n>`. Los ejemplos usan 300 solo como valor de prueba.
- `implement` sigue ejecutando la verificación completa antes de cada PR (D-0036).
- D-0037 sigue en pie para los objetivos mezclados. Su parte de tamaño queda sin número: la sustituye la pista de R2.

## Tareas

Un fichero por tarea en `tasks/`, cada una con su rama y su PR. Cuáles están listas: el tablero de `task-done` (`scripts/board.py`). No se listan aquí: los ficheros de tareas son la única fuente.
