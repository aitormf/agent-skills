---
id: D-0060
title: review-prepush revisa la rama por tramos de commits seguidos cuando pasa del umbral que el proyecto activa en .harness-config.toml (sin umbral, la review de siempre), con un code-reviewer por tramo, verificación contra HEAD y una pasada de costuras; los revisores siguen separados
type: architecture
status: accepted
date: 2026-11-18
affects: [skills/review-prepush/, skills/review-context/, .harness-config.toml, agents/code-reviewer.md, agents/finding-verifier.md]
supersedes: D-0047
superseded_by: null
issue: null
---

# D-0060: Review por tramos de commits

## Contexto

D-0047 mantiene los revisores separados (solo code-reviewer en `review-prepush`, las tres personas en los tiers 1–2 de `review-pr`) y dice que el tamaño del diff solo sirve para el límite de las tareas. Con D-0058 las tareas ya no tienen límite de líneas, y una rama puede salir más grande de lo que un code-reviewer revisa con precisión de una vez. Los commits de la rama ya dan un corte natural, que no hay que inventar ni validar: entre todos cubren `base..HEAD` y llevan la pareja roja/verde de cada tarea.

## Decisión

- `review_facts.py` parte `base..HEAD` en **tramos de commits seguidos**: junta commits en orden mientras el tramo no pase de `[review] max_lines_per_reviewer` de `.harness-config.toml`, leído de la rama base (D-0054). No hay valor por defecto: sin la clave, la rama es un solo tramo y la review es la de siempre. Cada proyecto lo activa con el número que mida. Cuenta como `diff_size.py`. Nunca separa un `test(Tn)` del commit siguiente. Un commit que pasa del umbral va solo, marcado como tramo grande. Si la rama cabe en un tramo, la review es la de hoy.
- Con varios tramos, `review-prepush` lanza un **code-reviewer por tramo**, en paralelo y sin historial (D-0046). Cada brief lleva su diff `a..b`, la tarea, los hechos completos y la orden de leer `git diff base...HEAD` si le falta contexto antes de informar algo como ausente.
- El **finding-verifier** solo confirma hallazgos que siguen siendo ciertos en HEAD.
- Un **code-reviewer más hace la pasada de costuras**: lo que expone cada tramo y quién lo usa en otro, y si están todos los ejemplos de la tarea. Los hallazgos repetidos entre tramos se fusionan.
- Lo que bloquea no cambia: solo un Critical confirmado. La caché de veredictos sigue ligada al diff entero (D-0042).
- Se mantiene de D-0047: los revisores separados y no elegidos por tamaño. El tamaño decide cuántos tramos hay, no qué personas revisan.

## Alternativas descartadas

- Que el agente que implementa elija los tramos: podría esconder lo difícil en un tramo grande. Además, la review la lanza el hook `harness-review`, no ese agente.
- Partir el diff final por ficheros o hunks con un manifiesto: habría que validar que cubre todo. Los commits ya lo cubren.
- Revisar cada commit por separado: un commit en rojo o a medias da falsos positivos de «falta X».
- Un registro de la revisión commiteado en git y comprobado por el gate y CI: el hook ya ejecuta la review él mismo y el agente no puede desactivarlo (D-0055, D-0056).
- Un umbral distinto del límite de cada tramo: dos números para lo mismo.
- Un umbral por defecto (300 líneas): un número sin medir que acaba funcionando como regla, lo mismo que se descartó en D-0053. Si las historias se parten por objetivo (D-0058), casi todas las ramas caben en una review, así que los tramos pueden ser opcionales.

## Cómo se hace cumplir

Tests E10–E24 del cambio `tareas-por-objetivo` en `scripts/check.sh` (el corte, con ramas de prueba; el texto de `review-prepush` y de los agentes). La medición final del cambio fija el valor de este repo.
