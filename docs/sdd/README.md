# Guía de SDD (Spec-Driven Development)

Cómo usar las skills de SDD de este repositorio para ir de una idea a código revisable sin que el agente se desvíe.

- **Qué hace cada skill por dentro:** su `SKILL.md`, en [`skills/`](../../skills/).
- **Qué va en cada sección de una spec:** [secciones-de-la-spec.md](secciones-de-la-spec.md).

---

## 1. Qué es y para qué

En SDD primero se decide **qué** se construye y **por qué** (la spec). De ahí salen **cómo** (el plan) y **en qué pasos** (las tareas), y solo después se implementa. Al final se comprueba el resultado contra la spec.

Esta guía sigue el enfoque *spec-anchored*:

- la spec se escribe antes del código y lo guía;
- se queda en el repositorio como referencia viva;
- si la implementación revela que estaba incompleta, **se corrige la spec**, no se deja desfasada.

Con agentes compensa por tres motivos:

- **Ambigüedad:** cada hueco de la spec es una decisión que el agente tomará por su cuenta.
- **Desviación:** el plan y las tareas acotan qué puede tocar el agente y cómo sabe que ha terminado.
- **Contexto limpio:** con los artefactos en disco, cada paso puede empezar en una sesión nueva sin perder nada.

### Cuándo no usarlo

