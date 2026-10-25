---
id: D-0020
title: code-reviewer busca llamadores fuera del diff y choques con decisiones, con grep y con límites fijos
type: architecture
status: accepted
date: 2026-10-24
affects: [agents/code-reviewer.md]
supersedes: null
superseded_by: null
issue: "#10"
---

# D-0020: code-reviewer busca llamadores fuera del diff y choques con decisiones, con grep y con límites fijos

## Contexto

Un cambio de firma, de valor de retorno o de comportamiento puede romper un fichero que el diff no toca (#10). Y la review debe comparar el diff con las decisiones aceptadas que afectan a los ficheros tocados (plan-v2, sección 5.4). Las dos cosas leen fuera del diff y pueden disparar el coste de una review que debe ser rápida.

## Decisión

- Las dos comprobaciones van en el cuerpo de `code-reviewer` («Beyond the diff»), así que las hacen `review-prepush` y `review-pr` sin cambiar sus pasos.
- **Llamadores:** solo de los símbolos cuyo contrato cambia; búsqueda con Grep; como mucho 10 símbolos y 20 usos por símbolo, leyendo solo el sitio de la llamada. El revisor dice en una línea qué miró y qué no.
- **Decisiones:** lee solo el índice, filtra por *Affects* y por los `D-NNNN` citados en líneas cambiadas, y abre como mucho 10. Un choque con una decisión aceptada sin otra que la sustituya en el diff es Required.

## Alternativas descartadas

- No pedirlo de forma explícita (como hasta ahora): el revisor se queda en el diff.
- Un grafo de llamadas o un servidor de lenguaje: depende del lenguaje y de herramientas que la review no tiene.
- Una persona aparte para los llamadores: más tokens y otra pieza que mantener.
- Filtrar las decisiones por *Affects* con un script: el índice es corto por diseño y es lo mismo que ya hace `implement` al leerlo.
- De la propuesta de #10, suponer la carga del sistema y el campo «If we skip it»: no son llamadores fuera del diff; quedan fuera de esta fase.

## Cómo se hace cumplir

No se automatiza. `tests/review-sandbox` tiene un bug que solo se ve fuera del diff (B6 en `EXPECTED.md`).
