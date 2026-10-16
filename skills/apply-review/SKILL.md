---
name: apply-review
description: Recorre los hallazgos de una revisión de spec o plan con la persona y aplica solo los cambios que apruebe explícitamente, uno a uno. Después busca otras specs en borrador afectadas por las decisiones. Úsala cuando haya un review-spec.md o review-plan.md y quieran aplicar o descartar sus hallazgos.
---

# Aplicar una revisión

Ayuda a la persona a decidir sobre cada hallazgo y aplica solo lo que apruebe.

**Regla central:** nunca asumas, deduzcas ni apliques un cambio sin una decisión explícita. Si un hallazgo es ambiguo, pide aclaración antes de dar opciones. Cada hallazgo se decide por separado; nunca los agrupes.

## Artefactos y estado

- Cada trabajo vive en `docs/specs/<AAAAMMDD>-<tipo>-<nombre>/`.
- `spec.md` y `plan.md` llevan en el frontmatter `status: borrador | aprobada | obsoleta`. Solo una persona pone `aprobada`.
- Si cambias un artefacto que estaba `aprobada`, devuélvelo a `borrador` y avisa.

## Paso 1: presentar los hallazgos

1. Identifica el trabajo y la revisión (`review-spec.md` o `review-plan.md`). Pregunta si no está claro.
2. Lista todos los hallazgos numerados, primero los bloqueantes. Para cada uno muestra:
   - **Hallazgo [N]:** qué señala la revisión.
   - **Arreglo sugerido**, si lo hay.
   - **Opciones:**
     - A) Aplicar el arreglo tal cual.
     - B) Aplicar un arreglo modificado (lo indica la persona).
     - C) Descartar, con el motivo.
     - D) Aplazar.

Espera a que la persona responda a **todos** antes de seguir.

## Paso 2: confirmar

```
Resumen de decisiones
─────────────────────
[N] <título> → aplicar / modificado / descartado / aplazado
```

Pregunta: "¿Confirmas estas decisiones antes de aplicarlas?" No sigas sin confirmación.

## Paso 3: aplicar

1. Aplica solo los cambios confirmados (A y B), y solo en los artefactos revisados. No toques nada más.
2. Anota en el fichero de revisión, debajo de cada hallazgo, la decisión tomada:
   - para los descartados, el motivo;
   - para los aplazados, qué queda pendiente.
3. Dile a la persona cómo queda:
   - Si no quedan bloqueantes abiertos, el artefacto está listo para que ella lo marque como `aprobada`, o para otra pasada de `review-spec`.
   - Si quedan bloqueantes aplazados o descartados con riesgo, señálalo.

## Paso 4: otras specs afectadas

Comprueba si alguna decisión del paso 2 afecta a otras specs en curso:

1. Busca en `docs/specs/*/spec.md` las que tengan `status: borrador`.
2. Para cada una, razona si alguna decisión introduce un conflicto, cambia una dependencia o invalida un supuesto.
3. Para cada spec que *pueda* verse afectada:
   - enseña qué spec, qué sección y qué habría que cambiar;
   - pregunta: "¿Le afecta esta decisión? ¿Propongo un cambio?". **Espera un sí o un no.**
4. Si dice que sí, redacta solo el cambio mínimo (la sección y las líneas exactas), enseña el diff y **aplícalo solo tras aprobación**.

No mejores, amplíes ni reformatees nada más en esas specs. Si en algún momento no está claro qué hacer, para y pregunta.
