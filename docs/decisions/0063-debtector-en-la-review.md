---
id: D-0063
title: La review usa debtector diff como fuente determinista opcional, activada con [review] debtector = true en la rama base; sus hallazgos son candidatos y nunca bloquea
type: architecture
status: accepted
date: 2026-11-26
affects: [skills/review-context/, skills/review-prepush/, skills/review-pr/, skills/review-report/, .harness-config.toml]
supersedes: null
superseded_by: null
issue: null
---

# D-0063: La review usa debtector diff como fuente determinista opcional, activada con [review] debtector = true en la rama base; sus hallazgos son candidatos y nunca bloquea

## Contexto

debtector compara el grafo de dependencias de la rama con el de la base (`debtector diff --base <ref>`) y lista lo que la rama añade: ciclos, god modules, violaciones SDP, regresiones de inestabilidad, funciones más complejas y hotspots. Ninguna fuente de la review ve eso. Solo tiene sentido en los repos que ya usan debtector, que tienen su `debtector.toml` con los umbrales, y tarda más que Semgrep, porque indexa la base en un worktree temporal. Su propio job de CI ya bloquea lo que el proyecto marca como `error`.

## Decisión

- `review-context/scripts/debtector_diff.py <base>` ejecuta `debtector --json diff --base <base>` y lista un hallazgo por línea de lo que la rama añade o empeora, más un recuento final. Sale con 2 si debtector no está en el `PATH` o falla.
- Se activa con `[review] debtector = true` en el `.harness-config.toml` de la rama base. Por defecto, `false`. El hook la lee de la base, como `verify` y `semgrep` (D-0054, D-0061), y añade la salida al fichero de resultados. Sin el hook, la review ejecuta el script según review-context §2.7 si la clave está activa en la base.
- debtector nunca bloquea el push: ni su exit 1 ni sus hallazgos. Lo que el proyecto marca como `error` ya lo bloquea su propio job de CI.
- La review trata sus líneas como hallazgos candidatos (`Source: debtector`): pasan por las reglas de precisión y por el verifier, como los de Semgrep.

## Alternativas descartadas

- Activarlo en cuanto la base tiene `debtector.toml`: una review que tarda más sin que nadie lo haya pedido; y la clave en `.harness-config.toml` sigue el mismo patrón que `verify` y `semgrep`.
- Activado por defecto, como Semgrep: Semgrep vale para cualquier repo; debtector solo para los que lo han configurado.
- Que su exit 1 bloquee el push en el hook: duplicaría el gate del job de debtector en CI con otra política, y un falso positivo del grafo (un movimiento de fichero, por ejemplo) bloquearía sin pasar por el verifier.
- Instalarlo al vuelo con `uvx debtector`: necesita red y ejecuta un paquete descargado en cada push.
- `debtector baseline status`: mide la deuda acumulada contra el baseline, no lo que añade la rama; los hallazgos no serían del autor (el mismo criterio de D-0043).

## Cómo se hace cumplir

`scripts/check.sh`, con un `debtector` falso en el `PATH`: la salida de `debtector_diff.py` y la sección de debtector en el fichero del hook, que solo aparece con la clave en la base y no bloquea.
