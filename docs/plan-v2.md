# Plan de la v2

Fecha: 2026-10-23. Estado: **en curso** (2026-10-24: fases 0, 1, 2 y 3 hechas. La fase 3 añadió `idea-to-issue`, `task-done --issue` y el fragmento de niveles con glosario y regla de evidencia fresca ([D-0013 a D-0017](decisions/README.md), en `proposed`). Quedan pendientes de la fase 3: pasar la suite de activación con los casos nuevos de `idea-to-issue` (necesita `claude` y red) y probar el flujo B en un trabajo real; este repo no tiene `AGENTS.md`, así que no lleva el fragmento. Para la fase 4, que la review lea el issue de la rama; para la fase 5, el orden de los tests en `plan-to-tasks` (#18), los componentes reutilizados en `spec-to-plan` (#11) y el campo `tests:` en la plantilla de `tasks.md`). Las decisiones de la sección 11 y de la 12 están en [`docs/decisions/`](decisions/README.md).

Sale de contrastar la [guía de desarrollo con IA](guia_desarrollo_ia.md) con lo que hay en el repo, y de revisar las issues abiertas y el [plan de mejoras](plan-de-mejoras.md). Parte de `origin/main` tal como está hoy: la PR #6 (`debug-root-cause`, `task-done`) y la #19 (issue #14) ya están mergeadas.

## 1. Objetivo

Trabajar más ágil sin perder los porqués.

- **Más ágil:** el proceso se ajusta al tamaño y al riesgo de la tarea, como dice la guía. El SDD completo pasa a ser el último nivel, no el camino por defecto.
- **Sin perder los porqués:** dentro de dos meses habrá cosas que no recordemos. Toda decisión real deja un registro, para que un desarrollo nuevo no contradiga uno anterior sin darnos cuenta.

Hoy el repo es un kit de SDD: el centro es `idea-to-spec → spec → plan → tasks → implement`, con dos aprobaciones de documentos largos. En un trabajo real medido (#13, #15), eso costó unas 2h20 y unos 50k caracteres de lectura para 6–8 decisiones de verdad. La v2 conserva esas 6–8 decisiones y quita el resto.

## 2. El modelo: qué vive dónde

La contradicción entre la guía («el código manda») y el SDD actual («la spec es referencia viva») se resuelve separando tres cosas que hoy van juntas en `spec.md`:

| Qué | Dónde | Vida | Por qué |
|---|---|---|---|
| **Qué hace** el sistema | Tests (y tests de arquitectura) | Mientras exista el código | Avisan cuando el código se desfasa; una spec no |
| **Por qué** se decidió así | `docs/decisions/NNNN-*.md` + índice | Permanente; no se editan, se sustituyen | Registran lo que se pensó en un momento; si cambia, queda escrito que cambió |
| **Qué vamos a hacer y en qué pasos** | Issue de GitHub (nota, mapa de ejemplos, tareas) | Hasta cerrar el issue | Solo sirve mientras se trabaja; el issue da el tablero Kanban sin hacer nada más |

`spec.md` y `plan.md` siguen existiendo en el nivel SDD, pero como **documentos de trabajo**: al terminar, sus decisiones se pasan a `docs/decisions/` y la spec se marca `obsolete` o se archiva. Nadie la mantiene al día.

## 3. Niveles de proceso y puerta humana

Cada nivel indica dónde se para la persona antes de que haya código. Todos terminan igual: si hubo decisiones, se registran.

| Tipo de tarea | Proceso | Puerta antes del código |
|---|---|---|
| Prototipo o experimento desechable | Vibe coding: pedir, probar, tirar | Ninguna. Si empieza a usarse de verdad, sube de nivel |
| Trivial en código que dura | Prompt directo y leer el diff | **C**: ninguna; se revisa el diff |
| Bug con causa clara | Test que reproduce el bug y arreglo | **C** |
| Bug de causa desconocida | `debug-root-cause` | **C**; el test de regresión que falla sin el arreglo es la prueba |
| Feature normal | Issue → Example Mapping → tareas (sección 4) | **B**: una parada por idea, en el mapa de ejemplos y las decisiones |
| Reglas delicadas (dinero, datos personales) o feature grande | Lo mismo, y SDD si hay diseño de verdad que decidir | **A**: además de B, parada en los tests en rojo de cada tarea delicada |

- **C, revisión al final:** `review-prepush` y leer el diff, tests incluidos.
- **B, mapa de ejemplos:** la persona revisa reglas, ejemplos y decisiones (10–15 líneas en lenguaje de negocio). Después el agente hace todas las tareas sin parar, con la protección mecánica de la sección 4.4.
- **A, tests en rojo:** por cada tarea delicada, el agente escribe los tests, los ve fallar y espera el «ok». Es el TDD ping-pong de la guía.

Las señales para subir o bajar de nivel de la guía («el plan es más largo que el diff», «llevas tres intentos», «el agente toca ficheros que no esperabas») se copian en `AGENTS.md` (sección 6.1).

## 4. El flujo por defecto (nivel B)

```
1. Issue con la nota de la idea
2. Example Mapping con el agente → reglas, ejemplos, preguntas
3. Preguntas que son decisiones → el agente redacta docs/decisions/ en `proposed`
   ★ persona: revisa el mapa y las decisiones → `accepted`
4. Tareas en el issue (rebanadas verticales)
5. Por tarea: commit de tests en rojo → implementación de un test cada vez → task-done → commit
6. review-prepush (ejemplos cubiertos, tests intactos, decisiones respetadas) → PR
```

### 4.1 La nota de la idea

Cuerpo del issue, unas 10 líneas:

- **Problema:** qué pasa hoy y a quién le importa.
- **Plazo máximo (appetite):** cuánto estamos dispuestos a invertir. Si no cabe, se parte en varias ideas.
- **Fuera de alcance:** lo que el agente no debe hacer aunque parezca útil.

### 4.2 Example Mapping

El agente propone y la persona corrige:

```
Regla R1: reembolso total si se cancela con más de 1h de antelación
  E1: cancela 2h antes     → reembolso 10 €
  E2: cancela 59 min antes → sin reembolso total
Regla R2: un viaje ya empezado no se puede cancelar
  E3: cancela con el viaje en curso → error "viaje iniciado"
Pregunta: ¿y exactamente 1h? → D-0021
```

- Cada regla es una tarea candidata.
- Cada ejemplo es un test de esa tarea.
- Cada pregunta se clasifica con el criterio de `sdd-decisions`. Las decisiones van a `docs/decisions/` (sección 5); los supuestos se anotan en el issue.
- Para el trabajo que no es una regla (infraestructura, refactor, migraciones), el mapa se sustituye por pasos que dejan el proyecto en verde y se verifican con un comando.

### 4.3 Tareas

Checklist en el issue, con el formato que ya usa `task-done`:

```
- [ ] T1. Esqueleto de punta a punta: cancelar sin reembolso — tests: E2 — verificación: <comando>
- [ ] T2. R1 reembolso total — tests: E1 — verificación: <comando>
- [ ] T3. R2 viaje iniciado — tests: E3 — verificación: <comando>
- [ ] W1. Verificación completa — verificación: <comando de AGENTS.md>
```

**Una tarea está bien acotada si:**

- puedes nombrar su test antes de empezar (si no, falta pensar: vuelta al mapa);
- cabe en un commit con un diff que se puede leer (si no, se parte);
- deja el proyecto en verde.

T1 es siempre la rebanada más fina que funciona de punta a punta.

### 4.4 Protección mecánica de los tests

Lo que sustituye a la parada por tarea en el nivel B:

1. **Tests nombrados por ejemplo:** `test_E1_reembolso_total_si_cancela_2h_antes`. Si protege una decisión, el test la cita (`# D-0021`).
2. **Commit de tests en rojo antes que el código:** `test(T2): E1 en rojo`, y después `feat(T2): …`.
3. **Comprobación en git:** el commit de implementación no toca los tests del commit en rojo, y cada ejemplo del mapa tiene su test. La hacen `task-done` (determinista, al marcar la tarea) y la review (al final).

Lo que no cubre: que el agente traduzca mal un ejemplo a test. Eso se ve al leer el diff final, y es la razón del nivel A para lo delicado.

## 5. El registro de decisiones

### 5.1 Formato

Sustituye a `docs/adr/`. Un fichero por decisión: `docs/decisions/NNNN-titulo.md`, con numeración correlativa que no se reutiliza.

```markdown
---
id: D-NNNN
title: <decisión en pocas palabras>
type: architecture | rule | discarded
status: proposed | accepted | superseded | obsolete
date: YYYY-MM-DD
affects: [src/billing/, api/refunds]   # módulos o rutas; lo usa el agente para filtrar
supersedes: null
superseded_by: null
issue: "#42"
---

## Contexto
## Decisión
## Alternativas descartadas
## Cómo se hace cumplir   <!-- test, regla de lint, test de arquitectura; o "no se automatiza" -->
```

Las claves y los valores del frontmatter van en inglés; los encabezados y el texto, en el idioma del proyecto (como el `status` de las specs).

- **architecture:** lo que cubren hoy los ADRs.
- **rule:** regla de negocio («reembolso total con más de 1h»).
- **discarded:** «probamos X y no sirvió». Es el tipo que más trabajo ahorra a largo plazo.

Las secciones de consecuencias y de contexto de IA de la plantilla actual pasan a ser opcionales.

### 5.2 Índice

`docs/decisions/README.md`, con una línea por decisión: id, título, tipo, estado y `affects`. El agente lee solo el índice y abre las decisiones que tocan lo que va a cambiar, así que el contexto no crece con el número de decisiones. Un fichero único se descartó por eso.

### 5.3 Ciclo de vida

1. Tras planificar con la persona (mapa de ejemplos, plan mode o plan del SDD), el agente redacta las decisiones en `proposed` y añade sus líneas al índice.
2. La persona las revisa y las pasa a `accepted`. En el nivel B es la misma parada que el mapa.
3. Una decisión aceptada no se edita. Si cambia, se escribe una nueva que la sustituye y se enlazan las dos.
4. Solo se registra lo que tuvo alternativas reales (criterio de `sdd-decisions`). La mayoría de las tareas triviales y de los bugs no dejan ninguna.

### 5.4 Cómo se detectan las contradicciones

| Momento | Quién | Qué hace |
|---|---|---|
| Al planificar | El agente, en Research, plan mode o Example Mapping | Lee el índice, filtra por `affects` y avisa si el plan choca con una decisión aceptada |
| Al ejecutar | Los tests | El test que protege una regla cita su id. Si se rompe, el agente encuentra el porqué en vez de «arreglar» el test |
| Al revisar | `review-prepush` / `review-pr` | Compara el diff con las decisiones que afectan a los ficheros tocados |

Contradecir una decisión no está prohibido: se hace escribiendo la que la sustituye, no en silencio.

## 6. Cambios en el repo

### 6.1 Nuevo

| Pieza | Qué hace | Esfuerzo |
|---|---|---|
| Skill `idea-to-issue` | Issue con la nota → Example Mapping → decisiones en `proposed` → tareas en el issue. Es la entrada por defecto | M |
| Skill `record-decision` | Redacta decisiones desde la conversación, actualiza el índice y gestiona la sustitución. La usan `idea-to-issue`, `debug-root-cause` (descartes) y el nivel SDD | S |
| Snippet de niveles para `AGENTS.md` | La tabla de la sección 3 y las señales de subir o bajar, en ~20 líneas. Lo instala `generate-project-context` | S |

### 6.2 Adaptar

| Pieza | Cambio | Esfuerzo |
|---|---|---|
| `generate-project-context` | `docs/decisions/` en lugar de `docs/adr/`, plantilla corta con `type` y `affects`, glosario en `AGENTS.md` (DDD ligero). En brownfield, ofrece mover los ADRs existentes a `docs/decisions/` como tipo `architecture` (con `git mv`); si la persona no quiere, conviven y el índice los enlaza | S |
| `agents/implement.md` | Un test cada vez (#18), orden de preferencia y criterio de test (#11), commit en rojo separado, no tocar tests ya en rojo, leer el índice de decisiones | S–M |
| `task-done` | Marcar tareas en el checklist de un issue (`gh`), además de `tasks.md`. El issue es el que se le pasa o el enlazado en la rama; sin etiqueta. Comprobar que los tests del commit en rojo no cambiaron | M |
| `review-prepush`, `code-reviewer` | Ejemplos con test, tests intactos tras el rojo, choques con decisiones. Llamadores fuera del diff (#10) | S–M |
| `sdd-decisions` | Además de qué se pregunta, qué se registra. Renombrar a `decisions` cuando deje de ser solo de SDD | S |
| `idea-to-spec`, `spec-to-plan`, `plan-to-tasks` | Solo para el nivel SDD. Borradores sin aprobación en el chat (#13), plan de diseño y trabajos acotados (#15), y al cerrar: decisiones a `docs/decisions/` y spec `obsolete` | M |
| `sdd-next` | Se retira en la fase 5: el tablero de GitHub da el estado de los issues, y en el nivel SDD basta con mirar el `status` de los artefactos. Quitar sus referencias del README y de `docs/sdd/` | S |
| `setup-guardrails-python` | Tests de arquitectura con import-linter; complejidad con ruff (idea 20) | S |
| Documentación | README con los niveles como entrada; la guía personal integrada; `docs/sdd/` queda como guía del último nivel | M |

### 6.3 Sin cambios

`debug-root-cause` (solo enlazar con `record-decision` para los descartes), `review-pr`, `review-context`, `review-report`, `finding-verifier`, `security-auditor`, `test-engineer`, el Stop hook y la confirmación al forzar el push.

## 7. Valoración de las issues abiertas

| Issue | En la v2 | Decisión |
|---|---|---|
| #18 TDD de un test cada vez | Es el paso 5 del flujo y la base de la protección mecánica | **Fase 2** |
| #11 orden de preferencia y criterio de test | El criterio de test decide cuándo una tarea exige test. Toca `implement.md` igual que #18: juntas | **Fase 2** |
| #3 tests de activación | La v2 crea y renombra skills; protege contra que dejen de activarse. Solo la suite de activación | **Fase 0** |
| #13 borradores sin aprobación en el chat | Aplica a todo artefacto, también a las decisiones y al issue | **Fase 3** (en `idea-to-issue` desde el principio) y **fase 5** (skills de SDD) |
| #15 plan de diseño y trabajos acotados | El tamaño acotado pasa a la sección 4.3; el nivel de detalle del plan solo afecta al SDD | Absorber: **fases 3 y 5** |
| #10 llamadores fuera del diff | Independiente; barata y atrapa bugs reales | **Fase 4** |
| #8 revisor de otro modelo | Trabajando solo, lo más parecido a otro par de ojos | Backlog con prioridad; tras la fase 4 |
| #7 veredicto ligado al hash del diff | Independiente; ahorra reviews repetidas | Backlog |
| #9 prompt injection | Independiente; `docs/decisions/` y los issues son texto nuevo que el agente lee | Backlog |
| #2 revisión entre tareas | Su `## Decisiones` en `tasks.md` queda superado por `docs/decisions/`. Revisar cada tarea multiplica tokens; la puerta por tarea es el nivel A | **Cerrar** con referencia a este plan |

## 8. Qué cambia en el plan de mejoras

- **Idea 6** (Stop hook que marca «implementar sin spec o plan aprobados»): descartada en esa forma, porque obligaría a hacer SDD. Si se retoma, la regla sería «código editado en la rama base» y «código sin ningún test tocado» según el criterio de #11.
- **Idea 4** (adherencia a `tasks.md`): baja al backlog. Con tareas en el issue y un commit por tarea, se resuelve casi sola mirando los commits.
- **Choque 3.3** (dónde se registran las decisiones): resuelto por la sección 5.
- **Choque 3.1** (¿todo cambio lleva test?): resuelto en la fase 2 con el criterio de #11 ([D-0011](decisions/0011-criterio-de-test.md)).
- **Secciones 4 y 5** (PR #6 y orden propuesto): desfasadas; la PR #6 y #14 están mergeadas. El orden pasa a ser el de la sección 9 de este documento.

Cuando este plan se apruebe, `plan-de-mejoras.md` se actualiza para remitir aquí en lo que se solapa.

## 9. Fases

Cada fase deja el repo usable. Las fases 1 y 2 aportan valor aunque no se haga el resto.

| Fase | Qué | Por qué en este orden |
|---|---|---|
| 0 | Suite de activación de #3 con las skills actuales | Línea base antes de crear y renombrar skills |
| 1 | `docs/decisions/` en `generate-project-context`, `record-decision`, criterio de registro en `sdd-decisions` | Es el requisito de «no perder los porqués» y funciona también con el SDD actual |
| 2 | #18 + #11 en `implement`, commit en rojo y comprobación en `task-done` | La protección de los tests es la base del nivel B |
| 3 | `idea-to-issue`, `task-done` sobre issues, snippet de niveles en `AGENTS.md` | El flujo por defecto; depende de 1 y 2 |
| 4 | Comprobaciones nuevas en la review y #10 | Cierra el círculo: ejemplos, tests intactos y decisiones |
| 5 | Adelgazar el SDD (#13, #15, cierre con decisiones), retirar `sdd-next`, documentación y versión del plugin | Con el flujo nuevo probado, el SDD queda como último nivel |
| Backlog | #8, #7, #9, ideas restantes del plan de mejoras | Sin evidencia de que hagan falta todavía |

**Prueba antes de la fase 5:** usar el flujo B en un trabajo real (por ejemplo, en `ia-testing`) y medir lo mismo que en #13 y #15: tiempo, caracteres leídos y preguntas que eran decisiones.

## 10. Riesgos

| Riesgo | Mitigación |
|---|---|
| Las decisiones se dejan de escribir porque no hay puerta que lo exija | El agente las redacta y la persona solo revisa; la parada del nivel B incluye revisarlas |
| El índice crece y llena el contexto | Una línea por decisión y filtro por `affects`. Si pasa de unas 100 líneas, partir por `type` |
| La persona aprueba las decisiones sin leerlas, igual que las specs | Son cortas por diseño (plantilla de 4 secciones) y en lenguaje de negocio |
| El flujo con issues necesita red y `gh` | `tasks.md` sigue siendo válido para `task-done`; el issue es la opción por defecto, no la única |
| El agente traduce mal un ejemplo a test | Leer el diff final; nivel A para lo delicado |
| Dos flujos (issues y SDD) que mantener | El SDD comparte decisiones, `task-done`, `implement` y la review; solo cambian la entrada y los artefactos de trabajo |

## 11. Decisiones de este plan

Las tomadas en la conversación del 2026-10-23. Al aprobar el plan, serán los primeros registros de `docs/decisions/` en este repo.

| # | Decisión | Alternativas descartadas |
|---|---|---|
| 1 | El proceso se ajusta al riesgo; el SDD completo es el último nivel | SDD como camino por defecto (coste medido en #13 y #15) |
| 2 | Las decisiones viven en `docs/decisions/`, un fichero por decisión con índice | Fichero único (llena el contexto); seguir en `docs/adr/` (no cubre reglas ni descartes) |
| 3 | El agente redacta las decisiones tras planificar con la persona, y ella las revisa | Que las escriba la persona (más lento) |
| 4 | El trabajo en curso (nota, mapa, tareas) vive en un issue de GitHub | Fichero `docs/work/` en el repo |
| 5 | Puerta por defecto en el mapa de ejemplos (B), con A y C según el riesgo | Parada en cada tarea siempre (A); ninguna parada (C) |
| 6 | `spec.md` y `plan.md` son documentos de trabajo; lo que perdura son las decisiones y los tests | Spec viva mantenida al día |

## 12. Preguntas resueltas

Resueltas el 2026-10-24.

1. **`sdd-next`:** se retira (fase 5). El tablero de GitHub cubre el estado de los issues y no compensa mantener una segunda vista.
2. **Cómo se reconoce un issue de trabajo:** sin etiqueta. `task-done` y la review usan el issue que se les pasa o el enlazado en la rama, y buscan el checklist `- [ ] T1.`. Si más adelante algo necesita listar trabajos, se añade una etiqueta entonces.
3. **Nombres:** `idea-to-issue` (paralelo a `idea-to-spec`: dice qué produce) y `record-decision`. Las skills y los agentes se escriben siempre en inglés, también la `description`; la suite de activación de la fase 0 comprueba que las peticiones en español las activan igual.
4. **Migración de `docs/adr/`:** `generate-project-context` ofrece moverlos en modo brownfield; si la persona no quiere, conviven y el índice los enlaza.
