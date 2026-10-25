<!--
PLANTILLA → docs/decisions/NNNN-titulo-en-kebab-case.md
Cópiala con el siguiente número libre (check_decisions.py --next). Los números no se reutilizan.
Corta: estas cuatro secciones, pocas líneas cada una. Borra este comentario.
Las claves y los valores del frontmatter van en inglés; el texto, en el idioma del proyecto.
-->
---
id: D-NNNN
title: <la decisión en pocas palabras>
type: architecture        # architecture | rule | discarded
status: proposed          # proposed | accepted | superseded | obsolete. Solo una persona la pasa a accepted.
date: YYYY-MM-DD
affects: [src/billing/]   # módulos o rutas que restringe; los agentes filtran por aquí
supersedes: null          # D-XXXX si sustituye a otra decisión
superseded_by: null       # D-YYYY, cuando otra más nueva la sustituya
issue: null               # "#42" o una URL
---

# D-NNNN: <la decisión en pocas palabras>

## Contexto

<!-- Qué obligó a elegir: el problema, las restricciones, los hechos. No opiniones. -->

## Decisión

<!-- En voz activa y concreta: "El reembolso es total si se cancela con más de 1 h de antelación". Para un
descarte: qué se probó, qué pasó y "no usamos X". -->

## Alternativas descartadas

<!-- La sección más valiosa: evita que personas y agentes vuelvan a proponerlas. -->

- <opción>: <motivo concreto>

## Cómo se hace cumplir

<!-- Test (y su nombre), regla de lint, test de arquitectura, comprobación en CI, o "no se automatiza". -->
