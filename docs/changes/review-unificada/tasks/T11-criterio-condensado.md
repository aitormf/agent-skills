---
id: T11
title: code-reviewer con el criterio condensado en lugar de precargar code-review-and-quality
status: done
depends_on: [T3]
examples: [E25, E26, E27, E28]
verification: scripts/check.sh
---
**Propósito:** refactor del contexto de `code-reviewer`: deja de precargar `code-review-and-quality` (22 KB) y lleva en su cuerpo solo el criterio que produce hallazgos (R6, D-0045).

**Dentro:** un inventario, sección por sección de `code-review-and-quality`, de dónde queda cada una (en el agente, ya en `review-report`, en la pasada de seguridad o de rendimiento, o descartada con su motivo: Change Descriptions, Review Speed, Handling Disagreements, Multi-Model, la plantilla de checklist), en el cuerpo de la PR; una sección "Judgement" en `agents/code-reviewer.md`, de unos 1,5–2 KB, con lo que el inventario conserva: remedios estructurales con nombre (proponer el movimiento, no solo el problema), mover complejidad no es reducirla (contar conceptos), condicionales esparcidos en flujos ajenos, ficheros que crecen en vez de partirse, código muerto que deja el cambio (listarlo por nombre), no suavizar un bug ni aprobar sin evidencia, cuantificar cuando se pueda, el código de agente necesita más escrutinio; con `--deep`, leer además la skill completa; `skills:` sin `code-review-and-quality`; adaptadores regenerados; checks en `check.sh` nombrados E25–E28 que comprueban que cada regla del inventario marcada "en el agente" sigue en él (una lista de frases clave en el propio check).

**Fuera:** editar `code-review-and-quality` (copia de upstream, se sigue usando en la sesión principal); las plantillas de las otras personas (T13).

**Flag:** ninguno.
