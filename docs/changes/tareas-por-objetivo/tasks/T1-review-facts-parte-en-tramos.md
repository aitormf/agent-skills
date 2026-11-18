---
id: T1
title: review_facts.py parte la rama en tramos de commits
status: done
depends_on: []
examples: [E7, E10, E11, E12, E13, E14, E15, E16, E17]
verification: scripts/check.sh
---

**Propósito:** comportamiento nuevo: `review_facts.py` imprime el tamaño de la rama y sus tramos de commits seguidos, según `[review] max_lines_per_reviewer` del `.harness-config.toml` de la rama base (R3, D-0060).

**Dentro:** el corte (voraz, en orden, sin separar `test(Tn)` del commit siguiente, un commit grande en un tramo propio), el recuento con las reglas de `diff_size.py`, la lectura de la clave desde la base (D-0054) y una sección `tramos:` en la salida con el rango `a..b` y las líneas de cada tramo. Sin la clave, un solo tramo `base..HEAD`. Los tests con ramas de prueba en `scripts/check.sh`.

**Fuera:** que `review-prepush` use los tramos (T2); quitar el aviso de tamaño del gate (T3).

**Flag:** ninguno. Sin la clave en `.harness-config.toml`, nada cambia.
