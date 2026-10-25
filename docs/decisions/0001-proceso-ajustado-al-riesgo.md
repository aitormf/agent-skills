---
id: D-0001
title: El proceso se ajusta al riesgo; el SDD completo es el último nivel
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/, docs/sdd/]
supersedes: null
superseded_by: null
issue: null
---

# D-0001: El proceso se ajusta al riesgo; el SDD completo es el último nivel

## Contexto

El kit era un SDD por defecto: idea → spec → plan → tareas, con dos aprobaciones de documentos largos. En #13 y #15 costó unas 2h20 y unos 50k caracteres de lectura para 6–8 decisiones reales.

## Decisión

Cada tarea sigue el nivel que le toca por tamaño y riesgo (plan-v2, sección 3): vibe coding, prompt directo, test y arreglo, `debug-root-cause`, issue con Example Mapping (por defecto) y SDD para reglas delicadas o diseño de verdad.

## Alternativas descartadas

- SDD como camino por defecto: el coste medido en #13 y #15.

## Cómo se hace cumplir

No se automatiza. Las señales para subir o bajar de nivel irán en el snippet de `AGENTS.md` (fase 3).
