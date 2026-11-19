## Summary and verdict

La rama reúne los hechos de revisión en `review_facts.py` e integra su salida en `review-prepush`. Los mensajes de commit describen ese trabajo, aunque el nombre de la rama apunta a otra tarea. Se han confirmado dos problemas que conviene corregir antes de abrir el PR.

**Verdict:** FIX BEFORE PR

## Critical

None.

## Required

#### R1 El fallo del script de hechos salta las verificaciones

- **Location:** [skills/review-prepush/SKILL.md:37](repo/skills/review-prepush/SKILL.md:37)
- **Problem:** Si `review_facts.py` falla, la instrucción indica continuar directamente en el paso 3, omitiendo el paso 2.
- **Why it fails / scenario:** Una revisión puede continuar sin ejecutar las comprobaciones configuradas ni Semgrep cuando no se pueden obtener los hechos.
- **Fix:** Continuar con el paso 2 y definir cómo obtener la base y la tarea necesarias para la revisión cuando falle el script.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 La auditoría de una rama de plan carece de prueba

- **Location:** [skills/review-context/scripts/review_facts.py:106](repo/skills/review-context/scripts/review_facts.py:106)
- **Problem:** Las pruebas añadidas no ejercitan la ruta específica de una rama `<change>/plan`.
- **Why it fails / scenario:** Las pruebas seguirían pasando si esa rama dejase de ejecutar la auditoría del plan completo o pasase incorrectamente un identificador de tarea.
- **Fix:** Añadir un caso que compruebe la identificación del plan y la llamada a la auditoría sin identificador de tarea.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 1 TODO/FIXME without a ticket

- **Location:** [scripts/check.sh:1419](repo/scripts/check.sh:1419)
- **Problem:** El script de hechos ha listado esta ubicación como comentario sin ticket.
- **Why it fails / scenario:** La referencia no identifica una tarea de seguimiento.
- **Fix:** Añadir una referencia de seguimiento si corresponde.
- **Confidence:** high para la salida del script; ubicación no verificada manualmente.
- **Source:** verification
- **Impact / cost:** low / S

## What's done well

- La prueba de rama de tarea comprueba que los hechos incluyan tanto la salida como el código de la auditoría; otra prueba comprueba que los demás hechos sigan disponibles si falta el script de auditoría ([scripts/check.sh:1412](repo/scripts/check.sh:1412)).

## Verification

- Commands found in AGENTS.md: none; no existe un `AGENTS.md` en la raíz.
- `python3 .agents/skills/review-context/scripts/review_facts.py main` → completado; un tramo, sin tarea identificada.
- No verification commands found in AGENTS.md — nothing was run.
- Semgrep: el comando falló porque no hay un directorio temporal utilizable; no hay herramientas MCP de Semgrep disponibles.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- Callers: un símbolo cambiado; no se encontraron llamadas externas al diff; la invocación dinámica fuera del repositorio no se comprobó.

REVIEW_RESULT: PASS critical=0 required=2 uncertain=0