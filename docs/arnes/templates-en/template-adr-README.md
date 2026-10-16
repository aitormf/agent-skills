<!--
TEMPLATE for docs/adr/README.md: ADR index.
Keep it up to date in the same PR that adds or supersedes an ADR.
-->

# Architecture Decision Records

The project's architecture decisions, with their context and the alternatives that were rejected. This directory explains **why** the system is the way it is; `docs/ARCHITECTURE.md` describes **how it is** today.

**Before changing** persistence, module boundaries, authentication, the public API or a structural dependency, look here for related decisions. If your change contradicts an accepted ADR, don't change it silently: propose a new ADR that supersedes it.

**To create one:** copy `0000-template.md` as `NNNN-title.md` with the next free number, open it with status `proposed` in a PR, and move it to `accepted` once approved.

| ADR | Title | Status | Date |
|---|---|---|---|
| [0001](0001-uv-ruff-mypy.md) | Use uv, ruff and mypy as the toolchain | accepted | YYYY-MM-DD |
| [0002](0002-layered-architecture.md) | Layered architecture (domain, application, infra, api) | accepted | YYYY-MM-DD |
| [0003](0003-tdd.md) | Test-first as a mandatory practice | accepted | YYYY-MM-DD |
