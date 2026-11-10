---
id: D-0049
title: El board manager de Karajan es un paquete Node fino en integrations/karajan-board/ que llama a board.py --json; check.sh pasa sus tests con Node ≥ 22
type: architecture
status: accepted
date: 2026-11-10
affects: [integrations/karajan-board/, skills/task-done/scripts/board.py, scripts/check.sh]
supersedes: null
superseded_by: null
issue: null
---

# D-0049: El manager de Karajan vive en integrations/karajan-board/ y delega en board.py

## Contexto

Karajan carga un backend de tablero como un paquete JS que exporta `createManager({ config, env, run })` y `credentials`. Lo valida con `assertManager` y lo prueba con `runStoryContract` (vitest). Nuestro repo es Markdown y Python, y la lógica del tablero (estados, dependencias, ramas, rama base) está en `skills/task-done/scripts/board.py`.

## Decisión

- El paquete `kj-board-changes` vive en `integrations/karajan-board/`, no en `adapters/`, que es salida generada por `build-agents.py`.
- Es un adaptador fino. Usa el `run` que le pasa Karajan para llamar a `python3 skills/task-done/scripts/board.py --json <cambio>` y traduce la salida al story-contract. La lógica de estados no se duplica en JS.
- `board.py` gana un modo `--json` con id, título, estado del tablero, rama, `depends_on`, `examples`, `tier` y ruta de cada tarea.
- Sus tests (los nuestros y `runStoryContract`) corren en `scripts/check.sh`. Necesitan Node ≥ 22 y las devDependencies del paquete. Si falta Node, `check.sh` falla y dice por qué, no se salta en silencio.

## Alternativas descartadas

- **Repo o paquete npm aparte.** Se versiona separado del formato de tareas que lee, y un cambio en el frontmatter rompería el manager sin que `check.sh` lo viera.
- **Reescribir el tablero en JS.** Habría dos implementaciones de D-0030 y D-0034 que pueden divergir.
- **Saltar los tests de JS si no hay Node.** Un check que se salta solo deja pasar un manager roto.

## Cómo se hace cumplir

En `scripts/check.sh`:

- la salida de `board.py --json`, comprobada en Python;
- `npm test` en `integrations/karajan-board/`.
