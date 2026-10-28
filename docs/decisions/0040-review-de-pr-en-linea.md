---
id: D-0040
title: En CI, la review de PR publica cada hallazgo en su línea desde un bloque JSON que el job publish valida contra el diff; nunca aprueba ni pide cambios
type: architecture
status: accepted
date: 2026-10-28
affects: [skills/review-pr/, skills/review-report/]
supersedes: null
superseded_by: null
issue: null
---

# D-0040: En CI, la review de PR publica cada hallazgo en su línea desde un bloque JSON que el job publish valida contra el diff; nunca aprueba ni pide cambios

## Contexto

El comentario único de la review era largo: todos los hallazgos enteros, lo bien hecho y la verificación. Asustaba y obligaba a buscar cada `fichero:línea` a mano (plan v3, fase 1).

## Decisión

- `review-pr --inline` añade al informe un bloque ```` ```json review-kit ```` con el veredicto, el resumen y los hallazgos (`review-report` §4.3).
- El job `publish` lee ese bloque como datos: comprueba cada `path` y `line` contra el diff de la PR, publica los que caben en una review con `event: COMMENT` y pone el resto enteros en el resumen. Sigue sin ejecutar ningún modelo (D-0027), y su script va en el propio workflow, no en el artefacto del job `review`, que el modelo podría haber escrito.
- El resumen se edita en cada run; los comentarios en línea se quedan. Un hallazgo que ya tiene comentario del bot en la misma línea y con el mismo título no se repite.
- Sin bloque válido, se publica el informe en Markdown como antes.

## Alternativas descartadas

- Sacar los hallazgos del Markdown: el job tendría que interpretar texto libre que escribe el modelo.
- Que el modelo publique la review: necesitaría token en el job que lee el diff (D-0027).
- Borrar los comentarios anteriores en cada run: se perderían las respuestas de la persona.

## Cómo se hace cumplir

`scripts/check.sh` («review: the publish job comments each finding on its line…»): ejecuta el script del workflow contra un `gh` falso y comprueba que solo comenta líneas del diff, nunca aprueba ni pide cambios, no repite hallazgos, solo edita los comentarios del bot y cae al Markdown si el bloque no es válido.
