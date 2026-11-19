## Summary and verdict

La rama reúne datos para las revisiones mediante `review_facts.py` y añade el tratamiento de TODO sin ticket. Los commits permiten inferir ese objetivo, aunque el nombre de la rama no lo refleja. Se han confirmado dos problemas en el flujo de revisión que conviene corregir antes de abrir el PR.

**Verdict:** FIX BEFORE PR

## Critical

None.

## Required

#### R1 La revisión omite las verificaciones si falla el script de hechos

- **Location:** [skills/review-prepush/SKILL.md:37](repo/skills/review-prepush/SKILL.md:37)
- **Problem:** La instrucción de recuperación salta directamente al paso 3 cuando `review_facts.py` no puede ejecutarse.
- **Why it fails / scenario:** Si falta Python o no se puede resolver la base, se omite el paso 2, incluidas las comprobaciones configuradas en `AGENTS.md` y Semgrep. También pueden faltar la base y el comando de diff que necesita el revisor.
- **Fix:** Continuar por el paso 2 y recuperar explícitamente los datos necesarios, o detener la revisión si no se pueden determinar.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 La auditoría puede usar una base distinta de la revisión

- **Location:** [skills/review-context/scripts/review_facts.py:115](repo/skills/review-context/scripts/review_facts.py:115)
- **Problem:** La llamada a `task_done.py --audit` no recibe la base resuelta para la revisión; el auditor resuelve la suya por separado.
- **Why it fails / scenario:** Si la base de revisión es `develop` y `origin/HEAD` apunta a `main`, el diff se revisa frente a `develop`, pero la protección de tests y las dependencias se comprueban frente a `main`. La auditoría puede omitir problemas o producir hallazgos incorrectos.
- **Fix:** Permitir que el auditor reciba y utilice la base resuelta y añadir una prueba con bases divergentes.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 1 TODO/FIXME sin ticket

- **Location:** [scripts/check.sh:1419](repo/scripts/check.sh:1419)
- **Problem:** El script de hechos detecta un TODO sin ticket; aparece dentro de datos preparados para una prueba.
- **Why it fails / scenario:** La detección automática lo incluye en el informe de revisión.
- **Confidence:** high
- **Source:** verification
- **Impact / cost:** low / S

## What's done well

- La medición documenta sus límites y la variación entre ejecuciones, lo que facilita interpretar los resultados ([docs/review/medicion-review.md:621](repo/docs/review/medicion-review.md:621)).

## Verification

- Commands found in AGENTS.md: ninguno; no hay `AGENTS.md` en la raíz. No se ejecutaron comandos de verificación del proyecto.
- Run: `python3 .agents/skills/review-context/scripts/review_facts.py main` → completado; un tramo, sin carpeta de tarea identificada.
- Semgrep: falló porque no había un directorio temporal utilizable; no se comprobó el diff con Semgrep.
- Callers: un contrato cambiado; el revisor no identificó llamadas fuera del diff. No se comprobaron invocaciones dinámicas externas al repositorio.
- Findings refuted by the verifier: 0. Ambos hallazgos se confirmaron y se clasificaron como Required.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: PASS critical=0 required=2 uncertain=0