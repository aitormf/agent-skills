---
id: T2
title: Script que cuenta el tamaño del diff para la review
status: done
depends_on: []
examples: [E1, E2, E3, E4, E5, E6]
verification: scripts/check.sh
---
**Propósito:** comportamiento nuevo: `skills/review-context/scripts/diff_size.py <base>...<head>` imprime el tamaño del diff según R1 (D-0045) y si es pequeño (≤200).

**Dentro:** el script (sobre `git diff --numstat`, sin dependencias), con la lista de lockfiles por nombre, los ficheros `linguist-generated` de `.gitattributes`, los snapshots (`__snapshots__/`, `*.snap`) y los binarios a 0; `.gitattributes` de este repo con `adapters/** linguist-generated`; sus casos en `check.sh`, uno por ejemplo, nombrados E1–E6.

**Fuera:** usarlo desde las skills (T4, T5, T7).

**Flag:** ninguno.
