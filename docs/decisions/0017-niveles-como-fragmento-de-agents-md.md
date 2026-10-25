---
id: D-0017
title: Los niveles de proceso son un fragmento aparte que generate-project-context copia en AGENTS.md
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/generate-project-context/]
supersedes: null
superseded_by: null
issue: null
---

# D-0017: Los niveles de proceso son un fragmento aparte que generate-project-context copia en AGENTS.md

## Contexto

La tabla de niveles y las señales de subir o bajar (plan-v2, sección 3) tienen que estar en el `AGENTS.md` de cada proyecto, también en los que ya tienen uno. Con ellos van la regla de evidencia fresca (#11, D-0011) y el glosario (D-0016).

## Decisión

Viven en `skills/generate-project-context/assets/<idioma>/AGENTS-levels.md`, unas 25 líneas. `generate-project-context` lo copia tal cual en los `AGENTS.md` nuevos y lo propone como diff en los existentes; solo se rellena el glosario. Las plantillas de `AGENTS.md` marcan dónde va.

## Alternativas descartadas

- Dentro de la plantilla de `AGENTS.md`: en brownfield habría que recortarlo a mano de la plantilla, y se mezcla con lo que sí se adapta a cada proyecto.
- En una skill que se carga a demanda: el nivel se elige antes de saber qué skill cargar, así que tiene que estar en lo que se lee en cada sesión.

## Cómo se hace cumplir

No se automatiza.
