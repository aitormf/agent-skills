<!--
  Sección opcional de AGENTS.md para las skills de review (review-prepush, review-pr).
  Copia lo que necesites y borra estos comentarios.

  OJO: AGENTS.md se carga en TODAS las sesiones del agente, no solo en las reviews.
  Mantén esta sección corta (10–20 líneas).

  Los comandos de verificación NO van aquí: la review los lee de la sección `## Comandos`
  de AGENTS.md, la misma que usan implement y plan-to-tasks. Si hay un comando agregado
  (`./scripts/check.sh`, `make check`), solo ejecuta ese. Solo ejecuta comandos que comprueban:
  nunca deploy, migraciones, install, --fix ni --write.
-->

## Code review
<!-- Todo opcional. Lo que no pongas usa el valor por defecto indicado. -->
- Rama base: `main`                       <!-- defecto: rama por defecto del remoto -->
- Output language: Spanish                <!-- defecto: inglés. Títulos y etiquetas siempre en inglés -->
- Rutas de alto riesgo: `src/auth/**`, `src/billing/**`, `migrations/**`
  <!-- fuerzan tier 2 en review-pr y más profundidad en seguridad.
       defecto: rutas que contengan auth, session, token, payment, billing, migration, secret, webhook, admin… -->
- Marcar siempre: queries SQL construidas a mano; llamadas HTTP sin timeout
- Ignorar: `src/generated/**`, `*.snap`, cambios de formato en `docs/`
- Convenciones que no cubre el linter: los errores de dominio se lanzan como `DomainError`, nunca `Error`
- Max Optional: 3                          <!-- cuántos Optional se muestran (los de más impacto y menos coste). 0 = ninguno -->
- Max Nits: 3                              <!-- ídem para Nits -->
- Semgrep: no                              <!-- "no" si ya lo ejecuta vuestro comando de verificación (setup-guardrails-python lo hace en CI) -->
