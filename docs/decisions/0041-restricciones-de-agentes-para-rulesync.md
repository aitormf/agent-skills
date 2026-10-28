---
id: D-0041
title: Las restricciones de cada agente van también en un bloque por herramienta, generado por build-agents.py, para que rulesync no las pierda
type: architecture
status: accepted
date: 2026-10-28
affects: [agents/, scripts/build-agents.py]
supersedes: null
superseded_by: null
issue: null
---

# D-0041: Las restricciones de cada agente van también en un bloque por herramienta, generado por build-agents.py, para que rulesync no las pierda

## Contexto

Con atril, lo que se fija de forma permanente llega a cada herramienta con rulesync. En la prueba del plan v3 (§3.1), rulesync quitó `tools` y `skills` de un agente cuando iban en el primer nivel del frontmatter, y los conservó dentro de un bloque `claudecode:`. Un `code-reviewer` sin `tools` deja de ser de solo lectura.

## Decisión

- `scripts/build-agents.py` escribe al final del frontmatter de cada `agents/*.md` un bloque `claudecode:` (`tools`, `skills`, `model`) y uno `opencode:` (`mode` y el mapa `permission`, el mismo del adaptador), desde los campos de primer nivel. `--check` falla si no están al día.
- El primer nivel no cambia: es lo que lee Claude Code al cargar el plugin.
- No hay bloque `codexcli:`: Codex no aplica `sandbox_mode` por agente, y el bloque prometería una restricción que no existe.
- Cada skill y cada agente declara `kind` y sus relaciones (`uses`, `delegates`, `related`), y un agente lleva en `uses` las skills que precarga.

## Alternativas descartadas

- Escribir los bloques a mano: se desincronizan de `tools:` sin que nadie lo note.
- Mover las restricciones solo al bloque: Claude Code las lee del primer nivel.
- Que atril cargue los agentes bajo demanda: leído como fichero, un agente no tiene restricciones. Se fijan con `atril expose`.

## Cómo se hace cumplir

`scripts/check.sh`: `build-agents.py --check` («agentes generados al día») y «atril: kind, nombre y relaciones de skills y agentes».
