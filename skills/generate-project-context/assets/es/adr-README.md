<!--
PLANTILLA de docs/adr/README.md: índice de ADRs.
Mantenlo actualizado en la misma PR que añade o sustituye un ADR.
-->

# Architecture Decision Records

Decisiones de arquitectura del proyecto, con su contexto y las alternativas descartadas. Este directorio explica **por qué** el sistema es como es; `docs/ARCHITECTURE.md` describe **cómo es** hoy.

**Antes de cambiar** persistencia, límites entre módulos, autenticación, la API pública o una dependencia estructural, busca aquí las decisiones relacionadas. Si tu cambio contradice un ADR aceptado, no lo cambies en silencio: propón un ADR nuevo que lo sustituya.

**Para crear uno:** copia `0000-plantilla.md` como `NNNN-titulo.md` con el siguiente número libre, ábrelo en estado `propuesto` en una PR y pasa a `aceptado` al aprobarse.

| ADR | Título | Estado | Fecha |
|---|---|---|---|
| [0001](0001-uv-ruff-mypy.md) | Usar uv, ruff y mypy como toolchain | aceptado | AAAA-MM-DD |
| [0002](0002-arquitectura-por-capas.md) | Arquitectura por capas (domain, application, infra, api) | aceptado | AAAA-MM-DD |
| [0003](0003-tdd.md) | Test primero como práctica obligatoria | aceptado | AAAA-MM-DD |
