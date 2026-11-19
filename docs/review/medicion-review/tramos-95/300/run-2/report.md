## Summary and verdict

La rama modifica la recopilación de hechos para las revisiones pre-push y documenta una medición del proceso. El nombre de la rama no permite identificar una tarea correspondiente a esos cambios; la revisión se ha basado en los commits.

Se ha confirmado un fallo en el flujo cuando falla el script de hechos.

**Verdict:** FIX BEFORE PR

## Critical

None.

## Required

#### R1 El fallo del script omite la verificación y deja la revisión sin alcance

- **Location:** [skills/review-prepush/SKILL.md:37](repo/skills/review-prepush/SKILL.md:37)
- **Problem:** Si `review_facts.py` falla, la instrucción salta directamente al paso 3. Esto omite las verificaciones del paso 2 y puede dejar al revisor sin una base para construir el diff.
- **Why it fails / scenario:** Una base configurada que no existe hace fallar el script antes de imprimirla; el flujo continúa hacia la revisión sin las comprobaciones requeridas ni un alcance definido.
- **Fix:** Ejecutar el paso 2 también cuando falle el script y determinar la base y el alcance mediante una alternativa segura. Si no pueden determinarse, indicar que no se puede emitir un veredicto.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 1 TODO/FIXME sin ticket

- **Location:** [scripts/check.sh:1419](repo/scripts/check.sh:1419)
- **Problem:** El script de hechos lista un TODO sin ticket en esta línea.
- **Why it fails / scenario:** No tiene una referencia de seguimiento en la misma línea.
- **Confidence:** high
- **Source:** verification
- **Impact / cost:** low / S

## What's done well

- [review_facts.py:119](repo/skills/review-context/scripts/review_facts.py:119) distingue los errores que impiden ejecutar la auditoría de los resultados válidos que contienen problemas.
- [medicion-review.md:16](repo/docs/review/medicion-review.md:16) documenta que la medición no ejercita la detección de tareas ni su auditoría.

## Seams

La revisión de las conexiones entre los dos tramos no encontró hallazgos.

## Verification

- Commands found in AGENTS.md: ninguno; no existe un `AGENTS.md` en la raíz.
- Run: `python3 .agents/skills/review-context/scripts/review_facts.py main` → completado; dos tramos, ninguna tarea detectada y un TODO sin ticket.
- Semgrep: no ejecutado; el comando puede escribir archivos y acceder a la red, en conflicto con las restricciones de esta ejecución.
- Auditoría de tareas: no aplicable; el script no detectó una tarea de rama.
- Callers, tramo 1: un contrato cambiado y dos referencias externas al diff revisadas; no se detectaron llamadores rotos.
- Callers, tramo 2: ningún contrato cambiado ni llamada externa.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: PASS critical=0 required=1 uncertain=0