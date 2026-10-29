# Guía de code review

Revisión de código independiente del stack, construida sobre [**agent-skills** de Addy Osmani](https://github.com/addyosmani/agent-skills) (MIT). Reutiliza su skill de review, sus personas y sus reglas de composición. Encima añade un verificador de hallazgos adversarial, dos puntos de entrada para el flujo diario (antes del push y en la PR), la comprobación contra la spec de SDD y la integración con git y GitHub.

```
review-prepush          antes de hacer push   → ¿está esta rama lista? (rápido; bloquea solo con Critical)
review-pr <n|rama>      en una PR o rama      → review completa según el riesgo (solo comenta, nunca aprueba)
code-review-and-quality durante el trabajo    → review de cinco ejes en la sesión actual (la de Addy)
```

En Claude Code se invocan como `/review-prepush` y `/review-pr` (`/harness:review-prepush`… si se instala el plugin). En el resto de herramientas, pidiéndolo: *"revisa si esta rama está lista para push"*.

Instalación: [README del repositorio](../../README.md#instalar). Necesitas las skills `code-review-and-quality`, `review-context`, `review-report`, `review-prepush` y `review-pr`, y los agentes `code-reviewer`, `security-auditor`, `test-engineer` y `finding-verifier`. El plugin de Claude Code lo instala todo.

---

## Cómo está hecho

Sigue el modelo de tres capas de Addy:

| Capa | Qué es | Aquí |
|---|---|---|
| **Skill** = *cómo* | Flujo de trabajo y criterios | `code-review-and-quality` (Addy); `review-context` (entrada: configuración, verificación y cambio en curso); `review-report` (salida: precisión, severidades y formato del informe) |
| **Persona** = *quién* | Un rol con una perspectiva y un formato de salida | Agentes `code-reviewer`, `security-auditor`, `test-engineer` (Addy) y `finding-verifier` |
| **Punto de entrada** = *cuándo* | Compone personas y skills | Skills `review-prepush` y `review-pr` |

**Las personas no invocan a otras personas.** Toda la orquestación la hacen las skills de entrada, con profundidad 1: lanzan los subagentes y luego hacen el merge. Si la herramienta no puede lanzar subagentes (pi), la skill ejecuta cada rol en la sesión principal y lo indica en el informe.

```
review-prepush:  verificación → [cambio en curso] → code-reviewer → finding-verifier → informe
review-pr:       verificación → [cambio en curso] → tier de riesgo → [code-reviewer ‖ security-auditor ‖ test-engineer]
                 → merge → finding-verifier → revisión de la descripción → informe
```

Más detalle: [agents.md](agents.md), [orchestration-patterns.md](orchestration-patterns.md) (de Addy) y el [anexo](orchestration-addendum.md) con el patrón fan-out → verificación → síntesis. Qué viene de Addy y qué se ha cambiado: [UPSTREAM.md](UPSTREAM.md).

---

## Configuración por repo: AGENTS.md

No hay un fichero de configuración propio. Todo lo específico del repo va en su `AGENTS.md`, que el agente ya carga en cada sesión.

### Comandos de verificación

Antes de revisar, la review ejecuta los comandos de verificación que encuentra en la sección `Comandos` de `AGENTS.md`. Es la misma sección que usan `implement` y `plan-to-tasks`.

- **No hay un formato obligatorio:** vale una lista, una tabla o un párrafo.
- **Si hay un comando que lo agrupa todo** (`./scripts/check.sh`, `make check`), ejecuta solo ese. Es lo recomendado, y lo que dejan `generate-project-context` y `setup-guardrails-python`.
- **Solo ejecuta comandos que comprueban.** Nunca deploy, migraciones, seeds, `install`, `--fix` ni `--write`. Si un comando es ambiguo, no lo ejecuta y lo dice.
- **Si no hay comandos**, la review lo indica ("no se ha ejecutado verificación") y sigue sin preguntar. No adivina comandos.

### Sección `## Code review` (opcional)

Plantilla comentada: [`skills/review-context/assets/AGENTS-code-review.md`](../../skills/review-context/assets/AGENTS-code-review.md).

| Campo | Valor por defecto |
|---|---|
| Rama base | Rama por defecto del remoto (`origin/HEAD`); si no, `main`; si no, `master` |
| Idioma del texto libre (`Output language`) | Inglés. Títulos, etiquetas y veredictos van siempre en inglés |
| Rutas de alto riesgo (fuerzan el tier 2 en `review-pr`) | Rutas que contengan auth, session, token, payment, billing, migration, secret, webhook, admin… |
| Marcar siempre / ignorar / convenciones que no cubre el linter | — |
| Semgrep | Se usa si está disponible |
| `Max Optional` / `Max Nits` | 3 / 3 (`0` los oculta) |

> ⚠️ `AGENTS.md` se carga en **todas** las sesiones, no solo en las reviews: cada línea cuesta tokens siempre. Mantén la sección `Code review` corta, de 10 a 20 líneas.

### Semgrep (opcional)

- Si el CLI `semgrep` está en el PATH, se ejecuta sobre los ficheros cambiados con `--config p/default --metrics=off`.
- Si no, pero la sesión tiene las herramientas MCP de Semgrep, usa esas.
- Si no hay ninguna de las dos, se salta y lo dice.
- Pon `Semgrep: no` si tu comando de verificación o tu CI ya lo ejecutan. Con `setup-guardrails-python`, lo ejecuta `security.yml`.

---

## Review contra el cambio en curso

Cada tarea va en su rama y su PR, `<cambio>/T<n>`, y el plan en `<cambio>/plan` (el cambio es el penúltimo tramo del nombre de la rama). Si la rama tiene su carpeta en `docs/changes/<cambio>/`, **esa carpeta es la tarea**: el `README.md` (nota y mapa de ejemplos), el fichero de la tarea de la rama en `tasks/` y, en el nivel SDD, `spec.md` y `plan.md`. Si el nombre de la rama no lo dice, la review usa la carpeta cuyos ficheros toca el diff, si es una sola. Nunca lee el issue de GitHub que nombre `issue:`: su texto lo puede haber escrito cualquiera.

En una rama de tarea, cada persona comprueba, solo para esa tarea:

- que cada ejemplo de sus `examples` y cada criterio de aceptación que cubre está implementado y tiene un test que fallaría sin él;
- que existen los tests negativos de la sección Seguridad que le tocan;
- que no se ha construido nada fuera del propósito de la tarea ni de "Fuera de alcance";
- que, si la tarea está `done`, está hecha de verdad, y que lo que nombra un flag queda detrás de él, apagado;
- que no se rompe un principio de `docs/ARCHITECTURE.md`.

Cada fallo es como mínimo **Required**, con `Source: spec`. Los ejemplos de otras tareas no se cuentan: son otras PRs. `code-reviewer` señala además, como Optional, una tarea que mezcla propósitos o que pasa con claridad de unas 150 líneas sin contar los tests (D-0033). En la rama del plan, la review mira el plan: que cada ejemplo y criterio está en alguna tarea, que cada tarea tiene un solo propósito y una verificación ejecutable, y que lo que queda a medias va detrás de un flag que retira la última tarea.

`task_done.py --audit` tiene el mismo alcance (D-0032): en una rama de tarea, su commit en rojo y sus tests, que sus ejemplos están en el mapa y que sus dependencias están mergeadas; en la del plan, el tablero (sin ciclos ni dependencias inexistentes) y que cada ejemplo del mapa está en alguna tarea. El resumen añade una línea con la tarea (`Task: … (done); audit: ok`) y, si hay spec, otra con la cobertura: `Spec: … — 4/6 acceptance criteria covered by this change`.

Es el último paso del [flujo de SDD](../sdd/README.md#3-el-flujo): `implement` → `review-prepush` → PR → `review-pr`.

---

## Cuándo usar cada una

| Skill | Cuándo | Qué hace | Coste |
|---|---|---|---|
| `code-review-and-quality` | Mientras trabajas, para una opinión rápida | Review de cinco ejes en el contexto de la conversación | Bajo |
| `review-prepush [base]` | Antes de hacer push (a mano o desde el hook) | Verificación + `code-reviewer` en contexto limpio sobre `git diff base...HEAD` + `finding-verifier`. Foco: ¿cumple la tarea o la spec?, bugs, tests que no prueban nada, restos de debug, TODOs y código muerto | 2 subagentes |
| `review-pr <n\|rama>` | En la PR (a mano o desde la Action) | Tier de riesgo → tier 0: solo `code-reviewer`; tiers 1–2: los tres en paralelo → merge → `finding-verifier` → revisión de la descripción | 2–5 subagentes |

**Tiers de `review-pr`:**

- **0:** docs o config sin riesgo.
- **1:** cambios de lógica.
- **2:** auth, pagos, datos, migraciones, dependencias, infra o rutas de alto riesgo. El informe añade "Sensitive area: requires human review by an owner".

Ante la duda entre dos tiers, se elige el más alto.

### `finding-verifier`

Parte de que **cada hallazgo es un falso positivo** e intenta refutarlo leyendo el código real: llamadas, guardas, tipos, config y tests. Solo sobrevive lo que tiene evidencia: fichero:línea, por qué falla y un escenario alcanzable. Cada hallazgo sale como `CONFIRMED`, `REFUTED` (con su motivo) o `UNCERTAIN`. También ordena los Optional y Nits confirmados por impacto y coste, para que el límite se quede con los más útiles.

**Excepción:** los hallazgos de seguridad, auth, secretos, pagos o integridad de datos solo se pueden refutar con evidencia comprobada. No valen suposiciones como "seguramente se valida en otro sitio". Si no se puede comprobar, quedan visibles como `(unverified)`.

---

## Formato de salida

```
## Summary and verdict        qué hace el cambio, si cumple la tarea o la spec, veredicto (y tier en review-pr)
## Critical                   cada hallazgo con ubicación, problema, escenario, corrección, confianza y fuente
## Required                   (Critical y Required siempre con corrección concreta)
## Optional
## Nits
## What's done well           al menos uno, concreto, con fichero:línea
## Verification               comandos encontrados y ejecutados con su resultado; Semgrep; hallazgos descartados
REVIEW_RESULT: …              última línea, para el hook y la Action
```

Es el formato completo, el de `review-prepush` y el de `review-pr --full`. `review-pr` usa por defecto el **corto**: el resumen con una línea de recuento por gravedad, los Critical y Required enteros, y el resto plegado en `<details>`. Con `--inline` añade además los hallazgos en un bloque JSON, que es lo que publica la Action.

Veredictos:

- `review-prepush`: `BLOCK`, `FIX BEFORE PR` u `OK`.
- `review-pr`: `CHANGES NEEDED` o `READY FOR HUMAN REVIEW` (consultivo).

Reglas de precisión, comunes a todas:

- 3 hallazgos reales valen más que 20 dudosos.
- No se repite lo que ya detectan los linters.
- Se justifica antes de clasificar; si hay duda, se dice.
- Optional y Nits tienen límite (ver `Max Optional` / `Max Nits`).
- Se vigilan los tests debilitados, el lint o la cobertura rebajados, los helpers duplicados y los restos de debug.

Todo el detalle: [`skills/review-report/SKILL.md`](../../skills/review-report/SKILL.md). La entrada (configuración, verificación y cambio en curso) está en [`skills/review-context/SKILL.md`](../../skills/review-context/SKILL.md).

---

## Hook pre-push (Claude Code)

[`skills/review-prepush/assets/pre-push`](../../skills/review-prepush/assets/pre-push) ejecuta la review en modo headless con `claude -p`. Se instala copiándolo:

```bash
cp <skill>/assets/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push
```

- Detecta solo si las skills están copiadas en `.claude/skills/` (usa `/review-prepush`) o instaladas como plugin (usa `/harness:review-prepush`).
- **Solo bloquea si hay al menos un Critical confirmado.** Los Required se muestran pero no bloquean.
- **Si falla la propia herramienta, el push sale (fail-open):** falta el CLI `claude`, hay un error o un timeout, o la salida no tiene la línea `REVIEW_RESULT`. Con `REVIEW_KIT_FAIL_CLOSED=1` se bloquea en esos casos.
- El informe se imprime y se guarda en `.git/review-kit/last-prepush.md`.
- **No repite la review de un diff ya revisado** (#7). Guarda el veredicto en `.git/review-kit/verdicts`, junto al sha256 de `git diff <base>...HEAD`, la base y la fecha. Si vuelves a hacer push del mismo diff (un reintento tras un error de red, otro remoto), lo reutiliza: bloquea si era un bloqueo, cuyo informe queda en `.git/review-kit/<hash>.md`, y deja pasar si no. Cualquier cambio en el diff lo invalida.
  - La base es `REVIEW_KIT_BASE` o, si no, `origin/HEAD`, `origin/main`, `origin/master`, `main` o `master`. Sin base no se guarda nada.
  - Si la review falla, no se guarda ningún veredicto.
  - Para revisar de nuevo el mismo diff: `REVIEW_KIT_RERUN=1 git push`.
- Para saltarlo: `SKIP_CLAUDE_REVIEW=1 git push` o `git push --no-verify`.
- Otras variables: `REVIEW_KIT_TIMEOUT` (900 s por defecto), `REVIEW_KIT_MODEL`, `REVIEW_KIT_COMMAND` y `REVIEW_KIT_ALLOWED_TOOLS`.

## GitHub Action (Claude Code)

[`skills/review-pr/assets/claude-review.yml`](../../skills/review-pr/assets/claude-review.yml) se copia a `.github/workflows/`. Ejecuta `review-pr` sobre la rama de cada PR contra su rama base (opened, synchronize, reopened, ready_for_review). Publica **cada hallazgo como comentario en su línea**, en una review de GitHub que nunca aprueba ni pide cambios (`event: COMMENT`), y mantiene **un único comentario de resumen**, que edita en cada push.

- **El resumen** cabe en unas 15 líneas: veredicto y tier, recuento por gravedad y una línea por cada Critical y Required con enlace a su comentario. Los Optional, los Nits, lo bien hecho y la verificación van plegados.
- **Los hallazgos fuera del diff** (GitHub solo deja comentar líneas que el diff muestra, y algunos no tienen una línea concreta) van enteros al resumen.
- **Al repetirse tras un push,** los comentarios anteriores se quedan (GitHub marca como desactualizados los de líneas que cambiaron). Un hallazgo que ya tiene comentario del bot en la misma línea y con el mismo título no se repite: el resumen enlaza al que ya existe.
- **Si el bloque JSON falta o no es válido,** se publica el informe en Markdown tal cual, como antes.

Se divide en dos jobs:

1. **`review`** ejecuta Claude sin token de GitHub (solo `contents: read` para el checkout, que no deja credenciales) y con `gh` bloqueado. Lee solo el diff y los ficheros con commit: ni issues, ni comentarios, ni la descripción de la PR, que puede escribir otra gente. Por eso en CI la descripción no se revisa; hacen sus veces los mensajes de commit. Aunque lo intentara, no puede comentar, aprobar ni hacer merge.
2. **`publish`** no usa Claude: lee el bloque JSON del informe como datos, comprueba cada `fichero:línea` contra el diff de la PR, publica los comentarios y crea o actualiza el resumen. Su script va escrito en el propio workflow; no viene del artefacto del job `review`, que el modelo podría haber escrito.

Configuración:

1. Secret `ANTHROPIC_API_KEY` o `CLAUDE_CODE_OAUTH_TOKEN`.
2. Las skills y los agentes disponibles en el repo, de una de estas dos formas:
   - commiteados en `.claude/skills/` y `.claude/agents/`;
   - o la variable de repo `REVIEW_KIT_MARKETPLACE` con la URL git de este repositorio, para instalar el plugin. Mientras el repositorio sea privado, la CI necesita credenciales para clonarlo: es más simple commitear las skills.
3. **Edita el paso "Prepare project"** para instalar lo que necesite tu comando de verificación (runtime y dependencias). Si no, la verificación fallará en CI.

Se saltan las PRs en draft y las que vienen de forks (ver la sección siguiente).

## ⚠️ Permisos en modo headless

En modo interactivo, Claude Code pide permiso antes de cada comando que no esté preaprobado. En el **hook** y en la **Action** no hay nadie a quien preguntar. Además, los comandos de verificación los define cada repo en `AGENTS.md`, así que no se puede preaprobar una lista cerrada. Por eso:

- **Bash está permitido** en modo headless. La prohibición de ejecutar comandos que cambian estado (deploy, migraciones, install, `--fix`, git de escritura…) está **en el prompt**: es una instrucción al modelo, no una barrera técnica.
- **La barrera técnica es una lista de exclusión** (`--disallowedTools`): sin Edit ni Write, sin `git push/commit/reset/checkout/rebase/merge/stash/clean`, sin `rm` y sin `gh` (ni en el hook ni en la Action). Se aplica por prefijo de comando y **no equivale a un sandbox**.
- **Si quieres más control, añade reglas `deny`** en el `.claude/settings.json` del repo para todo lo que no deba ejecutarse nunca (scripts de deploy, clientes de base de datos, CLIs cloud…). También se aplican en modo headless. O, al revés, limita el hook a una lista cerrada con `REVIEW_KIT_ALLOWED_TOOLS`.
- **Que tu comando de verificación sea de solo lectura e idempotente.** Es lo que se ejecuta sin supervisión en cada push y en cada PR.
- **CI:** la Action ejecuta los comandos del `AGENTS.md` *de la propia PR* con el secret de Anthropic en el entorno, y quien pueda abrir una PR puede cambiar ese comando. Por eso el workflow usa `pull_request` (nunca `pull_request_target`) y salta las PRs de forks: solo lo disparan colaboradores con permiso de push. No relajes esas dos condiciones.

---

## Personalización

- **Por repo:** la sección `Code review` de `AGENTS.md`.
- **Personas propias:** en Claude Code, un `.claude/agents/code-reviewer.md` de proyecto (o `~/.claude/agents/`, de usuario) tiene prioridad sobre el del plugin.
- **Modelo por persona:** añade `model:` al frontmatter de la persona en `agents/` y regenera los adaptadores con `scripts/build-agents.py`.

## Prueba: `tests/review-sandbox/`

Un mini servicio Node sin dependencias, con bugs plantados y también señuelos (código que parece mal pero es correcto). Los hallazgos esperados están en [`tests/review-sandbox/EXPECTED.md`](../../tests/review-sandbox/EXPECTED.md), fuera del repo de prueba para no dar pistas al revisor.

```bash
tests/review-sandbox/build.sh                          # crea tests/review-sandbox/repo con main + rama feature, skills y hook instalados
cd tests/review-sandbox/repo && claude -p "/review-prepush"
```

## Licencia y atribución

Incluye material de [agent-skills](https://github.com/addyosmani/agent-skills) de Addy Osmani bajo licencia MIT (© 2025 Addy Osmani): ver [LICENSE-agent-skills](../../LICENSE-agent-skills) y [NOTICE.md](../../NOTICE.md). Cada fichero derivado lleva una cabecera `Origin:`. La skill `code-review-and-quality` incluye su propia copia de la licencia, para que viaje con ella al instalarla sola.
