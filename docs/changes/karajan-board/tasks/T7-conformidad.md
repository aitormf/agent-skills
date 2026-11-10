---
id: T7
title: El manager pasa la suite runStoryContract de Karajan
status: todo
depends_on: [T3, T4]
examples: [E27]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: la suite oficial de conformidad del story-contract corre en `check.sh` contra un repo de prueba con un cambio de tres tareas.

**Dentro:** `runStoryContract("kj-board-changes", makeManager)` (vitest) con un `makeManager` que monta el repo de prueba en un directorio temporal.

**Fuera:** si la suite exige que `create` o `move` escriban (pregunta del mapa), no se fuerza el manager: se para y se pide la decisión a la persona. Si cambia D-0048, va en otra decisión.

**Flag:** ninguno.
