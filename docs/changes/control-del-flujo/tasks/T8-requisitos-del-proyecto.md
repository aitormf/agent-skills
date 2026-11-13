---
id: T8
title: Documentar como requisito la branch protection, CODEOWNERS y la identidad del agente
status: done
depends_on: [T5]
examples: []
verification: scripts/check.sh
---
**Propósito:** documentación: lo que el kit no puede poner y sin lo que el gate se queda en avisos (S1).

**Dentro:** en `setup-guardrails-python`, un paso con el requisito: branch protection en la rama base con el check `harness-gate` obligatorio, "Require review from Code Owners", `CODEOWNERS` sobre la lista de control, protección aplicada también a admins, y el agente con identidad propia (cuenta bot o fine-grained token) sin permiso para saltarse la protección ni aprobar. En el README, filas nuevas en «Qué se garantiza en cada herramienta» para el gate y los ficheros de control. `check.sh` comprueba que esos textos existen.

**Fuera:** configurar GitHub desde el kit.

**Flag:** ninguno.
