---
id: D-0045
title: Hasta 200 líneas de diff, la review usa un solo code-reviewer con pasadas condicionales y el verifier; el fan-out de tres personas queda para diffs mayores o --deep, y los subagentes no reescriben lo que otro ya escribió
type: architecture
status: superseded
date: 2026-11-03
affects: [skills/review-prepush/, skills/review-pr/, skills/review-context/, skills/review-report/, agents/code-reviewer.md, agents/security-auditor.md, agents/test-engineer.md, agents/finding-verifier.md]
supersedes: null
superseded_by: D-0047
issue: null
---

# D-0045: Hasta 200 líneas, un solo code-reviewer con pasadas condicionales; fan-out solo para diffs mayores o con --deep

## Contexto

`review-pr` lanzaba en los tiers 1–2 tres personas en paralelo y el verifier (`docs/review/orchestration-addendum.md`). En el uso real se ejecuta en local, con Codex, antes de abrir la PR: cuatro contextos leen el mismo diff, cargan sus instrucciones (de 18 a 44 KB cada uno) y los hallazgos se escriben tres veces (persona, verifier, informe). En un diff pequeño el coste fijo de cada agente domina, y `code-reviewer` ya revisa seguridad (uno de sus cinco ejes) y aplica los checks de tests de `review-report` §5 cuando va solo. Con tareas de como mucho 200 líneas (D-0044), la mayoría de los diffs son pequeños.

## Decisión

- **Tamaño del diff:** líneas añadidas + borradas, tests incluidos, sin lockfiles (por nombre), ficheros marcados `linguist-generated` en `.gitattributes` ni snapshots; los binarios cuentan 0. Lo calcula `skills/review-context/scripts/diff_size.py`, no el modelo.
- **Hasta 200 líneas**, en `review-prepush` y en `review-pr` (tiers 1–2): un solo `code-reviewer` y, si hay hallazgos, el `finding-verifier`. El reviewer hace siempre la pasada base y la de tests (§5), activa la de seguridad (con `security-checklist.md` y los criterios de `security-auditor`) si el diff toca entrada externa, ficheros o paths, consultas, auth, secretos, dependencias o una ruta de alto riesgo, y la de rendimiento si hay bucles sobre datos, I/O o consultas. Dice en el informe qué pasadas hizo y por qué. En tier 2 la pasada de seguridad es obligatoria.
- **Más de 200 líneas o `--deep`:** fan-out completo como hasta ahora, y el informe avisa de que la tarea pasa del tamaño (D-0044).
- **Tier 0 de `review-pr`:** sin cambios, solo `code-reviewer`.
- **Contexto mínimo:** cada subagente carga solo lo que usa. `code-reviewer` no precarga `code-review-and-quality`: lleva su criterio condensado (sacado de un inventario sección por sección) y la lee completa solo con `--deep`. Los layouts del informe y el bloque JSON viven en una referencia que solo lee la sesión principal. Las personas no llevan plantillas de salida que contradigan `review-report` §3.
- **Salida compacta:** las personas del fan-out devuelven solo hallazgos (§3), sin resumen ni "what's done well"; el reviewer unificado añade un "what's done well"; el verifier devuelve una línea por ID (veredicto y motivo) y el ranking, sin repetir el hallazgo.

## Alternativas descartadas

- Fan-out siempre (diseño anterior): paga tres contextos para diffs donde dos personas aportan poco; es lo que motivó este cambio.
- Un solo reviewer siempre, también en diffs grandes: en un diff grande la atención se diluye y se pierde la independencia de tres contextos, que es donde el fan-out compensa.
- `security-auditor` independiente en tier 2 aunque el diff sea pequeño: con diffs de ≤200 líneas basta la pasada de seguridad obligatoria; queda disponible con `--deep`.
- Quitar el verifier: es lo que mantiene bajos los falsos positivos, y ya se salta cuando no hay hallazgos.
- Que el modelo cuente las líneas: no es determinista ni se puede probar.
- Recortar `code-review-and-quality`: es una copia de upstream y se sigue usando entera en la sesión principal; se deja de precargar en el subagente, no se edita.

## Cómo se hace cumplir

`diff_size.py` con sus casos en `check.sh`; `check.sh` comprueba que `review-prepush`, `review-pr` y `code-reviewer` dicen el umbral y las pasadas. La medición en `tests/review-sandbox/` (`docs/review/medicion-review.md`) compara tokens y hallazgos con el fan-out.
