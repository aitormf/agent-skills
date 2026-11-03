---
id: D-0046
title: Los subagentes de la review arrancan sin el historial de la sesión principal; en Codex, con fork_turns none
type: architecture
status: proposed
date: 2026-11-03
affects: [skills/review-prepush/, skills/review-pr/]
supersedes: null
superseded_by: null
issue: null
---

# D-0046: Los subagentes de la review arrancan sin el historial de la sesión principal

## Contexto

`review-prepush` promete un revisor en contexto limpio, pero `spawn_agent` de Codex hereda todo el historial por defecto (`fork_turns` vale `all`). En 16 de los 18 subagentes medidos en T1 el hilo arranca con ese historial, así que no era independiente de lo que había leído la sesión principal. Su primera llamada lleva de 41.000 a 50.000 tokens de entrada, frente a unos 21.000 en los dos subagentes lanzados con `fork_turns: "none"` (`docs/review/medicion-review.md`).

## Decisión

Las skills de review lanzan cada persona sin historial heredado: en Codex, con `fork_turns: "none"`. El encargo lleva todo lo que necesita: cómo leer el cambio, los resultados de la verificación, la tarea y los límites.

## Alternativas descartadas

- Heredar el historial (el valor por defecto): paga el contexto de la sesión principal en cada llamada de cada subagente y quita independencia al revisor.
- Fijarlo en la configuración de cada persona: `fork_turns` es un parámetro de la llamada a `spawn_agent`, no de la persona.

## Cómo se hace cumplir

`check.sh` comprueba que las dos skills lo dicen. La medición de `tests/review-sandbox/` registra el historial heredado de cada subagente.
