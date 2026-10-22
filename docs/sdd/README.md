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
   │     plan-to-tasks ─────► tasks.md
   │           │
   │     implement (agente) ► código + [x] en tasks.md + verificación en verde
   │           │
   └──── review-prepush (contra la spec) → PR → review-pr
```

En cualquier momento puedes preguntar *"¿en qué punto está X?"* o *"¿qué specs hay abiertas?"*. La skill `sdd-next` te lo dice leyendo los artefactos.

### Paso a paso

| Paso | Cómo pedirlo | Qué produce | Qué decides tú |
|---|---|---|---|
| **1. Spec** | *"Quiero una spec para <idea>"* | `docs/specs/<trabajo>/spec.md` en `draft` | Las decisiones de producto, alcance, seguridad o difíciles de revertir. Cada pregunta trae una opción recomendada; "ok" las acepta todas. Lo demás se anota en `Supuestos` (ver [§3.1](#31-qué-se-pregunta-y-qué-se-propone)) |
| **2. Revisar la spec** | *"Revisa la spec de <trabajo>"* (mejor con el subagente `spec-reviewer`) | `review-spec.md`: hallazgos por prioridad, cada uno como **decisión** (con opciones y recomendación) o **arreglo** (con el cambio concreto), y una recomendación | Nada todavía |
| **3. Aplicar la revisión** | *"Aplica la revisión de <trabajo>"* | La spec corregida y las decisiones anotadas en la revisión | Las decisiones, una a una. Los arreglos llegan en bloque: se aplican todos salvo los que excluyas ("todos menos el 4"). Luego, si afecta a otras specs en borrador |
| **4. Aprobar** | Tú, a mano: `status: approved` en el frontmatter | — | Que la spec está lista. **Es la puerta principal** |
| **5. Plan** | *"Planifica <trabajo>"* | `plan.md` en `draft`, con la tabla de principios | Solo las decisiones técnicas que son tuyas; lo que la spec ya decide no se vuelve a preguntar. Los principios que se incumplen se justifican o llevan un ADR |
| **6. Revisar y aprobar el plan** | Como los pasos 2–4 (se genera `review-plan.md`) | — | Aprobar el plan |
| **7. Tareas** | *"Parte el plan de <trabajo> en tareas"* | `tasks.md`: tareas pequeñas con los ficheros que tocan y cómo se verifican | Que el desglose es razonable |
| **8. Implementar** | *"Implementa <trabajo>"* (agente `implement`, sesión limpia) | Código y tests, `[x]` en cada tarea verificada y el comando de verificación en verde | Revisar el diff. Si el agente para por un hueco, resolverlo, normalmente corrigiendo la spec |
| **9. Revisar el código y PR** | *"¿Está lista para push?"* (`review-prepush`), y en la PR `review-pr` | Informe con hallazgos verificados y la cobertura de la spec: criterios con test, nada fuera de alcance, tareas `[x]` hechas | Corregir lo Critical y Required; hacer merge. Ver la [guía de code review](../review/README.md) |

Consejos:

- **Sesión nueva para implementar.** El agente `implement` arranca con contexto limpio y solo lee los artefactos. Si funciona así, los artefactos son buenos; si no, sabes qué falta en ellos.
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

No hay backlog central ni máquina de estados. Cada trabajo es un directorio, y su estado se deduce de los ficheros:

```
docs/specs/
├── 20261016-feat-alertas-retraso/
│   ├── spec.md            status: approved
│   ├── review-spec.md
│   ├── plan.md            status: approved
│   ├── review-plan.md
│   └── tasks.md           5/8 tareas [x]
└── 20261020-fix-zona-horaria/
    ├── spec.md            status: draft
    └── tasks.md
