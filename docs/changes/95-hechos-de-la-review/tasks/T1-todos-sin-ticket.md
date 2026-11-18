---
id: T1
title: review_facts.py lista los TODO que añade la rama sin ticket
status: done
depends_on: []
examples: [E1, E2, E3, E4, E5]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: un script que lista, sin modelo, los TODO, FIXME, XXX y HACK que añade la rama sin ticket (R1, D-0057, #90).

**Dentro:** `skills/review-context/scripts/review_facts.py <base>`, con una sección «TODO sin ticket» que sale de las líneas añadidas por `git diff <base>...HEAD`, con `fichero:línea`. Aplica los supuestos del README: qué es un ticket, la forma de comentario y los lockfiles de `diff_size.py`. Los tests van en `scripts/check.sh`, sobre un repo temporal.

**Fuera:** que el informe recoja los TODO (T2); el resto de hechos de la rama (T3, T4).

**Flag:** ninguno.
