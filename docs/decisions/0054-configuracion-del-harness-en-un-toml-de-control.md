---
id: D-0054
title: La configuración del harness que leen sus scripts va en un único .harness-config.toml en la raíz, que es fichero de control y se lee de la rama base
type: architecture
status: proposed
date: 2026-11-12
affects: [skills/task-done/scripts/gate.py, .harness-config.toml, skills/setup-guardrails-python/]
supersedes: null
superseded_by: null
issue: null
---

# D-0054: La configuración del harness va en un .harness-config.toml de control

## Contexto

R7 de control-del-flujo deja que el proyecto amplíe la lista de ficheros de control «en un fichero propio» sin nombrarlo, y T4 lo implementó como `.kit-control`, un patrón por línea. Ese fue el primer fichero de configuración del kit que lee un script: hasta entonces la configuración iba en prosa en `AGENTS.md`, para los modelos. Además, la lista solo se podía ampliar, y en este repo cada tarea añade sus tests a `scripts/check.sh`, que es de control por defecto. El frente de la review multi-agente (#8) también necesita configuración que lean scripts: qué revisor, con qué modelo y con qué reserva.

## Decisión

La configuración del harness que leen sus scripts va en un solo fichero, `.harness-config.toml`, en la raíz del proyecto, con una tabla por componente. El gate usa `[gate.control]`, donde `add` añade patrones a la lista por defecto y `remove` los quita. El fichero es siempre de control, aunque se intente quitar con `remove`. Se lee siempre de la rama base, nunca de la rama que se comprueba. Si el de la base no es válido, el gate sale con 2 (no puede comprobar). Lo que se escribe para los modelos sigue en `AGENTS.md`.

## Alternativas descartadas

- **`.kit-control` con `!patrón`**: un fichero suelto por cada cosa que se configura, con una sintaxis propia.
- **Una sección de `AGENTS.md` leída por los scripts**: convertiría todo `AGENTS.md` en fichero de control, y cada tarea que tocara el glosario o las convenciones iría a una PR aparte; además mezcla instrucciones para el modelo con configuración para scripts.
- **`[tool.harness]` en `pyproject.toml`**: ata el gate a Python y vuelve de control todo `pyproject.toml`, que las tareas tocan al añadir dependencias.
- **Visible (`harness-config.toml`)**: la persona lo prefiere oculto, como `.pre-commit-config.yaml`.

## Cómo se hace cumplir

Tests de R7 (E27, E28 y los de `add`, `remove` y fichero no válido) en `scripts/check.sh`. CODEOWNERS sobre `.harness-config.toml`, como requisito de `setup-guardrails-python` (S1).
