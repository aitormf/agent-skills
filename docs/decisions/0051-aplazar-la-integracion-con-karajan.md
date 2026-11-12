---
id: D-0051
title: Se aplaza la integración con Karajan Code después de T1; el esfuerzo pasa a la review cruzada y a un gate en git y CI que valgan para cualquier agente
type: architecture
status: accepted
date: 2026-11-12
affects: [docs/changes/karajan-board/, integrations/karajan-board/]
supersedes: null
superseded_by: null
issue: null
---

# D-0051: Se aplaza la integración con Karajan después de T1

## Contexto

El change `karajan-board` (D-0048, D-0049) expone nuestras tareas como HUs de Karajan Code. T1 (`board.py --json`) está mergeada. Al revisar Karajan 5.20.0 (2026-11-12):

- La v5 retiró el pipeline multi-agente (`kj run`). Sentinel, su control en la sesión, solo funciona en Claude Code y tiene un plan de retirada propio (`docs/health/sentinel-retirement-plan.md`). El story-contract es interno y se mueve con cada versión.
- La integración es parcial a propósito: deja fuera `delegate`, `hu-reviewer`, `create` y los estados `failed` y `skipped`.
- Solo sirve a quien usa Karajan y nuestras skills en el mismo proyecto, y no sabemos de nadie que lo haga.
- Mete código Node en un repo de markdown y Python (D-0049).

Lo que de verdad nos falta para ser multi-agente no es Karajan, sino lo que Karajan hace bien y es independiente de la herramienta: que revise una IA distinta de la que escribe y que lo obligatorio se compruebe en git y en CI.

## Decisión

- El change `karajan-board` queda **en pausa** después de T1. No se implementan T2 a T8.
- T1 se queda: `board.py --json` sirve a cualquier herramienta y a CI.
- D-0048 y D-0049 siguen `accepted`: son el diseño si se retoma.
- **Se retoma** cuando alguien que use `kj` lo pida.
- El esfuerzo pasa a dos changes nuevos: la review cruzada (el revisor no es de la familia del autor) y un gate determinista en pre-push y CI.

## Alternativas descartadas

- **Terminar la integración ahora**: ataría código nuestro a una pieza que cambia rápido, para un uso que nadie ha pedido, y duplicaría gates con los nuestros.
- **Borrar el change y las decisiones**: se pierde un diseño que ya se discutió y que vale si alguien lo pide.
- **Adoptar Karajan entero o copiar Sentinel**: su control en la sesión solo existe en Claude Code; lo que no se puede saltar está en git y en CI, que valen para cualquier agente.

## Cómo se hace cumplir

No se automatiza: la nota del README de `docs/changes/karajan-board/` dice que está en pausa, y `implement` no debe tomar sus tareas.
