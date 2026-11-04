---
id: D-0047
title: La review mantiene sus revisores separados (code-reviewer solo en review-prepush; las tres personas en los tiers 1–2 de review-pr), sin elegirlos por el tamaño del diff; el tamaño del diff solo sirve para el límite de las tareas
type: architecture
status: accepted
date: 2026-11-04
affects: [skills/review-prepush/, skills/review-pr/, skills/review-context/, agents/code-reviewer.md]
supersedes: D-0045
superseded_by: null
issue: null
---

# D-0047: La review mantiene sus revisores separados; el tamaño del diff solo sirve para el límite de las tareas

## Contexto

D-0045 juntaba la review de los diffs de hasta 200 líneas en un solo `code-reviewer` con pasadas condicionales (seguridad, rendimiento, tests), sin `security-auditor` ni `test-engineer`, y le quitaba la precarga de `code-review-and-quality` a cambio de un criterio condensado. La medición de T10 en `tests/review-sandbox/` (`docs/review/medicion-review.md`) mostró que ese revisor pierde bugs que la base encontraba: B2 (un test que pasa con el bug, Required) y B5 en 6 de 9 ejecuciones de `review-prepush`, y B7 en `review-pr`. El ahorro de `review-pr` estaba en la entrada total (−46 %), no en la entrada sin caché (−8 %). La salida de los agentes, que motivó el cambio, es menos del 1 % del gasto: casi todo es la entrada que reenvía la sesión principal. Un revisor con muchos encargos a la vez se dispersa.

## Decisión

- `review-prepush`: un `code-reviewer`, con `code-review-and-quality` precargada, y el `finding-verifier`, como antes de D-0045.
- `review-pr`: tier 0 con `code-reviewer`; tiers 1–2 con las tres personas en paralelo y el `finding-verifier`, sea cual sea el tamaño.
- **Tamaño del diff:** líneas añadidas + borradas, tests incluidos, sin lockfiles (por nombre), ficheros marcados `linguist-generated` en el `.gitattributes` de la base ni snapshots; los binarios cuentan 0. Lo calcula `skills/review-context/scripts/diff_size.py`. Solo se usa para el límite de las tareas (D-0044), no para elegir revisores.
- Se mantiene de D-0045 lo que no depende de juntar revisores: el formato del informe final vive en una referencia que solo lee la sesión principal, y las personas no llevan plantillas de salida que contradigan `review-report` §3.

## Alternativas descartadas

- Reviewer unificado hasta 200 líneas (D-0045): pierde bugs, en especial los tests que no pueden fallar, que caza `test-engineer`; el ahorro no está en la parte del gasto que importa.
- Mantenerlo y reforzar sus disparadores: cada criterio que se le añade es un encargo más al mismo revisor, que es lo que lo dispersa.
- Salida compacta de las personas (T6): recorta la parte pequeña del gasto.

## Cómo se hace cumplir

`check.sh` comprueba los casos de `diff_size.py`, el formato del informe en su referencia y que las personas no llevan plantillas. Cambiar el reparto de revisores necesita una medición en `tests/review-sandbox/` contra la base.