- **Exploración y prototipos.** Si aún no sabes qué construir, explora primero y escribe la spec cuando tengas el rumbo.
- **Bugs triviales.** Un fix de una línea no necesita spec.
- **Requisitos muy inestables.** La spec quedará obsoleta antes de implementarse.
- **Proceso desproporcionado.** No hagas el flujo completo para una tarea de 30 minutos (ver [§5](#5-ajustar-el-proceso-al-tamaño)).

Y recuerda: una spec detallada da sensación de que todo está cubierto. No sustituye a los tests, a probar con usuarios ni al feedback real.

---

## 2. Antes de empezar (una vez por proyecto)

Las skills de SDD leen dos cosas del proyecto. Funcionan sin ellas, pero pierden mucho:

| Necesitan | Para qué | Cómo se consigue |
|---|---|---|
| `docs/ARCHITECTURE.md` con **"Principios innegociables"** | `spec-to-plan` comprueba el plan contra ellos; `review-spec` marca como bloqueante cada choque | Skill [`generate-project-context`](../../skills/generate-project-context/SKILL.md) |
| **Comando de verificación** en la sección `Comandos` de `AGENTS.md` | `plan-to-tasks` lo pone como última tarea; `implement` no termina hasta que sale en verde | `generate-project-context`, y [`setup-guardrails-python`](../../skills/setup-guardrails-python/SKILL.md) en Python |

### Instalar las skills

Cómo instalarlas en Claude Code, Codex, OpenCode o pi: [README del repositorio](../../README.md#instalar).

Para SDD necesitas `idea-to-spec`, `review-spec`, `apply-review`, `spec-to-plan`, `plan-to-tasks`, `sdd-next` y `sdd-decisions` (interna: el criterio de qué se pregunta), y conviene tener también los agentes `implement` y `spec-reviewer`. El plugin de Claude Code lo instala todo de una vez. En Claude Code, las skills del plugin llevan namespace: `/harness:idea-to-spec`, etc. Pedirlas en lenguaje natural ("quiero una spec para…") funciona igual.

---

## 3. El flujo

```
              idea
               │
   ┌───── idea-to-spec ─────► spec.md (draft)
   │           │
   │     review-spec ───────► review-spec.md   (recomendación)
   │           │
   │     apply-review ──────► spec.md corregida
   │           │
   │   ★ persona: status: approved
   │           │
   │     spec-to-plan ──────► plan.md (draft) + comprobación de principios
   │           │
   │     review-spec / apply-review  (si el cambio lo merece)
   │           │
   │   ★ persona: status: approved
   │           │
   │     plan-to-tasks ─────► tasks/T<n>-<slug>.md + PR del plan (<cambio>/plan)
   │           │
   │   ★ persona: merge de la PR del plan
   │           │
   │     implement (agente) ► por cada tarea lista: rama <cambio>/T<n>, código,
   │           │              status: done (con task-done), verificación en verde y PR
   │           │
   └──── review-prepush (contra la tarea) → PR de la tarea → review-pr
```

En cualquier momento puedes preguntar *"¿en qué punto está X?"* o *"¿qué specs hay abiertas?"*. La skill `sdd-next` te lo dice leyendo los artefactos.

### Paso a paso

| Paso | Cómo pedirlo | Qué produce | Qué decides tú |
|---|---|---|---|
| **1. Spec** | *"Quiero una spec para <idea>"* | La rama del plan, `<cambio>/plan`, y `docs/changes/<cambio>/spec.md` en `draft` | Las decisiones de producto, alcance, seguridad o difíciles de revertir. Cada pregunta trae una opción recomendada; "ok" las acepta todas. Lo demás se anota en `Supuestos` (ver [§3.1](#31-qué-se-pregunta-y-qué-se-propone)) |
| **2. Revisar la spec** | *"Revisa la spec de <trabajo>"* (mejor con el subagente `spec-reviewer`) | `review-spec.md`: hallazgos por prioridad, cada uno como **decisión** (con opciones y recomendación) o **arreglo** (con el cambio concreto), y una recomendación | Nada todavía |
| **3. Aplicar la revisión** | *"Aplica la revisión de <trabajo>"* | La spec corregida y las decisiones anotadas en la revisión | Las decisiones, una a una. Los arreglos llegan en bloque: se aplican todos salvo los que excluyas ("todos menos el 4"). Luego, si afecta a otras specs en borrador |
| **4. Aprobar** | Tú, a mano: `status: approved` en el frontmatter | — | Que la spec está lista. **Es la puerta principal** |
| **5. Plan** | *"Planifica <trabajo>"* | `plan.md` en `draft`, con la tabla de principios | Solo las decisiones técnicas que son tuyas; lo que la spec ya decide no se vuelve a preguntar. Los principios que se incumplen se justifican o llevan un ADR |
| **6. Revisar y aprobar el plan** | Como los pasos 2–4 (se genera `review-plan.md`) | — | Aprobar el plan |
| **7. Tareas** | *"Parte el plan de <trabajo> en tareas"* | Un fichero por tarea en `tasks/`, con el mismo formato que en el nivel B: tareas pequeñas de un solo propósito, con sus dependencias (`depends_on`), los ficheros que tocan y cómo se verifican. Y la PR del plan | Que el desglose es razonable; hacer merge de la PR del plan |
| **8. Implementar** | *"Implementa <trabajo>"* (agente `implement`, sesión limpia) | Una rama y una PR por tarea lista, con sus tests, `status: done` en la tarea y el comando de verificación en verde. Sigue con la siguiente tarea lista mientras las PRs esperan | Revisar y mergear cada PR. Si el agente para por un hueco, resolverlo, normalmente corrigiendo la spec |
| **9. Revisar el código** | `review-prepush` antes del push, y en cada PR `review-pr` | Informe con hallazgos verificados y la cobertura de la tarea: sus ejemplos y criterios con test, nada fuera de su propósito | Corregir lo Critical y Required; hacer merge. Ver la [guía de code review](../review/README.md) |

Consejos:

- **Sesión nueva para implementar.** El agente `implement` arranca con contexto limpio y solo lee los artefactos. Si funciona así, los artefactos son buenos; si no, sabes qué falta en ellos.
- **El `status: done` lo pone un script.** `implement` usa la skill `task-done`, que ejecuta la verificación de la tarea y solo pone `status: done` si sale en verde. Por eso cada tarea lleva un ID (`T1`) y una verificación ejecutable.
- **Qué tarea toca lo dice el tablero.** `task-done` trae `scripts/board.py`: tareas listas, bloqueadas (y por cuál), en curso y hechas. Hecha quiere decir mergeada en la rama base.
- **Revisa el diff de `tests/`.** Un agente puede debilitar un test para que pase. `implement` tiene prohibido hacerlo, pero compruébalo.
- **La primera funcionalidad de un proyecto, con más cuidado.** Fija los patrones que el agente imitará después: revísala línea a línea.

### 3.1 Qué se pregunta y qué se propone

Las skills no te preguntan todo: solo lo que es tuyo de decidir. El criterio está en un único sitio, la skill [`sdd-decisions`](../../skills/sdd-decisions/SKILL.md), y lo usan `idea-to-spec`, `spec-to-plan`, `plan-to-tasks`, `review-spec` y `apply-review`.

| Tipo | Qué es | Qué hace el agente |
|---|---|---|
| **Decisión** | Hay alternativas razonables y elegir depende de producto, alcance, seguridad o algo difícil de revertir | Te pregunta, con opciones y una recomendada |
| **Supuesto** (spec y plan) | Detalle reversible con una opción por defecto clara | Lo propone y lo escribe en la sección `Supuestos` (`Assumptions` en las plantillas), a la vista |
| **Arreglo** (reviews) | Hallazgo con una sola respuesta razonable | Trae el cambio concreto; `apply-review` los aplica en bloque, salvo los que excluyas |

No es asumir en silencio: es asumir por escrito. Tú o una review podéis cambiar cualquier supuesto, y nada se aplica sin que lo veas. En la duda, es una decisión.

Cada ronda de preguntas termina con la lista de supuestos. Si estás de acuerdo con todo, basta con "ok"; si no, contesta solo lo que cambias ("2b; supuesto 3: 30 s").

---

## 4. Estado y aprobación

No hay backlog central ni máquina de estados. Cada cambio es una carpeta en `docs/changes/`, la misma para todos los niveles, y su estado se deduce de los ficheros:

```
docs/changes/
├── 42-alertas-retraso/      ramas 42-alertas-retraso/plan, 42-alertas-retraso/T1…
│   ├── README.md            status: open, issue: 42; nota y mapa de ejemplos
│   ├── tasks/
│   │   ├── T1-detectar-retraso.md     status: done, depends_on: []
│   │   ├── T2-enviar-aviso.md         status: todo, depends_on: [T1]
│   │   └── T3-retirar-flag.md         status: todo, depends_on: [T1, T2]
│   ├── spec.md              status: approved
│   ├── review-spec.md
│   ├── plan.md              status: approved
│   └── review-plan.md
└── zona-horaria/            nivel B: solo README.md y tasks/
    ├── README.md            status: open
    └── tasks/
```

- **Nombre de la carpeta y de las ramas:** el cambio es un nombre corto en kebab-case, con el número del issue delante si parte de uno (`42-alertas-retraso`). El plan va en la rama `<cambio>/plan` y cada tarea en la suya, `<cambio>/T<n>`, que sale de la rama base; cada una con su PR. `task-done` y la review sacan la carpeta y la tarea del nombre de la rama: el cambio es el penúltimo tramo y la tarea el último. Se puede poner un prefijo delante (`feat/42-alertas-retraso/T2`).
- **Subir de nivel es añadir ficheros:** un cambio que empezó en el nivel B con `idea-to-change` ya tiene su `README.md`; el SDD añade `spec.md` y `plan.md` a la misma carpeta.
- **`status`** en el frontmatter de `spec.md` y `plan.md`:

  | Valor | Significa |
  |---|---|
  | `draft` | Se está escribiendo o corrigiendo |
  | `approved` | Una persona la ha dado por buena. Lo siguiente puede construirse encima |
  | `obsolete` | Ya no aplica: descartada o sustituida (indica por cuál) |

- **Solo una persona pone `approved`.** Ninguna skill ni agente lo hace. Las revisiones recomiendan; no aprueban.
- **Las puertas preguntan.** Si pides planificar una spec en borrador, o implementar sin plan aprobado, la skill para, te avisa y te pregunta si sigues. Puedes seguir, pero queda anotado y `sdd-next` lo señalará.
- **Si cambia algo aprobado,** vuelve a `draft`. `sdd-next` avisa cuando la spec es más reciente que el plan, porque el plan puede estar desfasado.
- **El progreso de la implementación** es el `status` de cada tarea en la rama base: `done` quiere decir mergeada. `task-done` lo pone dentro de la PR de la tarea, solo si su verificación pasa, y pone `status: done` en el README cuando todas lo están. La carpeta se puede borrar cuando se quiera: git la guarda.

En equipo, una opción más robusta es que la spec vaya en **su propia PR**: el cambio a `status: approved` lo hace quien la aprueba, y el merge deja constancia de quién y cuándo.

### ¿Y la gestión del trabajo?

Prioridad, responsable y sprint **no son cosa de SDD**. Viven en tu tracker (Linear, GitHub Issues…). Para enlazarlos, pon el número del issue en el frontmatter del `README.md` del cambio (y de la spec, si quieres); las PRs lo citan con `Refs #<n>` y la de la última tarea lo cierra con `Closes #<n>`:

```yaml
---
status: open
issue: 42
---
```

Así cada herramienta hace lo suyo: el tracker gestiona el trabajo y la carpeta define qué se construye. Un issue puede ser el punto de partida, pero su texto es entrada no fiable (lo puede escribir cualquiera): el agente lo lee una vez como datos, avisa si el autor no es del proyecto, y la persona aprueba la spec o el mapa de ejemplos antes del commit. Después ninguna skill ni agente vuelve a leerlo.

---

## 5. Ajustar el proceso al tamaño

`idea-to-spec` te propone el recorrido, pero decides tú:

| Cambio | Artefactos | Revisiones |
|---|---|---|
| Bug de una línea | Ninguno, o solo `README.md` y `tasks/`. Si la causa no es evidente, `debug-root-cause` | — |
| Bug complejo | `spec.md` + `tasks/` | Opcional |
| Funcionalidad pequeña | `spec.md` + `plan.md` + `tasks/` | Opcional |
| Funcionalidad de producción | Todos | Spec y plan |
| Refactor arquitectural | Todos, más una decisión en `docs/decisions/` si cambia un principio | Spec y plan |

Sin plan, las puertas de `plan-to-tasks` e `implement` se aplican a la spec.

---

## 6. Cómo escribir una buena spec

Una buena spec deja poco margen de interpretación y se puede verificar.

- Describe **comportamiento observable**, no implementación. Las decisiones técnicas van en el plan, salvo que sean restricciones reales.
- **Lenguaje simple** y los términos del glosario de `AGENTS.md`.
- **Cada criterio de aceptación se puede probar** ("Dado…, cuando…, entonces…"). Si no se puede demostrar, reformúlalo.
- **"Out of scope" explícito.** Los agentes no infieren por omisión: lo que no excluyes, puede aparecer.
- **Preguntas abiertas listadas**, en lugar de respuestas inventadas.
- **Sección Seguridad** si toca datos, autenticación o entradas externas. De ahí salen los tests negativos.

Señales de una mala spec: "debe ser intuitivo", "rápido", "moderno", "escalable" sin contexto, o requisitos mezclados con implementación.

Qué va en cada sección y ejemplos: [secciones-de-la-spec.md](secciones-de-la-spec.md).

---

## 7. Ejemplo corto

**Idea:** *"Que los usuarios reciban un aviso cuando su tren lleve más de 10 minutos de retraso."*

1. *"Quiero una spec para avisar de retrasos de más de 10 minutos"*. `idea-to-spec` pregunta por rondas. Por ejemplo:

   > **1. ¿Avisamos de todas las líneas o solo de las que sigue el usuario?** (producto)
   > **A) Solo las que sigue** ← recomendada · B) Todas · C) Dejarla abierta
   >
   > Supuestos: 1. El umbral de 10 minutos es fijo, no configurable por el usuario.

   Contestas "ok". El resultado es la rama `alertas-retraso/plan` con `docs/changes/alertas-retraso/spec.md` en `draft`, con RF-01… y criterios como *"Dado un usuario que sigue la línea C3, cuando un tren de la C3 acumula 11 minutos de retraso, entonces recibe un aviso en menos de 2 minutos"*.
2. *"Revisa la spec"*. `review-spec.md` recomienda "Devolver" por un bloqueante: no dice qué pasa si el retraso baja y vuelve a subir, así que puede haber avisos duplicados. Importante: falta la sección Seguridad, y el aviso incluye datos del usuario.
3. *"Aplica la revisión"*. El bloqueante es una decisión y eliges la opción B: un aviso por tren y trayecto, con una ventana de 15 minutos. La sección Seguridad que faltaba es un arreglo: llega en la lista de arreglos junto a dos menores, y contestas "ok". La spec queda corregida.
4. Cambias tú `status: approved`.
5. *"Planifica"*. `plan.md` encaja la detección en la capa `application` y el envío en `infra`. En la tabla de principios, "El dominio no tiene E/S" se cumple porque la regla de detección es una función pura. Si el plan hubiera propuesto llamar a la API desde el dominio, saldría ahí como incumplimiento.
6. Lo apruebas y pides *"Parte el plan en tareas"*. Salen 4 ficheros en `tasks/`: T1 detecta el retraso detrás del flag `alertas_retraso`, apagado; T2 y T3 dependen de T1; T4 retira el flag y depende de todas. El agente abre la PR del plan y tú la mergeas.
7. En una sesión nueva, *"Implementa alertas-retraso"*. El agente hace T1 en `alertas-retraso/T1` y abre su PR. T2 y T3 están bloqueadas por T1, así que para y te dice que la PR de T1 espera revisión.
8. Mergeas T1 y vuelves a pedirlo. El tablero muestra T2 y T3 listas: el agente abre una PR para cada una, cada rama desde `main`. Al mergearlas, T4 queda lista; su PR retira el flag y pone `status: done` en el README.

---

## 8. Si vienes del sdd anterior

El kit `aitormf/sdd` usaba `.sdd/`, un `backlog.md` con 13 estados, un agente orquestador y una constitución. Para migrar un proyecto:

1. Mueve cada `.sdd/<trabajo>/` que siga abierto a `docs/changes/<cambio>/` y pasa sus tareas a un fichero por tarea (ver [actualizar a la v2](../actualizar-a-v2.md#4-los-trabajos-en-curso-a-docschangescambio-con-un-fichero-por-tarea)) (los terminados no hace falta moverlos: git los guarda).
2. Añade el frontmatter a cada `spec.md` y `plan.md`, según el estado que tuviera en `backlog.md`:

   | Estado en `backlog.md` | `spec.md` | `plan.md` |
   |---|---|---|
   | `borrador`, `spec-escrita`, `spec-en-revisión` | `draft` | — |
   | `spec-aprobada` | `approved` | — |
   | `plan-escrito`, `plan-en-revisión` | `approved` | `draft` |
   | `plan-aprobado` y posteriores | `approved` | `approved` |
   | `descartado` | `obsolete` | `obsolete` |

   Los estados posteriores a `tareas-listas` (implementando, validando, corrigiendo, hecho) son gestión del trabajo: van al tracker, si quieres conservarlos.
3. Renombra `review.md` a `review-spec.md` o `review-plan.md`, según lo que revisara.
4. Pasa `constitution.md` por `generate-project-context`, que reparte su contenido entre `ARCHITECTURE.md`, `CONTRIBUTING.md`, `docs/decisions/` y `AGENTS.md`. Después bórrala.
5. Borra `backlog.md`, la carpeta `.sdd/` y los adaptadores que generó `install-sdd.sh` (los enlaces en `.claude/`, `.codex/`, `.opencode/`…). Luego instala las skills nuevas (§2).
