---
id: T2
title: review-prepush revisa por tramos con una pasada de costuras
status: done
depends_on: [T1]
examples: [E18, E19, E20, E21, E22, E23, E24]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: con varios tramos en los hechos, `review-prepush` lanza un `code-reviewer` por tramo, verifica contra HEAD y añade una pasada de costuras (R4, D-0060).

**Dentro:** el texto de `review-prepush` (brief por tramo con su diff `a..b`, la tarea, los hechos completos y la orden de leer `git diff base...HEAD` antes de informar algo como ausente; la pasada de costuras con un `code-reviewer` más, sin historial; la fusión de los hallazgos repetidos; el modo sin subagentes), lo que necesiten `agents/code-reviewer.md` y `agents/finding-verifier.md` (confirmar solo lo que es cierto en HEAD), los adaptadores regenerados con `scripts/build-agents.py` y los tests de texto en `scripts/check.sh`.

**Fuera:** `review-pr`; la caché de veredictos (D-0042), que no cambia; lo que bloquea el push, que sigue siendo un Critical confirmado.

**Flag:** ninguno. Con un solo tramo, la review es la de hoy.
