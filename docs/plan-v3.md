# Plan de la v3

Fecha: 2026-10-28. Estado: **aprobado** (PR #25). Fase 1 hecha, versión 0.6.0 ([D-0040](decisions/0040-review-de-pr-en-linea.md)). Fase 2 hecha, versión 0.7.0 ([D-0041](decisions/0041-restricciones-de-agentes-para-rulesync.md)), probada de punta a punta (§3.5). Fase 3 hecha, versión 0.8.0 ([D-0042](decisions/0042-veredicto-del-pre-push-ligado-al-diff.md), [D-0043](decisions/0043-semgrep-solo-en-lineas-anadidas.md)).

Sale de usar la v2 (versión 0.5.0) y de repasar el [plan de mejoras](plan-de-mejoras.md). Tres mejoras pedidas y unas cuantas pequeñas que siguen pendientes.

## 1. Fases

| Fase | Qué | Por qué en este orden |
|---|---|---|
| 1 | Review de PR con comentarios en línea y un resumen corto (§2) | Es lo que más se nota al usarlo cada día: hoy el comentario es largo y asusta |
| 2 | Compatibilidad con atril (§3) | Tener el kit bajo demanda, no todas las skills cargadas en cada sesión |
| 3 | Mejoras pequeñas del plan de mejoras (§4) | Sin prisa; cada una es pequeña |

## 2. Review en línea y resumen corto (fase 1)

- **Comentarios en línea.** El job que publica en CI crea una review de GitHub (`POST /pulls/{n}/reviews`) con un comentario por hallazgo en su `fichero:línea`, siempre con `event: COMMENT`: la review nunca aprueba ni pide cambios.
  - GitHub solo deja comentar líneas del diff. Los hallazgos fuera del diff van al resumen.
  - La review saca los hallazgos también en un bloque JSON, para que el job los publique sin interpretar texto libre. El job valida cada `path` y `line` contra el diff antes de publicar, y sigue sin ejecutar ningún modelo (D-0027).
  - Al repetir la review tras un push, los comentarios anteriores se quedan (GitHub marca como desactualizados los de líneas que cambiaron) y solo se actualiza el resumen.
- **Resumen corto,** unas 15 líneas: veredicto y nivel de riesgo, recuento por gravedad, una línea por cada Critical y Required con enlace a su comentario. Los Optional, los Nits y la verificación van plegados en `<details>`.
- **En local,** `/review-pr` usa el mismo formato corto por defecto, con una opción para el informe completo.

## 3. Compatibilidad con atril (fase 2)

[atril](https://github.com/manufosela/karajan-code/tree/main/packages/atril) guarda skills, comandos y agentes en un almacén (`.atril/` del proyecto y `~/.atril` de la persona) y carga solo los que necesita cada tarea (`atril route`). Lo que se fija de forma permanente pasa a cada herramienta con [rulesync](https://github.com/dyoshikawa/rulesync).

### 3.1 Qué se probó

Prueba del 2026-10-28 con atril 1.1.0 y rulesync, en un proyecto de usar y tirar:

| Qué | Resultado |
|---|---|
| Instalar una skill o un agente del kit | Falla: `missing kind`, también desde un catálogo local |
| Skills globales (`~/.claude/skills`) | `atril import --from openskills --root ~/.atril` desde el home las mueve a `~/.atril` y borra la original; el proyecto las ve |
| `review-pr` con `uses` y `delegates` | `atril route` devuelve el bloque entero en orden: skills de apoyo, los cuatro agentes y `review-pr` |
| `review-pr` sin relaciones | Carga sola; `atril enrich` no deduce las relaciones del texto. Instalar una skill no instala sus dependencias |
| Scripts (`task_done.py`, `board.py`) | Se copian con la carpeta de la skill |
| Búsqueda | Por palabras; con descripciones en inglés, las tareas en español encajan peor |
| Plugins (`/plugin`) | atril no tiene comando para ellos; para tener `harness` bajo demanda hay que desinstalar el plugin |
| rulesync `generate` | Escribe `CLAUDE.md`, `.claude/rules`, `settings.json` y más en el proyecto |

### 3.2 Permisos: qué se pierde y en qué herramienta

Hay dos cosas distintas:

- **`allowed-tools` de una skill** (Claude Code): **no restringe**, aprueba de antemano. Durante el turno que invoca la skill, esas herramientas se usan sin pedir permiso; el resto siguen disponibles con los permisos normales, y la aprobación se borra con el siguiente mensaje. En el kit solo lo usan `review-prepush` y `review-pr` (lectura, `Agent`, git y `gh pr` de solo lectura). Si atril carga la skill leyendo el fichero (`route`, `/atril`), no se invoca como skill y esas herramientas **piden permiso**. Es fricción, no un agujero de seguridad. En los modos sin persona (`claude -p` en el hook y en CI) no afecta: allí los permisos se pasan con `--allowedTools`. Se evita con esos permisos en los ajustes o exponiendo las dos skills con `atril expose`.
- **`disallowed-tools` de una skill** (Claude Code): **sí restringe** mientras la skill está activa. Hoy no lo usa ninguna skill del kit; si alguna lo usa, cargarla vía atril perdería la restricción.
- **Codex y OpenCode no tienen ninguno de los dos campos.** Codex solo admite `name` y `description` en `SKILL.md` (más `policy.allow_implicit_invocation` y `dependencies.tools` en `agents/openai.yaml`, que no restringen); sus permisos son de la sesión. OpenCode admite `name`, `description`, `license`, `compatibility` y `metadata`, ignora las demás claves, y sus permisos son del agente (`permission`, incluido `permission.skill` para qué skills puede cargar). Restringir desde la skill solo existe en Claude Code, así que la protección del kit va en los agentes y en `--allowedTools`/`--disallowedTools`, nunca en `disallowed-tools` de una skill.
- **`tools` de un agente:** **sí restringe**. Es lo que deja a `code-reviewer` y al resto de la review en solo lectura. Perderlo es un problema de seguridad.

| Herramienta | `allowed-tools` de las skills | Restricción de herramientas de los agentes | Con atril y rulesync |
|---|---|---|---|
| Claude Code | Lo usa (aprobación previa) | `tools:` en el agente | rulesync **quita** `tools` y `skills` si van arriba; los **conserva** dentro de un bloque `claudecode:` (probado) |
| Codex | No lo usa: los permisos son de la sesión (sandbox y política de aprobación) | Hoy ninguna: `build-agents.py` asume que el agente hereda el sandbox de la sesión | rulesync escribe `sandbox_mode` en el `.toml` del agente si va en un bloque `codexcli:` (probado). Falta comprobar si Codex lo respeta por agente |
| OpenCode | No lo usa: los permisos son del agente | `permission:` en el agente (edit, bash, webfetch, task) | rulesync traduce un bloque `opencode:` a la lista `permissions:`, que es el formato propio de OpenCode 2. Los dos restringen en OpenCode 2.2.0 (probado, §3.3) |

Conclusión: la pérdida de `allowed-tools` solo existe en Claude Code y es fricción. En Codex y OpenCode ya no se usa hoy, con o sin atril. Lo que importa son las restricciones de los agentes, y rulesync las conserva si cada agente las declara en el bloque de cada herramienta.

### 3.3 Prueba de OpenCode (2026-10-28)

Con OpenCode 2.2.0 y `opencode run --auto` (aprueba todo lo que no está denegado), un agente al que se pide escribir un fichero y ejecutar `touch`:

| Agente | Escribir | Shell |
|---|---|---|
| Sin restricciones | sí | sí |
| `permission:` (v1, nuestro adaptador) | no | no |
| `permissions:` (v2, el de rulesync) | no | no |
| v1 con `kind` y `uses` de atril | no | no |
| v1 con un campo de v2 (`disabled: false`) | **sí** | **sí** |

- OpenCode 2 lee el formato v1 con su capa de compatibilidad, e ignora las claves que no conoce. El adaptador sigue en v1, que también entiende OpenCode 1.
- **Mezclar** `permission:` con un campo de v2 (`permissions`, `request`, `system`, `disabled`) hace que OpenCode ignore `permission:` sin avisar. `check.sh` lo prohíbe en los adaptadores.
- **Agujero encontrado:** el adaptador no denegaba `task`, y `code-reviewer` creó un fichero delegando en el subagente `general`, que no tiene restricciones. Ahora `task` solo se permite a un agente con `Agent` en `tools:`, y `check.sh` lo comprueba.
- `bash: ask` se aprueba solo con `--auto`: igual que en Claude Code sin nadie delante, la barrera es la lista de lo denegado, no un sandbox (`docs/review/README.md`).

### 3.4 Qué cambia en el kit

1. `kind: skill` o `kind: agent` en todo el frontmatter.
2. `uses` y `delegates` donde hay dependencia real (las reviews, `implement`, `idea-to-change`, el SDD).
3. En cada agente, bloques `claudecode:` y `opencode:` con sus restricciones, generados por `build-agents.py` desde `tools:`, para no escribirlos a mano. Sin bloque `codexcli:`: `sandbox_mode` por agente no se aplica en Codex (el agente hereda el de la sesión), y un bloque que lo declara prometería una restricción que no existe.
4. `check.sh` valida las reglas de atril (nombre en minúsculas, `kind`, relaciones bien formadas).
5. Antes de nada, comprobar que Claude Code, Codex y OpenCode ignoran esas claves de más cuando el kit se instala como plugin o con `npx skills`.
6. Documentar el uso recomendado:
   - **Fijo**, con `atril expose`: los agentes, para que conserven sus restricciones, las skills de uso diario (`task-done`, `idea-to-change`) y todo lo que usan (§3.5).
   - **Bajo demanda:** el resto (SDD, `generate-project-context`, `setup-guardrails-python`, `debug-root-cause`).
   - Primero en Claude Code; Codex y OpenCode cuando se compruebe lo que falta en la tabla.

### 3.5 Prueba de punta a punta (2026-10-29)

En un contenedor `node:22` con atril 1.2.0 y rulesync 43.2.0, sobre un proyecto vacío:

- **Instalar:** las 17 skills y los 6 agentes entran sin errores (antes, `missing kind`).
- **Un ciclo lo rompía todo.** `review-spec` delegaba en `spec-reviewer`, que usa `review-spec`, y `atril route`, `graph` y `enrich` fallaban para cualquier tarea. `spec-reviewer` pasa a `related` de `review-spec`, y `check.sh` busca ciclos en `uses` y `delegates`.
- **`atril route`** devuelve el bloque completo y en orden: «review my branch before pushing» trae `review-context`, `review-report`, `task-done`, los dos agentes con sus skills precargadas y `review-prepush`. «review this pull request» empata con `code-review-and-quality` (búsqueda por palabras), y las tareas en español encajan peor.
- **`atril enrich`** solo añade `keywords` y un hash en el bloque `atril:` de la copia del almacén; no se commitea en el kit.
- **rulesync también quita `allowed-tools` y `argument-hint` de las skills** si no van en un bloque `claudecode:`. `build-agents.py` lo escribe ahora también en las skills que tienen campos solo de Claude Code (`review-pr`, `review-prepush`).
- **`atril expose` no fija lo que usa cada pieza:** un agente fijado sin sus skills precargadas no las encuentra. El README da la lista completa, que es el cierre de `uses`: 6 agentes y 10 skills; 7 quedan bajo demanda.
- **`rulesync init` no incluye `commands`** en `features`, y sin él no se genera el puente `/atril`.
- **Resultado en Claude Code 2.1.312:** carga los 6 agentes con sus herramientas (`code-reviewer`: `Read, Grep, Glob, Bash`) y las 10 skills; `review-pr` conserva `allowed-tools`. En OpenCode, los agentes salen en formato v2 con `edit` y `subagent` denegados. `atril sync --check` pasa.
- **Plugins:** atril 1.2.0 tiene código para plugins, pero ningún comando que lo use. El plugin `harness` sigue instalándose aparte (`/plugin`), y no conviene tenerlo a la vez que el almacén, porque cargaría todo.
- Del punto 5 de §3.4: Claude Code carga el plugin con las claves nuevas y `claude plugin validate --strict` pasa; Codex 0.165 carga una skill con `kind`, `uses` y `delegates` (`codex debug prompt-input`); OpenCode 2.2.0 ignora `kind` y `uses` sin perder `permission:` (§3.3).

## 4. Mejoras pequeñas (fase 3)

Del [plan de mejoras](plan-de-mejoras.md), lo que sigue siendo útil:

1. Tope de tamaño para `SKILL.md` y agentes en `check.sh` (ideas 9 y 3.4).
2. Veredicto ligado al hash del diff en el hook pre-push (#7).
3. Falsos positivos conocidos, con su motivo, que llegan al `finding-verifier` (idea 8).
4. Semgrep solo en las líneas añadidas (idea 18).
5. Reglas de complejidad de ruff en `setup-guardrails-python` (idea 20).
6. Tabla de qué se garantiza en cada herramienta (idea 7).

Hecho (2026-10-29):

1. `check.sh` limita las descripciones a 1.024 caracteres y cada `SKILL.md` o agente a 12.500 (22.000 los copiados de addyosmani, que no crecen). Subir un tope es una decisión explícita en el propio `check.sh`.
2. El hook pre-push guarda el veredicto con el sha256 del diff y lo reutiliza; `REVIEW_KIT_RERUN=1` repite la review (D-0042).
3. `Known non-issues` en la sección `Code review` de AGENTS.md, cada uno con su motivo. Llega al `finding-verifier`, que los refuta mientras el motivo siga siendo cierto.
4. `review-context/scripts/semgrep_added.py`: Semgrep solo cuenta los hallazgos en líneas añadidas (D-0043).
5. `C90`, `PLR0912` y `PLR0915` en el `pyproject.toml` de `setup-guardrails-python`, probados con ruff.
6. La tabla está en el README, «Qué se garantiza en cada herramienta».

Al aprobarse este plan, `plan-de-mejoras.md` pasó a ser histórico, con una nota que remite aquí, y #2 se cerró (cubierto por la fase 5 de la v2).
