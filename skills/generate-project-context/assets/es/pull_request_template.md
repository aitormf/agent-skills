<!--
PLANTILLA de .github/pull_request_template.md
GitHub la carga automáticamente al abrir una PR. Coherente con CONTRIBUTING.md (sección 7).
Borra las secciones que no apliquen; no dejes casillas marcadas sin haberlas comprobado.
-->

## Qué cambia y por qué

<!-- 2-5 frases. El "por qué" importa más que el "qué": el diff ya muestra el qué. -->

Relacionado con: #<issue> · Spec: `docs/specs/<feature>.md` · Decisión: `docs/decisions/<NNNN>-<titulo>.md`

## Tipo de cambio

- [ ] `feat`: funcionalidad nueva
- [ ] `fix`: corrección de bug
- [ ] `refactor`: sin cambio de comportamiento
- [ ] `docs` / `test` / `chore`
- [ ] **Cambio incompatible** (API pública, esquema de BD, configuración): explica la migración abajo

## Cómo se ha verificado

<!-- Evidencia, no afirmaciones: comandos ejecutados, tests añadidos, capturas, pasos de prueba manual. -->

- [ ] `./scripts/check.sh` en verde en local
- [ ] Tests nuevos o actualizados que cubren el cambio (en un bug: test que lo reproducía en rojo)
- [ ] Probado manualmente: <cómo>

## Revisión de principios

- [ ] No incumple ningún principio innegociable de `docs/ARCHITECTURE.md` (o se justifica aquí / en una decisión)
- [ ] No se elimina ni debilita ningún test (o se explica por qué)
- [ ] Sin dependencias nuevas (o justificadas abajo: qué aportan, mantenimiento, licencia)
- [ ] Sin secretos, datos personales ni credenciales

## Documentación

- [ ] Actualizada en esta misma PR si aplica: `README.md` · `docs/ARCHITECTURE.md` · `docs/decisions/` · `AGENTS.md` · `.env.example`
- [ ] No aplica

## Uso de IA

<!-- Transparencia, no penalización. Quien abre la PR responde de todo su contenido. -->

- [ ] Sin uso relevante de IA
- [ ] Parte del código/tests lo generó un agente (<herramienta>) y **lo he revisado y entiendo cada línea**
- [ ] Si el agente cometió un error recurrente, he mejorado el arnés (lint, test, hook o `AGENTS.md`) o abierto un issue: #<n>

## Riesgos y despliegue

<!-- Migraciones, flags, orden de despliegue, cómo revertir. "Ninguno" es una respuesta válida. -->

## Notas para quien revisa

<!-- Por dónde empezar, qué mirar con más cuidado, dudas abiertas. -->
