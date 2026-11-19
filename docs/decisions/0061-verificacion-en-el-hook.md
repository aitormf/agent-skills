---
id: D-0061
title: En el push de un agente, el hook harness-review ejecuta la verificación de [review] verify (leída de la rama base) y Semgrep antes de lanzar al revisor, y le pasa los resultados en un fichero; el revisor no los vuelve a ejecutar
type: architecture
status: accepted
date: 2026-11-19
affects: [skills/review-prepush/, skills/review-context/, .harness-config.toml, skills/setup-guardrails-python/]
supersedes: null
superseded_by: null
issue: 97
---

# D-0061: La verificación la ejecuta el hook

## Contexto

La review del push la ejecuta el hook `harness-review` con un revisor de otra familia (D-0055, D-0056). Hoy es ese revisor quien busca los comandos en `AGENTS.md` y los ejecuta (`review-context` §2). Con Codex en `read-only` no hay directorio temporal, y fallan `check.sh`, `uv` y Semgrep (#97). La review se queda sin tests ni Semgrep y el veredicto no lo refleja. Además, los comandos salen de un texto libre que lee el modelo y que la rama del agente puede cambiar.

## Decisión

- Los comandos están en `[review] verify` de `.harness-config.toml`, una lista de comandos que se lee de la rama base (D-0054). Así la rama no puede cambiarlos.
- En el push de un agente, el hook los ejecuta desde la raíz del repo, después del gate y antes de lanzar al revisor. También ejecuta `semgrep_added.py`, salvo con `[review] semgrep = false`.
- Los resultados van a un fichero, que el hook pasa al revisor con `REVIEW_KIT_VERIFICATION`. Si la variable está, `review-prepush` no ejecuta nada: cita el fichero y trata los hallazgos de Semgrep como candidatos.
- Sin la clave, nada cambia: el revisor hace la verificación como hoy.

## Alternativas descartadas

- Dar escritura al sandbox de Codex (`workspace-write` o un `TMPDIR` propio): el revisor sigue ejecutando comandos arbitrarios, cada familia necesita su propio arreglo y la verificación sigue dependiendo del modelo.
- Que el hook lea los comandos de `AGENTS.md`: es texto libre, no hay forma fiable de sacarlos sin modelo y la rama puede cambiarlo.
- Pasar los resultados en el prompt: la salida puede ser larga y el prompt de Claude y el de Codex son distintos. Un fichero sirve para los dos.

## Cómo se hace cumplir

Tests E1–E6 y E10–E16 del cambio `97-verificacion-en-el-hook` en `scripts/check.sh`, con un revisor falso que comprueba que recibe el fichero.
