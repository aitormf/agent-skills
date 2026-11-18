---
id: T5
title: review-prepush reúne los hechos con una llamada a review_facts.py
status: done
depends_on: [T2, T4]
examples: [E14]
verification: scripts/check.sh
---

**Propósito:** refactor: los pasos 1 y 2 de `review-prepush` sustituyen los comandos git y la auditoría por una llamada al script, y su salida va tal cual en el brief del `code-reviewer` (R4).

**Dentro:** el texto de `review-prepush` y los tests de texto de `scripts/check.sh` que nombran los pasos antiguos (E32, E33 y la auditoría). Los comandos de verificación de `AGENTS.md` y Semgrep se siguen ejecutando como hoy.

**Fuera:** `review-pr`; que el hook calcule los hechos.

**Flag:** ninguno.
