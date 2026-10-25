---
id: D-0018
title: Las comprobaciones de tests de la review viven en review-report §5 y tienen un solo dueño por review
type: architecture
status: accepted
date: 2026-10-24
affects: [skills/review-report/, agents/code-reviewer.md, agents/test-engineer.md, agents/implement.md, skills/review-pr/, skills/review-prepush/]
supersedes: null
superseded_by: null
issue: null
---

# D-0018: Las comprobaciones de tests de la review viven en review-report §5 y tienen un solo dueño por review

## Contexto

En la fase 4 la review comprueba el criterio de test (D-0011) y la protección de los tests en rojo (D-0012). D-0011 dejaba abierto cómo lo leería `code-reviewer`. En `review-prepush`, `code-reviewer` es la única persona; en `review-pr` corre en paralelo con `test-engineer`, que ya revisa los tests, y las dos personas darían los mismos hallazgos.

## Decisión

- El texto de las comprobaciones de tests (el párrafo del criterio y cómo convertir la salida de `task_done.py --audit` en hallazgos) vive en `review-report` §5, que ya precargan todas las personas de la review.
- Un solo dueño por review: `test-engineer` cuando corre (`review-pr`, niveles 1 y 2); `code-reviewer` cuando es la única persona (`review-prepush`, `review-pr` nivel 0). El comando de la review le dice a `code-reviewer` si `test-engineer` corre a su lado.
- `implement` conserva su copia del párrafo del criterio; `scripts/check.sh` falla si las dos copias no son idénticas.

## Alternativas descartadas

- Copiar el criterio en `code-reviewer` y en `test-engineer`: tres copias, y hallazgos duplicados en `review-pr`.
- Una skill interna solo para el criterio: una pieza más para un párrafo; los agentes de Codex y OpenCode no precargan skills, y `review-report` ya la carga cada persona.
- Enlazar desde las personas a `agents/implement.md`: una vez instalado el plugin, ese fichero no está en el proyecto.
- Que `implement` cargue `review-report`: le metería las reglas de salida de la review para leer un párrafo.

## Cómo se hace cumplir

`scripts/check.sh` («test criterion: same text in implement and review-report»). El reparto de dueños no se automatiza: lo dicen `review-pr`, `review-prepush` y las dos personas.
