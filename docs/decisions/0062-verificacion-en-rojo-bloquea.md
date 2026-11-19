---
id: D-0062
title: Una verificación en rojo o que pasa de su tiempo límite bloquea el push del agente sin lanzar al revisor
type: rule
status: accepted
date: 2026-11-19
affects: [skills/review-prepush/scripts/harness-review.sh]
supersedes: null
superseded_by: null
issue: 97
---

# D-0062: La verificación en rojo bloquea

## Contexto

Con la verificación en el hook (D-0061), su resultado se conoce antes de pagar al revisor. Hoy el hook solo bloquea por un Critical confirmado, y ante sus propios errores deja pasar (fail-open). Un test roto no es un error de la herramienta: es el estado del código que se sube. `implement` exige la verificación en verde antes de cada PR (D-0036).

## Decisión

Si un comando de `[review] verify` sale con un código distinto de 0, o pasa de 600 s, el hook bloquea el push del agente. Muestra el comando, el código de salida o el timeout y las últimas 40 líneas de su salida, y no lanza al revisor. No guarda veredicto, así que el siguiente push vuelve a verificar. Semgrep nunca bloquea por sí solo: sus hallazgos son candidatos para la review.

## Alternativas descartadas

- Pasar el rojo al revisor para que decida: se paga una review para un push que no puede subir, y el resultado depende del modelo.
- Un timeout que deja pasar (fail-open): un test que se cuelga permitiría subir código sin verificar.
- Bloquear también por hallazgos de Semgrep: tiene falsos positivos y por eso pasa por el verifier (review-context §2).

## Cómo se hace cumplir

Tests E7–E9 del cambio `97-verificacion-en-el-hook` en `scripts/check.sh`.
