---
id: T7
title: Conformidad propia del manager de solo lectura con el story-contract
status: todo
depends_on: [T3, T4]
examples: [E27]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: `check.sh` comprueba que el manager cumple el story-contract en lo que un tablero de solo lectura puede cumplir (D-0050), contra un repo de prueba con un cambio de tres tareas.

**Dentro:** un test propio (con `node:test`, como los de T2) que pasa `assertManager` y reproduce los casos de `runStoryContract` que caben en solo lectura: capabilities y credentials válidos, `list` con la forma de `HU_FIELDS`, `move` que relee el estado de git, y `BoardRejectedError` cuando git no dice lo pedido. Una lista en `integrations/karajan-board/README.md` de los casos de la suite que no aplican (crear, mover escribiendo, reservar con dueño) y por qué.

**Fuera:** correr `runStoryContract` tal cual; escribir en git o en un fichero lateral (D-0048, D-0050); proponer a Karajan una capability de solo lectura (si se quiere, es una issue aparte en su repo, la abre la persona).

**Flag:** ninguno.
