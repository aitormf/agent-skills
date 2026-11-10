---
id: T3
title: isId y canonicalId para los ids <cambio>/T<n>
status: todo
depends_on: [T2]
examples: [E19, E20, E21]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: Karajan reconoce nuestros ids, también dentro de una rama con prefijo (D-0031).

**Dentro:** `isId`, `canonicalId` e `idHint` del manager, con sus tests. El id es `<cambio>/T<n>`, donde `<cambio>` está en kebab-case y puede llevar delante el número del issue. `canonicalId` quita el prefijo de rama (`feat/42-cancelar-viaje/T3` → `42-cancelar-viaje/T3`).

**Fuera:** reconocer las ramas `feat/<id>-<slug>` que crea `kj` (supuesto del README: no se reconocen).

**Flag:** ninguno.
