---
id: T9
title: Documentar cómo elegir el modelo de los subagentes en Codex
status: done
depends_on: []
examples: []
verification: scripts/check.sh
---
**Propósito:** documentación: explicar cómo se elige por llamada el modelo de los subagentes de la review en Codex (S2).

**Dentro:** una sección en `docs/review/README.md`, junto a "Modelo por persona": cómo se pasa el modelo en la llamada (`codex exec -m …` / config de `[agents]`), qué hereda un subagente sin `model`, y la recomendación de usar un modelo más barato para las reviews locales. Se comprueba contra la documentación de Codex antes de escribirla.

**Fuera:** fijar un modelo en `agents/` o en los adaptadores.

**Flag:** ninguno.
