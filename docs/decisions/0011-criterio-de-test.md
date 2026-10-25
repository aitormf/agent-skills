---
id: D-0011
title: Qué cambios exigen test
type: rule
status: accepted
date: 2026-10-24
affects: [agents/implement.md, agents/code-reviewer.md]
supersedes: null
superseded_by: null
issue: "#11"
---

# D-0011: Qué cambios exigen test

## Contexto

`implement` pedía test solo «si el proyecto trabaja con TDD», y nada decía cuándo un cambio lo exige (choque 3.1 del plan de mejoras). El criterio lo van a usar `implement` (fase 2), `code-reviewer` (fase 4) y, si se hace, el Stop hook de la idea 6, así que tiene que ser uno solo.

## Decisión

Exige test todo cambio que añade o modifica una rama, un bucle, un parser o una conversión de formato, dinero, seguridad o permisos, una escritura de datos, o que arregla un bug (test de regresión que falla sin el arreglo). No lo exigen la documentación, los comentarios, los valores de configuración, los renombrados cubiertos por tests existentes ni un refactor cuyo comportamiento ya cubren tests que siguen en verde sin cambios. «Es un cambio pequeño» no es una excepción. En caso de duda, lleva test.

El texto vive en `agents/implement.md` (sección «When a change needs a test»); `code-reviewer` y el Stop hook lo enlazarán desde allí cuando lo usen.

## Alternativas descartadas

- Todo cambio lleva test (#4): obliga a tests vacíos para docs y config, y se acaba ignorando.
- Solo la lógica «no trivial» (Ponytail): no se puede comprobar; cada agente decide qué es trivial.
- Una skill compartida solo para el criterio: hoy solo la usa `implement`; se extrae si `code-reviewer` lo necesita en la fase 4.

## Cómo se hace cumplir

No se automatiza todavía. La review de la fase 4 y, si se hace, el Stop hook de la idea 6 lo comprobarán.
