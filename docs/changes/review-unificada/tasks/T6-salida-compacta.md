---
id: T6
title: Salida compacta de las personas y del verifier
status: todo
depends_on: [T4, T5, T12, T13]
examples: [E17, E18, E19]
verification: scripts/check.sh
---
**Propósito:** refactor de la salida: ningún subagente reescribe lo que otro ya escribió (R4, D-0045).

**Dentro:** `security-auditor` y `test-engineer` (y `code-reviewer` en el fan-out) devuelven solo hallazgos en formato §3; `code-reviewer` solo añade "what's done well" cuando va solo; `finding-verifier` devuelve una línea por ID (`CONFIRMED` | `REFUTED <motivo>` | `UNCERTAIN <qué lo confirmaría>`) y el ranking de Optional/Nits; el paso de merge y el de verificación de `review-prepush` y `review-pr` construyen el informe con los hallazgos originales y esas líneas. Si `review-report` crece, se recorta en esta tarea para seguir bajo el tope de `check.sh`. Adaptadores regenerados; checks nombrados E17–E19.

**Fuera:** el formato del informe final (§4) y el bloque JSON (§4.3), que no cambian.

**Flag:** ninguno.