```

- **Nombre del directorio:** `YYYYMMDD-tipo-nombre`. La fecha es la de creación (da orden y evita colisiones entre ramas). El tipo va como en Conventional Commits: `feat`, `fix`, `refactor`, `docs`…
- **`status`** en el frontmatter de `spec.md` y `plan.md`:

  | Valor | Significa |
  |---|---|
  | `draft` | Se está escribiendo o corrigiendo |
  | `approved` | Una persona la ha dado por buena. Lo siguiente puede construirse encima |
  | `obsolete` | Ya no aplica: descartada o sustituida (indica por cuál) |

- **Solo una persona pone `approved`.** Ninguna skill ni agente lo hace. Las revisiones recomiendan; no aprueban.
- **Las puertas preguntan.** Si pides planificar una spec en borrador, o implementar sin plan aprobado, la skill para, te avisa y te pregunta si sigues. Puedes seguir, pero queda anotado y `sdd-next` lo señalará.
- **Si cambia algo aprobado,** vuelve a `draft`. `sdd-next` avisa cuando la spec es más reciente que el plan, porque el plan puede estar desfasado.
- **El progreso de la implementación** son las casillas de `tasks.md`. Solo se marcan las tareas verificadas.

En equipo, una opción más robusta es que la spec vaya en **su propia PR**: el cambio a `status: approved` lo hace quien la aprueba, y el merge deja constancia de quién y cuándo.

### ¿Y la gestión del trabajo?

Prioridad, responsable, sprint y "hecho" **no son cosa de SDD**. Viven en tu tracker (Linear, GitHub Issues…). Para enlazarlos, pon el ID en el frontmatter de la spec:

```yaml
---
status: approved
issue: TRIBBU-123
---
```

Así cada herramienta hace lo suyo: el tracker gestiona el trabajo y la spec define qué se construye. Ninguna skill de SDD lee ni escribe en el tracker.

---

## 5. Ajustar el proceso al tamaño

`idea-to-spec` te propone el recorrido, pero decides tú:

| Cambio | Artefactos | Revisiones |
|---|---|---|
| Bug de una línea | Ninguno, o solo `tasks.md` | — |
| Bug complejo | `spec.md` + `tasks.md` | Opcional |
| Funcionalidad pequeña | `spec.md` + `plan.md` + `tasks.md` | Opcional |
| Funcionalidad de producción | Todos | Spec y plan |
| Refactor arquitectural | Todos, más un ADR si cambia un principio | Spec y plan |

Sin plan, las puertas de `plan-to-tasks` e `implement` se aplican a la spec.

---

## 6. Cómo escribir una buena spec

Una buena spec deja poco margen de interpretación y se puede verificar.

- Describe **comportamiento observable**, no implementación. Las decisiones técnicas van en el plan, salvo que sean restricciones reales.
- **Lenguaje simple** y los términos del glosario de `ARCHITECTURE.md`.
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

   Contestas "ok". El resultado es `docs/specs/20261016-feat-alertas-retraso/spec.md` en `draft`, con RF-01… y criterios como *"Dado un usuario que sigue la línea C3, cuando un tren de la C3 acumula 11 minutos de retraso, entonces recibe un aviso en menos de 2 minutos"*.
2. *"Revisa la spec"*. `review-spec.md` recomienda "Devolver" por un bloqueante: no dice qué pasa si el retraso baja y vuelve a subir, así que puede haber avisos duplicados. Importante: falta la sección Seguridad, y el aviso incluye datos del usuario.
3. *"Aplica la revisión"*. El bloqueante es una decisión y eliges la opción B: un aviso por tren y trayecto, con una ventana de 15 minutos. La sección Seguridad que faltaba es un arreglo: llega en la lista de arreglos junto a dos menores, y contestas "ok". La spec queda corregida.
4. Cambias tú `status: approved`.
5. *"Planifica"*. `plan.md` encaja la detección en la capa `application` y el envío en `infra`. En la tabla de principios, "El dominio no tiene E/S" se cumple porque la regla de detección es una función pura. Si el plan hubiera propuesto llamar a la API desde el dominio, saldría ahí como incumplimiento.
6. Lo apruebas y pides *"Parte el plan en tareas"*. `tasks.md` tiene 6 tareas, cada una con su test. La última es `./scripts/check.sh` en verde.
7. En una sesión nueva, *"Implementa alertas-retraso"*. El agente marca 6/6 y termina con la verificación en verde.
8. *"¿Qué specs hay abiertas?"*. `sdd-next` muestra este trabajo como listo para PR y otro en borrador sin revisar.

---

## 8. Si vienes del sdd anterior

El kit `aitormf/sdd` usaba `.sdd/`, un `backlog.md` con 13 estados, un agente orquestador y una constitución. Para migrar un proyecto:

1. Mueve cada `.sdd/<trabajo>/` a `docs/specs/<trabajo>/`.
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
4. Pasa `constitution.md` por `generate-project-context`, que reparte su contenido entre `ARCHITECTURE.md`, `CONTRIBUTING.md`, los ADRs y `AGENTS.md`. Después bórrala.
5. Borra `backlog.md`, la carpeta `.sdd/` y los adaptadores que generó `install-sdd.sh` (los enlaces en `.claude/`, `.codex/`, `.opencode/`…). Luego instala las skills nuevas (§2).
