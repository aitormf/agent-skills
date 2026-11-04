---
id: T3
title: code-reviewer con pasadas condicionales cuando va solo
status: done
depends_on: [T17]
examples: [E13, E14, E15, E16]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: cuando `code-reviewer` es el único revisor, hace la pasada base y la de tests siempre y activa la de seguridad y la de rendimiento por lo que ve en el diff, y dice cuáles hizo y por qué (R3, D-0045).

**Dentro:** una sección "Passes" en `agents/code-reviewer.md`: los disparadores de la pasada de seguridad (entrada externa, ficheros o paths, consultas, auth, secretos, dependencias o lockfiles, rutas de alto riesgo de AGENTS.md; obligatoria si el comando dice tier 2), que lee `references/security-checklist.md` y aplica los criterios de frontera de confianza de `security-auditor` (quién puede dispararlo y qué obtiene); los de rendimiento (bucles sobre datos, I/O, consultas), que lee `references/performance-checklist.md`; la línea `Passes: …` del informe. Adaptadores regenerados con `scripts/build-agents.py`. Checks en `check.sh` nombrados E13–E16 que comprueban que el agente dice cada disparador y la línea `Passes:`.

**Fuera:** que las skills lo lancen solo (T4, T5); la salida compacta (T6); la regla de tamaño de la tarea (T7).

**Flag:** ninguno.
